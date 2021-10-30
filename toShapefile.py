#input information 
f = r'C:\01_firstSteps'
folder1 = f + '\\00_ORIGINAL'
 
arcpy.CreateFolder_management(f, '01_KML_TO_SHAPEFILE')
folder2 = f + '\\01_KML_TO_SHAPEFILE'
arcpy.CreateFolder_management(f, '02_SHAPEFILE_UTM')
folder3 = f+ '\\02_SHAPEFILE_UTM'
coord = arcpy.SpatialReference('SIRGAS 2000 UTM Zone 22S')

#part1
def toShapefile(input, output):
    """"
    Identifies the file in kmz format and changes to shapefile (.shp).
	:::input: Folder with initial files.
	:::output: Folder with output files.
    """

    arcpy.env.workspace = input
    files = arcpy.ListFiles('*.kmz')

    for item in files:
        i = item.split('.')[0]
        try:
            arcpy.KMLToLayer_conversion(input+'\\'+item,output,i)
            
            path = output + '\\' + i + '.gdb\\Placemarks\\Polygons'
            arcpy.FeatureToPolygon_management(path,output + '\\' + i +'.shp')
            print('Polygon: {}'.format(item))
		
        except arcpy.ExecuteError:
            path = output + '\\' + i + '.gdb\\Placemarks\\Polylines'
            arcpy.FeatureToPolygon_management(path,output + '\\' + i +'.shp')
            print('Polyline: {}'.format(item))

        except:
            print('Error: {}'.format(item))
            continue
			
toShapefile(folder1, folder2)
			
#part2
def toUTM(input, output, coordinate):
    """
    Change the coordinate system shapefile (.shp) file.
	:::input: Folder with initial files.
	:::output: Folder with output files.
	:::coordinate: Pre-established coordinate system.
    """
    arcpy.env.workspace = input
    files = arcpy.ListFiles('*.shp')

    for item in files:
        i = item.split('.')[0]
        arcpy.management.Project(input + '\\' + item, output + '\\' + i + '_UTM.shp', coordinate)
		
toUTM(folder2, folder3, coord)

#part3
def fillAttributes(input):
    """
    Creates basic information in the attribute table and deletes what is not needed.
	:::input: Folder with initial files.
    """
    arcpy.env.workspace = input
    files = arcpy.ListFiles('*.shp')
    
    for i in files:
        arcpy.AddField_management(i, 'CODE', 'TEXT')
        with arcpy.da.UpdateCursor(i, 'CODE') as rows:
            for row in rows:
                if row[0] == '':
                    row[0] = i.split('_')[0]
                    rows.updateRow(row)
		
        arcpy.AddField_management(i, 'STATE', 'TEXT')
        with arcpy.da.UpdateCursor(i, 'STATE') as rows:
            for row in rows:
                if row[0] == '':
                    row[0] = i.split('_')[1]
                    rows.updateRow(row)

        arcpy.AddField_management(i, 'AREA', 'DOUBLE')
        arcpy.CalculateField_management(i, 'AREA', '!shape.Area@hectares!', "PYTHON", '')

        remove = ['Id', 'FID_Polygo', 'Name', 'FolderPath', 'SymbolID', 'AltMode', 'Base', 'Clamped', 'Extruded', 'Snippet', 'PopupInfo', 'Shape_Leng', 'Shape_Area']
        arcpy.DeleteField_management(i, remove)
		
fillAttributes(folder3)

#part4
def joinAll(input, output):
    """
    Include all states in a single shapefile (.shp) file.
	:::input: Folder with initial files.
	:::output: Folder with output files.
    """
    arcpy.env.workspace = input
    files = arcpy.ListFiles('*.shp')
	
    list = []
    for i in files:
        list.append(i)
		
    arcpy.Merge_management(list, output + '\\' + 'Brazilian_States.shp')

joinAll(folder3, pf)
