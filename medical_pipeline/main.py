import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.services.api import router as medical_router
from src.services.chat_api import router as chat_router

from src.services.vector_service import AzureVectorService

load_dotenv()

app = FastAPI(
    title="Medical Agentic RAG API",
    description="Bachelor Thesis: Automated Medical Report Analysis System",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    try:
        print(" Checking Azure AI Search infrastructure...")
        vector_service = AzureVectorService()
        vector_service.create_index()
        print(" Infrastructure is ready!")
    except Exception as e:
        print(f" Critical Error during startup: {str(e)}")

app.include_router(medical_router)

app.include_router(chat_router)


@app.get("/")
async def welcome():
    return {
        "project": "Agentic Multi-Agent RAG Assistant",
        "docs": "/docs",
        "status": "online",
        "author": "Artur Serobyan"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
