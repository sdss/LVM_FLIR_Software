# LVM_FLIR_Software
 Python scripts for working with the LVM Acquisition and Guide (AG) cameras from FLIR. These routines use packages from the [Aravis Project](https://github.com/AravisProject)

**FLIR_Utils.py** Python utilities to work with the FLIR camera. These include:

         Setup_Camera   - Does initial setup, returning cam, dev
    Standard_Settings   - Sets up and (eventually) checks standard settings that are unlikely to change.
           FLIR2numpy   - Converts a (single frame) FLIR buffer to numpy
          FLIR_Status   - Prints a lot of camera status info
           FLIR_Power   - Returns voltage, current, power, temperature
            Write_PNG   - Writes a PNG file with the supplied image
       Acquire_Frames   - Acquires and returns a single frame or multiple frames
            ResetFLIR   - Immediately resets and reboots the device
     FactoryResetFLIR   - Does a reset to Factory parameter values

**CharFLIR.py** Python script to acquire gain, read noise, dark current data.

**read_FLIR.py** Python script to read the FLIR camera and display the image and histogram.

**FLIR_FullStatus.py** Simple utility to dump the full status of the FLIR camera to the screen.

**ResetFLIR.py** Simply issues the DeviceReset command, which immediately resets and reboots the device

**FactoryResetFLIR.py** Issues the FactoryResetFLIR command. Use with caution!

**WriteTestScript.py** Writes a generic script file for testing FLIR cameras with CharFLIR.py

**WriteTestScript_MV.py** Same as WriteTestScript.py, but specifically for mean-variance testing

**description.txt** List of all commands, etc., including some description. Produced by arv-tool-0.8 description

**features.txt** List of all "features". Produced by arv-tool-0.8 features. Note that arv-tool-0.8 values lists the current values.
