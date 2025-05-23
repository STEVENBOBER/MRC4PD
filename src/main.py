#!/usr/bin/env python3
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore

    dotenv_loaded = True
except ImportError:
    dotenv_loaded = False

from notifier import (
    setup_logger,
    load_data,
    compose_message,
    send_signal,
    ExcelFormatError,
)


def main():
    # load .env from repo root
    repo_root = Path(__file__).resolve().parent.parent

    # Only load .env if running locally
    if dotenv_loaded and os.getenv("GITHUB_ACTIONS") != "true":
        env_path = repo_root / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)

    logger = setup_logger(repo_root)
    logger.info("== New MRC4 notifier job run ==")

    # Check test mode
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    if test_mode:
        logger.info("⚠️ Running in TEST MODE — no messages will be sent.")

    # Required environment variables
    signal_number = os.getenv("SIGNAL_NUMBER")
    group_id = os.getenv("GROUP_ID")

    # Signal Error
    if not signal_number or not group_id:
        logger.error("Environment variables SIGNAL_NUMBER or GROUP_ID not set.")
        sys.exit(1)

    # Optional configuration
    alert_number = os.getenv("ALERT_NUMBER", signal_number)
    sheet_name = os.getenv("MRC4_SHEET", "MRC4")

    # Load and validate MRC4_PATH
    raw_path = os.getenv("MRC4_PATH")
    logger.info(f"MRC4_PATH from env: {raw_path}")
    logger.info(f"Working directory: {os.getcwd()}")

    if not raw_path:
        logger.error(
            "❌ MRC4_PATH is not set. Did you forget to add it as a GitHub secret?"
        )
        sys.exit(1)

    data_path = (repo_root / raw_path).resolve()
    logger.info(f"Resolved file path: {data_path}")

    if not data_path.is_file():
        logger.error(f"MRC4 Excel file not found at: {data_path}")
        sys.exit(1)

    try:
        # data pipeline
        df = load_data(data_path, logger, sheet=sheet_name)
        msg = compose_message(df, logger)

        if test_mode:
            logger.info(f"🔍 Test message content:\n{msg}")
        else:
            send_signal(msg, signal_number, group_id, logger)

    except ExcelFormatError as e:
        logger.error("ExcelFormatError detected, sending admin alert...")
        alert_msg = f"⚠️ MRC4 notifier skipped: {str(e)}"

        if not test_mode:
            send_signal(alert_msg, alert_number, group_id=None, logger=logger)
        sys.exit(1)

    except Exception:
        logger.exception("Unhandled exception occurred.")
        sys.exit(1)


if __name__ == "__main__":
    main()
