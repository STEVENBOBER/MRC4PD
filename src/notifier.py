import os
import time
import subprocess
import logging
import pandas as pd  # type: ignore

from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler


class ExcelFormatError(Exception):
    """Custom error for bad Excel file structure."""

    pass


def setup_logger(repo_root: Path) -> logging.Logger:
    log_path = Path(os.getenv("LOG_PATH", repo_root / "logs" / "launchd.log"))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("mrc4_notifier")
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(fmt)
    logger.addHandler(console)

    return logger


def load_data(path: Path, logger: logging.Logger, sheet: str) -> pd.DataFrame:
    try:
        # Check if file is available before loading
        wait_seconds = 10
        attempts = 0

        # Check if file path exists.
        while not path.exists():
            logger.warning(
                f"⏳ MRC4.xlsx not found. Waiting for OneDrive to sync... Attempt {attempts + 1}"
            )
            time.sleep(5)
            attempts += 1
            if attempts * 5 >= wait_seconds:
                logger.error(
                    f"❌ MRC4.xlsx could not be found at {path} after waiting. Exiting."
                )
                raise FileNotFoundError(
                    f"Excel file {path} not available after waiting."
                )

        # 1st: Get all Excel sheet names
        all_sheets = pd.ExcelFile(path).sheet_names
        logger.info(f"Available sheets in {path.name}: {all_sheets}")

        # If a sheet not found, default to the first one
        if sheet not in all_sheets:
            logger.warning(
                f"⚠️ Requested sheet '{sheet}' not found. Defaulting to first sheet '{all_sheets[0]}'."
            )
            sheet = all_sheets[0]

        # Load the data
        df = pd.read_excel(path, sheet_name=sheet)

        # Detect unnamed columns
        unnamed_columns = [col for col in df.columns if col.startswith("Unnamed")]
        if len(unnamed_columns) >= len(df.columns) / 2:
            logger.error(
                f"❌ Bad Excel format detected: too many unnamed columns {unnamed_columns}"
            )
            raise ValueError(
                "Excel file format error: Headers missing or wrong. Please fix the MRC4.xlsx file."
            )

        logger.info(f"Loaded Excel data from {path} (sheet: {sheet})")
        return df

    except Exception:
        logger.exception(f"Unable to read Excel file at {path}")
        raise


def compose_message(df: pd.DataFrame, logger: logging.Logger) -> str:
    try:
        status_col = "Status"
        name_col = "Soldier Name"
        mrc4 = df[df[status_col].str.upper() == "MRC4"][name_col].tolist()

        today = datetime.now().strftime("%Y-%m-%d")
        if mrc4:
            names = ",\n".join(mrc4)
            body = (
                f"[{today}]\n"
                "Reminder: The following soldiers are currently listed as MRC4:\n\n"
                f"{names}\n\n"
                "Please have them schedule their medical readiness appointments ASAP.\n\n"
                "Also, please remind all soldiers on the flu shot list to send over the pictures of their flu shots uploaded to QTC."
            )
        else:
            body = f"[{today}]\nAll soldiers are currently medically ready. Great job!"

        logger.info("Message composed.")
        return body
    except Exception:
        logger.exception("Failed to compose message")
        raise


def send_signal(message: str, number: str, group: str, logger: logging.Logger):
    binary = os.getenv("SIGNAL_CLI_PATH")

    cmd = [binary, "-a", number, "send", "-g", group, "-m", message]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Signal message sent")
        logger.debug(result.stdout)
    except subprocess.CalledProcessError:
        logger.error("Failed to send Signal message")
        logger.error("stderr: " + (result.stderr if "result" in locals() else ""))
        raise
