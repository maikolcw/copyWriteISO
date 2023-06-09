# This Python program tries to replicate optical_write_test.sh as best as possible in a Windows environment without
# a physical drive to test
import argparse
import glob
import hashlib
import os
import shutil
import subprocess
import time
import ctypes

# Used wmi for finding drives in computer and getting letter of ROM drive
import wmi

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
FULL_PATH_TO_TEMP_DIR = os.path.join(START_DIR, TEMP_DIR)
FULL_PATH_TO_TEMP_DIR_MD5SUM_FILE = os.path.join(START_DIR, TEMP_DIR, MD5SUM_FILE)
FULL_PATH_TO_SAMPLE_FILE_PATH_SAMPLE_FILE = os.path.join(START_DIR, SAMPLE_FILE_PATH, SAMPLE_FILE)
FULL_PATH_TO_TEMP_DIR_ISO_NAME = os.path.join(START_DIR, TEMP_DIR, ISO_NAME)


def create_working_dirs():
    # First, create the temp dir and cd there
    print('Creating Temp directory and moving there ...')
    try:
        os.makedirs(FULL_PATH_TO_TEMP_DIR, exist_ok=True)
        os.chdir(FULL_PATH_TO_TEMP_DIR)
        print("Now working in", os.getcwd())
        return 1
    except OSError as error:
        print(error)
        return 0


