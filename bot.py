import requests
import socket
import json
import base64
import uuid
import re
from datetime import datetime, timedelta
import os
import sys
import time
import logging
import html
from io import BytesIO
from urllib.parse import urlparse, urlunparse
import PyPDF2
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import random
import string
from pymongo import MongoClient, ReturnDocument
import certifi
import ddddocr
try:
    from PIL import Image, ImageFilter, ImageEnhance
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

# 1. TELEGRAM BOT TOKEN (BotFather se lo)
TELEGRAM_BOT_TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN",
    "8789664654:AAFnfU6kjH286S0XSozttkf4AfGljb5kulg"
)

# 2. ADMIN / OWNER IDs (apni Telegram user ID)
OWNER_IDS = {8901139503}

# 3. OWNER USERNAME (support ke liye)
OWNER_USERNAME = "@RedxOnline"

# 4. BOT BRANDING (naam & channel)
BOT_NAME         = "✜ REDxAadhar Bot"
CHANNEL_USERNAME = "@redpbty"
CHANNEL_LINK     = "https://t.me/redpbty"

# 5. LOG CHANNELS (Telegram channel IDs)
LOG_CHANNEL_ID      = -1004434031
PDF_LOG_CHANNEL_ID  = int(os.environ.get("PDF_LOG_CHANNEL_ID", "-1004434031"))

# 6. MONGODB DATABASE URI
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://aadhar:aadhar@cluster0.9p0qosx.mongodb.net/?appName=Cluster0"
)

# 7. UIDAI PROXY (residential proxy chahiye)
#    Khali chhodna ho toh: UIDAI_PROXIES = []
UIDAI_PROXIES = [
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_57271233_time_5:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_58883140_time_5:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_81621065_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_34483036_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_35165080_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_18317258_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_37970288_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_10917488_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_67339987_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_32731696_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_36159890_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_36326285_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_58087635_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_12204065_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_86268847_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_10331406_time_90:5170715@change4.owlproxy.com:7778",
    "http://MYkwiWgDiK30_custom_zone_IN_st__city_sid_10758522_time_90:5170715@change4.owlproxy.com:7778"
]

# 8. BOT BEHAVIOR SETTINGS
SESSION_TIMEOUT  = 180
MAINTENANCE_MODE = False
PAGE_SIZE        = 10
CACHE_TTL        = 15

# 9. SECOND BOT TOKEN (Broadcast fallback ke liye)
SECOND_BOT_TOKEN = "8642245501:AAGYDhvomuulvAwG-Psco9TSNkscLZ3G2NU"

# 10. CRYPTO WALLET ADDRESSES (payment ke liye)
WALLET_USDT_TRC20 = "TFM71mHznKPQVUKE6nE9SKmiSmG5GW8PUg"
WALLET_USDT_BEP20 = "0x2cb31fc4cad2058926b8733e603e8ed13c706637"
WALLET_USDT_ERC20 = "0x2cb31fc4cad2058926b8733e603e8ed13c706637"
WALLET_BTC        = "13BeEVpjkQErHhPTdLd6CnBp8RRzRxmJMN"
WALLET_ETH_ERC20  = "0x2cb31fc4cad2058926b8733e603e8ed13c706637"
WALLET_LTC        = "LTYDLqisVrSYrDdvjHfyB43j3Nvrq5oGkn"

# 11. PRICING PLANS
LIMITED_PLANS = {
    'l1':    {'name': '1 Search',     'price': '$0.50'},
    'l5':    {'name': '5 Searches',    'price': '$2.50'},
    'l10':   {'name': '10 Searches',   'price': '$4.00'},
    'l20':   {'name': '20 Searches',   'price': '$7.00'},
    'l30':   {'name': '30 Searches',   'price': '$10.00'},
    'l50':   {'name': '50 Searches',   'price': '$15.00'},
    'l100':  {'name': '100 Searches',  'price': '$25.00'},
    'l200':  {'name': '200 Searches',  'price': '$40.00'},
    'l500':  {'name': '500 Searches',  'price': '$75.00'},
    'l1000': {'name': '1000 Searches', 'price': '$100.00'},
}

UNLIMITED_PLANS = {
    'u1d':   {'name': '1 Day Unlimited',    'price': '$2.50'},
    'u3d':   {'name': '3 Days Unlimited',   'price': '$5.00'},
    'u7d':   {'name': '7 Days Unlimited',   'price': '$9.00'},
    'u15d':  {'name': '15 Days Unlimited',  'price': '$15.00'},
    'u1m':   {'name': '1 Month Unlimited',  'price': '$25.00'},
    'u3m':   {'name': '3 Months Unlimited', 'price': '$60.00'},
    'u6m':   {'name': '6 Months Unlimited', 'price': '$80.00'},
    'u12m':  {'name': '1 Year Unlimited',   'price': '$99.00'},
    'ulife': {'name': 'Lifetime Unlimited', 'price': '$149.00'},
}

DIVIDER = "━━━━━━━━━━━━━━━"

# =====================================================================
#                  CONFIG SECTION END
# =====================================================================


ocr_solver_beta = ddddocr.DdddOcr(show_ad=False, beta=True)
ocr_solver_std  = ddddocr.DdddOcr(show_ad=False, beta=False)


def preprocess_captcha(image_bytes):
    if not _PIL_AVAILABLE:
        return image_bytes
    try:
        img = Image.open(BytesIO(image_bytes)).convert('L')
        new_w = img.width * 2
        new_h = img.height * 2
        img = img.resize((new_w, new_h), Image.LANCZOS)
        img = img.filter(ImageFilter.SHARPEN)
        img = ImageEnhance.Contrast(img).enhance(2.2)
        out = BytesIO()
        img.save(out, format='PNG')
        return out.getvalue()
    except Exception:
        return image_bytes


def solve_captcha_robust(image_bytes, chat_id="system"):
    start_time = time.time()
    captcha_code = ""

    try:
        prep_bytes = preprocess_captcha(image_bytes)
        r = ocr_solver_beta.classification(prep_bytes)
        if r:
            code = re.sub(r'[^a-zA-Z0-9]', '', r.strip())
            if len(code) == 6:
                captcha_code = code
    except Exception:
        pass

    if not captcha_code:
        try:
            r = ocr_solver_beta.classification(image_bytes)
            if r:
                code = re.sub(r'[^a-zA-Z0-9]', '', r.strip())
                if len(code) == 6:
                    captcha_code = code
        except Exception:
            pass

    ocr_dur = time.time() - start_time
    if captcha_code:
        log_activity(chat_id, "solve_captcha", "success", duration=ocr_dur)
    else:
        log_activity(chat_id, "solve_captcha", "failed", duration=ocr_dur, error="Failed to solve captcha locally (must be 6 chars)")

    return captcha_code


def get_session_proxy(proxy_url: str, session_id: int) -> str:
    if not proxy_url:
        return None
    try:
        parsed = urlparse(proxy_url)
        if parsed.username:
            session_suffix = f"-{session_id}"
            if parsed.username.endswith(session_suffix):
                return proxy_url
            new_username = f"{parsed.username}-{session_id}"
            netloc = f"{new_username}:{parsed.password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
    except Exception:
        pass
    return proxy_url


PROXY_CONFIG = {
    'use_proxy': len(UIDAI_PROXIES) > 0,
    'http': None,
    'https': None
}

_proxy_failures: dict = {p: 0 for p in UIDAI_PROXIES}
_proxy_lock = threading.Lock()


def _pick_proxy() -> str:
    with _proxy_lock:
        if not UIDAI_PROXIES:
            return None
        min_fail = min(_proxy_failures.get(p, 0) for p in UIDAI_PROXIES)
        candidates = [p for p in UIDAI_PROXIES if _proxy_failures.get(p, 0) == min_fail]
        return random.choice(candidates)


def _mark_proxy_ok(proxy_url: str):
    with _proxy_lock:
        _proxy_failures[proxy_url] = 0


def _mark_proxy_fail(proxy_url: str):
    with _proxy_lock:
        _proxy_failures[proxy_url] = _proxy_failures.get(proxy_url, 0) + 1
        logger.warning(f"Proxy failure count for {proxy_url.split('@')[-1]}: {_proxy_failures[proxy_url]}")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


class FastHTTPAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, socket_options=None, **kwargs):
        self.socket_options = socket_options
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        if self.socket_options is not None:
            pool_kwargs['socket_options'] = self.socket_options
        return super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        if self.socket_options is not None:
            proxy_kwargs['socket_options'] = self.socket_options
        return super().proxy_manager_for(proxy, **proxy_kwargs)


def create_session(use_proxy=False, proxy_string=None):
    session = requests.Session()

    socket_opts = [
        (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
        (socket.SOL_SOCKET, socket.SO_RCVBUF, 524288),
        (socket.SOL_SOCKET, socket.SO_SNDBUF, 262144),
    ]
    adapter = FastHTTPAdapter(
        socket_options=socket_opts,
        pool_connections=50,
        pool_maxsize=50,
        max_retries=1,
        pool_block=False
    )
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.headers.update({
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    if use_proxy and proxy_string:
        parsed = urlparse(proxy_string)
        proxy_url = f"{parsed.scheme}://{parsed.netloc}"
        session.proxies = {'http': proxy_url, 'https': proxy_url}
        logger.debug(f"Proxy set locally in session: {proxy_url.split('@')[-1]}")
    else:
        logger.debug("No proxy set in this session (direct connection)")
    return session


captcha_prefetch_cache = {}
captcha_prefetch_lock = threading.Lock()


def prefetch_captcha_async(chat_id, revamp=False):
    def _worker():
        try:
            image_bytes, captcha_txn_id, transaction_id, captcha_proxy = bot.get_captcha(chat_id, revamp=revamp)
            if image_bytes:
                captcha_code = solve_captcha_robust(image_bytes, chat_id)
                if captcha_code and len(captcha_code) >= 5:
                    with captcha_prefetch_lock:
                        captcha_prefetch_cache[chat_id] = {
                            'image_bytes': image_bytes,
                            'captcha_txn_id': captcha_txn_id,
                            'transaction_id': transaction_id,
                            'captcha_proxy': captcha_proxy,
                            'captcha_code': captcha_code,
                            'time': time.time(),
                            'revamp': revamp
                        }
        except Exception as e:
            logger.debug(f"Prefetch captcha error: {e}")
    threading.Thread(target=_worker, daemon=True).start()


def get_prefetched_captcha(chat_id, revamp=False):
    with captcha_prefetch_lock:
        item = captcha_prefetch_cache.pop(chat_id, None)
        if item and item.get('revamp') == revamp and (time.time() - item['time'] < 90):
            return item
    return None


thread_local = threading.local()


def reset_uidai_session():
    thread_local.uidai_session = None


_telegram_global_session = None
_telegram_session_lock = threading.Lock()


def get_telegram_session():
    global _telegram_global_session
    if _telegram_global_session is None:
        with _telegram_session_lock:
            if _telegram_global_session is None:
                s = requests.Session()
                socket_opts = [
                    (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
                    (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                ]
                adapter = FastHTTPAdapter(
                    socket_options=socket_opts,
                    pool_connections=100, pool_maxsize=100, max_retries=2, pool_block=False
                )
                s.mount('https://', adapter)
                s.mount('http://', adapter)
                s.headers.update({
                    'Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                _telegram_global_session = s
    return _telegram_global_session


def get_uidai_session(proxy_hint=None, session_id=None, force_direct=False):
    if not force_direct and PROXY_CONFIG['use_proxy']:
        env_proxy = os.environ.get('PROXY_URL', '').strip()
        if env_proxy:
            return create_session(True, env_proxy), env_proxy
        elif UIDAI_PROXIES:
            proxy = proxy_hint if proxy_hint else _pick_proxy()
            if session_id and not proxy_hint:
                safe_session_id = (abs(int(session_id)) % 99999) + 1
                proxy = get_session_proxy(proxy, safe_session_id)
            if _proxy_failures.get(proxy, 0) < 3:
                return create_session(True, proxy), proxy
    return create_session(False), None


def clean_user_error(err_str):
    if not err_str:
        return "Government Portal Busy / Technical Error. [Govt Site Issue - NOT Bot Issue] Please try again."
    err_lower = str(err_str).lower()
    if any(x in err_lower for x in ["httpsconnectionpool", "connection", "read timed out", "timeout", "timed out", "ssl", "ssleoferror", "max retries", "disconnected", "socket", "http", "api", "url", "tathya", "uidai", "dns", "proxy"]):
        return "Government Portal Busy / Network Timeout. [Govt Site Issue - NOT Bot Issue] Please retry."
    if "captcha" in err_lower:
        return "Government Portal Busy / Captcha Server Error. [Govt Site Issue - NOT Bot Issue] Please try again."
    if "technical difficulties" in err_lower or "server error" in err_lower or "500" in err_lower or "502" in err_lower or "503" in err_lower or "service unavailable" in err_lower:
        return "Government Portal is experiencing technical difficulties. [Govt Site Issue - NOT Bot Issue] Please try again."
    if "no record" in err_lower or "not found" in err_lower:
        return "No Records Found for the provided details."
    if "permissible limit" in err_lower or "exceeded" in err_lower or "regenerate the otp" in err_lower:
        return "OTP limit exceeded or OTP already used. Please request a NEW OTP after a few minutes."
    if "otp" in err_lower and ("invalid" in err_lower or "incorrect" in err_lower or "expired" in err_lower or "wrong" in err_lower):
        return "Invalid or Expired OTP. Please retry."
    if "eid" in err_lower and ("invalid" in err_lower or "format" in err_lower):
        return "Invalid EID format. Please check and retry."

    if any(tech in err_lower for tech in ["http", "host", "port", "traceback", "exception", "line ", "error", "failed", "call", "tathya", "uidai", "api", "url", ".py", "c:\\", "/"]):
        return "Govt Portal Technical Error. [Govt Site Issue - NOT Bot Issue] Please try again."

    clean = re.sub(r'\s+', ' ', str(err_str)).strip()
    if len(clean) > 50:
        return "Govt Portal Technical Error. [Govt Site Issue - NOT Bot Issue] Please try again."
    return clean


_SENTINEL = object()


class PDFPasswordCracker:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=16)
        self.found_password = None
        self.stop_flag = False
        self.progress = 0
        self.total_years = 0

    def try_password(self, pdf_bytes, password):
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            if pdf_reader.decrypt(password):
                return True, password
            return False, None
        except Exception:
            return False, None

    def decrypt_pdf(self, pdf_path, password, output_path=None):
        try:
            if output_path is None:
                output_path = pdf_path.replace('.pdf', '_decrypted.pdf')
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_reader.decrypt(password)
                pdf_writer = PyPDF2.PdfWriter()
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
            logger.info(f"Decrypted PDF saved: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error decrypting PDF: {e}")
            return None

    def crack_pdf(self, pdf_path, name, dob=None, progress_callback=None):
        self.found_password = None
        self.stop_flag = False
        self.progress = 0

        try:
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
        except Exception as e:
            logger.error(f"Failed to read PDF for cracking: {e}")
            return False, None, None

        name_upper = name.upper()

        unique_prefixes = []
        seen_pref = set()

        name_letters = "".join(c for c in name_upper if c.isalpha())
        if name_letters:
            unique_prefixes.append(name_letters)

        name_no_spaces = name_upper.replace(" ", "")
        if name_no_spaces:
            unique_prefixes.append(name_no_spaces)

        words = [w for w in name_upper.split() if w]
        if words:
            unique_prefixes.append(words[0])

        unique_prefixes.append(name_upper)

        prefixes_to_use = []
        for p in unique_prefixes:
            p = p.strip()
            if p and p not in seen_pref:
                seen_pref.add(p)
                prefixes_to_use.append(p)

        birth_year = None
        if dob:
            match = re.search(r'\b(19\d\d|20[0-2]\d)\b', str(dob))
            if match:
                birth_year = int(match.group(1))
                logger.info(f"PDF Crack - extracted birth year from DOB: {birth_year}")

        if birth_year:
            common_years = [birth_year, birth_year - 1, birth_year + 1]
        else:
            current_year = datetime.now().year
            y_80_10 = list(range(1980, 2011))
            y_70_79 = list(range(1970, 1980))
            y_11_now = list(range(2011, current_year + 1))
            y_others = list(range(1940, 1970)) + list(range(1930, 1940))
            common_years = y_80_10 + y_70_79 + y_11_now + y_others

        highly_likely = []
        for year in common_years:
            for pref in prefixes_to_use:
                p4 = pref[:4]
                highly_likely.append(f"{p4}{year}")

        secondary = []
        for year in common_years:
            for pref in prefixes_to_use:
                p4 = pref[:4]
                secondary.append(f"{p4.lower()}{year}")
                secondary.append(f"{p4.title()}{year}")
                if len(pref) >= 6:
                    p6 = pref[:6]
                    secondary.append(f"{p6}{year}")
                    secondary.append(f"{p6.lower()}{year}")

        rare = []
        name_full = name_upper[:10] if len(name_upper) > 10 else name_upper
        for year in common_years:
            for pref in prefixes_to_use:
                p4 = pref[:4]
                rare.append(f"{year}@{p4}")
                rare.append(f"{p4}@{year}")
                rare.append(f"{p4}#{year}")
                rare.append(f"{p4}!{year}")
            rare.append(f"{name_full}{year}")

        prioritized_passwords = []
        seen = set()
        for pwd in (highly_likely + secondary + rare):
            if pwd not in seen:
                seen.add(pwd)
                prioritized_passwords.append(pwd)

        no_year_fallback = []
        for pref in prefixes_to_use:
            p4 = pref[:4]
            no_year_fallback.extend([p4, p4.lower(), p4.title()])
            if len(pref) >= 6:
                p6 = pref[:6]
                no_year_fallback.extend([p6, p6.lower()])

        for pwd in no_year_fallback:
            if pwd not in seen:
                seen.add(pwd)
                prioritized_passwords.append(pwd)

        num_workers = 16
        chunk_size = (len(prioritized_passwords) + num_workers - 1) // num_workers
        chunks = [prioritized_passwords[i:i+chunk_size] for i in range(0, len(prioritized_passwords), chunk_size)]

        state = {'found': False, 'password': None}

        def worker_task(pdf_data, password_chunk, worker_state):
            try:
                reader = PyPDF2.PdfReader(BytesIO(pdf_data))
                for pwd in password_chunk:
                    if worker_state['found'] or self.stop_flag:
                        break
                    if reader.decrypt(pwd):
                        worker_state['found'] = True
                        worker_state['password'] = pwd
                        self.stop_flag = True
                        return True, pwd
            except Exception:
                pass
            return False, None

        logger.info(f"PDF Crack - starting chunked decryption of {len(prioritized_passwords)} candidate passwords across {num_workers} threads...")
        t_crack_start = time.time()

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_task, pdf_bytes, chunk, state) for chunk in chunks]
            for future in as_completed(futures):
                try:
                    success, found_pwd = future.result()
                    if success:
                        self.found_password = found_pwd
                except Exception:
                    pass

        crack_duration = time.time() - t_crack_start
        if self.found_password:
            logger.info(f"PDF Crack - Success! Password found: '{self.found_password}' in {crack_duration:.4f}s")
            decrypted_path = self.decrypt_pdf(pdf_path, self.found_password)
            return True, self.found_password, decrypted_path if decrypted_path else None
        else:
            logger.warning(f"PDF Crack - Failed to decrypt PDF. Tried {len(prioritized_passwords)} passwords in {crack_duration:.4f}s")
            return False, None, None


class AadhaarBot:
    def __init__(self):
        self.base_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en_IN',
            'Content-Type': 'application/json',
            'Origin': 'https://myaadhaar.uidai.gov.in',
            'Referer': 'https://myaadhaar.uidai.gov.in/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
            'appid': 'MYAADHAAR',
            'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'dnt': '1',
        }
        self.stable_download_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en_IN',
            'Content-Type': 'application/json',
            'Origin': 'https://myaadhaar.uidai.gov.in',
            'Referer': 'https://myaadhaar.uidai.gov.in/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
            'appid': 'MYAADHAAR',
            'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'dnt': '1',
        }
        logger.info("AadhaarBot initialized")
        self.cracker = PDFPasswordCracker()

    def _get_sess(self, proxy_hint=None, session_id=None, force_direct=False):
        sess, proxy_url = get_uidai_session(proxy_hint, session_id, force_direct=force_direct)
        sess.headers.update(self.base_headers)
        return sess, proxy_url

    def _get_sess_revamp(self, proxy_hint=None, session_id=None, force_direct=False):
        sess, proxy_url = get_uidai_session(proxy_hint, session_id, force_direct=force_direct)
        revamp_headers = self.base_headers.copy()
        revamp_headers.update({
            "Origin":             "https://myaadhaarbeta.uidai.gov.in",
            "Referer":            "https://myaadhaarbeta.uidai.gov.in/",
            "appid":              "MYAADHAARREVAMP",
            "User-Agent":         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
            "sec-ch-ua":          '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
            "sec-ch-ua-mobile":   "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Accept-Encoding":    "gzip, deflate",
            "Accept-Language":    "en_IN",
            "dnt":                "1",
        })
        sess.headers.update(revamp_headers)
        return sess, proxy_url

    def generate_transaction_id(self):
        return str(uuid.uuid4())

    def is_base64(self, s):
        if not isinstance(s, str) or len(s) < 100:
            return False
        if s.startswith('data:'):
            s = s.split(',')[1] if ',' in s else s
        if len(s) % 4 != 0:
            return False
        try:
            base64.b64decode(s)
            return True
        except Exception:
            return False

    def detect_file_type(self, file_bytes):
        if file_bytes[:4] == b'%PDF':
            return 'pdf'
        elif file_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            return 'png'
        elif file_bytes[:2] == b'\xff\xd8':
            return 'jpg'
        return 'unknown'

    def extract_pdf_bytes_fast(self, data):
        if isinstance(data, dict):
            for key in ['aadhaarPdf', 'pdfData', 'pdf', 'fileBytes', 'file', 'data', 'byteArray', 'aadhaarData']:
                val = data.get(key)
                if isinstance(val, str) and len(val) > 100:
                    try:
                        clean_b64 = val.split(',')[1] if val.startswith('data:') and ',' in val else val
                        b = base64.b64decode(clean_b64)
                        if self.detect_file_type(b) == 'pdf':
                            return b
                    except Exception:
                        pass
                elif isinstance(val, dict):
                    res = self.extract_pdf_bytes_fast(val)
                    if res:
                        return res

        decoded_items = self.detect_and_decode_base64(data)
        for item in decoded_items:
            if item.get('type') == 'pdf':
                return item.get('data')
            elif item.get('data'):
                return item.get('data')
        return None

    def detect_and_decode_base64(self, data, field_name="unknown", save=False):
        decoded_items = []
        if isinstance(data, dict):
            for key, value in list(data.items()):
                if isinstance(value, str) and len(value) > 100 and self.is_base64(value):
                    try:
                        clean_base64 = value.split(',')[1] if value.startswith('data:') and ',' in value else value
                        decoded_bytes = base64.b64decode(clean_base64)
                        file_type = self.detect_file_type(decoded_bytes)
                        if save and file_type in ['pdf', 'png', 'jpg']:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            ext = {'pdf': 'pdf', 'png': 'png', 'jpg': 'jpg'}.get(file_type, 'bin')
                            filename = os.path.abspath(f"decoded_{field_name}_{key}_{timestamp}.{ext}")
                            with open(filename, 'wb') as f:
                                f.write(decoded_bytes)
                            decoded_items.append({'field': key, 'filename': filename, 'type': file_type, 'size': len(decoded_bytes), 'data': decoded_bytes})
                            logger.info(f"Saved: {filename}")
                        elif not save:
                            decoded_items.append({'field': key, 'type': file_type, 'size': len(decoded_bytes), 'data': decoded_bytes})
                    except Exception as e:
                        logger.error(f"Base64 decode error: {e}")
                if isinstance(value, (dict, list)):
                    decoded_items.extend(self.detect_and_decode_base64(value, f"{field_name}.{key}", save))
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    decoded_items.extend(self.detect_and_decode_base64(item, f"{field_name}[{idx}]", save))
        return decoded_items

    def get_captcha(self, user_id, _retries=3, _delay=0.1, revamp=False):
        captcha_data = {
            'captchaLength': '6',
            'captchaType': '2',
            'audioCaptchaRequired': False
        }
        for attempt in range(1, _retries + 1):
            transaction_id = self.generate_transaction_id()
            reset_uidai_session()
            if attempt > 1:
                time.sleep(_delay)
            proxy_url = None
            try:
                force_direct = (attempt == _retries)
                sess, proxy_url = self._get_sess_revamp(session_id=user_id, force_direct=force_direct) if revamp else self._get_sess(session_id=user_id, force_direct=force_direct)
                sess.headers.update({'x-request-id': transaction_id, 'transactionId': transaction_id})
                response = sess.post(
                    'https://tathya.uidai.gov.in/audioCaptchaService/api/captcha/v3/generation',
                    json=captcha_data, timeout=(15, 20)
                )
                if response.status_code != 200:
                    logger.warning(f"Captcha HTTP {response.status_code} (attempt {attempt})")
                    if proxy_url:
                        _mark_proxy_fail(proxy_url)
                    continue
                resp_json = response.json()
                captcha_txn_id = resp_json.get('transactionId')
                captcha_base64 = resp_json.get('imageBase64')
                if not captcha_base64:
                    for key, value in resp_json.items():
                        if isinstance(value, str) and len(value) > 100 and self.is_base64(value):
                            captcha_base64 = value
                            break
                if not captcha_base64:
                    logger.warning(f"No captcha image in response (attempt {attempt})")
                    if proxy_url:
                        _mark_proxy_fail(proxy_url)
                    continue
                if captcha_base64.startswith('data:image'):
                    captcha_base64 = captcha_base64.split(',')[1]
                image_bytes = base64.b64decode(captcha_base64)
                if proxy_url:
                    _mark_proxy_ok(proxy_url)
                return image_bytes, captcha_txn_id, transaction_id, proxy_url
            except Exception as e:
                logger.error(f"Error getting captcha (attempt {attempt}/{_retries}): {str(e)}")
                if proxy_url:
                    _mark_proxy_fail(proxy_url)
        return None, None, None, None

    def send_aadhaar_otp(self, user_id, eid_number, captcha_value, captcha_txn_id, transaction_id, proxy_hint=None):
        sess, proxy_url = self._get_sess(proxy_hint, session_id=user_id)
        sess.headers.update({'x-request-id': transaction_id, 'transactionId': transaction_id})

        clean_id = str(eid_number).strip().replace(' ', '').replace('/', '')
        if len(clean_id) == 12:
            otp_request_data = {
                'uidNumber': clean_id, 'idType': 'uid',
                'captchaTxnId': captcha_txn_id, 'captchaValue': captcha_value,
                'transactionId': transaction_id, 'resendOTP': False
            }
        else:
            otp_request_data = {
                'eidNumber': eid_number, 'idType': 'eid',
                'captchaTxnId': captcha_txn_id, 'captchaValue': captcha_value,
                'transactionId': transaction_id, 'resendOTP': False
            }
        last_exc = None
        for attempt in range(1, 4):
            try:
                response = sess.post(
                    'https://tathya.uidai.gov.in/unifiedAppAuthService/api/v2/generate/aadhaar/otp',
                    json=otp_request_data, timeout=20
                )
                if response.status_code == 200:
                    resp_json = response.json()
                    otp_txn_id = resp_json.get('txnId') or resp_json.get('transactionId') or resp_json.get('otpTxnId')
                    status = resp_json.get('status')
                    message = resp_json.get('message')
                    if otp_txn_id and status == "Success":
                        if proxy_url:
                            _mark_proxy_ok(proxy_url)
                        return True, otp_txn_id, message
                    else:
                        return False, None, message
                else:
                    last_exc = f"HTTP {response.status_code}"
            except Exception as e:
                last_exc = str(e)
                if proxy_url:
                    _mark_proxy_fail(proxy_url)
                sess, proxy_url = self._get_sess(None, session_id=user_id, force_direct=(attempt >= 2))
                sess.headers.update({'x-request-id': transaction_id, 'transactionId': transaction_id})
                if attempt < 3:
                    time.sleep(0.5)
        return False, None, last_exc

    def download_aadhaar_pdf(self, user_id, eid_number, otp, otp_txn_id, transaction_id, mask=False, proxy_hint=None):
        clean_id = str(eid_number).strip().replace(' ', '').replace('/', '')
        clean_otp = str(otp).strip()
        if len(clean_id) == 12:
            download_data = {
                'uidNumber': clean_id,
                'uid': clean_id,
                'mask': mask,
                'otp': clean_otp,
                'otpTxnId': otp_txn_id
            }
        else:
            download_data = {
                'eid': eid_number,
                'mask': mask,
                'otp': clean_otp,
                'otpTxnId': otp_txn_id
            }
        tag = get_user_log_tag(user_id)

        retries = 3
        last_error = None
        for attempt in range(1, retries + 1):
            p_hint = proxy_hint
            sess, proxy_url = self._get_sess(p_hint, session_id=user_id)
            sess.headers.update(self.stable_download_headers)
            sess.headers.update({
                'x-request-id': transaction_id,
                'transactionId': transaction_id
            })
            route_str = f"proxy {proxy_url.split('@')[-1]}" if proxy_url else "Direct Connection"
            start_time = time.time()
            try:
                logger.info(f"[PDF Download] {tag} Attempt {attempt}/{retries} starting ({route_str})...")
                response = sess.post(
                    'https://tathya.uidai.gov.in/downloadAadhaarService/api/aadhaar/download',
                    json=download_data, timeout=90, stream=True
                )

                chunks = []
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        chunks.append(chunk)
                raw_data = b"".join(chunks)

                resp_json = {}
                if raw_data:
                    try:
                        resp_json = json.loads(raw_data)
                    except Exception:
                        pass

                duration = time.time() - start_time
                status_msg = resp_json.get('status') or resp_json.get('message') or resp_json.get('statusMessage') if isinstance(resp_json, dict) else "N/A"
                logger.info(f"UIDAI Download API responded in {duration:.2f}s (HTTP {response.status_code} | Status: {status_msg})")
                if response.status_code == 200:
                    t_decode_start = time.time()
                    pdf_bytes = self.extract_pdf_bytes_fast(resp_json)
                    if pdf_bytes:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = os.path.abspath(f"decoded_aadhaar_download_pdf_{timestamp}.pdf")
                        with open(filename, 'wb') as f:
                            f.write(pdf_bytes)
                        logger.info(f"Fast extracted & saved PDF ({len(pdf_bytes)} bytes): {filename} in {time.time() - t_decode_start:.4f}s")
                        if proxy_url:
                            _mark_proxy_ok(proxy_url)
                        log_activity(user_id, "download_pdf", "success", duration)
                        return True, filename

                    decoded_files = self.detect_and_decode_base64(resp_json, "aadhaar_download", save=True)
                    if decoded_files:
                        if proxy_url:
                            _mark_proxy_ok(proxy_url)
                        log_activity(user_id, "download_pdf", "success", duration)
                        return True, decoded_files[0]['filename']
                    else:
                        extracted_err = None
                        if isinstance(resp_json, dict):
                            err_details = resp_json.get('errorDetails')
                            if isinstance(err_details, dict):
                                extracted_err = err_details.get('messageEnglish') or err_details.get('message')
                            if not extracted_err:
                                extracted_err = resp_json.get('message') or resp_json.get('errorMessage') or resp_json.get('errorDescription')

                        error_msg = extracted_err if extracted_err else "Download Error: Invalid OTP / No PDF data received"
                        logger.warning(f"PDF Download Error: {error_msg} | Full JSON: {resp_json}")
                        log_activity(user_id, "download_pdf", "failed", duration, error=error_msg)
                        return False, error_msg
                else:
                    error_msg = f"Govt Portal Server Error (HTTP {response.status_code})"
                    if resp_json:
                        extracted_err = resp_json.get('message') or resp_json.get('errorMessage') or resp_json.get('errorDetails', {}).get('messageEnglish')
                        if extracted_err:
                            error_msg = extracted_err
                    last_error = error_msg
                    logger.warning(f"PDF Download Attempt {attempt} failed (HTTP {response.status_code}): {error_msg}")
                    if any(x in error_msg.lower() for x in ["expired", "invalid", "incorrect", "validation", "exceeded", "not generated", "limit", "regenerate"]):
                        log_activity(user_id, "download_pdf", "failed", duration, error=error_msg)
                        return False, error_msg
            except Exception as e:
                duration = time.time() - start_time
                logger.warning(f"Download PDF attempt {attempt} exception ({duration:.2f}s): {e}")
                last_error = str(e)
                if proxy_url:
                    _mark_proxy_fail(proxy_url)
                if "incompleteread" in str(e).lower() or "connection broken" in str(e).lower():
                    error_msg = "Network connection dropped during PDF download. The OTP was consumed. Please generate a new OTP."
                    log_activity(user_id, "download_pdf", "failed", duration, error=error_msg)
                    return False, error_msg

            if attempt < retries:
                time.sleep(1)

        duration = time.time() - start_time
        error_msg = "Govt Portal Connection Error. Please retry."
        if last_error:
            if "timed out" in last_error.lower() or "timeout" in last_error.lower():
                error_msg = "Govt Portal Server Timeout. Please retry."
            else:
                error_msg = f"Download failed: {last_error}"
        log_activity(user_id, "download_pdf", "failed", duration, error=error_msg)
        return False, error_msg

    def send_eid_otp(self, user_id, mobile, name, captcha_code, captcha_txn_id, transaction_id, proxy_hint=None):
        reset_uidai_session()
        sess, proxy_url = self._get_sess_revamp(proxy_hint, session_id=user_id)
        sess.headers.update({'x-request-id': transaction_id, 'transactionId': transaction_id})
        request_data = {
            'mobileNumber': mobile, 'dob': None, 'email': None,
            'name': name.upper(), 'option': 'EID', 'otp': None,
            'otpTxnId': None, 'captchaTxnId': captcha_txn_id,
            'captcha': captcha_code, 'resendOtp': False
        }
        try:
            response = sess.post(
                'https://tathya.uidai.gov.in/retrieveEidUid/ext/v1/generic/retrieveuideid',
                json=request_data, timeout=45
            )
            if response.status_code == 200:
                resp_json = response.json()
                if 'responseData' in resp_json:
                    response_data = resp_json['responseData']
                    otp_txn_id = response_data.get('otpTxnId')
                    status = response_data.get('status')
                    if otp_txn_id and status == "Success":
                        if proxy_url:
                            _mark_proxy_ok(proxy_url)
                        return True, otp_txn_id
                    else:
                        return False, response_data.get('message', 'Unknown error')
                else:
                    err_msg = resp_json.get('message') or resp_json.get('errorDetails', {}).get('messageEnglish') or resp_json.get('errorMessage') or 'Invalid response'
                    return False, err_msg
            else:
                return False, f'HTTP {response.status_code}'
        except Exception as e:
            if proxy_url:
                _mark_proxy_fail(proxy_url)
            return False, str(e)

    def verify_eid_otp(self, user_id, mobile, name, otp_code, otp_txn_id, captcha_txn_id, captcha_code, proxy_hint=None):
        reset_uidai_session()
        sess, proxy_url = self._get_sess_revamp(proxy_hint, session_id=user_id)
        sess.headers.update({'x-request-id': self.generate_transaction_id()})
        verify_data = {
            'mobileNumber': mobile, 'dob': None, 'name': name.upper(),
            'email': None, 'option': 'EID', 'otp': otp_code,
            'otpTxnId': otp_txn_id, 'captchaTxnId': captcha_txn_id,
            'captcha': captcha_code, 'resendOtp': False
        }
        start_time = time.time()
        try:
            response = sess.post(
                'https://tathya.uidai.gov.in/retrieveEidUid/ext/v1/generic/retrieveuideid',
                json=verify_data, timeout=45
            )

            resp_json = {}
            if response.content:
                try:
                    resp_json = response.json()
                except Exception:
                    pass

            duration = time.time() - start_time
            if response.status_code == 200:
                response_data = resp_json.get('responseData')
                if isinstance(response_data, dict) and response_data.get('eidNumber'):
                    eid_number = response_data.get('eidNumber')
                    name_from_response = response_data.get('name', name)
                    dob_from_response = response_data.get('dob')
                    if proxy_url:
                        _mark_proxy_ok(proxy_url)
                    log_activity(user_id, "retrieve_eid", "success", duration)
                    return True, eid_number, name_from_response, dob_from_response

                error_details = resp_json.get('errorDetails')
                error_msg = error_details.get('messageEnglish') if isinstance(error_details, dict) else None
                if not error_msg:
                    error_msg = (response_data or {}).get('message') if isinstance(response_data, dict) else None
                if not error_msg:
                    error_msg = resp_json.get('message') or resp_json.get('errorMessage') or 'Verification failed'

                log_activity(user_id, "retrieve_eid", "failed", duration, error=error_msg)
                return False, None, error_msg, None
            else:
                error_msg = f'HTTP {response.status_code}'
                if resp_json:
                    extracted_err = resp_json.get('message') or resp_json.get('errorMessage') or resp_json.get('errorDetails', {}).get('messageEnglish')
                    if extracted_err:
                        error_msg = extracted_err
                log_activity(user_id, "retrieve_eid", "failed", duration, error=error_msg)
                return False, None, error_msg, None
        except Exception as e:
            duration = time.time() - start_time
            if proxy_url:
                _mark_proxy_fail(proxy_url)
            log_activity(user_id, "retrieve_eid", "failed", duration, error=str(e))
            return False, None, str(e), None

    def send_uid_sms_otp(self, user_id, mobile, name, captcha_code, captcha_txn_id, transaction_id, proxy_hint=None):
        reset_uidai_session()
        sess, proxy_url = self._get_sess_revamp(proxy_hint, session_id=user_id)
        sess.headers.update({'x-request-id': transaction_id, 'transactionId': transaction_id})
        request_data = {
            'mobileNumber': mobile, 'dob': None, 'email': None,
            'name': name.upper(), 'option': 'UID', 'otp': None,
            'otpTxnId': None, 'captchaTxnId': captcha_txn_id,
            'captcha': captcha_code, 'resendOtp': False
        }
        try:
            response = sess.post(
                'https://tathya.uidai.gov.in/retrieveEidUid/ext/v1/generic/retrieveuideid',
                json=request_data, timeout=45
            )
            if response.status_code == 200:
                resp_json = response.json()
                if 'responseData' in resp_json:
                    response_data = resp_json['responseData']
                    otp_txn_id = response_data.get('otpTxnId')
                    status = response_data.get('status')
                    if otp_txn_id and status == "Success":
                        if proxy_url:
                            _mark_proxy_ok(proxy_url)
                        return True, otp_txn_id
                    else:
                        return False, response_data.get('message', 'Unknown error')
                else:
                    err_msg = resp_json.get('message') or resp_json.get('errorDetails', {}).get('messageEnglish') or resp_json.get('errorMessage') or 'Invalid response'
                    return False, err_msg
            else:
                return False, f'HTTP {response.status_code}'
        except Exception as e:
            if proxy_url:
                _mark_proxy_fail(proxy_url)
            return False, str(e)

    def verify_uid_sms_otp(self, user_id, mobile, name, otp_code, otp_txn_id, captcha_txn_id, captcha_code, proxy_hint=None):
        reset_uidai_session()
        sess, proxy_url = self._get_sess_revamp(proxy_hint, session_id=user_id)
        sess.headers.update({'x-request-id': self.generate_transaction_id()})
        verify_data = {
            'mobileNumber': mobile, 'dob': None, 'name': name.upper(),
            'email': None, 'option': 'UID', 'otp': otp_code,
            'otpTxnId': otp_txn_id, 'captchaTxnId': captcha_txn_id,
            'captcha': captcha_code, 'resendOtp': False
        }
        start_time = time.time()
        try:
            response = sess.post(
                'https://tathya.uidai.gov.in/retrieveEidUid/ext/v1/generic/retrieveuideid',
                json=verify_data, timeout=45
            )

            resp_json = {}
            if response.content:
                try:
                    resp_json = response.json()
                except Exception:
                    pass

            duration = time.time() - start_time
            if response.status_code == 200:
                response_data = resp_json.get('responseData') if isinstance(resp_json.get('responseData'), dict) else {}
                uid_number = response_data.get('uidNumber') or response_data.get('uid')
                name_from_response = response_data.get('name') or name
                dob_from_response = response_data.get('dob') or "N/A"
                res_status = str(resp_json.get('status', '')).lower()
                resp_data_status = str(response_data.get('status', '')).lower()

                if uid_number or res_status == "success" or resp_data_status == "success":
                    if proxy_url:
                        _mark_proxy_ok(proxy_url)
                    log_activity(user_id, "retrieve_uid_sms", "success", duration)
                    return True, uid_number, name_from_response, dob_from_response

                error_details = resp_json.get('errorDetails')
                error_msg = error_details.get('messageEnglish') if isinstance(error_details, dict) else None
                if not error_msg:
                    error_msg = response_data.get('message')
                if not error_msg:
                    error_msg = resp_json.get('message') or resp_json.get('errorMessage') or 'Verification failed'

                logger.warning(f"Aadhaar SMS verification failed: {error_msg} | Full JSON: {resp_json}")
                log_activity(user_id, "retrieve_uid_sms", "failed", duration, error=error_msg)
                return False, None, error_msg, None
            else:
                error_msg = f'HTTP {response.status_code}'
                log_activity(user_id, "retrieve_uid_sms", "failed", duration, error=error_msg)
                return False, None, error_msg, None
        except Exception as e:
            duration = time.time() - start_time
            if proxy_url:
                _mark_proxy_fail(proxy_url)
            log_activity(user_id, "retrieve_uid_sms", "failed", duration, error=str(e))
            return False, None, str(e), None

    def crack_pdf_with_name(self, pdf_path, name, dob=None, progress_callback=None):
        success, password, decrypted_path = self.cracker.crack_pdf(pdf_path, name, dob, progress_callback)
        tips = None
        return success, password, decrypted_path, tips


bot = AadhaarBot()
# ============== DNS-over-HTTPS MongoDB SRV Fix ==============
def _resolve_mongo_srv_via_doh(srv_uri):
    import re as _re
    m = _re.match(
        r'^mongodb\+srv://([^:@]+):([^@]+)@([^/?]+)(.*)?$', srv_uri
    )
    if not m:
        return srv_uri

    user, pwd, host, rest = m.group(1), m.group(2), m.group(3), m.group(4) or ''
    srv_query = f'_mongodb._tcp.{host}'

    try:
        doh_url = f'https://dns.google/resolve?name={srv_query}&type=SRV'
        resp = requests.get(doh_url, timeout=10)
        data = resp.json()
        answers = data.get('Answer', [])
        if not answers:
            logger.warning("DoH returned no SRV records - falling back to original URI")
            return srv_uri

        hosts = []
        for ans in answers:
            parts = ans.get('data', '').split()
            if len(parts) == 4:
                port = parts[2]
                target = parts[3].rstrip('.')
                hosts.append(f'{target}:{port}')

        if not hosts:
            return srv_uri

        txt_url = f'https://dns.google/resolve?name={host}&type=TXT'
        txt_resp = requests.get(txt_url, timeout=10)
        txt_data = txt_resp.json()
        auth_source = 'admin'
        replicaset = None
        for txt_ans in txt_data.get('Answer', []):
            txt_val = txt_ans.get('data', '').strip('"')
            for part in txt_val.split('&'):
                if part.startswith('authSource='):
                    auth_source = part.split('=', 1)[1]
                elif part.startswith('replicaSet='):
                    replicaset = part.split('=', 1)[1]

        hosts_str = ','.join(hosts)
        qs_parts = [f'authSource={auth_source}', 'tls=true']
        if replicaset:
            qs_parts.append(f'replicaSet={replicaset}')
        extra_qs = ''
        if '?' in rest:
            extra_qs = rest.split('?', 1)[1].rstrip('/')
            if extra_qs:
                qs_parts.append(extra_qs)
        std_uri = f'mongodb://{user}:{pwd}@{hosts_str}/?{"&".join(qs_parts)}'
        logger.info(f"DoH SRV resolved - {len(hosts)} host(s), authSource={auth_source}")
        return std_uri

    except Exception as e:
        logger.warning(f"DoH SRV resolution failed ({e}) - falling back to original URI")
        return srv_uri


# ============== MONGO DB SETUP ==============
MONGO_URI = _resolve_mongo_srv_via_doh(MONGO_URI)
mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000, connectTimeoutMS=15000, tls=True, tlsCAFile=certifi.where())
db = mongo_client["aadhar_bot"]
users_col = db["users"]
keys_collection = db["redeem_keys"]
settings_col = db["settings"]
logs_col = db["activity_logs"]

setting = settings_col.find_one({"_id": "config"})
if not setting:
    settings_col.insert_one({"_id": "config", "maintenance_mode_b1": False})
    MAINTENANCE_MODE = False
else:
    MAINTENANCE_MODE = setting.get("maintenance_mode_b1", False)

PENDING_ADMIN_PDFS = {}


def get_next_pdf_log_count():
    try:
        res = settings_col.find_one_and_update(
            {"_id": "pdf_log_counter"},
            {"$inc": {"count": 1}},
            upsert=True,
            return_document=ReturnDocument.BEFORE
        )
        if res is None:
            return 0
        return res.get("count", 0)
    except Exception as e:
        logger.error(f"Error incrementing PDF log counter: {e}")
        return 0


# ============== IN-MEMORY USER CACHE ==============
USER_CACHE = {}
cache_lock = threading.Lock()
log_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="log_worker")


