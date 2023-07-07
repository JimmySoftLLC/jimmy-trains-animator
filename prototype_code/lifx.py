import adafruit_requests
import ssl
import wifi
import os
import socketpool
import files
import time
import json

#  connect to your SSID
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

#  prints MAC address to REPL

mystring = [hex(i) for i in wifi.radio.mac_address]
print("My MAC addr:", mystring)

#  prints IP address to REPL
print("My IP address is", wifi.radio.ipv4_address)

print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
#server = HTTPServer(pool)
   
get_time_url = "https://worldtimeapi.org/api/timezone/America/New_York"

requests = adafruit_requests.Session(pool, ssl.create_default_context())

class LIFX(object):
    
    def __init__(self):
        self.token = os.getenv('CIRCUITPY_LIFX_TOKEN')
        self.brightness = 1
        print(self.token)
    
    def auth(self):
        token = self.token
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        response = requests.get('https://api.lifx.com/v1/lights/all', headers=headers)
        print(response.json())
        
    def get_status(self):
        token = self.token
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        response = requests.get('https://api.lifx.com/v1/lights/all', headers=headers)
        my_json = response.json()
        return my_json
    
    def effects_off(self):
        token = self.token
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        data = {
            "power_off": True
        }
        response = requests.post('https://api.lifx.com/v1/lights/all/effects/off', 
                                 data=data, headers=headers)
        print(response.json())
    
    def pulse(self, period=2, cycles=5, color="green"):
        token = self.token
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        data = {
            "period": 2,
            "cycles": 5,
            "color": "blue saturation:0.5",
        }
        response = requests.post('https://api.lifx.com/v1/lights/id:d073d5703f20/effects/pulse', 
                                 data=data, headers=headers)
        print(response.json())
        
    def pulse2(self):
        token = self.token
        headers = {
            "Authorization": "Bearer %s" % token,
        }

        payload = {
          "states": [
            {
                "selector" : "id:d073d5703f20",
                
            }
          ],
        }

        #response = requests.put('https://api.lifx.com/v1/lights/states', data=json.dumps(payload), headers=headers)

        data = {
            "period": 10,
            "cycles": 2,
            "color": "hue:360 saturation:1.0 brightness:1.0",
            "from_color": "hue:180 saturation:1.0 brightness:1.0",
            "peak": .5
        }

        response = requests.post('https://api.lifx.com/v1/lights/id:d073d5703f20/effects/breathe', data=data, headers=headers)


        print(response.json())
          
    def power_off(self):
        token = self.token
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        payload = {
            "power": "off",
        }
        response = requests.put('https://api.lifx.com/v1/lights/all/state', 
                                data=payload, headers=headers)
        print(response.json())
    
    def power_on(self):
        token = self.token
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        payload = {
            "power": "on",
        }
        response = requests.put('https://api.lifx.com/v1/lights/all/state', 
                                data=payload, headers=headers)
        print(response.json())
        
    def preset(self):
        token = self.token
        presets= {"mexicana": self.mexicana,
                  "mango": self.mango,
                  "pisces": self.pisces,
                  "focus": self.focus,
                  "hygge": self.hygge,
                  "blue_haus": self.blue_haus,
                  "lady_prep": self.lady_prep,
                  "vday_vibes": self.vday_vibes,
                  "habesha_nation": self.habesha_nation
        }
        s = input("""
        Pick preset theme:\n 'mexicana'\n 'mango'\n
        'pisces'\n 'focus'\n 'hygge'\n 'blue_haus'\n
        'lady_prep'\n 'vday_vibes'\n 'habesha_nation' 
        """)
        
        b = input("Enter level of brightness 0 to 1 ")
        scene = presets[s]
        brightness = b
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        payload = {
            "brightness": brightness,
        }
        response = requests.put('https://api.lifx.com/v1/scenes/scene_id:%s/activate' % scene, headers=headers)
        response = requests.put('https://api.lifx.com/v1/lights/all/state', data=payload, headers=headers)
        print(response.json())
    def brightness(self, brightness):
        token = self.token
        brightness = brightness
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        payload = {
            "brightness": brightness,
        }
        response = requests.put('https://api.lifx.com/v1/lights/all/state', data=payload, headers=headers)
        print(response.json())
        
        
my_lifx = LIFX()
#my_object = my_lifx.get_status()
#print("bulb ids")
#for val in my_object:
#    dude = str("id: " + val["id"] + " label: " + val["label"] + " connected: " + str(val["connected"]) )
#    print(dude)
    
# my_lifx.pulse()
my_lifx.pulse2()
    
