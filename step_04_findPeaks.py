## Author: Kang
## Last Update: 2025-Mar-28
## Purpose: Find peaks from curves of delta F/F0, zscored delta F/F0
import os
import openpyxl
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from rich import print
from PySide6.QtWidgets import QApplication
from classes.dialog_GetPath import GetPath
from classes.plot_results import PlotResults


# Set event handler
app = QApplication()

# Get the path of the excel file analysis.xlsx
excelfile_analysis = GetPath(title="Please select the processed data of a xlsx file.",
                        filemode="file",
                        filetype="excel")
analysis_xlsx_path = excelfile_analysis.get_path()

isAnalysisExcelFileLoaded = True
areNecessarySheetsLoaded = True

def readDataFromExcel():
    if not os.path.exists(analysis_xlsx_path):
        print("No excel file is chosen. Task cancelled")
        global isAnalysisExcelFileLoaded
        isAnalysisExcelFileLoaded = False
        return [], [], [], []

    wb = openpyxl.load_workbook(analysis_xlsx_path)
    necessary_sheets = ['DeltaF_f0_ACSF_percent', 'DeltaF_f0_NEO_percent', 'DeltaF_f0_ACSF_zscores', 'DeltaF_f0_NEO_zscores']
    if not all(sheet in wb.sheetnames for sheet in necessary_sheets):
        print("The file does not have necessary sheets. Please check the file.")
        global areNecessarySheetsLoaded
        areNecessarySheetsLoaded = False
        return [], [], [], []
    
    # Read each tab as a dataframe of pandas
    DeltaF_f0_ACSF_percent = pd.read_excel(analysis_xlsx_path, sheet_name="DeltaF_f0_ACSF_percent")
    DeltaF_f0_NEO_percent = pd.read_excel(analysis_xlsx_path, sheet_name="DeltaF_f0_NEO_percent")
    DeltaF_f0_ACSF_zscores = pd.read_excel(analysis_xlsx_path, sheet_name="DeltaF_f0_ACSF_zscores")
    DeltaF_f0_NEO_zscores = pd.read_excel(analysis_xlsx_path, sheet_name="DeltaF_f0_NEO_zscores")
    return DeltaF_f0_ACSF_percent, DeltaF_f0_NEO_percent, DeltaF_f0_ACSF_zscores, DeltaF_f0_NEO_zscores

def findPeaks(DeltaF_f0_ACSF_percent, DeltaF_f0_NEO_percent, DeltaF_f0_ACSF_zscores, DeltaF_f0_NEO_zscores):
    total_frames = DeltaF_f0_ACSF_percent.shape[0]
    # columns_data = columns - 1
    search_range = 30
    start_frame = total_frames - 300
    df_all_peaks_and_time = pd.DataFrame()

    peakValues_ACSF_percent = []
    peakTimes_ACSF_percent = []
    for col in DeltaF_f0_ACSF_percent.columns[1:]:
        searching_segments = np.array(DeltaF_f0_ACSF_percent[col][start_frame:start_frame+search_range])
        searching_time_interval = np.array(DeltaF_f0_ACSF_percent["Time"][start_frame:start_frame+search_range])
        peaks_idx, properties = find_peaks(searching_segments, distance=30)

        if peaks_idx.size == 0:
            print("No peaks are found in", col)
            peakValues_ACSF_percent.append(np.nan)
            peakTimes_ACSF_percent.append(np.nan)
        else:
            peakValues_ACSF_percent.append(searching_segments[peaks_idx][0])
            peakTimes_ACSF_percent.append(searching_time_interval[peaks_idx][0])
            
    df_all_peaks_and_time['peakTimes_ACSF_percent'] = peakTimes_ACSF_percent
    df_all_peaks_and_time['peakValues_ACSF_percent'] = peakValues_ACSF_percent

    peakValues_NEO_percent = []
    peakTimes_NEO_percent = []
    for col in DeltaF_f0_NEO_percent.columns[1:]:
        searching_segments = np.array(DeltaF_f0_NEO_percent[col][start_frame:start_frame+search_range])
        searching_time_interval = np.array(DeltaF_f0_NEO_percent["Time"][start_frame:start_frame+search_range])
        peaks_idx, properties = find_peaks(searching_segments, distance=30)

        if peaks_idx.size == 0:
            print("No peaks are found in", col)
            peakValues_NEO_percent.append(np.nan)
            peakTimes_NEO_percent.append(np.nan)
        else:
            peakValues_NEO_percent.append(searching_segments[peaks_idx][0])
            peakTimes_NEO_percent.append(searching_time_interval[peaks_idx][0])
            
    df_all_peaks_and_time['peakTimes_NEO_percent'] = peakTimes_NEO_percent
    df_all_peaks_and_time['peakValues_NEO_percent'] = peakValues_NEO_percent


    peakValues_ACSF_zscores = []
    peakTimes_ACSF_zscores = []
    for col in DeltaF_f0_ACSF_zscores.columns[1:]:
        searching_segments = np.array(DeltaF_f0_ACSF_zscores[col][start_frame:start_frame+search_range])
        searching_time_interval = np.array(DeltaF_f0_ACSF_zscores["Time"][start_frame:start_frame+search_range])
        peaks_idx, properties = find_peaks(searching_segments, distance=30)

        if peaks_idx.size == 0:
            print("No peaks are found in", col)
            peakValues_ACSF_zscores.append(np.nan)
            peakTimes_ACSF_zscores.append(np.nan)
        else:
            peakValues_ACSF_zscores.append(searching_segments[peaks_idx][0])
            peakTimes_ACSF_zscores.append(searching_time_interval[peaks_idx][0])

    df_all_peaks_and_time['peakTimes_ACSF_zscores'] = peakTimes_ACSF_zscores
    df_all_peaks_and_time['peakValues_ACSF_zscores'] = peakValues_ACSF_zscores


    peakValues_NEO_zscores = []
    peakTimes_NEO_zscores = []

    for col in DeltaF_f0_NEO_zscores.columns[1:]:
        searching_segments = np.array(DeltaF_f0_NEO_zscores[col][start_frame:start_frame+search_range])
        searching_time_interval = np.array(DeltaF_f0_NEO_zscores["Time"][start_frame:start_frame+search_range])
        peaks_idx, properties = find_peaks(searching_segments, distance=30)

        if peaks_idx.size == 0:
            print("No peaks are found in", col)
        else:
            peakValues_NEO_zscores.append(searching_segments[peaks_idx][0])
            peakTimes_NEO_zscores.append(searching_time_interval[peaks_idx][0])
            
    df_all_peaks_and_time['peakTimes_NEO_zscores'] = peakTimes_NEO_zscores
    df_all_peaks_and_time['peakValues_NEO_zscores'] = peakValues_NEO_zscores

    return df_all_peaks_and_time

