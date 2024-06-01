from vidgear.gears import NetGear
import cv2
import numpy as np

# Define NetGear server with default parameters
server = NetGear(address='127.0.0.1', port='5454', protocol='tcp', pattern=0, receive_mode=True, logging=True, timeout=999999)

# Open video writer
output_stream = None
codec = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 codec
fps = 30
output_file = 'out.mp4'

while True:
    try:
        # Receive frame from client
        frame = server.recv()
        if frame is None:
            continue

        # Check for "end frame"
        if frame.shape == (10, 10, 3) and np.array_equal(frame, np.zeros((10, 10, 3), np.uint8)):
            print("End frame received. Closing video writer.")
            if output_stream:
                output_stream.release()
                output_stream = None
            continue

        if output_stream is None:
            # Initialize video writer with the frame's dimensions
            height, width = frame.shape[:2]
            output_stream = cv2.VideoWriter(output_file, codec, fps, (width, height))
            if not output_stream.isOpened():
                print("Error: Could not open video writer.")
                break

        # Write the frame to output video file
        output_stream.write(frame)

    except Exception as e:
        print(f"Error occurred: {e}")
        break

# Release resources
if output_stream:
    output_stream.release()
server.close()
print("Server closed and resources released.")
