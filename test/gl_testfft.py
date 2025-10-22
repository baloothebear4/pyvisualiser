# stereo_spectrum_gl.py
# FINAL VERSION: Corrected FFT size, Octave-Band processing, 90 degree rotation, and needle scaling.

import sys, time
import pygame
from pygame.locals import *
from OpenGL.GL import *
import numpy as np
import math
from scipy.fft import rfft 
import pyaudio
from multiprocessing import Queue

# PyOpenGL context fix for certain environments
from OpenGL import contextdata
contextdata.setValue = lambda *args, **kwargs: None

# --- General Configuration ---
AUDIO_DEVICE_NAME = 'loopin' 
VU_RMS_SCALING    = 10.0 
FFT_SMOOTH_FACTOR = 0.5 

# TALL screen dimensions for the window
WIDTH, HEIGHT = 400, 1280
# Content aspect ratio is WIDE (1280x400)
CONTENT_WIDTH, CONTENT_HEIGHT = 1280, 400
FPS = 60
# -----------------------------

# --- Audio Processor Constants ---
CHANNELS        = 2
INFORMAT        = pyaudio.paInt16
RATE            = 44100
FRAME           = 1024 # FFT buffer size
FRAMESIZE       = FRAME * CHANNELS
maxValue        = float(2**15)
VUSAMPLES       = 0.25 / (FRAMESIZE/RATE)
AUDIO_QUEUE_MAXSIZE = 10
WINDOW          = 12
NUMPADS         = 0
# --- Octave Band Constants ---
FIRSTCENTREFREQ = 31.25     
LASTCENTREFREQ  = 16000.0   
DCOFFSETSAMPLES = 50        
VUGAIN          = 0.25      

# Calculate dependent constants
BINBANDWIDTH = RATE / (FRAME + NUMPADS)
OCTAVE_SPACING = 3.0 
# ---------------------------------

# Mock Events class 
class Events:
    def Audio(self, event_name):
        pass

# --- Audio Processor Classes ---
class WindowAve:
    def __init__(self, size):
        self.window = [1.0]*int(size)
        self.size   = int(size)
    def average(self, data):
        self.window.insert(0, data)
        del self.window[-1]
        return sum(self.window)/len(self.window)
    def reset(self,type):
        self.window = [0.0]*int(self.size) if type == 'silence' else [1.0]*int(self.size)

