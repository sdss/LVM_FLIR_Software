'''
    ResetFLIR - Resets and Reboots FLIR Camera

    Simply issues the DeviceReset command, which immediately resets and reboots the device

'''

import sys,time
import gi 
import cv2
import ctypes
import numpy as np
import matplotlib.pyplot as plt

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

Aravis.update_device_list()

if fakeCam:
    Aravis.enable_interface("Fake")    # using arv-fake-gv-camera-0.8
    cam = Aravis.Camera.new(None)      # Instantiate cam
    print ("Instantiated cam with arv-fake-gv-camera-0.8")

else:             # Note: We expect only one "real"camera

    try:
      cam = Aravis.Camera.new(Aravis.get_device_id(0))      # Instantiate cam
      print ("Instantiated cam with FLIR")
    except:
      print("No camera found")
      exit()

printStatus(cam)

#--- Execute the reset

print("Issuing DeviceReset Command")
print("")

dev = cam.get_device()                    # Allows access to "deeper" features
dev.execute_command ('DeviceReset')       # Do the reset

print("")
time.sleep(5)
printStatus(cam)

