import numpy as np
from utilities import p,FORMAT,CHANNELS,RATE,CHUNK,THRESHOLD,init_jarvis

# Open audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Main loop
def main():

    print("JARVIS is now listening...")
    print("*" * 50)

    try:
        while True:
            # Read audio data
            data = stream.read(CHUNK)

            # Check if the root mean square is above the threshold
            rms = np.sqrt(np.mean(np.square(np.frombuffer(data, dtype=np.int16))))

            if rms > THRESHOLD:
                init_jarvis()

    except KeyboardInterrupt:
        print("Exiting...")
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()