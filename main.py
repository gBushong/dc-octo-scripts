import arcpy
import os


output_folder = r"C:\Users\grac9792\Documents\ArcGIS\Projects\DC OCTO"
output_gdb = "DC OCTO.gdb"


def main():
    # create map?
    # add data to map

    # for each layer, do feature class to feature class
    # (New name replace spaces and hyphens with underscores)
    arcpy.conversion.FeatureClassToFeatureClass("High Flow Hydrants", os.path.join(output_folder, output_gdb), "High_Flow_Hydrants")
    arcpy.conversion.FeatureClassToFeatureClass("New Standard Hydrants", os.path.join(output_folder, output_gdb), "New_Standard_Hydrants")
    arcpy.conversion.FeatureClassToFeatureClass("Not Flow Tested", os.path.join(output_folder, output_gdb), "Not_Flow_Tested")
    arcpy.conversion.FeatureClassToFeatureClass("Non-Working Hydrants", os.path.join(output_folder, output_gdb), "Non_Working_Hydrants")
    arcpy.conversion.FeatureClassToFeatureClass("Old Standard Hydrants", os.path.join(output_folder, output_gdb), "Old_Standard_Hydrants")

    # change symbology

    # project from 26985 to 3857
    # re-project map? Not sure how to change via code
    input_project_str = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]"
    projection = "WGS_1984_(ITRF00)_To_NAD_1983"
    output_project_str = "PROJCS['NAD_1983_StatePlane_Maryland_FIPS_1900',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.0],PARAMETER['Standard_Parallel_1',38.3],PARAMETER['Standard_Parallel_2',39.45],PARAMETER['Latitude_Of_Origin',37.66666666666666],UNIT['Meter',1.0]]"
    arcpy.management.Project("High_Flow_Hydrants", os.path.join(output_folder, output_gdb, "High_Flow_Hydrants_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
    arcpy.management.Project("New Standard Hydrants", os.path.join(output_folder, output_gdb, "New_Standard_Hydrants_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
    arcpy.management.Project("Not Flow Tested", os.path.join(output_folder, output_gdb, "Not_Flow_Tested_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
    arcpy.management.Project("Non-Working Hydrants", os.path.join(output_folder, output_gdb, "Non_Working_Hydrants_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
    arcpy.management.Project("Old Standard Hydrants", os.path.join(output_folder, output_gdb, "Old_Standard_Hydrants_Project"), input_project_str, projection, output_project_str, "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")

    # remove minimum scale and make visible
    # edit alias to remove underscores

    # sign in

    # manage tile cache
    # tiling scheme: WGS1984, 12-21
    arcpy.management.ManageTileCache(output_folder, "RECREATE_ALL_TILES", "RECREATE_ALL_TILES_AGOL", "FEMS Awareness Viewer", "ARCGISONLINE_SCHEME", None, "9027.977411;4513.988705;2256.994353;1128.497176;564.248588;282.124294;141.062147", r"in_memory\feature_set1", None, 9027.977411, 141.062147)

    # export tile cache
    arcpy.management.ExportTileCache("FEMS Awareness Viewer", os.path.join(output_folder, "FEMS Awareness Viewer Cache"), "CACHE_AGOL", "TILE_PACKAGE_TPKX", "COMPACT_V2", [9027.977411, 4513.988705, 2256.994353, 1128.497176, 564.248588, 282.124294, 141.062147], r"in_memory\feature_set1")

    # share package/ replace tile cache
    arcpy.management.SharePackage(os.path.join(output_folder, r"FEMS Awareness Viewer Cache\CACHE_AGOL.tpkx"), '', None, "test", "t", '', "MYGROUPS", None, "MYORGANIZATION", "TRUE", '')


if __name__ == '__main__':
    main()
