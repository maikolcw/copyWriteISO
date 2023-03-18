# This is a sample Python script.
import argparse
import glob
import hashlib
import os
import shutil
import time

# imports for pycdlib for iso management
from pycdlib.pycdlibexception import PyCdlibException

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO
import pycdlib

TEMP_DIR = 'tmp\\optical-test'
ISO_NAME = 'optical-test.iso'
SAMPLE_FILE_PATH = 'usr\\share\\example-content'
SAMPLE_FILE = 'Ubuntu_Free_Culture_Showcase.txt'
MD5SUM_FILE = 'optical_test.md5'
START_DIR = os.getcwd()

# Some helper paths
FULL_PATH_TO_TEMP_DIR_MD5SUM_FILE = os.path.join(START_DIR, TEMP_DIR, MD5SUM_FILE)
FULL_PATH_TO_SAMPLE_FILE_PATH_SAMPLE_FILE = os.path.join(START_DIR, SAMPLE_FILE_PATH, SAMPLE_FILE)


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
    dst = os.path.join(START_DIR, TEMP_DIR)
    try:
        shutil.copy2(FULL_PATH_TO_SAMPLE_FILE_PATH_SAMPLE_FILE, dst)
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
            with open(FULL_PATH_TO_TEMP_DIR_MD5SUM_FILE, 'a', newline='\n') as md5_file:
                md5_file.write("% s  % s\n" % (md5_hasher.hexdigest(), file_name))
        # Check the sums for paranoia’s sake
        rt = check_md5(FULL_PATH_TO_TEMP_DIR_MD5SUM_FILE)
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


def generate_iso():
    # Generate ISO image
    print("Creating ISO Image ...")
    try:
        # create pycdlib object and create new iso with parameters
        iso = pycdlib.PyCdlib()
        # interchange dictates rules on names of files with level 4 being most relaxed
        # rock ridge extension, selection of '1.09', '1.10', or '1.12' with 1.09 most compatible
        # joliet Microsoft extension, selection of 1, 2, or 3. 3 is most common
        iso.new(interchange_level=4, rock_ridge='1.09', joliet=3)

        target_file_name = SAMPLE_FILE.split(".")[0]

        prepare_file_handle = open(FULL_PATH_TO_SAMPLE_FILE_PATH_SAMPLE_FILE, 'rb')
        prepare_file_body = prepare_file_handle.read()

        # add file to iso. First argument takes file like object
        # Second argument, length of content to add to ISO (required)
        # Third argument, location of the file on the resulting ISO(iso_path), must be absolute path,
        # all intermediate directories must exist. Some other restrictions on length and format like
        # ending with semicolon and version number, please look at pycdlib docs for more detail
        # rr_name required if using rock ridge extension
        iso.add_fp(BytesIO(prepare_file_body), len(prepare_file_body), '/' + target_file_name.upper() + ';1',
                   rr_name=target_file_name)

        # write out the iso / mastering
        iso.write(ISO_NAME)
        # close out pycdlib object, freeing resources. Object can be reused for new or existing ISO
        iso.close()

        prepare_file_handle.close()
        return 1
    except PyCdlibException as error:
        print(error)
        return 0


def burn_iso():
    # Burn the ISO with the appropriate tool
    print("Sleeping 10 seconds in case drive is not yet ready ...")
    time.sleep(10)
    print("Beginning image burn ...")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--drive", help="Optical drive file path", default="dev\\sr0")
    parser.add_argument("-t", "--type", help="Optical type", default="cd")
    args = parser.parse_args()
    OPTICAL_DRIVE = args.drive
    OPTICAL_TYPE = args.type
    print(OPTICAL_DRIVE)
    print(OPTICAL_TYPE)

    # create_working_dirs() or print("Failed to create working directories")
    # get_sample_data() or print("Failed to copy sample data")
    # generate_md5() or print("Failed to generate initial md5")
    # generate_iso()
    # burn_iso()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
