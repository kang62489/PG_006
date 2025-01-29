# Author: Kang
# Last Update: 2024-Apr-15

# Initialization
import os, shutil
import pandas as pd
import numpy as np
import skimage.io as skio

data_path = "D:\\Research\\Gideon\\Raw Data"
export_path = "D:\\PhD Thesis\\Mtg_WD\\2024-10-21"

# Select data by date
dateSets = ["2023_10_05","2023_10_12","2024_03_07","2024_03_22"]

# Get rec data info by read JSONs
n = 1
dfs = []
for date in dateSets:
    filename = "{}_REC summary_updated.json".format(date)
    print(filename)
    df_temp = pd.read_json(os.path.join(data_path, date, "notes", filename))
    dfs.append(df_temp)
    

# Find the files fit the conditions in each date of folders
pickedFiles = []
pickedFiles_NEO = []
for df in dfs:
    filtered = df[(df["P.Pulses"]==1) & (df["P.Period"]=="30ms") & (df["Bathed_with"] != 'NEO')]
    filtered_NEO = df[(df["P.Pulses"]==1) & (df["P.Period"]=="30ms") & (df["Bathed_with"] == 'NEO')]

    print("Files which puffing = 30 ms pulses = 1 Bathing = None: \n", filtered )
    print("======================================================================\n")
    print("Files which puffing = 30 ms pulses = 1 Bathing = NEO: \n", filtered_NEO )
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    pickedFiles = pickedFiles + (filtered["Filename"].values).tolist()
    pickedFiles_NEO = pickedFiles_NEO + (filtered_NEO["Filename"].values).tolist()

# Load and trim the files
# 
cut_start = 10
cut_end = 400
ROI_sizes = [512]
location_x = 1792
location_y = 1024

for r in ROI_sizes:
    output_foldername = ["output_"+str(r),"output_NEO_"+str(r)]
    ROI_coords = [int(location_y-(r/2)), int(location_y+(r/2)), int(location_x-(r/2)), int(location_x+(r/2))]
    for out in output_foldername:
        if os.path.isdir(os.path.join(export_path, out)):
            shutil.rmtree(os.path.join(export_path, out))
            os.mkdir(os.path.join(export_path, out))
        else:
            os.mkdir(os.path.join(export_path, out))

        if "NEO" in out:
            filelist = pickedFiles_NEO
        else:
            filelist = pickedFiles

        for date in dateSets:
            filenames = [s for s in filelist if date in s]
            for filename in filenames:
                im = skio.imread(os.path.join(data_path,date,filename), plugin="tifffile")
                skio.imsave(os.path.join(export_path,out,"ROI_{}_".format(r)+filename),im[cut_start:cut_end,ROI_coords[0]:ROI_coords[1],ROI_coords[2]:ROI_coords[3]], plugin="tifffile", check_contrast=False)
                print(filename, " saved!!")