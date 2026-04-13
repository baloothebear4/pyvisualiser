"""
Advanced Visualiser Frames
High-fidelity visualization components with 3D effects, particle systems, and dynamic geometry.
"""
from   pyvisualiser.core.framecore import Frame
import math, random, numpy as np
# import pygame

class EchoWaveFrame(Frame):
    """
    3D effect where waves of amplitude traverse the screen and look like echos 
    going behind them.
    """
    @property
    def type(self): return 'Visualiser'

    def __init__(self, parent, channel='mono', history_size=40, decay=0.95, 
                 perspective_scale=0.98, y_step=8, x_step=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.channel = channel
        self.history_size = history_size
        self.decay = decay
        self.perspective_scale = perspective_scale
        self.y_step = y_step
        self.x_step = x_step
        self.wave_history = []  # Stores list of waveform_data

    def update_history(self, waveform):
        """Updates the wave history buffer."""
        # Ensure we have a valid waveform list/array
        if waveform is None or len(waveform) == 0 or self.w <= 0:
            return
            
        # Downsample waveform to match screen width roughly if it's huge
        step = max(1, len(waveform) // self.w)
        reduced_wave = waveform[::step]
        
        self.wave_history.insert(0, reduced_wave)
        if len(self.wave_history) > self.history_size:
            self.wave_history.pop()

    def update_screen(self):
        # Get raw samples (int16)
        waveform = self.platform.samples[self.channel]
        self.update_history(waveform)
        
        self.draw_background(True)

        max_amp = 32768.0
        
        # Baseline is at the bottom of the frame
        rect = self.abs_rect()
        bottom_y = rect[1] + rect[3]
        start_x = rect[0]
        
        # Iterate backwards to draw from far to near
        for i, wave in reversed(list(enumerate(self.wave_history))):
            scale = self.perspective_scale ** i
            
            # Canted effect: Shift right and up as we go back in history
            x_offset = self.x_step * i
            y_offset = self.y_step * i 
            
            # Calculate alpha decay
            alpha = 255 * (self.decay ** i)
            if alpha < 10: continue
            
            # Colour gradient based on depth (i)
            col_idx = (1.0 - (i / self.history_size)) * self.colours.num_colours
            rgb = self.colours.get(col_idx)
            colour = list(rgb[:3]) + [int(alpha)]

            points = []
            x_step = self.w / (len(wave) or 1)
            
            for idx, val in enumerate(wave):
                px = start_x + x_offset + (idx * x_step * scale)
                # Draw upwards from the baseline
                norm_val = abs(val) / max_amp # Use absolute value for "hills"
                py = bottom_y - y_offset - (norm_val * (self.h * 0.6) * scale)
                points.append((px, py))

            if len(points) > 1:
                # Use a slightly thicker, softer line for the "neon" look
                self.platform.renderer.draw_lines(colour, False, points, width=1, softness=0.0)
        
        return True


class KaleidoscopeFrame(Frame):
    """
    A glowing, shader-like starburst mirrored 4 times in a kaleidoscope pattern.
    """
    @property
    def type(self): return 'Visualiser'

    def __init__(self, parent, channel='mono', min_tentacles=5, max_tentacles=20, 
                 base_radius=5, sensitivity=1.2, **kwargs):
        super().__init__(parent, **kwargs)
        self.channel = channel
        # Tentacle count is for one quadrant, which will be mirrored 4 times
        self.min_tentacles = min_tentacles
        self.max_tentacles = max_tentacles
        self.base_radius = base_radius
        self.sensitivity = sensitivity
        self.current_tentacles = []

    def calculate_tentacles(self, fft_data, bass_energy):
        """
        Maps FFT bins to ray geometry for a single 90-degree quadrant.
        """
        # Number of tentacles based on bass energy
        num_tentacles = int(self.min_tentacles + (self.max_tentacles - self.min_tentacles) * bass_energy)
        num_tentacles = max(self.min_tentacles, min(self.max_tentacles, num_tentacles))
        
        if num_tentacles < 2: return []

        tentacles = []
        # Confine tentacles to the first quadrant (0 to PI/2)
        angle_step = (math.pi / 2) / (num_tentacles or 1)
        
        # Map FFT bins to tentacles
        fft_bins_per_tentacle = len(fft_data) // num_tentacles
        if fft_bins_per_tentacle == 0: fft_bins_per_tentacle = 1

        for i in range(num_tentacles):
            angle = i * angle_step
            
            start_bin = i * fft_bins_per_tentacle
            end_bin = start_bin + fft_bins_per_tentacle
            energy = np.mean(fft_data[start_bin:end_bin]) if end_bin > start_bin else 0
            
            length = self.base_radius + energy * self.h * self.sensitivity
            width = 2 + (energy * 15)
            
            tentacles.append({'angle': angle, 'length': length, 'width': width, 'energy': energy})
            
        return tentacles

    def update_screen(self):
        fft_data = self.platform.bins[self.channel]
        
        # Calculate bass energy (approx first 10% of bins)
        bass_cut = max(1, len(fft_data) // 10)
        bass_energy = np.mean(fft_data[:bass_cut]) if len(fft_data) > 0 else 0
        
        self.current_tentacles = self.calculate_tentacles(fft_data, bass_energy)
        
        # self.draw_background(True)
        
        base_colour = self.colours.get('foreground')
        cx, cy = self.abs_centre()
        
        # Draw star as a series of closed shapes or lines
        for tentacle in self.current_tentacles:
            intensity = min(1.0, 0.2 + tentacle['energy'] * 5)
            alpha = int(255 * intensity)
            colour = list(base_colour[:3]) + [alpha]
            
            original_angle = tentacle['angle']
            
            # Create 4 reflections for a kaleidoscope effect
            # Q1: (x, y), Q2: (-x, y), Q3: (-x, -y), Q4: (x, -y)
            angles = [
                original_angle,             # Q1
                math.pi - original_angle,   # Q2 (reflection across Y axis)
                original_angle + math.pi,   # Q3 (reflection across origin)
                (2 * math.pi) - original_angle, # Q4 (reflection across X axis)
            ]
            
            for angle in angles:
                reflected_tentacle = tentacle.copy()
                reflected_tentacle['angle'] = angle
                p1, p2, p3, p4 = self._get_tentacle_poly(reflected_tentacle, cx, cy)
                self.platform.renderer.draw_lines(colour, True, [p1, p2, p3, p4], width=1)
            
        return True

    def _get_tentacle_poly(self, tentacle, cx, cy):
        angle, length, width = tentacle['angle'], tentacle['length'], tentacle['width']
        # To avoid division by zero if length is tiny
        width_angle = math.atan(width / length) if length > 0 else 0

        p1 = (cx + self.base_radius * math.cos(angle - width_angle),
              cy + self.base_radius * math.sin(angle - width_angle))
        p2 = (cx + self.base_radius * math.cos(angle + width_angle),
              cy + self.base_radius * math.sin(angle + width_angle))
        p3 = (cx + length * math.cos(angle + width_angle),
              cy + length * math.sin(angle + width_angle))
        p4 = (cx + length * math.cos(angle - width_angle),
              cy + length * math.sin(angle - width_angle))
        return p1, p2, p3, p4


class PulseOrbFrame(Frame):
    """
    Colourful turning ball pulsing growing and shrinking with pulses or dots coming off.
    """
    @property
    def type(self): return 'Visualiser'

    def __init__(self, parent, channel='mono', particle_limit=100, spin_speed=0.03, 
                 pulse_scale=1.2, particle_decay=0.04, **kwargs):
        super().__init__(parent, **kwargs)
        self.channel = channel
        self.particle_limit = particle_limit
        self.spin_speed = spin_speed
        self.pulse_scale = pulse_scale
        self.particle_decay = particle_decay
        self.particles = [] # list of dicts: {'pos': [x,y], 'vel': [vx,vy], 'life': 1.0}
        self.hue_offset = 0.0
        self.angle = 0.0
        self.smoothing_amp =0.0

    def update_physics(self, amplitude, peak, current_radius, cx, cy, col_idx):
        """Updates orb rotation and particle system."""
        self.angle += self.spin_speed
        self.hue_offset = (self.hue_offset + 0.5) % self.colours.num_colours
        if self.angle > math.pi * 2:
            self.angle -= math.pi * 2
            
        # Particle emission logic based on peaks (and amplitude for continuous flow)
        if peak > 0.6 or amplitude > 0.7: 
            self._emit_particles(amount=int(amplitude * 5), radius=current_radius, cx=cx, cy=cy, col_idx=col_idx)
            
        self._update_particles()

    def _emit_particles(self, amount, radius, cx, cy, col_idx):
        for _ in range(amount):
            if len(self.particles) < self.particle_limit:
                emit_angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 5)
                
                pos_x = cx + radius * math.cos(emit_angle)
                pos_y = cy + radius * math.sin(emit_angle)
                
                vel = [math.cos(emit_angle) * speed, math.sin(emit_angle) * speed]
                
                self.particles.append({'pos': [pos_x, pos_y], 'vel': vel, 'life': 1.0, 'col_idx': col_idx})

    def _update_particles(self):
        new_particles = []
        for p in self.particles:
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['vel'][1] += 0.2 # Gravity
            p['life'] -= self.particle_decay
            if p['life'] > 0:
                new_particles.append(p)
        self.particles = new_particles

    def update_screen(self):
        amplitude = self.platform.vu[self.channel]
        peak = self.platform.peak.get(self.channel, amplitude)
        self.smoothing_amp = (self.smoothing_amp * 0.9) + (amplitude * 0.1)
        
        # Smaller base radius
        base_radius = min(self.w, self.h) // 12
        pulse_radius = base_radius + (amplitude * self.pulse_scale * base_radius)
        
        # Dynamic colour based on amplitude + time cycling
        orb_col_idx = ( (self.smoothing_amp**2) * self.colours.num_colours + self.hue_offset) % self.colours.num_colours
        
        cx, cy = self.abs_centre()
        self.update_physics(amplitude, peak, pulse_radius, cx, cy, orb_col_idx)
        
        # self.draw_background(True)

        colour_core = list(self.colours.get(orb_col_idx)[:3]) + [255]
        colour_glow = list(self.colours.get(orb_col_idx)[:3]) + [100]
        colour_white = (255, 255, 255, 255)
        
        # Draw Orb Glow (Large, Soft)
        glow_size = pulse_radius * 3
        glow_rect = (cx - glow_size/2, cy - glow_size/2, glow_size, glow_size)
        self.platform.renderer.draw_rect(colour_glow, glow_rect, border_radius=glow_size/2, softness=0.8)
        
        # Draw Orb Core (Small, Harder)
        orb_size = pulse_radius * 2
        orb_rect = (cx - pulse_radius, cy - pulse_radius, orb_size, orb_size)
        self.platform.renderer.draw_rect(colour_core, orb_rect, border_radius=orb_size/2, softness=0.2)
        
        # Draw Inner Nucleus (White, pulsing)
        nuc_size = pulse_radius * 0.8
        nuc_rect = (cx - nuc_size/2, cy - nuc_size/2, nuc_size, nuc_size)
        self.platform.renderer.draw_rect(colour_white, nuc_rect, border_radius=nuc_size/2, softness=0.4)
        
        # Draw Particles
        for p in self.particles:
            life = p['life']
            # Particles use their birth color
            p_rgb = self.colours.get(p['col_idx'])
            p_colour = list(p_rgb[:3]) + [int(255 * life)]
            p_size = int(life * 4)
            if p_size > 0:
                p_rect = (p['pos'][0] - p_size/2, p['pos'][1] - p_size/2, p_size, p_size)
                self.platform.renderer.draw_rect(p_colour, p_rect, border_radius=p_size/2, softness=0.5)
                
        return True


class SpectrumWaveFrame(Frame):
    """
    3D effect where waves of spectrum data traverse the screen, similar to EchoWave.
    """
    @property
    def type(self): return 'Visualiser'

    def __init__(self, parent, channel='mono', history_size=30, decay=0.95, 
                 perspective_scale=0.98, y_step=8, x_step=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.channel = channel
        self.history_size = history_size
        self.decay = decay
        self.perspective_scale = perspective_scale
        self.y_step = y_step
        self.x_step = x_step
        self.wave_history = []
        self.bar_freqs = []
        self._calculate_bar_freqs()

    def _calculate_bar_freqs(self):
        """Calculates spectrum band frequencies based on frame width."""
        # This logic is borrowed from the Spectrum class in frames.py
        for spacing in (48, 24, 12, 6, 3, 2, 1):
            self.bar_freqs = self.platform.createBands(spacing, flast=self.platform.w * 10)
            if len(self.bar_freqs) <= self.w:
                break

    def update_history(self, spectrum_data):
        """Updates the spectrum history buffer."""
        if spectrum_data is None or len(spectrum_data) == 0:
            return
        
        self.wave_history.insert(0, spectrum_data)
        if len(self.wave_history) > self.history_size:
            self.wave_history.pop()

    def update_screen(self):
        # Recalculate if width has changed
        if len(self.bar_freqs) > self.w * 1.2 or len(self.bar_freqs) < self.w / 2:
            self._calculate_bar_freqs()

        spectrum_data = self.platform.packFFT(self.bar_freqs, self.channel)
        self.update_history(spectrum_data)
        
        # self.draw_background(True)

        rect = self.abs_rect()
        bottom_y = rect[1] + rect[3]
        start_x = rect[0]
        
        for i, wave in reversed(list(enumerate(self.wave_history))):
            scale = self.perspective_scale ** i
            x_offset = self.x_step * i
            y_offset = self.y_step * i 
            
            alpha = 255 * (self.decay ** i)
            if alpha < 10: continue
            
            col_idx = (1.0 - (i / self.history_size)) * self.colours.num_colours
            rgb = self.colours.get(col_idx)
            colour = list(rgb[:3]) + [int(alpha)]

            points = []
            x_step = self.w / (len(wave) or 1)
            
            for idx, val in enumerate(wave):
                px = start_x + x_offset + (idx * x_step * scale)
                py = bottom_y - y_offset - (val * (self.h * 0.8) * scale)
                points.append((px, py))

            if len(points) > 1:
                self.platform.renderer.draw_lines(colour, False, points, width=1, softness=0.0)
        
        return True


class FreqWaveFrame(Frame):
    """
    Scrolling time-series display (Oscilloscope/Roll mode).
    New data appears on the right and scrolls left.
    Supports 'rms' (single line) or 'spectrum' (multiple lines).
    """
    @property
    def type(self): return 'Visualiser'

    def __init__(self, parent, channel='mono', mode='rms', num_bands=5, 
                 speed=2, line_width=2, y_step=0, perspective_scale=1.0, **kwargs):
        super().__init__(parent, **kwargs)
        self.channel = channel
        self.mode = mode
        self.num_bands = num_bands
        self.speed = speed
        self.line_width = line_width
        self.y_step = y_step
        self.perspective_scale = perspective_scale
        self.history = []
        self.bar_freqs = []

    def _get_spectrum_data(self):
        # Initialize bands if needed
        if not self.bar_freqs:
            # Try to find a spacing that gives us at least num_bands
            for spacing in (12, 6, 3, 2, 1):
                freqs = self.platform.createBands(spacing)
                if len(freqs) >= self.num_bands:
                    self.bar_freqs = freqs
                    break
            if not self.bar_freqs:
                self.bar_freqs = self.platform.createBands(1)

        data = self.platform.packFFT(self.bar_freqs, self.channel)
        
        # Resample/Select bands to match num_bands
        if len(data) < self.num_bands:
            return data # Return what we have
        
        # Pick evenly spaced bands
        result = []
        if self.num_bands == 1:
             result.append(data[0])
        else:
            step = (len(data) - 1) / (self.num_bands - 1)
            for i in range(self.num_bands):
                idx = int(i * step)
                result.append(data[idx])
        return result

    def update_screen(self):
        # 1. Get Data
        if self.mode == 'rms':
            val = self.platform.vu[self.channel]
            current_data = [val]
        else:
            current_data = self._get_spectrum_data()

        # 2. Update History
        self.history.append(current_data)
        
        # Prune history (keep enough to fill width)
        if self.w <= 0: return False
        max_items = int(self.w / self.speed) + 2
        if len(self.history) > max_items:
            self.history = self.history[-max_items:]

        # self.draw_background(True)

        if len(self.history) < 2: return True

        # 3. Draw Lines
        rect = self.abs_rect()
        right_x = rect[0] + rect[2]
        bottom_y = rect[1] + rect[3]
        h = rect[3]
        
        num_lines = len(self.history[0])
        
        for line_idx in range(num_lines):
            points = []
            
            # Determine Color
            if self.mode == 'rms':
                colour = self.colours.get('light')
            else:
                # Gradient for spectrum bands
                col_idx = (line_idx / (num_lines or 1)) * self.colours.num_colours
                colour = self.colours.get(col_idx)

            # Build Polyline
            for i, data_snapshot in enumerate(reversed(self.history)):
                val = data_snapshot[line_idx]
                scale = self.perspective_scale ** i
                x = right_x - (i * self.speed)
                y = bottom_y - (i * self.y_step) - (val * h * 0.9 * scale) # 90% height usage
                points.append((x, y))
                
                if x < rect[0]: break
            
            if len(points) > 1:
                self.platform.renderer.draw_lines(colour, False, points, width=self.line_width)

        return True