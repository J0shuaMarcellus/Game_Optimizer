"""
====================================================================
GAME OPTIMIZER - Step 2: Web Server (connects backend to frontend)
====================================================================

WHAT THIS FILE DOES:
  This creates a local web server on your computer. When you open
  your browser to http://localhost:8080, it shows the Game Optimizer
  dashboard. The dashboard talks to this server to get process data,
  kill processes, and manage your whitelist.

CONCEPTS YOU'LL LEARN:
  - What a web server is and how it works
  - What an API is (Application Programming Interface)
  - What HTTP methods (GET, POST, DELETE) mean
  - How a frontend and backend communicate
  - What JSON is and why we use it for APIs

KEY CONCEPT - CLIENT / SERVER MODEL:
  Your BROWSER (the frontend) is the "client" - it asks for things.
  This PYTHON SCRIPT is the "server" - it responds with data.
  
  They communicate using HTTP requests:
    GET    = "Give me data"        (reading)
    POST   = "Here's new data"     (creating/updating)
    DELETE = "Remove this data"    (deleting)
  
  The data goes back and forth as JSON (JavaScript Object Notation).

HOW TO RUN:
  1. Make sure you have Python and psutil installed (see Step 1)
  2. Install Flask:  pip install flask flask-cors
  3. Run AS ADMINISTRATOR:  python step2_server.py
  4. Open your browser to:  http://localhost:8080

WHAT IS FLASK?
  Flask is a Python "web framework." It handles all the complicated
  stuff about running a web server (listening for requests, routing
  URLs, sending responses) so you can focus on your logic.
  Docs: https://flask.palletsprojects.com

WHAT IS CORS?
  CORS = Cross-Origin Resource Sharing. Browsers block requests
  between different domains/ports by default (security feature).
  flask-cors tells the browser "it's okay, allow these requests."
====================================================================
"""

# Import Flask and its helpers
from flask import Flask, jsonify, request, send_from_directory

# CORS lets our frontend (which might run on a different port) 
# talk to this server without the browser blocking it
from flask_cors import CORS

# Import everything we built in Step 1
# Python finds this file because it's in the same folder
import step1_process_manager as pm

import step4_optimizations as opt

import step5_hardware_setup as hw

# 'threading' lets us run the CPU measurement in the background
# without freezing the server
import threading
import time
import psutil

# --------------------------------------------------------------
# CREATE THE APP
# --------------------------------------------------------------

# This creates our web server. '__name__' tells Flask where to
# find files (templates, static files, etc.)
app = Flask(__name__, static_folder="frontend", static_url_path="")

# Enable CORS for all routes - allows the browser to make requests
CORS(app)


# --------------------------------------------------------------
# API ROUTES - these are the URLs the frontend can call
# --------------------------------------------------------------
# 
# WHAT'S A ROUTE?
#   A route maps a URL to a Python function. When someone visits
#   that URL, Flask runs the function and sends back the result.
#
#   Think of it like a restaurant menu:
#     URL (what you order)  ->  Function (kitchen makes it)  ->  Response (your food)
#

@app.route("/")
def serve_frontend():
    """Serve dashboard, or redirect to setup if first run"""
    if not hw.is_setup_complete():
        return send_from_directory("frontend", "setup.html")
    return send_from_directory("frontend", "index.html")

@app.route("/api/processes", methods=["GET"])
def get_processes():
    """
    API ENDPOINT: Get all running processes
    
    URL:     GET /api/processes
    Returns: JSON list of all processes with their info
    
    WHAT THE FRONTEND DOES WITH THIS:
      Displays the process list in a table, color-coded by category.
      The frontend calls this endpoint every few seconds to keep
      the display updated.
    
    EXAMPLE RESPONSE:
    {
      "processes": [
        {
          "pid": 1234,
          "name": "chrome.exe",
          "ram_mb": 450.2,
          "cpu_percent": 3.5,
          "category": "Browser",
          "safe_to_kill": true
        },
        ...
      ],
      "summary": {
        "total": 142,
        "bloat_count": 8,
        "bloat_ram_mb": 1240.5
      }
    }
    """
    processes = pm.get_running_processes()
    
    # Build a summary for the dashboard stats
    bloat = [p for p in processes if p["safe_to_kill"]]
    
    return jsonify({
        "processes": processes,
        "summary": {
            "total": len(processes),
            "bloat_count": len(bloat),
            "bloat_ram_mb": round(sum(p["ram_mb"] for p in bloat), 1),
            "bloat_cpu_percent": round(sum(p["cpu_percent"] for p in bloat), 1),
        }
    })


