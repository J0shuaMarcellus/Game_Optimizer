"""
====================================================================
GAME OPTIMIZER - Step 1: Process Manager (Backend Core)
====================================================================

WHAT THIS FILE DOES:
  This is the "brain" of your game optimizer. It looks at every
  program running on your Windows PC, figures out which ones are
  necessary and which ones are bloat, and can kill the bloat.

CONCEPTS YOU'LL LEARN:
  - How Windows processes work
  - How to interact with your OS using Python
  - What "whitelisting" means in software
  - How to safely terminate programs via code

HOW TO RUN:
  1. Install Python from https://python.org (check "Add to PATH")
  2. Open Command Prompt and run:  pip install psutil
  3. Run this script:  python step1_process_manager.py

  * You MUST run as Administrator to kill other processes.
    Right-click Command Prompt -> "Run as administrator"
====================================================================
"""

# --------------------------------------------------------------
# IMPORTS - these are libraries (pre-built code) we're using
# --------------------------------------------------------------

# 'psutil' = Process and System Utilities
# This library lets Python talk to your operating system.
# It can list running processes, check CPU/RAM usage, and kill programs.
# Docs: https://psutil.readthedocs.io
import psutil

# 'json' lets us save/load your whitelist settings to a file.
# JSON is a simple text format that looks like: {"key": "value"}
import json

# 'os' gives us basic operating system functions (file paths, etc.)
import os

# 'time' lets us add pauses and measure time
import time


# --------------------------------------------------------------
# CONFIGURATION - things you can change
# --------------------------------------------------------------

# This is the file where your whitelist gets saved.
# It will be created automatically in the same folder as this script.
import sys

def get_whitelist_path():
    if getattr(sys, '_MEIPASS', False):
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, "whitelist.json")
    else:
        return "whitelist.json"

WHITELIST_FILE = get_whitelist_path()

# These are processes that Windows NEEDS to run. Never kill these.
# If you kill these, your computer could crash or freeze.
# 
# HOW I KNOW THESE ARE CRITICAL:
#   - "svchost.exe"  -> Hosts dozens of Windows services (networking, updates, etc.)
#   - "csrss.exe"    -> Client/Server Runtime - handles console windows
#   - "lsass.exe"    -> Local Security Authority - handles your login/passwords
#   - "explorer.exe" -> Your desktop, taskbar, and file explorer
#   - "dwm.exe"      -> Desktop Window Manager - renders all your windows
#   - "System"       -> The Windows kernel itself
#
# RULE: If you don't know what a process is, Google it before adding
#       it here. Never remove things from this list.

