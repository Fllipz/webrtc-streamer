#! /bin/bash

gst-launch-1.0 videotestsrc pattern=ball   \
    ! videoconvert \
    ! x264enc tune=zerolatency \
    ! rtph264pay \
    ! udpsink host=localhost port=8005
