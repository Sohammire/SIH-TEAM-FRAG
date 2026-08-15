import os

class Settings:
    PROJECT_NAME: str = "TyreIQ API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tyreiq.db")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")

settings = Settings()
