# Author: Kang
# Last Update: 2024-Oct-21

# Initialization
import os, openpyxl
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Load the excel file with 1-D temporal sequences
Tk().withdraw()
xlsx_filepath = askopenfilename(title="Please select a recording xlsx file.",filetypes=[("Excel Files ", ".xlsx .csv")])
print("<" + xlsx_filepath + "> Selected!!")

# Read each tab as a dataframe of pandas
raw_df_none = pd.read_excel(xlsx_filepath, sheet_name="raw_df_none")
raw_df_NEO = pd.read_excel(xlsx_filepath, sheet_name="raw_df_NEO")
df_none_fitted = pd.read_excel(xlsx_filepath, sheet_name="df_none_monoExp_fitted")
df_NEO_fitted = pd.read_excel(xlsx_filepath, sheet_name="df_NEO_monoExp_fitted")

dfF0 = pd.DataFrame()
dfF0['Time'] = raw_df_none["Time"]

dfF0_zscores = pd.DataFrame()
dfF0_zscores['Time'] = raw_df_none["Time"]

cal_zscore = pd.DataFrame()
cal_zscore['Time'] = raw_df_none["Time"]

n = 1
accum = np.zeros_like(dfF0["Time"])
accum_2 = np.zeros_like(dfF0["Time"])
SNseries = ""

# Calibrate signals by their baseline
for raw_col, raw_fitted_col in zip(raw_df_none.columns[1:], df_none_fitted.columns[1:]):
    # cal = np.array([i/j for i, j in zip(raw_df_none[raw_col], df_none_fitted[raw_fitted_col])],dtype=float)
    cal = np.array([100*(i-j)/j for i, j in zip(raw_df_none[raw_col], df_none_fitted[raw_fitted_col])],dtype=float)
    cal_2 = np.array([(i-j) for i, j in zip(raw_df_none[raw_col], df_none_fitted[raw_fitted_col])],dtype=float)
    cal_2_zscored = stats.zscore(cal_2)
    # F_0 = np.mean(cal[20:90])
    # delta_F = cal-F_0
    
    next_serial_number = int(raw_col.split('-')[1])+1
    
 # For averaging the results of dF/F0 from the same date (serial number should be continuous)
    if raw_col.replace(raw_col.split('-')[1], f'{next_serial_number:04}') in raw_df_none.columns[1:]:
        print(raw_col+" start to average")
        # data_temp = 100*(delta_F/F_0)
        data_temp = cal
        data_temp_2 = cal_2_zscored
        SNseries = SNseries + "-" +str(int(raw_col.split("-")[1]))
        print(SNseries)
        accum = accum + data_temp
        accum_2 = accum_2 + data_temp_2
        n += 1
    
    else:
        if n == 1:
            # dfF0["cal_"+raw_col]=100*(delta_F/F_0)
            dfF0["cal_"+raw_col]=cal
            # dfF0_zscores["cal_"+raw_col]=stats.zscore(100*(delta_F/F_0))
            dfF0_zscores["cal_"+raw_col]=stats.zscore(cal)
            # cal_zscore: zscore of calibrated intensity
            cal_zscore["cal_"+raw_col]=cal_2_zscored
            print("no need to average")
        else:
            print(n, raw_col)
            SNseries = SNseries + "-" +str(int(raw_col.split("-")[1]))
            dfF0["avg_"+raw_col.replace("_"+raw_col.split("-")[1],"")+SNseries]= accum/n
            dfF0_zscores["avg_zscored_"+raw_col.replace("_"+raw_col.split("-")[1],"")+SNseries]=stats.zscore(accum/n)
            cal_zscore["avg_zscored_"+raw_col.replace("_"+raw_col.split("-")[1],"")+SNseries]=accum_2/n
            print("averaged and averaged!")
            n = 1
            accum = np.zeros_like(accum)
            accum_2 = np.zeros_like(accum_2)
            
            SNseries = ""

    


