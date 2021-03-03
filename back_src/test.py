import subprocess
import os
import signal
from time import sleep
import re

def kill_ffmpeg():
    pid = int(subprocess.check_output(["pidof","ffmpeg"]))
    subprocess.run(["kill",str(pid)])

def run_ffmpeg(size, fps):
    subprocess.Popen(['ffmpeg', '-f', 'v4l2', '-framerate', fps, '-video_size', size, '-codec:v', 'h264', '-i', '/dev/video2', '-an', '-c:v', 'copy', '-f', 'rtp', 'rtp://localhost:8005' ])


def find_between_strs( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def get_feed_options():
    result = subprocess.run(['v4l2-ctl', '-d', '2', '--list-formats-ext', ],capture_output=True,text=True)
    found = find_between_strs(result.stdout,"(H.264, compressed)","[2]")
    chunks = found.split("Size: Discrete")
    parsed = {}
    for chunk in chunks[1:]:
        size = chunk.split('\n')[0]
        i=0
        parsed[size] = {}
        for line in chunk.split('\n')[1:]:
            res = re.search(r'\((.*?) fps\)',line)
            if res != None:
                parsed[size][i]=res.group(1)
                i+=1
        

    return parsed

get_feed_options()