# backend/app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Required variables will raise an error if not set in .env
    Optional variables have default values.
    """
    
    # ===================
    # Application
    # ===================
    APP_NAME: str = Field(default="VectorizeDB")
    DEBUG: bool = Field(default=False)
    API_V1_PREFIX: str = Field(default="/api/v1")
    
    # Required - No default, must be in .env
    SECRET_KEY: str = Field(..., description="Secret key for signing tokens")
    
    # ===================
    # Database (Required)
    # ===================
    SUPABASE_DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    
    # ===================
    # Supabase (Required)
    # ===================
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase anon/public key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., description="Supabase service role key")
    SUPABASE_JWT_SECRET: str = Field(..., description="Supabase JWT secret for token verification")
    
    # ===================
    # Security / JWT
    # ===================
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30)
    
    # ===================
    # Auth Settings
    # ===================
    REQUIRE_EMAIL_VERIFICATION: bool = Field(default=False)
    
    # ===================
    # CORS
    # ===================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )
    
    # ===================
    # Frontend URLs (Required for auth redirects)
    # ===================
    FRONTEND_URL: str = Field(..., description="Frontend application URL")
    PASSWORD_RESET_REDIRECT: str = Field(default="/auth/reset-password")
    EMAIL_CONFIRM_REDIRECT: str = Field(default="/auth/callback")
    
    # ===================
    # File Uploads
    # ===================
    UPLOAD_DIR: str = Field(
        default=str(Path(__file__).parent.parent / "uploads")
    )
    MAX_FILE_SIZE: int = Field(default=104857600)  # 100MB
    
    # ===================
    # Email / SMTP (Optional)
    # ===================
    SMTP_HOST: Optional[str] = Field(default=None)
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    SMTP_FROM_EMAIL: str = Field(default="noreply@vectorizedb.com")
    
    # ===================
    # OAuth Providers (Optional)
    # ===================
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None)
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None)
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None)
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None)

    # ===================
    # Computed Properties
    # ===================
    @property
    def password_reset_url(self) -> str:
        """Full URL for password reset redirect"""
        return f"{self.FRONTEND_URL}{self.PASSWORD_RESET_REDIRECT}"
    
    @property
    def email_confirm_url(self) -> str:
        """Full URL for email confirmation redirect"""
        return f"{self.FRONTEND_URL}{self.EMAIL_CONFIRM_REDIRECT}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars not defined here


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reading .env file on every call.
    """
    return Settings()


# Global settings instance
settings = get_settings()