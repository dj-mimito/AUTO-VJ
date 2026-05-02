import sys
import os

# ============================================================================
# [环境补丁] 强制修正库搜索路径 (解决 pip 安装后找不到模块的问题)
# ============================================================================
PI_PATH = r"d:\app\python\lib\site-packages"
if PI_PATH not in sys.path:
    sys.path.append(PI_PATH)

import time
import glob
import threading
import subprocess
import requests
import re
import traceback
import http.server
import socketserver
import math
import random
import tempfile
import shutil
import json
from PyQt6.QtGui import QIcon
from enum import Enum
from datetime import datetime
from urllib.parse import urlparse, parse_qs, quote

# ============================================================================
# [核心修复] - 全局致命异常捕获器 (杜绝无提示默默闪退)
# ============================================================================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    拦截所有未捕获的导致崩溃的异常，并强制弹出错误窗口，而不是直接让程序消失！
    """
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print("Fatal Error:\n", error_msg, file=sys.stderr)
    
    if QApplication.instance():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("致命崩溃拦截 (Fatal Crash)")
        msg.setText("程序发生了未捕获的严重错误！\n请截图并将下方的详细信息反馈排错。")
        msg.setDetailedText(error_msg)
        msg.exec()

# 挂载全局钩子
sys.excepthook = global_exception_handler

# --- 修复代理/VPN引起的 SSL EOF 下载错误 ---
import ssl
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

# --- PyQt6 Imports ---
from PyQt6.QtCore import (Qt, pyqtSignal, QThread, QObject, QUrl, QCoreApplication, QTimer, QSizeF)
from PyQt6.QtGui import (QPixmap, QColor, QPainter, QPainterPath, QImage, QFont, QKeySequence, QShortcut)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QPushButton, QLineEdit, QFileDialog,
                             QFrame, QButtonGroup, QPlainTextEdit, QGroupBox, QGridLayout, QSlider, QMessageBox, QCheckBox, QSizePolicy, QRadioButton, QGraphicsOpacityEffect, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsProxyWidget)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem

# --- Web Automation Imports ---
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import yt_dlp
    # [核心修复] 彻底移除了 webdriver_manager，避免多余的控制台刷屏日志和权限引发的崩溃
except ImportError:
    print("CRITICAL ERROR: 缺少核心依赖，请运行: pip install selenium undetected-chromedriver yt-dlp requests PyQt6")
    sys.exit(1)

# --- Spout Support (现代官方免编译版本 + 深度错误追踪) ---
HAS_SPOUT = False
SPOUT_ERROR_MSG = ""
try:
    import spoutgl
    # 尝试实例化底层对象，验证 DLL 驱动是否真的能跑通
    _test_sender = spoutgl.SpoutSender()
    _test_sender.releaseSender()
    HAS_SPOUT = True
    SPOUT_ERROR_MSG = "加载成功"
except Exception as e:
    # 这里会捕获如 DLL load failed, ModuleNotFoundError 等所有真实报错
    HAS_SPOUT = False
    SPOUT_ERROR_MSG = f"{type(e).__name__}: {str(e)}"

# ============================================================================
# [打包核心终极修复] 兼容 PyInstaller 6.x+ _internal 文件夹机制
# ============================================================================
def get_resource_path(relative_path):
    """获取打包后资源的绝对路径，完美兼容 PyInstaller 6+ 的 _internal 目录"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        
        # 1. 优先检查 PyInstaller 6+ 独有的 _internal 目录
        internal_path = os.path.join(base_dir, "_internal", relative_path)
        if os.path.exists(internal_path):
            return internal_path
            
        # 2. 检查单文件模式的 _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            meipass_path = os.path.join(sys._MEIPASS, relative_path)
            if os.path.exists(meipass_path):
                return meipass_path
                
        # 3. 兜底旧版释放规则
        return os.path.join(base_dir, relative_path)
        
    return os.path.join(os.path.abspath("."), relative_path)

# ============================================================================
# [Configuration & Constants]
# ============================================================================

APP_NAME = "DJ Mimito AutoVDJ "
VERSION = "1.0(加入Anirave Q群:921954533)"

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        BASE_DIR = os.path.abspath(os.getcwd())

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
APP_CONFIG = {
    "vdj_path": os.path.expanduser("~/Documents/VirtualDJ"),
    "vdj_port": "80",
    "browser_type": "chrome",
    "show_osd": True,
    "osd_song_opacity": 100,
    "osd_video_opacity": 100,
    "enable_spout": False,
    "enable_download": True,
    "extra_search_keyword": "",
    "only_search_title": False,
    "only_search_artist": False,
    "pure_keyword_mode": False  # [新增] 纯关键词模式
}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            APP_CONFIG.update(json.load(f))
    except:
        pass

def save_config():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(APP_CONFIG, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Error] 保存配置失败: {e}")

PROFILE_DIR = os.path.join(BASE_DIR, "vdj_browser_profile")
CACHE_DIR = os.path.join(BASE_DIR, "video_cache")
STATIC_COOKIE_FILE = os.path.join(BASE_DIR, "cookies.txt")

# [重点保护] 锁定驱动文件的绝对路径，防闪退
DRIVER_PATH = get_resource_path("chromedriver.exe")

