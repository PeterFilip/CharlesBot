import asyncio
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# In-memory storage for streams
streams = {}

class Stream:
    def __init__(self):
        self.video_queue = asyncio.Queue()
        self.video_consumers = set()

class StreamInfo(BaseModel):
    stream_id: str

@app.post("/create_stream")
async def create_stream():
    """
    Create a new stream and return its ID.

    Returns:
        dict: A dictionary containing the new stream's ID.
    """
    stream_id = str(uuid.uuid4())
    streams[stream_id] = Stream()
    return {"stream_id": stream_id}



@app.websocket("/ws/produce/video/{stream_id}")
async def produce_video(websocket: WebSocket, stream_id: str):
    await websocket.accept()
    if stream_id not in streams:
        await websocket.close(code=1000)
        return

    stream = streams[stream_id]

    try:
        while True:
            frame_data = await websocket.receive_bytes()
            await stream.video_queue.put(frame_data)

            for consumer in stream.video_consumers:
                await consumer.send_bytes(frame_data)

    except WebSocketDisconnect:
        print(f"Video producer disconnected from stream {stream_id}")



@app.websocket("/ws/consume/video/{stream_id}")
async def consume_video(websocket: WebSocket, stream_id: str):
    await websocket.accept()
    if stream_id not in streams:
        await websocket.close(code=1000)
        return

    stream = streams[stream_id]
    stream.video_consumers.add(websocket)

    try:
        while True:
            video_frame = await stream.video_queue.get()
            await websocket.send_bytes(video_frame)

    except WebSocketDisconnect:
        print(f"Video consumer disconnected from stream {stream_id}")
    finally:
        stream.video_consumers.remove(websocket)






if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# TODO: add endpoints to flush/delete streams
# TODO: add item expiration so that after x times the frames start getting deleted
    #-add endpoints to modify existing streams' params like expiration time

# TODO: have args in consume endpoint to delete frames upon consumption