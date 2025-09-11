from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

ENV_FILE = BASE_DIR / ".env"
LOG_FILE_PATH = BASE_DIR / "log.txt"

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

settings = Config()
