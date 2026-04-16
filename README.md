# Game Optimizer - Learn-As-You-Build Guide

## What You're Building
A Windows app that kills unnecessary background processes when you game,
freeing up RAM and CPU for smoother performance. You control which apps 
stay alive via a whitelist.

---

## Quick Setup (5 minutes)

### 1. Install Python
- Download from https://python.org
- **IMPORTANT**: Check "Add Python to PATH" during install

### 2. Install Dependencies
Open Command Prompt (search "cmd" in Start) and run:
```
pip install psutil flask flask-cors
```

### 3. Organize Your Files
Put all files in one folder, like this:
```
C:\GameOptimizer\
  ├── step1_process_manager.py    (backend core)
  ├── step2_server.py             (web server)
  ├── whitelist.json              (auto-created on first run)
  └── frontend\
      └── index.html              (dashboard UI)
```

### 4. Test the Backend (Step 1)
```
cd C:\GameOptimizer
python step1_process_manager.py
```
This does a READ-ONLY scan — nothing gets killed. You'll see a list
of detected bloat processes and how much RAM they use.

### 5. Run the Full App (Step 2)
**Right-click Command Prompt → "Run as administrator"**, then:
```
cd C:\GameOptimizer
python step2_server.py
```
Open your browser to **http://localhost:5000** and you'll see the dashboard.

---

## How It Works (The Architecture)

```
┌─────────────┐     HTTP requests      ┌──────────────────┐
│   Browser   │ ◄──────────────────────►│  Flask Server    │
│  (frontend) │   JSON responses        │  (step2_server)  │
│  index.html │                         │                  │
└─────────────┘                         │  Uses functions  │
                                        │  from step1      │
                                        │                  │
                                        │  ┌────────────┐  │
                                        │  │  psutil    │  │
                                        │  │ (talks to  │  │
                                        │  │  Windows)  │  │
                                        │  └────────────┘  │
                                        └──────────────────┘
```

1. **You click "Game Mode"** in the browser
2. **Browser sends** a POST request to `/api/gamemode`
3. **Flask receives it** and calls `activate_game_mode()`
4. **psutil scans** all Windows processes
5. **Backend kills** bloat processes (skipping whitelist + system-critical)
6. **Server responds** with a report (what was killed, RAM freed)
7. **Browser updates** the dashboard with the results

---

## What Each File Teaches You

### step1_process_manager.py
- How Windows processes work (PIDs, memory, CPU)
- Reading/writing JSON config files
- Sets, lists, and dictionaries in Python
- Error handling with try/except
- The `psutil` library for OS interaction

### step2_server.py
- What a web server does
- REST API design (GET, POST, DELETE)
- How Flask routes work
- Client-server architecture
- What CORS is and why it exists

### frontend/index.html
- HTML structure and semantic elements
- CSS styling, variables, flexbox, and grid
- JavaScript async/await and fetch()
- DOM manipulation (updating the page dynamically)
- Security basics (escaping HTML to prevent XSS)

---

## Next Steps (Things to Try)

1. **Add a new bloat process**: Found an app eating RAM? Add it to 
   `KNOWN_BLOAT` in step1 and restart the server.

2. **Create game profiles**: Different whitelists for different games
   (keep Spotify for RPGs, kill it for competitive FPS).

3. **Auto-detect games**: Use psutil to detect when a game launches
   and automatically activate Game Mode.

4. **System tray icon**: Use `pystray` to put the app in your 
   system tray so it runs in the background.

5. **Startup script**: Create a .bat file to launch everything 
   with one double-click.

---

## Troubleshooting

**"Access Denied" errors when killing processes**
→ You must run Command Prompt as Administrator

**"Module not found: psutil"**
→ Run: `pip install psutil`

**Browser shows "Server offline"**
→ Make sure step2_server.py is running in your terminal

**A process keeps coming back after killing it**
→ Some Windows services auto-restart. You may need to disable 
   them in Windows Services (services.msc) instead.

   "whitelist": [
    "Spotify.exe",
    "Python",
    "Claude.exe",
    "Discord.exe",
    "Steam.exe",
    "steamwebhelper.exe",
    "lghub.exe",
    "nvcontainer.exe",
    "Widgets.exe",
    "msedgewebview2.exe",
    "python3.12.exe",
    "RocketLeague.exe",
    "Peace.exe",
    "BakkesMod.exe",
    "Marathon.exe"
  ]
}