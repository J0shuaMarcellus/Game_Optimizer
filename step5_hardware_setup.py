import json
import os
import subprocess
import sys

import psutil

try:
    import winreg
except ImportError:  # pragma: no cover - Windows-only app
    winreg = None


CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def get_config_path():
    if getattr(sys, "_MEIPASS", False):
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, "hardware_config.json")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "hardware_config.json")


CONFIG_FILE = get_config_path()


# ==============================================================
# HARDWARE PROFILES
# ==============================================================

HARDWARE_PROFILES = {
    "nvidia": {
        "display_name": "NVIDIA GPU",
        "category": "GPU",
        "processes": [
            "nvidia overlay.exe",
            "nvcontainer.exe",
            "nvdisplay.container.exe",
            "nvidia web helper.exe",
            "nvidia share.exe",
            "nvspcaps64.exe",
            "nvbackend.exe",
        ],
        "description": "NVIDIA graphics card drivers and overlay services",
    },
    "amd_gpu": {
        "display_name": "AMD GPU (Radeon)",
        "category": "GPU",
        "processes": [
            "amdrsserv.exe",
            "amddvr.exe",
            "atieclxx.exe",
            "atiesrxx.exe",
            "raabortsvc.exe",
            "amdow.exe",
            "amdrssrc.exe",
            "cncmd.exe",
            "radeonsoft.exe",
        ],
        "description": "AMD Radeon graphics drivers and software",
    },
    "intel_gpu": {
        "display_name": "Intel GPU (Arc / Integrated)",
        "category": "GPU",
        "processes": [
            "igfxem.exe",
            "igfxhk.exe",
            "igfxtray.exe",
            "intelcphdcpsvc.exe",
            "dptf_helper.exe",
        ],
        "description": "Intel graphics drivers",
    },
    "asus": {
        "display_name": "ASUS / ROG Motherboard",
        "category": "Motherboard",
        "processes": [
            "asus_framework.exe",
            "armourycrate.usersessionhelper.exe",
            "armourycrate.service.exe",
            "armourysocketserver.exe",
            "armouryhtmldebugserver.exe",
            "armouryswagent.exe",
            "asuscertservice.exe",
            "asusfancontrolservice.exe",
            "atkexcomsvc.exe",
            "rogliveservice.exe",
            "lightingservice.exe",
            "dipawaymode.exe",
            "asus_framework.exe",
        ],
        "description": "ASUS Armoury Crate, fan control, and RGB services",
    },
    "msi": {
        "display_name": "MSI Motherboard",
        "category": "Motherboard",
        "processes": [
            "msiservice.exe",
            "dragon center.exe",
            "mysticlight.exe",
            "msicenter.exe",
            "liveupdate.exe",
            "msiafterburner.exe",
            "rtsstauber.exe",
        ],
        "description": "MSI Center, Dragon Center, Mystic Light, Afterburner",
    },
    "gigabyte": {
        "display_name": "Gigabyte / Aorus Motherboard",
        "category": "Motherboard",
        "processes": [
            "rgbfusion.exe",
            "gigabyteacpi.exe",
            "appcentercenter.exe",
            "gigabyteupd.exe",
            "easytune.exe",
            "siv.exe",
        ],
        "description": "Gigabyte RGB Fusion, App Center, System Info",
    },
    "asrock": {
        "display_name": "ASRock Motherboard",
        "category": "Motherboard",
        "processes": [
            "asrusb.exe",
            "asrpolychrome.exe",
            "asrockrgbled.exe",
        ],
        "description": "ASRock Polychrome RGB and utilities",
    },
    "nzxt": {
        "display_name": "NZXT (CAM Software)",
        "category": "Cooling",
        "processes": [
            "nzxt cam.exe",
            "cam_helper.exe",
            "nzxt_cam.exe",
        ],
        "description": "NZXT CAM - fan/pump control and monitoring",
    },
    "corsair": {
        "display_name": "Corsair (iCUE)",
        "category": "Cooling / Peripherals",
        "processes": [
            "icue.exe",
            "corsair.service.exe",
            "corsairgamingaudiocfgservice64.exe",
            "cuepluginhost.exe",
        ],
        "description": "Corsair iCUE - controls fans, RGB, and peripherals",
    },
    "noctua": {
        "display_name": "Noctua Fans (no software needed)",
        "category": "Cooling",
        "processes": [],
        "description": "Noctua fans don't need software - nothing to protect",
    },
    "logitech": {
        "display_name": "Logitech (G Hub)",
        "category": "Peripherals",
        "processes": [
            "lghub.exe",
            "lghub_system_tray.exe",
            "lghub_agent.exe",
            "lghub_updater.exe",
            "logi_lamparray_service.exe",
        ],
        "description": "Logitech G Hub - mouse, keyboard, headset settings",
    },
    "razer": {
        "display_name": "Razer (Synapse)",
        "category": "Peripherals",
        "processes": [
            "razercentral.exe",
            "synapse3.exe",
            "razer synapse service.exe",
            "rzsdkservice.exe",
            "gamescanner.exe",
            "razerchromasdkserver.exe",
        ],
        "description": "Razer Synapse - mouse, keyboard, RGB settings",
    },
    "steelseries": {
        "display_name": "SteelSeries (GG / Engine)",
        "category": "Peripherals",
        "processes": [
            "steelseries engine.exe",
            "steelseriesgg.exe",
            "steelseriesengine3.exe",
            "steelseriessonar.exe",
        ],
        "description": "SteelSeries GG and Engine - peripheral control",
    },
    "hyperx": {
        "display_name": "HyperX (NGENUITY)",
        "category": "Peripherals",
        "processes": [
            "ngenuity.exe",
            "hyperxcloud.exe",
        ],
        "description": "HyperX NGENUITY - peripheral settings",
    },
    "bitdefender": {
        "display_name": "Bitdefender Antivirus",
        "category": "Security",
        "processes": [
            "bdservicehost.exe",
            "bdagent.exe",
            "bdntwrk.exe",
            "bdredline.exe",
            "bdvpnservice.exe",
            "productagentservice.exe",
            "updatesrv.exe",
        ],
        "description": "Bitdefender antivirus and firewall",
    },
    "norton": {
        "display_name": "Norton Antivirus",
        "category": "Security",
        "processes": [
            "ns.exe",
            "nsbu.exe",
            "nswsc.exe",
            "navapsvc.exe",
            "nortonantivirusdefinitionupdates.exe",
        ],
        "description": "Norton security services",
    },
    "kaspersky": {
        "display_name": "Kaspersky Antivirus",
        "category": "Security",
        "processes": [
            "avp.exe",
            "avpui.exe",
            "kavtray.exe",
        ],
        "description": "Kaspersky security services",
    },
    "malwarebytes": {
        "display_name": "Malwarebytes",
        "category": "Security",
        "processes": [
            "mbamservice.exe",
            "mbamtray.exe",
        ],
        "description": "Malwarebytes anti-malware",
    },
    "windows_defender": {
        "display_name": "Windows Defender (built-in)",
        "category": "Security",
        "processes": [
            "msmpeng.exe",
            "securityhealthsystray.exe",
            "mpcmdrun.exe",
        ],
        "description": "Windows built-in antivirus (already in system critical)",
    },
    "meta_quest": {
        "display_name": "Meta Quest / Oculus VR",
        "category": "VR",
        "processes": [
            "ovrserver_x64.exe",
            "ovrservicelaunch.exe",
            "ovrredir.exe",
            "oculusclient.exe",
            "oculusdash.exe",
        ],
        "description": "Meta/Oculus VR runtime services",
    },
    "steamvr": {
        "display_name": "SteamVR",
        "category": "VR",
        "processes": [
            "vrserver.exe",
            "vrmonitor.exe",
            "vrcompositor.exe",
        ],
        "description": "SteamVR runtime",
    },
    "anticheat": {
        "display_name": "Anti-Cheat Services",
        "category": "Gaming",
        "processes": [
            "easyanticheat.exe",
            "beclient.exe",
            "beservice.exe",
            "vanguard.exe",
            "vgtray.exe",
            "faceit.exe",
            "eac_service.exe",
        ],
        "description": "Anti-cheat required by competitive games (Valorant, Fortnite, etc.)",
    },
    "kingston_ram": {
        "display_name": "Kingston RAM (FURY / HyperX)",
        "category": "Hardware",
        "processes": [
            "aackingstondramhal_x64.exe",
            "aackingstondramhal_x86.exe",
            "aac3572mbhal_x86.exe",
            "aac3572dramhal_x86.exe",
            "extensioncardhal_x86.exe",
        ],
        "description": "Kingston FURY CTRL RAM monitoring",
    },
    "gskill_ram": {
        "display_name": "G.Skill RAM (Trident Z)",
        "category": "Hardware",
        "processes": [
            "lightingcontrol.exe",
        ],
        "description": "G.Skill Trident Z RGB control",
    },
    "realtek_audio": {
        "display_name": "Realtek Audio",
        "category": "Audio",
        "processes": [
            "rtkauduservice64.exe",
            "ravbg64.exe",
            "rtkngui64.exe",
        ],
        "description": "Realtek audio drivers",
    },
    "nahimic_audio": {
        "display_name": "Nahimic Audio",
        "category": "Audio",
        "processes": [
            "nahimicservice.exe",
            "nahimicsvc64.exe",
        ],
        "description": "Nahimic 3D audio enhancement",
    },
    "process_lasso": {
        "display_name": "Process Lasso",
        "category": "System Tool",
        "processes": [
            "processlasso.exe",
            "processgovernor.exe",
        ],
        "description": "Process Lasso CPU optimizer",
    },
}


