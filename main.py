import os
import sys
import threading
import time
import uuid

import pywinctl
import vlc
from pymidi import server


# https://github.com/mik3y/pymidi#using-in-another-project
class PlayerHandler(server.Handler):
    player_1 = None
    player_2 = None
    current = None

    def __init__(self, player_1, player_2):
        self.player_1 = player_1
        self.player_2 = player_2
        self.current = self.player_2

    def on_peer_connected(self, peer):
        print('Peer connected: {}'.format(peer))

    def on_peer_disconnected(self, peer):
        print('Peer disconnected: {}'.format(peer))

    def on_midi_commands(self, peer, command_list):
        for command in command_list:
            if command.command == 'note_on':
                key = command.params.key
                velocity = command.params.velocity
                other = self.current
                self.current = self.player_1 if self.current == self.player_2 else self.player_2
                self.current[0].play_item_at_index(int(key) * 100 + int(velocity))

                def wait_and_front():
                    time.sleep(command.channel)
                    self.current[1].activate()
                    other[0].pause()

                t = threading.Thread(target=wait_and_front)
                t.start()

                print('Someone hit command {} the key {} with velocity {}'.format(key, velocity, command.command))


def spawn_player():
    window_title = str(uuid.uuid4())
    args = ['--input-repeat=999999', '--no-video-title-show', '--no-audio', '--vout=gles2']  # , '--no-autoscale'
    args = ['--input-repeat=999999', '--no-video-title-show', '--no-audio', '--video-title=' + window_title]

    instance = vlc.Instance(args)
    playlist_media = instance.media_new(sys.argv[1])
    playlist_media.parse()  # deprecated but nice

    # Initialize background player
    player = instance.media_list_player_new()
    player.get_media_player().set_fullscreen(True)
    player.set_media_list(playlist_media.subitems())
    player.play()  # open window ...
    time.sleep(1)
    player.pause()  # ... but do not play

    windows = pywinctl.getWindowsWithTitle(window_title)
    if windows:
        window = windows[0]
    else:
        raise Exception('Did not find window ' + window_title + '! Check the video title')

    return player, window

if __name__ == '__main__':

    player1 = spawn_player()
    player2 = spawn_player()
    player2[0].play()

    # Start RTP server and accept all incoming connection requests
    rtpMidiServer = server.Server([('0.0.0.0', 5004)])
    rtpMidiServer.add_handler(PlayerHandler(player1, player2))
    rtpMidiServer.serve_forever()
