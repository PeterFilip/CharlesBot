from vidgear.gears import NetGear
import cv2
import numpy as np

# Define NetGear client with compression enabled
options = {'compression_param': cv2.IMWRITE_JPEG_QUALITY, 'compression_quality': 50, "jpeg_compression": True}  # Adjust quality as needed
client = NetGear(address='127.0.0.1', port='5454', protocol='tcp', pattern=1, logging=True, **options)

# Open the video source
video_stream = cv2.VideoCapture('vid.mp4')
if not video_stream.isOpened():
    print("Error: Could not open video.")
    exit()

while True:
    # Read frame from video stream
    grabbed, frame = video_stream.read()
    if not grabbed:
        break

    # Send frame to server
    client.send(frame)

# Send an "end frame" (a blank frame with specific content)
end_frame = np.zeros((10, 10, 3), np.uint8)  # A small black frame to indicate end of stream
client.send(end_frame)

# Release resources
video_stream.release()
# client.close()  # NOTE: this sends signal to server to terminate and not receive connections from client(s) again in the future
