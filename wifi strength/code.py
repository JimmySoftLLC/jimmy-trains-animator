import time
import wifi

MY_SSID = "jimmytrainsguest"  # ← change this

def measure_signal_strength(MY_SSID, cycles):
    print("Monitoring signal for:", MY_SSID)
    print("Showing current RSSI + running average (simple sum + count)\n")

    total_sum = 0.0      # running sum of all valid RSSI values
    count = 0            # number of valid readings so far

    while True:
        current_rssi = None
        found = False
        
        try:
            for network in wifi.radio.start_scanning_networks():
                if network.ssid == MY_SSID:
                    current_rssi = network.rssi
                    print(f"{time.monotonic():.1f}s | {MY_SSID} → RSSI = {current_rssi} dBm", end="")
                    found = True
                    break
            
            wifi.radio.stop_scanning_networks()
            
            if found and current_rssi is not None:
                # Update running total
                total_sum += current_rssi
                count += 1
                
                # Calculate and show average
                if count > 0:
                    avg_rssi = total_sum / count
                    print(f"   |   Avg ({count} readings): {avg_rssi:.1f} dBm")
                else:
                    print("   |   Avg: waiting...")
            else:
                print("   |   Could not see your SSID (hidden, out of range, or scan miss)")
        
        except Exception as e:
            print(f"Scan error: {e}")
            wifi.radio.stop_scanning_networks()  # cleanup on error
        
        time.sleep(0.1)  # your fast polling; increase to 1–5 if needed
        if count > cycles:
            return avg_rssi

cycles = 10
avg_rssi = measure_signal_strength(MY_SSID, cycles)
print(f"Avg ({cycles} readings): {avg_rssi:.1f} dBm")
