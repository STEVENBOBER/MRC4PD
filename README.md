# MRC4 Readiness Notifier

## Overview

**MRC4 Readiness Notifier** is an automated notification tool designed to assist U.S. Army unit leaders in identifying and following up with soldiers listed as *Medical Readiness Category 4 (MRC4)*. These are personnel flagged for overdue or incomplete medical requirements.

The tool parses an Excel sheet exported from MEDPROS (or similar systems), extracts the list of MRC4 soldiers, and sends automated alerts via Signal to designated leadership groups. This helps streamline readiness reporting and ensures timely action—even when your laptop is off.

I'm continuously updating this project—feel free to clone it, build upon it, or adapt it for your own unit's needs.

---

## Features

* ✅ Parses Excel data for MRC4 personnel
* 📤 Sends group notifications via Signal CLI
* 🔄 Syncs automatically via OneDrive
* 📆 Supports automated scheduling via `launchd` (macOS) or GitHub Actions
* 🔒 Keeps soldier data secure (local processing only)

---

## Setup

### 1. Prerequisites

* **Python 3.9+** (for parsing Excel and running the notifier)
* **Signal CLI** (v0.13+), installed and linked to your unit’s Signal number  *—only required for live sends; not needed in test mode*
* **OneDrive** desktop app, installed and synced with your readiness folder
* **GitHub** account (for cloud-based test runs) or macOS (for `launchd` scheduling)

### 2. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

1. Save your Excel file in a synced folder, for example:

   ```
   ~/OneDrive/Unit Readiness/MRC4_TEST.xlsx
   ```
2. Create a `.env` file in the project root with these variables:

   ```bash
   # Required
   SIGNAL_CLI_PATH=/path/to/signal-cli
   SIGNAL_NUMBER=+1xxxxxxxxxx
   GROUP_ID=your-signal-group-id
   MRC4_PATH=~/OneDrive/Unit Readiness/MRC4_TEST.xlsx

   # Optional
   ALERT_NUMBER=           # override recipient for error alerts
   MRC4_SHEET=             # sheet name (default: MRC4)
   TEST_MODE=true          # safe preview mode (no real sends)
   ```
3. Learn how to install install Signal CLI through documentation(it's well worth a read):

   ```
   https://github.com/AsamK/signal-cli
   ```
---

## Running the Notifier

### Option 1: Run Manually

```bash
source .venv/bin/activate
python3 main.py
```

* When `TEST_MODE=true`, alerts are printed to console instead of sent.
* Remove or set `TEST_MODE=false` for live Signal sends once you’ve configured Signal CLI.

---

## Scheduling Options

### Option A: Automate with `launchd` (macOS)

1. Create a `.plist` file in `~/Library/LaunchAgents/`
2. Point it to your Python binary and script
3. Load it with:

   ```bash
   launchctl load ~/Library/LaunchAgents/com.mrc4.notifier.plist
   ```

A sample `.plist` is included in the `scheduling/` folder—update paths to match your environment.

---

### Option B: Automate with GitHub Actions (Cloud-Based)

> **Note:** Currently only **test mode** (`TEST_MODE=true`) works when run in GitHub Actions.
> Next, you’ll add steps to restore your registered Signal‑CLI config and run in live mode.

1. **Add secrets** under `Repo → Settings → Secrets and variables → Actions`:

   * `SIGNAL_NUMBER`
   * `GROUP_ID`
   * `MRC4_PATH`
2. **Enable scheduled runs** via the provided workflow at `.github/workflows/mrc4-notifier.yml`.

#### ▶️ Manual Test Run

Trigger the workflow from the GitHub **Actions** tab. With `TEST_MODE=true`, the output is printed instead of sent.

#### ⏰ Automated Runs

The script is scheduled to run every Monday at 7 AM PT. Modify the cron expression in the workflow YAML to change this.

---

## Notes

* All processing occurs locally; no data is sent until Signal sends are triggered.
* Ideal for Company Commanders, First Sergeants, and Readiness NCOs.

---

## License

This project is released under the [MIT License](LICENSE).






