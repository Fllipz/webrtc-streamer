# webrtc-streamer

**Janus Gateway (WebRTC) + web UI powered by Bootstrap 5 + Husarnet VPN Client**

A dockerized firmware for an IP camera (eg. Single Board Computer + USB web camera) to access the video and audio stream over the internet minimizing latency.

![WebRTC server](https://docs.staging.husarnet.com/assets/images/webrtc-demo-cceb1931a92418cb0e2d966e9db7906d.png)

💡 Use prebuilt Docker images from Docker Hub to run the project quickly. 

https://hub.docker.com/r/husarnet/webrtc-streamer

Otherwise, the following steps will show you how to start the project manually.

## Requirements

1. **A single board computer** (SBC) with connected USB camera - tested on RaspberryPi 4 and Logitech C920 USB web camera
2. **A user's laptop** running Linux with Firefox or Chrome web browser to access a video stream over the Internet.
3. **Husarnet VPN join code**. 

  You will find your JoinCode at **https://app.husarnet.com  
   -> Click on the desired network  
   -> `Add element` button  
   -> `Join code` tab**

## General Comments

1. Due to the way Janus handles networking You may need to disable mDNS in your browser in order to view the stream.

    - On FireFox open URL: `about:config` and setup:

    ```bash
    mdns -> false
    media.peerconnection.ice.obfuscate_host_addresses -> false
    ```

2. The firmware is capable of using one of two codecs: H264 or VP8. 
    - `H.264` is used only if the camera provides this kind of output stream. By using H.264 stream provided by camera, the stream can be used directly by a WebRTC gateway saving SBC computing power and lowering the latency.
    - `VP8` is used if the camera doesn't provide `H.264` output stream. VP8 is an open and royalty-free video compression format, but probably don't used by any popular USB camera, so encoding need to be done on SBC. That increases latency and requires much more computing power.

    There is a handy Linux toolset to check available output stream options for your USB camera:

    ```bash
    $ sudo v4l2-ctl --list-formats
    ioctl: VIDIOC_ENUM_FMT
        Type: Video Capture

        [0]: 'YUYV' (YUYV 4:2:2)
        [1]: 'MJPG' (Motion-JPEG, compressed)
        [2]: 'H264' (H.264, compressed)
    ```
## Build an Image

Ensure bash scrpits are executable:

```bash
sudo chmod +x init-container.sh
```

Then build an image:

```bash
sudo docker build -t webrtc-streamer .
```

### Raspberry Pi Specific

On Raspberry Pi OS you may see a signature error when trying to build the image in order to solve this you need to manually install the latest  libseccomp2.

To do so go to: https://packages.debian.org/sid/libseccomp2 and download armhf version.

Then install it as such:

```bash
sudo dpkg -i libseccomp2_2.4.3-1+b1_armhf.deb
```

## Start the Project Using `docker run`

### Create `.env` File:

…and specify Husarnet JoinCode and hostname there. Also change `CAM_AUDIO_CHANNELS` to `=1` if you can't hear a sound. The file should look something like this:

```
HOSTNAME=webrtc-streamer-1
JOINCODE=fc94:b01d:1803:8dd8:3333:2222:1234:1111/xxxxxxxxxxxxxxxxx
CAM_AUDIO_CHANNELS=2
```

You will find your JoinCode at **https://app.husarnet.com  
 -> Click on the desired network  
 -> `Add element` button  
 -> `Join code` tab**

### Run a Container

```bash
sudo docker run --rm -it \
--env-file ./.env \
--volume webrtc_streamer_v:/var/lib/husarnet \
--device /dev/net/tun \
--device /dev/video0:/dev/video0  \
--device /dev/snd \
--cap-add NET_ADMIN \
--sysctl net.ipv6.conf.all.disable_ipv6=0 \
webrtc-streamer
```

description:
- `--volume webrtc_streamer_v:/var/lib/husarnet` - you need to make `/var/lib/husarnet` as a volume to preserve it's state for example if you would like to update the image your container is based on. If you would like to run multiple containers on your host machine remember to provide unique volume name for each container (in our case `HOSTNAME-v`).
- `--device /dev/video0:/dev/video0` - you need to give the container access to your webcam in this case `/dev/video0` which will be referenced in the `pipline.sh` script as `/dev/video0`

## Important Notes

### Mock Camera Feed For Testing

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

This overrides the `TEST` environment variable and makes the init-container.sh scrpit use mock pipelines. There will be generated a fake feed in place of camera feed.

### P2P Connection

In order to achieve low latency we take advantage of the Husarnet P2P connection establishment. If the stream is accessed from a host for which our connection is not P2P the quality of stream will degrade. You can check your connection status using:

```bash
sudo husarnet status
```

The demo site will also display a warning if it detects lack of P2P connection and (by default) turn-off the streaming. But access to web UI will be still possible over the Husarnet Base Server proxy. 

In order to solve connection issues go to:

https://husarnet.com/docs/tutorial-troubleshooting

### Changing Stream Parameters

The project allows user to change stream parameters from a level of web UI.

As such this process may fail if You use a differen webcam which outputs data in different format.

During testing we used a Logitech C920 camera.

## Result

Runing above commands should result in the following output:

```bash
$ sudo docker run --rm -it --env-file ./.env --volume webrtc_streamer_v:/var/lib/husarnet --device /dev/net/tun --device /dev/video0:/dev/video0  --device /dev/snd --cap-add NET_ADMIN --sysctl net.ipv6.conf.all.disable_ipv6=0 webrtc-streamer

⏳ [1/2] Initializing Husarnet Client:
waiting...
waiting...
waiting...
waiting...
success

🔥 [2/2] Connecting to Husarnet network as "webrtc-streamer-abc":
[5031000] joining...
[5033001] joining...
done

*******************************************
💡 Tip
To access a live video stream visit:
👉 http://[fc94:4090:c101:c65e:ef7a:fcf1:6789:3b51]:80/ 👈
in your web browser 💻
*******************************************

H264
Janus commit: 414edcae7955b924f8a434909fafe243c2ad8d6c
Compiled on:  Tue Mar 23 09:43:22 UTC 2021

Logger plugins folder: /opt/janus/lib/janus/loggers
[WARN]  Couldn't access logger plugins folder...
---------------------------------------------------
  Starting Meetecho Janus (WebRTC Server) v0.11.1
---------------------------------------------------

Checking command line arguments...
Debug/log level is 0
Debug/log timestamps are disabled
Debug/log colors are enabled
h264_supp
ffmpeg version 4.2.4-1ubuntu0.1 Copyright (c) 2000-2020 the FFmpeg developers
  built with gcc 9 (Ubuntu 9.3.0-10ubuntu2)
  configuration: --prefix=/usr --extra-version=1ubuntu0.1 
  
  ...
  
  libpostproc    55.  5.100 / 55.  5.100
Guessed Channel Layout for Input Stream #0.0 : mono
Input #0, alsa, from 'hw: 1':
  Duration: N/A, start: 1616493155.444667, bitrate: 768 kb/s
    Stream #0:0: Audio: pcm_s16le, 48000 Hz, mono, s16, 768 kb/s
Stream mapping:
  Stream #0:0 -> #0:0 (pcm_s16le (native) -> opus (libopus))
Press [q] to stop, [?] for help
Output #0, rtp, to 'rtp://localhost:8007':
  Metadata:
    encoder         : Lavf58.29.100
    Stream #0:0: Audio: opus (libopus), 48000 Hz, mono, s16, 16 kb/s
    Metadata:
      encoder         : Lavc58.54.100 libopus
SDP:
v=0
o=- 0 0 IN IP6 ::1
s=No Name
c=IN IP6 ::1
t=0 0
a=tool:libavformat 58.29.100
m=audio 8007 RTP/AVP 97
b=AS:16
a=rtpmap:97 opus/48000/2

Input #0, video4linux2,v4l2, from '/dev/video0':
  Duration: N/A, start: 5035.942407, bitrate: N/A
    Stream #0:0: Video: h264 (High), yuvj420p(pc, bt470bg/bt470bg/bt709, progressive), 320x240, 30 fps, 30 tbr, 1000k tbn, 2000k tbc
Output #0, rtp, to 'rtp://localhost:8005':
  Metadata:
    encoder         : Lavf58.29.100
    Stream #0:0: Video: h264 (High), yuvj420p(pc, bt470bg/bt470bg/bt709, progressive), 320x240, q=2-31, 30 fps, 30 tbr, 90k tbn, 1000k tbc
SDP:
v=0
o=- 0 0 IN IP6 ::1
s=No Name
c=IN IP6 ::1
t=0 0
a=tool:libavformat 58.29.100
m=video 8005 RTP/AVP 96
a=rtpmap:96 H264/90000
a=fmtp:96 packetization-mode=1; sprop-parameter-sets=Z2QAFKwsaoUH6bgoCCgQ,aO4xshsA; profile-level-id=640014

Stream mapping:
  Stream #0:0 -> #0:0 (copy)
Press [q] to stop, [?] for help
[rtp @ 0xaaaae5965570] Timestamps are unset in a packet for stream 0. This is deprecated and will stop working in the future. Fix your code to set the timestamps properly
frame=  265 fps= 31 q=-1.0 size=    1398kB time=00:00:08.76 bitrate=1306.7kbits/s speed=1.02x  
```

## Accessing a Web User Interface and a Stream

To access a web UI and video stream hosted by the SBC, you need to connect your computer running Firefox or Chrome web browser to the same Husarnet network as the SBC.

**Simply use the same Husarnet Join Code as used befor for SBC**

1. Save your Husarnet VPN Join Code as an environmental variable:

```bash
export HUSARNET_JOINCODE="fc94:b01d:1803:8dd8:3333:2222:1234:1111/xxxxxxxxxxxxxxxxx"
```

2. Install Husarnet VPN client:

```bash
curl https://install.husarnet.com/install.sh | sudo bash
sudo systemctl restart husarnet
```

3. Connect your laptop to the same Husarnet VPN network as SBC, by using the same Husarnet Join Code:

```bash
sudo husarnet join ${HUSARNET_JOINCODE} mylaptop
```

4. Open the URL provided by the SBC in Firefox or Chrome web browser on your laptop:

![WebRTC docker webserver](https://docs.staging.husarnet.com/assets/images/webrtc-webbrowser-a59bc0237ce183695c5f734ccb53758b.png)

