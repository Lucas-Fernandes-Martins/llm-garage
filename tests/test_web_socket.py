import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://127.0.0.1:8000/finetune/ws/train"
    async with websockets.connect(uri, open_timeout=60, ping_interval=20, ping_timeout=20) as websocket:
        # Define the JSON payload with training parameters
        payload = {
            "model_name": "princeton-nlp/Sheared-LLaMA-1.3B",
            "dataset_path": "data_test.json"
        }
        # Send the payload as a JSON string
        await websocket.send(json.dumps(payload))
        
        # Listen for messages from the server
        async for message in websocket:
            print(message)

asyncio.run(test_websocket())