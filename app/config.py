from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

ENV_FILE = BASE_DIR / ".env"
LOG_FILE_PATH = BASE_DIR / "log.txt"
