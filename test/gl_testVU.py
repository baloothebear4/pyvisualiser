# stereo_vu_meter_gl.py
# Dual Analogue VU Meters (Left/Right) driven by AudioProcessor
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

# --- Configuration ---
# Target Audio Device
AUDIO_DEVICE_NAME = 'loopin' 

# Mock Events class 
class Events:
    def Audio(self, event_name):
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
VUSAMPLES       = 0.25 / SAMPLEPERIOD
AUDIO_QUEUE_MAXSIZE = 10
# VU Scaling: The user requested a scaling of 10.0. 
# This constant is used as the RMS multiplier for meter sensitivity.
VU_RMS_SCALING  = 10.0 
WINDOW = 12
# --- End of constants ---

# --- Audio Processor Classes (Kept minimal for brevity) ---

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
        self.window = [0.0]*int(self.size) if type == 'silence' else [1.0]*int(self.size)

class AudioData:
    def __init__(self):
        data_s = np.arange(FRAMESIZE)
        self.vu = {'left': 0.0, 'right':0.0, 'mono':0.0}
        self.samples  = {'left': data_s, 'right':data_s, 'mono':data_s}
        self.vuwindow = {'left': WindowAve(VUSAMPLES), 'right': WindowAve(VUSAMPLES), 'mono': WindowAve(VUSAMPLES)}
    def find_next_file(self, path_pattern):
        return "mock_recording.wav"

