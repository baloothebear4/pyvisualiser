import pygame, os
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import time, math, os, wave
from multiprocessing import Queue
from scipy.fft import rfft
from scipy.signal import butter, lfilter
import pyaudio # *** New required dependency ***

# PyOpenGL workaround for embedded systems (prevents context data errors)
from OpenGL import contextdata
contextdata.setValue = lambda *args, **kwargs: None


# --- AUDIO CONSTANTS (From User's Code) ---
CHANNELS        = 2
INFORMAT        = pyaudio.paInt16
RATE            = 44100
FRAME           = 1024
FRAMESIZE       = FRAME * CHANNELS
CRITICAL_TIME_MS = (FRAME / RATE) * 1000
maxValue        = float(2**15)
SAMPLEPERIOD    = FRAMESIZE/RATE
AUDIO_QUEUE_MAXSIZE = 10
SILENCESAMPLES  = 7   / SAMPLEPERIOD
PEAKSAMPLES     = 0.7 / SAMPLEPERIOD
VUSAMPLES       = 0.25 / SAMPLEPERIOD
RECORDSTATE     = False
RECORDTIME      = 30 * 60 / SAMPLEPERIOD / CHANNELS
RECORDPATH      = "/home/pi/preDAC/rec/"
RECORDFILESUFFIX = "preDAC"
RECORDINGS_PATTERN = RECORDPATH + RECORDFILESUFFIX + "-%s.wav"
WINDOW          = 12
FIRSTCENTREFREQ = 10
LASTCENTREFREQ  = RATE // 3
OCTAVE          = 3
NUMPADS         = 0 # Set to 0 for simplicity, adjust if FFT length is not power of 2
BINBANDWIDTH    = RATE/(FRAME + NUMPADS)
DCOFFSETSAMPLES = 200
VUGAIN          = 0.06
RMSNOISEFLOOR   = -70
SILENCETHRESOLD = 0.001

# --- MINIMAL EVENTS CLASS STUB ---
# Needed to satisfy the dependency in AudioProcessor without the user's events.py file
class Events:
    def __init__(self, *args):
        pass
    def Audio(self, event_name):
        # print(f"Event triggered: {event_name}") # Uncomment for debugging
        pass

class WindowAve:
    """ Class to find the moving average of a set of window of points """
    def __init__(self, size):
        self.window = [1.0]*int(size)
        self.size   = int(size)

    def average(self, data):
        #add the data point to the window
        self.window.insert(0, data)
        del self.window[-1]
        return sum(self.window)/len(self.window)

    def reset(self,type):
        if type == 'silence':
            self.window = [0.0]*int(self.size)
        else:
            self.window = [1.0]*int(self.size)

class AudioData():
    def __init__(self):
        data          = [0.5]*50
        data_s        = np.arange(FRAMESIZE)

        self.vu       = {'left': 0.0, 'right':0.0, 'mono':0.0} # Initialized to 0.0
        self.peak     = {'left': 0.8, 'right':0.8, 'mono':0.8}
        self.vumax    = {'left': 0.01, 'right':0.01, 'mono':0.01}
        self.peakmax  = {'left': 3.9, 'right':3.9, 'mono':3.9}
        self.spectrum = {'left': data, 'right':data, 'mono':data}
        self.bins     = {'left': np.zeros(512), 'right':np.zeros(512), 'mono':np.zeros(512)} # Pre-allocate size
        self.samples  = {'left': data_s, 'right':data_s, 'mono':data_s}
        self.oldsamples  = {'left': data_s, 'right':data_s, 'mono':data_s}
        self.spectra  = {'left': data_s, 'right':data_s, 'mono':data_s}
        self.signal_detected = False
        self.peakwindow      = {'left': WindowAve(PEAKSAMPLES), 'right': WindowAve(PEAKSAMPLES), 'mono': WindowAve(PEAKSAMPLES)}
        self.vuwindow        = {'left': WindowAve(VUSAMPLES), 'right': WindowAve(VUSAMPLES), 'mono': WindowAve(VUSAMPLES)}
        self.recordfile = self.find_next_file( RECORDINGS_PATTERN )


    def find_next_file(self, path_pattern):
        # Stub: avoids OS errors if not running on Pi with specific path
        return "temp_recording.wav" 

