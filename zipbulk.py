import os
import zipfile
import pyminizip

def get_folder_path():
    while True:
        folder_path = input("Enter the folder path to zip: ")
        if folder_path.lower() == 'undo':
            return 'undo'
        if os.path.isdir(folder_path):
            print("\nItems in the folder:")
            for item in os.listdir(folder_path):
                print(f"- {item}")
            print()
            return folder_path
        print("Invalid folder path. Please try again or type 'undo' to go back.")

def get_zip_option():
    while True:
        option = input("Do you want to zip all files into one zip (1) or each file into individual zips (2)? Enter 1 or 2: ")
        if option.lower() == 'undo':
            return 'undo'
        if option in ['1', '2']:
            return option
        print("Invalid choice. Please enter 1 or 2, or type 'undo' to go back.")

def get_compression_level():
    compression_levels = {
        '1': zipfile.ZIP_STORED,
        '2': zipfile.ZIP_DEFLATED,
        '3': zipfile.ZIP_BZIP2,
        '4': zipfile.ZIP_LZMA
    }
    while True:
        print("Supported compression levels:")
        print("1. No Compression")
        print("2. Deflate")
        print("3. BZIP2")
        print("4. LZMA")
        level = input("Choose a compression level (1-4): ")
        if level.lower() == 'undo':
            return 'undo'
        if level in compression_levels:
            return compression_levels[level]
        print("Invalid choice. Please choose a level between 1 and 4, or type 'undo' to go back.")

def get_compression_format():
    while True:
        print("Supported compression formats:")
        print("1. zip")
        format_choice = input("Choose a compression format (currently only zip is supported): ")
        if format_choice.lower() == 'undo':
            return 'undo'
        if format_choice == '1':
            return 'zip'
        print("Invalid choice. Currently, only zip format is supported. Please type 'undo' to go back.")

def get_zip_name():
    return input("Enter the base name for the zip file(s): ")

def get_password_protection():
    while True:
        option = input("Do you want to password protect the zip files? (yes or no): ").lower()
        if option == 'undo':
            return 'undo'
        if option in ['yes', 'no']:
            return option == 'yes'
        print("Invalid choice. Please enter 'yes' or 'no', or type 'undo' to go back.")

def get_password():
    return input("Enter the password for the zip file(s): ")

def zip_files_individual(folder_path, base_name, compression_level, password_protected, password):
    for idx, filename in enumerate(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            zip_name = f"{base_name}{idx+1}.zip"
            if password_protected:
                pyminizip.compress(file_path, None, zip_name, password, compression_level)
            else:
                with zipfile.ZipFile(zip_name, 'w', compression=compression_level) as zipf:
                    zipf.write(file_path, os.path.basename(file_path))
            print(f"Created zip: {zip_name}")

def zip_files_all_in_one(folder_path, base_name, compression_level, password_protected, password):
    zip_name = f"{base_name}.zip"
    if password_protected:
        file_paths = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, filename))]
        pyminizip.compress_multiple(file_paths, [os.path.basename(path) for path in file_paths], zip_name, password, compression_level)
    else:
        with zipfile.ZipFile(zip_name, 'w', compression=compression_level) as zipf:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    zipf.write(file_path, os.path.basename(file_path))
    print(f"Created zip: {zip_name}")

def main():
    steps = [
        ('folder_path', get_folder_path),
        ('zip_option', get_zip_option),
        ('compression_level', get_compression_level),
        ('compression_format', get_compression_format),
        ('zip_name', get_zip_name),
        ('password_protection', get_password_protection),
        ('password', get_password)
    ]

    user_inputs = {}
    current_step = 0

    while current_step < len(steps):
        step_name, step_function = steps[current_step]
        result = step_function()

        if result == 'undo':
            if current_step > 0:
                current_step -= 1
                continue
            else:
                print("Cannot undo. Already at the first step.")
        else:
            user_inputs[step_name] = result
            current_step += 1

    folder_path = user_inputs['folder_path']
    zip_option = user_inputs['zip_option']
    compression_level = user_inputs['compression_level']
    compression_format = user_inputs['compression_format']
    zip_name = user_inputs['zip_name']
    password_protected = user_inputs['password_protection']
    password = user_inputs['password'] if password_protected else None

    if zip_option == '1':
        zip_files_all_in_one(folder_path, zip_name, compression_level, password_protected, password)
    else:
        zip_files_individual(folder_path, zip_name, compression_level, password_protected, password)

if __name__ == "__main__":
    main()
