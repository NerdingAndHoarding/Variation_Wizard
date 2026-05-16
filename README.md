Variation_Wizard and Gen_Vocab by Nerding and Hoarding 2026
Variation_Wizard
An addon to the python_wizard that can generate LPC speech library to arduino. The Variation_wizard is a graphic interface windows program lets you generate many LPC variations of the same wave-file. The best version can then be used by Batch_Wizard to turn several wave-files into a speach library to run using Talkie on Arduino

TODO update this text to be about variation_wizard


User instructions
Save your audio-clips for your Vocab Library in a folder. They must be .wav Mono 8000khz Signed 16-bit PCM. You can use Audacity for cutting and making wave from mp3. About 80-90 seconds total fits on Arduino Nano.
 
2. Click "01_Batch_Wizard_gui.py"
Select your audio folder and name your txt file. (it is only a temporary file). Make adjustments to all the parameters.

3. Click "02_Gen_Vocab_gui.py"
Name your vocal libray (YOURNAME). And find the txt file generated earlier. Click generate.

4. Open the talkie_YOURNAME.ino file in the talkie_YOURNAME folder and upload to your arduino board.

5. Start serial monitor at 115200. write number 1, 2 , 3 etc + ENTER to test the sounds in your vocab library.

6. To use your vocab in an arduino scetch you must have the  YOURNAME.h and YOURNAME.cpp in the same folder as your arduino sketch (.ino file) write (#include "Talkie.h"
#include "vocab_YOURNAME.h") at the top of your scetch. call the sounds voice.say(z_001);

7. Quick n' Dirty Tutorial at: https://youtu.be/mL2wercQGJo

8. Read more on https://github.com/NerdingAndHoarding

9. https://github.com/ptwz/python_wizard

10. Read up on original Talkie for more information https://github.com/going-digital/Talkie

...below copy pasted from original python_wizard https://github.com/ptwz/python_wizard :


Updates to base python_wizard
Added "lpcplayer" package (based on talkie) to support Play feature in GUI.
Added dirty support for other LPC coding tables. TMS5100 is default now.
```
    -T {tms5220,tms5100}, --tablesVariant {tms5220,tms5100}
                          Tables variant
  ```                        
Support for python formatted output
```
    -f {arduino,C,hex,python}, --outputFormat {arduino,C,hex,python}
                          Output file format
  ```
Small fixes and enhancements in GUI

---
This project is a python port of the great macOS tool BlueWizard (https://github.com/patrick99e99/BlueWizard), which is written in objective C and I was not familiar enough with this C dialect to make an portable command line application out of it.
It is intended to convert (voice) audio streams into LPC bitstreams used in the TMS 5220 chip or e.g. in the Arduino library Talkie. Now you can generate your own LPC streams and make your chips say the things you want them to.
Compared to BlueWizard some minor features have been added:
Ability to downsample a wave file automatically
Automated output formatters for C, Arduino (C-Dialect) and plain hex
Prerequisites:
Python 2.7
SciPy >= 0.18.1
Usage:
```
       python\\\\\\\\\\\\\\\_wizard.py \\\\\\\\\\\\\\\[-h] \\\\\\\\\\\\\\\[-u UNVOICEDTHRESHOLD] \\\\\\\\\\\\\\\[-w WINDOWWIDTH] \\\\\\\\\\\\\\\[-U] \\\\\\\\\\\\\\\[-V]
                        \\\\\\\\\\\\\\\[-S] \\\\\\\\\\\\\\\[-p] \\\\\\\\\\\\\\\[-a PREEMPHASISALPHA] \\\\\\\\\\\\\\\[-d] \\\\\\\\\\\\\\\[-r PITCHRANGE]
                        \\\\\\\\\\\\\\\[-F FRAMERATE] \\\\\\\\\\\\\\\[-m SUBMULTIPLETHRESHOLD]
                        \\\\\\\\\\\\\\\[-f {arduino,C,hex}]
                        filename

positional arguments:
  filename              File name of a .wav file to be processed

optional arguments:
  -h, --help            show this help message and exit
  -u UNVOICEDTHRESHOLD, --unvoicedThreshold UNVOICEDTHRESHOLD
                        Unvoiced frame threshold
  -w WINDOWWIDTH, --windowWidth WINDOWWIDTH
                        Window width in frames
  -U, --normalizeUnvoicedRMS
                        Normalize unvoiced frame RMS
  -V, --normalizeVoicedRMS
                        Normalize voiced frame RMS
  -S, --includeExplicitStopFrame
                        Create explicit stop frame (needed e.g. for Talkie)
  -p, --preEmphasis     Pre emphasize sound to improve quality of translation
  -a PREEMPHASISALPHA, --preEmphasisAlpha PREEMPHASISALPHA
                        Emphasis coefficient
  -d, --debug           Enable (lots) of debug output
  -r PITCHRANGE, --pitchRange PITCHRANGE
                        Comma separated range of available voice pitch in Hz.
                        Default: 50,500
  -F FRAMERATE, --frameRate FRAMERATE
  -m SUBMULTIPLETHRESHOLD, --subMultipleThreshold SUBMULTIPLETHRESHOLD
                        sub-multiple threshold
  -f {arduino,C,hex}, --outputFormat {arduino,C,hex}
                        Output file format
```
