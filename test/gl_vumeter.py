# vu_meter_gl.py
# Analogue VU Meter driven by AudioProcessor
# Requires: pygame, PyOpenGL, numpy, scipy, pyaudio

import sys, time, threading
import pygame
from pygame.locals import *
from OpenGL.GL import *
import numpy as np
import math
import os
from scipy.fft import rfft
from scipy.signal import butter, lfilter
import pyaudio
import wave
from multiprocessing import Queue

# PyOpenGL context fix for certain environments
from OpenGL import contextdata
contextdata.setValue = lambda *args, **kwargs: None

# Mock Events class since the full context isn't provided
class Events:
    def Audio(self, event_name):
        # print(f"Event: Audio.{event_name}")
        pass

# --- Audio Processor Constants ---
CHANNELS        = 2
INFORMAT        = pyaudio.paInt16
RATE            = 44100
FRAME           = 1024
FRAMESIZE       = FRAME * CHANNELS
CRITICAL_TIME_MS = (FRAME / RATE) * 1000
maxValue        = float(2**15)
SAMPLEPERIOD    = FRAMESIZE/RATE
SILENCESAMPLES  = 7   / SAMPLEPERIOD
VUSAMPLES       = 0.25 / SAMPLEPERIOD  # 0.25 seconds is the ANSI VU standard
AUDIO_QUEUE_MAXSIZE = 10
VUGAIN          = 0.06 # Original value, adjusted in VU method for better visualization
RMSNOISEFLOOR   = -70
SILENCETHRESOLD = 0.001
WINDOW = 12
NUMPADS = FRAME
# --- End of constants ---

# --- Audio Processor Classes ---

class WindowAve:
    """ Class to find the moving average of a set of window of points """
    def __init__(self, size):
        self.window = [1.0]*int(size)
        self.size   = int(size)

    def average(self, data):
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
        data = [0.0]*50
        data_s = np.arange(FRAMESIZE)
        self.vu = {'left': 0.0, 'right':0.0, 'mono':0.0}
        self.samples  = {'left': data_s, 'right':data_s, 'mono':data_s}
        self.signal_detected = False
        self.vuwindow = {'left': WindowAve(VUSAMPLES), 'right': WindowAve(VUSAMPLES), 'mono': WindowAve(VUSAMPLES)}

    def find_next_file(self, path_pattern):
        # Mock implementation
        return "mock_recording.wav"

