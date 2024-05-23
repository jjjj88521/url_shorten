from datetime import datetime
import logging
import os

file_path = os.path.dirname(os.path.dirname(__file__))

# 設定全局logger
logging.basicConfig(
    level=None,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"{file_path}/logs/app-{datetime.now().strftime('%Y%m%d')}.log",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

# 獲取特定的logger
logger = logging.getLogger(__name__)
