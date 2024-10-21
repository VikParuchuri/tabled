from typing import Optional

from dotenv import find_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # General
    IN_STREAMLIT: bool = False
    TORCH_DEVICE: Optional[str] = None

    # Batch sizes
    # See https://github.com/VikParuchuri/surya for default values
    ## Table recognition
    TABLE_REC_BATCH_SIZE: Optional[int] = None
    ## OCR
    RECOGNITION_BATCH_SIZE: Optional[int] = None
    ## Text detector
    DETECTOR_BATCH_SIZE: Optional[int] = None
    ## Layout
    LAYOUT_BATCH_SIZE: Optional[int] = None

    class Config:
        env_file = find_dotenv("local.env")
        extra = "ignore"


settings = Settings()