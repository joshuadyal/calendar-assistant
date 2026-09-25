import logging
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

logger = logging.getLogger("calendar_agent")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/agent.log", encoding="utf-8")

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
