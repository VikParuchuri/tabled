from typing import Optional

from dotenv import find_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # General
    IN_STREAMLIT: bool = False
    TORCH_DEVICE: Optional[str] = None

    class Config:
        env_file = find_dotenv("local.env")
        extra = "ignore"


settings = Settings()