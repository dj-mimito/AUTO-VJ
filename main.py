# -*- coding: utf-8 -*-
"""
==============================================================================
VDJ BILI VISUAL PRO MAX - THE ULTIMATE NATIVE VJ ENGINE (ARENA EDITION V6)
Version: 600.0.3 (Deep Rhythm Matrix - HW Accel Import Fixed)
==============================================================================
"""

import sys
import os
import time
import glob
import json
import threading
import subprocess
import requests
import re
import traceback
import http.server
import socketserver
import math
import random
from enum import Enum
from datetime import datetime
from urllib.parse import quote, unquote

# ============================================================================
# [核心修复] - 全局异常接管机制
# ============================================================================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_report.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] CRITICAL CRASH:\n{error_msg}\n{'-'*60}\n")
    print(f"\033[91mFatal Error:\n{error_msg}\033[0m", file=sys.stderr)
    
    if QApplication.instance():
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("致命崩溃拦截 (Fatal Crash Guard)")
        msg.setText("系统发生严重错误，但已成功拦截闪退！\n详细信息已写入 crash_report.log")
        msg.setDetailedText(error_msg)
        msg.exec()

sys.excepthook = global_exception_handler

import ssl
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

# ============================================================================
# [PyQt6 Imports]
# ============================================================================
from PyQt6.QtCore import (Qt, pyqtSignal, QThread, QObject, QUrl, QCoreApplication, 
                          QTimer, QSizeF, QRectF, QPointF, QPropertyAnimation, QEasingCurve)
from PyQt6.QtGui import (QPixmap, QColor, QPainter, QPainterPath, QImage, QFont, QFontDatabase,
                         QKeySequence, QShortcut, QBrush, QTransform, QPen)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QPushButton, QLineEdit, QFileDialog,
                             QFrame, QButtonGroup, QPlainTextEdit, QGroupBox, QGridLayout, 
                             QSlider, QMessageBox, QCheckBox, QRadioButton,
                             QGraphicsView, QGraphicsScene, QGraphicsTextItem, 
                             QGraphicsRectItem, QGraphicsDropShadowEffect, QGraphicsColorizeEffect,
                             QTabWidget, QScrollArea, QGraphicsItemGroup, QGraphicsProxyWidget, QGraphicsPixmapItem)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem

# [核心修复]：模块名应为 QtOpenGLWidgets (带s)
try:
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget 
except ImportError:
    # 兼容性兜底，某些精简版 PyQt 可能不包含此模块
    print("WARNING: PyQt6.QtOpenGLWidgets not found. Hardware acceleration might be limited.")
    QOpenGLWidget = QWidget

# ============================================================================
# [Web Automation Imports]
# ============================================================================
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    import yt_dlp
except ImportError:
    print("CRITICAL ERROR: 缺少核心依赖，请运行: pip install selenium undetected-chromedriver yt-dlp requests PyQt6")
    sys.exit(1)

# ============================================================================
# [Constants & Configuration]
# ============================================================================
APP_NAME = "VDJ Visual Pro Max - Arena Edition"
VERSION = "600.0.3 (Deep Rhythm Matrix)"

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    try: BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    except NameError: BASE_DIR = os.path.abspath(os.getcwd())

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
APP_CONFIG = {
    "vdj_path": os.path.expanduser("~/Documents/VirtualDJ"), 
    "vdj_port": "80"
}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            APP_CONFIG.update(json.load(f))
    except: pass

def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(APP_CONFIG, f, indent=4)

CACHE_DIR = os.path.join(BASE_DIR, "video_cache")
VJ1_MATERIAL_DIR = os.path.join(BASE_DIR, "vj_materials_vj1")
VJ2_MATERIAL_DIR = os.path.join(BASE_DIR, "vj_materials_vj2")
STATIC_COOKIE_FILE = os.path.join(BASE_DIR, "cookies.txt")
DRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")

PROFILE_DIR_MAIN = os.path.join(BASE_DIR, "profile_main")
PROFILE_DIR_VJ1 = os.path.join(BASE_DIR, "profile_vj1")
PROFILE_DIR_VJ2 = os.path.join(BASE_DIR, "profile_vj2")

for d in [CACHE_DIR, VJ1_MATERIAL_DIR, VJ2_MATERIAL_DIR, PROFILE_DIR_MAIN, PROFILE_DIR_VJ1, PROFILE_DIR_VJ2]:
    os.makedirs(d, exist_ok=True)

if not os.path.exists(STATIC_COOKIE_FILE):
    with open(STATIC_COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")

C_BG, C_PANEL, C_ACCENT_1, C_ACCENT_2, C_TEXT, C_BORDER = "#050505", "#121212", "#FF0055", "#00F0FF", "#F0F0F0", "#2A2A2A"

STYLESHEET = f"""
    QMainWindow {{ background-color: {C_BG}; }}
    QWidget {{ font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; color: {C_TEXT}; }}
    QFrame#Panel {{ background-color: {C_PANEL}; border-radius: 12px; border: 1px solid {C_BORDER}; }}
    QLabel#Title {{ font-size: 30px; font-weight: 900; color: {C_ACCENT_1}; letter-spacing: 2px; text-transform: uppercase; }}
    QLabel#SongTitle {{ font-size: 22px; font-weight: bold; color: #FFF; }}
    QLabel#GenreLabel {{ font-size: 14px; font-weight: bold; color: #111; background: {C_ACCENT_2}; padding: 4px 8px; border-radius: 6px; }}
    QLabel#VibeLabel {{ font-size: 14px; font-weight: bold; color: #FFF; background: #E91E63; padding: 4px 8px; border-radius: 6px; }}
    QLineEdit {{ background-color: #1A1A1A; border: 1px solid #444; border-radius: 6px; padding: 10px; color: white; font-size: 14px; }}
    QLineEdit:focus {{ border: 1px solid {C_ACCENT_2}; background-color: #222; }}
    QPushButton {{ background-color: #252525; border: 1px solid #444; border-radius: 6px; padding: 8px 16px; font-weight: bold; font-size: 13px; color: #EEE; }}
    QPushButton:hover {{ background-color: #383838; border-color: {C_ACCENT_2}; color: {C_ACCENT_2}; }}
    QPushButton:pressed {{ background-color: {C_ACCENT_1}; color: #000; }}
    QPushButton:checked {{ background-color: {C_ACCENT_2}; color: #000; border: none; }}
    QGroupBox {{ border: 2px solid {C_BORDER}; border-radius: 8px; margin-top: 15px; font-weight: bold; color: #FFF; background-color: #0A0A0A; }}
    QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; color: {C_ACCENT_2}; font-size: 13px; letter-spacing: 1px; }}
    QPlainTextEdit {{ background-color: #000; color: #00FF00; font-family: 'Consolas'; border-radius: 6px; padding: 8px; font-size: 12px; border: 1px solid #111; }}
    QSlider::groove:horizontal {{ border: 1px solid #333; height: 6px; background: #111; border-radius: 3px; }}
    QSlider::handle:horizontal {{ background: {C_ACCENT_2}; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }}
    QSlider::groove:vertical {{ border: 1px solid #333; width: 6px; background: #111; border-radius: 3px; }}
    QSlider::handle:vertical {{ background: {C_ACCENT_2}; height: 16px; width: 16px; margin: 0 -5px; border-radius: 8px; }}
    QCheckBox {{ font-weight: bold; font-size: 13px; color: #CCC; }}
    QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 2px solid #555; background-color: #1A1A1A; }}
    QCheckBox::indicator:checked {{ background-color: {C_ACCENT_2}; border-color: {C_ACCENT_2}; }}
    QTabWidget::pane {{ border: 1px solid {C_BORDER}; border-radius: 8px; background: {C_PANEL}; }}
    QTabBar::tab {{ background: #1A1A1A; color: #777; padding: 10px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: bold; margin-right: 2px; }}
    QTabBar::tab:selected {{ background: {C_PANEL}; color: {C_ACCENT_2}; border-bottom: 3px solid {C_ACCENT_2}; }}
"""

# ============================================================================
# [Utility & Helper Class]
# ============================================================================
class VJHelper:
    @staticmethod
    def safe_float(val_str, default=0.0):
        try:
            val = float(val_str)
            return default if math.isnan(val) or math.isinf(val) else val
        except Exception: return default

    @staticmethod
    def parse_vdj_time_to_ms(val_str):
        if not isinstance(val_str, str): return None
        val = val_str.strip().replace('+', '')
        if not val or "error" in val.lower() or val.lower() == "nan": return None
        sign = -1 if val.startswith('-') else 1
        val = val.replace('-', '')
        if ':' in val:
            parts = val.split(':')
            try:
                if len(parts) == 3: return sign * (int(parts[0]) * 3600 + int(parts[1]) * 60 + VJHelper.safe_float(parts[2])) * 1000.0
                if len(parts) == 2: return sign * (int(parts[0]) * 60 + VJHelper.safe_float(parts[1])) * 1000.0
            except Exception: return None
        try:
            num = float(val)
            if math.isnan(num) or math.isinf(num): return None
            return sign * (num if num > 10000 else num * 1000.0)
        except Exception: return None

    @staticmethod
    def parse_views_count(text):
        if not text: return 0.0
        text = text.replace('播放', '').strip()
        multiplier = 1.0
        if '万' in text: multiplier, text = 10000.0, text.replace('万', '')
        elif '亿' in text: multiplier, text = 100000000.0, text.replace('亿', '')
        try: return float(text) * multiplier
        except Exception: return 0.0

    @staticmethod
    def sanitize_filename(name):
        if not isinstance(name, str): name = str(name)
        return re.sub(r'[\\/*?:"<>|]', "", name).strip()

    @staticmethod
    def clean_text_for_match(text):
        if not isinstance(text, str): return ""
        text = re.sub(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}|\<[^>]*\>|（[^）]*）|【[^】]*】|《[^》]*》', ' ', text)
        text = re.sub(r'[^\w\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', ' ', text)
        return ' '.join(text.lower().split())

    @staticmethod
    def lerp(a, b, t):
        return a + (b - a) * t

# ============================================================================
# [AI Genre & Vibe Engine]
# ============================================================================
class MusicGenre(Enum):
    EDM = "EDM / Big Room"      
    ANISONG = "Anisong / Hardcore"  
    HOUSE = "House / Tech"          
    TRANCE = "Trance / Progressive" 
    DUBSTEP = "Dubstep / Bass"      
    GARAGE = "Garage / UK Bass"     
    POP = "Pop / Vocal"             
    UNKNOWN = "Unknown / Freeform"

class EnergyVibe(Enum):
    CHILL = "Chill / Intro"         
    ACTIVE = "Active / Verse"       
    BUILDUP = "Build-Up / Rising"   
    DROP = "DROP / PEAK"            
    OUTRO = "Outro / Fade"

def analyze_genre(title, artist):
    text = (title + " " + artist).lower()
    if any(kw in text for kw in ['dubstep', 'riddim', 'brostep', 'bass', 'tearout', 'deathstep']): return MusicGenre.DUBSTEP
    if any(kw in text for kw in ['edm', 'electro', 'big room', 'bounce', 'dj', 'festival']): return MusicGenre.EDM
    if any(kw in text for kw in ['acg', 'anime', 'anisong', 'bootleg', 'vocaloid', '初音', '东方', 'touhou', 'hardcore']): return MusicGenre.ANISONG
    if any(kw in text for kw in ['trance', 'psytrance', 'progressive', 'uplifting']): return MusicGenre.TRANCE
    if any(kw in text for kw in ['house', 'tech', 'bass house', 'deep house', 'slap house']): return MusicGenre.HOUSE
    if any(kw in text for kw in ['garage', 'ukg', 'uk bass', '2-step', 'grime', 'dnb', 'drum']): return MusicGenre.GARAGE
    if any(kw in text for kw in ['remix', 'mix', 'mashup']): return MusicGenre.EDM
    return MusicGenre.POP

# ============================================================================
# [State Management]
# ============================================================================
class VJStateManager:
    def __init__(self):
        self.state = {
            "level": 0.0,            
            "beat": 1,               
            "bpm": 120.0, 
            "pos_ratio": 0.0, 
            "is_playing": False,
            "title": "AWAITING VDJ SIGNAL", 
            "artist": "",
            "genre": MusicGenre.UNKNOWN,
            "vibe": EnergyVibe.CHILL,
            "deck": "active",
            "last_beat_time": time.time(),
            "phrase_counter": 1,    
            "total_beats": 0,       
            "isDrop": False,
            "isBuildUp": False,
            "transition_trigger": False,
            "macro_swap_trigger": False 
        }
        self.energy_history = []
        self.long_term_energy = []
        self._lock = threading.Lock()
        self.http_session = requests.Session()

    def update_from_vdj(self):
        deck = self.state["deck"]
        try:
            endpoints = {
                "level": f"deck {deck} level",
                "beat": f"deck {deck} get_beat_num",
                "pos": f"deck {deck} get_position",
                "play": f"deck {deck} play",
                "bpm": f"deck {deck} get_bpm",
                "d1_bpm": "deck 1 get_bpm",
                "d1_high": "deck 1 eq_high",
                "d1_mid": "deck 1 eq_mid",
                "d1_low": "deck 1 eq_low",
                "d1_level": "deck 1 level",               
                "d1_loop": "deck 1 loop",                 
                "d1_fx": "deck 1 get_effects_used",       
                "d2_bpm": "deck 2 get_bpm",
                "d2_high": "deck 2 eq_high",
                "d2_mid": "deck 2 eq_mid",
                "d2_low": "deck 2 eq_low",
                "d2_level": "deck 2 level",               
                "d2_loop": "deck 2 loop",                 
                "d2_fx": "deck 2 get_effects_used"        
            }
            results = {}
            for k, script in endpoints.items():
                try:
                    r = self.http_session.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script={quote(script)}", timeout=0.2)
                    results[k] = r.text.strip() if r.status_code == 200 else "0"
                except Exception: 
                    results[k] = "0"
            
            level_val = VJHelper.safe_float(results["level"])
            beat_val = int(VJHelper.safe_float(results["beat"]))
            if beat_val == 0: beat_val = 1
            pos_val = VJHelper.safe_float(results["pos"])
            bpm_val = VJHelper.safe_float(results["bpm"])
            
            play_str = results["play"].lower()
            is_playing = VJHelper.safe_float(play_str) > 0.5 if play_str.replace('.','',1).isdigit() else play_str in ['yes', 'true', 'on', '1']

            with self._lock:
                trans_trig = False
                macro_swap = False
                
                if is_playing and beat_val != self.state["beat"]:
                    self.state["last_beat_time"] = time.time()
                    self.state["total_beats"] += 1
                    
                    if beat_val == 1:
                        self.state["phrase_counter"] += 1
                        if self.state["phrase_counter"] in [1, 9, 17, 25]: 
                            trans_trig = True
                        if self.state["phrase_counter"] > 32:
                            self.state["phrase_counter"] = 1
                            macro_swap = True 

                self.state["beat"] = beat_val

                self.energy_history.append(level_val)
                if len(self.energy_history) > 30: self.energy_history.pop(0)
                short_avg = sum(self.energy_history) / max(len(self.energy_history), 1)

                self.long_term_energy.append(level_val)
                if len(self.long_term_energy) > 200: self.long_term_energy.pop(0)
                long_avg = sum(self.long_term_energy) / max(len(self.long_term_energy), 1)

                vibe = EnergyVibe.ACTIVE
                is_drop = False
                is_build = False
                
                if short_avg < 0.25 and long_avg < 0.35:
                    vibe = EnergyVibe.CHILL
                elif short_avg > long_avg * 1.3 and short_avg > 0.5:
                    vibe = EnergyVibe.BUILDUP
                    is_build = True
                
                if (self.state["phrase_counter"] in [1, 17] and beat_val == 1 and level_val > 0.7) or \
                   (level_val > long_avg * 2.0 and level_val > 0.8):
                    vibe = EnergyVibe.DROP
                    is_drop = True

                if vibe != self.state["vibe"] and (is_drop or vibe == EnergyVibe.CHILL):
                    macro_swap = True

                self.state.update({
                    "level": level_val,
                    "isDrop": is_drop, 
                    "isBuildUp": is_build,
                    "pos_ratio": pos_val,
                    "bpm": bpm_val if bpm_val > 0 else 120.0,
                    "is_playing": is_playing,
                    "vibe": vibe,
                    "transition_trigger": trans_trig or self.state["transition_trigger"],
                    "macro_swap_trigger": macro_swap or self.state["macro_swap_trigger"],
                    
                    "d1_bpm": VJHelper.safe_float(results.get("d1_bpm", 0.0)),
                    "d1_high": VJHelper.safe_float(results.get("d1_high", 0.5)),
                    "d1_mid": VJHelper.safe_float(results.get("d1_mid", 0.5)),
                    "d1_low": VJHelper.safe_float(results.get("d1_low", 0.5)),
                    "d2_bpm": VJHelper.safe_float(results.get("d2_bpm", 0.0)),
                    "d2_high": VJHelper.safe_float(results.get("d2_high", 0.5)),
                    "d2_mid": VJHelper.safe_float(results.get("d2_mid", 0.5)),
                    "d2_low": VJHelper.safe_float(results.get("d2_low", 0.5)),

                    "d1_level": VJHelper.safe_float(results.get("d1_level", 0.0)),
                    "d2_level": VJHelper.safe_float(results.get("d2_level", 0.0)),
                    "d1_loop": str(results.get("d1_loop", "off")).lower() in ["on", "true", "1"],
                    "d2_loop": str(results.get("d2_loop", "off")).lower() in ["on", "true", "1"],
                    "d1_fx": int(VJHelper.safe_float(results.get("d1_fx", 0))),
                    "d2_fx": int(VJHelper.safe_float(results.get("d2_fx", 0)))
                })
        except Exception: 
            pass

    def update_song_info(self, title, artist, deck):
        with self._lock:
            self.state["title"] = title
            self.state["artist"] = artist
            self.state["deck"] = deck
            self.state["genre"] = analyze_genre(title, artist)
            self.state["phrase_counter"] = 1
            self.state["total_beats"] = 0
            self.state["transition_trigger"] = True
            self.state["macro_swap_trigger"] = True

    def get_state(self):
        with self._lock: 
            ret = self.state.copy()
            self.state["transition_trigger"] = False
            self.state["macro_swap_trigger"] = False
            return ret

vj_manager = VJStateManager()

def vdj_polling_worker():
    while True:
        try:
            vj_manager.update_from_vdj()
        except: pass
        time.sleep(0.05)

# ============================================================================
# [Network Routing Core]
# ============================================================================
PROXY_PORT = 48765

class MultiStreamManager:
    def __init__(self):
        self.streams = {"main": "", "vj1_A": "", "vj1_B": "", "vj2_A": "", "vj2_B": ""}
        self.lock = threading.Lock()
    def set_stream(self, channel, url):
        with self.lock: self.streams[channel] = url
    def get_stream(self, channel):
        with self.lock: return self.streams.get(channel, "")

stream_hub = MultiStreamManager()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class MultiChannelProxy(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
        
    def do_GET(self):
        channel = "main"
        for c in ["vj1_A", "vj1_B", "vj2_A", "vj2_B"]:
            if f"/stream/{c}/" in self.path: channel = c; break
            
        target_url = stream_hub.get_stream(channel)
        if not target_url:
            self.send_response(404)
            self.end_headers()
            return

        req_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
            'Referer': 'https://www.bilibili.com',
            'Accept-Encoding': 'identity'
        }
        
        client_range = self.headers.get('Range')
        if client_range: req_headers['Range'] = client_range
            
        try:
            with requests.get(target_url, headers=req_headers, stream=True, timeout=10) as r:
                if r.status_code not in (200, 206):
                    self.send_response(r.status_code)
                    self.end_headers()
                    return
                    
                self.send_response(r.status_code)
                for k, v in r.headers.items():
                    if k.lower() in ['content-type', 'content-length', 'content-range', 'accept-ranges']:
                        self.send_header(k, v)
                self.end_headers()
                
                raw_stream = r.raw
                while True:
                    chunk = raw_stream.read(128 * 1024) 
                    if not chunk: break
                    try:
                        self.wfile.write(chunk)
                        self.wfile.flush()
                    except Exception: return 
        except Exception as e: 
            print(f"[Proxy] Error streaming channel {channel}: {e}")
            pass

# ============================================================================
# [Triple-Browser Engine]
# ============================================================================
class TaskMode(Enum):
    AUTO = 1          
    SEARCH_ONLY = 2   
    GRAB_CURRENT = 3  

class MultiBrowserManager:
    _drivers = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_driver(cls, instance_name="main"):
        with cls._lock:
            if instance_name not in cls._drivers:
                cls._init_driver(instance_name)
            try:
                _ = cls._drivers[instance_name].window_handles
            except Exception:
                try: cls._drivers[instance_name].quit()
                except Exception: pass
                cls._init_driver(instance_name)
            return cls._drivers[instance_name]
            
    @classmethod
    def _init_driver(cls, instance_name):
        print(f"[Engine] 启动 Bilibili 隔离环境: {instance_name.upper()}...")
        
        if instance_name == "main": profile_dir = PROFILE_DIR_MAIN
        elif instance_name == "vj1": profile_dir = PROFILE_DIR_VJ1
        else: profile_dir = PROFILE_DIR_VJ2
        
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--mute-audio")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-software-rasterizer")
        
        try:
            driver = uc.Chrome(
                options=options, 
                user_data_dir=profile_dir, 
                use_subprocess=True, 
                driver_executable_path=DRIVER_PATH
            )
            
            if instance_name == "main": driver.set_window_rect(50, 50, 1024, 768)
            elif instance_name == "vj1": driver.set_window_rect(100, 100, 1024, 768)
            else: driver.set_window_rect(150, 150, 1024, 768)
                
            cls._drivers[instance_name] = driver
        except Exception as e:
            raise RuntimeError(f"浏览器 {instance_name} 启动失败: {str(e)}")
            
    @classmethod
    def close_all(cls):
        with cls._lock:
            for name, driver in cls._drivers.items():
                try: driver.quit()
                except Exception: pass
            cls._drivers.clear()

