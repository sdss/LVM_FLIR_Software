'''
    WriteTestScript.py - Writes a script file for testing FLIR cameras for Mean Variance

    The test script looks like this:

    Name1  GainConversion1  gain1  expTime1  nFrames1
    Name2  GainConversion2  gain2  expTime2  nFrames2
      :         :             :       :         :

    A typical Name would be TA_H_10_0.05_7.dat for High Conversion Gain, a gain of 10.0
    and the seventh exposure time in the sequence. The corresponding script line is:

    TA_H_10.0_0.05_10.dat  HCG  10.0  0.05   (where 0.05 is the actual exposure time)

    The testing routine (CharFLIR.py) writes a file with this name containing the (numpy) data.

    I tested the maximum exposure time as a function of gain and gain mode:

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

    Note that the maximum gain reported by the camera (with the cam.get_gain_bounds()
    command) is 47.994294033026364

'''

import numpy as np

scNm = "MV_Feb13.txt"       # Name of script file to write
outFile = open(scNm, "w")   # Open file to write text

nmRt = "V1"      # Root for test file names
nFrm = "20"      # This many frames per test
nTim = 20         # This many time steps per gain, gainMode combination
tMin = 18.0E-6   # Minimum exposure time (sec)

gain = [0.0,5.0,15.0,25.0,35.0,45.0,47.994294]    # Array of gain values
eTHmax = [3.5,2.0,0.6,0.2,0.06,0.015,0.01]        # Max exposure time HCG mode  VALUES for MV 13 Feb 21 
eTLmax = [20.0,10.0,3.5,1.0,0.35,0.1,0.07]        # Max exposure time LCG mode     after Black Clamping off
gModes = ["HCG","LCG"]                            # Gain modes

# eTHmax = [9.0,5.0,1.5,0.5,0.15,0.05,0.035]         # Max exposure time HCG mode  VALUES FOR Dec.20 Illuminated
# eTLmax = [30.0,25.0,8.0,2.5,0.8,0.25,0.18]        # Max exposure time LCG mode
# eTHmax = [30.0,30.0,30.0,30.0,5.0,1.0,1.0]         # Max exposure time HCG mode  VALUES for Dakr case
# eTLmax = [30.0,30.0,30.0,30.0,25.0,8.0,5.0]        # Max exposure time LCG mode


nGains = len(gain)   # This many gain settings
nGmodes = 2          # And this many gain modes

###--- Low gain first

for g in range(nGains):        #   and gains...

    expT = np.linspace(tMin,eTLmax[g],nTim)       # Create sequence of exposure times

    for t in range(nTim):      #   and expTime

        Name = nmRt +"_L_"+ str(gain[g]) +"_"+ str(t)                                               # Name of data file to write
        scrLine = Name +" LCG "+ str(gain[g]) +" "+ str("{:.3e}".format(expT[t]*1.0E6) +" "+nFrm)   # One line of the script

        outFile.write(scrLine+"\n")     # Write script line to file

###--- And now high gain

for g in range(nGains):        #   and gains...

    expT = np.linspace(tMin,eTHmax[g],nTim)       # Create sequence of exposure times

    for t in range(nTim):      #   and expTime

        Name = nmRt +"_H_"+ str(gain[g]) +"_"+ str(t) + ".dat"           # Name of data file to write
        scrLine = Name +" HCG "+ str(gain[g]) +" "+ str("{:.3e}".format(expT[t]*1.0E6) +" "+nFrm)   # One line of the script

        outFile.write(scrLine+"\n")     # Write script line to file

outFile.flush()             # Apparently necessary
outFile.close               # Close the file
