#!/usr/bin/env python3

import os
import sys
import getopt
import pprint
from termcolor import colored
import requests
import re
import json
import csv


def usage():
    print ("""
The script is controlled by following options:
    -h, --help \t\t: this help
    -r, --radius \t: gets an argument, the radius around central start to
      put on the map
    -s, --system: \t: gets an argument, the name of the system to prepare map for.
      Please note, that the more complex name e.g. HIP 2033, have to in quotations
    -v, --verbose \t: extra information to the console during script execution
    """)

def set_default(option, default_opts):
    if verbose:
        print(f"Set '{option}' to it's default value {default_opts[option]}")
    return default_opts[option]


def create_cache(filename, system_name, radius):

    url_server = "https://www.edsm.net"
    url_api = "/api-v1"
    url_sphere = f"/sphere-systems?systemName={system_name}"
    url_parameters = f"&radius={radius}&showCoordinates=1&showPrimaryStar=1&showInformation=1&showPermit=1"

    url = url_server + url_api + url_sphere + url_parameters
    if verbose:
        print (url)

    sphere = requests.get(url).json()
    sphere = sorted(sphere, key=lambda k: k["distance"])
    with open(filename,'w') as outfile:
       json.dump(sphere, outfile)

    return(sphere)


def print_basic_info(sphere):
    for system in sphere:
        try:
             pop = system['information']['population']
             color = 'cyan'
        except KeyError:
            pop = 0
            color = 'blue'
        name = system['name']
        print (colored(f"{name:<30s}\t {pop:15,d}".format(), color))


def color_to_int(color):
    return(int(color, 0))

def def_color(star_type):
    a = r"^A"
    f = r"^F"
    g = r"^G"
    k = r"^K"
    l = r"^L"
    y = r"^Y"
    m = r"M"
    wd = r"White Dwarf"
    tt = r"T Tauri Star"

    if re.search(a, star_type):
        color = '0xF0FFFF'
    elif re.search(f, star_type):
        color = '0xFFFFF0'
    elif re.search(g, star_type):
        color = '0xFFDF00'
    elif re.search(k, star_type):
        color = '0xFFA500'
    elif re.search(l, star_type):
        color = '0xA52A2A'
    elif re.search(m, star_type):
        color = '0xFF4500'
    elif re.search(wd, star_type):
        color = '0xFFFFFF'
    elif re.search(tt, star_type):
        color = '0x8B0000'
    else:
        color = '0xBEBEBE'
    return(color_to_int(color))



def prepare_gnuplot(sphere):
    zero = sphere[0]['coords']
    new_sphere = []
    # Translate location for each system
    for system in sphere:
        x = system['coords']['x'] - zero['x']
        y = system['coords']['y'] - zero['y']
        z = system['coords']['z'] - zero['z']
        system['coords'] = {'x':x, 'y':y, 'z':z }
        if verbose:
            print (system['primaryStar'])
        try:
            color = def_color(system['primaryStar']['type'])
        except KeyError:
            if system['primaryStar'] ==  {}:
                color = def_color('unknown')
            else:
                print (system['primaryStar'])
                sys.exit(2)
        new_sphere.append((system['name'], x, y, z, color))
        if color == 'black':
            print ("%s has no colour" %system['name'])
    return(new_sphere)

def save_data(stars, filename_output):
    csv.register_dialect('gnuplot', delimiter=' ')
    with open(filename_output,'w') as f:
        writer = csv.writer(f, 'gnuplot')
        writer.writerows(stars)

#### MAIN PART


opts, args = getopt.getopt(sys.argv[1:], "hs:r:v", ["help", "system=", "radius=" "verbose"])

verbose = False
default_opts = {
    "system_name": "V1688 Aquilae",
    "radius": 15.0,
}

if len(opts) > 0:
    for o, a in opts:
        if o in ["-h", "--help"]:
            usage()
            sys.exit()
        elif o in ["-s", "--system"]:
            system_name = a
        elif o in ["-r", "--radius"]:
            radius = a
        elif o in ["-v", "--verbose"]:
            verbose = True
        else:
            assert False, "unhandled option"
else:
    print ("No option specify. Using default ones")

try:
    radius
except NameError:
    radius = set_default('radius', default_opts)

try:
    system_name
except NameError:
    system_name = set_default('system_name', default_opts)

if verbose:
    print(f"Prepare map for {system_name}")

filename = system_name.lower().replace(' ','')

# Read data from local cache (if exists)
# or create it to avoid unnecessary calls to EDSM
filename_cache = f'{filename}.json'
if os.path.isfile(filename_cache):
    sphere = json.load(open(filename_cache))
else:
    sphere = create_cache(filename_cache, system_name, radius)

if sys.platform != 'win32':
    print_basic_info(sphere)

# Prepare information for GNUplot data file
stars = prepare_gnuplot(sphere)

# Save data to the file
filename_output ='{}.3d.dat'.format(filename)
save_data(stars, filename_output)
