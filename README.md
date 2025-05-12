# MRC4 Readiness Notifier

## Overview

**MRC4 Readiness Notifier** is an automated notification tool designed to assist U.S. Army unit leaders in identifying and following up with soldiers who are listed as *Medical Readiness Category 4 (MRC4)*. These are personnel flagged for overdue or incomplete medical requirements.

The tool parses an Excel sheet exported from MEDPROS or similar systems, extracts the list of MRC4 soldiers, and sends automated alerts via Signal to designated leadership groups. This helps streamline readiness reporting and ensures timely action.

I'm continuously updating this project—feel free to clone it, build upon it, or adapt it for your own unit's needs.

---

## Features

- ✅ Parses Excel data for MRC4 personnel  
- 📤 Sends group notifications via Signal CLI  
- 🔄 Syncs automatically via OneDrive  
- 📆 Supports scheduled execution (e.g., weekly via `launchd` or cron)  
- 🔒 Keeps soldier data secure (local processing only)

---

## Setup

### 1. Prerequisites

- Python 3.9+
- `pandas`, `openpyxl`, and other dependencies listed in `requirements.txt`
- [Signal CLI](https://github.com/AsamK/signal-cli) installed and linked to your unit’s Signal number
- macOS (recommended for scheduling with `launchd`) or other UNIX-like OS
- OneDrive desktop app installed and synced with your readiness folder

---

### 2. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

---

### 3. Configuration

* Ensure your Excel file is saved and synced to your OneDrive folder:

  ```
  ~/OneDrive/Unit Readiness/MRC4.xlsx
  ```

* Set required environment variables manually or by creating a `.env` file in the project root:

```bash
SIGNAL_CLI_PATH=/path/to/signal-cli
SIGNAL_NUMBER=+1xxxxxxxxxx
GROUP_ID=your-signal-group-id
MRC4_PATH=/Users/user/Desktop/code/MRC4PD/data/MRC4.xlsx
```
* Set optional environment variables:

```bash
ALERT_NUMBER=           # Override recipient Signal number for direct alerts
MRC4_SHEET=             # Optional: specify the sheet name in the Excel file
```

---

### 4. Run Manually

To manually run the notification script:

```bash
python3 main.py
```

---

### 5. Schedule with `launchd` (macOS)

To automate weekly alerts:

1. Create a `.plist` file in `~/Library/LaunchAgents/`
2. Point it to your script path and desired schedule
3. Load it with:

```bash
launchctl load ~/Library/LaunchAgents/com.mrc4.notifier.plist
```

An example `.plist` file is included in the `scheduling/` folder.

🔧 Update paths in the .plist file to match your Python binary and script location before using.

---

## Notes

* Notifications include Soldier Names and Status of all current MRC4 personnel.
* All processing is done locally—no external data storage or transmission beyond your designated Signal group.

---

## License

This project is released under the [MIT License](LICENSE).

```

---






