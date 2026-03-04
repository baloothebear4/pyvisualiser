'''
Mar 26. Baloothebear4 v1

Collating all the classes that hold the styles of how visualisers work enables:
- standardisation & consistency
- use of presets
- the ability to careful curate themes or overall profiles for finished visualisers

'''


class Effects:
    def __init__(self, threshold=0.75, scale=2.5, blur=1.0, alpha=150, attack=0.4, decay=0.1, power=2.0):
        self.threshold = threshold
        self.scale     = scale
        self.blur      = blur
        self.alpha     = alpha
        self.attack    = attack
        self.decay     = decay
        self.power     = power



class BarStyle:
    def __init__(self, led_h=10, led_gap=4, peak_h=1, right_offset=0, flip=False, radius=0, tip=False, orient='vert', col_mode=None, segment_size=None, segment_gap=None, corner_radius=None, edge_softness=0.0):
        self.segment_size = segment_size if segment_size is not None else led_h
        self.segment_gap  = segment_gap  if segment_gap  is not None else led_gap
        self.corner_radius = corner_radius if corner_radius is not None else radius
        self.peak_h     = peak_h
        self.right_offset = right_offset
        self.flip       = flip
        self.orient     = orient
        self.col_mode   = col_mode if col_mode is not None else orient
        self.tip        = tip
        self.edge_softness = edge_softness


class SpectrumStyle:
    def __init__(self, bar_space=0.5, barw_min=1, barw_max=20):
        self.bar_space = bar_space
        self.barw_min  = barw_min
        self.barw_max  = barw_max