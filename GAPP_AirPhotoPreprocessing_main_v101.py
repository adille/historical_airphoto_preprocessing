#!C:\\Users\\adille\\anaconda3\\envs\\GEO-Env\\python

"""
------------------------------------------------------------------------------
GeoRiskA Aerial Photo Preprocessing Chain
PYTHON INTERFACE FOR THE STANDARDIZING OF AERIAL PHOTO ARCHIVE
------------------------------------------------------------------------------

Version: 1.0.1
Author: Antoine Dille
        (Royal Museum for Central Africa  )

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
        > Glob
        > Joblib
        > OpenCV
        > Pillow

    - To use this script, simply adapt the directory paths and required values
      in the setup section of the script.


"""
from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import *
from tkinter import filedialog
import os, sys
from functools import partial


sys.path.insert(0, '') # Local imports

from GAPP_Script_01_AirPhoto_CanvasSizing_v201 import main_script_01
from GAPP_Script_02_AutomaticFiducialDetection_v201 import main_script_02
from GAPP_Script_03_AirPhoto_Reprojection_v201 import main_script_03
from GAPP_Script_04_AirPhotos_Resize_v201 import main_script_04

# from Script_3_AirPhoto_CreateSingleMask_v101 import script3

if __name__ == "__main__":
    """
    print(' ')
    print('=====================================================================')
    print('=               GeoRiskA Aerial Photos Preprocessing Chain           =')
    print('=         Version 1.0.1 (December 2021) |  Antoine Dille (RMCA)     =')
    print('=====================================================================')
    print(' ')
    """

    #Initialize Main Window
    root = Tk()

    #
    # Set the Interface Icon and Name
    #
    # root.iconphoto(True, tk.PhotoImage(file='logo.png'))
    root.title('GeoRiskA Aerial Photos Preprocessing Chain')

    # Set appearence theme
    root.tk.call("source", "ttk_Theme/sun-valley.tcl")  # https://github.com/rdbende/Sun-Valley-ttk-theme
    root.tk.call("set_theme", "light")  # light or dark theme
    root.option_add('*Font', 'TkMenuFont')  # define font

    # add epmty label for better spacing
    # emptylabel = tk.Label(root, text="  ").grid(row=0, column=0, sticky="nsew")
    emptylabel = tk.Label(root, text="  ").grid(row=12, column=0,columnspan=9, sticky="nsew")
    # emptylabel = tk.Label(root, text="       ").grid(row=0, column=1, sticky="nsew")
    emptylabel = tk.Label(root, text="       ").grid(row=3, column=7, sticky="nsew")
    emptylabel = tk.Label(root, text="       ").grid(row=6, column=7, sticky="nsew")
    emptylabel = tk.Label(root, text="       ").grid(row=11, column=1, sticky="nsew")
    emptylabel = tk.Label(root, text="  ").grid(row=24, column=0, sticky="nsew")
    emptylabel = tk.Label(root, text="              ").grid(row=25, column=1, columnspan=9,sticky="nsew")
    emptylabel = tk.Label(root, text="       ").grid(row=20, column=1,columnspan=4, sticky="nsew")
    emptylabel = tk.Label(root, text="       ").grid(row=29, column=1,columnspan=4, sticky="nsew")
    emptylabel = tk.Label(root, text="       ").grid(row=33, column=1,columnspan=4, sticky="nsew")


    label1 = tk.Label(root,text="\n   Folders", font=('calibre',11, 'bold'))
    label_input_folder = Label(root,text='   Aerial images folder:')
    label_output_folder = Label(root,text='   Output folder:')
    label_template_folder = Label(root,text='   Fiducial template folder:')
    label_template_folder_info = Label(root,text='   templates images for 4 typical fiducial marks + associated .txt file. See Script_00_Tool_FiducialTemplateCreator', font=('calibre',7, 'italic'))

    label5 = tk.Label(root,text="   Input parameters", font=('calibre',11, 'bold'))
    label6 = tk.Label(root,text="\n   Steps to launch", font=('calibre',11, 'bold'))


    label1.grid(row=1,columnspan=4, sticky="w")
    label_input_folder.grid(row=2,columnspan=4, sticky="w")
    label_output_folder.grid(row=5,columnspan=4, sticky="w")
    label_template_folder.grid(row=8,columnspan=4, sticky="w")
    label_template_folder_info.grid(row=9,columnspan=6, sticky="w")

    label5.grid(row=12,columnspan=3, sticky="w")
    label6.grid(row=30,columnspan=3, sticky="w")

    global path
    path = "./"

    #size
    n = 60
    #Initialize Entries
    # folders
    entry_input_images = tk.Entry(root, width=80)
    entry_input_images.grid(row=3, column=1, columnspan=4, sticky="nsew")
    entry_output_images = tk.Entry(root, width=80)
    entry_output_images.grid(row=6,column=1,columnspan=4, sticky="nsew")

    # fiducial template folder
    entry_fidu = tk.Entry(root, width=80)
    entry_fidu.grid(row=10,column=1,columnspan=4, sticky="nsew")

    # Dataset
    label_dataset = tk.Label(root, text="   Dataset name:").grid(row=13, columnspan=2, sticky="w")
    dataset = tk.StringVar(root, value='Luluaburg_1959')
    entry_dataset = tk.Entry(root, textvariable=dataset)
    entry_dataset.grid(row=14, column=1,columnspan=2, sticky="nsew")

    # P value
    p_value_list = [0.0,0.01,0.02,0.04,0.06,0.08,0.1,0.15,0.20]
    labelp = tk.Label(root, text=" p-value:").grid(row=15, column=1, sticky="w")
    label_p_info = Label(root,text='   % of image width that is a black/white strip. See Script_02_AutomaticFiducialDetection', font=('calibre',7, 'italic'))
    label_p_info.grid(row=16,columnspan=6, sticky="w")
    chosen_p = tk.StringVar(root)
    chosen_p.set(p_value_list[3]) # by default
    entry_p = tk.OptionMenu(root, chosen_p, *p_value_list)
    entry_p.grid(row=15, column=2, sticky="nsew")

    # blackStripe location
    label_stripes = tk.Label(root, text="    Stripes location:").grid(row=17, columnspan=2, sticky="w")
    stripes = tk.StringVar(root, value='right, bottom')
    entry_stripes = tk.Entry(root, textvariable=stripes) #
    entry_stripes.grid(row=19, column=1,columnspan=2, sticky="nsew")

    # camera
    camera_value_list = ["Wild RC5a"] # other camera could be added here. Values should then be adapted in Script_03_AirPhoto_Reprojection_v102_GAPP.py
    labelcamera = tk.Label(root, text=" Camera system:").grid(row=21, column=1, sticky="w")
    chosen_camera= tk.StringVar(root)
    chosen_camera.set(camera_value_list[0]) # by default
    entry_camera = tk.OptionMenu(root, chosen_camera, *camera_value_list)
    entry_camera.grid(row=22, column=1, sticky="nsew")

    # resolution
    resolution_value_list = ["300","400","600","800","900","1200","1500","1600","1800"]
    label_input_res = tk.Label(root, text=" Input scan resolution:").grid(row=23, column=1, sticky="w")
    chosen_input_res= tk.StringVar(root)
    chosen_input_res.set(resolution_value_list[7]) # by default
    entry_input_res = tk.OptionMenu(root, chosen_input_res, *resolution_value_list)
    entry_input_res.grid(row=24, column=1, sticky="nsew")

    label_output_res = tk.Label(root, text=" Output scan resolution:").grid(row=23, column=2, sticky="w")
    chosen_output_res = tk.StringVar(root)
    chosen_output_res.set(resolution_value_list[4])  # by default
    entry_ouput_res = tk.OptionMenu(root, chosen_output_res, *resolution_value_list)
    entry_ouput_res.grid(row=24, column=2, sticky="nsew")

    # Histogram calibration
    HistoCal_value_list = ['True', 'False']
    label_HistoCal = tk.Label(root, text=" CLAHE Histogram calibration:").grid(row=25, column=1, sticky="w")
    chosen_HistoCal = tk.StringVar(root)
    chosen_HistoCal.set(HistoCal_value_list[0])  # by default
    entry_HistoCal = tk.OptionMenu(root, chosen_HistoCal, *HistoCal_value_list)
    entry_HistoCal.grid(row=26, column=1, sticky="nsew")

    # Sharpening Intensity
    SharpIntensity_value_list =  [0,1,2]
    label_SharpIntensity = tk.Label(root, text=" Sharpening intensity:").grid(row=25, column=2, sticky="w")
    chosen_SharpIntensity = tk.StringVar(root)
    chosen_SharpIntensity.set(SharpIntensity_value_list[2])  # by default
    entry_SharpIntensity = tk.OptionMenu(root, chosen_SharpIntensity, *SharpIntensity_value_list)
    entry_SharpIntensity.grid(row=26, column=2, sticky="nsew")


    def find_input_folder(e, text):
        global path
        root.filename = filedialog.askdirectory(initialdir=path, title=text)
        path = root.filename
        e.insert(0, root.filename)
        input_folder.append(path)

    def find_output_folder(e, text):
        global path
        root.filename = filedialog.askdirectory(initialdir=path, title=text)
        path = root.filename
        e.insert(0, root.filename)
        output_folder.append(path)

    def find_template_folder(e, text):
        global path
        root.filename = filedialog.askdirectory(initialdir=path, title=text)
        path = root.filename
        e.insert(0, root.filename)
        template_folder.append(path)


    def main_script(input_folder,output_folder, template_folder, dataset, chosen_p, stripes, chosen_camera,chosen_input_res,chosen_output_res,chosen_HistoCal, chosen_SharpIntensity, Steps ):
        input_0=input_folder[0]
        output_canvas_sized=output_folder[0] + '/' + '01_CanvasSized'
        output_reprojected=output_folder[0] + '/' + '02_Reprojected'
        output_resized=output_folder[0] + '/' + '03_Resized'

        template_0= template_folder[0]
        dataset_0=dataset.get()
        chosen_p_0=float(chosen_p.get())
        stripes_0=stripes.get()
        camera=str(chosen_camera.get())
        fiducialmarks_file= output_canvas_sized + '/' + '_fiducial_marks_coordinates_' + dataset_0 + '.csv'

        scale_percent_0= 100 / float(chosen_input_res.get()) * float(chosen_output_res.get())
        chosen_HistoCal_0=str(chosen_HistoCal.get())
        chosen_SharpIntensity_0=float(chosen_SharpIntensity.get())

        Steps={'Script_01': check_01.get(), 'Script_02': check_02.get(), 'Script_03': check_03.get(),
               'Script_04': check_04.get()}
        print('-> will run the following steps:')
        print(Steps)


        # scripts
        # 01_CanvasSizing
        if Steps['Script_01'] == 1:
            main_script_01(input_0,output_canvas_sized)
        # 02_AutomaticFiducialDetection
        if Steps['Script_02'] == 1:
            main_script_02(output_canvas_sized, template_0, dataset_0, chosen_p_0, stripes_0)
        # 03_Reprojection
        if Steps['Script_03'] == 1:
            main_script_03(output_canvas_sized, output_reprojected, fiducialmarks_file, camera)
        # 04_Resize
        if Steps['Script_04'] == 1:
            main_script_04(output_reprojected, output_resized, scale_percent_0, chosen_HistoCal_0, chosen_SharpIntensity_0)


    #Initialize Buttons:
    input_folder = []
    output_folder = []
    template_folder = []
    check_01 = tk.IntVar()
    check_02 = tk.IntVar()
    check_03 = tk.IntVar()
    check_04 = tk.IntVar()
    Steps = {'Script_01': 0, 'Script_02': 0, 'Script_03': 0,
             'Script_04': 0} # by defaulft nothing is runned



    entry_input_folder = Button(root,text="Select folder",command=lambda: find_input_folder(entry_input_images,"Select aerial image folder")).grid(row=3,column=9, sticky="w")
    entry_output_folder = Button(root,text="Select folder",command=lambda: find_output_folder(entry_output_images,"Select output directory")).grid(row=6,column=9, sticky="w")
    entry_template_folder = Button(root,text="Select folder",command=lambda: find_template_folder(entry_fidu,"Select template directory")).grid(row=10,column=9, sticky="w")


    # Partial library is used to preset partial functions with the chosen parameters before run it
    main_script = partial(main_script,input_folder,output_folder, template_folder, dataset, chosen_p, stripes, chosen_camera,chosen_input_res,chosen_output_res,chosen_HistoCal, chosen_SharpIntensity, Steps)
    buttonRun = ttk.Button(root, text="Run", style='Accent.TButton', command=main_script).grid(row=34,column=7,columnspan = 6, sticky="nsew")

    c = ttk.Checkbutton(root, text="Script_01: Canvas Sizing", variable=check_01).grid(row=31,column=1, sticky="w")
    c = ttk.Checkbutton(root, text="Script_02: Fiducial Detection", variable=check_02).grid(row=31,column=2, sticky="w")
    c = ttk.Checkbutton(root, text="Script_03: Reproject", variable=check_03).grid(row=32,column=1, sticky="w")
    c = ttk.Checkbutton(root, text="Script_04: Downsampling", variable=check_04).grid(row=32,column=2, sticky="w")

    # buttonUpdate = ttk.Button(root, text=" update ", style='Accent.TButton', command=click_me).grid(row=31,column=3,columnspan = 2, sticky="w")

    # b = Button(root, text=" update ", command=click_me).grid(row=31,column=3,columnspan = 2, sticky="w")



    root.rowconfigure(9, {'minsize': 30})
    root.columnconfigure(9, {'minsize': 30})
    root.geometry(str(700) + "x" + str(800))  # defined a window size to be sure it doesn't change over time
    root.resizable(width=TRUE, height=TRUE)

    # End of interface

    #Mainloop
    root.mainloop()



