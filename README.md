# Raspberry installation

## config.txt
disable_overscan=1
dtoverlay=rpivid-v4l2

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
$ sudo apt install nextcloud-cmd vlc python3-pip git vim
$ pip install pipenv

$ git clone git@github.com:NlL5/RtpMidiVideoPlayer.git
$ cd ./RtpMidiVideoPlayer
```

# Starting
```
$ pipenv run python ./main.py /home/flammenmeer/nextcloud/Live-Beamer/playlist.xspf
```