SYSTEM_CRITICAL = {
    # These are lowercase so we can do case-insensitive matching later
    "system",
    "system idle process",
    "registry",
    "memory compression",
    "svchost.exe",
    "csrss.exe",
    "smss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "lsaiso.exe",
    "winlogon.exe",
    "explorer.exe",
    "dwm.exe",
    "conhost.exe",
    "fontdrvhost.exe",
    "sihost.exe",
    "taskhostw.exe",
    "spoolsv.exe",
    "ctfmon.exe",           # Text input services (keyboard)
    "dllhost.exe",
    "wmiprvse.exe",
    "dashost.exe",
    "audiodg.exe",          # Windows audio - you want game sound!
    "searchindexer.exe",
    "securityhealthservice.exe",
    "sgrmbroker.exe",
    "shellexperiencehost.exe",
    "startmenuexperiencehost.exe",
    "textinputhost.exe",
    "runtimebroker.exe",
    "applicationframehost.exe",
    # Python itself - don't kill the script that's running!
    "python.exe",
    "pythonw.exe",
    "python3.exe",
    "cmd.exe",
    "powershell.exe",
    "windowsterminal.exe",
    # GPU services (you want your graphics to work!)
    "nvdisplay.container.exe",
    "nvcontainer.exe",
    "amdrsserv.exe",
    "amddvr.exe",
    "atieclxx.exe",
    "atiesrxx.exe",
    "raabortsvc.exe"
    # GPU drivers - essential for gaming!
    "nvdisplay.container.exe",
    "nvcontainer.exe",
    "nvidia web helper.exe",
    "amdrsserv.exe",
    "amddvr.exe",
    "atieclxx.exe",
    "atiesrxx.exe",
    "raabortsvc.exe",
    
    # Audio services - you want game sound!
    "nahimicservice.exe",
    "realtek audio service.exe",
    "ravbg64.exe",
    
    # Anti-cheat - many games won't launch without these
    "easyanticheat.exe",
    "beclient.exe",
    "beservice.exe",
    "vanguard.exe",
    "vgtray.exe",
    "faceit.exe",
    
    # Windows security - don't disable your protection
    "msmpeng.exe",
    "securityhealthsystray.exe",
    "mpcmdrun.exe",
    
    # Networking - need internet for online games
    "networkservice.exe",
    "wlanext.exe",
    "dhcp.exe",
    
    # Input devices - controllers, gaming mice, keyboards
    "synapse3.exe",
    "icue.exe",
    "lghub.exe",
    # ASUS motherboard/ROG services - controls your hardware
    "asus_framework.exe",
    "armourycrate.usersessionhelper.exe",
    "armourycrate.service.exe",
    "armourysocketserver.exe",
    "armouryhtmldebugserver.exe",
    "armoury sw agent.exe",  
    "armouryswagent.exe",
    "asuscertservice.exe",
    "asusfancontrolservice.exe",
    "atkexcomsvc.exe",
    "rogliveservice.exe",
    "lightingservice.exe",
    "dipawaymode.exe",
    
    # NVIDIA GPU - essential for gaming
    "nvidia overlay.exe",
    "nvcontainer.exe",
    "nvdisplay.container.exe",
    
    # Logitech peripherals (your mouse/keyboard)
    "lghub.exe",
    "lghub_system_tray.exe",
    "lghub_agent.exe",
    "lghub_updater.exe",
    "logi_lamparray_service.exe",
    
    
    # Audio
    "rtkauduservice64.exe",
    
    # Bitdefender antivirus - don't kill your security
    "bdservicehost.exe",
    "bdagent.exe",
    "bdntwrk.exe",
    "bdredline.exe",
    "bdvpnservice.exe",
    
    # Windows system services
    "memcompression",
    "searchhost.exe",
    "shellhost.exe",
    "wudfhost.exe",
    "backgroundtaskhost.exe",
    "systemsettings.exe",
    "gamingservices.exe",
    "gameinputredistservice.exe",
    "windowspackagemanagerserver.exe",
    "searchfilterhost.exe",
    "searchprotocolhost.exe",
    "aggregatorhost.exe",
    "msdtc.exe",
    "vds.exe",
    "tabletip.exe",  
    "tabtip.exe",
    "srvstub.exe",
    "jhi_service.exe",
    "rstmwservice.exe",
    "wmiregistrationservice.exe",
    "discoverysrv.exe",
    "wsccommunicator.exe",
    "productagentservice.exe",
    "sdxhelper.exe",
    "gameinputredistservice.exe",
    "gamesdk.exe",
    "ngciso.exe",
    "unsecapp.exe",
    "bitsumsessionagent.exe",
    "setthreadaffinitymaskx64.exe",
    
    # Steam core
    "steam.exe",
    "steamservice.exe",
    
    # Kingston RAM hardware
    "aackingstondramhal_x64.exe",
    "aackingstondramhal_x86.exe",
    "aac3572mbhal_x86.exe",
    "aac3572dramhal_x86.exe",
    "extensioncardhal_x86.exe",
    
    # Process Lasso (system optimizer)
    "processlasso.exe",

    # Game Optimizer itself - don't kill ourselves!
    "gameoptimizer.exe",
    "flask.exe",

    # WebView2 - needed for the Game Optimizer window
    "msedgewebview2.exe",
    "gameoptimizer.exe",
}

# Known bloatware / background apps that are safe to kill for gaming.
# Each entry has a "category" so the frontend can group them nicely.
#
# WHAT MAKES SOMETHING "BLOAT" FOR GAMING?
#   - It uses RAM/CPU but isn't needed for your game
#   - It syncs files in the background (cloud storage)
#   - It checks for updates constantly
#   - It's a communication app you're not actively using
#
# You can add more entries here as you discover them!

