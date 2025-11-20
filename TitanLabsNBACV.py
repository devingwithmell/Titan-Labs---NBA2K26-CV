"""
Titan Labs
Copyright (c) 2025 Titan Labs. All rights reserved.
"""

import sys, os, time, json, socket, threading, tempfile, subprocess, atexit, signal, ctypes, hashlib
from PyQt6.QtCore import Qt
import cv2
import numpy as np
from gtuner import *
from PyQt6.QtGui import QColor
import urllib.request
import requests

VERIFY_API = "http://IP:PORT" 
GUILD_ID = 1369603913648439356 
REQUIRED_ROLE_IDS = [
    1372488977084321882,  # Owner
    1434796700735770674,  # Lifetime
    1434796593340743711   # Monthly
]
WEBHOOK_URL = ""  # your webhook

# if you keep KeyAuth gating on:
DISABLE_KEYAUTH = True

# === Optimized Constants ===
FONT_SIMPLEX = cv2.FONT_HERSHEY_SIMPLEX
FONT_DUPLEX = cv2.FONT_HERSHEY_DUPLEX
FONT_TRIPLEX = cv2.FONT_HERSHEY_TRIPLEX

COLOR_BLACK = (0,0,0)
COLOR_YELLOW = (255,255,0)
COLOR_GREEN = (0,255,0)
COLOR_PURPLE = (255,0,255)

MORPH_KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 5))

def _xor_str(s, k=0x7F):
    return ''.join(chr(ord(c) ^ k) for c in s)

def _check_vm():
    if sys.platform == 'win32':
        try:
            checks = [
                ('VBOX', 'VirtualBox'),
                ('QEMU', 'QEMU'),
                ('VMWARE', 'VMware'),
                ('VIRTUAL', 'VM'),
            ]
            import wmi
            c = wmi.WMI()
            for item in c.Win32_ComputerSystem():
                model = item.Model.upper()
                manufacturer = item.Manufacturer.upper()
                for check, _ in checks:
                    if check in model or check in manufacturer:
                        return True
        except:
            pass
    return False

def _check_dbg():
    if sys.platform == 'win32':
        try:
            k32 = ctypes.windll.kernel32
            if k32.IsDebuggerPresent():
                return True
            dbg = ctypes.c_int(0)
            ntdll = ctypes.windll.ntdll
            ntdll.NtQueryInformationProcess(k32.GetCurrentProcess(), 0x1f, ctypes.byref(dbg), ctypes.sizeof(dbg), None)
            if dbg.value:
                return True

            h = k32.GetModuleHandleW(None)
            peb = ctypes.c_void_p()
            ntdll.NtQueryInformationProcess(k32.GetCurrentProcess(), 0, ctypes.byref(peb), ctypes.sizeof(peb), None)

        except:
            pass
    return False

def _check_tools():
    if sys.platform == 'win32':
        try:
            tools = [
                _xor_str('\x1b\x0c\x13\x04\x12'),
                _xor_str('\x08\x03\x00'),
                _xor_str('x64dbg'),
                _xor_str('\x17\r\x13\r\x13\x18\x13\r\x12'),
                _xor_str('\x0f\x0e\x13\x13\x04\x12'),
            ]
            result = subprocess.run(['tasklist'], capture_output=True, text=True, creationflags=0x08000000)
            output = result.stdout.lower()
            for tool in tools:
                if tool.lower() in output:
                    return True
        except:
            pass
    return False

def _scan_loaded_modules():
    try:
        import psutil
        for dll in psutil.Process().memory_maps():
            p = dll.path.lower()
            if any(x in p for x in ("cheatengine", "x64dbg", "ida", "ollydbg", "scylla")):
                os._exit(1)
    except:
        pass

def _timing_check():
    start = time.perf_counter()
    x = sum(i for i in range(1000))
    end = time.perf_counter()
    return (end - start) > 0.01

_integrity_hash = None

def _calc_integrity():
    global _integrity_hash
    try:
        script_path = os.path.abspath(__file__)
        with open(script_path, 'rb') as f:
            content = f.read()
        _integrity_hash = hashlib.sha256(content).hexdigest()
    except:
        _integrity_hash = None

_script_mtime = os.path.getmtime(__file__)

def _mtime_check():
    if os.path.getmtime(__file__) != _script_mtime:
        os._exit(1)

def _verify_integrity():
    if _integrity_hash is None:
        return True
    try:
        script_path = os.path.abspath(__file__)
        with open(script_path, 'rb') as f:
            content = f.read()
        current = hashlib.sha256(content).hexdigest()
        return current == _integrity_hash
    except:
        return False

def _sec_init():
    if _check_dbg() or _check_vm() or _check_tools():
        os._exit(1)
    if _timing_check():
        time.sleep(0.1)
        if _timing_check():
            os._exit(1)
    _calc_integrity()

_sec_init()
# --- FULL DEVELOPMENT BYPASS ---
if DISABLE_KEYAUTH:
    LOGGED_IN = True
    TITANLABS_ENABLED = True
    print("[DEV] Full bypass mode enabled: KeyAuth + Discord + Login skipped")

def _runtime_check():
    if not _verify_integrity():
        os._exit(1)
    if _check_dbg():
        os._exit(1)
    if sys.gettrace():
        os._exit(1)
    _mtime_check()

class _SecurityMonitor(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.running = True

    def run(self):
        while self.running:
            try:
                time.sleep(5)

                # ✅ Debugger detection
                if _check_dbg():
                    os._exit(1)

                # ✅ Known reversing tools (x64dbg, cheatengine, etc)
                if _check_tools():
                    os._exit(1)

                # ✅ Hash tamper detection
                if not _verify_integrity():
                    os._exit(1)

                # ✅ Loaded DLL/module scan
                if _scan_loaded_modules():
                    os._exit(1)

                # ✅ Modification timestamp check
                _mtime_check()

            except:
                pass

    def run(self):
        while self.running:
            try:
                time.sleep(5)
                if _check_dbg() or _check_tools():
                    os._exit(1)
                if not _verify_integrity():
                    os._exit(1)
            except:
                pass

_monitor = _SecurityMonitor()
_monitor.start()

RESET_DROP_PX = 15
MIN_STABLE_FRAMES = 3
MIN_OVER_FRAMES = 1
REFRACTORY_FRAMES = 10

class MeterCycle:
    def __init__(self, max_meter_px=95):
        self.state = "IDLE"
        self.baseline_start = None
        self.stable_count = 0
        self.over_count = 0
        self.refractory = 0
        self.peak = 0
        self.last_height = 0
        self.max_meter_px = max_meter_px

    def reset_cycle(self):
        self.state = "IDLE"
        self.baseline_start = None
        self.stable_count = 0
        self.over_count = 0
        self.peak = 0

    def update(self, h_now, want_px):
        try:
            h_now = max(0, min(self.max_meter_px, int(h_now)))
        except Exception:
            h_now = 0
        if self.refractory > 0:
            self.refractory -= 1
        if self.state in ("TRACKING", "FIRED", "COOLDOWN"):
            if (self.last_height - h_now) >= RESET_DROP_PX or h_now == 0:
                self.reset_cycle()
        if self.state == "IDLE":
            if h_now > 0:
                self.state = "ARMING"
                self.stable_count = 1
                self.baseline_start = h_now
                self.peak = h_now
        elif self.state == "ARMING":
            self.baseline_start = min(self.baseline_start, h_now)
            self.stable_count += 1
            self.peak = max(self.peak, h_now)
            if self.stable_count >= MIN_STABLE_FRAMES:
                self.state = "TRACKING"
                self.over_count = 0
        elif self.state == "TRACKING":
            self.peak = max(self.peak, h_now)
            growth = max(0, h_now - (self.baseline_start or 0))
            total_fill = min(self.max_meter_px, (self.baseline_start or 0) + growth)
            if total_fill >= want_px and self.refractory == 0:
                self.over_count += 1
            else:
                self.over_count = 0
            if self.over_count >= MIN_OVER_FRAMES:
                self.state = "FIRED"
                self.refractory = REFRACTORY_FRAMES
                self.last_height = h_now
                return "fire", total_fill
            self.last_height = h_now
            return "none", total_fill
        self.last_height = h_now
        total_fill = h_now if self.baseline_start is None else min(self.max_meter_px, self.baseline_start + max(0, h_now - self.baseline_start))
        return "none", total_fill


def get_asset_path(filename):
    base = os.path.join(os.getenv("APPDATA") or tempfile.gettempdir(), "2kVision", "Assets")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, filename)