def get_cached_user(user_id_str):
    with cache_lock:
        if user_id_str in USER_CACHE:
            doc, ts = USER_CACHE[user_id_str]
            if time.time() - ts < CACHE_TTL:
                return doc
    return None


def set_cached_user(user_id_str, user_doc):
    with cache_lock:
        if user_doc:
            USER_CACHE[str(user_id_str)] = (user_doc, time.time())


def invalidate_cached_user(user_id_str):
    with cache_lock:
        USER_CACHE.pop(str(user_id_str), None)


def log_activity(chat_id, action, status, duration=0.0, error=None):
    def _async_log():
        try:
            log_doc = {
                "timestamp": datetime.now(),
                "chat_id": str(chat_id),
                "action": action,
                "status": status,
                "duration": float(duration),
                "error": error
            }
            logs_col.insert_one(log_doc)
        except Exception as e:
            logger.error(f"Error writing activity log: {e}")
    log_executor.submit(_async_log)


def get_user_log_tag(user_id):
    try:
        uid = str(user_id)
        u = get_user(uid)
        if u:
            username = u.get('username')
            first_name = u.get('first_name')

            clean_f = re.sub(r'[^\x00-\x7F]+', '', first_name).strip() if first_name else ''
            clean_u = re.sub(r'[^\x00-\x7F]+', '', username).strip() if username else ''

            parts = []
            if clean_f and clean_f.lower() != "unknown":
                parts.append(clean_f)
            if clean_u:
                parts.append(f"@{clean_u}")
            elif username:
                parts.append(f"@{username}")

            if parts:
                return f"[{uid} {' '.join(parts)}]"
            return f"[{uid}]"
    except Exception:
        pass
    return f"[{user_id}]"


def ensure_user(user_id, referrer_id=None, first_name=None, username=None):
    uid = str(user_id)
    user = users_col.find_one({"_id": uid})
    if user is None:
        new_user = {
            "_id": uid,
            "first_name": first_name or "Unknown",
            "username": username,
            "credits": 1,
            "lifetime": False,
            "referred_by": str(referrer_id) if referrer_id else None,
            "referral_count": 0,
            "searches": 0,
            "joined": datetime.now().isoformat()
        }
        users_col.insert_one(new_user)
        if referrer_id:
            rid = str(referrer_id)
            if rid != uid:
                users_col.update_one(
                    {"_id": rid},
                    {"$inc": {"credits": 1, "referral_count": 1}}
                )
                invalidate_cached_user(rid)
        try:
            uname_str = f"@{username}" if username else "N/A"
            msg = (
                f"\U0001f7e2 <b>NEW USER ALERT</b>\n"
                f"------------------------------\n"
                f"\U0001f464 <b>Name:</b> {first_name or 'Unknown'}\n"
                f"\U0001f468\U0001f3fb <b>User:</b> {uname_str}\n"
                f"\U0001f194 <b>ID:</b> <code>{uid}</code>"
            )
            if referrer_id:
                referrer = users_col.find_one({"_id": str(referrer_id)})
                ref_uname = f"@{referrer.get('username')}" if referrer and referrer.get('username') else "Unknown"
                msg += (
                    f"\nReferred By: {ref_uname} (<code>{referrer_id}</code>)\n"
                    f"------------------------------"
                )
            send_log(msg)
        except Exception:
            pass
        return True
    else:
        current_first = user.get('first_name')
        current_user = user.get('username')

        upd = {}
        if first_name and first_name != current_first:
            upd['first_name'] = first_name

        if username != current_user:
            upd['username'] = username

        if upd:
            users_col.update_one({"_id": uid}, {"$set": upd})
    return False


def get_user(user_id):
    uid = str(user_id)
    cached = get_cached_user(uid)
    if cached:
        return cached
    doc = users_col.find_one({"_id": uid})
    if doc:
        set_cached_user(uid, doc)
    return doc


def check_expiry(user):
    if user and user.get('expiry'):
        try:
            if datetime.fromisoformat(user['expiry']) > datetime.now():
                return True
        except Exception:
            pass
    return False


def check_and_notify_expiry(chat_id):
    u = get_user(chat_id)
    if not u:
        return

    expiry_str = u.get('expiry')
    if expiry_str and not u.get('lifetime'):
        try:
            expiry_dt = datetime.fromisoformat(expiry_str)
            now = datetime.now()

            if now < expiry_dt <= (now + timedelta(hours=1)) and not u.get('expiry_warning_notified'):
                users_col.update_one({"_id": str(chat_id)}, {"$set": {"expiry_warning_notified": True}})
                invalidate_cached_user(chat_id)
                warning_text = (
                    f"Unlimited Plan Expiring Soon!\n\n"
                    f"Your Unlimited plan will expire in 1 hour. Tap /buy to extend your access!"
                )
                try:
                    send_message(chat_id, warning_text)
                except Exception as e:
                    logger.error(f"Failed to send 1-hr warning message to {chat_id}: {e}")

                username = u.get('username')
                uname_disp = f"@{username}" if username else "(No Username)"
                plan_days = u.get('unlimited_days')
                plan_str = f"{plan_days} Day Unlimited" if plan_days == 1 else (f"{plan_days} Days Unlimited" if plan_days else format_plan_display(u))

                log_text = (
                    f"1-HOUR REMINDER SENT\n"
                    f"User ID: <code>{chat_id}</code>\n"
                    f"Username: {uname_disp}\n"
                    f"Plan: {plan_str}"
                )
                send_log(log_text)

            if expiry_dt <= now and not u.get('expiry_notified'):
                balance = int(u.get('credits', 0))
                upd_set = {"expiry_notified": True, "expiry_warning_notified": True}
                if balance <= 0:
                    upd_set["is_premium"] = False

                users_col.update_one({"_id": str(chat_id)}, {"$set": upd_set})
                invalidate_cached_user(chat_id)

                msg_text = (
                    f"Plan Expired\n\n"
                    f"Your Unlimited plan has ended.\n"
                    f"Restored Balance: <code>{balance}</code> Searches\n\n"
                    f"Tap /buy to top-up or upgrade again!"
                )
                try:
                    send_message(chat_id, msg_text)
                except Exception as e:
                    logger.error(f"Failed to send plan expired message to {chat_id}: {e}")

                username = u.get('username')
                uname_disp = f"@{username}" if username else "(No Username)"
                plan_days = u.get('unlimited_days')
                status_str = f"{plan_days} Day Unlimited" if plan_days == 1 else (f"{plan_days} Days Unlimited" if plan_days else "Unlimited")

                log_text = (
                    f"UNLIMITED PLAN EXPIRED\n"
                    f"User ID: <code>{chat_id}</code>\n"
                    f"Username: {uname_disp}\n"
                    f"Plan: {status_str}\n"
                    f"Restored Balance: <code>{balance}</code> Searches"
                )
                send_log(log_text)
        except Exception as e:
            logger.error(f"Error checking/notifying expiry for {chat_id}: {e}")


def expiry_checker_scheduler():
    while True:
        try:
            active_users = users_col.find({
                "expiry": {"$exists": True, "$ne": None},
                "lifetime": {"$ne": True}
            })
            for user_doc in active_users:
                chat_id = user_doc.get('_id')
                if chat_id:
                    check_and_notify_expiry(chat_id)
        except Exception as e:
            logger.error(f"Error in expiry_checker_scheduler: {e}")
        time.sleep(30)


def get_credits(user_id):
    u = get_user(user_id)
    if u is None:
        return 0
    if u.get('lifetime') or check_expiry(u):
        return float('inf')
    return u.get('credits', 0)


def is_lifetime(user_id):
    u = get_user(user_id)
    return (u.get('lifetime', False) or check_expiry(u)) if u else False


def has_credits(user_id):
    return get_credits(user_id) > 0


def add_credits(user_id, amount, make_lifetime=False):
    uid = str(user_id)
    user = get_user(user_id)
    if user is None:
        new_user = {
            "_id": uid,
            "credits": 0,
            "lifetime": False,
            "referred_by": None,
            "referral_count": 0,
            "joined": datetime.now().isoformat()
        }
        users_col.insert_one(new_user)

    if make_lifetime:
        users_col.update_one({"_id": uid}, {"$set": {"lifetime": True, "is_premium": True}})
    else:
        users_col.update_one({"_id": uid}, {"$inc": {"credits": amount, "initial_credits": max(0, amount)}, "$set": {"is_premium": True}})
    invalidate_cached_user(uid)


def deduct_credit(user_id):
    uid = str(user_id)
    user = get_user(user_id)
    if user:
        upd = {"$inc": {"searches": 1}}
        if not user.get('lifetime'):
            new_credits = max(0, user.get('credits', 0) - 1)
            upd["$set"] = {"credits": new_credits}
        users_col.update_one({"_id": uid}, upd)
        invalidate_cached_user(uid)


def all_users():
    docs = users_col.find({})
    return {doc["_id"]: doc for doc in docs}


