import pyaudio


def print_input_device_info():
    p = pyaudio.PyAudio()

    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["maxInputChannels"] > 0:
            print(f"Device ID: {device_info['index']}")
            print(f"Device Name: {device_info['name']}")
            print(f"Sample Rate: {device_info['defaultSampleRate']}")
            print(f"Max Input Channels: {device_info['maxInputChannels']}")
            print("--------------")

    p.terminate()


print_input_device_info()