def saveToAnalysis(df_all_peaks_and_time):
    with pd.ExcelWriter(analysis_xlsx_path, mode="a", if_sheet_exists="replace") as f:
        df_all_peaks_and_time.to_excel(f, sheet_name="all_peaks", index=False)
        print("The peaks are saved into the file.")

def plotting(DeltaF_f0_ACSF_percent, DeltaF_f0_NEO_percent, DeltaF_f0_ACSF_zscores, DeltaF_f0_NEO_zscores, df_all_peaks_and_time):
    set_df_1 ={}
    set_df_1['DeltaF_f0_ACSF_percent'] = DeltaF_f0_ACSF_percent
    set_df_1['DeltaF_f0_NEO_percent'] = DeltaF_f0_NEO_percent
    set_df_1['dfF0_Peaks'] = df_all_peaks_and_time.iloc[:, :5]
    
    set_df_2 = {}
    set_df_2['DeltaF_f0_ACSF_zscores'] = DeltaF_f0_ACSF_zscores
    set_df_2['DeltaF_f0_NEO_zscores'] = DeltaF_f0_NEO_zscores
    set_df_2['dfF0_Peaks_cal_zscores'] = df_all_peaks_and_time.iloc[:, 4:]

    results_0 = PlotResults(set_df_1, title_left=r"Peaks of ACSF_$\Delta F/F_0$ (Percent)", title_right=r"Peaks of NEO_$\Delta F/F_0$ (Percent)",
                            ylim=[-0.5, 2], xlabel = 'time (sec.)', ylabel=r"$\Delta$"+"F/"+r"$F_0$"+"(%)",)
    results_0.show()
    results_1 = PlotResults(set_df_2, title_left=r"Peaks of ACSF_$\Delta F/F_0$ (Z-scores)", title_right=r"Peaks of NEO$\Delta F/F_0$ (Z-scores)",
                            ylim=[-10, 45], xlabel='time (sec.)', ylabel='Z-scores (A.U.)')
    results_1.show()

    app.exec()
    
# Main
DeltaF_f0_ACSF_percent, DeltaF_f0_NEO_percent, DeltaF_f0_ACSF_zscores, DeltaF_f0_NEO_zscores = readDataFromExcel()
if isAnalysisExcelFileLoaded and areNecessarySheetsLoaded:
    df_all_peaks_and_time = findPeaks(DeltaF_f0_ACSF_percent, DeltaF_f0_NEO_percent, DeltaF_f0_ACSF_zscores, DeltaF_f0_NEO_zscores)
    saveToAnalysis(df_all_peaks_and_time)
    plotting(DeltaF_f0_ACSF_percent, DeltaF_f0_NEO_percent, DeltaF_f0_ACSF_zscores, DeltaF_f0_NEO_zscores, df_all_peaks_and_time)