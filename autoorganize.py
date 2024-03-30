import os
import shutil
import time
import sys
import subprocess
import ctypes
import threading

DEFAULT_SETTINGS = """AUTO_START: OFF
WATCH_DIRECTORIES: C:\\Folder1
OUTPUT_FOLDER: C:\\OutputFolder"""

def create_default_settings():
    if not os.path.exists("settings.txt"):
        with open("settings.txt", "w") as file:
            file.write(DEFAULT_SETTINGS)

# Call this function before reading settings to ensure that the settings file exists
create_default_settings()

def read_settings():
    if not os.path.exists("settings.txt"):
        with open("settings.txt", "w") as file:
            file.write(DEFAULT_SETTINGS)
    
    settings = {}
    while True:
        try:
            with open("settings.txt", "r") as file:
                lines = file.readlines()
                auto_start_setting = lines[0].strip().split(": ")[1].upper()
                if auto_start_setting not in ['ON', 'OFF']:
                    raise ValueError("Auto start setting must be 'ON' or 'OFF'")
                settings['auto_start'] = auto_start_setting == 'ON'
                settings['watch_directories'] = [dir.strip() for dir in lines[1].split(": ")[1].split(",")]
                settings['output_folder'] = lines[2].strip().split(": ")[1]
                
                # Validate WATCH_DIRECTORIES
                for dir in settings['watch_directories']:
                    if not os.path.exists(dir):
                        raise FileNotFoundError(f"The directory '{dir}' specified in the settings is not found.")
                
                # Validate OUTPUT_FOLDER
                if not os.path.exists(settings['output_folder']):
                    raise FileNotFoundError(f"The output folder '{settings['output_folder']}' specified in the settings is not found.")
                
                break  # Exit the loop if settings are successfully read
            
        except PermissionError:
            print("PermissionError occurred while reading settings. Retrying in 10 seconds...")
            time.sleep(10)  # Retry after 10 seconds if PermissionError occurs
        
        except (IndexError, ValueError, FileNotFoundError) as e:
            print(f"An error occurred while reading settings: {e}")
            show_error_notification("Settings Error", str(e))
            time.sleep(10)  # Retry after 10 seconds for other exceptions
            
    return settings

# Call this function before reading settings to ensure that the settings file exists
create_default_settings()

