import numpy as np
from utilities import p,wave_recorder,FORMAT,CHANNELS,RATE,CHUNK,THRESHOLD,wake_word

# Open audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# FOR TESTING PURPOSES - Set up the wave file writer
wf = wave_recorder()

# Main loop
def init_jarvis():

    try:
        while True:
            # Read audio data
            data = stream.read(CHUNK)
            # FOR TESTING PURPOSES - Write data to file
            wf.writeframes(data)

            # Check if the root mean square is above the threshold
            rms = np.sqrt(np.mean(np.square(np.frombuffer(data, dtype=np.int16))))

            if rms > THRESHOLD:
                wake_word()

    except KeyboardInterrupt:
        print("Exiting...")
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    init_jarvis()