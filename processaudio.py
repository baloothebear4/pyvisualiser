#!/usr/bin/env python
"""
 preDAC preamplifier project

 Process Audio class
    - provides a full alsaaudio interface
    - maniuplates audio packages
    - does Digital signal processing
    - uses alsaaudio package to control ADC and DAC

 baloothebear4
 v1.0 April 2020
 v1.1 Sept 2022

"""

import  time, math, os
import  numpy as np
from    scipy.fft import rfft
from    scipy.signal import butter, lfilter
import  pyaudio
import  wave
from    events import Events


# constants
CHANNELS        = 2
# INFORMAT        = alsaaudio.PCM_FORMAT_S16_LE
INFORMAT        = pyaudio.paInt16
RATE            = 44100  #33075  # 22050, 24000,
FRAME           = 1024
FRAMESIZE       = FRAME * CHANNELS
CRITICAL_TIME_MS = (FRAME / RATE) * 1000
maxValue        = float(2**15)
SAMPLEPERIOD    = FRAMESIZE/RATE
SMOOTHFACTOR    = 0

SILENCESAMPLES  = 7   / SAMPLEPERIOD  #7 seconds worth of samples
PEAKSAMPLES     = 0.7 / SAMPLEPERIOD  #0.5 seconds worth of VU measurements
VUSAMPLES       = 0.25 / SAMPLEPERIOD  #0.3 seconds is the ANSI VU standard

RECORDSTATE     = False
RECORDTIME      = 30 * 60 / SAMPLEPERIOD / CHANNELS # failfase to stop the disk filling up
RECORDPATH      = "/home/pi/preDAC/rec/"
RECORDFILESUFFIX = "preDAC"
RECORDINGS_PATTERN = RECORDPATH + RECORDFILESUFFIX + "-%s.wav"

WINDOW          = 12 #12 # 4 = Hanning
FIRSTCENTREFREQ = 10 #31.25        # Hz
LASTCENTREFREQ  = RATE // 2
OCTAVE          = 3
NUMPADS         = FRAME
BINBANDWIDTH    = RATE/(FRAME + NUMPADS) #ie 43.5 Hz for 44.1kHz/1024
DCOFFSETSAMPLES = 200
TWOPI           = 2*3.14152

VUGAIN          = 0.06
RMSNOISEFLOOR   = -70    # dB
DYNAMICRANGE    = 50     # Max dB
SILENCETHRESOLD = 0.001   #0.02   # Measured from VU Noise Floor + VU offset

# VU calibration and scaling  DEPRECATED
PeakRange = DYNAMICRANGE - 5 # was 50 antificipated dB range
VURange   = DYNAMICRANGE - 20
PeakOff   = -(RMSNOISEFLOOR + 10) # lower limit to display
VUOff     = -(RMSNOISEFLOOR + 10) # was 40

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

        self.vu       = {'left': 0.5, 'right':0.5, 'mono':0.5}
        self.peak     = {'left': 0.8, 'right':0.8, 'mono':0.8}
        self.vumax    = {'left': 0.01, 'right':0.01, 'mono':0.01}
        self.peakmax  = {'left': 3.9, 'right':3.9, 'mono':3.9}
        self.spectrum = {'left': data, 'right':data, 'mono':data}
        self.bins     = {'left': data, 'right':data, 'mono':data_s}
        self.samples  = {'left': data_s, 'right':data_s, 'mono':data_s}
        self.oldsamples  = {'left': data_s, 'right':data_s, 'mono':data_s}
        self.spectra  = {'left': data_s, 'right':data_s, 'mono':data_s}
        self.signal_detected = False
        self.peakwindow      = {'left': WindowAve(PEAKSAMPLES), 'right': WindowAve(PEAKSAMPLES), 'mono': WindowAve(PEAKSAMPLES)}
        self.vuwindow        = {'left': WindowAve(VUSAMPLES), 'right': WindowAve(VUSAMPLES), 'mono': WindowAve(VUSAMPLES)}
        self.recordfile = self.find_next_file( RECORDINGS_PATTERN )

    def filter(self, signal, fc):
        return signal

    def printPower(self, power, fCentre):
        # apply a frequency dependent filter
        print("%6.1f @f=%-5d %s" % (power, fCentre , "*"*int(self.filter(power, fCentre))))

    def seeData(self, data, title):
        line = "[%d] %s\n" % (len(data), title)
        for i in range(len(data)):
            line += "%6d "%data[i]
            if i % 16 == 15:
                print(line)
                line = ""

    def _print(self):
        self.LR2(self.vu, self.peak)




