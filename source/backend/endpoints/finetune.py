from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from utils.training import run_finetuning
from finetuning.finetuning import *
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket
from finetuning.finetuning import FineTuningEngine
from utils.file_handler import UPLOAD_DIR
import time
import asyncio

class FinetuneRequest(BaseModel):
    model_name: str
    dataset_path: str
    epochs: int
    learning_rate: float


requests = []

router = APIRouter()

@router.websocket("/ws/train")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Wait for the client to send the JSON payload with training parameters
    try:
        payload = await websocket.receive_json()
    except Exception as e:
        await websocket.send_json({"error": "Invalid JSON payload", "details": str(e)})
        await websocket.close()
        return

    # Extract the model name and other parameters from the payload, using defaults if necessary
    model_name = payload.get("model_name", "princeton-nlp/Sheared-LLaMA-1.3B")
    dataset_path = payload.get("dataset_path")
    epochs = payload.get("epochs")
    learning_rate = payload.get("learning_rate")

    await websocket.send_json({"test connection": "success", "model_name": model_name, "dataset_path": dataset_path})
    
    # Get the main event loop
    main_loop = asyncio.get_running_loop()
    
    engine = FineTuningEngine(model_name, websocket)
    dataset = engine.load_new_dataset(dataset_path)
    engine.set_lora_fine_tuning(dataset, 
                                learning_rate= learning_rate, 
                                epochs = epochs, 
                                callback_loop=main_loop)  # Pass the loop to set up callbacks
    
    # Offload the blocking training process to a thread
    await asyncio.to_thread(engine.perform_fine_tuning)
    
    await asyncio.sleep(1)
    try:
        await websocket.send_json({"status": "training complete", "weights_url": engine.weights_path})
    except Exception as e:
        print("Error sending final update:", e)
    await websocket.close()

@router.post("/set_train_params")
async def set_train_params(request:FinetuneRequest):
    model_name = request.model_name
    dataset_path = request.dataset_path

    file_name = UPLOAD_DIR + "/" + dataset_path
    if not os.path.exists(UPLOAD_DIR):
        raise HTTPException(status_code=500, detail=str('Dataset not found'))

    new_request = FinetuneRequest(model_name=model_name, dataset_path=file_name)
    requests.append(new_request)
    return {"status": "success"}
    


@router.post("/")
async def finetune(request:FinetuneRequest):
    try:
        # This function should run the LoRA fine-tuning process and return a path to the saved weights.
        # weights_path = run_finetuning(model_name, dataset_path)
        # if not os.path.exists(weights_path):
        #     raise HTTPException(status_code=500, detail="Fine-tuning failed to produce weights")
        # # Return file as a download
        # return FileResponse(path=weights_path, filename=os.path.basename(weights_path))
        model_name = request.model_name
        dataset_path = request.dataset_path

        engine = FineTuningEngine(model_name)
        engine.load_new_dataset(dataset_path)
        engine.set_lora_fine_tuning()
        engine.perform_fine_tuning()
        return {"model_name": request.model_name, "dataset_path": request.dataset_path}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
