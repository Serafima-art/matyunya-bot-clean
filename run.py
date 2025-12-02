# -*- coding: utf-8 -*-
import os
import sys
import asyncio
import argparse
from pathlib import Path

# ---------------------------------------
# 1) Настройка путей (как было у тебя)
# ---------------------------------------
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# ---------------------------------------
# 2) Парсим аргументы командной строки
# ---------------------------------------
parser = argparse.ArgumentParser(description="Run Matyunya bot")
parser.add_argument(
    "--dev",
    action="store_true",
    help="Запустить Матюню в режиме разработки с .env.dev",
)
args = parser.parse_args()

# ---------------------------------------
# 3) Определяем нужный .env файл
# ---------------------------------------
env_file = project_root / (".env.dev" if args.dev else ".env")

if not env_file.exists():
    raise FileNotFoundError(f"Файл {env_file} не найден.")

# ---------------------------------------
# 4) Загружаем переменные окружения
# ---------------------------------------
from dotenv import load_dotenv
load_dotenv(env_file)

bot_token = os.getenv("BOT_TOKEN")

if not bot_token:
    raise RuntimeError("BOT_TOKEN не найден в выбранном .env файле!")

# ---------------------------------------
# 5) Импортируем основной движок Матюни
# ---------------------------------------
from matunya_bot_final.main_v2 import main


# ---------------------------------------
# 6) Запускаем Матюню
# ---------------------------------------
if __name__ == "__main__":
    mode = "DEV" if args.dev else "PROD"
    print(f"Матюня запускается... режим: {mode}")
    asyncio.run(main(bot_token=bot_token))
