# O2M (Oxygen Monitoring System)

A robust, asynchronous desktop application designed to interface with Modbus TCP sensors (such as the SINTESY S210.smartSensor) for real-time monitoring, background data logging, and automated PDF report generation.

---

## 📦 Quick Start (Precompiled Binaries)

If you just want to run the O2 Dashboard without installing Python or messing with code, you can download the standalone executable for your operating system.

1. Navigate to the **[Releases](../../releases)** tab of this repository.
2. Download the `.zip` file for your OS (Windows, macOS, or Linux).
3. Extract the folder and double-click the `O2M` executable. 

*Note: Ensure your `.env` configuration file is placed in the same folder as the executable before launching!*

---

## 🌟 Key Features

* **Live Monitoring Dashboard**: Real-time visualization of Oxygen (O2) concentration, Internal Temperature, and Pressure using modern, responsive UI gauges and readouts.
* **Asynchronous Hardware Polling**: Utilizes `pymodbus` and `asyncio` in a dedicated background thread to ensure the UI remains smooth and responsive while polling the sensor.
* **Persistent Data Logging**: Automatically logs sensor telemetry into a local SQLite database (`.db`) for historical tracking.
* **Automated PDF Reporting**: Generates comprehensive daily reports complete with Min/Max/Avg statistical summaries and high-resolution `matplotlib` timeseries graphs.
* **Dynamic Configuration**: Built-in settings menu to easily swap Sensor IPs, Ports, Device IDs, and Register offsets without touching the code.
* **Modern GUI**: Built with `customtkinter` featuring automatic Light/Dark mode syncing and responsive layouts.
* **Smart Error Handling**: Includes smart Modbus client lifecycle management, preventing socket leaks, and graceful UI pop-ups for network disconnects.

---

## 🛠️ Tech Stack & Dependencies

* **UI & Graphics**: `customtkinter`, `tkdial` (gauges), `matplotlib` (headless data visualization)
* **Hardware Interface**: `pymodbus`, `asyncio`
* **Database**: `sqlite3`
* **Reporting**: `xhtml2pdf`, `jinja2`
* **Config**: `python-dotenv`

---

## 🐍 Setting Up the Virtual Environment (For Developers)

If you are running the project from source, it is highly recommended to use a Python virtual environment to manage dependencies. Make sure you have Python 3.8+ installed.

### 🍎 macOS Specific Prerequisites
If you are building on a Mac, we strictly enforce **Python 3.12**. You also need to install system-level graphics and UI dependencies so the PDF generator and Tkinter engines can compile correctly.
Open your terminal and run:
```bash
brew install cairo pkg-config python-tk@3.12
```

**1. Create the virtual environment:**
Open your terminal inside the project folder and run:
* **Windows:** `python -m venv venv`
* **macOS/Linux:** `python3 -m venv venv`

**2. Activate the virtual environment:**
* **Windows:** `venv\Scripts\activate`
* **macOS/Linux:** `source venv/bin/activate`

**3. Install dependencies:**
Once activated (you will see `(venv)` in your terminal prompt), you can safely install the required packages:
```bash
pip install -r requirements.txt
```
Or (if errors arise) install them manually:
```bash
pip install customtkinter tkdial pymodbus python-dotenv matplotlib xhtml2pdf jinja2
```

### Configuration (.env)
To ensure your data is secure and isn't accidentally overwritten when updating the app, the O2 Dashboard stores its configuration and database in a hidden folder inside your system's Home directory.

**Default Storing Locations:**
* **macOS/Linux:** `~/.o2m/`
* **Windows:** `C:\Users\<YourUsername>\.o2m`

Inside this folder, you will find two critical files:
* `.env`: Your saved settings, UI preferences, and Modbus memory maps.
* `sensor_readings.db`: The SQLite database containing all logged historical data.

*Environment Variables (`.env`)*
* `SENSOR_IP`: The IPv4 address of your Modbus sensor (e.g., `192.128.0.7`).
* `SENSOR_PORT`: The Modbus TCP port (default is usually `502`).
* `DEVICE_ID`: The Modbus Slave/Device ID (default is usually `1`).
* `DATABASE_PATH`: The relative or absolute path to your SQlite database (e.g., `./sensor_readings.db`).
* `THEME_PREFERENCE`: UI theme (`Light`, `Dark`, `System`).
* `O2_MIN_THRESHOLD`: The lower-bound limit for oxygen warnings (e.g., `19.5`).

