## Table of contents :

<img align="right" src=https://user-images.githubusercontent.com/52712038/91175054-79dfe300-e6e0-11ea-98a7-9cae7162c29f.png> 

- [About the project](#about-the-project)
	- [Who is it for ?](#who-is-it-for)
	- [What is it for ?](#what-is-it-for)
- [Getting started !](#getting-started)
	- [Prerequisites](#prerequisites)
	- [Installation](#installation)
- [How to use](#how-to-use)
	- [setting up the application](#setting-up-the-application)
- [License](#license)
- [Contact](#contact-not-for-bug-reports)
- [Help](#help)

## About the project
### Who is it for
**Zi²** is an application for people who are working with **AFM** *(Atomic Force Microscopes)* and **PFM** *(Piezo Force Microscope)* on the **Nanoscope V** with a **Zurich Instruments HF2LI** lock-in amplifier.

### What is it for
The goal of this application is to fulfill a need from the scientists working with the previously described instruments. They needed to be able *(in my case)* to **plot more than the 3 images they where limited to in the Nanoscope V's software**. Given that all the signals that we want can be sourced to the Zurich Instruments **HF2LI**, we thus can **communicate with it's API using Python** to obtain all the demodulators data streams *(R, Theta, X, Y, Frequency)* we need and plot as many graphs as we want.

## Getting started
### Prerequisites
There are two ways of running this application, either using an simple ***EXE*** for **Windows** that has to be launched within its folder (because they contain all the python modules, appliccation data etc...) and that requieres no installer. 

**Or** by **running the source code** of the application with Python and all the modules. In wich case you'll need :
- **Python version 3.7.7** at https://www.python.org/downloads/

- **Numpy** module version ***1.19.0***, to deal with matrixes and data
```bash
pip install numpy
```
- **Zhinst** module version ***20.1.1335*** *(from Zurich Instruments)*, to communicate with the HF2LI
```bash
pip install zhinst
```
or get it at https://pypi.org/project/zhinst/
- **Matplotlib** module version ***3.2.2*** *(upper versions don't work if you want the EXE)*, to do annimated 3D plotting 
```bash
pip install matplotlib==3.2.2
```
- **Datetime** module (usualy included in Python), to get the current time
```bash
pip install DateTime
```
- **Pillow** module version ***7.2.0***, to load pngs to the GUI
```bash
pip install pillow
```
- **Gwyfile** module version ***0.2.0***, to save microscope's images 
```bash
pip install gwyfile
```
The versions of the modules shouldn't cause any problems except for matplolib wich for some reason won't run in an EXE in versions upper than 3.2.2, I just included my versions in case you have problems and want to replicate my setup to avoid any conflict.

### Installation
Like i said there no installer, just a folder wich contains all the necessary files.
If you want the Windows EXE version than :
- **download** the Github repository as a ZIP
- **UnZIP** it and open it
- **UnZIP** the *"Zi²"* part 1 *(had to be on two parts because >25MB)*
- **Open** the folder *"Zi²"* and find the executable named *"Zi²"*

If you want to run the source code than :
- **download** the Github repository as a ZIP
- **UnZIP** it and open it
- **Go to** the folder named *"Source code"*
- **find** the file *"Zi².py"*
- **Run** it with your editor (Python's IDLE, Vscode, etc...)

## How to use 
### setting up the application

Here you can see the "Command" part of the GUI wich is divided in frames
<img align="right" src=https://user-images.githubusercontent.com/52712038/91230716-4cb92200-e72c-11ea-8862-33c57b3ada5d.png> 
- **Demods**
In which you can select the demod you want and the data you want to plot from it
- **Settings** *(line by line)*
	- Tell the software in which direction the microscope is scanning by clicking on **"Up-Down"** which changes to **"Down-up"** and vice versa so that the application starts plotting in the right dirrection. If you make a mistake you can just click on **"Flip"** to Flip the image.
	- **Draw** represents the number of Images you want to make, if you have the Nanoscope V and HF2LI then put 0, it will run continuously like the Nanoscope V does and synchronize with it. If you put another number than 0 the process won't be synchronized but it will make the number of images you requested. **TLDR : Let it at 0 unless you know what you're doing**
	- **Size** is simply the size in pixels of the square images you want to make *(limits are 32 and 4096)*
	- **Freq** is the frequency of line scanning (number of lines per second) **put the same as in the Nanoscope V software**
	- **Trace mode** let's you select wether you want to see the trace or retrace of the AFM image, however both are saved so it's just for visualisation
	- **Color** is just the color grading for the scale in the 3D graphs
- **Save**
	- **Sample** is the sample name, it will change the name of the files that will be saved, the files will be saved in a different folder that will be named ***"Year-Month-Day"*** and the files in it will be ***"Hour-Minute-Second : SampleName : HF2LI id : demods X sample,Y : frame Z trace.format"*** and another named the same with **retrace** at the end. **X** is the demod number **Y** the demod data **Z** the number of the frame being saved and **format** the format which can be **csv** or **gwy** 
**TLDR name of sample**
	- **Save after image** check if you want to save
	- **Save to custom** check if you want to save in the adress you've chosen instead of the default adress
	- **Custom adress Path** the path to your custom adress, you can click in the **"..."** button to choose one instead of typing
- **Controls**
	- **Reset** , resets all the images and waits for a Vertical Trigger from the Nanoscope V to plot
	- **Pause** , pauses the graphs but does not pause the sampling process, so it's just a graphical pause but not a real pause
	- **Start**, verifies that all the settings are correct, initializes the graphs and then waits for a Vertical Trigger from Nanoscope V to begin the sampling process and plotting
	- **Stop**, stops all the processes and clears the graphs, confirmation box befor stoping
- **Connect**
Connects to your HF2LI, make sure Labone is runing
- **Show logs**
Opens a window with logs and tells you what the program does, also tells you if there are problems so feel free to use it if something goes wrong.
- **Advanced settings**
Please read the ***advanced settings section*** if you want to go further.

## License
The application is protected by the CeCILL-C FREE SOFTWARE LICENSE AGREEMENT

*"The purpose of this Free Software license agreement is to grant users the right to modify and re-use the software governed by this license. The exercising of this right is conditional upon the obligation to make available to the community the modifications made to the source code of the software so as to contribute to its evolution."*

You can read the full LICENSE at : https://cecill.info/licences/Licence_CeCILL-C_V1-en.txt

## Contact, *Not for bug reports*
You can contact me at adrianos.sidiras@gmail.com, however I no longer work on this project since it was for an internship
## Help 
Please consider reading the manual to see commun errors if something goes wrong, and if the problem can't be solved i encourage you to modify the source code so as to solve the problem



	






 




 


