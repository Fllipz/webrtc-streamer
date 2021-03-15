# webrtc-streamer

## Intorduction 

This repo describes how to setup janus webcam stream over the Husarnet VPN using docker.

### General comments

1. Due to the way janus handles networking You may need to disable mDNS in your browser in order to view the stream.

- On FireFox open URL: `about:config` and setup:
```
mdns -> false
media.peerconnection.ice.obfuscate_host_addresses -> false
```

2. This example is capable of using one of two codecs: H264 or VP8. H264 is used be default, in order to change it to VP8 You need to set the env variable CODEC when starting the container as such: `--env CODEC="vp8"`

3. During testing I used a webcam which ofered a feed encoded using hte H264 codec and as such there was no need to reencode the stream in ffmpeg, lowering latency. However when streaming VP8 codec there is a need for encoding the stream in ffmpeg which makes latency higher. During testing vlatency vaules for H264 codec were around 400ms whereas for tge VP8 codec it was cloaser to 1s.


## Build an Image

Ensure bash scrpits are executable:

```bash
sudo chmod +x init-container.sh
```

Then build an image:

```bash
sudo docker build -t webrtc-streamer .
```

### Raspberry Pi specific

On Raspberry Pi OS you may see a signature error when trying to build the image in order to solve this you need to manually install the latest  libseccomp2.

To do so go to: https://packages.debian.org/sid/libseccomp2 and download armhf version.

Then install it as such:

```bash
sudo dpkg -i libseccomp2_2.4.3-1+b1_armhf.deb
```

## Start a Container

### Create `.env` File:

```
HOSTNAME=webrtc-streamer-1
JOINCODE=fc94:b01d:1803:8dd8:3333:2222:1234:1111/xxxxxxxxxxxxxxxxx
CODEC=H264
CAM_AUDIO_CHANNELS=2
```

description:
- `HOSTNAME='docker-vpn-1'` - is an easy to use hostname, that you can use instead of Husarnet IPv6 addr to access your container over the internet
- `JOINCODE='fc94:b01d:1803:8dd8:3333:2222:1234:1111/xxxxxxxxxxxxxxxxx'` - is an unique Join Code from your Husarnet network. You will find it at **https://app.husarnet.com -> choosen network -> `[Add element]` button ->  `join code` tab**
- `CODEC=H264` - codec for videostream. Available opitons: `H264`, and `VP8`. If your web camera already provide h.264 stream, then it will be bypassed over the transcoder saving computing power and lowering latency.
- `CAM_AUDIO_CHANNELS=2` - number of audio channels associated with your web camera. TL;DR if there is no audio change this line to `CAM_AUDIO_CHANNELS=1` .

### Start container
```bash
sudo docker run --rm -it \
--env-file ./.env \
--volume webrtc-streamer_v:/var/lib/husarnet \
--device /dev/net/tun \
--device /dev/video0:/dev/video0  \
--device /dev/snd \
--cap-add NET_ADMIN \
--sysctl net.ipv6.conf.all.disable_ipv6=0 \
webrtc-streamer
```

description:
- `--volume webrtc_streamer_v:/var/lib/husarnet` - you need to make `/var/lib/husarnet` as a volume to preserve it's state for example if you would like to update the image your container is based on. If you would like to run multiple containers on your host machine remember to provide unique volume name for each container (in our case `HOSTNAME-v`).
- `--device /dev/video0:/dev/video0` - you need to give the container access to your webcam in this case /dev/video0 which will be referenced in the pipline.sh script as /dev/video0

## Important Notes

### H264 support detection

Server detects if video device supports h264 encoded feed if so it makes ffmpeg use the h264 feed from device otherwise ffmpeg uses the raw camera feed. The h264 codec support on camera matters in order to provide low latency, as in this case ffmpeg does no reencoding which significantly lowers latency.

### Mock camera feed for testing

If you do not wish to use a webcam at some point there is a possibility to tell docker to use a video feed generated by gstreamer instead of webcam, to do so just start the container as such:

```bash
sudo docker run --rm -it \
--env HOSTNAME='webrtc-streamer-1' \
--env JOINCODE='fc94:b01d:1803:8dd8:3333:2222:1234:1111/xxxxxxxxxxxxxxxxx' \
--env TEST='true' \
-v webrtc-streamer_v:/var/lib/husarnet \
-v /dev/net/tun:/dev/net/tun \
--device=/dev/video0:/dev/video0  \
--cap-add NET_ADMIN --sysctl net.ipv6.conf.all.disable_ipv6=0 \
webrtc-streamer
```

