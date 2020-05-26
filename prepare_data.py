#!/usr/bin/env python3

import os
import requests
import re
import json
import csv


def create_cache(filename, system_name, radius):

    url_server = "https://www.edsm.net"
    url_api = "/api-v1"
    url_sphere = f"/sphere-systems?systemName={system_name}"
    url_parameters = f"&radius={radius}&showCoordinates=1&showPrimaryStar=1&showInformation=1&showPermit=1"

    url = url_server + url_api + url_sphere + url_parameters
    #print (url)

    sphere = requests.get(url).json()
    sphere = sorted(sphere, key=lambda k: k["distance"])
    with open(filename,'w') as outfile:
       json.dump(sphere, outfile)

    return(sphere)



def color_to_int(color):
    return(int(color, 0))

def def_color(star_type):
    a = r"^A"
    f = r"^F"
    g = r"^G"
    k = r"^K"
    l = r"^L"
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
        color = def_color(system['primaryStar']['type'])
        new_sphere.append((system['name'], x, y, z, color))
        if color == 'black':
            print ("%s has no colour" %system['name'])
    return(new_sphere)

def save_data(stars):
    csv.register_dialect('gnuplot', delimiter=' ')
    with open(filename_output,'w') as f:
        writer = csv.writer(f, 'gnuplot')
        writer.writerows(stars)

#### MAIN PART
filename_cache = 'mySphere15.json'
filename_output = 'data3d.dat'
system_name = "V1688 Aquilae"
radius = 15.0

# Read data from local cache (if exists)
# or create it to avoid unnecessary calls to EDSM
if os.path.isfile(filename_cache):
    sphere = json.load(open(filename_cache))
else:
    sphere = create_cache(filename_cache, system_name, radius)

# Prepare information for GNUplot data file
stars = prepare_gnuplot(sphere)

# Save data to the file
save_data(stars)
