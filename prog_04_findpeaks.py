# Author: Kang
# Last Update: 2024-Nov-20

# Initialization
import os, glob, matplotlib, openpyxl
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# request path of files and then load files
Tk().withdraw()
xlsx_filepath = askopenfilename(title="Please select a recording xlsx file.",filetypes=[("Excel Files ", ".xlsx .csv")])

dfF0 = pd.read_excel(xlsx_filepath, sheet_name="dfF0")

frames, total_columns = dfF0.shape
total_columns = total_columns - 1

start_frame = frames - 300
frames_to_be_checked = 30
peaks_Set = pd.DataFrame()
peak_values = []
# look for peaks at designated range
plt.figure()
plt.subplot(121)
for col_none in dfF0.columns[1:int(1+0.5*total_columns)]:   
    check_range = np.array(dfF0[col_none][start_frame:start_frame+frames_to_be_checked])
    time_range = np.array(dfF0["Time"][start_frame:start_frame+frames_to_be_checked])
    peaks, properties = find_peaks(check_range, distance=30)

    if peaks.size == 0:
        print("No peaks are found in", col_none)
    else:
        peak_values.append(check_range[peaks][0])
        # plt.plot(time_range, check_range)
        # plt.plot(time_range[peaks], check_range[peaks], "x")

        peaks_origin = peaks + start_frame
        plt.plot(dfF0["Time"], dfF0[col_none])
        plt.plot(dfF0["Time"][peaks_origin], dfF0[col_none][peaks_origin], "x")

plt.xlabel('time (sec.)')
plt.ylabel(r"$\Delta$"+"F/"+r"$F_0$"+"(%)")
plt.ylim(-0.5,2)
plt.grid('both')
plt.title('Fluorescence response in normal Recording ACSF')
peaks_Set['None'] = peak_values


plt.subplot(122)
peak_values = []
for col_NEO in dfF0.columns[int(1+0.5*total_columns):]:   
    check_range = np.array(dfF0[col_NEO][start_frame:start_frame+frames_to_be_checked])
    time_range = np.array(dfF0["Time"][start_frame:start_frame+frames_to_be_checked])
    peaks, properties = find_peaks(check_range, distance=30)

    if peaks.size == 0:
        print("No peaks are found in", col_NEO)
    else:
        peak_values.append(check_range[peaks][0])
        # plt.plot(time_range, check_range)
        # plt.plot(time_range[peaks], check_range[peaks], "x")

        peaks = peaks + start_frame
        plt.plot(dfF0["Time"], dfF0[col_NEO])
        plt.plot(dfF0["Time"][peaks], dfF0[col_NEO][peaks], "x")

plt.xlabel('time (sec.)')
plt.ylabel(r"$\Delta$"+"F/"+r"$F_0$"+"(%)")
plt.ylim(-0.5,2)
plt.grid('both')
plt.title('Peaks of puffs in 50'+r"$\mu$"+ 'M Neostigmine presented' + ' Recording ACSF')
peaks_Set['NEO'] = peak_values
plt.show()

wb = openpyxl.load_workbook(os.path.join(os.path.dirname(xlsx_filepath),'processed.xlsx'))
if 'Peaks' in wb.sheetnames:
    del wb['Peaks']
wb.save(os.path.join(os.path.dirname(xlsx_filepath),'processed.xlsx'))

with pd.ExcelWriter(os.path.join(os.path.dirname(xlsx_filepath),'processed.xlsx'),mode="a") as f:
    peaks_Set.to_excel(f,sheet_name="Peaks",index=False)