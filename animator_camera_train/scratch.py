# MIT License
#
# Copyright (c) 2024 JimmySoftLLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#######################################################
# this code requires the following installs
# [Your existing install comments remain unchanged...]
#######################################################

import os
import gc
import json
import socket
import socketserver
import threading
from http import server
import io
import time
import sys
import signal
import asyncio
import websockets
import subprocess
import netifaces
import requests
import pygame
import vlc
import psutil
import random
import board
import digitalio
from adafruit_debouncer import Debouncer
import neopixel_spi
from rainbowio import colorwheel
from lifxlan import LifxLAN, BLUE, CYAN, GREEN, ORANGE, PINK, PURPLE, RED, YELLOW
from adafruit_servokit import ServoKit
from zeroconf import ServiceInfo, Zeroconf
from collections import OrderedDict, deque
from concurrent.futures import ThreadPoolExecutor
from gtts import gTTS
from pydub import AudioSegment
import files
import utilities
import pyautogui
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, JpegEncoder
from picamera2.outputs import FileOutput

# Setup pin for audio enable
aud_en = digitalio.DigitalInOut(board.D26)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False

def get_home_path(subpath=""):
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, subpath)

code_folder = get_home_path() + "code/"
media_folder = get_home_path() + "media/"
plylst_folder = get_home_path() + "media/play lists/"
snd_opt_folder = code_folder + "snd_opt/"
current_media_playing = ""
current_scene = ""
current_neo = ""
is_midori_running = False
override_switch_state = {"switch_value": ""}

# [Your existing wallpaper and utility functions remain unchanged...]

# Camera streaming globals
camera_running = False
picam2 = None
stream_output = None
camera_thread = None
recording = False

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()
        self.frame_count = 0

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.frame_count += 1
            print(f"Frame {self.frame_count} written to stream_output (size: {len(buf)} bytes)")
            self.condition.notify_all()

# [Your existing hardware setup (servos, sound, switches, etc.) remains unchanged...]

# Setup routes (combined server on port 8083)
class MyHttpRequestHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            print(self.path)
            self.handle_serve_file("/code/index.html")
        elif self.path.endswith(".css"):
            print(self.path)
            self.handle_serve_file("/code" + self.path, "text/css")
        elif self.path.endswith(".js"):
            print(self.path)
            self.handle_serve_file("/code" + self.path, "application/javascript")
        elif self.path == "/record_stream":
            print(self.path)
            self.handle_serve_file("/code/record_stream.html")
        elif self.path == "/stream.mjpg":
            self.handle_stream_mjpg()
        else:
            self.handle_serve_file(self.path)

    def do_POST(self):
        if self.path == "/upload":
            self.handle_file_upload()
        else:
            self.handle_generic_post(self.path)

    def handle_serve_file(self, path, content_type="text/html"):
        file_path = path.lstrip("/")
        try:
            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"File not found")

    def handle_serve_file_name(self, f_n, content_type="text/html"):
        try:
            with open(f_n, 'rb') as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"File not found")

    def handle_stream_mjpg(self):
        global picam2, stream_output
        if not camera_running:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b'Camera not running')
            return
        self.send_response(200)
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
        self.end_headers()
        try:
            while camera_running:
                with stream_output.condition:
                    if not stream_output.condition.wait(timeout=2.0):
                        print("Timeout waiting for frame - no frame received within 2 seconds")
                        continue
                    if stream_output.frame is None:
                        print("No frame available - frame buffer is empty")
                        continue
                    frame = stream_output.frame
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')
                print(f"Sent frame {stream_output.frame_count} to client (size: {len(frame)} bytes)")
        except Exception as e:
            print(f'Removed streaming client {self.client_address}: {e}')

    # [Your existing handle_file_upload and handle_generic_post remain unchanged...]

    def start_camera(self, rq_d):
        global cfg
        start_camera_server()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "started camera"
        self.wfile.write(response.encode('utf-8'))

    def stop_camera(self, rq_d):
        global cfg
        stop_camera_server()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "stopped camera"
        self.wfile.write(response.encode('utf-8'))

    # [Your other POST handlers remain unchanged...]

