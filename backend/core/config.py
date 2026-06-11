from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENVIRONMENT: str = "development"
    APP_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    SECRET_KEY: str = "change-this-in-production"

    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "hisaab_verify_2025"
    WHATSAPP_API_VERSION: str = "v21.0"
    WHATSAPP_APP_SECRET: str = ""

    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    DATABASE_URL: str = ""
    SUPABASE_STORAGE_BUCKET: str = "hisaab-files"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""

    UPSTASH_REDIS_URL: str = "redis://localhost:6379"

    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"

    ENABLE_WHISPER: bool = False
    ENABLE_OCR: bool = False
    ENABLE_QDRANT_MEMORY: bool = False


settings = Settings()
