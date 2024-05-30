import asyncio
# from vidgear.gears.asyncio import NetGear_Async
from vidgear.gears import NetGear
import cv2

async def stream_video():
    # Open the video source
    video_stream = cv2.VideoCapture('vid.mp4')
    if not video_stream.isOpened():
        print("Error: Could not open video.")
        return

    # Define NetGear client with default parameters
    client = NetGear(address='127.0.0.1', port='5454', protocol='tcp', pattern=0, receive_mode=False)

    while True:
        # Read frame from video stream
        grabbed, frame = video_stream.read()
        if not grabbed:
            break

        # Send frame to server
        client.send(frame)

    # Release resources
    video_stream.release()
    await client.close()

# Run the async function
asyncio.run(stream_video())
