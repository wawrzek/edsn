#!/usr/bin/env python3

import hashlib
import subprocess
import sys


hashes = {
    "sol-r20.json": "33f7b844cb41c76a573771372768932f21f27f4d",
    "v1688aquilae-r15.json": "41ef7be79b300f96dca5c12ed981bf560229107a"
        }

errors = 0

def compare_hashes(filename):
    errors_hashes = 0
    with open(filename) as f:
        text = f.read().encode('utf-8')
        h = hashlib.sha1(text).hexdigest()
        if h == hashes[filename]:
            print (f"SHA1 hash for {filename} is fine")
        else:
            print ('ERROR!')
            print (f'SHA1 hash for {filename} is wrong')
            errors_hashes = 1
        return errors_hashes


print ("Test script with default values")
command1 = subprocess.run('../prepare_data.py', capture_output=True, check=True)
errors += compare_hashes('v1688aquilae-r15.json')

print ("Test script with system=Sol, radius=20")
command2 = subprocess.run(['../prepare_data.py', '-s', 'Sol', '-r', '20'], capture_output=True, check=True)
errors += compare_hashes('sol-r20.json')

if errors > 0:
    sys.exit(1)
