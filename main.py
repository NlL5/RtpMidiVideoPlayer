import sys
import threading
import time
import uuid
from typing import Dict

import pywinctl
import vlc
from pymidi import server


class Player:
    player: vlc.MediaListPlayer = None
    window: pywinctl.BaseWindow = None

    def __init__(self, player, window):
        self.player = player
        self.window = window


# https://github.com/mik3y/pymidi#using-in-another-project
class PlayerHandler(server.Handler):
    player_1: Player = None
    player_2: Player = None
    current: Player = None
    playerKey: Dict[int, Player] = {}

    def __init__(self, player_1, player_2):
        self.player_1 = player_1
        self.player_2 = player_2
        self.current = self.player_1

    def on_peer_connected(self, peer):
        print('Peer connected: {}'.format(peer))

    def on_peer_disconnected(self, peer):
        print('Peer disconnected: {}'.format(peer))

    def on_midi_commands(self, peer, command_list):
        for command in command_list:

            if command.command != 'note_on' and command.command != 'note_off':
                continue
            key = command.params.key
            velocity = command.params.velocity
            channel = command.channel
            index = int(channel) * 100 + int(key)

            if command.command == 'note_on' and velocity > 0:
                self.current = self.player_1 if self.current == self.player_2 else self.player_2
                self.current.player.play_item_at_index(index)
                self.playerKey[index] = self.current

                def wait_and_front():
                    time.sleep((velocity - 1) * 0.1)
                    self.current.window.activate()
                    # other.player.pause()

                t = threading.Thread(target=wait_and_front)
                t.start()
            elif index in self.playerKey and not (command.command == 'note_off' and velocity == 127):
                player = self.playerKey[index]
                del self.playerKey[index]

                other = self.player_1 if player == self.player_2 else self.player_2
                other.window.activate()
                self.current = other
                player.player.pause()

            print('Someone hit command {} the key {} with velocity {}'.format(command.command, key, velocity))


def spawn_player():
    window_title = str(uuid.uuid4())
    args = ['--input-repeat=999999', '--no-video-title-show', '--no-audio', '--video-title=' + window_title, '--vout=gles2']

    instance = vlc.Instance(args)
    playlist_media = instance.media_new(sys.argv[1])
    playlist_media.parse()  # deprecated but nice

    # Initialize background player
    player = instance.media_list_player_new()
    player.get_media_player().set_fullscreen(True)
    player.set_media_list(playlist_media.subitems())
    #player.play()  # open window ...
    player.play_item_at_index(2)
    time.sleep(1)
    #player.pause()  # ... but do not play
    #time.sleep(1)

    windows = pywinctl.getWindowsWithTitle(window_title)
    if windows:
        window = windows[0]
    else:
        raise Exception('Did not find window ' + window_title + '! Check the video title')

    return Player(player, window)

if __name__ == '__main__':

    player1 = spawn_player()
    player2 = spawn_player()
    player1.window.activate()
    player2.player.pause()

    # Start RTP server and accept all incoming connection requests
    rtpMidiServer = server.Server([('0.0.0.0', 5005)])
    rtpMidiServer.add_handler(PlayerHandler(player1, player2))
    rtpMidiServer.serve_forever()
