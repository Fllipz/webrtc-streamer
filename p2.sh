#!/bin/bash

ffmpeg -f v4l2 -framerate 10 -video_size 640x480 -codec:v h264 -i /dev/video0   -codec:v libvpx  -preset ultrafast  -s 640x480 -b:v 1000k -f rtp rtp://localhost:8006

