import asyncio
import cv2
import numpy as np
import websockets
import aiohttp

class StreamClient:
    def __init__(self, server_url):
        self.http_url = server_url
        self.ws_url = f"ws://{server_url.split('://')[1]}"
        self.stream_id = None
        self.video_producer_ws = None
        self.video_consumer_ws = None

    async def create_stream(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.http_url}/create_stream") as response:
                if response.status == 200:
                    data = await response.json()
                    self.stream_id = data["stream_id"]
                    print(f"Created stream with ID: {self.stream_id}")
                else:
                    raise Exception(f"Failed to create stream: {response.status}")

    async def connect_video_producer(self):
        self.video_producer_ws = await websockets.connect(f"{self.ws_url}/ws/produce/video/{self.stream_id}")

    async def connect_video_consumer(self):
        self.video_consumer_ws = await websockets.connect(f"{self.ws_url}/ws/consume/video/{self.stream_id}")

    async def push_video_frame(self, frame_data):
        await self.video_producer_ws.send(frame_data)

    async def consume_video_frames(self):
        while True:
            video_frame = await self.video_consumer_ws.recv()
            nparr = np.frombuffer(video_frame, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imshow('Received Video', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

async def video_producer(client):
    cap = cv2.VideoCapture('vid.mp4')
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return

    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    if frame_rate == 0:
        print("Warning: Could not read frame rate from video. Using default of 30 fps.")
        frame_rate = 30

    delay = 1 / frame_rate

    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video reached. Restarting from beginning.")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        await client.push_video_frame(buffer.tobytes())
        await asyncio.sleep(delay)

    cap.release()

async def main():
    client = StreamClient("http://localhost:8000")
    try:
        await client.create_stream()
        await client.connect_video_producer()
        await client.connect_video_consumer()

        producer_task = asyncio.create_task(video_producer(client))
        consumer_task = asyncio.create_task(client.consume_video_frames())

        await asyncio.gather(producer_task, consumer_task)
    except Exception as e:
        print(f"An error occurred: {e}")




if __name__ == "__main__":
    asyncio.run(main())