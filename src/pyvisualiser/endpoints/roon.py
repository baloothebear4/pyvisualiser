
from roonapi import RoonApi, RoonDiscovery
# import pygame # Keeping imports minimal as requested in original file structure context
import time
from typing import Tuple, Dict, Any, List, Optional

# Assuming Events is defined elsewhere and available for type hinting purposes
# from events import Events 

"""

I want to separate RoonEndpoint from RoonMetadata. When I have multiple endpoints, there will still only be 
one type of Metadata, it is then populated by the active Endpoint. 

This is a change to how the Platform class is initiated, RoonMetadata and RoonEndpoint are initialised
from the screen handler

MetaData needs to be in its own file and abstracted from Roon altogether, as it is the data model for the metadata 
captured from Roon, Apple, MPDand should be independent of the API connection logic.


"""


class MetaData:
    """
    Data model class to manage the metadata captured from MPD.
    Handles state reading from the connected Roon instance.
    """

    ZONE_KEYS: Tuple[str, ...] = ( 'zone_id', 'display_name', 'state', 'now_playing', 'seek_position')
    NOW_PLAYING_KEYS: Tuple[str, ...] = ( 
        'seek_position', 'length', 'one_line', 'two_line', 'three_line', 'image_key', 'artist_image_keys'
    )
    # Default URLs should ideally be loaded from configuration/assets, not hardcoded in class structure.
    DEFAULT_URL: Optional[str] = None 

    def __init__(self, roonapi, maxwh: Tuple[int, int]):
        """
        Initializes the metadata cache and state tracking variables.
        :param roonapi: Initialized RoonApi object.
        :param maxwh: Tuple (width, height) for image scaling.
        """
        self._metadata: Dict[str, Any] = {}
        self.roon = roonapi
        self.maxwh = maxwh
        self._initialize_state()
        self._play_changed: bool = False
        self._track_changed: bool = False
        self._album_art_url: Optional[str] = MetaData.DEFAULT_URL
        self._artist_art_url: Optional[str] = MetaData.DEFAULT_URL
        self._target_zone: str = 'pre3' # Initial default value

    def _initialize_state(self):
        """Sets up the initial empty state for all tracked keys."""
        # Initialize Zone Metadata structure
        self._metadata = { k : "" for k in self.ZONE_KEYS }
        # Initialize Now Playing Metadata structure
        self._metadata['now_playing'] = { k : "" for k in MetaData.NOW_PLAYING_KEYS }
        # Initialize numeric fields with valid defaults to prevent conversion errors
        self._metadata['now_playing']['length'] = 0
        self._metadata['now_playing']['seek_position'] = 0
        self._metadata['seek_position'] = 0
        self._metadata['state'] = 'stopped'
        # Deep initialization for multi-line data
        self._metadata['now_playing']['three_line'] = {'line1':'', 'line2':'', 'line3':''}


    @property
    def album_art(self) -> Optional[str]:
        """Retrieves and generates the scaled album art URL."""
        try:
            image_key = self._metadata.get('now_playing', {}).get('image_key')
            if not image_key:
                return MetaData.DEFAULT_URL

            # Assume width needs to match height for square output if only one dimension is passed, 
            # or use the provided maxwh[1] (height) as suggested by original code logic.
            target_width = self.maxwh[0] # Using width from maxwh just in case? Reverting to matching suggestion's pattern.
            target_height = self.maxwh[1]

            return self.roon.get_image(image_key, width=target_width, height=target_height)
        except Exception as e:
            # Catch specific API/network errors if possible, but for now, keep it general 
            # while acknowledging the original broad catch scope issue.
            print(f"Error retrieving album art: {e}")
            return MetaData.DEFAULT_URL

    @property
    def artist_art(self) -> Optional[str]:
        """Retrieves the scaled artist art URL."""
        try:
            artist_keys = self._metadata.get('now_playing', {}).get('artist_image_keys')
            if not artist_keys or not isinstance(artist_keys, list):
                 return MetaData.DEFAULT_URL

            first_key = artist_keys[0]
            target_width = self.maxwh[0]
            target_height = self.maxwh[1]
            
            return self.roon.get_image(first_key, width=target_width, height=target_height)
        except Exception as e:
            print(f"Error retrieving artist art: {e}")
            return MetaData.DEFAULT_URL

    # --- Read-Only Properties (Simplified Error Handling) ---

    @property
    def artist(self) -> str:
        """Returns the Artist name."""
        try:
            return self._metadata['now_playing']['three_line']['line2']
        except (KeyError, TypeError):
            return ""

    @property
    def album(self) -> str:
        """Returns the Album name."""
        try:
            return self._metadata['now_playing']['three_line']['line3']
        except (KeyError, TypeError):
            return ""

    @property
    def track(self) -> str:
        """Returns the Track/Title name."""
        try:
            return self._metadata['now_playing']['three_line']['line1']
        except (KeyError, TypeError):
            return ""

    @property
    def playing(self) -> bool:
        """Checks if Roon state is 'playing'."""
        state = self.play_status # Use the property getter for state reading
        return state == 'playing'

    @property
    def play_status(self) -> str:
        """Returns the current state ('playing', 'paused', etc.)."""
        return self._metadata['state']

    @property
    def zone_name(self) -> str:
        """Returns the display name of the target zone."""
        # We rely on set_target_zone having already populated this.
        return self._metadata['display_name'] 

    @property
    def elapsedpc(self) -> float:
        """Calculates percentage elapsed time."""
        return (self.elapsed / self.duration) if self.duration > 0 else 0.0

    @property
    def duration(self) -> float:
        """Returns the total duration of the track in seconds."""
        try:
            val = self._metadata.get('now_playing', {}).get('length')
            return float(val) if val not in (None, "") else 0.0
        except (KeyError, ValueError, TypeError):
            return 0.0

    @property
    def elapsed(self) -> float:
        """Returns the current elapsed time in seconds."""
        try:
            # Roon often provides seek_position both in 'now_playing' and at the top level
            val = self._metadata.get('seek_position')
            if val in (None, ""):
                val = self._metadata.get('now_playing', {}).get('seek_position')
            
            return float(val) if val not in (None, "") else 0.0
        except (KeyError, ValueError, TypeError):
            return 0.0

    @property
    def remaining(self) -> float:
        """Calculates the time remaining."""
        return self.duration - self.elapsed

    # --- State Flag Management (Keep setters/getters as they handle change detection) ---
    @property
    def track_changed(self) -> bool: return self._track_changed
    @track_changed.setter
    def track_changed(self, val: bool): self._track_changed = val

    @property
    def play_changed(self) -> bool: return self._play_changed
    @play_changed.setter
    def play_changed(self, val: bool): self._play_changed = val

    # --- Zone Targeting ---

    @property
    def zone(self):
        """Returns the full dictionary representation of the target zone."""
        return self.roon.zone_by_name(self._target_zone_name)

    @property
    def target_zone_name(self) -> str:
        return self._target_zone_name

    def set_target_zone(self, name: str):
        """Sets the target zone by display name and updates internal IDs."""
        try:
            # Try exact match first
            target_zone = self.roon.zone_by_name(name) if self.roon else None
            
            # Fallback to partial match if exact match fails
            if not target_zone and self.roon:
                target_zone = next((z for z in self.roon.zones.values() if name.lower() in z.get('display_name', '').lower()), None)

            if not target_zone: # Assuming an empty dict or None means it doesn't exist
                print(f"MetaData Error: Zone '{name}' does not exist.")
                self._target_zone_name = 'Unknown'
                self._target_zone = ''
                self._metadata['display_name'] = 'Unknown' # Ensure display_name is updated
            else:
                # Update IDs and names based on the retrieved zone object structure
                self._target_zone = target_zone['zone_id']
                self._target_zone_name = target_zone.get('display_name', name)
                self._metadata['display_name'] = self._target_zone_name
                print(f"MetaData Info: Target zone '{self._target_zone_name}' set, id {self._target_zone}")
        except Exception as e:
            print(f"MetaData Error setting target zone to {name}: {e}")
            self._target_zone_name = 'Unknown'
            self._target_zone = ''
            self._metadata['display_name'] = 'Unknown' # Ensure display_name is updated


    def update(self, changed_zoneids: List[str]):
        """ 
        Updates metadata from Roon based on reported changes.
        Triggered by roon_callback when zone data changes.
        """
        # Store old values to detect changes for event emission
        old_track: str = self.track
        old_play_status: str = self.play_status

        # Only process if the target zone is among the changed zones
        if self._target_zone not in changed_zoneids:
            # Log updates for non-target zones (logging only, no state update needed for them)
            for zone_id in changed_zoneids:
                if self.roon:
                    zone_info = self.roon.zones.get(zone_id) or self.roon.outputs.get(zone_id)
                    if zone_info:
                        print(f"MetaData Info: Metadata updated for non-target zone/output: {zone_info.get('display_name', zone_id)}")
                    else:
                        print(f"MetaData Info: Metadata updated for unknown non-target ID: {zone_id}")
            return # No need to update our target zone's state

        # Fetch the latest zone data for the target zone
        zone_data = self.roon.zone_by_name(self._target_zone_name)

        if zone_data:
            # Reset internal metadata to a clean state before populating from Roon
            # This ensures that if a field is no longer present in Roon's update,
            # it reverts to its default empty/zero value instead of retaining old data.
            self._initialize_state()

            # Populate top-level zone keys
            for key in MetaData.ZONE_KEYS:
                if key in zone_data and key != 'now_playing':
                    self._metadata[key] = zone_data[key]
            
            # Populate 'now_playing' details if available
            if 'now_playing' in zone_data and isinstance(zone_data['now_playing'], dict):
                self._metadata['now_playing'].update(zone_data['now_playing'])
                
                # Ensure 'three_line' is a dictionary and populate its lines
                if 'three_line' in zone_data['now_playing'] and isinstance(zone_data['now_playing']['three_line'], dict):
                    self._metadata['now_playing']['three_line'].update(zone_data['now_playing']['three_line'])
                else:
                    # If 'three_line' is missing or not a dict, ensure it's an empty dict
                    self._metadata['now_playing']['three_line'] = {'line1':'', 'line2':'', 'line3':''}
            
            # Update numeric fields that might be at the top level of zone_data
            self._metadata['seek_position'] = zone_data.get('seek_position', 0)
            self._metadata['state'] = zone_data.get('state', 'stopped')
            # print(f"MetaData Info: Target zone '{self._target_zone_name}' metadata updated successfully. Seek position: {self._metadata['seek_position']}, State: {self._metadata['state']}")

        else:
            # If zone_data is None, it means our target zone might have stopped playing or been removed.
            print(f"MetaData Info: Target zone '{self.target_zone_name}' state is no longer available. Resetting metadata.")
            self._initialize_state() # Reset all metadata to initial state

        # Check for state changes based on the new metadata
        self.track_changed = self.track != old_track
        self.play_changed = self.play_status != old_play_status
        
        # if self.track_changed:
        #     print(f"ZoneMetadata Update: Track changed for {self.target_zone_name}. New Track: {self.track}")
        # if self.play_changed:
        #      print(f"ZoneMetadata Update: Play status changed to {self.play_status}.")


    def __str__(self) -> str:
        """Returns a string representation of the current metadata cache."""
        text = "\n--- Current Metadata Cache ---\n"
        for k, v in self._metadata.items():
            text += f"{k}: {v}\n"
        return text