DETECTION_RULES = {
    "nvidia": {
        "gpu_keywords": ["nvidia", "geforce", "quadro", "rtx", "gtx"],
        "installed_program_keywords": ["nvidia app", "geforce experience", "nvidia control panel"],
        "service_keywords": ["nvidia", "nvcontainer", "nvdisplay.container"],
    },
    "amd_gpu": {
        "gpu_keywords": ["amd", "radeon"],
        "installed_program_keywords": ["amd software", "radeon software", "adrenalin"],
        "service_keywords": ["amd", "radeon", "amdrs"],
    },
    "intel_gpu": {
        "gpu_keywords": ["intel arc", "intel iris", "intel uhd", "intel hd"],
        "installed_program_keywords": ["intel graphics", "intel arc control"],
        "service_keywords": ["intel graphics", "igcc", "intel arc"],
    },
    "asus": {
        "baseboard_keywords": ["asus", "asustek", "rog"],
        "installed_program_keywords": ["armoury crate", "asus", "rog live service"],
        "service_keywords": ["armoury", "asus", "rog"],
    },
    "msi": {
        "baseboard_keywords": ["msi", "micro-star"],
        "detect_processes": [
            "msiservice.exe",
            "dragon center.exe",
            "mysticlight.exe",
            "msicenter.exe",
            "liveupdate.exe",
        ],
        "installed_program_keywords": ["msi center", "dragon center", "mystic light"],
        "service_keywords": ["msi center", "dragon center", "mystic light", "msiservice"],
    },
    "gigabyte": {
        "baseboard_keywords": ["gigabyte", "aorus"],
        "installed_program_keywords": ["gigabyte", "aorus", "rgb fusion", "app center", "easytune"],
        "service_keywords": ["gigabyte", "aorus", "rgb fusion"],
    },
    "asrock": {
        "baseboard_keywords": ["asrock"],
        "installed_program_keywords": ["asrock", "polychrome"],
        "service_keywords": ["asrock", "polychrome"],
    },
    "nzxt": {
        "installed_program_keywords": ["nzxt cam", "nzxt"],
        "service_keywords": ["nzxt", "cam_helper"],
    },
    "corsair": {
        "installed_program_keywords": ["corsair icue", "icue", "corsair"],
        "service_keywords": ["corsair", "icue"],
    },
    "logitech": {
        "installed_program_keywords": ["logitech g hub", "ghub", "logitech gaming software"],
        "service_keywords": ["logitech", "lghub", "logi"],
    },
    "razer": {
        "installed_program_keywords": ["razer synapse", "razer central", "razer"],
        "service_keywords": ["razer", "synapse"],
    },
    "steelseries": {
        "installed_program_keywords": ["steelseries gg", "steelseries engine", "steelseries"],
        "service_keywords": ["steelseries"],
    },
    "hyperx": {
        "installed_program_keywords": ["hyperx ngenuity", "ngenuity", "hyperx"],
        "service_keywords": ["hyperx", "ngenuity"],
    },
    "bitdefender": {
        "antivirus_keywords": ["bitdefender"],
        "installed_program_keywords": ["bitdefender"],
        "service_keywords": ["bitdefender", "bdservicehost", "bdagent"],
    },
    "norton": {
        "antivirus_keywords": ["norton"],
        "installed_program_keywords": ["norton", "symantec"],
        "service_keywords": ["norton", "symantec"],
    },
    "kaspersky": {
        "antivirus_keywords": ["kaspersky"],
        "installed_program_keywords": ["kaspersky"],
        "service_keywords": ["kaspersky"],
    },
    "malwarebytes": {
        "antivirus_keywords": ["malwarebytes"],
        "installed_program_keywords": ["malwarebytes"],
        "service_keywords": ["malwarebytes"],
    },
    "windows_defender": {
        "antivirus_keywords": ["windows defender", "microsoft defender"],
    },
    "meta_quest": {
        "detect_processes": [
            "ovrserver_x64.exe",
            "ovrservicelaunch.exe",
            "ovrredir.exe",
            "oculusclient.exe",
            "oculusdash.exe",
        ],
        "installed_program_keywords": ["oculus", "meta quest link", "meta quest"],
        "service_keywords": ["oculus", "ovrservice", "ovrlibraryservice"],
    },
    "steamvr": {
        "detect_processes": [
            "vrserver.exe",
            "vrmonitor.exe",
            "vrcompositor.exe",
        ],
        "installed_program_keywords": ["steamvr"],
        "service_keywords": ["steamvr", "vrserver", "vrmonitor", "vrcompositor"],
    },
    "kingston_ram": {
        "installed_program_keywords": ["kingston fury ctrl", "fury ctrl", "kingston fury"],
    },
    "gskill_ram": {
        "installed_program_keywords": ["g.skill", "trident z lighting", "lighting control"],
    },
    "realtek_audio": {
        "sound_keywords": ["realtek"],
        "installed_program_keywords": ["realtek audio", "realtek audio console"],
    },
    "nahimic_audio": {
        "sound_keywords": ["nahimic"],
        "installed_program_keywords": ["nahimic"],
        "service_keywords": ["nahimic"],
    },
    "process_lasso": {
        "installed_program_keywords": ["process lasso"],
        "service_keywords": ["process lasso", "processgovernor"],
    },
}