def ensure_asset(filename, url):
    """Download asset if missing or 0-byte."""
    path = get_asset_path(filename)
    if not os.path.exists(path) or os.path.getsize(path) < 10_000:  
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=6).read()
            with open(path, "wb") as f:
                f.write(data)
        except Exception:
            pass
    return path

TL_LOGO_PATH = ensure_asset("TL.png", "https://raw.githubusercontent.com/devingwithmell/TitanLabs-Buildsv2/main/TL.png")
TL_FULL_LOGO_PATH = ensure_asset("TL_FULL_LOGO.png", "https://raw.githubusercontent.com/devingwithmell/TitanLabs-Buildsv2/main/TL%20FULL%20LOGO.png")
LOGGED_IN = False
_WORKER_INSTANCE = None

# Shot threshold: when meter reaches this pixel height, shot fires
# Set to 95 = fires at 100% meter fill (when MAX_METER_PX = 95)
# Lower this value to fire earlier (e.g., 86 = 90% fill, 76 = 80% fill)
# This is for Arrow2 Meter. Increase/decrease for whatever meter you would like to use. Remember to increase height of meter roi if changing to Straight meter...etc.
_METER_THRESHOLD_PIXEL = 95

# Tempo shot pulse duration in milliseconds
# Controls how long the tempo shot button is held
# How long software waits before it flicks up
_TEMPO_DURATION = 50

TITANLABS_ENABLED = False

# Meter detection region on screen (x, y, width, height)
# Adjust these values to match where the meter appears on your screen
METER_REGION = {"x": 900, "y": 220, "w": 64, "h": 593}

# Maximum meter height in pixels
# This is the full height of the meter bar when at 100%
# Increase this if your meter bar is taller on screen
# Example: if meter bar is 100px tall, set MAX_METER_PX = 100
MAX_METER_PX = 95
DRAW_ROI_WIDTH = 64 # Green ROI Width - change for whatever meter you would like to use. Straight is taller but thinner...
DRAW_ROI_HEIGHT = 200 # Green ROI Height - change for whatever meter you would like to use. Straight is taller but thinner...

# BGR color ranges for meter detection (multiple ranges for better accuracy)
METER_BGR_RANGES = [
    (np.array([244, 45, 237], dtype=np.uint8), np.array([255, 65, 255], dtype=np.uint8)),
    (np.array([230, 40, 220], dtype=np.uint8), np.array([255, 70, 255], dtype=np.uint8)),
    (np.array([240, 50, 230], dtype=np.uint8), np.array([255, 60, 255], dtype=np.uint8))
]

SHOW_BBOX = True
MODE = "Online"
# === User-selected Meter Color (default Purple) ===
USER_METER_COLOR = (255, 0, 255)  # BGR

try:
    save_path = os.path.join(os.getenv("APPDATA") or tempfile.gettempdir(), "TitanLabs")
    state_file = os.path.join(save_path, "ui_state.json")
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "show_bbox" in data:
                SHOW_BBOX = bool(data["show_bbox"])
except Exception:
    pass

_state_lock = threading.Lock()

def set_state(new_vals: dict):
    global LOGGED_IN
    with _state_lock:
        if "logged_in" in new_vals:
            LOGGED_IN = bool(new_vals["logged_in"])
        if "tlabs_enabled" in new_vals:
            globals()["TITANLABS_ENABLED"] = bool(new_vals["tlabs_enabled"])
        if "meter_region" in new_vals and isinstance(new_vals["meter_region"], dict):
            mr = new_vals["meter_region"]
            for k in ("x","y","w","h"):
                if k in mr:
                    METER_REGION[k] = int(mr[k])
        if "mode" in new_vals:
            globals()["MODE"] = str(new_vals["mode"])
        if "show_bbox" in new_vals:
            globals()["SHOW_BBOX"] = bool(new_vals["show_bbox"])
                # ---- Handle user-selected meter color ----
        if "meter_color" in new_vals:
            try:
                global USER_METER_COLOR
                USER_METER_COLOR = tuple(map(int, new_vals["meter_color"]))  # BGR
            except:
                pass
            try:
                save_path = os.path.join(os.getenv("APPDATA") or tempfile.gettempdir(), "TitanLabs")
                os.makedirs(save_path, exist_ok=True)
                state_file = os.path.join(save_path, "ui_state.json")
                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump({"show_bbox": SHOW_BBOX}, f)
            except Exception:
                pass
        if "meter_fill_threshold" in new_vals:
            try:
                fill_pct = int(new_vals["meter_fill_threshold"])
                fill_pct = max(1, min(100, fill_pct))
                # Convert percentage to pixels 
                fill_px = max(1, min(MAX_METER_PX, int(round((fill_pct / 100.0) * MAX_METER_PX))))
                global _METER_THRESHOLD_PIXEL
                _METER_THRESHOLD_PIXEL = fill_px
            except Exception:
                pass
        if "tempo_duration" in new_vals:
            try:
                tempo_ms = int(new_vals["tempo_duration"])
                tempo_ms = max(0, min(255, tempo_ms))
                # Update global tempo duration (survives script reloads)
                global _TEMPO_DURATION
                _TEMPO_DURATION = tempo_ms
            except Exception:
                pass