os.makedirs(CACHE_DIR, exist_ok=True)
if not os.path.exists(STATIC_COOKIE_FILE):
    with open(STATIC_COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")

COLOR_BG = "#121212"
COLOR_PANEL = "#1E1E1E"
COLOR_ACCENT = "#00ADB5"  
COLOR_TEXT_MAIN = "#EEEEEE"
COLOR_TEXT_SUB = "#AAAAAA"
COLOR_BORDER = "#333333"

STYLESHEET = f"""
    QMainWindow {{ background-color: {COLOR_BG}; }}
    QWidget {{ font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; color: {COLOR_TEXT_MAIN}; }}
    QFrame#Panel {{ background-color: {COLOR_PANEL}; border-radius: 12px; border: 1px solid {COLOR_BORDER}; }}
    QLabel#Title {{ font-size: 26px; font-weight: bold; color: {COLOR_ACCENT}; }}
    QLabel#SongTitle {{ font-size: 18px; font-weight: bold; color: #FFFFFF; }}
    QLabel#Artist {{ font-size: 15px; color: {COLOR_TEXT_SUB}; }}
    QLineEdit {{ background-color: #2A2A2A; border: 1px solid {COLOR_BORDER}; border-radius: 8px; padding: 12px; color: white; font-size: 14px; }}
    QLineEdit:focus {{ border: 1px solid {COLOR_ACCENT}; }}
    QPushButton {{ background-color: #2A2A2A; border: 1px solid {COLOR_BORDER}; border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px; }}
    QPushButton:hover {{ background-color: #333333; border-color: {COLOR_ACCENT}; color: {COLOR_ACCENT}; }}
    QPushButton:checked {{ background-color: {COLOR_ACCENT}; color: #000000; border-color: {COLOR_ACCENT}; }}
    QPushButton#ActionBtn {{ background-color: #D84315; color: white; border-color: #BF360C; font-size: 15px; padding: 15px; font-weight: bold; }}
    QPushButton#ActionBtn:hover {{ background-color: #FF5722; }}
    QPushButton#CtrlBtn {{ background-color: #1A365D; color: #63B3ED; border: 1px solid #2B6CB0; border-radius: 8px; font-size: 13px; }}
    QPushButton#CtrlBtn:hover {{ background-color: #2B6CB0; color: white; }}
    QPushButton#DangerBtn {{ background-color: #7f1d1d; color: #fca5a5; border: 1px solid #991b1b; border-radius: 8px; font-size: 13px; }}
    QPushButton#DangerBtn:hover {{ background-color: #b91c1c; color: white; }}
    QGroupBox {{ border: 2px solid {COLOR_BORDER}; border-radius: 10px; margin-top: 1.5ex; font-weight: bold; color: {COLOR_ACCENT}; font-size: 14px; }}
    QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; }}
    QPlainTextEdit {{ background-color: #0A0A0A; color: #00FF00; font-family: 'Consolas', 'Monospace'; border-radius: 8px; border: 1px solid {COLOR_BORDER}; padding: 10px; font-size: 12px; }}
    
    QSlider::groove:horizontal {{ border: 1px solid #333; height: 12px; background: #111; border-radius: 6px; }}
    QSlider::handle:horizontal {{ background: {COLOR_ACCENT}; width: 24px; height: 24px; margin: -6px 0; border-radius: 12px; }}
    
    QSlider#BPMSlider::handle:horizontal {{ background: #E91E63; }}
    
    QRadioButton {{ font-weight: bold; font-size: 13px; }}
    QRadioButton::indicator {{ width: 16px; height: 16px; border-radius: 8px; border: 2px solid #555; background-color: #222; }}
    QRadioButton::indicator:checked {{ background-color: {COLOR_ACCENT}; border: 2px solid #FFF; }}
"""

def safe_float(val_str, default=0.0):
    try:
        val = float(val_str)
        if math.isnan(val) or math.isinf(val):
            return default
        return val
    except Exception:
        return default

def parse_vdj_time_to_ms(val_str):
    if not isinstance(val_str, str): 
        return None
    val = val_str.strip().replace('+', '')
    if not val or "error" in val.lower() or val.lower() == "nan":
        return None
    
    sign = -1 if val.startswith('-') else 1
    val = val.replace('-', '')
    
    if ':' in val:
        parts = val.split(':')
        try:
            if len(parts) == 3: return sign * (int(parts[0]) * 3600 + int(parts[1]) * 60 + safe_float(parts[2])) * 1000.0
            if len(parts) == 2: return sign * (int(parts[0]) * 60 + safe_float(parts[1])) * 1000.0
        except Exception:
            return None
        
    try:
        num = float(val)
        if math.isnan(num) or math.isinf(num):
            return None
        if num > 10000:
            return sign * num
        return sign * num * 1000.0
    except Exception:
        return None

def parse_views_count(text):
    """提取播放量文本，转换为实际浮点数以便排序"""
    if not text:
        return 0.0
    text = text.replace('播放', '').strip()
    multiplier = 1.0
    if '万' in text:
        multiplier = 10000.0
        text = text.replace('万', '')
    elif '亿' in text:
        multiplier = 100000000.0
        text = text.replace('亿', '')
    try:
        return float(text) * multiplier
    except Exception:
        return 0.0

def sanitize_filename(name):
    """清理文件名中的非法字符，防止保存缓存文件时报错"""
    if not isinstance(name, str):
        name = str(name)
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def clean_text_for_match(text):
    """
    清洗文本用于精准单词匹配：
    1. 彻底移除所有常见成对括号及其内部内容：() [] {} <> （） 【】 《》
    2. 移除所有标点符号和特殊字符，仅保留字母、数字、中文、日文(平/片假名)及韩文
    3. 全部转为小写并缩减多余空格
    """
    if not isinstance(text, str): 
        return ""
    text = re.sub(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}|\<[^>]*\>|（[^）]*）|【[^】]*】|《[^》]*》', ' ', text)
    # [中日韩支持]：保留了 \u3040-\u309f(平假名) \u30a0-\u30ff(片假名) \uac00-\ud7af(韩文)
    text = re.sub(r'[^\w\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', ' ', text)
    return ' '.join(text.lower().split())

# ============================================================================
# [核心逻辑] - 内网穿透代理服务器
# ============================================================================

PROXY_PORT = 48765
CURRENT_STREAM_URL = ""

# [终极伪装] 预设一个合法 UA，后续会被真实浏览器的 UA 覆盖同步，防止风控注销 Cookie
BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class BiliStreamProxy(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        pass
        
    def do_GET(self):
        global CURRENT_STREAM_URL, BROWSER_USER_AGENT
        if not CURRENT_STREAM_URL:
            self.send_response(404)
            self.end_headers()
            return

        # [打包修复] 代理推流时强行套上与登录环境一模一样的伪装外衣
        req_headers = {
            'User-Agent': BROWSER_USER_AGENT,
            'Referer': 'https://www.bilibili.com',
            'Accept-Encoding': 'identity'
        }
        
        client_range = self.headers.get('Range')
        if client_range:
            req_headers['Range'] = client_range
            
        start_byte = 0
        if client_range:
            try:
                start_byte = int(re.search(r'bytes=(\d+)-', client_range).group(1))
            except Exception:
                pass

        bytes_sent = 0
        headers_sent = False
        max_retries = 3
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    req_headers['Range'] = f'bytes={start_byte + bytes_sent}-'

                with requests.get(CURRENT_STREAM_URL, headers=req_headers, stream=True, timeout=10) as r:
                    if r.status_code not in (200, 206):
                        if not headers_sent:
                            self.send_response(r.status_code)
                            self.end_headers()
                        break
                        
                    if not headers_sent:
                        self.send_response(r.status_code)
                        for k, v in r.headers.items():
                            if k.lower() in ['content-type', 'content-length', 'content-range', 'accept-ranges']:
                                self.send_header(k, v)
                        self.end_headers()
                        headers_sent = True

                    raw_stream = r.raw
                    while True:
                        chunk = raw_stream.read(128 * 1024) 
                        if not chunk:
                            break
                        try:
                            self.wfile.write(chunk)
                            self.wfile.flush()
                        except Exception:
                            return 
                        bytes_sent += len(chunk)
                break 
            except Exception:
                time.sleep(1)

# ============================================================================
# [引擎]
# ============================================================================

class TaskMode(Enum):
    AUTO = 1          
    SEARCH_ONLY = 2   
    GRAB_CURRENT = 3  

class BrowserEngine:
    _driver = None
    _lock = threading.Lock()
    
    @classmethod
    def get_driver(cls):
        with cls._lock:
            if cls._driver is None:
                cls._init_driver()
            try:
                _ = cls._driver.window_handles
            except Exception:
                try:
                    cls._driver.quit()
                except Exception:
                    pass
                cls._init_driver()
            return cls._driver
            
    @staticmethod
    def _cleanup_processes():
        try:
            if sys.platform == "win32":
                # 清理由于连接失败可能残留的无头驱动
                subprocess.run("taskkill /f /im chromedriver.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run("taskkill /f /im vdj_chromedriver.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # [终极狙杀] 解决无限弹窗的核心：仅查杀属于我们特定配置文件的 chrome 残尸，保护用户个人日常浏览器
                try:
                    kill_cmd = r'wmic process where "name=\'chrome.exe\' and CommandLine like \'%vdj_browser_profile%\'" call terminate'
                    subprocess.run(kill_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
            time.sleep(0.3)
        except Exception:
            pass
            
    @classmethod
    def _init_driver(cls):
        cls._cleanup_processes()
        print("[Engine] 冷启动 Bilibili 环境浏览器...")
        os.makedirs(PROFILE_DIR, exist_ok=True)
        
        b_type = APP_CONFIG.get("browser_type", "chrome").lower()
        if b_type == "edge":
            try:
                from selenium.webdriver.edge.options import Options as EdgeOptions
                opts = EdgeOptions()
                opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
                opts.add_argument("--mute-audio")
                opts.add_argument("--disable-gpu")
                opts.add_argument("--no-sandbox")
                opts.add_argument(f"--remote-debugging-port={random.randint(10000, 20000)}")
                opts.add_experimental_option("excludeSwitches", ["enable-automation"])
                opts.add_experimental_option('useAutomationExtension', False)
                import selenium.webdriver
                cls._driver = selenium.webdriver.Edge(options=opts)
                cls._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                })
                cls._driver.set_window_rect(100, 100, 1280, 720)
                print("[Engine] Edge 浏览器后端已稳定运行")
                return
            except Exception as e:
                print(f"[Engine] Edge 启动失败: {e}，将回退到 Chrome...")

        # 原有 Chrome 启动逻辑：为避免 you cannot reuse the ChromeOptions object 报错，
        # 改为通过工厂函数获取全新 options 实例
        def get_chrome_options():
            opts = uc.ChromeOptions()
            opts.add_argument("--disable-gpu")
            opts.add_argument("--mute-audio")
            return opts
        
        runnable_driver_path = DRIVER_PATH
        has_local_driver = os.path.exists(DRIVER_PATH)
        
        if has_local_driver:
            temp_dir = tempfile.gettempdir()
            runnable_driver_path = os.path.join(temp_dir, "vdj_chromedriver.exe")
            try:
                shutil.copy2(DRIVER_PATH, runnable_driver_path)
            except Exception as e:
                runnable_driver_path = DRIVER_PATH
                
        try:
            if has_local_driver:
                try:
                    cls._driver = uc.Chrome(
                        options=get_chrome_options(),
                        user_data_dir=PROFILE_DIR,
                        use_subprocess=True,
                        driver_executable_path=runnable_driver_path
                    )
                except Exception as e:
                    error_msg = str(e)
                    # [自适应解析引擎] 使用正则从报错中精准抓取用户当前的 Chrome 主版本号 (例如 147)
                    match = re.search(r"Current browser version is (\d+)", error_msg)
                    if "version of chromedriver only supports" in error_msg.lower() or "session not created" in error_msg.lower():
                        v_main = int(match.group(1)) if match else None
                        cls._cleanup_processes() # 必须先杀掉刚才连接失败产生的丧尸浏览器，防止屏幕占满
                        
                        if v_main:
                            print(f"\n=======================================================")
                            print(f"🔄 [自动更新引擎] 检测到您的 Chrome 浏览器已自动升级！")
                            print(f"💡 提取到您当前的 Chrome 真实主版本号为: {v_main}")
                            print(f"🚀 正在后台激活专属通道，为您自动下载并适配 v{v_main} 驱动...")
                            print(f"⏳ 请耐心等待数十秒 (视网络情况而定)，完成后将自动恢复！")
                            print(f"=======================================================\n")
                            # [灵魂机制]：将抓取到的 v_main 传递给 undetected_chromedriver 
                            # 激活其内部隐蔽的自动下载器，完美实现终身自愈更新，且不受 exe 打包限制！
                            cls._driver = uc.Chrome(
                                options=get_chrome_options(),
                                user_data_dir=PROFILE_DIR,
                                use_subprocess=True,
                                version_main=v_main 
                            )
                        else:
                            print(f"[Engine] 无法精准识别版本，尝试让系统自动适配最新驱动...")
                            cls._driver = uc.Chrome(
                                options=get_chrome_options(),
                                user_data_dir=PROFILE_DIR,
                                use_subprocess=True
                            )
                    else:
                        raise e
            else:
                cls._driver = uc.Chrome(
                    options=get_chrome_options(),
                    user_data_dir=PROFILE_DIR,
                    use_subprocess=True
                )
                
            cls._driver.set_window_rect(100, 100, 1280, 720)
            print("[Engine] 浏览器后端已稳定运行")
        except Exception as e:
            cls._cleanup_processes() # 无论如何失败，都要狙杀丧尸浏览器，绝对不留垃圾弹窗
            raise e
            
    @classmethod
    def close(cls):
        if cls._driver:
            try:
                cls._driver.quit()
            except Exception:
                pass
            cls._driver = None

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
                if BrowserEngine._driver:
                    driver = BrowserEngine.get_driver()
                    handles = driver.window_handles
                    if handles and driver.current_window_handle != handles[-1]:
                        driver.switch_to.window(handles[-1])
                    current_url = driver.current_url
                    if "/video/BV" in current_url:
                        clean_url = current_url.split('?')[0]
                        if clean_url != self.last_url:
                            self.last_url = clean_url
                            self.video_detected.emit(clean_url)
            except Exception:
                pass
                
    def stop(self):
        self.running = False
        self.wait()

class EngineStarter(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def run(self):
        try:
            BrowserEngine.get_driver()
            self.log_signal.emit("✅ 浏览器后端及全时监控已同步在线")
            self.finished_signal.emit()
        except Exception as e:
            self.log_signal.emit(f"❌ 浏览器后端启动失败: {e}")

# ============================================================================
# [业务逻辑] - VDJ 后台安全轮询器
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
        
        # 1. 引入持久化 Session 极大降低 CPU 与网络开销，并开启重试
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=2)
        self.session.mount('http://', adapter)
        
    def run(self):
        while self.running:
            time.sleep(0.2) 
            
            if not self.network_ok:
                try:
                    # 稍微放宽心跳检测的超时时间
                    r = self.session.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=get_clock", timeout=1.0)
                    if r.status_code == 200:
                        self.network_ok = True
                        self.network_ok_signal.emit()
                except Exception:
                    pass
                continue
                
            try:
                state = {
                    'is_playing': False,
                    'pitch': 1.0,
                    'time_ms': 0.0,
                    'pos_ratio': -1.0,
                    'cur_bpm': 0.0,
                    'orig_bpm': 0.0
                }
                
                deck_str = self.current_deck
                
                # 2. 将所有 timeout=0.1 统一放宽至 timeout=1.0，防止 VDJ 繁忙时直接判定掉线
                r_play = self.session.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20play", timeout=1.0)
                if r_play.status_code == 200:
                    play_str = r_play.text.strip().lower()
                    if play_str.replace('.', '', 1).isdigit():
                        state['is_playing'] = safe_float(play_str) > 0.5
                    else:
                        state['is_playing'] = play_str in ['yes', 'true', 'on', '1']
                        
                target_rate = 1.0
                cur_bpm = 0.0
                orig_bpm = 0.0
                bpm_valid = False
                
                try:
                    r_bpm = self.session.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20get_bpm", timeout=1.0)
                    r_obpm = self.session.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20get_bpm%20%27absolute%27", timeout=1.0)
                    if r_bpm.status_code == 200 and r_obpm.status_code == 200:
                        bpm_str = r_bpm.text.strip()
                        obpm_str = r_obpm.text.strip()
                        if "error" not in bpm_str.lower() and "error" not in obpm_str.lower():
                            cur_bpm = safe_float(bpm_str)
                            orig_bpm = safe_float(obpm_str)
                            if orig_bpm > 0:
                                target_rate = cur_bpm / orig_bpm
                                bpm_valid = True
                except Exception:
                    pass
                    
                if not bpm_valid:
                    try:
                        r_pitch = self.session.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20get_pitch_value", timeout=1.0)
                        if r_pitch.status_code == 200:
                            pitch_str = r_pitch.text.strip().replace('%', '')
                            if "error" not in pitch_str.lower():
                                pitch_val = safe_float(pitch_str)
                                if pitch_val > 5.0 or pitch_val < -5.0:
                                    target_rate = 1.0 + (pitch_val / 100.0)
                                else:
                                    target_rate = pitch_val if pitch_val > 0.01 else 1.0
                                orig_bpm = 120.0
                                cur_bpm = orig_bpm * target_rate
                    except Exception:
                        pass
                        
                if math.isnan(target_rate) or math.isinf(target_rate):
                    target_rate = 1.0
                    
                state['pitch'] = max(0.01, min(target_rate, 4.0)) 
                state['cur_bpm'] = cur_bpm
                state['orig_bpm'] = orig_bpm
                        
                r_pos = self.session.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20get_position", timeout=1.0)
                if r_pos.status_code == 200:
                    pos_str = r_pos.text.strip()
                    if "error" not in pos_str.lower():
                        val = safe_float(pos_str, -1.0)
                        if val >= 0:
                            state['pos_ratio'] = val
                            
                r_time = self.session.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{deck_str}%20get_time%20%27absolute%27", timeout=1.0)
                if r_time.status_code == 200:
                    parsed_ms = parse_vdj_time_to_ms(r_time.text)
                    if parsed_ms is not None:
                        state['time_ms'] = parsed_ms
                            
                self.vdj_state_signal.emit(state)
            except Exception as e:
                self.network_ok = False
                self.network_error_signal.emit(str(e))
                # 3. 错峰避让：如果发生碰撞掉线，随机休眠 0.2~0.5 秒再继续，错开并发峰值
                time.sleep(random.uniform(0.2, 0.5))
                
    def stop(self):
        self.running = False
        self.wait()

# ============================================================================
# [业务逻辑] - Bilibili 推流解析
# ============================================================================

class SearchWorker(QObject):
    finished = pyqtSignal(dict)
    log = pyqtSignal(str)
    play_media = pyqtSignal(str, str)
    update_ui = pyqtSignal(dict)      
    
    def __init__(self, query, song_name, raw_filename, mode: TaskMode, use_vdj_sync=False, algo_mode=2, enable_download=True):
        super().__init__()
        self.query = query
        self.song_name = song_name  
        self.raw_filename = raw_filename  
        self.mode = mode
        self.use_vdj_sync = use_vdj_sync
        self.algo_mode = algo_mode # 1:精准 2:智能均衡 3:语义优先 4:时长优先 5:完全匹配
        self.enable_download = enable_download

    def run(self):
        result_data = {"success": False, "title": "Bili Video", "cover_data": None, "original_url": None, "is_search_only": False}
        global BROWSER_USER_AGENT
        
        try:
            for old_f in glob.glob(os.path.join(CACHE_DIR, "*.f*.mp4")) + glob.glob(os.path.join(CACHE_DIR, "*.f*.m4a")):
                if time.time() - os.path.getmtime(old_f) > 3600:
                    try:
                        os.remove(old_f)
                    except Exception:
                        pass
        except Exception:
            pass

        try:
            target_duration = 0
            if self.use_vdj_sync:
                self.log.emit("⏳ 正在请求底层，读取稳定的原曲物理时间...")
                time.sleep(1.0)
                last_dur = -1
                
                target_deck = "active"
                if self.raw_filename:
                    for d in range(1, 5):
                        try:
                            r_file = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{d}%20get_filepath", timeout=0.5)
                            if r_file.status_code == 200:
                                filepath = r_file.text.strip().replace('"', '').replace("'", "")
                                if filepath and "error" not in filepath.lower() and filepath != "0":
                                    file_title = os.path.splitext(os.path.basename(filepath))[0]
                                    if self.raw_filename.lower() in file_title.lower() or file_title.lower() in self.raw_filename.lower():
                                        target_deck = str(d)
                                        self.log.emit(f"🔎 智能定位: 目标歌曲已在 Deck {target_deck} 加载。")
                                        break
                        except Exception:
                            pass
                
                self.update_ui.emit({"target_deck": target_deck})

                for attempt in range(15):
                    try:
                        dur_sec = 0
                        r_dur = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_time%20%27total%27%20%27absolute%27", timeout=1.0)
                        if r_dur.status_code == 200:
                            dur_ms = parse_vdj_time_to_ms(r_dur.text)
                            if dur_ms is not None and dur_ms > 0:
                                dur_sec = dur_ms / 1000.0
                                
                        if dur_sec <= 0:
                            r_dur = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_songlength", timeout=1.0)
                            if r_dur.status_code == 200:
                                dur_ms = parse_vdj_time_to_ms(r_dur.text)
                                if dur_ms is not None and dur_ms > 0:
                                    dur_sec = dur_ms / 1000.0
                                    
                                    pitch_rate = 1.0
                                    try:
                                        r_bpm = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_bpm", timeout=0.5)
                                        r_obpm = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_bpm%20%27absolute%27", timeout=0.5)
                                        if r_bpm.status_code == 200 and r_obpm.status_code == 200:
                                            bpm_val = safe_float(r_bpm.text)
                                            obpm_val = safe_float(r_obpm.text)
                                            if obpm_val > 0:
                                                pitch_rate = bpm_val / obpm_val
                                        else:
                                            r_pitch = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{target_deck}%20get_pitch_value", timeout=0.5)
                                            if r_pitch.status_code == 200:
                                                pitch_str = r_pitch.text.strip().replace('%', '')
                                                if "error" not in pitch_str.lower():
                                                    pitch_val = safe_float(pitch_str)
                                                    if pitch_val > 5.0 or pitch_val < -5.0:
                                                        pitch_rate = 1.0 + (pitch_val / 100.0)
                                                    else:
                                                        pitch_rate = pitch_val if pitch_val > 0.01 else 1.0
                                    except Exception:
                                        pass
                                    dur_sec = dur_sec * pitch_rate
                        
                        if dur_sec > 0:
                            if abs(dur_sec - last_dur) < 0.1:
                                target_duration = dur_sec
                                self.log.emit(f"✅ 成功锁定 VDJ 原曲绝对时长: {int(target_duration)} 秒")
                                self.update_ui.emit({"target_duration": target_duration})
                                break
                            last_dur = dur_sec
                            
                    except Exception:
                        pass
                    time.sleep(0.5)

            driver = None
            target_url = ""
            candidate_urls = []
            found_candidates = []

            try:
                driver = BrowserEngine.get_driver()
                
                # ========================================================================
                # [核心打包防封补丁] 动态吸取当前浏览器的真实 UA，传给 yt-dlp 和 Proxy
                # 防止由于 "Python" 或 "yt-dlp" 的指纹导致二次登录时被 B 站风控注销
                # ========================================================================
                try:
                    if "Windows NT" in BROWSER_USER_AGENT and "Chrome" in BROWSER_USER_AGENT and BROWSER_USER_AGENT.endswith("Safari/537.36"):
                        BROWSER_USER_AGENT = driver.execute_script("return navigator.userAgent;")
                except Exception:
                    pass
                
                # ========================================================================
                # [核心打包补丁] 安全提取 Cookie 逻辑，确保无论开发还是打包版都能稳稳写入 cookies.txt
                # 加入 5 分钟限制，彻底解决因频繁读写造成的浏览器卡顿！
                # ========================================================================
                try:
                    need_sync_cookie = True
                    if os.path.exists(STATIC_COOKIE_FILE):
                        if time.time() - os.path.getmtime(STATIC_COOKIE_FILE) < 300: 
                            need_sync_cookie = False
                            
                    if need_sync_cookie:
                        cookies = driver.get_cookies()
                        with open(STATIC_COOKIE_FILE, 'w', encoding='utf-8') as f:
                            f.write("# Netscape HTTP Cookie File\n")
                            for cookie in cookies:
                                domain = cookie.get('domain', '')
                                inc_sub = 'TRUE' if domain.startswith('.') else 'FALSE'
                                path = cookie.get('path', '/')
                                secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                                expiry = str(int(cookie.get('expiry', time.time() + 86400 * 30)))
                                name = cookie.get('name', '')
                                value = cookie.get('value', '')
                                f.write(f"{domain}\t{inc_sub}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
                        self.log.emit("🍪 已后台静默同步 Cookie 与防踢出伪装！")
                except Exception:
                    pass
                # ========================================================================
                
                if self.mode == TaskMode.SEARCH_ONLY:
                    self.log.emit(f"🔍 [半自动搜索已就绪] 关键词: {self.query}。请在浏览器中手动点击播放！")
                    driver.get(f"https://search.bilibili.com/all?keyword={quote(self.query)}")
                    result_data["is_search_only"] = True
                    result_data["success"] = True
                    # ===== [修复半自动模式不推送时长的问题] =====
                    if target_duration > 0:
                        self.update_ui.emit({"target_duration": target_duration})
                    # ==========================================
                    self.finished.emit(result_data)
                    return
                elif self.mode == TaskMode.GRAB_CURRENT:
                    target_url = self.query if (self.query and self.query.startswith("http")) else driver.current_url
                    candidate_urls.append(target_url)
                else: 
                    self.log.emit(f"🔍 [全自动联动] 正在深度搜索: {self.query}")
                    safe_query = quote(self.query)
                    
                    try:
                        driver.get(f"https://search.bilibili.com/all?keyword={safe_query}")
                    except Exception:
                        self.log.emit("⚠️ 检测到底层浏览器渲染崩溃，正在极速热重连...")
                        BrowserEngine.close()
                        driver = BrowserEngine.get_driver()
                        driver.get(f"https://search.bilibili.com/all?keyword={safe_query}")
                    
                    self.log.emit("⏳ 正在极速提取首页前 30 个视频结果...")
                    # [修复搜不到结果的Bug] 强制页面向下滚动，打破 B站 懒加载机制！
                    try:
                        driver.execute_script("window.scrollBy(0, 600);")
                    except Exception:
                        pass
                        
                    try:
                        WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.bili-video-card, .video-list-item, .v-card')))
                    except Exception:
                        self.log.emit("⚠️ 页面元素加载缓慢，尝试强制解析...")
                    time.sleep(1.5) # 必须等待 Vue/React 把时间数据挂载到 DOM 上
                    
                    js_code = """
                    let res = [];
                    let idx = 0;
                    let cards = document.querySelectorAll('.bili-video-card, .video-list-item, .v-card');
                    for(let i = 0; i < cards.length; i++) {
                        if (res.length >= 30) break; 
                        let card = cards[i];
                        let a = card.querySelector('a');
                        let dur = card.querySelector('.bili-video-card__stats__duration, .bili-video-length, .time');
                        let viewNode = card.querySelector('.bili-video-card__stats--item, .play-text, .play');
                        let views = viewNode ? viewNode.innerText.trim() : "0";
                        
                        let titNode = card.querySelector('h3') || card.querySelector('.bili-video-card__info--tit') || card.querySelector('.title');
                        let titleText = titNode ? (titNode.getAttribute('title') || titNode.innerText.trim()) : "";
                        if (!titleText && a) titleText = a.getAttribute('title') || a.innerText.trim();
                        
                        if(a && dur && a.href.includes('/video/BV')) {
                            res.push({
                                url: a.href, 
                                dur_text: dur.innerText.trim(), 
                                views_text: views, 
                                title: titleText,
                                original_index: idx
                            });
                            idx++;
                        }
                    }
                    return res;
                    """
                    raw_results = driver.execute_script(js_code)
                    
                    for item_idx, item in enumerate(raw_results):
                        clean_h = item['url'].split('?')[0]
                        if clean_h.startswith("//"):
                            clean_h = "https:" + clean_h
                        parts = item['dur_text'].split(':')
                        dur_sec = 0
                        if len(parts) == 3:
                            dur_sec = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        elif len(parts) == 2:
                            dur_sec = int(parts[0]) * 60 + int(parts[1])
                        
                        if dur_sec > 0 and not any(c['url'] == clean_h for c in found_candidates):
                            found_candidates.append({
                                "url": clean_h,
                                "duration": dur_sec,
                                "title": item.get('title', ''),
                                "views_text": item.get('views_text', '0'),
                                "views": parse_views_count(item.get('views_text', '0')),
                                "original_index": item['original_index']
                            })
            except Exception as e:
                self.log.emit(f"⚠️ 页面提取阶段异常: {e}")

            best_url = None
            original_first_url = found_candidates[0]["url"] if found_candidates else None
            
            if target_duration > 0 and found_candidates and self.mode == TaskMode.AUTO:
                self.log.emit(f"⏱️ 页面解析完毕，共锁定 {len(found_candidates)} 个结果。目标时长: {int(target_duration)} 秒")
                
                # =========================================================
                # 【终极匹配算法】 - 文本与时间的基础特征分析
                # =========================================================
                clean_song_str = clean_text_for_match(self.query)
                song_words = set(clean_song_str.split())
                max_views = max((c['views'] for c in found_candidates), default=1)
                
                for c in found_candidates:
                    clean_tit = clean_text_for_match(c['title'])
                    
                    # 1. 文本命中率计算 (Text Score 0~1.0)
                    if not song_words:
                        c['text_score'] = 1.0
                    else:
                        matched = sum(1 for w in song_words if w in clean_tit)
                        base_txt = matched / len(song_words)
                        # 如果出现完整无缝短语，给予巨大加成(防止被乱序干扰)
                        if clean_song_str and clean_song_str in clean_tit:
                            base_txt += 0.5 
                        c['text_score'] = min(base_txt, 1.0)
                        
                    # 2. 时间误差计算
                    c['time_diff'] = abs(c['duration'] - target_duration)
                    
                    # 3. 智能权重分数计算 (Google-style Ranking)
                    # 时间衰减分(0~1): 误差0s得1分，误差10s约得0.45分，误差30s得0.09分
                    time_score = math.exp(-0.08 * c['time_diff'])
                    # 热度分(0~1): 对数平滑防止千万播放量通杀
                    pop_score = math.log(c['views'] + 2) / max(math.log(max_views + 2), 1)
                    # 原生排序分(0~1): 尊重B站搜索本身的自然语言处理结果
                    rank_score = 1.0 / (1.0 + 0.1 * c['original_index'])
                    
                    # 综合分数公式 (总满分1.0)
                    c['smart_score'] = (c['text_score'] * 0.45) + (time_score * 0.35) + (pop_score * 0.15) + (rank_score * 0.05)
                
                best_candidate = None
                
                # =========================================================
                # 引擎路由：按照四种模式分发
                # =========================================================
                if self.algo_mode == 1:
                    # 模式1：绝对精准 (时间误差≤5秒 且 纯净文本命中率满分)
                    valid_cands = [c for c in found_candidates if c['time_diff'] <= 5 and c['text_score'] >= 1.0]
                    if valid_cands:
                        valid_cands.sort(key=lambda x: x['views'], reverse=True)
                        best_candidate = valid_cands[0]
                        self.log.emit(f"🎯 [模式1-绝对精准] 命中完美目标！(文本满分, 误差: {best_candidate['time_diff']}秒)")
                    else:
                        self.log.emit(f"⚠️ [模式1-绝对精准] 未找到完美目标，自动退回综合智能兜底...")
                        
                elif self.algo_mode == 2:
                    # 模式2：智能均衡 (基于 Google 算法的综合得分最高者)
                    found_candidates.sort(key=lambda x: x['smart_score'], reverse=True)
                    best_candidate = found_candidates[0]
                    self.log.emit(f"🧠 [模式2-智能均衡] 选中目标！综合评分: {best_candidate['smart_score']:.3f} (文本命中: {best_candidate['text_score']:.2f}, 误差: {best_candidate['time_diff']}秒)")
                    
                elif self.algo_mode == 3:
                    # 模式3：冷门文本优先 (强行文本优先 -> 同等文本再看时间梯队 -> 最后看播放量)
                    found_candidates.sort(key=lambda x: (
                        -x['text_score'], 
                        int(x['time_diff'] / 3), 
                        -x['views']
                    ))
                    best_candidate = found_candidates[0]
                    self.log.emit(f"📖 [模式3-冷门文本] 选中目标！文本命中率最大化: {best_candidate['text_score']:.2f} (附带误差: {best_candidate['time_diff']}秒)")
                    
                elif self.algo_mode == 4:
                    # 模式4：时长绝对优先 (强行时间误差最小 -> 同等时间看文本 -> 最后看播放量)
                    found_candidates.sort(key=lambda x: (
                        x['time_diff'], 
                        -x['text_score'], 
                        -x['views']
                    ))
                    best_candidate = found_candidates[0]
                    self.log.emit(f"⏱️ [模式4-时长优先] 选中目标！时长误差最小化: {best_candidate['time_diff']}秒 (附带文本: {best_candidate['text_score']:.2f})")

                elif self.algo_mode == 5:
                    # 模式5：完全文本匹配 (强行文本匹配度最大化 -> 其次时长误差 -> 最后看播放量)
                    found_candidates.sort(key=lambda x: (
                        -x['text_score'], 
                        x['time_diff'], 
                        -x['views']
                    ))
                    best_candidate = found_candidates[0]
                    self.log.emit(f"📝 [模式5-完全文本匹配] 选中目标！完全遵循文本关键词最优: {best_candidate['text_score']:.2f} (时长误差: {best_candidate['time_diff']}秒)")

                # =========================================================
                # 终极抗死锁兜底
                # =========================================================
                if not best_candidate:
                    found_candidates.sort(key=lambda x: x['smart_score'], reverse=True)
                    best_candidate = found_candidates[0]
                    self.log.emit(f"🛡️ [系统强制兜底] 按照智能权重锁定安全目标！")

                best_url = best_candidate['url']

            # 安全赋值候选序列
            if best_url:
                candidate_urls = [best_url]
            elif original_first_url and not candidate_urls:
                candidate_urls = [original_first_url]
            
            if not candidate_urls:
                raise Exception("搜索页面未找到任何有效的视频结果！")
            
            target_url = None
            bvid = None
            title = None
            thumb = None
            target_size_mb = 0 
            
            # [核心打包补丁] 把动态吸取的浏览器 UA 穿透到 yt-dlp 中，防爬虫检测
            ydl_opts_info = {
                'format': 'bestvideo[vcodec^=avc][height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'quiet': True,
                'cookiefile': STATIC_COOKIE_FILE,
                'noplaylist': True,
                'http_headers': {'User-Agent': BROWSER_USER_AGENT}
            }

            for idx, curl in enumerate(candidate_urls[:3]):
                try:
                    bv_match = re.search(r'(BV[a-zA-Z0-9]+)', curl)
                    if not bv_match:
                        continue
                    temp_bvid = bv_match.group(1)
                    self.log.emit(f"⏳ 正在雷达评估选定源 ({temp_bvid})...")
                    
                    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                        info = ydl.extract_info(curl, download=False)
                        
                        total_size = sum([f.get('filesize') or f.get('filesize_approx') or 0 for f in info.get('requested_formats', [])]) or info.get('filesize') or 0
                        size_mb = total_size / (1024 * 1024)
                        duration = info.get('duration', 0)
                        
                        if size_mb == 0 and duration > 0:
                            size_mb = duration * (15 / 60)
                            
                        target_url = curl
                        bvid = temp_bvid
                        title = info.get('title', bvid)
                        thumb = info.get('thumbnail')
                        target_size_mb = size_mb 
                        
                        self.log.emit(f"✅ 锁定流媒体！预估体积: 约 {size_mb:.1f} MB")
                        break 
                except Exception as e:
                    self.log.emit(f"⚠️ 流媒体解析失败: {e}")
                    continue
                    
            if self.mode == TaskMode.AUTO and target_url and driver:
                try:
                    driver.get(target_url)
                except Exception:
                    pass
                
            result_data["original_url"] = target_url
            v_url = None
            if 'info' in locals():
                for f in reversed(info.get('formats', [])):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and 'url' in f:
                        v_url = f.get('url')
                        self.log.emit("🔗 获取原生预混流成功！")
                        break
                if not v_url and 'requested_formats' in info:
                    for f in info['requested_formats']:
                        if f.get('vcodec') != 'none':
                            v_url = f.get('url')
                            break
                if not v_url:
                    v_url = info.get('url')
                    
            global CURRENT_STREAM_URL
            CURRENT_STREAM_URL = v_url or ""

            cached_files = glob.glob(os.path.join(CACHE_DIR, f"*_{bvid}.mp4"))
            if cached_files:
                local_file = os.path.abspath(cached_files[0])
                self.log.emit(f"🚀 [命中精准缓存] 极速秒播 ({bvid})")
                self.play_media.emit(local_file, "local")
                
                update_payload = {"title": os.path.basename(local_file).replace(f"_{bvid}.mp4", ""), "cover_data": None}
                if target_duration > 0:
                    update_payload["target_duration"] = target_duration
                self.update_ui.emit(update_payload)
                
                result_data["success"] = True
                self.finished.emit(result_data)
                return

            result_data["title"] = title
            if thumb:
                try:
                    result_data["cover_data"] = requests.get(thumb, timeout=3).content
                except Exception:
                    pass
                    
            update_payload = {"title": title, "cover_data": result_data.get("cover_data")}
            if target_duration > 0:
                update_payload["target_duration"] = target_duration
            self.update_ui.emit(update_payload)

            safe_title = sanitize_filename(title)
            local_save_path = os.path.abspath(os.path.join(CACHE_DIR, f"{safe_title}_{bvid}.mp4"))

            # ========================================================================
            # [打包核心终极补丁] 彻底解决 "yt-dlp不是内部命令" 的报错！
            # 获取内部绑定的 yt-dlp.exe，同时给下载过程穿上浏览器伪装衣服
            # ========================================================================
            ffmpeg_path = get_resource_path("ffmpeg.exe")
            aria2c_path = get_resource_path("aria2c.exe")
            ytdlp_path = get_resource_path("yt-dlp.exe")
            
            # 如果打包没包进去 yt-dlp，兜底使用系统的
            if not os.path.exists(ytdlp_path):
                ytdlp_path = "yt-dlp"

            cmd_str = (
                f'"{ytdlp_path}" -f "bestvideo[vcodec^=avc][height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" '
                f'--user-agent "{BROWSER_USER_AGENT}" '
                f'--no-keep-video --no-playlist --no-check-certificate --downloader "{aria2c_path}" --downloader-args "aria2c:-x 4 -k 2M --file-allocation=none --check-certificate=false" '
                f'--ffmpeg-location "{ffmpeg_path}" '
                f'--no-part -o "{local_save_path}" --cookies "{STATIC_COOKIE_FILE}" "{target_url}"'
            )
            
            def clean_fragments():
                try:
                    for f in glob.glob(os.path.join(CACHE_DIR, "*.f*.mp4")) + glob.glob(os.path.join(CACHE_DIR, "*.f*.m4a")) + glob.glob(os.path.join(CACHE_DIR, "*.temp")):
                        try: os.remove(f)
                        except: pass
                except: pass

            if not self.enable_download:
                self.log.emit(f"⚡ 启动【代理穿透】无缝流播模式 (已禁用本地缓存)！")
                if CURRENT_STREAM_URL:
                    unique_ts = int(time.time() * 1000)
                    self.play_media.emit(f"http://127.0.0.1:{PROXY_PORT}/stream_{bvid}_{unique_ts}.mp4", "stream")
                else:
                    self.log.emit("❌ 提取直连流失败，且未开启下载功能。")
                    result_data["success"] = False
            else:
                if 0 < target_size_mb <= 10:
                    self.log.emit(f"⏳ 触发小体积直接下载 (约 {target_size_mb:.1f} MB)。请查看旁边的 CMD 黑框了解进度...")
                    proc = subprocess.Popen(cmd_str, shell=True)
                    proc.wait() 
                    clean_fragments()
                    if os.path.exists(local_save_path):
                        self.log.emit("🎉 本地下载彻底完成！文件已存入缓存。")
                        self.play_media.emit(local_save_path, "local")
                    else:
                        self.log.emit("❌ 下载完毕但找不到合并后的视频，请检查 CMD 黑框中的报错信息。")
                else:
                    self.log.emit(f"⚡ 启动【代理穿透】无缝流播模式！")
                    if CURRENT_STREAM_URL:
                        unique_ts = int(time.time() * 1000)
                        self.play_media.emit(f"http://127.0.0.1:{PROXY_PORT}/stream_{bvid}_{unique_ts}.mp4", "stream")
                        
                        self.log.emit("📥 后台静默下载已挂载，请查看旁边的 CMD 黑框获取实时进度...")
                        def delayed_dl(cmd, path):
                            time.sleep(3.5)
                            print("\n" + "="*60)
                            print("📥 [后台下载系统] 开始为您悄悄缓存高清原视频...")
                            proc = subprocess.Popen(cmd, shell=True)
                            proc.wait()
                            clean_fragments()
                            if os.path.exists(path):
                                print(f"🎉 [后台下载系统] 彻底完成！视频已安全保存至: {path}")
                            else:
                                print("❌ [后台下载系统] 下载或合并失败，请检查上方红字报错信息。")
                            print("="*60 + "\n")
                        threading.Thread(target=delayed_dl, args=(cmd_str, local_save_path), daemon=True).start()
                    else:
                        self.log.emit("⚠️ 提取直连流失败，尝试直接下载...")
                        proc = subprocess.Popen(cmd_str, shell=True)
                        proc.wait()
                        clean_fragments()
                        if os.path.exists(local_save_path):
                            self.log.emit("🎉 本地下载彻底完成！")
                            self.play_media.emit(local_save_path, "local")
                        else:
                            self.log.emit("❌ 下载失败，请检查 CMD 黑框中的报错信息。")

            result_data["success"] = True
            
        except Exception as e:
            self.log.emit(f"❌ 解析/执行发生致命错误: {str(e)}")
            traceback.print_exc()
            result_data["success"] = False

        self.finished.emit(result_data)

# ============================================================================
# [UI 核心] - 渲染与控制
# ============================================================================

class OBSVideoWindow(QMainWindow):
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OBS Bili-Source Render")
        self.resize(1280, 720)
        self.setStyleSheet("background-color: black;")
        icon_path = get_resource_path("app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # [核心架构升级] 抛弃普通 QVideoWidget，改用支持层级渲染的图形场景引擎
        self.view = QGraphicsView(self)
        self.view.setStyleSheet("background: black; border: none;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(self.view)
        
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)

        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.audio.setVolume(0.0)
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_item)
        
        self.is_looping = True
        self.needs_initial_sync = False  
        self.player.positionChanged.connect(self.position_changed.emit)
        self.player.durationChanged.connect(self.duration_changed.emit)
        self.player.mediaStatusChanged.connect(self.loop_handler)

        # ====== OSD UI for OBS (Graphics Scene) =====
        self.osd_song_label = QLabel("歌曲：等待加载...")
        self.osd_video_label = QLabel("匹配到的视频标题：等待匹配...")
        
        # 将背景颜色 background-color 改为了 transparent (全透明)，彻底去除黑框
        osd_style = "color: white; font-size: 18px; font-weight: bold; background-color: transparent; padding: 5px; border-radius: 5px;"
        self.osd_song_label.setStyleSheet(osd_style)
        self.osd_video_label.setStyleSheet(osd_style)
        
        self.osd_song = self.scene.addWidget(self.osd_song_label)
        self.osd_video = self.scene.addWidget(self.osd_video_label)
        
        self.osd_song.setPos(20, 20)
        self.osd_video.setPos(20, 60)
        
        self.osd_song_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.osd_video_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # 初始载入配置的透明度和显示状态
        self.set_osd_song_opacity(APP_CONFIG.get("osd_song_opacity", 100))
        self.set_osd_video_opacity(APP_CONFIG.get("osd_video_opacity", 100))
        self.set_osd_visible(APP_CONFIG.get("show_osd", True))

    def set_osd_visible(self, visible):
        self.osd_song.setVisible(visible)
        self.osd_video.setVisible(visible)
        
    def set_osd_song_opacity(self, opacity_value):
        self.osd_song.setOpacity(opacity_value / 100.0)
        
    def set_osd_video_opacity(self, opacity_value):
        self.osd_video.setOpacity(opacity_value / 100.0)
        
    def update_osd(self, song_text=None, video_text=None):
        if song_text is not None:
            self.osd_song_label.setText(song_text)
            self.osd_song_label.adjustSize()
        if video_text is not None:
            self.osd_video_label.setText(video_text)
            self.osd_video_label.adjustSize()
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        self.view.setSceneRect(0, 0, w, h)
        self.video_item.setSize(QSizeF(w, h))
            
    def loop_handler(self, s):
        if s == QMediaPlayer.MediaStatus.EndOfMedia and self.is_looping:
            self.player.setPosition(0)
            self.player.play()
            
    def play_url(self, url):
        self.player.stop()
        self.player.setSource(QUrl()) 
        QCoreApplication.processEvents() 
        if url.startswith("http"):
            self.player.setSource(QUrl(url))
        else:
            self.player.setSource(QUrl.fromLocalFile(url))
            
        self.needs_initial_sync = True 
        self.player.pause() 
        
    def blackout(self):
        self.player.stop()
        self.player.setSource(QUrl())

    def closeEvent(self, event):
        super().closeEvent(event)

class RoundedImageLabel(QLabel):
    def __init__(self, size=200, parent=None):
        super().__init__(parent)
        self.target_size = size
        self.setFixedSize(size, size)
        self.setPixmap(self.create_placeholder())
        
    def create_placeholder(self):
        img = QPixmap(self.target_size, self.target_size)
        img.fill(QColor("#2A2A2A"))
        p = QPainter(img)
        p.setPen(QColor("#444"))
        p.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, "NO COVER")
        p.end()
        return self._round(img)
        
    def set_image(self, data):
        if not data:
            self.setPixmap(self.create_placeholder())
            return
        pix = QPixmap.fromImage(QImage.fromData(data)).scaled(
            self.target_size, self.target_size, 
            Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(self._round(pix))
        
    def _round(self, pix):
        out = QPixmap(self.size())
        out.fill(Qt.GlobalColor.transparent)
        p = QPainter(out)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        p.setClipPath(path)
        p.drawPixmap(0, 0, pix)
        p.end()
        return out

class ControlCenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.resize(1100, 850)
        icon_path = get_resource_path("app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.is_processing = False
        self.slider_locked = False
        self.bpm_locked = False
        self.current_orig_bpm = 120.0 
        self.audio_orig_duration_ms = 0.0 
        self.active_workers = [] 
        
        def start_proxy():
            try:
                server = ThreadedHTTPServer(("127.0.0.1", PROXY_PORT), BiliStreamProxy)
                server.serve_forever()
            except Exception:
                pass
                
        threading.Thread(target=start_proxy, daemon=True).start()
        
        self.obs_window = OBSVideoWindow()
        self.obs_window.set_osd_visible(APP_CONFIG.get("show_osd", True))
        self.obs_window.show() 
        self.obs_window.position_changed.connect(self.sync_progress)
        self.obs_window.duration_changed.connect(self.sync_duration)

        self.setup_ui()
        self.start_vdj_monitor()
        self.check_vdj_network()
        
        QTimer.singleShot(3000, self.safe_delayed_start)

        self.vdj_poller = VDJPoller()
        self.vdj_poller.vdj_state_signal.connect(self.on_vdj_state_received)
        self.vdj_poller.network_ok_signal.connect(lambda: self.log("✅ VDJ Network 重新连接成功！深度同步已接管。"))
        self.vdj_poller.network_error_signal.connect(lambda e: self.log(f"⚠️ VDJ Network 连接异常: {e}"))
        self.vdj_poller.start()

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
        QMessageBox.information(self, "配置已应用",
                                f"端口已切换为 {APP_CONFIG['vdj_port']}\n路径已切换为:\n{APP_CONFIG['vdj_path']}\n\n系统正在后台尝试重新握手...")

    def update_browser_config(self, b_type):
        if (b_type == "chrome" and self.radio_chrome.isChecked()) or \
                (b_type == "edge" and self.radio_edge.isChecked()):
            APP_CONFIG["browser_type"] = b_type
            save_config()
            print(f"[Config] 已更新浏览器内核为: {b_type}")

    def check_vdj_network(self):
        self.log("📡 正在自检 VDJ Network (HTTP API) 连通性...")
        try:
            r = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=get_clock", timeout=1.0)
            if r.status_code == 200:
                self.log(f"✅ VDJ Network 通信插件握手成功！(通信端口: {APP_CONFIG['vdj_port']})")
                if hasattr(self, 'vdj_poller'):
                    self.vdj_poller.network_ok = True
            else:
                self.log(f"❌ <b>VDJ Network 未连接！(收到异常状态码: {r.status_code})</b>")
        except Exception as e:
            self.log(f"❌ <b>VDJ Network 未连接！({str(e)})</b>")

    def fmt_time(self, ms): 
        if ms is None or math.isnan(ms) or math.isinf(ms):
            return "00:00"
        sign = "-" if ms < 0 else ""
        ms = abs(ms)
        return f"{sign}{int(ms)//60000:02d}:{(int(ms)%60000)//1000:02d}"

    def on_vdj_state_received(self, state):
        if hasattr(self, 'cb_sync') and not self.cb_sync.isChecked():
            return
        
        try:
            is_playing = state.get('is_playing', False)
            target_rate = state.get('pitch', 1.0)
            vdj_time_ms = state.get('time_ms', 0)
            pos_ratio = state.get('pos_ratio', -1.0)
            cur_bpm = state.get('cur_bpm', 0.0)
            orig_bpm = state.get('orig_bpm', 0.0)
            
            if orig_bpm > 0:
                self.current_orig_bpm = orig_bpm
            
            my_state = self.obs_window.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
            current_rate = self.obs_window.player.playbackRate()
            current_video_pos = self.obs_window.player.position()
            vid_duration = self.obs_window.player.duration()

            if getattr(self.obs_window, 'needs_initial_sync', False):
                if vid_duration <= 0:
                    if my_state:
                        self.obs_window.player.pause()
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
            except Exception:
                pass
                
            threshold_ms = threshold_sec * 1000
            
            is_background_mode = False
            if vid_duration > 0 and self.audio_orig_duration_ms > 0:
                diff_ms = abs(vid_duration - self.audio_orig_duration_ms)
                if diff_ms > threshold_ms:
                    is_background_mode = True

            if is_background_mode:
                final_rate = 1.0
                if abs(current_rate - final_rate) > 0.01:
                    self.obs_window.player.setPlaybackRate(final_rate)
                    
                if getattr(self.obs_window, 'needs_initial_sync', False):
                    self.obs_window.needs_initial_sync = False
                    if is_playing:
                        self.obs_window.player.play()
                    else:
                        self.obs_window.player.pause()
                    self.log(f"⚠️ 视音频时长相差过大，已自动切换至【背景原速自由循环模式】")
                    return

                if is_playing:
                    if not my_state:
                        self.obs_window.player.play()
                else:
                    if my_state:
                        self.obs_window.player.pause()
                
            elif vid_duration > 0 and self.audio_orig_duration_ms > 0 and pos_ratio >= 0:
                base_rate = vid_duration / self.audio_orig_duration_ms
                final_rate = target_rate * base_rate
                
                if math.isnan(final_rate) or math.isinf(final_rate) or final_rate <= 0.01:
                    final_rate = 1.0
                
                if abs(current_rate - final_rate) > 0.01:
                    self.obs_window.player.setPlaybackRate(final_rate)
                
                expected_video_pos = pos_ratio * vid_duration
                
                if getattr(self.obs_window, 'needs_initial_sync', False):
                    self.obs_window.player.setPosition(int(expected_video_pos))
                    self.obs_window.needs_initial_sync = False
                    if is_playing:
                        self.obs_window.player.play()
                    else:
                        self.obs_window.player.pause()
                    self.sync_progress(expected_video_pos)
                    self.log(f"⚡ 初始预缩放完成: 视频已等比空降至 [{self.fmt_time(expected_video_pos)}]")
                    return
                
                if is_playing:
                    if not my_state:
                        self.obs_window.player.play()
                else:
                    if my_state:
                        self.obs_window.player.pause()
                        
                drift = expected_video_pos - current_video_pos
                if not self.slider_locked and not self.bpm_locked:
                    if is_playing:
                        if abs(drift) > 4000:
                            self.obs_window.player.setPosition(int(expected_video_pos))
                            self.slider.setValue(int(expected_video_pos * 1000 / vid_duration))
                    else:
                        if abs(drift) > 300:
                            self.obs_window.player.setPosition(int(expected_video_pos))
                            self.slider.setValue(int(expected_video_pos * 1000 / vid_duration))
                            self.obs_window.player.pause()
            else:
                if orig_bpm > 0 and abs(current_rate - target_rate) > 0.01:
                    self.obs_window.player.setPlaybackRate(target_rate)
                    
                if is_playing and not my_state:
                    self.obs_window.player.play()
                elif not is_playing and my_state:
                    self.obs_window.player.pause()
                    
        except Exception as e:
            pass 

    def safe_delayed_start(self):
        self.engine_starter = EngineStarter()
        self.engine_starter.log_signal.connect(self.log)
        self.engine_starter.finished_signal.connect(self.on_engine_started)
        self.engine_starter.start()

    def on_engine_started(self):
        self.monitor = BrowserMonitor() 
        self.monitor.video_detected.connect(self.on_manual_click)
        self.monitor.start()

    def setup_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QHBoxLayout(cw)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        left = QVBoxLayout()
        layout.addLayout(left, 5)
        right = QVBoxLayout()
        layout.addLayout(right, 4)
        
        header = QLabel(APP_NAME)
        header.setObjectName("Title")
        left.addWidget(header)
        
        np = QFrame()
        np.setObjectName("Panel")
        np_l = QHBoxLayout(np)
        self.cover = RoundedImageLabel(150)
        np_l.addWidget(self.cover)
        
        txt_l = QVBoxLayout()
        self.lbl_title = QLabel("队列待机中...")
        self.lbl_title.setObjectName("SongTitle")
        self.lbl_title.setWordWrap(True)
        self.lbl_status = QLabel("系统启动中...")
        self.lbl_status.setObjectName("Artist")
        
        self.lbl_orig_duration = QLabel("原曲时长: 等待提取...")
        self.lbl_orig_duration.setStyleSheet("font-family: Consolas; font-size: 14px; font-weight: bold; color: #00FF00; margin-top: 10px;")
        
        txt_l.addWidget(self.lbl_title)
        txt_l.addWidget(self.lbl_status)
        txt_l.addWidget(self.lbl_orig_duration)
        txt_l.addStretch()
        np_l.addLayout(txt_l)
        left.addWidget(np)
        
        pg = QGroupBox("Bilibili 专属播控台")
        pg_l = QVBoxLayout(pg)
        pg_l.setContentsMargins(15, 20, 15, 15)
        pg_l.setSpacing(15)
        
        top_ctrl = QHBoxLayout()
        top_ctrl.setSpacing(10)
        
        self.btn_play = QPushButton("⏯ 播放 / 暂停", objectName="CtrlBtn")
        self.btn_loop = QPushButton("🔁 循环: 开启", objectName="CtrlBtn")
        self.btn_loop.setCheckable(True)
        self.btn_loop.setChecked(True)
        
        top_ctrl.addWidget(self.btn_play)
        top_ctrl.addWidget(self.btn_loop)
        top_ctrl.addSpacing(20)
        
        lbl_bpm_title = QLabel("BPM:")
        lbl_bpm_title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_bpm_title.setStyleSheet("font-weight: bold; color: #AAAAAA;")
        
        self.lbl_bpm_val = QLabel("0.0")
        self.lbl_bpm_val.setFixedWidth(60)
        self.lbl_bpm_val.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_bpm_val.setStyleSheet("font-family: Consolas; font-weight: bold; font-size: 22px; color: #E91E63;")
        
        self.bpm_slider = QSlider(Qt.Orientation.Horizontal)
        self.bpm_slider.setObjectName("BPMSlider")
        self.bpm_slider.setRange(0, 3000) 
        self.bpm_slider.setValue(1200)
        
        self.bpm_slider.sliderPressed.connect(self.lock_bpm)
        self.bpm_slider.sliderReleased.connect(self.release_bpm)
        self.bpm_slider.valueChanged.connect(self.on_local_bpm_changed)
        
        top_ctrl.addWidget(lbl_bpm_title)
        top_ctrl.addWidget(self.lbl_bpm_val)
        top_ctrl.addWidget(self.bpm_slider, stretch=1)
        
        pg_l.addLayout(top_ctrl)
        
        prog_layout = QHBoxLayout()
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.slider.sliderPressed.connect(self.lock_s)
        self.slider.sliderReleased.connect(self.seek_p)
        
        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setFixedWidth(130)
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet("font-family: Consolas; font-weight: bold; color: #00ADB5; font-size: 16px;")
        
        prog_layout.addWidget(self.slider)
        prog_layout.addWidget(self.lbl_time)
        
        pg_l.addLayout(prog_layout)
        left.addWidget(pg)
        
        cp = QFrame()
        cp.setObjectName("Panel")
        cp_l = QVBoxLayout(cp)
        
        # 自动化与匹配模式行
        row1_layout = QHBoxLayout()
        self.btn_auto = QPushButton("VDJ 全自动联动")
        self.btn_auto.setCheckable(True)
        self.btn_auto.setChecked(True)
        self.btn_semi = QPushButton("VDJ 半自动模式")
        self.btn_semi.setCheckable(True)
        
        self.bg_mode = QButtonGroup(self)
        self.bg_mode.addButton(self.btn_auto)
        self.bg_mode.addButton(self.btn_semi)
        
        row1_layout.addWidget(self.btn_auto)
        row1_layout.addWidget(self.btn_semi)
        row1_layout.addStretch()
        cp_l.addLayout(row1_layout)
        
        # [算法引擎重构] 新增四大专属模式 RadioButtons
        row2_layout = QHBoxLayout()
        self.algo_group = QButtonGroup(self)
        
        self.rb_mode1 = QRadioButton("1:绝对精准 (Alt+1)")
        self.rb_mode1.setStyleSheet("color: #4CAF50;")
        
        self.rb_mode2 = QRadioButton("2:智能均衡 (Alt+2)")
        self.rb_mode2.setStyleSheet("color: #00ADB5;")
        self.rb_mode2.setChecked(True) # 默认最强 Google-style 算法
        
        self.rb_mode3 = QRadioButton("3:冷门文本 (Alt+3)")
        self.rb_mode3.setStyleSheet("color: #9C27B0;")
        
        self.rb_mode4 = QRadioButton("4:时长优先 (Alt+4)")
        self.rb_mode4.setStyleSheet("color: #FF9800;")
        
        self.rb_mode5 = QRadioButton("5:完全文本匹配 (Alt+5)")
        self.rb_mode5.setStyleSheet("color: #E91E63;")
        
        self.algo_group.addButton(self.rb_mode1, 1)
        self.algo_group.addButton(self.rb_mode2, 2)
        self.algo_group.addButton(self.rb_mode3, 3)
        self.algo_group.addButton(self.rb_mode4, 4)
        self.algo_group.addButton(self.rb_mode5, 5)
        
        row2_layout.addWidget(self.rb_mode1)
        row2_layout.addWidget(self.rb_mode2)
        row2_layout.addWidget(self.rb_mode3)
        row2_layout.addWidget(self.rb_mode4)
        row2_layout.addWidget(self.rb_mode5)
        row2_layout.addStretch()
        cp_l.addLayout(row2_layout)
        
        # [配置全局快捷键]
        self.shortcut_mode1 = QShortcut(QKeySequence("Alt+1"), self)
        self.shortcut_mode1.activated.connect(self.rb_mode1.click)
        
        self.shortcut_mode2 = QShortcut(QKeySequence("Alt+2"), self)
        self.shortcut_mode2.activated.connect(self.rb_mode2.click)
        
        self.shortcut_mode3 = QShortcut(QKeySequence("Alt+3"), self)
        self.shortcut_mode3.activated.connect(self.rb_mode3.click)
        
        self.shortcut_mode4 = QShortcut(QKeySequence("Alt+4"), self)
        self.shortcut_mode4.activated.connect(self.rb_mode4.click)
        
        self.shortcut_mode5 = QShortcut(QKeySequence("Alt+5"), self)
        self.shortcut_mode5.activated.connect(self.rb_mode5.click)
        
        # --- 附加关键词输入框 ---
        kw_layout = QHBoxLayout()
        
        self.cb_only_title = QCheckBox("仅搜歌名")
        self.cb_only_title.setChecked(APP_CONFIG.get("only_search_title", False))
        self.cb_only_title.stateChanged.connect(self.save_extra_keyword)
        
        self.cb_only_artist = QCheckBox("仅搜歌手")
        self.cb_only_artist.setChecked(APP_CONFIG.get("only_search_artist", False))
        self.cb_only_artist.stateChanged.connect(self.save_extra_keyword)
        
        self.cb_pure_keyword = QCheckBox("纯关键词模式")
        self.cb_pure_keyword.setChecked(APP_CONFIG.get("pure_keyword_mode", False))
        self.cb_pure_keyword.stateChanged.connect(self.save_extra_keyword)
        
        lbl_kw = QLabel("附加限定搜索词:")
        lbl_kw.setStyleSheet("font-weight: bold; color: #AAAAAA;")
        self.ipt_extra_keyword = QLineEdit(APP_CONFIG.get("extra_search_keyword", ""))
        self.ipt_extra_keyword.setPlaceholderText("例如输入: 音MAD、Live、静止画，MV等")
        self.ipt_extra_keyword.editingFinished.connect(self.save_extra_keyword)
        
        kw_layout.addWidget(self.cb_only_title)
        kw_layout.addWidget(self.cb_only_artist)
        kw_layout.addWidget(self.cb_pure_keyword)
        kw_layout.addWidget(lbl_kw)
        kw_layout.addWidget(self.ipt_extra_keyword)
        cp_l.addLayout(kw_layout)
        # ------------------------
        
        # 同步机制底层配置
        sync_layout = QHBoxLayout()
        self.cb_sync = QCheckBox("启用极致同步引擎 (预缩放映射 / 动态总长)")
        self.cb_sync.setChecked(True)
        self.cb_sync.setStyleSheet("color: #00ADB5;")
        
        lbl_thresh = QLabel("自由循环模式误差阈值(秒):")
        lbl_thresh.setStyleSheet("color: #AAAAAA; font-weight: bold;")
        self.ipt_threshold = QLineEdit("40")
        self.ipt_threshold.setFixedWidth(50)
        self.ipt_threshold.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ipt_threshold.setStyleSheet("background-color: #2A2A2A; border: 1px solid #00ADB5; border-radius: 4px; padding: 2px; color: white;")
        
        sync_layout.addWidget(self.cb_sync)
        sync_layout.addStretch()
        sync_layout.addWidget(lbl_thresh)
        sync_layout.addWidget(self.ipt_threshold)
        cp_l.addLayout(sync_layout)
        
        # OSD 控制区
        osd_op_layout = QVBoxLayout()
        
        row1 = QHBoxLayout()
        self.cb_osd = QCheckBox("显示 OSD 歌曲信息")
        self.cb_osd.setChecked(APP_CONFIG.get("show_osd", True))
        self.cb_osd.stateChanged.connect(self.toggle_osd)
        
        self.cb_download = QCheckBox("启用视频自动下载缓存")
        self.cb_download.setChecked(APP_CONFIG.get("enable_download", True))
        self.cb_download.stateChanged.connect(self.toggle_download)

        row1.addWidget(self.cb_osd)
        row1.addWidget(self.cb_download)
        row1.addStretch()
        osd_op_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        lbl_song_op = QLabel("歌曲 OSD 透明度:")
        lbl_song_op.setStyleSheet("color: #AAAAAA; font-weight: bold;")
        self.sld_osd_song_opacity = QSlider(Qt.Orientation.Horizontal)
        self.sld_osd_song_opacity.setRange(0, 100)
        self.sld_osd_song_opacity.setFixedWidth(150)
        self.sld_osd_song_opacity.setValue(int(APP_CONFIG.get("osd_song_opacity", 100)))
        self.sld_osd_song_opacity.valueChanged.connect(self.change_osd_song_opacity)
        
        lbl_video_op = QLabel("视频 OSD 透明度:")
        lbl_video_op.setStyleSheet("color: #AAAAAA; font-weight: bold;")
        self.sld_osd_video_opacity = QSlider(Qt.Orientation.Horizontal)
        self.sld_osd_video_opacity.setRange(0, 100)
        self.sld_osd_video_opacity.setFixedWidth(150)
        self.sld_osd_video_opacity.setValue(int(APP_CONFIG.get("osd_video_opacity", 100)))
        self.sld_osd_video_opacity.valueChanged.connect(self.change_osd_video_opacity)
        
        row2.addWidget(lbl_song_op)
        row2.addWidget(self.sld_osd_song_opacity)
        row2.addStretch()
        row2.addWidget(lbl_video_op)
        row2.addWidget(self.sld_osd_video_opacity)
        
        osd_op_layout.addLayout(row2)
        cp_l.addLayout(osd_op_layout)
        
        left.addWidget(cp)

        # ==========================================
        # [VDJ CONNECTION (底层连接设置)]
        # ==========================================
        conn_group = QGroupBox("VDJ CONNECTION (底层连接设置)")
        conn_l = QHBoxLayout(conn_group)

        self.ipt_port = QLineEdit(str(APP_CONFIG["vdj_port"]))
        self.ipt_port.setFixedWidth(50)
        self.ipt_path = QLineEdit(APP_CONFIG["vdj_path"])

        # === 浏览器选择框 ===
        browser_group = QGroupBox("浏览器内核 (Engine)")
        browser_layout = QHBoxLayout()
        self.radio_chrome = QRadioButton("Chrome")
        self.radio_edge = QRadioButton("Edge")

        # 根据当前配置勾选
        if APP_CONFIG.get("browser_type") == "edge":
            self.radio_edge.setChecked(True)
        else:
            self.radio_chrome.setChecked(True)

        # 绑定切换事件
        self.radio_chrome.toggled.connect(lambda: self.update_browser_config("chrome"))
        self.radio_edge.toggled.connect(lambda: self.update_browser_config("edge"))

        browser_layout.addWidget(self.radio_chrome)
        browser_layout.addWidget(self.radio_edge)
        browser_group.setLayout(browser_layout)
        conn_l.addWidget(browser_group) 

        btn_browse = QPushButton("📁 浏览")
        btn_apply = QPushButton("✅ 应用并重连")

        conn_l.addWidget(QLabel("端口:"))
        conn_l.addWidget(self.ipt_port)
        conn_l.addWidget(QLabel("M3U历史路径:"))
        conn_l.addWidget(self.ipt_path)
        conn_l.addWidget(btn_browse)
        conn_l.addWidget(btn_apply)
        left.addWidget(conn_group)

        btn_browse.clicked.connect(self.browse_vdj_path)
        btn_apply.clicked.connect(self.apply_vdj_settings)

        left.addStretch()
        
        right.addWidget(QLabel("🔥 系统运行日志"))
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        right.addWidget(self.log_area)
        
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_loop.toggled.connect(self.toggle_loop)

    def save_extra_keyword(self):
        APP_CONFIG["extra_search_keyword"] = self.ipt_extra_keyword.text().strip()
        APP_CONFIG["only_search_title"] = self.cb_only_title.isChecked()
        APP_CONFIG["only_search_artist"] = self.cb_only_artist.isChecked()
        APP_CONFIG["pure_keyword_mode"] = self.cb_pure_keyword.isChecked()
        save_config()

    def lock_s(self):
        self.slider_locked = True
        
    def seek_p(self):
        d = self.obs_window.player.duration()
        if d > 0:
            self.obs_window.player.setPosition(int(self.slider.value() * d / 1000))
        self.slider_locked = False
        
    def lock_bpm(self):
        self.bpm_locked = True
        
    def release_bpm(self):
        self.bpm_locked = False
    
    def on_local_bpm_changed(self, val):
        new_bpm = val / 10.0
        self.lbl_bpm_val.setText(f"{new_bpm:.1f}")
        
        if hasattr(self, 'current_orig_bpm') and self.current_orig_bpm > 0:
            target_rate = new_bpm / self.current_orig_bpm
            vid_duration = self.obs_window.player.duration()
            
            threshold_sec = 40
            try:
                val_t = int(self.ipt_threshold.text().strip())
                if val_t > 0: threshold_sec = val_t
            except Exception:
                pass
            threshold_ms = threshold_sec * 1000
            
            if vid_duration > 0 and self.audio_orig_duration_ms > 0:
                if abs(vid_duration - self.audio_orig_duration_ms) > threshold_ms:
                    final_rate = 1.0 
                else:
                    base_rate = vid_duration / self.audio_orig_duration_ms
                    final_rate = target_rate * base_rate
            else:
                final_rate = target_rate
                
            if math.isnan(final_rate) or math.isinf(final_rate):
                final_rate = 1.0
                
            self.obs_window.player.setPlaybackRate(max(0.01, min(final_rate, 4.0)))

        if self.bpm_locked and getattr(self.vdj_poller, 'network_ok', False):
            cmd = f"deck%20active%20pitch%20{new_bpm}%20bpm"
            try:
                threading.Thread(target=lambda: requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/execute?script={cmd}", timeout=0.2), daemon=True).start()
            except Exception:
                pass

    def sync_progress(self, p):
        if not self.slider_locked:
            d = self.obs_window.player.duration()
            if d > 0:
                self.slider.setValue(int(p * 1000 / d))
                self.update_t(p, d)
            
    def sync_duration(self, d):
        self.update_t(self.obs_window.player.position(), d)
        
    def update_t(self, c, t):
        rate = self.obs_window.player.playbackRate()
        
        if math.isnan(rate) or math.isinf(rate) or rate <= 0.01:
            rate = 1.0
            
        real_c = c / rate
        real_t = t / rate
        self.lbl_time.setText(f"{self.fmt_time(real_c)} / {self.fmt_time(real_t)}")
        
    def toggle_play(self):
        if self.obs_window.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.obs_window.player.pause()
        else:
            self.obs_window.player.play()
            
    def toggle_loop(self, c):
        self.obs_window.is_looping = c
        self.btn_loop.setText(f"🔁 循环: {'开启' if c else '禁用'}")
        
    def toggle_osd(self, state):
        is_checked = bool(state)
        self.obs_window.set_osd_visible(is_checked)
        APP_CONFIG["show_osd"] = is_checked
        save_config()

    def toggle_download(self, state):
        is_checked = bool(state)
        APP_CONFIG["enable_download"] = is_checked
        save_config()
        self.log(f"{'✅ 已开启' if is_checked else '🛑 已关闭'} 视频自动下载缓存功能")
        
    def change_osd_song_opacity(self, val):
        self.obs_window.set_osd_song_opacity(val)
        APP_CONFIG["osd_song_opacity"] = val
        save_config()
        
    def change_osd_video_opacity(self, val):
        self.obs_window.set_osd_video_opacity(val)
        APP_CONFIG["osd_video_opacity"] = val
        save_config()
        
    def log(self, m):
        self.log_area.appendHtml(f"<span style='color:#666'>[{datetime.now().strftime('%H:%M:%S')}]</span> {m}")
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())
        
    def start_vdj_monitor(self):
        path = APP_CONFIG["vdj_path"]
        if os.path.exists(path):
            self.vdj_watcher = VDJWatcher(path)
            self.vdj_watcher.track_changed.connect(self.on_track_changed)
            self.vdj_watcher.start()
            self.log("✅ VDJ 队列侦听已连接")
        else:
            self.log(f"⚠️ 未找到目录: {path}，切歌侦听失败！")
            
    def on_manual_click(self, url):
        if self.is_processing: return
        self.log(f"⚡ <span style='color:#E91E63'>网页端截获链接，开始处理...</span>")
        self.start_process(url, TaskMode.GRAB_CURRENT)
        
    def on_track_changed(self, t):
        self.log(f"🎵 VDJ 触发切歌(历史记录文件): <b>{t}</b>")
        
        raw_filename = t
        song_name = t
        search_query = t
        first_artist = ""
        
        target_deck = None
        if getattr(self.vdj_poller, 'network_ok', False):
            for d in range(1, 5):
                try:
                    r_file = requests.get(f"http://127.0.0.1:{APP_CONFIG['vdj_port']}/query?script=deck%20{d}%20get_filepath", timeout=0.2)
                    if r_file.status_code == 200:
                        filepath = r_file.text.strip().replace('"', '').replace("'", "")
                        if filepath and t.lower() in filepath.lower():
                            target_deck = d
                            break
                except:
                    pass
            
            if target_deck:
                try:
                    title = ""
                    artist = ""
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
                        
                        if artist:
                            first_artist = re.split(r'[、/,&，]', artist)[0].strip()
                        
                        if first_artist:
                            search_query = f"{song_name} {first_artist}"
                        else:
                            search_query = song_name
                            
                        self.log(f"💿 成功读取底层 ID3 元数据: 歌名[{song_name}] 艺人[{first_artist}]")
                except:
                    pass
                    
        if search_query == t and " - " in t:
            parts = t.split(" - ", 1)
            p1 = parts[0].strip()
            p2 = parts[1].strip()
            
            if "、" in p2 or "," in p2 or "&" in p2:
                artist_part, title_part = p2, p1
            else:
                artist_part, title_part = p1, p2
                
            first_artist = re.split(r'[、/,&，]', artist_part)[0].strip()
            song_name = title_part
            
            search_query = f"{song_name} {first_artist}"
            self.log(f"💿 智能文件名解析: 歌名[{song_name}] 艺人[{first_artist}]")

        if first_artist:
            display_song = f"歌曲：{song_name} - {first_artist}"
        else:
            display_song = f"歌曲：{song_name}"
        self.obs_window.update_osd(song_text=display_song)
            
        # --- 搜索范围与附加关键词拼接逻辑 ---
        only_title = self.cb_only_title.isChecked()
        only_artist = self.cb_only_artist.isChecked()
        pure_keyword = self.cb_pure_keyword.isChecked()
        extra_kw = self.ipt_extra_keyword.text().strip()
        
        if pure_keyword and extra_kw:
            search_query = extra_kw
        else:
            if only_title and not only_artist:
                search_query = song_name
            elif only_artist and not only_title:
                search_query = first_artist if first_artist else song_name
            else:
                search_query = f"{song_name} {first_artist}" if first_artist else song_name

            if extra_kw:
                search_query = f"{search_query} {extra_kw}"
        # --------------------------

        self.log(f"🔍 最终进入B站搜索指令: <b>{search_query}</b>")
        mode = TaskMode.AUTO if self.btn_auto.isChecked() else TaskMode.SEARCH_ONLY
        self.start_process(search_query, mode, song_name=song_name, raw_filename=raw_filename)

    def start_process(self, q, mode: TaskMode, song_name="", raw_filename=""):
        if self.is_processing:
            return
        self.is_processing = True
        self.lbl_status.setText("🔄 调度中...")
        
        has_sync = hasattr(self, 'cb_sync') and self.cb_sync.isChecked() and getattr(self.vdj_poller, 'network_ok', False)
        
        algo_mode = self.algo_group.checkedId()
        if algo_mode == -1: algo_mode = 2 

        enable_dl = APP_CONFIG.get("enable_download", True)

        worker = QThread()
        logic = SearchWorker(q, song_name, raw_filename, mode, has_sync, algo_mode, enable_download=enable_dl)
            
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
        try:
            self.active_workers.remove((worker, logic))
        except Exception:
            pass
        
    def on_ui_update(self, d):
        if "target_deck" in d:
            if hasattr(self, 'vdj_poller'):
                self.vdj_poller.current_deck = d["target_deck"]

        if d.get("title"):
            self.lbl_title.setText(d["title"])
            self.obs_window.update_osd(video_text=f"匹配到的视频标题：{d['title']}")
        if d.get("cover_data"):
            self.cover.set_image(d["cover_data"])
        
        if "target_duration" in d:
            dur = int(d["target_duration"])
            self.audio_orig_duration_ms = d["target_duration"] * 1000.0 
            self.lbl_orig_duration.setText(f"原曲物理时长: {dur//60:02d}:{dur%60:02d} ({dur}秒)")
        
    def on_media_ready(self, url, m):
        self.obs_window.play_url(url)
    
    def on_process_done(self, d):
        self.is_processing = False
        self.lbl_status.setText("✅ 调度系统空闲")
        if hasattr(self, 'monitor') and d.get("original_url"):
            clean_url = d["original_url"].split('?')[0]
            self.monitor.last_url = clean_url
            
    def closeEvent(self, event):
        if hasattr(self, 'vdj_poller'):
            self.vdj_poller.stop()
        self.obs_window.close()
        BrowserEngine.close()
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
                except Exception:
                    pass 
            time.sleep(2)

if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, False)
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    
    window = ControlCenter()
    window.show()
    sys.exit(app.exec())
