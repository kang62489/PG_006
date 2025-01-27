## Author: Kang
## Last Update: 2024-Nov-19


## Initialization
import os, glob
import pandas as pd
import numpy as np
import skimage.io as skio
from scipy.optimize import *
from scipy import interpolate as interp
from pathlib import Path as pt
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score


## Set directories for import and export images
data_path = "D:\\Research\\Gideon\\Analysis\\2024-10-21"
export_path = "D:\\Research\\Gideon\\Analysis\\2024-10-21"
## Sampling Rates: 50 ms = 20 Hz
fs = 20


## Set time label by frames of images
total_frames = 390
time = np.arange(total_frames)/fs


## Pick up folders of images for analysis
ROIs = ["512"]
for ROI in ROIs:
    lst_prep_folders_none = [f for f in next(os.walk(os.path.join(data_path)))[1] if ("output"  in f) & (ROI in f) & ("NEO" not in f)]
    lst_prep_folders_NEO = [f for f in next(os.walk(os.path.join(data_path)))[1] if ("output"  in f) & (ROI in f) & ("NEO" in f)]

for folder_none, folder_NEO in zip(lst_prep_folders_none, lst_prep_folders_NEO):
    lst_files_none =glob.glob(os.path.join(data_path, folder_none,"*.tif"))
    lst_files_NEO = glob.glob(os.path.join(data_path, folder_NEO,"*.tif"))


## Prepare empty dataframes for saving converted data
raw_none = pd.DataFrame()
raw_NEO = pd.DataFrame()


## Insert time seqence for easily ploting in the output excel file_none
raw_none['Time'] = time
raw_NEO['Time'] = time


## Load imaging trains and calculate averages of each frame
## Save each train into a column in each dataframe
for file_none, file_NEO in zip(lst_files_none, lst_files_NEO):
    im_none = skio.imread(file_none, plugin="tifffile")
    im_NEO = skio.imread(file_NEO, plugin="tifffile")
    
    im_none_temporal = im_none.mean(axis=(1,2))
    im_NEO_temporal = im_NEO.mean(axis=(1,2))

    raw_none['_'.join(pt(os.path.basename(file_none)).stem.split("_")[2:6])]=im_none_temporal
    raw_NEO['_'.join(pt(os.path.basename(file_NEO)).stem.split("_")[2:6])]=im_NEO_temporal


## Fitting models
def mono_exp_3vars(t, coeffs):
    return coeffs[0]+coeffs[1]*np.exp(-coeffs[2]*t)

def mono_exp_2vars(t, coeffs):
    return coeffs[0]*np.exp(-coeffs[1]*t)

def bi_exp_5vars(t, coeffs):
    return coeffs[0]+coeffs[1]*np.exp(-coeffs[2]*t) + coeffs[3]*np.exp(-coeffs[4]*t)

def bi_exp_4vars(t, coeffs):
    return coeffs[0]*np.exp(-coeffs[1]*t) + coeffs[2]*np.exp(-coeffs[3]*t)

def resd_1(coeffs, y, t):
    return y - mono_exp_3vars(t, coeffs)

def resd_2(coeffs, y, t):
    return y - bi_exp_5vars(t, coeffs)


lst_model_name = ["mono_exp_3vars", "mono_exp_2vars", "bi_exp_5vars", "bi_exp_4vars", "B-Spline"]
print("Current models (in order): [", ', '.join(lst_model_name),"]")
# ctrlcode = input("please enter the combinations of 1 (enable) or 0 (disable), e.g. 10101, to determine the fitting models: ")
ctrlcode="00001"
passed = False
while not passed:
    if len(ctrlcode) != 5:
        ctrlcode = input("The length of the code is not fit, please enter again: ")
    elif any(c not in ["0", "1"] for c in ctrlcode):
        ctrlcode = input("The input contains elements which are not 1 or 0, please enter again: ")
    else:
        passed = True
        lst_TF_fitting = [bool(int(s)) for s in ctrlcode]
        print("Input code '", lst_TF_fitting, "' accepted!")


df_none_monoExp_fitted = pd.DataFrame()
df_NEO_monoExp_fitted = pd.DataFrame()
df_monoExp_coef = pd.DataFrame()

df_none_biExp_fitted = pd.DataFrame()
df_NEO_biExp_fitted = pd.DataFrame()
df_biExp_coef = pd.DataFrame()

