import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Tải file .env chính xác từ thư mục gốc
load_dotenv(str(BASE_DIR / ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash").strip()
ENABLE_HOTKEY = os.getenv("ENABLE_HOTKEY", "true").lower() == "true"
HOTKEY = os.getenv("HOTKEY", "ctrl+shift+space")
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
ALWAYS_ON_TOP = os.getenv("ALWAYS_ON_TOP", "true").lower() == "true"
MAX_FILE_BYTES = int(os.getenv("MAX_FILE_BYTES", str(10 * 1024 * 1024)))
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "60000"))
BROWSER_TIMEOUT_MS = int(os.getenv("BROWSER_TIMEOUT_MS", "30000"))


def expand_path(value: str) -> str:
    return os.path.expandvars(os.path.expanduser(value.strip()))


def default_search_roots():
    home = Path.home()
    return [str(home / 'Desktop'), str(home / 'Documents'), str(home / 'Downloads')]

SEARCH_ROOTS = [expand_path(x) for x in os.getenv("SEARCH_ROOTS", ";".join(default_search_roots())).split(";") if x.strip()]
DB_PATH = DATA_DIR / "agent.db"
APP_CACHE_PATH = DATA_DIR / "app_registry.json"
BROWSER_PROFILE_DIR = DATA_DIR / "browser_profile"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)