def normalize_text(value):
    if not value:
        return ""
    return " ".join(str(value).strip().lower().split())


def unique_strings(values):
    result = []
    seen = set()
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        key = normalize_text(text)
        if key in seen:
            continue
        seen.add(key)
        result.append(text)
    return result


def build_lookup(values):
    lookup = {}
    for value in values:
        key = normalize_text(value)
        if key and key not in lookup:
            lookup[key] = str(value).strip()
    return lookup


def run_command(command, timeout=10):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            creationflags=CREATE_NO_WINDOW,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def run_powershell_json(script, timeout=10):
    output = run_command(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        timeout=timeout,
    )
    if not output:
        return []

    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def run_wmic_list_query(class_name, fields):
    output = run_command(
        ["wmic", "path", class_name, "get", ",".join(fields), "/format:list"],
        timeout=10,
    )
    if not output:
        return []

    records = []
    current = {}
    for line in output.splitlines():
        line = line.strip()
        if not line:
            if current:
                records.append(current)
                current = {}
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        current[key.strip()] = value.strip()

    if current:
        records.append(current)

    return records


def collect_running_processes():
    names = set()
    for proc in psutil.process_iter(["name"]):
        try:
            name = proc.info["name"]
            if name:
                names.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(names)


def collect_services():
    service_names = set()
    if not hasattr(psutil, "win_service_iter"):
        return []

    try:
        for service in psutil.win_service_iter():
            try:
                info = service.as_dict()
            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                continue

            for key in ("name", "display_name"):
                value = info.get(key)
                if value:
                    service_names.add(value)
        return sorted(service_names)
    except Exception:
        return []


