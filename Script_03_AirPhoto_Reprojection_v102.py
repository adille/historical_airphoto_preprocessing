#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
------------------------------------------------------------------------------
PYTHON SCRIPT FOR AERIAL PHOTO ARCHIVE REPROJECTION INTO A STANDARD FORMAT
BEFORE PHOTOGRAMMETRIC PROCESSING USING AGISOFT METASHAPE PRO
------------------------------------------------------------------------------
This script aims to reproject the aerial photographs based on the pixel coordinates of the fiducial marks, in order
to obtain a homogeneous dataset with the center of perspective located in the middle of the images. To run this script,
you first need to create a table, in csv format, containing the XY coordinates (in pixel) of four fiducial marks used to
locate the center of perspective (see SCRIPT 02). A template of such a table is provided
(*"fiducial_marks_coordinates_TEMPLATE.csv"*). Please, keep the name of each columns similar to those in the
template, as these names are used in the script to find the corresponding information. Image's names, in the
CSV file, must also be similar to the files that will be processed. By default, the fiducial marks 1, 2, 3 and
4 correspond to the top-left, top-right, bottom-right and bottom-left corners, respectively. If the fiducial marks
are located at mid-distance from the corners, the fiducial marks 1, 2, 3 and 4 correspond to the top, right, bottom
and left positions, respectively.

Version: 1.0.2 (09/12/2021)
Authors: Benoît SMETS
        (Royal Museum for Central Africa  /  Vrije Universiteit Brussel)
        &
        Antoine DILLE for version 1.0.2
        (Royal Museum for Central Africa)

Citation:
    Smets, B., 2021
    Historical Aerial Photo Pre-Processing
    [Script_2_AirPhoto_Reprojection_v101.py].
    Version 1.0
    https://github.com/GeoRiskA/historical_airphoto_preprocessing
    DOI: N/A
    
Associated article (to be cited too):
    Smets, B., Dewitte, O., Michellier, C., Muganga, G., Dille, A., Kervyn, F.,
    SUBMITTED
    Insights into the SfM photogrammetric processing of historical
    panchromatic aerial photographs without camera calibration
    information.
    ISPRS International Journal of Geo-Information.
    DOI: N/A

Notes:
    
    - For the required Python libraries, we recommend the use of Anaconda
      or Miniconda.
      
    - Specific Python modules needed for this script:
        > Joblib
        > Numpy
        > OpenCV
        > Pandas
    
    - To use this script, simply adapt the directory paths and required values
      in the setup section of the script.

Log:
        - v1.0.2 (AD)
                - changed the way the image files are selected for better handling of different format
                - modified output size so that no 'image data' is lost in the process
                - adapted the naming convention of fiducial mark template
                - check if output folder exists and create if needed
                - improved image save name (only one '.tif')
                - handle two cases if image name column in csv has/has no extension

