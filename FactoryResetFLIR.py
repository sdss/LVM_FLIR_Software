'''
    FactoryResetFLIR - Executes Factory Reset of the FLIR Camera

    Simply sets up communication and then issues the FactoryResetFLIR command.

    Note: This overwrites any options you have set!
    
'''

import sys,time
import gi 
import cv2
import ctypes
import numpy as np
import matplotlib.pyplot as plt

import FLIR_Utils as FU           # All the camera interface stuff

def printStatus(cam):
    dev = cam.get_device()    # Allows access to "deeper" features
    [fullWidth,fullHeight] = cam.get_sensor_size()    # Full frame size
    [x,y,width,height] = cam.get_region()             # Get RoI details
    vlt=cam.get_float('PowerSupplyVoltage')
    cur=cam.get_float('PowerSupplyCurrent')


    print ("")
    print("Full Frame is : %dx%d "%(fullWidth,fullHeight))
    print("ROI           : %dx%d at %d,%d" %(width, height, x, y))
    print("Pixel format  : %s" %(cam.get_pixel_format_as_string()))
    print("Framerate     : %s Hz" %(cam.get_frame_rate()))
    print("Exposure time : %s seconds " %(cam.get_exposure_time()/1.0E6))
    print ("Power Supply Voltage   : ",vlt," V")
    print ("Power Supply Current   : ",cur," A")
    print ("Total Dissiapted Power :",vlt*cur, "W")
    print("Camera Temp   : %s C" % (dev.get_float_feature_value("DeviceTemperature")))
    print("")

    print ("acquisition_mode ",Aravis.acquisition_mode_to_string(cam.get_acquisition_mode()))
    print("Gain Conv.    : ",cam.get_string('GainConversion'))
    print("Gain Setting  : ",cam.get_gain())
    print("Exposure time : %s seconds " %(cam.get_exposure_time()/1.0E6))
    print("")



fakeCam = False   # Whether to use the Aravis "fake" camera (software) instead of the FLIR
verbose = True    # How wordy to be

print ("-----")

gi.require_version('Aravis', '0.8')
from gi.repository import Aravis

###--- Set up camera 

cam,dev = FU.Setup_Camera(verbose,False)    # Instantiate camera and dev
FU.Standard_Settings(cam,dev,verbose)       # Standard settings (full frame, etc.)
FU.FLIR_Status(cam,dev)                     # Print out camera info

#--- Execute the reset

print("")

FU.FactoryResetFLIR(cam,dev,True)    # Execute factory reset

print("")
time.sleep(5)
printStatus(cam)

