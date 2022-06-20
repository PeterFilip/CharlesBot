import asyncio
import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosed
from classifier import IntentClassifier



#init model  
classifier = IntentClassifier()
classifier.load()


#Coroutine to monitor dataset and retrain
async def monitor_dataset():
    prev_dataset = classifier.query_dataset()
    while True:
        curr_dataset = classifier.query_dataset()

        if curr_dataset != prev_dataset:
            #retrain
            print("Retraining...")
            classifier.retrain()
            prev_dataset = curr_dataset

        await asyncio.sleep(0.1)



async def serve(websocket, path):
    try:
        while True:
            # receive inquery from client
            client_inquery = await websocket.recv()
            # feed it through classifer
            result = classifier.query_intent(client_inquery)[1]
            # send result back
            await websocket.send(result)
    except (ConnectionClosedOK, ConnectionClosed):
        pass




async def main():
    async with websockets.serve(serve, "localhost", 8765):
        await asyncio.Future()  # run forever




if __name__ == "__main__":
    asyncio.gather(main(), monitor_dataset())
    asyncio.get_event_loop().run_forever()