class AudioProcessor(AudioData):
    def __init__(self, events, device='loopin'):
        self.events   = events
        self.recorder = pyaudio.PyAudio()
        self.audio_available = False
        self.find_device_index(device)
        self.recordingState = False
        AudioData.__init__(self)
        self.silence    = WindowAve(SILENCESAMPLES)
        self.window     = np.kaiser(FRAME, WINDOW)
        
        device_name = self.recorder.get_device_info_by_index(self.device)['name'] if self.device != -1 else "Default"
        print(f"AudioProcessor.__init__> ready and reading from soundcard {device_name}")
        
        self.audio_queue = Queue(maxsize=AUDIO_QUEUE_MAXSIZE)

    def find_device_index(self, device):
        p = self.recorder
        self.device = -1
        # Try to find the specified device
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0 and device.lower() in info['name'].lower():
                self.device = i
                print(f"  Found target device: {info['name']} at index {i}")
                return
        
        # Fallback to default input
        try:
            self.device = p.get_default_input_device_info()['index']
            print(f"  Could not find '{device}'. Defaulting to input device index {self.device}")
        except Exception as e:
            print(f"  ERROR: Could not find any suitable input device: {e}")
            self.device = -1

    def start_capture(self):
        if self.device == -1:
            print("AudioProcessor.start_capture> No input device available. Skipping capture.")
            return

        try:
            # FRAME is used as frames_per_buffer (1024), not FRAMESIZE (2048)
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
        except Exception as e:
            print(f"AudioProcessor.Stop_capture> error: {e}")

    def callback(self, in_data, frame_count, time_info, status):
        if status & pyaudio.paInputOverflow:
            print(f"AudioProcessor.callback> *** [FRAME DROPPED] *** queue size {self.audio_queue.qsize()}")
        try:
            data = np.frombuffer(in_data, dtype=np.int16)
            if not self.audio_queue.full():
                self.audio_queue.put_nowait(data)
        except Exception as e:
            # print(f"AudioProcessor.callback> exception {e}")
            pass
        return (None, pyaudio.paContinue)

    def process_audio_frame(self):
        """Pulls a frame from the queue and processes it."""
        if not self.audio_queue.empty():
            data = self.audio_queue.get_nowait()
            
            # 1. Split/Reshape Samples
            self.samples['left']  = data[0::2]
            self.samples['right'] = data[1::2]
            # Mono conversion
            self.samples['mono']  = np.mean(data.reshape(len(data)//CHANNELS, CHANNELS) ,axis=1) 
            
            # 2. Run VU processing
            vu_left  = self.VU('left')
            vu_right = self.VU('right')
            vu_mono  = self.VU('mono')

            # 3. Apply smoothing and update final VU value
            self.vu['left']  = self.vuwindow['left'].average(vu_left)
            self.vu['right'] = self.vuwindow['right'].average(vu_right)
            self.vu['mono']  = self.vuwindow['mono'].average(vu_mono)
            
            # Clamp the output value to ensure it stays between 0 and 1
            for key in self.vu:
                self.vu[key] = max(0.0, min(1.0, self.vu[key]))

            self.audio_available = True 
        return self.audio_available

    def record(self, data):
        pass # Mocked

    def VU(self, channel):
        # Calculate RMS
        normalized_data = self.samples[channel] / maxValue
        rms = np.sqrt(np.mean(np.square(normalized_data)))
        
        if np.isnan(rms): rms = 0.0

        # FIX: Scaling factor adjusted from 1/VUGAIN (1/0.06=16.6) to 1.4 for better
        # visual responsiveness after smoothing. 16.6 is too volatile. 
        return min(1.0, rms * 1.4) 

# --- End of AudioProcessor classes ---


# -------- Configuration --------
# Physical Screen/Viewport Resolution (Portrait)
WIDTH, HEIGHT = 400, 1280
# Content Resolution (Desired render target for the visualizer content - Landscape)
CONTENT_WIDTH, CONTENT_HEIGHT = 1280, 400
FPS = 60
# --------------------------------

# --- VERTEX SHADER: Handles 90-degree Rotation ---
VERTEX_SHADER = """#version 130
in vec2 a_pos;
out vec2 v_uv;

void main() {
    // 90-degree Clockwise rotation: (x, y) -> (y, -x).
    vec2 rotated_pos = vec2(a_pos.y, -a_pos.x);
    gl_Position = vec4(rotated_pos, 0.0, 1.0);
    // v_uv.x is the long dimension (1280), v_uv.y is the short dimension (400).
    v_uv = a_pos * 0.5 + 0.5;
}
"""

# --- FRAGMENT SHADER: VU Meter Visuals (FIXED) ---
FRAGMENT_SHADER_VU = """#version 130
out vec4 outColor;
uniform float time;
uniform vec2 resolution; // (1280, 400)
in vec2 v_uv;
uniform float vu_level; // New uniform: 0.0 to 1.0

const float PI = 3.14159265359;

// Draw a line segment
float line(vec2 p, vec2 a, vec2 b, float width) {
    vec2 pa = p - a;
    vec2 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return smoothstep(1.0, 0.0, length(pa - ba * h) / width);
}

void main() {
    // uv represents the normalized coordinate of the 1280x400 content space.
    vec2 uv = v_uv;
    vec3 color = vec3(0.0);

    // 1. Setup Coordinates for the Meter Dial
    // Center of the dial in content space (e.g., x=320, y=200)
    // dial_center is normalized to UV (0-1) space: (320/1280, 200/400) = (0.25, 0.5)
    vec2 dial_center = vec2(resolution.y * 0.8 / resolution.x, 0.5); 
    
    // p is the coordinate relative to the dial center
    vec2 p = uv - dial_center;
    
    // Aspect Correction: make the visual elements correctly proportioned.
    // 1280 / 400 = 3.2. This scales p.x down to match p.y's aspect.
    p.x *= resolution.x / resolution.y; 

    // Outer radius of the entire meter area
    float radius = 0.45;
    float dist = length(p);

    // Background dial color
    float dial_mask = smoothstep(radius, radius - 0.02, dist);
    color = mix(color, vec3(0.07, 0.09, 0.19), dial_mask); // Dark background

    // 2. VU Meter Scale/Arc
    // Full scale deflection range (e.g., 180 degrees)
    float min_angle = PI * 0.75; // 135 degrees (VU = 0.0)
    float max_angle = PI * 0.25; // 45 degrees (VU = 1.0)
    float dial_radius = 0.4;
    
    // Draw the arc line (Arc drawing remains for visual reference)
    float arc_line = smoothstep(dial_radius, dial_radius - 0.005, dist) * smoothstep(dial_radius - 0.02, dial_radius - 0.015, dist);
    if (dist < dial_radius) { // Only draw arc inside the radius
        color = mix(color, vec3(0.1, 0.1, 0.3), arc_line * 0.5); // Subtle dark arc
    }
    
    // 3. Draw Needle (FIXED length)
    float needle_length = 0.35; // FIX: Length is 0.35 (shorter than dial_radius 0.4)
    
    // Map the vu_level (0 to 1.0) to an angle (min_angle to max_angle)
    // vu_level=0 -> min_angle. vu_level=1.0 -> max_angle.
    float needle_angle = mix(min_angle, max_angle, clamp(vu_level, 0.0, 1.0));
    
    // Calculate the end point in *relative* coordinates (from dial_center)
    vec2 needle_end_relative = vec2(needle_length * cos(needle_angle), needle_length * sin(needle_angle));
    
    // Start and end points for the needle line segment using *absolute* UV coordinates
    vec2 needle_start = dial_center;
    vec2 needle_end = dial_center + needle_end_relative * vec2(resolution.y / resolution.x, 1.0); // FIX: Scale the needle end back to UV space

    // The line function needs its own un-centered coordinates (0-1) for 'p'
    vec2 p_uncentered = uv;
    float needle_width = 0.003;
    
    // Draw needle line using the absolute UV coordinates
    float needle_mask = line(p_uncentered, dial_center, needle_end, needle_width);
    
    // Draw needle
    vec3 needle_color = vec3(0.8, 0.1, 0.1); // Bright red needle
    color = mix(color, needle_color, needle_mask);

    // 4. Center Hub
    float hub_mask = smoothstep(0.05, 0.0, dist);
    color = mix(color, vec3(0.3), hub_mask);

    outColor = vec4(color, 1.0);
}
"""


# --------- GL helper functions ----------
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
    # Fullscreen quad positions (NDC: Normalized Device Coordinates)
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

    # --- 2. Pygame/GL Setup ---
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    surface = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("VU Meter Demo")

    prog = link_program(VERTEX_SHADER, FRAGMENT_SHADER_VU)
    glUseProgram(prog)

    # Get uniform locations
    time_loc = glGetUniformLocation(prog, "time")
    res_loc = glGetUniformLocation(prog, "resolution")
    vu_loc = glGetUniformLocation(prog, "vu_level")

    # Prepare VBO
    vbo = make_fullscreen_quad_vao()
    a_pos = glGetAttribLocation(prog, "a_pos")
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glEnableVertexAttribArray(a_pos)
    glVertexAttribPointer(a_pos, 2, GL_FLOAT, GL_FALSE, 0, None)

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)

    clock = pygame.time.Clock()
    running = True
    start_time = time.time()
    
    current_vu = 0.0
    
    print("\nStarting visualizer. Make sure audio is playing into the selected input device.")

    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for evt in pygame.event.get():
            if evt.type == QUIT or (evt.type == KEYDOWN and evt.key == K_ESCAPE):
                running = False

        # --- 3. Audio Processing Update ---
        audio_proc.process_audio_frame()
        current_vu = audio_proc.vu['mono']
        
        # --- 4. Render Frame ---
        now = time.time() - start_time
        glUseProgram(prog)

        # Set uniforms
        glUniform2f(res_loc, float(CONTENT_WIDTH), float(CONTENT_HEIGHT))
        glUniform1f(time_loc, now)
        glUniform1f(vu_loc, current_vu) # Pass the current VU level

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        pygame.display.flip()
        
        # print(f"VU: {current_vu:.4f}") # Uncomment to debug VU level

    # --- 5. Cleanup ---
    audio_proc.stop_capture()
    glDeleteBuffers(1, [vbo])
    glDeleteProgram(prog)
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()