animator_configs = [{'fn': 'jim.json', 'device': 'engine', 'address': '1111', 'baseUrl': 'a.local', 'animatorIpAddress': '192.168.0.101',
                     'table_data': [['f2', 'API_test-animation_{"an": "HORN"}', None], ['speed', '', None],['direction', '', None],]}]


loco = {
    "address": 3,
    "speed": 20,
    "direction": "Forward",
    "speed_steps": 128,
    "functions": {
        "f0": True,
        "f1": True,
        "f2": False,
        "f3": False,
        "f4": False,
        "f5": False,
        "f6": False,
        "f7": False,
        "f8": False,
        "f9": False,
        "f10": False,
        "f11": False,
        "f12": False,
        "f13": False,
        "f14": False,
        "f15": False,
        "f16": False,
        "f17": False,
        "f18": False,
        "f19": False,
        "f20": False,
        "f21": False,
        "f22": False,
        "f23": False,
        "f24": False,
        "f25": False,
        "f26": False,
        "f27": False,
        "f28": True
    }
}

def find_matches(loco, animator_configs):
    """Find matches between loco state and animator_configs table_data."""
    matches = []
    for animator_config in animator_configs:
        if animator_config["address"] == loco["address"]:
            for row in animator_config['table_data']:
                # Check for speed match
                if row[0] == loco["speed"]:
                    matches.append((row, animator_config))
                # Check for direction match
                if row[0] == loco["direction"]:
                    matches.append((row, animator_config))
                # Check for function state match (e.g., "f0=ON", "f1=OFF")
                for func_key, func_state in loco["functions"].items():
                    func_str = f"{func_key}={'ON' if func_state else 'OFF'}"
                    if row[0] == func_str:
                        matches.append((row, animator_config))
    return matches


