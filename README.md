# edsn
ED:SN - Elite Dangerous: Star Neighbourhood is a set of tools to prepare a 3d map of surroundings of one of million star systems in Elite Dangerous.
The main tools is a [GNUplot](http://gnuplot.sourceforge.net/) script taking as an input list of star systems and producing 3D star map.
Additionally, in the repository there is a python script calling [EDSM](https://www.edsm.net/) API to obtain required information and store them into GNUplot data file.
Finally, there is an example data file.

## GNUplot
make_starmap.gnuplot takes as an input the "example.dat" file.
The file name can be change in the line 18 of the script.
Graph titles is defined in line 14.
The radius of circles are controlled by the "radius" variable in line 5 and the number of them is set by a loop in line 16.

### Input data specification

There are 5 columns in an input file.
The first one is the star system name.
Columns two, three and four are coordinates with a central star in the origin of axes (0,0,0).
The last (fifth) column represent the color of a main star.
It is an integer value of a RGB colour number.

## Python

"prepare_data.py" is an example script taking information about V1688 Aquilae star system and surrounding area from the EDSM website (*create_cache* function), and saves it in the example.dat file (*save_data* function).
The script uses a main star type as a base for integer representation of the RGB colour matching stars colour (*def_color* function).
It also translates stars coordinates by shifting the origin of a coordinate system into the central star (*prepare_gnuplot* function).
The central star system name as well radius and filenames can be changed in lines 86 to 89 of the script.

Please note that the list of translated main body types is limited. t can be found in the *def_color* function.

# Links

* EDSM REST API used by the python script is defined [here](https://www.edsm.net/en/api-v1).
* My script uses tricks presented in the Lee Phillips book titled "[gnuplot 5](https://lee-phillips.org/gnuplot/)".
