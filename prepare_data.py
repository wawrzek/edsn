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



def save_script(radius, system, filename, datafile):

    script_text = f"""#!/usr/bin/env gnuplot

set parametric
radius = 5
fy(v) = radius * cos(v)
fx(v) = radius * sin(v)
fz = 0

unset xtics
unset ytics
unset ztics
unset border

set title "Star Systems in distance of {radius} Light Years from {system}" font ",20"

splot for [n = 1 : 3 ] \\
  n * fx(v), n * fy(v), fz lt 3 lw 1 lc "gray70" notitle, \\
  '{datafile}' using 2:3:4:1 with labels right offset -1,-1,-1 font ",13" notitle, \\
  '' using 2:3:4:5 ps 2 pt 7 lc rgbcolor var notitle,\\
  '' using 2:3:4 ps 2 pt 6 lc black notitle, \\
  '' using 2:3:4 with impulses dt 3 lc black notitle \\
    """
    with open(filename,'w') as f:
        print (f'Creating {filename}')
        f.write(script_text)

def prepare_gnuplot_data(sphere):
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

def save_data(stars, filename):
    csv.register_dialect('gnuplot', delimiter=' ')
    with open(filename,'w') as f:
        print (f'Creating {filename}')
        writer = csv.writer(f, 'gnuplot')
        writer.writerows(stars)

#### MAIN PART


opts, args = getopt.getopt(sys.argv[1:], "hs:r:v", ["help", "system=", "radius=" "verbose"])

filenames = {}
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

filenames['core'] = system_name.lower().replace(' ','') + '-r' + radius
filenames['cache'] = filenames['core'] + '.json'
filenames['data'] = filenames['core'] + '.3d.dat'
filenames['gnuplot'] = filenames['core'] + '.gnuplot'

# Read data from local cache (if exists)
# or create it to avoid unnecessary calls to EDSM
if os.path.isfile(filenames['cache']):
    sphere = json.load(open(filenames['cache']))
else:
    sphere = create_cache(filenames['cache'], system_name, radius)

if sys.platform != 'win32':
    print_basic_info(sphere)

# Prepare information for GNUplot data file
stars = prepare_gnuplot_data(sphere)

# Save data to the file
save_data(stars, filenames['data'])
# Save Gnuplot scripts
save_script(radius, system_name, filenames['gnuplot'], filenames['data'])

