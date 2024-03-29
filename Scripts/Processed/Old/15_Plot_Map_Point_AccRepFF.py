import os
import sys
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import metview as mv

#######################################################################################
# CODE DESCRIPTION
# 15_Plot_Map_Point_AccRepFF.py plots the accumulated point flash flood reports over a specific 
# accumulation period.
# Runtime: The code takes up to 60 minutes to run in serial mode.

# INPUT PARAMETERS DESCRIPTION
# Year (year, in YYYY format): year to consider.
# Acc (integer, in hours): accumulation period.
# Disc_Acc (integer, in hours): discretization for the accumulation peiods to consider.
# Mask_Domain (list of floats, in S/W/N/E coordinates): domain's coordinates.
# Git_Repo (string): repository's local path.
# FileIN_Mask (string): relative path where the USA's mask is stored.
# DirIN (string): relative path where the accumulated reports are stored.
# DirOUT (string): relative path where to store the map plots. 

# INPUT PARAMETERS
Year = int(sys.argv[1])
Acc = 12
Disc_Acc = 12
Mask_Domain = [22,-130,52,-60]
Git_Repo = "/ec/vol/ecpoint_dev/mofp/Papers_2_Write/Use_FlashFloodsRep_4Verif_USA"
FileIN_Mask = "Data/Raw/Mask/USA_ENS_18km/Mask.grib"
DirIN = "Data/Compute/14_Point_AccRepFF"
DirOUT = "Data/Plot/15_Map_Point_AccRepFF"
#######################################################################################


# Reading the domain's mask
mask = mv.read(Git_Repo + "/" + FileIN_Mask)

# Convert the domain's mask into a geopoint
mask_vals = mv.values(mask)
mask_lats = mv.latitudes(mask)
mask_lons = mv.longitudes(mask)

mask_lats = mv.filter(mask_lats, mask_vals == 1)
mask_lons = mv.filter(mask_lons, mask_vals == 1)
mask_vals = mv.filter(mask_vals, mask_vals == 1) - 2 # to assign the value -1 to the domain's grid points 

mask_geo = mv.create_geo(type = "xyv",
      latitudes = mask_lats,
      longitudes = mask_lons,
      values = mask_vals
      )

# Plotting the reports for specific accumulation periods
print()
print("Plotting the maps of accumulated point flash flood reports over the " + str(Acc) + "-hourly period ending:")

DateTime_Start_S = datetime(Year,1,1,0)
DateTime_Start_F = datetime(Year,12,31,12)

TheDateTime_Start = DateTime_Start_S
while TheDateTime_Start <= DateTime_Start_F:

      TheDateTime_Final = TheDateTime_Start + timedelta(hours=Acc)
      print(" - on " + TheDateTime_Final.strftime("%Y-%m-%d") + " at " + TheDateTime_Final.strftime("%H") + " UTC")
      
      # Reading the reports 
      FileIN = Git_Repo + "/" + DirIN + "/" + TheDateTime_Final.strftime("%Y") + "/" + TheDateTime_Final.strftime("%Y%m%d") + "/FlashFloodRep_" + TheDateTime_Final.strftime("%Y%m%d%H") + ".csv"
      if os.path.exists(FileIN):
            
            ff = pd.read_csv(FileIN)
            
            # Creating the geopoints that contain the reports
            lats = ff["AREA_AFFECTED_CENTRE_LAT"].values
            lons = ff["AREA_AFFECTED_CENTRE_LON"].values

            ff_geo = mv.create_geo(type = "xyv",
                              latitudes = lats,
                              longitudes = lons,
                              values = np.zeros(len(lats))
                              )
            
            # Plotting the reports
            coastlines = mv.mcoast(
                  map_coastline_colour = "charcoal",
                  map_coastline_thickness = 1,
                  map_coastline_resolution = "high",
                  map_coastline_sea_shade = "on",
                  map_coastline_sea_shade_colour = "RGB(0.7398,0.9465,0.943)",
                  map_boundaries = "on",
                  map_boundaries_colour = "charcoal",
                  map_boundaries_thickness = 1,
                  map_grid_latitude_increment = 5,
                  map_grid_longitude_increment = 10,
                  map_label_right = "off",
                  map_label_top = "off",
                  map_label_colour = "charcoal",
                  map_grid_thickness = 1,
                  map_grid_colour = "charcoal",
                  map_label_height = 0.5
                  )
            
            geo_view = mv.geoview(
                  map_projection = "epsg:3857",
                  map_area_definition = "corners",
                  area = Mask_Domain,
                  coastlines = coastlines
                  )
            
            symb_points = mv.msymb(
                  legend = "off",
                  symbol_type = "marker",
                  symbol_table_mode = "on",
                  symbol_outline = "on",
                  symbol_min_table = [-0.1],
                  symbol_max_table = [0.1],
                  symbol_colour_table = "red",
                  symbol_marker_table = 15,
                  symbol_height_table = 0.5
                  )

            symb_gridpoints = mv.msymb(
                  legend = "off",
                  symbol_type = "marker",
                  symbol_table_mode = "on",
                  symbol_outline = "on",
                  symbol_min_table = [-1.1],
                  symbol_max_table = [-0.9],
                  symbol_colour_table = "rgb(0.8,0.8,0.8)",
                  symbol_marker_table = 15,
                  symbol_height_table = 0.1
                  )

            title = mv.mtext(
                  text_line_count = 2,
                  text_line_1 = "Point flood reports accumulated over the " + str(Acc) + "-hourly period ending on " + TheDateTime_Final.strftime("%Y-%m-%d") + " at " + TheDateTime_Final.strftime("%H") + " UTC",
                  text_line_2 = " ",
                  text_colour = "charcoal",
                  text_font = "arial",
                  text_font_size = 0.6
                  )

            # Saving the plot
            MainDirOUT = Git_Repo + "/" + DirOUT + "/" + str(Year) + "/" + TheDateTime_Final.strftime("%Y%m%d") 
            if not os.path.exists(MainDirOUT):
                  os.makedirs(MainDirOUT)
            FileOUT = MainDirOUT + "/FlashFloodRep_" + TheDateTime_Final.strftime("%Y%m%d%H")
            png = mv.png_output(output_name = FileOUT)
            mv.setoutput(png)
            mv.plot(geo_view, mask_geo, symb_gridpoints, ff_geo, symb_points, title)

      TheDateTime_Start = TheDateTime_Start + timedelta(hours=Disc_Acc)