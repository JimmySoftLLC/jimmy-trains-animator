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

from flask import Flask, Response
import picamera
import io
import threading
import cv2
import numpy as np
from time import sleep
from zeroconf import ServiceInfo, Zeroconf

app = Flask(__name__)

# Global buffer for video frames
output_frame = None
lock = threading.Lock()

# Create a video writer object to save the video to a file
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Choose codec ('XVID' for .avi or 'mp4v' for .mp4)
video_writer = cv2.VideoWriter('output.avi', fourcc, 24, (1280, 720))  # Save as 1280x720 video at 24 FPS

def camera_thread():
    global output_frame, lock
    with picamera.PiCamera() as camera:
        camera.resolution = (1280, 720)  # Set resolution to 1280x720
        camera.framerate = 24  # Set framerate

        # Create an in-memory stream
        stream = io.BytesIO()
        for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            with lock:
                # Store the current frame in the global buffer
                stream.seek(0)
                output_frame = stream.read()

                # Convert the JPEG frame to a NumPy array and then to an OpenCV image for saving
                np_img = np.frombuffer(output_frame, dtype=np.uint8)
                frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

                # Write the frame to the video file
                video_writer.write(frame)

            # Reset stream for the next frame
            stream.seek(0)
            stream.truncate()

            # Sleep to match the framerate
            sleep(1 / 24)

@app.route('/video_feed')
def video_feed():
    def generate():
        global output_frame, lock
        while True:
            with lock:
                if output_frame is None:
                    continue
                frame = output_frame

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def register_mdns_service():
    zeroconf = Zeroconf()
    service_info = ServiceInfo(
        "_http._tcp.local.",
        "mycamera._http._tcp.local.",
        addresses=[b"\xC0\xA8\x01\x02"],  # Replace with your RPi IP in byte format
        port=5000,
        properties={},
        server="mycamera.local.",
    )
    zeroconf.register_service(service_info)
    return zeroconf

if __name__ == '__main__':
    # Start the camera thread
    camera_thread = threading.Thread(target=camera_thread, daemon=True)
    camera_thread.start()

    # Register mDNS service
    zeroconf = register_mdns_service()

    try:
        # Start the Flask app
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        zeroconf.close()
        # Release the video writer resource
        video_writer.release()
