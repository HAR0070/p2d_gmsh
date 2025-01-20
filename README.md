# NASA's Plot3D to Gmsh's MSH converter

Small Python script to convert from Plot3D into Gmsh mesh format. 
This is tested on 2D version of NASA mesh [2D version of grids in plot 3D format](https://turbmodels.larc.nasa.gov/Airfoilwake_grids/nak_a_fine_unified_1121.p2dfmt.gz)

## Usage


```sh
$ p3d2gmsh.py <input_file> <output_file.msh>

    input file should be 2D p2dfmt format (only tested for that)
    output will be .msh file
```

#ignore p3Dgsm file
