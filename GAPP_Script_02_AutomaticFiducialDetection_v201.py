#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
------------------------------------------------------------------------------
PYTHON SCRIPT FOR AERIAL PHOTOS AUTOMATIC FIDUCIAL DETECTION
------------------------------------------------------------------------------
This script aims to detect the (pixel coordinates) centre of the four fiducial marks of an aerial image. This
information will be used to reproject the aerial photographs in order to obtain a homogeneous dataset with the
center of perspective located in the middle of the images (see SCRIPT 03: AirPhoto_reprojection). It requires one
(or more) template for each fiducial of a typical aerial image of the dataset (see SCRIPT 00 -
Tool: FiducialTemplateCreator to create such templates). One can precise the presence of stripes with no
data around some side of the image. Note that: a) it is OpenCV tool matchTemplate that is used, the latter
is not able to account for change in size nor orientation (e.g., rotation) between the template and the image
(--> so consider using SCRIPT 00 to have templates at the correct size for your dataset); b) for now it only
handles fiducials located in the corner of the image; c) there are some checks to monitor the accuracy of the
matching and provide warnings, but sometimes it is not sufficient --> do not hesisitate to do a visual check of
the coordinates found. To help with that one figure with the location of the four fiducials is created for each images
(in folder >/_temp_corners/_all_fiducials).

Version: 2.0.1 (24/12/2021)
Authors: Paul Barriere for V1.0
        &
        Benoît SMETS
        (Royal Museum for Central Africa  /  Vrije Universiteit Brussel)
        &
        Antoine DILLE for v1.1, v2
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

General notes:
    - For the required Python libraries, we recommend the use of Anaconda
      or Miniconda.
    - To use this script, simply adapt the directory paths and required values
      in the setup section of the script.

Processing notes:
    - As it is now it only works with fiducials located at the corner of the image
    - Can use "Script_00_Tool_FiducialTemplateCreator_v101.py" to create fiducial templates
    - Can use more than one template per corner (simply add increasing number at the end of the name)

Log:
        - v1.1. (AD)
                - improved naming convention + commenting
                - improved the way the black strips around photos are considered
                - added checks for wrong matching (the list will be added to a CSV + Figure)
                - added new runs with larger fiducial corner window for wrong matches + try with circle detection
                - can use multiple templates for each corner as input
                - changed the way the image files are selected for better handling of different format
                - check if output folder exists and create if needed
                - ...
        - v2.0 (AD)
                - adapted for GAPP (graphic interface)
