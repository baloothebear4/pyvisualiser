#!/usr/bin/env python3
import pyaudio
import numpy as np
import wave
import time

def test_audio_capture():
    """Test 16-bit audio capture from ALSA loopback device"""
    
    # Audio parameters
    CHUNK = 2048  # Larger buffer to prevent overflow
    FORMAT = pyaudio.paInt16  # 16-bit
    CHANNELS = 2
    RATE = 44100  # Will auto-convert if source is different
    RECORD_SECONDS = 5
    
    print("Testing 16-bit audio capture...")
    print(f"Format: 16-bit signed")
    print(f"Channels: {CHANNELS}")
    print(f"Sample rate: {RATE} Hz")
    print(f"Buffer size: {CHUNK} frames")
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # List available devices (optional - for debugging)
    print("\nAvailable audio devices:")
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
            if 'loopin' in info['name'].lower():
                loopback_device = i
                print(f"Found loopin device at index {i}")
                break
#            elif 'loopback' in info['name'].lower() and 'hw:2,1' in info['name']:
#                loopback_device = i
#                print(f"Found hardware loopback device at index {i}")
#                break
        
        if loopback_device is None:
            print("Trying device 4 (loopin) explicitly")
            loopback_device = 4
        
        # Open stream with specific loopback device
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       input_device_index=loopback_device,
                       frames_per_buffer=CHUNK)
        
        print(f"\nRecording for {RECORD_SECONDS} seconds...")
        print("Play some audio through shairport-sync or run speaker-test")
        
        frames = []
        max_amplitude = 0
        
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                
                # Convert to numpy array for analysis
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Check amplitude
                current_max = np.max(np.abs(audio_data))
                if current_max > max_amplitude:
                    max_amplitude = current_max
                
                # Show progress and levels
                if i % 20 == 0:  # Update every ~0.5 seconds with larger buffer
                    level_percent = (current_max / 32767) * 100
                    print(f"Recording... {i*CHUNK/RATE:.1f}s - Level: {level_percent:.1f}%")
                    
            except OSError as e:
                if e.errno == -9981:  # Input overflow
                    print(f"Buffer overflow at {i*CHUNK/RATE:.1f}s - continuing...")
                    # Add empty frame to maintain timing
                    frames.append(b'\x00' * (CHUNK * CHANNELS * 2))
                else:
                    raise
        
        print("Recording finished!")
        
        # Close stream
        stream.stop_stream()
        stream.close()
        
        # Save to file for verification
        wf = wave.open('test_recording.wav', 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Analysis results
        total_samples = len(frames) * CHUNK * CHANNELS
        max_level_db = 20 * np.log10(max_amplitude / 32767) if max_amplitude > 0 else -float('inf')
        
        print(f"\n=== Recording Results ===")
        print(f"Total samples captured: {total_samples}")
        print(f"Data type: 16-bit signed integer")
        print(f"Max amplitude: {max_amplitude} / 32767")
        print(f"Peak level: {max_level_db:.1f} dB")
        print(f"File saved as: test_recording.wav")
        
        if max_amplitude == 0:
            print("\n⚠️  WARNING: No audio detected!")
            print("   - Check that audio is playing through shairport-sync")
            print("   - Verify ALSA loopback configuration")
            print("   - Test with: speaker-test -c2 -twav")
        else:
            print("\n✅ SUCCESS: 16-bit audio capture working!")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Check your ALSA configuration and device permissions")
        
    finally:
        p.terminate()

def analyze_audio_properties():
    """Analyze the captured audio file properties"""
    try:
        with wave.open('test_recording.wav', 'rb') as wf:
            print(f"\n=== WAV File Analysis ===")
            print(f"Channels: {wf.getnchannels()}")
            print(f"Sample width: {wf.getsampwidth()} bytes ({wf.getsampwidth() * 8} bit)")
            print(f"Frame rate: {wf.getframerate()} Hz")
            print(f"Frames: {wf.getnframes()}")
            print(f"Duration: {wf.getnframes() / wf.getframerate():.1f} seconds")
            
            # Read a small sample for data type verification
            wf.rewind()
            sample_data = wf.readframes(1024)
            audio_array = np.frombuffer(sample_data, dtype=np.int16)
            print(f"Data type in memory: {audio_array.dtype}")
            print(f"Value range in sample: {np.min(audio_array)} to {np.max(audio_array)}")
            
    except FileNotFoundError:
        print("No recording file found to analyze")
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    test_audio_capture()
    analyze_audio_properties()