KNOWN_BLOAT = {
    # Format: "process_name.exe": "Category"
    
    # -- Cloud sync services (constantly read/write your disk) --
    "onedrive.exe":             "Cloud Sync",
    "dropbox.exe":              "Cloud Sync",
    "googledrivesync.exe":      "Cloud Sync",
    "icloud.exe":               "Cloud Sync",
    
    # -- Communication apps (use RAM + network even when minimized) --
    "slack.exe":                "Communication",
    "teams.exe":                "Communication",
    "skypeapp.exe":             "Communication",
    "zoom.exe":                 "Communication",
    "telegram.exe":             "Communication",
    "signal.exe":               "Communication",
    "discord.exe":              "Communication",  # Many gamers whitelist this
    
    # -- Browsers (HUGE RAM hogs, especially Chrome) --
    "chrome.exe":               "Browser",
    "msedge.exe":               "Browser",
    "firefox.exe":              "Browser",
    "opera.exe":                "Browser",
    "brave.exe":                "Browser",
    
    # -- Adobe background services --
    "adobe cef helper.exe":     "Creative",
    "adobeupdateservice.exe":   "Updater",
    "ccxprocess.exe":           "Creative",
    "adobeipcbroker.exe":       "Creative",
    "armsvc.exe":               "Updater",        # Adobe ARM update checker
    
    # -- Media players --
    "spotify.exe":              "Media",
    "ituneshelper.exe":         "Media",
    
    # -- Windows extras you don't need while gaming --
    "cortana.exe":              "Assistant",
    "yourphone.exe":            "Utility",
    "gamebar.exe":              "Utility",
    "widgets.exe":              "Utility",
    "phoneexperiencehost.exe":  "Utility",
    
    # -- Game launchers (you usually only need the one for YOUR game) --
    "epicgameslauncher.exe":    "Game Launcher",
    "steamwebhelper.exe":       "Game Launcher",
    "battle.net.exe":           "Game Launcher",
    "originthinsetupinternal.exe": "Game Launcher",
    "eadesktop.exe":            "Game Launcher",
    
    # -- GPU overlay / extras --
    "nvidia share.exe":         "GPU Overlay",
    "nvcontainer.exe":          "GPU Service",
    "raabortsvc.exe":           "GPU Service",
    
    # -- Streaming --
    "obs64.exe":                "Streaming",
    "streamlabs obs.exe":       "Streaming",
    
    # -- Desktop customization --
    "wallpaperengine.exe":      "Utility",
    "rainmeter.exe":            "Utility",
}


# ==============================================================
# FUNCTIONS - reusable blocks of code
# ==============================================================

def load_whitelist():
    """
    Load the user's whitelist from a JSON file.
    
    WHAT'S A WHITELIST?
      A whitelist is a list of things you ALLOW. Everything NOT on the
      list gets blocked (or in our case, killed). This is the opposite
      of a "blacklist" where you list things to block.
    
    WHY JSON?
      JSON files are human-readable text files. You could open
      whitelist.json in Notepad and edit it by hand if you wanted.
    
    RETURNS:
      A Python list of process names, like: ["discord.exe", "spotify.exe"]
    """
    # Check if the file exists first
    if os.path.exists(WHITELIST_FILE):
        # 'with open(...)' automatically closes the file when done
        # 'r' means "read mode"
        with open(WHITELIST_FILE, "r") as f:
            data = json.load(f)  # Parse the JSON text into Python data
            return data.get("whitelist", [])  # Get the whitelist, or empty list
    else:
        # First time running - create a default whitelist
        # Discord is whitelisted by default since most gamers use it
        default = ["discord.exe"]
        save_whitelist(default)
        return default


def save_whitelist(whitelist):
    """
    Save the whitelist to a JSON file so it persists between runs.
    
    WHAT "PERSISTS" MEANS:
      When you close this program and reopen it, your settings are
      still there. Without saving to a file, everything would reset.
    """
    with open(WHITELIST_FILE, "w") as f:  # 'w' = write mode (overwrites file)
        json.dump({"whitelist": whitelist}, f, indent=2)
        # 'indent=2' makes the JSON file look pretty with spacing


