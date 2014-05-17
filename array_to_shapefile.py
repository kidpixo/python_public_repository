import numpy as np

def output_ogr_from_2darray(array_2D,raster_NoDataValue,geotransformation,classes,classes_attributes,outputh_file):
   """
   Convert an input 2D numpy array to shapefile, merging all pixels with the same value.

   @author: damo_ma
   """
   ##########################################################################
   # create 1 bands in raster file in Memory

   from osgeo import gdal
   from osgeo import ogr
   from osgeo import osr
   import os
   
   print 20*'='
   # create a Raster Layer in memory
   driver = gdal.GetDriverByName( 'MEM' )
   # see : GDALDataType > http://www.gdal.org/gdal_8h.html#a22e22ce0a55036a96f652765793fb7a4
   gdal_datasource = driver.Create( '',array_2D.shape[1], array_2D.shape[0], 1, gdal.GDT_Byte) # GDT_Byte : Eight bit unsigned integer
   gdal_datasource.SetGeoTransform(geotransformation)

   # set Spatial Reference System
   srs = osr.SpatialReference() # import srs
   srs.ImportFromEPSG(4326) #use the WGS04 in lat/long
   print 'Spatial Reference System : \n',srs.ExportToPrettyWkt()
   print 10*'='
   # here ImportFromProj4 could be used!
   # spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
   gdal_datasource.SetProjection( srs.ExportToWkt() ) # set the data source srs

   # get the 1st raster band, starting from 1, see http://www.gdal.org/classGDALDataset.html#ad96adcf07f2979ad176e37a7f8638fb6
   raster_band = gdal_datasource.GetRasterBand(1) 
   raster_band.SetNoDataValue(raster_NoDataValue) # set the NoDataValues 
   raster_band.WriteArray(array_2D)
   print 'Create a Raster Layer of %sx%s points in Memory' % (array_2D.shape)
   print 10*'='
   
   ##########################################################################
   # create a Vector Layer in memory
   drv = ogr.GetDriverByName( 'Memory' )
   ogr_datasource = drv.CreateDataSource( 'out' )

   # create a new layer to accept the ogr.wkbPolygon from gdal.Polygonize
   input_layer     = ogr_datasource.CreateLayer('polygonized', srs, ogr.wkbPolygon )

   # add a field to put the classes in
   # see OGRFieldType > http://www.gdal.org/ogr/ogr__core_8h.html#a787194bea637faf12d61643124a7c9fc
   field_defn = ogr.FieldDefn(b'class', ogr.OFTInteger) # OFTInteger : Simple 32bit integer
   input_layer.CreateField(field_defn) # add the field to the layer

   # create "vector polygons for all connected regions of pixels in the raster sharing a common pixel value"
   # see documentation : www.gdal.org/gdal_polygonize.html
   gdal.Polygonize( raster_band, raster_band.GetMaskBand(), input_layer,  0)

   print 'Create a Vector Layer of %s Features in Memory' % (input_layer.GetFeatureCount())
   print 10*'='
   ##########################################################################
   # create 1 bands in raster file

   layerDefinition = input_layer.GetLayerDefn()

   driver = ogr.GetDriverByName("ESRI Shapefile")

   # select the field name to use for merge the polygon from the first and unique field in input_layer
   field_name = layerDefinition.GetFieldDefn(0).GetName()
   print 'Joing classification based on values in field "%s"' % field_name
   print 10*'='
   # Remove output shapefile if it already exists
   if os.path.exists(outputh_file):
       driver.DeleteDataSource(outputh_file)
   out_datasource = driver.CreateDataSource( outputh_file )
   # create a new layer with wkbMultiPolygon, Spatial Reference as middle OGR file = input_layer
   multi_layer = out_datasource.CreateLayer("merged", input_layer.GetSpatialRef(), ogr.wkbMultiPolygon)
   print 'Create output file in %s' % outputh_file
   print 10*'='
   # Add the fields we're interested in
   field_field_name = ogr.FieldDefn(field_name, ogr.OFTInteger) # add a Field named field_name = class
   multi_layer.CreateField(field_field_name)
   for attributes_name in classes_attributes['names']:
      print ' Set feature "%s" in output file' % attributes_name
      # iteratively define a new file from classes_attributes
      field_defn = ogr.FieldDefn(attributes_name, ogr.OFTReal) # make the type matching input type?
      # field_defn.SetWidth = len(attributes_name) # unusfeul : driver "ESRI Shapefile" limit field name to 10 characters!
      # add new file to actual layer
      multi_layer.CreateField(field_defn)
   
   # print out the field name defined
   multylayerDefinition = multi_layer.GetLayerDefn()
   print 10*'='

   for i in classes:
      # select the features in the middle OGR file with field_name == i
      input_layer.SetAttributeFilter("%s = %s" % (field_name,i))
      print 'Field %s == %s : %s features ' % (field_name,i,input_layer.GetFeatureCount())

      # # create a new layer with wkbMultiPolygon : each new layer is a new shp file, se this to create separated file for each class
      # multi_layer = out_datasource.CreateLayer("class %s"  % i, input_layer.GetSpatialRef(), ogr.wkbMultiPolygon) # add a Layer
      # To Do : add field definiton for each layer

      multi_feature = ogr.Feature(multi_layer.GetLayerDefn()) # generate a feature
      multipolygon  = ogr.Geometry(ogr.wkbMultiPolygon) # generate a polygon based on layer unique Geometry definition
      for feature in input_layer:
         multipolygon.AddGeometry(feature.geometry()) #aggregate all the input geometry sharing the class value i
      multi_feature.SetGeometry(multipolygon) # add the merged geoemtry to the current feature
      multi_feature.SetField(field_name, i) # set the field of the current feature
      # set all the field
      for k in range(len(classes_attributes[i])):
         multi_feature.SetField(classes_attributes['names'][k],classes_attributes[i][k]) # set the field of the current feature
      multi_layer.CreateFeature(multi_feature) # add the current feature to the layer
      multi_feature.Destroy() # desrtroy the current feature

   gdal_datasource = None
   ogr_datasource  = None
   out_datasource  = None
   print 20*'='


# Define the Data
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

# class 0 represent No Data, so we have 3-1 = 2 classes
classes = np.unique(plot_matrix)[1:]

attributes_n = 5

attributes_values = np.random.random_sample((len(classes),attributes_n))

# Re-Define NaN as -1, classes normaly span [0,N] 
NoDataValue = 255

plot_matrix[np.isfinite(plot_matrix) == 0] = raster_NoDataValue
plot_matrix = plot_matrix.astype('int8') # cast to 8 bit int, it works up to 254 classes

# assign classes attributes names
# Important : Driver "ESRI Shapefile" limit field name to 10 characters!!
classes_attributes = { 'names' : ['attr_'+str(i) for i in range(attributes_n)]}

# assign classes attributes values
for i in range(classes.size):
   classes_attributes[classes[i]] = attributes_values[i,:]
   
# Some Fake Raster georereference
img_extent = (-180, 180, -90, 90)
xmin,xmax,ymin,ymax = img_extent
nrows,ncols = plot_matrix.shape
xres=(xmax-xmin)/float(ncols)
yres=(ymax-ymin)/float(nrows)
geotransform = (xmin,xres,0,ymax,0, -yres)

out_path = '/YOUR/OUTPUT/DIRECTORY/'
output_file = out_path+'GDAL_test.shp'

mariolib.output_ogr_from_2darray(plot_matrix,NoDataValue,geotransform,classes,classes_attributes,output_file)

