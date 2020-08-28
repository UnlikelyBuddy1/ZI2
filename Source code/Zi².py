# This code has been made by Adrianos SIDIRAS GALANTE for the INL
# region LICENSE (EN)
"""
Copyright or © or Copr. Adrianos SIDIRAS GALANTE
contributor(s) : David ALBERTINI, INL CNRS UMR 5270 (31/08/2020)

[adrianos.sidiras@gmail.com]

This software is a computer program whose purpose is to be able to bypass 
the limitation of using the 4 auxiliary signals of the HF2LI by taking 
the signals data dirrectly from the HF2LI through the USB port instead of coaxial cables.
 The application will communicate with the HF2LI API using Python to obtain 
 all the demodulators data streams (R, Theta, X, Y, Frequency) we need 
 and plot as many graphs as we want. It has more specificly been built for PFM with DFRT.

This software is governed by the [CeCILL|CeCILL-B|CeCILL-C] license under French law and
abiding by the rules of distribution of free software.  You can  use, 
modify and/ or redistribute the software under the terms of the [CeCILL|CeCILL-B|CeCILL-C]
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the [CeCILL|CeCILL-B|CeCILL-C] license and that you accept its terms.
"""
# endregion
# region Imports
import time
import numpy as np
import csv
import zhinst.utils
from zhinst.ziPython import ziListEnum
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tkinter import *
import tkinter as tk
from tkinter import filedialog
import tkinter.font as tkFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from datetime import datetime
from PIL import ImageTk, Image
from gwyfile.objects import GwyContainer, GwyDataField
import os
import sys
"""
Here it's just some imports, the main ones are Zhinst, Matplotlib and Numpy ..
howerver they are all necessary if you want to run the program
"""
# endregion
# region dictionaries and variables definition
current_directory = (os.path.dirname(os.path.realpath(__file__)))
current_directory = current_directory.replace("\\", '/')

signal_paths = []  # setting up the array in which the signal adresses will be stored
frequency_index = []
data = {}  # setting up data dictionary
im = {}  # setting up ploted images dictionary
"""
here are the default limits of both size of the image in pixels and the nanoscope head quick axis frequency
which corresponds to the "x" axis scanning frequency of a line = trace + retrace
"""
size_min_limit = 31
size_max_limit = 4096
frequency_min_limit = 0.1
frequency_max_limit = 4.1

launch = 1
ani = None  # defining ani for animation as a global variable, otherwise it won't work with Tkinter and the GUI
"""
Here are defined the two triggers we'll be using wich are DIO 0 and DIO 1
those can be found at the back of the HF2LI and are to be plugged in with a coaxial cable
"""
end_of_line = '.TrigDio0'
end_of_frame = '.TrigDio1'

