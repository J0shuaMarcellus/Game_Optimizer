r"""
====================================================================
GAME OPTIMIZER - Build Script (creates the .exe)
====================================================================

WHAT THIS FILE DOES:
  Run this ON YOUR WINDOWS PC to create GameOptimizer.exe
  It tells PyInstaller exactly what to include in the bundle.

HOW TO USE:
  1. Copy your entire GameOptimizer folder to your Windows PC
  2. Install Python on Windows (https://python.org)
  3. Open Command Prompt and run:
       cd Desktop\GameOptimizer
       pip install psutil flask flask-cors pywebview pyinstaller
       python build.py
  4. Your .exe will be in the 'dist' folder when it's done

WHAT IS PYINSTALLER?
  PyInstaller analyzes your Python code, finds every library it
  needs, and packs everything (including Python itself) into a
  single .exe file. The person running the .exe doesn't need
  Python installed at all.

WHAT THIS SCRIPT DOES STEP BY STEP:
  1. Tells PyInstaller the entry point is app.py
  2. Includes step1_process_manager.py and step2_server.py as data
  3. Includes the frontend folder with index.html
  4. Sets it to "windowed" mode (no console window pops up)
  5. Names the output GameOptimizer.exe
====================================================================
"""

import os
import sys

import PyInstaller.__main__

# Get the directory this script is in
base_dir = os.path.dirname(os.path.abspath(__file__))

# Separator is ; on Windows, : on Mac/Linux
sep = ";"  # Change to ":" if building on Mac for testing

dist_dir = os.path.join(base_dir, "dist")
output_exe = os.path.join(dist_dir, "GameOptimizer.exe")


def remove_stale_exe():
    """
    Remove the previous build output before packaging.

    PyInstaller's final overwrite step is where builds usually fail if
    the old .exe is still running or locked by Windows. Checking here
    gives a clearer error message before waiting through the whole build.
    """
    if not os.path.exists(output_exe):
        return

    try:
        os.remove(output_exe)
        print(f"Removed old build: {output_exe}")
    except PermissionError:
        print()
        print("=" * 60)
        print("BUILD BLOCKED")
        print(f"Could not overwrite: {output_exe}")
        print("Close any running GameOptimizer.exe windows and try again.")
        print("If needed, open Task Manager and end GameOptimizer.exe first.")
        print("=" * 60)
        sys.exit(1)


remove_stale_exe()

PyInstaller.__main__.run([
    # The main entry point - this is what runs when you double-click
    os.path.join(base_dir, "app.py"),

    # --onefile: Bundle everything into a SINGLE .exe
    # Without this, you'd get a folder full of files
    "--onefile",

    # --windowed: Don't show a console/terminal window
    # Without this, a black command prompt would pop up behind your app
    "--windowed",

    # --name: What to call the .exe
    "--name=GameOptimizer",

    # --add-data: Include extra files in the bundle
    # Format is "source;destination" (semicolon on Windows)
    # These files get extracted to a temp folder when the .exe runs
    f"--add-data={os.path.join(base_dir, 'step1_process_manager.py')}{sep}.",
    f"--add-data={os.path.join(base_dir, 'step2_server.py')}{sep}.",
    f"--add-data={os.path.join(base_dir, 'step4_optimizations.py')}{sep}.",
     f"--add-data={os.path.join(base_dir, 'step5_hardware_setup.py')}{sep}.",
    f"--add-data={os.path.join(base_dir, 'frontend')}{sep}frontend",

    # --hidden-import: Libraries that PyInstaller might miss
    # PyInstaller analyzes your imports, but sometimes it misses
    # things that are imported dynamically (inside functions)
    "--hidden-import=psutil",
    "--hidden-import=flask",
    "--hidden-import=flask_cors",
    "--hidden-import=webview",

    # --clean: Remove old build files before starting
    "--clean",

    # -y: Auto-confirm overwriting old builds
    "-y",
])

print()
print("=" * 60)
print("  BUILD COMPLETE!")
print("  Your .exe is at: dist/GameOptimizer.exe")
print()
print("  To run it:")
print("  1. Right-click GameOptimizer.exe")
print("  2. Select 'Run as administrator'")
print("  3. The app window will open automatically")
print("=" * 60)