def format_plan_display(u, days_left=None):
    if u.get('lifetime'):
        return "Lifetime Unlimited"

    unlim_days = u.get('unlimited_days')
    if unlim_days:
        try:
            d = int(unlim_days)
            if d == 1:
                return "1 Day Unlimited"
            if 6 <= d <= 8:
                return "1 Week Unlimited"
            if 13 <= d <= 15:
                return "2 Weeks Unlimited"
            if 27 <= d <= 31:
                return "1 Month Unlimited"
            if 56 <= d <= 62 or d == 60:
                return "2 Months Unlimited"
            if 85 <= d <= 93 or d == 90:
                return "3 Months Unlimited"
            if 170 <= d <= 185 or d == 180:
                return "6 Months Unlimited"
            if 350 <= d <= 370 or d == 365:
                return "12 Months Unlimited"
            if d % 30 == 0:
                m = d // 30
                return f"{m} Month{'s' if m > 1 else ''} Unlimited"
            if d % 7 == 0:
                w = d // 7
                return f"{w} Week{'s' if w > 1 else ''} Unlimited"
            return f"{d} Days Unlimited"
        except Exception:
            pass

    if days_left is not None and days_left >= 0:
        d = days_left
        if d <= 1:
            return "1 Day Unlimited"
        if 5 <= d <= 8:
            return "1 Week Unlimited"
        if 12 <= d <= 16:
            return "2 Weeks Unlimited"
        if 20 <= d <= 32:
            return "1 Month Unlimited"
        if 50 <= d <= 65:
            return "2 Months Unlimited"
        if 80 <= d <= 95:
            return "3 Months Unlimited"
        if 160 <= d <= 190:
            return "6 Months Unlimited"
        if 340 <= d <= 370:
            return "12 Months Unlimited"
        if d % 30 == 0:
            m = d // 30
            return f"{m} Month{'s' if m > 1 else ''} Unlimited"
        if d % 7 == 0:
            w = d // 7
            return f"{w} Week{'s' if w > 1 else ''} Unlimited"
        return f"{d} Days Unlimited"

    exp_str = u.get('expiry')
    if exp_str and not u.get('lifetime'):
        try:
            if datetime.fromisoformat(exp_str) <= datetime.now():
                cr = u.get('credits', 0)
                if cr > 0:
                    return f"{int(cr)} Credits (Expired Plan)"
                return "Expired Plan"
        except Exception:
            pass

    cr = u.get('credits', 0)
    if cr > 0:
        total_cr = int(u.get('initial_credits') or u.get('total_credits') or cr)
        return f"{total_cr} Credits"
    return "0 Credits"


