import cv2
import numpy as np
import redis
from redis_streams.consumer import Consumer

# Connect to Redis
r = redis.Redis(host='10.0.0.216', port=6379, db=0, decode_responses=True)
STREAM = "video_stream1"
GROUP = "group1"

# Function to publish frames to Redis Stream
def publish_frames_to_stream(vid_file, stream_name):
    cap = cv2.VideoCapture(vid_file)
    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()

        # add frame to stream with unique ID
        data = {"id": i, "frame": frame_bytes}
        r.xadd(name=stream_name, fields=data)

        i += 1

    cap.release()

# Function to consume frames from Redis Stream and write to out.mp4
def consume_frames_from_stream(stream_name, output_file):
    consumer = Consumer(
        redis_conn=r,
        stream=STREAM,
        consumer_group=GROUP,
        batch_size=5,
        max_wait_time_ms=30000,
    )

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None
    frame_width, frame_height = None, None

    while True:
        messages = consumer.get_items()
        print("got em")
        for i, item in enumerate(messages):
            frame_bytes = item.data['frame']
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

            if out is None:
                frame_height, frame_width = frame.shape[:2]
                out = cv2.VideoWriter(output_file, fourcc, 20.0, (frame_width, frame_height))

            out.write(frame)

            consumer.remove_item_from_stream(item_id=item.msgid)

    out.release()

# Function to clear the stream
def clear_stream(stream_name):
    r.xtrim(stream_name, 0)

# Usage
if __name__ == "__main__":
    clear_stream(STREAM)
    publish_frames_to_stream('frames_streaming/vid.mp4', STREAM)
    # consume_frames_from_stream(STREAM, 'out.mp4')
