from flask import Flask, Response
import picamera
import io
from zeroconf import ServiceInfo, Zeroconf

app = Flask(__name__)

def gen():
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)  # Set resolution
        camera.framerate = 24  # Set framerate
        stream = io.BytesIO()

        while True:
            # Start capturing video in continuous mode
            camera.capture(stream, 'jpeg', use_video_port=True)
            stream.seek(0)
            frame = stream.read()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            stream.seek(0)
            stream.truncate()

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
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
    zeroconf = register_mdns_service()
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        zeroconf.close()