row, colNums_of_none = dfF0.shape

n = 1
accum = np.zeros_like(dfF0["Time"])
accum_2 = np.zeros_like(dfF0["Time"])
SNseries = ""
for raw_NEO_col, raw_NEO_fitted_col in zip(raw_df_NEO.columns[1:], df_NEO_fitted.columns[1:]):
    # cal = np.array([i/j for i, j in zip(raw_df_NEO[raw_NEO_col], df_NEO_fitted[raw_NEO_fitted_col])],dtype=float)
    cal = np.array([100*(i-j)/j for i, j in zip(raw_df_NEO[raw_NEO_col], df_NEO_fitted[raw_NEO_fitted_col])],dtype=float)
    cal_2 = np.array([(i-j) for i, j in zip(raw_df_NEO[raw_NEO_col], df_NEO_fitted[raw_NEO_fitted_col])],dtype=float)
    cal_2_zscored = stats.zscore(cal_2)
    
    # F_0 = np.mean(cal[20:90])
    # delta_F = cal-F_0

    next_serial_number = int(raw_NEO_col.split('-')[1])+1
    
    
    if raw_NEO_col.replace(raw_NEO_col.split('-')[1], f'{next_serial_number:04}') in raw_df_NEO.columns[1:]:
        print(raw_NEO_col+" start to average")
        # temp = 100*(delta_F/F_0)
        temp = cal
        temp_2 = cal_2
        SNseries = SNseries + "-" +str(int(raw_NEO_col.split("-")[1]))
        accum = accum + temp
        accum_2 = accum_2 + temp_2
        n += 1
    
    else:
        if n == 1:
            # dfF0["cal_"+raw_NEO_col]=100*(delta_F/F_0)
            # dfF0_zscores["cal_"+raw_NEO_col]=stats.zscore(100*(delta_F/F_0))

            dfF0["cal_"+raw_NEO_col]=cal
            dfF0_zscores["cal_"+raw_NEO_col]=stats.zscore(cal)
            cal_zscore["cal_"+raw_NEO_col]=cal_2_zscored
            print("no need to average")
        else:
            print(n, raw_NEO_col)
            SNseries = SNseries + "-" +str(int(raw_NEO_col.split("-")[1]))
            dfF0["avg_"+raw_NEO_col.replace("_"+raw_NEO_col.split("-")[1],"")+SNseries]= accum/n
            dfF0_zscores["avg_zscored_"+raw_NEO_col.replace("_"+raw_NEO_col.split("-")[1],"")+SNseries]=stats.zscore(accum/n)
            cal_zscore["avg_zscored_"+raw_NEO_col.replace("_"+raw_NEO_col.split("-")[1],"")+SNseries]=accum_2/n
            print("averaged and averaged!")
            n = 1
            accum = np.zeros_like(accum)
            accum_2 = np.zeros_like(accum_2)
            SNseries = ""



# Plot two sets for comaprison
plt.figure()
# plt.subplot(121)
plt.plot(dfF0["Time"], dfF0.iloc[:,1], 'b-')
plt.plot(dfF0["Time"], dfF0.iloc[:,2], 'r-',)
plt.ylim(-1,30)
plt.xlabel('time (sec.)')
plt.ylabel(r"$\Delta$"+"F/"+r"$F_0$"+"(%)")
plt.grid('both')
# plt.title('Fluorescence response in normal Recording ACSF')
plt.title('Comparison of Neostigmine Wash-off Effect')
# plt.legend(['ACh (10 mM) puffed', 'ACh (50 '+r"$\mu$"+'M) puffed'])
plt.legend(['ACh (10 mM) puffed after washing > 35 min.', 'ACh (10 mM) puffed in normal Recording ACSF'])

