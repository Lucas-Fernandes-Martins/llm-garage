from fastapi import APIRouter

router = APIRouter()

@router.get("/select")
async def select_model(model_name: str):
    # Here you might check if the model_name is supported, load metadata, etc.
    return {"message": f"Model '{model_name}' selected"}
