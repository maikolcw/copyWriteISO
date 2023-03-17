# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import shutil

TEMP_DIR = 'tmp\\optical-test'
ISO_NAME = 'optical-test.iso'
SAMPLE_FILE_PATH = 'usr\\share\\example-content\\'
SAMPLE_FILE = 'Ubuntu_Free_Culture_Showcase.txt'
MD5SUM_FILE = 'optical_test.md5'
START_DIR = os.getcwd()


def create_working_dirs():
    # First, create the temp dir and cd there
    print('Creating Temp directory and moving there ...')
    try:
        path = os.path.join(START_DIR, TEMP_DIR)
        os.makedirs(path, exist_ok=True)
        os.chdir(path)
        print("Now working in", os.getcwd())
        return 1
    except OSError as error:
        print(error)
        return 0


def get_sample_data():
    # Get our sample files
    print("Getting sample files from % s ..." % SAMPLE_FILE_PATH)
    src = os.path.join(START_DIR, SAMPLE_FILE_PATH, SAMPLE_FILE)
    dst = os.path.join(START_DIR, TEMP_DIR)
    try:
        shutil.copy2(src, dst)
        return 1
    except IOError as error:
        print(error)
        return 0


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    create_working_dirs() or print("Failed to create working directories")
    get_sample_data() or print("Failed to copy sample data")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