class AudioProcessor(AudioData):
    def __init__(self, events, device=AUDIO_DEVICE_NAME):
        self.events   = events
        self.recorder = pyaudio.PyAudio()
        self.device = -1 # Initialize device index
        self.find_device_index(device)
        AudioData.__init__(self)
        self.window     = np.kaiser(FRAME, WINDOW)
        self.audio_queue = Queue(maxsize=AUDIO_QUEUE_MAXSIZE)

        device_name = self.recorder.get_device_info_by_index(self.device)['name'] if self.device != -1 else "Default"
        print(f"AudioProcessor.__init__> ready and reading from soundcard: {device_name}")

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
            print("AudioProcessor.start_capture> No input device available. Skipping capture.")
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
        """Pulls a frame from the queue and processes it."""
        if not self.audio_queue.empty():
            data = self.audio_queue.get_nowait()
            
            # 1. Split Samples
            self.samples['left']  = data[0::2]
            self.samples['right'] = data[1::2]
            self.samples['mono']  = np.mean(data.reshape(len(data)//CHANNELS, CHANNELS) ,axis=1) 
            
            # 2. Run VU processing
            vu_left  = self.VU('left')
            vu_right = self.VU('right')

            # 3. Apply smoothing and update final VU value
            self.vu['left']  = self.vuwindow['left'].average(vu_left)
            self.vu['right'] = self.vuwindow['right'].average(vu_right)
            
            # Clamp the output value to ensure it stays between 0 and 1
            self.vu['left'] = max(0.0, min(1.0, self.vu['left']))
            self.vu['right'] = max(0.0, min(1.0, self.vu['right']))
            
            return True
        return False

    def VU(self, channel):
        # Calculate RMS
        normalized_data = self.samples[channel] / maxValue
        rms = np.sqrt(np.mean(np.square(normalized_data)))
        
        if np.isnan(rms): rms = 0.0

        # FIX: Scaling factor set to VU_RMS_SCALING (10.0)
        return min(1.0, rms * VU_RMS_SCALING) 

# --- End of AudioProcessor classes ---

# --- General Configuration ---
WIDTH, HEIGHT = 400, 1280
CONTENT_WIDTH, CONTENT_HEIGHT = 1280, 400
FPS = 60
# -----------------------------

# --- VERTEX SHADER (Rotation remains) ---
VERTEX_SHADER = """#version 130
in vec2 a_pos;
out vec2 v_uv;

void main() {
    vec2 rotated_pos = vec2(a_pos.y, -a_pos.x);
    gl_Position = vec4(rotated_pos, 0.0, 1.0);
    v_uv = a_pos * 0.5 + 0.5;
}
"""

# --- FRAGMENT SHADER: STEREO VU Meter Visuals ---
FRAGMENT_SHADER_STEREO_VU = """#version 130
out vec4 outColor;
uniform vec2 resolution; // (1280, 400)
in vec2 v_uv;
uniform float vu_left;  // Left channel VU (0.0 to 1.0)
uniform float vu_right; // Right channel VU (0.0 to 1.0)

const float PI = 3.14159265359;

// Draw a line segment
float line(vec2 p, vec2 a, vec2 b, float width) {
    vec2 pa = p - a;
    vec2 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return smoothstep(1.0, 0.0, length(pa - ba * h) / width);
}

// Function to draw a single VU meter dial and needle
vec3 draw_vu_meter(vec2 center_uv, float vu_level, float dial_radius, float needle_length) {
    vec2 p = v_uv - center_uv;
    
    // Aspect Correction relative to content resolution
    p.x *= resolution.x / resolution.y; 

    float radius_outer = dial_radius + 0.05;
    float dist = length(p);
    vec3 color = vec3(0.0);

    // Background dial color
    float dial_mask = smoothstep(radius_outer, radius_outer - 0.02, dist);
    color = mix(color, vec3(0.07, 0.09, 0.19), dial_mask); // Dark background

    // VU Meter Scale/Arc constants
    float min_angle = PI * 0.75; // 135 degrees (VU = 0.0)
    float max_angle = PI * 0.25; // 45 degrees (VU = 1.0)

    // Draw the arc line (Arc drawing remains for visual reference)
    float arc_line = smoothstep(dial_radius, dial_radius - 0.005, dist) * smoothstep(dial_radius - 0.02, dial_radius - 0.015, dist);
    if (dist < dial_radius) { 
        color = mix(color, vec3(0.1, 0.1, 0.3), arc_line * 0.5); // Subtle dark arc
    }
    
    // Draw Needle
    float needle_angle = mix(min_angle, max_angle, clamp(vu_level, 0.0, 1.0));
    
    // Calculate the end point in *relative* coordinates (from dial_center)
    vec2 needle_end_relative = vec2(needle_length * cos(needle_angle), needle_length * sin(needle_angle));
    
    // Scale the needle end point back to UV space for the line function
    vec2 needle_end_uv = center_uv + needle_end_relative * vec2(resolution.y / resolution.x, 1.0);

    // Draw needle line using absolute UV coordinates
    float needle_width = 0.003;
    float needle_mask = line(v_uv, center_uv, needle_end_uv, needle_width);
    
    // Draw needle
    vec3 needle_color = vec3(0.8, 0.1, 0.1); // Bright red needle
    color = mix(color, needle_color, needle_mask);

    // Center Hub
    float hub_mask = smoothstep(0.05, 0.0, dist);
    color = mix(color, vec3(0.3), hub_mask);
    
    return color;
}


void main() {
    // Meter 1: Left Channel (Centered at x=0.25, y=0.5)
    vec2 center_left = vec2(0.25, 0.5);
    vec3 color_left = draw_vu_meter(center_left, vu_left, 0.4, 0.35);

    // Meter 2: Right Channel (Centered at x=0.75, y=0.5)
    vec2 center_right = vec2(0.75, 0.5);
    vec3 color_right = draw_vu_meter(center_right, vu_right, 0.4, 0.35);

    // Combine colors: since the meters are far apart, we can just add them.
    // If they overlap, the color will naturally be the result of the mix operations.
    vec3 final_color = color_left + color_right;

    outColor = vec4(final_color, 1.0);
}
"""

# --- GL helper functions (Kept unchanged) ---
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

    # --- 2. Pygame/GL Setup ---
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    surface = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Stereo VU Meter Demo")

    prog = link_program(VERTEX_SHADER, FRAGMENT_SHADER_STEREO_VU)
    glUseProgram(prog)

    # Get uniform locations
    res_loc = glGetUniformLocation(prog, "resolution")
    vu_left_loc = glGetUniformLocation(prog, "vu_left")  # New Left uniform
    vu_right_loc = glGetUniformLocation(prog, "vu_right") # New Right uniform

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
    
    current_vu_left = 0.0
    current_vu_right = 0.0
    
    print("\nStarting visualizer. Monitoring stereo audio input.")

    while running:
        clock.tick(FPS)
        
        for evt in pygame.event.get():
            if evt.type == QUIT or (evt.type == KEYDOWN and evt.key == K_ESCAPE):
                running = False

        # --- 3. Audio Processing Update ---
        audio_proc.process_audio_frame()
        current_vu_left = audio_proc.vu['left']
        current_vu_right = audio_proc.vu['right']
        
        # --- 4. Render Frame ---
        glUseProgram(prog)

        # Set uniforms
        glUniform2f(res_loc, float(CONTENT_WIDTH), float(CONTENT_HEIGHT))
        glUniform1f(vu_left_loc, current_vu_left)   # Pass Left VU
        glUniform1f(vu_right_loc, current_vu_right) # Pass Right VU

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