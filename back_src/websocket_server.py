#!/usr/bin/env python

import asyncio
import websockets
import json
import argparse
import os
import subprocess



from time import sleep

event = asyncio.Event()
loop = asyncio.get_event_loop() 

def check_if_conection_p2p(addr):
    result = subprocess.run("sudo husarnet status", capture_output=True, shell=True, text=True)
    start = result.stdout.find("Peer "+addr)
    end = result.stdout.find("Peer ", start)
    if start == -1:
        return False
    if end != -1:
        found = result.stdout.find("tunnelled", start,end)
    else:
        found = result.stdout.find("tunnelled",start)
    if found == -1:
        return True
    return False


def kill_ffmpeg():
    pid = int(subprocess.check_output(["pidof","ffmpeg"]))
    subprocess.run(["kill",str(pid)])

def run_ffmpeg(size, fps):
    subprocess.Popen(['ffmpeg', '-f', 'v4l2', '-framerate', fps, '-video_size', size, '-codec:v', 'h264', '-i', '/dev/video0', '-an', '-c:v', 'copy', '-f', 'rtp', 'rtp://localhost:8005' ])

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
    


async def hello(websocket, path):
    while(True):
        data = await websocket.recv()
        data = json.loads(data)
        if 'check_connection' in data.keys():
            addr, port, a, b = websocket.remote_address
            if(check_if_conection_p2p(addr)):
                await websocket.send(json.dumps({"connection":1}))
            else:
                await websocket.send(json.dumps({"connection":0}))
        elif 'get_ffed_options' in data.keys():
            await websocket.send(json.dumps({"options":0}))
    
        

start_server = websockets.serve(hello, port=8001)

loop.run_until_complete(start_server)
loop.run_forever()