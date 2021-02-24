#!/bin/bash

ffmpeg -f v4l2 -framerate 10 -video_size 320x240 -codec:v h264 -i /dev/video0 \
         -codec:v libx264 -profile:v baseline -preset ultrafast -tune zerolatency -s 320x240 -b:v 1000k -f rtp rtp://localhost:8005 