@app.route("/api/kill", methods=["POST"])
def kill_process():
    """
    API ENDPOINT: Kill a specific process
    
    URL:     POST /api/kill
    Body:    {"name": "chrome.exe"}
    Returns: Result of the kill attempt
    
    WHY POST AND NOT GET?
      Convention: GET is for reading data, POST is for changing things.
      Killing a process changes the system state, so we use POST.
    
    'request.json' contains the data the frontend sent us.
    """
    data = request.json  # Parse the JSON body
    name = data.get("name", "")
    
    if not name:
        return jsonify({"success": False, "error": "No process name provided"}), 400
    
    whitelist = pm.load_whitelist()
    result = pm.kill_process_by_name(name, whitelist)
    
    return jsonify(result)


@app.route("/api/gamemode", methods=["POST"])
def toggle_game_mode():
    """
    API ENDPOINT: Activate Game Mode (kill all bloat + optimize system)
    
    Now does THREE things:
    1. Kills all non-whitelisted, non-critical processes
    2. Switches to High Performance power plan
    3. Clears RAM cache
    
    Optional: Set game process to HIGH CPU priority
    Body: {"activate": true, "game_process": "valorant.exe"}
    """
    data = request.json
    activate = data.get("activate", False)
    game_process = data.get("game_process", None)
    
    if activate:
        whitelist = pm.load_whitelist()
        
        # Step 1: Kill bloat processes
        kill_result = pm.activate_game_mode(whitelist)
        
        # Step 2: Run system optimizations
        opt_result = opt.full_optimization(game_process)
        
        # Combine results
        result = {
            "killed": kill_result.get("killed", []),
            "total_killed": kill_result.get("total_killed", 0),
            "ram_freed_mb": kill_result.get("ram_freed_mb", 0),
            "cpu_freed_percent": kill_result.get("cpu_freed_percent", 0),
            "kept_whitelisted": kill_result.get("kept_whitelisted", []),
            "optimizations": opt_result.get("summary", []),
            "ram_cleared_mb": opt_result.get("ram_clear", {}).get("ram_freed_mb", 0),
            "power_plan": opt_result.get("power_plan", {}),
        }
        return jsonify(result)
    else:
        # Restore defaults when deactivating
        restore_result = opt.restore_defaults()
        return jsonify({
            "message": "Game mode deactivated. Power plan restored to Balanced.",
            "restore": restore_result
        })


@app.route("/api/whitelist", methods=["GET"])
def get_whitelist():
    """
    API ENDPOINT: Get the current whitelist
    
    URL:     GET /api/whitelist
    Returns: List of whitelisted process names
    """
    whitelist = pm.load_whitelist()
    return jsonify({"whitelist": whitelist})


@app.route("/api/whitelist", methods=["POST"])
def add_to_whitelist():
    """
    API ENDPOINT: Add a process to the whitelist
    
    URL:     POST /api/whitelist
    Body:    {"name": "discord.exe"}
    Returns: Updated whitelist
    
    NOTICE: Same URL as GET, but different METHOD (POST vs GET).
    Flask routes by both URL and method, so these don't conflict.
    """
    data = request.json
    name = data.get("name", "")
    
    if not name:
        return jsonify({"success": False, "error": "No process name provided"}), 400
    
    whitelist = pm.load_whitelist()
    
    # Don't add duplicates (case-insensitive check)
    if name.lower() not in [w.lower() for w in whitelist]:
        whitelist.append(name)
        pm.save_whitelist(whitelist)
    
    return jsonify({"success": True, "whitelist": whitelist})


