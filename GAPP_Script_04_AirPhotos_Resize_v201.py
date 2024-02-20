"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
------------------------------------------------------------------------------
PYTHON SCRIPT FOR AERIAL PHOTO ARCHIVE RESIZING TO LOWER DPI
BEFORE PHOTOGRAMMETRIC PROCESSING USING AGISOFT METASHAPE PRO
------------------------------------------------------------------------------

# In order to smooth the potential noise introduced by the reprojection of each image, **I strongly suggest to
downsample the images to a lower resolution**. At the RMCA, we scan the photos at a resolution of 1600 dpi
(except for specific collections), which is, in general, too much considering the quality of the collections. So,
we use to resample the reprojected photos to 900 dpi (+ or - 300 dpi, depending on the quality of the dataset). The
script will resize all the images in a folder to a user defined resolution value using bicubic interpolation. An
unsharp mask can be applied after the interpolation, as well as a adaptative histogram calibration (CLAHE). Applying
an unsharp mask is an image sharpening technique commonly used in digital image processing software after downscaling
to maintain details in the image despite size changes (e.g. used by default in photoshop when downscaling an image).
The technique uses a blurred, or "unsharp", negative image to create a mask of the original image. The unsharp mask is
then combined with the original positive image, creating an image that is less blurry than the original.

Version: 2.0.1 (24/12/2021)
Authors: Antoine DILLE for version 1.0.1, v2
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

    - To use this script, simply adapt the directory paths and required values
      in the setup section of the script.

Log:
        - v1.0.1 (AD)
        - v2.0.1 (AD)
                - adapted for GAPP (graphic interface)
Todo:
    - could be parallelized, but not sure it would be really faster (main limitation being probably the disk writing capacity)

Different options
    - OpenCV
    - Pillow
    - scikit image

see for unsharp mask in python
- https://www.idtools.com.au/unsharp-masking-with-python-and-opencv/
- https://stackoverflow.com/questions/32454613/python-unsharp-mask/32455269


