from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints import model, dataset, finetune, download, inference

app = FastAPI(title="LLM Garage API")

origins = [
    "http://localhost:3000",  # your React app's origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(model.router, prefix="/model", tags=["Model"])
app.include_router(dataset.router, prefix="/dataset", tags=["Dataset"])
app.include_router(finetune.router, prefix="/finetune", tags=["Fine-tuning"])
app.include_router(download.router, prefix="/download", tags=["Download"])
app.include_router(inference.router, prefix="/inference", tags=["Inference"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
