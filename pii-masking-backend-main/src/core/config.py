import os
from typing import Optional

class Settings:
    PROJECT_NAME: str = "PII Detection & Masking Enterprise Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Feature Flags
    ENABLE_AUTH: bool = os.getenv("ENABLE_AUTH", "false").lower() == "true"
    ENABLE_AUDIT: bool = os.getenv("ENABLE_AUDIT", "true").lower() == "true"
    ENABLE_FILE_ENCRYPTION: bool = os.getenv("ENABLE_FILE_ENCRYPTION", "false").lower() == "true"
    
    # Storage & TTL
    FILE_TTL_SECONDS: int = int(os.getenv("FILE_TTL_SECONDS", "3600"))  # 1 hour default
    ENCRYPTION_SECRET_KEY: str = os.getenv("ENCRYPTION_SECRET_KEY", "super-secret-local-enterprise-key-32b!")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pii_enterprise.db")
    
    # AI Fallback Settings
    OFFLINE_MODE: bool = os.getenv("OFFLINE_MODE", "false").lower() == "true"

settings = Settings()
