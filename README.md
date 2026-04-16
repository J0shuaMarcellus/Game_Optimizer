# Game Optimizer

Game Optimizer is a Windows desktop app that helps reduce background clutter before gaming. It scans running processes, protects critical system and hardware services, lets you manage a whitelist, and applies a few gaming-focused optimizations through a simple local UI.

## Features

- Desktop app launcher with a local embedded Flask server
- Running process scan with RAM and CPU usage
- Aggressive Game Mode that closes non-critical, non-whitelisted processes
- Whitelist management for apps you want to keep alive
- First-run hardware setup to protect device-specific services
- Hardware detection using installed apps, services, process matches, and Windows inventory where available
- System optimizations including power plan switching, RAM cleanup, and process priority boosts
- PyInstaller build script for packaging into a Windows `.exe`

## How It Works

The app starts a local server on `127.0.0.1:8080`, then opens the dashboard in a desktop window using `pywebview`. If the desktop window cannot start, it can fall back to the default browser. The UI talks only to the local backend.

## Project Structure

- `app.py`: desktop launcher, local server startup, and runtime logging
- `step1_process_manager.py`: process scanning, whitelist logic, and Game Mode killing logic
- `step2_server.py`: Flask API and frontend serving
- `step4_optimizations.py`: power plan, RAM cleanup, and process priority tools
- `step5_hardware_setup.py`: first-run setup, hardware detection, and hardware-specific protection
- `frontend/`: dashboard and setup UI
- `build.py`: Windows build script for `GameOptimizer.exe`

## Requirements

- Windows
- Python 3.12 recommended for builds
- Administrator privileges for the full optimization and process-management features

## Run In Development

Install dependencies:

```cmd
pip install psutil flask flask-cors pywebview
```

Run the app:

```cmd
python app.py
```

This starts the local server and opens the desktop window. If the desktop window fails, check `error_log.txt`.

## Build The EXE

Create a build environment and install dependencies:

```cmd
py -3.12 -m venv .venv-build
.\.venv-build\Scripts\python.exe -m pip install --upgrade pip
.\.venv-build\Scripts\python.exe -m pip install --no-cache-dir psutil flask flask-cors pywebview pyinstaller
```

Build the app:

```cmd
.\.venv-build\Scripts\python.exe build.py
```

The packaged app will be written to:

```text
dist\GameOptimizer.exe
```

## Notes

- Some features will not work correctly unless the app is run as Administrator.
- Hardware detection is best-effort and can depend on what Windows exposes on the machine.
- The app stores local runtime state such as `whitelist.json`, `hardware_config.json`, and `error_log.txt` next to the executable or project files.

## Troubleshooting

**The app opens in the browser instead of the desktop window**

- `pywebview` likely failed to start. Check `error_log.txt`.

**The app says localhost is offline**

- The local Flask server likely failed to start. Check `error_log.txt`.

**The build fails because `GameOptimizer.exe` is in use**

- Close any running copies of the app and rebuild.
- If needed, end leftover `GameOptimizer.exe`, `python.exe`, or `msedgewebview2.exe` processes in Task Manager.

**Process-kill actions fail with access denied**

- Run the app as Administrator.

## Publishing

This repo includes a `.gitignore` for virtual environments, build artifacts, logs, and local machine state. A basic release checklist is included in `RELEASE_CHECKLIST.md`.
