import arcpy
import os
import logging


HOME_FOLDER = r"C:\Users\grac9792\Documents\dc-octo-scripts"
output_folder = r"C:\Users\grac9792\Documents\ArcGIS\Projects\DC OCTO MVP"
output_gdb = "DC OCTO_MVP.gdb"
aprx_name = "DC OCTO MVP.aprx"
input_service_url = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_APPS/FEMS_Awareness_Viewer/MapServer"
input_layers_list = {0: "High_Flow_Hydrants",
                     5: "New_Standard_Hydrants",
                     12: "Not_Flow_Tested",
                     13: "Non_Working_Hydrants",
                     14: "Old_Standard_Hydrants"}


def log(msg):
    '''print & log message - can add arcpy.AddMessage() here as well'''
    print(msg)
    logging.info(msg)


def err(msg):
    '''print & log error - can add arcpy.AddError() here as well'''
    print(msg)
    logging.error(msg)


def cleanup_files(delete_file):
    try:
        if(arcpy.Exists(delete_file)):
            arcpy.Delete_management(delete_file)
    except Exception as e:
        err("Could not delete file: {}".format(e))


def main():
    # set up logger
    logging.basicConfig(filename=f"{HOME_FOLDER}/main.log", format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(logging.getLevelName('INFO'))

    # get project and map
    aprx = arcpy.mp.ArcGISProject(os.path.join(output_folder, aprx_name))
    m = aprx.listMaps("FEMS Awareness Viewer")[0]
    arcpy.env.workspace = os.path.join(output_folder, output_gdb)
    arcpy.env.overwriteOutput = True

    # TODO: maybe do an initial table comparison to see if anything has actually changed??

    # for each layer, do feature class to feature class
    log("Creating feature classes from services")
    for layer_id in input_layers_list:
        arcpy.conversion.FeatureClassToFeatureClass(os.path.join(input_service_url, str(layer_id)), os.path.join(output_folder, output_gdb), input_layers_list[layer_id])

    # TODO: change symbology?

    # add projected layers to map and remove old ones
    for lyr in m.listLayers():
        if lyr.name != "Manage_Tile_Cache_Area_of_Interest_Polygons":
            log(f"Removing {lyr.name} from the map")
            m.removeLayer(lyr)

    # remove files before overwriting
    log("Removing files from gdb")
    cleanup_files(os.path.join(output_folder, output_gdb, "High_Flow_Hydrants_Project"))
    cleanup_files(os.path.join(output_folder, output_gdb, "New_Standard_Hydrants_Project"))
    cleanup_files(os.path.join(output_folder, output_gdb, "Not_Flow_Tested_Project"))
    cleanup_files(os.path.join(output_folder, output_gdb, "Non_Working_Hydrants_Project"))
    cleanup_files(os.path.join(output_folder, output_gdb, "Old_Standard_Hydrants_Project"))

    # project from 26985 to 3857
    log("Projecting new service versions to the correct projection")
    input_project_str = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]"
    projection = "WGS_1984_(ITRF00)_To_NAD_1983"
    output_project_str = "PROJCS['NAD_1983_StatePlane_Maryland_FIPS_1900',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.0],PARAMETER['Standard_Parallel_1',38.3],PARAMETER['Standard_Parallel_2',39.45],PARAMETER['Latitude_Of_Origin',37.66666666666666],UNIT['Meter',1.0]]"
    arcpy.management.Project("High_Flow_Hydrants", os.path.join(output_folder, output_gdb, "High_Flow_Hydrants_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
    arcpy.management.Project("New_Standard_Hydrants", os.path.join(output_folder, output_gdb, "New_Standard_Hydrants_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
    arcpy.management.Project("Not_Flow_Tested", os.path.join(output_folder, output_gdb, "Not_Flow_Tested_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
    arcpy.management.Project("Non_Working_Hydrants", os.path.join(output_folder, output_gdb, "Non_Working_Hydrants_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
    arcpy.management.Project("Old_Standard_Hydrants", os.path.join(output_folder, output_gdb, "Old_Standard_Hydrants_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")

    m.addDataFromPath(os.path.join(output_folder, output_gdb, "High_Flow_Hydrants_Project"))
    m.addDataFromPath(os.path.join(output_folder, output_gdb, "New_Standard_Hydrants_Project"))
    m.addDataFromPath(os.path.join(output_folder, output_gdb, "Not_Flow_Tested_Project"))
    m.addDataFromPath(os.path.join(output_folder, output_gdb, "Non_Working_Hydrants_Project"))
    m.addDataFromPath(os.path.join(output_folder, output_gdb, "Old_Standard_Hydrants_Project"))

    for lyr in m.listLayers():
        log(lyr.name)

    # TODO: remove minimum scale and make visible

    # manage tile cache
    log("Running manage tile cache")
    with arcpy.EnvManager(parallelProcessingFactor="75%"):
        arcpy.management.ManageTileCache(output_folder, "RECREATE_ALL_TILES", "Script_Cache", m, "ARCGISONLINE_SCHEME", None, [72223.819286, 36111.909643, 18055.954822, 9027.977411, 4513.988705, 2256.994353, 1128.497176, 564.248588], "Manage_Tile_Cache_Area_of_Interest_Polygons", None, 591657527.591555, 70.5310735)

    # export tile cache
    log("Running export tile cache")
    with arcpy.EnvManager(parallelProcessingFactor="75%"):
        arcpy.management.ExportTileCache(os.path.join(output_folder, "Script_Cache", "FEMS Awareness Viewer"), os.path.join(output_folder, "FEMS Awareness Viewer Cache"), "Script_Cache", "TILE_PACKAGE_TPKX", "COMPACT_V2", [591657527.591555, 295828763.795777, 147914381.897889, 73957190.948944, 36978595.474472, 18489297.737236, 9244648.868618, 4622324.434309, 2311162.217155, 1155581.108577, 577790.554289, 288895.277144, 144447.638572, 72223.819286, 36111.909643, 18055.954822, 9027.977411, 4513.988705, 2256.994353, 1128.497176, 564.248588, 282.124294, 141.062147, 70.5310735], r"in_memory\feature_set1")

    # share package/ replace tile cache
    # arcpy.ReplaceWebLayer_server(targetLayerID, archiveLayerName, updateLayerID, replaceItemInfo, createNewItem)
    log("Running share package")
    arcpy.management.SharePackage(os.path.join(output_folder, "FEMS Awareness Viewer Cache", "Script_Cache.tpkx"), '', None, "test", "st", '', "MYGROUPS", None, "MYORGANIZATION", "TRUE", '')


if __name__ == '__main__':
    main()