This overrides the TEST environment variable and makes the init-container.sh scrpit use mock pipelines. Gstreamer will generate a feed of a ball moving around the screen and forward it in place of camera feed.

### P2P Connection

In order to achieve low latency we take advantage of the Husarnet P2P connection establishment. If the stream is accessed from a host for which our connection is not P2P the quality of stream will degrade. You can check your connection status using:

```bash
sudo husarnet status
```

The demo site will also display a warning if it detects lack of P2P connection. In order to solve connection issues go to:

https://husarnet.com/docs/tutorial-troubleshooting

### Changing stream parameters

The demo page allows user to change stream parameters from default ones. 

In order to access possible stream options server runs and parses several system commands, same goes for changing stream parameters.

As such this process may fail if You use a differen webcam which outputs data in different format.
During testing we used a Logitech C920 camera.

## Result

Runing above commands should result in the following output:

```bash
sysctl: setting key "net.ipv6.conf.lo.disable_ipv6": Read-only file system

⏳ [1/2] Initializing Husarnet Client:
waiting...
waiting...
waiting...
waiting...
success

🔥 [2/2] Connecting to Husarnet network as "web-streamer":
[9929599] joining...
[9931602] joining...
done

*******************************************
💡 Tip
To test a WebRTC stream visit:
👉 http://[fc94:40d4:4574:7b91:da05:db42:45bb:f6ab]:80/ 👈
in your web browser 💻
*******************************************

Janus commit: caaba91081ba8e5578a24bca1495a8572f08e65c
Compiled on:  Wed Feb 24 11:32:15 UTC 2021

Logger plugins folder: /opt/janus/lib/janus/loggers
[WARN] 	Couldn't access logger plugins folder...
---------------------------------------------------
  Starting Meetecho Janus (WebRTC Server) v0.11.1
---------------------------------------------------

Checking command line arguments...
Debug/log level is 0
Debug/log timestamps are disabled
Debug/log colors are enabled
ffmpeg version 4.3.1-4ubuntu1 Copyright (c) 2000-2020 the FFmpeg developers
  built with gcc 10 (Ubuntu 10.2.0-9ubuntu2)
  configuration: --prefix=/usr --extra-version=4ubuntu1 --toolchain=hardened --libdir=/usr/lib/arm-linux-gnueabihf --incdir=/usr/include/arm-linux-gnueabihf --arch=arm --enable-gpl --disable-stripping --enable-avresample --disable-filter=resample --enable-gnutls --enable-ladspa --enable-libaom --enable-libass --enable-libbluray --enable-libbs2b --enable-libcaca --enable-libcdio --enable-libcodec2 --enable-libdav1d --enable-libflite --enable-libfontconfig --enable-libfreetype --enable-libfribidi --enable-libgme --enable-libgsm --enable-libjack --enable-libmp3lame --enable-libmysofa --enable-libopenjpeg --enable-libopenmpt --enable-libopus --enable-libpulse --enable-librabbitmq --enable-librsvg --enable-librubberband --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libspeex --enable-libsrt --enable-libssh --enable-libtheora --enable-libtwolame --enable-libvidstab --enable-libvorbis --enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx265 --enable-libxml2 --enable-libxvid --enable-libzmq --enable-libzvbi --enable-lv2 --enable-omx --enable-openal --enable-opencl --enable-opengl --enable-sdl2 --enable-pocketsphinx --enable-libdc1394 --enable-libdrm --enable-libiec61883 --enable-chromaprint --enable-frei0r --enable-libx264 --enable-shared
  libavutil      56. 51.100 / 56. 51.100
  libavcodec     58. 91.100 / 58. 91.100
  libavformat    58. 45.100 / 58. 45.100
  libavdevice    58. 10.100 / 58. 10.100
  libavfilter     7. 85.100 /  7. 85.100
  libavresample   4.  0.  0 /  4.  0.  0
  libswscale      5.  7.100 /  5.  7.100
  libswresample   3.  7.100 /  3.  7.100
  libpostproc    55.  7.100 / 55.  7.100
Input #0, video4linux2,v4l2, from '/dev/video0':
  Duration: N/A, start: 9936.517693, bitrate: N/A
    Stream #0:0: Video: h264 (Constrained Baseline), yuvj420p(pc, progressive), 320x240 [SAR 1:1 DAR 4:3], 15 fps, 15 tbr, 1000k tbn, 30 tbc
Output #0, rtp, to 'rtp://localhost:8005':
  Metadata:
    encoder         : Lavf58.45.100
    Stream #0:0: Video: h264 (Constrained Baseline), yuvj420p(pc, progressive), 320x240 [SAR 1:1 DAR 4:3], q=2-31, 15 fps, 15 tbr, 90k tbn, 15 tbc
SDP:
v=0
o=- 0 0 IN IP6 ::1
s=No Name
c=IN IP6 ::1
t=0 0
a=tool:libavformat 58.45.100
m=video 8005 RTP/AVP 96
a=rtpmap:96 H264/90000
a=fmtp:96 packetization-mode=1; sprop-parameter-sets=Z0JAKLtAoPv4CiQAAAMABAAAAwB5gQAAtxsAC3Hve+F4RCNQ,aM44gAA=; profile-level-id=424028

Stream mapping:
  Stream #0:0 -> #0:0 (copy)
Press [q] to stop, [?] for help
```

