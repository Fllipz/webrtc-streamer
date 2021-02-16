# # webrtc-streamer

## Intorduction 
This repo describes how to setup janus webcam stream over the Husarnet VPN using docker.

### General comments
- Due to the way janus handles networking You may need to disable mDNS in your browser in order to view the stream.
- This example uses a h264 codec which is not supported by Google Chrome, in order to view stream in Chrome either change the codec used or
  customize Your chrome installation as to support h264 codec.

## Build Image
Ensure bash scrpits are executable:
```bash
sudo chmod +x init-container.sh
sudo chmod +x pipeline.sh
```

Then build an image:
```bash
sudo docker build -t docker-vpn .
```

### Raspberry Pi specific
On Raspberry Pi OS you may see a signature error when trying to build the image in order to solve this you need to manually install the latest  libseccomp2.
To do so go to: https://packages.debian.org/sid/libseccomp2 and download armhf version.
Then install it as such:
```bash
sudo dpkg -i libseccomp2_2.4.3-1+b1_armhf.deb
```

## Start container
```bash
sudo docker run --rm -it \
--env HOSTNAME='docker-vpn-1' \
--env JOINCODE='fc94:b01d:1803:8dd8:3333:2222:1234:1111/xxxxxxxxxxxxxxxxx' \
-v docker-vpn-v:/var/lib/husarnet \
-v /dev/net/tun:/dev/net/tun \
--device=/dev/video0:/dev/video0  \
--cap-add NET_ADMIN --sysctl net.ipv6.conf.all.disable_ipv6=0 docker-vpn
```

description:
- `HOSTNAME='docker-vpn-1'` - is an easy to use hostname, that you can use instead of Husarnet IPv6 addr to access your container over the internet
- `JOINCODE='fc94:b01d:1803:8dd8:3333:2222:1234:1111/xxxxxxxxxxxxxxxxx'` - is an unique Join Code from your Husarnet network. You will find it at **https://app.husarnet.com -> choosen network -> `[Add element]` button ->  `join code` tab**
- `-v my-container-1-v:/var/lib/husarnet` - you need to make `/var/lib/husarnet` as a volume to preserve it's state for example if you would like to update the image your container is based on. If you would like to run multiple containers on your host machine remember to provide unique volume name for each container (in our case `HOSTNAME-v`).
- `--device=/dev/video0:/dev/video0` - you need to give the container access to your webcam in this case /dev/video0 which will be referenced in the pipline.sh script as /dev/video0

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

🔥 [2/2] Connecting to Husarnet network as "docker-vpn-1":
[244141459] joining...
[244143460] joining...
done

*******************************************
💡 Tip
To access a webserver visit:
👉 http://[fc94:eaa2:5adf:91d4:d0ec:b14f:3968:f519]:80 👈
in your web browser 💻
*******************************************

Janus commit: ad54495df09e8b96386df40b96b4212fe36a92b7
Compiled on:  Mon Feb 15 11:30:55 UTC 2021

Logger plugins folder: /opt/janus/lib/janus/loggers
[WARN] 	Couldn't access logger plugins folder...
---------------------------------------------------
  Starting Meetecho Janus (WebRTC Server) v0.11.1
---------------------------------------------------

Checking command line arguments...
Debug/log level is 4
Debug/log timestamps are disabled
Debug/log colors are enabled
Adding 'vmnet' to the ICE ignore list...
Using 172.17.0.2 as local IP...
Token based authentication disabled
Initializing recorder code
Using nat_1_1_mapping for public IP: 
Initializing ICE stuff (Full mode, ICE-TCP candidates disabled, half-trickle, IPv6 support enabled)
[WARN] Janus is deployed on a private address (172.17.0.2) but you didn't specify any STUN server! Expect trouble if this is supposed to work over the internet and not just in a LAN...
Crypto: OpenSSL >= 1.1.0
No cert/key specified, autogenerating some...
Fingerprint of our certificate: 92:86:5F:BF:E2:21:DA:5D:45:BD:5F:32:C1:7B:D8:74:1D:5F:23:C7:F3:1F:35:19:84:CE:09:3A:8C:48:96:E6
[WARN] Data Channels support not compiled
Event handlers support disabled
Plugins folder: /opt/janus/lib/janus/plugins
Sessions watchdog started
Joining Janus requests handler thread
Loading plugin 'libjanus_audiobridge.so'...
JANUS AudioBridge plugin initialized!
Loading plugin 'libjanus_textroom.so'...
[WARN] Data channels support not compiled, disabling TextRoom plugin
[WARN] The 'janus.plugin.textroom' plugin could not be initialized
Loading plugin 'libjanus_videoroom.so'...
JANUS VideoRoom plugin initialized!
Loading plugin 'libjanus_voicemail.so'...
JANUS VoiceMail plugin initialized!
Loading plugin 'libjanus_nosip.so'...
JANUS NoSIP plugin initialized!
Loading plugin 'libjanus_sip.so'...
JANUS SIP plugin initialized!
Loading plugin 'libjanus_recordplay.so'...
JANUS Record&Play plugin initialized!
Loading plugin 'libjanus_videocall.so'...
JANUS VideoCall plugin initialized!
Loading plugin 'libjanus_streaming.so'...
[WARN] libcurl not available, Streaming plugin will not have RTSP support
JANUS Streaming plugin initialized!
Loading plugin 'libjanus_echotest.so'...
JANUS EchoTest plugin initialized!
Transport plugins folder: /opt/janus/lib/janus/transports
Loading transport plugin 'libjanus_pfunix.so'...
[WARN] No Unix Sockets server started, giving up...
[WARN] The 'janus.transport.pfunix' plugin could not be initialized
Loading transport plugin 'libjanus_http.so'...
HTTP transport timer started
HTTP webserver started (port 8088, /janus path listener)...
JANUS REST (HTTP/HTTPS) transport plugin initialized!
Setting pipeline to PAUSED ...
Pipeline is live and does not need PREROLL ...
Pipeline is PREROLLED ...
Setting pipeline to PLAYING ...
New clock: GstSystemClock
Redistribute latency...
[h264-sample] New video stream! (ssrc=3800949643, index 0)
```

Now going to the ipv6 adress printed by the script and navigating to path /demos/streamingtest.html you should be able to access the stream from your webcam listed as H.264.
This should be accessible from any devices connected to your Husarnet network

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
### Install Gstreamer
```bash
$ apt-get install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc \
  gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa 
```


### Install nginx
```bash
$ apt-get install nginx
$ cp -r /opt/janus/share/janus/demos/ /var/www/html
```

### Configure janus
In file /opt/janus/etc/janus.jcfg
Under section media
uncoment:        ipv6 = true
In order to tell janus to service ipv6 traffic, since Husarnet is an ipv6 network.
In file /opt/janus/etc/janus.plugin.streaming.jcfg  
You need to uncomment the following section:
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
This is a description of our stream that we want to capture and forward.

### Start nginx
```bash
service nginx start
```

### Create Gstreamer pipeline
```bash
$ gst-launch-1.0 v4l2src device=/dev/video0 ! 'video/x-raw, width=640, height=480, framerate=15/1' ! \
 videoconvert ! timeoverlay  ! x264enc tune=zerolatency  ! rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=8005
```

### Run janus
In /opt/janus/bin:
```bash
$ ./janus

```