def show_user_profile_admin(chat_id, target_uid, message_id=None):
    user_doc = get_user(target_uid)
    if not user_doc:
        send_message(chat_id, f"User {target_uid} not found.")
        return

    uid = str(user_doc.get('_id', target_uid))
    first_name = user_doc.get('first_name', 'Unknown')
    username = user_doc.get('username')
    username_display = f"@{username}" if username else "N/A"
    searches = user_doc.get('searches', 0)

    now = datetime.now()
    expiry_str = user_doc.get('expiry')
    expiry_dt = None
    days_left = None
    if expiry_str and not user_doc.get('lifetime'):
        try:
            expiry_dt = datetime.fromisoformat(expiry_str)
            if expiry_dt > now:
                days_left = max(1, int(((expiry_dt - now).total_seconds() + 86399) // 86400))
        except Exception:
            pass

    plan_name = format_plan_display(user_doc, days_left)

    if user_doc.get('banned'):
        subscription_display = "Banned"
    elif user_doc.get('lifetime'):
        subscription_display = "Lifetime Unlimited\n<b>Expiry:</b> Forever (No Expiry)"
    elif expiry_dt and expiry_dt > now:
        formatted_exp = expiry_dt.strftime("%d-%b-%Y at %I:%M %p")
        subscription_display = f"<b>{plan_name}</b>\n<b>Expiry:</b> {formatted_exp} ({days_left}d left)"
    else:
        cr = user_doc.get('credits', 0)
        subscription_display = f"{int(cr)} Searches"

    text = (
        f"PROFILE OVERVIEW\n\n"
        f"<b>Name:</b> {first_name}\n"
        f"<b>Username:</b> {username_display}\n"
        f"<b>User ID:</b> <code>{uid}</code>\n"
        f"<b>Total Searches:</b> {searches}\n"
        f"<b>Credits Left:</b> {subscription_display}\n"
        f"<b>Referrals:</b> {user_doc.get('referral_count', 0)}"
    )

    kb = {
        'inline_keyboard': [
            [{'text': 'Edit User', 'callback_data': f'edit_user_{uid}'}],
            [{'text': 'Back to Panel', 'callback_data': 'panel_back'}]
        ]
    }

    if message_id:
        edit_message(chat_id, message_id, text, reply_markup=kb)
    else:
        send_message(chat_id, text, reply_markup=kb)


def get_admin_panel_data():
    total_users = users_col.count_documents({})
    now_iso = datetime.now().isoformat()
    lifetime_users = users_col.count_documents({"lifetime": True})
    timed_users = users_col.count_documents({"lifetime": {"$ne": True}, "expiry": {"$gt": now_iso}})
    total_unlimited = lifetime_users + timed_users
    mm_status = "ON" if MAINTENANCE_MODE else "OFF"
    text = (
        f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
        f"<b>[ admin panel ]</b>\n\n"
        f"Total Users   - {total_users}\n"
        f"Unlimited     - {total_unlimited} (Lifetime: {lifetime_users} | Timed: {timed_users})\n"
        f"Maintenance   - {mm_status}\n\n"
        f"<i>Manage bot settings below</i>"
    )
    kb = {
        'inline_keyboard': [
            [
                {'text': 'Active Users', 'callback_data': 'panel_users_0'},
                {'text': 'Search User', 'callback_data': 'panel_search_user'}
            ],
            [
                {'text': 'Generate Key', 'callback_data': 'panel_gen_key'},
                {'text': 'Revoke User', 'callback_data': 'panel_revoke'}
            ],
            [
                {'text': 'Broadcast', 'callback_data': 'panel_broadcast'},
                {'text': f'Maintenance: {mm_status}', 'callback_data': 'panel_toggle_mm'}
            ]
        ]
    }
    return text, kb


def show_users_page(chat_id, page=0, message_id=None):
    now = datetime.now()
    now_iso = now.isoformat()

    lifetime_count = users_col.count_documents({"lifetime": True})
    timed_count = users_col.count_documents({"lifetime": {"$ne": True}, "expiry": {"$gt": now_iso}})
    credit_count = users_col.count_documents({"lifetime": {"$ne": True}, "$or": [{"expiry": {"$exists": False}}, {"expiry": {"$lte": now_iso}}], "is_premium": True, "credits": {"$gt": 0}})
    total_active = lifetime_count + timed_count + credit_count

    all_docs = list(users_col.find({}).sort("joined", -1))

    def _user_sort_key(u):
        if u.get('lifetime'):
            return (0, -float('inf'))
        exp = u.get('expiry')
        if exp and not u.get('lifetime'):
            try:
                exp_dt = datetime.fromisoformat(exp)
                if exp_dt > now:
                    return (0, -exp_dt.timestamp())
            except Exception:
                pass
        credits = u.get('credits', 0)
        if credits > 0:
            return (1, -credits)
        return (2, 0)

    all_docs.sort(key=_user_sort_key)

    total = len(all_docs)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    chunk = all_docs[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]

    lines = [
        f"Active Premium Users: {total_active}\n{DIVIDER}\n"
        f"Lifetime: {lifetime_count} | Timed: {timed_count} | Credits: {credit_count}\n{DIVIDER}\n"
    ]

    for i, u in enumerate(chunk, start=page * PAGE_SIZE + 1):
        uid = u['_id']
        name = u.get('first_name', 'Unknown')
        uname = u.get('username')
        uname_str = f" (@{uname})" if uname else " (No Username)"

        expiry_str = u.get('expiry')
        expiry_dt = None
        days_left = None
        time_left_str = ""
        is_active_unlimited = False
        if expiry_str and not u.get('lifetime'):
            try:
                expiry_dt = datetime.fromisoformat(expiry_str)
                if expiry_dt > now:
                    is_active_unlimited = True
                    sec_left = (expiry_dt - now).total_seconds()
                    days_left = int(sec_left // 86400)
                    if days_left >= 1:
                        time_left_str = f"{days_left}d left"
                    else:
                        hours_left = int(sec_left // 3600)
                        if hours_left >= 1:
                            time_left_str = f"{hours_left}h left"
                        else:
                            mins_left = max(1, int(sec_left // 60))
                            time_left_str = f"{mins_left}m left"
            except Exception:
                pass

        plan_str = format_plan_display(u, days_left if is_active_unlimited else None)

        if u.get('lifetime'):
            icon = "[L]"
        elif is_active_unlimited:
            sec_left = (expiry_dt - now).total_seconds()
            icon = "[!]" if sec_left < 86400 else "[U]"
        elif u.get('credits', 0) > 0:
            icon = "[C]"
        else:
            icon = "[X]"

        lines.append(f"{icon} {i}. <b>{name}</b>{uname_str}")
        lines.append(f"    ID: <code>{uid}</code>")
        lines.append(f"    Plan: <b>{plan_str}</b>")
        if u.get('lifetime'):
            lines.append(f"    Lifetime\n")
        elif is_active_unlimited:
            formatted_exp = expiry_dt.strftime("%d-%b-%Y at %I:%M %p")
            lines.append(f"    {formatted_exp} ({time_left_str})\n")
        elif u.get('credits', 0) > 0:
            cr_left = int(u.get('credits', 0))
            lines.append(f"    {cr_left} Credits left\n")
        else:
            lines.append(f"    Expired\n")

    lines.append(f"Page {page + 1} of {total_pages}")

    nav = []
    if page > 0:
        nav.append({'text': 'Prev', 'callback_data': f'panel_users_{page - 1}'})
    if page < total_pages - 1:
        nav.append({'text': 'Next', 'callback_data': f'panel_users_{page + 1}'})

    kb = {
        'inline_keyboard': [
            nav,
            [{'text': 'Back to Panel', 'callback_data': 'panel_back'}]
        ]
    }

    edit_message(chat_id, message_id, "\n".join(lines), reply_markup=kb)


# ============== SESSION MANAGEMENT ==============
user_sessions = {}
_sessions_lock = threading.Lock()


def get_session(chat_id):
    with _sessions_lock:
        return user_sessions.get(chat_id, {'step': 'main', 'data': {}, 'last_activity': time.time()})


def set_session(chat_id, step, data=None):
    with _sessions_lock:
        existing = user_sessions.get(chat_id, {})
        d = data if data is not None else existing.get('data', {})
        user_sessions[chat_id] = {'step': step, 'data': d, 'last_activity': time.time()}


def update_session_data(chat_id, key, value):
    with _sessions_lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = {'step': 'main', 'data': {}, 'last_activity': time.time()}
        user_sessions[chat_id]['data'][key] = value
        user_sessions[chat_id]['last_activity'] = time.time()


def clear_session(chat_id):
    with _sessions_lock:
        user_sessions[chat_id] = {'step': 'main', 'data': {}, 'last_activity': time.time()}


def touch_session(chat_id):
    with _sessions_lock:
        if chat_id in user_sessions:
            user_sessions[chat_id]['last_activity'] = time.time()


def _cleanup_sessions():
    while True:
        time.sleep(20)
        try:
            with _sessions_lock:
                for cid, s in list(user_sessions.items()):
                    if s.get('step', 'main') != 'main':
                        idle = time.time() - s.get('last_activity', time.time())
                        if idle > SESSION_TIMEOUT:
                            user_sessions[cid] = {'step': 'main', 'data': {}, 'last_activity': time.time()}
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")


# ============== CHANNEL MEMBERSHIP ==============
def is_channel_member(user_id):
    try:
        r = get_telegram_session().get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatMember",
            params={'chat_id': CHANNEL_USERNAME, 'user_id': user_id},
            timeout=6
        ).json()
        if r.get('ok'):
            status = r['result']['status']
            return status in ('member', 'administrator', 'creator')
    except Exception as e:
        logger.error(f"Channel check error: {e}")
    return False


_bot_username = None


def get_bot_username():
    global _bot_username
    if _bot_username:
        return _bot_username
    try:
        r = get_telegram_session().get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe", timeout=5
        ).json()
        if r.get('ok'):
            _bot_username = r['result']['username']
    except Exception:
        pass
    return _bot_username or "ModxAadharbot"


# ============== TELEGRAM HELPERS ==============
def send_message(chat_id, text, reply_markup=None, disable_web_page_preview=True):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': disable_web_page_preview}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    try:
        response = get_telegram_session().post(url, json=data, timeout=10)
        result = response.json()
        if not result.get('ok'):
            logger.error(f"Telegram send error: {result}")
        return result
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None


def send_photo(chat_id, photo, caption="", reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {'chat_id': chat_id, 'parse_mode': 'HTML'}
    if caption:
        data['caption'] = caption
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup) if isinstance(reply_markup, dict) else reply_markup
    try:
        if isinstance(photo, bytes):
            files = {'photo': ('captcha.png', photo, 'image/png')}
            response = get_telegram_session().post(url, data=data, files=files, timeout=20)
        else:
            data['photo'] = photo
            response = get_telegram_session().post(url, data=data, timeout=20)
        return response.json()
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        return None


def edit_message(chat_id, message_id, text, reply_markup=None, disable_web_page_preview=True):
    if not message_id:
        return send_message(chat_id, text, reply_markup, disable_web_page_preview)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    data = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': disable_web_page_preview}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    try:
        response = get_telegram_session().post(url, json=data, timeout=10)
        result = response.json()
        if not result.get('ok'):
            if "message is not modified" in result.get('description', '').lower():
                return result
            return send_message(chat_id, text, reply_markup, disable_web_page_preview)
        return result
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        return None


def make_progress_bar(percent, total_blocks=10):
    filled = int(round(total_blocks * (percent / 100)))
    filled = max(0, min(total_blocks, filled))
    bar = '#' * filled + '-' * (total_blocks - filled)
    return f"[{bar}] {percent}%"


def delete_message(chat_id, message_id):
    if not message_id:
        return None
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteMessage"
    data = {'chat_id': chat_id, 'message_id': message_id}
    try:
        response = get_telegram_session().post(url, json=data, timeout=5)
        return response.json()
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        return None


def animate_progress_thread(chat_id, status_msg_id, stop_event, finish_event=None, done_event=None):
    percent = 5
    while not stop_event.is_set():
        if finish_event and finish_event.is_set():
            while percent < 100:
                percent += random.randint(8, 15)
                percent = min(100, percent)
                edit_message(
                    chat_id, status_msg_id,
                    f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                    f"<b>Processing</b>\n\n"
                    f"<b>{make_progress_bar(percent)}</b>\n"
                    f"<i>Preparing file for delivery...</i>"
                )
                time.sleep(0.15)
            if done_event:
                done_event.set()
            return

        if percent >= 90:
            status_title = "Processing"
            slow_messages = [
                "Official server is busy, hold on tight...",
                "High network traffic, fetching response...",
                "Govt portal taking longer than usual...",
                "Still processing, almost done..."
            ]
            detail_text = slow_messages[int(time.time() // 4) % len(slow_messages)]
            sleep_time = 3.0
            increment = 1 if random.random() < 0.4 else 0
        elif percent < 25:
            status_title = "Processing"
            detail_text = "Connecting to Govt server..."
            sleep_time = 1.2
            increment = random.randint(5, 10)
        elif percent < 50:
            status_title = "Processing"
            detail_text = "Retrieving encrypted Aadhaar PDF..."
            sleep_time = 1.5
            increment = random.randint(3, 7)
        elif percent < 70:
            status_title = "Processing"
            detail_text = "Decrypting Aadhaar document..."
            sleep_time = 2.0
            increment = random.randint(2, 5)
        else:
            status_title = "Processing"
            detail_text = "Verifying security credentials..."
            sleep_time = 2.5
            increment = random.randint(1, 3)

        steps_count = int(sleep_time * 10)
        for _ in range(steps_count):
            if stop_event.is_set():
                return
            if finish_event and finish_event.is_set():
                break
            time.sleep(0.1)

        if stop_event.is_set():
            return

        if finish_event and finish_event.is_set():
            continue

        percent += increment
        percent = min(98, percent)

        edit_message(
            chat_id, status_msg_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>{status_title}</b>\n\n"
            f"<b>{make_progress_bar(percent)}</b>\n"
            f"<i>{detail_text}</i>"
        )


def send_log(text, reply_markup=None):
    try:
        send_message(LOG_CHANNEL_ID, text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Log channel error: {e}")


def answer_callback_query(callback_query_id, text=None, show_alert=False):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    data = {'callback_query_id': callback_query_id}
    if text:
        data['text'] = text
    if show_alert:
        data['show_alert'] = True
    try:
        get_telegram_session().post(url, json=data, timeout=5)
    except Exception as e:
        logger.error(f"Error answering callback: {e}")


def edit_message_reply_markup(chat_id, message_id, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageReplyMarkup"
    data = {'chat_id': chat_id, 'message_id': message_id}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup) if isinstance(reply_markup, dict) else reply_markup
    try:
        response = get_telegram_session().post(url, json=data, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error editing message reply markup: {e}")
        return None


def copy_message(chat_id, from_chat_id, message_id, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/copyMessage"
    data = {
        'chat_id': chat_id,
        'from_chat_id': from_chat_id,
        'message_id': message_id
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup) if isinstance(reply_markup, dict) else reply_markup
    try:
        response = get_telegram_session().post(url, json=data, timeout=15)
        return response.json()
    except Exception as e:
        logger.error(f"Error copying message: {e}")
        return None


def send_document(chat_id, file_path, caption=None, filename="Aadhaar.pdf", auto_delete=True):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            files = {'document': (filename, f, 'application/pdf')}
            data = {'chat_id': chat_id, 'parse_mode': 'HTML'}
            if caption:
                data['caption'] = caption
            response = get_telegram_session().post(url, data=data, files=files, timeout=30).json()
        if auto_delete:
            try:
                os.remove(file_path)
            except Exception:
                pass
        return response
    except Exception as e:
        logger.error(f"Error sending document: {e}")
        return None


# ============== KEYBOARDS ==============
def get_main_keyboard():
    return {
        'keyboard': [
            ['Mobile Number', 'Aadhaar Number'],
            ['EID', 'Aadhaar SMS'],
            ['Credits', 'Buy Credits', 'Referral'],
            ['About Bot']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': False
    }


def get_cancel_keyboard():
    return {'inline_keyboard': [[{'text': 'Cancel', 'callback_data': 'cancel'}]]}


def get_retry_keyboard(callback_data):
    return {
        'inline_keyboard': [
            [{'text': 'Re-try', 'callback_data': callback_data}],
            [{'text': 'Cancel', 'callback_data': 'cancel'}]
        ]
    }


def get_join_keyboard():
    return {
        'inline_keyboard': [
            [{'text': 'Join Channel', 'url': CHANNEL_LINK}],
            [{'text': 'Check Joined', 'callback_data': 'check_join'}]
        ]
    }


def track_buy_interest(chat_id, plan_info=None):
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        user_doc = users_col.find_one({"_id": str(chat_id)})
        if not user_doc:
            return

        click_date = user_doc.get("buy_click_date")
        clicks = user_doc.get("buy_clicks_count", 0)
        last_logged_date = user_doc.get("last_buy_log_date")

        if click_date != today_str:
            clicks = 1
            click_date = today_str
        else:
            clicks += 1

        users_col.update_one(
            {"_id": str(chat_id)},
            {"$set": {"buy_click_date": click_date, "buy_clicks_count": clicks}}
        )

        should_trigger = (clicks >= 2) and (last_logged_date != today_str)

        if should_trigger:
            users_col.update_one(
                {"_id": str(chat_id)},
                {"$set": {"last_buy_log_date": today_str}}
            )
            name = user_doc.get("first_name", "Unknown")
            username = user_doc.get("username")
            uname_str = f" (@{username})" if username else ""
            plan_str = f"<b>{plan_info['name']}</b> ({plan_info['price']})" if plan_info else "Browsing Payment Plans"

            offer_kb = {
                'inline_keyboard': [
                    [{'text': 'Send Offer to User', 'callback_data': f'send_offer_plans_{chat_id}'}]
                ]
            }

            send_log(
                f"PURCHASE INTEREST ALERT\n"
                f"------------------------------\n"
                f"User   - <b>{name}</b>{uname_str}\n"
                f"ID     - <code>{chat_id}</code>\n"
                f"Plan   - {plan_str}\n"
                f"Clicks - <b>{clicks} buy actions today</b>\n\n"
                f"<i>User is actively checking out payment plans. Contact them to offer help!</i>",
                reply_markup=offer_kb
            )
    except Exception as e:
        logger.debug(f"track_buy_interest error: {e}")


def show_buy_menu(chat_id, message_id=None):
    track_buy_interest(chat_id)
    kb = {
        'inline_keyboard': [
            [{'text': 'Limited Search Plans', 'callback_data': 'buy_menu_limited'}],
            [{'text': 'Unlimited Plans', 'callback_data': 'buy_menu_unlimited'}],
            [{'text': 'Back to Profile', 'callback_data': 'credits'}]
        ]
    }
    edit_message(
        chat_id, message_id,
        f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
        f"Choose your plan type:\n\n"
        f"<i>Need help? Contact admin:</i> {OWNER_USERNAME}",
        reply_markup=kb
    )


def show_referral_info(chat_id):
    username = get_bot_username()
    link = f"https://t.me/{username}?start=ref_{chat_id}"
    u = get_user(chat_id)
    ref_count = u.get('referral_count', 0) if u else 0
    earned = ref_count
    send_message(
        chat_id,
        f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
        f"<b>Referral</b>\n\n"
        f"<code>{link}</code>\n\n"
        f"Friends joined  -  {ref_count}\n"
        f"Credits earned  -  {earned}\n\n"
        f"{DIVIDER}\n"
        f"<i>Share your link - earn +1 credit per friend who joins</i>"
    )


def show_credits_info(chat_id, message_id=None):
    u = get_user(chat_id)
    cr = get_credits(chat_id)

    if u and u.get('lifetime'):
        subscription_display = "Lifetime Unlimited\n<b>Validity:</b> Forever (No Expiry)"
    elif u and check_expiry(u):
        try:
            expiry_dt = datetime.fromisoformat(u['expiry'])
            delta = expiry_dt - datetime.now()
            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds // 60) % 60

            time_parts = []
            if days > 0:
                time_parts.append(f"{days}d")
            if hours > 0:
                time_parts.append(f"{hours}h")
            if minutes > 0 or not time_parts:
                time_parts.append(f"{minutes}m")
            time_left_str = " ".join(time_parts)

            plan_name = format_plan_display(u, days)
            subscription_display = f"<b>{plan_name}</b>\n<b>Time Left:</b> {time_left_str} (Expires {expiry_dt.strftime('%d-%b-%Y')})"
        except Exception:
            subscription_display = "Unlimited Plan"
    else:
        subscription_display = f"{int(cr)} Searches"

    first_name = u.get('first_name', 'User') if u else 'User'
    username = u.get('username') if u else None
    username_display = f"@{username}" if username else "N/A"
    searches = u.get('searches', 0) if u else 0

    bot_username = get_bot_username()
    link = f"https://t.me/{bot_username}?start=ref_{chat_id}"

    text = (
        f"PROFILE OVERVIEW\n\n"
        f"<b>Name:</b> {first_name}\n"
        f"<b>Username:</b> {username_display}\n"
        f"<b>User ID:</b> <code>{chat_id}</code>\n"
        f"<b>Total Searches:</b> <b>{searches}</b>\n"
        f"<b>Credits Left:</b> {subscription_display}\n\n"
        f"<b>Referral Link:</b> <code>{link}</code>"
    )

    owner_clean = OWNER_USERNAME.replace("@", "")
    kb = {
        'inline_keyboard': [
            [
                {'text': 'Buy Credits', 'callback_data': 'buy'},
                {'text': 'Support', 'url': f'https://t.me/{owner_clean}'}
            ]
        ]
    }

    if message_id:
        edit_message(chat_id, message_id, text, reply_markup=kb)
    else:
        send_message(chat_id, text, reply_markup=kb)


def show_about_bot(chat_id, message_id=None):
    text = (
        f"<b>{BOT_NAME} - ABOUT & USER GUIDE</b>\n"
        f"{DIVIDER}\n\n"
        f"<blockquote><b>Welcome to {BOT_NAME}!</b>\n"
        f"Your all-in-one secure platform for instant identity searches and official Govt document retrievals.</blockquote>\n\n"
        f"<b>FEATURES & SEARCH MODES</b>\n"
        f"Mobile Search - Find owner name, address & Aadhaar linked to 10-digit mobile.\n"
        f"Aadhaar Search - Fetch profile details & download official PDF via 12-digit Aadhaar.\n"
        f"EID Search - Retrieve status & PDF via Enrollment ID (Format: 1234/56789/12345).\n\n"
        f"<b>HOW TO USE (STEP-BY-STEP)</b>\n"
        f"<blockquote>1. Select a search option from bottom menu.\n"
        f"2. Enter Mobile Number / Aadhaar / EID.\n"
        f"3. Enter 6-digit OTP for PDF downloads.\n"
        f"4. Receive your result or PDF instantly!</blockquote>\n\n"
        f"<b>CREDITS & REFERRALS</b>\n"
        f"- Credits - Check active plan & search balance.\n"
        f"- Referral - Share your link & earn free searches.\n"
        f"- Buy Plan - Purchase top-up credits or Unlimited plans.\n\n"
        f"<b>SUPPORT & ADMIN</b>\n"
        f"<blockquote>Admin: {OWNER_USERNAME}\n"
        f"Channel: {CHANNEL_LINK}\n"
        f"Contact {OWNER_USERNAME} for custom plans & key redemptions.</blockquote>\n"
        f"{DIVIDER}"
    )
    kb = {
        'inline_keyboard': [
            [
                {'text': 'Contact Admin', 'url': f'https://t.me/{OWNER_USERNAME.replace("@", "")}'},
                {'text': 'Official Channel', 'url': CHANNEL_LINK}
            ]
        ]
    }
    if message_id:
        edit_message(chat_id, message_id, text, reply_markup=kb)
    else:
        send_message(chat_id, text, reply_markup=kb)


# ============== GATES ==============
def channel_gate(chat_id):
    if is_channel_member(chat_id):
        return True
    send_message(
        chat_id,
        f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
        f"<b>Channel Required</b>\n\n"
        f"Join <b>{CHANNEL_USERNAME}</b> to use this bot.\n\n"
        f"{DIVIDER}\n"
        f"<i>Tap Join below, then confirm with the button.</i>",
        reply_markup=get_join_keyboard()
    )
    return False


def credit_gate(chat_id):
    if has_credits(chat_id):
        return True
    send_message(
        chat_id,
        f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
        f"<b>No Credits</b>\n\n"
        f"Balance  -  <b>0</b>\n\n"
        f"Tap /buy to purchase a plan.\n"
        f"Tap /referral to earn credits free.\n\n"
        f"{DIVIDER}"
    )
    return False


# ============== PDF EXTRACTION ==============
def extract_all_aadhaar_details(pdf_path):
    details = {
        'name': 'Not found',
        'gender': 'Not found',
        'dob': 'Not found',
        'aadhaar': 'Not found',
        'address': 'Not found'
    }

    d = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]
    p = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 1, 4, 6, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]

    def validate_verhoeff(num_str):
        try:
            c = 0
            for i, item in enumerate(reversed(num_str)):
                c = d[c][p[i % 8][int(item)]]
            return c == 0
        except Exception:
            return False

    try:
        if not os.path.exists(pdf_path):
            return details

        with open(pdf_path, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            normalized_text = re.sub(r'\s+', ' ', text)
            consecutive_matches = re.findall(r'(?<!\d)\d{12}(?!\d)', normalized_text)
            spaced_matches = re.findall(r'(?<!\d)(?:\d{4}\s\d{4}\s\d{4})(?!\d)', text)

            candidates = []
            for m in consecutive_matches:
                candidates.append(m)
            for m in spaced_matches:
                candidates.append(m.replace(" ", "").replace("\n", "").replace("\r", ""))

            for cand in candidates:
                if validate_verhoeff(cand):
                    details['aadhaar'] = f"{cand[:4]} {cand[4:8]} {cand[8:]}"
                    break

            if details['aadhaar'] == 'Not found' and candidates:
                cand = candidates[0]
                details['aadhaar'] = f"{cand[:4]} {cand[4:8]} {cand[8:]}"

            lines = [l.strip() for l in text.split('\n') if l.strip()]
            dob_idx = -1

            for idx, line in enumerate(lines):
                line_lower = line.lower()
                if any(kw in line_lower for kw in ['dob', 'birth', 'yob', 'year of birth']):
                    if not any(ign in line_lower for ign in ['issued', 'issue', 'details as on', 'download']):
                        dob_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', line)
                        if not dob_match:
                            dob_match = re.search(r'\b\d{4}\b', line)
                        if dob_match:
                            details['dob'] = dob_match.group(0)
                            dob_idx = idx
                            break

            if details['dob'] == 'Not found':
                for idx, line in enumerate(lines):
                    line_lower = line.lower()
                    if not any(ign in line_lower for ign in ['issued', 'issue', 'details as on', 'download']):
                        dob_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', line)
                        if dob_match:
                            details['dob'] = dob_match.group(0)
                            dob_idx = idx
                            break

            for line in lines:
                l_upper = line.upper()
                if "FEMALE" in l_upper:
                    details['gender'] = "FEMALE"
                    break
                elif "MALE" in l_upper:
                    details['gender'] = "MALE"
                    break
                elif "TRANSGENDER" in l_upper:
                    details['gender'] = "TRANSGENDER"
                    break

            if dob_idx != -1:
                name_cand_1 = lines[dob_idx - 1] if dob_idx - 1 >= 0 else ""
                name_cand_2 = lines[dob_idx - 2] if dob_idx - 2 >= 0 else ""

                if name_cand_1 and re.match(r'^[a-zA-Z\s\.]+$', name_cand_1) and len(name_cand_1) >= 3:
                    if name_cand_1.upper() not in ["MALE", "FEMALE", "TRANSGENDER", "TO"]:
                        details['name'] = name_cand_1.strip().title()

                if details['name'] == 'Not found' and name_cand_2 and re.match(r'^[a-zA-Z\s\.]+$', name_cand_2) and len(name_cand_2) >= 3:
                    if name_cand_2.upper() not in ["MALE", "FEMALE", "TRANSGENDER", "TO"]:
                        details['name'] = name_cand_2.strip().title()

            if details['name'] == 'Not found':
                for idx, line in enumerate(lines):
                    if line.upper() == "TO":
                        if idx + 1 < len(lines):
                            cand = lines[idx + 1]
                            if re.match(r'^[a-zA-Z\s\.]+$', cand) and len(cand) >= 3:
                                details['name'] = cand.strip().title()
                                break

            address_start_match = re.search(r'\bAddress\s*:\s*', text, re.IGNORECASE)
            if address_start_match:
                start_pos = address_start_match.end()
                pin_match = re.search(r'\b\d{6}\b', text[start_pos:])
                if pin_match:
                    end_pos = start_pos + pin_match.end()
                    raw_address = text[start_pos:end_pos].strip()
                    clean_address = re.sub(r'\s+', ' ', raw_address)
                    clean_address = re.sub(r'\s*/\s*', '/', clean_address)
                    clean_address = re.sub(r'\s+([,;:\.])', r'\1', clean_address)
                    clean_address = re.sub(r'([,;:\.])([a-zA-Z0-9])', r'\1 \2', clean_address)
                    details['address'] = clean_address.strip()
            else:
                co_match = re.search(r'\b(C/O|S/O|W/O|D/O)\b', text, re.IGNORECASE)
                if co_match:
                    start_pos = co_match.start()
                    pin_match = re.search(r'\b\d{6}\b', text[start_pos:])
                    if pin_match:
                        end_pos = start_pos + pin_match.end()
                        raw_address = text[start_pos:end_pos].strip()
                        clean_address = re.sub(r'\s+', ' ', raw_address)
                        clean_address = re.sub(r'\s*/\s*', '/', clean_address)
                        clean_address = re.sub(r'\s+([,;:\.])', r'\1', clean_address)
                        clean_address = re.sub(r'([,;:\.])([a-zA-Z0-9])', r'\1 \2', clean_address)
                        details['address'] = clean_address.strip()

    except Exception as e:
        logger.error(f"Error in extract_all_aadhaar_details: {e}")

    return details


# ============== PDF DELIVERY ==============
def deliver_pdf(chat_id, pdf_path, verified_name, dob=None, status_msg_id=None, stop_event=None, finish_event=None, done_event=None):
    name_display = verified_name if verified_name and verified_name.strip() else "Mr."
    pdf_path = os.path.abspath(pdf_path)

    try:
        if not os.path.exists(pdf_path):
            if stop_event:
                stop_event.set()
            logger.error(f"PDF file not found: {pdf_path}")
            if status_msg_id:
                delete_message(chat_id, status_msg_id)
            send_message(chat_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\nPDF file not found. Please try again.")
            deduct_credit(chat_id)
            clear_session(chat_id)
            return

        crack_success, password, decrypted_path, _ = bot.crack_pdf_with_name(pdf_path, name_display, dob, None)
        tag = get_user_log_tag(chat_id)

        details = None
        if crack_success and decrypted_path and os.path.exists(decrypted_path):
            logger.info(f"UNLOCKED PDF SUCCESS! {tag} Name: '{name_display}' | Password: '{password}' | Delivered.")

            details = extract_all_aadhaar_details(decrypted_path)
            if details['name'] != 'Not found' and (name_display.upper() in ["MR", "MR."]):
                name_display = details['name']
        else:
            logger.warning(f"Password crack failed for name='{name_display}'. Sending locked PDF. {tag}")

        if stop_event:
            stop_event.set()
        if status_msg_id:
            delete_message(chat_id, status_msg_id)
            status_msg_id = None

        if crack_success and decrypted_path and os.path.exists(decrypted_path):
            caption = (
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Document Ready  OK</b>\n\n"
                f"Name    -  {name_display}\n"
                f"Format  -  e-Aadhaar PDF\n"
                f"Status  -  <b>Unlocked</b>\n"
                f"{DIVIDER}"
            )

            send_document(chat_id, decrypted_path, caption=caption, filename="Aadhaar.pdf", auto_delete=False)

            if details and details['aadhaar'] != 'Not found':
                info_msg = (
                    f"<b>Name</b>     - <code>{name_display}</code>\n"
                    f"<b>Gender</b>   - <code>{details['gender']}</code>\n"
                    f"<b>DOB</b>      - <code>{details['dob']}</code>\n"
                    f"<b>Aadhaar</b>  - <code>{details['aadhaar']}</code>\n"
                    f"<b>Address</b>  - <code>{details['address']}</code>"
                )
                send_message(chat_id, info_msg)

            u = get_user(chat_id)
            uname_str = f" (@{u['username']}" + ")" if u and u.get('username') else ""

            cr_after = get_credits(chat_id)
            if cr_after != float('inf'):
                cr_after = max(0, int(cr_after) - 1)
                cr_log = f"{cr_after} Left"
            else:
                if u and u.get('lifetime'):
                    cr_log = "Lifetime Unlimited"
                elif u and u.get('expiry'):
                    try:
                        expiry_dt = datetime.fromisoformat(u['expiry'])
                        delta = expiry_dt - datetime.now()
                        days_left = max(0, delta.days)
                        cr_log = f"{days_left} day unlimited left"
                    except Exception:
                        cr_log = "Unlimited"
                else:
                    cr_log = "Unlimited"

            log_text = (
                f"PDF Delivered\n"
                f"User  - {u.get('first_name','Unknown') if u else 'Unknown'}{uname_str}\n"
                f"ID    - <code>{chat_id}</code>\n"
                f"Name  - {name_display}\n"
                f"Credits -  {cr_log}"
            )
            offer_kb = None
            if cr_log == "0 Left" or (isinstance(cr_after, (int, float)) and cr_after <= 0):
                offer_kb = {
                    'inline_keyboard': [
                        [{'text': 'Send Offer to User', 'callback_data': f'send_offer_zero_{chat_id}'}]
                    ]
                }
            send_log(log_text, reply_markup=offer_kb)

            if chat_id in OWNER_IDS:
                token = str(uuid.uuid4())[:8]
                PENDING_ADMIN_PDFS[token] = {
                    'chat_id': chat_id,
                    'pdf_path': decrypted_path,
                    'other_pdf_path': pdf_path if decrypted_path != pdf_path else None,
                    'created_at': time.time()
                }
                admin_prompt = (
                    f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                    f"<b>Channel Log Permission</b>\n\n"
                    f"Kya is PDF ko <b>PDF Logs Channel</b> me post karna hai?\n"
                    f"{DIVIDER}"
                )
                admin_kb = {
                    'inline_keyboard': [
                        [
                            {'text': 'Send to Channel', 'callback_data': f'admin_pdf_send_{token}'},
                            {'text': "Don't Send", 'callback_data': f'admin_pdf_skip_{token}'}
                        ]
                    ]
                }
                send_message(chat_id, admin_prompt, reply_markup=admin_kb)
            else:
                if PDF_LOG_CHANNEL_ID and os.path.exists(decrypted_path):
                    pdf_num = str(get_next_pdf_log_count())
                    send_document(PDF_LOG_CHANNEL_ID, decrypted_path, caption=pdf_num, filename="Aadhaar.pdf", auto_delete=False)

                try:
                    if decrypted_path and os.path.exists(decrypted_path):
                        os.remove(decrypted_path)
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                except Exception:
                    pass
        else:
            caption = (
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Document Ready</b>\n\n"
                f"Name    -  {name_display}\n"
                f"Format  -  e-Aadhaar PDF\n"
                f"Status  -  Password Protected\n"
                f"{DIVIDER}\n\n"
                f"<i>Password: first 4 letters of name + birth year\n"
                f"Example: <code>RAJE1995</code></i>"
            )
            send_document(chat_id, pdf_path, caption=caption, filename="Aadhaar.pdf", auto_delete=False)

            u = get_user(chat_id)
            uname_str = f" (@{u['username']}" + ")" if u and u.get('username') else ""
            log_text = (
                f"PDF Delivered (Locked)\n"
                f"User  - {u.get('first_name','Unknown') if u else 'Unknown'}{uname_str}\n"
                f"ID    - <code>{chat_id}</code>\n"
                f"Name  - {name_display}"
            )
            send_log(log_text)

            if chat_id in OWNER_IDS:
                token = str(uuid.uuid4())[:8]
                PENDING_ADMIN_PDFS[token] = {
                    'chat_id': chat_id,
                    'pdf_path': pdf_path,
                    'other_pdf_path': None,
                    'created_at': time.time()
                }
                admin_prompt = (
                    f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                    f"<b>Channel Log Permission</b>\n\n"
                    f"Kya is PDF ko <b>PDF Logs Channel</b> me post karna hai?\n"
                    f"{DIVIDER}"
                )
                admin_kb = {
                    'inline_keyboard': [
                        [
                            {'text': 'Send to Channel', 'callback_data': f'admin_pdf_send_{token}'},
                            {'text': "Don't Send", 'callback_data': f'admin_pdf_skip_{token}'}
                        ]
                    ]
                }
                send_message(chat_id, admin_prompt, reply_markup=admin_kb)
            else:
                if PDF_LOG_CHANNEL_ID and os.path.exists(pdf_path):
                    pdf_num = str(get_next_pdf_log_count())
                    send_document(PDF_LOG_CHANNEL_ID, pdf_path, caption=pdf_num, filename="Aadhaar.pdf", auto_delete=False)

                try:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                except Exception:
                    pass
    except Exception as e:
        logger.error(f"PDF delivery error: {e}")
        if stop_event:
            stop_event.set()
        if status_msg_id:
            delete_message(chat_id, status_msg_id)
        if pdf_path and os.path.exists(pdf_path):
            send_document(
                chat_id, pdf_path,
                caption=f"<b>{BOT_NAME}</b>\n{DIVIDER}\n<b>Document Ready</b>",
                filename="Aadhaar.pdf",
                auto_delete=False
            )
            if PDF_LOG_CHANNEL_ID:
                pdf_num = str(get_next_pdf_log_count())
                send_document(
                    PDF_LOG_CHANNEL_ID, pdf_path,
                    caption=pdf_num,
                    filename="Aadhaar.pdf",
                    auto_delete=False
                )
            try:
                os.remove(pdf_path)
            except Exception:
                pass

    deduct_credit(chat_id)
    cr = get_credits(chat_id)
    cr_display = "Lifetime" if cr == float('inf') else str(int(cr))
    clear_session(chat_id)
    no_credits_msg = ""
    send_message(
        chat_id,
        f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
        f"<b>Download Complete  OK</b>\n\n"
        f"Credits remaining  -  {cr_display}"
        f"{no_credits_msg}\n\n"
        f"{DIVIDER}\n"
        f"<i>Select a method below for another download.</i>",
        reply_markup=get_main_keyboard()
    )


def send_multibot_broadcast_message(target_chat_id, admin_chat_id, broadcast_msg_id=None, photo_file_id=None, message_text=None):
    tokens = [
        TELEGRAM_BOT_TOKEN,
        SECOND_BOT_TOKEN
    ]
    for token in tokens:
        try:
            if broadcast_msg_id:
                url = f"https://api.telegram.org/bot{token}/copyMessage"
                data = {'chat_id': target_chat_id, 'from_chat_id': admin_chat_id, 'message_id': broadcast_msg_id}
                res = get_telegram_session().post(url, json=data, timeout=15).json()
            elif photo_file_id:
                url = f"https://api.telegram.org/bot{token}/sendPhoto"
                data = {'chat_id': target_chat_id, 'photo': photo_file_id, 'caption': message_text or "", 'parse_mode': 'HTML'}
                res = get_telegram_session().post(url, json=data, timeout=15).json()
            else:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {'chat_id': target_chat_id, 'text': message_text or "<b>Broadcast</b>", 'parse_mode': 'HTML', 'disable_web_page_preview': True}
                res = get_telegram_session().post(url, json=data, timeout=15).json()

            if res and res.get('ok'):
                return True
        except Exception:
            pass
    return False


def run_background_broadcast(admin_chat_id, status_msg_id, broadcast_msg_id=None, message_text=None, photo_file_id=None, target_type='all'):
    now = datetime.now()
    all_docs = list(users_col.find({"banned": {"$ne": True}}))

    if target_type == 'premium':
        users = []
        for u in all_docs:
            has_exp = False
            exp_str = u.get('expiry')
            if exp_str:
                try:
                    if datetime.fromisoformat(exp_str) > now:
                        has_exp = True
                except Exception:
                    pass
            if u.get('is_premium') or u.get('lifetime') or has_exp:
                users.append(u)
    elif target_type == 'zerocr':
        users = []
        for u in all_docs:
            has_exp = False
            exp_str = u.get('expiry')
            if exp_str:
                try:
                    if datetime.fromisoformat(exp_str) > now:
                        has_exp = True
                except Exception:
                    pass
            is_premium_user = u.get('is_premium') or u.get('lifetime') or has_exp
            if not is_premium_user:
                users.append(u)
    else:
        users = all_docs

    total_targets = len(users)
    if total_targets == 0:
        target_labels = {
            'all': 'All Users',
            'premium': 'Premium Users',
            'zerocr': '0 Credit & No Plan Users'
        }
        lbl = target_labels.get(target_type, 'Target Users')
        edit_message(
            admin_chat_id, status_msg_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Broadcast Cancelled</b>\n\n"
            f"No users found matching <b>{lbl}</b> segment."
        )
        return

    target_labels = {
        'all': 'All Users',
        'premium': 'Premium Users',
        'zerocr': '0 Credit & No Plan Users'
    }
    label = target_labels.get(target_type, 'All Users')

    u_success = 0
    u_failed = 0
    processed = 0
    last_update_time = 0.0

    def get_progress_bar(percent, length=10):
        filled_length = int(length * percent // 100)
        filled_length = min(max(filled_length, 0), length)
        return '#' * filled_length + '-' * (length - filled_length)

    def send_to_user(user_id):
        return send_multibot_broadcast_message(
            user_id, admin_chat_id,
            broadcast_msg_id=broadcast_msg_id,
            photo_file_id=photo_file_id,
            message_text=message_text
        )

    max_workers = min(30, len(users) if users else 1)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(send_to_user, str(doc["_id"])): str(doc["_id"]) for doc in users}

        for future in as_completed(futures):
            success = future.result()
            if success:
                u_success += 1
            else:
                u_failed += 1

            processed += 1

            now_t = time.time()
            if now_t - last_update_time >= 3.0 or processed == total_targets:
                last_update_time = now_t
                progress = (processed / total_targets) * 100
                bar = get_progress_bar(progress)
                status_text = (
                    f"Broadcast in Progress ({label})\n"
                    f"{DIVIDER}\n"
                    f"Progress: <code>{progress:.1f}%</code>\n"
                    f"[{bar}]\n\n"
                    f"Target ({label}):\n"
                    f"Sent: <code>{u_success}</code>\n"
                    f"Failed: <code>{u_failed}</code>\n\n"
                    f"Processed: <code>{processed}/{total_targets}</code>"
                )
                try:
                    edit_message(admin_chat_id, status_msg_id, status_text)
                except Exception as e:
                    logger.error(f"Error updating broadcast progress: {e}")

    bar = get_progress_bar(100.0)
    report = (
        f"Broadcast Complete ({label})\n"
        f"{DIVIDER}\n"
        f"Progress: <code>100.0%</code>\n"
        f"[{bar}]\n\n"
        f"Target ({label}):\n"
        f"Sent: <code>{u_success}</code>\n"
        f"Failed: <code>{u_failed}</code>\n\n"
        f"Total Success: <code>{u_success} / {total_targets}</code>"
    )
    edit_message(admin_chat_id, status_msg_id, report)


SPINNER_FRAMES = ["|", "/", "-", "\\"]


def get_spinner(attempt):
    return SPINNER_FRAMES[(attempt - 1) % len(SPINNER_FRAMES)]
    # ============== OTP FLOWS ==============
def send_mobile_otp_flow(chat_id, mobile, name, current_data, tag, status_msg_id=None):
    if status_msg_id:
        edit_message(
            chat_id, status_msg_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Sending OTP</b>\n\n"
            f"<i>Generating & solving Captcha...</i>",
            reply_markup=get_cancel_keyboard()
        )
    else:
        status_msg = send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Sending OTP</b>\n\n"
            f"<i>Generating & solving Captcha...</i>",
            reply_markup=get_cancel_keyboard()
        )
        status_msg_id = status_msg.get('result', {}).get('message_id') if status_msg else None

    sd = {**current_data, 'mobile': mobile, 'name': name}
    max_attempts = 8
    otp_sent_successfully = False
    last_error = "Could not generate captcha"
    no_record_count = 0

    for attempt in range(1, max_attempts + 1):
        spin = get_spinner(attempt)
        if status_msg_id:
            if attempt >= 3:
                sub_text = f"UIDAI portal busy, retrying request ({attempt}/{max_attempts})..."
            else:
                sub_text = f"Solving Captcha (Attempt {attempt}/{max_attempts})..."
            edit_message(
                chat_id, status_msg_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Sending OTP</b>\n\n"
                f"<i>{spin}  {sub_text}</i>"
            )

        pre = get_prefetched_captcha(chat_id, revamp=True) if attempt == 1 else None
        if pre:
            image_bytes = pre['image_bytes']
            captcha_txn_id = pre['captcha_txn_id']
            transaction_id = pre['transaction_id']
            captcha_proxy = pre['captcha_proxy']
            captcha_code = pre['captcha_code']
            logger.info(f"Using pre-fetched Captcha (0ms latency!) {tag}")
        else:
            image_bytes, captcha_txn_id, transaction_id, captcha_proxy = bot.get_captcha(chat_id, revamp=True)
            if not image_bytes:
                last_error = "Captcha service unavailable"
                time.sleep(0.5)
                continue

            try:
                captcha_code = solve_captcha_robust(image_bytes, chat_id)
            except Exception as e:
                logger.error(f"ddddocr error: {e}")
                captcha_code = ""

        if not captcha_code:
            last_error = "Failed to solve captcha locally"
            continue

        sd.update({
            'captcha_code': captcha_code,
            'captcha1_txn_id': captcha_txn_id,
            'transaction_id': transaction_id
        })

        success, result = bot.send_eid_otp(
            chat_id, sd['mobile'], sd['name'],
            captcha_code, captcha_txn_id, transaction_id,
            proxy_hint=captcha_proxy
        )

        if success:
            logger.info(f"Mobile OTP Sent successfully to {sd['mobile']} on attempt {attempt} {tag}")
            otp_sent_successfully = True

            otp_text = (
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>OTP Sent  OK</b>\n\n"
                f"Enter the 6-digit OTP sent to your mobile\n\n"
                f"<i>Valid for 10 minutes</i>"
            )
            if status_msg_id:
                edit_message(chat_id, status_msg_id, otp_text, reply_markup=get_cancel_keyboard())
                otp_sent_msg_id = status_msg_id
            else:
                otp_sent_res = send_message(chat_id, otp_text, reply_markup=get_cancel_keyboard())
                otp_sent_msg_id = otp_sent_res.get('result', {}).get('message_id') if otp_sent_res else None

            set_session(chat_id, 'awaiting_otp', {**sd, 'eid_otp_txn_id': result, 'otp_sent_msg_id': otp_sent_msg_id, 'proxy_hint': captcha_proxy})
            prefetch_captcha_async(chat_id, revamp=False)
            break
        else:
            clean_err = re.sub(r'\s+', ' ', str(result)).strip()
            logger.warning(f"Mobile OTP Attempt {attempt} failed: {clean_err} {tag}")
            last_error = clean_err
            err_lower = clean_err.lower()

            if "no record" in err_lower:
                no_record_count += 1
                if no_record_count >= 2:
                    break
                time.sleep(1)
                continue
            if any(x in err_lower for x in ["exceeded", "blocked", "banned", "suspended"]):
                break
            if any(x in err_lower for x in ["technical", "difficulties", "server", "internal", "service unavailable"]):
                time.sleep(0.5)
                continue
            if any(x in err_lower for x in ["connection", "ssl", "timeout", "disconnected", "proxy"]):
                time.sleep(0.2)
                continue
            if any(x in err_lower for x in ["captcha", "invalid", "incorrect", "mismatch"]):
                time.sleep(0.1)
                continue
            time.sleep(0.2)

    if not otp_sent_successfully:
        if status_msg_id:
            delete_message(chat_id, status_msg_id)
        set_session(chat_id, 'awaiting_otp_retry', sd)
        user_err = clean_user_error(last_error)
        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"{user_err}\n\n"
            f"<i>Select a method below to retry.</i>",
            reply_markup=get_retry_keyboard('retry_mobile_otp')
        )


def send_aadhaar_sms_otp_flow(chat_id, mobile, name, current_data, tag, status_msg_id=None):
    if status_msg_id:
        edit_message(
            chat_id, status_msg_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Sending OTP (Aadhaar SMS)</b>\n\n"
            f"<i>Generating & solving Captcha...</i>",
            reply_markup=get_cancel_keyboard()
        )
    else:
        status_msg = send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Sending OTP (Aadhaar SMS)</b>\n\n"
            f"<i>Generating & solving Captcha...</i>",
            reply_markup=get_cancel_keyboard()
        )
        status_msg_id = status_msg.get('result', {}).get('message_id') if status_msg else None

    sd = {**current_data, 'mobile': mobile, 'name': name}
    max_attempts = 8
    otp_sent_successfully = False
    last_error = "Could not generate captcha"
    no_record_count = 0

    for attempt in range(1, max_attempts + 1):
        spin = get_spinner(attempt)
        if status_msg_id:
            if attempt >= 3:
                sub_text = f"UIDAI portal busy, retrying request ({attempt}/{max_attempts})..."
            else:
                sub_text = f"Solving Captcha (Attempt {attempt}/{max_attempts})..."
            edit_message(
                chat_id, status_msg_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Sending OTP (Aadhaar SMS)</b>\n\n"
                f"<i>{spin}  {sub_text}</i>"
            )

        pre = get_prefetched_captcha(chat_id, revamp=True) if attempt == 1 else None
        if pre:
            image_bytes = pre['image_bytes']
            captcha_txn_id = pre['captcha_txn_id']
            transaction_id = pre['transaction_id']
            captcha_proxy = pre['captcha_proxy']
            captcha_code = pre['captcha_code']
            logger.info(f"Using pre-fetched Captcha (0ms latency!) {tag}")
        else:
            image_bytes, captcha_txn_id, transaction_id, captcha_proxy = bot.get_captcha(chat_id, revamp=True)
            if not image_bytes:
                last_error = "Captcha service unavailable"
                time.sleep(0.5)
                continue

            try:
                captcha_code = solve_captcha_robust(image_bytes, chat_id)
            except Exception as e:
                logger.error(f"ddddocr error: {e}")
                captcha_code = ""

        if not captcha_code:
            last_error = "Failed to solve captcha locally"
            continue

        sd.update({
            'captcha_code': captcha_code,
            'captcha1_txn_id': captcha_txn_id,
            'transaction_id': transaction_id
        })

        success, result = bot.send_uid_sms_otp(
            chat_id, sd['mobile'], sd['name'],
            captcha_code, captcha_txn_id, transaction_id,
            proxy_hint=captcha_proxy
        )

        if success:
            logger.info(f"Aadhaar SMS OTP Sent successfully to {sd['mobile']} on attempt {attempt} {tag}")
            otp_sent_successfully = True

            otp_text = (
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>OTP Sent  OK</b>\n\n"
                f"Enter the 6-digit OTP sent to your mobile\n\n"
                f"<i>Valid for 10 minutes</i>"
            )
            if status_msg_id:
                edit_message(chat_id, status_msg_id, otp_text, reply_markup=get_cancel_keyboard())
                otp_sent_msg_id = status_msg_id
            else:
                otp_sent_res = send_message(chat_id, otp_text, reply_markup=get_cancel_keyboard())
                otp_sent_msg_id = otp_sent_res.get('result', {}).get('message_id') if otp_sent_res else None

            set_session(chat_id, 'awaiting_aadhaar_sms_otp', {**sd, 'eid_otp_txn_id': result, 'otp_sent_msg_id': otp_sent_msg_id, 'proxy_hint': captcha_proxy})
            prefetch_captcha_async(chat_id, revamp=False)
            break
        else:
            clean_err = re.sub(r'\s+', ' ', str(result)).strip()
            logger.warning(f"Aadhaar SMS OTP Attempt {attempt} failed: {clean_err} {tag}")
            last_error = clean_err
            err_lower = clean_err.lower()

            if "no record" in err_lower:
                no_record_count += 1
                if no_record_count >= 2:
                    break
                time.sleep(1)
                continue
            if any(x in err_lower for x in ["exceeded", "blocked", "banned", "suspended"]):
                break
            if any(x in err_lower for x in ["technical", "difficulties", "server", "internal", "service unavailable"]):
                time.sleep(0.5)
                continue
            if any(x in err_lower for x in ["connection", "ssl", "timeout", "disconnected", "proxy"]):
                time.sleep(0.2)
                continue
            if any(x in err_lower for x in ["captcha", "invalid", "incorrect", "mismatch"]):
                time.sleep(0.1)
                continue
            time.sleep(0.2)

    if not otp_sent_successfully:
        if status_msg_id:
            delete_message(chat_id, status_msg_id)
        set_session(chat_id, 'awaiting_otp_retry', sd)
        user_err = clean_user_error(last_error)
        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"{user_err}\n\n"
            f"<i>Select a method below to retry.</i>",
            reply_markup=get_retry_keyboard('retry_aadhaar_sms_otp')
        )


def send_pdf_otp_flow(chat_id, eid, verified_name, current_data, tag, status_msg_id=None):
    if status_msg_id:
        edit_message(
            chat_id, status_msg_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Sending OTP for PDF</b>\n\n"
            f"<i>Generating & solving Captcha...</i>"
        )
    else:
        status_msg = send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Sending OTP for PDF</b>\n\n"
            f"<i>Generating & solving Captcha...</i>"
        )
        status_msg_id = status_msg.get('result', {}).get('message_id') if status_msg else None

    sd = {**current_data, 'eid': eid, 'verified_name': verified_name}
    max_attempts = 8
    otp_sent_successfully = False
    last_error = "Could not generate captcha"

    for attempt in range(1, max_attempts + 1):
        spin = get_spinner(attempt)
        if status_msg_id:
            if attempt >= 3:
                sub_text = f"UIDAI portal busy, retrying request ({attempt}/{max_attempts})..."
            else:
                sub_text = f"Solving Captcha (Attempt {attempt}/{max_attempts})..."
            edit_message(
                chat_id, status_msg_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Sending OTP for PDF</b>\n\n"
                f"<i>{spin}  {sub_text}</i>"
            )

        pre = get_prefetched_captcha(chat_id, revamp=False) if attempt == 1 else None
        if pre:
            image_bytes = pre['image_bytes']
            captcha_txn_id = pre['captcha_txn_id']
            transaction_id = pre['transaction_id']
            captcha_proxy = pre['captcha_proxy']
            captcha_code = pre['captcha_code']
            logger.info(f"Using pre-fetched Captcha for PDF OTP (0ms latency!) {tag}")
        else:
            logger.info(f"Generating Captcha for PDF Download (Attempt {attempt}/{max_attempts})... {tag}")
            image_bytes, captcha_txn_id, transaction_id, captcha_proxy = bot.get_captcha(chat_id)
            if not image_bytes:
                last_error = "Captcha service unavailable"
                time.sleep(0.5)
                continue

            try:
                logger.info(f"Solving Captcha locally via ddddocr... {tag}")
                captcha_code = solve_captcha_robust(image_bytes, chat_id)
                if captcha_code:
                    logger.info(f"Captcha Solved Successfully: '{captcha_code}' {tag}")
            except Exception as e:
                logger.error(f"ddddocr error: {e}")
                captcha_code = ""

        if not captcha_code:
            last_error = "Failed to solve captcha locally"
            continue

        sd.update({
            'captcha2_code': captcha_code,
            'captcha2_txn_id': captcha_txn_id,
            'transaction_id2': transaction_id
        })

        success_otp, otp_txn_id, msg = bot.send_aadhaar_otp(
            chat_id, sd['eid'], captcha_code, captcha_txn_id, transaction_id,
            proxy_hint=captcha_proxy
        )

        if success_otp:
            logger.info(f"PDF OTP Sent successfully for EID: {sd['eid']} on attempt {attempt} {tag}")
            otp_sent_successfully = True

            otp_text = (
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>OTP Sent  OK</b>\n\n"
                f"Enter the 6-digit OTP to download your PDF\n\n"
                f"<i>Valid for 10 minutes</i>"
            )
            if status_msg_id:
                edit_message(chat_id, status_msg_id, otp_text, reply_markup=get_cancel_keyboard())
                otp_sent_msg_id = status_msg_id
            else:
                otp_sent_res = send_message(chat_id, otp_text, reply_markup=get_cancel_keyboard())
                otp_sent_msg_id = otp_sent_res.get('result', {}).get('message_id') if otp_sent_res else None

            set_session(chat_id, 'awaiting_pdf_otp', {**sd, 'pdf_otp_txn_id': otp_txn_id, 'pdf_otp_sent_msg_id': otp_sent_msg_id, 'proxy_hint': captcha_proxy})
            break
        else:
            clean_err = re.sub(r'\s+', ' ', str(msg)).strip()
            logger.warning(f"PDF OTP Attempt {attempt} failed: {clean_err} {tag}")
            last_error = clean_err
            err_lower = clean_err.lower()
            if any(x in err_lower for x in ["correct format", "not in the correct", "eid/sid", "format", "not valid", "invalid eid", "28 digit", "12 digit", "length"]):
                break
            if any(x in err_lower for x in ["exceeded", "blocked", "banned", "suspended"]):
                break
            if any(x in err_lower for x in ["technical", "difficulties", "server", "internal", "service unavailable"]):
                time.sleep(0.5)
                continue
            if any(x in err_lower for x in ["connection", "ssl", "timeout", "disconnected", "proxy"]):
                time.sleep(0.2)
                continue
            if any(x in err_lower for x in ["captcha", "invalid", "incorrect", "mismatch"]):
                time.sleep(0.1)
                continue
            time.sleep(0.2)

    if not otp_sent_successfully:
        if status_msg_id:
            delete_message(chat_id, status_msg_id)
        last_err_lower = last_error.lower()
        is_format_error = any(x in last_err_lower for x in ["correct format", "not in the correct", "eid/sid", "format", "not valid", "invalid eid", "28 digit", "12 digit", "length"])
        if is_format_error:
            clear_session(chat_id)
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Invalid EID</b>\n\n"
                f"The EID you entered is <b>invalid or in incorrect format</b>.\n\n"
                f"EID must be <b>28 digits</b>\n"
                f"Aadhaar Number must be <b>12 digits</b>\n\n"
                f"<i>Please start again with a valid EID/Aadhaar number.</i>"
            )
        else:
            set_session(chat_id, 'awaiting_pdf_otp_retry', sd)
            user_err = clean_user_error(last_error)
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"{user_err}\n\n"
                f"<i>Select a method below to retry.</i>",
                reply_markup=get_retry_keyboard('retry_pdf_otp')
            )


def send_pdf_otp_direct_flow(chat_id, eid, verified_name, current_data, tag, status_msg_id=None):
    if status_msg_id:
        edit_message(
            chat_id, status_msg_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Sending OTP</b>\n\n"
            f"<i>Generating & solving Captcha...</i>"
        )
    else:
        status_msg = send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Sending OTP</b>\n\n"
            f"<i>Generating & solving Captcha...</i>"
        )
        status_msg_id = status_msg.get('result', {}).get('message_id') if status_msg else None

    sd = {**current_data, 'eid': eid, 'verified_name': verified_name}
    max_attempts = 8
    otp_sent_successfully = False
    last_error = "Could not generate captcha"

    for attempt in range(1, max_attempts + 1):
        spin = get_spinner(attempt)
        if status_msg_id:
            if attempt >= 3:
                sub_text = f"UIDAI portal busy, retrying request ({attempt}/{max_attempts})..."
            else:
                sub_text = f"Solving Captcha (Attempt {attempt}/{max_attempts})..."
            edit_message(
                chat_id, status_msg_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Sending OTP</b>\n\n"
                f"<i>{spin}  {sub_text}</i>"
            )

        pre = get_prefetched_captcha(chat_id, revamp=False) if attempt == 1 else None
        if pre:
            image_bytes = pre['image_bytes']
            captcha_txn_id = pre['captcha_txn_id']
            transaction_id = pre['transaction_id']
            captcha_proxy = pre['captcha_proxy']
            captcha_code = pre['captcha_code']
            logger.info(f"Using pre-fetched Direct Captcha (0ms latency!) {tag}")
        else:
            image_bytes, captcha_txn_id, transaction_id, captcha_proxy = bot.get_captcha(chat_id)
            if not image_bytes:
                last_error = "Captcha service unavailable"
                time.sleep(1)
                continue

            try:
                captcha_code = solve_captcha_robust(image_bytes, chat_id)
            except Exception as e:
                logger.error(f"ddddocr error: {e}")
                captcha_code = ""

        if not captcha_code:
            last_error = "Failed to solve captcha locally"
            continue

        sd.update({
            'captcha2_code': captcha_code,
            'captcha2_txn_id': captcha_txn_id,
            'transaction_id2': transaction_id
        })

        success, otp_txn_id, msg = bot.send_aadhaar_otp(
            chat_id, sd['eid'], captcha_code, captcha_txn_id, transaction_id,
            proxy_hint=captcha_proxy
        )

        if success:
            logger.info(f"Direct PDF OTP Sent successfully for: {sd['eid']} on attempt {attempt} {tag}")
            otp_sent_successfully = True

            otp_text = (
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>OTP Sent  OK</b>\n\n"
                f"Enter the 6-digit OTP to download your PDF\n\n"
                f"<i>Valid for 10 minutes</i>"
            )
            if status_msg_id:
                edit_message(chat_id, status_msg_id, otp_text, reply_markup=get_cancel_keyboard())
                otp_sent_msg_id = status_msg_id
            else:
                otp_sent_res = send_message(chat_id, otp_text, reply_markup=get_cancel_keyboard())
                otp_sent_msg_id = otp_sent_res.get('result', {}).get('message_id') if otp_sent_res else None

            set_session(chat_id, 'awaiting_pdf_otp_direct', {**sd, 'pdf_otp_txn_id': otp_txn_id, 'pdf_otp_sent_msg_id': otp_sent_msg_id, 'proxy_hint': captcha_proxy})
            break
        else:
            clean_err = re.sub(r'\s+', ' ', str(msg)).strip()
            logger.warning(f"Direct PDF OTP Attempt {attempt} failed: {clean_err} {tag}")
            last_error = clean_err
            err_lower = clean_err.lower()
            if any(x in err_lower for x in ["correct format", "not in the correct", "eid/sid", "format", "not valid", "invalid eid", "invalid aadhaar", "does not exist", "not found", "28 digit", "12 digit", "length"]):
                break
            if any(x in err_lower for x in ["invalid otp", "wrong otp", "incorrect otp", "otp mismatch", "exceeded", "blocked", "banned", "suspended"]):
                break
            if any(x in err_lower for x in ["technical", "difficulties", "server", "internal", "service unavailable"]):
                time.sleep(0.5)
                continue
            if any(x in err_lower for x in ["connection", "ssl", "timeout", "disconnected", "proxy"]):
                time.sleep(0.2)
                continue
            if any(x in err_lower for x in ["captcha", "invalid captcha", "incorrect captcha", "mismatch"]):
                time.sleep(0.1)
                continue
            time.sleep(0.2)

    if not otp_sent_successfully:
        if status_msg_id:
            delete_message(chat_id, status_msg_id)
        last_err_lower = last_error.lower()
        is_format_error = any(x in last_err_lower for x in ["correct format", "not in the correct", "eid/sid", "format", "not valid", "invalid eid", "28 digit", "12 digit", "length"])
        if is_format_error:
            clear_session(chat_id)
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Invalid EID</b>\n\n"
                f"The EID you entered is <b>invalid or in incorrect format</b>.\n\n"
                f"EID must be <b>28 digits</b>\n"
                f"Aadhaar Number must be <b>12 digits</b>\n\n"
                f"<i>Please start again with a valid EID/Aadhaar number.</i>"
            )
        else:
            set_session(chat_id, 'awaiting_pdf_otp_direct_retry', sd)
            user_err = clean_user_error(last_error)
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"{user_err}\n\n"
                f"<i>Select a method below to retry.</i>",
                reply_markup=get_retry_keyboard('retry_pdf_otp_direct')
            )


