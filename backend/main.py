import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import dashboard, health, webhook
from core.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="HisaabAI Backend",
    description="AI Business Assistant for Pakistani SMEs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router, tags=["WhatsApp"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(health.router, tags=["Health"])

# Meta sometimes gets saved without /webhook/whatsapp — accept webhooks on / too
app.add_api_route(
    "/",
    webhook.verify_webhook,
    methods=["GET"],
    tags=["WhatsApp"],
    include_in_schema=False,
)
app.add_api_route(
    "/",
    webhook.receive_message,
    methods=["POST"],
    tags=["WhatsApp"],
    include_in_schema=False,
)


@app.on_event("startup")
async def startup():
    print("🚀 HisaabAI Backend Started")
    print(f"   Environment: {settings.ENVIRONMENT}")
