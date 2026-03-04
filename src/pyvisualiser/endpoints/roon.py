
from roonapi import RoonApi, RoonDiscovery
import pygame
import requests
from io import BytesIO
import os

from events       import Events
import time



# SONG_KEYS       = ('file', 'artist', 'album', 'title', 'comment', 'pos', 'id')
# STATUS_KEYS     = ('repeat', 'random', 'single', 'consume', 'playlist', 'playlistlength', \
#                     'mixrampdb', 'state', 'song', 'songid', 'time', 'elapsed', 'bitrate', \
#                     'duration', 'audio', 'nextsong', 'nextsongid')

class RoonMetaData:
    """
        Data model class to manage the metadata captured from MPD
    """

    ZONE_KEYS        = ( 'zone_id', 'display_name', 'state', 'now_playing', 'seek_position')
    NOW_PLAYING_KEYS = ( 'seek_position', 'length', 'one_line', 'two_line', 'three_line', 'image_key', 'artist_image_keys')
    DEFAULT_URL      = 'https://cdn10.bigcommerce.com/s-x8dfmo/products/8700/images/31754/Thunderbird-2-in-Thunderbirds-Premium-Photograph-and-Poster-1015146__92732.1432428503.1280.1280.jpg?c=2'
    DEFAULT_URL      =  None

    def __init__(self, roonapi, maxwh):
        self.clear_metadata()
        self.roon = roonapi
        self.maxwh = maxwh
        # print("RoonMetaData.__init__> OK")

    def clear_metadata(self):
        self._metadata = { k : "" for k in RoonMetaData.ZONE_KEYS }
        self._metadata['now_playing'] = { k : "" for k in RoonMetaData.NOW_PLAYING_KEYS }
        self._metadata['now_playing']['three_line']={'line1':'', 'line2':'', 'line3':''}
        self._play_changed, self._track_changed = False, False
        self._album_art_url        =  RoonMetaData.DEFAULT_URL
        self._artist_art_url       =  RoonMetaData.DEFAULT_URL
        self._target_zone          =  'pre3'


    # @property
    def album_art(self):
        try:
            self._album_art_url        = self.roon.get_image(self._metadata['now_playing']['image_key'], width=self.maxwh[1], height=self.maxwh[1]) if self._metadata['now_playing']['image_key'] !='' else RoonMetaData.DEFAULT_URL
            return self._album_art_url
        except:
            return RoonMetaData.DEFAULT_URL

    # @property
    def artist_art(self):  #Just take the first one
        try:
            self._artist_art_url       =  self.roon.get_image(self._metadata['now_playing']['artist_image_keys'][0], width=self.maxwh[0], height=self.maxwh[1]) if 'artist_image_keys' in self._metadata['now_playing'] else RoonMetaData.DEFAULT_URL
            return self._artist_art_url
        except:
            return RoonMetaData.DEFAULT_URL

    # @property
    def artist(self):
        return self._metadata['now_playing']['three_line']['line2']

    # @property
    def album(self):
        return self._metadata['now_playing']['three_line']['line3']

    # @property
    def track(self):
        # print(self._metadata['now_playing'])
        if 'three_line' in self._metadata['now_playing']:
            track = self._metadata['now_playing']['three_line']['line1']
        else:
            track = ""
        return track

    @property
    def playing(self):
        return self._metadata['state']=='playing'

    @property
    def play_status(self):
        return self._metadata['state']

    @property
    def zone_name(self):
        return self._metadata['display_name']

    @property
    def elapsedpc(self):
        try:
            return self.elapsed/self.duration
        except:
            return 0.0

    @property
    def duration(self):
        try:
            return float(self._metadata['now_playing']['length'])
        except:
            # print("RoonMetaData> - WARN - duration not available")
            return 0.0

    @property
    def elapsed(self):
        try:
            return float(self._metadata['seek_position'])
        except:
            # print("RoonMetaData> - WARN - elapsed not available")
            return 0.0

    @property
    def remaining(self):
        return self.duration - self.elapsed

    @property
    def track_changed(self):
        return self._track_changed

    @track_changed.setter
    def track_changed(self, val):
        self._track_changed = val

    @property
    def play_changed(self):
        return self._play_changed

    @play_changed.setter
    def play_changed(self, val):
        self._play_changed = val

    @property
    def metadata(self):
        return self._metadata

    @property
    def zone(self):
        return self.roon.zone_by_name(self._target_zone_name)

    @property
    def target_zone_name(self):
        return self._target_zone_name

    def set_target_zone(self, name):
        target_zone = self.roon.zone_by_name(name)
        if target_zone == None:
            print("RoonMetaData> %s zone does not exist" % name)
            self._target_zone_name = 'None'
        else:
            self._target_zone = target_zone['zone_id']
            self._target_zone_name = name
            print("RoonMetaData> target zone %s set, id %s" % (self._target_zone_name, self._target_zone))

    @property
    def target_zone_id(self):
        return self._target_zone

    def update(self, changed_zoneids):
        """ updates with new meta data and returns a list of the keys that have changed
            Roon can be playing from multiple rooms, so collect the data for the room being displayed
            Events = ("zones_changed", "zones_seek_changed", "outputs_changed")

            {'zone_id': '16012f7401c058d4b5c791c852ed544791e6',
              'display_name': 'Den',
              'outputs': [{'output_id': '17012f7401c058d4b5c791c852ed544791e6', 'zone_id': '16012f7401c058d4b5c791c852ed544791e6', 'can_group_with_output_ids': ['170146b4f3155666f6da486b52f3e0307e69', '1701d749a336232183dfb21c86dccf968c8c', '17011ad28566c7bd306c8230bbea207c5e00', '1701261d747196dd4beadd1b0d6aaba4b6e9', '170100524e74dadf8ccd26ecb9a849c1ce71', '17012f7401c058d4b5c791c852ed544791e6'],
                          'display_name': 'Den',
                          'volume': {'type': 'number', 'min': 0, 'max': 100, 'value': 9, 'step': 1, 'is_muted': False, 'hard_limit_min': 0, 'hard_limit_max': 100, 'soft_limit': 100},
                          'source_controls': [{'control_key': '1', 'display_name': 'ARCAM USB Audio 2.0', 'supports_standby': False, 'status': 'indeterminate'}]}],
              'state': 'playing',
              'is_next_allowed': True,
              'is_previous_allowed': True,
              'is_pause_allowed': True,
              'is_play_allowed': False,
              'is_seek_allowed': True,
              'queue_items_remaining': 1,
              'queue_time_remaining': 49,
              'settings': {'loop': 'disabled', 'shuffle': False, 'auto_radio': True},
              'now_playing': {'seek_position': 501, 'length': 567, 'one_line': {'line1': 'Dusk - Gidge'}, 'two_line': {'line1': 'Dusk', 'line2': 'Gidge'}, 'three_line': {'line1': 'Dusk', 'line2': 'Gidge', 'line3': 'Autumn Bells'}, 'image_key': 'eb3298cff0b0db6f366fe1818ea43f09', 'artist_image_keys': ['4380b4806c9b8c49426de5fe39f20e37']},
              'seek_position': 518
             }
        """

        old_track       = self.track
        old_play_status = self.play_status

        if self.target_zone_id in changed_zoneids:
            for key in RoonMetaData.ZONE_KEYS:
                if key in self.zone:
                    self._metadata[key] = self.zone[key]

            self.track_changed  = self.track != old_track
            self.play_changed   = self.play_status != old_play_status
            if self.track_changed:
                # self._album_art_url       = self.roon.get_image(self._metadata['now_playing']['image_key'], width=self.maxh, height=self.maxh) if self._metadata['now_playing']['image_key'] !='' else RoonMetaData.DEFAULT_URL
                # print("ZoneMetadata.update> changed for Zone %s, Play %s, Track %s" % (self.target_zone_name, self.play_changed, self.track_changed ))
                print("ZoneMetadata.update> now playing: Zone %s Track %s > Artist %s Album %s" % (self.target_zone_name, self.track, self.artist, self.album))
        else:
            for zone_id in changed_zoneids:
                if zone_id in self.roon.zones:
                    pass
                    # print("ZoneMetadata.update> metadata update for non target zone: name %s target %s" % (self.roon.zones[zone_id]['display_name'], self.target_zone_name))
                else:
                    # pass
                    print("ZoneMetadata.update> metadata update for outputs on %s" % (self.roon.outputs[zone_id]['display_name']))

    def __str__(self):
        text = ""
        for i, k in enumerate(self._metadata):
            text  += "%s : %s,  " % (k, self._metadata[k])
        return text

