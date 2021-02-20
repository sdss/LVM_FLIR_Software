'''
	Simple utility to dump the full status of the FLIR camera to the screen.
'''

import sys
import gi 
import cv2
import ctypes
import numpy as np

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

[fullWidth,fullHeight] = cam.get_sensor_size()    # Full frame size
[x,y,width,height] = cam.get_region()             # Get RoI details
payload = cam.get_payload()                       # Get "payload", the size of in bytes


print("Camera vendor : %s" %(cam.get_vendor_name()))
print("Camera model  : %s" %(cam.get_model_name()))
print("Camera id     : %s" %(cam.get_device_id()))
print("Pixel format  : %s" %(cam.get_pixel_format_as_string()))

print ("")
print("Full Frame is : %dx%d "%(fullWidth,fullHeight))
print("ROI           : %dx%d at %d,%d" %(width, height, x, y))
print("Pixel format  : %s" %(cam.get_pixel_format_as_string()))
print("Frame size     : %d  Bytes" %(payload))

print ("")
print("Framerate     : %s Hz" %(cam.get_frame_rate()))
print("Exposure time : %s seconds " %(cam.get_exposure_time()/1.0E6))
print("Gain Conv.    : ",cam.get_string('GainConversion'))
print("Gamma enable  : ",cam.get_boolean('GammaEnable'))
print("Gamma value   : ",cam.get_float('Gamma'))

print("")
print ("Available Formats : ",cam.dup_available_pixel_formats_as_display_names ())
print ("acquisition_mode ",Aravis.acquisition_mode_to_string(cam.get_acquisition_mode()))
print ("framerate bounds ",cam.get_frame_rate_bounds())
print ("Exp. Time bounds ",cam.get_exposure_time_bounds())
print ("Gain bounds      ",cam.get_gain_bounds())
print ("")

print ("BlackLevelSelector ",cam.get_string('BlackLevelSelector'))

print ("Gain ",cam.get_float('Gain'))
print ("BlackLevelClampingEnable ",cam.get_boolean('BlackLevelClampingEnable'))
cam.set_boolean('BlackLevelClampingEnable',False)
print ("BlackLevelClampingEnable ",cam.get_boolean('BlackLevelClampingEnable'))

# print ("Features :", cam.dup_available_enumerations_as_strings ())  # Dumps all enumertions

print ("GainAuto :", cam.dup_available_enumerations_as_display_names ('GainAuto'))
print (cam.get_gain_auto())