# ============== CALLBACK HANDLER ==============
def handle_callback(chat_id, callback_query_id, data, message_id=None, cq=None):
    if data.startswith('admin_pdf_send_'):
        if chat_id not in OWNER_IDS:
            return
        token = data.replace('admin_pdf_send_', '')
        entry = PENDING_ADMIN_PDFS.pop(token, None)
        if not entry:
            if message_id:
                edit_message(chat_id, message_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\nRequest expired or already processed.")
            return

        pdf_path_to_send = entry['pdf_path']
        other_path = entry.get('other_pdf_path')

        if not os.path.exists(pdf_path_to_send):
            if message_id:
                edit_message(chat_id, message_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\nPDF file not found on disk.")
            return

        pdf_num = "0"
        if PDF_LOG_CHANNEL_ID and os.path.exists(pdf_path_to_send):
            pdf_num = str(get_next_pdf_log_count())
            send_document(PDF_LOG_CHANNEL_ID, pdf_path_to_send, caption=pdf_num, filename="Aadhaar.pdf", auto_delete=False)

        try:
            if os.path.exists(pdf_path_to_send):
                os.remove(pdf_path_to_send)
            if other_path and os.path.exists(other_path):
                os.remove(other_path)
        except Exception:
            pass

        if message_id:
            edit_message(chat_id, message_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\n<b>PDF Logs Channel me send kar diya gaya!</b> (Count: #{pdf_num})")
        return

    if data.startswith('admin_pdf_skip_'):
        if chat_id not in OWNER_IDS:
            return
        token = data.replace('admin_pdf_skip_', '')
        entry = PENDING_ADMIN_PDFS.pop(token, None)
        if not entry:
            if message_id:
                edit_message(chat_id, message_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\nRequest expired or already processed.")
            return

        pdf_path_to_send = entry['pdf_path']
        other_path = entry.get('other_pdf_path')

        try:
            if os.path.exists(pdf_path_to_send):
                os.remove(pdf_path_to_send)
            if other_path and os.path.exists(other_path):
                os.remove(other_path)
        except Exception:
            pass

        if message_id:
            edit_message(chat_id, message_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\n<b>PDF Logs Channel me send nahi kiya gaya.</b> (Count unchanged)")
        return

    if data.startswith('send_offer_help_') or data.startswith('send_offer_zero_') or data.startswith('send_offer_plans_'):
        if data.startswith('send_offer_zero_'):
            target_uid = data.split('send_offer_zero_', 1)[1]
            offer_msg = (
                "apke credits khatam hogye hai, or lene hai toh\n"
                f"DM {OWNER_USERNAME}"
            )
        elif data.startswith('send_offer_plans_'):
            target_uid = data.split('send_offer_plans_', 1)[1]
            offer_msg = (
                "Bot mei credits chahiye?\n"
                f"Dm {OWNER_USERNAME}"
            )
        else:
            target_uid = data.split('send_offer_help_', 1)[1]
            offer_msg = (
                "Bot mei credits chahiye?\n"
                f"Dm {OWNER_USERNAME}"
            )
        res = send_message(target_uid, offer_msg)
        if res and res.get('ok'):
            answer_callback_query(callback_query_id, "Special offer sent to user!", show_alert=False)
            if message_id:
                done_kb = {'inline_keyboard': [[{'text': 'Offer Sent to User', 'callback_data': 'offer_sent_done'}]]}
                edit_message_reply_markup(chat_id, message_id, done_kb)
        else:
            error_reason = "User blocked bot or chat not found"
            if res and not res.get('ok'):
                error_reason = res.get('description', error_reason)
            answer_callback_query(callback_query_id, f"Failed to send offer: {error_reason}", show_alert=True)
        return

    if data == 'offer_sent_done':
        answer_callback_query(callback_query_id, "Offer has already been sent to this user.", show_alert=False)
        return

    answer_callback_query(callback_query_id)

    _from = cq.get('from', {}) if cq else {}
    first_name = _from.get('first_name')
    username = _from.get('username')

    if data != 'check_join':
        ensure_user(chat_id, first_name=first_name, username=username)

    check_and_notify_expiry(chat_id)
    tag = get_user_log_tag(chat_id)
    logger.info(f"Clicked button: '{data}' {tag}")

    if data == 'check_join':
        if is_channel_member(chat_id):
            s = get_session(chat_id)
            referrer_id = s.get('data', {}).get('referrer_id')

            first_name = None
            username = None
            if cq and 'from' in cq:
                first_name = cq['from'].get('first_name')
                username = cq['from'].get('username')

            is_new = ensure_user(
                chat_id,
                referrer_id=referrer_id,
                first_name=first_name,
                username=username
            )
            cr = get_credits(chat_id)
            cr_display = "Lifetime" if cr == float('inf') else str(int(cr))
            u = get_user(chat_id)
            user_name = u.get('first_name', 'User') if u else 'User'
            send_message(
                chat_id,
                f"<b>{BOT_NAME} - WELCOME</b>\n{DIVIDER}\n"
                f"<blockquote><b>Hey {user_name}!</b>\n"
                f"Welcome to <b>{BOT_NAME}</b> - Fast and easy Aadhaar PDF download Bot from Govt site.</blockquote>\n\n"
                f"<b>System Highlights</b>\n"
                f"Source - Official Govt & OSINT Portals\n"
                f"Delivery - Auto-Unlocked PDF (No Password)\n"
                f"Modes - Mobile | Aadhaar | EID\n\n"
                f"<blockquote><b>Search Balance:</b> <code>{cr_display}</code></blockquote>\n"
                f"<i>Select a search mode from the bottom menu to begin.</i>",
                reply_markup=get_main_keyboard()
            )
        else:
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Not Joined Yet</b>\n\n"
                f"Channel membership not detected.\n\n"
                f"<i>Join the channel, then tap the button again.</i>",
                reply_markup=get_join_keyboard()
            )
        return

    if data == 'cancel':
        clear_session(chat_id)
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<i>Session cancelled.</i>"
        )
        return

    if data == 'retry_mobile_otp':
        s = get_session(chat_id)
        d = s.get('data', {})
        mobile = d.get('mobile')
        name = d.get('name', 'MR')
        if not mobile:
            send_message(chat_id, "Session expired or invalid. Please start again.")
            clear_session(chat_id)
            return

        send_mobile_otp_flow(chat_id, mobile, name, d, tag, status_msg_id=message_id)
        return

    if data == 'retry_pdf_otp':
        s = get_session(chat_id)
        d = s.get('data', {})
        eid = d.get('eid')
        verified_name = d.get('verified_name', 'Mr.')
        if not eid:
            send_message(chat_id, "Session expired or invalid. Please start again.")
            clear_session(chat_id)
            return

        send_pdf_otp_flow(chat_id, eid, verified_name, d, tag, status_msg_id=message_id)
        return

    if data == 'retry_pdf_otp_direct':
        s = get_session(chat_id)
        d = s.get('data', {})
        eid = d.get('eid')
        verified_name = d.get('verified_name', 'Mr.')
        if not eid:
            send_message(chat_id, "Session expired or invalid. Please start again.")
            clear_session(chat_id)
            return

        send_pdf_otp_direct_flow(chat_id, eid, verified_name, d, tag, status_msg_id=message_id)
        return

    if data == 'retry_aadhaar_sms_otp':
        s = get_session(chat_id)
        d = s.get('data', {})
        mobile = d.get('mobile')
        name = d.get('name', 'MR')
        if not mobile:
            send_message(chat_id, "Session expired or invalid. Please start again.")
            clear_session(chat_id)
            return

        send_aadhaar_sms_otp_flow(chat_id, mobile, name, d, tag, status_msg_id=message_id)
        return

    if data == 'eid_name_auto':
        s = get_session(chat_id)
        d = s.get('data', {})
        mobile = d.get('mobile')
        if not mobile:
            send_message(chat_id, "Session expired or invalid. Please start again.")
            clear_session(chat_id)
            return

        send_mobile_otp_flow(chat_id, mobile, 'MR', d, tag, status_msg_id=message_id)
        return

    if data == 'eid_name_custom':
        s = get_session(chat_id)
        d = s.get('data', {})
        if not d.get('mobile'):
            send_message(chat_id, "Session expired or invalid. Please start again.")
            clear_session(chat_id)
            return

        set_session(chat_id, 'awaiting_mobile_name', d)

        if message_id:
            delete_message(chat_id, message_id)

        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"Enter your full name as on Aadhaar\n\n"
            f"<i>This name will be used to generate EID OTP.</i>",
            reply_markup=get_cancel_keyboard()
        )
        return

    if data == 'aadhaar_sms_name_auto':
        s = get_session(chat_id)
        d = s.get('data', {})
        mobile = d.get('mobile')
        if not mobile:
            send_message(chat_id, "Session expired or invalid. Please start again.")
            clear_session(chat_id)
            return

        send_aadhaar_sms_otp_flow(chat_id, mobile, 'MR', d, tag, status_msg_id=message_id)
        return

    if data == 'aadhaar_sms_name_custom':
        s = get_session(chat_id)
        d = s.get('data', {})
        if not d.get('mobile'):
            send_message(chat_id, "Session expired or invalid. Please start again.")
            clear_session(chat_id)
            return

        set_session(chat_id, 'awaiting_aadhaar_sms_custom_name', d)

        if message_id:
            delete_message(chat_id, message_id)

        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"Enter your full name as on Aadhaar\n\n"
            f"<i>This name will be used to generate Aadhaar SMS OTP.</i>",
            reply_markup=get_cancel_keyboard()
        )
        return

    if data == 'panel_gen_key':
        type_kb = {
            'inline_keyboard': [
                [{'text': 'Limited (Credits)', 'callback_data': 'key_limited_1'}],
                [{'text': 'Unlimited (Lifetime)', 'callback_data': 'key_unlimited_1'}],
                [{'text': 'Back', 'callback_data': 'panel_back'}]
            ]
        }
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ generate key ]</b>\n\n"
            f"Select key type:",
            reply_markup=type_kb
        )
        return

    if data.startswith('key_limited_'):
        amount = int(data.split('_')[-1])
        set_session(chat_id, 'awaiting_key_credits', {'key_amount': amount, 'key_type': 'limited'})
        back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': 'panel_gen_key'}]]}
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ limited key ]</b>\n\n"
            f"Keys to generate - {amount}\n\n"
            f"Enter the number of credits each key should give:",
            reply_markup=back_kb
        )
        return

    if data.startswith('key_unlimited_'):
        amount = int(data.split('_')[-1])
        set_session(chat_id, 'awaiting_key_days', {'key_amount': amount, 'key_type': 'unlimited'})
        back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': 'panel_gen_key'}]]}
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ unlimited key ]</b>\n\n"
            f"Keys to generate - {amount}\n\n"
            f"Enter validity in days (e.g. 1, 7, 30) or 0 for Lifetime:",
            reply_markup=back_kb
        )
        return

    if data == 'panel_toggle_mm':
        global MAINTENANCE_MODE
        MAINTENANCE_MODE = not MAINTENANCE_MODE
        settings_col.update_one({"_id": "config"}, {"$set": {"maintenance_mode_b1": MAINTENANCE_MODE}}, upsert=True)
        text, kb = get_admin_panel_data()
        edit_message(chat_id, message_id, text, reply_markup=kb)
        return

    if data.startswith('panel_users_'):
        if chat_id not in OWNER_IDS:
            return
        try:
            pg = int(data.split('_')[-1])
        except ValueError:
            pg = 0
        show_users_page(chat_id, pg, message_id)
        return

    if data == 'panel_revoke':
        if chat_id not in OWNER_IDS:
            return
        set_session(chat_id, 'awaiting_revoke_id', {})
        back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': 'panel_back'}]]}
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ revoke user ]</b>\n\n"
            f"Enter the <b>User ID</b> to revoke access:",
            reply_markup=back_kb
        )
        return

    if data == 'panel_search_user':
        if chat_id not in OWNER_IDS:
            return
        set_session(chat_id, 'awaiting_search_user', {})
        back_kb = {'inline_keyboard': [[{'text': 'Back to Panel', 'callback_data': 'panel_back'}]]}
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ search user ]</b>\n\n"
            f"Enter the <b>User ID</b> or <b>Username</b> (e.g. @username) of the user:",
            reply_markup=back_kb
        )
        return

    if data.startswith('edit_user_'):
        if chat_id not in OWNER_IDS:
            return

        parts = data.split('_')

        if len(parts) == 3:
            clear_session(chat_id)
            uid = parts[2]
            user_doc = users_col.find_one({"_id": uid})
            if not user_doc:
                return
            is_banned = user_doc.get('banned', False)
            ban_btn_text = "Unban User" if is_banned else "Ban User"

            kb = {
                'inline_keyboard': [
                    [{'text': 'Add/Remove Searches', 'callback_data': f'edit_user_credits_{uid}'}],
                    [{'text': 'Set Unlimited', 'callback_data': f'edit_user_unlimited_{uid}'}],
                    [{'text': 'Remove Credits', 'callback_data': f'edit_user_reset_{uid}'}],
                    [{'text': ban_btn_text, 'callback_data': f'edit_user_ban_{uid}'}],
                    [{'text': 'Cancel', 'callback_data': f'edit_user_cancel_{uid}'}]
                ]
            }

            edit_message(chat_id, message_id, f"<b>Edit User: {uid}</b>\n\nChoose an action below:", reply_markup=kb)
            return

        elif len(parts) == 4:
            action = parts[2]
            uid = parts[3]

            if action == 'cancel':
                show_user_profile_admin(chat_id, uid, message_id)
                return

            elif action == 'reset':
                user_doc = users_col.find_one({"_id": uid})
                name = user_doc.get('first_name', 'Unknown') if user_doc else 'Unknown'
                confirm_kb = {
                    'inline_keyboard': [
                        [{'text': 'Yes, Revoke All Credits', 'callback_data': f'edit_user_confirmreset_{uid}'}],
                        [{'text': 'Back / Cancel', 'callback_data': f'edit_user_{uid}'}]
                    ]
                }
                edit_message(
                    chat_id, message_id,
                    f"<b>Confirm Revoke Credits</b>\n\n"
                    f"Are you sure you want to revoke all credits and unlimited access for <b>{name}</b> (<code>{uid}</code>)?",
                    reply_markup=confirm_kb
                )
                return

            elif action == 'confirmreset':
                users_col.update_one(
                    {"_id": uid},
                    {
                        "$set": {"credits": 0, "lifetime": False, "is_premium": False},
                        "$unset": {"expiry": "", "unlimited_days": "", "expiry_notified": ""}
                    }
                )
                invalidate_cached_user(uid)

                user_doc = users_col.find_one({"_id": uid})
                name = user_doc.get('first_name', 'Unknown') if user_doc else 'Unknown'
                username = user_doc.get('username') if user_doc else None
                uname_str = f" (@{username})" if username else ""

                send_log(
                    f"All Credits & Plan Revoked\n"
                    f"User   - <b>{name}</b>{uname_str}\n"
                    f"ID     - <code>{uid}</code>\n"
                    f"Status - <b>0 Credits & Unlimited Revoked</b>\n"
                    f"By     - Admin <code>{chat_id}</code>"
                )

                try:
                    send_message(
                        int(uid),
                        f"<b>Plan Update</b>\n\n"
                        f"An admin has reset your account. All search credits and unlimited access have been revoked."
                    )
                except Exception:
                    pass

                show_user_profile_admin(chat_id, uid, message_id)
                return

            elif action == 'ban':
                user_doc = users_col.find_one({"_id": uid})
                if not user_doc:
                    return
                is_banned = user_doc.get('banned', False)
                name = user_doc.get('first_name', 'Unknown')

                if is_banned:
                    title = "Confirm Unban User"
                    btn_text = "Yes, Unban User"
                    desc = f"Are you sure you want to <b>UNBAN</b> user <b>{name}</b> (<code>{uid}</code>)?"
                else:
                    title = "Confirm Ban User"
                    btn_text = "Yes, Ban User"
                    desc = f"Are you sure you want to <b>BAN</b> user <b>{name}</b> (<code>{uid}</code>)?"

                confirm_kb = {
                    'inline_keyboard': [
                        [{'text': btn_text, 'callback_data': f'edit_user_confirmban_{uid}'}],
                        [{'text': 'Back / Cancel', 'callback_data': f'edit_user_{uid}'}]
                    ]
                }
                edit_message(
                    chat_id, message_id,
                    f"<b>{title}</b>\n\n{desc}",
                    reply_markup=confirm_kb
                )
                return

            elif action == 'confirmban':
                user_doc = users_col.find_one({"_id": uid})
                if user_doc:
                    new_banned = not user_doc.get('banned', False)
                    users_col.update_one({"_id": uid}, {"$set": {"banned": new_banned}})
                    invalidate_cached_user(uid)

                    status_word = "Banned" if new_banned else "Unbanned"
                    name = user_doc.get('first_name', 'Unknown')
                    username = user_doc.get('username')
                    uname_str = f" (@{username})" if username else ""
                    send_log(
                        f"User {status_word}\n"
                        f"User   - <b>{name}</b>{uname_str}\n"
                        f"ID     - <code>{uid}</code>\n"
                        f"By     - Admin <code>{chat_id}</code>"
                    )

                    if new_banned:
                        try:
                            send_message(
                                int(uid),
                                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                                f"<b>[ access revoked ]</b>\n\n"
                                f"Your access to this bot has been <b>revoked</b>.\n"
                                f"Contact admin if you believe this is an error."
                            )
                        except Exception:
                            pass
                show_user_profile_admin(chat_id, uid, message_id)
                return

            elif action == 'credits':
                set_session(chat_id, 'awaiting_edit_user_credits', {'target_uid': uid, 'msg_id': message_id})
                back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': f'edit_user_{uid}'}]]}
                edit_message(
                    chat_id, message_id,
                    f"<b>Add/Remove Searches ({uid})</b>\n\n"
                    f"Enter the number of credits to add/remove:\n"
                    f"Example: <code>7</code> to add 7 searches.\n"
                    f"Example: <code>-7</code> to remove 7 searches.",
                    reply_markup=back_kb
                )
                return

            elif action == 'unlimited':
                set_session(chat_id, 'awaiting_edit_user_unlimited', {'target_uid': uid, 'msg_id': message_id})
                back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': f'edit_user_{uid}'}]]}
                edit_message(
                    chat_id, message_id,
                    f"<b>Set Unlimited ({uid})</b>\n\n"
                    f"Enter value:\n"
                    f"<code>0</code> to set unlimited (Lifetime).\n"
                    f"<code>-0</code> to remove unlimited.",
                    reply_markup=back_kb
                )
                return

    if data == 'panel_broadcast':
        if chat_id not in OWNER_IDS:
            return
        set_session(chat_id, 'awaiting_broadcast_target_choice', {})
        target_kb = {
            'inline_keyboard': [
                [{'text': 'All Users', 'callback_data': 'broadcast_select_all'}],
                [{'text': 'Premium Users', 'callback_data': 'broadcast_select_premium'}],
                [{'text': '0 Credit & No Plan Users', 'callback_data': 'broadcast_select_zerocr'}],
                [{'text': 'Single User', 'callback_data': 'broadcast_select_single'}],
                [{'text': 'Back to Panel', 'callback_data': 'panel_back'}]
            ]
        }
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ Send Broadcast To ]</b>\n\n"
            f"Choose broadcast target:\n\n"
            f"<b>All Users</b> - Send to everyone in the database\n"
            f"<b>Premium Users</b> - Send to users who bought premium / active plan\n"
            f"<b>0 Credit & No Plan</b> - Send to users with 0 credits & no unlimited plan\n"
            f"<b>Single User</b> - Send to one specific user (by ID or @username)",
            reply_markup=target_kb
        )
        return

    if data == 'broadcast_select_all':
        if chat_id not in OWNER_IDS:
            return
        set_session(chat_id, 'awaiting_broadcast_msg_all', {})
        back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': 'panel_broadcast'}]]}
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ Broadcast to All Users ]</b>\n\n"
            f"Send the text or photo (with caption) you want to broadcast to ALL users:\n\n"
            f"<i>Type /cancel or tap Back to cancel.</i>",
            reply_markup=back_kb
        )
        return

    if data == 'broadcast_select_premium':
        if chat_id not in OWNER_IDS:
            return
        set_session(chat_id, 'awaiting_broadcast_msg_premium', {})
        back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': 'panel_broadcast'}]]}
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ Broadcast to Premium Users ]</b>\n\n"
            f"Send the text or photo (with caption) you want to broadcast to <b>PREMIUM users</b>:\n\n"
            f"<i>Type /cancel or tap Back to cancel.</i>",
            reply_markup=back_kb
        )
        return

    if data == 'broadcast_select_zerocr':
        if chat_id not in OWNER_IDS:
            return
        set_session(chat_id, 'awaiting_broadcast_msg_zerocr', {})
        back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': 'panel_broadcast'}]]}
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ Broadcast to 0 Credit & No Plan Users ]</b>\n\n"
            f"Send the text or photo (with caption) you want to broadcast to <b>0 CREDIT & NO PLAN users</b>:\n\n"
            f"<i>Type /cancel or tap Back to cancel.</i>",
            reply_markup=back_kb
        )
        return

    if data == 'broadcast_select_single':
        if chat_id not in OWNER_IDS:
            return
        set_session(chat_id, 'awaiting_broadcast_user_id', {})
        back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': 'panel_broadcast'}]]}
        edit_message(
            chat_id, message_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ Single User Broadcast ]</b>\n\n"
            f"Enter the <b>User ID</b> or <b>@username</b> of the target user:\n\n"
            f"<i>Type /cancel or tap Back to cancel.</i>",
            reply_markup=back_kb
        )
        return

    if data == 'confirm_broadcast_all':
        if chat_id not in OWNER_IDS:
            return
        s = get_session(chat_id)
        d = s.get('data', {})
        broadcast_msg_id = d.get('broadcast_msg_id')
        photo_file_id = d.get('photo_file_id')
        text_content = d.get('text_content')

        if not (broadcast_msg_id or photo_file_id or text_content):
            send_message(chat_id, "Session expired. Please try again.")
            clear_session(chat_id)
            return

        clear_session(chat_id)
        status_res = send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Starting Broadcast...</b>\n"
            f"<i>Preparing to send message to all users.</i>"
        )
        status_msg_id = status_res.get('result', {}).get('message_id') if status_res and status_res.get('ok') else None

        t = threading.Thread(
            target=run_background_broadcast,
            args=(chat_id, status_msg_id, broadcast_msg_id, text_content, photo_file_id, 'all'),
            daemon=True
        )
        t.start()
        return

    if data == 'confirm_broadcast_premium':
        if chat_id not in OWNER_IDS:
            return
        s = get_session(chat_id)
        d = s.get('data', {})
        broadcast_msg_id = d.get('broadcast_msg_id')
        photo_file_id = d.get('photo_file_id')
        text_content = d.get('text_content')

        if not (broadcast_msg_id or photo_file_id or text_content):
            send_message(chat_id, "Session expired. Please try again.")
            clear_session(chat_id)
            return

        clear_session(chat_id)
        status_res = send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Starting Premium Broadcast...</b>\n"
            f"<i>Preparing to send message to premium users.</i>"
        )
        status_msg_id = status_res.get('result', {}).get('message_id') if status_res and status_res.get('ok') else None

        t = threading.Thread(
            target=run_background_broadcast,
            args=(chat_id, status_msg_id, broadcast_msg_id, text_content, photo_file_id, 'premium'),
            daemon=True
        )
        t.start()
        return

    if data == 'confirm_broadcast_zerocr':
        if chat_id not in OWNER_IDS:
            return
        s = get_session(chat_id)
        d = s.get('data', {})
        broadcast_msg_id = d.get('broadcast_msg_id')
        photo_file_id = d.get('photo_file_id')
        text_content = d.get('text_content')

        if not (broadcast_msg_id or photo_file_id or text_content):
            send_message(chat_id, "Session expired. Please try again.")
            clear_session(chat_id)
            return

        clear_session(chat_id)
        status_res = send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>Starting 0 Credit Broadcast...</b>\n"
            f"<i>Preparing to send message to 0 credit & no plan users.</i>"
        )
        status_msg_id = status_res.get('result', {}).get('message_id') if status_res and status_res.get('ok') else None

        t = threading.Thread(
            target=run_background_broadcast,
            args=(chat_id, status_msg_id, broadcast_msg_id, text_content, photo_file_id, 'zerocr'),
            daemon=True
        )
        t.start()
        return

    if data == 'confirm_broadcast_single':
        if chat_id not in OWNER_IDS:
            return
        s = get_session(chat_id)
        d = s.get('data', {})
        target_uid = d.get('target_uid')
        target_name = d.get('target_name')
        target_uname_str = d.get('target_uname_str')
        broadcast_msg_id = d.get('broadcast_msg_id')
        photo_file_id = d.get('photo_file_id')
        text_content = d.get('text_content')

        if not target_uid or not (broadcast_msg_id or photo_file_id or text_content):
            send_message(chat_id, "Session expired. Please try again.")
            clear_session(chat_id)
            return

        try:
            res_ok = send_multibot_broadcast_message(
                int(target_uid), chat_id,
                broadcast_msg_id=broadcast_msg_id,
                photo_file_id=photo_file_id,
                message_text=text_content
            )

            if res_ok:
                send_message(
                    chat_id,
                    f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                    f"<b>Message Delivered</b>\n\n"
                    f"User   - <b>{target_name}</b>{target_uname_str}\n"
                    f"ID     - <code>{target_uid}</code>\n"
                    f"Status - Sent OK"
                )
                msg_preview = html.escape(text_content) if text_content else "[Photo/Media Message]"
                send_log(
                    f"Single Broadcast Sent\n"
                    f"To     - <b>{target_name}</b>{target_uname_str}\n"
                    f"ID     - <code>{target_uid}</code>\n"
                    f"Msg    - <blockquote>{msg_preview}</blockquote>\n"
                    f"By     - Admin <code>{chat_id}</code>"
                )
            else:
                send_message(
                    chat_id,
                    f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                    f"<b>Failed to deliver message</b>\n\n"
                    f"User   - <b>{target_name}</b>{target_uname_str}\n"
                    f"ID     - <code>{target_uid}</code>\n"
                    f"Reason - User may have blocked the bot."
                )
        except Exception as e:
            send_message(chat_id, f"Error sending to user <code>{target_uid}</code>: {e}")

        clear_session(chat_id)
        return

    if data == 'awaiting_broadcast_target_user_back':
        if chat_id not in OWNER_IDS:
            return
        s = get_session(chat_id)
        d = s.get('data', {})
        set_session(chat_id, 'awaiting_broadcast_msg_single', d)
        back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': 'broadcast_select_single'}]]}
        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ Send to User ]</b>\n\n"
            f"Target: <b>{d.get('target_name')}</b>{d.get('target_uname_str')} (<code>{d.get('target_uid')}</code>)\n\n"
            f"Send the text or photo (with caption) you want to send to this user:",
            reply_markup=back_kb
        )
        return

    if data == 'panel_back':
        if chat_id not in OWNER_IDS:
            return
        clear_session(chat_id)
        text, kb = get_admin_panel_data()
        edit_message(chat_id, message_id, text, reply_markup=kb)
        return

    if data == 'credits':
        show_credits_info(chat_id, message_id)
        return

    if data == 'buy':
        show_buy_menu(chat_id, message_id)
        return

    if data == 'referral':
        show_referral_info(chat_id)
        return

    if data == 'about':
        show_about_bot(chat_id, message_id)
        return

    if data == 'buy_menu_limited':
        track_buy_interest(chat_id)
        kb = {'inline_keyboard': []}
        for k, v in LIMITED_PLANS.items():
            kb['inline_keyboard'].append([{'text': f"{v['name']}  -  {v['price']}", 'callback_data': f'buy_plan_{k}'}])
        kb['inline_keyboard'].append([{'text': 'Custom Plan', 'url': f'https://t.me/{OWNER_USERNAME.replace("@", "")}?text=i%20want%20to%20purchase%20custom%20plan%20in%20%40{get_bot_username()}'}])
        kb['inline_keyboard'].append([{'text': 'Back', 'callback_data': 'buy'}])
        edit_message(chat_id, message_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\n<b>Limited Search Plans</b>", reply_markup=kb)
        return

    if data == 'buy_menu_unlimited':
        track_buy_interest(chat_id)
        kb = {'inline_keyboard': []}
        for k, v in UNLIMITED_PLANS.items():
            kb['inline_keyboard'].append([{'text': f"{v['name']}  -  {v['price']}", 'callback_data': f'buy_plan_{k}'}])
        kb['inline_keyboard'].append([{'text': 'Back', 'callback_data': 'buy'}])
        edit_message(chat_id, message_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\n<b>Unlimited Plans</b>", reply_markup=kb)
        return

    if data.startswith('buy_plan_'):
        plan_id = data.replace('buy_plan_', '')
        plan = LIMITED_PLANS.get(plan_id) or UNLIMITED_PLANS.get(plan_id)
        if not plan:
            return
        track_buy_interest(chat_id, plan_info=plan)

        plan_name = plan['name']
        usd_price = plan['price']

        crypto_message = (
            f"<b>Crypto Payment for: {plan_name}</b>\n\n"
            f"Amount to pay: <code>{usd_price}</code>\n\n"
            "------------------------------\n"
            "Wallet Addresses:\n\n"
            f"USDT (TRC20):\n <code>{WALLET_USDT_TRC20}</code>\n\n"
            f"USDT (BEP20): <code>{WALLET_USDT_BEP20}</code>\n\n"
            f"USDT (ERC20): <code>{WALLET_USDT_ERC20}</code>\n\n"
            f"BTC:\n <code>{WALLET_BTC}</code>\n\n"
            f"ETH (ERC20): <code>{WALLET_ETH_ERC20}</code>\n\n"
            f"LTC:\n <code>{WALLET_LTC}</code>\n"
            "------------------------------\n\n"
            "Instructions:\n"
            "1. Send the exact amount to any address above.\n"
            "2. Take a screenshot of the successful transaction.\n"
            f"3. Send the screenshot and your User ID to {OWNER_USERNAME}\n\n"
            "Your plan will be activated manually by admin."
        )

        back_data = 'buy_menu_limited' if plan_id in LIMITED_PLANS else 'buy_menu_unlimited'
        kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': back_data}]]}
        edit_message(chat_id, message_id, crypto_message, reply_markup=kb)
        return

    if data in ('search_mobile', 'search_aadhaar', 'search_eid', 'search_aadhaar_sms'):
        if MAINTENANCE_MODE and chat_id not in OWNER_IDS:
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Bot Under Maintenance</b>\n\n"
                f"Upgrading systems for a better & smoother experience\n\n"
                f"Please wait for the official announcement on the channel"
            )
            return
        if not channel_gate(chat_id):
            return
        if not credit_gate(chat_id):
            return

    if data == 'search_mobile':
        set_session(chat_id, 'awaiting_mobile', {'mode': 'mobile'})
        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ Mobile Search ]</b>\n\n"
            f"Enter your 10-digit mobile number\n\n"
            f"<i>OTP will be sent to this number</i>",
            reply_markup=get_cancel_keyboard()
        )
    elif data == 'search_aadhaar':
        set_session(chat_id, 'awaiting_aadhaar', {'mode': 'aadhaar'})
        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ Aadhaar Search ]</b>\n\n"
            f"Enter your 12-digit Aadhaar number\n\n"
            f"<i>Spaces are removed automatically</i>",
            reply_markup=get_cancel_keyboard()
        )
    elif data == 'search_eid':
        set_session(chat_id, 'awaiting_eid_input', {'mode': 'eid'})
        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ EID Search ]</b>\n\n"
            f"Enter your Enrollment ID (EID)\n\n"
            f"<i>Format: 1234/56789/12345</i>",
            reply_markup=get_cancel_keyboard()
        )
    elif data == 'search_aadhaar_sms':
        set_session(chat_id, 'awaiting_aadhaar_sms_mobile', {'mode': 'aadhaar_sms'})
        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ Aadhaar SMS Search ]</b>\n\n"
            f"Enter your 10-digit mobile number\n\n"
            f"<i>OTP (Aadhaar Number) will be sent to this number</i>",
            reply_markup=get_cancel_keyboard()
        )