class Roon(RoonMetaData):
    def __init__(self, events, target_name='Den', maxwh=(400,400)):
        self.events = events
        self.image_cache = {}

        self.appinfo = {
            "extension_id": "Pyvisualiser",
            "display_name": "Pyvisualiser",
            "display_version": "1.0.0",
            "publisher": "SRC Visualiser",
            "email": "baloothebear4@example.com" }

        try:
            core_id = open("my_core_id_file").read()
            token   = open("my_token_file").read()
        except OSError:
            print("Please authorise first...")
            core_id, token = self.startup()

        self.discover = RoonDiscovery(core_id)
        server        = self.discover.first()
        self.discover.stop()

        RoonMetaData.__init__(self, RoonApi(self.appinfo, token, server[0], server[1], True), maxwh)
        self.set_target_zone(target_name)

        # get all zones (as dict)
        print("Roon.__init__>> Connecting with server for metadata on output>>>", target_name)
        # print(self.roon.host)
        # print(self.roon.core_name)
        # print(self.roon.core_id)
        self.roon.register_state_callback(self.roon_callback) # , id_filter=[self.target_zone_id])

    def metadata_stop(self):
        self.roon.stop()

    def startup(self):
        print("Discover Roon servers and connect")
        discover = RoonDiscovery(None)
        servers = discover.all()

        # print("Shutdown discovery")
        discover.stop()


        apis = [RoonApi(self.appinfo, None, server[0], server[1], False) for server in servers]
        print("Found the following servers & apis", servers, apis)

        auth_api = []
        while len(auth_api) == 0:
            print("Waiting for authorisation on Roon display -> settings/extensions", )
            time.sleep(1)
            auth_api = [api for api in apis if api.token is not None]

        api = auth_api[0]

        print("Got authorisation", api)
        print(api.host)
        print(api.core_name)
        print(api.core_id)

        print("Shutdown apis")
        for api in apis:
            api.stop()

        # This is what we need to reconnect
        core_id = api.core_id
        token = api.token

        with open("my_core_id_file", "w") as f:
            f.write(api.core_id)
        with open("my_token_file", "w") as f:
            f.write(api.token)

        return core_id, token

    def roon_callback(self, event, changed_zone):
        """Call when something changes in roon."""

        self.update(changed_zone)

        """ multiple events can be triggered from one event update """
        try:
            if self.track_changed:
                # print("track changed")
                self.events.Metadata('new_track')

            if self.play_changed:
                # print("play changed")
                if self.playing:
                    self.events.Metadata('start')
                else:
                    self.events.Metadata('stop')
        except Exception as e:
            print(f"\n Roon callback Error: {e}") 

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