class AudioData:
    def __init__(self):
        data_s = np.arange(FRAME)
        self.vu = {'left': 0.0, 'right':0.0, 'mono':0.0}
        
        self.dc             = []
        self.dcoffset       = 0.0
        # bins needs to hold the raw rfft output length (FRAME/2 + NUMPADS + 1)
        self.bins           = {'left': np.zeros(FRAME//2 + NUMPADS + 1), 'right': np.zeros(FRAME//2 + NUMPADS + 1)}
        self.minC           = 120.0 
        self.peakC          = 0.0   
        self.readtime       = []
        self.startreadtime  = 0.0
        
        self.intervalUpperF = self.createBands(OCTAVE_SPACING)
        self.SPECTRUM_BINS  = len(self.intervalUpperF)

        self.spectrum = {'left': np.zeros(self.SPECTRUM_BINS, dtype=np.float32), 
                         'right': np.zeros(self.SPECTRUM_BINS, dtype=np.float32),
                         'mono': np.zeros(self.SPECTRUM_BINS, dtype=np.float32)}
        
        self.samples  = {'left': data_s, 'right':data_s, 'mono':data_s}
        self.vuwindow = {'left': WindowAve(VUSAMPLES), 'right': WindowAve(VUSAMPLES), 'mono': WindowAve(VUSAMPLES)}
        self.oldspectrum = np.zeros(self.SPECTRUM_BINS, dtype=np.float32)

    def createBands(self, spacing, fcentre=FIRSTCENTREFREQ, flast=LASTCENTREFREQ):
        flast = LASTCENTREFREQ if flast is None else flast
        intervalUpperF      = []
        centres             = []
        startbin      = 1
        FFACTOR       = math.pow(2, 1.0/float(2*spacing) )
        intervalUpper = fcentre * FFACTOR

        while intervalUpper < flast:
            bincount        = startbin
            fcentre         = fcentre * math.pow(2, float(1.0/spacing))
            intervalUpper   = fcentre * FFACTOR

            if bincount*BINBANDWIDTH > intervalUpper:
                continue
            else:
                while (bincount+1)*BINBANDWIDTH <= intervalUpper:
                    bincount    += 1
                intervalUpperF.append( intervalUpper )
                centres.append( fcentre )

            startbin = bincount+1
        return intervalUpperF

class AudioProcessor(AudioData):
    def __init__(self, events, device=AUDIO_DEVICE_NAME):
        self.events   = events
        self.recorder = pyaudio.PyAudio()
        self.device = -1 
        self.find_device_index(device)
        AudioData.__init__(self) 
        
        # CORRECTED: Window size must be the full FRAME length (e.g., 1024)
        self.window     = np.kaiser(FRAME, WINDOW) 
        self.audio_queue = Queue(maxsize=AUDIO_QUEUE_MAXSIZE)

        device_name = self.recorder.get_device_info_by_index(self.device)['name'] if self.device != -1 else "Default"
        print(f"AudioProcessor.__init__> ready and reading from soundcard: {device_name}. Spectrum Bins: {self.SPECTRUM_BINS}")

    def find_device_index(self, device):
        p = self.recorder
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0 and device.lower() in info['name'].lower():
                self.device = i
                return
        try:
            self.device = p.get_default_input_device_info()['index']
        except Exception:
            self.device = -1

    def start_capture(self):
        if self.device == -1:
            return
        try:
            self.stream   = self.recorder.open(format = INFORMAT,rate = RATE,channels = CHANNELS,input = True, \
                                               input_device_index=self.device, frames_per_buffer=FRAME, stream_callback=self.callback)
            self.stream.start_stream()
        except Exception as e:
            print(f"AudioProcessor.start_capture> ADC/DAC not available: {e}")

    def stop_capture(self):
        try:
            if hasattr(self, 'stream') and self.stream.is_active():
                self.stream.stop_stream()
                self.stream.close()
            self.recorder.terminate()
        except Exception:
            pass

    def callback(self, in_data, frame_count, time_info, status):
        try:
            data = np.frombuffer(in_data, dtype=np.int16)
            if not self.audio_queue.full():
                self.audio_queue.put_nowait(data)
        except Exception:
            pass
        return (None, pyaudio.paContinue)

    def process_audio_frame(self):
        if not self.audio_queue.empty():
            data = self.audio_queue.get_nowait()
            
            raw_left  = data[0::2]
            raw_right = data[1::2]
            
            self.calcDCoffset(raw_left) 
            raw_left  = raw_left - self.dcoffset
            raw_right = raw_right - self.dcoffset

            self.samples['left']  = raw_left
            self.samples['right'] = raw_right
            self.samples['mono']  = np.mean(data.reshape(len(data)//CHANNELS, CHANNELS) ,axis=1) 
            
            self.process_vu()
            self.process_spectrum() 
            
            return True
        return False

    def process_vu(self):
        vu_left  = self.VU('left')
        vu_right = self.VU('right')

        self.vu['left']  = self.vuwindow['left'].average(vu_left)
        self.vu['right'] = self.vuwindow['right'].average(vu_right)
        
        self.vu['left'] = max(0.0, min(1.0, self.vu['left']))
        self.vu['right'] = max(0.0, min(1.0, self.vu['right']))

    def process_spectrum(self):
        self.bins['left']  = self.calcFFT(self.samples['left'])
        self.bins['right'] = self.calcFFT(self.samples['right'])
        
        left_bands = self.packFFT(self.intervalUpperF, channel='left')
        right_bands = self.packFFT(self.intervalUpperF, channel='right')

        new_spectrum_L = np.array(left_bands, dtype=np.float32)
        new_spectrum_R = np.array(right_bands, dtype=np.float32)
        
        self.spectrum['left'] = (self.spectrum['left'] * FFT_SMOOTH_FACTOR) + (new_spectrum_L * (1.0 - FFT_SMOOTH_FACTOR))
        self.spectrum['right'] = (self.spectrum['right'] * FFT_SMOOTH_FACTOR) + (new_spectrum_R * (1.0 - FFT_SMOOTH_FACTOR))
        
        self.spectrum['mono'] = (self.spectrum['left'] + self.spectrum['right']) / 2.0


    def VU(self, channel):
        normalized_data = self.samples[channel] / maxValue
        rms = np.sqrt(np.mean(np.square(normalized_data)))
        if np.isnan(rms): rms = 0.0
        return min(1.0, rms / VUGAIN)

    def calcDCoffset(self, data):
        self.dc.append(np.mean(data))
        if len(self.dc) > DCOFFSETSAMPLES:
            del self.dc[0]
        self.dcoffset = sum(self.dc)/len(self.dc)
        return self.dcoffset

    def calcFFT(self, data):
        """ Calculate the Real FFT using the full frame size. """
        # CORRECTED: Use the full FRAME length data (no slicing)
        windowed_data = data * self.window 
        
        # Padded length is based on the full FRAME size
        padded_len = FRAME + NUMPADS 
        
        spectrum = rfft(windowed_data, n=padded_len)
        
        spectrum = np.abs(spectrum) / maxValue 
        return spectrum

    def packFFT(self, intervalUpperF, channel='left'):
        '''
        # Pack bins into octave intervals
        # Convert amplitude into dBs
        '''
        bins = self.bins[channel]

        startbin = 1 #do not use bin[0] which is DC
        spectrumBands = []
        
        # Max valid bin index (e.g., 512)
        MAX_BIN_INDEX = FRAME//2 + NUMPADS 

        for band in intervalUpperF:  # collect bins at a time
            bincount    = startbin

            while bincount*BINBANDWIDTH <= band:
                bincount    += 1
            
            # IMPORTANT FIX: Clamp the upper boundary to the highest valid bin index
            # Ensure we don't try to read past the end of the rfft array
            end_bin = min(bincount, MAX_BIN_INDEX + 1) # +1 because slicing is exclusive

            # If the startbin is already beyond the MAX_BIN_INDEX, stop processing bands
            if startbin > MAX_BIN_INDEX:
                 break
            
            # Calculate the mean only on the available bins [startbin : end_bin]
            level = 20*np.log2((bins[startbin:end_bin].mean() + 1e-7))
            spectrumBands.append( self.normalise(level) )
            
            # Update startbin for the next band
            startbin = end_bin
            
        return spectrumBands

    def normalise(self, level):
        self.dynamicRange(level) 
        floor = -self.minC
        scale = self.peakC + floor + 0.0001
        return (floor + level)/(scale )

    def dynamicRange(self, level):
        if level > self.peakC: self.peakC = level
        if level < self.minC: self.minC = level

    def getSpectrum(self, octave=OCTAVE_SPACING, intervalUpperF=None, left=True):
        if intervalUpperF is None: intervalUpperF = self.intervalUpperF
        power = self.spectrum['left'] if left else self.spectrum['right']
        return power.tolist() 


# --- END OF AUDIO PROCESSOR CLASSES ---

# --- VERTEX SHADER (FINAL: 90 degree clockwise rotation) ---
VERTEX_SHADER = """#version 130
in vec2 a_pos;
out vec2 v_uv;

void main() {
    // FINAL: 90 degree clockwise rotation for a TALL display.
    vec2 rotated_pos = vec2(a_pos.y, -a_pos.x); 
    
    gl_Position = vec4(rotated_pos, 0.0, 1.0);
    v_uv = a_pos * 0.5 + 0.5;
}
"""

# --- FRAGMENT SHADER: STEREO VU & SPECTRUM (Needle Fix Applied) ---
FRAGMENT_SHADER_SPECTRUM = """#version 130
out vec4 outColor;
uniform vec2 resolution; // (1280, 400)
in vec2 v_uv;
uniform float vu_left;
uniform float vu_right;
uniform float spectrum[50]; 

const float PI = 3.14159265359;
const int MAX_BINS = 50; 

// Draw a line segment
float line(vec2 p, vec2 a, vec2 b, float width) {
    vec2 pa = p - a;
    vec2 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return smoothstep(1.0, 0.0, length(pa - ba * h) / width);
}

// Draw a VU meter dial and needle
vec3 draw_vu_meter(vec2 center_uv, float vu_level, float dial_radius, float needle_length) {
    vec2 p = v_uv - center_uv;
    p.x *= resolution.x / resolution.y; 
    float radius_outer = dial_radius + 0.05;
    float dist = length(p);
    vec3 color = vec3(0.0);

    float dial_mask = smoothstep(radius_outer, radius_outer - 0.02, dist);
    color = mix(color, vec3(0.07, 0.09, 0.19), dial_mask);

    float min_angle = PI * 0.75; 
    float max_angle = PI * 0.25; 

    float needle_angle = mix(min_angle, max_angle, clamp(vu_level, 0.0, 1.0));
    
    vec2 needle_end_relative = vec2(needle_length * cos(needle_angle), needle_length * sin(needle_angle));
    
    // Correct X-component for aspect ratio
    vec2 needle_end_corrected_relative = needle_end_relative * vec2(resolution.y / resolution.x, 1.0); 
    
    // Define the final endpoint in UV space
    vec2 needle_end_uv = center_uv + needle_end_corrected_relative;

    float needle_width = 0.003;
    
    // Use the fully corrected UV endpoint
    float needle_mask = line(v_uv, center_uv, needle_end_uv, needle_width); 
    
    vec3 needle_color = vec3(0.8, 0.1, 0.1); 
    color = mix(color, needle_color, needle_mask);

    float hub_mask = smoothstep(0.05, 0.0, dist);
    color = mix(color, vec3(0.3), hub_mask);
    
    return color;
}

vec3 draw_spectrum_bar(vec2 uv, int num_bins) {
    vec3 color = vec3(0.0);
    
    float x_start = 0.30;
    float x_end = 0.70;
    float y_base = 0.05; 
    float max_height = 0.70; 

    float total_width = x_end - x_start;
    float bar_width_total = total_width / float(MAX_BINS); 
    float bar_spacing = bar_width_total * 0.1;
    float bar_width = bar_width_total - bar_spacing;
    
    for (int i = 0; i < num_bins; i++) {
        float bar_x_start = x_start + float(i) * bar_width_total;
        float bar_x_end = bar_x_start + bar_width;
        float bar_height = spectrum[i] * max_height;
        
        float bar_y_end = y_base + bar_height;
        
        if (uv.x >= bar_x_start && uv.x < bar_x_end && uv.y >= y_base && uv.y <= bar_y_end) {
            
            float h_norm = (uv.y - y_base) / max_height;
            vec3 bar_color = mix(vec3(0.1, 0.3, 0.5), vec3(0.3, 0.6, 0.9), h_norm);

            float edge_x = smoothstep(0.0, 0.001, uv.x - bar_x_start) * smoothstep(0.0, 0.001, bar_x_end - uv.x);
            float edge_y = smoothstep(0.0, 0.002, bar_y_end - uv.y) * smoothstep(0.0, 0.001, uv.y - y_base);
            
            color = mix(color, bar_color, edge_x * edge_y);
        }
    }
    return color;
}


void main() {
    int num_bins = int(min(gl_MaxTextureImageUnits, 50)); 
    
    vec2 center_left = vec2(0.25, 0.5);
    vec3 color_left = draw_vu_meter(center_left, vu_left, 0.4, 0.35); 

    vec2 center_right = vec2(0.75, 0.5);
    vec3 color_right = draw_vu_meter(center_right, vu_right, 0.4, 0.35);
    
    vec3 final_color = color_left + color_right;
    
    vec3 spectrum_color = draw_spectrum_bar(v_uv, num_bins);

    final_color = mix(final_color, spectrum_color, max(spectrum_color.r, max(spectrum_color.g, spectrum_color.b)));
    
    outColor = vec4(final_color, 1.0);
}
"""

# --- GL helper functions (Unchanged) ---
def compile_shader(src, shader_type):
    sh = glCreateShader(shader_type)
    glShaderSource(sh, src)
    glCompileShader(sh)
    ok = glGetShaderiv(sh, GL_COMPILE_STATUS)
    if not ok:
        err = glGetShaderInfoLog(sh).decode()
        raise RuntimeError("Shader compile error: " + err)
    return sh

def link_program(vs_src, fs_src):
    vs = compile_shader(vs_src, GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, GL_FRAGMENT_SHADER)
    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    ok = glGetProgramiv(prog, GL_LINK_STATUS)
    if not ok:
        err = glGetProgramInfoLog(prog).decode()
        raise RuntimeError("Program link error: " + err)
    glDeleteShader(vs)
    glDeleteShader(fs)
    return prog

def make_fullscreen_quad_vao():
    data = np.array([
        -1.0, -1.0, 1.0, -1.0,
        -1.0,  1.0, 1.0,  1.0
    ], dtype=np.float32)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo

# ----------------- Main Loop -----------------
def main():
    # --- 1. Audio Setup ---
    events = Events()
    audio_proc = AudioProcessor(events)
    audio_proc.start_capture() 

    SPECTRUM_BINS_GL = audio_proc.SPECTRUM_BINS 
    
    # --- 2. Pygame/GL Setup ---
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Stereo VU & Spectrum Demo")

    prog = link_program(VERTEX_SHADER, FRAGMENT_SHADER_SPECTRUM)
    glUseProgram(prog)

    res_loc = glGetUniformLocation(prog, "resolution")
    vu_left_loc = glGetUniformLocation(prog, "vu_left")
    vu_right_loc = glGetUniformLocation(prog, "vu_right")
    spectrum_loc = glGetUniformLocation(prog, "spectrum")

    vbo = make_fullscreen_quad_vao()
    a_pos = glGetAttribLocation(prog, "a_pos")
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glEnableVertexAttribArray(a_pos)
    glVertexAttribPointer(a_pos, 2, GL_FLOAT, GL_FALSE, 0, None)

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)

    clock = pygame.time.Clock()
    running = True
    
    print(f"\nStarting visualizer. Monitoring stereo audio input. Drawing {SPECTRUM_BINS_GL} Octave Bands.")

    while running:
        clock.tick(FPS)
        
        for evt in pygame.event.get():
            if evt.type == QUIT or (evt.type == KEYDOWN and evt.key == K_ESCAPE):
                running = False

        # --- 3. Audio Processing Update ---
        audio_proc.process_audio_frame()
        current_vu_left = audio_proc.vu['left']
        current_vu_right = audio_proc.vu['right']
        spectrum_data = audio_proc.spectrum['mono'] 
        
        # --- 4. Render Frame ---
        glUseProgram(prog)

        glUniform2f(res_loc, float(CONTENT_WIDTH), float(CONTENT_HEIGHT))
        glUniform1f(vu_left_loc, current_vu_left)
        glUniform1f(vu_right_loc, current_vu_right)
        
        glUniform1fv(spectrum_loc, SPECTRUM_BINS_GL, spectrum_data) 

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        pygame.display.flip()

    # --- 5. Cleanup ---
    audio_proc.stop_capture()
    glDeleteBuffers(1, [vbo])
    glDeleteProgram(prog)
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()