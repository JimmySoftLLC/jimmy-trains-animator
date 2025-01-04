from scapy.all import *

# Function to process each packet
def packet_callback(packet):
    if packet.haslayer(Dot11):
        # Check if it's a beacon frame or probe request (common broadcast packets)
        if packet.type == 0 and packet.subtype in [8, 4]:
            ssid = packet.info.decode('utf-8', 'ignore') if packet.info else 'Hidden SSID'
            mac_address = packet.addr2
            print(f"Broadcast detected: SSID='{ssid}' MAC='{mac_address}'")

# Sniff traffic on the Wi-Fi interface (use your interface name)
print("Starting Wi-Fi traffic snooper...")
sniff(iface='wlan0', prn=packet_callback, store=0)
