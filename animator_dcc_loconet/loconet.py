#!/usr/local/bin/python3.11

import serial
import argparse
import time

def interpret_loconet_commands(commands, track_errors=False):
    """
    Interpret LocoNet commands for locomotives (A0, A1, A2) and switches (B0, BC).
    Skip B4 (LONG_ACK) and ED packets to show only executed commands.
    
    Args:
        commands (list): List of LocoNet commands as strings, e.g., ['A1 06 20 78', 'B0 00 10 5F'].
        track_errors (bool): If True, include error info (excluding B4).
        
    Returns:
        list: List of dictionaries containing the state for each command.
    """
    slot_states = {}
    output = []
    
    for cmd in commands:
        cmd_clean = cmd.replace('[', '').replace(']', '')
        bytes = cmd_clean.split()
        if len(bytes) < 3:
            continue
        try:
            opcode = int(bytes[0], 16)
            byte1 = int(bytes[1], 16) if len(bytes) > 1 else 0
            byte2 = int(bytes[2], 16) if len(bytes) > 2 else 0
        except ValueError:
            continue
            
        error = None
        if opcode in [0xA0, 0xA1, 0xA2]:
            slot = byte1
            if slot not in slot_states:
                slot_states[slot] = {
                    'speed': 0,
                    'direction': 'Forward',
                    **{f'F{i}': False for i in range(29)}
                }
            identifier = f"Slot {slot}"
            state = slot_states[slot]
        elif opcode == 0xB0:  # Switch command
            sw1 = byte1
            sw2 = byte2
            switch_number = (sw1 & 0x7F) + 1  # LT1 = 0x00 + 1
            switch_state = 'Thrown' if (sw2 & 0x01) else 'Closed'
            output_on = (sw2 & 0x10) != 0
            identifier = f"Switch LT{switch_number}"
            output.append({
                'slot_or_address': identifier,
                'switch_number': switch_number,
                'speed': None,
                'direction': None,
                **{f'F{i}': None for i in range(29)},
                'command': cmd,
                'switch_state': switch_state,
                'switch_on': output_on,
                'error': None
            })
            continue
        elif opcode == 0xBC:  # Switch state request
            sw1 = byte1
            switch_number = (sw1 & 0x7F) + 1
            identifier = f"Switch LT{switch_number}"
            output.append({
                'slot_or_address': identifier,
                'switch_number': switch_number,
                'speed': None,
                'direction': None,
                **{f'F{i}': None for i in range(29)},
                'command': cmd,
                'switch_state': None,
                'switch_on': None,
                'error': None
            })
            continue
        elif opcode in [0xB4, 0xED]:  # Skip LONG_ACK and ED packets
            continue
        else:
            if opcode == 0xBB and track_errors:
                error = "Request Command Station OpSwitches (or DCS210/DCS240 check for multiple command stations on LocoNet)"
                output.append({
                    'slot_or_address': "N/A",
                    'speed': None,
                    'direction': None,
                    **{f'F{i}': None for i in range(29)},
                    'command': cmd,
                    'error': error
                })
            continue
        
        if opcode == 0xA0:
            state['speed'] = byte2
        elif opcode == 0xA1:
            state['direction'] = 'Reverse' if (byte2 & 0x20) else 'Forward'
            state['F0'] = bool(byte2 & 0x10)
            state['F1'] = bool(byte2 & 0x08)
            state['F2'] = bool(byte2 & 0x04)
            state['F3'] = bool(byte2 & 0x02)
            state['F4'] = bool(byte2 & 0x01)
        elif opcode == 0xA2:
            state['F5'] = bool(byte2 & 0x08)
            state['F6'] = bool(byte2 & 0x04)
            state['F7'] = bool(byte2 & 0x02)
            state['F8'] = bool(byte2 & 0x01)
        
        output.append({
            'slot_or_address': identifier,
            'speed': state['speed'],
            'direction': state['direction'],
            **{f'F{i}': state[f'F{i}'] for i in range(29)},
            'command': cmd,
            'error': error
        })
    
    return output

