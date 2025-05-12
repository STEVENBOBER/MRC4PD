#!/usr/bin/env python3

import os
import sys
from pathlib import Path

from dotenv import load_dotenv  # type: ignore

from notifier import (
    setup_logger,
    load_data,
    compose_message,
    send_signal,
    ExcelFormatError,
)


def main():
    # load .env from project root
    project_root = Path(__file__).parent.parent
    load_dotenv(dotenv_path=project_root / ".env")

    logger = setup_logger(project_root)

    logger.info("==New job run==")

    # configuration
    data_path = Path(os.getenv("MRC4_PATH", project_root / "data" / "MRC4.xlsx"))

    signal_number = os.getenv("SIGNAL_NUMBER")

    group_id = os.getenv("GROUP_ID")

    alert_number = os.getenv("ALERT_NUMBER", signal_number)

    sheet_name = os.getenv("MRC4_SHEET", "MRC4")

    # Signal Error
    if not signal_number or not group_id:
        logger.error("Environment variables SIGNAL_NUMBER or GROUP_ID not set.")
        sys.exit(1)

    try:
        # data pipeline
        df = load_data(data_path, logger, sheet=sheet_name)
        msg = compose_message(df, logger)
        send_signal(msg, signal_number, group_id, logger)

    except ExcelFormatError as e:
        logger.error("ExcelFormatError detected, sending admin alert...")
        alert_msg = f"⚠️ MRC4 notifier skipped: {str(e)}"
        send_signal(alert_msg, alert_number, group_id=None, logger=logger)
        sys.exit(1)

    except Exception:
        logger.exception("Unhandled exception occurred.")
        sys.exit(1)


if __name__ == "__main__":
    main()