@app.route("/api/whitelist", methods=["DELETE"])
def remove_from_whitelist():
    """
    API ENDPOINT: Remove a process from the whitelist
    
    URL:     DELETE /api/whitelist
    Body:    {"name": "discord.exe"}
    Returns: Updated whitelist
    
    WHY DELETE METHOD?
      REST convention: DELETE means "remove a resource."
      We're removing an item from the whitelist.
    """
    data = request.json
    name = data.get("name", "")
    
    whitelist = pm.load_whitelist()
    # Remove the item (case-insensitive)
    whitelist = [w for w in whitelist if w.lower() != name.lower()]
    pm.save_whitelist(whitelist)
    
    return jsonify({"success": True, "whitelist": whitelist})


@app.route("/api/system", methods=["GET"])
def get_system_info():
    """
    API ENDPOINT: Get overall system resource usage
    
    URL:     GET /api/system
    Returns: CPU, RAM, and disk usage percentages
    
    This powers the gauges/stats at the top of the dashboard.
    
    WHAT THESE NUMBERS MEAN:
      - cpu_percent:    How busy your processor is (0-100%)
      - ram_total:      Total RAM installed (e.g., 16384 MB = 16 GB)
      - ram_used:       How much RAM is currently in use
      - ram_percent:    RAM usage as a percentage
    """
    # psutil makes this super easy
    cpu = psutil.cpu_percent(interval=0.5)  # Measure over 0.5 seconds
    ram = psutil.virtual_memory()
    
    return jsonify({
        "cpu_percent": cpu,
        "ram_total_mb": round(ram.total / (1024 * 1024)),
        "ram_used_mb": round(ram.used / (1024 * 1024)),
        "ram_percent": ram.percent,
        "ram_available_mb": round(ram.available / (1024 * 1024)),
    })

@app.route("/api/optimize", methods=["POST"])
def run_optimization():
    """
    API ENDPOINT: Run specific optimizations without full Game Mode
    
    Body: {"action": "power_plan" | "clear_ram" | "boost_game",
           "game_process": "valorant.exe"}
    """
    data = request.json
    action = data.get("action", "")
    
    if action == "power_plan":
        result = opt.set_power_plan("high_performance")
    elif action == "clear_ram":
        result = opt.clear_ram_cache()
    elif action == "boost_game":
        game = data.get("game_process", "")
        if not game:
            return jsonify({"success": False, "error": "Provide game_process name"}), 400
        result = opt.set_process_priority(game, "high")
    elif action == "restore":
        result = opt.restore_defaults()
    else:
        return jsonify({"success": False, "error": "Unknown action"}), 400
    
    return jsonify(result)


@app.route("/api/system/power", methods=["GET"])
def get_power_plan():
    """Get current power plan"""
    return jsonify(opt.get_current_power_plan())


@app.route("/setup")
def serve_setup():
    """Serve the first-run setup page"""
    return send_from_directory("frontend", "setup.html")


@app.route("/api/setup/status", methods=["GET"])
def setup_status():
    """Check if first-run setup has been completed"""
    return jsonify({"setup_complete": hw.is_setup_complete()})


@app.route("/api/setup/detect", methods=["GET"])
def detect_hardware():
    """Auto-detect hardware and return profiles"""
    return jsonify(hw.auto_detect_hardware())


@app.route("/api/setup/save", methods=["POST"])
def save_setup():
    """Save hardware selections"""
    data = request.json
    selected = data.get("selected_profiles", [])
    config = hw.save_hardware_config(selected)
    return jsonify({
        "success": True,
        "critical_count": len(config["critical_processes"]),
        "config": config
    })

# --------------------------------------------------------------
# START THE SERVER
# --------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  GAME OPTIMIZER - Web Server")
    print("  Open your browser to: http://localhost:8080")
    print("  Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    print("Make sure you're running as Administrator!")
    print()
    
    # 'debug=True' means:
    #   - Auto-restarts when you edit the code
    #   - Shows detailed error pages in the browser
    #   - DO NOT use debug=True in production (security risk)
    #
    # 'host="127.0.0.1"' means only YOUR computer can access it.
    #   If you used "0.0.0.0", other devices on your network could too.
    #
    # 'port=8080' is the port number. Like an apartment number for
    #   your server. The full address is 127.0.0.1:8080
    app.run(host="127.0.0.1", port=8080, debug=True)
