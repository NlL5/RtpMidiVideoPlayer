# Raspberry installation

## config.txt
```
disable_overscan=1
dtoverlay=rpivid-v4l2
```
Does not work for video playback: dtoverlay=vc4-fkms-v3d,cma-256

## basic config
```
$ touch ./ssh
$ echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=DE

network={
    ssid=\"Die wilde Wutz\"
    psk=\"«your_PSK»\"
    key_mgmt=WPA-PSK
}" > ./wpa_supplicant.conf
```

## Setup in the raspberry
```
$ sudo apt update && sudo apt upgrade
$ sudo apt install vlc python3-pip python3-tk git vim nextcloud-desktop nextcloud-cmd
$ pip install pipenv

$ git clone git@github.com:NlL5/RtpMidiVideoPlayer.git
$ cd ./RtpMidiVideoPlayer
$ pipenv install
```

For Raspberry Pi without display manager, you can use the services.
For a Pi _with_ display manager, you can use the autostart entries. Put the *.desktop files into:
```
ln -s -r services/com.nextcloud.desktopclient.nextcloud.desktop ~/.config/autostart/
ln -s -r services/video-player.desktop ~/.config/autostart/
```

# Starting
```
$ pipenv run python ./main.py background_playlist.m3u foreground_playlist.m3u
```