def get_running_processes():
    """
    Scan all running processes and return info about each one.
    
    HOW THIS WORKS:
      psutil.process_iter() gives us an "iterator" - basically a list
      of every running process. For each one, we grab:
        - pid:  Process ID (unique number Windows assigns)
        - name: The .exe filename
        - cpu_percent: How much CPU it's using (0-100%)
        - memory_info: RAM usage in bytes
    
    WHY TRY/EXCEPT?
      Some system processes won't let us read their info (permission
      denied). We just skip those - they're system-critical anyway.
    
    RETURNS:
      A list of dictionaries, each representing one process.
    """
    process_list = []
    
    # Ask psutil for all processes, requesting specific attributes
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            info = proc.info  # The data we requested
            name = info['name']
            
            if name is None:
                continue  # Skip processes with no name (zombies)
            
            # Get RAM usage in megabytes (MB)
            # memory_info().rss = "Resident Set Size" = actual RAM being used
            # We divide by 1024*1024 to convert bytes -> megabytes
            ram_mb = 0
            if info['memory_info']:
                ram_mb = round(info['memory_info'].rss / (1024 * 1024), 1)
            
            # Build a dictionary (key-value pairs) for this process
            process_data = {
                "pid": info['pid'],
                "name": name,
                "name_lower": name.lower(),  # For case-insensitive matching
                "ram_mb": ram_mb,
                "cpu_percent": info['cpu_percent'] or 0.0,
            }
            
            # Categorize this process
            # WHITELIST APPROACH: Everything is killable UNLESS it's
            # system-critical. This is the aggressive approach -
            # if it's not essential to Windows, it gets killed
            # unless you've whitelisted it.
            # Load hardware-specific critical processes
            try:
                import step5_hardware_setup as hw
                hardware_critical = set(hw.get_hardware_critical_processes())
            except:
                hardware_critical = set()

            # Categorize this process
            name_lower = name.lower()
            if name_lower in SYSTEM_CRITICAL or name_lower in hardware_critical:
                process_data["category"] = "System Critical"
                process_data["safe_to_kill"] = False
            elif name_lower in KNOWN_BLOAT:
                process_data["category"] = KNOWN_BLOAT[name_lower]
                process_data["safe_to_kill"] = True
            else:
                process_data["category"] = "Other"
                process_data["safe_to_kill"] = True 
            
            process_list.append(process_data)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Process disappeared or we can't access it - skip
            pass
    
    return process_list


def kill_process_by_name(name, whitelist):
    """
    Kill all instances of a process by name.
    
    WHAT "KILLING A PROCESS" MEANS:
      We're asking Windows to force-stop the program. It's the same
      as right-clicking in Task Manager and choosing "End Task."
      
      The process gets a "terminate" signal. It stops immediately.
      Any unsaved work in that app would be lost.
    
    SAFETY CHECKS:
      1. Won't kill system-critical processes (would crash Windows)
      2. Won't kill whitelisted processes (ones you chose to keep)
      3. Uses try/except in case the process disappears mid-kill
    
    PARAMETERS:
      name:      The process name to kill (e.g., "chrome.exe")
      whitelist: List of process names to never kill
    
    RETURNS:
      Dictionary with the result: success, count killed, or error
    """
    name_lower = name.lower()
    
    # Safety check 1: Is this a system-critical process?
    if name_lower in SYSTEM_CRITICAL:
        return {
            "success": False, 
            "error": f"BLOCKED: {name} is system-critical. Killing it could crash Windows."
        }
    
    # Safety check 2: Is this on the user's whitelist?
    if name_lower in [w.lower() for w in whitelist]:
        return {
            "success": False,
            "error": f"BLOCKED: {name} is on your whitelist. Remove it first if you want to kill it."
        }
    
    # Find and kill all instances of this process
    killed_count = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == name_lower:
                proc.terminate()  # Send termination signal
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if killed_count > 0:
        return {"success": True, "killed": killed_count, "name": name}
    else:
        return {"success": False, "error": f"{name} is not currently running."}