"""

import numpy as np
import os, pandas as pd
import cv2
from joblib import Parallel, delayed
import multiprocessing
from time import sleep
from pathlib import Path

# ----------------------------------------------------------------------------
################################    SETUP     ################################
# ----------------------------------------------------------------------------

##### DIRECTORY PATHS ##### (for Windows paths, please use "//" between directories ; for Mac, simply use "/" between directories)

input_image_folder = r"E:\Adille-Data\RESIST\GIS\Optical_Imagery\Aerial_Photographs_Bukavu_1958-59\Aerial_Pictures\Bukavu_1959_CC\CanvasSized_02"

fiducialmarks_file = r"C:\Users\adille\Desktop\Tests\SCANs\Fiducials_Barriere\Bukavu_1959\fiducial_marks_coordinates_Bukavu_1959.csv"
CSV_Separator=';' # separator for columns in csv files (e.g., ',' or ';')

output_image_folder = r"E:\Adille-Data\RESIST\GIS\Optical_Imagery\Aerial_Photographs_Bukavu_1958-59\Aerial_Pictures\Bukavu_1959_CC\CanvasSized_02\Reprojected"


'''
fiducialmarks_file.csv example:

name	X1	Y1	X2	Y2	X3	Y3	X4	Y4
5942_005_CC_CanvasSized.tif	636	916	10383	766	10469	10424	730	10580
5968_Bande-19-072_CanvasSized.tiff	727	750	11218	699	11175	11003	722	11061

'''


##### NEW COORDINATES OF FIDUCIAL MARKS #####
    # (1 = upper left; 2 = upper right; 3 = lower right; 4 = lower left)
    # (If the fiducial marks are at the medians: 1 = up; 2 = right; 3 = down ; 4 = left)

# pts2 = np.float32([[473,473],[12923,473],[12923,12923],[473,12923]])
pts2 = np.float32([[673,673],[12723,673],[12723,12723],[673,12723]])

##### DIMENSIONS OF THE OUTPUT IMAGE #####

dimX = 13395
dimY = 13395

#### PARALLEL PROCESSING #####
    # (Choose the number of CPU cores you want to use)
    # (minimum = 1; suggested value = (number of cores) - 1)
    # (if you don't know how many cores you have, write: 'multiprocessing.cpu_count()')

num_cores = multiprocessing.cpu_count() - 1

# ----------------------------------------------------------------------------
################################ END OF SETUP ###############################
# ----------------------------------------------------------------------------

print(' ')
print('=====================================================================')
print('=         PYTHON SCRIPT FOR AIR PHOTO ARCHIVE PREPROCESSING         =')
print('=         Version 1.0.2 (December 2021)  |  B. Smets (RMCA/VUB)          =')
print('=====================================================================')
print(' ')

##### DEFINE ADDITIONAL USEFUL VARIABLES #####

allfiles=os.listdir(input_image_folder)
images_list=[filename for filename in allfiles if filename[-4:] in [".tif",".TIF"]] #,".jpg",".JPG"
images_list = images_list + [filename for filename in allfiles if filename[-5:] in [".tiff",".TIFF"]]

FM = pd.read_csv(fiducialmarks_file,sep=CSV_Separator, header=[0])
number_images = str(len(FM))

##### DISPLAY THE NUMBER OF IMAGES TO PROCESS #####

print('Number of tasks (images to process): ' + number_images)
print(' ')

##### PROCESSING WORKFLOW #####

def reproject_and_crop(image):
        # Read the images, keep the original pixel depth (-1) and read its dimensions
        dst_filename = os.path.join(input_image_folder, image ) #os.path.splitext(os.path.basename(image))[0] + '.tif')
        img = cv2.imread(dst_filename, -1)
        rows, cols = img.shape
        print('working on image: ' + image)
        
        # Extract the image name and find the corresponding row with fiducial marks coordinates, in the CSV file
        try:
                name_col=FM['name']
                df=FM[name_col.str.contains(image)]
                x = FM.loc[name_col == image].index[0]

        except: # try with an extension to the name items"
                name_col = FM['name'] + '.tif'
                df = FM[name_col.str.contains(image)]
                x = FM.loc[name_col == image].index[0]


        pts1 = np.float32([[df['X1'][x],df['Y1'][x]],[df['X2'][x],df['Y2'][x]],[df['X3'][x],df['Y3'][x]],[df['X4'][x],df['Y4'][x]]])

        # Reproject the image by applying the new coordinates of the fiducial marks and crop it at the provided dimensions
        M = cv2.getPerspectiveTransform(pts1,pts2)
        imready = cv2.warpPerspective(img,M,(dimX,dimY))
        
        # Export the reprojected and cropped images
        Path(output_image_folder).mkdir(parents=True, exist_ok=True) # Check if output folder exists
        cv2.imwrite(os.path.join(output_image_folder, str(image.split('.')[0]) + '_standardized.tif'), imready)

##### PARALLEL PROCESSING #####

Parallel(n_jobs=num_cores, verbose=30)(delayed(reproject_and_crop)(image) for image in images_list)

##### END PROCESSING #####

sleep(3)

print(' ')
print('======================')
print(' PROCESSING COMPLETED ')
print('======================')
