import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:CTVkFKPwcMuRwNoknMlnYuToVORDaCsS@postgres.railway.internal:5432/railway"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    port: int

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