### Finding Unknown Sensor Registers
Different manufacturers store their sensor data at different Modbus memory addresses.
* **SINTESY S210.smartSensor (Default):** Stores data at `REGISTER_START_ADDRESS=10` and uses `REGISTER_COUNT=6` (3 values taking up 6 FLOAT32 regusters each).
* **Other Sensors:** If you are using a non-SINTESY sensor, you must use the included `scanner.py` tool (detailed below) to reverse-engineer your device's memory map and update your `.env` file accordingly.

## 🚀 Running the Application

### Launching the Graphical UI
With your virtual environment activated, run the main orchestrator:
```bash
python main.py
```
*Note: On first launch, if your `.env` file is missing critical connection details, the app will automatically redirect you to the Settings page.*

### CLI & Diagnostics Tools
For headless environments, servers, or hardware debugging, the project includes several command-line tools. Make sure your `.env` file is configured before running these.

### 1. Hardware Discovery (`scanner.py`)
Use this tool if you bought a new sensor and don't know which registers hold the data. It connects to the sensor, scans addresses 0 through 60, and attempts to decode any active FLOAT32 data blocks.
```bash
python scanner.py
```
*Tip: Once it spits out the active addresses, blow on the sensor or change the temperature and run the scan again to see which values fluctuate. Update your .env file with the correct start address.*

### 2. Headless Monitor (`monitor.py`)
A lightweight, terminal-based monitor. It uses the exact register settings from your .env file to print a live, updating string of the current O2, Temperature, and Pressure readings. Excellent for quickly verifying network stability.
```bash
python monitor.py
```

### 3. Background Logger (`logger.py`)
A headless daemon that polls the sensor every 10 seconds and saves the data directly to your SQLite database. It runs continuously until stopped (`Ctrl+C`). It relies entirely on the `.env` file for its IP and database paths.
```bash
python logger.py
```

### 4. PDF Generator (`reporter.py`)
Generates a highly-detailed PDF summary for a specific date, bypassing the GUI entirely. Perfect for scheduling automated daily cron jobs.

**Arguments:**
* `-d`, `--date`: (Optional) The target date to pull from the database in `YYYY-MM-DD` format.

**Examples:**
```bash
# Generate a report for today's data (the system's current date)
python reporter.py

# Generate a report for a specific historical date
python reporter.py -d 2026-05-07
```

## 📦 Compiling to an Executable from Source
If you wish to compile your own version of the application using PyInstaller, run the following command from the root directory:

### 5. Manual Data Insertion (`database.py`)
The database script includes a built-in Command Line Interface (CLI) powered by `argparse`. This allows developers to manually inject mock sensor readings directly into the SQLite database without needing physical Modbus hardware. This is highly useful for testing the reporting engine, simulating hypoxic events, or generating historical graphs.

**Basic Usage:**
If you run the script without a date or time, it will automatically use the current system timestamp.
```bash
python database.py -o 19.4 -t 25.5 -p 1012
```
**Advanced Usage (Simulating Past Events):**
```bash
python database.py -o 18.1 -t 24.0 -p 998 -d 2026-05-07 -c 14:30:00
```
**Available Arguments:**
| Flag | Long Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `-o` | `--oxygen` | `float` | `20.00` | Oxygen concentration (e.g., `20.9`, `19.5`). |
| `-t` | `--temp` | `float` | `30.0` | Internal sensor temperature in °C. |
| `-p` | `--press` | `float` | `1000` | Internal barometric pressure in mbar. |
| `-d` | `--date` | `string`| `Current Date` | Target date in `YYYY-MM-DD` format. |
| `-c` | `--time` | `string`| `Current Time` | Target time in `HH:MM:SS` format. |

**Windows:**
```bash
pyinstaller --noconsole --onedir --name "O2M" --icon "o2m-logo.ico" --add-data "o2m-logo.ico;." --add-data "templates;templates" --collect-all customtkinter --collect-all reportlab --collect-all xhtml2pdf main.py
```

**macOs:**
```bash
pyinstaller --noconsole --onedir --name "O2M" --icon "o2m-logo.icns" --add-data "templates:templates" --collect-all customtkinter --collect-all reportlab --collect-all xhtml2pdf main.py
```

**Linux:**
```bash

```

*Don't forget to copy your `.env` file into the generated dist/O2M/ folder before launching the new binary!*