import asyncio
import redis
import cv2
import librosa

# Redis connection settings
REDIS_HOST = '10.0.0.216'
REDIS_PORT = 6379
REDIS_DB = 0

# Video settings
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 30

# Audio settings
AUDIO_BITRATE = 128000

# Lossy video compression settings
VIDEO_COMPRESSOR = cv2.VideoWriter_fourcc(*'X264')

# Lossless audio compression settings
AUDIO_COMPRESSOR = 'PCM'




async def produce_video_frames():
    # Open the video capture device (e.g. camera or file)
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Compress the video frame using X264
        compressed_frame = cv2.imencode('.avi', frame, [VIDEO_COMPRESSOR, int(VIDEO_WIDTH), int(VIDEO_HEIGHT), VIDEO_FPS])

        # Publish the compressed video frame to Redis Streams
        async with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB) as r:
            await r.xadd('video-stream', ' * '.join(map(str, compressed_frame)))


async def consume_and_uncompress_video_frames():
    async with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB) as r:
        while True:
            message = await r.xread({'video-stream': ''})
            if not message:
                break

            frame_data = message[0][1].decode('utf-8').split(' * ')
            frame = cv2.imdecode(frame_data, [cv2.IMECODE_X264])

            # Display the un compressed video frame
            cv2.imshow('Video', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()



async def produce_and_compress_audio_frames():
    async with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB) as r:
        while True:
            message = await r.xread({'audio-stream': ''})
            if not message:
                break

            frame_data = message[0][1].decode('utf-8')

            # Decompress the audio frame using PCM
            frame = np.frombuffer(frame_data.encode(), dtype=np.int16)

            # Play the un compressed audio frame
            stream = pyaudio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
            stream.start_stream()
            stream.write(frame.tobytes())
            stream.stop_stream()
            stream.close()

    pyaudio.terminate()


async def consume_audio_frames():
    # Open the audio file or capture device (e.g. microphone)
    y, sr = librosa.load('audio_file.wav', sr=None)

    for frame in librosa.effects.split(y, 0.1):
        # Compress the audio frame using PCM
        compressed_frame = frame.tobytes()

        # Publish the compressed audio frame to Redis Streams
        async with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB) as r:
            await r.xadd('audio-stream', str(compressed_frame))

async def main():
    await asyncio.gather(
        produce_video_frames(),
        consume_audio_frames()
    )

if __name__ == '__main__':
    asyncio.run(main())