class AudioProcessor(AudioData):
    def __init__(self, events, device='BlackHole 2ch'):
        self.events   = events
        self.recorder = pyaudio.PyAudio()

        # set up audio input
        self.find_device_index(device)

        self.recordingState = RECORDSTATE
        self.recording      = []
        #self.device = 1

        AudioData.__init__(self)

        self.peakC      = RMSNOISEFLOOR
        self.minC       = maxValue
        self.dc         = []
        self.readtime   = []
        self.silence    = WindowAve(SILENCESAMPLES)
        self.window     = np.kaiser(FRAME + 0, WINDOW)  #Hanning window
        print("AudioProcessor.__init__> ready and reading from soundcard %s, Recording is %s " % (self.recorder.get_default_input_device_info()['name'], RECORDSTATE))

    @property
    def framesize(self):
        return FRAME    

    def find_device_index(self, device):
        print("\nAvailable audio devices:")
        p = self.recorder
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  Device {i}: {info['name']} (inputs: {info['maxInputChannels']})")
    
        try:
            # Get default input device info first
            default_input = p.get_default_input_device_info()
            print(f"Default input device: {default_input['name']}")
            print(f"Max input channels: {default_input['maxInputChannels']}")
            print(f"Default sample rate: {default_input['defaultSampleRate']}")
        
            # Try to find the loopback device
            loopback_device = None
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if device in info['name'].lower():
                    self.device = i
                    print(f"Found loopin device at index {i}")
                    break
#                elif 'loopback' in info['name'].lower() and 'hw:2,1' in info['name']:
#                    self.device = i
#                    print(f"Found hardware loopback device at index {i}")
#                    break

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            print("Check your ALSA configuration and device permissions")
            self.device = 4
        
#        for id in range(self.recorder.get_device_count()):
#            # print()
#            dev_dict = self.recorder.get_device_info_by_index(id)
#            print(dev_dict)
#            for key, value in dev_dict.items():
#                if key == 'index': self.device = value
#                if value == device:
#                    print("AudioProcessor.find_device_index: device",value, " index:", self.device)
#                    return self.device

    def start_capture(self):
        try:
            self.stream   = self.recorder.open(format = INFORMAT,rate = RATE,channels = CHANNELS,input = True, input_device_index=self.device, frames_per_buffer=FRAMESIZE, stream_callback=self.callback)
            self.stream.start_stream()
            print("AudioProcessor.start_capture> ADC/DAC ready ", self.recorder.get_default_input_device_info()['name'], " index>", self.device)
        except Exception as e:
            print("AudioProcessor.start_capture> ADC/DAC not available", e)

    def stop_capture(self):
        try:
            self.stream.stop_stream()
            self.stream.close()
        except Exception as e:
            print("AudioProcessor.Stop_capture> error", e)

    # def callback(self, in_data, frame_count, time_info, status):

    #     # print('AudioProcessor.callback> received %d frames, time %s, status %s, data bytes %d' % (frame_count, time_info, status, len(in_data)))
    #     self.calcReadtime()
    #     data        = np.frombuffer(in_data, dtype=np.int16 )   #/maxValue
    #     # self.oldsamples['left']  = self.samples['left']
    #     # self.oldsamples['right'] = self.samples['right']
    #     self.samples['left']  = data[0::2] # * self.window
    #     self.samples['right'] = data[1::2] # * self.window
    #     self.samples['mono']  = np.mean(data.reshape(len(data)//CHANNELS, CHANNELS) ,axis=1)
    #     # print('AudioProcessor.callback>', len(self.samples['left']), len(self.samples['right']), len(self.samples['mono']))
    #     self.record(in_data)
    #     self.events.Audio('capture')
    #     # self.calcReadtime(False)
    #     return (in_data, pyaudio.paContinue)

