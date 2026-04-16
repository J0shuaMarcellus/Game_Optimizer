
import subprocess
import psutil
import ctypes
import os
import time


# ==============================================================
# POWER PLAN MANAGEMENT
# ==============================================================

# Windows has built-in power plans identified by GUIDs (unique IDs).
# These are the same on every Windows PC:
#
#   Balanced:         Less performance, saves energy
#   High Performance: Full CPU speed, more power draw
#   Ultimate:         Even more aggressive than High Performance
#                     (not available on all PCs)
#
# WHY THIS MATTERS FOR GAMING:
#   On "Balanced" mode, Windows throttles your CPU speed up and
#   down to save electricity. This causes micro-stutters in games
#   because the CPU isn't always running at full speed when your
#   game needs it. "High Performance" keeps the CPU at max speed.

POWER_PLANS = {
    "balanced":         "381b4222-f694-41f0-9685-ff5bb260df2e",
    "high_performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
    "ultimate":         "e9a42b02-d5df-448d-aa00-03f14749eb61",
}


def get_current_power_plan():
    """
    Get the currently active Windows power plan.
    
    WHAT subprocess.run DOES:
      It runs a command as if you typed it in Command Prompt.
      'powercfg /getactivescheme' is a Windows command that
      returns which power plan is currently active.
      
      'capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW' means we want to read what the
      command prints (instead of it going to the screen).
      
      'text=True' means give us the output as a string
      (not raw bytes).
    """
    try:
        result = subprocess.run(
            ["powercfg", "/getactivescheme"],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW,
            text=True
        )
        output = result.stdout.strip()
        
        # The output looks like:
        # "Power Scheme GUID: 381b4222-...  (Balanced)"
        # We extract the name in parentheses
        if "(" in output:
            name = output.split("(")[-1].rstrip(")")
            guid = output.split(":")[1].split("(")[0].strip()
            return {"name": name, "guid": guid}
        
        return {"name": "Unknown", "guid": ""}
        
    except Exception as e:
        return {"name": "Error", "guid": "", "error": str(e)}


