"""
Simple test harness to exercise the whole API of an endpoints, to verify the robustness.  
As there are multiple endpoints, they should all implement the API consistently and reliably
"""

import time
import sys
import os

# Ensure the src directory is in the path to allow imports of core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

try:
    from events import Events
except ImportError:
    # Fallback mock for testing script logic if Events is not in path
    class Events:
        def __init__(self, names):
            for name in names: setattr(self, name, self._fire)
        def _fire(self, *args, **kwargs): pass
        def __iadd__(self, other): return self


from pyvisualiser.endpoints.roon import RoonEndpoint


# from pyvisualiser.endpoints.apple import AppleEndpoint
# from pyvisualiser.endpoints.mpd import MPDEndpoint
# from pyvisualiser.endpoints.spotify import SpotifyEndpoint
# from pyvisualiser.endpoints.tidal import TidalEndpoint

def test_endpoint_api(endpoint_class, target_name="MacViz"):
    """
    Instantiates the endpoint and monitors the API output for consistency and robustness.
    """
    print(f"\n{'='*60}")
    print(f"Starting API Robustness Test: {endpoint_class.__name__}")
    print(f"{'='*60}")

    # 1. Setup Event System
    events = Events(('Metadata',))
    event_stats = {'count': 0}
    
    def metadata_logger(event_type):
        event_stats['count'] += 1
        msg = f">> [EVENT #{event_stats['count']}] Metadata: '{event_type}'"
        if event_type == 'new_track' and 'ep' in locals():
            msg += f" -> Now Playing: {ep.artist} - {ep.track}"
        print(msg)

    events.Metadata += metadata_logger

    try:
        # 2. Initialize Endpoint
        # maxwh is required for internal image scaling logic
        print(f"Connecting to endpoint for zone '{target_name}'...")
        ep = endpoint_class(events, target_name=target_name, maxwh=(800, 400))
        
        # 3. Static API Property Check
        print("\n--- Current Metadata API State ---")
        print(f"  Connected:    {ep.roon is not None}")
        print(f"  Zone Name:    {ep.zone_name or 'None'}")
        print(f"  Play Status:  {ep.play_status} (Playing: {ep.playing})")
        print(f"  Artist:       {ep.artist}")
        print(f"  Track:        {ep.track}")
        print(f"  Album:        {ep.album}")
        print(f"  Duration:     {ep.duration:.2f}s")
        print(f"  Elapsed:      {ep.elapsed:.2f}s ({ep.elapsedpc*100:.1f}%)")
        print(f"  Remaining:    {ep.remaining:.2f}s")
        print(f"  Art URL:      {ep.album_art[:70] if ep.album_art else 'None'}...")

        # 4. Live Monitoring Loop
        print(f"\nMonitoring '{target_name}' for live updates (60 seconds). Use Roon remote to trigger events...")
        print("-" * 60)
        
        start_time = time.time()
        while time.time() - start_time < 60:
            progress_bar = "#" * int(ep.elapsedpc * 20) + "-" * (20 - int(ep.elapsedpc * 20))
            print(f"  [{time.strftime('%H:%M:%S')}] {ep.play_status:8} | {ep.artist[:15]:15} | {ep.track[:20]:20} | [{progress_bar}] {ep.elapsedpc*100:5.1f}%")
            time.sleep(2.0)

    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    except Exception as e:
        print(f"\n[FAIL] Test encountered an error: {e}")
    finally:
        print("\nShutting down endpoint...")
        if 'ep' in locals(): ep.metadata_stop()
        print("Test harness exit.\n")

if __name__ == "__main__":
    # Use CLI arg for zone name if provided, otherwise default to MacViz
    run_target = sys.argv[1] if len(sys.argv) > 1 else "MacViz"
    test_endpoint_api(RoonEndpoint, target_name=run_target)





# future endpoints....
#
# from pyvisualiser.endpoints.local import LocalEndpoint
# from pyvisualiser.endpoints.deezer import DeezerEndpoint
# from pyvisualiser.endpoints.qobuz import QobuzEndpoint
# from pyvisualiser.endpoints.youtube import YouTubeEndpoint
# from pyvisualiser.endpoints.lastfm import LastFMEndpoint
# from pyvisualiser.endpoints.tunein import TuneInEndpoint
# from pyvisualiser.endpoints.pandora import PandoraEndpoint
# from pyvisualiser.endpoints.soundcloud import SoundCloudEndpoint
# from pyvisualiser.endpoints.amazon import AmazonEndpoint
# from pyvisualiser.endpoints.bandcamp import BandcampEndpoint
# from pyvisualiser.endpoints.hypem import HypemEndpoint