def collect_installed_programs():
    if winreg is None:
        return []

    programs = set()
    uninstall_roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    for hive, subkey in uninstall_roots:
        try:
            with winreg.OpenKey(hive, subkey) as root:
                key_count = winreg.QueryInfoKey(root)[0]
                for index in range(key_count):
                    try:
                        child_name = winreg.EnumKey(root, index)
                        with winreg.OpenKey(root, child_name) as child:
                            display_name = winreg.QueryValueEx(child, "DisplayName")[0]
                            if display_name:
                                programs.add(display_name)
                    except OSError:
                        continue
        except OSError:
            continue

    return sorted(programs)


def collect_gpu_devices():
    ps_records = run_powershell_json(
        "Get-CimInstance Win32_VideoController | "
        "Select-Object Name, AdapterCompatibility | "
        "ConvertTo-Json -Depth 3 -Compress"
    )

    devices = []
    for record in ps_records:
        name = record.get("Name", "")
        vendor = record.get("AdapterCompatibility", "")
        if name:
            combined = name if not vendor else f"{name} ({vendor})"
            devices.append(combined)

    if devices:
        return unique_strings(devices)

    wmic_records = run_wmic_list_query("Win32_VideoController", ["Name", "AdapterCompatibility"])
    for record in wmic_records:
        name = record.get("Name", "")
        vendor = record.get("AdapterCompatibility", "")
        if name:
            combined = name if not vendor else f"{name} ({vendor})"
            devices.append(combined)

    return unique_strings(devices)


