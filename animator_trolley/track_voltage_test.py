def get_track_voltage():
    global track_voltage_file_number

    samples = 200
    total = 0.0
    readings = []

    for _ in range(samples):
        reading = track_a_in.value / 65536 * 3.3 * 14.7
        total += reading
        readings.append(reading)
        time.sleep(.0017)

    average = total / samples

    track_voltage_data = {
        "readings": readings,
        "average": average
    }

    file_name = "track_voltage_" + str(track_voltage_file_number) + ".json"
    files.write_json_file(file_name, track_voltage_data)

    track_voltage_file_number += 1

    return average