df_none_monoExp_fitted['Time'] = time
df_NEO_monoExp_fitted['Time'] = time



df_none_biExp_fitted['Time'] = time
df_NEO_biExp_fitted['Time'] = time

mask_start = 90
mask_end = 190
masked_none = raw_none.loc[(raw_none["Time"]<mask_start*0.05) | (raw_none["Time"]>= mask_end*0.05)]
masked_NEO = raw_NEO.loc[(raw_NEO["Time"]<mask_start*0.05) | (raw_NEO["Time"]>= mask_end*0.05)]
# degree = 2
knots = 9
xdata_new = np.linspace(0,1,knots+2)[1:-1]



## Initial guess of least squared fit
# for mono exponential
x_0 = np.array([1, 1, 1],dtype=float)
# x_0 = np.array([1000, 0.1],dtype=float)


# for bi-exponential
# x_1 = np.array([1000, 3, 0.5, 3, 0.5],dtype=float)
x_1 = np.array([3, 0.5, 3, 0.5],dtype=float)

xdata = masked_none["Time"]
# xdata = np.array([d - np.min(masked_none["Time"])/(np.max(masked_none["Time"])-np.min(masked_none["Time"])) for d in masked_none["Time"]])
q_knots = np.quantile(xdata, xdata_new)
smooth = 3


for col, col_NEO in zip(raw_none.columns[1:], raw_NEO.columns[1:]):
    # ydata_1 = raw_none[col][0:90]
    # ydata_1 = np.array([d - np.min(masked_none[col])/(np.max(masked_none[col])-np.min(masked_none[col])) for d in masked_none[col]])
    ydata_1 = masked_none[col]
    print(ydata_1.shape)
    # popt_1, pcov_1 = leastsq(resd_1, x_0, args=(ydata_1, xdata), maxfev = 100000)
    # popt_1, pcov_1 = leastsq(resd_3, x_0, args=(ydata_1, xdata), maxfev = 100000)
    # popt_1, pcov_1 = curve_fit(log_model_copy, xdata, ydata_1, maxfev = 100000)
    # print(r2_score(ydata_1, mono_exp_3vars(xdata, popt_1)))
    # print(r2_score(ydata_1, log_model(xdata, popt_1)))
    
    popt_1 = interp.splrep(xdata, ydata_1, t = q_knots, s=smooth)
    baseline_1 = interp.BSpline(*popt_1, extrapolate=True)
    print(r2_score(ydata_1, baseline_1(xdata)))

    # ydata_2 = raw_NEO[col_NEO][0:90]
    # ydata_2 = np.array([d - np.min(masked_NEO[col_NEO])/(np.max(masked_NEO[col_NEO])-np.min(masked_NEO[col_NEO])) for d in masked_NEO[col_NEO]])
    ydata_2 = masked_NEO[col_NEO]
    # popt_2, pcov_2 = leastsq(resd_1, x_0, args=(ydata_2, xdata), maxfev= 100000)
    # popt_2, pcov_2 = leastsq(resd_3, x_0, args=(ydata_2, xdata), maxfev= 100000)
    # popt_2, pcov_2 = curve_fit(log_model_copy, xdata, ydata_2, maxfev = 100000)
    popt_2 = interp.splrep(xdata, ydata_2, t = q_knots, s=smooth)
    baseline_2 = interp.BSpline(*popt_2, extrapolate=True)
    # print(r2_score(ydata_2, mono_exp_3vars(xdata, popt_2)))
    # print(r2_score(ydata_2, log_model(xdata, popt_2)))
    print(r2_score(ydata_2, baseline_2(xdata)))

    # df_none_monoExp_fitted[col] = mono_exp_3vars(time, popt_1)
    # df_NEO_monoExp_fitted[col_NEO] = mono_exp_3vars(time, popt_2)
    df_none_monoExp_fitted[col] = baseline_1(time)
    df_NEO_monoExp_fitted[col_NEO] = baseline_2(time)
    # df_monoExp_coef[col] = popt_1
    # df_monoExp_coef[col_NEO] = popt_2

    # ydata_3 = raw_none[col][0:90]
    # ydata_3 = np.array([d - np.min(masked_none[col])/(np.max(masked_none[col])-np.min(masked_none[col])) for d in masked_none[col]])
    # ydata_3 = masked_none[col]
    # popt_3, pcov_3 = leastsq(resd_2, x_1, args=(ydata_3, xdata), maxfev = 100000)
    # print(r2_score(ydata_3, bi_exp_5vars(xdata, popt_3)))

    # ydata_4 = raw_NEO[col_NEO][0:90]
    # ydata_4 = np.array([d - np.min(masked_NEO[col_NEO])/(np.max(masked_NEO[col_NEO])-np.min(masked_NEO[col_NEO])) for d in masked_NEO[col_NEO]])
    # ydata_4 = masked_NEO[col_NEO]
    # popt_4, pcov_4 = leastsq(resd_2, x_1, args=(ydata_4, xdata), maxfev = 100000)
    # print(r2_score(ydata_4, bi_exp_5vars(xdata, popt_4)))

    # df_none_biExp_fitted[col] = bi_exp_5vars(time, popt_3)
    # df_NEO_biExp_fitted[col_NEO] = bi_exp_5vars(time, popt_4)
    # df_biExp_coef[col] = popt_3
    # df_biExp_coef[col_NEO] = popt_4
    print("\nDATA ", col, "and ", col_NEO, "are fitted")
    print("============================================================")

