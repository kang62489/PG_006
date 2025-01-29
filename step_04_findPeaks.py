## Author: Kang
## Last Update: 2025-Jan-29
## Purpose: Find peaks from curves of delta F/F0, zscored delta F/F0

import os
import glob
from unittest import result
import openpyxl
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from rich import print
from PySide6.QtWidgets import QApplication
from classes.dialog_getPath import GetPath
from classes.plot_results import PlotResults


# Set event handler
app = QApplication()

# Get the path of the excel file
xlsx_filepath = GetPath(title="Please select the processed data of a xlsx file.",
                        filemode="file",
                        filetype="excel")
xlsx_filepath = xlsx_filepath.get_path()

# Check if the file has necessary sheets
wb = openpyxl.load_workbook(xlsx_filepath)
loaded = [False, False, False, False]
if 'dfF0_ACSF' in wb.sheetnames:
    loaded[0] = True
    if 'dfF0_NEO' in wb.sheetnames:
        loaded[1] = True
        if 'dfF0_ACSF_cal_zscores' in wb.sheetnames:
            loaded[2] = True
            if 'dfF0_NEO_cal_zscores' in wb.sheetnames:
                loaded[3] = True
            else:
                print("The sheet dfF0_NEO_cal_zscores is not exist in the file. Please check the file.")
        else:
            print("The sheet dfF0_ACSF_cal_zscores is not exist in the file. Please check the file.")
    else:
        print("The sheet dfF0_NEO is not exist in the file. Please check the file.")
else:
    print("The sheet dfF0_ACSF is not exist in the file. Please check the file.")

dfF0_ACSF = pd.read_excel(xlsx_filepath, sheet_name="dfF0_ACSF")
dfF0_NEO = pd.read_excel(xlsx_filepath, sheet_name="dfF0_NEO")
dfF0_ACSF_cal_zscores = pd.read_excel(xlsx_filepath, sheet_name="dfF0_ACSF_cal_zscores")
dfF0_NEO_cal_zscores = pd.read_excel(xlsx_filepath, sheet_name="dfF0_NEO_cal_zscores")

frames, columns = dfF0_ACSF.shape 
columns_data = columns - 1
search_range = 30
start_frame = frames - 300
set_peaks = pd.DataFrame()

ACSF_peakValue = []
ACSF_peakTime = []
for col in dfF0_ACSF.columns[1:]:
    seg_data = np.array(dfF0_ACSF[col][start_frame:start_frame+search_range])
    seg_time = np.array(dfF0_ACSF["Time"][start_frame:start_frame+search_range])
    peaks_idx, properties = find_peaks(seg_data, distance=30)

    if peaks_idx.size == 0:
        print("No peaks are found in", col)
    else:
        ACSF_peakValue.append(seg_data[peaks_idx][0])
        ACSF_peakTime.append(seg_time[peaks_idx][0])
        
set_peaks['ACSF_peakTime'] = ACSF_peakTime
set_peaks['ACSF_peakValue'] = ACSF_peakValue

NEO_peakValue = []
NEO_peakTime = []
for col in dfF0_NEO.columns[1:]:
    seg_data = np.array(dfF0_NEO[col][start_frame:start_frame+search_range])
    seg_time = np.array(dfF0_NEO["Time"][start_frame:start_frame+search_range])
    peaks_idx, properties = find_peaks(seg_data, distance=30)

    if peaks_idx.size == 0:
        print("No peaks are found in", col)
    else:
        NEO_peakValue.append(seg_data[peaks_idx][0])
        NEO_peakTime.append(seg_time[peaks_idx][0])
        
set_peaks['NEO_peakTime'] = NEO_peakTime
set_peaks['NEO_peakValue'] = NEO_peakValue


ACSF_cal_zscores_peakValue = []
ACSF_cal_zscores_peakTime = []
for col in dfF0_ACSF_cal_zscores.columns[1:]:
    seg_data = np.array(dfF0_ACSF_cal_zscores[col][start_frame:start_frame+search_range])
    seg_time = np.array(dfF0_ACSF_cal_zscores["Time"][start_frame:start_frame+search_range])
    peaks_idx, properties = find_peaks(seg_data, distance=30)

    if peaks_idx.size == 0:
        print("No peaks are found in", col)
    else:
        ACSF_cal_zscores_peakValue.append(seg_data[peaks_idx][0])
        ACSF_cal_zscores_peakTime.append(seg_time[peaks_idx][0])

set_peaks['ACSF_cal_zscores_peakTime'] = ACSF_cal_zscores_peakTime
set_peaks['ACSF_cal_zscores_peakValue'] = ACSF_cal_zscores_peakValue


NEO_cal_zscores_peakValue = []
NEO_cal_zscores_peakTime = []

for col in dfF0_NEO_cal_zscores.columns[1:]:
    seg_data = np.array(dfF0_NEO_cal_zscores[col][start_frame:start_frame+search_range])
    seg_time = np.array(dfF0_NEO_cal_zscores["Time"][start_frame:start_frame+search_range])
    peaks_idx, properties = find_peaks(seg_data, distance=30)

    if peaks_idx.size == 0:
        print("No peaks are found in", col)
    else:
        NEO_cal_zscores_peakValue.append(seg_data[peaks_idx][0])
        NEO_cal_zscores_peakTime.append(seg_time[peaks_idx][0])
        
set_peaks['NEO_cal_zscores_peakTime'] = NEO_cal_zscores_peakTime
set_peaks['NEO_cal_zscores_peakValue'] = NEO_cal_zscores_peakValue

# Save the peaks to the xlsx file
wb = openpyxl.load_workbook(xlsx_filepath)
if 'all_peaks' in wb.sheetnames:
    del wb['all_peaks']
    wb.save(xlsx_filepath)
    
with pd.ExcelWriter(xlsx_filepath, mode="a") as f:
    set_peaks.to_excel(f, sheet_name="all_peaks", index=False)
    print("The peaks are saved into the file.")

set_df ={}
set_df['dfF0_ACSF'] = dfF0_ACSF
set_df['dfF0_NEO'] = dfF0_NEO
set_df['dfF0_Peaks'] = set_peaks.iloc[:, :5]

results_0 = PlotResults(set_df, title_left=r"Peaks of ACSF_$\Delta F/F_0$", title_right=r"Peaks of NEO_$\Delta F/F_0$", ylim=[-0.5, 2])
results_0.show()

app.exec()