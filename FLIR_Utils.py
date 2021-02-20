'''
    Python utilities to work with the FLIR camera.

         Setup_Camera   - Does initial setup, returning cam, dev
    Standard_Settings   - Sets up and (eventually) checks standard settings that are unlikely to change.
           FLIR2numpy   - Converts a (single frame) FLIR buffer to numpy
          FLIR_Status   - Prints a lot of camera status info
           FLIR_Power   - Returns voltage, current, power, temperature
            Write_PNG   - Writes a PNG file with the supplied image
       Acquire_Frames   - Acquires and returns a single frame or multiple frames
            ResetFLIR   - Immediately resets and reboots the device
     FactoryResetFLIR   - Does a reset to Factory parameter values
'''

import sys
import gi           # To ensure correct Aravis version
import cv2          # To (optionally) write png files
import numpy as np

gi.require_version('Aravis', '0.8')     # Version check
from gi.repository import Aravis        # Aravis package

#--------------------------------------------------------------------------------------------

def Setup_Camera(verbose, fakeCam = False):

    '''
        Instantiates a camera and returns it, along with the corresponding "dev". This
        gives access to "deeper" camera functions, such as the device temperature.

        If fakeCam = True, it returns the fake camera object, a software equivalent,
        with (presumably realistic) noise, etc.

    '''

    Aravis.update_device_list()             # Scan for live cameras

    if fakeCam:
        Aravis.enable_interface("Fake")     # using arv-fake-gv-camera-0.8
        cam = Aravis.Camera.new(None)       # Instantiate cam

        if verbose:
            print ("Instantiated FakeCam")

    else:             # Note: We expect only one "real" camera !!

        try:
            cam = Aravis.Camera.new(Aravis.get_device_id(0))      # Instantiate cam
            if verbose: 
                   print ("Instantiated real camera")
        except:
          print("ERROR - No camera found")  # Ooops!!
          return None,None,None             # Send back nothing

    dev = cam.get_device()        # Allows access to "deeper" features

    return cam,dev          # Send back camera, device

#--------------------------------------------------------------------------------------------

def Standard_Settings(cam, dev, verbose):

    '''
        Write standard settings to the camera. This is typically items that will
        never change (such as single frame mode, use full frame, no Auto-exposure, etc.)

        Note that the DefectCorrectStaticEnable option uses an internal look-up table of
        factory-measured bad pixels and interpolates across them. We want this off!

    '''

    # [fWid,fHgt] = cam.get_sensor_size()   # Full frame size

    fWid,fHgt = 1600,1100                 # Full frame size
    cam.set_binning(1,1)                  # Pixel binning 1x1
    cam.set_region(0,0,fWid,fHgt)         # Use full frame

    frameRate = 1.0                       # Frame rate (Hz). I don't think that this has any effect (for single frames)
    cam.set_frame_rate(frameRate)         # Frame rate (Hz)

    dev.set_string_feature_value('PixelFormat', 'Mono16')

    cam.set_boolean('GammaEnable',False)                                               # No gamma correction!
    cam.set_exposure_time_auto(Aravis.auto_from_string('Off'))                         # Auto-exposure off
    cam.set_gain_auto(Aravis.auto_from_string('Off'))                                  # Also auto-gain
    cam.set_acquisition_mode( (Aravis.acquisition_mode_from_string('SingleFrame')) )   # Set to single frames

    cam.set_boolean('ReverseX',False)     # Use these to flip left-right
    cam.set_boolean('ReverseY',False)     #   and up-down

    cam.set_string('AdcBitDepth','Bit12')                  # 12-bit ADC - only option for this camera
    cam.set_string('DeviceTemperatureSelector','Sensor')   # Which temperature sensor - only option for this camera

    cam.set_boolean('DefectCorrectStaticEnable',False)     # Turn off auto-correction of (known) bad pixels

    cam.set_boolean('BlackLevelClampingEnable',False)      # CHECK - seems to correct low signal clamping

    if verbose:
        print ("Set RoI to Full Frame ",fWid," x ",fHgt)
        print ("Set binning to 1 x 1")
        print ("Auto-exposure off, Single frame mode")
        print ("No X or Y-flips of frame")
        print ("ADC depth 12 bits")
        print ("auto-correction of bad pixels off")
        print ("BlackLevelClampingEnable off")

    # cam.set_string('ImageCompressionMode','Off')      # Definitely don't want this (WRITE-PROTECTED?)
    # [x,y,width,height] = cam.get_region()             # Get RoI details
    # print(cam.dup_available_enumerations_as_display_names('GainConversion'))  # List Gain Conversion modes

#--------------------------------------------------------------------------------------------

