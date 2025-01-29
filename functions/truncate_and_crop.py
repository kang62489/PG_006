## Author: Kang
## Last Update: 2025-Jan-27
## Purpose: To truncate and crop the images for the analysis


## Modules
import os
import shutil
import imageio.v3 as imageio
from rich import print

def truncate_and_crop(dateSets, output_foldername, data_path, export_path, df_ACSF, df_NEO, ROI_coords, cut_start, cut_end, r):
    for out in output_foldername:
        print(f"Processing {out}...\n\n")
        if os.path.isdir(os.path.join(export_path, out)):
            shutil.rmtree(os.path.join(export_path, out))
            os.mkdir(os.path.join(export_path, out))
        else:
            os.mkdir(os.path.join(export_path, out))

        if "NEO" in out:
            filelist = df_NEO["Filename"].tolist()
        else:
            filelist = df_ACSF["Filename"].tolist()

        accum = 0
        for date in dateSets:
            filenames = [s for s in filelist if date in s]
            for n, filename in enumerate(filenames):
                im = imageio.imread(os.path.join(data_path,date,filename))
                cropped_im = im[cut_start:cut_end,ROI_coords[0]:ROI_coords[1],ROI_coords[2]:ROI_coords[3]]
                imageio.imwrite(os.path.join(export_path,out,"ROI_{}_".format(r)+filename), cropped_im, plugin='tifffile') 
                print(f"ROI_{r}_{filename}", " saved!!", f"Current {n+1}/{len(filenames)}", f"Total {accum+1}/{len(filelist)}")
                del im
                accum += 1
        
        print("\n\n")