def collect_baseboard_info():
    ps_records = run_powershell_json(
        "Get-CimInstance Win32_BaseBoard | "
        "Select-Object Manufacturer, Product | "
        "ConvertTo-Json -Depth 3 -Compress"
    )

    boards = []
    for record in ps_records:
        manufacturer = record.get("Manufacturer", "")
        product = record.get("Product", "")
        details = " ".join(part for part in [manufacturer, product] if part).strip()
        if details:
            boards.append(details)

    if boards:
        return unique_strings(boards)

    wmic_records = run_wmic_list_query("Win32_BaseBoard", ["Manufacturer", "Product"])
    for record in wmic_records:
        manufacturer = record.get("Manufacturer", "")
        product = record.get("Product", "")
        details = " ".join(part for part in [manufacturer, product] if part).strip()
        if details:
            boards.append(details)

    return unique_strings(boards)


def collect_sound_devices():
    ps_records = run_powershell_json(
        "Get-CimInstance Win32_SoundDevice | "
        "Select-Object Name, Manufacturer | "
        "ConvertTo-Json -Depth 3 -Compress"
    )

    devices = []
    for record in ps_records:
        name = record.get("Name", "")
        manufacturer = record.get("Manufacturer", "")
        if name:
            combined = name if not manufacturer else f"{name} ({manufacturer})"
            devices.append(combined)

    if devices:
        return unique_strings(devices)

    wmic_records = run_wmic_list_query("Win32_SoundDevice", ["Name", "Manufacturer"])
    for record in wmic_records:
        name = record.get("Name", "")
        manufacturer = record.get("Manufacturer", "")
        if name:
            combined = name if not manufacturer else f"{name} ({manufacturer})"
            devices.append(combined)

    return unique_strings(devices)


def collect_antivirus_products():
    records = run_powershell_json(
        "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | "
        "Select-Object displayName | ConvertTo-Json -Depth 3 -Compress"
    )

    products = []
    for record in records:
        name = record.get("displayName", "")
        if name:
            products.append(name)

    return unique_strings(products)


