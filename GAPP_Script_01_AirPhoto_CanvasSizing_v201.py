#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
------------------------------------------------------------------------------
PYTHON SCRIPT FOR THE STANDARDIZING OF AERIAL PHOTO ARCHIVE CANVAS SIZE
------------------------------------------------------------------------------

Version: 2.0.1 (24/12/2021)
Author: Benoît SMETS
        (Royal Museum for Central Africa  /  Vrije Universiteit Brussel)
        Antoine Dille
        (Royal Museum for Central Africa)

Citation:
    Smets, B., 2021
    Historical Aerial Photo Pre-Processing
    [Script_1_AirPhoto_CanvasSizing_v101.py].
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
        > OpenCV
        > Pillow

    - To use this script, simply adapt the directory paths and required values
      in the setup section of the script.

Log:
        - v1.1. (AD)
                - changed the way the image files are selected for better handling of different formats
                - check if output folder exists and create if needed
                - increased max image size handled in PIL to avoid warnings
        - v2.0 (AD)
                - adapted for GAPP (graphic interface)
"""

import os
from PIL import Image
Image.MAX_IMAGE_PIXELS = 300000000
import numpy as np
import cv2
from joblib import Parallel, delayed
import multiprocessing
from time import sleep
from pathlib import Path

################################    SETUP     ################################

##### DIRECTORY PATHS #####
input_image_folder = r"E:\Adille-Data\RESIST\GIS\Optical_Imagery\Aerial_Photographs_Bukavu_1958-59\Aerial_Pictures\Bukavu_1959_CC"
output_image_folder = r"E:\Adille-Data\RESIST\GIS\Optical_Imagery\Aerial_Photographs_Bukavu_1958-59\Aerial_Pictures\Bukavu_1959_CC\CanvasSized_02"

#### PARALLEL PROCESSING #####
# (Choose the number of CPU cores you want to use)
# (minimum = 1; suggested value = (number of cores) - 1)
# (if you don't know how many cores you have, write: 'multiprocessing.cpu_count()')
num_cores = multiprocessing.cpu_count() - 1

################################ END OF SETUP ################################

def main_script_01(input_image_folder, output_image_folder):

    print(' ')
    print('=====================================================================')
    print('=           PYTHON SCRIPT FOR IMAGE CANVAS STANDARDIZING            =')
    print('=  Version 2.0.1 (December 2021)  |  B. Smets/A. Dille (RMCA/VUB)   =')
    print('=====================================================================')
    print(' ')

    os.chdir(input_image_folder)
    ### Define the list of images and count the number of files to process ###
    # also look into sub directory
    allfiles=[]
    allfiles_path=[]
    for root, dirs, files in os.walk(input_image_folder):
        for file in files:
            allfiles.append(file)
            images_list = [image for image in allfiles if image[-4:] in [".tif", ".TIF"]]  # ,".jpg",".JPG"
            images_list = images_list + [image for image in allfiles if image[-5:] in [".tiff", ".TIFF"]]
            allfiles_path.append(os.path.join(root, file))
            images_list_path = [image for image in allfiles_path if image[-4:] in [".tif", ".TIF"]]  # ,".jpg",".JPG"
            images_list_path = images_list_path + [image for image in allfiles_path if image[-5:] in [".tiff", ".TIFF"]]


    # ### Define the list of images and count the number of files to process ###
    # Only main dir
    # allfiles = os.listdir(input_image_folder)
    # images_list = [filename for filename in allfiles if filename[-4:] in [".tif", ".TIF"]]  # ,".jpg",".JPG"
    # images_list = images_list + [filename for filename in allfiles if filename[-5:] in [".tiff", ".TIFF"]]

    print('Number of images to process: ' + str(len(images_list)))
    print(' ')

    ### Detect the max width and height in the dataset ###
    sizes = [Image.open(f, 'r').size for f in images_list_path]
    sizes_array = np.asarray(sizes)
    widths = sizes_array[:, 0]
    heights = sizes_array[:, 1]
    width_max = max(widths)
    height_max = max(heights)

    print('maximum width found = ' + str(width_max) + ' pixels')
    print('maximum height found = ' + str(height_max) + ' pixels')
    print(' ')

    ### Standardize the the canvas size of each image ###
    def standardize_canvas(image_path):
        # Read the images, keep the original pixel depth (-1) and read its dimensions
        # file = os.path.join(input_image_folder, os.path.splitext(os.path.basename(image))[0] + '.tif')
        img = cv2.imread(image_path, -1)
        rows, cols = img.shape
        # Add columns and rows to change the canvas size to maximum width and height
        rows_added = height_max - rows
        cols_added = width_max - cols
        imready = cv2.copyMakeBorder(img, top=0, bottom=rows_added, left=0, right=cols_added,
                                     borderType=cv2.BORDER_CONSTANT, value=0)
        # Save the new image with the standardized size of canvas
        img_name = os.path.splitext(os.path.basename(image_path))[
            0]  # Find the name of the input image, without its file extension, in order to use it into the output image name
        Path(output_image_folder).mkdir(parents=True, exist_ok=True)  # create folder if does no exist
        cv2.imwrite(os.path.join(output_image_folder, img_name + '_CanvasSized.tif'), imready)

    # Use parallel processing
    Parallel(n_jobs=num_cores, verbose=30)(delayed(standardize_canvas)(image_path) for image_path in images_list_path)

    sleep(3)

    print(' ')
    print('======================')
    print(' PROCESSING COMPLETED ')
    print('======================')

    ##### END PROCESSING #####

if __name__ == "__main__":
    main_script_01(input_image_folder, output_image_folder)



