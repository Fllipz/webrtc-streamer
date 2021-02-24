#!/bin/bash


ffmpeg -re -f lavfi -i testsrc -c:v libvpx -b:v 1600k -preset ultrafast   -b 1000k -f rtp rtp://localhost:8006
