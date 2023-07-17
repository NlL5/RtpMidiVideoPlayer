import os
import sys
import time

import vlc
from pymidi import server


# https://github.com/mik3y/pymidi#using-in-another-project
class PlayerHandler(server.Handler):
    background_player = None
    foreground_player = None

    def __init__(self, background_player, foreground_player):
        self.background_player = background_player
        self.foreground_player = foreground_player

    def on_peer_connected(self, peer):
        print('Peer connected: {}'.format(peer))

    def on_peer_disconnected(self, peer):
        print('Peer disconnected: {}'.format(peer))

    def on_midi_commands(self, peer, command_list):
        for command in command_list:
            if command.command == 'note_on':
                key = command.params.key
                velocity = command.params.velocity
                player = self.background_player if command.channel == 0 else self.foreground_player
                player.play_item_at_index(int(key) * 100 + int(velocity))

                print('Someone hit the key {} with velocity {}'.format(key, velocity))


if __name__ == '__main__':
    background_instance = vlc.Instance('--input-repeat=999999', '--no-video-title-show', '--no-audio',
                                       '--vout=gles2')  # , '--no-autoscale'

    # Load playlist
    playlist_media = background_instance.media_new(sys.argv[1])
    playlist_media.parse()  # deprecated but nice

    # Initialize background player
    background_player = background_instance.media_list_player_new()
    background_player.get_media_player().set_fullscreen(True)
    # background_player.get_media_player().set_renderer()
    # background_player.get_media_player().video_set_scale(1)
    # background_player.get_media_player().video_set_aspect_ratio('1:1')
    background_player.set_media_list(playlist_media.subitems())
    background_player.play()  # start with first element

    foreground_instance = vlc.Instance('--input-repeat=999999', '--no-video-title-show', '--no-audio',
                                       '--vout=gles2')  # , '--no-autoscale'
    playlist_media = foreground_instance.media_new(sys.argv[2])
    playlist_media.parse()  # deprecated but nice

    # initialize foreground player
    foreground_player = foreground_instance.media_list_player_new()
    foreground_player.get_media_player().set_fullscreen(True)
    foreground_player.set_media_list(playlist_media.subitems())

    # Start RTP server and accept all incoming connection requests
    rtpMidiServer = server.Server([('0.0.0.0', 5004)])
    rtpMidiServer.add_handler(PlayerHandler(background_player, foreground_player))
    rtpMidiServer.serve_forever()
