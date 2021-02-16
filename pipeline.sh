#!/bin/bash

#gst-launch-1.0 v4l2src device=/dev/video0 ! 'video/x-raw, width=640, height=480, framerate=15/1' ! videoconvert ! timeoverlay  ! x264enc tune=zerolatency  ! rtph264pay config-interval=1 pt=96 ! udpsink host=localhost port=8004
gst-launch-1.0 v4l2src device=/dev/video0  \
    ! videoconvert \
    ! x264enc tune=zerolatency \
    ! rtph264pay \
    ! udpsink host=localhost port=8005