def get_sample_data():
    # Get our sample files
    print("Getting sample files from % s ..." % SAMPLE_FILE_PATH)
    try:
        shutil.copy2(FULL_PATH_TO_SAMPLE_FILE_PATH_SAMPLE_FILE, FULL_PATH_TO_TEMP_DIR)
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
        # Attempt to imitate, assuming md5sum -- * is get all files' md5sum and put into md5 file
        # Grab all file names in current directory and put in list file_names
        file_names = glob.glob('*')
        # For each file, get the md5 hash and write hash and file name to file MD5SUM_FILE
        for file_name in file_names:
            md5_hasher = hashlib.md5()
            with open(file_name, 'rb') as file_to_md5:
                for chunk in iter(lambda: file_to_md5.read(4096), b""):
                    md5_hasher.update(chunk)
            with open(FULL_PATH_TO_TEMP_DIR_MD5SUM_FILE, 'a', newline='\n') as md5_file:
                # Trying to imitate .md5 format with double-spacing between hash and file name
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
    # This function might fail if the md5 file has multiple lines of hash and files and some don't exist
    # It will try to open a file that doesn't exist and return 0
    # Caused by generate_md5 function ran more than once back to back since it adds to md5 file and not overwrite
    print("Checking md5sums ...")
    try:
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
    except IOError as error:
        print(error)
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
        iso.add_fp(BytesIO(prepare_file_body), len(prepare_file_body), '/' + SAMPLE_FILE + ';1',
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
    # time.sleep(10)
    print("Beginning image burn ...")
    # This command should burn to CD/DVD/BD
    os.system("isoburn.exe /Q % s % s" % (OPTICAL_DRIVE, FULL_PATH_TO_TEMP_DIR_MD5SUM_FILE))
    # check if burning succeeded by checking if SAMPLE_FILE is present in optical drive
    # assuming burning will only burn ISO with one file called SAMPLE_FILE
    # Comment out this if check to skip this check when failing burn_iso
    if not os.path.exists(OPTICAL_DRIVE + SAMPLE_FILE):
        return 0
    if not OPTICAL_TYPE == 'cd' or OPTICAL_TYPE == 'dvd' or OPTICAL_TYPE == 'bd':
        print("Invalid type specified % s" % OPTICAL_TYPE)
        exit(1)
    return 1


def check_disk():
    time_out = 300
    sleep_count = 0
    interval = 3
    global OPTICAL_DRIVE
    # Give the tester up to 5 minutes to reload the newly created CD/DVD
    print("Waiting up to 5 minutes for drive to be mounted ...")
    while True:
        time.sleep(interval)
        sleep_count = sleep_count + interval
        # Goes through each drive in computer, check if drive is a CD-ROM/DVD-ROM by number and if SAMPLE_FILE exist
        # Assign new drive letter to OPTICAL_DRIVE
        find_optical_drive()
        if os.path.exists(OPTICAL_DRIVE + SAMPLE_FILE):
            print("Drive appears to be mounted now")
            break
        else:
            # Use powershell for mounting an ISO with given full path, can subsequently unmount at same path
            # Assuming user's powershell.exe is in system32
            subprocess.call("C:\\Windows\\system32\\WindowsPowerShell\\v1.0\\powershell.exe"
                            " Mount-DiskImage -ImagePath % s" % FULL_PATH_TO_TEMP_DIR_ISO_NAME, shell=True)

        # If they exceed the timeout limit, make a best effort to load the tray
        # in the next steps
        if sleep_count >= time_out:
            print("WARNING: TIMEOUT Exceeded and no mount detected!")
            break
    print("Deleting original data files ...")
    # Check to remove file
    if os.path.exists(SAMPLE_FILE):
        os.remove(SAMPLE_FILE)
    if os.path.exists(OPTICAL_DRIVE):
        os.system("dir")
        print("Disk is mounted to % s" % OPTICAL_DRIVE)
    else:
        # Since windows mounting command is different, this just retries to mount again with same powershell command
        print("Attempting best effort to mount % s on my own" % OPTICAL_DRIVE)
        mount_pt = os.path.join(START_DIR, TEMP_DIR, "mnt")
        print("Creating temp mount: % s" % mount_pt)
        os.makedirs(mount_pt, exist_ok=True)
        print("Mounting disk to mount point ...")
        # Mounting via powershell might put the mount on a drive different from OPTICAL_DRIVE
        mount_test_again = subprocess.call("C:\\Windows\\system32\\WindowsPowerShell\\v1.0\\powershell.exe"
                                           " Mount-DiskImage -ImagePath % s" % FULL_PATH_TO_TEMP_DIR_ISO_NAME,
                                           shell=True)
        # This mounted working ROM drive and assign letter to OPTICAL_DRIVE
        find_optical_drive()
        print(OPTICAL_DRIVE)
        if mount_test_again == 1:
            print("ERROR: Unable to re-mount % s!" % OPTICAL_DRIVE)
            return 0
    print("Copying files from ISO ...")
    file_list = os.listdir(OPTICAL_DRIVE)
    file_list = [OPTICAL_DRIVE + "\\" + filename for filename in file_list]
    for file in file_list:
        shutil.copy2(file, FULL_PATH_TO_TEMP_DIR)
    rt = check_md5(FULL_PATH_TO_TEMP_DIR_MD5SUM_FILE)
    return rt


def cleanup():
    print("Moving back to original location")
    try:
        os.chdir(START_DIR)
        print("Now residing in % s" % START_DIR)
        print("Cleaning up ...")
        # Assuming ISO will only be mounted in TEMP_DIR and never in mnt
        # Unmount ISO
        if os.path.exists(FULL_PATH_TO_TEMP_DIR_ISO_NAME):
            subprocess.call("C:\\Windows\\system32\\WindowsPowerShell\\v1.0\\powershell.exe"
                            " Dismount-DiskImage -ImagePath % s" % FULL_PATH_TO_TEMP_DIR_ISO_NAME, shell=True)
        # Check to remove directory
        if os.path.exists(FULL_PATH_TO_TEMP_DIR):
            os.system("rmdir /s /q % s" % FULL_PATH_TO_TEMP_DIR)
        print("Ejecting spent media ...")
        # Untested ctypes cmd to eject in Windows, set OPTICAL_DRIVE as drive to eject
        if os.path.exists(OPTICAL_DRIVE):
            ctypes.windll.WINMM.mciSendStringW(u"open % s type cdaudio alias d_drive" % OPTICAL_DRIVE, None, 0, None)
            ctypes.windll.WINMM.mciSendStringW(u"set d_drive door open", None, 0, None)
        return 1
    except OSError as error:
        print(error)
        return 0


def failed(failed_message):
    print(failed_message)
    print("Attempting to clean up ...")
    cleanup()
    exit(1)


def find_optical_drive():
    """
    Checks computer for all drives, finds ROM drive by number, and if it contains SAMPLE_FILE, assign OPTICAL_DRIVE
    with ROM drive's letter.
    :return:
    """
    wmi_object = wmi.WMI()
    global OPTICAL_DRIVE
    for drive in wmi_object.Win32_LogicalDisk():
        if drive.DriveType == 5 and os.path.exists(drive.DeviceID + SAMPLE_FILE):
            OPTICAL_DRIVE = drive.DeviceID
            return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Assuming Windows will have default disk drive of D and D is not used by any other drive
    parser.add_argument("-d", "--drive", help="Optical drive file path", default="D:")
    parser.add_argument("-t", "--type", help="Optical type", default="cd")
    args = parser.parse_args()
    OPTICAL_DRIVE = args.drive
    OPTICAL_TYPE = args.type

    create_working_dirs() or failed("Failed to create working directories")
    get_sample_data() or failed("Failed to copy sample data")
    generate_md5() or failed("Failed to generate initial md5")
    generate_iso() or failed("Failed to create ISO image")
    burn_iso() or failed("Failed to burn ISO image")
    check_disk() or failed("Failed to verify files on optical disk")
    cleanup() or failed("Failed to clean up")
