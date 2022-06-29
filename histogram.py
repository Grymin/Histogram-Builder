import easygui
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# TODO - for smaller values, in rounding take magnitude.
#  Rounding is necessary to exclude binary rounding (1.000000004 etc.)


class Histogram:
    """
    Author: W. Grymin, 28.06.2022
    Histograms in Tkinter
    """

    fontsize = 16

    def __init__(self):

        # Window
        self.root = tk.Tk()
        self.root.geometry("1200x1200")
        self.root.title("File Manager")

        # PARAMETERS
        self.data = np.empty((0, 0))            # Data

        self.len = None                         # Size of data
        self.max = None                         # Max value
        self.min = None                         # Min value
        self.wid = None                         # Width of the data
        self.mag = None                         # Order of magnitude of the width of the data
        self.bin = None                         # Number of the bins
        self.dx = None                          # Width of a single bin
        self.beg = None                         # Min x value on the x-axis
        self.end = None                         # Max x value on the x-axis
        self.bins = None                        # Number of the bins
        self.bins_list = None                   # List of the bins
        self.dens = None                        # Density of the ticks on the x-axis
        self.xtitle, self.ytitle = None, None   # Titles on x and y axis

        # Booleans
        self.normalized = tk.BooleanVar()       # Normalized histogram? Bool value

        # String values
        self.frame = tk.StringVar()
        self.xtitle = tk.StringVar()
        self.ytitle = tk.StringVar()

        # File path
        self.fpath = None
        self.fname = None
        self.path = None
        self.extension = None
        self.hist_file = None

        # Definition of buttons
        but_h = 2
        but_w = 15
        but_bg = "white"
        self.but_choose_file = tk.Button(height=but_h, width=but_w, bg=but_bg,
                                         command=lambda: self.choose_file(), text="Choose file")
        self.but_show = tk.Button(height=but_h, width=but_w, bg=but_bg,
                                  command=lambda: self.draw_histogram(), text="Graph that!", state="disabled")
        self.but_save_hist = tk.Button(height=but_h, width=but_w, bg=but_bg,
                                       command=lambda: self.save_histogram(), text="Save histogram", state="disabled")

        # Defintion of textboxes and entries - disabled before defining the file
        self.tb_min_desc = tk.Label(self.root, text="Min:", state='disabled')
        self.tb_min = tk.Entry(self.root, textvariable=self.min, state='disabled')

        self.tb_max_desc = tk.Label(self.root, text="Max:", state='disabled')
        self.tb_max = tk.Entry(self.root, textvariable=self.max, state='disabled')

        self.tb_bins_desc = tk.Label(self.root, text="Bins:", state='disabled')
        self.tb_bins = tk.Entry(self.root, textvariable=self.bins, state='disabled')

        self.tb_dens_desc = tk.Label(self.root, text="Density of x main lines:", state='disabled')
        self.tb_dens = tk.Entry(self.root, textvariable=self.dens, state='disabled')

        self.tb_frame_desc = tk.Label(self.root, text="Frame", state='disabled')
        self.tb_frame = tk.Entry(self.root, textvariable=self.frame, state='disabled')

        self.tb_xtitle_desc = tk.Label(self.root, text="X Title", state='disabled')
        self.tb_xtitle = tk.Entry(self.root, textvariable=self.xtitle, state='disabled')
        self.tb_ytitle_desc = tk.Label(self.root, text="Y Title", state='disabled')
        self.tb_ytitle = tk.Entry(self.root, textvariable=self.ytitle, state='disabled')

        # Checkbox
        self.cb_normalized = tk.Checkbutton(self.root, text="Normalized?",
                                            variable=self.normalized)

        # Positions of buttons / textboxes / entries
        px = 5
        py = 30
        self.but_choose_file.grid(row=1, column=1, padx=px, pady=py)
        self.but_show.grid(row=2, column=1, padx=px, pady=py)
        self.but_save_hist.grid(row=12, column=1, padx=px, pady=py)

        self.tb_min_desc.grid(row=3, column=1)
        self.tb_max_desc.grid(row=4, column=1)
        self.tb_bins_desc.grid(row=5, column=1)
        self.tb_dens_desc.grid(row=6, column=1)
        self.tb_frame_desc.grid(row=7, column=1)
        self.tb_xtitle_desc.grid(row=8, column=1)
        self.tb_ytitle_desc.grid(row=9, column=1)
        self.cb_normalized.grid(row=10, column=1)

        self.tb_min.grid(row=3, column=2)
        self.tb_max.grid(row=4, column=2)
        self.tb_bins.grid(row=5, column=2)
        self.tb_dens.grid(row=6, column=2)
        self.tb_frame.grid(row=7, column=2)
        self.tb_xtitle.grid(row=8, column=2)
        self.tb_ytitle.grid(row=9, column=2)

        # Temp figure
        self.imgtk = ImageTk.PhotoImage(Image.open("temp.png"))
        self.img_label = tk.Label(image=self.imgtk)
        self.img_label.grid(row=2, column=4)

        # Mainloop
        self.root.mainloop()

    def choose_file(self):
        """ Reading the file data and switching buttons and textboxes to active afterwards"""

        # Definition of the file parameters
        self.fpath = easygui.fileopenbox()
        self.fname = os.path.basename(self.fpath)
        self.path = os.path.dirname(self.fpath)
        self.extension = self.fname.split('.')[1]

        # Name of the hist file
        self.hist_file = self.fname[:-4] + ".png"

        # Read data
        self.get_data()

        # Define main parameters
        self.get_main_par()

        # Calculating number of the bins
        self.number_of_bins()

        # Determining list of bins
        self.list_of_bins()

        # Activate the buttons after choice of the file
        self.switch_activity()

    def switch_activity(self):
        """Function activates the buttons and writes the calculated parameters to the entries"""
        self.but_save_hist['state'] = "normal"
        self.but_show['state'] = "normal"

        self.tb_min_desc['state'] = "normal"
        self.tb_min['state'] = "normal"
        self.tb_min.delete(0, tk.END)
        self.tb_min.insert(0, self.beg)

        self.tb_max_desc['state'] = "normal"
        self.tb_max['state'] = "normal"
        self.tb_max.delete(0, tk.END)
        self.tb_max.insert(0, self.end)

        self.tb_bins_desc['state'] = "normal"
        self.tb_bins['state'] = "normal"
        self.tb_bins.delete(0, tk.END)
        self.tb_bins.insert(0, self.bins)

        self.tb_dens_desc['state'] = "normal"
        self.tb_dens['state'] = "normal"
        self.tb_dens.delete(0, tk.END)
        self.tb_dens.insert(0, self.dens)

        self.tb_frame_desc['state'] = "normal"
        self.tb_frame['state'] = "normal"

        self.tb_xtitle_desc['state'] = "normal"
        self.tb_xtitle['state'] = "normal"
        self.tb_ytitle_desc['state'] = "normal"
        self.tb_ytitle['state'] = "normal"

    def get_data(self):
        """Reading data from file and calculation of main parameters"""
        self.data = np.genfromtxt(self.fpath, delimiter='\n')

    def get_main_par(self):
        self.max = round(self.data.max(), 4)
        self.min = round(self.data.min(), 4)
        self.wid = round(self.max - self.min, 4)
        self.mag = self.magnitude(self.wid)
        self.len = len(self.data)

    @staticmethod
    def magnitude(val):
        """Defines order of magnitude - used only for positive numbers, so no abs used"""
        return int(math.floor(math.log10(val))) if val != 0 else 0

    def read_values(self):
        """Reads the values from the entries"""
        self.beg = float(self.tb_min.get())
        self.end = float(self.tb_max.get())
        self.bins = int(self.tb_bins.get())
        self.dens = int(self.tb_dens.get())
        self.frame = self.tb_frame.get()
        self.xtitle = self.tb_xtitle.get()
        self.ytitle = self.tb_ytitle.get()

    def number_of_bins(self):

        self.bin = math.ceil(self.wid / (10 ** self.mag))
        self.dx = math.ceil((self.wid / (10 ** self.mag)) / self.bin) * 10 ** self.mag
        self.dens = 1
        self.beg = round(math.floor(self.min / self.dx) * self.dx, 4)
        self.end = round(math.ceil(self.max / self.dx) * self.dx, 4)

        # Sturge's rule
        self.bins = int(np.ceil(np.log2(self.len)))
        # print('      square-root: {}'.format(math.sqrt(leng)))
        # print('      rices formula: {}'.format(2 * leng ** (1 / 3)))
        # print('      3.3: {}'.format(math.ceil(3.3 * math.log10(len(self.data)) + 1)))

    def list_of_bins(self):
        """List of the bins borders"""
        self.bins_list = np.linspace(self.beg, self.end, self.bins + 1)

    def draw_histogram(self):

        # Read values from entries
        self.read_values()

        # Actualize list of bins
        self.list_of_bins()

        # Rysowanie histogramu
        _, ax = plt.subplots(figsize=(7.9, 6))
        # p = self.figure.gca()
        # p.hist(self.data, bins=self.bins_list, density=True, fc='lightgray', ec='black')

        # Odczytaj wartości ymax i ymin histogramu

        # Rysuj histogram
        yy, xx, _ = plt.hist(self.data, bins=self.bins_list, density=self.normalized.get(), fc='lightgray', ec='black')
        ymax, ymin = yy.max(), yy.min()

        # Siatka
        plt.grid(axis='y', alpha=0.9)
        plt.grid(axis='x', alpha=0.9)

        # Min/maks wartości na osi x
        plt.xlim(self.beg, self.end)

        # Wpisanie wartości x
        plt.xticks(np.linspace(self.beg, self.end, (int(self.bins/self.dens) + 1)))

        # Oznaczenie osi x, osi y
        plt.xlabel(self.xtitle, fontsize=Histogram.fontsize, weight='bold')
        plt.ylabel(self.ytitle, fontsize=Histogram.fontsize, weight='bold')

        # Optymalizacja wielkości wykresu na rysunku
        # plt.subplots_adjust(left=0.22, bottom=0.15, right=0.93, top=0.95)

        # Czcionka legendy
        # plt.legend(fontsize=fontsize - 6)

        # Edycja czcionki na osi y
        plt.tick_params(axis='x', labelsize=Histogram.fontsize)
        plt.tick_params(axis='y', labelsize=Histogram.fontsize)

        # Dodanie ramek z A/B
        if len(str(self.frame)):
            plt.text(self.beg + 1 / 20 * (self.end-self.beg), (ymax - 1 / 10 * (ymax - ymin)),
                     self.frame, fontsize=Histogram.fontsize + 14, bbox=dict(fc='white', alpha=0.5))

        # Wydruk na ekran jeśli output = True

        # Zapisanie samego histogramu w katalogu zdefiniowanym na górze kodu
        plt.savefig("temp.png")
        # plt.show()

        self.imgtk = ImageTk.PhotoImage(Image.open("temp.png"))
        self.img_label = tk.Label(image=self.imgtk)
        self.img_label.grid(row=2, column=4)

    @staticmethod
    def save_histogram():
        dest = tk.filedialog.askdirectory()
        name = easygui.enterbox("New name of the file:", "New name", "New_name")
        new_fpath = os.path.join(dest, '.'.join((name, 'png')))
        if os.path.exists(new_fpath):
            tk.messagebox.showerror("UPS!", "Such a file exists in this direction!")
        else:
            shutil.copy("temp.png", new_fpath)
            tk.messagebox.showinfo('SUCCESS', "File saved")


h = Histogram()
