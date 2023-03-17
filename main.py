# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import glob
import hashlib
import os
import shutil

TEMP_DIR = 'tmp\\optical-test'
ISO_NAME = 'optical-test.iso'
SAMPLE_FILE_PATH = 'usr\\share\\example-content'
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


def generate_md5():
    # Generate the md5sum
    print("Generating md5sums of sample files ...")
    cur_dir = os.getcwd()
    try:
        path = os.path.join(START_DIR, SAMPLE_FILE_PATH)
        os.chdir(path)
        # Grab all file names in current directory and put in list file_names
        file_names = glob.glob('*')
        # For each file, get the md5 hash and write hash and file name to file MD5SUM_FILE
        for file_name in file_names:
            md5_hasher = hashlib.md5()
            with open(file_name, 'rb') as file_to_md5:
                for chunk in iter(lambda: file_to_md5.read(4096), b""):
                    md5_hasher.update(chunk)
            with open(os.path.join(cur_dir, MD5SUM_FILE), 'a', newline='\n') as md5_file:
                md5_file.write("% s  % s\n" % (md5_hasher.hexdigest(), file_name))
        # Check the sums for paranoia’s sake
        rt = check_md5(os.path.join(cur_dir, MD5SUM_FILE))
    except OSError as error:
        print(error)
        return 0
    try:
        os.chdir(cur_dir)
    except OSError as error:
        print(error)
        exit()
    return rt


def check_md5(md5_file):
    print("Checking md5sums ...")
    with open(md5_file, 'r') as file_to_check_md5:
        data = file_to_check_md5.read()
        # put each line in file into list list_of_lines
        list_of_lines = data.split("\n")
        # remove empty string at end of list
        list_of_lines.pop(len(list_of_lines) - 1)
        for line in list_of_lines:
            # for every line in list_of_lines, split the hash and file name into a list hash_and_file
            hash_and_file = line.split("  ")
            # open file in hash_and_file, get md5 checksum, and compare new hash to hash from hash_and_file
            # if not equal, return 0 and step out
            md5_hasher = hashlib.md5()
            with open(hash_and_file[1], 'rb') as file_to_md5:
                for chunk in iter(lambda: file_to_md5.read(4096), b""):
                    md5_hasher.update(chunk)
            if not md5_hasher.hexdigest() == hash_and_file[0]:
                return 0
    return 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    create_working_dirs() or print("Failed to create working directories")
    get_sample_data() or print("Failed to copy sample data")
    generate_md5() or print("Failed to generate initial md5")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