entries_fieldnames=['draw','size','freq','trace_mode','color','save_after_image']
# endregion
# region GUI colors theme
# default
light_gray_color = "#333333"
dark_gray_color = "#1e1e1e"
white_color = "#f1f1f1"
accent_color = "#007acc" 
connect_color = "#eaa100" 
start_color = "#ff830f"
selected_color = "#252526"
#endregion
# region GUI Root declaration and config
"""
Here is the definition of the main window which is called root
we also define the background color and the icon image, 
if you delete the image the program will still launch without problem 
but i would not recommend it
"""
def shut_down():
    try:
        daq_module.finish()
        daq.disconnect()
    except:
        pass
    else:
        pass
    if(os.path.isfile(current_directory+'/configs/entries.csv')):
        with open(current_directory+'/configs/entries.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=entries_fieldnames, delimiter=',')
            csv_writer.writeheader()
            line = {entries_fieldnames[0]:'{}'.format(frames_to_draw_entry.get()), entries_fieldnames[1]:'{}'.format(size_entry.get()),
                    entries_fieldnames[2]:'{}'.format(frequency_entry.get()), entries_fieldnames[3]:'{}'.format(trace_mode_radio.get()),
                    entries_fieldnames[4]:'{}'.format(cmap_selected.get()), entries_fieldnames[5]:'{}'.format(save_after_image_checkbox_state.get())}
            csv_writer.writerow(line)
    if(os.path.isfile(current_directory+'/configs/connexion.csv')):
        with open(current_directory+'/configs/connexion.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=connexion_fieldnames, delimiter=',')
            csv_writer.writeheader()
            line = {connexion_fieldnames[0]:'{}'.format(autoconnect_checkbox_state.get()), connexion_fieldnames[1]:'{}'.format(advanced_checkbox_state.get()),
                    connexion_fieldnames[2]:'{}'.format(manual_sample_freq_checkbox_state.get()), connexion_fieldnames[3]:'{}'.format(save_to_gwy_checkbox_state.get()),
                    connexion_fieldnames[4]:'{}'.format(save_to_txt_checkbox_state.get())}
            csv_writer.writerow(line)
    sys.exit()


root = Tk()
root.title("Zi²")  # assign a title to the window
root.configure(background="#222222")
try:
    root.iconphoto(False, tk.PhotoImage(
        file=current_directory+'/imgs/logo.png'))
except:
    pass
root.config(highlightbackground=dark_gray_color)
fontStyle = tkFont.Font(family="sans-serif", size=16)
root.protocol('WM_DELETE_WINDOW', shut_down)

if("win" in sys.platform):
    root.state('zoomed')
else:
    root.attributes('-zoomed', True)

# endregion
# region GUI FRAMES
"""
Here is the definition of all the frames that are in our GUI 
Frames act like Window inside a bigger window, they are usefull when it 
comes to make some segmentation in the GUI
"""
configuration_frame = LabelFrame(root, padx=0, pady=0, bd=0)
configuration_frame.configure(background=dark_gray_color, fg='#f1f1f1',
                              highlightbackground=dark_gray_color, highlightcolor=dark_gray_color)
configuration_frame.grid(row=0, column=0, sticky=N+E+W)

ploting_frame = LabelFrame(root, padx=0, pady=0, bd=0)
ploting_frame.configure(background=dark_gray_color, fg='#f1f1f1',
                        highlightbackground=dark_gray_color, highlightcolor=dark_gray_color)
ploting_frame.grid(row=0, column=1, sticky=N+E+W+S)

toolbar_frame = LabelFrame(ploting_frame, padx=0, pady=0, bd=0)
toolbar_frame.configure(background=accent_color, fg=accent_color,
                        highlightbackground=accent_color, highlightcolor=accent_color)
toolbar_frame.grid(row=1, column=0, sticky=S+W)

main_frame = LabelFrame(configuration_frame,
                        text="Demods", padx=0, pady=0)
main_frame.configure(background=dark_gray_color, fg=white_color,
                     highlightbackground=dark_gray_color, highlightcolor=dark_gray_color)
main_frame.grid(row=0, column=0, columnspan=4, sticky=N+E+W)

settings_frame = LabelFrame(
    configuration_frame, text="Settings", padx=0, pady=0)
settings_frame.configure(background=dark_gray_color, fg='#f1f1f1',
                         highlightbackground=dark_gray_color, highlightcolor=dark_gray_color)
settings_frame.grid(row=1, column=0, columnspan=4, sticky=N+E+W)

save_frame = LabelFrame(configuration_frame, text="Save", padx=0, pady=0)
save_frame.configure(background=dark_gray_color, fg='#f1f1f1',
                     highlightbackground=dark_gray_color, highlightcolor=dark_gray_color)
save_frame.grid(row=2, column=0, columnspan=4, sticky=N+E+W)

connexion_frame = LabelFrame(
    configuration_frame, text="Connexion & more", padx=0, pady=0)
connexion_frame.configure(background=dark_gray_color, fg='#f1f1f1',
                          highlightbackground=dark_gray_color, highlightcolor=dark_gray_color)

controls_frame = LabelFrame(
    configuration_frame, text="Controls", padx=0, pady=0)
controls_frame.configure(background=dark_gray_color, fg='#f1f1f1',
                         highlightbackground=dark_gray_color, highlightcolor=dark_gray_color)
controls_frame.grid(row=4, column=0, columnspan=4, sticky=N+E+W)
# endregion
# region GUI logs
"""
Here is the logging window, in which you'll be able to see what the program does 
and also have an instant feedback and explaination if an error occurs
this works like a print() statment, you can add your on text using the following instruction :

logs_text.insert('end', "your text \n")
the "\n" is not necessary but it is usefull as it works like the Enter key and thus 
the text will not print on the same line
"""


def dont_close():
    logs.withdraw()


def show_log():
    global logs
    logs.update()
    logs.deiconify()


def save_logs():
    save_text = logs_text.get('1.0', END)
    now = datetime.now()
    day_time = now.strftime("%Y-%m-%d %H-%M-%S")
    filename = 'logs at {}'.format(day_time)
    adress = '{}/logs/{}'.format(current_directory, filename)
    with open(adress, 'w') as csv_file:
        csv_file.write(save_text)


def clear_logs():
    save_text = logs_text.delete('1.0', END)


logs = Toplevel()
logs.title("logs")
logs.configure(bg=light_gray_color)
logs.iconphoto(False, tk.PhotoImage(file=current_directory+'/imgs/logo2.png'))
logs.protocol('WM_DELETE_WINDOW', dont_close)
logs.withdraw()
logs_text = Text(logs, padx=15, pady=10, fg=white_color, bg=light_gray_color,
                 bd=0, highlightbackground=dark_gray_color, highlightcolor=selected_color)
logs_text.grid(row=0, column=0, columnspan=4, sticky=W+E+S+N)
logs_text.insert(
    'end', "Credits to Adrianos SIDIRAS GALANTE - developper of this app\n")
logs_text.insert(
    'end', "- Here you can see the activity and logs of the program ...\n")

save_logs_button = Button(logs, text="Save logs", padx=5, pady=0, fg=white_color, bg=light_gray_color,
                          bd=1, highlightbackground=dark_gray_color, highlightcolor=dark_gray_color, command=save_logs)
save_logs_button.grid(row=1, column=1, sticky=E)
clear_logs_button = Button(logs, text="Clear logs", padx=5, pady=0, fg=white_color, bg=light_gray_color,
                           bd=1, highlightbackground=dark_gray_color, highlightcolor=dark_gray_color, command=clear_logs)
clear_logs_button.grid(row=1, column=2, sticky=W)
spacer_text = Label(configuration_frame, text="    ", padx=0, pady=0, fg=dark_gray_color,
                    bg=dark_gray_color, bd=0, highlightbackground=dark_gray_color, highlightcolor=selected_color)
spacer_text.grid(row=7, column=0, columnspan=4)
show_logs_button = Button(configuration_frame, text="Show logs", padx=0, pady=0, fg=white_color, bg=light_gray_color,
                          bd=1, highlightbackground=dark_gray_color, highlightcolor=selected_color, command=show_log)
show_logs_button.grid(row=8, column=2, columnspan=2, sticky=W+N+E+S)
# endregion
# region GUI logs scrollbar
"""
Here is the scrollbar, it is usefull when your logs are full of text and you need to scroll down
it's just a nice addition. If it bothers you, you can just comment the three following lines using "#" and get rid of it
"""
scrollbar = Scrollbar(logs, command=logs_text.yview,
                      orient="vertical", bg=light_gray_color, bd=1)
scrollbar.grid(row=0, column=5, sticky=N+E+W+S)
logs_text.configure(yscrollcommand=scrollbar.set)
# endregion
# region check all folders are present
if(os.path.isfile(current_directory+'/configs/entries.csv'))and(os.path.isfile(current_directory+'/configs/configs.csv'))and(os.path.isfile(current_directory+'/configs/connexion.csv')):
    logs_text.insert('end',"- all the config files are present\n")
#endregion
# region GUI graphs initialisation
"""
Here we define our Canvas and figure, without those we can't plot anything.
We also state that we want our figures to be drawn inside of our GUI insted of on an other window
"""
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
ratio=w/h
ratio=round(ratio,1)
screen_size=h/111
screen_size_small=screen_size*0.979
fig = plt.figure(figsize=(screen_size_small*ratio, screen_size), facecolor=dark_gray_color)
fig.suptitle('Zi²',  fontsize=16, family="sans-serif",
             color=accent_color, fontweight="bold")
canvas = FigureCanvasTkAgg(fig, master=ploting_frame)
canvas_widget = canvas.get_tk_widget()
# endregion
# region GUI Demodulators list to put in graphs
"""
Here is the definition of what is inside the Demods and Pids frame
You can manually add sample options if you need to
or Demod option if your device posseses more than 6

The same goes for PIDs, if you need to see another thing than Error or value
you can add it
and if you have more than 4 PIDs you can add more
"""
sample_option = ["r", "theta", "r & t", "x", "y", "frequency"]
demod_option = ["1", "2", "3", "4", "5", "6"]
demods_frame = LabelFrame(main_frame, bg=dark_gray_color,
                          fg=white_color, padx=0, pady=0, bd=0)
demods_frame.configure(background=dark_gray_color)
demods_frame.grid(row=3, column=0, columnspan=3, sticky=W)
add_count = 0


def Add_sample_fct():
    global demod_selected, demod_selection, sample_selected, sample_selection, demod_checkbox_state, demod_checkbox, current_row, add_count, demod_option, sample_option
    demod_selected.append(StringVar())
    demod_selected[add_count].set(demod_option[0])
    demod_selection.append(OptionMenu(
        demods_frame, demod_selected[add_count], *demod_option))
    demod_selection[add_count].configure(background=dark_gray_color, fg=accent_color,
                                         highlightbackground=dark_gray_color, highlightcolor=selected_color, bd=0, justify='center')
    demod_selection[add_count].grid(
        row=current_row+add_count, column=0, sticky=W)

    sample_selected.append(StringVar())
    sample_selected[add_count].set(sample_option[0])
    sample_selection.append(OptionMenu(
        demods_frame, sample_selected[add_count], *sample_option))
    sample_selection[add_count].configure(background=dark_gray_color, fg=accent_color,
                                          highlightbackground=dark_gray_color, highlightcolor=selected_color, bd=0, justify='center')
    sample_selection[add_count].grid(
        row=current_row+add_count, column=1, columnspan=3, sticky=W+N+E+S)
    add_count += 1


def Remove_sample_fct():
    global demod_selected, demod_selection, sample_selected, sample_selection, demod_checkbox_state, demod_checkbox, current_row, add_count, demod_option, sample_option
    if(add_count != 0):
        add_count -= 1
        demod_selected.pop(add_count)
        demod_selection[add_count].destroy()
        demod_selection.pop(add_count)
        sample_selected.pop(add_count)
        sample_selection[add_count].destroy()
        sample_selection.pop(add_count)


Add_sample_button = Button(demods_frame, text="  +  ", width=11, padx=0, pady=0, fg=white_color, bg=light_gray_color, bd=1,
                           highlightbackground=dark_gray_color, highlightcolor=selected_color, command=Add_sample_fct).grid(row=2, column=0, columnspan=2, sticky=N+S+E+W)
Remove_sample_button = Button(demods_frame, text="  -  ", width=8, padx=0, pady=0, fg=white_color, bg=light_gray_color, bd=1,
                              highlightbackground=dark_gray_color, highlightcolor=selected_color, command=Remove_sample_fct).grid(row=2, column=2, columnspan=2, sticky=N+S+E+W)
demod_text = Label(demods_frame, text="Demod", bg=dark_gray_color,
                   fg=white_color, justify='center').grid(row=3, column=0, sticky=W)
sample_text = Label(demods_frame, text="Sample", bg=dark_gray_color, fg=white_color,
                    justify='center').grid(row=3, column=1, columnspan=3, sticky=W+E)

demod_selected = []
demod_selection = []
sample_selected = []
sample_selection = []
demod_checkbox_state = []
demod_checkbox = []
current_row = 4

demod_selected.append(StringVar())
demod_selected[add_count].set(demod_option[0])
demod_selection.append(OptionMenu(
    demods_frame, demod_selected[add_count], *demod_option))
demod_selection[add_count].configure(background=dark_gray_color, fg=accent_color,
                                     highlightbackground=dark_gray_color, highlightcolor=selected_color, bd=0, justify='center')
demod_selection[add_count].grid(row=current_row+add_count, column=0, sticky=W)

sample_selected.append(StringVar())
sample_selected[add_count].set(sample_option[0])
sample_selection.append(OptionMenu(
    demods_frame, sample_selected[add_count], *sample_option))
sample_selection[add_count].configure(background=dark_gray_color, fg=accent_color,
                                      highlightbackground=dark_gray_color, highlightcolor=selected_color, bd=0, justify='center')
sample_selection[add_count].grid(
    row=current_row+add_count, column=1, columnspan=3, sticky=W+N+E+S)
add_count += 1
# endregion
# region GUI frames to draw
"""
Here we define the number of frames to draw.
Be carefull, if you input 0 than it will work in endless mode and scan with the microscope
"""
frames_to_draw_text = Label(settings_frame, text="Draw : ", bg=dark_gray_color, fg=white_color,
                            justify='center').grid(row=1, column=0, sticky=W)  # put text on the window
frames_to_draw_entry = Entry(settings_frame, bg=light_gray_color, width=7, fg=accent_color,
                             justify='center', highlightbackground="#2d2d30", highlightcolor=selected_color, bd=0)
frames_to_draw_entry.grid(row=1, column=1, columnspan=2, sticky=W+E)
# endregion
# region GUI Size Text And Entry
size_text = Label(settings_frame, text="Size : ", bg=dark_gray_color, fg=white_color,
                  justify='center').grid(row=2, column=0, sticky=W)  # put text on the window
size_entry = Entry(settings_frame, bg=light_gray_color, width=7, fg=accent_color,
                   justify='center', highlightbackground="#2d2d30", highlightcolor=selected_color, bd=0)
size_entry.grid(row=2, column=1, columnspan=2, sticky=W+E)
# endregion
# region GUI Frequency Text And Entry
frequency_text = Label(settings_frame, text="Freq : ", bg=dark_gray_color, fg=white_color,
                       justify='center').grid(row=3, column=0, sticky=W)  # put text on the window
frequency_entry = Entry(settings_frame, bg=light_gray_color, width=7, fg=accent_color,
                        justify='center', highlightbackground="#2d2d30", highlightcolor=selected_color, bd=0)
frequency_entry.grid(row=3, column=1, columnspan=2, sticky=W+E)
# endregion
# region GUI display modes
trace_mode_radio = IntVar()
trace_mode_text = Label(settings_frame, text="Display mode :", bg=dark_gray_color,
                        justify='left', fg=white_color).grid(row=4, column=0, columnspan=3, sticky=W)
Radiobutton(settings_frame, text="Trace", variable=trace_mode_radio, value=0, bg=dark_gray_color, fg=accent_color, justify='left',
            highlightbackground=dark_gray_color, highlightcolor=dark_gray_color).grid(row=5, column=0, columnspan=3, sticky=W)
Radiobutton(settings_frame, text="Retrace", variable=trace_mode_radio, value=1, bg=dark_gray_color, fg=accent_color, justify='left',
            highlightbackground=dark_gray_color, highlightcolor=dark_gray_color).grid(row=6, column=0, columnspan=3, sticky=W)
# endregion
# region GUI save image 
save_after_image_text = Label(
    save_frame, text="Save image", bg=dark_gray_color, fg=white_color, justify='left')
save_after_image_checkbox_state = IntVar()
save_after_image_checkbox = Checkbutton(
    save_frame, variable=save_after_image_checkbox_state)
save_after_image_checkbox.configure(background=dark_gray_color, fg=dark_gray_color,
                                    highlightbackground=dark_gray_color, highlightcolor=selected_color, bd=0)
def check_save_default(*args):
    if (not(save_to_gwy_checkbox_state.get())) and (not(save_to_txt_checkbox_state.get())):
        if(save_after_image_checkbox_state.get()):
            save_to_gwy_checkbox_state.set(1)


# endregion
# region GUI sample name + fieldnames
fieldname = ['custom_save_directory',
             'custom_save_directory_adress', 'sample_name']
logs_text.insert(
    'end', "- the current directory is : {} \n".format(current_directory))

def sample_name_fct(*args):
    global fieldname, current_directory
    if(os.path.isfile(current_directory+'/configs/configs.csv')):
        with open(current_directory+'/configs/configs.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(
                csv_file, fieldnames=fieldname, delimiter=',')
            csv_writer.writeheader()
            line = {fieldname[0]: '{}'.format(save_to_custom_folder_checkbox_state.get()), fieldname[1]: '{}'.format(
                save_to_custom_folder_entry.get()), fieldname[2]: '{}'.format(sample_name_entry.get())}
            csv_writer.writerow(line)
# endregion
# region GUI save to custom directory


def custom_save(*args):
    global fieldname, current_directory
    if(save_to_custom_folder_checkbox_state.get() != 0):
        if(os.path.isfile(current_directory+'/configs/configs.csv')):
            with open(current_directory+'/configs/configs.csv', 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for line in csv_reader:
                    custom_save_directory_adress = line['custom_save_directory_adress']
                if(custom_save_directory_adress == "None"):
                    root.directory = filedialog.askdirectory(
                        title="select a directory in which all the app data will be saved")  # ask directory
                    custom_save_directory_adress = root.directory
                    custom_save_directory_adress = str(
                        custom_save_directory_adress)
                    if((type(custom_save_directory_adress) == str) and (len(custom_save_directory_adress) > 2)):
                        save_to_custom_folder_entry.delete(first=0, last='end')
                        save_to_custom_folder_entry.insert(
                            INSERT, custom_save_directory_adress)
                        if(os.path.isdir(save_to_custom_folder_entry.get())):
                            if(os.path.isfile(current_directory+'/configs/configs.csv')):
                                with open(current_directory+'/configs/configs.csv', 'w') as csv_file:
                                    csv_writer = csv.DictWriter(
                                        csv_file, fieldnames=fieldname, delimiter=',')
                                    csv_writer.writeheader()
                                    line = {fieldname[0]: '{}'.format(save_to_custom_folder_checkbox_state.get()), fieldname[1]: '{}'.format(
                                        save_to_custom_folder_entry.get()), fieldname[2]: '{}'.format(sample_name_entry.get())}
                                    csv_writer.writerow(line)
                    else:
                        save_to_custom_folder_entry.delete(first=0, last='end')
                        save_to_custom_folder_entry.insert(INSERT, "None")
                if(os.path.isfile(current_directory+'/configs/configs.csv')):
                    with open(current_directory+'/configs/configs.csv', 'w') as csv_file:
                        csv_writer = csv.DictWriter(
                            csv_file, fieldnames=fieldname, delimiter=',')
                        csv_writer.writeheader()
                        line = {fieldname[0]: '{}'.format(save_to_custom_folder_checkbox_state.get()), fieldname[1]: '{}'.format(
                            save_to_custom_folder_entry.get()), fieldname[2]: '{}'.format(sample_name_entry.get())}
                        csv_writer.writerow(line)
        save_to_custom_folder_entry.configure(bg='#333333', fg=accent_color)
    else:
        if(os.path.isfile(current_directory+'/configs/configs.csv')):
            with open(current_directory+'/configs/configs.csv', 'w') as csv_file:
                csv_writer = csv.DictWriter(
                    csv_file, fieldnames=fieldname, delimiter=',')
                csv_writer.writeheader()
                line = {fieldname[0]: '{}'.format(save_to_custom_folder_checkbox_state.get()), fieldname[1]: '{}'.format(
                    save_to_custom_folder_entry.get()), fieldname[2]: '{}'.format(sample_name_entry.get())}
                csv_writer.writerow(line)
        save_to_custom_folder_entry.configure(bg='#222222', fg='#f1f1f1')


save_to_custom_folder_text = Label(
    save_frame, text="Save to custom dir", bg=dark_gray_color, fg=white_color, justify='left')
save_to_custom_folder_checkbox_state = IntVar()
save_to_custom_folder_checkbox = Checkbutton(
    save_frame, variable=save_to_custom_folder_checkbox_state)
save_to_custom_folder_checkbox.configure(background=dark_gray_color, fg=dark_gray_color,
                                         highlightbackground=dark_gray_color, highlightcolor=selected_color, bd=0)

sample_name_var = StringVar()
sample_name_text = Label(save_frame, text="Sample :", bg=dark_gray_color,
                         fg=white_color, justify='center')  # put text on the window
sample_name_entry = Entry(save_frame, width=10, bg=light_gray_color, fg=accent_color, justify='center',
                          highlightbackground="#2d2d30", highlightcolor=selected_color, bd=0, textvariable=sample_name_var)

save_to_custom_folder_entry = Entry(save_frame, width=19, bg=light_gray_color, fg=accent_color,
                                    justify='center', highlightbackground="#2d2d30", highlightcolor=selected_color, bd=0)

if(os.path.isfile(current_directory+'/configs/configs.csv')):
    with open(current_directory+'/configs/configs.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            custom_save_directory = line['custom_save_directory']
            custom_save_directory_adress = line['custom_save_directory_adress']
            sample_name = line['sample_name']
        sample_name_entry.insert(INSERT, sample_name)
        save_to_custom_folder_checkbox_state.set(custom_save_directory)
        

        if(custom_save_directory_adress != '0'):
            save_to_custom_folder_entry.delete(first=0, last='end')
            save_to_custom_folder_entry.insert(
                INSERT, custom_save_directory_adress)
            logs_text.insert('end', "   found custom save adress : {} \n".format(
                custom_save_directory_adress))
        else:
            save_to_custom_folder_entry.delete(first=0, last='end')
            save_to_custom_folder_entry.insert(INSERT, "None")
    logs_text.insert('end',"- found in configs/configs\n   custom directory = {}\n   adress = {}\n   sample name = {}\n".format(save_to_custom_folder_checkbox_state.get(), save_to_custom_folder_entry.get(), sample_name_entry.get()))  
else:
    save_to_custom_folder_checkbox_state.set(0)
    save_to_custom_folder_entry.delete(first=0, last='end')
    save_to_custom_folder_entry.insert(INSERT, "None")
if(custom_save_directory == '0'):
    save_to_custom_folder_entry.configure(bg='#222222', fg='#444444')
else:
    save_to_custom_folder_entry.configure(bg='#333333', fg='#007ACC')

save_to_custom_folder_text.grid(row=2, column=0, columnspan=2, sticky=W)
save_to_custom_folder_checkbox.grid(row=2, column=2, sticky=W)

save_to_custom_folder_entry.grid(row=3, column=0, columnspan=2, sticky=W+N+S)

save_after_image_text.grid(row=1, column=0, columnspan=2, sticky=W)
save_after_image_checkbox.grid(row=1, column=2, sticky=W)

sample_name_text.grid(row=0, column=0, sticky=W)
sample_name_entry.grid(row=0, column=1, columnspan=2, sticky=W)

sample_name_var.trace("w", sample_name_fct)
save_to_custom_folder_checkbox_state.trace("w", custom_save)
# endregion
# region GUI button to Ask directory


def askdir():
    global fieldname, current_directory
    root.directory = filedialog.askdirectory(
        title="select a directory in which all the app data will be saved")  # ask directory
    custom_save_directory_adress = root.directory
    custom_save_directory_adress = str(custom_save_directory_adress)
    logs_text.insert(
        'end', "- you selected : {} as the custom save directory\n".format(custom_save_directory_adress))
    if len(custom_save_directory_adress) > 2:
        pass
    else:
        custom_save_directory_adress = "None"
    save_to_custom_folder_entry.delete(first=0, last='end')
    save_to_custom_folder_entry.insert(
        INSERT, str(custom_save_directory_adress))
    if(os.path.isfile(current_directory+'/configs/configs.csv')):
        with open(current_directory+'/configs/configs.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(
                csv_file, fieldnames=fieldname, delimiter=',')
            csv_writer.writeheader()
            line = {fieldname[0]: '{}'.format(save_to_custom_folder_checkbox_state.get()), fieldname[1]: '{}'.format(
                save_to_custom_folder_entry.get()), fieldname[2]: '{}'.format(sample_name_entry.get())}
            csv_writer.writerow(line)


askdir_button = Button(save_frame, text=" ... ", padx=0, pady=0, fg=white_color, bg=light_gray_color,
                       bd=1, highlightbackground=dark_gray_color, highlightcolor=selected_color, command=askdir)
askdir_button.grid(row=3, column=2, sticky=W+N)
# endregion
# region GUI choose the graphs color (CMAP)
img = {}
"""
Here you can add more color options, however they will not have the previsualisation
the other colors can be found here :
https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html
"""
cmap_option = ["viridis", "inferno", "hot", "cool", "coolwarm", "tab20", "jet"]
default_save = '/saved_data/'


def change_image(*args):
    global img
    cmap = cmap_selected.get()
    cmap_selection.configure(bg=dark_gray_color)
    if(len(img) > 0):
        try :
            cmap_selection.configure(image=img[cmap], fg=accent_color, highlightbackground=dark_gray_color,highlightcolor=selected_color, bd=0, justify='center')
        except :
            pass

for cmap in cmap_option:
    img_adress = '{}/colors/{}.png'.format(current_directory, cmap)
    if os.path.isfile(img_adress):
        img[cmap] = (ImageTk.PhotoImage(Image.open(img_adress)))
cmap_text = Label(settings_frame, text="color : ", bg=dark_gray_color, fg=white_color,
                  justify='center').grid(row=7, column=0, sticky=W)  # put text on the window
cmap_selected = (StringVar())
cmap_selected.trace("w", change_image)
cmap_selection = OptionMenu(settings_frame, cmap_selected, *cmap_option)
cmap_selection.grid(row=7, column=1, columnspan=3, sticky=W)
# endregion
# region GUI display the frequency delta
frequency_delta_text = Label(toolbar_frame, text="", bg=dark_gray_color,
                         fg=white_color, justify='center')  # put text on the window
frequency_delta_text.pack(side=RIGHT, fill=BOTH)
#endregion
# region Animation part 1
line_number = 0
frame_vertical_trace = 0  # 0 is top to bottom, 1 is bottom to top
right_to_plot = 0
frames_drawn = 0
initialized = 0
size = None
stoped = 1
trace_names = ['trace', 'retrace']
EOF = 0
min_r = {}
max_r = {}
first_range = 0
flip=0

def animate(i):
    global line_number, im, signal_paths, data, size, frame_vertical_trace, frames_drawn, right_to_plot, current_directory, default_save, stoped, initialized, trace_names, end_of_line, end_of_frame, EOF, min_r, max_r, first_range, frequency_index
    if(stoped == 0):  # if the program is supposed tu be running
        data_read = daq_module.read(True)  # read the sampling information
        if(frames_drawn == 0) and (line_number == 0):  # if we wait for End of Frame trigger
            # check if we received and EOF trigger @
            EOF_trigger = daq_module.get("triggered")
            EOF_dict = EOF_trigger['triggered']
            EOF = EOF_dict[0]
            if EOF != 0:  # if we received EOF trigger
                # what is the current trigger node ?
                trigger_node = daq_module.get("triggernode")
                trigger_node = trigger_node['triggernode'][0]
                # if the trigger node is not EOL
                if(trigger_node != '/{}/demods/0/sample{}'.format(device, end_of_line)):
                    # set triggernode to EOL
                    daq_module.set("triggernode", dev_adress +'/demods/0/sample'+end_of_line)
                    logs_text.insert('end', "- has aquired EOF trigger, switching to EOL trigger\n")  # print it
                    first_range = 1
        if (data_read) and (right_to_plot != 0):  # if we have received data and we are not paused
            now = datetime.now()
            current_time = now.strftime("%Hh-%Mm-%Ss")
            # if the data we want is in the returned signals
            returned_signal_paths = [signal_path.lower()for signal_path in data_read.keys()]
            graph_to_update_number = 1
            sample_loss = 0
            delta_text=""
            sample_loss_indexs = []
            for signal_path in signal_paths:  # for every signal we want to plot
                if signal_path.lower() in returned_signal_paths:
                    for index, signal_burst in enumerate(data_read[signal_path.lower()]):
                        value = signal_burst['value'][0, :]
                        for index in range(0, len(value)):
                            if np.isnan(value[index]):
                                sample_loss += 1
                                sample_loss_indexs.append(index)
                        if sample_loss != 0:
                            logs_text.insert('end', "there has been {} sample(s) lost in line {}\n".format(
                                sample_loss, line_number))
                        if first_range!= 0:
                            min_r[signal_path] = np.nanmin(value)
                            max_r[signal_path] = np.nanmax(value)
                            if signal_path==signal_paths[(len(signal_paths)-1)]:
                                first_range=0
                        else:
                            prev = min_r[signal_path]
                            min_r[signal_path] = np.nanmin(value)
                            if min_r[signal_path] < prev:
                                pass
                            else:
                                min_r[signal_path] = prev
                            prev = max_r[signal_path]
                            max_r[signal_path] = np.nanmax(value)
                            if max_r[signal_path] > prev:
                                pass
                            else:
                                max_r[signal_path] = prev
                        min = min_r[signal_path]
                        max = max_r[signal_path]

                        # fill the corresponding line in the matrix
                        data[signal_path][line_number] = value[:]
                        data_splited = np.hsplit(data[signal_path], 2)
                        data_trace = data_splited[trace_mode_radio.get()]
                        if trace_mode_radio.get() == 0:
                            data_trace = np.fliplr(data_trace)
                        if flip:
                            data_trace = np.flipud(data_trace)
                        
                        if len(frequency_index):
                            for index in frequency_index:
                                if graph_to_update_number-1 == index:
                                    delta = max-min
                                    delta_text=str(delta_text+("   delta freq graph n°{} = {:.2f}hz   ".format((index+1), delta)))
                            frequency_delta_text.configure(text=delta_text)
                        # update plot with trace or retrace
                        im[graph_to_update_number].set_data(data_trace)
                        im[graph_to_update_number].set_clim(min, max)  # set the colorbar range
                    graph_to_update_number += 1
            actual_size = size_entry.get()
            if(frame_vertical_trace == 0) and ((graph_to_update_number-1) == len(signal_paths)):
                frames_to_show = frames_drawn+1
                line_number += 1

            elif(frame_vertical_trace != 0) and ((graph_to_update_number-1) == len(signal_paths)):
                line_number_to_show = int(actual_size)-line_number
                frames_to_show = frames_drawn+1
                line_number -= 1
            else:
                pass
#endregion
# region Save image 
            # here we save the data if we reach the bottom or top of the image
            if(line_number == (size)) or (line_number < 0):
                """
                Here we're saving both trace and retrace as opposed to the plotting part which only displays one
                the File is called : curent time + sample name + signal path + frame number + trace or retrace
                the file is saved as a Gwyddyon file and the directory can be :
                - a custom set one
                - the default with is current directory + saved data
                - the current one
                """
                frame_vertical_trace = not(frame_vertical_trace)
                frames_drawn += 1
                if(save_after_image_checkbox_state.get() != 0):
                    now = datetime.now()
                    day_time_sample = now.strftime("%H-%M-%S")
                    for signal_path in signal_paths:
                        data_to_save = np.hsplit(data[signal_path], 2)
                        if(flip):
                            data_to_save=np.flipud(data_to_save)
                        for index in range(0, 2):
                            saved_signal_path = signal_path.replace('/', ' ')
                            saved_signal_path = saved_signal_path.replace(
                                '.', ',')
                            file_name = str('{} ; {} ; {} ; frame {} {}'.format(day_time_sample, sample_name_var.get(), saved_signal_path, (frames_drawn+1), trace_names[index]))
                            if save_to_gwy_checkbox_state.get():
                                obj = GwyContainer()
                                obj['/0/data/title'] = file_name
                                data_to_gwy = data_to_save[index]
                                obj['/0/data'] = GwyDataField(data_to_gwy)
                            now = datetime.now()
                            day_time = now.strftime("%Y-%m-%d")   
                            if(save_to_custom_folder_checkbox_state.get() == 0):
                                save_adress = current_directory+default_save
                                save_adress = save_adress+'/'+day_time
                                if not os.path.isdir(save_adress):
                                    os.mkdir(save_adress)
                                if(os.path.isdir(save_adress)):
                                    save_adress = save_adress+'/'+file_name+'.gwy'
                                else:
                                    logs_text.insert(
                                        'end', "- default path does not exist saving to current directory instead \n")
                                    save_adress = current_directory+'/'+file_name+'.gwy'
                            else:
                                save_adress = save_to_custom_folder_entry.get()
                                if os.path.isdir(save_adress):
                                    save_adress = save_adress+'/'+day_time
                                    if not os.path.isdir(save_adress):
                                        os.mkdir(save_adress)
                                    if(os.path.isdir(save_adress)):
                                        save_adress = save_adress+'/'+file_name+'.gwy'
                                else:
                                    logs_text.insert(
                                        'end', "- save path does not exist, saving to default path \n")
                                    save_adress = current_directory+default_save
                                    save_adress = save_adress+'/'+day_time
                                    if not os.path.isdir(save_adress):
                                        os.mkdir(save_adress)
                                    if(os.path.isdir(save_adress)):
                                        save_adress = save_adress+'/'+file_name+'.gwy'
                                    else:
                                        logs_text.insert(
                                            'end', "- default path does not exist saving to current directory instead \n")
                                        save_adress = current_directory+'/'+file_name+'.gwy'        
                            if save_to_gwy_checkbox_state.get(): 
                                obj.tofile(save_adress)
                            if save_to_txt_checkbox_state.get():
                                data_to_txt=data_to_save[index]
                                save_adress=save_adress.replace('.gwy','.csv')
                                with open(save_adress, 'w') as csv_file:
                                    np.savetxt(save_adress,data_to_txt, delimiter=',')
                                        
                            now = datetime.now()
                            current_time = now.strftime("%Hh-%Mm-%Ss")
                            logs_text.insert(
                                'end', "- saved data at adress {} at {}\n".format(save_adress, current_time))
#endregion
# region Animation part 2
                if(frame_vertical_trace == 0):
                    line_number += 1
                else:
                    line_number -= 1
            if int(frames_to_draw_entry.get()) != 0:
                if(frames_drawn == int(frames_to_draw_entry.get())):
                    stoped = 1
                    daq_module.finish()
                    now = datetime.now()
                    current_time = now.strftime("%Hh-%Mm-%Ss")
                    logs_text.insert(
                        'end', "- all the frames have been drawn, sampling process has been stoped at {}\n".format(current_time))
                    initialized = 0
                    frame_vertical_trace = 0
                    frames_drawn = 0
                    line_number = 0

# endregion
# region GUI start button + Checking variables befor launching
first_launch = 1

def check_fct():
    global fig, size_min_limit, size_max_limit, frequency_min_limit, frequency_max_limit, launch, size, right_to_plot, initialized, ani, stoped, first_launch, connected, end_of_line, end_of_frame, frequency_index
    if(initialized == 0):
        now = datetime.now()
        current_time = now.strftime("%Hh-%Mm-%Ss")
        logs_text.insert(
            'end', "- the sampling process is being initialized ... at {}\n".format(current_time))
        size = int(size_entry.get())
        if (size <= size_min_limit):
            logs_text.insert(
                'end', "- the image size is too low. The application does not support it, however you can manually change the bottom limit in the program script \n")
            launch = 0
            size_entry.configure(
                highlightbackground="#aa2222", highlightcolor="#aa2222")
        elif (size > size_max_limit):
            logs_text.insert(
                'end', "- The image size is too high. The application does not support it, however you an manually change the upper limit in the program script \n")
            launch = 0
            size_entry.configure(
                highlightbackground="#aa2222", highlightcolor="#aa2222")
        else:
            launch = 1
            size_entry.configure(highlightbackground="#2d2d30",
                                 highlightcolor=selected_color)
        frequency = float(frequency_entry.get())
        if (frequency < frequency_min_limit):
            logs_text.insert(
                'end', "- the line sacnning frequency is too low. The application does not support it, however you an manually change the upper limit in the program script \n")
            launch = 0
            frequency_entry.configure(
                highlightbackground="#aa2222", highlightcolor="#aa2222")
        elif (frequency > frequency_max_limit):
            logs_text.insert(
                'end', "- The line sacnning frequency is too high. The application does not support it, however you an manually change the upper limit in the program script \n")
            launch = 0
            frequency_entry.configure(
                highlightbackground="#aa2222", highlightcolor="#aa2222")
        else:
            frequency_entry.configure(
                highlightbackground="#2d2d30", highlightcolor=selected_color)
            if launch != 0:
                launch = 1
        # IF THE SETTINGS ARE CORRECT
        if(launch != 0 and connected != 0):
            logs_text.insert(
                'end', "- all the settings are correct, launching the program \n")
            # empty the current adress list befor re launching
            for signal_path in range(0, len(signal_paths)):
                signal_paths.pop(0)
            for index in range(0, len(frequency_index)):
                frequency_index.pop(0)
            size_entry.configure(bg="#222222", fg=light_gray_color)
            frequency_entry.configure(bg="#222222", fg=light_gray_color)
            for signal_number in range(0, add_count):
                demod_number = (int(demod_selected[signal_number].get()))-1
                demod_adress = '/demods/{}'.format(demod_number)
                sample_number = sample_selected[signal_number].get()
                if sample_number == sample_option[2]:
                    for index in range(0, 2):
                        sample_number = sample_option[index]
                        sample_adress = '/sample.{}'.format(sample_number)
                        signal_path = dev_adress+demod_adress+sample_adress
                        signal_paths.append(signal_path)
                else:
                    sample_adress = '/sample.{}'.format(sample_number)
                    signal_path = str(dev_adress+demod_adress+sample_adress)
                    if sample_number == 'frequency':
                        frequency_index.append(len(signal_paths))
                    signal_paths.append(signal_path)

            signals_to_plot = len(signal_paths)
            if signals_to_plot > 9:
                ratio = 4
            else:
                ratio = 3
            logs_text.insert(
                'end', "- the signal paths are : {} \n".format(signal_paths))
            rows = int(np.ceil(signals_to_plot/ratio))
            columns = int(np.ceil(signals_to_plot/rows))
            trace_mode = trace_mode_radio.get()
            cmap = cmap_selected.get()
            for signal_number in signal_paths:
                daq_module.subscribe(signal_number)
                data[signal_number] = np.empty(shape=(size, 2*size))
                data[signal_number][:] = np.nan
                min_r[signal_number] = 0
                max_r[signal_number] = 0
            # INIT
            T = 1/frequency  # time to draw a line (trace + retrace time)
            # Time in seconds for each data burst/segment.
            burst_duration = (T-1e-7)
            holdoff_time = burst_duration*0.75
            num_cols = int(size*2)
            if(int(frames_to_draw_entry.get()) != 0):
                lines_to_draw = int(int(frames_to_draw_entry.get())*size)
                real_duration = lines_to_draw*T
                total_duration = real_duration*2  # time to draw a frame
                num_bursts = int(total_duration/burst_duration)
                daq_module.set("device", device)
                daq_module.set('type', 0)  # 0 for continious 6 for trigged
                daq_module.set("grid/mode", 2)
                daq_module.set("count", num_bursts)
            else:
                daq_module.set("device", device)
                daq_module.set('type', 6)  # 0 for continious 6 for trigged
                daq_module.set("grid/mode", 2)
                daq_module.set("edge", 1)  # falling edge
                daq_module.set("endless", 1)
                # trigger always on first demod @
                daq_module.set("triggernode", dev_adress +'/demods/0/sample'+end_of_frame)

            daq_module.set("duration", burst_duration)
            daq_module.set("grid/cols", num_cols)
            daq_module.set("clearhistory", 1)
            daq_module.set("holdoff/time", holdoff_time)
            if((manual_sample_freq_checkbox_state.get()!= 0) and (advanced_checkbox_state.get()!= 0)):
                pass
            else:
                try:
                    high_rate = 230000
                    low_rate = 1800
                    daq.setDouble(dev_adress+'/demods/0/rate', high_rate)
                    logs_text.insert(
                        'end', '- demods n°0 rate has been set too {}\n'.format(high_rate))
                    for index in range(1, 6):
                        daq.setDouble(
                            dev_adress+'/demods/{}/rate'.format(index), low_rate)
                        logs_text.insert(
                            'end', '- demods n°{} rate has been set too {}\n'.format(index, low_rate))
                except:
                    too_low = 0
                    too_high = 0
                    logs_text.insert(
                        'end', "Couldn't change demods sampling rate !!\n")
                    high_rate = daq.getDouble(dev_adress+'/demods/0/rate')
                    if high_rate < 145000:
                        too_low = 1
                    for index in range(1, 6):
                        low_rate = daq.getDouble(
                            dev_adress+'/demods/{}/rate'.format(index))
                        if low_rate > 9000:
                            too_high = 1
                    if(too_low or too_high):
                        message = ''
                        if too_low:
                            message = '. The sampling rate of Demod 1 is too low, you risk missing triggers please use 230kSa/s'
                        if too_high:
                            message = message+'. The sampling rate of the Demods 2 too 6 are too high please use 1,8kSa/s or 9kSa/s max'
                        MsgBox_rate = tk.messagebox.showwarning(
                            'Warning', 'the sampling rates are Wrong{}'.format(message), icon='warning')
            initialized = 1
            stoped = 0
            blank_image = np.empty(shape=(size, size))
            blank_image[:] = np.nan
            plt.clf()
            fig.tight_layout(pad=3)
            fig.set_tight_layout(True)
            for i in range(1, len(signal_paths)+1):
                ax = fig.add_subplot(rows, columns, i)
                tittle = str(signal_paths[i-1])
                tittle = tittle.replace(dev_adress, '')
                tittle = tittle.replace('/', ' ')
                tittle = tittle.replace('.', ' ')
                number_in_adress = [int(s)
                                    for s in tittle.split() if s.isdigit()]
                number_in_adress = number_in_adress[0]
                number_to_display = number_in_adress+1
                tittle = tittle.replace(
                    str(number_in_adress), str(number_to_display))
                ax.set_title(tittle, fontsize=12, family="sans-serif",
                             color='#f1f1f1', fontweight="bold")
                ax.tick_params(axis='x', colors='#f1f1f1')
                ax.tick_params(axis='y', colors='#f1f1f1')
                ax.spines['bottom'].set_color('#f1f1f1')
                ax.spines['top'].set_color('#f1f1f1')
                ax.spines['right'].set_color('#f1f1f1')
                ax.spines['left'].set_color('#f1f1f1')
                im[i] = plt.imshow(blank_image, cmap=cmap, interpolation=None)
                cb = plt.colorbar(format='%.2e')
                cb.set_label('Range', color='#f1f1f1',
                             fontsize=12, family="sans-serif")
                cb.ax.yaxis.set_tick_params(color='#f1f1f1')
                cb.ax.xaxis.set_tick_params(color='#f1f1f1')
                cb.outline.set_edgecolor('#f1f1f1')
                plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='#f1f1f1')
                right_to_plot = 1
                ani = animation.FuncAnimation(
                    plt.gcf(), animate, interval=T*500)
                if first_launch != 0:
                    canvas_widget.grid(row=0, column=0, sticky=N+S+W+E)
                    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                    toolbar.config(background=white_color, bd=0)
                    toolbar._message_label.config(background=white_color)
                    for button in toolbar.winfo_children():
                        button.config(background=white_color, bd=0)
                    first_launch = 0
                else:
                    right_to_plot = 1
                daq_module.execute()
                now = datetime.now()
                current_time = now.strftime("%Hh-%Mm-%Ss")
                logs_text.insert(
                    'end', "- sampling module has been started at {} triggering on EOF\n".format(current_time))
                logs_text.insert('end', "- all the plots have initialized \n")
        else:
            pass
    else:
        right_to_plot = 1


Start_button = Button(controls_frame, text="        START      ", padx=0, pady=0, fg=start_color, bg=light_gray_color,
                      bd=1, highlightbackground=dark_gray_color, highlightcolor=selected_color, command=check_fct)
Start_button.grid(row=6, column=0, columnspan=3, sticky=S+W+E)
# endregion
# region GUI pause


def pause():
    global right_to_plot
    right_to_plot = not right_to_plot
    if (right_to_plot != 0):
        pause_button.configure(bg=light_gray_color)
    else:
        pause_button.configure(bg="#222222")


pause_button = Button(controls_frame, width=8, text="Pause", padx=0, pady=0, fg=white_color, bg=light_gray_color,
                      bd=1, highlightbackground=dark_gray_color, highlightcolor=selected_color, command=pause)
pause_button.grid(row=5, column=3, sticky=W+N+E)
# endregion
# region GUI stop


def stop():
    global initialized, right_to_plot, signal_paths, data, daq_module, stoped, line_number, frame_vertical_trace, frames_drawn
    if stoped == 0:
        MsgBox = tk.messagebox.askquestion(
            'Warning', 'Are you sure you want to Stop the process ?', icon='warning')
        if (MsgBox == 'yes'):
            try:
                daq_module.finish()
            except:
                logs_text.insert(
                    'end', "- DAQ module does not exist, thus it can't be stopped")
            else:
                initialized = 0
                frame_vertical_trace = 0
                frames_drawn = 0
                line_number = 0
                stoped = 1
                now = datetime.now()
                current_time = now.strftime("%Hh-%Mm-%Ss")
                logs_text.insert(
                    'end', "- sampling process has been stoped at {}\n".format(current_time))
                    
                if(save_after_image_checkbox_state.get() != 0):
                    now = datetime.now()
                    day_time_sample = now.strftime("%H-%M-%S")
                    for signal_path in signal_paths:
                        data_to_save = np.hsplit(data[signal_path], 2)
                        if(flip):
                            data_to_save=np.flipud(data_to_save)
                        for index in range(0, 2):
                            saved_signal_path = signal_path.replace('/', ' ')
                            saved_signal_path = saved_signal_path.replace(
                                '.', ',')
                            file_name = str('{} ; {} ; {} ; frame {} {}'.format(day_time_sample, sample_name_var.get(), saved_signal_path, (frames_drawn+1), trace_names[index]))
                            if save_to_gwy_checkbox_state.get():
                                obj = GwyContainer()
                                obj['/0/data/title'] = file_name
                                data_to_gwy = data_to_save[index]
                                obj['/0/data'] = GwyDataField(data_to_gwy)
                            now = datetime.now()
                            day_time = now.strftime("%Y-%m-%d")   
                            if(save_to_custom_folder_checkbox_state.get() == 0):
                                save_adress = current_directory+default_save
                                save_adress = save_adress+'/'+day_time
                                if not os.path.isdir(save_adress):
                                    os.mkdir(save_adress)
                                if(os.path.isdir(save_adress)):
                                    save_adress = save_adress+'/'+file_name+'.gwy'
                                else:
                                    logs_text.insert(
                                        'end', "- default path does not exist saving to current directory instead \n")
                                    save_adress = current_directory+'/'+file_name+'.gwy'
                            else:
                                save_adress = save_to_custom_folder_entry.get()
                                if os.path.isdir(save_adress):
                                    save_adress = save_adress+'/'+day_time
                                    if not os.path.isdir(save_adress):
                                        os.mkdir(save_adress)
                                    if(os.path.isdir(save_adress)):
                                        save_adress = save_adress+'/'+file_name+'.gwy'
                                else:
                                    logs_text.insert(
                                        'end', "- save path does not exist, saving to default path \n")
                                    save_adress = current_directory+default_save
                                    save_adress = save_adress+'/'+day_time
                                    if not os.path.isdir(save_adress):
                                        os.mkdir(save_adress)
                                    if(os.path.isdir(save_adress)):
                                        save_adress = save_adress+'/'+file_name+'.gwy'
                                    else:
                                        logs_text.insert(
                                            'end', "- default path does not exist saving to current directory instead \n")
                                        save_adress = current_directory+'/'+file_name+'.gwy'        
                            if save_to_gwy_checkbox_state.get(): 
                                obj.tofile(save_adress)
                            if save_to_txt_checkbox_state.get():
                                data_to_txt=data_to_save[index]
                                save_adress=save_adress.replace('.gwy','.csv')
                                with open(save_adress, 'w') as csv_file:
                                    np.savetxt(save_adress,data_to_txt, delimiter=',')
                                        
                            now = datetime.now()
                            current_time = now.strftime("%Hh-%Mm-%Ss")
                            logs_text.insert(
                                'end', "- saved data at adress {} at {}\n".format(save_adress, current_time))
                plt.clf()
                # empty the current adress list befor re launching
                for signal_path in range(0, len(signal_paths)):
                    signal_paths.pop(0)
                size_entry.configure(bg=light_gray_color, fg=accent_color)
                frequency_entry.configure(bg=light_gray_color, fg=accent_color)
        else:
            pass


stop_button = Button(controls_frame, text=" STOP ", padx=0, pady=0, fg=white_color, bg=light_gray_color,
                     bd=1, highlightbackground=dark_gray_color, highlightcolor=selected_color, command=stop)
stop_button.grid(row=6, column=3, sticky=W+S+E)
# endregion
# region GUI reset button


def refresh():
    global right_to_plot, signal_paths, data, daq_module, line_number, frames_drawn, frame_vertical_trace, stoped
    right_to_plot = 0
    for signal_path in signal_paths:
        data[signal_path] = np.empty(shape=(size, 2*size))
        data[signal_path][:] = np.nan
    line_number = 0
    frame_vertical_trace = 0
    frames_drawn = 0
    daq_module.set("triggernode", dev_adress+'/demods/0/sample' +
                   end_of_frame)  # trigger always on first demod
    logs_text.insert(
        'end', "- has changed trigger source from EOL to EOF trigger \n")
    right_to_plot = 1
    logs_text.insert('end', "- data and plots have been cleared\n")


refresh_button = Button(controls_frame, text="Reset", padx=0, pady=0, fg=white_color, bg=light_gray_color,
                        bd=1, highlightbackground=dark_gray_color, highlightcolor=selected_color, command=refresh)
refresh_button.grid(row=5, column=0, columnspan=3, sticky=W+N+E)
# endregion
# region GUI Up down dirrection
def up_down():
    global frame_vertical_trace, line_number
    frame_vertical_trace = not frame_vertical_trace

    if frame_vertical_trace == 0:
        direction_text = "Up-Down"
        up_down_button.configure(text=direction_text)
        if EOF == 0:
            line_number = 0
    else:
        direction_text = "Down-up"
        up_down_button.configure(text=direction_text)
        if EOF == 0:
            line_number = int(size_entry.get())-1
    logs_text.insert('end', "- line scanning direction has been set to : {} {} {}\n".format(
        direction_text, frame_vertical_trace, line_number))

def flip_matrix():
    global flip
    flip=not(flip)
    if flip:  
        logs_text.insert('end', "- Matrix will now be flipped\n")
        flip_button.configure(bg=dark_gray_color)
    else:
        logs_text.insert('end', "- Matrix will now be at normal state\n")
        flip_button.configure(bg=light_gray_color) 
up_down_button = Button(settings_frame, padx=0, pady=0, fg=white_color, bg=light_gray_color,bd=1, highlightbackground=dark_gray_color, highlightcolor=selected_color, command=up_down)
flip_button = Button(settings_frame,text='Flip',width=7, padx=0, pady=0, fg=white_color, bg=light_gray_color,bd=1, highlightbackground=dark_gray_color, highlightcolor=selected_color, command=flip_matrix)
if frame_vertical_trace == 0:
    up_down_button.configure(text="Up-Down")
else:
    up_down_button.configure(text="Down-up")
up_down_button.grid(row=0, column=0, columnspan=3, sticky=W+N+E)
flip_button.grid(row=0, column=3, sticky=W+N+E)
# endregion
# region read the values stored between each launch
if(os.path.isfile(current_directory+'/configs/entries.csv')):
    with open(current_directory+'/configs/entries.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            frames_to_draw_entry.insert('end',line['draw']) 
            size_entry.insert('end',line['size'])
            frequency_entry.insert('end', line['freq'])
            trace_mode_radio.set(line['trace_mode'])
            cmap_selected.set(line['color'])
            save_after_image_checkbox_state.set(line['save_after_image'])
    logs_text.insert('end',"- found in configs/entries\n   frames_to_draw = {}\n   size = {}\n   frequency = {}\n   trace mode = {}\n   color = {}\n   save image = {}\n".format(frames_to_draw_entry.get(), size_entry.get(), frequency_entry.get(), trace_mode_radio.get(), cmap_selected.get(), save_after_image_checkbox_state.get()))  
#endregion
# region HF2LI detection and Connecxion
hostname = 'localhost'
port = 8005
api_level = 1
daq = None
device = None
dev_adress = None
daq_module = None
connected = 0


def connect_me():
    global hostname, port, api_level, daq, device, dev_adress, daq_module, connected
    if(connected == 0):
        if(advanced_checkbox_state.get() != 0):
            hostname = str(hostname_entry.get())
            port = int(port_entry.get())
        try:
            daq = zhinst.ziPython.ziDAQServer(hostname, port, api_level)
        except:
            logs_text.insert(
                'end', "- couldn't start DAQ Server with 'localhost' and port 8005, verify that LabOne is running\n")
        else:
            logs_text.insert(
                'end', "- DAQ Server has been started with hostname : {}, port : {}, api level : {} \n".format(hostname, port, api_level))
        try:
            device = zhinst.utils.autoDetect(daq)
        except:
            logs_text.insert(
                'end', "- No device has been detected, make sure that the device is connected via USB or Ethernet\n")
        else:
            logs_text.insert(
                'end', "- Connected to device : {} \n".format(device))
            (daq, device, _) = zhinst.utils.create_api_session(device, api_level)
            zhinst.utils.api_server_version_check(daq)
            dev_adress = '/{}'.format(device)
            flags = ziListEnum.recursive | ziListEnum.absolute | ziListEnum.streamingonly
            streaming_nodes = daq.listNodes(
                '/{}'.format(device), flags)  # not necessary
            daq_module = daq.dataAcquisitionModule()
            connected = 1
            connect_button.configure(bg=accent_color)
            now = datetime.now()
            current_time = now.strftime("%Hh-%Mm-%Ss")
            logs_text.insert(
                'end', "- Started Data Acquisition Module at {} \n".format(current_time))
            logs_text.insert('end', "Device ready for biscotte beuration\n")
    else:
        daq.disconnect()
        connect_button.configure(bg="#eaa100")
        connected = 0
# endregion
# region GUI Connection + Advanced settings
def check_save(*args):
    if (not(save_to_gwy_checkbox_state.get())) and (not(save_to_txt_checkbox_state.get())):
        save_after_image_checkbox_state.set(0)
        MsgBox = tk.messagebox.showwarning(
            'Warning', 'if you uncheck both fields data will not be saved !', icon='warning')
    else:
        save_after_image_checkbox_state.set(1)
    
            
connexion_fieldnames = ['connect_at_start', 'advanced', 'manual_freq','save_to_gwy','save_to_txt']
connect_button = Button(configuration_frame, width=11, text="Connect", padx=3, pady=3, fg=dark_gray_color,
                        bg=connect_color, bd=1, highlightbackground=dark_gray_color, highlightcolor=selected_color, command=connect_me)
advanced_checkbox_state = IntVar()
advanced_text = Label(configuration_frame, text="Advanced settings", fg=white_color, bg=dark_gray_color,
                      bd=0, highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='left')
advanced_checkbox = Checkbutton(configuration_frame, fg=dark_gray_color, bg=dark_gray_color, bd=0,
                                highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='center', variable=advanced_checkbox_state)
autoconnect_checkbox_state = IntVar()
autoconnect_text = Label(connexion_frame, text="Connect at launch", fg=white_color, bg=dark_gray_color,
                         bd=0, highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='left')
autoconnect_checkbox = Checkbutton(connexion_frame, fg=dark_gray_color, bg=dark_gray_color, bd=0,
                                   highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='center', variable=autoconnect_checkbox_state)
manual_sample_freq_checkbox_state = IntVar()
manual_sample_freq_text = Label(connexion_frame, text="Manual Sampling rate", fg=white_color, bg=dark_gray_color,
                         bd=0, highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='left')
manual_sample_freq_checkbox = Checkbutton(connexion_frame, fg=dark_gray_color, bg=dark_gray_color, bd=0,
                                   highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='center', variable=manual_sample_freq_checkbox_state)

save_to_gwy_checkbox_state = IntVar()
save_to_gwy_text = Label(connexion_frame, text="Save to gwyddion", fg=white_color, bg=dark_gray_color,
                         bd=0, highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='left')
save_to_gwy_checkbox = Checkbutton(connexion_frame, fg=dark_gray_color, bg=dark_gray_color, bd=0,
                                   highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='center', variable=save_to_gwy_checkbox_state)

save_to_txt_checkbox_state = IntVar()
save_to_txt_text = Label(connexion_frame, text="Save to csv text", fg=white_color, bg=dark_gray_color,
                         bd=0, highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='left')
save_to_txt_checkbox = Checkbutton(connexion_frame, fg=dark_gray_color, bg=dark_gray_color, bd=0,
                                   highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='center', variable=save_to_txt_checkbox_state)

if(os.path.isfile(current_directory+'/configs/connexion.csv')):
    with open(current_directory+'/configs/connexion.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            advanced_checkbox_state.set(int(line['advanced']))
            autoconnect_checkbox_state.set(int(line['connect_at_start']))
            manual_sample_freq_checkbox_state.set(int(line['manual_freq']))
            save_to_gwy_checkbox_state.set(int(line['save_to_gwy']))
            save_to_txt_checkbox_state.set(int(line['save_to_txt']))
            if(advanced_checkbox_state.get() != 0):
                connexion_frame.grid(
                    row=3, column=0, columnspan=4, sticky=N+E+W)
    logs_text.insert('end',"- found in configs/connexion\n   advanced = {}\n   connect at start = {}\n   manual sampling frequency = {}\n   save to gwyddion = {}\n   save to csv text = {}\n".format(advanced_checkbox_state.get(), autoconnect_checkbox_state.get(), manual_sample_freq_checkbox_state.get(), save_to_gwy_checkbox_state.get(), save_to_txt_checkbox_state.get()))
hostname_text = Label(connexion_frame, text="hostname :", fg=white_color, bg=dark_gray_color,
                      bd=0, highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='left')
hostname_entry = Entry(connexion_frame, width=8, fg=white_color, bg=light_gray_color, bd=0,
                       highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='center')
port_text = Label(connexion_frame, text="port :", fg=white_color, bg=dark_gray_color, bd=0,
                  highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='left')
port_entry = Entry(connexion_frame, width=8, fg=white_color, bg=light_gray_color, bd=0,
                   highlightbackground=dark_gray_color, highlightcolor=selected_color, justify='center')
hostname_entry.insert(INSERT, hostname)
port_entry.insert(INSERT, port)
hostname_text.grid(row=1, column=0, sticky=W+N)
hostname_entry.grid(row=1, column=1, columnspan=2, sticky=W+N+E)
port_text.grid(row=2, column=0, sticky=W+N)
port_entry.grid(row=2, column=1, columnspan=2, sticky=W+N+E)
autoconnect_text.grid(row=0, column=0, columnspan=2, sticky=W)
autoconnect_checkbox.grid(row=0, column=2)
manual_sample_freq_text.grid(row=3, column=0, columnspan=2, sticky=W)
manual_sample_freq_checkbox.grid(row=3, column=2)
save_to_gwy_text.grid(row=4, column=0, columnspan=2, sticky=W)
save_to_gwy_checkbox.grid(row=4, column=2)
save_to_txt_text.grid(row=5, column=0, columnspan=2, sticky=W)
save_to_txt_checkbox.grid(row=5, column=2)

save_to_gwy_checkbox_state.trace('w', check_save)
save_to_txt_checkbox_state.trace('w', check_save)
save_after_image_checkbox_state.trace('w', check_save_default)
advanced_checkbox.grid(row=9, column=3, sticky=W+N+E)
advanced_text.grid(row=9, column=0, columnspan=3, sticky=W+N+E)
connect_button.grid(row=8, column=0, columnspan=2, sticky=W+N+E) 
if((autoconnect_checkbox_state.get() != 0) and (advanced_checkbox_state.get() != 0)):
    connect_me()
#endregion
root.mainloop()