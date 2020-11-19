#!/usr/bin/env python3

import hashlib
import subprocess
import sys

# hashes calcultes with
#def hash_test(filename):
#   with open(filename) as f:
#       print (hashlib.sha1(f.read().encode('utf-8')).hexdigest())

hashes = {
    "sol-r20.3d.dat": "8530b16d2c8dba047dfda6a64de57e240f56e38d",
    "v1688aquilae-r15.3d.dat": "5d667c1305cb276c6deea783ecbb7a4ee8b9aa55"
        }

errors = 0


if sys.platform == 'win32':
    script_path = "..\prepare_data.py"
else:
    script_path = "../prepare_data.py"

def compare_hashes(filename):
    errors_hashes = 0
    with open(filename) as f:
        text = f.read().encode('utf-8')
        hash_cal = hashlib.sha1(text).hexdigest()
        if hash_cal == hashes[filename]:
            print (f"SHA1 hash for {filename} is fine")
        else:
            print ("ERROR!")
            print (f"SHA1 hash for {filename} is wrong")
            print (f"CAL: {hash_cal}")
            print (f"SAV: {hashes[filename]}")
            errors_hashes = 1
        return errors_hashes


logfile = open("test.log","w")
print ("Test script with default values")
command1 = subprocess.run([sys.executable, script_path, '-v'], capture_output=True, check=True, text=True, shell=True)
errors += compare_hashes('v1688aquilae-r15.3d.dat')
logfile.write(command1.stdout)
logfile.flush()
print ("Test script with system=Sol, radius=20")
command2 = subprocess.run([sys.executable, script_path, '-v', '-s', 'Sol', '-r', '20'], capture_output=True, check=True, text=True, shell=True)
errors += compare_hashes('sol-r20.3d.dat')
logfile.write(command2.stdout)
logfile.flush()

if errors > 0:
    sys.exit(1)