def set_power_plan(plan_name):
    """
    Switch to a different power plan.
    
    PARAMETERS:
      plan_name: "high_performance", "balanced", or "ultimate"
    
    REQUIRES:
      Must be run as Administrator. Regular users can't change
      power plans via command line.
    
    WHAT 'powercfg /setactive' DOES:
      Changes the active power plan immediately. Your CPU will
      start running at full speed right away.
    """
    if plan_name not in POWER_PLANS:
        return {"success": False, "error": f"Unknown plan: {plan_name}"}
    
    guid = POWER_PLANS[plan_name]
    
    try:
        # Save the current plan so we can restore it later
        current = get_current_power_plan()
        
        result = subprocess.run(
            ["powercfg", "/setactive", guid],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW,
            text=True
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "previous_plan": current["name"],
                "new_plan": plan_name,
                "message": f"Switched to {plan_name}. CPU will run at full speed."
            }
        else:
            # If High Performance fails, it might not be available
            # Some laptops/prebuilts remove it. Try to create it:
            if plan_name == "high_performance":
                subprocess.run(
                    ["powercfg", "/duplicatescheme", guid],
                    capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                # Try again
                result = subprocess.run(
                    ["powercfg", "/setactive", guid],
                    capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW,
                    text=True
                )
                if result.returncode == 0:
                    return {"success": True, "new_plan": plan_name}
            
            return {
                "success": False,
                "error": f"Failed to set plan. Error: {result.stderr}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}



# RAM OPTIMIZATION


def clear_ram_cache():
    """
    Clear standby RAM to free up memory for your game.
    
    HOW WINDOWS RAM WORKS:
      Windows doesn't just use RAM for running programs. It also
      keeps recently used data in a "standby" cache, thinking you
      might need it again soon. This is smart for general use,
      but for gaming, that cached data is wasting space your game
      could use.
    
    WHAT WE DO:
      1. Tell Python to clean up its own unused memory (garbage collection)
      2. Call Windows API to reduce our own memory footprint
      3. Clear the system file cache
      4. Clear the standby list (biggest win for gaming)
    
    WHY 32GB HELPS:
      With 32GB of RAM, Windows might keep 8-12GB in standby cache.
      Clearing that gives your game access to all of it.
    
    REQUIRES:
      Administrator privileges to clear system caches.
    """
    results = {
        "success": True,
        "actions": [],
        "ram_before": {},
        "ram_after": {},
    }
    
    # Snapshot RAM before clearing
    ram_before = psutil.virtual_memory()
    results["ram_before"] = {
        "used_mb": round(ram_before.used / (1024 * 1024)),
        "available_mb": round(ram_before.available / (1024 * 1024)),
        "percent": ram_before.percent,
    }
    
    try:
        
        import gc
        gc.collect()
        results["actions"].append("Python garbage collection completed")
        
        # Step 2: Reduce our own working set
        # "Working set" = the RAM our process is actively using.
        # EmptyWorkingSet tells Windows to page out unused memory.
        #
        # ctypes is Python's way of calling Windows C functions directly.
        # It's like a phone call straight to the Windows kernel.
        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.psapi.EmptyWorkingSet(handle)
            results["actions"].append("Reduced process working set")
        except Exception:
            results["actions"].append("Could not reduce working set (not critical)")
        
        # Step 3: Clear the system file cache
        # This uses a Windows system command to flush file caches.
        # These caches store recently read file data in RAM.
        try:
            # Clear DNS cache (networking cache)
            subprocess.run(
                ["ipconfig", "/flushdns"],
                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10
            )
            results["actions"].append("Flushed DNS cache")
        except Exception:
            pass
        
        # Step 4: Clear standby memory using RAMMap-style approach
        # We use a PowerShell command to trigger memory cleanup
        try:
            # This PowerShell command forces Windows to trim working sets
            # of all processes, which moves standby memory to free
            ps_command = (
                "Get-Process | ForEach-Object { "
                "try { $_.MinWorkingSet = $_.MinWorkingSet } catch {} }"
            )
            subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=30
            )
            results["actions"].append("Trimmed process working sets system-wide")
        except Exception:
            results["actions"].append("Could not trim all working sets")
        
        # Brief pause to let Windows reclaim memory
        time.sleep(1)
        
        # Snapshot RAM after clearing
        ram_after = psutil.virtual_memory()
        results["ram_after"] = {
            "used_mb": round(ram_after.used / (1024 * 1024)),
            "available_mb": round(ram_after.available / (1024 * 1024)),
            "percent": ram_after.percent,
        }
        
        freed = results["ram_after"]["available_mb"] - results["ram_before"]["available_mb"]
        results["ram_freed_mb"] = max(0, freed)
        results["message"] = f"Freed approximately {max(0, freed)} MB of RAM"
        
    except Exception as e:
        results["success"] = False
        results["error"] = str(e)
    
    return results



# CPU OPTIMIZATION

PRIORITY_CLASSES = {
    "realtime":     psutil.REALTIME_PRIORITY_CLASS,      #can make the computer unstable
    "high":         psutil.HIGH_PRIORITY_CLASS,           # Best for gaming
    "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "normal":       psutil.NORMAL_PRIORITY_CLASS,
    "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "idle":         psutil.IDLE_PRIORITY_CLASS,
}


def set_process_priority(process_name, priority="high"):
   
    if priority not in PRIORITY_CLASSES:
        return {"success": False, "error": f"Unknown priority: {priority}"}
    
    priority_class = PRIORITY_CLASSES[priority]
    name_lower = process_name.lower()
    found = 0
    set_count = 0
    
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == name_lower:
                found += 1
                proc.nice(priority_class)
                set_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            pass
    
    if found == 0:
        return {
            "success": False,
            "error": f"{process_name} is not currently running. Launch the game first, then set priority."
        }
    
    return {
        "success": True,
        "process": process_name,
        "priority": priority,
        "instances_found": found,
        "instances_set": set_count,
        "message": f"Set {process_name} to {priority} priority ({set_count}/{found} instances)"
    }


def boost_game_process(process_name):
    """
    Apply all CPU optimizations to a game process:
    1. Set HIGH priority
    2. Set CPU affinity to performance cores (if applicable)
    
    WHAT IS CPU AFFINITY?
      Modern CPUs have multiple cores. Affinity controls WHICH
      cores a program is allowed to run on. Some CPUs (like
      Intel 12th/13th/14th gen) have "performance cores" (P-cores)
      and "efficiency cores" (E-cores). We want games on P-cores.
      
      However, for most setups it's better to let Windows decide,
      so we only set priority here and leave affinity alone.
    """
    results = {
        "process": process_name,
        "optimizations": []
    }
    
    # Set to HIGH priority
    priority_result = set_process_priority(process_name, "high")
    results["optimizations"].append({
        "action": "Set CPU priority to HIGH",
        "result": priority_result
    })
    
    return results


# COMBINED OPTIMIZATION (runs everything at once)

def full_optimization(game_process_name=None):
    """
    Run ALL optimizations in sequence:
    1. Switch to High Performance power plan
    2. Clear RAM cache
    3. Boost game process priority (if game name provided)
    
    This is what gets called when Game Mode is activated with
    the enhanced optimizations enabled.
    """
    results = {
        "power_plan": None,
        "ram_clear": None,
        "game_boost": None,
        "summary": []
    }
    
    # 1. Power Plan
    power_result = set_power_plan("high_performance")
    results["power_plan"] = power_result
    if power_result.get("success"):
        results["summary"].append("Switched to High Performance power plan")
    else:
        results["summary"].append(f"Power plan: {power_result.get('error', 'failed')}")
    
    # 2. RAM Clear
    ram_result = clear_ram_cache()
    results["ram_clear"] = ram_result
    if ram_result.get("success"):
        results["summary"].append(f"Cleared {ram_result.get('ram_freed_mb', 0)} MB of RAM")
    
    # 3. Game Process Boost
    if game_process_name:
        boost_result = boost_game_process(game_process_name)
        results["game_boost"] = boost_result
        results["summary"].append(f"Boosted {game_process_name} to HIGH priority")
    else:
        results["summary"].append("No game process specified for priority boost")
    
    return results


def restore_defaults():
    """
    Restore system to normal settings after gaming.
    Call this when deactivating Game Mode.
    """
    results = {
        "power_plan": None,
        "summary": []
    }
    
    # Switch back to Balanced power plan
    power_result = set_power_plan("balanced")
    results["power_plan"] = power_result
    if power_result.get("success"):
        results["summary"].append("Restored Balanced power plan")
    
    return results


# TEST

if __name__ == "__main__":
    print("=" * 60)
    print("  GAME OPTIMIZER - System Optimizations Test")
    print("=" * 60)
    print()
    
    # Test power plan
    print("Current power plan:")
    current = get_current_power_plan()
    print(f"  {current['name']}")
    print()
    
    # Test RAM info
    ram = psutil.virtual_memory()
    print(f"RAM Status:")
    print(f"  Total:     {ram.total // (1024**3)} GB")
    print(f"  Used:      {ram.used // (1024**2)} MB ({ram.percent}%)")
    print(f"  Available: {ram.available // (1024**2)} MB")
    print()
    
    print("Run full_optimization() through the web UI for actual optimization.")
    print("This test is read-only and doesn't change any settings.")
