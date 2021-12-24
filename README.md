# Historical Aerial Photo Pre-Processing  
[![DOI](https://zenodo.org/badge/366727725.svg)](https://zenodo.org/badge/latestdoi/366727725)  
*Last modified: 18th May 2021*  

The present repository contains a series of scripts that are useful to prepare datasets of scanned aerial photographs before their photogrammetric processing. The goal here is to go from raw scanned photographs to sets of images that have **1)** identical pixel dimensions in width and height, and **2)** the center of perspective relocated at the center of the image, based on the fiducial marks (i.e., "interior" or "intrinsic" orientation).  
  
All these scripts were developed in the frame of the **PAStECA Project** (BELSPO, BRAIN-be Programme, Contract n° BR/165/A3/PASTECA, http://pasteca.africamuseum.be/). They were written in Python 3.
  
Each script can be run by simply adapting the necessary parameters in the "setup" section of the script **or** together using a simple graphical interface based on tkinter. All these scripts have the same 4-part structure:  
  
*1) A header providing a description of the script, the name of the authors, the required Python modules, the reference to cite if used, etc.*  
*2) A section with the Python modules to install (in addition to the recommended Anaconda/Miniconda Package distribution)*  
*3) The SETUP section with the variables and parameters that must be adapted by the user (only part that must be modified before use)*  
*4) The required coding to perform the task (should not be modified, except for specific user needs)*  
  
To get the required Python working environment, the followed philosophy was to install the Anaconda/Miniconda Distribution for Python 3, create a virtual environment dedicated to the processing of aerial photographs (using "conda create --name *myenv* python=3") and add the required modules using the "conda install" or "pip install" functions. The required Python modules that are needed for each script are mentioned in the header of the script.  
  
Each script has been optimized for speed by parallelizing the job using the Multiprocessing module.  
  
The scripts have also been adapted to display information about the ongoing processing in the Python console or terminal.  
  
The Python scripts are under a *GPL-3.0 license*. They are attached to a specific DOI (10.5281/zenodo.4770166) and can be cited as follow:  
**Author:** Smets, B.  
**Year:** 2021  
**Title:** Historical Aerial Photo Pre-Processing  
**URL:** https://github.com/GeoRiskA/historical_airphoto_preprocessing  
**DOI:** 10.5281/zenodo.4770166  
  
The scripts are also attached to the following peer-reviewed article (not published yet):  
**Authors:** *Smets, B., Dewitte, O., Michellier, C., Muganga, G., Dille, A., Kervyn, F.*  
**Title:** *Insights into the SfM photogrammetric processing of historical panchromatic aerial photographs without camera calibration information*  
**Journal:** *International Journal of Geo-Information (submitted)*  
  
If you use these scripts or an adapted version of them, please, cite the references of the repository and article in your work. Thank you in advance! (The publication status of the article will be adapted asap) 

All the scripts provided here are created by an Earth Scientist with self-learned programming skills. They can definitely be improved by a professional programmer. So, if you have constructive comments or recommendations that could help me to improve or speed up these scripts, please do not hesitate to contact me! I thank you in advance.  
  
**Benoît Smets**   
- Senior Researcher, Natural Hazards Service (GeoRiskA), Royal Museum for Central Africa (Tervuren, Belgium)  
- Assistant Professor, Cartography & GIS Research Group, Dpt. of Geography, Vrije Universiteit Brussel (Brussels, Belgium)  
  
To contact me --> MyFirstName.MyLastName@africamuseum.be or MyFirstName.MyLastName@vub.be  
  
    
-----  
  
**!!! PLEASE READ THE FOLLOWING DESCRIPTION BEFORE USING THE SCRIPTS FOR THE FIRST TIME !!!**  


## GAPP_AirPhotoPreprocessing_main_v101
This script provide a graphic interface for controlling and launching all scripts at once. It offers to tune some of the main parameters and launch one or multiple GAPP scripts.

**The required Python modules:**  
*- tKinter* 