def auto_start():
    if sys.platform.startswith('win'):
        if settings['auto_start']:
            reg_add_command = f"reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v AutoOrganizer /t REG_SZ /d \"{os.path.abspath(sys.argv[0])}\" /f"
            subprocess.run(reg_add_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            # Disable auto-start if the setting is turned off
            reg_delete_command = "reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v AutoOrganizer /f"
            subprocess.run(reg_delete_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def organize_files():
    global settings
    settings = read_settings()
    for dir in settings['watch_directories']:
        try:
            if os.path.exists(dir):
                for filename in os.listdir(dir):
                    if os.path.isfile(os.path.join(dir, filename)):
                        extension = os.path.splitext(filename)[1][1:]  
                        output_folder = os.path.join(settings['output_folder'], extension)
                        os.makedirs(output_folder, exist_ok=True)
                        destination_file = os.path.join(output_folder, filename)
                        # If file with same name already exists, modify the name
                        count = 1
                        while os.path.exists(destination_file):
                            name, ext = os.path.splitext(filename)
                            new_filename = f"{name}_{count}{ext}"
                            destination_file = os.path.join(output_folder, new_filename)
                            count += 1
                        shutil.move(os.path.join(dir, filename), destination_file)
            else:
                show_error_notification("Directory Not Found", f"The directory '{dir}' specified in the settings is not found. Do you want to open the settings file?")
                break
        except PermissionError as e:
            handle_permission_error()

def show_error_notification(title, message):
    response = ctypes.windll.user32.MessageBoxW(0, message, title, 0x4 | 0x30)  # MB_YESNO | MB_ICONQUESTION
    if response == 6:  # User clicked Yes
        os.startfile("settings.txt")  # Open settings file

def ask_user_auto_start():
    global settings
    if settings['auto_start']:
        response = ctypes.windll.user32.MessageBoxW(0, "Do you want to auto-start the program on PC restart?", "Auto Start Confirmation", 0x4 | 0x30)  # MB_YESNO | MB_ICONQUESTION
        if response == 6:  # User clicked Yes
            settings['auto_start'] = True
            reg_add_command = f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v AutoOrganizer /t REG_SZ /d "{os.path.abspath(sys.argv[0])}" /f'
            subprocess.run(reg_add_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Update AUTO_START in settings.txt
            with open("settings.txt", "r+") as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if line.startswith("AUTO_START"):
                        lines[i] = "AUTO_START: ON\n"
                        break
                file.seek(0)
                file.writelines(lines)
        else:  # User clicked No
            settings['auto_start'] = False
            # Remove auto-start entry from registry
            reg_delete_command = "reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v AutoOrganizer /f"
            subprocess.run(reg_delete_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Update AUTO_START in settings.txt
            with open("settings.txt", "r+") as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if line.startswith("AUTO_START"):
                        lines[i] = "AUTO_START: OFF\n"
                        break
                file.seek(0)
                file.writelines(lines)

def get_auto_start_setting():
    with open("settings.txt", "r") as file:
        for line in file:
            if line.startswith("AUTO_START"):
                return line.strip().split(": ")[1].upper()
    return "OFF"  # Default to OFF if AUTO_START setting is not found in settings.txt

# Test the function
auto_start_setting = get_auto_start_setting()

def format_settings_file(settings):
    formatted_settings = [
        f"AUTO_START: {'ON' if settings['auto_start'] else 'OFF'}\n",
        f"WATCH_DIRECTORIES: {','.join(settings['watch_directories'])}\n",
        f"OUTPUT_FOLDER: {settings['output_folder']}\n"
    ]
    with open("settings.txt", "w") as file:
        file.writelines(formatted_settings)

# Usage example:
# Call this function to format and update the settings.txt file
settings = read_settings()  # Read the settings first
format_settings_file(settings)

def show_auto_start_notification(auto_start_setting):
    if auto_start_setting == "OFF":
        response = ctypes.windll.user32.MessageBoxW(0, "Auto start is currently OFF. Do you want to enable it now? You can change this in the settings.txt", "Auto Start Status", 0x4 | 0x30)  # MB_YESNO | MB_ICONQUESTION
        if response == 6:  # User clicked Yes
            enable_auto_start()

def enable_auto_start():
    with open("settings.txt", "r+") as file:
        lines = file.readlines()
        lines[0] = "AUTO_START: ON\n"
        file.seek(0)
        file.writelines(lines)
    
    # Format and update the settings.txt file
    settings['auto_start'] = True
    format_settings_file(settings)

# Test the function
auto_start_setting = get_auto_start_setting()
show_auto_start_notification(auto_start_setting)

def monitor_directories():
    while True:
        organize_files()
        time.sleep(10)  # Check every 10 seconds

def monitor_auto_start_settings():
    previous_auto_start = settings['auto_start']
    while True:
        current_settings = read_settings()
        if current_settings['auto_start'] != previous_auto_start:
            previous_auto_start = current_settings['auto_start']
            auto_start()  # Call auto_start function immediately after detecting a change
        time.sleep(5)  # Check every 5 seconds for changes in auto-start settings

def check_auto_start_registry():
    while True:
        auto_start_setting = get_auto_start_setting()
        if auto_start_setting == "OFF":
            # Check if the registry entry is present
            reg_query_command = "reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v AutoOrganizer"
            result = subprocess.run(reg_query_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if "AutoOrganizer" in result.stdout:
                # Remove the registry entry
                reg_delete_command = "reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v AutoOrganizer /f"
                subprocess.run(reg_delete_command, shell=True)
        time.sleep(10)  # Check every 10 seconds

def handle_permission_error():
    response = ctypes.windll.user32.MessageBoxW(0, "PermissionError occurred while accessing the directories. Do you want to change the directory settings?", "Permission Error", 0x4 | 0x30)  # MB_YESNO | MB_ICONQUESTION
    if response == 6:  # User clicked "Yes"
        os.startfile("settings.txt")  # Open the settings file for the user to change the directory

# Modify the main block to start the check_auto_start_registry thread
if __name__ == "__main__":
    settings = read_settings()
    auto_start()
    auto_start_settings_thread = threading.Thread(target=monitor_auto_start_settings)
    auto_start_settings_thread.start()
    auto_start_registry_thread = threading.Thread(target=check_auto_start_registry)
    auto_start_registry_thread.start()
    while True:
        monitor_directories()
