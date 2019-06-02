import tkinter as tk
from tkinter import filedialog, Button, LabelFrame, PanedWindow, Label, Entry, Scale, messagebox
from tkinter.ttk import Combobox, Separator, Notebook
from json import load
import os
import sys

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler

from src.util import get_inv_list, get_panel_list
from src.model import Model


curr_dir_path = os.path.dirname(os.path.realpath(__file__))

class GUI(tk.Tk):

    # PANEL_MODELS = tuple(['Select'] + get_panel_list())
    # INV_MODELS = tuple(['Select'] + get_inv_list())
    PANEL_MODELS = tuple(['Select'])
    INV_MODELS = tuple(['Select'])

    def __init__(self):
        super().__init__()

        self.title("Solar PV Plant Simulator")
        self.resizable(width=False, height=False)
        # self.geometry('300x450')
        self.make_panes()
        self.make_browse_frame()
        self.make_model_selector()
        self.make_location_frame()
        self.make_config_frame()
        self.make_scale()
        self.make_bot_buttons()
        self.modelname = 'PV Plant'
        self.model = Model()

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
        self.p1.grid(row=0, column=0, rowspan=2, sticky='n')


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
        self.weather_path = filedialog.askopenfilename(initialdir = curr_dir_path,title = "Select file", \
                                                        filetypes = (("csv files","*.csv"),("Excel files","*.xlsx")))
        self.f1l3.configure(text='Loading....')
        if self.weather_path != '':
            if self.model.weather_file_setter(self.weather_path):
                self.update_datapath(self.weather_path, 'weather')
                print('Weather browse path updated..')
            else:
                messagebox.showerror('Error', 'Error Updating the File Path')

    def openDialog_solar(self):
        self.solar_path = filedialog.askopenfilename(initialdir = curr_dir_path,title = "Select file", \
                                                        filetypes = (("csv files","*.csv"),("Excel files","*.xlsx")))
        self.f1l4.configure(text='Loading....')
        if self.solar_path != '':
            if self.model.solar_file_setter(self.solar_path):
                self.update_datapath(self.solar_path)
                print('Solar browse path updated..')
            else:
                messagebox.showerror('Error', 'Error Updating the File Path')
            
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
            self.modelname = data['name']

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
        self.b1 = Button(self.p1, text = "SaveAs Json(Not Working)",width = 10)
        self.p1.add(self.b1)
        self.b4 = Button(self.p1, text = "Run Configuration", command = self.Run_model, width = 10)
        self.p1.add(self.b4)
        self.b5 = Button(self.p1, text = "Quit Simulator", command = self.quit, width = 10)
        self.p1.add(self.b5)

    def quit(self):
        self.destroy()
        sys.exit()

    """
    This Function runs on pressing the Run Configuration button
    1. Make the GUI Pane
    2. Check if all the configs are correct
    3. Export the config to model object
    4. Run the Configuration

    """
    def Run_model(self):
        self.make_figure_frame()
        try:
            self.export_data_toModel()
        except:
            self.close_fig()
            messagebox.showerror('Invalid Format', 'One or More entries are in wrong format!!')
            return None
        self.model.run_api()
        self.geometry('900x500')
        self.add_figuresto_frame()

    def make_figure_frame(self):
        self.resizable(width=True, height=True)
        self.p2 = PanedWindow(self, orient='vertical')
        self.p2N = Notebook(self.p2)
        self.Ntab1 = LabelFrame(self.p2N)
        self.Ntab1.grid()
        self.Ntab2 = LabelFrame(self.p2N)
        self.Ntab2.grid()
        self.Ntab3 = LabelFrame(self.p2N)
        self.Ntab3.grid()
        self.p2N.add(self.Ntab1, text='Current')
        self.p2N.add(self.Ntab2, text='Voltage')
        self.p2N.add(self.Ntab3, text='Power')
        self.p2N.grid()
        self.p2.add(self.p2N)
        self.p2.grid(row=0, column=1, rowspan=2,columnspan=2, sticky='nsew')
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.b3 =  Button(self.p1, text = "Close Figure", command = self.close_fig, width = 10)
        self.p1.add(self.b3)

    def export_data_toModel(self):
        configdict = {}
        configdict['lats'] = float(self.f3t1.get())
        configdict['longs'] = float(self.f3t2.get())
        configdict['tilt'] = float(self.f4s1.get())
        configdict['surf_azi'] = float(self.f4t1.get())
        configdict['altitude'] = float(self.f3t3.get())
        configdict['name'] = self.modelname
        configdict['timezone'] = self.f3t4.get()
        configdict['module'] = self.f2co1.get()
        configdict['inverter'] = self.f2co2.get()
        configdict['modules_per_string'] = int(self.f4t2.get())
        configdict['strings_per_inverter'] = int(self.f4t3.get())
        configdict['albedo'] = float(self.f4t4.get())
        flag, msg = self.model.data_setter(configdict)
        if flag:
            print('Data Exported to Model Successfully')
        else:
            print('Export Unsuccessfull '+msg)
            messagebox.showerror('Invalid Model', msg)

        return None


    def close_fig(self):
        self.p2.destroy()
        self.b3.destroy()
        self.resizable(width=False, height=False)
        self.geometry("") 


    def add_figuresto_frame(self):
    
        def on_key_event(event, canvas, toolbar):
            print('you pressed %s' % event.key)
            key_press_handler(event, canvas, toolbar)

        f_v, f_c, f_p = self.model.export_fig(self.model.output)

        canvas_v = FigureCanvasTkAgg(f_v, master=self.Ntab1)
        canvas_v.draw()
        canvas_v.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        toolbar_v = NavigationToolbar2Tk(canvas_v, self.Ntab1)
        toolbar_v.update()
        canvas_v._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas_v.mpl_connect('key_press_event', lambda x :on_key_event(x, canvas_v, toolbar_v))

        canvas_c = FigureCanvasTkAgg(f_c, master=self.Ntab2)
        canvas_c.draw()
        canvas_c.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        toolbar_c = NavigationToolbar2Tk(canvas_c, self.Ntab2)
        toolbar_c.update()
        canvas_c._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas_c.mpl_connect('key_press_event', lambda x:on_key_event(x, canvas_c, toolbar_c))

        canvas_p = FigureCanvasTkAgg(f_p, master=self.Ntab3)
        canvas_p.draw()
        canvas_p.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        toolbar_p = NavigationToolbar2Tk(canvas_p, self.Ntab3)
        toolbar_p.update()
        canvas_p._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas_p.mpl_connect('key_press_event', lambda x:on_key_event(x, canvas_p, toolbar_p))

        return None


if __name__ == "__main__":
    gui = GUI()
    gui.mainloop()