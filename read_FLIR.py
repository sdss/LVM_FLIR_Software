'''
    Python script to read the FLIR camera and display the image and histogram.

    Adapted from:  https://kushalvyas.github.io/gige_ubuntu.html

    Things to worry about:

    Boolean     : 'IspEnable' = true  (Enables Image Signal Processing engine (for binning) see:
        http://softwareservices.flir.com/BFS-U3-89S6/latest/Model/public/ImageFormatControl.html)

    'AutoExposureTargetGreyValueAuto' = 'Continuous'  (Probably Ok, since we have disabled AutoExposure. See:
        http://softwareservices.flir.com/Spinnaker/latest/class_spinnaker_1_1_camera.html#ae82d7288e3e4d536eab2262031f4b92e)

    Boolean     : 'DefectCorrectStaticEnable' = true (This should be FALSE! (done) since it replaces a table
        of bad get_pixel_format_as_string measured at the factory, by the average of neighbours. See here:
        http://softwareservices.flir.com/BFS-U3-123S6/latest/Model/public/DefectivePixelCorrection.html)

    Enumeration : 'UserSetFeatureSelector' = 'AasRoiEnableAe' (refers to storing settings in non-volatile memory.
        Potentially useful when we deploy. See here: http://softwareservices.flir.com/BFS-U3-32S4/latest/Model/public/UserSetControl.html)

'''

import sys
import gi 
import ctypes
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits       # To read and write FITS files (for diagnostics)

import FLIR_Utils as FU           # All the camera interface stuff

#--------------------------------------------------------------------------------------------

###--- MAIN ROUTINE STARTS HERE ---###

fakeCam = False   # Whether to use the Aravis "fake" camera (software) instead of the FLIR
verbose = True    # How wordy to be
showImg = True    # Whether to show the resulting image with matplotlib
writeFITS = True  # Whether to write a "temp.fits" file of the result

print ("-----")

gi.require_version('Aravis', '0.8')
from gi.repository import Aravis

###--- Set up camera 

cam,dev = FU.Setup_Camera(verbose,False)    # Instantiate camera and dev
FU.Standard_Settings(cam,dev,verbose)       # Standard settings (full frame, etc.)
FU.FLIR_Status(cam,dev)                     # Print out camera info

# Aravis.update_device_list()

# if fakeCam:
#     Aravis.enable_interface("Fake")    # using arv-fake-gv-camera-0.8
#     cam = Aravis.Camera.new(None)      # Instantiate cam
#     print ("Instantiated cam with arv-fake-gv-camera-0.8")

# else:             # Note: We expect only one "real"camera

#     try:
#       cam = Aravis.Camera.new(Aravis.get_device_id(0))      # Instantiate cam
#       print ("Instantiated cam with FLIR")
#     except:
#       print("No camera found")
#       exit()

###--- Set Camera Parameters
'''
    I tested the maximum exposure time as a function of gain and gain mode:

    ILLUMINATED CASE (mean-variance test)

    Gain    HCG   LCG
     00      9    30
     05      5    25
     15     1.5    8
     25     0.5   2.5
     35     0.15  0.8
     45     0.05  0.25
  47.994294 0.035 0.18

    DARK CASE (dark current test)

    Gain    HCG   LCG
     00     30    30
     05     30    30
     15     30    30
     25     30    30
     35      5    25
     45      1     8
  47.994294  1     5

    ILLUMINATED CASE (13 Feb 21 - after correcting the silly "black-clamping" issue)

    Gain    HCG   LCG
     00     3.5   20.0
     05     2.0   10.0
     15     0.6    3.5
     25     0.2    1.0
     35     0.06   0.35
     45     0.015  0.1
  47.994294 0.01   0.07

'''



#--- Set conversion mode, gain, exposure time here:

GCM = "HCG"          # Gain Conversion Mode ("HCG" or "LCG")
GainSetting = 5.0   # Gain setting 0-48
ExpTime = 0.07        # Exposure time (Seconds: 18E-6 to 30)


cam.set_string('GainConversion',GCM)     # Set gain conversion mode
cam.set_gain(GainSetting)                #   and Gain Setting
cam.set_exposure_time(ExpTime*1.0E6)     # Exposure time (uSec)

#---

cam.set_acquisition_mode( (Aravis.acquisition_mode_from_string('SingleFrame')) )   # Set to single frames