![GAPP interface](https://github.com/adille/historical_airphoto_preprocessing/blob/GAPP/figures/GAPP_interface.JPG)


## SCRIPT 00 - Tool: FiducialTemplateCreator (optional)
*Current version:* **1.0.1** *(22nd December 2021)*  

This script aims at creating templates for the four fiducial (corners) of an aerial image for later automatic detection of the fiducials on a large set of aerial images (see SCRIPT 02 - Automatic Fiducials Detection). Simply provide the path of one image of the set with representative fiducial marks. Note that SCRIPT 02 allows to test multiple templates. Good practice to lauch it before GAPP_AirPhotoPreprocessing_main_v101.

**The required Python modules:**  
*- OpenCV* 
*- Matplotlib*  
*- Pathlib*  

**The parameters to provide are:**  
*- The path of one image of the set*  
*- The coordinates (in pixel) of the four fiducial mark center*  
*- The half-width of the fiducial mark*  
*- An output folder path where the templates images and a text file with the coordinates of the fiducial centre will be saved*  
*- A name for the dataset*  


## SCRIPT 01: AirPhoto_CanvasSizing 
*Current version:* **1.0.2** *(22nd December 2021)*  
  
This script aims to get images with the same number of pixels in width and height, which is not always the case with scanned photographs. The script will look at all photographs available in a given directory **and subdirectories** and search for the maximum width and height values in the dataset. Once found, it will homogenize the dataset by adding rows and/or columns of black pixels to images that don't have these maximum dimensions.  
  
**The required Python modules:**  
*- Joblib*  
*- OpenCV*  
*- Pillow*  
  
**The parameters that have to be adapted by the user:**  
*- Input folder (where the raw scans are located)*  
*- Output folder (where the resized images will be saved)*  
*- The number of CPU cores to use for the parallel processing (by default: max - 1)*  
  
The output images will be saved with the same name as the input images, complemented with "_CanvasSized". The images will be saved in tif format, as I personnally only work with raw (uint16) tif files. If you want to change this, you have to adapt the file format in the script, in line 109.  
  

## SCRIPT 02: AutomaticFiducialDetection  
*Current version:* **1.1.0** *(22nd December 2021)*  
  
This script aims to detect the (pixel coordinates) centre of the four fiducial marks of an aerial image. This information will be used to reproject the aerial photographs in order to obtain a homogeneous dataset with the center of perspective located in the middle of the images (see SCRIPT 03: AirPhoto_reprojection). It requires one (or more) template for each fiducial of a typical aerial image of the dataset (see SCRIPT 00 - Tool: FiducialTemplateCreator to create such templates). One can precise the presence of stripes with no data around some side of the image. Note that: a) it is OpenCV tool matchTemplate that is used, the latter is not able to account for change in size nor orientation (e.g., rotation) between the template and the image (--> so consider using SCRIPT 00 to have templates at the correct size for your dataset); b) for now it only handles fiducials located in the corner of the image; c) there are some checks to monitor the accuracy of the matching and provide warnings, but sometimes it is not sufficient --> do not hesisitate to do a visual check of the coordinates found. To help with that, one figure with the location of the four fiducials is created for each images and saved in folder >/_temp_corners/_all_fiducials).  

  
***The required Python modules:**  
*- Joblib*  
*- Numpy*  
*- OpenCV*  
*- Pandas*  
*- Matplotlib*  
*- Pathlib*  
*- Pillow*  

  
**The parameters that have to be adapted by the user:**  
*- A name for the dataset*  (used to find adequate reference template)
*- An image folder with the "canvas-sized" images (see SCRIPT 01)*  
*- The path to folder with the fiducial template (see SCRIPT 00)*  
*- The path to csv file where the centre of the fiducial template is indicated (see SCRIPT 00)*  
*- An output folder where temporary fiducials of the images will be saved for later check *  
*- A file path for the csv file with the pixel coordinates of the fiducial marks*  
*- The relative size and location of stripe of no-data within aerial images (e.g., balck stripe on on left and bottom of images) *  
*- The  size of the zones used to look for the fiducials within each image *  
*- A threshold value to define a good match (the higher the more confident) *  
*- The number of CPU cores to use for the parallel processing (by default: max - 1)*   
  

