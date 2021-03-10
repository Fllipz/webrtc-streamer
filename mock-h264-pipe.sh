#!/bin/bash


ffmpeg -re -f lavfi  -i testsrc=size=1280x720:rate=30 -c:v libx264 -b:v 1600k -preset ultrafast  -tune zerolatency   -b 1000k -f rtp rtp://localhost:8005
