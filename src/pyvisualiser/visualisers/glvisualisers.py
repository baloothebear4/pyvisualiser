"""
Kaleidoscope Visualiser Frame
"""
from pyvisualiser.core.glwrapper import GLSLFrame
import numpy as np
import moderngl
import time

def perspective_matrix(fovy, aspect, near, far):
    """Creates a row-major perspective projection matrix."""
    f = 1.0 / np.tan(np.radians(fovy) / 2.0)
    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0]
    ], dtype='f4')

def look_at_matrix(eye, target, up):
    """Creates a row-major look-at view matrix."""
    eye = np.array(eye, dtype='f4')
    target = np.array(target, dtype='f4')
    up = np.array(up, dtype='f4')

    z = eye - target
    z /= np.linalg.norm(z)
    x = np.cross(up, z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)

    return np.array([
        [x[0], y[0], z[0], 0],
        [x[1], y[1], z[1], 0],
        [x[2], y[2], z[2], 0],
        [-np.dot(x, eye), -np.dot(y, eye), -np.dot(z, eye), 1]
    ], dtype='f4')

class Kalidoscope(GLSLFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, "kalidoscope", **kwargs)

    def update_uniforms(self):
        super().update_uniforms()
        if not self.prog: return

        # 1. Map Volume (VU)
        vu = 0.2
        if hasattr(self.platform, 'vu'):
            vu = self.platform.vu['mono']
        
        if 'u_vu' in self.prog:
            self.prog['u_vu'].value = float(vu)
            
        # 2. Map Bass Frequency Energy
        # Calculate average of lower bins
        bass = 0.0
        if hasattr(self.platform, 'bins'):
            bins = self.platform.bins['mono']
            # Assuming ~512 bins, take a slice of low-mid frequencies
            if len(bins) > 20:
                # Bins 2 to 15 usually contain punchy bass info
                bass = np.mean(bins[2:15])
        
        if 'u_bass' in self.prog:
            self.prog['u_bass'].value = float(bass)

class SpectrumMesh(GLSLFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, "spectrum_mesh", **kwargs)
        self.render_mode = moderngl.LINES
        self.grid_res = (128, 64) # X, Z resolution
        self.spectrum_texture = None
        self.strength_multiplier = 1.0

    def create_geometry(self):
        """Creates a 2D grid and an index buffer for drawing lines."""
        # 1. Create Vertices for a plane
        x = np.linspace(-1.0, 1.0, self.grid_res[0])
        z = np.linspace(-1.0, 1.0, self.grid_res[1])
        xv, zv = np.meshgrid(x, z)
        
        vertices = np.dstack([xv, zv]).astype('f4').ravel()
        
        # 2. Create Indices for line segments
        indices = []
        for i in range(self.grid_res[1]): # For each row
            for j in range(self.grid_res[0]): # For each column
                idx = i * self.grid_res[0] + j
                if j < self.grid_res[0] - 1:
                    indices.extend([idx, idx + 1]) # Horizontal line
                if i < self.grid_res[1] - 1:
                    indices.extend([idx, idx + self.grid_res[0]]) # Vertical line

        indices = np.array(indices, dtype='i4')

        # 3. Create VBO, IBO and VAO
        self.vbo = self.ctx.buffer(vertices)
        self.ibo = self.ctx.buffer(indices)
        
        return self.ctx.vertex_array(self.prog, [(self.vbo, '2f', 'in_vert')], self.ibo)

    def update_uniforms(self):
        super().update_uniforms()
        if not self.prog: return

        # 1. Update Spectrum Texture from FFT bins
        if hasattr(self.platform, 'bins'):
            bins = self.platform.bins['mono']
            if len(bins) > 1:
                # Resample FFT data to match grid's X resolution
                x_orig = np.linspace(0, 1, len(bins))
                x_new = np.linspace(0, 1, self.grid_res[0])
                spectrum_data = np.interp(x_new, x_orig, bins).astype('f4')
                
                if self.spectrum_texture is None:
                    self.spectrum_texture = self.ctx.texture((self.grid_res[0], 1), 1, spectrum_data.tobytes(), dtype='f4')
                else:
                    self.spectrum_texture.write(spectrum_data.tobytes())
                
                self.spectrum_texture.use(location=0)
                if 'u_spectrum' in self.prog:
                    self.prog['u_spectrum'].value = 0

        # 2. Calculate and update Model-View-Projection matrix
        proj = perspective_matrix(45.0, self.w / max(1, self.h), 0.1, 100.0)
        
        t = time.time() - self.start_time
        # Slower orbit, lower camera position, and less 'bobbing'
        eye_pos = (np.sin(t * 0.05) * 3.0, 1.0 + np.sin(t * 0.1) * 0.2, np.cos(t * 0.05) * 3.0)
        # Lower the target Y to move the mesh down in the frame
        view = look_at_matrix(eye=eye_pos, target=(0.0, -0.5, 0.0), up=(0.0, 1.0, 0.0))
        
        mvp = proj @ view

        if 'u_mvp' in self.prog:
            self.prog['u_mvp'].value = tuple(mvp.T.flatten())

        if 'u_strength' in self.prog:
            vu = self.platform.vu.get('mono', 0.5)
            # Reduced base strength and VU multiplier for less sensitivity
            base_strength = 0.05 + vu * 0.5
            self.prog['u_strength'].value = base_strength * self.strength_multiplier

SHADERS = ["baltro", "cloudflight", "discosun", "kalidoscope", "pinkball", "spiralclouds", "warping"]
ANALYSIS_METADATA = ["beat", "bpm","centroid", "kurtosis","flux","volume"]

class GLshader(GLSLFrame):
    def __init__(self, parent, shader="baltro", **kwargs):
        super().__init__(parent, shader, **kwargs)

    def update_uniforms(self):
        super().update_uniforms()
        if not self.prog: return

        # 1. Map Volume (VU)
        vu = 0.2
        if hasattr(self.platform, 'vu'):
            vu = self.platform.vu['mono']
        
        if 'u_vu' in self.prog:
            self.prog['u_vu'].value = float(vu)
            
        # 2. Map Bass Frequency Energy
        # Calculate average of lower bins
        bass = self.platform.bass * 15
        
        if 'u_bass' in self.prog:
            self.prog['u_bass'].value = float(bass)

        # 4. Map the audio analysis metadata
        if hasattr(self.platform, 'audioanalysis'):
            for m in ANALYSIS_METADATA:
                key = f"u_{m}"
                if key in self.prog:
                    value = self.platform.audioanalysis.get(m, 0.0)
                    # Handle boolean 'beat' uniform which expects an int/bool
                    if isinstance(value, bool):
                        self.prog[key].value = int(value)
                    else:
                        self.prog[key].value = float(value)

        # print(f"Bass: {bass}"), print(f"VU: {vu}", print(f"BPM: {bpm}"))
        # print(f"BPM: {bpm}"), print(f"Bass: {bass}"), print(f"treble: {self.platform.treble}")