# ============== STATS DASHBOARD ==============
def generate_stats_dashboard():
    now = datetime.now()
    yesterday = now - timedelta(hours=24)

    try:
        query = {"timestamp": {"$gte": yesterday}}
        logs = list(logs_col.find(query))

        solve_captcha_logs = [l for l in logs if l.get("action") == "solve_captcha"]
        retrieve_eid_logs = [l for l in logs if l.get("action") == "retrieve_eid"]
        download_pdf_logs = [l for l in logs if l.get("action") == "download_pdf"]

        eid_success = len([l for l in retrieve_eid_logs if l.get("status") == "success"])
        eid_total = len(retrieve_eid_logs)
        pdf_success = len([l for l in download_pdf_logs if l.get("status") == "success"])
        pdf_total = len(download_pdf_logs)

        active_users = len(set(l.get("chat_id") for l in logs))

        avg_ocr_speed = 0.0
        if solve_captcha_logs:
            avg_ocr_speed = sum(l.get("duration", 0.0) for l in solve_captcha_logs) / len(solve_captcha_logs)

        avg_uidai_latency = 0.0
        all_api_logs = retrieve_eid_logs + download_pdf_logs
        if all_api_logs:
            avg_uidai_latency = sum(l.get("duration", 0.0) for l in all_api_logs) / len(all_api_logs)

        total_searches = eid_total + pdf_total
        overall_success = eid_success + pdf_success
        overall_success_rate = (overall_success / total_searches * 100) if total_searches > 0 else 0.0
    except Exception as e:
        logger.error(f"Error aggregating dashboard stats: {e}")
        total_searches = eid_total = pdf_total = overall_success_rate = avg_ocr_speed = avg_uidai_latency = active_users = 0
        eid_success = pdf_success = 0

    try:
        data = all_users()
        total_db_users = len(data)
        lifetime_count = sum(1 for u in data.values() if u.get('lifetime'))
        total_credits = sum(u.get('credits', 0) for u in data.values() if not u.get('lifetime'))
    except Exception:
        total_db_users = lifetime_count = total_credits = 0

    dashboard = (
        f"<b>{BOT_NAME} Dashboard</b>\n"
        f"{DIVIDER}\n"
        f"<b>[ User Base ]</b>\n"
        f"Total Users       -  <b>{total_db_users}</b>\n"
        f"Lifetime Users    -  <b>{lifetime_count}</b>\n"
        f"Credits in Use    -  <b>{total_credits}</b>\n\n"
        f"<b>[ 24 Hour Metrics ]</b>\n"
        f"Total Searches    -  <b>{total_searches}</b>\n"
        f"EID Retrievals    -  <b>{eid_total}</b> (Success: {eid_success})\n"
        f"PDF Downloads     -  <b>{pdf_total}</b> (Success: {pdf_success})\n"
        f"Overall Success   -  <b>{overall_success_rate:.1f}%</b>\n\n"
        f"<b>[ Performance ]</b>\n"
        f"Avg OCR Speed     -  <b>{avg_ocr_speed:.2f}s</b>\n"
        f"Avg UIDAI Latency -  <b>{avg_uidai_latency:.2f}s</b>\n"
        f"Active Users      -  <b>{active_users}</b>\n"
        f"{DIVIDER}"
    )
    return dashboard


def daily_report_scheduler():
    logger.info("Daily report scheduler thread started.")
    while True:
        try:
            now = datetime.now()
            tomorrow = now.date() + timedelta(days=1)
            next_run = datetime.combine(tomorrow, datetime.min.time().replace(hour=0, minute=0, second=0))
            sleep_sec = (next_run - now).total_seconds()

            logger.info(f"Daily report scheduled in {sleep_sec:.0f} seconds.")

            for _ in range(int(sleep_sec)):
                time.sleep(1)

            dashboard_msg = generate_stats_dashboard()
            send_log(f"DAILY AUTO REPORT\n\n{dashboard_msg}")
        except Exception as e:
            logger.error(f"Error in daily report scheduler: {e}")
            time.sleep(60)