def collect_system_signals():
    running_processes = collect_running_processes()
    services = collect_services()
    installed_programs = collect_installed_programs()
    gpu_devices = collect_gpu_devices()
    baseboards = collect_baseboard_info()
    sound_devices = collect_sound_devices()
    antivirus_products = collect_antivirus_products()

    return {
        "running_processes": running_processes,
        "running_process_lookup": build_lookup(running_processes),
        "services": services,
        "services_lookup": build_lookup(services),
        "installed_programs": installed_programs,
        "installed_programs_lookup": build_lookup(installed_programs),
        "gpu_devices": gpu_devices,
        "gpu_lookup": build_lookup(gpu_devices),
        "baseboards": baseboards,
        "baseboard_lookup": build_lookup(baseboards),
        "sound_devices": sound_devices,
        "sound_lookup": build_lookup(sound_devices),
        "antivirus_products": antivirus_products,
        "antivirus_lookup": build_lookup(antivirus_products),
    }


def exact_lookup_matches(values, lookup):
    matches = []
    for value in values:
        key = normalize_text(value)
        if key in lookup:
            matches.append(lookup[key])
    return unique_strings(matches)


def keyword_lookup_matches(keywords, lookup):
    matches = []
    for normalized_value, original_value in lookup.items():
        if any(keyword in normalized_value for keyword in keywords):
            matches.append(original_value)
    return unique_strings(matches)


def format_evidence(label, values):
    if not values:
        return None
    preview = ", ".join(values[:2])
    if len(values) > 2:
        preview += f", +{len(values) - 2} more"
    return f"{label}: {preview}"


def confidence_from_methods(methods, score):
    if score >= 3 or len(methods) >= 2:
        return "high"
    if score >= 1:
        return "medium"
    return "low"


def evaluate_profile(profile_id, profile, signals):
    rules = DETECTION_RULES.get(profile_id, {})
    evidence = []
    methods = set()
    score = 0

    process_candidates = rules.get("detect_processes", profile["processes"])
    process_matches = exact_lookup_matches(process_candidates, signals["running_process_lookup"])
    if process_matches:
        evidence.append(format_evidence("Running process", process_matches))
        methods.add("process")
        score += 1

    gpu_matches = keyword_lookup_matches(rules.get("gpu_keywords", []), signals["gpu_lookup"])
    if gpu_matches:
        evidence.append(format_evidence("Detected GPU", gpu_matches))
        methods.add("gpu")
        score += 2

    baseboard_matches = keyword_lookup_matches(rules.get("baseboard_keywords", []), signals["baseboard_lookup"])
    if baseboard_matches:
        evidence.append(format_evidence("Motherboard", baseboard_matches))
        methods.add("baseboard")
        score += 2

    sound_matches = keyword_lookup_matches(rules.get("sound_keywords", []), signals["sound_lookup"])
    if sound_matches:
        evidence.append(format_evidence("Audio device", sound_matches))
        methods.add("sound")
        score += 2

    antivirus_matches = keyword_lookup_matches(rules.get("antivirus_keywords", []), signals["antivirus_lookup"])
    if antivirus_matches:
        evidence.append(format_evidence("Antivirus", antivirus_matches))
        methods.add("antivirus")
        score += 2

    installed_matches = keyword_lookup_matches(
        rules.get("installed_program_keywords", []),
        signals["installed_programs_lookup"],
    )
    if installed_matches:
        evidence.append(format_evidence("Installed app", installed_matches))
        methods.add("installed_app")
        score += 1

    service_matches = keyword_lookup_matches(rules.get("service_keywords", []), signals["services_lookup"])
    if service_matches:
        evidence.append(format_evidence("Windows service", service_matches))
        methods.add("service")
        score += 1

    if not evidence:
        return None

    return {
        **profile,
        "matched_processes": process_matches,
        "evidence": [item for item in evidence if item],
        "detection_methods": sorted(methods),
        "confidence": confidence_from_methods(methods, score),
    }


# ==============================================================
# AUTO-DETECTION
# ==============================================================