cam.set_boolean('ReverseX',False)     # Use these to flip left-right
cam.set_boolean('ReverseY',False)     #   and up-down

# cam.set_string('ImageCompressionMode','Off')           # Definitely don't want this (WRITE-PROTECTED?)
cam.set_string('AdcBitDepth','Bit12')                  # Only option for this camera
cam.set_string('DeviceTemperatureSelector','Sensor')   # Only option for this camera

cam.set_boolean('DefectCorrectStaticEnable',False)     # Turn off auto-correction of (known) bad pixels

dev = cam.get_device()    # Allows access to "deeper" features

###--- Essential Camera Info

[fullWidth,fullHeight] = cam.get_sensor_size()    # Full frame size
[x,y,width,height] = cam.get_region()             # Get RoI details

###--- Optional Feedback

# print(cam.dup_available_enumerations_as_display_names('GainConversion'))  # List Gain Conversion modes

if verbose:
    print ("")
    print("Full Frame is : %dx%d "%(fullWidth,fullHeight))
    print("ROI           : %dx%d at %d,%d" %(width, height, x, y))
    print("Pixel format  : %s" %(cam.get_pixel_format_as_string()))
    print("Framerate     : %s Hz" %(cam.get_frame_rate()))
    print("Exposure time : %s seconds " %(cam.get_exposure_time()/1.0E6))
    print("Gain Conv.    : ",cam.get_string('GainConversion'))
    print("Gamma enable  : ",cam.get_boolean('GammaEnable'))
    print("Gamma value   : ",cam.get_float('Gamma'))
    print("Camera Temp   : %s C" % (dev.get_float_feature_value("DeviceTemperature")))
    print("")

    print ("Available Formats : ",cam.dup_available_pixel_formats_as_display_names ())
    print ("acquisition_mode ",Aravis.acquisition_mode_to_string(cam.get_acquisition_mode()))
    print ("framerate bounds ",cam.get_frame_rate_bounds())
    print ("Exp. Time bounds ",cam.get_exposure_time_bounds())
    print ("Gain bounds      ",cam.get_gain_bounds())
    print ("")

    vlt=cam.get_float('PowerSupplyVoltage')
    cur=cam.get_float('PowerSupplyCurrent')
    print ("Power Supply Voltage   : ",vlt," V")
    print ("Power Supply Current   : ",cur," A")
    print ("Total Dissiapted Power :",vlt*cur, "W")
    print ("")

    # print ("Features :", cam.dup_available_enumerations_as_strings ())
    # print ("")
    # print ("Features :", cam.dup_available_enumerations_as_display_names ())

#    exit()

###--- Do the Acquisition

print("Start acquisition")
cam.start_acquisition()
for i in range(1):

    rawFrame=cam.acquisition(0.0)           # Grab a single frame (timeout=0 means forever)
    npFrame = FU.FLIR2numpy(rawFrame,True)  # Convert to numpy array

    np.save("temp.npy",npFrame)             # Save a binary version

    if verbose:

        print ("")
        print ("Dimensions of image ",i," : ",npFrame.shape)
        
        print("Gain Conv.    : ",cam.get_string('GainConversion'))
        print("Gain Setting  : ",cam.get_gain())
        print("Exposure time : %s seconds " %(cam.get_exposure_time()/1.0E6))

    if writeFITS:   # Write "temp.fits" with result
        hdu = fits.PrimaryHDU(npFrame)            # Create HDU of new data
        hdu.writeto('temp.fits',overwrite=True)   #  and write it out!

    if showImg:
        minVal,maxVal = np.amin(npFrame),np.amax(npFrame)
        meanVal,medVal = np.mean(npFrame),np.median(npFrame)

        fig = plt.figure(figsize=(16,8))

        plt.subplot(1,2,1)
        plt.imshow(npFrame,cmap='gray',vmin=minVal,vmax=maxVal)
        plt.xticks([])
        plt.yticks([])
        plt.title("Single Read")
        plt.xlabel("Min "+str(minVal)+" Max "+str(maxVal)+" Mean "+str("{:.2f}".format(meanVal))+" Median "+str("{:.2f}".format(medVal)))
        plt.colorbar()

        plt.subplot(1,2,2)
        plt.hist(npFrame.reshape(-1),bins=20,  label="Pixel Values")   # range=[0,20],

        plt.show()

    # imnm = "test_"+str(i)+".png"
    # cv2.imwrite(imnm,npFrame)

cam.stop_acquisition()
print ("Done")


