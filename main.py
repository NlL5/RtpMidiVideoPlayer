import sys
import vlc
from pymidi import server


# https://github.com/mik3y/pymidi#using-in-another-project
class PlayerHandler(server.Handler):
    player = None

    def __init__(self, player):
        self.player = player

    def on_peer_connected(self, peer):
        print('Peer connected: {}'.format(peer))

    def on_peer_disconnected(self, peer):
        print('Peer disconnected: {}'.format(peer))

    def on_midi_commands(self, peer, command_list):
        for command in command_list:
            if command.command == 'note_on':
                key = command.params.key
                velocity = command.params.velocity
                print('Someone hit the key {} with velocity {}'.format(key, velocity))
                self.player.play_item_at_index(key*100 + velocity)


if __name__ == '__main__':
    # Load playlist
    playlist_media = vlc.Media(sys.argv[1])
    playlist_media.parse()  # deprecated but nice

    player = vlc.MediaListPlayer()
    player.set_media_list(playlist_media.subitems())
    player.vlm_set_loop("Flammenmeer_Banner", True)
    player.play()  # start with first element

    rtpMidiServer = server.Server([('0.0.0.0', 5004)])
    rtpMidiServer.add_handler(PlayerHandler(player))
    rtpMidiServer.serve_forever()
