import time
import wifi

MY_SSID = "yourssid"  # ← change this

print("Monitoring signal for:", MY_SSID)

while True:
    found = False
    for network in wifi.radio.start_scanning_networks():
        if network.ssid == MY_SSID:
            print(f"{MY_SSID} → RSSI = {network.rssi} dBm")
            found = True
            break
    
    wifi.radio.stop_scanning_networks()
    
    if not found:
        print(f"Could not see {MY_SSID} (might be hidden or out of range)")
    
    time.sleep(5)