#!/bin/bash

ffmpeg -f v4l2 -framerate 30 -video_size 640x480 -codec:v h264 -i /dev/video0 \
        -codec:v libx264 -profile:v baseline -preset ultrafast -tune zerolatency -s 640x480 -b:v 1000k -f rtp rtp://localhost:8005

