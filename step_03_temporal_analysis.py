## Author: Kang
## Last Update: 2024-Mar-28
## Purpose: To calculate deltaF/F0 and plot the data based on the output excel file
## of step_02_flatten_and_fitting.py

# Modules
import os
import openpyxl
import pandas as pd
import numpy as np
from scipy import stats
from tabulate import tabulate
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
    necessary_sheets = ['raw_ACSF', 'raw_NEO', 'fitted_ACSF', 'fitted_NEO']
    if not all(sheet in wb.sheetnames for sheet in necessary_sheets):
        print("The file does not have necessary sheets. Please check the file.")
        global areNecessarySheetsLoaded
        areNecessarySheetsLoaded = False
        return [], [], [], []
    
    # Read each tab as a dataframe of pandas
    raw_ACSF = pd.read_excel(analysis_xlsx_path, sheet_name="raw_ACSF")
    raw_NEO = pd.read_excel(analysis_xlsx_path, sheet_name="raw_NEO")
    fitted_ACSF = pd.read_excel(analysis_xlsx_path, sheet_name="fitted_ACSF")
    fitted_NEO = pd.read_excel(analysis_xlsx_path, sheet_name="fitted_NEO")
    return raw_ACSF, raw_NEO, fitted_ACSF, fitted_NEO