def FLIR2numpy(buf,verbose):

    '''
        Converts FLIR camera buffer to numpy Array

            Input:    buf - a (single frame) buffer returned from the FLIR camera
                      verbose - how wordy to be
            Returns:  img - a numpy array of the frame
    '''

    import ctypes     # Allows access to C data types (to read FLIR buffer)

    if not buf:       # Nothing there. Return nothing
        return None

    pixel_format = buf.get_image_pixel_format()
    print("pixel_format ",pixel_format)

    bits_per_pixel = pixel_format >> 16 & 0xff

    print("bpp=",bits_per_pixel)

    if bits_per_pixel == 8:
        INTP = ctypes.POINTER(ctypes.c_uint8)
    else:
        INTP = ctypes.POINTER(ctypes.c_uint16)

    addr = buf.get_data()
    ptr = ctypes.cast(addr, INTP)
    im = np.ctypeslib.as_array(ptr, (buf.get_image_height(), buf.get_image_width()))
    im = im.copy()

    print ("im size ",sys.getsizeof(im))
    print ("im type ",im.dtype)
    # f = open('im.bin', 'w+b')
    # binary_format = bytearray(im)
    # f.write(binary_format)
    # f.close()

    np.save("im",im)    # Make a .npy file    

    if verbose:
        print ("Mean, standard dev  ",np.mean(im), np.std(im))

    return im

#--------------------------------------------------------------------------------------------

def FLIR_Status(cam,dev):

    '''
        Prints a whole lot of info from the camera. Verbose is the only way...
    '''

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

#--------------------------------------------------------------------------------------------

def FLIR_Power(cam,dev,verbose):

    '''
        Returns info on current power, temperature, etc.
    '''

    volts=cam.get_float('PowerSupplyVoltage')
    current=cam.get_float('PowerSupplyCurrent')
    power=volts*current
    temperature = dev.get_float_feature_value("DeviceTemperature")

    if verbose:

        print ("Power Supply Voltage   : ",volts," V")
        print ("Power Supply Current   : ",current," A")
        print ("Total Dissiapted Power :",power, "W")
        print ("Camera Temperature      : %s C" % (temperature))


    return volts,current,power,temperature

#--------------------------------------------------------------------------------------------

def Write_PNG(img,imName):

    '''
        Writes a PNG file with the supplied image.
    '''

    cv2.imwrite(imName,img)

#--------------------------------------------------------------------------------------------

def Acquire_Frames(cam,nFrames,frameWait=1.0,verbose=False):

    '''
        Acquires and returns a single frame or multiple frames. If nFrames>1, the
        routine first builds a list of individual frames and then returns the .stack of
        the result. This means that if nFrames=1, the routine returns a 2D numpy array
        of the frame, whereas if nFrames>1, it returns a 3D array of data. This makes
        doing statistics "down the cube" easier.

    '''
    import time     # To sleep between frames

    if verbose:
        print("  Starting acquisition of ",nFrames," frame(s)...")

    cam.start_acquisition()    # Start acquisition process

    if nFrames==1:                       # Only a single frame

        rawFrame=cam.acquisition(0.0)        # Grab a single frame (timeout=0 means forever)
        img = FLIR2numpy(rawFrame,verbose)   # Convert to numpy

        if verbose:
            print ("")
            print ("Dimensions of image : ",img.shape)
            print ("Mean, standard dev  ",np.mean(img), np.std(img))
            print("")

    else:

        imList = []                 # Initialize list to hold numpy arrays

        for i in range(nFrames):    # Do this many

            if verbose:
                print ("    Frame ",i+1)       # Some feedback

            rawFrame=cam.acquisition(0.0)       # Grab a single frame (timeout=0 means forever)
            imN = FLIR2numpy(rawFrame,False)    # Convert to numpy
            imList.append(imN)                  # Add it to the list

            time.sleep(frameWait)   # Pause between exposures

        img = np.stack(imList)      # Convert to 3D array

    cam.stop_acquisition()     # Stop acquisition

    if verbose:
        print ("  Returning image data with dimensions ",img.shape)

    return img

#--------------------------------------------------------------------------------------------

def ResetFLIR(cam,dev,verbose):

    '''
        Simply issues the DeviceReset command, which immediately resets and reboots the device

    '''
    import time

    print("Issuing DeviceReset Command")
    print("")

    dev = cam.get_device()                    # Allows access to "deeper" features
    dev.execute_command ('DeviceReset')       # Do the reset

    print("")
    time.sleep(5)   # Need some time to restart (COULD BE SHORTER!)

#--------------------------------------------------------------------------------------------

def FactoryResetFLIR(cam,dev,verbose):

    '''
        Issues the FactoryReset command, which restores all values to factory new settings.

        Use with caution!

    '''
    import time

    print("Issuing FactoryReset Command")
    print("")

    dev.execute_command ('FactoryReset')       # Do the reset

    print("")
    time.sleep(5)   # Need some time to restart (COULD BE SHORTER!)

