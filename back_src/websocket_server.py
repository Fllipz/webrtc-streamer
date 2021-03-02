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
    if start == -1 or end == -1:
        return False
    found = result.stdout.find("tunnelled", start, end)
    if found == -1:
        return False
    return True

async def check_handler(websocket, path):
    addr, port, a, b = websocket.remote_address
    result = check_if_conection_p2p(addr)
    msg = {"connection" : result}
    await websocket.send(json.dumps(msg))





start_server = websockets.serve(check_handler, port=8001)

loop.run_until_complete(start_server)
loop.run_forever()