def calcute_DeltaF_f0(raw_ACSF, raw_NEO, fitted_ACSF, fitted_NEO):
    dfF0_ACSF = pd.DataFrame()
    dfF0_ACSF['Time'] = raw_ACSF["Time"]

    dfF0_ACSF_zscores = pd.DataFrame()
    dfF0_ACSF_zscores['Time'] = raw_ACSF["Time"]

    # Set empty arrays for averaging
    accum_ACSF_0 = np.zeros_like(dfF0_ACSF["Time"])
    accum_ACSF_1 = np.zeros_like(dfF0_ACSF["Time"])
    count_ACSF_SNs = 1
    Averaged_ACSF_SN = "-"
    
    for raw_acsf_col, fitted_acsf_col in zip(raw_ACSF.columns[1:], fitted_ACSF.columns[1:]):
        # Remove trend by division (raw/fitted)
        F_ACSF_detrended = np.array([(i/j) for i, j in zip(raw_ACSF[raw_acsf_col], fitted_ACSF[fitted_acsf_col])],dtype=float)
        
        # Calculate f0 (previous 90 frames 4.5 sec)
        f0_ACSF = np.mean(F_ACSF_detrended[0:91])
        
        # Calculate DeltaF/f0 (in percent)
        DeltaF_f0_ACSF_percent = np.array([100*(i-f0_ACSF)/f0_ACSF for i in F_ACSF_detrended],dtype=float)
        
        # Calculate DeltaF/f0 (in z-score)
        baseline_mean_ACSF = f0_ACSF
        baseline_std_ACSF = np.std(F_ACSF_detrended[0:91], ddof=1)
        DeltaF_f0_ACSF_zscore = np.array([(i-baseline_mean_ACSF)/baseline_std_ACSF for i in F_ACSF_detrended],dtype=float)
        
        # For averaging the results of DeltaF/f0 from the same date (continuous serial numbers)
        next_serial_number = int(raw_acsf_col.split('-')[-1])+1
        
        if raw_acsf_col.replace(raw_acsf_col.split('-')[-1], f'{next_serial_number:04}') in raw_ACSF.columns[1:]:
            Averaged_ACSF_SN = Averaged_ACSF_SN + " " +str(int(raw_acsf_col.split("-")[1]))
            accum_ACSF_0 = accum_ACSF_0 + DeltaF_f0_ACSF_percent
            accum_ACSF_1 = accum_ACSF_1 + DeltaF_f0_ACSF_zscore
            count_ACSF_SNs += 1
        else:
            if count_ACSF_SNs == 1:
                dfF0_ACSF["pt_"+raw_acsf_col]=DeltaF_f0_ACSF_percent
                dfF0_ACSF_zscores["zs_"+raw_acsf_col]=DeltaF_f0_ACSF_zscore
            else:
                Averaged_ACSF_SN = Averaged_ACSF_SN + " " +str(int(raw_acsf_col.split("-")[1]))
                accum_ACSF_0 = accum_ACSF_0 + DeltaF_f0_ACSF_percent
                accum_ACSF_1 = accum_ACSF_1 + DeltaF_f0_ACSF_zscore
                
                dfF0_ACSF["avg_pt_"+raw_acsf_col.replace("-"+raw_acsf_col.split("-")[1],"")+Averaged_ACSF_SN]= accum_ACSF_0/count_ACSF_SNs
                dfF0_ACSF_zscores["avg_zs_"+raw_acsf_col.replace("-"+raw_acsf_col.split("-")[1],"")+Averaged_ACSF_SN]=accum_ACSF_1/count_ACSF_SNs
                
                # Reset counter and accumulators
                count_ACSF_SNs = 1
                accum_ACSF_0 = np.zeros_like(dfF0_ACSF["Time"])
                accum_ACSF_1 = np.zeros_like(dfF0_ACSF["Time"])
                Averaged_ACSF_SN = ""

    dfF0_NEO = pd.DataFrame()
    dfF0_NEO['Time'] = raw_NEO["Time"]
    
    dfF0_NEO_zscores = pd.DataFrame()
    dfF0_NEO_zscores['Time'] = raw_NEO["Time"]
    
    accum_NEO_0 = np.zeros_like(dfF0_NEO["Time"])
    accum_NEO_1 = np.zeros_like(dfF0_NEO["Time"])
    count_NEO_SNs = 1
    Averaged_NEO_SN = "-"
    
    for raw_NEO_col, fitted_NEO_col in zip(raw_NEO.columns[1:], fitted_NEO.columns[1:]):
        # Remove trend by division (raw/fitted)
        F_NEO_detrended = np.array([(i/j) for i, j in zip(raw_NEO[raw_NEO_col], fitted_NEO[fitted_NEO_col])],dtype=float)
        
        # Calculate f0 (previous 90 frames 4.5 sec)
        f0_NEO = np.mean(F_NEO_detrended[0:91])
        
        # Calculate DeltaF/F0 (in percent)
        DeltaF_f0_NEO_percent = np.array([100*(i-f0_NEO)/f0_NEO for i in F_NEO_detrended],dtype=float)
        
        # Calculate DeltaF/F0 (in z-score)
        baseline_mean_NEO = f0_NEO
        basline_std_NEO = np.std(F_NEO_detrended[0:91], ddof=1)
        DeltaF_f0_NEO_zscore = np.array([(i-baseline_mean_NEO)/basline_std_NEO for i in F_NEO_detrended],dtype=float)

        # For averaging the results of DeltaF/f0 from the same date (continuous serial numbers)
        next_serial_number = int(raw_NEO_col.split('-')[1])+1
        
        if raw_NEO_col.replace(raw_NEO_col.split('-')[1], f'{next_serial_number:04}') in raw_NEO.columns[1:]:
            Averaged_NEO_SN = Averaged_NEO_SN + " " +str(int(raw_NEO_col.split("-")[1]))
            accum_NEO_0 = accum_NEO_0 + DeltaF_f0_NEO_percent
            accum_NEO_1 = accum_NEO_1 + DeltaF_f0_NEO_zscore
            count_NEO_SNs += 1
        
        else:
            if count_NEO_SNs == 1:
                dfF0_NEO['pt_'+raw_NEO_col]=DeltaF_f0_NEO_percent
                dfF0_NEO_zscores["zs_"+raw_NEO_col]=DeltaF_f0_NEO_zscore
            else:
                Averaged_NEO_SN = Averaged_NEO_SN + "-" +str(int(raw_NEO_col.split("-")[1]))
                accum_NEO_0 = accum_NEO_0 + DeltaF_f0_NEO_percent
                accum_NEO_1 = accum_NEO_1 + DeltaF_f0_NEO_zscore
                
                dfF0_NEO["avg_pt_"+raw_NEO_col.replace("-"+raw_NEO_col.split("-")[1],"")+Averaged_NEO_SN]= accum_NEO_0/count_NEO_SNs
                dfF0_NEO_zscores["avg_zs_"+raw_NEO_col.replace("-"+raw_NEO_col.split("-")[1],"")+Averaged_NEO_SN]=accum_NEO_1/count_NEO_SNs
                
                # Reset counter and accumulators
                count_NEO_SNs = 1
                accum_NEO_0 = np.zeros_like(accum_NEO_0)
                accum_NEO_1 = np.zeros_like(accum_NEO_1)
                Averaged_NEO_SN = ""
    
    return dfF0_ACSF, dfF0_NEO, dfF0_ACSF_zscores, dfF0_NEO_zscores

