from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import asyncio
import concurrent.futures

router = APIRouter()
executor = concurrent.futures.ThreadPoolExecutor()

def load_model_and_tokenizer(model_name: str, weights_path: str):
    # Load the tokenizer and base model using the provided model name
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
    # Load fine-tuned adapter weights via PEFT's API

    # model = PeftModel.from_pretrained(base_model, weights_path)
    # model.eval()
    # return model, tokenizer
    # Load the state dict from the weights file
    state_dict = torch.load(weights_path, map_location=torch.device("cpu"))
    
    # Load the state dict into the base model
    base_model.load_state_dict(state_dict, strict=False)
    base_model.eval()

    return base_model, tokenizer

def generate_text(prompt: str, model, tokenizer):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        inputs.input_ids,
        max_length=20,            
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7            
    )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text

@router.websocket("/ws/test_llm")
async def test_llm_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        # Wait for a JSON message containing prompt, model_name, and weights_path
        data = await websocket.receive_json()
        prompt = data.get("prompt")
        model_name = data.get("model_name")
        weights_path = data.get("weights_path")
        
        if not prompt or not model_name or not weights_path:
            await websocket.send_json({"error": "Prompt, model_name, and weights_path must be provided"})
            await websocket.close()
            return

        loop = asyncio.get_event_loop()
        try:
            # Offload the model loading to a background thread
            model, tokenizer = await loop.run_in_executor(executor, load_model_and_tokenizer, model_name, weights_path)
        except Exception as e:
            await websocket.send_json({"error": f"Error loading model or weights: {str(e)}"})
            await websocket.close()
            return

        try:
            # Offload the generation to a background thread
            generated_text = await loop.run_in_executor(executor, generate_text, prompt, model, tokenizer)
        except Exception as e:
            await websocket.send_json({"error": f"Error during generation: {str(e)}"})
            await websocket.close()
            return
        
        # Send the generated text back to the client
        await websocket.send_json({"response": generated_text})
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()
