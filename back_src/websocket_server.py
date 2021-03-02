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