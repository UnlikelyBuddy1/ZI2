# ASG : Zi²
![image](https://user-images.githubusercontent.com/52712038/91175054-79dfe300-e6e0-11ea-98a7-9cae7162c29f.png)
## Table of contents :
- About the project
	- Description
	- Who is it for ?
- Getting started
	- Prerequisites
	- Installation
- Usage
	- Setting up Zi²
	- Making an image
	- Saving an image
	- Getting further
- License
- Contact
- Getting help
	- Manual
	- Report bugs

## About the project
### Who is it for ?
**Zi²** is an application for people who are working with **AFM** *(Atomic Force Microscopes)* and **PFM** *(Piezo Force Microscope)* on the **Nanoscope V** with a **Zurich Instruments HF2LI** lock-in amplifier.

### What is it for ?
The goal of this application is to fulfill a need from the scientists working with the previously described instruments. They needed to be able *(in my case)* to **plot more than the 3 images they where limited to in the Nanoscope V's software**. Given that all the signals that we want can be sourced to the Zurich Instruments **HF2LI**, we thus can **communicate with it's API using Python** to obtain all the demodulators data streams *(R, Theta, X, Y, Frequency)* we need and plot as many graphs as we want.

## Getting started !
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


