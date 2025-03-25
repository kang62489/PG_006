## Author: Kang
## Last Update: 2024-Jan-30
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
from classes.dialog_getPath import GetPath
from classes.plot_results import PlotResults

# Set event handler
app = QApplication()

# Get the path of the excel file
xlsx_filepath = GetPath(title="Please select the processed data of a xlsx file.",
                        filemode="file",
                        filetype="excel")
xlsx_filepath = xlsx_filepath.get_path()

if os.path.exists(xlsx_filepath):
    # Read each tab as a dataframe of pandas
    raw_ACSF = pd.read_excel(xlsx_filepath, sheet_name="raw_ACSF")
    raw_NEO = pd.read_excel(xlsx_filepath, sheet_name="raw_NEO")
    fitted_ACSF = pd.read_excel(xlsx_filepath, sheet_name="fitted_ACSF")
    fitted_NEO = pd.read_excel(xlsx_filepath, sheet_name="fitted_NEO")


    # Set empty dataframes for saving calculated data
    dfF0_ACSF = pd.DataFrame()
    dfF0_ACSF['Time'] = raw_ACSF["Time"]

    dfF0_NEO = pd.DataFrame()
    dfF0_NEO['Time'] = raw_NEO["Time"]

    dfF0_ACSF_zscores = pd.DataFrame()
    dfF0_ACSF_zscores['Time'] = raw_ACSF["Time"]

    dfF0_NEO_zscores = pd.DataFrame()
    dfF0_NEO_zscores['Time'] = raw_NEO["Time"]

    dfF0_ACSF_calibrated_zscores = pd.DataFrame()
    dfF0_ACSF_calibrated_zscores['Time'] = raw_ACSF["Time"]

    dfF0_NEO_calibrated_zscores = pd.DataFrame()
    dfF0_NEO_calibrated_zscores['Time'] = raw_NEO["Time"]

    # Set empty arrays for averaging
    accum_ACSF_0 = np.zeros_like(dfF0_ACSF["Time"])
    accum_ACSF_1 = np.zeros_like(dfF0_ACSF["Time"])
    count = 1
    SNseries = ""
    for raw_acsf_col, fitted_acsf_col in zip(raw_ACSF.columns[1:], fitted_ACSF.columns[1:]):
        f = np.array([(i/j) for i, j in zip(raw_ACSF[raw_acsf_col], fitted_ACSF[fitted_acsf_col])],dtype=float)
        f_0 = np.mean(f[50:101])
        df_f0_percent = np.array([100*(i-f_0)/f_0 for i in f],dtype=float)
        df_f0_ratio = np.array([(i-f_0) for i in f],dtype=float)
        df_f0_ratio_mean = np.mean(df_f0_ratio[50:101])
        df_f0_ratio_std = np.std(df_f0_ratio[50:101], ddof=1)
        df_f0_ratio_zscored = (df_f0_ratio-df_f0_ratio_mean)/df_f0_ratio_std
        
        next_serial_number = int(raw_acsf_col.split('-')[-1])+1
        
    # For averaging the results of dF/F0 from the same trial of the date (serial number should be continuous)
        if raw_acsf_col.replace(raw_acsf_col.split('-')[-1], f'{next_serial_number:04}') in raw_ACSF.columns[1:]:
            data_temp = df_f0_percent
            data_temp_2 = df_f0_ratio_zscored
            
            SNseries = SNseries + "-" +str(int(raw_acsf_col.split("-")[1]))
            accum_ACSF_0 = accum_ACSF_0 + df_f0_percent
            accum_ACSF_1 = accum_ACSF_1 + df_f0_ratio_zscored
            count += 1
        
        else:
            if count == 1:
                dfF0_ACSF["cal_"+raw_acsf_col]=df_f0_percent
                # dfF0_ACSF_zscores["cal_"+raw_acsf_col]=stats.zscore(df_f0_percent)
                dfF0_ACSF_calibrated_zscores["zscored_"+raw_acsf_col]=df_f0_ratio_zscored
            else:
                SNseries = SNseries + "-" +str(int(raw_acsf_col.split("-")[1]))
                dfF0_ACSF["avg_"+raw_acsf_col.replace("_"+raw_acsf_col.split("-")[1],"")+SNseries]= accum_ACSF_0/count
                # dfF0_ACSF_zscores["avg_zscored_"+raw_acsf_col.replace("_"+raw_acsf_col.split("-")[1],"")+SNseries]=stats.zscore(accum_ACSF_0/count)
                dfF0_ACSF_calibrated_zscores["avg_zscored_"+raw_acsf_col.replace("_"+raw_acsf_col.split("-")[1],"")+SNseries]=accum_ACSF_1/count
                
                # Reset counter and accumulators
                count = 1
                accum_ACSF_0 = np.zeros_like(dfF0_ACSF["Time"])
                accum_ACSF_1 = np.zeros_like(dfF0_ACSF["Time"])
                SNseries = ""

    accum_NEO_0 = np.zeros_like(dfF0_NEO["Time"])
    accum_NEO_1 = np.zeros_like(dfF0_NEO["Time"])
    count = 1
    SNseries = ""
    for raw_NEO_col, fitted_NEO_col in zip(raw_NEO.columns[1:], fitted_NEO.columns[1:]):
        f = np.array([(i/j) for i, j in zip(raw_NEO[raw_NEO_col], fitted_NEO[fitted_NEO_col])],dtype=float)
        f_0 = np.mean(f[50:101])
        df_f0_percent = np.array([100*(i-f_0)/f_0 for i in f],dtype=float)
        df_f0_ratio = np.array([(i-f_0) for i in f],dtype=float)
        df_f0_ratio_mean = np.mean(df_f0_ratio[50:101])
        df_f0_ratio_std = np.std(df_f0_ratio[50:101], ddof=1)
        df_f0_ratio_zscored = (df_f0_ratio-df_f0_ratio_mean)/df_f0_ratio_std

        next_serial_number = int(raw_NEO_col.split('-')[1])+1
        
        if raw_NEO_col.replace(raw_NEO_col.split('-')[1], f'{next_serial_number:04}') in raw_NEO.columns[1:]:
            SNseries = SNseries + "-" +str(int(raw_NEO_col.split("-")[1]))
            accum_NEO_0 = accum_NEO_0 + df_f0_percent
            accum_NEO_1 = accum_NEO_1 + df_f0_ratio
            count += 1
        
        else:
            if count == 1:
                dfF0_NEO["cal_"+raw_NEO_col]=df_f0_percent
                # dfF0_NEO_zscores["cal_"+raw_NEO_col]=stats.zscore(df_f0_percent)
                dfF0_NEO_calibrated_zscores["zscored_"+raw_NEO_col]=df_f0_ratio_zscored
            else:
                SNseries = SNseries + "-" +str(int(raw_NEO_col.split("-")[1]))
                dfF0_NEO["avg_"+raw_NEO_col.replace("_"+raw_NEO_col.split("-")[1],"")+SNseries]= accum_NEO_0/count
                # dfF0_NEO_zscores["avg_zscored_"+raw_NEO_col.replace("_"+raw_NEO_col.split("-")[1],"")+SNseries]=stats.zscore(accum_NEO_0/count)
                dfF0_NEO_calibrated_zscores["avg_zscored_"+raw_NEO_col.replace("_"+raw_NEO_col.split("-")[1],"")+SNseries]=accum_NEO_1/count
                
                # Reset counter and accumulators
                count = 1
                accum_NEO_0 = np.zeros_like(accum_NEO_0)
                accum_NEO_1 = np.zeros_like(accum_NEO_1)
                SNseries = ""
                
    # Save the calculated data into the same excel file
    wb = openpyxl.load_workbook(xlsx_filepath)
    if 'dfF0_ACSF' in wb.sheetnames:
        del wb['dfF0_ACSF']
        wb.save(xlsx_filepath)

    if 'dfF0_NEO' in wb.sheetnames:
        del wb['dfF0_NEO']
        wb.save(xlsx_filepath)

    if 'dfF0_ACSF_cal_zscores' in wb.sheetnames:
        del wb['dfF0_ACSF_cal_zscores']
        wb.save(xlsx_filepath)

    if 'dfF0_NEO_cal_zscores' in wb.sheetnames:
        del wb['dfF0_NEO_cal_zscores']
        wb.save(xlsx_filepath)

    with pd.ExcelWriter(xlsx_filepath,mode="a") as f:
        dfF0_ACSF.to_excel(f,sheet_name="dfF0_ACSF",index=False)

    with pd.ExcelWriter(xlsx_filepath,mode="a") as f:
        dfF0_NEO.to_excel(f,sheet_name="dfF0_NEO",index=False)
        
    with pd.ExcelWriter(xlsx_filepath,mode="a") as f:
        dfF0_ACSF_calibrated_zscores.to_excel(f,sheet_name="dfF0_ACSF_cal_zscores",index=False)
        
    with pd.ExcelWriter(xlsx_filepath,mode="a") as f:
        dfF0_NEO_calibrated_zscores.to_excel(f,sheet_name="dfF0_NEO_cal_zscores",index=False)
        

    set_dfF0 = {"dfF0_ACSF": dfF0_ACSF,
                "dfF0_NEO": dfF0_NEO}

    set_cal_zscores = {"dfF0_ACSF_cal_zscores": dfF0_ACSF_calibrated_zscores,
                    "dfF0_NEO_cal_zscores": dfF0_NEO_calibrated_zscores}    
        
    # Plot the data
    results_0 = PlotResults(set_dfF0, title_left=r"ACSF_100%$\times \Delta F/F_0$", title_right=r"NEO_100%$\times \Delta F/F_0$", 
                            ylim=[-0.5, 2], xlabel = 'time (sec.)', ylabel=r"$\Delta$"+"F/"+r"$F_0$"+"(%) (A.U.)")
    results_0.show()

    results_1 = PlotResults(set_cal_zscores, title_left=r"ACSF_Z-scores of $\Delta F/F_0$(Ratio)", title_right=r"NEO_Z-scores of $\Delta F/F_0$(Ratio)",
                            ylim=[-4, 8], xlabel='time (sec.)', ylabel='Z-scores (A.U.)')
    results_1.show()
    app.exec_()
else:
    print("The file does not exist. Please check the file path.")