class RoonEndpoint(MetaData):
    """
    Controller class responsible for connecting to Roon API, 
    handling discovery, and managing metadata updates via callbacks.
    Inherits state tracking from MetaData.
    """
    def __init__(self, events, target_name: str = 'Den', maxwh: Tuple[int, int] = (400, 400)):
        super().__init__(roonapi=None, maxwh=maxwh) # Initialize parent first with dummy API object
        self.events = events
        self.image_cache: Dict[str, str] = {}

        self.appinfo: Dict[str, str] = {
            "extension_id": "Pyvisualiser",
            "display_name": "Pyvisualiser",
            "display_version": "1.0.0",
            "publisher": "SRC Visualiser",
            "email": "baloothebear4@example.com" 
        }
        
        self._target_zone_name = target_name

        try:
            core_id, token = self._connect_to_roon()

            # Use Discovery to find the server IP/Port for the core_id
            print(f"Connecting to Roon Core {core_id}...")
            discover = RoonDiscovery(core_id)
            server = discover.first()
            discover.stop()

            if server:
                # Initialize the main API connection
                self.roon = RoonApi(self.appinfo, token, server[0], server[1], True)
                self._initialize_state()
                self.set_target_zone(target_name)
                self.roon.register_state_callback(self.roon_callback)
                print(f"Roon Initialization: Successfully connected to '{target_name}'.")
            else:
                # If cached server not found, we may need to re-auth
                print("Roon Initialization Warning: Cached Core not found on network.")
                self.roon = None
                self._initialize_state()
                self._target_zone = ''

        except (ConnectionError, AttributeError) as e:
            print(f"\n Roon failed to initialise due to connection error: {e}") 
            # If setup fails, self.roon remains None or an invalid object, which is safer than crashing.


    def _load_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """Safely attempts to read core ID and token from local files."""
        try:
            core_id = open("my_core_id_file").read().strip()
            token = open("my_token_file").read().strip()
            print("Roon Initialization: Credentials loaded successfully.")
            return core_id, token
        except FileNotFoundError:
            print("Roon Initialization Warning: Credential files not found. Must authorize first.")
            return None, None

    def _authenticate(self) -> Tuple[Optional[str], Optional[str]]:
        """Handles the flow of discovering servers and obtaining authorization."""
        print("\n--- Starting Roon Discovery & Authentication ---")
        discover = RoonDiscovery(None) # Passing None first to discover all available instances
        servers: List[Tuple[str, str]] = discover.all()
        discover.stop()

        if not servers:
            raise ConnectionError("No Roon services found on the network.")

        print(f"Found {len(servers)} potential Roon servers.")
        
        apis: List[RoonApi] = []
        for server in servers:
             # Create temporary APIs for checking tokens/auth status
            try:
                api = RoonApi(self.appinfo, None, server[0], server[1], False) 
                apis.append(api)
            except Exception:
                continue

        auth_api: Optional[RoonApi] = None
        print("Waiting for authorization on Roon display (Check Settings/Extensions)...")
        
        # Poll until at least one API has a valid token
        wait_start = time.time()
        while (time.time() - wait_start < 60):
            auth_api = next((api for api in apis if api.token is not None), None)
            if auth_api:
                break
            time.sleep(2)
        
        if not auth_api:
             raise ConnectionError("Timeout waiting for Roon authorization.")

        print("\n--- Authorization Successful ---")
        print(f"Connected to Roon Core: {auth_api.core_name} ({auth_api.core_id})")

        core_id, token = auth_api.core_id, auth_api.token

        # Cleanup temporary API instances
        for api in apis:
            try:
                api.stop()
            except Exception:
                pass # Ignore stop errors on already stopped APIs

        # Save credentials for next run
        with open("my_core_id_file", "w") as f:
            f.write(core_id)
        with open("my_token_file", "w") as f:
            f.write(token)

        return core_id, token


    def _connect_to_roon(self) -> Tuple[str, str]:
        """Uses authentication flow to establish the necessary credentials."""
        core_id, token = self._load_credentials()
        if not core_id or not token:
            core_id, token = self._authenticate()
        return core_id, token

    def metadata_stop(self):
        """Gracefully stops the underlying Roon API connection."""
        if self.roon:
            print("Stopping Roon connection.")
            try:
                self.roon.stop()
            except Exception as e:
                print(f"Error stopping Roon API: {e}")

    def startup(self) -> Tuple[str, str]:
        """Public entry point to initiate authentication and setup."""
        # This method now acts as the primary call to trigger auth flow if needed.
        return self._connect_to_roon()

    def roon_callback(self, event: str, changed_zone: Any):
            """Callback executed when Roon reports a change in any zone/output."""

            # Safely extract zone_ids as strings regardless of the payload structure
            zone_ids_to_update: List[str] = []
            
            if isinstance(changed_zone, list):
                for item in changed_zone:
                    if isinstance(item, dict) and 'zone_id' in item:
                        zone_ids_to_update.append(item['zone_id'])
                    elif isinstance(item, str):
                        zone_ids_to_update.append(item)
            elif isinstance(changed_zone, dict) and 'zone_id' in changed_zone:
                zone_ids_to_update.append(changed_zone['zone_id'])
            elif isinstance(changed_zone, str):
                zone_ids_to_update.append(changed_zone)

            if not zone_ids_to_update:
                print(f"Roon Callback Warning: Unhandled changed_zone format for event '{event}': {changed_zone}")
                return # Don't proceed if we can't get zone IDs
                
            self.update(zone_ids_to_update)

            # print(f"\n[Roon Callback] Event: {event}")

            # 2. Emit high-level application events based on state changes detected during update()
            try:
                if self.track_changed:
                    # print("Roon Callback: Detected track change, emitting 'new_track' event.")
                    self.events.Metadata('new_track')

                if self.play_changed:
                    # print(f"Roon Callback: Detected play status change to {self.play_status}, emitting appropriate event.")
                    if self.playing:
                        self.events.Metadata('start')
                    else:
                        self.events.Metadata('stop')
            except Exception as e:
                print(f"Roon Callback Error: {e}")

    # def roon_callback(self, event: str, changed_zone: Any):
    #     """Callback executed when Roon reports a change in any zone/output."""

    #     # The changed_zone parameter can be a list of zone_ids or a single zone object
    #     zone_ids_to_update: List[str] = []
    #     if isinstance(changed_zone, list):
    #         zone_ids_to_update = changed_zone
    #     elif isinstance(changed_zone, dict) and 'zone_id' in changed_zone:
    #         zone_ids_to_update = [changed_zone['zone_id']]
    #     else:
    #         print(f"Roon Callback Warning: Unhandled changed_zone format for event '{event}': {changed_zone}")
    #         return # Don't proceed if we can't get zone IDs
    #     self.update(zone_ids_to_update)

    #     print(f"\n[Roon Callback] Event: {event}")

    #     # 2. Emit high-level application events based on state changes detected during update()
    #     try:
    #         if self.track_changed:
    #             # print("Roon Callback: Detected track change, emitting 'new_track' event.")
    #             self.events.Metadata('new_track')

    #         if self.play_changed:
    #             # print(f"Roon Callback: Detected play status change to {self.play_status}, emitting appropriate event.")
    #             if self.playing:
    #                 self.events.Metadata('start')
    #             else:
    #                 self.events.Metadata('stop')
    #     except Exception as e:
    #         print(f"Roon Callback Error: {e}")

    # def roon_callback(self, event, changed_zone):
    #     """Call when something changes in roon."""

    #     self.update(changed_zone)

    #     """ multiple events can be triggered from one event update """
    #     try:
    #         if self.track_changed:
    #             # print("track changed")
    #             self.events.Metadata('new_track')

    #         if self.play_changed:
    #             # print("play changed")
    #             if self.playing:
    #                 self.events.Metadata('start')
    #             else:
    #                 self.events.Metadata('stop')
    #     except Exception as e:
    #         print(f"\n Roon callback Error: {e}") 

        # print("Roon.roon_callback> event:>> %s << changed_zone: %s --> play changed %s, track changed %s" % (event, changed_zone, self.play_changed, self.track_changed))


"""
Test code
"""
# Pygame setup
# pygame.init()
# pygame.display.set_caption('Roon Album Art Display')
# screen = pygame.display.set_mode((1000, 1000))
# font = pygame.font.Font(None, 36)
#
# events = Events('Roon')
#
#
# #RoonAPI startup
# roon = Roon(events)
#
# def RoonAction(e):
#     print('RoonAction> event %s' % e)
#     print('RoonAction> Meta data: ', roon.artist, roon.track, roon.album, roon.playing, roon.elapsedpc )
#
# try:
#     # time.sleep(3)
#     events.Roon      += RoonAction     # respond to a new sample, or audio silence
#     while True:
#         for event in pygame.event.get():
#
#             """ Update display with image """
#             # print()
#             image = pygame.image.load(roon.album_art)
#             album_art = pygame.transform.scale(image, (1000, 1000))
#
#             # Display album art in Pygame window
#             screen.blit(album_art, (0, 0))
#
#             # Update Pygame window
#             pygame.display.flip()
#
#
#             if event.type == pygame.QUIT:
#                 roon.stop()
#                 pygame.quit()
#                 exit()
#
#             time.sleep(1/60)
#
# except KeyboardInterrupt:
#     roon.stop()
#     pygame.quit()