def format_log_entry(state):
    """Format the state dictionary as a log entry matching JMRI LocoNet Monitor."""
    cmd = state['command']
    identifier = state['slot_or_address']
    
    if state['error']:
        return f"{cmd}  {state['error']}."
    
    if identifier.startswith("Slot"):
        slot = int(identifier.split()[1])
        direction = state['direction']
        speed = state['speed']
        f0_f4 = [f"F{i}={'On' if state[f'F{i}'] else 'Off'}" for i in range(5)]
        functions = " ".join(f0_f4)
        return f"{cmd}  Set loco in slot {slot} direction {direction} speed {speed} {functions}."
    elif identifier.startswith("Switch"):
        switch = state['switch_number']
        if state['switch_state'] is None:  # BC packet
            return f"{cmd}  Request status of switch LT{switch} ()."
        switch_state = state['switch_state']
        on = "On" if state['switch_on'] else 'Off'
        return f"{cmd}  Requesting Switch at LT{switch} to {switch_state} (Output {on})."
    
    return f"{cmd}  Unknown command."

def read_serial_port(port, baudrate=57600):
    """Read LocoNet packets from the serial port and yield formatted commands."""
    try:
        with serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            rtscts=False,
            xonxoff=False
        ) as ser:
            print(f"Reading from serial port {port} at {baudrate} baud...")
            buffer = []
            while True:
                byte = ser.read(1)
                if not byte:
                    continue
                byte_val = int.from_bytes(byte, 'big')
                if byte_val & 0x80:
                    if buffer:
                        if len(buffer) >= 2:
                            cmd = f"[{' '.join(f'{b:02X}' for b in buffer)}]"
                            yield cmd
                        buffer = [byte_val]
                    else:
                        buffer = [byte_val]
                else:
                    buffer.append(byte_val)
                if len(buffer) > 20:
                    print(f"Buffer overflow, resetting: [{' '.join(f'{b:02X}' for b in buffer)}]")
                    buffer = []
    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except KeyboardInterrupt:
        print("\nStopped serial reading")

def main():
    parser = argparse.ArgumentParser(description="LocoNet command interpreter")
    parser.add_argument('--serial', action='store_true', help="Read from serial port")
    parser.add_argument('--port', default='/dev/tty.usbmodem520021191', 
                        help="Serial port (default: /dev/tty.usbmodem520021191)")
    parser.add_argument('--baudrate', type=int, default=57600, 
                        help="Baud rate (default: 57600)")
    args = parser.parse_args()
    
    while True:
        if True:
            commands = []
            for cmd in read_serial_port(args.port, args.baudrate):
                commands.append(cmd)
                results = interpret_loconet_commands([cmd], track_errors=True)
                for state in results:
                    print(format_log_entry(state))
        else:
            commands = [
                '[A1 06 20 78]', '[A1 06 00 58]', '[A0 06 00 59]', '[A0 06 22 7B]',
                '[BC 00 30 73]', '[B4 3C 10 67]', '[B0 00 10 5F]', '[B4 30 00 7B]',
                '[B0 00 00 4F]', '[B4 30 00 7B]', '[B0 00 30 7F]', '[B4 30 00 7B]',
                '[B0 00 20 6F]', '[B4 30 00 7B]', '[B0 00 10 5F]', '[B4 30 00 7B]',
                '[B0 00 00 4F]', '[B4 30 00 7B]', '[B0 00 30 7F]', '[B4 30 00 7B]',
                '[B0 00 20 6F]', '[B4 30 00 7B]', '[BC 01 30 72]', '[B4 3C 10 67]',
                '[B0 01 10 5E]', '[B4 30 00 7B]', '[B0 01 00 4E]', '[B4 30 00 7B]',
                '[B0 01 30 7E]', '[B4 30 00 7B]', '[B0 01 20 6E]', '[B4 30 00 7B]',
                '[BC 02 30 71]', '[B4 3C 30 47]', '[B0 02 10 5D]', '[B4 30 00 7B]',
                '[B0 02 00 4D]', '[B4 30 00 7B]', '[B0 02 30 7D]', '[B4 30 00 7B]',
                '[B0 02 20 6D]', '[B4 30 00 7B]'
            ]
            
            results = interpret_loconet_commands(commands, track_errors=True)
            for state in results:
                print(format_log_entry(state))

if __name__ == "__main__":
    main()