def activate_game_mode(whitelist):
    """
    GAME MODE: Kill EVERYTHING except system-critical and whitelisted.
    
    WHITELIST APPROACH:
      Instead of only killing known bloat, we kill ANYTHING that
      isn't system-critical or on your whitelist. This is aggressive
      but gives you maximum performance.
    
      The logic is simple:
        - System Critical? → NEVER touch it
        - On your whitelist? → Keep it alive
        - Anything else? → Kill it
    
    WHY THIS IS BETTER FOR GAMING:
      The old approach only killed apps we recognized. But there
      are thousands of random apps, updaters, and services that
      could be eating your RAM. This approach catches ALL of them.
    
    WHY THE WHITELIST MATTERS:
      Since we're killing everything, your whitelist is your safety
      net. Make sure your game launcher (Steam, Epic, etc.) and any
      apps you want (Discord, etc.) are on the whitelist BEFORE
      activating Game Mode.
    """
    processes = get_running_processes()
    whitelist_lower = [w.lower() for w in whitelist]
    
    killed = []
    total_ram_freed = 0
    total_cpu_freed = 0
    skipped_whitelist = []
    
    for proc in processes:
        # Never touch system-critical processes
        if proc["category"] == "System Critical":
            continue
        
        # Skip whitelisted processes
        if proc["name_lower"] in whitelist_lower:
            skipped_whitelist.append(proc["name"])
            continue
        
       # Kill everything else
        try:
            my_pid = os.getpid()
            for p in psutil.process_iter(['name', 'pid']):
                if p.info['name'] and p.info['name'].lower() == proc["name_lower"]:
                    # Don't kill ourselves!
                    if p.info['pid'] == my_pid or p.info['pid'] == os.getppid():
                        continue
                    p.terminate()
            killed.append(proc["name"])
            total_ram_freed += proc["ram_mb"]
            total_cpu_freed += proc["cpu_percent"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return {
        "killed": killed,
        "ram_freed_mb": round(total_ram_freed, 1),
        "cpu_freed_percent": round(total_cpu_freed, 1),
        "kept_whitelisted": skipped_whitelist,
        "total_killed": len(killed),
    }


# ==============================================================
# MAIN - this runs when you execute the script directly
# ==============================================================

if __name__ == "__main__":
    """
    WHY 'if __name__ == "__main__"'?
      This is a Python pattern. It means "only run this code if 
      this file is being run directly (not imported by another file)."
      
      Later, when our web server imports this file, it won't run
      this test code - it'll just use our functions.
    """
    
    print("=" * 60)
    print("  GAME OPTIMIZER - Process Scanner")
    print("  Run as Administrator for full functionality!")
    print("=" * 60)
    print()
    
    # Load your whitelist
    whitelist = load_whitelist()
    print(f"Your whitelist: {whitelist}")
    print()
    
    # Scan processes
    print("Scanning running processes...")
    time.sleep(0.5)  # Brief pause so CPU readings are more accurate
    processes = get_running_processes()
    
    # Separate into categories for display
    bloat = [p for p in processes if p["safe_to_kill"]]
    critical = [p for p in processes if p["category"] == "System Critical"]
    unknown = [p for p in processes if p["category"] == "Unknown" and p["ram_mb"] > 5]
    
    print(f"\nFound {len(processes)} total processes:")
    print(f"  System Critical: {len(critical)} (protected)")
    print(f"  Known Bloat:     {len(bloat)} (can be killed)")
    print(f"  Unknown:         {len(unknown)} (left alone)")
    
    if bloat:
        print("\n--- KILLABLE BLOAT ---")
        # Sort by RAM usage, highest first
        bloat.sort(key=lambda p: p["ram_mb"], reverse=True)
        for p in bloat:
            whitelisted = " [WHITELISTED]" if p["name_lower"] in [w.lower() for w in whitelist] else ""
            print(f"  {p['name']:<30} RAM: {p['ram_mb']:>7} MB  CPU: {p['cpu_percent']:>5}%  ({p['category']}){whitelisted}")
        
        total_bloat_ram = sum(p["ram_mb"] for p in bloat)
        print(f"\n  Total bloat RAM: {total_bloat_ram:.0f} MB could be freed")
    
    print("\n" + "=" * 60)
    print("This was a READ-ONLY scan. Nothing was killed.")
    print("To actually kill processes, we'll use the web UI (Step 2).")
    print("=" * 60)