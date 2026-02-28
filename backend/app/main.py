from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from backend.app.api import requirements, design, simulation, export, codegen

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

app = FastAPI(
    title="VitaBlueprint – Generative System Design & Digital Twin",
    version="1.0.0",
    description="Deterministic medical device system design and compliance platform"
)

# Allow the frontend dev server to make requests (adjust origins for production)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://129.154.227.67",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requirements.router, prefix="/requirements")
app.include_router(design.router, prefix="/design")
app.include_router(simulation.router, prefix="/simulation")
app.include_router(export.router, prefix="/export")
app.include_router(codegen.router, prefix="/codegen")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "VitaBlueprint backend running"}