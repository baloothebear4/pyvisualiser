

""" Old preamp classes that need refactoring """
class VolumeSourceFrame(Frame):
    """
        Displays the volume as a percentage with the source underneath
        - has a width determined by the scale
    """
    def __init__(self, parent, scale, align=('right','top')):
        Frame.__init__(self, display.boundary, platform, (scale,1.0), 'middle', Halign=align)
        self += VolumeTextFrame(self, "top", 0.7, "22")        # this are the widest number
        self += SourceTextFrame(self, 'bottom', 0.3, self.platform.longestSourceText) # this are the widest source text
        # self += OutlineFrame(self, display)
        self.check()

    @property
    def width(self):
        return

class RecordFrame(Frame):
    """
        Displays the volume as a percentage with the source underneath
        - has a width determined by the scale
    """
    def __init__(self, parent, scale):
        Frame.__init__(self, display.boundary, platform, (scale,1.0), 'middle', 'left')
        self +=  TextFrame( display.boundary, platform, 'middle', 1.0, 'Recording', X=0.6, align=('left','middle'))
        # self += OutlineFrame(self, display)
        self.check()

    @property
    def width(self):
        return




class dbVolumeSourceFrame(Frame):
    """
        Displays the volume as a percentage with the source underneath
        - has a width determined by the scale
    """
    def __init__(self, parent, scale, align=('right','top')):
        Frame.__init__(self, display.boundary, platform, scalers=scalers(scale, 1.0), align=align)
        self += dbVolumeTextFrame(self, align=('right','top'), Y=0.7, text='-64.0dB')        # this are the widest number
        self += SourceTextFrame(self, align=('left','bottom'), Y=0.3, text=self.platform.longestSourceText) # this are the widest source text
        # self += OutlineFrame(self, display)
        self.check()

    @property
    def width(self):
        return

class VolumeAmountFrame(Frame):
    """
        Displays a triangle filled proportional to the Volume level
    """
    def __init__(self, parent, scale):
        Frame.__init__(self, parent, scalers=scalers(scale,0.5), align=('left', 'middle'))

    def draw(self, basis):

        self.display.drawFrameTriange( basis, self, 1.0, fill="red" )
        vol = self.platform.volume
        self.display.drawFrameTriange( basis, self, vol, fill="white" )


class VolumeTextFrame(TextFrame):
    def draw(self, basis):
        if self.platform.muteState:
            vol = 0
        else:
            vol = self.platform.volume * 100

        self.display.drawFrameCentredText(basis, self, "%2d" % vol, self.font)

class SourceTextFrame(TextFrame):
    def draw(self, basis):
        self.display.drawFrameCentredText(basis, self, self.platform.activeSourceText, self.font)

class dbVolumeTextFrame(TextFrame):
    def draw(self, basis):
        if self.platform.muteState:
            text = "Mute"
        else:
            text = "%3.1fdB" % self.platform.volume_db
        self.display.drawFrameCentredText(basis, self, text, self.font)

class MenuFrame(TextFrame):
    def draw(self, basis):
        text = self.platform.screenName
        self.display.drawFrameCentredText(basis, self, text, self.font)

class RecordEndFrame(TextFrame):
    """
        Displays the file name used to save the recording
        - has a width determined by the scale
    """
    def draw(self, basis):
        (dirname, filename) = os.path.split(self.platform.recordfile)
        self.display.drawFrameCentredText(basis, self, filename, self.font)
