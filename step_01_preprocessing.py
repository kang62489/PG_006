## Author: Kang
## Last Update: 2025-Jan-27
## Purpose: To analyze the specificity of the iAChSnFR and Integrate the old codes

# Modules
import os
import sys
import pandas as pd
from pathlib import Path
from tabulate import tabulate
from rich import print
from classes.dialog_confirm import Confirm
from PySide6.QtWidgets import QApplication

from functions.truncate_and_crop import truncate_and_crop

# Set event handler
app = QApplication(sys.argv)

# Set the paths
data_path = "E:/PRO_iAChSnFR_Specificity/Raw"
export_path = Path(__file__).parent / "Outputs"

# Select data by date
dateSets = ["2023_10_05","2023_10_12","2024_03_07","2024_03_22"]

# Read summary csv files for getting all information of recording files of the selected folders
dfs = []
for date in dateSets:
    filename = "{}_summary.csv".format(date)
    print(filename)
    df_temp = pd.read_csv(os.path.join(data_path, date, filename))
    dfs.append(df_temp)
    print(tabulate(df_temp, headers='keys', tablefmt='pretty'))
    
# Find the files fit the conditions in each date of folders
# Conditions:
# PUFF_PERIOD = 30 ms
# PUFF_COUNT = 1
# BATH_IN = ACSF, NEO

df_ACSF = pd.DataFrame()
df_NEO = pd.DataFrame()
for df in dfs:
    filtered = df[(df["PUFF_COUNT"]==1) & (df["PUFF_PERIOD"]=="30ms") & (df["BATH_IN"] != 'NEO')]
    filtered_NEO = df[(df["PUFF_COUNT"]==1) & (df["PUFF_PERIOD"]=="30ms") & (df["BATH_IN"] == 'NEO')]

    df_ACSF = pd.concat([df_ACSF, filtered]).reset_index(drop=True)   
    df_NEO = pd.concat([df_NEO, filtered_NEO]).reset_index(drop=True)

print(tabulate(df_ACSF, headers='keys', tablefmt='pretty'))
print(tabulate(df_NEO, headers='keys', tablefmt='pretty'))

# Save the filtered files to text files
if not os.path.exists(export_path):
    os.mkdir(export_path)

with open(export_path / "pickedFiles_All.txt", "w") as f:
    f.write("Files which puffed ACh 30 ms for 1 time(s) and bathed in ACSF\n")
    f.write(tabulate(df_ACSF, headers='keys', tablefmt='simple'))
    f.write("\n\n")
    dividing_line = "="*(df_ACSF.shape[1]*12)
    f.write(dividing_line +"\n\n")
    f.write("Files which puffed ACh 30 ms for 1 time(s) and bathed in NEO\n")
    f.write(tabulate(df_NEO, headers='keys', tablefmt='simple'))
    
# Truncate and crop the imaging files
# Load and trim the files
cut_start = 10
cut_end = 400
ROI_sizes = [512]
center_x = 1792
center_y = 1024

for r in ROI_sizes:
    output_foldername = ["Preprocessed_ACSF_"+str(r),"Preprocessed_NEO_"+str(r)]
    ROI_coords = [int(center_y-(r/2)), int(center_y+(r/2)), int(center_x-(r/2)), int(center_x+(r/2))]
    for outdir in output_foldername:
        # Check if preprocessing folder exists
        if os.path.exists(export_path / outdir):
            title = "Warning"
            message = f"Folder {outdir} already exists. Do you want to continue the process?"
            dlg_checkContinue = Confirm(title, message)
            if dlg_checkContinue.exec():
                truncate_and_crop(dateSets, output_foldername, data_path, export_path, df_ACSF, df_NEO, ROI_coords, cut_start, cut_end, r)
            else:
                print(f"Preprocessing has been canceled or skipped.")
                break
        else:
            truncate_and_crop(dateSets, output_foldername, data_path, export_path, df_ACSF, df_NEO, ROI_coords, cut_start, cut_end, r)
