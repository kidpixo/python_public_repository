This repository collects some of my public python.

## array_to_shapefile - convert 2D array to shapefile

The `array_to_shapefile.py` aim is to convert 2D numpy array to shapefile, collecting pixels sharing the same values in the same MultiPolygon.

#### Prerequisites 

	import numpy
	from osgeo import gdal
	from osgeo import ogr
	from osgeo import osr
	import os


#### Example Data

In the example below, the matrix results from a classification, so the do numbers have a meaning: I can not simply smooth or interpolate the image for cosmetic reason without loosing information.

Here an example of dummy data from [Raster Layers — Python GDAL/OGR Cookbook 1.0 documentation][Cookbook], a 2D numpy array  representing the text 'GDAL'

	np.array([[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			  [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			  [ 0, 1, 1, 1, 1, 0, 2, 2, 2, 2, 0, 1, 1, 1, 0, 2, 0, 0, 0],
			  [ 0, 1, 0, 0, 0, 0, 0, 2, 0, 2, 0, 1, 0, 1, 0, 2, 0, 0, 0],
			  [ 0, 1, 0, 1, 1, 0, 0, 2, 0, 2, 0, 1, 1, 1, 0, 2, 0, 0, 0],
			  [ 0, 1, 0, 0, 1, 0, 0, 2, 0, 2, 0, 1, 0, 1, 0, 2, 0, 0, 0],
			  [ 0, 1, 1, 1, 1, 0, 2, 2, 2, 2, 0, 1, 0, 1, 0, 2, 2, 2, 0],
			  [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			  [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			  [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])



The data has 2 disjoint regions with 2 different labels (1 and 2) and a background of "No Data" values, the 0s.

The data geographic information are controlled by
   
	# Some Fake Raster georereference
	img_extent = (-180, 180, -90, 90)
	xmin,xmax,ymin,ymax = img_extent
	nrows,ncols = plot_matrix.shape
	xres = (xmax-xmin)/float(ncols)
	yres = (ymax-ymin)/float(nrows)
	geotransform = (xmin,xres,0,ymax,0, -yres)

The projection is now fixed to `WGS 84` or `EPSG 4326` that I find comfortable (global in lat/lon), but I'm planning to pass a Proj.4 definition via `osr.SpatialReference().ImportFromProj4`, stay tuned. the projection Well-known text is 

	GEOGCS["WGS 84",
	    DATUM["WGS_1984",
	        SPHEROID["WGS 84",6378137,298.257223563,
	            AUTHORITY["EPSG","7030"]],
	        AUTHORITY["EPSG","6326"]],
	    PRIMEM["Greenwich",0,
	        AUTHORITY["EPSG","8901"]],
	    UNIT["degree",0.0174532925199433,
	        AUTHORITY["EPSG","9122"]],
	    AUTHORITY["EPSG","4326"]]


## Script Steps 

What the script does:

- Create a GDAL Raster in memory an put the 2D numpy array in a band, defining the NoData value as 0 in this case.

![The Data][1]

- Create a OGR vector layer in memory.
- Use [gdal_polygonize.py][gdal_polygonize] to convert to "vector polygons for all connected regions of pixels in the raster sharing a common pixel value" (see documentation). This produce 5 different polygons, for the 5 regions in my data.

- Create a OGR vector layer on disk.

- Get the `gdal_polygonize` results from the Vector Layer in Memory and aggregate the polygons sharing the same value in MultiPolygon collection: in my case there will be 2 MultiPolygon for the 2 original labels, 0 representing NoData.

The result is a shapefile with 2 MultiPolygon, each with an unique value of the Field "class"

![Merged polygons, 2 classes ][3]

[Cookbook]: http://pcjericks.github.io/py
[gdal_polygonize]: http://www.gdal.org/gdal_polygonize.html


  [1]: http://i.stack.imgur.com/s6ms6.jpg
  [2]: http://i.stack.imgur.com/qLlZU.jpg
  [3]: http://i.stack.imgur.com/yJ8LT.jpg