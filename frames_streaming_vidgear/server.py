import asyncio
import cv2
from vidgear.gears.asyncio import NetGear_Async

# Apply the fix for Proactor event loop on Windows
if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def receive_video():
    # Define NetGear server with default parameters
    server = NetGear_Async(address='127.0.0.1', port='5454', protocol='tcp', pattern=0, receive_mode=True, timeout=9999999999).launch()

    # Open video writer
    output_stream = None
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 30
    width, height = 0, 0

    try:
        # Create a frame generator
        async for frame in server.recv_generator():
            if frame is None:
                await asyncio.sleep(0.5)  # Wait for new frames if none are received
                continue

            if output_stream is None:
                height, width = frame.shape[:2]
                output_stream = cv2.VideoWriter('out.mp4', codec, fps, (width, height))

            # Write the frame to output video file
            output_stream.write(frame)

            await asyncio.sleep(0)

    except asyncio.CancelledError:
        print("Server was cancelled.")
    finally:
        # Release resources
        if output_stream:
            output_stream.release()
        await server.close()




# Run the async function
asyncio.run(receive_video())
