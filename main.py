import arcpy
import os
import logging
import time
import json
import keyring
import arcgis
import re


HOME_FOLDER = r"C:\Users\grac9792\Documents\dc-octo-scripts"
output_folder = r"C:\Users\grac9792\Documents\ArcGIS\Projects\DC OCTO MVP"
output_gdb = "DC OCTO_2.gdb"
aprx_name = "DC OCTO MVP.aprx"
map_name = "FEMS Awareness Viewer"
cache_name = f"{map_name} Cache"
input_service_url = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_APPS/FEMS_Awareness_Viewer/MapServer"
input_layers_list = {0: "High_Flow_Hydrants",
                     5: "New_Standard_Hydrants",
                     12: "Not_Flow_Tested",
                     13: "Non_Working_Hydrants",
                     14: "Old_Standard_Hydrants"}
target_tile_service_id = "ec3c842d5a6e456091fe6a2052ee3e78"
target_tpkx_id = "360a51375bae4f75975f7705d6f086a6"
output_service_name = "Script_Cache_New"  # (should not be the same as the service we're overwriting or there will be an error)
layer_files = ["Old Standard Hydrants.lyrx",
               "Not Flow Tested.lyrx",
               "Non-Working Hydrants.lyrx",
               "New Standard Hydrants.lyrx",
               "High Flow Hydrants.lyrx"
               ]
org_url = "https://ps-cc.maps.arcgis.com/home"
keyring_id = "pscc"
org_username = "gbushong_PS_CC"


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
    print(f"Active Portal: {arcpy.GetActivePortalURL()}")

    # set up logger
    logging.basicConfig(filename=f"{HOME_FOLDER}/publishing.log", format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(logging.getLevelName('INFO'))

    # get project and map
    aprx = arcpy.mp.ArcGISProject(os.path.join(output_folder, aprx_name))
    m = aprx.listMaps(map_name)[0]
    arcpy.env.workspace = os.path.join(output_folder, output_gdb)
    arcpy.env.overwriteOutput = True

    # TODO: maybe do an initial table comparison to see if anything has actually changed??

    # for each layer, do feature class to feature class
    log("Creating feature classes from services")
    for layer_id in input_layers_list:
        arcpy.MakeFeatureLayer_management(os.path.join(input_service_url, str(layer_id)),"tmp")
        arcpy.conversion.FeatureClassToFeatureClass("tmp", os.path.join(output_folder, output_gdb), input_layers_list[layer_id])

    # add projected layers to map and remove old ones
    for lyr in m.listLayers():
        if lyr.name != "Manage_Tile_Cache_Area_of_Interest_Polygons":
            log(f"Removing {lyr.name} from the map")
            m.removeLayer(lyr)

    # remove files before overwriting
    log("Removing files from gdb")
    for layer_id in input_layers_list:
        cleanup_files(os.path.join(output_folder, output_gdb, f"{input_layers_list[layer_id]}_Project"))

    # project from 26985 to 3857
    log("Projecting new service versions to the correct projection")
    input_project_str = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]"
    projection = "WGS_1984_(ITRF00)_To_NAD_1983"
    output_project_str = "PROJCS['NAD_1983_StatePlane_Maryland_FIPS_1900',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.0],PARAMETER['Standard_Parallel_1',38.3],PARAMETER['Standard_Parallel_2',39.45],PARAMETER['Latitude_Of_Origin',37.66666666666666],UNIT['Meter',1.0]]"

    for layer_id in input_layers_list:
        arcpy.management.Project(input_layers_list[layer_id], os.path.join(output_folder, output_gdb, f"{input_layers_list[layer_id]}_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")

    for layer_id in input_layers_list:
        m.addDataFromPath(os.path.join(output_folder, output_gdb, f"{input_layers_list[layer_id]}_Project"))

    # log layers present in map and apply symbology
    log("Applying symbology and ensuring all new layers are present in map")
    for lyr, lyrx in zip(m.listLayers(), layer_files):
        arcpy.ApplySymbologyFromLayer_management(lyr, os.path.join(output_folder, lyrx))
        log(lyr.name)

    # TODO: remove minimum scale and make visible

    # manage tile cache
    log("Running manage tile cache")
    with arcpy.EnvManager(parallelProcessingFactor="75%"):
        arcpy.management.ManageTileCache(output_folder, "RECREATE_ALL_TILES", output_service_name, m, "ARCGISONLINE_SCHEME", None, [72223.819286, 36111.909643, 18055.954822, 9027.977411, 4513.988705, 2256.994353, 1128.497176, 564.248588], "Manage_Tile_Cache_Area_of_Interest_Polygons", None, 591657527.591555, 70.5310735)

    # export tile cache
    log("Running export tile cache")
    with arcpy.EnvManager(parallelProcessingFactor="75%"):
        arcpy.management.ExportTileCache(os.path.join(output_folder, output_service_name, map_name), os.path.join(output_folder, cache_name), output_service_name, "TILE_PACKAGE_TPKX", "COMPACT_V2", [72223.819286, 36111.909643, 18055.954822, 9027.977411, 4513.988705, 2256.994353, 1128.497176, 564.248588, 282.124294, 141.062147], r"in_memory\feature_set1")

    # share package/ replace tile cache
    log("Running share package")
    out_results, package_json_str, new_tpkx_id = arcpy.management.SharePackage(os.path.join(output_folder, cache_name, f"{output_service_name}.tpkx"), '', None, "test", "test", '', "MYGROUPS", None, "MYORGANIZATION", "TRUE", '')
    package_item_dict = json.loads(package_json_str)
    new_tile_service_id = package_item_dict["publishResult"]["serviceItemId"]
    log(f"New tile service ID: {new_tile_service_id}")

    # Log in to AGOL
    pw = keyring.get_password(keyring_id, org_username)
    gis = arcgis.gis.GIS(org_url, org_username, pw)

    # Remove archives from 1 hour + ago
    # curr_timestamp = time.strftime("%Y%m%d")
    gis_items = gis.content.search("title:archive_ AND owner:{}".format(org_username), item_type="Map Image Layer")
    # If there are more than one archived services
    if len(gis_items) > 1:
        for item in gis_items:
            match = re.search("archive_[0-9]{8}_[0-9]{4}", item.title)
            if match:
                log(f"Deleting old archive: {item.title}")
                item.delete()

    # Archive old service
    try:
        arcpy.ReplaceWebLayer_server(target_tile_service_id, "archive_" + time.strftime("%Y%m%d_%H%M"), new_tile_service_id)
    except Exception:
        log("Could not replace archive")

    # update item
    item = gis.content.get(target_tpkx_id)
    item.update(data=os.path.join(output_folder, cache_name, f"{output_service_name}.tpkx"))


if __name__ == '__main__':
    main()