"""

import os
import time
from pathlib import Path

import cv2
import numpy as np

# ----------------------------------------------------------------------------
################################    SETUP     ################################
# ----------------------------------------------------------------------------

image_folder=r"E:\Adille-Data\RESIST\GIS\Optical_Imagery\Aerial_Photographs_Bukavu_1958-59\Aerial_Pictures\Bukavu_1959_CC\CanvasSized_02\Reprojected"
output_folder = image_folder + '/Downscaled_60_2_hist'

extension = '.tif' #'.png'. output file extension
tool = 'opencv' #opencv works best, and is the only one thoroughly tested. also 'pillow' and 'scikit'
HistoCal = True # apply Contrast Limited adaptive histogram equalization to image (CLAHE)
scale_percent = 60  # percent of original size. e.g., with 60% -->  1500dpi*0.6=900 dpi
SharpeningIntensity = 2 # [0, 1 or 2]; 0 for no sharpening, 1 for low intensity, 2 for medium intensity sharpening.
                        # can be further tuned in the function unsharp_mask_OpenCV

# ----------------------------------------------------------------------------
################################ END OF SETUP ###############################
# ----------------------------------------------------------------------------
def main_script_04(image_folder, output_folder, scale_percent, HistoCal, SharpeningIntensity ):

    print(' ')
    print('=====================================================================')
    print('=         PYTHON SCRIPT FOR AIR PHOTO ARCHIVE DOWNSAMPLING         =')
    print('=         Version 2.0.1 (December 2021)  |  A. Dille (RMCA/VUB)     =')
    print('=====================================================================')
    print(' ')

    # --------------------------------------------------
    # listing files to process
    # --------------------------------------------------
    allfiles=os.listdir(image_folder)
    imlist=[filename for filename in allfiles if filename[-4:] in [".tif",".TIF",".png",".jpg",".JPG"]]
    imlist = imlist + [filename for filename in allfiles if filename[-5:] in [".tiff",".TIFF"]]

    resizedimlist=[]

    print('\n-------------------------------'
          '\n-------------------------------\n'
          ' > found ' + str(len(imlist)) + ' images to process'
          '\n-------------------------------'
          '\n-------------------------------\n')

    # --------------------------------------------------
    # Functions
    # --------------------------------------------------

    def unsharp_mask_OpenCV(image, kernel_size=(3, 3), sigma=1.0):
        im_blurred = cv2.GaussianBlur(image, kernel_size, sigma) # First we blur the image. By smoothing an image we suppress
        # most of the high-frequency components.

        # Second we subtract this smoothed image from the original image(the resulting difference is known as a mask).
        # Thus, the output image will have most of the high-frequency components that are blocked by the smoothing filter.
        # Adding this mask back to the original will enhance the high-frequency components.
        if SharpeningIntensity == 1: # low intensity
            sharpened = cv2.addWeighted(image, 2, im_blurred, -1.0, 0)
        elif SharpeningIntensity == 2: # medium intensity
            sharpened = cv2.addWeighted(image, 1.0 + 3.0, im_blurred, -3.0, 0)

        return sharpened

    # functions
    def unsharp_mask_Pillow(image, Inradius=3):
        from PIL import ImageFilter
        sharpened = image.filter(ImageFilter.UnsharpMask(radius=Inradius, percent=150))
        return sharpened


    def OpenCVDownscaler(imlist, scale_percent):
        # A. Downscaling with OpenCV
        count=1
        for image in imlist:
            print('\n >>> Image [' + str(count) + '/' + str(len(imlist)) + ']: ' + image)
            img = cv2.imread(image_folder + '\\' + image, cv2.IMREAD_UNCHANGED)
            print('     Original Dimensions : ', img.shape)


            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            # resize image
            resized = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC ) #INTER_CUBIC is a bicubic interpolation

            """[optional] flag that takes one of the following methods. INTER_NEAREST – a nearest-neighbor interpolation INTER_LINEAR
            – a bilinear interpolation (used by default) INTER_AREA – resampling using pixel area relation. It may be a
            preferred method for image decimation, as it gives moire’-free results. But when the image is zoomed, it is
            similar to the INTER_NEAREST method. INTER_CUBIC – a bicubic interpolation over 4×4 pixel neighborhood INTER_LANCZOS4 – a
            Lanczosinterpolation over 8×8 pixel neighborhood
            """

            print('     Resized Dimensions : ', resized.shape)

            # B. apply unsharp mask to resized image
            if SharpeningIntensity >0:
                resized=unsharp_mask_OpenCV(resized, kernel_size=(3, 3), sigma=1.0)

            # C. apply Contrast Limited adaptive histogram equalization to image (CLAHE)
            if HistoCal is True:
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(40,40))
                resized = clahe.apply(resized)


            # D. Save the image
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            resized_name= image[:-4] + "_DownSharp" + extension
            downSname = output_folder + '/' + resized_name   # output filename

            # Saving the image using cv2.imwrite() method
            cv2.imwrite(downSname, resized)
            print( '    -> saved to: ' + downSname)
            resizedimlist.append(resized_name)
            count = count + 1


    if tool == 'opencv':
        print('\n --------------------------------------'
              '\n Using OpenCV to resize the images \n '
              '-----------------------------------------\n')
        start_time = time.time()

        OpenCVDownscaler(imlist, scale_percent) # main

        print("\n--- data processing time was %.2f s seconds ---\n" % (time.time() - start_time))

        #check number of file processed compared to input files
        outfiles = os.listdir(output_folder)
        outimlist = [filename for filename in outfiles if filename[-4:] in [".tif", ".TIF", ".png", ".jpg", ".JPG"]]
        outimlist = outfiles + [filename for filename in outimlist if filename[-5:] in [".tiff", ".TIFF"]]
        if len(imlist) != len(outimlist):
            print('*** WARNING ***')
            print('! it seems that some image(s) have not been processed!')
            print('--> # of input images= ' + str(len(imlist)) + ' while # of processed images= ' + str(len(outimlist)) + ' <--')
            print('*** WARNING ***')


if __name__ == "__main__":
    main_script_04(image_folder, output_folder, scale_percent, HistoCal, SharpeningIntensity)