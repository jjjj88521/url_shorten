import argparse
import asyncio
import logging
import os
import time
import uvicorn
from config.logger import logger
from config.config import settings


def main():
    parser = argparse.ArgumentParser(
        description="Run FastAPI application with different settings."
    )
    parser.add_argument(
        "--env",
        choices=["dev", "pro"],
        default="dev",
        help="Choose the environment to run the application.",
    )

    args = parser.parse_args()
    os.environ["FASTAPI_ENV"] = args.env  # 設置環境變數，用於讀取 .env 檔案

    if args.env == "dev":
        logging.info("Running in development environment")
    elif args.env == "prod":
        logging.info("Running in production environment")

    try:
        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=8000,
            log_level=None,
            reload=True,
        )
    except KeyboardInterrupt:
        print("Server stopped by user")
    except asyncio.CancelledError:
        print("Asyncio loop was cancelled")


if __name__ == "__main__":
    main()