with pd.ExcelWriter(os.path.join(export_path,'processed.xlsx')) as f:
    raw_none.to_excel(f,sheet_name="raw_df_none",index=False)
    df_none_monoExp_fitted.to_excel(f,sheet_name="df_none_monoExp_fitted",index=False)


    raw_NEO.to_excel(f,sheet_name='raw_df_NEO',index=False)
    df_NEO_monoExp_fitted.to_excel(f,sheet_name="df_NEO_monoExp_fitted",index=False)
    
    # df_monoExp_coef.to_excel(f,sheet_name="df_monoExp_coef",index=False)

    
    # df_none_biExp_fitted.to_excel(f,sheet_name="df_none_biExp_fitted",index=False)
    # df_NEO_biExp_fitted.to_excel(f,sheet_name="df_NEO_biExp_fitted",index=False)
    # df_biExp_coef.to_excel(f,sheet_name="df_biExp_coef",index=False)


# plot to check fitting
plt.figure()
# plt.plot(xdata, ydata_1)
# plt.plot(xdata, mono_exp_3vars(xdata, *popt_1), 'r-',)

# plt.subplot(2,2,1)
plt.subplot(1,2,1)
plt.plot(time, raw_none["2023_10_12-0004"],'.', markersize=4)
# plt.plot(time, mono_exp_3vars(time, popt_1), 'r-')
# plt.plot(time, log_model_copy(time, *popt_1), 'r-')
plt.plot(time, df_none_monoExp_fitted["2023_10_12-0004"], 'r-')
plt.xlabel('time (sec.)')
plt.ylabel('y')
plt.grid('both')
plt.title("ACh puffed in Normal Recording ACSF")
# plt.legend(['raw data','mono exp fitting'])
plt.legend(['raw data','baseline fitting'])

# plt.subplot(2,2,2)
plt.subplot(1,2,2)
plt.plot(time, raw_NEO[col_NEO],'.', markersize=4)
# plt.plot(time, mono_exp_3vars(time, popt_2), 'r-')
# plt.plot(time, log_model_copy(time, *popt_2), 'r-')
plt.plot(time, baseline_2(time), 'r-')
plt.xlabel('time (sec.)')
plt.ylabel('y')
plt.grid('both')
plt.title("ACh puffed in NEO Presented Recording ACSF")
plt.legend(['raw data','mono exp fitting'])

# plt.subplot(2,2,3)
# plt.plot(time, raw_none[col],'.', markersize=4)
# plt.plot(time, bi_exp_5vars(time, popt_3), 'r-')
# plt.xlabel('time (sec.)')
# plt.ylabel('y')
# plt.grid('both')
# plt.title("ACh puffed in Normal Recording ACSF")
# plt.legend(['raw data','bi exp fitting'])

# plt.subplot(2,2,4)
# plt.plot(time, raw_NEO[col_NEO],'.', markersize=4)
# plt.plot(time, bi_exp_5vars(time, popt_4), 'r-',)
# plt.xlabel('time (sec.)')
# plt.ylabel('y')
# plt.grid('both')
# plt.title("ACh puffed in NEO Presented Recording ACSF")
# plt.legend(['raw data','bi exp fitting'])

plt.show()