def auto_detect_hardware():
    """
    Detect hardware using multiple signals:
      - Real hardware inventory (GPU, motherboard, sound devices)
      - Installed applications
      - Windows services
      - Running processes

    This is much more reliable than looking only at running processes,
    because vendor software is not always open when setup runs.
    """
    signals = collect_system_signals()

    detected = {}
    not_detected = {}

    for profile_id, profile in HARDWARE_PROFILES.items():
        detection = evaluate_profile(profile_id, profile, signals)
        if detection:
            detected[profile_id] = detection
        else:
            not_detected[profile_id] = profile

    gpu_info = detect_gpu_brand(signals["gpu_devices"])

    return {
        "detected": detected,
        "not_detected": not_detected,
        "gpu_info": gpu_info,
        "scan_summary": {
            "running_process_count": len(signals["running_processes"]),
            "installed_program_count": len(signals["installed_programs"]),
            "service_count": len(signals["services"]),
            "gpu_count": len(signals["gpu_devices"]),
            "audio_device_count": len(signals["sound_devices"]),
            "antivirus_count": len(signals["antivirus_products"]),
        },
    }


def detect_gpu_brand(gpu_devices=None):
    """
    Detect the active GPU brand from collected device names.
    """
    gpus = unique_strings(gpu_devices or collect_gpu_devices())

    brands = []
    for gpu in gpus:
        gpu_lower = normalize_text(gpu)
        if "nvidia" in gpu_lower or "geforce" in gpu_lower or "quadro" in gpu_lower:
            brands.append("nvidia")
        elif "amd" in gpu_lower or "radeon" in gpu_lower:
            brands.append("amd_gpu")
        elif "intel" in gpu_lower and any(term in gpu_lower for term in ["arc", "iris", "uhd", "hd"]):
            brands.append("intel_gpu")

    brands = unique_strings(brands)

    return {
        "gpus": gpus,
        "brand": brands[0] if brands else "unknown",
        "brands": brands,
    }


# ==============================================================
# CONFIGURATION MANAGEMENT
# ==============================================================

def load_hardware_config():
    """
    Load the saved hardware configuration.
    Returns None if no config exists (first run).
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file_handle:
            return json.load(file_handle)
    return None


def save_hardware_config(selected_profiles):
    """
    Save the user's hardware selections.

    PARAMETERS:
      selected_profiles: List of profile IDs the user selected
                        e.g., ["nvidia", "asus", "logitech", "bitdefender"]
    """
    critical_processes = set()

    for profile_id in selected_profiles:
        if profile_id in HARDWARE_PROFILES:
            for process_name in HARDWARE_PROFILES[profile_id]["processes"]:
                critical_processes.add(process_name.lower())

    config = {
        "selected_profiles": selected_profiles,
        "critical_processes": sorted(list(critical_processes)),
        "setup_complete": True,
    }

    with open(CONFIG_FILE, "w") as file_handle:
        json.dump(config, file_handle, indent=2)

    return config


def is_setup_complete():
    """Check if the user has completed first-run setup."""
    config = load_hardware_config()
    return config is not None and config.get("setup_complete", False)


def get_hardware_critical_processes():
    """
    Get the list of hardware-specific critical processes.
    Returns empty list if setup hasn't been done yet.
    """
    config = load_hardware_config()
    if config:
        return config.get("critical_processes", [])
    return []


if __name__ == "__main__":
    print("=" * 60)
    print("  GAME OPTIMIZER - Hardware Detection Test")
    print("=" * 60)
    print()

    result = auto_detect_hardware()

    print(f"GPU devices: {result['gpu_info'].get('gpus', ['Unknown'])}")
    print(f"Primary GPU brand: {result['gpu_info'].get('brand', 'unknown')}")
    print()

    print("DETECTED HARDWARE:")
    for profile_id, info in result["detected"].items():
        print(f"  [{info['confidence'].upper()}] {info['display_name']}")
        for line in info.get("evidence", []):
            print(f"    {line}")

    print()
    print("NOT DETECTED (user can manually select):")
    for profile_id, info in result["not_detected"].items():
        print(f"  {info['display_name']} ({info['category']})")