# --- CRITICAL CONSTANT (Define this in your class __init__ once) ---
# Example: self.CRITICAL_TIME_MS = (self.CHUNK / self.RATE) * 1000 
# For 44100 Hz and 1024 frames, this is approx 23.22 ms
# -------------------------------------------------------------------

    def callback(self, in_data, frame_count, time_info, status):

        # 1. START HIGH-RESOLUTION TIMER
        start_time = time.perf_counter()
        
        # 2. CHECK FOR AUDIO BUFFER OVERFLOW
        # The 'status' flag tells us if the buffer overflowed BEFORE we even started processing.
        if status & pyaudio.paInputOverflow:
            print("\n*** [FATAL REAL-TIME WARNING] Input Buffer Overflow! ***")
            print("    -> Processing is too slow. Previous frame was dropped.")
            
        # --- Existing Audio Capture and Processing ---

        # Your custom time tracking hook (if you still need it)
        self.calcReadtime() 
        
        # Convert bytes to numpy array (assuming dtype=np.int16)
        data = np.frombuffer(in_data, dtype=np.int16) 
        
        # Split/Reshape Samples
        # Note: Using a global/class variable CHANNELS here
        self.samples['left']  = data[0::2]
        self.samples['right'] = data[1::2]
        
        # Mono conversion (Efficiently handles multiple channels)
        self.samples['mono']  = np.mean(data.reshape(len(data)//CHANNELS, CHANNELS) ,axis=1) 
        
        # Run the expensive audio processing/visual update functions here
        self.record(in_data)
        self.events.Audio('capture')
        
        # The visualization logic (drawing to the DSI screen) MUST be placed here 
        # for the timing check to be meaningful.
        # self.update_dsi_screen() # <-- ADD YOUR GRAPHICS CALL HERE!

        # self.calcReadtime(False) # Your custom time tracking hook (if you still need it)

        # --- END HIGH-RESOLUTION TIMER & CHECK ---
        
        processing_time_ms = (time.perf_counter() - start_time) * 1000
    
        # 3. CHECK AGAINST TIME BUDGET
        # We must ensure this method runs faster than the time it took the audio to arrive.
        if processing_time_ms > CRITICAL_TIME_MS:
            print(f"\n*** [LATENCY WARNING] FRAME LATE! ***")
            print(f"    -> Time Spent: {processing_time_ms:.2f} ms")
            print(f"    -> Time Limit: {CRITICAL_TIME_MS:.2f} ms")
            print(f"    -> **ACTION REQUIRED**: Increase CHUNK size or optimize code.")
        
        # Continue stream
        return (in_data, pyaudio.paContinue)


    def start_recording(self):
        self.recordingState = True

    def stop_recording(self):
        self.recordingState = False
        self.saveRecording()
        self.recording = []
        self.events.Audio('recording_stopped')

    def record(self, data):
        if self.recordingState:
            self.recording.append(data)

            if len(self.recording) >  RECORDTIME:
                self.stop_recording()

            elif len(self.recording) % SAMPLEPERIOD == 1:
                print("AudioProcessor.record> recorded %fs audio " % len(self.recording)/SAMPLEPERIOD )

    def saveRecording(self):
        # Save the recorded data as a WAV file
        self.recordfile = self.find_next_file( RECORDINGS_PATTERN )
        print('Finished recording to ', self.recordfile)
        try:
            # bits = self.recorder.get_sample_size(INFORMAT)
            # wf = PyWave.open(recordfile, mode='w', channels = CHANNELS, frequency = RATE, bits_per_sample = bits, format = INFORMAT)
            wf = wave.open(self.recordfile, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.recorder.get_sample_size(INFORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.recording))

            wf.close()
        except Exception as e:
            print("AudioProcessor.save_recording> ", e)


    def find_next_file(self, path_pattern):
        """
        Finds the next free path in an sequentially named list of files

        e.g. path_pattern = 'file-%s.txt':

        file-1.txt
        file-2.txt
        file-3.txt

        Runs in log(n) time where n is the number of existing files in sequence
        """
        i = 1

        # First do an exponential search
        while os.path.exists(path_pattern % i):
            i = i * 2

        # Result lies somewhere in the interval (i/2..i]
        # We call this interval (a..b] and narrow it down until a + 1 = b
        a, b = (i // 2, i)
        while a + 1 < b:
            c = (a + b) // 2 # interval midpoint
            a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

        return path_pattern % b


    def process(self, bass=500, treble=5000):
        # self.smoothed_samples['left']  = np.add(SMOOTHFACTOR * self.oldsamples['left'], (1-SMOOTHFACTOR)*self.samples['left'])
        # self.smoothed_samples['right'] = np.add(SMOOTHFACTOR * self.oldsamples['right'], (1-SMOOTHFACTOR)*self.samples['right'])
        # left  = self.samples['left']
        # right = self.samples['right']

        self.bins['left']   = self.calcFFT(self.samples['left'])
        self.bins['right']  = self.calcFFT(self.samples['right'])
        # The fastest way using already computed magnitude bins
        self.bins['mono'] = (self.bins['left'] + self.bins['right']) / 2.0
        # self.bins['mono']   = self.calcFFT(self.samples['mono'])
        # self.bins['left']     = self.spectral_average(left, 'left')
        # self.bins['right']    = self.spectral_average(right, 'right')


        self.vu['left']     = self.VU('left')
        self.vu['right']    = self.VU('right')
        self.vu['mono']     = self.VU('mono')
        self.detectSilence()
        self.calcReadtime(False)
        self.trigger_detected = []

        # bass_signal   = np.max( self.filter( self.samples[ 'mono' ], bass, type='lowpass' )/ maxValue)
        # treble_signal = np.max( self.filter( self.samples[ 'mono' ], treble, type='highpass')/ maxValue )
        bass_signal   = 0
        treble_signal = 0
        if bass_signal> 0.05:
            self.trigger_detected.append('bass')
            # print("bass ", bass_signal)
        if treble_signal> 0.05:
            self.trigger_detected.append('treble')
            # print("treble ", treble_signal)


    def detectSilence(self):
        # use hysterises - quick to detect a signal, slow to detect silience (5 seconds)
        signal_level = (self.vu['left'] + self.vu['right'])/2.0
        ave_level    = self.silence.average(signal_level)
        # print (signal_level )

        if ave_level < SILENCETHRESOLD:
            # print("ProcessAudio.detectSilence> Silence at", ave_level, signal_level)
            self.minC = 0
            self.signal_detected = False
            self.silence.reset('signal')  # clear the window to keep checking for Silence
            self.events.Audio('silence_detected')
        elif not self.signal_detected and signal_level >= SILENCETHRESOLD:
            print("ProcessAudio.detectSilence> Signal at", ave_level, signal_level)
            self.signal_detected = True
            self.silence.reset('signal')
            self.events.Audio('signal_detected')
        #else: no change to the silence detect state


    def createBands(self, spacing, fcentre=FIRSTCENTREFREQ, flast=LASTCENTREFREQ):
        '''
        Create the upper bounds of each interval as an array that can be used to fill the fft data
        - spacing is the octave spacing eg 3.0, 6.0
        - fcentre is the lowest start frequency eg 31.25
        '''
        flast = LASTCENTREFREQ if flast is None else flast
        intervalUpperF      = []
        centres             = []
        # print("AudioProcessor.createBands >Calculate Octave band frequencies: 1/%2d octave, starting at %2f Hz" % (spacing, fcentre))
        #
        # Loop in octaves bands
        #
        startbin      = 1
        FFACTOR       = math.pow(2, 1.0/float(2*spacing) )
        intervalUpper = fcentre * FFACTOR

        while intervalUpper < flast:
            bincount        = startbin
            fcentre         = fcentre * math.pow(2, float(1.0/spacing))
            intervalUpper   = fcentre * FFACTOR

            if bincount*BINBANDWIDTH > intervalUpper:
                # Check if the bin will fit in the octave band, if not discard the current octave band
                # print "  band too low @%dHz for bin %d at %dHz - skip it" % (intervalUpper, bincount, bincount*BINBANDWIDTH)
                continue
            else:
                # Check how many bins will comprise this octave band (must be at least one)
                while (bincount+1)*BINBANDWIDTH <= intervalUpper:
                    bincount    += 1
                intervalUpperF.append( intervalUpper )
                centres.append( fcentre )

            # print (" Fcentre %2.1f, Upper bound %2.1f, startbin %d (%4.0fHz), to bin %d (%4.0fHz)" % (fcentre, intervalUpper, startbin, startbin * BINBANDWIDTH, bincount, bincount * BINBANDWIDTH ))
            startbin = bincount+1
        # print("AudioProcessor.createBands>  %d bands determined at: %s" % (len(centres), ["%1.0f" % f for f in centres]))
        return intervalUpperF


    # def VU(self,channel):
    #     PEAK   = 0.0
    #     FLOOR  = -120.0
    #     RMSMAX = 0.03
    #     """
    #     Simply find the RMS level of a sample and take the log to get the average power
    #     """
    #     rms = np.sqrt(np.mean(np.square((self.samples[channel][:FRAMESIZE]//2)/ maxValue)))  #√[:FRAMESIZE]//2
    #     if np.isnan(rms): rms=0.0
    #     # if rms > self.vumax[channel]: self.vumax[channel] = rms

    #     # db_value = 20 * np.log10 (rms + 1e-6)
    #     # norm     = (-FLOOR + db_value)/ (PEAK-FLOOR)
    #     # print("AudioProcessor.VU> %s %f rms %f dB norm %f  vumax %f" % (channel, rms/RMSMAX, db_value, norm, self.vumax[channel]))
    #     return  min(1.0, rms/VUGAIN)   # normalise

    def VU(self, channel):
        # Use full framesize, normalize AFTER squaring/before mean for consistency
        normalized_data = self.samples[channel] / maxValue
        
        # Calculate RMS
        rms = np.sqrt(np.mean(np.square(normalized_data)))
        
        if np.isnan(rms): rms = 0.0

        return min(1.0, rms / VUGAIN)


    def reduceSamples(self, channel, reduceby, rms=True ):
        # reduce the sample window to the size available
        normalised_samples = self.samples[channel]/ maxValue  #[:FRAMESIZE//2]
        end = reduceby * int(len(normalised_samples)/ reduceby)
        # reshaped_samples   = np.mean( normalised_samples[:end].reshape(-1, reduceby), axis=1)
        rms_reshaped_samples   = np.sqrt( np.mean( np.square(normalised_samples[:end].reshape(-1, reduceby)), axis=1))/0.2
        reshaped_samples       = np.mean( normalised_samples[:end].reshape(-1, reduceby), axis=1)/0.2
        # print("AudioProcessor.reduceSamples by", reduceby, "from", len(normalised_samples), "to", len(reshaped_samples), "length", length)
        if rms:
            return rms_reshaped_samples.tolist()
        else:
            return reshaped_samples.tolist()


    """ use this to shift the noise floor eg: RMS 20 - 5000 -> 0->5000"""
    def floor(self, x,y):
        if x > y:
            return x
        else:
            return y

    def calcReadtime(self,start=True):
        if start:
            self.startreadtime = time.time()
        else:
            self.readtime.append(time.time()-self.startreadtime)
            if len(self.readtime)>100: del self.readtime[0]
            # print('AudioProcessor:calcReadtime> %3.3fms' % (np.mean(self.readtime)*1000))


    def calcDCoffset(self, data):
        """ Create a ring buffer of DC mean level """
        self.dc.append(np.mean(data))  #setDC

        if len(self.dc) > DCOFFSETSAMPLES:
            del self.dc[0]

        self.dcoffset = sum(self.dc)/len(self.dc)

        return self.dcoffset

    # def calcFFT(self, data):
    #     """
    #     Calculate the FFT and normalise to 0-1
    #     """
    #     data        = data[:FRAMESIZE//2] * self.window
    #     data        = np.pad(data, (0, NUMPADS), 'constant')
    #     spectrum    = np.abs(np.fft.fft(data)) # * self.window))
    #     spectrum    = spectrum / maxValue  #Normalize to 0-1 range

    #     return spectrum

    def calcFFT(self, data):
        """
        Calculate the Real FFT and normalise (fastest method)
        """
        # 1. Apply Window/Slice: (Make sure your window is applied as efficiently as possible)
        # If self.window is already the correct length (FRAMESIZE//2), this is fine.
        windowed_data = data[:FRAMESIZE//2] * self.window 
        
        # 2. Apply Zero Padding:
        # If the length is not a power of 2, FFT is much slower. Ensure (FRAMESIZE//2 + NUMPADS) is a power of 2.
        padded_len = FRAMESIZE//2 + NUMPADS
        
        # 3. Use rfft for a ~2x speedup on real-valued data
        # Specify the exact FFT length using 'n' to include the padding
        spectrum = np.fft.rfft(windowed_data, n=padded_len)
        
        # 4. Get magnitude and normalize
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

        for band in intervalUpperF:  # collect bins at a time
            bincount    = startbin

            while bincount*BINBANDWIDTH <= band:
                bincount    += 1

            level = 20*np.log2((bins[startbin:bincount].mean() + 1e-7))
            spectrumBands.append( self.normalise(level) )
            startbin = bincount
            # print("PackFFT >", spectrumBands)
        return spectrumBands

    def normalise(self, level):
        """ convert from dB into a percentage """
        """ need to calibrate this more carefully """
        # print("AudioProcessor.normalise > input level ", level)
        self.dynamicRange(level)
        """ measuring this on MAc shows the range to be about -72 to +40
            was (20 +level)/70 for preDAC HW
        """
        floor = -self.minC
        scale = self.peakC + floor + 0.0001
        # print("Normalise floor %f scale %f level %f" % (floor, scale, level))
        return (floor + level)/(scale )

    def printSpectrum(self, octave, intervalUpperF, left=True):
        FFACTOR = math.pow(2, 1.0/float(2*octave) )
        if left:
            power = self.spectrum['left']
        else:
            power = self.spectrum['right']

        for i in range (0,len(power)):
            fCentre = intervalUpperF[i]/FFACTOR
            self.printPower(power[i], intervalUpperF[i]/FFACTOR)
        print("--------------")

    def getSpectrum(self, octave, intervalUpperF, left=True):
        FFACTOR = math.pow(2, 1.0/float(2*octave) )
        if left:
            power = self.spectrum['left']
        else:
            power = self.spectrum['right']

        channelPower = []
        for i in range (0,len(power)):
            fCentre = intervalUpperF[i]/FFACTOR
            channelPower.append(self.filter(power[i], fCentre))
        return channelPower


    def leftCh(self):
        return self.getSpectrum()

    def rightCh(self):
        return self.getSpectrum(left=False)

    def dynamicRange(self, level):
        # assume input is a level in dB - calc the dynamicRange
        text = ""
        change = False
        if level > self.peakC:
            self.peakC = level
            text  += "max %8f " % self.peakC
            change = True
        if level < self.minC:
            if level < RMSNOISEFLOOR: level = RMSNOISEFLOOR
            self.minC = level
            text  += " min %8f " % self.minC
            change = True
        # if change: print("AudioProcessor.dynamicRange> RMS max %f, min %f" % (self.peakC, self.minC))


    """ calculate the RMS power (NB: sqrt is not required) """
    def rmsPower(self, y):
        return np.abs(np.mean(np.square(y)))

    def processstatus(self):
        text  = "Process audio> signal det %s" % self.signal_detected
        text += "\n L%10f-^%10f^%10f\t%10f R"% (self.vu['left'], self.peak['left'], self.peak['right'], self.vu['right'])
        text += "\n Peak Spectrum L:%f, R:%f" % (max(self.bins['left']), max(self.bins['right']) )
        return text

    """ Butterworth digital filters """
    def butterworth_coeffs(self, cutoff, order=5,type='lowpass'):
        #btype{‘lowpass’, ‘highpass’, ‘bandpass’, ‘bandstop’}
        # cutoff in Hz
        return butter(order, cutoff, fs=RATE, btype=type, analog=False)

    def filter(self, data, cutoff, order=5, type='lowpass'):
        b, a = self.butterworth_coeffs(cutoff, order=order, type=type)
        y = lfilter(b, a, data)
        return y



    """ test code """

#     def LR2(self, vu, peak):
#         lString = "-"*int(bars-vu['left']*bars)+"#"*int(vu['left']*bars)
#         rString = "#"*int(vu['right']*bars)+"-"*int(bars-vu['right']*bars)
#         print(("[%s]=L%10f-^%10f^%10f\t%10f R=[%s]"% (lString, vu['left'], peak['left'], peak['right'], vu['right'], rString)))
#         # print("L=[%s]\tR=[%s]"%(lString, rString))

#     def printBins(bins):
#         text  = ""
#         for i in range (1,len(bins)):
#             text += "[%2d %2.1f] " % (i*BINBANDWIDTH, bins[i]/250)
#             if i >50: break
#         print(text)

# def main():
#     # main loop
#     events = Events('Audio')
#     audioprocessor = AudioProcessor(events)
#     runflag = 1
#     while runflag:

#         for i in range(int(10*44100/FRAMESIZE)): #go for a few seconds

#             audioprocessor.process()
#             audioprocessor.printSpectrum()
#             # audioprocessor._print()
#             # audioprocessor.calibrate()

#         audioprocessor.dynamicRange()
#         runflag = 0

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         pass