![Automatic Fiducial Detection](https://github.com/adille/historical_airphoto_preprocessing/blob/GAPP/figures/GAPP_fiducial_automatic_detection.JPG)


## SCRIPT 03: AirPhoto_reprojection  
*Current version:* **1.0.2** *(22nd December 2021)*  
  
This script aims to reproject the aerial photographs based on the pixel coordinates of the fiducial marks, in order to obtain a homogeneous dataset with the center of perspective located in the middle of the images. To run this script, you first need to create a table, in csv format, containing the XY coordinates (in pixel) of four fiducial marks used to locate the center of perspective (see SCRIPT 02). A template of such a table is provided (*"fiducial_marks_coordinates_TEMPLATE.csv"*). Please, keep the name of each columns similar to those in the template, as these names are used in the script to find the corresponding information. Image's names, in the CSV file, must also be similar to the files that will be processed. By default, the fiducial marks 1, 2, 3 and 4 correspond to the top-left, top-right, bottom-right and bottom-left corners, respectively. If the fiducial marks are located at mid-distance from the corners, the fiducial marks 1, 2, 3 and 4 correspond to the top, right, bottom and left positions, respectively. 
  
***The required Python modules:**  
*- Joblib*  
*- Numpy*  
*- OpenCV*  
*- Pandas*  
  
**The parameters that have to be adapted by the user:**  
*- Input folder (with the "canvas-sized" images)*  
*- Directory path of the csv file with the pixel coordinates of the fiducial marks*  
*- Output folder (where the standardized images will be saved)*  
*- The new pixel coordinates of the fiducial marks in the output images (must be estimated based on the type of photo and scanning resolution)*  
*- The dimensions in width (X) and height (Y) of the output images (unit = pixel)*  
*- The image format of the input images (e.g., tif, jpeg, png, etc.)*  
*- The number of CPU cores to use for the parallel processing (by default: max - 1)*   
  
The output images will be saved with the same name as the input images, complemented with "_standardized". The images will be saved in tif format, as I personally only work with raw (uint16) tif files. If you want to change this, you have to adapt the file format in the script, in line 130.

## SCRIPT 04: AirPhoto_Resize [Downsampling of the images]
*Current version:* **1.0.1** *(22nd December 2021)*  

In order to smooth the potential noise introduced by the reprojection of each image, **I strongly suggest to downsample the images to a lower resolution**. At the RMCA, we scan the photos at a resolution of 1600 dpi (except for specific collections), which is, in general, too much considering the quality of the collections. So, we use to resample the reprojected photos to 900 dpi (+ or - 300 dpi, depending on the quality of the dataset). The script will resize all the images in a folder to a user defined resolution value using bicubic interpolation. An unsharp mask can be applied after the interpolation, as well as a adaptative histogram calibration (CLAHE). Applying an unsharp mask is an image sharpening technique commonly used in digital image processing software after downscaling to maintain details in the image despite size changes (e.g. used by default in photoshop when downscaling an image). The technique uses a blurred, or "unsharp", negative image to create a mask of the original image. The unsharp mask is then combined with the original positive image, creating an image that is less blurry than the original.

***The required Python modules:**  
*- Numpy*  
*- OpenCV*  

## SCRIPT 05: CreateSingleMask (optional)
*Current version:* **1.0.1** *(18th May 2021)*  

This script is only useful for photogrammetric software that allows you to apply a single mask file to all the photos of the same dimensions, like with Agisoft Photoscan/Metashape Pro.

This script aims to create a mask with the same dimensions of the preprocessed photos (i.e., photos sized, reprojected and downsampled). The mask consists of rectangles hiding the image corners, where the fiducial marks are ususally still visible on the final photos. In a future version of the script, an option will be added to hide fiducial marks that are at mid-distance between the corners of the image.

**The required Python modules to add (in addition to the Anaconda Distribution):**  
*- Glob*   
*- Numpy*  
*- Pillow*  

**The parameters that have to be adapted by the user:**  
*- Input folder (with the reprojected photos)*  
*- Output mask folder (where the mask will be stored)*  
*- The image format (of the reprojected photos)*  
*- The size of the rectangles to mask in the corners of the photos (in percentage of the photo's width and height)*  
*- The name of the dataset (i.e., the name you will give to the mask)*  

The output mask will be saved with the given name of the dataset, complemented with "_mask". The mask will be saved in png format, as Agisoft Photoscan/Metashape Pro preferentially works with this format for masks. If you want to change this, you have to adapt the mask format in the script, in line 133.


-----

**Prof. Dr. Benoît SMETS**  
Natural Hazards Service (GeoRiskA)  
ROYAL MUSEUM FOR CENTRAL AFRICA -- Tervuren, Belgium  
Cartography & GIS Research Group (CGIS)  
VRIJE UNIVERSITEIT BRUSSEL -- Brussels, Belgium  
  
https://georiska.africamuseum.be/en  
https://we.vub.ac.be/en/cartography-and-gis  
http://www.virunga-volcanoes.org/  
https://bsmets.net/  
