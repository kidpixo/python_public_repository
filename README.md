This repository collect some of my public python.

The `array_to_shapefile.py` aim is to convert 2D numpy array to shapefile, collecting pixels sharing the same values in the same MultiPolygon.
In the example,the matrix results from a classification, so the numbers have a meaning.

Here an example of dummy data from [Raster Layers — Python GDAL/OGR Cookbook 1.0 documentation][Cookbook]

    plot_matrix =  np.array([[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   	                   [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   	                   [ 0, 1, 1, 1, 1, 0, 2, 2, 2, 2, 0, 1, 1, 1, 0, 2, 0, 0, 0],
   	                   [ 0, 1, 0, 0, 0, 0, 0, 2, 0, 2, 0, 1, 0, 1, 0, 2, 0, 0, 0],
   	                   [ 0, 1, 0, 1, 1, 0, 0, 2, 0, 2, 0, 1, 1, 1, 0, 2, 0, 0, 0],
   	                   [ 0, 1, 0, 0, 1, 0, 0, 2, 0, 2, 0, 1, 0, 1, 0, 2, 0, 0, 0],
   	                   [ 0, 1, 1, 1, 1, 0, 2, 2, 2, 2, 0, 1, 0, 1, 0, 2, 2, 2, 0],
   	                   [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   	                   [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   	                   [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])



The data represent 2 disjoint region, with 2 different values of the classification (1 and 2) plus a background of "No Data" values, represented by 0s.

My actual solutions steps :

1. Create a GDAL Raster in memory an put the 2D numpy array in a band, defining the NoData value as 0 in this case.

![Show the data][1]

2. Create a OGR vector layer in memory.
3. Use [gdal_polygonize.py][gdal_polygonize] to convert to "vector polygons for all connected regions of pixels in the raster sharing a common pixel value" (see documentation). This produce 5 different polygons, for the 5 regions in my data.

![Polygonized Raster, 5 classes][2]

4. Create a OGR vector layer on disk.

5. Get produced shapefile from point 3. and aggregate the polygon sharing the same value in multi polygon collection, in my case there will be 2 MultiPolygon (0 represent no data in the original data).

The result is a shapefile with 2 MultiPolygon, each with an unique value of the Field "class"

![Merged polygons, 2 classes ][3]

[Cookbook]: http://pcjericks.github.io/py
[gdal_polygonize]: http://www.gdal.org/gdal_polygonize.html


  [1]: http://i.stack.imgur.com/s6ms6.jpg
  [2]: http://i.stack.imgur.com/qLlZU.jpg
  [3]: http://i.stack.imgur.com/yJ8LT.jpg