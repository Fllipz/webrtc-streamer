#!/usr/bin/env python

import asyncio
import websockets
import json
import argparse
import os
import subprocess
import re
import ipaddress



from time import sleep

event = asyncio.Event()
loop = asyncio.get_event_loop() 

def check_if_conection_p2p(addr):
    result = subprocess.run(["sudo husarnet status"], capture_output=True, shell=True, text=True)
    addr = ipaddress.ip_address(addr)
    start = result.stdout.find(str(addr.exploded))
    end = result.stdout.find("Peer ", start)
    if start == -1:
        return False
    if end != -1:
        found = result.stdout.find("tunnelled", start,end)
    else:
        found = result.stdout.find("tunnelled",start)
    if found ==-1:
        return True
    return False


def kill_ffmpeg():
    try:
        pid = int(subprocess.check_output(["pidof","ffmpeg"]))
        subprocess.run(["kill",str(pid)])
    except subprocess.CalledProcessError as e:
        print("Error killing ffmpeg!")

def run_ffmpeg_h264(size, fps):
    subprocess.Popen(['ffmpeg', '-f', 'v4l2', '-framerate', fps, '-video_size', size, '-codec:v', 'h264', '-i', '/dev/video0', '-an', '-c:v', 'copy', '-f', 'rtp', 'rtp://localhost:8005' ])

def run_ffmpeg_vp8(size,fps):
    subprocess.Popen(['ffmpeg', '-f', 'v4l2', '-framerate', fps, '-video_size', size, '-codec:v', 'h264', '-i', '/dev/video0', '-codec:v', 'libvpx',  '-preset', 'ultrafast',  '-s', size, '-b:v', '1000k', '-f', 'rtp', 'rtp://localhost:8006'])

def find_between_strs( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        if start!=-1 and end==-1:
            return s[start:]

def get_feed_options():
    result = subprocess.run(['v4l2-ctl', '-d', '0', '--list-formats-ext', ],capture_output=True,text=True)
    found = find_between_strs(result.stdout,"(H.264, compressed)","[")
    chunks = found.split("Size: Discrete")
    parsed = {"options":{}}
    for chunk in chunks[1:]:
        size = chunk.split('\n')[0]
        i=0
        parsed["options"][size] = {}
        for line in chunk.split('\n')[1:]:
            res = re.search(r'\((.*?) fps\)',line)
            if res != None:
                parsed["options"][size][i]=res.group(1)
                i+=1
        

    return parsed



async def hello(websocket, path):
    while(True):
        data = await websocket.recv()
        data = json.loads(data)
        if 'check_connection' in data.keys():
            addr, port, a, b = websocket.remote_address
            if check_if_conection_p2p(addr):
                await websocket.send(json.dumps({"connection":1}))
            else:
                await websocket.send(json.dumps({"connection":0}))
        elif 'get_feed_options' in data.keys():
            await websocket.send(json.dumps(get_feed_options()))
        elif 'change_feed' in data.keys():
            kill_ffmpeg()
            sleep(1)
            if(data['change_feed']['protocol']=='H264'):
                run_ffmpeg_h264(data['change_feed']['size'],data['change_feed']['fps'])
                await websocket.send(json.dumps({'stream_start':1}))
            elif(data['change_feed']['protocol']=='VP8'):
                run_ffmpeg_vp8(data['change_feed']['size'],data['change_feed']['fps'])
                await websocket.send(json.dumps({'stream_start':1}))
            else:
                await websocket.send(json.dumps({"error":"Error setting up ffmpeg"}))
        

start_server = websockets.serve(hello, port=8001)

loop.run_until_complete(start_server)
loop.run_forever()