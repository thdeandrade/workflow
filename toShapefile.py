# Informações de entrada
p1 = r'.....\00_INIT\KML'
p2 = r'.....\00_INIT\SHP_KML'
p3 = r'.....\00_INIT\SHP_UTM'
saida = r'.....\00_INIT'

coord = arcpy.SpatialReference('SIRGAS 2000 UTM Zone 22S')

empresa = 'NOME DA EMPRESA'
lote = 'LOTE UTILIZADO'

# Parte1
def toShapefile(input, output):
    """"
    Identifica a estrutura do arquivo recebido e converte para o formato shapefile (.shp).
    """

    arcpy.env.workspace = input
    l1 = arcpy.ListFiles(['*.kmz', '*.kml'])

    for item in l1:
        i = item.split('.')[0].replace(' - ', '_')
        
        try:
            arcpy.KMLToLayer_conversion(p1+'\\'+item,output,i)
            
            path = output + '\\' + i + '.gdb\\Placemarks\\Polygons'                 #Caso seja polígono
            arcpy.FeatureToPolygon_management(path,output + '\\' + i +'.shp')
            print('Polygon: {}'.format(item))
		
        except arcpy.ExecuteError:
            path = output + '\\' + i + '.gdb\\Placemarks\\Polylines'                #Caso seja linha
            arcpy.FeatureToPolygon_management(path,output + '\\' + i +'.shp')
            print('Polyline: {}'.format(item))

        except:
            print('Error: {}'.format(item))                                         #Qualquer outro erro
            continue

toShapefile(p1, p2)

# Parte2
def toUTM(input, output, coordinate):
    """
    Altera a projeção do arquivo shapefile (.shp) criado anteriormente (no caso, para UTM).
    """
    arcpy.env.workspace = input
    l2 = arcpy.ListFiles('*.shp')

    for item in l2:
        i = item.split('.')[0]
        arcpy.management.Project(input + '\\' + item, output + '\\' + i + '_UTM.shp', coordinate)
		
toUTM(p2, p3, coord)

# Parte 3
def fillAttributes(input, company, batch):
    """
    Manipula a tabela de atributos (attribute table) para criar e preencher com informações inicias básicas e apaga o que não for necessário.
    As colunas criadas são CÓDIGO DA FAZENDA, NOME DA FAZENDA, AREA (ha), NOME DO CLIENTE e LOTE.
    """
    arcpy.env.workspace = input
    l3 = arcpy.ListFiles('*.shp')
    
    for i in l3:
        arcpy.AddField_management(i, 'CODE', 'TEXT')
        with arcpy.da.UpdateCursor(i, 'CODE') as rows:
            for row in rows:
                if row[0] == '':
                    row[0] = i.split('_')[0].replace(' ', '.')
                    rows.updateRow(row)
		
        arcpy.AddField_management(i, 'FARM', 'TEXT')
        with arcpy.da.UpdateCursor(i, 'FARM') as rows:
            for row in rows:
                if row[0] == '':
                    row[0] = i.upper().split('_')[1]
                    rows.updateRow(row)

    arcpy.AddField_management(i, 'AREA', 'DOUBLE')
    arcpy.CalculateField_management(i, 'AREA', '!shape.Area@hectares!', "PYTHON", '')

    arcpy.AddField_management(i, 'LOTE', 'TEXT')
    with arcpy.da.UpdateCursor(i, 'LOTE') as rows:
        for row in rows:
            if row[0] == '':
                row[0] = batch
                rows.updateRow(row)
				
    arcpy.AddField_management(i, 'EMPRESA', 'TEXT')
	
    with arcpy.da.UpdateCursor(i, 'EMPRESA') as rows:
        for row in rows:
            if row[0] == '':
                row[0] = company
                rows.updateRow(row)
		
    remove = ['FID_Polygo', 'Name', 'FolderPath', 'SymbolID', 'AltMode', 'Base', 'Clamped', 'Extruded', 'Snippet', 'PopupInfo', 'Shape_Leng', 'Shape_Area']
    arcpy.DeleteField_management(i, remove)

fillAttributes(p3, empresa, lote)

# Parte 4 - opcional
def joinAll(input, output, company, batch):
    """
    Inclui todas as fazendas em um único arquivo (função opcional).
    """
    arcpy.env.workspace = p3
    l3 = arcpy.ListFiles('*.shp')
	
    list = []
    for i in l3:
        list.append(i)
		
    final_name = batch.split('.')
    arcpy.Merge_management(list, output + '\\' + company + '_' + final_name[0] + '_' + final_name[1] + '.shp')

joinAll(p3, saida, empresa, lote)
