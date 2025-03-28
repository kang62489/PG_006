## Author: Kang
## Last Update: 2025-Mar-28
## Purpose: To flatten and fit the temporal sequences derived from the preprocessed images (truncate and crop)

## Modules
import os
import glob
import pandas as pd
import numpy as np
import imageio.v3 as imageio
from scipy.optimize import *
from scipy import interpolate as interp
from pathlib import Path as pt
from sklearn.metrics import r2_score
from pathlib import Path
from rich import print
from tabulate import tabulate
from PySide6.QtWidgets import QApplication
from classes.plot_results import PlotResults

## File I/O
preprocessed_imaging_sequences_path = Path(__file__).parent / "Outputs"
export_path = Path(__file__).parent / "Outputs"
if not os.path.exists(export_path):
    os.mkdir(export_path)

## Sampling Rates: 50 ms = 20 Hz
fs = 20

## Convert frames to time
cut_start = 10
cut_end = 400
frame_start = cut_start + 1
frame_end = cut_end + 1
time = (np.arange(frame_start, frame_end))/fs

## Pick up folders of images for analysis
lst_ROI_sizes = ["512"]
for ROI in lst_ROI_sizes:
    lst_preprossed_folders_ACSF = [f for f in next(os.walk(os.path.join(preprocessed_imaging_sequences_path)))[1] if ("Preprocessed"  in f) & (ROI in f) & ("ACSF" in f)]
    lst_preprossed_folders_NEO = [f for f in next(os.walk(os.path.join(preprocessed_imaging_sequences_path)))[1] if ("Preprocessed"  in f) & (ROI in f) & ("NEO" in f)]

for folder_ACSF, folder_NEO in zip(lst_preprossed_folders_ACSF, lst_preprossed_folders_NEO):
    lst_files_ACSF =glob.glob(os.path.join(preprocessed_imaging_sequences_path, folder_ACSF,"*.tif"))
    lst_files_NEO = glob.glob(os.path.join(preprocessed_imaging_sequences_path, folder_NEO,"*.tif"))

print("number of files in ACSF: ", len(lst_files_ACSF))
print(lst_files_ACSF)

print("number of files in NEO: ", len(lst_files_NEO))
print(lst_files_NEO)

## Prepare empty dataframes for saving converted data
raw_ACSF = pd.DataFrame()
raw_NEO = pd.DataFrame()


## Insert time seqence for easily ploting in the output excel file_ACSF
raw_ACSF['Time'] = time
raw_NEO['Time'] = time

## Load every imaging sequence and calculate average of each frame
## Store each temporal sequence in each column of corresponding dataframe
for file_ACSF, file_NEO in zip(lst_files_ACSF, lst_files_NEO):
    im_ACSF = imageio.imread(file_ACSF)
    im_NEO = imageio.imread(file_NEO)
    
    im_ACSF_temporal = im_ACSF.mean(axis=(1,2))
    im_NEO_temporal = im_NEO.mean(axis=(1,2))

    raw_ACSF['_'.join(pt(os.path.basename(file_ACSF)).stem.split("_")[2:6])]=im_ACSF_temporal
    raw_NEO['_'.join(pt(os.path.basename(file_NEO)).stem.split("_")[2:6])]=im_NEO_temporal
    
# Fitting and Plotting
# fitting model: B-Spline

# Prepare empty dataframes for saving fitted data
fitted_ACSF = pd.DataFrame()
fitted_NEO = pd.DataFrame()

# Insert time seqence for easily ploting in the output excel file_ACSF
fitted_ACSF['Time'] = time
fitted_NEO['Time'] = time


# Masking the frames of ONSET of the puffing (100 frames, 5 seconds)
mask_start = 90
mask_end = 190
masked_ACSF = raw_ACSF.loc[(raw_ACSF["Time"]<mask_start*0.05) | (raw_ACSF["Time"]>= mask_end*0.05)]
masked_NEO = raw_NEO.loc[(raw_NEO["Time"]<mask_start*0.05) | (raw_NEO["Time"]>= mask_end*0.05)]

# Define parameters for B-Spline
knots = 21
xdata_new = np.linspace(0,1,knots+2)[1::4]
xdata = masked_ACSF["Time"]
q_knots = np.quantile(xdata, xdata_new)
smooth = 3

for col_ACSF, col_NEO in zip(raw_ACSF.columns[1:], raw_NEO.columns[1:]):
    ydata_1 = masked_ACSF[col_ACSF]
    popt_1 = interp.splrep(xdata, ydata_1, t = q_knots, s=smooth)
    baseline_1 = interp.BSpline(*popt_1, extrapolate=True)
    print(f"{col_ACSF} R-Square:", r2_score(ydata_1, baseline_1(xdata)))
    
    ydata_2 = masked_NEO[col_NEO]
    popt_2 = interp.splrep(xdata, ydata_2, t = q_knots, s=smooth)
    baseline_2 = interp.BSpline(*popt_2, extrapolate=True)
    print(f"{col_NEO} R-Square:", r2_score(ydata_2, baseline_2(xdata)))

    fitted_ACSF[col_ACSF] = baseline_1(time)
    fitted_NEO[col_NEO] = baseline_2(time)
    print("\nDATA ", col_ACSF, "and ", col_NEO, "are fitted")
    print("============================================================")


original_puffing_frame = 101

original_puffing_timepoint = original_puffing_frame/fs

raw_ACSF["Time"] = raw_ACSF["Time"] - original_puffing_timepoint
raw_NEO["Time"] = raw_NEO["Time"] - original_puffing_timepoint
fitted_ACSF["Time"] = fitted_ACSF["Time"] - original_puffing_timepoint
fitted_NEO["Time"] = fitted_NEO["Time"] - original_puffing_timepoint

set_dfs = {}
set_dfs["raw_ACSF"] = raw_ACSF
set_dfs["raw_NEO"] = raw_NEO
set_dfs["fitted_ACSF"] = fitted_ACSF
set_dfs["fitted_NEO"] = fitted_NEO

# Save the results to analysis.xlsx
with pd.ExcelWriter(os.path.join(export_path,'analysis.xlsx')) as f:
    raw_ACSF.to_excel(f,sheet_name="raw_ACSF",index=False)
    raw_NEO.to_excel(f,sheet_name='raw_NEO',index=False)
    
    fitted_ACSF.to_excel(f,sheet_name="fitted_ACSF",index=False)
    fitted_NEO.to_excel(f,sheet_name="fitted_NEO",index=False)

# Plotting
app = QApplication()
window = PlotResults(set_dfs, title_left="ACh puffed in Normal ACSF solution", title_right="ACh puffed in NEO presented ACSF solution",
                     xlabel='time (sec.)', ylabel='counts')

window.show()
app.exec()
