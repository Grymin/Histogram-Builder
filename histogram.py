import csv
import easygui
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# TODO scientific format checkbox
# TODO Ramka checkbox + Entry
# TODO zapis w innym miejscu
# TODO Odczyt z okienek
# TODO aktualizacja wartości w oknie

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
        self.scientific_format = [0, 0]         # Scientific format on x/y
        self.podpisy = ["-", "-"]               # Labels on x/y
        self.ramka = "A"                        # Frame with symbol of the drawing
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
        self.dens = None                # Density of the ticks on the x-axis

        self.min_str = tk.StringVar()
        self.max_str = tk.StringVar()
        self.bins_str = tk.StringVar()
        self.dens_str = tk.StringVar()

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
                                       command=lambda: self.draw_histogram(), text="Save histogram", state="disabled")

        # Defintion of textboxes and entries - disabled before defining the file
        self.tb_min_desc = tk.Label(self.root, text="Min:", state='disabled')
        self.tb_min = tk.Entry(self.root, textvariable=self.min_str, state='disabled')

        self.tb_max_desc = tk.Label(self.root, text="Max:", state='disabled')
        self.tb_max = tk.Entry(self.root, textvariable=self.max_str, state='disabled')

        self.tb_bins_desc = tk.Label(self.root, text="Bins:", state='disabled')
        self.tb_bins = tk.Entry(self.root, textvariable=self.bins_str, state='disabled')

        self.tb_dens_desc = tk.Label(self.root, text="Density of x main lines:", state='disabled')
        self.tb_dens = tk.Entry(self.root, textvariable=self.dens_str, state='disabled')

        self.tb_savefile = tk.Entry(self.root, state='disabled')

        # Positions of buttons / textboxes / entries
        px = 5
        py = 30
        self.but_choose_file.grid(row=1, column=1, padx=px, pady=py)
        self.but_show.grid(row=2, column=1, padx=px, pady=py)
        self.but_save_hist.grid(row=9, column=1, padx=px, pady=py)

        self.tb_min_desc.grid(row=3, column=1)
        self.tb_max_desc.grid(row=4, column=1)
        self.tb_bins_desc.grid(row=5, column=1)
        self.tb_dens_desc.grid(row=6, column=1)

        self.tb_min.grid(row=3, column=2)
        self.tb_max.grid(row=4, column=2)
        self.tb_bins.grid(row=5, column=2)
        self.tb_dens.grid(row=6, column=2)

        # Figure
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

        self.tb_savefile['state'] = "normal"

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
        """Reads the values from the entries""" #TODO divide?
        self.beg = float(self.tb_min.get())
        self.end = float(self.tb_max.get())
        self.bins = int(self.tb_bins.get())
        self.dens = int(self.tb_dens.get())

    def format_ticks(self, val):
        """Transforms value into the scientific format"""
        order = self.magnitude(val)
        value = val / 10**order
        return f'{round(value,2)}E{order}'

    def number_of_bins(self):
        # TODO

        self.bin = math.ceil(self.wid / (10 ** self.mag))
        self.dx = math.ceil((self.wid / (10 ** self.mag)) / self.bin) * 10 ** self.mag
        self.dens = 1
        self.beg = round(math.floor(self.min / self.dx) * self.dx,4)
        self.end = round(math.ceil(self.max / self.dx) * self.dx,4)

        # Sturge's rule
        self.bins = int(np.ceil(np.log2(self.len)))
        # print('      square-root: {}'.format(math.sqrt(leng)))
        # print('      rices formula: {}'.format(2 * leng ** (1 / 3)))
        # print('      3.3: {}'.format(math.ceil(3.3 * math.log10(len(self.data)) + 1)))

    def list_of_bins(self):
        """List of the bins borders"""
        self.bins_list = np.linspace(self.beg, self.end, self.bins + 1)

    def draw_histogram(self):   #TODO nieskonczone

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
        yy, xx, _ = plt.hist(self.data, bins=self.bins_list, density=True, fc='lightgray', ec='black')
        ymax, ymin = yy.max(), yy.min()

        # Wprowadzenie zapisu naukowego na osi y i x
        if self.scientific_format[0]:
            formatter = plt.FuncFormatter(self.format_ticks)
            ax.xaxis.set_major_formatter(formatter)
        if self.scientific_format[1]:
            formatter = plt.FuncFormatter(self.format_ticks)
            ax.yaxis.set_major_formatter(formatter)

        # Siatka
        plt.grid(axis='y', alpha=0.9)
        plt.grid(axis='x', alpha=0.9)

        # Min/maks wartości na osi x
        plt.xlim(self.beg, self.end)

        # Wpisanie wartości x
        plt.xticks(np.linspace(self.beg, self.end, (int(self.bins/self.dens) + 1)))

        # Oznaczenie osi x, osi y
        plt.xlabel(self.podpisy[0], fontsize=Histogram.fontsize, weight='bold')
        plt.ylabel(self.podpisy[1], fontsize=Histogram.fontsize, weight='bold')

        # Optymalizacja wielkości wykresu na rysunku
        # plt.subplots_adjust(left=0.22, bottom=0.15, right=0.93, top=0.95)

        # Czcionka legendy
        # plt.legend(fontsize=fontsize - 6)

        # Edycja czcionki na osi y
        plt.tick_params(axis='x', labelsize=Histogram.fontsize)
        plt.tick_params(axis='y', labelsize=Histogram.fontsize)

        # Dodanie ramek z A/B
        if self.ramka is not False:
            plt.text(self.beg + 1 / 20 * (self.end-self.beg), (ymax - 1 / 10 * (ymax - ymin)),
                     self.ramka, fontsize=Histogram.fontsize + 14, bbox=dict(fc='white', alpha=0.5))

        # Wydruk na ekran jeśli output = True

        # Zapisanie samego histogramu w katalogu zdefiniowanym na górze kodu
        plt.savefig("temp.png")
        # plt.show()

        self.imgtk = ImageTk.PhotoImage(Image.open("temp.png"))
        self.img_label = tk.Label(image=self.imgtk)
        self.img_label.grid(row=2, column=4)

h = Histogram()