"""


import os, sys, copy, csv
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib
from math import atan,pi, sin, cos
from time import sleep
import multiprocessing
from joblib import Parallel, delayed
import cv2
from PIL import Image
import json
matplotlib.use('Agg') # so that no figures are showing up (note that it may pose problems when using Spyder (?))


# ----------------------------------------------------------------------------
################################    SETUP     ################################
# ----------------------------------------------------------------------------



# input: dataset
dataset='Dataset_01' # image dataset name (e.g., 'Virunga_1958'). this variable is include in the template name (e.g., Template_Virunga_1958_top_left_1.tif)

# input: images
image_folder = r"D:\PROCESSING\SCANS\Test_SCANS_GAPPS\output\01_CanvasSized" # where are located the images to process

# input: fiducial templates
fiducial_template_folder = r"D:\PROCESSING\SCANS\Test_SCANS_GAPPS\Fiducial_templates_01" # folder with the template images
center_fidu_tempate_CSV= fiducial_template_folder + "/Center_Fiducials.txt" #text file where the centre of the template is indicated
'''
e.g., of Center_Fiducials.txt
Template Xc Yc 
Template_Virunga_1958_top_left_1 220 220
Template_Virunga_1958_top_left_2 220 220            ## if one want to use multiple templates for one corner side have to change the integer at the end
Template_Virunga_1958_top_right_1 220 220
'''


# outputs
corner_folder=rf"{image_folder}/_temp_corners_{dataset}" # folder where temporary fiducials of the images (i.e., where
            # the fiducial marks are located) will be saved
input_image_folder = image_folder # folder where the images are located
type_fidu = "barycentre" # parameter for ShiTomasi corner detection. 'fixed' or 'barycentre'
Out_fiducialmarks_CSV = rf"{image_folder}/fiducial_marks_coordinates_{dataset}.csv" # output with the
#  location of the fiducial centre


RunParallel = True # to run using parallel processing (otherwise will process one image after the other
DebugMode = False # will provide more info about subprocess to the console for checking
OneTemplateMax = True  # if True it will only use the first matching template. If False it will take more time...

#### SOME PARAMETERS #####
p=0.05 # percentage of black stripe width compare to the total width of the picture (e.g., 0.05). To be associated with parameter >> black_stripe_location
black_stripe_location = ['bottom' , 'right'] # ['bottom' , 'right'] # should be included in 'top' 'left' 'right' 'bottom' or 'None'
S=2500  #size of the sub-image around the fiducial for template matching (square of S pixels in size)
MatchingValueThreshold= 0.85 # value to define a good match. See OpenCV cv2.matchTemplate. Should probably be included between 0.75 and 0.90
DPI=200 # resolution of figures for visual check
Fiducial_type = 'target' # type : target or rectangle or cross. Should be target for now ;)


#### PARALLEL PROCESSING #####
    # (Choose the number of CPU cores you want to use)
    # (minimum = 1; suggested value = (number of cores) - 1)
    # (if you don't know how many cores you have, write: 'multiprocessing.cpu_count()')
num_cores = multiprocessing.cpu_count() - 1

# ----------------------------------------------------------------------------
################################ END OF SETUP ###############################
# ----------------------------------------------------------------------------

# functions

def toCSV(image,Coo):
    """
    Fonction detecting the manual marking of fiducial marks and returning a csv line corresponding.

    :param image: path of the image file
    :type image: string

    :return: line to fill the csv file (corresponding to the image)
    :rtype : string
    """
    line = ";".join([os.path.splitext(os.path.basename(image))[0],str(Coo['top_left'][0]),str(Coo['top_left'][1]),str(Coo['top_right'][0]),str(Coo['top_right'][1]),str(Coo['bot_right'][0]),str(Coo['bot_right'][1]),str(Coo['bot_left'][0]),str(Coo['bot_left'][1])])
    return(line)

def addLine(image_name, Fiducial_Coordinates, Out_fiducialmarks_CSV):
    """
    Fonction adding a line to the csv we are creating
    
    :param image: path of the image file
    :type image: string
    
    :return: None
    """
    line=[toCSV(image_name,Fiducial_Coordinates)]
    f = open(Out_fiducialmarks_CSV, "a",newline='')
    w = csv.writer(f,delimiter=",")
    w.writerow(line)
    f.close()
    
def distance(matrice,xc,yc):
    """
    Calculate distance between 2 points
    
    :param matrice: matrice of points'coordinates
    :type matrice: numpy [int,int]
    :param xc: pixel's column of the center in template image
    :type xc: int
    :param yc: pixel's line of the center in template image
    :type yc: int
    
    :return: distance between 2 points 
    :rtype: float

    """
    dx = matrice[:,:,0]-xc
    dy = matrice[:,:,1]-yc
    return np.sqrt(dx**2 + dy**2)
    
def CenterFiducial_LUCASKANADE(img2,Fidu_type,orientation,template,xc,yc,image_name, corner,type_fidu, corner_folder):
     """
    allow to detect and give the coordinates of a fiducial mark using the Lucas Kanade filter
    
    :param img2: image cropped where the fiducial should be 
    :type img2: .tif
    :param Fidu_type: type of fiducial : 'rectangular'; 'target'
    :type Fidu_Type: str
    :param template:image of the template of the fiduciale
    :type template: .tif
    :param orientation: orientation of rectangular fidicial 'h' : horizontal or 'v' : vertical
    :type orientation: str
    :param xc: pixel's column of the center in template image
    :type xc: int
    :param yc: pixel's line of the center in template image
    :type yc: int
    
    :return: u,v Coordinates of the fiducial
    :rtype: int,int
    """
     text=image_name + '_' + corner
     if Fidu_type =='target':
         res = cv2.matchTemplate(img2,template,cv2.TM_CCOEFF_NORMED)
         (_, maxVal, _, maxLoc) = cv2.minMaxLoc(res) #maxloc = (u,v)

         if DebugMode is True:
            # print(img2.shape)
            print('     template matching statistics for '+ corner +' > Max value: ' + str(maxVal) + ' | ' + str(maxLoc))

            # Create a fancy figure
            import matplotlib.patches as patches
            fig, axs = plt.subplots(1, 2, figsize=(6, 4))
            fig.suptitle(text, fontweight="bold")
            axs[0].imshow(img2, cmap=plt.cm.gray)
            axs[0].set_title('corner image')
            # Add a rectangle with location of template
            rect = patches.Rectangle((maxLoc[0], maxLoc[1]), template.shape[0], template.shape[1], linewidth=2, edgecolor='r', facecolor='none')
            # Add the patch to the Axes
            axs[0].add_patch(rect)
            axs[1].imshow(template, cmap=plt.cm.gray)
            axs[1].set_title('template')


         Sfid=0
         Img=img2[maxLoc[1]-Sfid:maxLoc[1]+template.shape[0]+Sfid,\
                                maxLoc[0]-Sfid:maxLoc[0]+template.shape[1]+Sfid] # temlate and image should have the same size
         im_gray = cv2.cvtColor(Img,cv2.COLOR_BGR2GRAY)
         # template = cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)

        # find the corners (ie points of reconition) in the image---------------
        #-----------------------------------------------------------------------
        # params for ShiTomasi corner detection
         if type_fidu == "barycentre":
             feature_params = dict(maxCorners = 25,
                           qualityLevel = 0.01,
                           minDistance = 3,
                           blockSize = 3)
    
             p0 = cv2.goodFeaturesToTrack(im_gray, **feature_params)
             d = distance(p0,xc,yc)
             err=np.argsort(d,axis=0)
             if(d[err[0][0]][0] >= 15 ):
                 x=xc
                 y=yc
             else:
                 i=0
                 x=0
                 y=0
                 while( i < 4 and  d[err[i][0]][0] < 15):
                     x+=p0[err[i][0]][0][0]
                     y+=p0[err[i][0]][0][1]
                     i+=1         
                 x = x/i
                 y = y/i

            # Match the fiducial on the picture------------------------------------
            #-----------------------------------------------------------------------
            # Parameters for lucas kanade optical flow
             final_mask=copy.deepcopy(im_gray)
             final_mask = cv2.circle(final_mask,(int(round(x)),int(round(y))),1,255,-1)
             save_folder_path=corner_folder + '/' + corner + "/barycentre/"
             Path(save_folder_path).mkdir(parents=True, exist_ok=True) #create folder if does no exist
             plt.imsave(save_folder_path + "/file_%s.png"%(text),final_mask)
         if type_fidu == "fixed":
             x = xc
             y = yc
             final_mask=copy.deepcopy(im_gray)
             final_mask = cv2.circle(final_mask,(int(round(x)),int(round(y))),1,255,-1)
             save_folder_path=corner_folder + '/' + corner + "/fixedCopie/"
             Path(save_folder_path).mkdir(parents=True, exist_ok=True) #create folder if does no exist
             plt.imsave(save_folder_path + "/file_%s.png"%(text),final_mask)

         return x+maxLoc[0],y+maxLoc[1], maxVal

def FindCircles(corner_image,DP=0.05, MinDist=20, MinRadius=170, MaxRadius=250, parameter2=100):
    """
    OpenCV HoughCircles is used when template matching isn't working. It only works if the fiducial is a circle...

    :param corner_image_path:
    :param DP:This parameter is the inverse ratio of the accumulator resolution to the image resolution
    (see Yuen et al. for more details). Essentially, the larger the dp gets, the smaller the accumulator array gets.
    :param MinDist: Minimum distance between the center (x, y) coordinates of detected circles. If the minDist is too
    small, multiple circles in the same neighborhood as the original may be (falsely) detected. If the minDist is too
    large, then some circles may not be detected at all.
    :param MinRadius: Minimum size of the radius (in pixels).
    :param MaxRadius: Maximum size of the radius (in pixels).
    :param parameter2: Accumulator threshold value for the cv2.HOUGH_GRADIENT method. The smaller the threshold is,
    the more circles will be detected (including false circles). The larger the threshold is less circles will
    potentially be returned.
    :return:
    """

    # corner_image = cv2.imread(corner_image_path, cv2.CV_8UC1)
    corner_imageBlr = cv2.GaussianBlur(corner_image, (11, 11), cv2.BORDER_DEFAULT)

    im = corner_imageBlr

    detected_circles = None
    while detected_circles is None:  # or len(detected_circles[0])<2: # will decrease the parameter2 until it founds a circle
        detected_circles = cv2.HoughCircles(im,
                                            cv2.HOUGH_GRADIENT,dp=DP, minDist=MinDist, param1=50,
                                            param2=parameter2, minRadius=MinRadius, maxRadius=MaxRadius)
        if DebugMode is True:
            print('   ' + os.path.basename(corner_image_path) + '> ' + str(MinDist)+ ' ' + str(parameter2)) #for debugging

        parameter2 = parameter2 - 2

        if parameter2 < 14:
            break
    if DebugMode is True:
        fig, axs = plt.subplots(1, 2, figsize=(6, 6))
        fig.suptitle(os.path.basename(corner_image_path[:-4]), fontweight="bold")
        axs[0].imshow(corner_image, cmap=plt.cm.gray)
        axs[0].set_title('corner')
        axs[1].imshow(im)
        axs[1].set_title('thresholded')
        if detected_circles is not None:
            for i in range(len(detected_circles[0])):
                circle1 = plt.Circle((detected_circles[0][i][0], detected_circles[0][i][1]), (detected_circles[0][i][2]), fill=False, color='r')
                axs[1].add_patch(circle1)
                axs[1].plot(detected_circles[0][i][0], detected_circles[0][i][1], 'r',marker=".", markersize=10)

    return detected_circles

def systeme(a1,b1,c1,a2,b2,c2): 
    """ 
    find the coordinate of the intersection point of 2 lines
    inputs:  parameters of equation
        a1*x + b1*y =c1
        a2*x + b2*y =c2'
    
    :param a1: parameter of the equation (line 1)
    :type a1: float
    :param b1: parameter of the equation (line 1)
    :type b1: float
    :param c1: result of the equation (line 1)
    :type c1: float
    :param a2: parameter of the equation (line 2)
    :type a2: float
    :param b2: parameter of the equation (line 2)
    :type b2: float
    :param c2: result of the equation (line 2)
    :type c2: float
    
    :results: result approximation
    :rtype: float
    
     """
    x=float()
    y=float()
    
    if a1*b2-a2*b1==0:
       print('Pas de solution')
    else:    
       y=(c2*a1-c1*a2)/(a1*b2-a2*b1)
       x=(c1-b1*y)/a1
       print('x =',round(x,0),"",'y =',round(y,0))
    return x, y 

def select_fiducial_corners(img,S,p,Fidu_type, black_stripe_location):
    """ 
    Crop image to select area where are the fiducials

    :param img: aerial photo
    :type img: cv2 img
    :param S: max size of the black border of the picture
    :type S: int
    :param p: percentage of bandwidth width compare to the half size of the photo
    :type p: float
    :param Fidu_type: fiducial type (ex target)
    :type Fidu_type: str
    :param black_stripe_location: (top, left, right, bot)
    :type black_stripe_location: [str]
        
    :returns:
        - F :if Fidu-type == target or cross: atrributes top_left, top_right, bot_left, bot_right
                    if Fidu-type == rectangle : atrributes top, bot, right, left
            ex : 
                F['top']=  [img, coord_u0, coord_v0 int  ]
    :rtype: dic                           
    """
    F={}
    U=img.shape[1] #hori
    V=img.shape[0] #verti

    if Fidu_type == "target" or Fidu_type == "cross":
        # by default corner size
        u_left = 0
        u_right = U - S
        v_top = 0
        v_bot = V - S

        # Update for black strip:
        if 'top' in black_stripe_location:
            v_top = v_top + int(p*V)
        if 'bottom' in black_stripe_location:
            v_bot = v_bot - int(p*V)
        if 'left' in black_stripe_location:
            u_left = u_left + int(p * U)
        if 'right' in black_stripe_location:
            u_right = u_right - int(p*U)

        F['top_left'] = [img[v_top:v_top+S,u_left:u_left+S],v_top,u_left]
        F['top_right'] = [img[v_top:v_top+S,u_right:u_right+S],v_top,u_right]
        F['bot_right'] = [img[v_bot:v_bot+S,u_right:u_right+S],v_bot,u_right]
        F['bot_left'] = [img[v_bot:v_bot+S,u_left:u_left+S],v_bot,u_left]
    else :
        print("type of fiducial not defined: please complete the code")
    return F


def FiducialFig(F,fidu_coordinates, corner_folder):
    """
    Create a figure with the 4 corners per image, with a red rectangle showing the outline of the template position
    and a point at the fiducial coordinates

    :param F:
    :param fidu_coordinates:
    :return:
    """

    fidu_coordinates2=fidu_coordinates.set_index('corner')

    # Create a figure
    fig, axs = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle(fidu_coordinates['image'][0] +"\n", fontweight="bold")
    x = 0
    y = 0
    for corner in fidu_coordinates['corner']:
        axs[y, x].imshow(F[corner][0], cmap=plt.cm.gray)
        axs[y, x].set_title(corner)

        # Add a rectangle with location of template
        template_rectangle = patches.Rectangle(
            (fidu_coordinates2.loc[corner]['u1'] - int(F[corner][2]+ fidu_coordinates2.loc[corner]['xc'] ), fidu_coordinates2.loc[corner]['v1'] - int(F[corner][1]) - fidu_coordinates2.loc[corner]['yc']),
            fidu_coordinates2.loc[corner]['xc']*2, fidu_coordinates2.loc[corner]['yc']*2,
            linewidth=2, edgecolor='r', facecolor='none')
        axs[y, x].add_patch(template_rectangle) # Add the patch to the Axes

        # Add a circle at the found fiducial coordinates
        axs[y, x].plot(
            fidu_coordinates2.loc[corner]['u1'] - int(F[corner][2]), fidu_coordinates2.loc[corner]['v1'] - int(F[corner][1]),
            5, color='r', marker=".", markersize=2)



        x = x + 1
        if x == 2:
            x = 0;
            y = 1

    fig.tight_layout()
    # save figure
    save_folder_path = corner_folder + '/_all_fiducials'
    Path(save_folder_path).mkdir(parents=True,
                                 exist_ok=True)  # create folder if does no exist
    plt.savefig(save_folder_path + '/_FiducialsDetection_' + fidu_coordinates['image'][0] + '_' + corner + '.png',
                dpi=DPI)



def Main(image_folder, image_name, S, p, Fiducial_type, black_stripe_location,type_fidu,dataset, fiducial_template_folder, corner_folder, Out_fiducialmarks_CSV,center_fidu_tempate_CSV):

    if Fiducial_type!='rectangle' and Fiducial_type!='target' and Fiducial_type!='cross' : 
        print('Code not yet built for this fiducial type' )
        sys.exit()

    # -------------------------------------------------------------------------------------
    # 1.0. #select the area of the image where the fiducials are located (i.e., the corners)
    # -------------------------------------------------------------------------------------

    image_path = image_folder + '/' + image_name
    img=cv2.imread(image_path)
    F=select_fiducial_corners(img, S, p, Fiducial_type, black_stripe_location) # cropping image corner
    F_area=F.keys() 
    Coord={}
    ToBeChecked = pd.DataFrame(columns=['image', 'corner', 'x', 'y', 'maxVal'])

    fidu_coordinates = pd.DataFrame(columns=['image','corner', 'template', 'xc', 'yc', 'u1', 'v1', 'maxVal'])
    for corner in F_area:
        #-------------------------------------------------------------------------------------
        # 1.1 Load fiducial template
        #-------------------------------------------------------------------------------------

        # create dic with fiducial template that match
        template_list_all=[template for template in os.listdir(fiducial_template_folder) if template[-4:] in ['.tif'] ]
        # template_list=[template for template in template_list if template[:len('Template_%s_%s' % (dataset, corner))] in 'Template_%s_%s' % (dataset, corner) ]
        template_list=[template for template in template_list_all if corner in template ]

        if len(template_list) == 0:
            print("Can't find any corresponding fiducial template")
            # sys.exit()
        else:
            template_dic={}
            for template_name in template_list:
                template_img = cv2.imread(fiducial_template_folder + '/'+ template_name)
                template_dic[template_name] = template_img

        #-------------------------------------------------------------------------------------
        # 1.2. select a smaller area where the fiducial should be and match it with the found fiducial templates
        #-------------------------------------------------------------------------------------
        center_fidu_tempate = open(center_fidu_tempate_CSV)
        Lcenter= center_fidu_tempate.readlines()
        best_template = pd.DataFrame(columns=['template', 'u1', 'v1', 'maxVal'])

        if OneTemplateMax is True: # will only use the first matching template
            template_list=[template_list[0]]

        xc,yc=0,0
        for template_name in template_list:
            for line in Lcenter:
                 line=line.split(' ')
                 if template_name.split('.')[0] == line[0]:
                     xc, yc= (int(line[1]),int(line[2])) # coordinates of the center of the fiducial template (pointed by hand)
                     # print(str(xc) + ' '+ str(yc))
                     break


            if xc !=0 and yc != 0: # i.e., it found a template
                try :
                    if Fiducial_type=='target' :
                        orient='False'
                        u,v, maxVal = CenterFiducial_LUCASKANADE(F[corner][0],Fiducial_type,orient,template_dic[template_name],xc,yc,image_name,corner,type_fidu, corner_folder)

                        u1=int(F[corner][2]+u)#colon
                        v1=int(F[corner][1]+v)#line
                        # Coord[corner]=[u1,v1] #line,colon

                        best_template = pd.concat([best_template, pd.DataFrame(
                            [{'template': template_name, 'u1': u1, 'v1': v1, 'maxVal': maxVal}])], ignore_index=True)

                        if template_name == template_list[-1]:
                            best=best_template.iloc[best_template['maxVal'].idxmax()]


                            if best['maxVal'] >= 0.85:
                                Coord[corner] = [best['u1'], best['v1']]  # line,colon
                                fidu_coordinates = pd.concat([fidu_coordinates, pd.DataFrame(
                                    [{'image': image_name, 'corner': corner, 'template': template_name, 'xc': xc,
                                      'yc': yc, 'u1': best['u1'], 'v1': best['v1'], 'maxVal': best['maxVal']}]
                                )], ignore_index=True)


                            elif best['maxVal'] < MatchingValueThreshold: # Value could be increased to be more constraining on the quality of the match
                                # Another try with larger corner area?
                                S2=S+400
                                if p-0.02>=0:
                                    p2=p-0.02
                                else:
                                    p2=0
                                F2 = select_fiducial_corners(img, S2, p2, Fiducial_type,
                                                    black_stripe_location)  # cropping image corner
                                u, v, maxVal = CenterFiducial_LUCASKANADE(F2[corner][0], Fiducial_type, orient,
                                                                          template_dic[template_name], xc, yc,
                                                                          image_name, corner, type_fidu, corner_folder)

                                u1 = int(F[corner][2] + u)  # colon
                                v1 = int(F[corner][1] + v)  # line
                                best_template = pd.concat([best_template, pd.DataFrame(
                                    [{'template': template_name, 'u1': u1, 'v1': v1, 'maxVal': maxVal}]
                                )], ignore_index=True)
                                best = best_template.iloc[best_template['maxVal'].idxmax()]


                                if best['maxVal'] >= MatchingValueThreshold:  # Value could be increased to be more constraining on the quality of the match
                                    Coord[corner] = [best['u1'], best['v1']]
                                    fidu_coordinates = pd.concat([fidu_coordinates, pd.DataFrame(
                                        [{'image': image_name, 'corner': corner, 'template': template_name, 'xc': xc,
                                          'yc': yc, 'u1': best['u1'], 'v1': best['v1'], 'maxVal': best['maxVal']}]
                                    )], ignore_index=True)

                                else:
                                    ToBeChecked = pd.concat([ToBeChecked, pd.DataFrame(
                                        {'image': [image_name], 'corner': [corner], 'x': [best['u1']],
                                         'y': [best['v1']], 'maxVal': [best['maxVal']]}
                                    )], ignore_index=True)

                                    # Try with circle
                                    corner_monoband=[item[0] for item in F[corner][0][0]]
                                    detected_fiducial_circles = FindCircles(np.asarray(corner_monoband), DP=1, MinDist=500,
                                                                            MinRadius=xc - 50,
                                                                            MaxRadius=xc + 50,
                                                                            parameter2=120)

                                    # Create a fancy figure for the corner with problem
                                    fig, axs = plt.subplots(1, 2, figsize=(6, 4))
                                    fig.suptitle('to check: ' + image_name +'_'+corner, fontweight="bold")
                                    axs[0].imshow(F[corner][0], cmap=plt.cm.gray)
                                    axs[0].set_title('corner image')
                                    # Add a rectangle with location of template
                                    rect = patches.Rectangle((best['u1']-int(F[corner][2]-xc), best['v1']-int(F[corner][1])-yc), template_dic[template_name].shape[0], template_dic[template_name].shape[1],
                                                             linewidth=2, edgecolor='r', facecolor='none')
                                    # Add the patch to the Axes
                                    axs[0].add_patch(rect)
                                    axs[1].imshow(template_dic[template_name], cmap=plt.cm.gray)
                                    axs[1].set_title('template')

                                    if detected_fiducial_circles is not None:
                                        Coord[corner] = [detected_fiducial_circles[0][0][0],detected_fiducial_circles[0][0][1]]
                                        fidu_coordinates = pd.concat([fidu_coordinates, pd.DataFrame(
                                            [{'image': image_name, 'corner': corner, 'template': template_name,
                                              'xc': xc,
                                              'yc': yc, 'u1': detected_fiducial_circles[0][0][0],
                                              'v1': detected_fiducial_circles[0][0][1],
                                              'maxVal': 0}]
                                        )], ignore_index=True)
                                        # add circle
                                        circle = plt.Circle((detected_fiducial_circles[0][0][0], detected_circles[0][0][1]),
                                                             (detected_circles[0][0][2]), fill=False, color='r')
                                        axs[0].add_patch(circle)
                                        axs[0].plot(detected_circles[0][0][0], detected_circles[0][0][1], 'r', marker=".",
                                                    markersize=10)
                                        axs[0].add_patch(circle)

                                    else:
                                        Coord[corner] = [best['u1'], best['v1']]
                                        fidu_coordinates = pd.concat([fidu_coordinates, pd.DataFrame(
                                            [{'image': image_name, 'corner': corner, 'template': template_name, 'xc': xc,
                                             'yc': yc, 'u1': best['u1'], 'v1': best['v1'],
                                             'maxVal': best['maxVal']}]
                                        )], ignore_index=True)



                                    # save figure
                                    save_folder_path = corner_folder + '/_To_Be_Checked'
                                    Path(save_folder_path).mkdir(parents=True, exist_ok=True)  # create folder if does no exist
                                    plt.savefig(save_folder_path + '/_ToCheck_' + image_name +'_'+corner + '.png', dpi=DPI)

                        if len(Coord) == 4 and template_name==template_list[-1] and corner == list(F.keys())[-1]:
                            print("  >> " + image_name + ' > found for fiducial coordinates: ' + str(Coord) )
                            addLine(image_name, Coord, Out_fiducialmarks_CSV) # Add to CSV file

                            FiducialFig(F, fidu_coordinates, corner_folder) # save a figure

                except (ValueError,IndexError) as e:
                    print(e)
                    print ('cannot find fidu ' , image_name,'   ',corner)


            else:
                print("! Could not find center coordinates for template | << check 'Center_Fiducial.csv' file >>")
                print('Template_%s_%s_%s'%(Fiducial_type,dataset,temp) + " != " + line[0])

                ToBeChecked = pd.concat([ToBeChecked, pd.DataFrame(
                    [{'image': image_name, 'corner': corner, 'x': 0, 'y': 0, 'maxVal': 0}]
                )], ignore_index=True)

                fidu_coordinates = pd.concat([fidu_coordinates, pd.DataFrame(
                    [{'template': template_name, 'xc': 0, 'yc': 0, 'u': 0, 'v': 0}]
                )], ignore_index=True)
                sys.exit(0)


    if not ToBeChecked.empty:
        # write to file
        if not os.path.isfile(Out_fiducialmarks_CSV[:-4] + '_TobeChecked.csv'):
            ToBeChecked.to_csv(Out_fiducialmarks_CSV[:-4] + '_TobeChecked.csv', mode='w', header=['image', 'corner', 'x', 'y', 'maxVal']) # append to file
        else:  # else it exists so append without writing the header
            ToBeChecked.to_csv(Out_fiducialmarks_CSV[:-4] + '_TobeChecked.csv', mode='a', header=False) # append to file

def parameters_02(input_image_folder, fiducial_template_folder, dataset): #defaulting parameters for running in tkinter

    center_fidu_tempate_CSV = fiducial_template_folder + "/Center_Fiducials.txt"  # text file where the centre of the template is indicated
    corner_folder = os.path.dirname(input_image_folder) + '/' + '_temp_fiducials'  # folder where temporary fiducials of the images will be saved
    type_fidu = "barycentre"  # parameter for ShiTomasi corner detection. 'fixed' or 'barycentre'
    Out_fiducialmarks_CSV = input_image_folder + '/' + '_fiducial_marks_coordinates_' + dataset + '.csv'

    RunParallel = False  # to run using parallel processing (otherwise will process one image after the other
    DebugMode = False  # will provide more info about subprocess to the console for checking
    OneTemplateMax = True  # if True it will only use the first matching template. If False it will take more time...
    S = 2500  # size of the sub-image around the fiducial for template matching (square of S pixels in size)
    MatchingValueThreshold = 0.85  # value to define a good match. See OpenCV cv2.matchTemplate. Should probably be included between 0.75 and 0.90
    DPI = 200  # resolution of figures for visual check
    Fiducial_type = 'target'  # type : target or rectangle or cross. Should be target for now ;)

    #### PARALLEL PROCESSING #####
    # (Choose the number of CPU cores you want to use)
    # (minimum = 1; suggested value = (number of cores) - 1)
    # (if you don't know how many cores you have, write: 'multiprocessing.cpu_count()')
    num_cores = multiprocessing.cpu_count() - 1

    return center_fidu_tempate_CSV, corner_folder, type_fidu, Out_fiducialmarks_CSV, RunParallel, DebugMode, OneTemplateMax, S, \
           MatchingValueThreshold, DPI, Fiducial_type, num_cores

def main_script_02(image_folder, fiducial_template_folder, dataset, p, black_stripe_location):

    print(' ')
    print('=====================================================================')
    print('=         PYTHON SCRIPT FOR AUTOMATIC FIDUCIAL DETECTION            =')
    print('=  Version 2.0.1 (December 2021)  |  B. Smets/A. Dille (RMCA/VUB)   =')
    print('=====================================================================')
    print(' ')


    if __name__ != "__main__": # defaulting parameters if running in tkinter
        center_fidu_tempate_CSV, corner_folder, type_fidu, Out_fiducialmarks_CSV, RunParallel, DebugMode, OneTemplateMax, S, \
        MatchingValueThreshold, DPI, Fiducial_type, num_cores\
            = parameters_02(image_folder, fiducial_template_folder, dataset)

        print("\n"
              "corner folder: " + corner_folder +
              "\nOut_fiducialmarks_CSV: "+ Out_fiducialmarks_CSV +
              "\ncenter_fidu_tempate_CSV: " + center_fidu_tempate_CSV  )

    ##### PARALLEL PROCESSING #####

    lines =[["name;X1;Y1;X2;Y2;X3;Y3;X4;Y4"]]
    f = open(Out_fiducialmarks_CSV, "w",newline='')
    w = csv.writer(f,delimiter=",")
    w.writerows(lines)
    f.close()

    # List image files
    allfiles=os.listdir(image_folder)
    imlist=[filename for filename in allfiles if filename[-4:] in [".tif",".TIF",".jpg",".JPG"]]
    imlist = imlist + [filename for filename in allfiles if filename[-5:] in [".tiff",".TIFF"]]

    print('\n-------------------------------'
          '\n-------------------------------\n'
          ' > found ' + str(len(imlist)) + ' images to process'
          '\n-------------------------------'
          '\n-------------------------------\n')

    # Main
    if RunParallel is True:
        Parallel(n_jobs=num_cores, verbose=30)(delayed(Main)(image_folder, image,S,p,Fiducial_type,black_stripe_location,
                                                             type_fidu,dataset,fiducial_template_folder, corner_folder,
                                                             Out_fiducialmarks_CSV, center_fidu_tempate_CSV) for image in imlist)
        sleep(3)

    else:
        count=1
        for image in imlist:
            print('\n >>> Image [' + str(count) + '/' + str(len(imlist)) + ']: ' + image)
            Main(image_folder, image,S,p,Fiducial_type,black_stripe_location,type_fidu,dataset,fiducial_template_folder,
                 corner_folder,Out_fiducialmarks_CSV, center_fidu_tempate_CSV)
            count=count +1



    # print list of image corners to check (uncertainties in the template matching)
    if os.path.isfile(Out_fiducialmarks_CSV[:-4] + '_TobeChecked.csv'):
        ToBeChecked_O2=pd.read_csv(Out_fiducialmarks_CSV[:-4] + '_TobeChecked.csv') # append
        print("\n-------------------------------------------------------------------------\n "
              "image corners to to check")
        print(ToBeChecked_O2)

    print("\n-------------------------------------------------------------------------\n"
          '>>>>> fiducial coordinates saved to: ' + Out_fiducialmarks_CSV )
    print("\nYou can have a visual look at the detected fiducials in the folder: " + corner_folder + '/_all_fiducials')



if __name__ == "__main__":
    main_script_02(image_folder, fiducial_template_folder, dataset, p, black_stripe_location)

##### END PROCESSING #####