class JSONServer(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self.sock.listen(1)
        self.client = None
        self.stop_flag = False

    def run(self):
        self.sock.settimeout(0.5)
        buf = b""
        while not self.stop_flag:
            try:
                if self.client is None:
                    try:
                        c, _ = self.sock.accept()
                        c.settimeout(0.05)
                        self.client = c
                        init = {"type": "state"}
                        c.sendall((json.dumps(init) + "\n").encode("utf-8"))
                    except socket.timeout:
                        continue
                else:
                    try:
                        data = self.client.recv(4096)
                        if not data:
                            self.client.close()
                            self.client = None
                            continue
                        buf += data
                        while b"\n" in buf:
                            line, buf = buf.split(b"\n", 1)
                            if not line.strip():
                                continue
                            try:
                                msg = json.loads(line.decode("utf-8", errors="ignore"))
                            except Exception:
                                continue
                            if isinstance(msg, dict) and msg.get("type") == "update":
                                set_state(msg)
                    except socket.timeout:
                        pass
                    except (ConnectionResetError, OSError):
                        if self.client:
                            try: self.client.close()
                            except: pass
                        self.client = None
            except Exception:
                time.sleep(0.02)

    def stop(self):
        self.stop_flag = True
        try:
            if self.client:
                self.client.close()
        except: pass
        try:
            self.sock.close()
        except: pass

def launch_external_gui(port: int):
    gui_code = r'''
import sys, json, socket, threading, urllib.request, urllib.parse, time, os, tempfile, traceback
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QScrollArea, QFrame, QGridLayout, QSizePolicy,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox, QColorDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QColor, QIcon, QPixmap
import os
import requests

VERIFY_API = os.getenv("VERIFY_API") or "http://104.234.236.62:30249"
TL_LOGO_PATH = os.getenv("TL_LOGO_PATH", "")
TL_FULL_LOGO_PATH = os.getenv("TL_FULL_LOGO_PATH", "")

THEME = {
    "accent": "#E05B5B",       
    "accent_hover": "#FF6D6D",
    "bg_main": "#0D0D10",
    "bg_panel": "#17171D",
    "bg_sidebar": "#121218",
    "text": "#EDEDF7",
    "text_muted": "#A9ACBF",
    "border": "#2A2B35",
    "chip_bg": "#1F2028",
    "chip_border": "#2F303A",
    "sidebar_active": "#1E1E26",
    "divider": "#1F1F26",
}

def apply_theme(widget):
    widget.setStyleSheet(f"""
        QWidget {{
            background: {THEME['bg_main']};
            color: {THEME['text']};
            border: none;
            font-size: 13px;
        }}

        QFrame {{
            background: {THEME['bg_panel']};
            border: none;
            border-radius: 10px;
        }}

        QLabel[role="title"] {{
            color: #FFFFFF;
            font-weight: 700;
            letter-spacing: .3px;
        }}

        QPushButton {{
            background: {THEME['chip_bg']};
            color: {THEME['text']};
            border: 1px solid {THEME['chip_border']};
            border-radius: 8px;
            padding: 6px 10px;
        }}
        QPushButton:hover {{
            background: {THEME['accent_hover']};
            color: #fff;
            border: none;
        }}
        QPushButton:checked {{
            background: {THEME['accent']};
            color: #fff;
            border: none;
        }}
        *:focus {{
            outline: none;
            border: none;
        }}
        QPushButton:focus {{
            outline: none;
            border: none;
        }}

        QLineEdit, QSpinBox, QDoubleSpinBox {{
            background: #0F0F14;
            color: {THEME['text']};
            border: 1px solid #2B2C37;
            border-radius: 8px;
            padding: 6px 8px;
        }}
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {THEME['accent']};
        }}

        QScrollArea {{
            border:none; background: transparent;
        }}

        #LeftSidebar {{
            background: {THEME['bg_sidebar']};
            border: none;
            border-radius: 12px;
        }}
        #NavButton {{
            text-align: left;
            padding: 9px 12px;
            background: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            color: {THEME['text_muted']};
        }}
        #NavButton:hover {{
            background: {THEME['sidebar_active']};
            color: {THEME['text']};
            border-color: {THEME['chip_border']};
        }}
        #NavButton[active="true"] {{
            background: {THEME['accent']};
            color: #ffffff;
            border-color: {THEME['accent']};
        }}
    """)

KEYAUTH_URL       = "https://keyauth.win/api/1.2/"
KEYAUTH_APP_NAME  = "Enter App Name"
KEYAUTH_OWNER_ID  = "Enter Owner ID"
KEYAUTH_SECRET    = "Enter Secret"
KEYAUTH_VERSION   = "1.0"
WEBHOOK_URL = "POST WEBHOOK"
DISABLE_KEYAUTH = False   

VERIFY_API = "http://IP:PORT"  # e.g. 
GUILD_ID = 1369603913648439356
REQUIRED_ROLE_IDS = [
    1372488977084321882,  # Owner
    1434796700735770674,  # Lifetime
    1434796593340743711   # Monthly
]

class HostClient(threading.Thread):
    def __init__(self, host, port):
        super().__init__(daemon=True)
        self.host, self.port = host, port
        self.sock = None
        self.stop_flag = False
        self.connected_once = False
        self.disconnect_count = 0

    def run(self):
        while not self.stop_flag:
            try:
                self.sock = socket.create_connection((self.host, self.port), timeout=1.0)
                self.sock.settimeout(0.05)
                self.connected_once = True
                self.disconnect_count = 0
                while not self.stop_flag:
                    try:
                        data = self.sock.recv(4096)
                        if not data: break
                    except socket.timeout:
                        pass
            except Exception:
                if self.connected_once:
                    self.disconnect_count += 1
                    if self.disconnect_count > 30:  # 30 failed reconnect attempts
                        os._exit(0)
                time.sleep(1)
            try:
                if self.sock: self.sock.close()
            except: pass
            self.sock = None

    def send(self, obj: dict):
        try:
            if self.sock:
                self.sock.sendall((json.dumps(obj)+"\n").encode("utf-8"))
        except Exception:
            pass

def http_post(url, data: dict, timeout=8):
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")

class Panel(QFrame):
    def __init__(self, title):
        super().__init__()
        v = QVBoxLayout(self)
        t = QLabel(title); t.setProperty("role","title")
        v.addWidget(t)
        self.body = QVBoxLayout(); self.body.setSpacing(8)
        v.addLayout(self.body)

class LeftNav(QWidget):
    def __init__(self, tab_names, on_change):
        super().__init__()
        self.setObjectName("LeftSidebar")
        self._on_change = on_change
        self._buttons = []

        v = QVBoxLayout(self)
        v.setContentsMargins(10,10,10,10); v.setSpacing(8)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(6)
        logo_row.setContentsMargins(0, 0, 0, 0)

        logo = QLabel()
        logo.setFixedSize(28, 28)
        logo.setStyleSheet("border:none; background:transparent;")

        try:
            from PyQt6.QtGui import QPixmap
            if TL_FULL_LOGO_PATH and os.path.exists(TL_FULL_LOGO_PATH):
                pix = QPixmap(TL_FULL_LOGO_PATH)
                if not pix.isNull():
                    logo.setPixmap(pix.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    logo.setText("TL")
                    logo.setStyleSheet("font-weight:800; color:#E05B5B;")
            else:
                logo.setText("TL")
                logo.setStyleSheet("font-weight:800; color:#E05B5B;")
        except Exception as e:
            logo.setText("TL")
            logo.setStyleSheet("font-weight:800; color:#E05B5B;")

        title = QLabel("Titan Labs")
        title.setStyleSheet("font-weight:800; font-size:15px;")

        logo_row.addWidget(logo)
        logo_row.addWidget(title)
        logo_row.addStretch(1)

        v.addLayout(logo_row)

        subtitle = QLabel("Modules")
        subtitle.setStyleSheet(f"color:{THEME['text_muted']}; font-size:12px; margin-top:2px;")
        v.addWidget(subtitle)
        v.addSpacing(6)
        divider2 = QFrame()
        divider2.setFixedHeight(1)
        divider2.setStyleSheet(f"background:{THEME['border']}; border:none; margin-top:6px; margin-bottom:6px;")
        v.addWidget(divider2)

        for i, name in enumerate(tab_names):
            b = QPushButton(name)
            b.setObjectName("NavButton")
            b.setProperty("active", "false")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setMinimumHeight(36)
            b.clicked.connect(lambda _, idx=i: self.set_active(idx))
            self._buttons.append(b)
            v.addWidget(b)

        v.addStretch(1)
        foot = QLabel("Version  •  1.0.0")
        foot.setStyleSheet(f"color:{THEME['text_muted']}; font-size:11px;")
        v.addWidget(foot)

        self.setFixedWidth(176)

    def set_active(self, idx: int):
        for i, b in enumerate(self._buttons):
            b.setProperty("active", "true" if i == idx else "false")
            b.style().unpolish(b); b.style().polish(b)
        self._on_change(idx)

class AuthPage(QWidget):
    def __init__(self, on_authed):
        super().__init__()
        self.on_authed = on_authed

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(10)

        card = QFrame(); card.setFixedWidth(420)
        h = QHBoxLayout(); h.addStretch(1); h.addWidget(card); h.addStretch(1)
        layout.addLayout(h)

        form = QVBoxLayout(card)
        form.setContentsMargins(24,24,24,24)
        form.setSpacing(12)

        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFixedHeight(140)
        form.addWidget(logo_label)
        try:
            if TL_LOGO_PATH and os.path.exists(TL_LOGO_PATH):
                pix = QPixmap(TL_LOGO_PATH)
                if not pix.isNull():
                    logo_label.setPixmap(pix.scaledToWidth(160, Qt.TransformationMode.SmoothTransformation))
                else:
                    logo_label.setText("Titan Labs"); logo_label.setStyleSheet("font-size:22px; font-weight:800; color:#E05B5B;")
            else:
                logo_label.setText("Titan Labs"); logo_label.setStyleSheet("font-size:22px; font-weight:800; color:#E05B5B;")
        except:
            logo_label.setText("Titan Labs"); logo_label.setStyleSheet("font-size:22px; font-weight:800; color:#E05B5B;")

        # --- Login fields ---
        self.user = QLineEdit(); self.user.setPlaceholderText("Username"); self.user.setFixedHeight(38)
        self.passw = QLineEdit(); self.passw.setPlaceholderText("Password"); self.passw.setEchoMode(QLineEdit.EchoMode.Password); self.passw.setFixedHeight(38)
        self.lic   = QLineEdit(); self.lic.setPlaceholderText("License Key (for register)"); self.lic.setFixedHeight(38)

        # --- Discord linking (ON LOGIN PAGE) ---
        self.discord_id = QLineEdit()
        self.discord_id.setPlaceholderText("Discord ID (right-click user → Copy ID)")
        self.discord_id.setFixedHeight(38)

# --- Login fields ---
        self.user = QLineEdit(); self.user.setPlaceholderText("Username"); self.user.setFixedHeight(38)
        self.passw = QLineEdit(); self.passw.setPlaceholderText("Password"); self.passw.setEchoMode(QLineEdit.EchoMode.Password); self.passw.setFixedHeight(38)
        self.lic   = QLineEdit(); self.lic.setPlaceholderText("License Key (for register)"); self.lic.setFixedHeight(38)

        # --- Discord linking (ON LOGIN PAGE) ---
        self.discord_id = QLineEdit()
        self.discord_id.setPlaceholderText("Discord ID (right-click user → Copy ID)")
        self.discord_id.setFixedHeight(38)

        # ✅ ✅ ✅ INSERT LOAD BLOCK HERE
        try:
            sp = os.path.join(os.getenv("APPDATA") or tempfile.gettempdir(), "TitanLabs")
            os.makedirs(sp, exist_ok=True)
            cf = os.path.join(sp, "login.json")

            if os.path.exists(cf):
                with open(cf, "r", encoding="utf-8") as f:
                    ld = json.load(f)

                u = ld.get("username", "")
                p = ld.get("password", "")
                k = ld.get("license_key", "")
                d = ld.get("discord_id", "")
                r = bool(ld.get("remember", False))

                if r:
                    self.user.setText(u)
                    self.passw.setText(p)
                    self.lic.setText(k)
                    self.discord_id.setText(d)
                    self.remember.setChecked(True)

        except Exception as e:
            print("LOAD LOGIN ERROR:", e)
        # ✅ ✅ ✅ END LOAD BLOCK

        self.btn_link = QPushButton("🔗 Link License to Discord"); self.btn_link.setFixedHeight(36)
        self.link_msg = QLabel(""); self.link_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.link_msg.setStyleSheet("color:#ff5f5f; font-weight:600;")

        for w in (self.user, self.passw, self.lic, self.discord_id, self.btn_link, self.link_msg):
            form.addWidget(w)

        # Remember me
        self.remember = QCheckBox("Remember me"); form.addWidget(self.remember)

        # Apply saved "remember me" state
        try:
            sp = os.path.join(os.getenv("APPDATA") or tempfile.gettempdir(), "TitanLabs")
            cf = os.path.join(sp, "login.json")
            if os.path.exists(cf):
                with open(cf, "r", encoding="utf-8") as f:
                    ld = json.load(f)
                if ld.get("remember"):
                    self.remember.setChecked(True)
        except:
            pass

        # Login/Register row
        row = QHBoxLayout()
        self.btn_login = QPushButton("Login"); self.btn_login.setFixedHeight(36)
        self.btn_reg   = QPushButton("Register"); self.btn_reg.setFixedHeight(36)
        row.addWidget(self.btn_login); row.addWidget(self.btn_reg)
        form.addLayout(row)

        # Status
        self.msg = QLabel("")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg.setStyleSheet("color:#ff5f5f; font-weight:600;")
        form.addWidget(self.msg)

        # Wire up actions
        self.btn_link.clicked.connect(self.link_license_to_discord)
        self.btn_login.clicked.connect(lambda: self._do_keyauth("login"))
        self.btn_reg.clicked.connect(lambda: self._do_keyauth("register"))

        if DISABLE_KEYAUTH:
            # Disable all login inputs entirely
            self.btn_login.setEnabled(False)
            self.btn_reg.setEnabled(False)
            self.user.setEnabled(False)
            self.passw.setEnabled(False)
            self.lic.setEnabled(False)
            self.discord_id.setEnabled(False)

            self.msg.setStyleSheet("color:#7bffa6; font-weight:700;")
            self.msg.setText("DEV MODE ENABLED — Auto Login")

            # Instantly notify GCV worker that login succeeded
            QTimer.singleShot(150, self._dev_bypass)
            return

    # ---------- Helpers ----------
    def _post_webhook(self, content: str):
        if not WEBHOOK_URL: return
        try:
            requests.post(WEBHOOK_URL, json={"content": content}, timeout=5)
        except: pass

    def ensure_session(self):
        if DISABLE_KEYAUTH:
            return "DEV_SESSION"
        try:
            payload = {
                "type": "init",
                "name": KEYAUTH_APP_NAME,
                "ownerid": KEYAUTH_OWNER_ID,
                "secret": KEYAUTH_SECRET,
                "version": KEYAUTH_VERSION
            }
            raw = http_post(KEYAUTH_URL, payload)
            j = json.loads(raw)
            if j.get("success"):
                return j.get("sessionid")
        except Exception:
            pass
        return None

    # ---------- Discord link (UI button on login page) ----------
    def link_license_to_discord(self):
        key = self.lic.text().strip()
        disc = self.discord_id.text().strip()

        if not key or not disc:
            self.link_msg.setText("❌ Enter license key + Discord ID")
            return

        try:
            r = requests.get(
                f"{VERIFY_API}/link_license",
                params={"key": key, "discord": disc},
                timeout=8
            )
            resp = r.json() if r.ok else {}
        except Exception as e:
            self.link_msg.setText(f"❌ Network error: {e}")
            return

        if resp.get("ok"):
            self.link_msg.setStyleSheet("color:#7bffa6; font-weight:700;")
            self.link_msg.setText("✅ Linked successfully")
            self._post_webhook(f"✅ License `{key}` linked to Discord `{disc}`")
        else:
            self.link_msg.setStyleSheet("color:#ff5f5f; font-weight:700;")
            self.link_msg.setText("❌ " + (resp.get("error") or "Link failed"))

    # ---------- Login / Register with KeyAuth, require Discord link ----------
    def _do_keyauth(self, mode):
        # DEV BUILD: skip KeyAuth entirely, just mark as logged in
        self.msg.setStyleSheet("color:#7bffa6; font-weight:700;")
        self.msg.setText("DEV BUILD: Logged in (KeyAuth skipped)")

        # Tell the host (GCVWorker) and flip to the main UI
        QTimer.singleShot(150, self._dev_bypass)

        # (normal KeyAuth code below if disable=False)

    def _dev_bypass(self):
        try:
            # Tell worker that login succeeded
            self.window().client.send({"type": "update", "logged_in": True})
            self.window().client.send({"type": "update", "tlabs_enabled": True})
        except:
            pass

        # Switch to main window
        QTimer.singleShot(50, self.on_authed)

class MainPage(QWidget):
    def __init__(self):
        super().__init__()

        self.tab_names = ["General", "Meter", "Icon - No Meter", "Skele - No Meter", "Misc", "Config", "Interface"]

        root = QHBoxLayout(self); root.setContentsMargins(8,8,8,8); root.setSpacing(8)

        self.sidebar = LeftNav(self.tab_names, self._on_nav_changed)
        root.addWidget(self.sidebar, 0)
        for b in self.sidebar._buttons:
            b.setEnabled(True)
        divider = QFrame()
        divider.setFixedWidth(1)
        divider.setStyleSheet(f"background:{THEME['divider']}; border:none;")
        root.addWidget(divider)

        right = QVBoxLayout(); right.setContentsMargins(0,0,0,0); right.setSpacing(8)
        root.addLayout(right, 1)

        header = QFrame(); header.setFixedHeight(44)
        header.setStyleSheet(f"QFrame{{background:{THEME['bg_panel']}; border:none; border-radius:10px;}}")
        hl = QHBoxLayout(header); hl.setContentsMargins(12,0,12,0)
        self.header_title = QLabel(self.tab_names[0]); self.header_title.setStyleSheet("font-weight:700;")
        hl.addWidget(self.header_title, alignment=Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignLeft)
        right.addWidget(header)

        self.pages = QStackedWidget()
        for t in self.tab_names:
            page = self.make_page(t)  
            self.pages.addWidget(page)
        right.addWidget(self.pages, 1)

        self.rainbow_accent_enabled = False
        self.rainbow_tabs_enabled = False
        self.rainbow_hue = 0
        self.rainbow_hue_tabs = 180
        self._rainbow_timer = QTimer(self)
        self._rainbow_timer.timeout.connect(self.update_rainbow_colors)
        self._rainbow_timer.start(100)

        QTimer.singleShot(0, lambda: self.sidebar.set_active(0))

    def update_rainbow_colors(self):
        changed = False
        if getattr(self, "rainbow_accent_enabled", False):
            self.rainbow_hue = (self.rainbow_hue + 2) % 360
            color = QColor.fromHsv(self.rainbow_hue, 255, 255).name()
            THEME["accent"] = color; THEME["accent_hover"] = color
            changed = True
        if getattr(self, "rainbow_tabs_enabled", False):
            self.rainbow_hue_tabs = (self.rainbow_hue_tabs + 3) % 360
            changed = True
        if changed: apply_theme(self.window())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "drag_pos"):
            self.window().move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if hasattr(self, "drag_pos"):
            self.drag_pos = None
            event.accept()

    def make_page(self, name):
        wrapper = QWidget()
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        page = QWidget(); grid = QGridLayout(page); grid.setSpacing(10)
        scroll.setWidget(page)
        box = QVBoxLayout(wrapper); box.addWidget(scroll)

        if name == "General":
            from PyQt6.QtWidgets import QComboBox, QLineEdit
            def _lock_feature_checks():
                for c in getattr(self, "_feature_checks", []):
                    try:
                        c.setEnabled(False)
                    except Exception:
                        pass

            def _unlock_feature_checks():
                for c in getattr(self, "_feature_checks", []):
                    try:
                        c.setEnabled(True)
                    except Exception:
                        pass

            p = Panel("Account Info")
            v = p.body
            v.setSpacing(10)

            self.err_label = QLabel("Error: Subscription Expired")
            self.err_label.setStyleSheet("color:#ff5f5f; font-weight:700; margin-bottom:4px;")
            v.addWidget(self.err_label)

            account_card = QFrame()
            account_card.setStyleSheet("background:#141419; border-radius:8px;")
            account_layout = QHBoxLayout(account_card)
            account_layout.setContentsMargins(10, 8, 10, 8)
            account_layout.setSpacing(8)

            acc_label = QLabel("Account ID")
            acc_label.setStyleSheet("font-weight:600; color:#ccc;")
            account_layout.addWidget(acc_label)

            self.account_id = QLineEdit("775985522706612235")
            self.account_id.setReadOnly(True)
            self.account_id.setFixedHeight(28)
            account_layout.addWidget(self.account_id, 1)

            self.readme_btn = QPushButton("📘 Read Me")
            self.readme_btn.setFixedWidth(90)
            self.readme_btn.setFixedHeight(28)
            self.readme_btn.setStyleSheet(f"""
                QPushButton {{
                    background:{THEME['chip_bg']};
                    border:1px solid {THEME['chip_border']};
                    border-radius:6px;
                    color:{THEME['text']};
                }}
                QPushButton:hover {{
                    background:{THEME['accent_hover']};
                    color:#fff;
                }}
            """)
            account_layout.addWidget(self.readme_btn)

            title = QLabel("Activation (Enable)")
            title.setStyleSheet("font-weight:600; color:#ccc;")
            v.addWidget(title)

            activation_card = QFrame()
            activation_card.setStyleSheet("background:#141419; border-radius:8px;")
            act_layout = QHBoxLayout(activation_card)
            act_layout.setContentsMargins(10, 6, 10, 6)
            act_layout.setSpacing(18)
            v.addWidget(activation_card)

            self.chk_skele = QCheckBox("Skele")
            self.chk_icon = QCheckBox("Icon")
            self.chk_meter = QCheckBox("Meter")
            self.chk_creative = QCheckBox("Creative")

            for c in [self.chk_skele, self.chk_icon, self.chk_meter, self.chk_creative]:
                c.setStyleSheet("font-weight:500; color:#ccc; font-size:13px;")
                act_layout.addWidget(c)

            self._feature_checks = [self.chk_skele, self.chk_icon, self.chk_meter, self.chk_creative]
            mode_label = QLabel("Mode")
            mode_label.setStyleSheet("font-weight:600; color:#ccc;")
            act_layout.addWidget(mode_label)

            self.mode_combo = QComboBox()
            self.mode_combo.addItems(["Online", "Offline"])
            self.mode_combo.setFixedWidth(120)
            self.mode_combo.setStyleSheet(f"""
                QComboBox {{
                    background:#0f0f14;
                    border:1px solid {THEME['chip_border']};
                    border-radius:6px;
                    color:{THEME['text']};
                    padding:4px;
                }}
                QComboBox:hover {{
                    border:1px solid {THEME['accent']};
                }}
            """)
            def mode_changed(text):
                self.window().client.send({"type": "update", "mode": text})
            self.mode_combo.currentTextChanged.connect(mode_changed)
            act_layout.addWidget(self.mode_combo)
            act_layout.addStretch()

            def toggle_meter():
                en = self.chk_meter.isChecked()
                self.window().client.send({"type":"update", "tlabs_enabled": en})
                if en:
                    try:
                        mr = {
                            "x": self.window().main.sl_x.value(),
                            "y": self.window().main.sl_y.value(),
                            "w": self.window().main.sl_w.value(),
                            "h": self.window().main.sl_h.value()
                        }
                        self.window().client.send({"type":"update", "meter_region": mr})
                        pass
                    except Exception as e:
                        pass

            self.chk_meter.stateChanged.connect(toggle_meter)

            v.addStretch()
            grid.addWidget(p, 0, 0, 1, 2)
            return wrapper

        if name == "Misc":
            p = Panel("Miscellaneous"); v = p.body
            save_btn = QPushButton("💾 Save Settings"); logout_btn = QPushButton("🚪 Logout")
            for b, color, hover in [(save_btn, "#00BFFF", "#1E90FF"), (logout_btn, "#ff5f5f", "#ff7878")]:
                b.setFixedHeight(36)
                b.setStyleSheet(f"""
                    QPushButton {{
                        background:{THEME['chip_bg']};
                        border:1px solid {color};
                        border-radius:8px;
                        color:{THEME['text']};
                        font-weight:600;
                        padding:4px;
                    }}
                    QPushButton:hover {{
                        background:{hover};
                        color:#fff;
                    }}
                """); v.addWidget(b)
            def save_settings():
                try:
                    sp = os.path.join(os.getenv("APPDATA") or tempfile.gettempdir(), "TitanLabs")
                    os.makedirs(sp, exist_ok=True)
                    fp = os.path.join(sp, "ui_settings.json")
                    data = {
                        "accent": THEME.get("accent"),
                        "accent_hover": THEME.get("accent_hover"),
                        "tab_selected_bg": THEME.get("accent"),  # using accent
                        "rainbow_accent_enabled": getattr(self, "rainbow_accent_enabled", False),
                        "rainbow_tabs_enabled": getattr(self, "rainbow_tabs_enabled", False),
                    }
                    with open(fp, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
                    msg = QLabel("✅ Settings saved to ui_settings.json"); msg.setStyleSheet("color:#7bffa6; font-weight:600;"); v.addWidget(msg)
                except Exception as e:
                    msg = QLabel(f"❌ Save failed: {e}"); msg.setStyleSheet("color:#ff5f5f; font-weight:600;"); v.addWidget(msg)
            def do_logout():
                from PyQt6.QtWidgets import QMessageBox
                confirm = QMessageBox.question(self, "Confirm Logout", "Log out?")
                if confirm == QMessageBox.StandardButton.Yes:
                    try: self.window().client.send({"type":"update","logged_in":False})
                    except Exception: pass
                    self.window().stack.setCurrentWidget(self.window().auth)
                    self.window().setFixedSize(440, self.window().auth.sizeHint().height())
            save_btn.clicked.connect(save_settings); logout_btn.clicked.connect(do_logout)
            grid.addWidget(p, 0, 0, 1, 2); return wrapper

        if name == "Meter":
            p = Panel("Meter Region")
            v = p.body
            v.setSpacing(12)

            from PyQt6.QtWidgets import QSlider

            card = QFrame()
            card.setStyleSheet("background:#121218; border-radius:10px;")
            v.addWidget(card)

            def make_slider(label_text, default, minv, maxv):
                lay = QVBoxLayout()
                lbl = QLabel(f"{label_text}: {default}")
                lbl.setStyleSheet("color:#ccc; font-size:12px; font-weight:600; margin-bottom:4px;")
                s = QSlider(Qt.Orientation.Horizontal)
                s.setRange(minv, maxv)
                s.setValue(default)
                s.setSingleStep(1)
                s.setStyleSheet(f"""
                    QSlider::groove:horizontal {{
                        height:6px; border-radius:3px; background:#2a2a33;
                    }}
                    QSlider::handle:horizontal {{
                        background:{THEME['accent']};
                        width:14px; height:14px; border-radius:7px; margin:-4px 0;
                    }}
                    QSlider::sub-page:horizontal {{
                        background:{THEME['accent']}; border-radius:3px;
                    }}
                """)
                def on_change(v): lbl.setText(f"{label_text}: {v}")
                s.valueChanged.connect(on_change)
                lay.addWidget(lbl)
                lay.addWidget(s)
                return lay, s

            card_lay = QVBoxLayout(card)
            card_lay.setContentsMargins(12,12,12,12)
            card_lay.setSpacing(10)

            pos_lbl = QLabel("Position & Size")
            pos_lbl.setStyleSheet("color:#a9acbf; font-weight:600; margin-bottom:4px;")
            card_lay.addWidget(pos_lbl)

            h1 = QHBoxLayout()
            x_block, self.sl_x = make_slider("Horizontal", 21, 0, 4096)
            y_block, self.sl_y = make_slider("Vertical", 226, 0, 4096)
            h1.addLayout(x_block); h1.addSpacing(10); h1.addLayout(y_block)
            card_lay.addLayout(h1)

            h2 = QHBoxLayout()
            w_block, self.sl_w = make_slider("Width", 1886, 1, 4096)
            h_block, self.sl_h = make_slider("Height", 539, 1, 4096)
            h2.addLayout(w_block); h2.addSpacing(10); h2.addLayout(h_block)
            card_lay.addLayout(h2)

            # Meter settings card 
            card2 = QFrame()
            card2.setStyleSheet("background:#121218; border-radius:10px;")
            v.addWidget(card2)

            card2_lay = QVBoxLayout(card2)
            card2_lay.setContentsMargins(12,12,12,12)
            card2_lay.setSpacing(10)

            thresh_lbl = QLabel("Meter Settings")

            # === Meter Color Picker ===
            from PyQt6.QtWidgets import QColorDialog
            btn_color = QPushButton("Pick Meter Color")
            btn_color.setFixedHeight(32)
            card2_lay.addWidget(btn_color)

            def choose_meter_color():
                col = QColorDialog.getColor()
                if col.isValid():
                    # send BGR not RGB
                    bgr = [col.blue(), col.green(), col.red()]
                    self.window().client.send({"type": "update", "meter_color": bgr})

            btn_color.clicked.connect(choose_meter_color)

            thresh_lbl.setStyleSheet("color:#a9acbf; font-weight:600; margin-bottom:4px;")
            card2_lay.addWidget(thresh_lbl)

            # Shot % slider 
            fill_block, self.sl_fill = make_slider("Green Release", 100, 1, 100)
            card2_lay.addLayout(fill_block)

            def _push_fill_threshold():
                fill_pct = self.sl_fill.value()
                self.window().client.send({"type":"update","meter_fill_threshold":fill_pct})

            self.sl_fill.valueChanged.connect(_push_fill_threshold)

            # Tempo Duration input 
            tempo_row = QHBoxLayout()
            tempo_lbl = QLabel("Tempo Duration:")
            tempo_lbl.setStyleSheet("color:#ccc; font-size:12px; font-weight:600;")
            tempo_row.addWidget(tempo_lbl)

            from PyQt6.QtWidgets import QLineEdit
            self.tempo_entry = QLineEdit("50")
            self.tempo_entry.setPlaceholderText("ms")
            self.tempo_entry.setFixedWidth(60)
            self.tempo_entry.setStyleSheet("""
                QLineEdit {
                    background:#0f0f14;
                    border:1px solid #2B2C37;
                    border-radius:6px;
                    padding:4px 6px;
                    color:#ededf7;
                }
            """)
            tempo_row.addWidget(self.tempo_entry)

            tempo_up = QPushButton("▲")
            tempo_up.setFixedSize(28, 28)
            tempo_down = QPushButton("▼")
            tempo_down.setFixedSize(28, 28)

            def tempo_up_click():
                try:
                    val = int(self.tempo_entry.text())
                    val = min(255, val + 1)
                    self.tempo_entry.setText(str(val))
                except: pass

            def tempo_down_click():
                try:
                    val = int(self.tempo_entry.text())
                    val = max(0, val - 1)
                    self.tempo_entry.setText(str(val))
                except: pass

            def tempo_changed(text):
                try:
                    val = int(text) if text.strip() else 50
                    val = max(0, min(255, val))
                    self.window().client.send({"type":"update","tempo_duration":val})
                except: pass

            tempo_up.clicked.connect(tempo_up_click)
            tempo_down.clicked.connect(tempo_down_click)
            self.tempo_entry.textChanged.connect(tempo_changed)

            tempo_row.addWidget(tempo_up)
            tempo_row.addWidget(tempo_down)
            tempo_row.addStretch()
            card2_lay.addLayout(tempo_row)

            # Send initial values
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, _push_fill_threshold)
            QTimer.singleShot(100, lambda: tempo_changed(self.tempo_entry.text()))

            self.btn_bbox = QPushButton("Hide Bounding Box")
            self.btn_bbox.setObjectName("danger")
            self.btn_bbox.setCheckable(True)
            self.btn_bbox.setChecked(True)
            self.btn_bbox.setFixedHeight(34)
            v.addWidget(self.btn_bbox)

            v.addStretch()

            def _push_settings():
                mr = {"x":self.sl_x.value(),"y":self.sl_y.value(),
                    "w":self.sl_w.value(),"h":self.sl_h.value()}
                self.window().client.send({"type":"update","meter_region":mr})

            for w in [self.sl_x,self.sl_y,self.sl_w,self.sl_h]:
                w.valueChanged.connect(_push_settings)

            def _toggle_bbox():
                show = not self.btn_bbox.isChecked()
                self.btn_bbox.setText("Hide Bounding Box" if show else "Show Bounding Box")
                self.window().client.send({"type":"update","show_bbox":show})
            self.btn_bbox.clicked.connect(_toggle_bbox)

            grid.addWidget(p,0,0,1,2)
            return wrapper

        if name == "Interface":
            p = Panel("Theme Customization"); v = p.body
            pick = QPushButton("Pick Accent Color"); pick.setFixedHeight(32); v.addWidget(pick)
            def choose_color():
                col = QColorDialog.getColor()
                if col.isValid():
                    hex_color = col.name(); THEME["accent"] = hex_color; THEME["accent_hover"] = hex_color; apply_theme(self.window())
            pick.clicked.connect(choose_color)

            self.rainbow_accent_enabled = False; self.rainbow_tabs_enabled = False
            self.rainbow_hue = 0; self.rainbow_hue_tabs = 180
            btn_rainbow_accent = QPushButton("🌈 Accent Rainbow: OFF"); btn_rainbow_accent.setFixedHeight(32); v.addWidget(btn_rainbow_accent)
            btn_rainbow_tabs = QPushButton("🌈 Tab Rainbow: OFF"); btn_rainbow_tabs.setFixedHeight(32); v.addWidget(btn_rainbow_tabs)
            def toggle_accent_rainbow():
                self.rainbow_accent_enabled = not self.rainbow_accent_enabled
                btn_rainbow_accent.setText("🌈 Accent Rainbow: ON" if self.rainbow_accent_enabled else "🌈 Accent Rainbow: OFF")
            def toggle_tabs_rainbow():
                self.rainbow_tabs_enabled = not self.rainbow_tabs_enabled
                btn_rainbow_tabs.setText("🌈 Tab Rainbow: ON" if self.rainbow_tabs_enabled else "🌈 Tab Rainbow: OFF")
            btn_rainbow_accent.clicked.connect(toggle_accent_rainbow); btn_rainbow_tabs.clicked.connect(toggle_tabs_rainbow)
            v.addStretch(); grid.addWidget(p,0,0,1,2); return wrapper

        p = Panel(name); p.body.addWidget(QLabel("GitHub Upload - YOU DONT HAVE THIS - METER ONLY!")); p.body.addStretch()
        grid.addWidget(p,0,0,1,2); return wrapper

    def _on_nav_changed(self, idx: int):
        self.pages.setCurrentIndex(idx)
        self.header_title.setText(self.tab_names[idx])

class Shell(QWidget):
    def __init__(self, host, port):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.client = HostClient(host, port); self.client.start()

        self.stack = QStackedWidget(self)
        lay = QVBoxLayout(self); lay.setSpacing(0); lay.setContentsMargins(0,0,0,0); lay.addWidget(self.stack)
        self.stack.setContentsMargins(0,0,0,0)

        self.auth = AuthPage(self._on_authed)
        self.main = MainPage()
        self.stack.addWidget(self.auth); self.stack.addWidget(self.main)
        self.stack.setCurrentWidget(self.auth)

        self.adjustSize(); self.setFixedWidth(460); self.setFixedHeight(self.sizeHint().height())

        try:
            sp = os.path.join(os.getenv("APPDATA") or tempfile.gettempdir(), "TitanLabs")
            fp = os.path.join(sp, "ui_settings.json")
            if os.path.exists(fp):
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if "accent" in data: THEME["accent"] = data["accent"]
                        if "accent_hover" in data: THEME["accent_hover"] = data["accent_hover"]
                        if "rainbow_accent_enabled" in data: self.main.rainbow_accent_enabled = bool(data["rainbow_accent_enabled"])
                        if "rainbow_tabs_enabled" in data: self.main.rainbow_tabs_enabled = bool(data["rainbow_tabs_enabled"])
        except Exception as e:
            pass

        apply_theme(self)
        self.keep = QTimer(self); self.keep.timeout.connect(lambda: None); self.keep.start(25)
        self.show()

    def _on_authed(self):
        self.setMinimumSize(820, 520)
        self.resize(900, 560)
        self.stack.setCurrentWidget(self.main)

    def paintEvent(self, event):
        super().paintEvent(event)
        from PyQt6.QtGui import QPainter, QPen
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(THEME['accent'])); pen.setWidth(3); p.setPen(pen)
        rect = self.stack.geometry().adjusted(1,1,-1,-1); p.drawRoundedRect(rect, 12, 12)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "drag_pos"):
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def closeEvent(self, event):
        try:
            self.client.send({"type":"shutdown"})
        except Exception:
            pass
        event.accept()

def main():
    if len(sys.argv) < 2: sys.exit(1)
    port = int(sys.argv[1])
    app = QApplication(sys.argv[:1])
    app.setApplicationName("Titan Labs"); app.setOrganizationName("Titan Labs"); app.setApplicationDisplayName("Titan Labs")
    ui = Shell("127.0.0.1", port); ui.setWindowTitle("Titan Labs")

    try:
        url = ("https://cdn.discordapp.com/attachments/1372493411923394692/"
               "1433287341681803465/istockphoto-1436070801-612x612.png?ex=6904245b&is=6902d2db&hm=2485b29ea138c7a2163a53d0efc0db1ee99e87a5b3ca9d1b21743db6ff0b1bf1&")
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=6).read()
        pix = QPixmap(); pix.loadFromData(data); icon = QIcon(pix)
        ui.setWindowIcon(icon); app.setWindowIcon(icon)
    except Exception as e:
        pass

    ui.show(); sys.exit(app.exec())

if __name__ == "__main__":
    sys.excepthook = lambda *exc: None
    main()
'''
    tmp_dir = tempfile.gettempdir()
    gui_path = os.path.join(tmp_dir, "gtuner_ext_gui.py")
    with open(gui_path, "w", encoding="utf-8") as f:
        f.write(gui_code)

    python_exe = sys.executable or "python"
    if python_exe.lower().endswith("python.exe"):
        pythonw = python_exe[:-4] + "w.exe"
        if os.path.exists(pythonw):
            python_exe = pythonw

    os.environ["TL_LOGO_PATH"] = TL_LOGO_PATH
    os.environ["TL_FULL_LOGO_PATH"] = TL_FULL_LOGO_PATH
    os.environ["VERIFY_API"] = VERIFY_API

    proc = subprocess.Popen([python_exe, gui_path, str(port)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return proc

ENABLED_SHOTS = ["square", "tempo"]  # Both shot types enabled

class GCVWorker:
    def __init__(self, width, height):
        self.server = JSONServer()
        self.meter_cycle = MeterCycle(max_meter_px=MAX_METER_PX)
        self.server.start()
        self.gui_launched = False
        self.gui_process = None

        
        self.last_shot_time = 0
        self.last_square_shot_time = 0
        self.last_tempo_shot_time = 0

        
        self._init_pulse()

    def _init_pulse(self):
        self._pulse_until_ms = 0.0
        self._pulse_ms = 100.0
        self._current_shot_type = "square"
        self._check_counter = 0

    def _start_pulse(self, shot_type="square"):
        global _TEMPO_DURATION
        if shot_type == "tempo":
            self._pulse_ms = float(_TEMPO_DURATION)
        else:
            self._pulse_ms = 100.0

        self._pulse_until_ms = time.time() * 1000.0 + self._pulse_ms
        self._current_shot_type = shot_type

    def _service_output(self, out_bytes):
        now = time.time() * 1000.0
        if now < self._pulse_until_ms:
            if self._current_shot_type == "square":
                out_bytes[0] = 1
                out_bytes[1] = 1
            elif self._current_shot_type == "tempo":
                out_bytes[0] = 0
                out_bytes[1] = 1
            else:
                out_bytes[0] = 0
                out_bytes[1] = 0
        else:
            out_bytes[0] = 0
            out_bytes[1] = 0

        global _TEMPO_DURATION
        out_bytes[3] = _TEMPO_DURATION

    def cleanup(self):
        """Cleanup GUI process and server on exit"""
        try:
            if self.gui_process and self.gui_process.poll() is None:
                pid = self.gui_process.pid
                self.gui_process.terminate()
                try:
                    self.gui_process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.gui_process.kill()
                    try:
                        self.gui_process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        # Last resort on Windows - use taskkill
                        if sys.platform == "win32":
                            subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
        except Exception as e:
            pass

        try:
            if self.server:
                self.server.stop()
        except Exception as e:
            pass

    def process(self, frame):
        self._check_counter += 1
        if self._check_counter % 100 == 0:
            _runtime_check()

        global LOGGED_IN
        if not self.gui_launched:
            self.gui_process = launch_external_gui(self.server.port)
            self.gui_launched = True

        out_bytes = bytearray(7); out_bytes[:] = [0] * 7

        if not LOGGED_IN:
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = "NOT AUTHORIZED"
            (tw, th), _ = cv2.getTextSize(text, font, 4, 6)
            cx = (frame.shape[1] // 2) - (tw // 2)
            cy = (frame.shape[0] // 2) + (th // 2)
            cv2.putText(frame, text, (cx, cy), font, 4, (0, 0, 0), 10)
            cv2.putText(frame, text, (cx, cy), font, 4, (0, 0, 255), 6)
            return frame, out_bytes

        global MODE
        text = f"Mode: {MODE}"
        font = cv2.FONT_HERSHEY_DUPLEX
        scale, color, thickness = 0.7, (255, 255, 0), 2
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        H, W = frame.shape[:2]; cx = W // 2
        x1, y1 = cx - tw // 2 - 10, 5; x2, y2 = cx + tw // 2 + 10, y1 + th + 12
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
        cv2.putText(frame, text, (cx - tw // 2, y2 - 6), font, scale, color, thickness, cv2.LINE_AA)

        version = "1.0"
        text = f"TitanLabs {version}"
        font = cv2.FONT_HERSHEY_TRIPLEX
        scale, color, thickness = 0.6, (255, 255, 0), 1
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        H, W = frame.shape[:2]; x, y = W - tw - 10, H - 10
        cv2.putText(frame, text, (x + 1, y + 1), font, scale, (0, 0, 0), thickness + 1, cv2.LINE_AA)
        cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)

        if not TITANLABS_ENABLED:
            return frame, out_bytes

        H, W = frame.shape[:2]

        if TITANLABS_ENABLED:
            x, y, w, h = METER_REGION["x"], METER_REGION["y"], METER_REGION["w"], METER_REGION["h"]
            x = max(0, min(W - 1, x)); y = max(0, min(H - 1, y))
            w = max(1, min(W - x, w)); h = max(1, min(H - y, h))
            roi = frame[y:y+h, x:x+w]

            # Multi-range color detection for better accuracy
            # ---- Universal Color Detection (based on user choice) ----
            b, g, r = USER_METER_COLOR

            tol = 40  # tolerance range for detection
            lower = np.array([max(0, b - tol), max(0, g - tol), max(0, r - tol)], dtype=np.uint8)
            upper = np.array([min(255, b + tol), min(255, g + tol), min(255, r + tol)], dtype=np.uint8)

            mask_color = cv2.inRange(roi, lower, upper)
            mask_color = cv2.morphologyEx(mask_color, cv2.MORPH_CLOSE, MORPH_KERNEL, iterations=1)

            if SHOW_BBOX:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255,255,0), 1)

            # Raw pixel measurement - NO processing
            pixels = cv2.findNonZero(mask_color)

            if pixels is not None and len(pixels) > 0:

                y_coords = pixels[:, 0, 1]
                x_coords = pixels[:, 0, 0]

                top_of_pixels = int(np.min(y_coords))
                bottom_of_pixels = int(np.max(y_coords))
                left = int(np.min(x_coords))
                right = int(np.max(x_coords))

                distance = bottom_of_pixels - top_of_pixels

                global _METER_THRESHOLD_PIXEL
                trigger_pixel = _METER_THRESHOLD_PIXEL

                now = time.time()
                action, total_fill = self.meter_cycle.update(distance, trigger_pixel)

                if action == "fire" and ((now - self.last_shot_time) > 0.15):
                    shot_fired = False

                    if "square" in ENABLED_SHOTS and (now - self.last_square_shot_time) > 0.10:
                        self._start_pulse("square")
                        self.last_square_shot_time = now
                        self.last_shot_time = now

                        if "gcv_ready" in globals() and gcv_ready():
                            if "gcv_write" in globals():
                                gcv_write(0, 1)
                                gcv_write(1, 1)
                                gcv_write(3, _TEMPO_DURATION)
                        shot_fired = True

                    elif "tempo" in ENABLED_SHOTS and (now - self.last_tempo_shot_time) > 0.10:
                        self._start_pulse("tempo")
                        self.last_tempo_shot_time = now
                        self.last_shot_time = now

                        if "gcv_ready" in globals() and gcv_ready():
                            if "gcv_write" in globals():
                                gcv_write(0, 0)
                                gcv_write(1, 1)
                                gcv_write(3, _TEMPO_DURATION)
                        shot_fired = True

                    if shot_fired:
                        color = (0, 255, 0)
                    else:
                        color = (0, 255, 255)

                elif distance >= trigger_pixel * 0.8:
                    color = (0, 255, 255)
                else:
                    color = (255, 0, 255)

                self._service_output(out_bytes)

                # ✅ STATIC BOX FOLLOWING METER POSITION (NOT FILL HEIGHT)
                if SHOW_BBOX:

                    # Stable horizontal anchor = meter center
                    meter_center_x = x + int((left + right) / 2)

                    # Stable vertical anchor = bottom of meter (fill grows upward)
                    meter_baseline_y = y + bottom_of_pixels

                    # Static box size
                    box_width = 60
                    box_height = 220

                    # Build rectangle
                    x1 = meter_center_x - box_width // 2
                    y1 = meter_baseline_y - box_height
                    x2 = meter_center_x + box_width // 2
                    y2 = meter_baseline_y

                    # Draw outline
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255,255,0), 1)

            else:
                self._service_output(out_bytes)

        return frame, out_bytes

if '_WORKER_INSTANCE' not in globals() or _WORKER_INSTANCE is None:
    worker = GCVWorker(1920, 1080)
    _WORKER_INSTANCE = worker
    
    atexit.register(worker.cleanup)
else:
    worker = _WORKER_INSTANCE


def signal_handler(sig, frame):
    worker.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def process_frame(frame):
    global _WORKER_INSTANCE
    frame, out_bytes = _WORKER_INSTANCE.process(frame)
    if gcv_ready():
        
        gcv_write(0, out_bytes[0])
        gcv_write(1, out_bytes[1])
        
        for i in range(2, len(out_bytes)):
            gcv_write(i, out_bytes[i])
    return frame