# ============== OWNER COMMANDS ==============
def handle_owner_command(chat_id, text):
    parts = text.strip().split()

    if parts[0] in ['/setpdfcount', '/resetpdfcount']:
        try:
            val = int(parts[1]) if len(parts) > 1 else 0
            settings_col.update_one({"_id": "pdf_log_counter"}, {"$set": {"count": val}}, upsert=True)
            send_message(chat_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\nPDF counter set to: <b>{val}</b>")
        except Exception as e:
            send_message(chat_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\nError setting PDF counter: {e}")
        return True

    if parts[0] == '/send' and len(parts) == 3:
        try:
            target_id = int(parts[1])
            amount = int(parts[2])
            if amount == -1:
                add_credits(target_id, 0, make_lifetime=True)
                send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\n<b>[ done ]</b>\n\nGranted Lifetime to <code>{target_id}</code>")
                send_message(target_id,
                    f"{BOT_NAME}\n{DIVIDER}\n"
                    f"<b>[ credits received ]</b>\n\n"
                    f"Plan     -  Lifetime\n"
                    f"Status   -  Active\n\n"
                    f"{DIVIDER}",
                    reply_markup=get_main_keyboard()
                )
            else:
                add_credits(target_id, amount)
                send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\n<b>[ done ]</b>\n\nSent {amount} credits to <code>{target_id}</code>")
                send_message(target_id,
                    f"{BOT_NAME}\n{DIVIDER}\n"
                    f"<b>[ credits received ]</b>\n\n"
                    f"Credits  -  +{amount}\n"
                    f"Balance  -  {int(get_credits(target_id))}\n\n"
                    f"{DIVIDER}",
                    reply_markup=get_main_keyboard()
                )
        except ValueError:
            send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\nUsage: /send USERID AMOUNT\n(-1 for lifetime)")
        return True

    if parts[0] == '/stats':
        dashboard_msg = generate_stats_dashboard()
        send_message(chat_id, dashboard_msg)
        return True

    if parts[0] == '/balance' and len(parts) == 2:
        try:
            uid = int(parts[1])
            cr = get_credits(uid)
            cr_display = "Lifetime" if cr == float('inf') else str(int(cr))
            send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\n<b>[ balance ]</b>\n\nUser    -  <code>{uid}</code>\nCredits -  {cr_display}\n\n{DIVIDER}")
        except ValueError:
            send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\nUsage: /balance USERID")
        return True

    if parts[0] == '/panel':
        text, kb = get_admin_panel_data()
        send_message(chat_id, text, reply_markup=kb)
        return True

    if parts[0] == '/key':
        try:
            amount = int(parts[1]) if len(parts) >= 2 else 1
        except ValueError:
            amount = 1
        set_session(chat_id, 'key_type', {'key_amount': amount})
        type_kb = {
            'inline_keyboard': [
                [{'text': 'Limited (Credits)', 'callback_data': f'key_limited_{amount}'}],
                [{'text': 'Unlimited (Lifetime)', 'callback_data': f'key_unlimited_{amount}'}]
            ]
        }
        send_message(
            chat_id,
            f"{BOT_NAME}\n{DIVIDER}\n"
            f"<b>[ generate key ]</b>\n\n"
            f"Amount - {amount} key(s)\n\n"
            f"Select key type:",
            reply_markup=type_kb
        )
        return True

    if parts[0] == '/broadcast':
        msg_text = text[10:].strip()
        if msg_text:
            status_res = send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Starting Broadcast...</b>\n"
                f"<i>Preparing to send message to all users.</i>"
            )
            status_msg_id = status_res.get('result', {}).get('message_id') if status_res and status_res.get('ok') else None
            t = threading.Thread(
                target=run_background_broadcast,
                args=(chat_id, status_msg_id, None, msg_text, None),
                daemon=True
            )
            t.start()
        else:
            set_session(chat_id, 'awaiting_broadcast_target_choice', {})
            target_kb = {
                'inline_keyboard': [
                    [{'text': 'All Users', 'callback_data': 'broadcast_select_all'}],
                    [{'text': 'Premium Users', 'callback_data': 'broadcast_select_premium'}],
                    [{'text': '0 Credit & No Plan Users', 'callback_data': 'broadcast_select_zerocr'}],
                    [{'text': 'Single User', 'callback_data': 'broadcast_select_single'}],
                    [{'text': 'Back to Panel', 'callback_data': 'panel_back'}]
                ]
            }
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>[ Send Broadcast To ]</b>\n\n"
                f"Choose broadcast target:\n\n"
                f"<b>All Users</b> - Send to everyone in the database\n"
                f"<b>Premium Users</b> - Send to users who bought premium / active plan\n"
                f"<b>0 Credit & No Plan</b> - Send to users with 0 credits & no unlimited plan\n"
                f"<b>Single User</b> - Send to one specific user (by ID or @username)",
                reply_markup=target_kb
            )
        return True

    if parts[0] == '/rm':
        banned_users = list(users_col.find({"banned": True}))
        total_banned = len(banned_users)

        header_lines = [
            "REVOKED / BANNED USERS",
            "------------------------------",
            f"Total Banned: {total_banned}",
            "------------------------------\n"
        ]

        user_blocks = []
        for idx, u in enumerate(banned_users, 1):
            raw_name = u.get('first_name', 'Unknown') or 'Unknown'
            name = html.escape(str(raw_name))
            username = u.get('username')
            username_str = f"@{html.escape(username)}" if username else "No Username"
            uid = u.get('_id')
            user_blocks.append(f"{idx}. {name} | {username_str}\n    ID: <code>{uid}</code>\n")

        chunks = []
        current_chunk = "\n".join(header_lines)
        if not user_blocks:
            chunks.append(current_chunk)
        else:
            for block in user_blocks:
                if len(current_chunk) + len(block) + 1 > 3800:
                    chunks.append(current_chunk)
                    current_chunk = block
                else:
                    if current_chunk:
                        current_chunk += "\n" + block
                    else:
                        current_chunk = block
            if current_chunk:
                chunks.append(current_chunk)

        for chunk in chunks:
            send_message(chat_id, chunk)
        return True

    if parts[0] == '/pr':
        now = datetime.now()
        now_iso = now.isoformat()

        all_users_list = list(users_col.find({
            "banned": {"$ne": True},
            "$or": [
                {"lifetime": True},
                {"expiry": {"$gt": now_iso}},
                {"is_premium": True},
                {"credits": {"$gt": 0}},
                {"granted_credits": {"$gt": 0}}
            ]
        }))

        lifetime_users_list = []
        timed_users_list = []
        credits_users_list = []

        for u in all_users_list:
            if u.get('lifetime'):
                lifetime_users_list.append(u)
                continue

            is_from_free = u.get('from_free_key', False)
            is_paid = u.get('paid_user', False)
            granted_cr = int(u.get('granted_credits') or u.get('initial_credits') or u.get('total_credits') or 0)

            expiry_str = u.get('expiry')
            has_valid_expiry = False
            if expiry_str:
                try:
                    expiry_dt = datetime.fromisoformat(expiry_str)
                    if expiry_dt > now:
                        has_valid_expiry = True
                except Exception:
                    pass

            if has_valid_expiry:
                if is_from_free and not is_paid and granted_cr <= 0:
                    continue
                timed_users_list.append(u)
                continue

            cr = int(u.get('credits', 0))
            if cr > 0:
                raw_granted = u.get('granted_credits') or u.get('initial_credits') or u.get('total_credits')
                if raw_granted is not None and int(raw_granted) > 0:
                    granted_cr = int(raw_granted)
                else:
                    granted_cr = cr

                if is_from_free and not is_paid and granted_cr <= 0:
                    continue
                if granted_cr < 10 and not is_paid and not u.get('is_premium'):
                    continue
                if granted_cr >= 10 or is_paid or (u.get('is_premium') and not is_from_free):
                    credits_users_list.append(u)

        def _timed_sort_key(u):
            try:
                return -datetime.fromisoformat(u.get('expiry')).timestamp()
            except Exception:
                return 0
        timed_users_list.sort(key=_timed_sort_key)
        credits_users_list.sort(key=lambda u: -int(u.get('credits', 0)))

        total_lifetime = len(lifetime_users_list)
        total_timed = len(timed_users_list)
        total_credits = len(credits_users_list)
        total_premium = total_lifetime + total_timed + total_credits

        header_lines = [
            f"Active Premium Users: {total_premium}",
            "------------------------------",
            f"Lifetime: {total_lifetime} | Timed: {total_timed} | Credits: {total_credits}",
            "------------------------------\n"
        ]

        user_blocks = []
        item_index = 1

        for u in lifetime_users_list:
            raw_name = u.get('first_name', 'Unknown') or 'Unknown'
            name = html.escape(str(raw_name))
            username = u.get('username')
            username_str = f" (@{html.escape(username)})" if username else ""
            uid = u.get('_id')
            plan_str = html.escape(str(format_plan_display(u)))

            user_blocks.append(
                f"[L] {item_index}. <b>{name}</b>{username_str}\n"
                f"    ID: <code>{uid}</code>\n"
                f"    Plan: {plan_str}\n"
                f"    Lifetime\n"
            )
            item_index += 1

        for u in timed_users_list:
            raw_name = u.get('first_name', 'Unknown') or 'Unknown'
            name = html.escape(str(raw_name))
            username = u.get('username')
            username_str = f" (@{html.escape(username)})" if username else ""
            uid = u.get('_id')

            expiry_dt = datetime.fromisoformat(u.get('expiry'))
            sec_left = (expiry_dt - now).total_seconds()
            days_left = int(sec_left // 86400)

            if days_left >= 1:
                time_left_str = f"{days_left}d left"
            else:
                hours_left = int(sec_left // 3600)
                if hours_left >= 1:
                    time_left_str = f"{hours_left}h left"
                else:
                    mins_left = max(1, int(sec_left // 60))
                    time_left_str = f"{mins_left}m left"

            plan_str = html.escape(str(format_plan_display(u, days_left)))
            icon = "[!]" if sec_left < 86400 else "[U]"
            date_str = expiry_dt.strftime("%d-%b-%Y at %I:%M %p")

            user_blocks.append(
                f"{icon} {item_index}. <b>{name}</b>{username_str}\n"
                f"    ID: <code>{uid}</code>\n"
                f"    Plan: {plan_str}\n"
                f"    {date_str} ({time_left_str})\n"
            )
            item_index += 1

        for u in credits_users_list:
            raw_name = u.get('first_name', 'Unknown') or 'Unknown'
            name = html.escape(str(raw_name))
            username = u.get('username')
            username_str = f" (@{html.escape(username)})" if username else ""
            uid = u.get('_id')

            cr = int(u.get('credits', 0))
            raw_granted = u.get('granted_credits') or u.get('initial_credits') or u.get('total_credits')
            if raw_granted is not None and int(raw_granted) > 0:
                granted_cr = int(raw_granted)
            else:
                granted_cr = cr

            user_blocks.append(
                f"[C] {item_index}. <b>{name}</b>{username_str}\n"
                f"    ID: <code>{uid}</code>\n"
                f"    Plan: {granted_cr} Credits\n"
                f"    {cr} Credits left\n"
            )
            item_index += 1

        chunks = []
        current_chunk = "\n".join(header_lines)
        if not user_blocks:
            chunks.append(current_chunk)
        else:
            for block in user_blocks:
                if len(current_chunk) + len(block) + 1 > 3800:
                    chunks.append(current_chunk)
                    current_chunk = block
                else:
                    if current_chunk:
                        current_chunk += "\n" + block
                    else:
                        current_chunk = block
            if current_chunk:
                chunks.append(current_chunk)

        for chunk in chunks:
            send_message(chat_id, chunk)
        return True

    return False


# ============== MESSAGE HANDLER ==============
_KB_ACTIONS = {
    'mobile number': 'search_mobile',
    'aadhaar number': 'search_aadhaar',
    'eid': 'search_eid',
    'aadhaar sms': 'search_aadhaar_sms',
    'credits': 'credits',
    'buy credits': 'buy',
    'referral': 'referral',
    'about bot': 'about',
}

user_request_history = {}
request_history_lock = threading.Lock()


def handle_message(chat_id, msg):
    message_text = msg.get('text', msg.get('caption', '')).strip()

    s = get_session(chat_id)
    referrer_id = s.get('data', {}).get('referrer_id')
    _from = msg.get('from', {})
    ensure_user(
        chat_id,
        referrer_id=referrer_id,
        first_name=_from.get('first_name'),
        username=_from.get('username')
    )
    check_and_notify_expiry(chat_id)
    tag = get_user_log_tag(chat_id)
    s = get_session(chat_id)
    current_step = s.get('step', 'main')
    logger.info(f"Msg: '{message_text[:60]}' | Step: {current_step} {tag}")

    if chat_id not in OWNER_IDS:
        u = get_user(chat_id)
        if u and u.get('banned'):
            send_message(
                chat_id,
                f"{BOT_NAME}\n{DIVIDER}\n"
                f"<b>[ access revoked ]</b>\n\n"
                f"Your access to this bot has been <b>revoked</b>.\n"
                f"Contact admin if you believe this is an error."
            )
            return

    if chat_id in OWNER_IDS and message_text.startswith('/'):
        if handle_owner_command(chat_id, message_text):
            return

    if message_text.startswith('/redeem'):
        parts = message_text.split()
        if len(parts) == 2:
            key_code = parts[1].strip().upper()
            key_doc = keys_collection.find_one({"_id": key_code})
            if key_doc:
                if key_doc.get("used"):
                    send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\nInvalid or already used key.")
                    return

                batch_id = key_doc.get("batch_id")
                batch_amount = key_doc.get("batch_amount", 1)
                is_free_key = key_doc.get("is_free", False) or (batch_amount > 1)

                if batch_id and batch_amount > 1:
                    already_redeemed = keys_collection.find_one({
                        "batch_id": batch_id,
                        "used_by": chat_id
                    })
                    if already_redeemed:
                        send_message(
                            chat_id,
                            f"{BOT_NAME}\n{DIVIDER}\n"
                            f"<b>[ giveaway limit ]</b>\n\n"
                            f"Aap is giveaway batch me se pehle hi 1 code redeem kar chuke hain!\n"
                            f"<i>(1 giveaway batch me se 1 user sirf 1 code redeem kar sakta hai)</i>"
                        )
                        return

                keys_collection.update_one({"_id": key_code}, {"$set": {"used": True, "used_by": chat_id, "used_at": datetime.now().isoformat()}})
                cr_val = key_doc.get("credits", 0)
                u = get_user(chat_id)
                uname_str = f" (@{u['username']})" if u and u.get('username') else ""
                uname_disp = (u.get('first_name', 'Unknown') if u else 'Unknown') + uname_str

                if cr_val == -1:
                    days = key_doc.get("days", 0)
                    if days > 0:
                        new_expiry = (datetime.now() + timedelta(days=days)).isoformat()
                        upd_set = {"expiry": new_expiry, "is_premium": True, "unlimited_days": days}
                        if is_free_key:
                            upd_set["from_free_key"] = True
                        else:
                            upd_set["paid_user"] = True
                        users_col.update_one({"_id": str(chat_id)}, {"$set": upd_set, "$unset": {"expiry_notified": "", "expiry_warning_notified": ""}})
                        invalidate_cached_user(str(chat_id))
                        send_message(chat_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\n<b>[ key redeemed ]</b>\n\nUnlimited access for {days} days activated!")
                        send_log(f"Key Redeemed\nUser   - {uname_disp}\nID     - <code>{chat_id}</code>\nCode   - <code>{key_code}</code>\nType   - Unlimited {days} Days")
                    else:
                        add_credits(chat_id, 0, make_lifetime=True)
                        send_message(chat_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\n<b>[ key redeemed ]</b>\n\nLifetime access activated!")
                        send_log(f"Key Redeemed\nUser   - {uname_disp}\nID     - <code>{chat_id}</code>\nCode   - <code>{key_code}</code>\nType   - Lifetime")
                else:
                    if is_free_key:
                        users_col.update_one({"_id": str(chat_id)}, {"$inc": {"credits": cr_val, "free_credits": cr_val}, "$set": {"is_premium": True, "from_free_key": True}})
                        invalidate_cached_user(str(chat_id))
                    else:
                        add_credits(chat_id, cr_val)
                    send_message(chat_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\n<b>[ key redeemed ]</b>\n\n+{cr_val} credits added to your account.")
                    send_log(f"Key Redeemed\nUser   - {uname_disp}\nID     - <code>{chat_id}</code>\nCode   - <code>{key_code}</code>\nType   - {cr_val} Credits")
            else:
                send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\nInvalid or already used key.")
        else:
            send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\nUsage: /redeem KEY")
        return

    if message_text.startswith('/buy'):
        show_buy_menu(chat_id)
        return

    if message_text.startswith('/referral'):
        show_referral_info(chat_id)
        return

    action = _KB_ACTIONS.get(message_text.strip().lower())
    if action:
        if action in ('search_mobile', 'search_aadhaar', 'search_eid', 'search_aadhaar_sms'):
            if MAINTENANCE_MODE and chat_id not in OWNER_IDS:
                send_message(
                    chat_id,
                    f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                    f"<b>Bot Under Maintenance</b>\n\n"
                    f"Upgrading systems for a better & smoother experience\n\n"
                    f"Please wait for the official announcement on the channel"
                )
                return
            if not channel_gate(chat_id):
                return
            if not credit_gate(chat_id):
                return
            clear_session(chat_id)
            if action == 'search_mobile':
                set_session(chat_id, 'awaiting_mobile', {'mode': 'mobile'})
                prefetch_captcha_async(chat_id, revamp=True)
                send_message(
                    chat_id,
                    f"{BOT_NAME}\n{DIVIDER}\n<b>[ mobile search ]</b>\n\nEnter your 10-digit mobile number",
                    reply_markup=get_cancel_keyboard()
                )
            elif action == 'search_aadhaar':
                set_session(chat_id, 'awaiting_aadhaar', {'mode': 'aadhaar'})
                prefetch_captcha_async(chat_id, revamp=False)
                send_message(
                    chat_id,
                    f"{BOT_NAME}\n{DIVIDER}\n<b>[ aadhaar search ]</b>\n\nEnter your 12-digit Aadhaar number",
                    reply_markup=get_cancel_keyboard()
                )
            elif action == 'search_eid':
                set_session(chat_id, 'awaiting_eid_input', {'mode': 'eid'})
                prefetch_captcha_async(chat_id, revamp=False)
                send_message(
                    chat_id,
                    f"{BOT_NAME}\n{DIVIDER}\n<b>[ EID search ]</b>\n\nEnter your Enrollment ID (EID)",
                    reply_markup=get_cancel_keyboard()
                )
            elif action == 'search_aadhaar_sms':
                set_session(chat_id, 'awaiting_aadhaar_sms_mobile', {'mode': 'aadhaar_sms'})
                prefetch_captcha_async(chat_id, revamp=True)
                send_message(
                    chat_id,
                    f"{BOT_NAME}\n{DIVIDER}\n<b>[ Aadhaar SMS Search ]</b>\n\nEnter your 10-digit mobile number",
                    reply_markup=get_cancel_keyboard()
                )
        elif action == 'credits':
            show_credits_info(chat_id)
        elif action == 'buy':
            show_buy_menu(chat_id)
        elif action == 'referral':
            show_referral_info(chat_id)
        elif action == 'about':
            show_about_bot(chat_id)
        return

    s = get_session(chat_id)
    current_step = s.get('step', 'main')
    d = s.get('data', {})

    if current_step != 'main':
        idle = time.time() - s.get('last_activity', time.time())
        if idle > SESSION_TIMEOUT:
            clear_session(chat_id)
            return

    touch_session(chat_id)

    if message_text.lower() in ['/cancel', 'cancel', '/stop', 'stop']:
        clear_session(chat_id)
        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<i>Session cancelled.</i>"
        )
        return

    if current_step in ('awaiting_otp_retry', 'awaiting_pdf_otp_retry', 'awaiting_pdf_otp_direct_retry', 'awaiting_eid_name_choice', 'awaiting_aadhaar_sms_name_choice'):
        return

    if current_step == 'main':
        return

    if current_step == 'awaiting_revoke_id':
        if chat_id not in OWNER_IDS:
            clear_session(chat_id)
            return
        target_id_str = message_text.strip()
        if target_id_str.isdigit():
            target_id = target_id_str
            u = users_col.find_one({"_id": target_id})
            if u:
                users_col.update_one(
                    {"_id": target_id},
                    {"$set": {"credits": 0, "lifetime": False, "banned": True}}
                )
                clear_session(chat_id)
                name = u.get('first_name', 'Unknown')
                uname = f" (@{u['username']}" + ")" if u.get('username') else ""
                back_kb = {'inline_keyboard': [[{'text': 'Back to Panel', 'callback_data': 'panel_back'}]]}
                send_message(
                    chat_id,
                    f"{BOT_NAME}\n{DIVIDER}\n"
                    f"<b>[ access revoked ]</b>\n\n"
                    f"User   - <b>{name}</b>{uname}\n"
                    f"ID     - <code>{target_id}</code>\n"
                    f"Status - Banned\n\n"
                    f"{DIVIDER}",
                    reply_markup=back_kb
                )
                try:
                    send_message(
                        int(target_id),
                        f"{BOT_NAME}\n{DIVIDER}\n"
                        f"<b>[ access revoked ]</b>\n\n"
                        f"Your access to this bot has been <b>revoked</b>.\n"
                        f"Contact admin if you believe this is an error."
                    )
                except Exception:
                    pass

                send_log(
                    f"User Revoked\n"
                    f"User   - <b>{name}</b>{uname}\n"
                    f"ID     - <code>{target_id}</code>\n"
                    f"By     - Admin <code>{chat_id}</code>"
                )
            else:
                send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\nUser ID <code>{target_id_str}</code> not found in database.")
        else:
            send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\nInvalid ID. Enter a numeric User ID.")
        return

    if current_step == 'awaiting_broadcast_target_choice':
        return

    if current_step == 'awaiting_broadcast_user_id':
        if chat_id not in OWNER_IDS:
            clear_session(chat_id)
            return

        query = message_text.strip()
        target_user_doc = None

        if query.lstrip('@').isdigit() or query.isdigit():
            uid_str = query.lstrip('@')
            target_user_doc = users_col.find_one({"_id": uid_str})

        if not target_user_doc:
            clean_uname = query.replace('@', '').strip()
            target_user_doc = users_col.find_one({"username": {"$regex": f"^{clean_uname}$", "$options": "i"}})

        if not target_user_doc:
            send_message(
                chat_id,
                f"{BOT_NAME}\n{DIVIDER}\n"
                f"User not found: <code>{query}</code>\n\n"
                f"<i>Enter a valid User ID or @username.</i>"
            )
            return

        target_uid = target_user_doc.get('_id')
        target_name = target_user_doc.get('first_name', 'Unknown')
        target_uname = target_user_doc.get('username')
        target_uname_str = f" (@{target_uname})" if target_uname else ""

        set_session(chat_id, 'awaiting_broadcast_msg_single', {
            'target_uid': target_uid,
            'target_name': target_name,
            'target_uname_str': target_uname_str
        })

        back_kb = {'inline_keyboard': [[{'text': 'Back', 'callback_data': 'broadcast_select_single'}]]}
        send_message(
            chat_id,
            f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
            f"<b>[ Send to User ]</b>\n\n"
            f"Target: <b>{target_name}</b>{target_uname_str} (<code>{target_uid}</code>)\n\n"
            f"Send the text or photo (with caption) you want to send to this user:",
            reply_markup=back_kb
        )
        return

    if current_step == 'awaiting_broadcast_msg_all':
        if chat_id not in OWNER_IDS:
            clear_session(chat_id)
            return

        broadcast_msg_id = msg.get('message_id')
        photo = msg.get('photo')
        photo_file_id = photo[-1]['file_id'] if photo else None
        text_content = msg.get('text', msg.get('caption', '')).strip()

        set_session(chat_id, 'awaiting_broadcast_confirm_all', {
            'broadcast_msg_id': broadcast_msg_id,
            'photo_file_id': photo_file_id,
            'text_content': text_content
        })

        confirm_kb = {
            'inline_keyboard': [
                [{'text': 'Send to All', 'callback_data': 'confirm_broadcast_all'}],
                [{'text': 'Edit Message (Back)', 'callback_data': 'broadcast_select_all'}]
            ]
        }

        send_message(chat_id, f"<b>Broadcast Preview:</b>\n{DIVIDER}")
        if photo_file_id:
            send_photo(chat_id, photo_file_id, caption=text_content)
        else:
            send_message(chat_id, text_content)

        send_message(
            chat_id,
            f"{DIVIDER}\n"
            f"<b>Do you want to send this broadcast to all users?</b>",
            reply_markup=confirm_kb
        )
        return

    if current_step == 'awaiting_broadcast_msg_premium':
        if chat_id not in OWNER_IDS:
            clear_session(chat_id)
            return

        broadcast_msg_id = msg.get('message_id')
        photo = msg.get('photo')
        photo_file_id = photo[-1]['file_id'] if photo else None
        text_content = msg.get('text', msg.get('caption', '')).strip()

        set_session(chat_id, 'awaiting_broadcast_confirm_premium', {
            'broadcast_msg_id': broadcast_msg_id,
            'photo_file_id': photo_file_id,
            'text_content': text_content
        })

        confirm_kb = {
            'inline_keyboard': [
                [{'text': 'Send to Premium Users', 'callback_data': 'confirm_broadcast_premium'}],
                [{'text': 'Edit Message (Back)', 'callback_data': 'broadcast_select_premium'}]
            ]
        }

        send_message(chat_id, f"<b>Broadcast Preview (Premium Users):</b>\n{DIVIDER}")
        if photo_file_id:
            send_photo(chat_id, photo_file_id, caption=text_content)
        else:
            send_message(chat_id, text_content)

        send_message(
            chat_id,
            f"{DIVIDER}\n"
            f"<b>Do you want to send this broadcast to all PREMIUM users?</b>",
            reply_markup=confirm_kb
        )
        return

    if current_step == 'awaiting_broadcast_msg_zerocr':
        if chat_id not in OWNER_IDS:
            clear_session(chat_id)
            return

        broadcast_msg_id = msg.get('message_id')
        photo = msg.get('photo')
        photo_file_id = photo[-1]['file_id'] if photo else None
        text_content = msg.get('text', msg.get('caption', '')).strip()

        set_session(chat_id, 'awaiting_broadcast_confirm_zerocr', {
            'broadcast_msg_id': broadcast_msg_id,
            'photo_file_id': photo_file_id,
            'text_content': text_content
        })

        confirm_kb = {
            'inline_keyboard': [
                [{'text': 'Send to 0 Credit Users', 'callback_data': 'confirm_broadcast_zerocr'}],
                [{'text': 'Edit Message (Back)', 'callback_data': 'broadcast_select_zerocr'}]
            ]
        }

        send_message(chat_id, f"<b>Broadcast Preview (0 Credit & No Plan):</b>\n{DIVIDER}")
        if photo_file_id:
            send_photo(chat_id, photo_file_id, caption=text_content)
        else:
            send_message(chat_id, text_content)

        send_message(
            chat_id,
            f"{DIVIDER}\n"
            f"<b>Do you want to send this broadcast to all 0 CREDIT & NO PLAN users?</b>",
            reply_markup=confirm_kb
        )
        return

    if current_step == 'awaiting_broadcast_msg_single':
        if chat_id not in OWNER_IDS:
            clear_session(chat_id)
            return

        broadcast_msg_id = msg.get('message_id')
        photo = msg.get('photo')
        photo_file_id = photo[-1]['file_id'] if photo else None
        text_content = msg.get('text', msg.get('caption', '')).strip()

        set_session(chat_id, 'awaiting_broadcast_confirm_single', {
            'target_uid': d.get('target_uid'),
            'target_name': d.get('target_name'),
            'target_uname_str': d.get('target_uname_str'),
            'broadcast_msg_id': broadcast_msg_id,
            'photo_file_id': photo_file_id,
            'text_content': text_content
        })

        confirm_kb = {
            'inline_keyboard': [
                [{'text': f"Send to {d.get('target_name')}", 'callback_data': 'confirm_broadcast_single'}],
                [{'text': 'Edit Message (Back)', 'callback_data': 'awaiting_broadcast_target_user_back'}]
            ]
        }

        send_message(chat_id, f"<b>Message Preview:</b>\n{DIVIDER}")
        if photo_file_id:
            send_photo(chat_id, photo_file_id, caption=text_content)
        else:
            send_message(chat_id, text_content)

        send_message(
            chat_id,
            f"{DIVIDER}\n"
            f"<b>Do you want to send this message to {d.get('target_name')}?</b>",
            reply_markup=confirm_kb
        )
        return

    if current_step == 'awaiting_key_credits':
        try:
            credits_val = int(message_text.strip())
            amount = d.get('key_amount', 1)
            batch_id = f"batch_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"
            keys_list = []
            for _ in range(amount):
                key_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
                keys_list.append(key_code)
                keys_collection.insert_one({
                    "_id": key_code,
                    "credits": credits_val,
                    "used": False,
                    "created_by": chat_id,
                    "created_at": datetime.now().isoformat(),
                    "batch_id": batch_id,
                    "batch_amount": amount,
                    "is_free": (amount > 1)
                })
            keys_str = "\n".join([f"<code>{k}</code>" for k in keys_list])
            clear_session(chat_id)
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n<b>[ limited keys generated ]</b>\n\n"
                f"Amount  - {amount}\n"
                f"Credits - {credits_val} each\n\n"
                f"{keys_str}\n\n{DIVIDER}"
            )
        except ValueError:
            send_message(chat_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\nEnter a valid number of credits (e.g. 10)")
        return

    if current_step == 'awaiting_key_days':
        try:
            days_val = int(message_text.strip())
            amount = d.get('key_amount', 1)
            batch_id = f"batch_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"
            keys_list = []
            for _ in range(amount):
                key_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
                keys_list.append(key_code)
                keys_collection.insert_one({
                    "_id": key_code,
                    "credits": -1,
                    "days": days_val,
                    "used": False,
                    "created_by": chat_id,
                    "created_at": datetime.now().isoformat(),
                    "batch_id": batch_id,
                    "batch_amount": amount,
                    "is_free": (amount > 1)
                })
            keys_str = "\n".join([f"<code>{k}</code>" for k in keys_list])
            clear_session(chat_id)
            type_str = f"{days_val} Days" if days_val > 0 else "Lifetime"
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n<b>[ unlimited keys generated ]</b>\n\n"
                f"Amount - {amount}\n"
                f"Type   - Unlimited ({type_str})\n\n"
                f"{keys_str}\n\n{DIVIDER}"
            )
        except ValueError:
            send_message(chat_id, f"<b>{BOT_NAME}</b>\n{DIVIDER}\nEnter a valid number of days (e.g. 1, 7, 30, or 0)")
        return

    if current_step == 'awaiting_search_user':
        if chat_id not in OWNER_IDS:
            clear_session(chat_id)
            return

        query = message_text.strip()
        user_doc = None

        if query.isdigit():
            user_doc = get_user(query)

        if not user_doc:
            clean_username = query.replace('@', '').strip()
            user_doc = users_col.find_one({"username": {"$regex": f"^{clean_username}$", "$options": "i"}})

        if user_doc:
            uid = user_doc.get('_id')
            show_user_profile_admin(chat_id, uid)
            clear_session(chat_id)
        else:
            send_message(chat_id, f"{BOT_NAME}\n{DIVIDER}\nUser not found. Please try again with User ID or Username.")
        return

    if current_step == 'awaiting_edit_user_credits':
        if chat_id not in OWNER_IDS:
            clear_session(chat_id)
            return

        target_uid = d.get('target_uid')
        msg_id = d.get('msg_id')

        try:
            amount = int(message_text.strip())
            user_doc = users_col.find_one({"_id": target_uid})
            if user_doc:
                current_credits = user_doc.get('credits', 0)
                new_credits = max(0, current_credits + amount)
                users_col.update_one({"_id": target_uid}, {"$set": {"credits": new_credits, "is_premium": (new_credits > 0)}})
                invalidate_cached_user(target_uid)

                change_word = f"+{amount}" if amount >= 0 else f"{amount}"
                name = user_doc.get('first_name', 'Unknown')
                username = user_doc.get('username')
                uname_str = f" (@{username})" if username else ""
                send_log(
                    f"Credits Modified\n"
                    f"User   - <b>{name}</b>{uname_str}\n"
                    f"ID     - <code>{target_uid}</code>\n"
                    f"Change - <code>{change_word}</code> (New Balance: {new_credits})\n"
                    f"By     - Admin <code>{chat_id}</code>"
                )

                try:
                    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteMessage"
                    get_telegram_session().post(url, json={'chat_id': chat_id, 'message_id': msg.get('message_id')})
                except Exception:
                    pass

                send_message(chat_id, f"Updated searches for user {target_uid}. New total: {new_credits}.")

                try:
                    send_message(
                        int(target_uid),
                        f"<b>Plan Update</b>\n\n"
                        f"An admin has updated your plan. You now have {new_credits} searches available."
                    )
                except Exception:
                    pass

                show_user_profile_admin(chat_id, target_uid, msg_id)
                clear_session(chat_id)
            else:
                send_message(chat_id, f"User {target_uid} not found in database.")
                clear_session(chat_id)
        except ValueError:
            send_message(chat_id, "Invalid number. Please enter a valid number (e.g. 7 or -7).")
        return

    if current_step == 'awaiting_edit_user_unlimited':
        if chat_id not in OWNER_IDS:
            clear_session(chat_id)
            return

        target_uid = d.get('target_uid')
        msg_id = d.get('msg_id')
        val_str = message_text.strip()

        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteMessage"
            get_telegram_session().post(url, json={'chat_id': chat_id, 'message_id': msg.get('message_id')})
        except Exception:
            pass

        if val_str == "-0":
            users_col.update_one({"_id": target_uid}, {"$set": {"lifetime": False}, "$unset": {"expiry": ""}})
            invalidate_cached_user(target_uid)
            send_message(chat_id, f"User {target_uid} unlimited plan removed.")

            try:
                send_message(
                    int(target_uid),
                    f"<b>Plan Update</b>\n\n"
                    f"An admin has updated your Unlimited plan. Your Unlimited plan has been deactivated."
                )
            except Exception:
                pass

            user_doc = users_col.find_one({"_id": target_uid})
            name = user_doc.get('first_name', 'Unknown') if user_doc else 'Unknown'
            username = user_doc.get('username') if user_doc else None
            uname_str = f" (@{username})" if username else ""
            send_log(
                f"Unlimited Status Modified\n"
                f"User   - <b>{name}</b>{uname_str}\n"
                f"ID     - <code>{target_uid}</code>\n"
                f"Status - <b>Unlimited Removed</b>\n"
                f"By     - Admin <code>{chat_id}</code>"
            )

            show_user_profile_admin(chat_id, target_uid, msg_id)
            clear_session(chat_id)
            return

        try:
            val = int(val_str)

            user_doc = users_col.find_one({"_id": target_uid})
            if not user_doc:
                send_message(chat_id, "User not found.")
                clear_session(chat_id)
                return

            name = user_doc.get('first_name', 'Unknown')
            username = user_doc.get('username')
            uname_str = f" (@{username})" if username else ""

            if val == 0:
                users_col.update_one({"_id": target_uid}, {"$set": {"lifetime": True, "is_premium": True}, "$unset": {"expiry": ""}})
                invalidate_cached_user(target_uid)
                send_message(chat_id, f"User {target_uid} unlimited plan set to Lifetime.")

                try:
                    send_message(
                        int(target_uid),
                        f"<b>Plan Update</b>\n\n"
                        f"An admin has updated your Unlimited plan. It is now valid until: Lifetime."
                    )
                except Exception:
                    pass

                send_log(
                    f"Unlimited Status Modified\n"
                    f"User   - <b>{name}</b>{uname_str}\n"
                    f"ID     - <code>{target_uid}</code>\n"
                    f"Status - <b>Unlimited Lifetime Activated</b>\n"
                    f"By     - Admin <code>{chat_id}</code>"
                )
            else:
                current_expiry_str = user_doc.get('expiry')
                base_time = datetime.now()

                if current_expiry_str and not user_doc.get('lifetime'):
                    try:
                        current_expiry = datetime.fromisoformat(current_expiry_str)
                        if current_expiry > base_time:
                            base_time = current_expiry
                    except Exception:
                        pass

                expiry_dt = base_time + timedelta(days=val)

                if expiry_dt <= datetime.now():
                    users_col.update_one({"_id": target_uid}, {"$set": {"lifetime": False}, "$unset": {"expiry": ""}})
                    invalidate_cached_user(target_uid)
                    send_message(chat_id, f"User {target_uid} unlimited plan removed (expired).")
                    send_log(
                        f"Unlimited Status Modified\n"
                        f"User   - <b>{name}</b>{uname_str}\n"
                        f"ID     - <code>{target_uid}</code>\n"
                        f"Status - <b>Unlimited Removed</b>\n"
                        f"By     - Admin <code>{chat_id}</code>"
                    )
                else:
                    new_expiry = expiry_dt.isoformat()
                    total_days = max(1, int(((expiry_dt - datetime.now()).total_seconds() + 86399) // 86400))
                    users_col.update_one({"_id": target_uid}, {"$set": {"lifetime": False, "expiry": new_expiry, "is_premium": True, "unlimited_days": total_days}, "$unset": {"expiry_notified": "", "expiry_warning_notified": ""}})
                    invalidate_cached_user(target_uid)

                    date_formatted = expiry_dt.strftime("%d-%b-%Y at %I:%M %p")
                    change_type = "added to" if val > 0 else "removed from"
                    send_message(
                        chat_id,
                        f"User {target_uid}: {abs(val)} day(s) {change_type} unlimited plan.\n"
                        f"Expires on: {date_formatted}."
                    )

                    user_date_formatted = expiry_dt.strftime("%d-%b-%Y")
                    try:
                        send_message(
                            int(target_uid),
                            f"<b>Plan Update</b>\n\n"
                            f"An admin has updated your Unlimited plan. It is now valid until: {user_date_formatted}."
                        )
                    except Exception:
                        pass

                    send_log(
                        f"Unlimited Status Modified\n"
                        f"User   - <b>{name}</b>{uname_str}\n"
                        f"ID     - <code>{target_uid}</code>\n"
                        f"Change - <b>{val:+d} Days</b>\n"
                        f"Expiry - {date_formatted}\n"
                        f"By     - Admin <code>{chat_id}</code>"
                    )

            show_user_profile_admin(chat_id, target_uid, msg_id)
            clear_session(chat_id)
        except ValueError:
            send_message(chat_id, "Invalid value. Enter <code>0</code> for lifetime, numbers for days (e.g. <code>3</code>, <code>-3</code>), or <code>-0</code> to remove.")
        return

    if current_step == 'awaiting_mobile':
        if re.match(r'^\d{10}$', message_text):
            logger.info(f"Entered Mobile Number: {message_text} {tag}")
            set_session(chat_id, 'awaiting_eid_name_choice', {**d, 'mobile': message_text})
            prefetch_captcha_async(chat_id, revamp=True)

            kb = {
                'inline_keyboard': [
                    [{'text': 'Auto Name', 'callback_data': 'eid_name_auto'}],
                    [{'text': 'Custom Name', 'callback_data': 'eid_name_custom'}],
                    [{'text': 'Cancel', 'callback_data': 'cancel'}]
                ]
            }
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<blockquote><b>[ Step 2/3 - Name Selection ]</b>\n"
                f"Choose a name option for OTP:</blockquote>\n\n"
                f"<code>Auto Name</code> - <i>Uses generic prefix (Mr). Fast and works in most cases.</i>\n\n"
                f"<code>Custom Name</code> - <i>Enter your exact name as on Aadhaar card.</i>",
                reply_markup=kb
            )
        else:
            logger.warning(f"Invalid Mobile input: '{message_text}' {tag}")
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"Invalid number.\n\n"
                f"<i>Enter a 10-digit mobile number.</i>"
            )

    elif current_step == 'awaiting_mobile_name':
        name = message_text.strip()
        logger.info(f"Entered Name for EID Retrieval: {name} {tag}")
        send_mobile_otp_flow(chat_id, d['mobile'], name, d, tag)

    elif current_step == 'awaiting_aadhaar_sms_mobile':
        if re.match(r'^\d{10}$', message_text):
            logger.info(f"Entered Mobile Number for Aadhaar SMS: {message_text} {tag}")
            set_session(chat_id, 'awaiting_aadhaar_sms_name_choice', {**d, 'mobile': message_text})
            prefetch_captcha_async(chat_id, revamp=True)

            kb = {
                'inline_keyboard': [
                    [{'text': 'Auto Name', 'callback_data': 'aadhaar_sms_name_auto'}],
                    [{'text': 'Custom Name', 'callback_data': 'aadhaar_sms_name_custom'}],
                    [{'text': 'Cancel', 'callback_data': 'cancel'}]
                ]
            }
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<blockquote><b>[ Step 2/3 - Name Selection ]</b>\n"
                f"Choose a name option for Aadhaar SMS OTP:</blockquote>\n\n"
                f"<code>Auto Name</code> - <i>Uses generic prefix (Mr). Fast and works in most cases.</i>\n\n"
                f"<code>Custom Name</code> - <i>Enter your exact name as on Aadhaar card.</i>",
                reply_markup=kb
            )
        else:
            logger.warning(f"Invalid Mobile input for Aadhaar SMS: '{message_text}' {tag}")
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"Invalid number.\n\n"
                f"<i>Enter a 10-digit mobile number.</i>"
            )

    elif current_step == 'awaiting_aadhaar_sms_custom_name':
        name = message_text.strip()
        logger.info(f"Entered Custom Name for Aadhaar SMS: {name} {tag}")
        send_aadhaar_sms_otp_flow(chat_id, d['mobile'], name, d, tag)

    elif current_step == 'awaiting_aadhaar_sms_otp':
        if re.match(r'^\d{6}$', message_text):
            logger.info(f"Entered Aadhaar SMS OTP: '{message_text}' -> Verifying UID... {tag}")

            verifying_res = send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Verifying</b>\n\n"
                f"<i>Checking OTP with UIDAI...</i>"
            )
            verifying_msg_id = verifying_res.get('result', {}).get('message_id') if verifying_res else None

            name = d.get('name', 'MR')
            success, uid_num, verified_name, dob = bot.verify_uid_sms_otp(
                chat_id, d['mobile'], name, message_text,
                d['eid_otp_txn_id'], d['captcha1_txn_id'], d['captcha_code'],
                proxy_hint=d.get('proxy_hint')
            )

            if d.get('otp_sent_msg_id'):
                delete_message(chat_id, d['otp_sent_msg_id'])

            if success:
                verified_name = verified_name if verified_name and verified_name.strip() else name
                uid_str = uid_num if uid_num else "Retrieved (Sent on Mobile SMS)"
                logger.info(f"AADHAAR SMS SUCCESS! UID: {uid_str} | Name: {verified_name} | DOB: {dob} {tag}")

                result_text = (
                    f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                    f"<b>Aadhaar Retrieval Success  OK</b>\n\n"
                    f"Name            -  <b>{verified_name}</b>\n"
                    f"Aadhaar Number  -  <code>{uid_str}</code>\n"
                    f"DOB             -  <b>{dob}</b>\n\n"
                    f"<i>Aadhaar Number has also been dispatched via SMS by UIDAI.</i>\n"
                    f"{DIVIDER}"
                )
                if verifying_msg_id:
                    edit_message(chat_id, verifying_msg_id, result_text)
                else:
                    send_message(chat_id, result_text)

                deduct_credit(chat_id)

                u = get_user(chat_id)
                uname_str = f" (@{u['username']})" if u and u.get('username') else ""
                user_disp = (u.get('first_name', 'Unknown') if u else 'Unknown') + uname_str

                if u and u.get('lifetime'):
                    cr_log = "Lifetime Unlimited"
                elif u and check_expiry(u):
                    try:
                        expiry_dt = datetime.fromisoformat(u['expiry'])
                        delta = expiry_dt - datetime.now()
                        days_left = max(0, delta.days)
                        cr_log = f"{days_left} day unlimited left"
                    except Exception:
                        cr_log = "Unlimited"
                else:
                    cr_log = f"{get_credits(chat_id)} credits left"

                send_log(
                    f"Aadhaar SMS Retrieval\n"
                    f"User    - <b>{user_disp}</b>\n"
                    f"ID      - <code>{chat_id}</code>\n"
                    f"Mobile  - <code>{d.get('mobile', 'N/A')}</code>\n"
                    f"Name    - <b>{verified_name}</b>\n"
                    f"Aadhaar - <code>{uid_str}</code>\n"
                    f"Status  - <b>{cr_log}</b>"
                )

                clear_session(chat_id)
            else:
                err_msg_to_user = verified_name or "OTP Verification Failed"
                logger.warning(f"Aadhaar SMS OTP Verification Failed: {err_msg_to_user} {tag}")
                set_session(chat_id, 'awaiting_otp_retry', d)
                user_err = clean_user_error(err_msg_to_user)
                fail_text = (
                    f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                    f"Verification failed - {user_err}\n\n"
                    f"<i>Select a method below to retry.</i>"
                )
                if verifying_msg_id:
                    edit_message(chat_id, verifying_msg_id, fail_text, reply_markup=get_retry_keyboard('retry_aadhaar_sms_otp'))
                else:
                    send_message(chat_id, fail_text, reply_markup=get_retry_keyboard('retry_aadhaar_sms_otp'))
        else:
            logger.warning(f"Invalid OTP input format: '{message_text}' {tag}")
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"Invalid OTP.\n\n"
                f"<i>Enter the 6-digit number (digits only).</i>"
            )

    elif current_step == 'awaiting_otp':
        if re.match(r'^\d{6}$', message_text):
            logger.info(f"Entered Mobile OTP: '{message_text}' -> Verifying EID... {tag}")

            verifying_res = send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Verifying</b>\n\n"
                f"<i>Checking OTP...</i>"
            )
            verifying_msg_id = verifying_res.get('result', {}).get('message_id') if verifying_res else None

            success, eid, name, dob = bot.verify_eid_otp(
                chat_id, d['mobile'], d['name'], message_text,
                d['eid_otp_txn_id'], d['captcha1_txn_id'], d['captcha_code'],
                proxy_hint=d.get('proxy_hint')
            )

            if d.get('otp_sent_msg_id'):
                delete_message(chat_id, d['otp_sent_msg_id'])

            if success:
                verified_name = name if name and name.strip() else "Mr."
                logger.info(f"EID FOUND SUCCESS! EID: {eid} | Name: {verified_name} | DOB: {dob} {tag}")
                d['dob'] = dob

                verified_text = (
                    f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                    f"<b>Identity Verified  OK</b>\n\n"
                    f"Name  -  {verified_name}\n"
                    f"EID   -  <code>{eid}</code>\n\n"
                    f"{DIVIDER}"
                )
                if verifying_msg_id:
                    edit_message(chat_id, verifying_msg_id, verified_text)
                else:
                    send_message(chat_id, verified_text)

                send_pdf_otp_flow(chat_id, eid, verified_name, d, tag)
            else:
                logger.warning(f"EID Verification Failed (Wrong OTP / No Record): {name} {tag}")
                set_session(chat_id, 'awaiting_otp_retry', d)
                user_err = clean_user_error(name)
                fail_text = (
                    f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                    f"Verification failed - {user_err}\n\n"
                    f"<i>Select a method below to retry.</i>"
                )
                if verifying_msg_id:
                    edit_message(chat_id, verifying_msg_id, fail_text, reply_markup=get_retry_keyboard('retry_mobile_otp'))
                else:
                    send_message(chat_id, fail_text, reply_markup=get_retry_keyboard('retry_mobile_otp'))
        else:
            logger.warning(f"Invalid OTP input format: '{message_text}' {tag}")
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"Invalid OTP.\n\n"
                f"<i>Enter the 6-digit number (digits only).</i>"
            )

    elif current_step == 'awaiting_pdf_otp':
        if re.match(r'^\d{6}$', message_text):
            logger.info(f"Entered PDF OTP: '{message_text}' -> Downloading PDF from Govt site... {tag}")

            if d.get('pdf_otp_sent_msg_id'):
                delete_message(chat_id, d['pdf_otp_sent_msg_id'])

            verifying_res = send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Verifying</b>\n\n"
                f"<i>Checking OTP...</i>"
            )
            status_msg_id = verifying_res.get('result', {}).get('message_id') if verifying_res and isinstance(verifying_res, dict) and verifying_res.get('ok') else None

            stop_event = threading.Event()
            finish_event = threading.Event()
            done_event = threading.Event()
            if status_msg_id:
                t = threading.Thread(target=animate_progress_thread, args=(chat_id, status_msg_id, stop_event, finish_event, done_event), daemon=True)
                t.start()

            try:
                success, pdf_path = bot.download_aadhaar_pdf(
                    chat_id, d['eid'], message_text, d['pdf_otp_txn_id'], d['transaction_id2'], False, d.get('proxy_hint')
                )
                if success and pdf_path and '.pdf' in pdf_path:
                    logger.info(f"PDF Downloaded successfully from Govt server -> Unlocking PDF... {tag}")
                    deliver_pdf(
                        chat_id, pdf_path, d.get('verified_name', 'Mr.'),
                        dob=d.get('dob'),
                        status_msg_id=status_msg_id,
                        stop_event=stop_event, finish_event=finish_event, done_event=done_event
                    )
                else:
                    logger.warning(f"PDF Download Failed: {pdf_path} {tag}")
                    stop_event.set()
                    if status_msg_id:
                        delete_message(chat_id, status_msg_id)
                    set_session(chat_id, 'awaiting_pdf_otp_retry', d)
                    user_err = clean_user_error(pdf_path)
                    send_message(
                        chat_id,
                        f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                        f"Download failed - {user_err}\n\n"
                        f"<i>Select a method below to retry.</i>",
                        reply_markup=get_retry_keyboard('retry_pdf_otp')
                    )
            finally:
                stop_event.set()
        else:
            logger.warning(f"Invalid PDF OTP input format: '{message_text}' {tag}")
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"Invalid OTP.\n\n"
                f"<i>Enter the 6-digit number (digits only).</i>"
            )

    elif current_step == 'awaiting_aadhaar':
        uid = message_text.strip().replace(' ', '')
        if re.match(r'^\d{12}$', uid):
            logger.info(f"Entered Aadhaar Number: {uid} -> Prompting for Name... {tag}")
            prefetch_captcha_async(chat_id, revamp=False)

            res = send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>[ Step 2 of 3 - Name ]</b>\n\n"
                f"Enter your full name as on Aadhaar",
                reply_markup=get_cancel_keyboard()
            )
            name_msg_id = res.get('result', {}).get('message_id') if res else None
            set_session(chat_id, 'awaiting_aadhaar_name', {**d, 'uid': uid, 'eid': uid, 'name_msg_id': name_msg_id})
        else:
            logger.warning(f"Invalid Aadhaar input: '{uid}' {tag}")
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"Invalid Aadhaar.\n\n"
                f"<i>Enter the 12-digit Aadhaar number (digits only).</i>"
            )

    elif current_step == 'awaiting_aadhaar_name':
        name = message_text.strip()
        logger.info(f"Entered Name for Aadhaar PDF: {name} {tag}")

        if d.get('name_msg_id'):
            delete_message(chat_id, d['name_msg_id'])

        uid = d.get('uid') or d.get('eid')
        send_pdf_otp_direct_flow(chat_id, uid, name, d, tag)

    elif current_step == 'awaiting_eid_input':
        eid = message_text.strip()
        if len(eid) >= 10:
            logger.info(f"Entered EID Number: {eid} -> Automatically generating & solving Captchas... {tag}")
            prefetch_captcha_async(chat_id, revamp=False)

            res = send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>[ Step 2 of 3 - Name ]</b>\n\n"
                f"Enter your full name as on Aadhaar",
                reply_markup=get_cancel_keyboard()
            )
            name_msg_id = res.get('result', {}).get('message_id') if res else None
            set_session(chat_id, 'awaiting_eid_name', {**d, 'eid': eid, 'name_msg_id': name_msg_id})
        else:
            logger.warning(f"Invalid EID input: '{eid}' {tag}")
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"Invalid EID.\n\n"
                f"<i>Please check and re-enter your Enrollment ID.</i>"
            )

    elif current_step == 'awaiting_eid_name':
        name = message_text.strip()
        logger.info(f"Entered Name for EID PDF: {name} {tag}")

        if d.get('name_msg_id'):
            delete_message(chat_id, d['name_msg_id'])

        eid = d.get('eid')
        send_pdf_otp_direct_flow(chat_id, eid, name, d, tag)

    elif current_step == 'awaiting_manual_name_input':
        name = message_text.strip()
        logger.info(f"Manually Entered Name for PDF: {name} {tag}")

        eid = d.get('eid')
        sd = {**d, 'verified_name': name}

        send_pdf_otp_flow(chat_id, eid, name, sd, tag)

    elif current_step == 'awaiting_pdf_otp_direct':
        if re.match(r'^\d{6}$', message_text):
            logger.info(f"Entered Direct PDF OTP: '{message_text}' -> Downloading PDF from Govt site... {tag}")

            if d.get('pdf_otp_sent_msg_id'):
                delete_message(chat_id, d['pdf_otp_sent_msg_id'])

            verifying_res = send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"<b>Verifying</b>\n\n"
                f"<i>Checking OTP...</i>"
            )
            status_msg_id = verifying_res.get('result', {}).get('message_id') if verifying_res and isinstance(verifying_res, dict) and verifying_res.get('ok') else None

            stop_event = threading.Event()
            finish_event = threading.Event()
            done_event = threading.Event()
            if status_msg_id:
                t = threading.Thread(target=animate_progress_thread, args=(chat_id, status_msg_id, stop_event, finish_event, done_event), daemon=True)
                t.start()

            try:
                success, pdf_path = bot.download_aadhaar_pdf(
                    chat_id, d['eid'], message_text, d['pdf_otp_txn_id'], d['transaction_id2'], False, d.get('proxy_hint')
                )
                if success and pdf_path and '.pdf' in pdf_path:
                    logger.info(f"Direct PDF Downloaded successfully from Govt server -> Unlocking PDF... {tag}")
                    deliver_pdf(
                        chat_id, pdf_path, d.get('verified_name', 'Mr.'),
                        dob=d.get('dob'),
                        status_msg_id=status_msg_id,
                        stop_event=stop_event, finish_event=finish_event, done_event=done_event
                    )
                else:
                    logger.warning(f"Direct PDF Download Failed: {pdf_path} {tag}")
                    stop_event.set()
                    if status_msg_id:
                        delete_message(chat_id, status_msg_id)
                    set_session(chat_id, 'awaiting_pdf_otp_direct_retry', d)
                    user_err = clean_user_error(pdf_path)
                    send_message(
                        chat_id,
                        f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                        f"Download failed - {user_err}\n\n"
                        f"<i>Select a method below to retry.</i>",
                        reply_markup=get_retry_keyboard('retry_pdf_otp_direct')
                    )
            finally:
                stop_event.set()
        else:
            logger.warning(f"Invalid Direct PDF OTP input format: '{message_text}' {tag}")
            send_message(
                chat_id,
                f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                f"Invalid OTP.\n\n"
                f"<i>Enter the 6-digit number (digits only).</i>"
            )