def start_camera_server():
    global camera_running, picam2, stream_output, camera_thread
    if not camera_running:
        try:
            picam2 = Picamera2()
            config = picam2.create_video_configuration(
                main={"size": (1280, 720)},
                controls={"FrameDurationLimits": (33333, 33333)}  # 30 FPS
            )
            picam2.configure(config)
            stream_output = StreamingOutput()
            picam2.start_recording(JpegEncoder(), FileOutput(stream_output))
            time.sleep(1)  # Give the camera time to start
            camera_running = True
            print("Camera server started with target 30 FPS via FrameDurationLimits")
        except Exception as e:
            print(f"Failed to start camera server: {e}")
            camera_running = False

def stop_camera_server():
    global camera_running, picam2, stream_output, camera_thread
    if camera_running:
        try:
            if recording:
                stop_recording()
            picam2.stop_recording()
            picam2.close()
            camera_running = False
            stream_output = None
            print("Camera server stopped")
        except Exception as e:
            print(f"Error stopping camera server: {e}")

# [Your existing start_recording, stop_recording, take_snapshot remain unchanged...]

if web:
    if wait_for_network():
        local_ip = get_local_ip()
        print(f"Local IP address: {local_ip}")

        QUEUE_PORT = 8001
        PORT = 8083

        httpd = None

        def start_http_server():
            global httpd
            handler = MyHttpRequestHandler
            httpd = socketserver.ThreadingTCPServer((local_ip, PORT), handler)
            httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print(f"Serving on {local_ip}:{PORT}")
            httpd.serve_forever()

        def get_mdns_info():
            name_str = cfg["HOST_NAME"] + "._http._tcp.local."
            server_str = cfg["HOST_NAME"] + ".local."
            desc = {'path': '/'}
            mdns_info = ServiceInfo(
                "_http._tcp.local.",
                name_str,
                addresses=[socket.inet_aton(local_ip)],
                port=PORT,
                properties=desc,
                server=server_str
            )
            return mdns_info

        mdns_info = get_mdns_info()

        async def command_queue_handler(websocket, path):
            global current_media_playing
            print("WebSocket connection established")
            try:
                while True:
                    if command_queue:
                        commands = list(command_queue)
                        response = {
                            'commands': commands,
                            'current_media_playing': current_media_playing
                        }
                        await websocket.send(json.dumps(response))
                    else:
                        response = {
                            'commands': [],
                            'current_media_playing': current_media_playing
                        }
                        await websocket.send(json.dumps(response))
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Error in command_queue_handler: {e}")
            finally:
                print("WebSocket connection closed")

        async def websocket_server():
            async with websockets.serve(command_queue_handler, "0.0.0.0", QUEUE_PORT):
                print(f"WebSocket server running on port {QUEUE_PORT}")
                await asyncio.Future()  # Run forever
    else:
        web = False

# [Your remaining code (command queue, state machine, etc.) remains unchanged...]

if (web):
    files.log_item("starting server...")
    try:
        zeroconf = Zeroconf()
        print("Registering mDNS service...")
        zeroconf.register_service(mdns_info)
        server_thread = threading.Thread(target=start_http_server, daemon=True)
        server_thread.start()
    except OSError:
        web = False
        files.log_item("server did not start...")

# [Your existing startup logic remains unchanged...]

def stop_program():
    stop_all_commands()
    if (web):
        print("Unregistering mDNS service...")
        zeroconf.unregister_service(mdns_info)
        zeroconf.close()
        httpd.shutdown()
    rst_an(media_folder + 'pictures/logo.jpg')
    quit()

while True:
    try:
        input("Press enter to exit...\n\n")
    finally:
        stop_program()

# type: ignore