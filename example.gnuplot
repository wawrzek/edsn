
set parametric
radius = 5
fy(v) = radius * cos(v)
fx(v) = radius * sin(v)
fz = 0

unset xtics
unset ytics
unset ztics
unset border

# Replace the name of the Star System here
set title "Star Systems in distance of 15 Light Years from V1688 Aquilae" font ",20"

splot for [n = 1 : 3 ] \
  n * fx(v), n * fy(v), fz lt 3 lw 1 lc "gray70" notitle,\
  'example.dat' using 2:3:4:1 \
    with labels right offset -1,-1,-1 font ",13" notitle,\
  '' using 2:3:4:5 ps 2 pt 7 lc rgbcolor var notitle, \
  '' using 2:3:4 ps 2 pt 6 lc black notitle, \
  '' using 2:3:4 with impulses dt 3 lc black notitle