Now going to the ipv6 adress printed by the script you should see the stream. This should be accessible from any devices connected to your Husarnet network.

## Non Docker version

If You don't want to use provided Dockerfile bellow is the set of instructions that accomplishes the same streaming on your host.
It was tested on Raspberry Pi OS

### Install libsrtp

```bash
$ wget https://github.com/cisco/libsrtp/archive/v2.2.0.tar.gz
$ tar xfv v2.2.0.tar.gz
$ cd libsrtp-2.2.0
$ ./configure --prefix=/usr --enable-openssl
$ make shared_library && sudo make install
``` 

### Install libcurl

```bash
$ apt-get install libcurl4-openssl-dev
```

### Install janus dependencies

```bash
$ apt-get install libmicrohttpd-dev libjansson-dev libnice-dev libssl-dev libsrtp-dev \
  libsofia-sip-ua-dev libglib2.0-dev libopus-dev libogg-dev libini-config-dev \
  libcollection-dev pkg-config gengetopt libtool automake dh-autoreconf
```

### Install janus 

```bash
$ git clone https://github.com/meetecho/janus-gateway.git
$ cd janus-gateway
$ sh autogen.sh
$ ./configure --disable-websockets --disable-data-channels --disable-rabbitmq --disable-docs --prefix=/opt/janus
$ make
$ make install
$ make configs
```

### Install ffmpeg

```bash
$ apt-get install ffmpeg
```

### Install nginx

```bash
$ apt-get install nginx
$ cp -r /opt/janus/share/janus/demos/ /var/www/html
```

### Configure janus

In file `/opt/janus/etc/janus.jcfg`

Under section media

uncoment: `ipv6 = true`

In order to tell janus to service ipv6 traffic, since Husarnet is an ipv6 network.

In file `/opt/janus/etc/janus.plugin.streaming.jcfg` you need to uncomment the following section:

```
264-sample: {
        type = "rtp"
        id = 10
        description = "H.264 live stream coming from gstreamer"
        audio = false
        video = true
        videoport = 8005
        videopt = 126
        videortpmap = "H264/90000"
        videofmtp = "profile-level-id=42e01f;packetization-mode=1"
        secret = "adminpwd"
}
```
This is a description of our stream that we want to capture and forward.

### Move index.html to ngnix folder as well as janus files to be served
```bash
$ cp -r /opt/janus/share/janus/demos/. /var/www/html
$ cp -f src/index.html /var/www/html/index.html
```

### Start nginx

```bash
service nginx start
```

### Create ffmpeg pipeline

This is an example that I used with a webcam capable of h264 feed

```bash
$ ffmpeg -f v4l2 -framerate 15 -video_size 320x240 -codec:v h264 -i /dev/video0 \
         -an -c:v copy  -f rtp rtp://localhost:8005
```

### Run janus

In `/opt/janus/bin`:

```bash
$ ./janus

```

Now you can go to the husarnet address and should see the stream.