# ============== PROXY SETUP ==============
proxy_setup_done = False


def setup_proxy():
    global proxy_setup_done
    if proxy_setup_done:
        return
    env_proxy = os.environ.get('PROXY_URL', '').strip()
    if env_proxy:
        if not env_proxy.startswith(('http://', 'https://', 'socks5://', 'socks5h://')):
            parts = env_proxy.split(':')
            if len(parts) == 4:
                env_proxy = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
            elif len(parts) == 2:
                env_proxy = f"http://{parts[0]}:{parts[1]}"
        try:
            parsed = urlparse(env_proxy)
            if parsed.scheme in ['http', 'https', 'socks5', 'socks5h']:
                PROXY_CONFIG['use_proxy'] = True
                PROXY_CONFIG['http'] = env_proxy
                PROXY_CONFIG['https'] = env_proxy
                print(f"Proxy from env: {env_proxy}")
            else:
                print("Invalid PROXY_URL scheme - running without proxy.")
        except Exception as e:
            print(f"Invalid PROXY_URL: {e} - running without proxy.")
    elif UIDAI_PROXIES:
        PROXY_CONFIG['use_proxy'] = True
        PROXY_CONFIG['http'] = UIDAI_PROXIES[0]
        PROXY_CONFIG['https'] = UIDAI_PROXIES[0]
        print(f"Proxy list loaded: {len(UIDAI_PROXIES)} proxies configured.")
    else:
        PROXY_CONFIG['use_proxy'] = False
        print("Proxy: off")
    reset_uidai_session()
    proxy_setup_done = True


def check_uidai_connectivity():
    if PROXY_CONFIG.get('use_proxy') and PROXY_CONFIG.get('https'):
        try:
            sess, _ = get_uidai_session()
            payload = {
                "captchaLength": "6",
                "captchaType": "2",
                "audioCaptchaRequired": False
            }
            resp = sess.post(
                'https://tathya.uidai.gov.in/audioCaptchaService/api/captcha/v3/generation',
                json=payload,
                timeout=12
            )
            if resp.status_code in [200, 400, 403, 405] or resp.content:
                return True
            return False
        except Exception as e:
            logger.debug(f"UIDAI proxy connectivity check failed: {e}")
            return False
    else:
        try:
            sock = socket.create_connection(("tathya.uidai.gov.in", 443), timeout=8)
            sock.close()
            return True
        except Exception:
            return False


# ============== GET UPDATES ==============
def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {'timeout': 5, 'allowed_updates': ['message', 'callback_query']}
    if offset:
        params['offset'] = offset
    try:
        response = get_telegram_session().get(url, params=params, timeout=8)
        result = response.json()
        if result.get('ok'):
            return result.get('result', [])
        else:
            logger.error(f"Telegram API error: {result}")
            return []
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return []


def process_update(update):
    try:
        cid = None
        if 'callback_query' in update:
            cid = update['callback_query']['message']['chat']['id']
        elif 'message' in update:
            cid = update['message']['chat']['id']

        if 'callback_query' in update:
            cq = update['callback_query']
            cid = cq['message']['chat']['id']
            cqid = cq['id']
            data = cq.get('data', '')
            msg_id = cq.get('message', {}).get('message_id')
            handle_callback(cid, cqid, data, msg_id, cq=cq)

        elif 'message' in update:
            msg = update['message']
            cid = msg['chat']['id']
            check_and_notify_expiry(cid)
            text = msg.get('text', msg.get('caption', '')).strip()
            photo = msg.get('photo')
            if not text and not photo:
                return

            if text.startswith('/start'):
                parts = text.split()
                referrer_id = None
                if len(parts) > 1 and parts[1].startswith('ref_'):
                    try:
                        referrer_id = int(parts[1][4:])
                    except ValueError:
                        pass

                if referrer_id:
                    update_session_data(cid, 'referrer_id', referrer_id)

                if not is_channel_member(cid):
                    send_message(
                        cid,
                        f"<b>{BOT_NAME}</b>\n{DIVIDER}\n"
                        f"<b>Channel Required</b>\n\n"
                        f"Join <b>{CHANNEL_USERNAME}</b> to use this bot.\n\n"
                        f"{DIVIDER}\n"
                        f"<i>Tap the button below after joining.</i>",
                        reply_markup=get_join_keyboard()
                    )
                    return

                is_new = ensure_user(
                    cid, referrer_id,
                    first_name=msg.get('from', {}).get('first_name'),
                    username=msg.get('from', {}).get('username')
                )
                clear_session(cid)
                cr = get_credits(cid)
                cr_display = "Lifetime" if cr == float('inf') else str(int(cr))
                _from = msg.get('from', {})
                user_name = _from.get('first_name', 'User') if _from else 'User'
                bonus_line = f"\n<blockquote>Bonus Reward: <code>+1 Free Credit for joining!</code></blockquote>\n" if is_new else ""
                send_message(
                    cid,
                    f"<b>{BOT_NAME} - WELCOME</b>\n{DIVIDER}\n"
                    f"<blockquote><b>Hey {user_name}!</b>\n"
                    f"Welcome to <b>{BOT_NAME}</b> - Fast and easy Aadhaar PDF download Bot from Govt site.</blockquote>\n\n"
                    f"<b>System Highlights</b>\n"
                    f"Source - Official Govt & OSINT Portals\n"
                    f"Delivery - Auto-Unlocked PDF (No Password)\n"
                    f"Modes - Mobile | Aadhaar | EID{bonus_line}\n\n"
                    f"<blockquote><b>Search Balance:</b> <code>{cr_display}</code></blockquote>\n"
                    f"<i>Select a search mode from the bottom menu to begin.</i>",
                    reply_markup=get_main_keyboard()
                )
            else:
                _from = msg.get('from', {})
                s = get_session(cid)
                referrer_id = s.get('data', {}).get('referrer_id')
                ensure_user(
                    cid,
                    referrer_id=referrer_id,
                    first_name=_from.get('first_name'),
                    username=_from.get('username')
                )
                handle_message(cid, msg)
    except Exception as e:
        logger.error(f"Error processing update: {e}")


# ============== DISABLE WINDOWS QUICK-EDIT MODE ==============
def disable_quick_edit():
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            h_input = kernel32.GetStdHandle(-10)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(h_input, ctypes.byref(mode)):
                new_mode = (mode.value & ~0x0040) | 0x0080
                kernel32.SetConsoleMode(h_input, new_mode)
        except Exception:
            pass


# ============== MAIN ==============
def main():
    disable_quick_edit()
    setup_proxy()

    print("=" * 60)
    print("           ModxAadhaar Telegram Bot - Starting Up")
    print("=" * 60)

    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("TELEGRAM_BOT_TOKEN not set.")
        return

    try:
        r = get_telegram_session().get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe", timeout=10
        )
        bot_info = r.json()
        if bot_info.get('ok'):
            _bot_username_val = bot_info['result']['username']
            global _bot_username
            _bot_username = _bot_username_val

            proxy_display = PROXY_CONFIG['https'].split('@')[-1] if (PROXY_CONFIG['use_proxy'] and PROXY_CONFIG.get('https')) else 'Direct Connection'

            print(f"[ONLINE ] Telegram Bot : @{_bot_username_val}")
            print(f"[PROXY  ] Egress Proxy : {proxy_display}")
            print(f"[ENGINE ] PDF Cracker  : PyPDF2 / 16 threads")
            print(f"[SYSTEM ] Status       : Active")
            print(f"[OWNERS ] Admin IDs    : {', '.join(map(str, OWNER_IDS))}")
            print("=" * 60)
        else:
            logger.error(f"Bot auth failed: {bot_info}")
            return
    except Exception as e:
        logger.error(f"Startup error: {e}")
        return

    t = threading.Thread(target=_cleanup_sessions, daemon=True)
    t.start()

    t_report = threading.Thread(target=daily_report_scheduler, daemon=True)
    t_report.start()

    t_expiry = threading.Thread(target=expiry_checker_scheduler, daemon=True)
    t_expiry.start()

    print("[SYSTEM ] Bot worker active - Press Ctrl+C to stop")
    print("=" * 60)

    last_update_id = 0
    executor = ThreadPoolExecutor(max_workers=50)

    while True:
        try:
            updates = get_updates(last_update_id + 1)

            for update in updates:
                last_update_id = update.get('update_id')
                executor.submit(process_update, update)

            time.sleep(0.2)

        except KeyboardInterrupt:
            print("\n[ stopped ]  shutting down...")
            executor.shutdown(wait=False)
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
