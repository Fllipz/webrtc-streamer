import subprocess
import os
import signal
from time import sleep

def kill_ffmpeg():
    pid = int(subprocess.check_output(["pidof","ffmpeg"]))
    subprocess.run(["kill",str(pid)])

def run_ffmpeg(size, fps):
    subprocess.Popen(['ffmpeg', '-f', 'v4l2', '-framerate', fps, '-video_size', size, '-codec:v', 'h264', '-i', '/dev/video2', '-an', '-c:v', 'copy', '-f', 'rtp', 'rtp://localhost:8005' ])

run_ffmpeg("320x240","15")
sleep(1)
kill_ffmpeg()