#!/bin/bash

ffmpeg -f v4l2 -framerate 15 -video_size 320x240 -codec:v h264 -i /dev/video0 \
         -an -c:v copy  -f rtp rtp://localhost:8005 
