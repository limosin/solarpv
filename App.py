import tkinter as tk
from tkinter import filedialog, Button, LabelFrame, PanedWindow, Label, Entry, Scale
from tkinter.ttk import Combobox, Separator
import os
from src.util import get_inv_list, get_panel_list
from json import load

curr_dir_path = os.path.dirname(os.path.realpath(__file__))

class GUI(tk.Tk):

    # PANEL_MODELS = tuple(['Select'] + get_panel_list())
    # INV_MODELS = tuple(['Select'] + get_inv_list())
    PANEL_MODELS = tuple(['Select'])
    INV_MODELS = tuple(['Select'])

    def __init__(self):
        super().__init__()

        self.title("Solar PV Plant Simulator")
        # self.resizable(width=False, height=False)
        self.geometry('305x420')

        self.make_panes()
        self.make_browse_frame()
        self.make_model_selector()
        self.make_location_frame()
        self.make_config_frame()
        self.make_scale()
        self.make_bot_buttons()

    def make_panes(self):
        self.p1 = PanedWindow(self, orient='vertical')
        self.p1f1 = LabelFrame(self.p1, text='Browse Data', width=300, height=70)
        self.p1f2 = LabelFrame(self.p1, text='Select Models', width=300, height=70)
        self.p1f3 = LabelFrame(self.p1, text='Select Location', width=200, height=130)
        self.p1f4 = LabelFrame(self.p1, text='Panel Configurations', width=200, height=200)

        self.p1.add(self.p1f1)
        self.p1.add(self.p1f2)
        self.p1.add(self.p1f3)
        self.p1.add(self.p1f4)
        self.p1.grid(row=0, column=0)


    #Browse frame
    def make_browse_frame(self):
        self.f1l1 = Label(self.p1f1, text='Weather :', padx=18)
        self.f1l2 = Label(self.p1f1, text='Solar :', padx=18)
        self.f1l3 = Label(self.p1f1, text='Path Weat:')
        self.f1l4 = Label(self.p1f1, text='Path Solar:')
        self.f11b1 = Button(self.p1f1, text = "Browse", command = self.openDialog_weather ,width = 7)
        self.f11b2 = Button(self.p1f1, text = "Browse", command = self.openDialog_solar ,width = 7)

        self.f1l1.grid(row=0, column=0)
        self.f1l2.grid(row=0, column=2)
        self.f1l3.grid(row=1, column=0, columnspan=4, sticky='w')
        self.f1l4.grid(row=2, column=0, columnspan=4, sticky='w')
        self.f11b1.grid(row=0, column=1)
        self.f11b2.grid(row=0, column=3)

    def openDialog_weather(self):
        self.weather_path = filedialog.askopenfilename(initialdir = curr_dir_path,title = "Select file",filetypes = (("csv files","*.csv"),("Excel files","xlsx.*")))
        if self.weather_path != '':
            self.update_datapath(self.weather_path, 'weather')

    def openDialog_solar(self):
        self.solar_path = filedialog.askopenfilename(initialdir = curr_dir_path,title = "Select file",filetypes = (("csv files","*.csv"),("Excel files","xlsx.*")))
        if self.solar_path != '':
            self.update_datapath(self.solar_path)
            
    def update_datapath(self, text, pathname=''):
        if len(text) >35:
            text = '...' + text[-35:]

        if pathname == 'weather':
            self.f1l3.configure(text='Path Weat: '+text)
        else:
            self.f1l4.configure(text='Path Solar: '+text)


    #Model Selector
    def make_model_selector(self):
        self.f2l1 = Label(self.p1f2, text='Panel')
        self.f2l2 = Label(self.p1f2, text='Inverter')
        self.f2co1 = Combobox(self.p1f2, width=36)
        self.f2co2 = Combobox(self.p1f2, width=36)
        self.f2co1['values'] = self.PANEL_MODELS
        self.f2co2['values'] = self.INV_MODELS
        self.f2co1.current(0)
        self.f2co2.current(0)

        self.f2l1.grid(row=0, column=0, sticky='w')
        self.f2l2.grid(row=1, column=0, sticky='w')
        self.f2co1.grid(row=0, columnspan=4, column=1)
        self.f2co2.grid(row=1, columnspan=4, column=1)


    #Location Properties
    def make_location_frame(self):
        self.f3l1 = Label(self.p1f3, text='Latitude')
        self.f3l2 = Label(self.p1f3, text='Longitude')
        self.f3l3 = Label(self.p1f3, text='Altitude')
        self.f3l4 = Label(self.p1f3, text='Time Zone')

        self.f3t1 = Entry(self.p1f3, width=20)
        # self.f3t1.insert('end', 'Enter')
        self.f3t2 = Entry(self.p1f3, width=20)
        # self.f3t2.insert('end', 'Enter')
        self.f3t3 = Entry(self.p1f3, width=20)
        # self.f3t3.insert('end', 'Enter')
        self.f3t4 = Entry(self.p1f3, width=20)
        self.f3t4.insert('end', 'Asia/Kolkata')

        self.f3l1.grid(row=0, column=0, sticky='w')
        self.f3l2.grid(row=1, column=0, sticky='w')
        self.f3l3.grid(row=2, column=0, sticky='w')
        self.f3l4.grid(row=3, column=0, sticky='w')
        self.f3t1.grid(row=0, column=1, sticky='w')
        self.f3t2.grid(row=1, column=1, sticky='w')
        self.f3t3.grid(row=2, column=1, sticky='w')
        self.f3t4.grid(row=3, column=1, sticky='w')

        self.p1f3f2 = LabelFrame(self.p1f3, width=20, height=20, padx=5)
        self.p1f3f2.grid(row=1, column=3, sticky='n', columnspan=4, rowspan=4)

        self.b2 = Button(self.p1f3f2, text = "Load Json", command = self.load_json, width = 8, height=2)
        self.b2.grid(row=0, column=4, rowspan=3,columnspan=2, sticky='e')

    def load_json(self):
        with open('data/config.json') as jsonfile:
            data = load(jsonfile)
            self.f2co1.set(data['module'])
            self.f2co2.set(data['inverter'])
            self.f3t1.delete(0, 'end')
            self.f3t1.insert(0,data['lats'])
            self.f3t2.delete(0, 'end')
            self.f3t2.insert(0,data['longs'])
            self.f3t3.delete(0, 'end')
            self.f3t3.insert(0,data['altitude'])
            self.f3t4.delete(0, 'end')
            self.f3t4.insert(0,data['timezone'])
            self.f4t1.delete(0, 'end')
            self.f4t1.insert(0,data['surf_azi'])
            self.f4t2.delete(0, 'end')
            self.f4t2.insert(0,data['modules_per_string'])
            self.f4t3.delete(0, 'end')
            self.f4t3.insert(0,data['strings_per_inverter'])
            self.f4t4.delete(0, 'end')
            self.f4t4.insert(0,data['albedo'])
            self.f4t5.delete(0, 'end')
            self.f4t5.insert(0,data['tilt'])
            self.f4s1.set(self.f4t5.get())

    #Panel Configurations
    def make_config_frame(self):
        self.f4l1 = Label(self.p1f4, text='Surf Azimuth')
        self.f4t1 = Entry(self.p1f4, width=10)
        self.f4l1.grid(row=0, column=0, sticky='w')
        self.f4t1.grid(row=0, column=1, sticky='e')

        self.f4l2 = Label(self.p1f4, text='Modules/String')
        self.f4t2 = Entry(self.p1f4, width=10)
        self.f4l2.grid(row=1, column=0, sticky='w')
        self.f4t2.grid(row=1, column=1, sticky='e')

        self.f4l3 = Label(self.p1f4, text='No of Strings')
        self.f4t3 = Entry(self.p1f4, width=10)
        self.f4l3.grid(row=2, column=0, sticky='w')
        self.f4t3.grid(row=2, column=1, sticky='e')

        self.f4l4 = Label(self.p1f4, text='Albedo')
        self.f4t4 = Entry(self.p1f4, width=10)
        self.f4t4.insert('end',0.4)
        self.f4l4.grid(row=3, column=0, sticky='w')
        self.f4t4.grid(row=3, column=1, sticky='e')

        self.f4l5 = Label(self.p1f4, text='Tilt')
        self.f4t5 = Entry(self.p1f4, width=10)
        self.f4l5.grid(row=4, column=0, sticky='w')
        self.f4t5.grid(row=4, column=1, sticky='e')

    def make_scale(self):
        self.f4s1 = Scale(self.p1f4, from_=0, to_=360, orient='vertical', label='Tilt', width=20, command = self.set_tilt_entry)
        self.f4s1.grid(row=0,rowspan=5, column=3, sticky='n')

    def set_tilt_entry(self,j):
        self.f4t5.delete(0, 'end')
        self.f4t5.insert(0,str(j))
        return

    
    #Make Bottom buttons
    def make_bot_buttons(self):
        self.b1 = Button(self.p1, text = "SaveAs Json",width = 10)
        self.p1.add(self.b1)
        self.b3 = Button(self.p1, text = "Run Configuration",width = 10)
        self.p1.add(self.b3)

if __name__ == "__main__":
    gui = GUI()
    gui.mainloop()