# plt.subplot(122)
# plt.plot(dfF0["Time"], dfF0.iloc[:,3], 'b-')
# plt.plot(dfF0["Time"], dfF0.iloc[:,4], 'r-',)
# plt.ylim(-1,30)
# plt.xlabel('time (sec.)')
# plt.ylabel(r"$\Delta$"+"F/"+r"$F_0$"+"(%)")
# plt.grid('both')
# plt.title('Fluorescence response in 50'+r"$\mu$"+ 'M Neostigmine presented' + ' Recording ACSF')
# plt.legend(['ACh (10 mM) puffed', 'ACh (50 '+r"$\mu$"+'M) puffed'])
# plt.show()


# Plot for different dates
# plt.figure()
# ax1 = plt.subplot(121)
# for col in dfF0.columns[1:colNums_of_none]:
#     plt.plot(dfF0["Time"], dfF0[col])

# for col in dfF0_zscores.columns[1:colNums_of_none]:
#     plt.plot(dfF0["Time"], dfF0_zscores[col])

# plt.xlabel('time (sec.)')
# plt.ylabel(r"$\Delta$"+"F/"+r"$F_0$"+"(%)")
# plt.ylabel('A.U.')
# plt.ylim(-1,15)
# plt.grid('both')
# plt.title('Fluorescence response in normal Recording ACSF')
# plt.title('Fluorescence response in normal Recording ACSF (Z-scored)')
# plt.legend([col for col in dfF0.columns[1:colNums_of_none]])
# ax1.legend([col for col in dfF0.columns[1:colNums_of_none]],loc='upper center', bbox_to_anchor=(0.5, -0.05),
        #   fancybox=True, shadow=True, ncol=5)

# ax2 = plt.subplot(122)
# for col in dfF0.columns[colNums_of_none:]:
#     plt.plot(dfF0["Time"], dfF0[col])

# for col in dfF0_zscores.columns[colNums_of_none:]:
#     plt.plot(dfF0["Time"], dfF0_zscores[col])


# plt.xlabel('time (sec.)')
# plt.ylabel(r"$\Delta$"+"F/"+r"$F_0$"+"(%)")
# plt.ylabel('A.U.')
# plt.ylim(-1,15)
# plt.grid('both')
# plt.title('Fluorescence response in 50'+r"$\mu$"+ 'M Neostigmine presented' + ' Recording ACSF')
# plt.title('Fluorescence response (Z-scored) in 50'+r"$\mu$"+ 'M Neostigmine presented' + ' Recording ACSF')
# plt.legend([col for col in dfF0.columns[colNums_of_none:]])
# ax2.legend([col for col in dfF0.columns[colNums_of_none:]],loc='upper center', bbox_to_anchor=(0.5, -0.05),
#           fancybox=True, shadow=True, ncol=5)
plt.show()


wb = openpyxl.load_workbook(os.path.join(os.path.dirname(xlsx_filepath),'processed.xlsx'))
if 'dfF0' in wb.sheetnames:
    del wb['dfF0']
wb.save(os.path.join(os.path.dirname(xlsx_filepath),'processed.xlsx'))

if 'dfF0_zscores' in wb.sheetnames:
    del wb['dfF0_zscores']

if 'cal_zscores' in wb.sheetnames:
    del wb['cal_zscores']

wb.save(os.path.join(os.path.dirname(xlsx_filepath),'processed.xlsx'))

with pd.ExcelWriter(os.path.join(os.path.dirname(xlsx_filepath),'processed.xlsx'),mode="a") as f:
    dfF0.to_excel(f,sheet_name="dfF0",index=False)

with pd.ExcelWriter(os.path.join(os.path.dirname(xlsx_filepath),'processed.xlsx'),mode="a") as f:
    dfF0_zscores.to_excel(f,sheet_name="dfF0_zscores",index=False)
    
with pd.ExcelWriter(os.path.join(os.path.dirname(xlsx_filepath),'processed.xlsx'),mode="a") as f:
    cal_zscore.to_excel(f,sheet_name="cal_zscores",index=False)
