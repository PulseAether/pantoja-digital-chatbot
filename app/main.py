import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes.chat import router as chat_router

load_dotenv()

app = FastAPI(title="Pixel - Pantoja Digital Chatbot")

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://pantojadigital.com,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "pixel-chatbot"}
