'''
    Python script to acquire gain, read noise, dark current data.

    The program reads a script file containing information about the data. This
    script file looks like this:

    Name1  GainConversion1  gain1  expTime1  nFrames1
    Name2  GainConversion2  gain2  expTime2  nFrames2
      :         :             :       :          :


    A typical Name would be TA_H_10_0.05.dat for High Conversion Gain, a gain of 10.0
    and an exposure time of 0.05 seconds. The corresponding script line is:

    TA_H_10_0.05_10.dat  HCG  10.0  0.05  10

    The routine writes a file with this name containing the (numpy) data.

'''

import numpy as np
import time                  # To measure how long this takes
import FLIR_Utils as FU      # All the camera interface stuff

start_time = time.time()     # And we're off...

sCroot = 'MV_Feb13_2'         # File root for script, log file
scriptFile = sCroot+'.txt'   # Script file of test runs
logFile = sCroot+'.log'      # Log file

verbose = True

frameWait = 1.0     # Wait this long between frames

gainConv = 'HCG'    # CHANGE - will be read from script
expTime = 1.0E6     # CHANGE = will be read from script
gain = 15.0         # # 47.994294 CHANGE - will be read from script

###--- Set up camera 

cam,dev = FU.Setup_Camera(verbose,False)    # Instantiate camera and dev
FU.Standard_Settings(cam,dev,verbose)       # Standard settings (full frame, etc.)
FU.FLIR_Status(cam,dev)                     # Print out camera info

###--- Now execute commands from script file, writing to log file

inList = open(scriptFile,"r").read().splitlines()    # Now one set of parameters per line
outLog = open(logFile,"w")                           # Open log file for text output

outLog.write("Filename  GainMode   Gain   ExpTime  nFrames  Temperature Mean  Variance\n")


for i in range(len(inList)):     # Step through one line at a time

    if inList[i][0]!="#":          # Ignore comment lines, if any

        ###--- Parse script file and provide feedback

        vals = inList[i].split()   # Split out to individual items and then extract:
        fName,gainConv,gain,expTime,nFrames = vals[0],vals[1],float(vals[2]),float(vals[3]),int(vals[4])

        print ("")
        print ("Working on file ",i+1," with ",nFrames," frames and output ",fName)                 # Feedback
        print ("  GainMode: ",gainConv,"  Gain: ",gain,"  Exposure Time: ",expTime/1.0E6," sec")

        ###--- Set parameters and take data

        cam.set_gain(gain)                          # Gain value
        cam.set_exposure_time(expTime)              # Exposure time (uSec)
        cam.set_string('GainConversion',gainConv)   # Gain conversion mode

        volts,current,power,temperature = FU.FLIR_Power(cam,dev,False)   # Get power temperature info

        theFrames = FU.Acquire_Frames(cam,nFrames,frameWait,verbose)       # Acquire the data

        ###--- Now save binary data and quick-look results

        np.save(fName,theFrames)               # Write binary file of data

        mean = np.mean(theFrames)              # Average pixel value across chip
        varMat = np.var(theFrames,axis=0)      # Collapse to 2D matrix of variances
        variance = np.mean(varMat)             # The average variance across the chip

        logLine = fName +" "+ gainConv +" "+ str(gain) +" "+ str("{:.3e}".format(expTime/1.0E6)) +" "+ str(nFrames) +" "+ str("{:.3f}".format(temperature)) +" "+ str("{:.3e}".format(mean)) +" "+ str("{:.3e}".format(variance))  
        outLog.write(logLine+"\n")
        print("  "+logLine)

inList.close     # Close script file
outLog.flush     # Purge buffer, if needed
outLog.close     # Close logfile

print ("")
print ("Elapsed time : ",(time.time() - start_time))
