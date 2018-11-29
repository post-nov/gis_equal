# Gis equalizer

Creates *shapefile* of points with elevation atributes wich evenly distributed along the lines. 
For this purpose it takes two layers:
1. One contains *shapefile* with target lines
2. Other contains points with *elev* attribute

## Usage 

By default script has a few atributes wich can be changed via terminal:
1. **LINES** shapefile(-l *lines*)
2. **ELEVATIONS** shapefile(-p *points*)
3. **ACCURACY** wich stands for meters needed to consider point as part of line (-a *0.5*)
4. **STEP** sets the lenght beetween points created along the line (-s *5*)

## Example

> python main.py -l lines_file -p points_file -a 3.4 -s 7