def saveToAnalysis(dfF0_ACSF, dfF0_NEO, dfF0_ACSF_zscores, dfF0_NEO_zscores):
    sheets_to_be_updated = ['DeltaF_f0_ACSF_percent', 'DeltaF_f0_NEO_percent', 'DeltaF_f0_ACSF_zscores', 'DeltaF_f0_NEO_zscores']
    dataframes_to_be_saved = {'DeltaF_f0_ACSF_percent': dfF0_ACSF, 'DeltaF_f0_NEO_percent': dfF0_NEO, 'DeltaF_f0_ACSF_zscores': dfF0_ACSF_zscores, 'DeltaF_f0_NEO_zscores': dfF0_NEO_zscores}

    for sheet in sheets_to_be_updated:
        with pd.ExcelWriter(analysis_xlsx_path, mode="a", if_sheet_exists="replace") as f:
            dataframes_to_be_saved[sheet].to_excel(f, sheet_name=sheet, index=False)

def plotting(dfF0_ACSF, dfF0_NEO, dfF0_ACSF_zscores, dfF0_NEO_zscores):
    set_DeltaF_f0_in_percent = {"dfF0_ACSF": dfF0_ACSF, "dfF0_NEO": dfF0_NEO}

    set_DeltaF_f0_in_zscores = {"dfF0_ACSF_cal_zscores": dfF0_ACSF_zscores, "dfF0_NEO_cal_zscores": dfF0_NEO_zscores}    
        
    results_0 = PlotResults(set_DeltaF_f0_in_percent, title_left=r"100%$\times \Delta F/F_0$ (ACSF)", title_right=r"100%$\times \Delta F/F_0$ (NEO)", 
                            ylim=[-0.5, 2], xlabel = 'time (sec.)', ylabel=r"$\Delta$"+"F/"+r"$F_0$"+"(%)")
    results_0.show()

    results_1 = PlotResults(set_DeltaF_f0_in_zscores, title_left=r"Z-scores of $\Delta F/F_0$ (ACSF)", title_right=r"Z-scores of $\Delta F/F_0$ (NEO)",
                            ylim=[-10, 45], xlabel='time (sec.)', ylabel='Z-scores (A.U.)')
    results_1.show()
    app.exec_()
    

# Main
raw_ACSF, raw_NEO, fitted_ACSF, fitted_NEO = readDataFromExcel()

if isAnalysisExcelFileLoaded and areNecessarySheetsLoaded:
    dfF0_ACSF, dfF0_NEO, dfF0_ACSF_zscores, dfF0_NEO_zscores = calcute_DeltaF_f0(raw_ACSF, raw_NEO, fitted_ACSF, fitted_NEO)
    saveToAnalysis(dfF0_ACSF, dfF0_NEO, dfF0_ACSF_zscores, dfF0_NEO_zscores)
    plotting(dfF0_ACSF, dfF0_NEO, dfF0_ACSF_zscores, dfF0_NEO_zscores)


