import os
from dotenv import load_dotenv

# 根據環境變數設定 .env 檔案名稱
environment = os.getenv("FASTAPI_ENV", "dev")
dotenv_file = f".env.{environment}"

# 讀取對應的 .env 檔案
load_dotenv(dotenv_file)

# 從 .env 檔案中讀取變數
DATABASE_URL = os.getenv("DATABASE_URL")