class EngineStarter(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    def run(self):
        try:
            self.log_signal.emit("⏳ 正在拉起 [主核] 浏览器，这通常需要几秒钟...")
            MultiBrowserManager.get_driver("main")
            self.log_signal.emit("✅ 主核浏览器后端已就绪 (Main Engine Standby)")
            time.sleep(3) 
            self.log_signal.emit("⏳ 正在拉起 [VJ1] 氛围核浏览器...")
            MultiBrowserManager.get_driver("vj1")
            self.log_signal.emit("✅ VJ1图层渲染核已就绪 (VJ1 Material Engine Standby)")
            time.sleep(3) 
            self.log_signal.emit("⏳ 正在拉起 [VJ2] 粒子核浏览器...")
            MultiBrowserManager.get_driver("vj2")
            self.log_signal.emit("✅ VJ2图层渲染核已就绪 (VJ2 Material Engine Standby)")
            self.finished_signal.emit()
        except Exception as e: 
            self.log_signal.emit(f"❌ 浏览器启动失败: {e}")

class BrowserMonitor(QThread):
    video_detected = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.running = True
        self.last_url = ""
    def run(self):
        while self.running:
            time.sleep(1.5)
            try:
                driver = MultiBrowserManager.get_driver("main")
                handles = driver.window_handles
                if handles and driver.current_window_handle != handles[-1]:
                    driver.switch_to.window(handles[-1])
                current_url = driver.current_url
                if "/video/BV" in current_url:
                    clean_url = current_url.split('?')[0]
                    if clean_url != self.last_url:
                        self.last_url = clean_url
                        self.video_detected.emit(clean_url)
            except Exception: pass
    def stop(self):
        self.running = False
        self.wait()

# ============================================================================
# [VDJ Poller Core]
# ============================================================================
class VDJPoller(QThread):
    vdj_state_signal = pyqtSignal(dict)
    network_error_signal = pyqtSignal(str)
    network_ok_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.network_ok = False
        self.current_deck = "active"
        
    def run(self):
        while self.running:
            time.sleep(0.1)
            if not self.network_ok:
                try:
                    r = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=get_clock", timeout=0.5)
                    if r.status_code == 200:
                        self.network_ok = True
                        self.network_ok_signal.emit()
                except Exception: pass
                continue
            try:
                state = {'is_playing': False, 'pitch': 1.0, 'time_ms': 0.0, 'pos_ratio': -1.0, 'cur_bpm': 0.0, 'orig_bpm': 0.0}
                deck_str = self.current_deck
                
                r_play = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20play", timeout=0.3)
                if r_play.status_code == 200:
                    play_str = r_play.text.strip().lower()
                    if play_str.replace('.', '', 1).isdigit(): state['is_playing'] = VJHelper.safe_float(play_str) > 0.5
                    else: state['is_playing'] = play_str in ['yes', 'true', 'on', '1']
                        
                target_rate, cur_bpm, orig_bpm, bpm_valid = 1.0, 0.0, 0.0, False
                try:
                    r_bpm = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20get_bpm", timeout=0.3)
                    r_obpm = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20get_bpm%20%27absolute%27", timeout=0.3)
                    if r_bpm.status_code == 200 and r_obpm.status_code == 200:
                        bpm_str, obpm_str = r_bpm.text.strip(), r_obpm.text.strip()
                        if "error" not in bpm_str.lower() and "error" not in obpm_str.lower():
                            cur_bpm, orig_bpm = VJHelper.safe_float(bpm_str), VJHelper.safe_float(obpm_str)
                            if orig_bpm > 0:
                                target_rate = cur_bpm / orig_bpm
                                bpm_valid = True
                except Exception: pass
                
                if not bpm_valid:
                    try:
                        r_pitch = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20get_pitch_value", timeout=0.3)
                        if r_pitch.status_code == 200:
                            pitch_str = r_pitch.text.strip().replace('%', '')
                            if "error" not in pitch_str.lower():
                                pitch_val = VJHelper.safe_float(pitch_str)
                                if pitch_val > 5.0 or pitch_val < -5.0: target_rate = 1.0 + (pitch_val / 100.0)
                                else: target_rate = pitch_val if pitch_val > 0.01 else 1.0
                                orig_bpm, cur_bpm = 120.0, 120.0 * target_rate
                    except Exception: pass
                
                if math.isnan(target_rate) or math.isinf(target_rate): target_rate = 1.0
                state['pitch'] = max(0.01, min(target_rate, 4.0)) 
                state['cur_bpm'], state['orig_bpm'] = cur_bpm, orig_bpm
                        
                r_pos = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20get_position", timeout=0.3)
                if r_pos.status_code == 200:
                    pos_str = r_pos.text.strip()
                    if "error" not in pos_str.lower():
                        val = VJHelper.safe_float(pos_str, -1.0)
                        if val >= 0: state['pos_ratio'] = val
                            
                r_time = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20get_time%20%27absolute%27", timeout=0.3)
                if r_time.status_code == 200:
                    parsed_ms = VJHelper.parse_vdj_time_to_ms(r_time.text)
                    if parsed_ms is not None: state['time_ms'] = parsed_ms
                            
                self.vdj_state_signal.emit(state)
            except Exception as e:
                self.network_ok = False
                self.network_error_signal.emit(str(e))
                
    def stop(self):
        self.running = False
        self.wait()

# ============================================================================
# [Task Worker] 
# ============================================================================
class SearchWorker(QObject):
    finished = pyqtSignal(dict)
    log = pyqtSignal(str)
    play_media = pyqtSignal(str, str, str) 
    update_ui = pyqtSignal(dict)      
    
    def __init__(self, query, song_name, raw_filename, mode: TaskMode, use_vdj_sync=False, algo_mode=2, channel="main"):
        super().__init__()
        self.query, self.song_name, self.raw_filename = query, song_name, raw_filename
        self.mode, self.use_vdj_sync, self.algo_mode, self.channel = mode, use_vdj_sync, algo_mode, channel

    def run(self):
        res_data = {"success": False, "channel": self.channel, "original_url": None, "title": "Bili Video", "is_search_only": False}
        
        try:
            target_duration = 0
            if self.use_vdj_sync and self.channel == "main":
                self.log.emit("⏳ [Main] 请求底层，读取稳定原曲物理时间...")
                time.sleep(1.0)
                last_dur, target_deck = -1, "active"
                
                if self.raw_filename:
                    for d in range(1, 5):
                        try:
                            r_file = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{d}%20get_filepath", timeout=0.5)
                            if r_file.status_code == 200:
                                filepath = r_file.text.strip().replace('"', '').replace("'", "")
                                if filepath and "error" not in filepath.lower() and filepath != "0":
                                    file_title = os.path.splitext(os.path.basename(filepath))[0]
                                    if self.raw_filename.lower() in file_title.lower() or file_title.lower() in self.raw_filename.lower():
                                        target_deck = str(d); break
                        except Exception: pass
                self.update_ui.emit({"target_deck": target_deck})

                for attempt in range(12):
                    try:
                        dur_sec = 0
                        r_dur = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_time%20%27total%27%20%27absolute%27", timeout=0.5)
                        if r_dur.status_code == 200:
                            dur_ms = VJHelper.parse_vdj_time_to_ms(r_dur.text)
                            if dur_ms and dur_ms > 0: dur_sec = dur_ms / 1000.0
                                
                        if dur_sec <= 0:
                            r_dur = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_songlength", timeout=0.5)
                            if r_dur.status_code == 200:
                                dur_ms = VJHelper.parse_vdj_time_to_ms(r_dur.text)
                                if dur_ms and dur_ms > 0:
                                    dur_sec = dur_ms / 1000.0
                                    pitch_rate = 1.0
                                    try:
                                        r_bpm = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_bpm", timeout=0.2)
                                        r_obpm = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_bpm%20%27absolute%27", timeout=0.2)
                                        if r_bpm.status_code == 200 and r_obpm.status_code == 200:
                                            bpm_val, obpm_val = VJHelper.safe_float(r_bpm.text), VJHelper.safe_float(r_obpm.text)
                                            if obpm_val > 0: pitch_rate = bpm_val / osbpm_val
                                    except Exception: pass
                                    dur_sec = dur_sec * pitch_rate
                        
                        if dur_sec > 0:
                            if abs(dur_sec - last_dur) < 0.1:
                                target_duration = dur_sec
                                self.log.emit(f"✅ 成功锁定 VDJ 原曲时长: {int(target_duration)} 秒")
                                self.update_ui.emit({"target_duration": target_duration})
                                break
                            last_dur = dur_sec
                    except Exception: pass
                    time.sleep(0.5)

            driver, target_url, candidate_urls, found_candidates = None, "", [], []

            try:
                browser_name = "main"
                if "vj1" in self.channel: browser_name = "vj1"
                elif "vj2" in self.channel: browser_name = "vj2"
                
                driver = MultiBrowserManager.get_driver(browser_name)
                
                if self.mode == TaskMode.SEARCH_ONLY:
                    self.log.emit(f"🔍 [{self.channel.upper()}] 开启半自动检索: {self.query}")
                    driver.get(f"https://search.bilibili.com/all?keyword={quote(self.query)}")
                    res_data["is_search_only"], res_data["success"] = True, True
                    self.finished.emit(res_data)
                    return
                elif self.mode == TaskMode.GRAB_CURRENT:
                    target_url = self.query if (self.query and self.query.startswith("http")) else driver.current_url
                    candidate_urls.append(target_url)
                else: 
                    self.log.emit(f"🔍 [{self.channel.upper()}] 正在深度检索: {self.query}")
                    safe_query = quote(self.query)
                    try: driver.get(f"https://search.bilibili.com/all?keyword={safe_query}")
                    except Exception:
                        self.log.emit(f"⚠️ [{self.channel.upper()}] 引擎重连中...")
                        MultiBrowserManager.close_all()
                        driver = MultiBrowserManager.get_driver(browser_name)
                        driver.get(f"https://search.bilibili.com/all?keyword={safe_query}")
                    
                    time.sleep(1.5) 
                    
                    js_extractor = """
                    let res = []; let idx = 0; 
                    let cards = document.querySelectorAll('.bili-video-card, .video-list-item, .v-card');
                    if (cards.length > 0) {
                        for(let i = 0; i < cards.length; i++) {
                            if (res.length >= 30) break; 
                            let card = cards[i]; let a = card.querySelector('a');
                            let dur = card.querySelector('.bili-video-card__stats__duration') || card.querySelector('.b-length');
                            let viewNode = card.querySelector('.bili-video-card__stats--item') || card.querySelector('.play-text');
                            let views = viewNode ? viewNode.innerText.trim() : "0";
                            let titNode = card.querySelector('h3') || card.querySelector('.bili-video-card__info--tit') || card.querySelector('.title');
                            let titleText = titNode ? (titNode.getAttribute('title') || titNode.innerText.trim()) : "";
                            if (!titleText && a) titleText = a.getAttribute('title') || a.innerText.trim();
                            let durText = dur ? dur.innerText.trim() : "00:00";
                            
                            if(a && a.href.includes('/video/BV')) {
                                res.push({ url: a.href, dur_text: durText, views_text: views, title: titleText, original_index: idx });
                                idx++;
                            }
                        }
                    } 
                    if (res.length === 0) {
                        let links = document.querySelectorAll('a[href*="/video/BV"]');
                        let uniqueLinks = new Set();
                        links.forEach(a => {
                            if(res.length >= 30) return;
                            let cleanHref = a.href.split('?')[0];
                            if(!uniqueLinks.has(cleanHref)) {
                                uniqueLinks.add(cleanHref);
                                let titleText = a.getAttribute('title') || a.innerText.trim() || "Fallback Title";
                                if (titleText.length > 2) {
                                    res.push({ url: cleanHref, dur_text: "00:00", views_text: "0", title: titleText, original_index: idx++ });
                                }
                            }
                        });
                    }
                    return res;
                    """
                    raw_results = driver.execute_script(js_extractor)
                    
                    for item in raw_results:
                        clean_h = "https:" + item['url'].split('?')[0] if item['url'].startswith("//") else item['url'].split('?')[0]
                        parts = item['dur_text'].split(':')
                        dur_sec = 0
                        if len(parts) == 3: dur_sec = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        elif len(parts) == 2: dur_sec = int(parts[0]) * 60 + int(parts[1])
                        
                        if not any(c['url'] == clean_h for c in found_candidates):
                            found_candidates.append({"url": clean_h, "duration": dur_sec, "title": item.get('title', ''), "views": VJHelper.parse_views_count(item.get('views_text', '0')), "original_index": item['original_index']})
            except Exception as e: self.log.emit(f"⚠️ [{self.channel.upper()}] 爬取异常: {e}")

            best_candidate = None
            if found_candidates:
                if self.channel == "main" and target_duration > 0:
                    clean_song_str = VJHelper.clean_text_for_match(self.song_name)
                    song_words = set(clean_song_str.split())
                    max_views = max((c['views'] for c in found_candidates), default=1)
                    for c in found_candidates:
                        clean_tit = VJHelper.clean_text_for_match(c['title'])
                        if not song_words: c['text_score'] = 1.0
                        else:
                            matched = sum(1 for w in song_words if w in clean_tit)
                            base_txt = matched / len(song_words)
                            if clean_song_str and clean_song_str in clean_tit: base_txt += 0.5 
                            c['text_score'] = min(base_txt, 1.0)
                            
                        c['time_diff'] = abs(c['duration'] - target_duration)
                        time_score = math.exp(-0.08 * c['time_diff'])
                        pop_score = math.log(c['views'] + 2) / max(math.log(max_views + 2), 1)
                        rank_score = 1.0 / (1.0 + 0.1 * c['original_index'])
                        c['smart_score'] = (c['text_score'] * 0.45) + (time_score * 0.35) + (pop_score * 0.15) + (rank_score * 0.05)
                    
                    if self.algo_mode == 1:
                        valid = [c for c in found_candidates if c['time_diff'] <= 5 and c['text_score'] >= 1.0]
                        if valid: valid.sort(key=lambda x: x['views'], reverse=True); best_candidate = valid[0]
                    elif self.algo_mode == 2:
                        found_candidates.sort(key=lambda x: x['smart_score'], reverse=True); best_candidate = found_candidates[0]
                    elif self.algo_mode == 3:
                        found_candidates.sort(key=lambda x: (-x['text_score'], int(x['time_diff'] / 3), -x['views'])); best_candidate = found_candidates[0]
                    elif self.algo_mode == 4:
                        found_candidates.sort(key=lambda x: (x['time_diff'], -x['text_score'], -x['views'])); best_candidate = found_candidates[0]

                    if not best_candidate:
                        found_candidates.sort(key=lambda x: x['smart_score'], reverse=True); best_candidate = found_candidates[0]
                        
                elif "vj1" in self.channel or "vj2" in self.channel:
                    valid_vj = found_candidates
                    if any(c['duration'] > 0 for c in found_candidates):
                        valid_vj = [c for c in found_candidates if c['duration'] == 0 or (10 <= c['duration'] <= 7200)]
                    bad_words = ["教", "学", "课程", "如何", "演示", "教程", "讲解"]
                    valid_vj = [c for c in valid_vj if not any(bw in c['title'] for bw in bad_words)]

                    strict_vj = [c for c in valid_vj if any(kw in c['title'].upper() for kw in ["素材", "背景", "VJ"])]
                    if strict_vj:
                        valid_vj = strict_vj
                    
                    if valid_vj:
                        valid_vj.sort(key=lambda x: x['views'], reverse=True)
                        best_candidate = random.choice(valid_vj[:5]) 
                        self.log.emit(f"🌠 [VJ智选] 锁定{self.channel.upper()}视觉源: {best_candidate['title'][:15]}...")

            if not best_candidate and found_candidates: best_candidate = found_candidates[0]
            if not best_candidate and not candidate_urls: raise Exception(f"未找到任何匹配的 {self.channel} 视频结果！")

            target_url = best_candidate['url'] if best_candidate else candidate_urls[0]
            title = best_candidate['title'] if best_candidate else "Unknown Video"
            bvid_match = re.search(r'(BV[a-zA-Z0-9]+)', target_url)
            bvid = bvid_match.group(1) if bvid_match else str(int(time.time()))

            if driver and self.mode == TaskMode.AUTO:
                self.log.emit(f"🚀 [{self.channel.upper()}] 浏览器下潜解析 JS 流协议...")
                try: driver.get(target_url)
                except Exception: pass

            v_url = None
            if driver:
                for _ in range(4):
                    time.sleep(1.5) 
                    try:
                        v_url = driver.execute_script("""
                            let pi = window.__playinfo__;
                            if (pi && pi.data) {
                                if (pi.data.dash && pi.data.dash.video) {
                                    let v = pi.data.dash.video.find(x => x.codecs.startsWith('avc')) || pi.data.dash.video[0];
                                    return v.baseUrl;
                                } else if (pi.data.durl) {
                                    return pi.data.durl[0].url;
                                }
                            }
                            return null;
                        """)
                        if v_url: break
                    except Exception: pass

            if not v_url:
                self.log.emit(f"⚠️ [{self.channel.upper()}] JS提取超时，调用本地 FFmpeg/ydl 引擎...")
                ydl_opts_info = {'format': 'bestvideo[vcodec^=avc][height<=1080][ext=mp4]/bestvideo/best', 'quiet': True, 'cookiefile': STATIC_COOKIE_FILE, 'noplaylist': True}
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                        info = ydl.extract_info(target_url, download=False)
                        for f in reversed(info.get('formats', [])):
                            if f.get('vcodec') != 'none' and 'url' in f:
                                v_url = f.get('url'); break
                        if not v_url: v_url = info.get('url')
                except Exception as e:
                    self.log.emit(f"⚠️ 备用解算器也失败: {e}")

            if not v_url:
                raise Exception("无法提取有效的无水印直连流(可能被B站风控拦截)。")

            res_data["original_url"] = target_url
            stream_hub.set_stream(self.channel, v_url)

            cached_files = [f for f in glob.glob(os.path.join(CACHE_DIR, f"*_{bvid}.mp4")) if not f.endswith(".temp.mp4")]
            if cached_files:
                local_file = os.path.abspath(cached_files[0])
                self.log.emit(f"🚀 [{self.channel.upper()}] 命中本地完整缓存，极速物理直读")
                self.play_media.emit(local_file, "local", self.channel)
            else:
                self.log.emit(f"⚡ [{self.channel.upper()}] 缓存未击中，挂载云端代理流播放！")
                unique_ts = int(time.time() * 1000)
                proxy_url = f"http://127.0.0.1:{PROXY_PORT}/stream/{self.channel}/{bvid}_{unique_ts}.mp4"
                self.play_media.emit(proxy_url, "stream", self.channel)
                
                safe_title = VJHelper.sanitize_filename(title)
                final_save_path = os.path.abspath(os.path.join(CACHE_DIR, f"{safe_title}_{bvid}.mp4"))
                temp_save_path = final_save_path + ".temp.mp4"
                
                cmd_str = f'yt-dlp -f "bestvideo[vcodec^=avc][height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --keep-video --no-playlist -o "{temp_save_path}" --cookies "{STATIC_COOKIE_FILE}" "{target_url}"'
                def safe_delayed_dl():
                    time.sleep(4.0)
                    try:
                        subprocess.run(cmd_str, shell=True, check=True)
                        if os.path.exists(temp_save_path):
                            os.rename(temp_save_path, final_save_path) 
                            print(f"[Core] 下载并合轨完成: {final_save_path}")
                    except Exception as e:
                        print(f"[Core] 下载队列异常: {e}")
                        try:
                            if os.path.exists(temp_save_path): os.remove(temp_save_path)
                        except: pass
                threading.Thread(target=safe_delayed_dl, daemon=True).start()

            if self.channel == "main":
                update_payload = {"title": title}
                if target_duration > 0: update_payload["target_duration"] = target_duration
                self.update_ui.emit(update_payload)
                
            res_data["success"] = True

        except Exception as e:
            self.log.emit(f"❌ [{self.channel.upper()}] 任务崩塌: {str(e)}")
            res_data["success"] = False

        self.finished.emit(res_data)

# ============================================================================
# [Native UI & Compositing Engine] 
# ============================================================================
class KineticHUDSystem:
    def __init__(self, scene, w, h):
        self.scene = scene
        self.w, self.h = w, h
        
        self.font_main = QFont("Arial Black", 50, QFont.Weight.Black)
        self.font_sub = QFont("Consolas", 20, QFont.Weight.Bold)
        self.font_hud = QFont("Consolas", 14)

        self.mixer_hud = QGraphicsTextItem("")
        self.mixer_hud.setFont(self.font_hud)
        self.mixer_hud.setDefaultTextColor(QColor(255, 255, 255, 220)) 
        self.scene.addItem(self.mixer_hud)

        self.cover_item = QGraphicsPixmapItem()
        self.scene.addItem(self.cover_item)

        self.tl_title_item = QGraphicsTextItem("")
        self.tl_title_item.setFont(self.font_hud)
        self.tl_title_item.setDefaultTextColor(QColor(255, 255, 255, 200))
        self.scene.addItem(self.tl_title_item)

        self.title_item = QGraphicsTextItem("")
        self.title_item.setFont(self.font_main)
        self.title_item.setDefaultTextColor(QColor(255, 255, 255))
        self.scene.addItem(self.title_item)
        
        self.title_shadow = QGraphicsDropShadowEffect()
        self.title_shadow.setBlurRadius(25)
        self.title_shadow.setColor(QColor(0, 255, 255, 200))
        self.title_shadow.setOffset(0, 0)
        self.title_item.setGraphicsEffect(self.title_shadow)

        self.hud_left = QGraphicsTextItem("BPM: ---\nPHR: --")
        self.hud_left.setFont(self.font_hud)
        self.hud_left.setDefaultTextColor(QColor(255, 255, 255, 150))
        self.scene.addItem(self.hud_left)

        self.hud_right = QGraphicsTextItem("DECK: ---\nLVL: ---")
        self.hud_right.setFont(self.font_hud)
        self.hud_right.setDefaultTextColor(QColor(255, 255, 255, 150))
        self.scene.addItem(self.hud_right)
        
        self.hide_all()

    def set_cover(self, image_data):
        if image_data:
            pix = QPixmap.fromImage(QImage.fromData(image_data)).scaled(
                80, 80, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.cover_item.setPixmap(pix)
        else:
            self.cover_item.setPixmap(QPixmap()) 

    def hide_all(self):
        self.title_item.hide()
        self.hud_left.hide()
        self.hud_right.hide()
        self.mixer_hud.hide()

    def show_all(self):
        self.title_item.show()
        self.hud_left.show()
        self.hud_right.show()
        self.mixer_hud.show()

    def update(self, state, kick_env, snare_env, w, h, cfg):
        self.w, self.h = w, h
        title = state.get('title', '')
        artist = state.get('artist', '')
        bpm = state.get('bpm', 120.0)
        vibe = state.get('vibe', EnergyVibe.CHILL)
        genre = state.get('genre', MusicGenre.UNKNOWN)
        phrase = state.get('phrase_counter', 1)
        level = state.get('level', 0.0)
        pos = state.get('pos_ratio', 0.0)
        
        if cfg.get('fx_mixer_hud', True):
            self.mixer_hud.show()
            def make_vu_bar(val):
                bars = max(0, min(15, int(val * 15))) 
                bar_str = "█" * bars + "-" * (15 - bars)
                return bar_str

            d1_vol = state.get("d1_level", 0.0)
            d2_vol = state.get("d2_level", 0.0)
            
            mixer_text = (
                f"L-VOL : [{make_vu_bar(d1_vol)}]  ||  R-VOL : [{make_vu_bar(d2_vol)}]\n"
            )
            
            self.mixer_hud.setPlainText(mixer_text)
            m_br = self.mixer_hud.boundingRect()
            self.mixer_hud.setPos((w - m_br.width()) / 2, h - m_br.height() - 30)
        else:
            self.mixer_hud.hide()

        def make_bar(val):
            bars = max(0, min(10, int(val * 10))) 
            return "■" * bars + "-" * (10 - bars)

        d1_bpm = state.get("d1_bpm", 0.0)
        d1_h, d1_m, d1_l = state.get("d1_high", 0.5), state.get("d1_mid", 0.5), state.get("d1_low", 0.5)
        text_left = (
            f"[ DECK 1 ]\n"
            f"BPM : {d1_bpm:.1f}\n"
            f"HI  : [{make_bar(d1_h)}]\n"
            f"MID : [{make_bar(d1_m)}]\n"
            f"LOW : [{make_bar(d1_l)}]"
        )
        self.hud_left.setPlainText(text_left)
        self.hud_left.setPos(50, h - 180)
        
        d2_bpm = state.get("d2_bpm", 0.0)
        d2_h, d2_m, d2_l = state.get("d2_high", 0.5), state.get("d2_mid", 0.5), state.get("d2_low", 0.5)
        text_right = (
            f"[ DECK 2 ]\n"
            f"BPM : {d2_bpm:.1f}\n"
            f"HI  : [{make_bar(d2_h)}]\n"
            f"MID : [{make_bar(d2_m)}]\n"
            f"LOW : [{make_bar(d2_l)}]"
        )
        self.hud_right.setPlainText(text_right)
        r_br = self.hud_right.boundingRect()
        self.hud_right.setPos(w - r_br.width() - 50, h - 180)

        display_tl = f"{artist} - {title}" if artist else title
        self.tl_title_item.setPlainText(display_tl)

        cover_x, cover_y = 30, 30
        self.cover_item.setPos(cover_x, cover_y)
        self.tl_title_item.setPos(cover_x + 95, cover_y + 25)

class VJGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

class OBSVideoWindow(QMainWindow):
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OBS Master Output - Arena Layer Engine")
        self.resize(1280, 720)
        self.setStyleSheet("background-color: black;")
        
        self.view = QGraphicsView(self)
        self.view.setStyleSheet("background: black; border: none;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # [核心修正] 挂载 OpenGL 视口以启用硬件加速，防止 "Unable to copy frame from decoder pool"
        self.opengl_viewport = QOpenGLWidget()
        self.view.setViewport(self.opengl_viewport)
        
        self.setCentralWidget(self.view)
        
        self.scene = VJGraphicsScene(self)
        self.view.setScene(self.scene)
        
        self.main_video_item = QGraphicsVideoItem()
        self.scene.addItem(self.main_video_item)
        self.player_main = QMediaPlayer()
        self.audio_main = QAudioOutput(); self.audio_main.setVolume(0.0) 
        self.player_main.setAudioOutput(self.audio_main)
        self.player_main.setVideoOutput(self.main_video_item)
        
        self.vj1_item_A = QGraphicsVideoItem()
        self.vj1_item_B = QGraphicsVideoItem()
        self.vj1_item_A.setOpacity(0.0)
        self.vj1_item_B.setOpacity(0.0)
        self.scene.addItem(self.vj1_item_A)
        self.scene.addItem(self.vj1_item_B)
        
        self.player_vj1_A = QMediaPlayer()
        self.player_vj1_B = QMediaPlayer()
        self.player_vj1_A.setVideoOutput(self.vj1_item_A)
        self.player_vj1_B.setVideoOutput(self.vj1_item_B)
        self.active_vj1_deck = "A"

        self.vj2_item_A = QGraphicsVideoItem()
        self.vj2_item_B = QGraphicsVideoItem()
        self.vj2_item_A.setOpacity(0.0)
        self.vj2_item_B.setOpacity(0.0)
        self.scene.addItem(self.vj2_item_A)
        self.scene.addItem(self.vj2_item_B)
        
        self.player_vj2_A = QMediaPlayer()
        self.player_vj2_B = QMediaPlayer()
        self.player_vj2_A.setVideoOutput(self.vj2_item_A)
        self.player_vj2_B.setVideoOutput(self.vj2_item_B)
        self.active_vj2_deck = "A"

        self.color_fx = QGraphicsColorizeEffect()
        self.color_fx.setColor(QColor(255, 0, 50))
        self.color_fx.setStrength(0.0)
        self.main_video_item.setGraphicsEffect(self.color_fx)

        self.glow_rect = QGraphicsRectItem()
        self.glow_rect.setBrush(QBrush(QColor(0, 150, 255, 0)))
        self.scene.addItem(self.glow_rect)

        self.flash_rect = QGraphicsRectItem()
        self.flash_rect.setBrush(QBrush(QColor(255, 255, 255, 255)))
        self.flash_rect.setOpacity(0.0)
        self.scene.addItem(self.flash_rect)
        
        self.hud = KineticHUDSystem(self.scene, 1280, 720)
        
        self._target_scale_x, self._target_scale_y = 1.0, 1.0
        self._current_scale_x, self._current_scale_y = 1.0, 1.0
        self._target_rot, self._current_rot = 0.0, 0.0
        self._target_dx, self._target_dy = 0.0, 0.0
        self._current_dx, self._current_dy = 0.0, 0.0
        self._target_shear_x, self._target_shear_y = 0.0, 0.0
        self._current_shear_x, self._current_shear_y = 0.0, 0.0
        self._hue_offset = 0
        
        self.vj1_cf = 1.0 
        self.vj2_cf = 1.0

        self.vj_config = {}
        self.is_looping = True
        self.needs_initial_sync = False  
        
        self.player_main.positionChanged.connect(self.position_changed.emit)
        self.player_main.durationChanged.connect(self.duration_changed.emit)
        self.player_main.mediaStatusChanged.connect(self._handle_main_loop)
        
        self.player_vj1_A.mediaStatusChanged.connect(lambda s: self._handle_loop(self.player_vj1_A, s))
        self.player_vj1_B.mediaStatusChanged.connect(lambda s: self._handle_loop(self.player_vj1_B, s))
        self.player_vj2_A.mediaStatusChanged.connect(lambda s: self._handle_loop(self.player_vj2_A, s))
        self.player_vj2_B.mediaStatusChanged.connect(lambda s: self._handle_loop(self.player_vj2_B, s))
        
        self.vj_timer = QTimer(self)
        self.vj_timer.timeout.connect(self._render_vj_frame)
        self.vj_timer.start(16) 

    def _handle_main_loop(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self.is_looping:
            self.player_main.setPosition(0); self.player_main.play()
            
    def _handle_loop(self, player, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            player.setPosition(0); player.play()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        self.view.setSceneRect(0, 0, w, h)
        for item in [self.main_video_item, self.vj1_item_A, self.vj1_item_B, self.vj2_item_A, self.vj2_item_B]:
            item.setSize(QSizeF(w, h))
        self.flash_rect.setRect(0, 0, w, h)
        self.glow_rect.setRect(0, 0, w, h)
            
    def play_url(self, url, channel="main"):
        if channel == "main":
            self.player_main.stop(); self.player_main.setSource(QUrl())
            QCoreApplication.processEvents() 
            self.player_main.setSource(QUrl(url) if url.startswith("http") else QUrl.fromLocalFile(url))
            self.needs_initial_sync = True 
            self.player_main.play() 
        elif "vj1" in channel:
            new_deck = "B" if self.active_vj1_deck == "A" else "A"
            player = self.player_vj1_B if new_deck == "B" else self.player_vj1_A
            player.stop()
            player.setSource(QUrl(url) if url.startswith("http") else QUrl.fromLocalFile(url))
            player.play()
            self.active_vj1_deck = new_deck
        elif "vj2" in channel:
            new_deck = "B" if self.active_vj2_deck == "A" else "A"
            player = self.player_vj2_B if new_deck == "B" else self.player_vj2_A
            player.stop()
            player.setSource(QUrl(url) if url.startswith("http") else QUrl.fromLocalFile(url))
            player.play()
            self.active_vj2_deck = new_deck
        
    def clear_overlay(self):
        self.player_vj1_A.stop(); self.player_vj1_B.stop()
        self.player_vj2_A.stop(); self.player_vj2_B.stop()
        self.vj1_item_A.setOpacity(0.0); self.vj1_item_B.setOpacity(0.0)
        self.vj2_item_A.setOpacity(0.0); self.vj2_item_B.setOpacity(0.0)
        
    def blackout(self):
        self.player_main.stop(); self.clear_overlay(); self.player_main.setSource(QUrl())

    def _render_vj_frame(self):
        state = vj_manager.get_state()
        cfg = self.vj_config
        w, h = self.width(), self.height()

        real_level = state.get('level', 0.0)
        beat = state.get('beat', 1)
        bpm = state.get('bpm', 120.0)
        is_playing = state.get('is_playing', False)
        vibe = state.get('vibe', EnergyVibe.CHILL)
        genre = state.get('genre', MusicGenre.UNKNOWN)
        trans_trigger = state.get('transition_trigger', False)
        
        now = time.time()
        beat_duration = 60.0 / max(bpm, 1.0)
        time_since_beat = now - state.get('last_beat_time', now)
        phase = min(1.0, time_since_beat / beat_duration) 
        
        kick_env = math.exp(-phase * 6.0) if beat in [1, 3] else 0.0
        snare_env = math.exp(-phase * 8.0) if beat in [2, 4] else 0.0
        hat_env = math.exp(-(phase % 0.25) * 10.0)
        bass_env = real_level if real_level > 0.4 else 0.0
        lfo_sine = math.sin(now * (bpm / 60.0) * math.pi)

        energy = max(real_level, kick_env) if is_playing and real_level > 0.1 else 0.0
        is_drop = (vibe == EnergyVibe.DROP)
        is_build = (vibe == EnergyVibe.BUILDUP)

        if not is_playing:
            self.flash_rect.hide()
            self.glow_rect.hide()
            self.hud.hide_all()
            self.color_fx.setStrength(0.0)
            for item in [self.main_video_item, self.vj1_item_A, self.vj1_item_B, self.vj2_item_A, self.vj2_item_B]:
                item.setTransform(QTransform())
                item.setPos(0, 0)
            return

        cf_speed = 0.02 
        if self.active_vj1_deck == "A": self.vj1_cf = min(1.0, self.vj1_cf + cf_speed)
        else: self.vj1_cf = max(0.0, self.vj1_cf - cf_speed)
        
        if self.active_vj2_deck == "A": self.vj2_cf = min(1.0, self.vj2_cf + cf_speed)
        else: self.vj2_cf = max(0.0, self.vj2_cf - cf_speed)

        self._target_scale_x, self._target_scale_y = 1.0, 1.0
        self._target_rot = 0.0
        self._target_dx, self._target_dy = 0.0, 0.0
        self._target_shear_x, self._target_shear_y = 0.0, 0.0
        lerp_speed = 0.2 
        
        if trans_trigger:
            self.flash_rect.setBrush(QBrush(QColor(255, 255, 255)))
            self.flash_rect.setOpacity(1.0)
            self.flash_rect.show()
            self._target_scale_x, self._target_scale_y = 1.3, 1.3
            lerp_speed = 0.9

        elif vibe == EnergyVibe.CHILL:
            lerp_speed = 0.05
            if cfg.get('fx_rotate', False):
                self._target_rot = lfo_sine * 1.5 
            if cfg.get('fx_shake', True):
                self._target_scale_x = 1.05 + (energy * 0.02)
                self._target_scale_y = 1.05 + (energy * 0.02)
            self.flash_rect.hide()
            self.glow_rect.setBrush(QBrush(QColor(0, 20, 50, int(50 * energy))))
            self.glow_rect.show()

        elif is_build:
            lerp_speed = 0.3
            if cfg.get('fx_shake', True):
                pulse = hat_env * (0.05 + energy * 0.1)
                self._target_scale_x = 1.0 + pulse
                self._target_scale_y = 1.0 + pulse
            if cfg.get('fx_rotate', False):
                self._target_rot = lfo_sine * (5 + energy * 25) 
            if cfg.get('fx_flash', True) and snare_env > 0.5:
                self.flash_rect.setBrush(QBrush(QColor(255, 255, 255)))
                self.flash_rect.setOpacity(0.4 * snare_env)
                self.flash_rect.show()
            else: self.flash_rect.hide()
            
            self.glow_rect.setBrush(QBrush(QColor(255, 200, 0, int(100 * energy))))
            self.glow_rect.show()

        elif is_drop:
            lerp_speed = 0.8 if snare_env > 0 or kick_env > 0 else 0.4
            
            if cfg.get('fx_shake', True):
                shake_amp = kick_env * (30 if genre == MusicGenre.DUBSTEP else 15)
                self._target_dx = random.uniform(-shake_amp, shake_amp)
                self._target_dy = random.uniform(-shake_amp, shake_amp)
                base_zoom = 1.0 + (kick_env * (0.2 if genre in [MusicGenre.EDM, MusicGenre.DUBSTEP] else 0.1))
                self._target_scale_x *= base_zoom
                self._target_scale_y *= base_zoom

            if cfg.get('fx_glitch', False):
                if genre in [MusicGenre.DUBSTEP, MusicGenre.GARAGE] and snare_env > 0.5:
                    self._target_shear_x = snare_env * random.choice([0.5, -0.5])
                    self._target_shear_y = snare_env * random.choice([0.2, -0.2])
                elif snare_env > 0.8:
                    self._target_shear_x = 0.15 * random.choice([1, -1])

            if cfg.get('fx_mirror', False):
                if genre in [MusicGenre.EDM, MusicGenre.ANISONG]:
                    if beat == 1 and kick_env > 0.4: self._target_scale_x *= -1.0
                    if beat == 3 and kick_env > 0.4: self._target_scale_y *= -1.0
                elif genre == MusicGenre.HOUSE and beat == 4 and phase > 0.7:
                    self._target_scale_x *= -1.0

            if cfg.get('fx_hue', False):
                self._hue_offset = (self._hue_offset + int(kick_env * 30)) % 360
                self.color_fx.setColor(QColor.fromHsl(self._hue_offset, 255, 128))
                self.color_fx.setStrength(0.7 * kick_env)
            
            if cfg.get('fx_flash', True) and beat == 1 and kick_env > 0.6:
                c_idx = random.randint(0, 2)
                colors = [QColor(255,0,50), QColor(0,255,100), QColor(0,100,255)] if genre != MusicGenre.DUBSTEP else [QColor(255,0,0), QColor(255,255,255)]
                self.flash_rect.setBrush(QBrush(random.choice(colors)))
                self.flash_rect.setOpacity(0.9 * kick_env)
                self.flash_rect.show()
            else:
                self.flash_rect.hide()

            glow_c = QColor(255, 0, 80, int(150 * bass_env)) if genre == MusicGenre.DUBSTEP else QColor(0, 255, 200, int(150 * bass_env))
            self.glow_rect.setBrush(QBrush(glow_c))
            self.glow_rect.show()

        else:
            lerp_speed = 0.2
            if cfg.get('fx_shake', True):
                self._target_scale_x = 1.0 + (kick_env * 0.05)
                self._target_scale_y = 1.0 + (kick_env * 0.05)
            self.flash_rect.hide()
            self.glow_rect.hide()

        self._current_scale_x = VJHelper.lerp(self._current_scale_x, self._target_scale_x, lerp_speed)
        self._current_scale_y = VJHelper.lerp(self._current_scale_y, self._target_scale_y, lerp_speed)
        self._current_rot = VJHelper.lerp(self._current_rot, self._target_rot, lerp_speed)
        self._current_dx = VJHelper.lerp(self._current_dx, self._target_dx, lerp_speed)
        self._current_dy = VJHelper.lerp(self._current_dy, self._target_dy, lerp_speed)
        self._current_shear_x = VJHelper.lerp(self._current_shear_x, self._target_shear_x, lerp_speed)
        self._current_shear_y = VJHelper.lerp(self._current_shear_y, self._target_shear_y, lerp_speed)

        for item in [self.main_video_item, self.vj1_item_A, self.vj1_item_B, self.vj2_item_A, self.vj2_item_B]:
            transform = QTransform()
            transform.translate(w/2, h/2) 
            transform.rotate(self._current_rot)
            transform.scale(self._current_scale_x, self._current_scale_y)
            transform.shear(self._current_shear_x, self._current_shear_y)
            transform.translate(-w/2, -h/2) 
            item.setTransform(transform)
            item.setPos(self._current_dx, self._current_dy)

        base_op1 = cfg.get('op_vj1', 0.5)
        base_op2 = cfg.get('op_vj2', 0.3)
        
        real_op1 = base_op1
        real_op2 = base_op2

        if cfg.get('fx_reactive', False):
            if is_drop:
                real_op1 = min(1.0, max(0.0, base_op1 + (kick_env * 0.5)))
                if genre == MusicGenre.GARAGE:
                    real_op2 = base_op2 if random.random() > 0.5 else 0.0 
                else:
                    real_op2 = min(1.0, base_op2 + (snare_env * 0.6))
            else:
                real_op1 = min(1.0, max(0.0, base_op1 + (energy * 0.2) - 0.1))
                real_op2 = min(1.0, base_op2 + (bass_env * 0.3))

        self.vj1_item_A.setOpacity(real_op1 * self.vj1_cf)
        self.vj1_item_B.setOpacity(real_op1 * (1.0 - self.vj1_cf))
        
        self.vj2_item_A.setOpacity(real_op2 * self.vj2_cf)
        self.vj2_item_B.setOpacity(real_op2 * (1.0 - self.vj2_cf))

        if cfg.get('fx_text', True):
            self.hud.show_all()
            self.hud.update(state, kick_env, snare_env, w, h, cfg)
        else: 
            self.hud.hide_all()

# ============================================================================
# [Main Control Panel UI - Pro Edition]
# ============================================================================
class RoundedImageLabel(QLabel):
    def __init__(self, size=150, parent=None):
        super().__init__(parent)
        self.target_size = size
        self.setFixedSize(size, size)
        self.setPixmap(self.create_placeholder())
    def create_placeholder(self):
        img = QPixmap(self.target_size, self.target_size)
        img.fill(QColor("#111")); p = QPainter(img)
        p.setPen(QColor("#555")); p.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, "NO COVER"); p.end()
        return self._round(img)
    def set_image(self, data):
        if not data: self.setPixmap(self.create_placeholder()); return
        pix = QPixmap.fromImage(QImage.fromData(data)).scaled(self.target_size, self.target_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self._round(pix))
    def _round(self, pix):
        out = QPixmap(self.size()); out.fill(Qt.GlobalColor.transparent)
        p = QPainter(out); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath(); path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        p.setClipPath(path); p.drawPixmap(0, 0, pix); p.end()
        return out

class MaterialOrchestrator(QThread):
    trigger_search = pyqtSignal(str, str) 
    
    def __init__(self, parent_controller):
        super().__init__()
        self.controller = parent_controller
        self.running = True
        
    def run(self):
        while self.running:
            time.sleep(1.0)
            if not getattr(self.controller, 'engines_ready', False):
                continue
            state = vj_manager.get_state()
            if state.get("macro_swap_trigger", False):
                genre = state.get("genre", MusicGenre.UNKNOWN)
                vibe = state.get("vibe", EnergyVibe.CHILL)
                self.controller.log(f"🔄 <b>[智能中控]</b> 检测到乐段突变或满32拍，重组素材矩阵...")
                self.controller.trigger_auto_vj_swap(genre, vibe)

class ControlCenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.resize(1300, 950)
        self.is_main_processing = False
        self.slider_locked = False
        self.bpm_locked = False
        self.current_orig_bpm = 120.0 
        self.audio_orig_duration_ms = 0.0 
        self.active_workers = [] 
        
        threading.Thread(target=self._start_proxy_server, daemon=True).start()
        threading.Thread(target=vdj_polling_worker, daemon=True).start()
        
        self.obs_window = OBSVideoWindow()
        self.obs_window.show() 
        self.obs_window.player_main.positionChanged.connect(self.sync_progress)
        self.obs_window.player_main.durationChanged.connect(self.sync_duration)

        self.setup_ui()
        self.start_vdj_monitor()
        self.check_vdj_network()
        
        QTimer.singleShot(2000, self.safe_delayed_start)

        self.engines_ready = False

        self.vdj_poller = VDJPoller()
        self.vdj_poller.vdj_state_signal.connect(self.on_vdj_state_received)
        self.vdj_poller.network_ok_signal.connect(lambda: self.log("✅ VDJ 通信节点正常。物理控制已接管。"))
        self.vdj_poller.network_error_signal.connect(lambda e: self.log(f"⚠️ VDJ Network 连接异常: {e}"))
        self.vdj_poller.start()

        self.orchestrator = MaterialOrchestrator(self)
        self.orchestrator.start()

    def browse_vdj_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择 VirtualDJ 目录", self.ipt_path.text())
        if path: 
            self.ipt_path.setText(path)

    def apply_vdj_settings(self):
        APP_CONFIG["vdj_port"] = self.ipt_port.text().strip()
        APP_CONFIG["vdj_path"] = self.ipt_path.text().strip()
        save_config()
        
        if hasattr(self, 'vdj_watcher') and self.vdj_watcher.isRunning():
            self.vdj_watcher.running = False
            self.vdj_watcher.quit() 
            QTimer.singleShot(500, self.start_vdj_monitor)
        else:
            self.start_vdj_monitor()
        
        if hasattr(self, 'vdj_poller'):
            self.vdj_poller.network_ok = False
            
        self.log(f"🔄 核心引擎配置已更新！新端口: {APP_CONFIG['vdj_port']}, 新路径: {APP_CONFIG['vdj_path']}")
        QMessageBox.information(self, "配置已应用", f"端口已切换为 {APP_CONFIG['vdj_port']}\n路径已切换为:\n{APP_CONFIG['vdj_path']}\n\n系统正在后台尝试重新握手...")

    def _start_proxy_server(self):
        try:
            server = ThreadedHTTPServer(("127.0.0.1", PROXY_PORT), MultiChannelProxy)
            server.serve_forever()
        except Exception as e: print(f"Proxy Server failed: {e}")

    def check_vdj_network(self):
        self.log("📡 检测本地虚拟音频节点状态...")
        try:
            r = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=get_clock", timeout=1.0)
            if r.status_code == 200:
                self.log("✅ 音频节点握手成功！")
                if hasattr(self, 'vdj_poller'): self.vdj_poller.network_ok = True
        except Exception as e: self.log(f"❌ <b>VDJ Network 未连接！</b>")

    def fmt_time(self, ms): 
        if ms is None or math.isnan(ms) or math.isinf(ms): return "00:00"
        sign = "-" if ms < 0 else ""
        ms = abs(ms)
        return f"{sign}{int(ms)//60000:02d}:{(int(ms)%60000)//1000:02d}"

    def on_vdj_state_received(self, state):
        if not self.cb_sync.isChecked(): return
        try:
            is_playing = state.get('is_playing', False)
            target_rate = state.get('pitch', 1.0)
            pos_ratio = state.get('pos_ratio', -1.0)
            cur_bpm = state.get('cur_bpm', 0.0)
            orig_bpm = state.get('orig_bpm', 0.0)
            genre = state.get('genre', MusicGenre.UNKNOWN)
            vibe = state.get('vibe', EnergyVibe.CHILL)
            
            self.lbl_genre.setText(f"Style: {genre.value}")
            self.lbl_vibe.setText(f"Energy: {vibe.value}")
            
            if orig_bpm > 0: self.current_orig_bpm = orig_bpm
            p_main = self.obs_window.player_main
            my_state = p_main.playbackState() == QMediaPlayer.PlaybackState.PlayingState
            current_rate = p_main.playbackRate()
            current_video_pos = p_main.position()
            vid_duration = p_main.duration()

            if getattr(self.obs_window, 'needs_initial_sync', False):
                if vid_duration <= 0:
                    if is_playing and not my_state: p_main.play()
                    elif not is_playing and my_state: p_main.pause()
                    return 

            if not self.bpm_locked and orig_bpm > 0:
                slider_val = int(cur_bpm * 10)
                if abs(self.bpm_slider.value() - slider_val) > 1:
                    self.bpm_slider.blockSignals(True)
                    self.bpm_slider.setValue(slider_val)
                    self.lbl_bpm_val.setText(f"{cur_bpm:.1f}")
                    self.bpm_slider.blockSignals(False)

            threshold_sec = 40
            try:
                val = int(self.ipt_threshold.text().strip())
                if val > 0: threshold_sec = val
            except Exception: pass
            
            is_background_mode = False
            if vid_duration > 0 and self.audio_orig_duration_ms > 0:
                if abs(vid_duration - self.audio_orig_duration_ms) > threshold_sec * 1000:
                    is_background_mode = True

            if is_background_mode:
                if abs(current_rate - 1.0) > 0.01: p_main.setPlaybackRate(1.0)
                
                if getattr(self.obs_window, 'needs_initial_sync', False):
                    self.obs_window.needs_initial_sync = False
                    if is_playing: p_main.play()
                    else: p_main.pause()
                    return
                
                if is_playing and not my_state: p_main.play()
                elif not is_playing and my_state: p_main.pause()
                
            elif vid_duration > 0 and self.audio_orig_duration_ms > 0 and pos_ratio >= 0:
                base_rate = vid_duration / self.audio_orig_duration_ms
                final_rate = target_rate * base_rate
                if math.isnan(final_rate) or math.isinf(final_rate) or final_rate <= 0.01: final_rate = 1.0
                if abs(current_rate - final_rate) > 0.01: p_main.setPlaybackRate(final_rate)
                expected_video_pos = pos_ratio * vid_duration
                
                if getattr(self.obs_window, 'needs_initial_sync', False):
                    p_main.setPosition(int(expected_video_pos))
                    self.obs_window.needs_initial_sync = False
                    if is_playing: p_main.play()
                    else: p_main.pause()
                    self.sync_progress(expected_video_pos)
                    return
                
                if is_playing and not my_state: p_main.play()
                elif not is_playing and my_state: p_main.pause()
                        
                drift = expected_video_pos - current_video_pos
                if not self.slider_locked and not self.bpm_locked:
                    if is_playing:
                        if abs(drift) > 4000:
                            p_main.setPosition(int(expected_video_pos))
                            self.slider.setValue(int(expected_video_pos * 1000 / vid_duration))
                    else:
                        if abs(drift) > 300:
                            p_main.setPosition(int(expected_video_pos))
                            self.slider.setValue(int(expected_video_pos * 1000 / vid_duration))
                            p_main.pause()
            else:
                if orig_bpm > 0 and abs(current_rate - target_rate) > 0.01: p_main.setPlaybackRate(target_rate)
                if is_playing and not my_state: p_main.play()
                elif not is_playing and my_state: p_main.pause()
        except Exception: pass 

    def safe_delayed_start(self):
        self.engine_starter = EngineStarter()
        self.engine_starter.log_signal.connect(self.log)
        self.engine_starter.finished_signal.connect(self.on_engine_started)
        self.engine_starter.start()

    def on_engine_started(self):
        self.engines_ready = True
        self.monitor = BrowserMonitor() 
        self.monitor.video_detected.connect(self.on_manual_click)
        self.monitor.start()

    def setup_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QHBoxLayout(cw)
        layout.setContentsMargins(15, 15, 15, 15)
        left_panel, right_panel = QVBoxLayout(), QVBoxLayout()
        layout.addLayout(left_panel, 5); layout.addLayout(right_panel, 6)
        
        header = QLabel(APP_NAME); header.setObjectName("Title")
        left_panel.addWidget(header)
        
        info_frame = QFrame(objectName="Panel")
        info_l = QHBoxLayout(info_frame)
        self.cover = RoundedImageLabel(140)
        info_l.addWidget(self.cover)
        
        txt_l = QVBoxLayout()
        self.lbl_title = QLabel("System Standby"); self.lbl_title.setObjectName("SongTitle"); self.lbl_title.setWordWrap(True)
        
        tags_l = QHBoxLayout()
        self.lbl_genre = QLabel("Style: Unknown"); self.lbl_genre.setObjectName("GenreLabel")
        self.lbl_vibe = QLabel("Energy: Intro"); self.lbl_vibe.setObjectName("VibeLabel")
        tags_l.addWidget(self.lbl_genre); tags_l.addWidget(self.lbl_vibe); tags_l.addStretch()
        
        self.lbl_status = QLabel("Awaiting input...")
        self.lbl_orig_duration = QLabel("Duration: --:--")
        self.lbl_orig_duration.setStyleSheet("font-family: Consolas; color: #4CAF50;")
        txt_l.addWidget(self.lbl_title); txt_l.addLayout(tags_l); txt_l.addWidget(self.lbl_status); txt_l.addWidget(self.lbl_orig_duration); txt_l.addStretch()
        info_l.addLayout(txt_l)
        left_panel.addWidget(info_frame)
        
        pg = QGroupBox("MASTER TRANSPORT (主控台)")
        pg_l = QHBoxLayout(pg)
        ctrl_l = QVBoxLayout()
        btn_g = QHBoxLayout()
        self.btn_play = QPushButton("⏯ PLAY / PAUSE")
        self.btn_loop = QPushButton("🔁 LOOP MODE"); self.btn_loop.setCheckable(True); self.btn_loop.setChecked(True)
        self.btn_stop = QPushButton("⬛ BLACKOUT", objectName="DangerBtn")
        btn_g.addWidget(self.btn_play); btn_g.addWidget(self.btn_loop); btn_g.addWidget(self.btn_stop)
        ctrl_l.addLayout(btn_g)
        
        prog_layout = QHBoxLayout()
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.sliderPressed.connect(self.lock_s); self.slider.sliderReleased.connect(self.seek_p)
        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setStyleSheet("font-family: Consolas; font-weight: bold; color: #FF0055;")
        prog_layout.addWidget(self.slider); prog_layout.addWidget(self.lbl_time)
        ctrl_l.addLayout(prog_layout)
        pg_l.addLayout(ctrl_l, stretch=5)
        
        bpm_l = QVBoxLayout()
        self.lbl_bpm_val = QLabel("120.0"); self.lbl_bpm_val.setStyleSheet("font-family: Consolas; font-size: 20px; font-weight:bold; color: #00F0FF;")
        self.bpm_slider = QSlider(Qt.Orientation.Vertical, objectName="BPMSlider")
        self.bpm_slider.setRange(0, 3000); self.bpm_slider.setValue(1200)
        self.bpm_slider.sliderPressed.connect(self.lock_bpm); self.bpm_slider.sliderReleased.connect(self.release_bpm); self.bpm_slider.valueChanged.connect(self.on_local_bpm_changed)
        bpm_l.addWidget(QLabel("BPM", alignment=Qt.AlignmentFlag.AlignCenter)); bpm_l.addWidget(self.lbl_bpm_val, alignment=Qt.AlignmentFlag.AlignCenter)
        bpm_l.addWidget(self.bpm_slider, alignment=Qt.AlignmentFlag.AlignHCenter)
        pg_l.addLayout(bpm_l, stretch=1)
        left_panel.addWidget(pg)
        
        mode_frame = QFrame(objectName="Panel")
        mode_l = QVBoxLayout(mode_frame)
        self.btn_auto = QRadioButton("完全自动感知 VDJ (Auto VJ Mode)"); self.btn_auto.setChecked(True)
        self.btn_semi = QRadioButton("半自动人工控制")
        hl1 = QHBoxLayout(); hl1.addWidget(self.btn_auto); hl1.addWidget(self.btn_semi); hl1.addStretch()
        mode_l.addLayout(hl1)

        algo_layout = QHBoxLayout()
        self.algo_group = QButtonGroup(self)
        
        self.rb_mode1 = QRadioButton("1:绝对精准")
        self.rb_mode1.setStyleSheet("color: #4CAF50;")
        
        self.rb_mode2 = QRadioButton("2:智能均衡")
        self.rb_mode2.setStyleSheet("color: #00F0FF;")
        self.rb_mode2.setChecked(True)
        
        self.rb_mode3 = QRadioButton("3:冷门文本")
        self.rb_mode3.setStyleSheet("color: #FF0055;")
        
        self.rb_mode4 = QRadioButton("4:时长优先")
        self.rb_mode4.setStyleSheet("color: #FF9800;")
        
        self.algo_group.addButton(self.rb_mode1, 1)
        self.algo_group.addButton(self.rb_mode2, 2)
        self.algo_group.addButton(self.rb_mode3, 3)
        self.algo_group.addButton(self.rb_mode4, 4)
        
        algo_layout.addWidget(self.rb_mode1)
        algo_layout.addWidget(self.rb_mode2)
        algo_layout.addWidget(self.rb_mode3)
        algo_layout.addWidget(self.rb_mode4)
        algo_layout.addStretch()
        mode_l.addLayout(algo_layout)
        
        self.cb_sync = QCheckBox("开启极致物理映射同步"); self.cb_sync.setChecked(True)
        self.ipt_threshold = QLineEdit("40"); self.ipt_threshold.setFixedWidth(50)
        hl2 = QHBoxLayout()
        hl2.addWidget(self.cb_sync); hl2.addStretch()
        hl2.addWidget(QLabel("脱离阀值(s):")); hl2.addWidget(self.ipt_threshold)
        mode_l.addLayout(hl2)
        
        self.ipt = QLineEdit(placeholderText="手动指令/直接输入URL...")
        self.ipt.returnPressed.connect(self.manual_start)
        hl3 = QHBoxLayout()
        btn_grab = QPushButton("抓取前台网页"); btn_grab.clicked.connect(self.grab_current)
        btn_show = QPushButton("弹射渲染大屏"); btn_show.clicked.connect(self.obs_window.show)
        hl3.addWidget(self.ipt); hl3.addWidget(btn_grab); hl3.addWidget(btn_show)
        mode_l.addLayout(hl3)
        left_panel.addWidget(mode_frame)
        
        conn_group = QGroupBox("VDJ CONNECTION (底层连接设置)")
        conn_l = QHBoxLayout(conn_group)
        
        self.ipt_port = QLineEdit(str(APP_CONFIG["vdj_port"]))
        self.ipt_port.setFixedWidth(50)
        self.ipt_path = QLineEdit(APP_CONFIG["vdj_path"])
        
        btn_browse = QPushButton("📁 浏览")
        btn_apply = QPushButton("✅ 应用并重连")
        
        conn_l.addWidget(QLabel("端口:"))
        conn_l.addWidget(self.ipt_port)
        conn_l.addWidget(QLabel("M3U历史路径:"))
        conn_l.addWidget(self.ipt_path)
        conn_l.addWidget(btn_browse)
        conn_l.addWidget(btn_apply)
        left_panel.addWidget(conn_group)
        
        btn_browse.clicked.connect(self.browse_vdj_path)
        btn_apply.clicked.connect(self.apply_vdj_settings)
        left_panel.addStretch()
        
        tabs = QTabWidget()
        
        tab_engine = QWidget()
        eng_l = QVBoxLayout(tab_engine)
        self.cb_vj_mode1 = QCheckBox("本地图层库: 自动检索 VJ Materials 叠加"); self.cb_vj_mode1.setChecked(True)
        self.cb_vj_mode3 = QCheckBox("云端 VJ 层: 唤醒无头浏览器智能爬取背景库"); self.cb_vj_mode3.setChecked(True)
        self.cb_vj_trilayer = QCheckBox("🔥 终极三核混合: 同时叠加 主图层 + 氛围层 + 粒子特效层"); self.cb_vj_trilayer.setChecked(True)
        self.cb_vj_mode2 = QCheckBox("启动智能鼓点编排引擎 (Rhythm-Bind AI)"); self.cb_vj_mode2.setChecked(True)
        self.cb_vj_mode2.stateChanged.connect(self._push_vj_config)
        eng_l.addWidget(self.cb_vj_mode1); eng_l.addWidget(self.cb_vj_mode3); eng_l.addWidget(self.cb_vj_trilayer); eng_l.addWidget(self.cb_vj_mode2)
        eng_l.addStretch()
        tabs.addTab(tab_engine, "🛠 SYSTEM MATRIX")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        tab_fx = QWidget()
        fx_l = QVBoxLayout(tab_fx)
        
        grp_trans = QGroupBox("PHYSICS & TRANSFORM (物理变形引擎)")
        gl_trans = QGridLayout(grp_trans)
        self.cb_fx_mirror = QCheckBox("节拍动态镜像/翻转 (Kick X/Y Mirror)"); self.cb_fx_mirror.setChecked(True)
        self.cb_fx_rotate = QCheckBox("LFO正弦波摇摆/自旋 (BPM Rotation)"); self.cb_fx_rotate.setChecked(True)
        self.cb_fx_shake = QCheckBox("踢鼓物理缩放弹跳 (Kick Scale Bounce)"); self.cb_fx_shake.setChecked(True)
        gl_trans.addWidget(self.cb_fx_mirror, 0, 0); gl_trans.addWidget(self.cb_fx_rotate, 0, 1)
        gl_trans.addWidget(self.cb_fx_shake, 1, 0)
        fx_l.addWidget(grp_trans)

        grp_color = QGroupBox("COLOR & GLITCH (色彩与故障)")
        gl_color = QGridLayout(grp_color)
        self.cb_fx_hue = QCheckBox("鼓点触发霓虹色域映射 (Hue Drift)"); self.cb_fx_hue.setChecked(True)
        self.cb_fx_glitch = QCheckBox("军鼓触发撕裂畸变效果 (Snare Shear/Glitch)"); self.cb_fx_glitch.setChecked(True)
        self.cb_fx_flash = QCheckBox("节拍光学高能爆闪遮罩 (Strobe Mask)"); self.cb_fx_flash.setChecked(True)
        self.cb_fx_reactive = QCheckBox("全局动态透明度呼吸混合 (LFO Opacity)"); self.cb_fx_reactive.setChecked(True)
        gl_color.addWidget(self.cb_fx_hue, 0, 0); gl_color.addWidget(self.cb_fx_glitch, 0, 1)
        gl_color.addWidget(self.cb_fx_flash, 1, 0); gl_color.addWidget(self.cb_fx_reactive, 1, 1)
        fx_l.addWidget(grp_color)

        grp_txt = QGroupBox("CYBER HUD & TYPOGRAPHY (全息排版)")
        gl_txt = QGridLayout(grp_txt)
        self.cb_fx_text = QCheckBox("歌曲状态赛博仪表盘 (Cyberpunk HUD)"); self.cb_fx_text.setChecked(True)
        self.cb_fx_mixer_hud = QCheckBox("硬件混音台状态监测 (VOL/LOOP/FX)"); self.cb_fx_mixer_hud.setChecked(True)
        gl_txt.addWidget(self.cb_fx_text, 0, 0)
        gl_txt.addWidget(self.cb_fx_mixer_hud, 1, 0) 
        fx_l.addWidget(grp_txt)

        grp_mix = QGroupBox("HARDWARE MIXER (图层透明度调音台)")
        gl_mix = QVBoxLayout(grp_mix)
        btn_layout = QHBoxLayout()
        self.btn_toggle_vj1 = QPushButton("🟢 VJ1 (背景层) ON")
        self.btn_toggle_vj1.setCheckable(True)
        self.btn_toggle_vj1.setChecked(True)
        self.btn_toggle_vj1.setStyleSheet("QPushButton:checked { background-color: #00F0FF; color: black; }")
        
        self.btn_toggle_vj2 = QPushButton("🟢 VJ2 (粒子层) ON")
        self.btn_toggle_vj2.setCheckable(True)
        self.btn_toggle_vj2.setChecked(True)
        self.btn_toggle_vj2.setStyleSheet("QPushButton:checked { background-color: #FF0055; color: black; }")
        
        btn_layout.addWidget(self.btn_toggle_vj1)
        btn_layout.addWidget(self.btn_toggle_vj2)
        gl_mix.addLayout(btn_layout)
        op1_l = QHBoxLayout()
        self.sld_op_vj1 = QSlider(Qt.Orientation.Horizontal); self.sld_op_vj1.setRange(0, 100); self.sld_op_vj1.setValue(60)
        op1_l.addWidget(QLabel("VJ1 (氛围层) 基准明度:")); op1_l.addWidget(self.sld_op_vj1)
        op2_l = QHBoxLayout()
        self.sld_op_vj2 = QSlider(Qt.Orientation.Horizontal); self.sld_op_vj2.setRange(0, 100); self.sld_op_vj2.setValue(45)
        op2_l.addWidget(QLabel("VJ2 (粒子层) 基准明度:")); op2_l.addWidget(self.sld_op_vj2)
        gl_mix.addLayout(op1_l); gl_mix.addLayout(op2_l)
        fx_l.addWidget(grp_mix)

        for cb in [self.cb_fx_text, self.cb_fx_shake, self.cb_fx_flash, self.cb_fx_reactive, 
                   self.cb_fx_mirror, self.cb_fx_rotate, self.cb_fx_hue, self.cb_fx_glitch]:
            cb.stateChanged.connect(self._push_vj_config)
        self.sld_op_vj1.valueChanged.connect(self._push_vj_config)
        self.sld_op_vj2.valueChanged.connect(self._push_vj_config)

        scroll.setWidget(tab_fx)
        tabs.addTab(scroll, "🎛 PRO VJ RACK")
        
        right_panel.addWidget(tabs, stretch=5)
        self._push_vj_config()
        
        right_panel.addWidget(QLabel("🔥 Engine Runtime Log"))
        self.log_area = QPlainTextEdit(); self.log_area.setReadOnly(True)
        right_panel.addWidget(self.log_area, stretch=2)
        
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_loop.toggled.connect(self.toggle_loop)
        self.btn_stop.clicked.connect(self.obs_window.blackout)

    def trigger_auto_vj_swap(self, genre, vibe, update_vj1=True, update_vj2=True):
        if not self.cb_vj_mode3.isChecked(): return

        pro_vj1_kws = ["4K VJ 循环 视觉 素材", "舞台 动态 抽象 背景", "无缝 循环 几何 视觉"]
        pro_vj2_kws = ["动态 粒子 光斑 特效", "镜头 漏光 叠加 视频"]
        
        if genre == MusicGenre.EDM or genre == MusicGenre.DUBSTEP:
            if vibe == EnergyVibe.DROP:
                pro_vj1_kws = ["硬核 几何 隧道 快速 循环", "高能 粒子 放射 爆闪 VJ", "赛博朋克 故障 视觉"]
                pro_vj2_kws = ["红色 警告 扫描 叠加 循环", "高频 爆闪 频闪 叠加 素材"]
            else:
                pro_vj1_kws = ["科幻 通道 缓慢 循环", "暗色 几何 VJ 素材"]
                pro_vj2_kws = ["数字 故障 撕裂 叠加 特效", "矩阵 代码 瀑布 叠加"]
                
        elif genre == MusicGenre.GARAGE or genre == MusicGenre.HOUSE:
            pro_vj1_kws = ["街头 涂鸦 动感 VJ 背景", "黑白 故障 循环 视觉", "极简 抽象 循环 视觉"]
            pro_vj2_kws = ["老电视 噪点 抽帧 叠加 素材", "VHS 录像带 干扰 叠加 特效"]
            
        elif genre == MusicGenre.TRANCE or genre == MusicGenre.POP or genre == MusicGenre.ANISONG:
            if vibe == EnergyVibe.BUILDUP:
                pro_vj1_kws = ["光速 穿梭 虫洞 VJ 素材", "极光 粒子 加速 视觉"]
            else:
                pro_vj1_kws = ["唯美 星空 宇宙 循环 背景", "流体 渐变 抽象 VJ 素材"]
                pro_vj2_kws = ["柔和 光晕 漏光 叠加 特效", "梦幻 星点 闪烁 叠加 素材"]

        filter_suffix = " 素材 "
        
        if update_vj1:
            kw1 = random.choice(pro_vj1_kws) + filter_suffix
            self.log(f"☁️ [云端填补] 注入VJ1底层背景指令: <span style='color:#FF0055'>{kw1}</span>")
            self.start_process(kw1, TaskMode.AUTO, task_type="vj1_B" if self.obs_window.active_vj1_deck=="A" else "vj1_A")

        if update_vj2 and self.cb_vj_trilayer.isChecked():
            kw2 = random.choice(pro_vj2_kws) + filter_suffix
            self.log(f"☁️ [云端填补] 注入VJ2粒子特效指令: <span style='color:#00F0FF'>{kw2}</span>")
            self.start_process(kw2, TaskMode.AUTO, task_type="vj2_B" if self.obs_window.active_vj2_deck=="A" else "vj2_A")
            
    def _push_vj_config(self):
        auto_fx = self.cb_vj_mode2.isChecked()
        self.obs_window.vj_config = {
            'auto_fx': auto_fx,
            'fx_text': self.cb_fx_text.isChecked() if auto_fx else False,
            'fx_mixer_hud': self.cb_fx_mixer_hud.isChecked() if auto_fx else False,
            'fx_shake': self.cb_fx_shake.isChecked() if auto_fx else False,
            'fx_flash': self.cb_fx_flash.isChecked() if auto_fx else False,
            'fx_reactive': self.cb_fx_reactive.isChecked() if auto_fx else False,
            'fx_mirror': self.cb_fx_mirror.isChecked() if auto_fx else False,
            'fx_rotate': self.cb_fx_rotate.isChecked() if auto_fx else False,
            'fx_hue': self.cb_fx_hue.isChecked() if auto_fx else False,
            'fx_glitch': self.cb_fx_glitch.isChecked() if auto_fx else False,
            'op_vj1': (self.sld_op_vj1.value() / 100.0) if self.btn_toggle_vj1.isChecked() else 0.0,
            'op_vj2': (self.sld_op_vj2.value() / 100.0) if self.btn_toggle_vj2.isChecked() else 0.0
        }

    def lock_s(self): self.slider_locked = True
    def seek_p(self):
        d = self.obs_window.player_main.duration()
        if d > 0: self.obs_window.player_main.setPosition(int(self.slider.value() * d / 1000))
        self.slider_locked = False
    def lock_bpm(self): self.bpm_locked = True
    def release_bpm(self): self.bpm_locked = False
    
    def on_local_bpm_changed(self, val):
        new_bpm = val / 10.0
        self.lbl_bpm_val.setText(f"{new_bpm:.1f}")
        if hasattr(self, 'current_orig_bpm') and self.current_orig_bpm > 0:
            target_rate = new_bpm / self.current_orig_bpm
            vid_duration = self.obs_window.player_main.duration()
            threshold_sec = 40
            try:
                val_t = int(self.ipt_threshold.text().strip())
                if val_t > 0: threshold_sec = val_t
            except Exception: pass
            
            if vid_duration > 0 and self.audio_orig_duration_ms > 0:
                if abs(vid_duration - self.audio_orig_duration_ms) > threshold_sec * 1000: final_rate = 1.0 
                else: final_rate = target_rate * (vid_duration / self.audio_orig_duration_ms)
            else: final_rate = target_rate
                
            if math.isnan(final_rate) or math.isinf(final_rate): final_rate = 1.0
            self.obs_window.player_main.setPlaybackRate(max(0.01, min(final_rate, 4.0)))

        if self.bpm_locked and getattr(self.vdj_poller, 'network_ok', False):
            cmd = f"deck%20active%20pitch%20{new_bpm}%20bpm"
            try: threading.Thread(target=lambda: requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/execute?script={cmd}", timeout=0.2), daemon=True).start()
            except Exception: pass

    def sync_progress(self, p):
        if not self.slider_locked:
            d = self.obs_window.player_main.duration()
            if d > 0:
                self.slider.setValue(int(p * 1000 / d))
                self.update_t(p, d)
            
    def sync_duration(self, d):
        self.update_t(self.obs_window.player_main.position(), d)
        
    def update_t(self, c, t):
        rate = self.obs_window.player_main.playbackRate()
        if math.isnan(rate) or math.isinf(rate) or rate <= 0.01: rate = 1.0
        real_c, real_t = c / rate, t / rate
        self.lbl_time.setText(f"{self.fmt_time(real_c)} / {self.fmt_time(real_t)}")
        
    def toggle_play(self):
        if self.obs_window.player_main.playbackState() == QMediaPlayer.PlaybackState.PlayingState: 
            self.obs_window.player_main.pause()
        else: 
            self.obs_window.player_main.play()
            
    def toggle_loop(self, c):
        self.obs_window.is_looping = c
        self.btn_loop.setText(f"🔁 LOOP MODE" if c else "NO LOOP")
        
    def log(self, m):
        self.log_area.appendHtml(f"<span style='color:#777'>[{datetime.now().strftime('%H:%M:%S')}]</span> {m}")
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())
        
    def start_vdj_monitor(self):
        path = APP_CONFIG["vdj_path"]
        if os.path.exists(path):
            self.vdj_watcher = VDJWatcher(path)
            self.vdj_watcher.track_changed.connect(self.on_track_changed)
            self.vdj_watcher.start()
            self.log("✅ 物理磁盘队列侦听已装载。")
        else:
            self.log(f"⚠️ 未找到目录: {path}，切歌侦听失败！")
            
    def on_manual_click(self, url):
        if self.is_main_processing: return
        self.log(f"⚡ <span style='color:#00F0FF'>前端截获流媒体链接，执行注入...</span>")
        self.start_process(url, TaskMode.GRAB_CURRENT, task_type="main")
        
    def on_track_changed(self, t):
        self.log(f"<br/>🎵 [VDJ 切歌解析触发]: <b>{t}</b>")
        raw_filename, song_name, search_query, first_artist = t, t, t, ""
        target_deck = None
        local_filepath = "" 
        
        if getattr(self.vdj_poller, 'network_ok', False):
            for d in range(1, 5):
                try:
                    r_file = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{d}%20get_filepath", timeout=0.2)
                    if r_file.status_code == 200:
                        filepath = r_file.text.strip().replace('"', '').replace("'", "")
                        if filepath and t.lower() in filepath.lower():
                            target_deck = str(d); break
                except: pass
            
            if target_deck:
                try:
                    title, artist = "", ""
                    r_title = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_title", timeout=0.2)
                    if r_title.status_code == 200:
                        val = r_title.text.strip().replace('"', '').replace("'", "")
                        if val and val.lower() != "error" and val != "0": title = val
                    r_artist = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_artist", timeout=0.2)
                    if r_artist.status_code == 200:
                        val = r_artist.text.strip().replace('"', '').replace("'", "")
                        if val and val.lower() != "error" and val != "0": artist = val
                        
                    if title:
                        song_name = title  
                        if artist: first_artist = re.split(r'[、/,&，]', artist)[0].strip()
                        if first_artist: search_query = f"{song_name} {first_artist}"
                        else: search_query = song_name
                        self.log(f"💿 成功嗅探 ID3 元数据: [{song_name}] - [{first_artist}]")
                except: pass
                
                if local_filepath and os.path.exists(local_filepath):
                    try:
                        import mutagen
                        audio_meta = mutagen.File(local_filepath)
                        cover_bytes = None
                        if audio_meta is not None:
                            if hasattr(audio_meta, 'tags') and audio_meta.tags:
                                for tag in audio_meta.tags.values():
                                    if tag.__class__.__name__ == 'APIC':
                                        cover_bytes = tag.data
                                        break
                            if not cover_bytes and hasattr(audio_meta, 'pictures') and audio_meta.pictures:
                                cover_bytes = audio_meta.pictures[0].data
                            if not cover_bytes and 'covr' in audio_meta:
                                cover_bytes = bytes(audio_meta['covr'][0])
                        
                        if cover_bytes:
                            self.cover.set_image(cover_bytes)
                            self.obs_window.hud.set_cover(cover_bytes)
                            self.log("🖼️ 成功提取并渲染本地音频专辑封面！")
                        else:
                            self.cover.set_image(None)
                            self.obs_window.hud.set_cover(None)
                            
                    except ImportError:
                        self.log("⚠️ 缺少 mutagen 库，无法提取封面，请执行 pip install mutagen")
                    except Exception as e:
                        self.log(f"⚠️ 封面提取失败: {e}")
                        
        if search_query == t and " - " in t:
            parts = t.split(" - ", 1)
            p1, p2 = parts[0].strip(), parts[1].strip()
            if "、" in p2 or "," in p2 or "&" in p2: artist_part, title_part = p2, p1
            else: artist_part, title_part = p1, p2
            first_artist = re.split(r'[、/,&，]', artist_part)[0].strip()
            song_name, search_query = title_part, f"{title_part} {first_artist}"
            
        vj_manager.update_song_info(song_name, first_artist, target_deck or "active")

        vj1_assigned = False
        vj2_assigned = False
        valid_exts = {".mp4", ".webm", ".avi", ".png", ".gif"}

        if self.cb_vj_mode1.isChecked():
            if os.path.exists(VJ1_MATERIAL_DIR):
                files_vj1 = glob.glob(os.path.join(VJ1_MATERIAL_DIR, "*.*"))
                cands_vj1 = [f for f in files_vj1 if os.path.splitext(f)[1].lower() in valid_exts]
                if cands_vj1:
                    smart_vj1 = [c for c in cands_vj1 if VJHelper.clean_text_for_match(first_artist) in VJHelper.clean_text_for_match(c) or VJHelper.clean_text_for_match(song_name) in VJHelper.clean_text_for_match(c)]
                    chosen1 = random.choice(smart_vj1) if smart_vj1 else random.choice(cands_vj1)
                    self.obs_window.play_url(chosen1, channel="vj1_A")
                    self.log(f"✨ [VJ1] 挂载本地底层背景: {os.path.basename(chosen1)}")
                    vj1_assigned = True

            if self.cb_vj_trilayer.isChecked() and os.path.exists(VJ2_MATERIAL_DIR):
                files_vj2 = glob.glob(os.path.join(VJ2_MATERIAL_DIR, "*.*"))
                cands_vj2 = [f for f in files_vj2 if os.path.splitext(f)[1].lower() in valid_exts]
                if cands_vj2:
                    smart_vj2 = [c for c in cands_vj2 if VJHelper.clean_text_for_match(first_artist) in VJHelper.clean_text_for_match(c) or VJHelper.clean_text_for_match(song_name) in VJHelper.clean_text_for_match(c)]
                    chosen2 = random.choice(smart_vj2) if smart_vj2 else random.choice(cands_vj2)
                    self.obs_window.play_url(chosen2, channel="vj2_A")
                    self.log(f"✨ [VJ2] 挂载本地粒子特效: {os.path.basename(chosen2)}")
                    vj2_assigned = True

        if self.cb_vj_mode3.isChecked() and (not vj1_assigned or (self.cb_vj_trilayer.isChecked() and not vj2_assigned)):
            genre = vj_manager.get_state().get('genre', MusicGenre.UNKNOWN)
            self.log("☁️ 检测到图层空缺，呼叫云端引擎进行独立填补...")
            self.trigger_auto_vj_swap(genre, EnergyVibe.ACTIVE, update_vj1=not vj1_assigned, update_vj2=not vj2_assigned)

        if not search_query:
            search_query = song_name

        if search_query:
            self.log(f"🔍 启动主视窗音画同步检索指令: <span style='color:#FF0055'>{search_query}</span>")
            mode = TaskMode.AUTO if self.btn_auto.isChecked() else TaskMode.SEARCH_ONLY
            self.start_process(search_query, mode, song_name=song_name, raw_filename=raw_filename, task_type="main")
        else:
            self.log("⚠️ 无法获取有效曲名，主视频层搜索被跳过！")

    def manual_start(self):
        q = self.ipt.text().strip()
        mode = TaskMode.AUTO if self.btn_auto.isChecked() else TaskMode.SEARCH_ONLY
        if q:
            song_name, search_query = q, q
            if " - " in q:
                parts = q.split(" - ", 1)
                p1, p2 = parts[0].strip(), parts[1].strip()
                if "、" in p2 or "," in p2 or "&" in p2: artist_part, title_part = p2, p1
                else: artist_part, title_part = p1, p2
                first_artist = re.split(r'[、/,&，]', artist_part)[0].strip()
                song_name, search_query = title_part, f"{title_part} {first_artist}"
            self.start_process(search_query, mode, song_name=song_name, raw_filename=q, task_type="main")
        
    def grab_current(self):
        self.start_process("", TaskMode.GRAB_CURRENT, task_type="main")

    def start_process(self, q, mode: TaskMode, song_name="", raw_filename="", task_type="main"):
        if self.is_main_processing and task_type == "main": return
        if task_type == "main":
            self.is_main_processing = True
            self.lbl_status.setText("🔄 主线引擎逻辑树调度中...")
            
        has_sync = hasattr(self, 'cb_sync') and self.cb_sync.isChecked() and getattr(self.vdj_poller, 'network_ok', False)

        algo_id = 2
        if hasattr(self, 'algo_group') and self.algo_group.checkedId() != -1:
            algo_id = self.algo_group.checkedId()
            
        worker = QThread()
        logic = SearchWorker(q, song_name, raw_filename, mode, has_sync, algo_mode=algo_id, channel=task_type)
        logic.moveToThread(worker)
        self.active_workers.append((worker, logic))
        
        worker.started.connect(logic.run)
        logic.log.connect(self.log)
        logic.play_media.connect(self.on_media_ready)
        logic.update_ui.connect(self.on_ui_update)
        logic.finished.connect(self.on_process_done)
        logic.finished.connect(worker.quit)
        logic.finished.connect(logic.deleteLater)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(lambda: self.cleanup_worker(worker, logic))
        worker.start()

    def cleanup_worker(self, worker, logic):
        try: self.active_workers.remove((worker, logic))
        except Exception: pass
        
    def on_ui_update(self, d):
        if d.get("title"): self.lbl_title.setText(d["title"])
        if "cover_data" in d: 
            self.cover.set_image(d.get("cover_data"))
            self.obs_window.hud.set_cover(d.get("cover_data"))
        if "target_duration" in d:
            dur = int(d["target_duration"])
            self.audio_orig_duration_ms = d["target_duration"] * 1000.0 
            self.lbl_orig_duration.setText(f"Track Time Map: {dur//60:02d}:{dur%60:02d} ({dur}s)")
        
    def on_media_ready(self, url, m_type, channel):
        self.obs_window.play_url(url, channel=channel)
    
    def on_process_done(self, d):
        if d.get("channel") == "main":
            self.is_main_processing = False
            self.lbl_status.setText("✅ 核心视频链路就绪")
            if hasattr(self, 'monitor') and d.get("original_url"):
                clean_url = d["original_url"].split('?')[0]
                self.monitor.last_url = clean_url
            
    def closeEvent(self, event):
        if hasattr(self, 'vdj_poller'): self.vdj_poller.stop()
        if hasattr(self, 'orchestrator'): self.orchestrator.running = False
        if hasattr(self, 'monitor'): self.monitor.stop()
        self.obs_window.close()
        MultiBrowserManager.close_all() 
        super().closeEvent(event)

class VDJWatcher(QThread):
    track_changed = pyqtSignal(str) 
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.running = True
        self.last_track = ""
    def run(self):
        while self.running:
            h = os.path.join(self.path, "History")
            f_list = glob.glob(os.path.join(h, "*.m3u"))
            if f_list:
                l = max(f_list, key=os.path.getctime)
                try:
                    with open(l, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = [x.strip() for x in f if x.strip() and not x.startswith("#")]
                        if lines:
                            t = os.path.splitext(os.path.basename(lines[-1]))[0]
                            if t != self.last_track:
                                self.last_track = t
                                self.track_changed.emit(t)
                except Exception: pass 
            time.sleep(2)

if __name__ == "__main__":
    # [核心修正] 必须开启 OpenGL 上下文共享，允许视频解码帧直接在视口间流动
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = ControlCenter()
    window.show()
    sys.exit(app.exec())