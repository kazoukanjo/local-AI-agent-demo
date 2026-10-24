import logging
from .config import LOG_DIR

def setup_logging():
    logging.basicConfig(filename=str(LOG_DIR/'agent.log'),level=logging.INFO,format='%(asctime)s | %(levelname)s | %(message)s',encoding='utf-8')
