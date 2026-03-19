import sys
import os
sys.path.insert(0, os.path.abspath('./tests'))
from vis import *
from pyvisualiser import ScreenController
from pyvisualiser.styles.profiles import ProfileManager
from pyvisualiser.styles.presets import EmbeddedHiFiProfile

ProfileManager.set_profile(EmbeddedHiFiProfile)
hw_platform = machine()
import pygame
pygame.init()
controller = ScreenController([AudioTestScreen], hw_platform=hw_platform)

TARGET_SCREENS = list(set(
    VU_METER_SCREENS + SPECTRUM_TEST_SCREENS + VU_BAR_TEST_SCREENS + GLSCREENS + TEST_SCREENS
))

successes = 0
failures = []

for ScreenClass in TARGET_SCREENS:
    print(f"Testing instantiation of {ScreenClass.__name__}...", end=" ")
    try:
        if ScreenClass.__name__ == 'VUMeterImageFrame':
            screen = ScreenClass(controller.platform, type='blueVU')
        elif ScreenClass.__name__ == 'IntensityTestScreen':
            # Needs specific arguments?
            screen = ScreenClass(controller.platform)
        else:
            screen = ScreenClass(controller.platform)
        print("OK")
        successes += 1
    except Exception as e:
        print(f"FAIL: {type(e).__name__}: {e}")
        failures.append(ScreenClass.__name__)

print(f"\n{successes} tests instantiated successfully!")
if failures:
    print(f"{len(failures)} failures: {failures}")
    sys.exit(1)
sys.exit(0)
