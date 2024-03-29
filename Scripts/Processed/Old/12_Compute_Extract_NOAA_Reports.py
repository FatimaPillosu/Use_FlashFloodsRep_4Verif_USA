import os
import numpy as np
import pandas as pd

###########################################################################
# CODE DESCRIPTION
# 12_Compute_Extract_NOAA_Reports.py extracts the flash flood reports from the NOAA 
# database, and manipulates the raw data to make it suitable for subsequent analysis:
#     - eliminates reports with no lat/lon coordinates or reporting date/time;
#     - indentify the flash flood affected areas: four new columns are created 
#        "AREA_AFFECTED_CENTRE_LAT", "AREA_AFFECTED_CENTRE_LON", 
#        "AREA_AFFECTED_LENGTH", and "AREA_AFFECTED_WIDTH";
# Runtime: the code takes up to 2 minutes to run in serial.

# INPUT PARAMETERS DESCRIPTION
# YearS (integer, in the YYYY format): start year for the flood reports to consider.
# YearF (integer, in the YYYY format): final year for the flood reports to consider.
# Git_Repo (string): repository's local path
# DirIN (string): relative path where USA's mask can be found
# DirOUT (string): relative path where to store the plot 

# INPUT PARAMETERS
YearS = 1950
YearF = 2023
Git_Repo = "/ec/vol/ecpoint_dev/mofp/Papers_2_Write/Use_FlashFloodsRep_4Verif_USA"
DirIN = "Data/Raw/OBS/NOAA_Rep"
DirOUT = "Data/Compute/12_Extract_NOAA_Rep"
###########################################################################


# Setting the main input/output directories
MainDirIN = Git_Repo + "/" + DirIN
MainDirOUT = Git_Repo + "/" + DirOUT
if not os.path.exists(MainDirOUT):
    os.makedirs(MainDirOUT)

# Creating the variable where to store the total number of reports per year
years_rep = []
num_rep_all = []
num_rep_ff = []

# Post-processing the raw flood reports
ff_all = pd.DataFrame()
for Year in range(YearS,YearF+1):
      
      print("Post-processing the reports for " + str(Year))
      
      # Reading the raw flood reports
      string2find = "d" + str(Year) + "_"
      FileIN = [f for f in os.listdir(MainDirIN) if string2find in f and os.path.isfile(os.path.join(MainDirIN, f))]
      df = pd.read_csv(Git_Repo + "/" + DirIN + "/" + FileIN[0], low_memory=False)
      df = df.dropna(subset=["BEGIN_DATE_TIME", "END_DATE_TIME", "BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON"])
      
      # Extracting reports for flash floods and surface runoff
      ff = df[df["EVENT_TYPE"].isin(["Flash Flood", "Tornado", "Flood", "Coastal Flood", "Heavy Rain", "Hurricane/Typhoon", "Tropical Storm"])]
      ff = ff.reset_index(drop=True)  # to reset the indexes of the new dataframe

      # Removing reports with no lat/lon coordinates or no reporting date/time
      ff = ff.dropna(subset=["BEGIN_DATE_TIME", "END_DATE_TIME", "BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON"])
      num_rows_ff = ff.shape[0]
      
      # Saving some metadata
      years_rep.append(Year)
      num_rep_all.append(df.shape[0])

      if num_rows_ff != 0:

            # Adding the new columns to the dataset
            ff["AREA_AFFECTED_CENTRE_LAT"] = np.nan
            ff["AREA_AFFECTED_CENTRE_LON"] = np.nan
            ff["AREA_AFFECTED_LENGTH"] = np.nan
            ff["AREA_AFFECTED_WIDTH"] = np.nan
            ff["NEAREST_DOMAIN_GRIDBOX_CENTRE_LAT"] = np.nan
            ff["NEAREST_DOMAIN_GRIDBOX_CENTRE_LON"] = np.nan
            ff["NEAREST_DOMAIN_GRIDBOX_WEST"] = np.nan
            ff["NEAREST_DOMAIN_GRIDBOX_EAST"] = np.nan
            ff["NEAREST_DOMAIN_GRIDBOX_NORTH"] = np.nan
            ff["NEAREST_DOMAIN_GRIDBOX_SOUTH"] = np.nan

            # Setting the values for the new columns
            for ind_row in range(num_rows_ff): 

                  # Extracting the reports' lat/lon coordinates
                  begin_lat = ff["BEGIN_LAT"].iloc[ind_row]
                  begin_lon = ff["BEGIN_LON"].iloc[ind_row]
                  end_lat = ff["END_LAT"].iloc[ind_row]
                  end_lon = ff["END_LON"].iloc[ind_row]
                  
                  # Computing the centre and the length/width of the area affected by a flash flood
                  area_affected_centre_lat = (begin_lat + end_lat) / 2
                  ff.loc[ind_row, "AREA_AFFECTED_CENTRE_LAT"] = area_affected_centre_lat
                  area_affected_centre_lon = ( (begin_lon + end_lon) / 2 ) + 360
                  ff.loc[ind_row, "AREA_AFFECTED_CENTRE_LON"] = area_affected_centre_lon
                  area_affected_length = abs(end_lat - begin_lat)
                  ff.loc[ind_row, "AREA_AFFECTED_LENGTH"] = area_affected_length
                  area_affected_width = abs(end_lon - begin_lon)
                  ff.loc[ind_row, "AREA_AFFECTED_WIDTH"] = area_affected_width

            # Extract all the rows from certain columns to streamline the dataset
            reduced_ff = ff[["EVENT_ID", "STATE", "CZ_TIMEZONE", "SOURCE", "EVENT_TYPE", "FLOOD_CAUSE", "BEGIN_DATE_TIME", "END_DATE_TIME", "BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON", "AREA_AFFECTED_CENTRE_LAT", "AREA_AFFECTED_CENTRE_LON", "AREA_AFFECTED_LENGTH", "AREA_AFFECTED_WIDTH"]]
            
            # Merging the reports from all the years
            ff_all = pd.concat([ff_all, reduced_ff], ignore_index=True)

            # Saving some metadata
            num_rep_ff.append(num_rows_ff)
            print(num_rows_ff)

      else:

            num_rep_ff.append(0)

# Saving the database with only flash flood reports and some metadata
FileOUT = MainDirOUT + "/FlashFloodRep.csv"
ff_all.to_csv(FileOUT, index=False)

FileOUT = MainDirOUT + "/years_rep"
np.save(FileOUT, years_rep)

FileOUT = MainDirOUT + "/num_rep_all"
np.save(FileOUT, num_rep_all)

FileOUT = MainDirOUT + "/num_rep_ff"
np.save(FileOUT, num_rep_ff)