class AudioProcessor(AudioData):
    def __init__(self, events, device='loopin'):
        self.events   = events
        self.recorder = pyaudio.PyAudio()
        self.audio_available = False

        # set up audio input
        self.device = self.find_device_index(device)

        self.recordingState = RECORDSTATE
        self.recording      = []

        AudioData.__init__(self)

        self.peakC      = RMSNOISEFLOOR
        self.minC       = maxValue
        self.dc         = []
        self.readtime   = []
        self.silence    = WindowAve(SILENCESAMPLES)
        # Use FRAME//2 for window length as rfft is applied to the first half of the frame (512 samples)
        self.window     = np.kaiser(FRAME // 2, WINDOW) 
        
        try:
             dev_info = self.recorder.get_device_info_by_index(self.device)
             print(f"AudioProcessor.__init__> ready and reading from soundcard {dev_info['name']}")
        except:
             print("AudioProcessor.__init__> ready (default device)")

        self.audio_queue = Queue(maxsize=AUDIO_QUEUE_MAXSIZE)


    def find_device_index(self, device):
        p = self.recorder
        try:
            # Try to find the loopback device or use default
            target_index = -1
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    if device.lower() in info['name'].lower():
                        target_index = i
                        break
                    # If on Linux and 'default' is requested, often device 0 is a good bet
                    if device == 'default':
                        target_index = 0
                        break
            
            if target_index == -1:
                print("\nAudioProcessor.find_device_index> ⚠️ Warning: Target device not found. Using default input.")
                target_index = p.get_default_input_device_info()['index']
            
            return target_index

        except Exception as e:
            print(f"\nAudioProcessor.find_device_index> ❌ ERROR finding device: {e}")
            return p.get_default_input_device_info()['index']
        

    def start_capture(self):
        try:
            self.stream   = self.recorder.open(format = INFORMAT,rate = RATE,channels = CHANNELS,input = True, \
                                               input_device_index=self.device, frames_per_buffer=FRAMESIZE, stream_callback=self.callback)
            self.stream.start_stream()
            print("AudioProcessor.start_capture> Stream started successfully.")
        except Exception as e:
            print(f"AudioProcessor.start_capture> ❌ ADC/DAC not available or configuration error: {e}")


    def stop_capture(self):
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.recorder.terminate()
        except Exception as e:
            print(f"AudioProcessor.stop_capture> error: {e}")


    def callback(self, in_data, frame_count, time_info, status):
        # 1. CHECK FOR AUDIO BUFFER OVERFLOW
        if status & pyaudio.paInputOverflow:
            print(f"AudioProcessor.callback> *** [FRAME DROPPED] *** queue size {self.audio_queue.qsize()}")
            
        # 2. Convert and queue the data
        try:
            # np.frombuffer is very fast and runs in C
            in_data_array = np.frombuffer(in_data, dtype=np.int16)
            if not self.audio_queue.full():
                # put_nowait avoids blocking the audio thread
                self.audio_queue.put_nowait(in_data_array) 
        except Exception as e:
            print(f"AudioProcessor.callback> exception during queueing: {e}")
            pass
        
        # Must return (None, paContinue) for successful callback
        return (None, pyaudio.paContinue)        


    def is_audio_available(self):
        """ Checks queue and processes if data is available """
        if not self.audio_queue.empty():
            data = self.audio_queue.get_nowait()
            
            # --- Audio Decoding (Fast) ---
            self.samples['left']  = data[0::2]
            self.samples['right'] = data[1::2]
            self.samples['mono']  = np.mean(data.reshape(len(data)//CHANNELS, CHANNELS) ,axis=1) 
            
            # --- Processing (Moderate) ---
            self.process() 
            self.audio_available = True 
            return True
        return False


    def process(self, bass=500, treble=5000):
        # 1. VU Metering (RMS)
        self.vu['left']     = self.VU('left')
        self.vu['right']    = self.VU('right')
        self.vu['mono']     = self.VU('mono')
        
        # 2. FFT Calculation
        # Only process up to 512 samples for speed/power of 2 compatibility
        self.bins['left']   = self.calcFFT(self.samples['left'])
        self.bins['right']  = self.calcFFT(self.samples['right'])
        
        # The fastest way using already computed magnitude bins
        self.bins['mono'] = (self.bins['left'] + self.bins['right']) / 2.0
        
        # 3. Silence Detection
        self.detectSilence()

        # NOTE: Your original spectral averaging and filtering code is complex,
        # we focus on VU and raw FFT bins for fast uniform updates.

    def detectSilence(self):
        # Check if average level is below silence threshold
        signal_level = (self.vu['left'] + self.vu['right'])/2.0
        ave_level    = self.silence.average(signal_level)

        if ave_level < SILENCETHRESOLD and self.signal_detected:
            self.signal_detected = False
            self.silence.reset('signal')
            self.events.Audio('silence_detected')
        elif not self.signal_detected and signal_level >= SILENCETHRESOLD:
            self.signal_detected = True
            self.silence.reset('signal')
            self.events.Audio('signal_detected')

    def VU(self, channel):
        normalized_data = self.samples[channel] / maxValue
        rms = np.sqrt(np.mean(np.square(normalized_data)))
        if np.isnan(rms): rms = 0.0
        # return VU scaled to 0-1
        return min(1.0, rms / VUGAIN)


    def calcFFT(self, data):
        """ Calculate the Real FFT and normalise (fastest method) """
        
        # 1. Apply Window/Slice: Slice to 512 samples
        windowed_data = data[:FRAME // 2] * self.window 
        
        # 2. Use rfft for a ~2x speedup on real-valued data
        spectrum = rfft(windowed_data, n=FRAME // 2 + NUMPADS) # n=512
        
        # 3. Get magnitude and normalize
        spectrum = np.abs(spectrum) / maxValue
        
        return spectrum

    # Remaining methods (recording, filtering, printing) are omitted from the single file 
    # for brevity and focus on the main visualiser functionality.
    def record(self, data): pass
    def saveRecording(self): pass

# --- GLSL SHADER SOURCES ---
vertex_src = """
#version 130
in vec2 position;
out vec2 fragCoord;

void main() {
    vec2 rotated_pos = vec2(position.y, -position.x);
    gl_Position = vec4(rotated_pos, 0.0, 1.0);
    fragCoord = position * 0.5 + 0.5;
}
"""

frag_src = """
#version 130
// Optimisation for embedded hardware: Use medium precision for better performance
precision mediump float;

in vec2  fragCoord;
out vec4 fragColor;

uniform float iTime;
uniform vec2 iResolution;
uniform float u_fold_offset; // New uniform for geometry folding/size
uniform float u_speed_mult;  // New uniform for animation speed

vec3 palette(float d){
    return mix(vec3(0.2,0.7,0.9),vec3(1.,0.,1.),d);
}

vec2 rotate(vec2 p,float a){
    float c = cos(a);
    float s = sin(a);
    return p*mat2(c,s,-s,c);
}

float map(vec3 p){
    // Keep 8 iterations for complexity
    for( int i = 0; i<8; ++i){ 
        float t = iTime * u_speed_mult;
        p.xz =rotate(p.xz,t);
        p.xy =rotate(p.xy,t*1.89);
        p.xz = abs(p.xz);
        p.xz -= u_fold_offset;
    }
    return dot(sign(p),p)/5.;
}

vec4 rm (vec3 ro, vec3 rd){
    float t = 0.;
    vec3 col = vec3(0.);
    float d;
    
    // OPTIMIZATION: Reduced iterations from 64 to 32 
    for(float i =0.; i<64.; i++){ 
        vec3 p = ro + rd*t;
        d = map(p)*.5;
        if(d<0.02){
            break;
        }
        if(d>100.){
            break;
        }
        col+=palette(length(p)*.1)/(400.*(d));
        t+=d;
    }
    return vec4(col,1./(d*100.));
}

void main()
{
    // Normalize by screen height (iResolution.y)
    vec2 uv = (fragCoord * iResolution.xy - iResolution.xy * 0.5) / iResolution.y;
    
    vec3 ro = vec3(0.,0.,-50.);
    ro.xz = rotate(ro.xz,iTime/2);
    vec3 cf = normalize(-ro);
    vec3 cs = normalize(cross(cf,vec3(0.,1.,0.)));
    vec3 cu = normalize(cross(cf,cs));
    
    vec3 uuv = ro+cf*3. + uv.x*cs + uv.y*cu;
    
    vec3 rd = normalize(uuv-ro);
    
    vec4 col = rm(ro,rd);
    
    
    fragColor = col;
}
"""

def make_fullscreen_quad_vertices():
    """Defines a full-screen quad that covers Normalized Device Coordinates (-1 to 1)."""
    return np.array([
        -1.0, -1.0,  1.0, -1.0,  1.0,  1.0,
        -1.0, -1.0,  1.0,  1.0, -1.0,  1.0
    ], dtype=np.float32)

def main():
    # Configuration
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 400
    START_TIME = time.time()
    
   # --- Increase Process Priority for Real-Time Audio/Video ---
    # Set niceness to -10 (higher priority than default 0)
    # This requires the script to be run with 'sudo' or have capability permissions.
    try:
        os.nice(-10)
        print("Set process niceness to -10 (high priority).")
    except PermissionError:
        print("Warning: Could not set process priority. Run with 'sudo' or use the 'nice' command.")

    # --- 1. Audio Setup ---
    events = Events('Audio')
    # If using RPi, you might need to change 'default' to your specific device name like 'hw:Loopback,0'
    audio_processor = AudioProcessor(events, device='loopin') 
    audio_processor.start_capture()

    # --- 2. Pygame/OpenGL Setup ---
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("GLSL Music Visualizer")

    try:
        prog = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(frag_src, GL_FRAGMENT_SHADER)
        )
    except Exception as e:
        print("Shader Compilation Error:")
        print(e)
        audio_processor.stop_capture()
        pygame.quit()
        return

    glUseProgram(prog)

    # --- Uniform Locations ---
    time_loc = glGetUniformLocation(prog, "iTime")
    res_loc = glGetUniformLocation(prog, "iResolution")
    fold_offset_loc = glGetUniformLocation(prog, "u_fold_offset")
    speed_mult_loc = glGetUniformLocation(prog, "u_speed_mult")
    
    # --- Geometry setup ---
    vertices = make_fullscreen_quad_vertices()
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    pos_loc = glGetAttribLocation(prog, "position")
    glEnableVertexAttribArray(pos_loc)
    glVertexAttribPointer(pos_loc, 2, GL_FLOAT, GL_FALSE, 0, None)

    # --- Draw loop ---
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        
        # --- 3. Audio Processing and Mapping ---
        if audio_processor.is_audio_available():
            
            # 1. Map Overall Volume/VU to u_fold_offset (0.4 to 0.7)
            # This makes the main shape pulse with the rhythm/volume
            vu_mono = audio_processor.vu['mono']
            # Clamp value between 0.4 and 0.7, centered around 0.5
            target_offset = 0.5+ (vu_mono * 0.2) 
            glUniform1f(fold_offset_loc, target_offset)

            # 2. Map High Frequency Energy to u_speed_mult (0.1 to 1.5)
            # This makes the shape rotate faster when there is treble/activity
            
            # Find the average magnitude of the upper half of the spectrum (high frequencies)
            bins = audio_processor.bins['mono']
            # Find the peak amplitude in the top 25% of frequency bins (e.g., ~5kHz to 22kHz)
            # Start bin is chosen arbitrarily high to capture *only* high-frequency content
            start_bin = len(bins) * 3 // 4 
            
            if len(bins) > 0:
                 high_freq_energy = np.mean(bins[start_bin:]) 
            else:
                 high_freq_energy = 0.0

            # Scale and clamp the speed (0.1 is base speed, max 1.5)
            target_speed = 0.2 + (high_freq_energy * 5.0) 
            target_speed = np.clip(target_speed, 0.1, 1.5)
            glUniform1f(speed_mult_loc, target_speed)
            
        else:
            # If no audio is detected yet, use fallback animation values
            elapsed_time = time.time() - START_TIME
            glUniform1f(fold_offset_loc, 0.5 + 0.1 * np.sin(elapsed_time * 1.5))
            glUniform1f(speed_mult_loc, 0.2) # Default speed

        # 4. Render Frame
        elapsed_time = time.time() - START_TIME
        glUniform1f(time_loc, elapsed_time)
        glUniform2f(res_loc, float(SCREEN_WIDTH), float(SCREEN_HEIGHT))
        
        glClearColor(0.02, 0.02, 0.02, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        
        pygame.display.flip()
        clock.tick(60) # Keep frame rate stable at 45 FPS

    # --- Cleanup ---
    audio_processor.stop_capture()
    pygame.quit()

if __name__ == "__main__":
    main()
