#! /bin/bash

gst-launch-1.0 videotestsrc pattern=ball   \
    ! tee name=t \
    ! videoconvert \
    ! x264enc tune=zerolatency \
    ! rtph264pay \
    ! udpsink host=localhost port=8005 t. \
    ! queue ! videoconvert \
    ! vp8enc \
    ! rtpvp8pay \
    ! udpsink host=localhost port=8006
