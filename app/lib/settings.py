from dotenv import load_dotenv

import os
from pathlib import Path


env_path = Path().cwd().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "PROJECT-FAST-API"
    PROJECT_VERSION: str = "1.0"
    ACCESS_TOKEN_EXPIRE_IN_MINUTES:float= float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

settings = Settings()