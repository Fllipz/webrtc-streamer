#!/bin/bash

gst-launch-1.0 v4l2src device=/dev/video0  \
    ! tee name=t \
    ! queue !  'video/x-raw,framerate=30/1,width=320,height=240' \
    ! videoconvert \
    ! vp8enc  \
    ! rtpvp8pay \
    ! udpsink host=localhost port=8006 t. \
    ! queue ! videoconvert \
    ! x264enc tune=zerolatency \
    ! rtph264pay \
    ! udpsink host=localhost port=8005
