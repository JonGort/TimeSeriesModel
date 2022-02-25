import time
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from calculations import *
from classes import *
import csv
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
plt.ioff()
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
plt.style.use('seaborn-dark')

GrowFactor = 2
BannedWords = ["", "Transmitters", "Receivers","Atmospheres","TimeSeries","None"]
def list_to_csv_row(liszt, sep=','):
    string = str(liszt).replace(", ",sep).replace("[","").replace("]","").replace("'","")
    return string

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)

        # TAB INDEX
        self.primarytabControl = ttk.Notebook(self)
        # subtabs
        self.timeseriestab = ttk.Frame(self.primarytabControl)
        self.primarytabControl.add(self.timeseriestab, text='Time Series')

        self.transmitterstab = ttk.Frame(self.primarytabControl)
        self.primarytabControl.add(self.transmitterstab, text='Transmitters')

        self.receiverstab = ttk.Frame(self.primarytabControl)
        self.primarytabControl.add(self.receiverstab, text='Receivers')

        self.atmospherestab = ttk.Frame(self.primarytabControl)
        self.primarytabControl.add(self.atmospherestab, text='Atmospheres')

        self.runcalculationtab = ttk.Frame(self.primarytabControl)
        self.primarytabControl.add(self.runcalculationtab, text='Run Calculation')

        self.primarytabControl.grid(row=0, column=0)


        #Time Series Tab

        self.tsplotframe = ttk.Frame(self.timeseriestab)
        self.is_ts_plot = False

        self.tsparamframe = ttk.Frame(self.timeseriestab)
        self.tsparamframe.grid(row=0, column=1)

        self.selectframe = ttk.Frame(self.tsparamframe)
        self.selectframe.grid(row=0,column=0)
        self.selecttext = ttk.Label(self.selectframe, text='Select Time Series')
        self.selecttext.grid(row=0, column=0)
        self.selectedseries = tk.StringVar()
        self.timeseries = []
        self.timeseriesnames = []
        self.timeseriesdropdown = ttk.OptionMenu(self.selectframe,
                                                 self.selectedseries,
                                                 None,
                                                 *self.timeseriesnames,
                                                 command=self.change_active_ts)
        self.timeseriesdropdown.grid(row=1, column=0)
        self.addtimeseries = ttk.Button(self.selectframe,
                                        text='New',
                                        command=self.open_ts_add_menu)
        self.addtimeseries.grid(row=1, column=1)

        self.tserror = tk.StringVar()
        self.tserrordisplay = ttk.Label(self.tsparamframe, textvariable = self.tserror)

        self.tsdisplayframe = ttk.Frame(self.tsparamframe)

        self.tsdisplay_active = False
        self.active_ts = None

        self.properties_label = ttk.Label(self.tsdisplayframe, text='Properties')
        self.properties_label.grid(row=1, column=0)
        self.properties_tab = ttk.Frame(self.tsdisplayframe)
        self.properties_tab.grid(row=2, column=0)

        self.name_label = ttk.Label(self.properties_tab, text='Name:')
        self.name_label.grid(row=0, column=0)
        self.ts_current_name = tk.StringVar()
        self.name_display = ttk.Label(self.properties_tab, textvariable=self.ts_current_name)
        self.name_display.grid(row=0, column=1)
        self.name_button_frame = ttk.Frame(self.properties_tab)
        self.name_button_frame.grid(row=0, column=2)
        self.edit_name_button = ttk.Button(self.name_button_frame, text='Edit', command=self.enter_ts_namechange)
        self.edit_name_button.grid(row=0, column=0)

        self.new_name = tk.StringVar()
        self.name_new_field = ttk.Entry(self.properties_tab, justify='center', textvariable=self.new_name)
        self.save_name_button = ttk.Button(self.name_button_frame, text='Save', command=self.save_ts_namechange)
        self.cancel_name_button = ttk.Button(self.name_button_frame, text='Cancel', command=self.exit_ts_namechange)

        self.ts_current_st = tk.StringVar()
        self.sample_time_label = ttk.Label(self.properties_tab, text='Sample Time (s):')
        self.sample_time_label.grid(row=1, column=0)
        self.sample_time_display = ttk.Label(self.properties_tab, textvariable=self.ts_current_st)
        self.sample_time_display.grid(row=1, column=1)
        self.sample_time_button_frame = ttk.Frame(self.properties_tab)
        self.sample_time_button_frame.grid(row=1, column=2)
        self.edit_sample_time_button = ttk.Button(self.sample_time_button_frame, text='Edit',
                                                  command=self.enter_ts_st_change, state='disabled')
        self.edit_sample_time_button.grid(row=0, column=0)

        self.ts_current_ylabel = tk.StringVar()
        self.ylabel_label = ttk.Label(self.properties_tab, text='Y-Label:')
        self.ylabel_label.grid(row=2, column=0)
        self.ylabel_display = ttk.Label(self.properties_tab, textvariable=self.ts_current_ylabel)
        self.ylabel_display.grid(row=2, column=1)
        self.ylabel_button_frame = ttk.Frame(self.properties_tab)
        self.ylabel_button_frame.grid(row=2, column=2)
        self.edit_ylabel_button = ttk.Button(self.ylabel_button_frame, text='Edit',
                                             command=self.enter_ts_ylabel_change)
        self.edit_ylabel_button.grid(row=0, column=0)

        self.new_ylabel = tk.StringVar()
        self.ylabel_new_field = ttk.Entry(self.properties_tab, justify='center', textvariable=self.new_ylabel)
        self.save_ylabel_button = ttk.Button(self.ylabel_button_frame, text='Save', command=self.save_ts_ylabel_change)
        self.cancel_ylabel_button = ttk.Button(self.ylabel_button_frame, text='Cancel',
                                               command=self.exit_ts_ylabel_change)

        self.add_sequence_label = ttk.Label(self.tsdisplayframe, text='Add Sequence')
        self.add_sequence_label.grid(row=3, column=0)
        self.addSequenceTabControl = ttk.Notebook(self.tsdisplayframe)
        self.addSequenceTabControl.grid(row=4, column=0)

        self.add_pulse_frame = ttk.Frame(self.addSequenceTabControl)
        self.addSequenceTabControl.add(self.add_pulse_frame, text='Pulse')

        self.pulse_amplitude_label = ttk.Label(self.add_pulse_frame, text='Amplitude:')
        self.pulse_amplitude_label.grid(row=0,column=0)
        self.pulse_amplitude = tk.StringVar()
        self.pulse_amplitude.set("100")
        self.pulse_amplitude_entry = ttk.Entry(self.add_pulse_frame, justify='center',
                                               textvariable=self.pulse_amplitude)
        self.pulse_amplitude_entry.grid(row=0, column=1)
        self.pulse_period_label = ttk.Label(self.add_pulse_frame, text='Period:')
        self.pulse_period_label.grid(row=1,column=0)
        self.pulse_period = tk.StringVar()
        self.pulse_period.set("10")
        self.pulse_period_entry = ttk.Entry(self.add_pulse_frame, justify='center',
                                            textvariable=self.pulse_period)
        self.pulse_period_entry.grid(row=1, column=1)
        self.pulse_period_units = ttk.Label(self.add_pulse_frame, text='s')
        self.pulse_period_units.grid(row=1,column=2)

        self.pulse_duty_cycle_label = ttk.Label(self.add_pulse_frame, text='Duty Cycle:')
        self.pulse_duty_cycle_label.grid(row=2, column=0)
        self.pulse_duty_cycle = tk.StringVar()
        self.pulse_duty_cycle.set("100")
        self.pulse_duty_cycle_entry = ttk.Entry(self.add_pulse_frame, justify='center',
                                                textvariable=self.pulse_duty_cycle)
        self.pulse_duty_cycle_entry.grid(row=2, column=1)
        self.pulse_duty_cycle_units = ttk.Label(self.add_pulse_frame, text='%')
        self.pulse_duty_cycle_units.grid(row=2, column=2)

        self.pulse_duration_label = ttk.Label(self.add_pulse_frame, text='Duration:')
        self.pulse_duration_label.grid(row=3, column=0)
        self.pulse_duration = tk.StringVar()
        self.pulse_duration.set("60")
        self.pulse_duration_entry = ttk.Entry(self.add_pulse_frame, justify='center',
                                              textvariable=self.pulse_duration)
        self.pulse_duration_entry.grid(row=3, column=1)
        self.pulse_duration_units = ttk.Label(self.add_pulse_frame, text='s')
        self.pulse_duration_units.grid(row=3, column=2)

        self.pulse_add_button = ttk.Button(self.add_pulse_frame, text='Add Pulse', command=self.add_pulse)
        self.pulse_add_button.grid(row=4, column=1)

        self.add_linear_frame = ttk.Frame(self.addSequenceTabControl)
        self.addSequenceTabControl.add(self.add_linear_frame, text='Linear')

        self.linear_init_label = ttk.Label(self.add_linear_frame, text='Initial Amplitude:')
        self.linear_init_label.grid(row=0, column=0)
        self.linear_init = tk.StringVar()
        self.linear_init.set("0")
        self.linear_init_entry = ttk.Entry(self.add_linear_frame, justify='center', textvariable=self.linear_init)
        self.linear_init_entry.grid(row=0, column=1)

        self.linear_final_label = ttk.Label(self.add_linear_frame, text='Final Amplitude:')
        self.linear_final_label.grid(row=1, column=0)
        self.linear_final = tk.StringVar()
        self.linear_final.set("100")
        self.linear_final_entry = ttk.Entry(self.add_linear_frame, justify='center', textvariable=self.linear_final)
        self.linear_final_entry.grid(row=1,column=1)

        self.linear_duration_label = ttk.Label(self.add_linear_frame, text='Duration:')
        self.linear_duration_label.grid(row=2, column=0)
        self.linear_duration = tk.StringVar()
        self.linear_duration.set("60")
        self.linear_duration_entry = ttk.Entry(self.add_linear_frame, justify='center',
                                               textvariable=self.linear_duration)
        self.linear_duration_entry.grid(row=2, column=1)
        self.linear_duration_units = ttk.Label(self.add_linear_frame, text='s')
        self.linear_duration_units.grid(row=2, column=2)

        self.linear_add_button = ttk.Button(self.add_linear_frame, text='Add Linear', command=self.add_linear)
        self.linear_add_button.grid(row=3, column=1)

        self.add_downtime_frame = ttk.Frame(self.addSequenceTabControl)
        self.addSequenceTabControl.add(self.add_downtime_frame, text='Downtime')

        self.downtime_from_label = ttk.Label(self.add_downtime_frame, text='From:')
        self.downtime_from_label.grid(row=0, column=0)
        self.downtime_from = tk.StringVar()
        self.downtime_from_entry = ttk.Entry(self.add_downtime_frame, textvariable=self.downtime_from, justify='center')
        self.downtime_from_entry.grid(row=0, column=1)
        self.downtime_from_units = ttk.Label(self.add_downtime_frame, text='s')
        self.downtime_from_units.grid(row=0, column=2)

        self.downtime_to_label = ttk.Label(self.add_downtime_frame, text='To:')
        self.downtime_to_label.grid(row=1, column=0)
        self.downtime_to = tk.StringVar()
        self.downtime_to_entry = ttk.Entry(self.add_downtime_frame, textvariable=self.downtime_to, justify='center')
        self.downtime_to_entry.grid(row=1, column=1)
        self.downtime_to_units = ttk.Label(self.add_downtime_frame, text='s')
        self.downtime_to_units.grid(row=1, column=2)

        self.downtime_add_button = ttk.Button(self.add_downtime_frame, text='Add Downtime', command=self.add_downtime)
        self.downtime_add_button.grid(row=2, column=1)

        self.remove_label = ttk.Label(self.tsdisplayframe, text='Remove Sequence(s)')
        self.remove_label.grid(row=5, column=0)
        self.remove_buttons = ttk.Frame(self.tsdisplayframe)
        self.remove_buttons.grid(row=6, column=0)
        self.remove_last_button = ttk.Button(self.remove_buttons, text='Remove Last', command=self.remove_last)
        self.remove_last_button.grid(row=0, column=0)
        self.clear_all_button = ttk.Button(self.remove_buttons, text='Clear All', command=self.clear_all)
        self.clear_all_button.grid(row=0, column=1)

        self.ts_delete_button = ttk.Button(self.tsdisplayframe, text='Delete Series', command=self.delete_current_ts)
        self.ts_delete_button.grid(row=7, column=0)
        # Prepare Graphs
        self.ts_fig, self.ts_ax1 = plt.subplots()
        self.ts_ax2 = self.ts_ax1.twinx()
        self.ts_fig.patch.set_facecolor("#F0F0F0")
        self.ts_x = 8
        self.ts_y = 5
        self.ts_fig.set_size_inches(self.ts_x, self.ts_y)
        self.canvas = FigureCanvasTkAgg(self.ts_fig, master=self.tsplotframe)  # A tk.DrawingArea.
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.tsplotframe, pack_toolbar=False)
        self.toolbar.update()
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.toolbar.grid(row=1, column=0)

        self.ts_buttonbar = ttk.Frame(self.tsplotframe)
        self.ts_buttonbar.grid(row=2, column=0)
        self.ts_shrink = ttk.Button(self.ts_buttonbar, text='-', command=self.ts_plot_shrink)
        self.ts_shrink.grid(row=0, column=0)
        self.ts_grow = ttk.Button(self.ts_buttonbar, text='+', command=self.ts_plot_grow)
        self.ts_grow.grid(row=0, column=1)

        # Transmitters tab
        self.changing_tx = False
        self.transmitters = []
        self.transmitternames = []
        self.txdisplay_active = False
        self.tx_dropdown_frame = ttk.Frame(self.transmitterstab)
        self.tx_dropdown_frame.grid(row=0,column=0)
        self.tx_current_name = tk.StringVar()
        self.choose_tx = ttk.Label(self.tx_dropdown_frame, text='Select Transmitter')
        self.choose_tx.grid(row=0, column=0)
        self.tx_dropdown = ttk.OptionMenu(self.tx_dropdown_frame,
                                          self.tx_current_name,
                                          None,
                                          *self.transmitternames,
                                          command=self.change_active_tx)
        self.tx_dropdown.grid(row=1, column=0)
        self.add_tx_button = ttk.Button(self.tx_dropdown_frame, text='New', command=self.open_tx_add_menu)
        self.add_tx_button.grid(row=1, column=1)

        self.tx_error = tk.StringVar()
        self.tx_error_display = ttk.Label(self.transmitterstab, textvariable=self.tx_error)

        self.txdisplayframe = ttk.Frame(self.transmitterstab)

        self.txnamelabel = ttk.Label(self.txdisplayframe, text='Name:')
        self.txnamelabel.grid(row=0, column=0)
        self.txnamedisplay = ttk.Label(self.txdisplayframe, textvariable=self.tx_current_name)
        self.txnamedisplay.grid(row=0, column=1)
        self.txnamebuttons = ttk.Frame(self.txdisplayframe)
        self.txnamebuttons.grid(row=0, column=2)
        self.edit_tx_name_button = ttk.Button(self.txnamebuttons, text='Edit', command=self.enter_tx_namechange)
        self.edit_tx_name_button.grid(row=0, column=0)

        self.save_tx_name_button = ttk.Button(self.txnamebuttons, text='Save', command=self.save_tx_namechange)
        self.cancel_tx_name_button = ttk.Button(self.txnamebuttons, text='Cancel', command=self.exit_tx_namechange)

        self.tx_new_name = tk.StringVar()
        self.tx_new_name_field = ttk.Entry(self.txdisplayframe, textvariable=self.tx_new_name, justify='center')

        self.tx_current_wavelength = tk.StringVar()
        self.wavelength_label = ttk.Label(self.txdisplayframe, text='Wavelength:')
        self.wavelength_label.grid(row=2, column=0)
        self.wavelength_menu = ttk.OptionMenu(self.txdisplayframe, self.tx_current_wavelength, None, *Wavelengths,
                                              command=self.change_tx_wavelength)
        self.wavelength_menu.grid(row=2, column=1)

        self.tx_current_max_charge = tk.StringVar()
        self.tx_current_max_charge.trace_add('write', lambda name,index,mode :
                                     self.tx_var_change(self.tx_current_max_charge, self.active_tx.set_max_charge))
        self.tx_max_charge_label = ttk.Label(self.txdisplayframe, text='Max Charge Rate (W):')
        self.tx_max_charge_label.grid(row=3, column=0)
        self.tx_max_charge_entry = ttk.Entry(self.txdisplayframe, textvariable=self.tx_current_max_charge, justify='center')
        self.tx_max_charge_entry.grid(row=3, column=1)

        self.tx_current_max_discharge = tk.StringVar()
        self.tx_current_max_discharge.trace_add('write', lambda name,index,mode :
                                     self.tx_var_change(self.tx_current_max_discharge, self.active_tx.set_max_discharge))
        self.tx_max_discharge_label = ttk.Label(self.txdisplayframe, text='Max Discharge Rate (W):')
        self.tx_max_discharge_label.grid(row=4, column=0)
        self.tx_max_discharge_entry = ttk.Entry(self.txdisplayframe, textvariable=self.tx_current_max_discharge, justify='center')
        self.tx_max_discharge_entry.grid(row=4, column=1)

        self.tx_current_init_energy = tk.StringVar()
        self.tx_current_init_energy.trace_add('write', lambda name,index,mode :
                                     self.tx_var_change(self.tx_current_init_energy, self.active_tx.set_init_charge))
        self.tx_init_energy_label = ttk.Label(self.txdisplayframe, text='Initial Energy (J):')
        self.tx_init_energy_label.grid(row=5, column=0)
        self.tx_init_energy_entry = ttk.Entry(self.txdisplayframe, textvariable=self.tx_current_init_energy, justify='center')
        self.tx_init_energy_entry.grid(row=5, column=1)

        self.tx_current_max_energy = tk.StringVar()
        self.tx_current_max_energy.trace_add('write', lambda name,index,mode :
                                     self.tx_var_change(self.tx_current_max_energy, self.active_tx.set_max_energy))
        self.tx_max_energy_label = ttk.Label(self.txdisplayframe, text='Maximum Energy (J):')
        self.tx_max_energy_label.grid(row=6, column=0)
        self.tx_max_energy_entry = ttk.Entry(self.txdisplayframe, textvariable=self.tx_current_max_energy, justify='center')
        self.tx_max_energy_entry.grid(row=6, column=1)

        self.tx_delete_current = ttk.Button(self.txdisplayframe, text='Delete Transmitter', command=self.delete_current_tx)
        self.tx_delete_current.grid(row=7, column=1)


        # Receivers tab
        self.receivers = []
        self.receivernames = []
        self.active_rx = None
        self.rx_dropdown_frame = ttk.Frame(self.receiverstab)
        self.rx_dropdown_frame.grid(row=0, column=0)
        self.rx_current_name = tk.StringVar()
        self.rx_label = ttk.Label(self.rx_dropdown_frame, text='Select Receiver')
        self.rx_label.grid(row=0, column=0)
        self.rx_current_name = tk.StringVar()
        self.rx_dropdown = ttk.OptionMenu(self.rx_dropdown_frame,
                                          self.rx_current_name,
                                          None,
                                          *self.receivernames,
                                          command=self.change_active_rx)
        self.rx_dropdown.grid(row=1, column=0)
        self.add_rx_button = ttk.Button(self.rx_dropdown_frame, text='New', command=self.open_rx_add_menu)
        self.add_rx_button.grid(row=1, column=1)

        self.rx_error = tk.StringVar()
        self.rx_error_display = ttk.Label(self.receiverstab, textvariable=self.rx_error)

        self.rxdisplay_active = False
        self.rxdisplayframe = ttk.Frame(self.receiverstab)
        self.rxtabControl = ttk.Notebook(self.rxdisplayframe)
        self.rxtabControl.grid(row=0, column=0)

        # rx primary tab
        self.rx_primary_tab = ttk.Frame(self.rxtabControl)
        self.rxtabControl.add(self.rx_primary_tab, text='Primary')

        self.changing_rx = False

        self.rxnamelabel = ttk.Label(self.rx_primary_tab, text='Name:')
        self.rxnamelabel.grid(row=0, column=0)
        self.rxnamedisplay = ttk.Label(self.rx_primary_tab, textvariable=self.rx_current_name)
        self.rxnamedisplay.grid(row=0, column=1)
        self.rxnamebuttons = ttk.Frame(self.rx_primary_tab)
        self.rxnamebuttons.grid(row=0, column=2)
        self.edit_rx_name_button = ttk.Button(self.rxnamebuttons, text='Edit', command=self.enter_rx_namechange)
        self.edit_rx_name_button.grid(row=0, column=0)

        self.save_rx_name_button = ttk.Button(self.rxnamebuttons, text='Save', command=self.save_rx_namechange)
        self.cancel_rx_name_button = ttk.Button(self.rxnamebuttons, text='Cancel', command=self.exit_rx_namechange)

        self.rx_new_name = tk.StringVar()
        self.rx_new_name_field = ttk.Entry(self.rx_primary_tab, textvariable=self.rx_new_name, justify='center')

        self.rx_distance_label = ttk.Label(self.rx_primary_tab, text='Distance:')
        self.rx_distance_label.grid(row=1, column=0)
        self.rx_distance = tk.StringVar()
        self.rx_distance.trace_add('write', lambda name,index,mode :
                                   self.rx_var_change(self.rx_distance, self.active_rx.set_distance))
        self.rx_distance_entry = ttk.Entry(self.rx_primary_tab, textvariable=self.rx_distance, justify='center')
        self.rx_distance_entry.grid(row=1, column=1)
        self.rx_distance_units = ttk.Label(self.rx_primary_tab, text='m')
        self.rx_distance_units.grid(row=1, column=2)

        self.rx_max_charge_label = ttk.Label(self.rx_primary_tab, text='Max Battery Charge:')
        self.rx_max_charge_label.grid(row=2, column=0)
        self.rx_max_charge = tk.StringVar()
        self.rx_max_charge.trace_add('write', lambda name,index,mode :
                                     self.rx_var_change(self.rx_max_charge, self.active_rx.set_max_charge))
        self.rx_max_charge_entry = ttk.Entry(self.rx_primary_tab, textvariable=self.rx_max_charge, justify='center')
        self.rx_max_charge_entry.grid(row=2, column=1)
        self.rx_max_charge_units = ttk.Label(self.rx_primary_tab, text='W')
        self.rx_max_charge_units.grid(row=2, column=2)

        self.rx_max_discharge_label = ttk.Label(self.rx_primary_tab, text='Max Battery Discharge:')
        self.rx_max_discharge_label.grid(row=3, column=0)
        self.rx_max_discharge = tk.StringVar()
        self.rx_max_discharge.trace_add('write', lambda name,index,mode :
                                        self.rx_var_change(self.rx_max_discharge, self.active_rx.set_max_discharge))
        self.rx_max_discharge_entry = ttk.Entry(self.rx_primary_tab, textvariable=self.rx_max_discharge, justify='center')
        self.rx_max_discharge_entry.grid(row=3, column=1)
        self.rx_max_discharge_units = ttk.Label(self.rx_primary_tab, text='W')
        self.rx_max_discharge_units.grid(row=3, column=2)

        self.rx_init_charge_label = ttk.Label(self.rx_primary_tab, text='Initial Charge:')
        self.rx_init_charge_label.grid(row=4, column=0)
        self.rx_init_charge = tk.StringVar()
        self.rx_init_charge.trace_add('write', lambda name,index,mode :
                                      self.rx_var_change(self.rx_init_charge, self.active_rx.set_init_charge))
        self.rx_init_charge_entry = ttk.Entry(self.rx_primary_tab, textvariable=self.rx_init_charge, justify='center')
        self.rx_init_charge_entry.grid(row=4, column=1)
        self.rx_init_charge_units = ttk.Label(self.rx_primary_tab, text='J')
        self.rx_init_charge_units.grid(row=4, column=2)

        # rx efficiency tab
        self.rx_efficiencies_tab = ttk.Frame(self.rxtabControl)
        self.rxtabControl.add(self.rx_efficiencies_tab, text='Efficiencies')

        self.rx_dcdc_conversion_label = ttk.Label(self.rx_efficiencies_tab, text='DC/DC Conversion:')
        self.rx_dcdc_conversion_label.grid(row=0, column=0)
        self.rx_dcdc_conversion = tk.StringVar()
        self.rx_dcdc_conversion.trace_add('write', lambda name,index,mode :
                                          self.rx_var_change(self.rx_dcdc_conversion, self.active_rx.set_dcdc_conversion,
                                                             0.01))
        self.rx_dcdc_conversion_entry = ttk.Entry(self.rx_efficiencies_tab, textvariable=self.rx_dcdc_conversion,
                                                  justify='center')
        self.rx_dcdc_conversion_entry.grid(row=0, column=1)
        self.rx_dcdc_conversion_units = ttk.Label(self.rx_efficiencies_tab, text='%')
        self.rx_dcdc_conversion_units.grid(row=0, column=2)

        self.rx_mppt_array_label = ttk.Label(self.rx_efficiencies_tab, text='MPPT & Array:')
        self.rx_mppt_array_label.grid(row=1, column=0)
        self.rx_mppt_array = tk.StringVar()
        self.rx_mppt_array.trace_add('write', lambda name,index,mode :
                                     self.rx_var_change(self.rx_mppt_array, self.active_rx.set_mppt_array, 0.01))
        self.rx_mppt_array_entry = ttk.Entry(self.rx_efficiencies_tab, textvariable=self.rx_mppt_array, justify='center')
        self.rx_mppt_array_entry.grid(row=1, column=1)
        self.rx_mppt_array_units = ttk.Label(self.rx_efficiencies_tab, text='%')
        self.rx_mppt_array_units.grid(row=1, column=2)

        self.rx_pv_active_area_label = ttk.Label(self.rx_efficiencies_tab, text='PV Active Area:')
        self.rx_pv_active_area_label.grid(row=2, column=0)
        self.rx_pv_active_area = tk.StringVar()
        self.rx_pv_active_area.trace_add('write', lambda name,index,mode :
                                         self.rx_var_change(self.rx_pv_active_area, self.active_rx.set_pv_active_area,
                                                             0.01))
        self.rx_pv_active_area_entry = ttk.Entry(self.rx_efficiencies_tab, textvariable=self.rx_pv_active_area,
                                                 justify='center')
        self.rx_pv_active_area_entry.grid(row=2, column=1)
        self.rx_pv_active_area_units = ttk.Label(self.rx_efficiencies_tab, text='%')
        self.rx_pv_active_area_units.grid(row=2, column=2)

        self.rx_concentrator_reflectivity_label = ttk.Label(self.rx_efficiencies_tab, text='Concentrator/Reflectivity:')
        self.rx_concentrator_reflectivity_label.grid(row=3, column=0)
        self.rx_concentrator_reflectivity = tk.StringVar()
        self.rx_concentrator_reflectivity.trace_add('write', lambda name,index,mode :
                                                    self.rx_var_change(self.rx_concentrator_reflectivity,
                                                                       self.active_rx.set_concentrator_reflectivity,
                                                                       0.01))
        self.rx_concentrator_reflectivity_entry = ttk.Entry(self.rx_efficiencies_tab,
                                                            textvariable=self.rx_concentrator_reflectivity,
                                                            justify='center')
        self.rx_concentrator_reflectivity_entry.grid(row=3, column=1)
        self.rx_concentrator_reflectivity_units = ttk.Label(self.rx_efficiencies_tab, text='%')
        self.rx_concentrator_reflectivity_units.grid(row=3, column=2)

        self.rx_pv_shadowing_label = ttk.Label(self.rx_efficiencies_tab, text='PV Shadowing:')
        self.rx_pv_shadowing_label.grid(row=4, column=0)
        self.rx_pv_shadowing = tk.StringVar()
        self.rx_pv_shadowing.trace_add('write', lambda name,index,mode :
                                         self.rx_var_change(self.rx_pv_shadowing, self.active_rx.set_pv_shadowing,
                                                             0.01))
        self.rx_pv_shadowing_entry = ttk.Entry(self.rx_efficiencies_tab, textvariable=self.rx_pv_shadowing,
                                               justify='center')
        self.rx_pv_shadowing_entry.grid(row=4, column=1)
        self.rx_pv_shadowing_units = ttk.Label(self.rx_efficiencies_tab, text='%')
        self.rx_pv_shadowing_units.grid(row=4, column=2)

        self.rx_coverglass_reflective_dirt_label = ttk.Label(self.rx_efficiencies_tab,
                                                             text='Coverglass Reflective+Dirt:')
        self.rx_coverglass_reflective_dirt_label.grid(row=5, column=0)
        self.rx_coverglass_reflective_dirt = tk.StringVar()
        self.rx_coverglass_reflective_dirt.trace_add('write', lambda name,index,mode :
                                                     self.rx_var_change(self.rx_coverglass_reflective_dirt,
                                                                        self.active_rx.set_coverglass_reflective_dirt,
                                                                        0.01))
        self.rx_coverglass_reflective_dirt_entry = ttk.Entry(self.rx_efficiencies_tab,
                                                             textvariable=self.rx_coverglass_reflective_dirt,
                                                             justify='center')
        self.rx_coverglass_reflective_dirt_entry.grid(row=5, column=1)
        self.rx_coverglass_reflective_dirt_units = ttk.Label(self.rx_efficiencies_tab,
                                                             text='%')
        self.rx_coverglass_reflective_dirt_units.grid(row=5, column=2)

        self.rx_beam_spill_label = ttk.Label(self.rx_efficiencies_tab, text='Beam Spill:')
        self.rx_beam_spill_label.grid(row=6, column=0)
        self.rx_beam_spill = tk.StringVar()
        self.rx_beam_spill.trace_add('write', lambda name,index,mode : self.rx_var_change(self.rx_beam_spill,
                                     self.active_rx.set_beam_spill,0.01))
        self.rx_beam_spill_entry = ttk.Entry(self.rx_efficiencies_tab, textvariable=self.rx_beam_spill, justify='center')
        self.rx_beam_spill_entry.grid(row=6, column=1)
        self.rx_beam_spill_units = ttk.Label(self.rx_efficiencies_tab, text='%')
        self.rx_beam_spill_units.grid(row=6, column=2)

        # rx scintillation tab
        self.rx_scintillation_tab = ttk.Frame(self.rxtabControl)
        self.rxtabControl.add(self.rx_scintillation_tab, text='Scintillation')

        self.rx_power_per_cell_label = ttk.Label(self.rx_scintillation_tab, text='Power Per Cell:')
        self.rx_power_per_cell_label.grid(row=0, column=0)
        self.rx_power_per_cell = tk.StringVar()
        self.rx_power_per_cell.trace_add('write', lambda name,index,mode :
                                         self.rx_var_change(self.rx_power_per_cell,
                                                            self.active_rx.set_power_per_cell))
        self.rx_power_per_cell_entry = ttk.Entry(self.rx_scintillation_tab, textvariable=self.rx_power_per_cell,
                                                 justify='center')
        self.rx_power_per_cell_entry.grid(row=0, column=1)
        self.rx_power_per_cell_units = ttk.Label(self.rx_scintillation_tab, text='W')
        self.rx_power_per_cell_units.grid(row=0, column=2)

        self.rx_v_mpp_label = ttk.Label(self.rx_scintillation_tab, text='V mpp:')
        self.rx_v_mpp_label.grid(row=1, column=0)
        self.rx_v_mpp = tk.StringVar()
        self.rx_v_mpp.trace_add('write', lambda name,index,mode :
                                self.rx_var_change(self.rx_v_mpp, self.active_rx.set_v_mpp))
        self.rx_v_mpp_entry = ttk.Entry(self.rx_scintillation_tab, textvariable=self.rx_v_mpp, justify='center')
        self.rx_v_mpp_entry.grid(row=1, column=1)
        self.rx_v_mpp_units = ttk.Label(self.rx_scintillation_tab, text='V')
        self.rx_v_mpp_units.grid(row=1, column=2)

        self.rx_diam_label = ttk.Label(self.rx_scintillation_tab, text='RX Diameter:')
        self.rx_diam_label.grid(row=2, column=0)
        self.rx_diam = tk.StringVar()
        self.rx_diam.trace_add('write', lambda name,index,mode :
                               self.rx_var_change(self.rx_diam, self.active_rx.set_rx_diam, 0.01))
        self.rx_diam_entry = ttk.Entry(self.rx_scintillation_tab, textvariable=self.rx_diam, justify='center')
        self.rx_diam_entry.grid(row=2, column=1)
        self.rx_diam_units = ttk.Label(self.rx_scintillation_tab, text='cm')
        self.rx_diam_units.grid(row=2, column=2)

        self.rx_f_pv_label = ttk.Label(self.rx_scintillation_tab, text='f PV:')
        self.rx_f_pv_label.grid(row=3, column=0)
        self.rx_f_pv = tk.StringVar()
        self.rx_f_pv.trace_add('write', lambda name,index,mode :
                               self.rx_var_change(self.rx_f_pv, self.active_rx.set_f_pv))
        self.rx_f_pv_entry = ttk.Entry(self.rx_scintillation_tab, textvariable=self.rx_f_pv, justify='center')
        self.rx_f_pv_entry.grid(row=3, column=1)

        self.rx_i_nom_label = ttk.Label(self.rx_scintillation_tab, text='I nom')
        self.rx_i_nom_label.grid(row=4, column=0)
        self.rx_i_nom = tk.StringVar()
        self.rx_i_nom.trace_add('write', lambda name,index,mode :
                               self.rx_var_change(self.rx_i_nom, self.active_rx.set_i_nom))
        self.rx_i_nom_entry = ttk.Entry(self.rx_scintillation_tab, textvariable=self.rx_i_nom, justify='center')
        self.rx_i_nom_entry.grid(row=4, column=1)
        self.rx_i_nom_units = ttk.Label(self.rx_scintillation_tab, text='A')
        self.rx_i_nom_units.grid(row=4, column=2)

        self.rx_delete_button = ttk.Button(self.rxdisplayframe, text='Delete Receiver', command=self.delete_current_rx)
        self.rx_delete_button.grid(row=1, column=0)

        # Atmospheres tab
        self.atmospheres = []
        self.atmospherenames = []
        self.atmdisplay_active = False
        self.changing_atm = False
        self.atm_dropdown_frame = ttk.Frame(self.atmospherestab)
        self.atm_dropdown_frame.grid(row=0, column=0)
        self.atm_current_name = tk.StringVar()
        self.atm_label = ttk.Label(self.atm_dropdown_frame, text='Select Atmosphere')
        self.atm_label.grid(row=0, column=0)
        self.atm_dropdown = ttk.OptionMenu(self.atm_dropdown_frame, self.atm_current_name, None,
                                           *self.atmospherenames, command=self.change_active_atm)
        self.atm_dropdown.grid(row=1, column=0)
        self.add_atm_button = ttk.Button(self.atm_dropdown_frame, text='New', command=self.open_atm_add_menu)
        self.add_atm_button.grid(row=1, column=1)

        self.atm_error = tk.StringVar()
        self.atm_error_display = ttk.Label(self.atmospherestab, textvariable=self.atm_error)

        self.active_atm = None
        self.atmdisplay_active = False
        self.atmdisplayframe = ttk.Frame(self.atmospherestab)

        self.atmnamelabel = ttk.Label(self.atmdisplayframe, text='Name:')
        self.atmnamelabel.grid(row=0, column=0)
        self.atmnamedisplay = ttk.Label(self.atmdisplayframe, textvariable=self.atm_current_name)
        self.atmnamedisplay.grid(row=0, column=1)
        self.atmnamebuttons = ttk.Frame(self.atmdisplayframe)
        self.atmnamebuttons.grid(row=0, column=2)
        self.edit_atm_name_button = ttk.Button(self.atmnamebuttons, text='Edit', command=self.enter_atm_namechange)
        self.edit_atm_name_button.grid(row=0, column=0)

        self.save_atm_name_button = ttk.Button(self.atmnamebuttons, text='Save', command=self.save_atm_namechange)
        self.cancel_atm_name_button = ttk.Button(self.atmnamebuttons, text='Cancel', command=self.exit_atm_namechange)

        self.atm_new_name = tk.StringVar()
        self.atm_new_name_field = ttk.Entry(self.atmdisplayframe, textvariable=self.atm_new_name, justify='center')


        self.atm_cn2 = tk.StringVar()
        self.atm_cn2.trace_add('write', lambda name,index,mode : self.atm_var_change(self.atm_cn2,
                                     self.active_atm.set_cn2))
        self.atm_cn2_seriesmode = tk.IntVar()
        self.atm_cn2_seriesmode.set(0)
        self.atm_precipitation = tk.StringVar()
        self.atm_precipitation.trace_add('write', lambda name,index,mode : self.atm_var_change(self.atm_precipitation,
                                     self.active_atm.set_precipitation))
        self.atm_precipitation_seriesmode = tk.IntVar()
        self.atm_precipitation_seriesmode.set(0)
        self.atm_temperature = tk.StringVar()
        self.atm_temperature.trace_add('write', lambda name,index,mode : self.atm_var_change(self.atm_cn2,
                                     self.active_atm.set_temperature))
        self.atm_temperature_seriesmode = tk.IntVar()
        self.atm_temperature_seriesmode.set(0)
        self.atm_visibility = tk.StringVar()
        self.atm_visibility.trace_add('write', lambda name,index,mode : self.atm_var_change(self.atm_visibility,
                                      self.active_atm.set_visibility))
        self.atm_visibility_seriesmode = tk.IntVar()
        self.atm_visibility_seriesmode.set(0)

        self.atm_cn2_label = ttk.Label(self.atmdisplayframe, text='Structure Constant (m^-2/3):')
        self.atm_cn2_label.grid(row=1, column=0),
        self.atm_cn2_field = ttk.Entry(self.atmdisplayframe, textvariable=self.atm_cn2, justify='center')
        self.atm_cn2_field.grid(row=1, column=1)
        self.atm_cn2_changemode = ttk.Checkbutton(self.atmdisplayframe, text='Use Time Series',
                                                  variable=self.atm_cn2_seriesmode, command=self.atm_cn2_toggle)
        self.atm_cn2_changemode.grid(row=1, column=2)

        self.atm_cn2_ts = tk.StringVar()
        self.atm_cn2_ts_dropdown = ttk.OptionMenu(self.atmdisplayframe, self.atm_cn2_ts, None, *self.timeseriesnames,
                                                  command=self.atm_change_cn2_ts)

        self.atm_precipitation_label = ttk.Label(self.atmdisplayframe, text='Precipitation (mm/h):')
        self.atm_precipitation_label.grid(row=2, column=0)
        self.atm_precipitation_field = ttk.Entry(self.atmdisplayframe, textvariable=self.atm_precipitation, justify='center')
        self.atm_precipitation_field.grid(row=2, column=1)
        self.atm_precipitation_changemode = ttk.Checkbutton(self.atmdisplayframe, text='Use Time Series',
                                                            variable=self.atm_precipitation_seriesmode, command=self.atm_precipitation_toggle)
        self.atm_precipitation_changemode.grid(row=2, column=2)

        self.atm_precipitation_ts = tk.StringVar()
        self.atm_precipitation_ts_dropdown = ttk.OptionMenu(self.atmdisplayframe, self.atm_precipitation_ts, None, *self.timeseriesnames,
                                                            command=self.atm_change_precipitation_ts)

        self.atm_temperature_label = ttk.Label(self.atmdisplayframe, text='Temperature (C):')
        self.atm_temperature_label.grid(row=3, column=0)
        self.atm_temperature_field = ttk.Entry(self.atmdisplayframe, textvariable=self.atm_temperature, justify='center')
        self.atm_temperature_field.grid(row=3, column=1)
        self.atm_temperature_changemode = ttk.Checkbutton(self.atmdisplayframe, text='Use Time Series',
                                                          variable=self.atm_temperature_seriesmode, command=self.atm_temperature_toggle)
        self.atm_temperature_changemode.grid(row=3, column=2)

        self.atm_temperature_ts = tk.StringVar()
        self.atm_temperature_ts_dropdown = ttk.OptionMenu(self.atmdisplayframe, self.atm_temperature_ts, None, *self.timeseriesnames,
                                                          command=self.atm_change_temperature_ts)

        self.atm_visibility_label = ttk.Label(self.atmdisplayframe, text='Visibility (km):')
        self.atm_visibility_label.grid(row=4, column=0)
        self.atm_visibility_field = ttk.Entry(self.atmdisplayframe, textvariable=self.atm_visibility, justify='center')
        self.atm_visibility_field.grid(row=4, column=1)
        self.atm_visibility_changemode = ttk.Checkbutton(self.atmdisplayframe, text='Use Time Series',
                                                         variable=self.atm_visibility_seriesmode,command=self.atm_visibility_toggle)
        self.atm_visibility_changemode.grid(row=4, column=2)

        self.atm_visibility_ts = tk.StringVar()
        self.atm_visibility_ts_dropdown = ttk.OptionMenu(self.atmdisplayframe, self.atm_visibility_ts, None, *self.timeseriesnames,
                                                         command=self.atm_change_temperature_ts)
        self.atm_delete_button = ttk.Button(self.atmdisplayframe, text='Delete Atmosphere', command=self.delete_current_atm)
        self.atm_delete_button.grid(row=5, column=1)

        # Calculations tab
        self.calculations_frame = ttk.Frame(self.runcalculationtab)
        self.calculations_frame.grid(row=0, column=1)

        self.laser_ts = tk.StringVar()
        self.laser_ts_label = ttk.Label(self.calculations_frame, text='Input Power Time Series (W):')
        self.laser_ts_dropdown = ttk.OptionMenu(self.calculations_frame,
                                                self.laser_ts,
                                                 None,
                                                 *self.timeseriesnames)
        self.laser_ts_label.grid(row=0, column=0)
        self.laser_ts_dropdown.grid(row=0, column=1)

        self.load_ts = tk.StringVar()
        self.load_ts_label = ttk.Label(self.calculations_frame, text='Load Power Time Series (W):')
        self.load_ts_dropdown = ttk.OptionMenu(self.calculations_frame,
                                                self.load_ts,
                                                 None,
                                                 *self.timeseriesnames)
        self.load_ts_label.grid(row=1, column=0)
        self.load_ts_dropdown.grid(row=1, column=1)

        self.calculation_transmitter = tk.StringVar()
        self.calc_tx_label = ttk.Label(self.calculations_frame, text='Transmitter:')
        self.calc_tx_dropdown = ttk.OptionMenu(self.calculations_frame, self.calculation_transmitter, None,
                                                    *self.transmitternames)
        self.calc_tx_label.grid(row=2,column=0)
        self.calc_tx_dropdown.grid(row=2, column=1)

        self.calculation_receiver = tk.StringVar()
        self.receiver_label = ttk.Label(self.calculations_frame, text='Receiver:')
        self.calc_rx_dropdown = ttk.OptionMenu(self.calculations_frame, self.calculation_receiver, None,
                                               *self.receivernames)
        self.receiver_label.grid(row=3, column=0)
        self.calc_rx_dropdown.grid(row=3, column=1)

        self.calculation_atmosphere = tk.StringVar()
        self.atmosphere_receiver = tk.StringVar()
        self.atmosphere_label = ttk.Label(self.calculations_frame, text='Atmosphere:')
        self.calc_atm_dropdown = ttk.OptionMenu(self.calculations_frame, self.atmosphere_receiver, None,
                                                *self.atmospherenames)
        self.atmosphere_label.grid(row=4, column=0)
        self.calc_atm_dropdown.grid(row=4, column=1)

        self.calculation_button = ttk.Button(self.calculations_frame, text='Run Calculation', command=self.do_calc)
        self.calculation_button.grid(row=5, column=1)

        self.save_output_button = ttk.Button(self.calculations_frame, text='Save Outputs',
                                             command=self.open_calc_add_menu, state='disabled')
        self.save_output_button.grid(row=6, column=1)
        #calculation plots
        self.is_calc_plot = False
        self.calc_plot_frame = ttk.Frame(self.runcalculationtab)

        self.calc_rows = 4
        self.calc_cols = 2

        self.calc_fig, self.calc_ax = plt.subplots(self.calc_rows, self.calc_cols)
        self.calc_fig.patch.set_facecolor("#F0F0F0")
        self.calc_x = 8
        self.calc_y = 5
        self.calc_fig.set_size_inches(self.calc_x, self.calc_y)
        self.calc_canvas = FigureCanvasTkAgg(self.calc_fig, master=self.calc_plot_frame)  # A tk.DrawingArea.
#       self.calc_canvas.mpl_connect("key_press_event", self.on_key_press)
        self.calc_toolbar = NavigationToolbar2Tk(self.calc_canvas, self.calc_plot_frame, pack_toolbar=False)
        self.calc_toolbar.update()
        self.calc_canvas.get_tk_widget().grid(row=0, column=0)
        self.calc_toolbar.grid(row=1, column=0)

        self.calc_buttonbar = ttk.Frame(self.calc_plot_frame)
        self.calc_buttonbar.grid(row=2, column=0)
        self.calc_shrink = ttk.Button(self.calc_buttonbar, text='-', command=self.calc_plot_shrink)
        self.calc_shrink.grid(row=0, column=0)
        self.calc_grow = ttk.Button(self.calc_buttonbar, text='+', command=self.calc_plot_grow)
        self.calc_grow.grid(row=0, column=1)

        self.calc_rx_ts = None
        self.calc_load_ts = None
        self.calc_battery_ts = None

        #below everything, export and import data options
        self.export_import_frame = ttk.Frame(self)
        self.export_import_frame.grid(row=1, column=0)
        self.export_data_button = ttk.Button(self.export_import_frame, text='Export Data', command=self.open_export_menu)
        self.export_data_button.grid(row=0, column=0)
        self.import_data_button = ttk.Button(self.export_import_frame, text='Import Data', command=self.import_data)
        self.import_data_button.grid(row=0, column=1)

    def on_key_press(self):
        pass



#GENERAL FUNCTIONS
    def open_export_menu(self):
        #create title:
        ts = time.gmtime()
        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S", ts)
        title = "tsm_" + timestamp + ".csv"


        win = tk.Toplevel()
        win.wm_title("Export to CSV")

        windowlabel = ttk.Label(win, text='Filename:')
        windowlabel.grid(row=0, column=0)

        optionframe1 = ttk.Frame(win)
        optionframe1.grid(row=1, column=0)
        #namelabel = ttk.Label(optionframe1, text='Filename:')
        #namelabel.grid(row=0, column=0)
        nametext = tk.StringVar()
        nametext.set(title)

        namefield = ttk.Entry(optionframe1, textvariable=nametext, justify='center', width=30)
        namefield.grid(row=0, column=1)

        errorframe = ttk.Frame(win)
        #errorframe.grid(row=2, column=0)
        errortext = tk.StringVar()
        errorlabel = tk.Label(errorframe, textvariable=errortext)
        #errorlabel.grid(row=0, column=0)

        buttonframe = ttk.Frame(win)
        buttonframe.grid(row=2, column=0)
        cancelbutton = ttk.Button(buttonframe, text='Cancel', command=win.destroy)
        cancelbutton.grid(row=0, column=1)
        exportbutton = ttk.Button(buttonframe, text='Export',
                                command=lambda : self.export_data(nametext.get(), win))
        exportbutton.grid(row=0, column=0)
        return
    def export_data(self, filename, win):
        export_text = ""

        #transmitter handling
        transmitter_count = np.size(self.transmitters)
        export_text += f"Transmitters,{transmitter_count}\n"
        export_text += "Name,Wavelength,MaxCharge,MaxDischarge,InitEnergy,MaxEnergy\n"
        for transmitter in self.transmitters:
            name = transmitter.name
            wavelength = Wavelengths[transmitter.type]
            maxcharge = transmitter.max_charge_rate
            maxdischarge = transmitter.max_discharge_rate
            initenergy = transmitter.initial_charge
            maxenergy = transmitter.max_energy
            export_text += f"{name},{wavelength},{maxcharge},{maxdischarge},{initenergy},{maxenergy}\n"

        #receiver handling
        receiver_count = np.size(self.receivers)
        export_text += f"Receivers,{receiver_count}\n"
        export_text += "Name,Distance,MaxCharge,MaxDischarge,InitCharge,DCDCConv,MPPTArray,PVActiveArea,ConcRefl,"
        export_text += "PVShadow,CoverReflDirt,BeamSpill,PowerPerCell,Vmpp,RXDiam,fPV,Inom\n"
        for receiver in self.receivers:
            export_text += f"{receiver.name},"
            export_text += f"{receiver.distance},"
            export_text += f"{receiver.max_charge_rate},"
            export_text += f"{receiver.max_discharge_rate},"
            export_text += f"{receiver.initial_charge},"
            export_text += f"{receiver.dcdc_conversion},"
            export_text += f"{receiver.mppt_array_efficiency},"
            export_text += f"{receiver.pv_active_area_factor},"
            export_text += f"{receiver.concentrator_reflectivity_losses},"
            export_text += f"{receiver.pv_shadowing},"
            export_text += f"{receiver.coverglass_reflective_dirt_factor},"
            export_text += f"{receiver.beam_spill_factor},"
            export_text += f"{receiver.power_per_cell},"
            export_text += f"{receiver.v_mpp},"
            export_text += f"{receiver.rx_diam},"
            export_text += f"{receiver.f_pv},"
            export_text += f"{receiver.i_nom}\n"

        #atmosphere handling
        atmosphere_count = np.size(self.atmospheres)
        export_text += f"Atmospheres,{atmosphere_count}\n"
        export_text += "Name,Cn2,Precip,Temp,Vis,Cn2Series,PrecipSeries,TempSeries,VisSeries,Cn2Mode,PrecipMode," \
                       "TempMode,VisMode\n"
        for atmosphere in self.atmospheres:
            export_text += f"{atmosphere.name},"
            export_text += f"{atmosphere.structure_constant},{atmosphere.precipitation},"
            export_text += f"{atmosphere.temperature},{atmosphere.visibility},"
            export_text += f"{atmosphere.cn2_series},{atmosphere.precipitation_series},"
            export_text += f"{atmosphere.temperature_series},{atmosphere.visibility_series},"
            export_text += f"{atmosphere.cn2_seriesmode},{atmosphere.precipitation_seriesmode},"
            export_text += f"{atmosphere.temperature_seriesmode},{atmosphere.visibility_seriesmode}\n"

        #time series handling
        time_series_count = np.size(self.timeseries)
        export_text += f"TimeSeries,{time_series_count}"
        param_list = []
        label_list = []
        first_series = True
        data_array = np.array([])
        for timeseries in self.timeseries:
            name = timeseries.name
            sample_time = timeseries.sample_time
            ylabel = timeseries.ylabel

            param_list.append(sample_time)
            param_list.append(ylabel)
            label_list.append(name+"TIME")
            label_list.append(name)
            data = timeseries.data
            new_rows = np.size(data)
            times = sample_time * np.arange(new_rows)

            new_data = np.concatenate((np.expand_dims(times, axis=1),np.expand_dims(data,axis=1)),axis=1)
            new_data = new_data.astype('object')

            if first_series:
                data_array = new_data
                first_series = False
            else:
                rows, cols = np.shape(data_array)
                if new_rows > rows:
                    data_array = np.concatenate((data_array,np.full((new_rows - rows, cols),"")), axis=0)
                elif rows > new_rows:
                    new_data = np.concatenate((new_data, np.full((rows - new_rows,2),"")),axis=0)
                data_array = np.concatenate((data_array, new_data), axis=1)

        if time_series_count > 0:
            export_text += "\n" + list_to_csv_row(param_list) + "\n"
            export_text += list_to_csv_row(label_list) + "\n"

        if np.size(data_array) > 0:
            for row in data_array[:-1,:]:
                export_text += list_to_csv_row(row.tolist()) + "\n"
            export_text += list_to_csv_row(data_array[-1].tolist())


        # write to file
        csv_file = open(filename, "w")
        csv_file.write(export_text)
        csv_file.close()
        win.destroy()

    def reset_data(self):
        self.timeseries = []
        self.timeseriesnames = []
        self.transmitters = []
        self.transmitternames = []
        self.receivers = []
        self.receivernames = []
        self.atmospheres = []
        self.atmospherenames = []

    def refresh_reload_all(self):
        if len(self.timeseries) > 0:
            self.reload_ts_list()
            self.complete_ts_action()
        if len(self.transmitters) > 0:
            self.reload_tx_list()
            self.complete_tx_action()
        if len(self.receivers) > 0:
            self.reload_rx_list()
            self.complete_rx_action()
        if len(self.atmospheres) > 0:
            self.reload_atm_list()
            self.complete_atm_action()

    def import_data(self):
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Select File",
                                              filetypes=(("CSV files",
                                                          "*.csv*"),
                                                         ("all files",
                                                          "*.*")))
        if filename == "":
            return
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            rows = []
            maxsize = 0
            i = 0
            transmitter_row = 0
            receiver_row = 0
            atmosphere_row = 0
            time_series_row = 0
            for row in reader:
                rows.append(row)
                rowsize = len(row)
                if rowsize > maxsize:
                    maxsize = rowsize
                if row[0] == "Transmitters":
                    transmitter_row = i
                elif row[0] == "Receivers":
                    receiver_row = i
                elif row[0] == "Atmospheres":
                    atmosphere_row = i
                elif row[0] == "TimeSeries":
                    time_series_row = i
                i += 1
        transmitter_count = int(rows[transmitter_row][1])
        receiver_count = int(rows[receiver_row][1])
        atmosphere_count = int(rows[atmosphere_row][1])
        time_series_count = int(rows[time_series_row][1])

        transmitter_params = rows[transmitter_row + 1]
        receiver_params = rows[receiver_row + 1]
        atmosphere_params = rows[atmosphere_row + 1]

        if time_series_count > 0:
            time_series_params1 = rows[time_series_row + 1]
            time_series_params2 = rows[time_series_row + 2]

        transmitters = rows[transmitter_row + 2:receiver_row]
        receivers = rows[receiver_row + 2:atmosphere_row]
        atmospheres = rows[atmosphere_row + 2:time_series_row]
        if time_series_count > 0:
            time_series = rows[time_series_row + 3:]

        #delete all current data
        self.reset_data()

        #load transmitters
        if transmitter_count > 0:
            idx_name = transmitter_params.index("Name")
            idx_wavelength = transmitter_params.index("Wavelength")
            if "MaxCharge" in transmitter_params:
                idx_maxcharge = transmitter_params.index("MaxCharge")
            else:
                idx_maxcharge = None
            if "MaxDischarge" in transmitter_params:
                idx_maxdischarge = transmitter_params.index("MaxDischarge")
            else:
                idx_maxdischarge = None
            if "InitEnergy" in transmitter_params:
                idx_initenergy = transmitter_params.index("InitEnergy")
            else:
                idx_initenergy = None
            if "MaxEnergy" in transmitter_params:
                idx_maxenergy = transmitter_params.index("MaxEnergy")
            else:
                idx_maxenergy = None

            for transmitter in transmitters:
                name = transmitter[idx_name]
                wavelength = transmitter[idx_wavelength]
                type = Wavelength_Dict[wavelength]
                if idx_maxcharge == None:
                    maxcharge = DEFAULT_TX_MAX_CHARGE
                else:
                    maxcharge = float(transmitter[idx_maxcharge])
                if idx_maxdischarge == None:
                    maxdischarge = DEFAULT_TX_MAX_DISCHARGE
                else:
                    maxdischarge = float(transmitter[idx_maxdischarge])
                if idx_initenergy == None:
                    initenergy = DEFAULT_TX_INIT_ENERGY
                else:
                    initenergy = float(transmitter[idx_initenergy])
                if idx_maxenergy == None:
                    maxenergy = DEFAULT_TX_MAX_ENERGY
                else:
                    maxenergy = float(transmitter[idx_maxenergy])
                new_tx = Laser(name, type, maxcharge, maxdischarge, initenergy, maxenergy)
                self.transmitters.append(new_tx)
                self.transmitternames.append(name)
            self.change_active_tx(self.transmitternames[0])
            if not self.txdisplay_active:
                self.txdisplayframe.grid(row=2, column=0)
                self.txdisplay_active = True
                self.calculation_transmitter.set(self.active_tx.name)

        #load receivers
        if receiver_count > 0:
            idx_name = receiver_params.index("Name")
            idx_distance = receiver_params.index("Distance")
            idx_maxcharge = receiver_params.index("MaxCharge")
            idx_maxdischarge = receiver_params.index("MaxDischarge")
            idx_initcharge = receiver_params.index("InitCharge")
            idx_dcdcconv = receiver_params.index("DCDCConv")
            idx_mpptarray = receiver_params.index("MPPTArray")
            idx_pvactivearea = receiver_params.index("PVActiveArea")
            idx_concrefl = receiver_params.index("ConcRefl")
            idx_pvshadow = receiver_params.index("PVShadow")
            idx_coverrefldirt = receiver_params.index("CoverReflDirt")
            idx_beamspill = receiver_params.index("BeamSpill")
            idx_powerpercell = receiver_params.index("PowerPerCell")
            idx_vmpp = receiver_params.index("Vmpp")
            idx_rxdiam = receiver_params.index("RXDiam")
            idx_fpv = receiver_params.index("fPV")
            idx_inom = receiver_params.index("Inom")
            for receiver in receivers:
                name = receiver[idx_name]
                distance = float(receiver[idx_distance])
                maxcharge = float(receiver[idx_maxcharge])
                maxdischarge = float(receiver[idx_maxdischarge])
                initcharge = float(receiver[idx_initcharge])
                dcdcconv = float(receiver[idx_dcdcconv])
                mpptarray = float(receiver[idx_mpptarray])
                pvactivearea = float(receiver[idx_pvactivearea])
                concrefl = float(receiver[idx_concrefl])
                pvshadow = float(receiver[idx_pvshadow])
                coverrefldirt = float(receiver[idx_coverrefldirt])
                beamspill = float(receiver[idx_beamspill])
                powerpercell = float(receiver[idx_powerpercell])
                vmpp = float(receiver[idx_vmpp])
                rxdiam = float(receiver[idx_rxdiam])
                fpv = float(receiver[idx_fpv])
                inom = float(receiver[idx_inom])

                new_rx = Receiver(name, distance, maxcharge, maxdischarge, initcharge)
                new_rx.set_dcdc_conversion(dcdcconv)
                new_rx.set_mppt_array(mpptarray)
                new_rx.set_pv_active_area(pvactivearea)
                new_rx.set_concentrator_reflectivity(concrefl)
                new_rx.set_pv_shadowing(pvshadow)
                new_rx.set_coverglass_reflective_dirt(coverrefldirt)
                new_rx.set_beam_spill(beamspill)
                new_rx.set_power_per_cell(powerpercell)
                new_rx.set_v_mpp(vmpp)
                new_rx.set_rx_diam(rxdiam)
                new_rx.set_f_pv(fpv)
                new_rx.set_i_nom(inom)

                self.receivernames.append(name)
                self.receivers.append(new_rx)
            self.change_active_rx(self.receivernames[0])
            if not self.rxdisplay_active:
                self.rxdisplayframe.grid(row=2, column=0)
                self.rxdisplay_active = True
                self.calculation_receiver.set(self.active_rx.name)

        #load atmospheres
        if atmosphere_count > 0:
            idx_name = atmosphere_params.index("Name")
            idx_cn2 = atmosphere_params.index("Cn2")
            idx_precip = atmosphere_params.index("Precip")
            idx_temp = atmosphere_params.index("Temp")
            idx_vis = atmosphere_params.index("Vis")
            idx_cn2series = atmosphere_params.index("Cn2Series")
            idx_precipseries = atmosphere_params.index("PrecipSeries")
            idx_tempseries = atmosphere_params.index("TempSeries")
            idx_visseries = atmosphere_params.index("VisSeries")
            idx_cn2mode = atmosphere_params.index("Cn2Mode")
            idx_precipmode = atmosphere_params.index("PrecipMode")
            idx_tempmode = atmosphere_params.index("TempMode")
            idx_vismode = atmosphere_params.index("VisMode")
            for atmosphere in atmospheres:
                name = atmosphere[idx_name]
                cn2 = float(atmosphere[idx_cn2])
                precip = float(atmosphere[idx_precip])
                temp = float(atmosphere[idx_temp])
                vis = float(atmosphere[idx_vis])
                cn2series = atmosphere[idx_cn2series]
                if cn2series == "None":
                    cn2series = None
                precipseries = atmosphere[idx_precipseries]
                if precipseries == "None":
                    precipseries = None
                tempseries = atmosphere[idx_tempseries]
                if tempseries == "None":
                    tempseries = None
                visseries = atmosphere[idx_visseries]
                if visseries == "None":
                    visseries = None
                cn2mode = int(atmosphere[idx_cn2mode])
                precipmode = int(atmosphere[idx_precipmode])
                tempmode = int(atmosphere[idx_tempmode])
                vismode = int(atmosphere[idx_vismode])

                new_atm = Atmosphere(name,cn2,precip,temp,vis)
                new_atm.cn2_series = cn2series
                new_atm.precipitation_series = precipseries
                new_atm.temperature_series = tempseries
                new_atm.visibility_series = visseries
                new_atm.cn2_seriesmode = cn2mode
                new_atm.precipitation_seriesmode = precipmode
                new_atm.temperature_seriesmode = tempmode
                new_atm.visibility_seriesmode = vismode

                self.atmospherenames.append(name)
                self.atmospheres.append(new_atm)
            self.change_active_atm(self.atmospherenames[0])
            if not self.atmdisplay_active:
                self.atmdisplayframe.grid(row=2, column=0)
                self.atmdisplay_active = True
                self.calculation_atmosphere.set(self.active_atm.name)

        #load time series
        if time_series_count > 0:
            expected_cols = 2*time_series_count
            for row in time_series:
                cols = len(row)
                if cols < expected_cols:
                    row.append(np.full(expected_cols - cols, "").tolist())
            time_series = np.transpose(np.array(time_series))
            for i in np.arange(time_series_count):
                name = time_series_params2[1 + 2*i]
                sample_time = float(time_series_params1[2*i])
                ylabel = time_series_params1[1 + 2*i]
                if np.size(time_series) > 0:
                    data = time_series[1 + 2*i]
                    as_list = data.tolist()
                    if "" in as_list:
                        endpoint = as_list.index("")
                        new_data = data[:endpoint].astype(float)
                    else:
                        new_data = data.astype(float)
                    new_ts = TimeSeries(name,new_data,sample_time,ylabel)
                    new_ts.sequences.append(new_data)
                else:
                    new_ts = TimeSeries(name,sample_time=sample_time,ylabel=ylabel)
                self.timeseriesnames.append(name)
                self.timeseries.append(new_ts)

            self.change_active_ts(self.timeseriesnames[0])
            if not self.tsdisplay_active:
                self.tsdisplayframe.grid(row=2, column=0)
                self.tsdisplay_active = True
                self.laser_ts.set(self.active_ts.name)
                self.load_ts.set(self.active_ts.name)

        #refresh and reload lists
        self.refresh_reload_all()


#TS FUNCTIONS

    def add_pulse(self):
        #first, error checks
        try:
            amplitude = float(self.pulse_amplitude.get())
        except ValueError:
            self.show_ts_error("Error: Invalid amplitude.")
            return
        try:
            period = float(self.pulse_period.get())
        except ValueError:
            self.show_ts_error("Error: Invalid period.")
            return
        if period <= 0:
            self.show_ts_error("Error: Period must be a positive value.")
            return
        try:
            duty_cycle = float(self.pulse_duty_cycle.get())/100
        except ValueError:
            self.show_ts_error("Error: Invalid duty cycle.")
            return
        if duty_cycle < 0 or duty_cycle > 1:
            self.show_ts_error("Error: Duty cycle must be between 0 and 100%.")
            return
        try:
            duration = float(self.pulse_duration.get())
        except ValueError:
            self.show_ts_error("Error: Invalid duration.")
            return
        if duration < 0:
            self.show_ts_error("Error: Duration must be a non-negative value.")
            return

        #now, actually create sequence
        sample_time = self.active_ts.sample_time
        full_cycles = np.floor(duration/period)
        remainder = np.round(duration % period / sample_time)
        active = np.round(duty_cycle * period / sample_time)
        period_integer = np.round(period / sample_time)
        inactive = period_integer - active



        if full_cycles == 0:
            if remainder == 0:
                return
            elif active >= remainder:
                sequence = amplitude * np.ones(int(remainder))
            else:
                sequence = amplitude * np.ones(int(active))
                append = np.zeros(int(remainder - active))
                sequence = np.concatenate((sequence, append))
        else:
            parts = []
            for i in np.arange(full_cycles):
                active_sequence = amplitude * np.ones(int(active))
                parts.append(active_sequence)
                inactive_sequence = amplitude * np.zeros(int(inactive))
                parts.append(inactive_sequence)
            if active >= remainder:
                tail = amplitude * np.ones(int(remainder))
                parts.append(tail)
            else:
                active_sequence = amplitude * np.ones(int(active))
                parts.append(active_sequence)
                tail = np.zeros(int(remainder - active))
                parts.append(tail)
            sequence = np.concatenate(tuple(parts))

        #now, add sequence to time series
        self.active_ts.append_right(sequence)

        self.complete_ts_action()
        return



    def add_linear(self):
        # first, error checks
        try:
            init = float(self.linear_init.get())
        except ValueError:
            self.show_ts_error("Error: Invalid initial amplitude.")
            return
        try:
            final = float(self.linear_final.get())
        except ValueError:
            self.show_ts_error("Error: Invalid final amplitude.")
            return
        try:
            duration = float(self.linear_duration.get())
        except ValueError:
            self.show_ts_error("Error: Invalid duration.")
            return
        if duration < 0:
            self.show_ts_error("Error: Duration must be a non-negative value.")
            return

        # now, build sequence
        if duration == 0:
            return
        sample_time = self.active_ts.sample_time
        no_samples = int(duration/sample_time)
        sequence = np.linspace(init, final, no_samples)

        #and append
        self.active_ts.append_right(sequence)
        self.complete_ts_action()
        return

    def add_downtime(self):
        #validity checks
        try:
            t_from = float(self.downtime_from.get())
        except ValueError:
            self.show_ts_error("Error: Invalid from time.")
            return
        try:
            t_to = float(self.downtime_to.get())
        except ValueError:
            self.show_ts_error("Error: Invalid to time.")
            return
        if t_from >= t_to:
            self.show_ts_error("Error: From time must be less than to time.")
            return
        if t_from < 0:
            self.show_ts_error("Error: Negative times not allowed.")
            return

        sample_time = self.active_ts.sample_time
        idx_from = int(round(t_from/sample_time))
        idx_to = int(round(t_to/sample_time))
        if idx_to > np.size(self.active_ts.data):
            self.show_ts_error("Error: Downtime interval outside allowed range.")

        self.active_ts.add_downtime(idx_from, idx_to)
        self.complete_ts_action()
        return

    def remove_last(self):
        if self.active_ts.empty_check():
            return
        self.active_ts.remove_sequence_right()
        self.complete_ts_action()
        return
    def clear_all(self):
        if self.active_ts.empty_check():
            return
        self.active_ts.clear_data()
        self.complete_ts_action()
        return

    def open_ts_add_menu(self):
        win = tk.Toplevel()
        win.wm_title("New Time Series")

        windowlabel = ttk.Label(win, text='New Time Series')
        windowlabel.grid(row=0, column=0)

        optionframe1 = ttk.Frame(win)
        optionframe1.grid(row=1, column=0)
        namelabel = ttk.Label(optionframe1, text='Name:')
        namelabel.grid(row=0, column=0)
        nametext = tk.StringVar()
        i=1
        nametext.set("TimeSeries1")
        while nametext.get() in self.timeseriesnames:
            i+=1
            nametext.set(f"TimeSeries{i}")

        namefield = ttk.Entry(optionframe1, textvariable=nametext, justify='center')
        namefield.grid(row=0, column=1)

        optionframe2 = ttk.Frame(win)
        optionframe2.grid(row=2, column=0)
        sampletimelabel = ttk.Label(optionframe2, text='Sample Time (s):')
        sampletimelabel.grid(row=0, column=0)
        sampletimetext = tk.StringVar()
        sampletimetext.set("1.0")
        sampletimefield = ttk.Entry(optionframe2, textvariable=sampletimetext, justify='center')
        sampletimefield.grid(row=0, column=1)

        optionframe3 = ttk.Frame(win)
        optionframe3.grid(row=3, column=0)
        ylabellabel = ttk.Label(optionframe3, text='Y-Label:')
        ylabellabel.grid(row=0, column=0)
        ylabeltext = tk.StringVar()
        ylabeltext.set("PowerW")
        ylabelfield = ttk.Entry(optionframe3, textvariable=ylabeltext, justify='center')
        ylabelfield.grid(row=0, column=1)

        errorframe = ttk.Frame(win)
        errorframe.grid(row=4, column=0)
        errortext = tk.StringVar()
        errorlabel = tk.Label(errorframe, textvariable=errortext)
        errorlabel.grid(row=0, column=0)

        buttonframe = ttk.Frame(win)
        buttonframe.grid(row=5, column=0)
        cancelbutton = ttk.Button(buttonframe, text='Cancel', command=win.destroy)
        cancelbutton.grid(row=0, column=1)
        okaybutton = ttk.Button(buttonframe, text='Save',
                                command=lambda : self.add_ts(nametext, sampletimetext, ylabeltext, errortext, win))
        okaybutton.grid(row=0, column=0)


        return


    def add_ts(self, name, sampletime, ylabel, err, window):
        ts_name = name.get()
        if ts_name in self.timeseriesnames:
            err.set("Error: Series name in use.")
            return
        elif ts_name in BannedWords:
            err.set("Error: Invalid name.")
        ts_sample_text = sampletime.get()
        try:
            ts_sample_time = float(ts_sample_text)
        except ValueError:
            err.set("Error: Invalid sample time.")
            return
        ylabel = ylabel.get()
        new_time_series = TimeSeries(ts_name, sample_time = ts_sample_time, ylabel=ylabel)
        self.timeseries.append(new_time_series)
        self.timeseriesnames.append(ts_name)
        window.destroy()
        self.change_active_ts(ts_name)
        self.reload_ts_list()
        if not self.tsdisplay_active:
            self.tsdisplayframe.grid(row=2,column=0)
            self.tsdisplay_active = True
            self.laser_ts.set(ts_name)
            self.load_ts.set(ts_name)
        self.complete_ts_action()

    def reload_ts_list(self, preserve_current = True):
        list_size = len(self.timeseriesnames)
        if list_size == 0:
            new_selection = None
        elif not preserve_current or list_size == 1:
            new_selection = self.timeseriesnames[0]
            self.change_active_ts(new_selection)
        else:
            new_selection = self.active_ts.name
        self.timeseriesdropdown.grid_remove()
        self.timeseriesdropdown = ttk.OptionMenu(self.selectframe,
                                                 self.selectedseries,
                                                 new_selection,
                                                 *self.timeseriesnames,
                                                 command=self.change_active_ts)
        self.timeseriesdropdown.grid(row=1, column=0)

        self.complete_ts_action()

    def refresh_ts_lists(self, removed=None):
        old_laser_choice = self.laser_ts.get()

        if len(self.timeseriesnames) > 0:
            replacement = self.timeseriesnames[0]
        else:
            replacement = None

        if old_laser_choice == removed:
            new_laser_choice = replacement
        else:
            new_laser_choice = old_laser_choice
        self.laser_ts_dropdown.grid_remove()
        self.laser_ts_dropdown = ttk.OptionMenu(self.calculations_frame,
                                                self.laser_ts,
                                                 new_laser_choice,
                                                 *self.timeseriesnames)
        self.laser_ts_dropdown.grid(row=0, column=1)

        old_load_choice = self.load_ts.get()
        if old_load_choice == removed:
            new_load_choice = replacement
        else:
            new_load_choice = old_load_choice
        self.load_ts_dropdown.grid_remove()
        self.load_ts_dropdown = ttk.OptionMenu(self.calculations_frame,
                                               self.load_ts,
                                               new_load_choice,
                                               *self.timeseriesnames)
        self.load_ts_dropdown.grid(row=1, column=1)


        old_cn2_ts = self.atm_cn2_ts.get()
        if old_cn2_ts == removed:
            new_cn2_ts = replacement
        else:
            new_cn2_ts = old_cn2_ts
        self.atm_cn2_ts_dropdown.grid_remove()
        self.atm_cn2_ts_dropdown = ttk.OptionMenu(self.atmdisplayframe,
                                                  self.atm_cn2_ts,
                                                  new_cn2_ts,
                                                  *self.timeseriesnames,
                                                  command=self.atm_change_cn2_ts)
        old_precipitation_ts = self.atm_precipitation_ts.get()
        if old_precipitation_ts == removed:
            new_precipitation_ts = replacement
        else:
            new_precipitation_ts = old_precipitation_ts
        self.atm_precipitation_ts_dropdown.grid_remove()
        self.atm_precipitation_ts_dropdown = ttk.OptionMenu(self.atmdisplayframe,
                                                  self.atm_precipitation_ts,
                                                  new_precipitation_ts,
                                                  *self.timeseriesnames,
                                                  command=self.atm_change_precipitation_ts)
        old_temperature_ts = self.atm_temperature_ts.get()
        if old_temperature_ts == removed:
            new_temperature_ts = replacement
        else:
            new_temperature_ts = old_temperature_ts
        self.atm_temperature_ts_dropdown.grid_remove()
        self.atm_temperature_ts_dropdown = ttk.OptionMenu(self.atmdisplayframe,
                                                  self.atm_temperature_ts,
                                                  new_temperature_ts,
                                                  *self.timeseriesnames,
                                                  command=self.atm_change_temperature_ts)
        old_visibility_ts = self.atm_visibility_ts.get()
        if old_visibility_ts == removed:
            new_visibility_ts = replacement
        else:
            new_visibility_ts = old_visibility_ts
        self.atm_visibility_ts_dropdown.grid_remove()
        self.atm_visibility_ts_dropdown = ttk.OptionMenu(self.atmdisplayframe,
                                                         self.atm_visibility_ts,
                                                         new_visibility_ts,
                                                         *self.timeseriesnames,
                                                         command=self.atm_change_visibility_ts)

        if len(self.atmospheres) == 0:
            return
        for atmosphere in self.atmospheres:
            if atmosphere.cn2_series == removed:
                atmosphere.cn2_series = replacement
            if atmosphere.precipitation_series == removed:
                atmosphere.precipitation_series = replacement
            if atmosphere.temperature_series == removed:
                atmosphere.temperature_series = replacement
            if atmosphere.visibility_series == removed:
                atmosphere.visibility_series = replacement

        self.refresh_atm_cn2()
        self.refresh_atm_precipitation()
        self.refresh_atm_temperature()
        self.refresh_atm_visibility()

    def change_active_ts(self, new_name, removed=None):
        ix = self.timeseriesnames.index(new_name)
        self.active_ts = self.timeseries[ix]
        self.ts_current_name.set(self.active_ts.name)
        self.ts_current_st.set(self.active_ts.sample_time)
        self.ts_current_ylabel.set(self.active_ts.ylabel)
        self.exit_ts_edits()
        self.complete_ts_action(removed=removed)

    def exit_ts_edits(self):
        self.exit_ts_namechange()
        self.exit_ts_st_change()
        self.exit_ts_ylabel_change()

    def enter_ts_ylabel_change(self):
        self.ylabel_display.grid_remove()
        self.edit_ylabel_button.grid_remove()
        self.new_ylabel.set(self.active_ts.ylabel)
        self.ylabel_new_field.grid(row=2, column=1)
        self.save_ylabel_button.grid(row=0, column=0)
        self.cancel_ylabel_button.grid(row=0, column=1)
        self.clear_ts_error()
        return

    def exit_ts_ylabel_change(self):
        self.ylabel_new_field.grid_remove()
        self.save_ylabel_button.grid_remove()
        self.cancel_ylabel_button.grid_remove()
        self.ylabel_display.grid(row=2, column=1)
        self.edit_ylabel_button.grid(row=0, column=0)
        self.new_ylabel.set("")
        self.clear_ts_error()
        pass

    def save_ts_ylabel_change(self):
        new_ylabel = self.new_ylabel.get()
        self.active_ts.ylabel = new_ylabel
        self.ts_current_ylabel.set(new_ylabel)
        self.exit_ts_ylabel_change()
        self.reload_ts_list()
        self.complete_ts_action()
        pass

    def enter_ts_namechange(self):
        self.name_display.grid_remove()
        self.edit_name_button.grid_remove()
        self.new_name.set(self.active_ts.name)
        self.name_new_field.grid(row=0, column=1)
        self.save_name_button.grid(row=0, column=0)
        self.cancel_name_button.grid(row=0, column=1)
        self.clear_ts_error()
        return


    def exit_ts_namechange(self):
        self.name_new_field.grid_remove()
        self.save_name_button.grid_remove()
        self.cancel_name_button.grid_remove()
        self.name_display.grid(row=0, column=1)
        self.edit_name_button.grid(row=0,column=0)
        self.new_name.set("")
        self.clear_ts_error()
        return

    def save_ts_namechange(self):
        new_name = self.new_name.get()
        if new_name in self.timeseriesnames:
            self.show_ts_error("Error: Series name in use.")
            return
        elif new_name in BannedWords:
            self.show_ts_error("Error: Invalid name.")
            return
        old_name = self.active_ts.name
        if self.load_ts.get() == old_name:
            self.load_ts.set(new_name)
        if self.laser_ts.get() == old_name:
            self.laser_ts.set(new_name)
        if self.atm_cn2_ts.get() == old_name:
            self.atm_cn2_ts.set(new_name)
        if self.atm_precipitation_ts.get() == old_name:
            self.atm_precipitation_ts.set(new_name)
        if self.atm_temperature_ts.get() == old_name:
            self.atm_temperature_ts.set(new_name)
        if self.atm_visibility_ts.get() == old_name:
            self.atm_visibility_ts.set(new_name)
        for atmosphere in self.atmospheres:
            if atmosphere.cn2_series == old_name:
                atmosphere.cn2_series = new_name
            if atmosphere.precipitation_series == old_name:
                atmosphere.precipitation_series = new_name
            if atmosphere.temperature_series == old_name:
                atmosphere.temperature_series = new_name
            if atmosphere.visibility_series == old_name:
                atmosphere.visibility_series = new_name
        self.timeseriesnames[self.timeseriesnames.index(old_name)] = new_name
        self.active_ts.name = new_name
        self.ts_current_name.set(new_name)
        self.exit_ts_namechange()
        self.reload_ts_list()
        self.complete_ts_action()


    def enter_ts_st_change(self):
        return

    def exit_ts_st_change(self):
        return

    def show_ts_error(self, error_string):
        self.tserrordisplay.grid(row=1,column=0)
        self.tserror.set(error_string)

    def clear_ts_error(self):
        self.tserrordisplay.grid_remove()
        self.tserror.set("")

    def update_ts_plot(self):
        if not self.is_ts_plot:
            if self.active_ts != None:
                self.ts_ax1.plot(self.active_ts.get_tvals(), self.active_ts())
                self.ts_ax1.set_title(self.active_ts.name)
                self.ts_ax1.set_xlabel("TimeS")
                self.ts_ax1.set_ylabel(self.active_ts.ylabel)
                self.is_ts_plot = True
                self.tsplotframe.grid(row=0,column=0)

            return
        self.ts_ax1.clear()
        self.ts_ax1.plot(self.active_ts.get_tvals(), self.active_ts())
        self.ts_ax1.set_title(self.active_ts.name)
        self.ts_ax1.set_xlabel("TimeS")
        self.ts_ax1.set_ylabel(self.active_ts.ylabel)
        self.canvas.draw()

    def ts_plot_shrink(self):
        self.ts_x -= 1 * GrowFactor
        self.ts_y -= 5/8 * GrowFactor
        self.ts_re_init_plot()

    def ts_plot_grow(self):
        self.ts_x += 1 * GrowFactor
        self.ts_y += 5/8 * GrowFactor
        self.ts_re_init_plot()

    def ts_re_init_plot(self):
        self.canvas.get_tk_widget().grid_remove()
        self.toolbar.grid_remove()
        plt.close(self.ts_fig)

        self.ts_fig, self.ts_ax1 = plt.subplots()
        self.ts_ax2 = self.ts_ax1.twinx()
        self.ts_fig.patch.set_facecolor("#F0F0F0")
        self.ts_fig.set_size_inches(self.ts_x, self.ts_y)
        self.canvas = FigureCanvasTkAgg(self.ts_fig, master=self.tsplotframe)  # A tk.DrawingArea.
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.tsplotframe, pack_toolbar=False)
        self.toolbar.update()
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.toolbar.grid(row=1, column=0)

        self.update_ts_plot()

    def complete_ts_action(self, removed=None):
        self.clear_ts_error()
        self.update_ts_plot()
        self.refresh_ts_lists(removed=removed)

    def delete_current_ts(self):
        current_ts_name = self.active_ts.name
        ts_count = len(self.timeseries)
        current_idx = self.timeseriesnames.index(current_ts_name)
        if current_idx == ts_count - 1:
            self.timeseries = self.timeseries[:current_idx]
            self.timeseriesnames = self.timeseriesnames[:current_idx]
        else:
            self.timeseries = self.timeseries[:current_idx] + self.timeseries[current_idx + 1:]
            self.timeseriesnames = self.timeseriesnames[:current_idx] + self.timeseriesnames[current_idx + 1:]
        if ts_count == 1:
            self.active_ts = None
            self.refresh_ts_lists(removed=current_ts_name)
            self.tsdisplayframe.grid_remove()
            self.tsplotframe.grid_remove()
            self.tsdisplay_active = False
            self.is_ts_plot = False
            self.selectedseries.set(None)
            self.reload_ts_list()
        else:
            self.change_active_ts(self.timeseriesnames[0], removed=current_ts_name)
            self.reload_ts_list()
# TX FUNCTIONS

    def change_active_tx(self, new_tx, removed=None):
        self.changing_tx = True
        self.selected_tx = new_tx
        self.active_tx = self.transmitters[self.transmitternames.index(new_tx)]
        self.tx_current_wavelength.set(Wavelengths[self.active_tx.type])
        self.tx_current_name.set(new_tx)
        self.tx_current_max_charge.set(self.active_tx.max_charge_rate)
        self.tx_current_max_discharge.set(self.active_tx.max_discharge_rate)
        self.tx_current_init_energy.set(self.active_tx.initial_charge)
        self.tx_current_max_energy.set(self.active_tx.max_energy)
        self.exit_tx_namechange()
        self.complete_tx_action(removed=removed)
        self.changing_tx = False

    def add_tx(self, name, wavelength, chargerate, dischargerate, initcharge, maxcharge, err, window):
        tx_name = name.get()
        if tx_name in self.transmitternames:
            err.set("Error: Transmitter name in use.")
            return
        elif tx_name in BannedWords:
            err.set("Error: Invalid name.")
        lastype = Wavelength_Dict[wavelength.get()]
        try:
            charge = float(chargerate.get())
        except TypeError:
            err.set("Error: Invalid charge rate.")
            return
        try:
            discharge = float(dischargerate.get())
        except TypeError:
            err.set("Error: Invalid discharge rate.")
            return
        try:
            init = float(initcharge.get())
        except TypeError:
            err.set("Error: Invalid initial charge.")
            return
        try:
            maxenergy = float(maxcharge.get())
        except TypeError:
            err.set("Error: Invalid maximum charge.")
        new_transmitter = Laser(tx_name, lastype, charge, discharge, init, maxenergy)
        self.transmitters.append(new_transmitter)
        self.transmitternames.append(tx_name)
        window.destroy()
        self.change_active_tx(tx_name)
        self.reload_tx_list()
        if not self.txdisplay_active:
            self.txdisplayframe.grid(row=2, column=0)
            self.txdisplay_active = True
            self.calculation_transmitter.set(tx_name)
        self.complete_tx_action()

    def reload_tx_list(self):
        if len(self.transmitters) == 0:
            new_tx = None
        else:
            new_tx = self.active_tx.name
        self.tx_dropdown.grid_remove()
        self.tx_dropdown = ttk.OptionMenu(self.tx_dropdown_frame,
                                          self.tx_current_name,
                                          new_tx,
                                          *self.transmitternames,
                                          command=self.change_active_tx)
        self.tx_dropdown.grid(row=1, column=0)

    def open_tx_add_menu(self):
        win = tk.Toplevel()
        win.wm_title("New Transmitter")

        windowlabel = ttk.Label(win, text='New Transmitter')
        windowlabel.grid(row=0, column=0)

        optionframe1 = ttk.Frame(win)
        optionframe1.grid(row=1, column=0)
        namelabel = ttk.Label(optionframe1, text='Name:')
        namelabel.grid(row=0, column=0)
        nametext = tk.StringVar()
        i=1
        nametext.set("Transmitter1")
        while nametext.get() in self.transmitternames:
            i+=1
            nametext.set(f"Transmitter{i}")

        namefield = ttk.Entry(optionframe1, textvariable=nametext, justify='center')
        namefield.grid(row=0, column=1)

        wavelengthlabel = ttk.Label(optionframe1, text='Wavelength (nm):')
        wavelengthlabel.grid(row=1, column=0)
        wavelength = tk.StringVar()
        wavelengthmenu = ttk.OptionMenu(optionframe1, wavelength, "808", *Wavelengths)
        wavelengthmenu.grid(row=1, column=1)

        chargeratelabel = ttk.Label(optionframe1, text='Max Charge Rate (W):')
        chargeratelabel.grid(row=2, column=0)
        chargerate = tk.StringVar()
        chargerate.set(DEFAULT_TX_MAX_CHARGE)
        chargerateentry = ttk.Entry(optionframe1, textvariable=chargerate, justify='center')
        chargerateentry.grid(row=2, column=1)

        dischargeratelabel = ttk.Label(optionframe1, text='Max Discharge Rate (W)')
        dischargeratelabel.grid(row=3, column=0)
        dischargerate = tk.StringVar()
        dischargerate.set(DEFAULT_TX_MAX_DISCHARGE)
        dischargerateentry = ttk.Entry(optionframe1, textvariable=dischargerate, justify='center')
        dischargerateentry.grid(row=3, column=1)

        initchargelabel = ttk.Label(optionframe1, text='Initial Energy (J)')
        initchargelabel.grid(row=4, column=0)
        initcharge = tk.StringVar()
        initcharge.set(DEFAULT_TX_INIT_ENERGY)
        initchargeentry = ttk.Entry(optionframe1, textvariable=initcharge, justify='center')
        initchargeentry.grid(row=4, column=1)

        maxenergylabel = ttk.Label(optionframe1, text='Maximum Energy (J)')
        maxenergylabel.grid(row=5, column=0)
        maxenergy = tk.StringVar()
        maxenergy.set(DEFAULT_TX_MAX_ENERGY)
        maxenergyentry = ttk.Entry(optionframe1, textvariable=maxenergy, justify='center')
        maxenergyentry.grid(row=5, column=1)

        errorframe = ttk.Frame(win)
        errorframe.grid(row=2, column=0)
        errortext = tk.StringVar()
        errorlabel = tk.Label(errorframe, textvariable=errortext)
        errorlabel.grid(row=0, column=0)

        buttonframe = ttk.Frame(win)
        buttonframe.grid(row=3, column=0)
        cancelbutton = ttk.Button(buttonframe, text='Cancel', command=win.destroy)
        cancelbutton.grid(row=0, column=1)
        okaybutton = ttk.Button(buttonframe, text='Save',
                                command=lambda : self.add_tx(nametext, wavelength, chargerate, dischargerate,
                                                             initcharge, maxenergy, errortext, win))
        okaybutton.grid(row=0, column=0)
        return

    def enter_tx_namechange(self):
        self.tx_new_name.set(self.active_tx.name)
        self.txnamedisplay.grid_remove()
        self.edit_tx_name_button.grid_remove()
        self.save_tx_name_button.grid(row=0, column=0)
        self.cancel_tx_name_button.grid(row=0, column=1)
        self.tx_new_name_field.grid(row=0, column=1)
        self.clear_tx_error()
        return

    def save_tx_namechange(self):
        new_name = self.tx_new_name.get()
        if new_name in self.transmitternames:
            self.show_tx_error("Error: Transmitter name in use.")
            return
        elif new_name in BannedWords:
            self.show_tx_error("Error: Invalid name.")
            return
        old_name = self.active_tx.name
        if self.calculation_transmitter.get() == old_name:
            self.calculation_transmitter.set(new_name)
        self.transmitternames[self.transmitternames.index(old_name)] = new_name
        self.active_tx.name = new_name
        self.reload_tx_list()
        self.exit_tx_namechange()
        self.complete_tx_action()

    def change_tx_wavelength(self, new_wavelength):
        self.active_tx.type = Wavelength_Dict[new_wavelength]

    def exit_tx_namechange(self):
        self.save_tx_name_button.grid_remove()
        self.cancel_tx_name_button.grid_remove()
        self.tx_new_name_field.grid_remove()
        self.edit_tx_name_button.grid(row=0, column=0)
        self.txnamedisplay.grid(row=0, column=1)
        return

    def clear_tx_error(self):
        self.tx_error.set("")
        self.tx_error_display.grid_remove()

    def show_tx_error(self, error_string):
        self.tx_error.set(error_string)
        self.tx_error_display.grid(row=1, column=0)

    def complete_tx_action(self, removed=None):
        self.clear_tx_error()
        self.refresh_tx_lists(removed=removed)

    def refresh_tx_lists(self, removed = None):
        old_tx = self.calculation_transmitter.get()
        if old_tx == removed:
            new_tx = self.transmitternames[0]
        else:
            new_tx = old_tx
        self.calc_tx_dropdown.grid_remove()
        self.calc_tx_dropdown = ttk.OptionMenu(self.calculations_frame, self.calculation_transmitter, new_tx,
                                               *self.transmitternames)
        self.calculation_transmitter.set(new_tx)
        self.calc_tx_dropdown.grid(row=2, column=1)

    def delete_current_tx(self):
        current_tx_name = self.active_tx.name
        tx_count = len(self.transmitters)
        current_idx = self.transmitternames.index(current_tx_name)
        if current_idx == tx_count - 1:
            self.transmitters = self.transmitters[:current_idx]
            self.transmitternames = self.transmitternames[:current_idx]
        else:
            self.transmitters = self.transmitters[:current_idx] + self.transmitters[current_idx + 1:]
            self.transmitternames = self.transmitternames[:current_idx] + self.transmitternames[current_idx + 1:]
        if tx_count == 1:
            self.active_tx = None
            self.refresh_tx_lists()
            self.txdisplayframe.grid_remove()
            self.txdisplay_active = False
            self.tx_current_name.set(None)
            self.reload_tx_list()
        else:
            self.change_active_tx(self.transmitternames[0], removed=current_tx_name)
            self.reload_tx_list()

    def tx_var_change(self, stringvar, func, scaling_factor=1):
        if self.changing_tx:
            return
        string = stringvar.get()
        try:
            val = float(string)
        except ValueError:
            return
        val = scaling_factor * val
        func(val)
#RX Functions

    def change_active_rx(self, new_rx, removed=None):
        self.changing_rx = True
        self.selected_rx = new_rx
        self.active_rx = self.receivers[self.receivernames.index(new_rx)]
        self.rx_current_name.set(new_rx)
        self.rx_distance.set(self.active_rx.distance)
        self.rx_max_charge.set(self.active_rx.max_charge_rate)
        self.rx_max_discharge.set(self.active_rx.max_discharge_rate)
        self.rx_init_charge.set(self.active_rx.initial_charge)

        self.rx_dcdc_conversion.set(self.active_rx.dcdc_conversion * 100)
        self.rx_mppt_array.set(self.active_rx.mppt_array_efficiency * 100)
        self.rx_concentrator_reflectivity.set(self.active_rx.concentrator_reflectivity_losses * 100)
        self.rx_pv_shadowing.set(self.active_rx.pv_shadowing * 100)
        self.rx_coverglass_reflective_dirt.set(self.active_rx.coverglass_reflective_dirt_factor * 100)
        self.rx_pv_active_area.set(self.active_rx.pv_active_area_factor * 100)
        self.rx_beam_spill.set(self.active_rx.beam_spill_factor * 100)

        self.rx_power_per_cell.set(self.active_rx.power_per_cell)
        self.rx_v_mpp.set(self.active_rx.v_mpp)
        self.rx_diam.set(self.active_rx.rx_diam * 100)
        self.rx_f_pv.set(self.active_rx.f_pv)
        self.rx_i_nom.set(self.active_rx.i_nom)

        self.changing_rx = False
        self.exit_rx_namechange()
        self.complete_rx_action(removed=removed)

    def reload_rx_list(self):
        if len(self.receivers) == 0:
            new_rx = None
        else:
            new_rx = self.active_rx.name
        self.rx_dropdown.grid_remove()
        self.rx_dropdown = ttk.OptionMenu(self.rx_dropdown_frame,
                                          self.rx_current_name,
                                          new_rx,
                                          *self.receivernames,
                                          command=self.change_active_rx)
        self.rx_dropdown.grid(row=1, column=0)

    def open_rx_add_menu(self):
        win = tk.Toplevel()
        win.wm_title("New Receiver")

        windowlabel = ttk.Label(win, text='New Receiver')
        windowlabel.grid(row=0, column=0)

        optionframe1 = ttk.Frame(win)
        optionframe1.grid(row=1, column=0)
        namelabel = ttk.Label(optionframe1, text='Name:')
        namelabel.grid(row=0, column=0)
        nametext = tk.StringVar()
        i=1
        nametext.set("Receiver1")
        while nametext.get() in self.receivernames:
            i+=1
            nametext.set(f"Receiver{i}")

        namefield = ttk.Entry(optionframe1, textvariable=nametext, justify='center')
        namefield.grid(row=0, column=1)

        distancelabel = ttk.Label(optionframe1, text='Distance (m):')
        distancelabel.grid(row=1, column=0)
        distance = tk.StringVar()
        distance.set("300")
        distancefield = ttk.Entry(optionframe1, textvariable=distance, justify='center')
        distancefield.grid(row=1, column=1)

        maxchargelabel = ttk.Label(optionframe1, text='Max Battery Charge (W):')
        maxchargelabel.grid(row=2, column=0)
        maxcharge = tk.StringVar()
        maxcharge.set("1000")
        maxchargefield = ttk.Entry(optionframe1, textvariable=maxcharge, justify='center')
        maxchargefield.grid(row=2, column=1)

        maxdischargelabel = ttk.Label(optionframe1, text='Max Battery Discharge (W):')
        maxdischargelabel.grid(row=3, column=0)
        maxdischarge = tk.StringVar()
        maxdischarge.set("1000")
        maxdischargefield = ttk.Entry(optionframe1, textvariable=maxdischarge, justify='center')
        maxdischargefield.grid(row=3, column=1)

        initchargelabel = ttk.Label(optionframe1, text='Initial Charge (J):')
        initchargelabel.grid(row=4, column=0)
        initcharge = tk.StringVar()
        initcharge.set("0")
        initchargefield = ttk.Entry(optionframe1, textvariable=initcharge, justify='center')
        initchargefield.grid(row=4, column=1)

        errorframe = ttk.Frame(win)
        errorframe.grid(row=5, column=0)
        errortext = tk.StringVar()
        errorlabel = tk.Label(errorframe, textvariable=errortext)
        errorlabel.grid(row=0, column=0)

        buttonframe = ttk.Frame(win)
        buttonframe.grid(row=6, column=0)
        cancelbutton = ttk.Button(buttonframe, text='Cancel', command=win.destroy)
        cancelbutton.grid(row=0, column=1)
        okaybutton = ttk.Button(buttonframe, text='Save',
                                command=lambda : self.add_rx(nametext, distance, maxcharge, maxdischarge, initcharge,
                                                             errortext, win))
        okaybutton.grid(row=0, column=0)
        return

    def add_rx(self, nametext, distance, maxcharge, maxdischarge, initcharge, errortext, window):
        name = nametext.get()
        if name in self.receivernames:
            errortext.set("Error: Receiver name already in use.")
            return
        elif name in BannedWords:
            errortext.set("Error: Invalid name.")
            return
        dist = distance.get()
        try:
            dist = float(dist)
        except ValueError:
            errortext.set("Error: Invalid distance.")
            return
        charge = maxcharge.get()
        try:
            charge = float(charge)
        except ValueError:
            errortext.set("Error: Invalid max battery charge.")
            return
        discharge = maxdischarge.get()
        try:
            discharge = float(discharge)
        except ValueError:
            errortext.set("Error: Invalid max battery discharge.")
            return
        init = initcharge.get()
        try:
            init = float(init)
        except ValueError:
            errortext.set("Error: Invalid initial charge.")
            return

        new_receiver = Receiver(name, dist, charge, discharge, init)
        self.receivers.append(new_receiver)
        self.receivernames.append(name)
        window.destroy()
        self.change_active_rx(name)
        self.reload_rx_list()
        if not self.rxdisplay_active:
            self.rxdisplayframe.grid(row=2, column=0)
            self.rxdisplay_active = True
            self.calculation_receiver.set(name)
        self.complete_rx_action()
        pass

    def enter_rx_namechange(self):
        self.rx_new_name.set(self.active_rx.name)
        self.rxnamedisplay.grid_remove()
        self.edit_rx_name_button.grid_remove()
        self.save_rx_name_button.grid(row=0, column=0)
        self.cancel_rx_name_button.grid(row=0, column=1)
        self.rx_new_name_field.grid(row=0, column=1)
        self.clear_rx_error()
        return

    def save_rx_namechange(self):
        new_name = self.rx_new_name.get()
        if new_name in self.receivernames:
            self.show_rx_error("Error: Receiver name in use.")
            return
        elif new_name in BannedWords:
            self.show_rx_error("Error: Invalid name.")
            return
        old_name = self.active_rx.name
        if self.calculation_receiver.get() == old_name:
            self.calculation_receiver.set(new_name)
        self.receivernames[self.receivernames.index(old_name)] = new_name
        self.active_rx.name = new_name
        self.reload_rx_list()
        self.exit_rx_namechange()
        self.complete_rx_action()

    def exit_rx_namechange(self):
        self.save_rx_name_button.grid_remove()
        self.cancel_rx_name_button.grid_remove()
        self.rx_new_name_field.grid_remove()
        self.edit_rx_name_button.grid(row=0, column=0)
        self.rxnamedisplay.grid(row=0, column=1)
        return

    def clear_rx_error(self):
        self.rx_error.set("")
        self.rx_error_display.grid_remove()

    def show_rx_error(self, error_string):
        self.rx_error.set(error_string)
        self.rx_error_display.grid(row=1, column=0)

    def complete_rx_action(self, removed=None):
        self.clear_rx_error()
        self.refresh_rx_lists(removed=removed)

    def refresh_rx_lists(self, removed = None):
        old_rx = self.calculation_receiver.get()
        if old_rx == removed:
            new_rx = self.receivernames[0]
        else:
            new_rx = old_rx
        self.calc_rx_dropdown.grid_remove()
        self.calc_rx_dropdown = ttk.OptionMenu(self.calculations_frame, self.calculation_receiver, new_rx,
                                                    *self.receivernames)
        self.calculation_receiver.set(new_rx)
        self.calc_rx_dropdown.grid(row=3, column=1)

    def rx_var_change(self, stringvar, func, scaling_factor=1):
        if self.changing_rx:
            return
        string = stringvar.get()
        try:
            val = float(string)
        except ValueError:
            return
        val = scaling_factor * val
        func(val)
    def delete_current_rx(self):
        current_rx_name = self.active_rx.name
        rx_count = len(self.receivers)
        current_idx = self.receivernames.index(current_rx_name)
        if current_idx == rx_count - 1:
            self.receivers = self.receivers[:current_idx]
            self.receivernames = self.receivernames[:current_idx]
        else:
            self.receivers = self.receivers[:current_idx] + self.receivers[current_idx + 1:]
            self.receivernames = self.receivernames[:current_idx] + self.receivernames[current_idx + 1:]
        if rx_count == 1:
            self.active_rx = None
            self.refresh_rx_lists()
            self.rxdisplayframe.grid_remove()
            self.rxdisplay_active = False
            self.rx_current_name.set(None)
            self.reload_rx_list()
        else:
            self.change_active_rx(self.receivernames[0], removed=current_rx_name)
            self.reload_rx_list()
# ATM FUNCTIONS
    def open_atm_add_menu(self):
        win = tk.Toplevel()
        win.wm_title("New Atmosphere")

        windowlabel = ttk.Label(win, text='New Atmosphere')
        windowlabel.grid(row=0, column=0)

        optionframe1 = ttk.Frame(win)
        optionframe1.grid(row=1, column=0)
        namelabel = ttk.Label(optionframe1, text='Name:')
        namelabel.grid(row=0, column=0)
        nametext = tk.StringVar()
        i=1
        nametext.set("Atmosphere1")
        while nametext.get() in self.atmospherenames:
            i+=1
            nametext.set(f"Atmosphere{i}")

        namefield = ttk.Entry(optionframe1, textvariable=nametext, justify='center')
        namefield.grid(row=0, column=1)

        cn2label = ttk.Label(optionframe1, text='Structure Constant (m^-2/3):')
        cn2label.grid(row=1, column=0)
        cn2 = tk.StringVar()
        cn2.set("1e-16")
        cn2field = ttk.Entry(optionframe1, textvariable=cn2, justify='center')
        cn2field.grid(row=1, column=1)

        precipitationlabel = ttk.Label(optionframe1, text='Precipitation Rate (mm/h):')
        precipitationlabel.grid(row=2, column=0)
        precipitation = tk.StringVar()
        precipitation.set("0")
        precipitationfield = ttk.Entry(optionframe1, textvariable=precipitation, justify='center')
        precipitationfield.grid(row=2, column=1)

        temperaturelabel = ttk.Label(optionframe1, text='Temperature (C):')
        temperaturelabel.grid(row=3, column=0)
        temperature = tk.StringVar()
        temperature.set("30")
        temperaturefield = ttk.Entry(optionframe1, textvariable=temperature, justify='center')
        temperaturefield.grid(row=3, column=1)

        visibilitylabel = ttk.Label(optionframe1, text='Visibility (km):')
        visibilitylabel.grid(row=4, column=0)
        visibility = tk.StringVar()
        visibility.set("100")
        visibilityfield = ttk.Entry(optionframe1, textvariable=visibility, justify='center')
        visibilityfield.grid(row=4, column=1)

        errorframe = ttk.Frame(win)
        errorframe.grid(row=5, column=0)
        errortext = tk.StringVar()
        errorlabel = tk.Label(errorframe, textvariable=errortext)
        errorlabel.grid(row=0, column=0)

        buttonframe = ttk.Frame(win)
        buttonframe.grid(row=6, column=0)
        cancelbutton = ttk.Button(buttonframe, text='Cancel', command=win.destroy)
        cancelbutton.grid(row=0, column=1)
        okaybutton = ttk.Button(buttonframe, text='Save',
                                command=lambda : self.add_atm(nametext, cn2, precipitation, temperature, visibility,
                                                             errortext, win))
        okaybutton.grid(row=0, column=0)

    def add_atm(self, nametext, cn2, precipitation, temperature, visibility, errortext, window):
        name = nametext.get()
        if name in self.atmospherenames:
            errortext.set("Error: Atmosphere name already in use.")
            return
        elif name in BannedWords:
            errortext.set("Error: Invalid name.")
            return
        cn2val = cn2.get()
        try:
            cn2val = float(cn2val)
        except ValueError:
            errortext.set("Error: Invalid structure constant.")
            return
        precip = precipitation.get()
        try:
            precip = float(precip)
        except ValueError:
            errortext.set("Error: Invalid precipitation.")
            return
        temp = temperature.get()
        try:
            temp = float(temp)
        except ValueError:
            errortext.set("Error: Invalid temperature.")
            return
        vis = visibility.get()
        try:
            vis = float(vis)
        except ValueError:
            errortext.set("Error: Invalid visibility.")
            return

        new_atmosphere = Atmosphere(name, cn2val, precip, temp, vis)
        self.atmospheres.append(new_atmosphere)
        self.atmospherenames.append(name)
        window.destroy()
        if not self.atmdisplay_active:
            self.atmdisplayframe.grid(row=2, column=0)
            self.atmdisplay_active = True
            self.calculation_atmosphere.set(name)
        self.change_active_atm(name)
        self.reload_atm_list()
        pass

    def change_active_atm(self, new_atm, removed=None):
        self.changing_atm = True

        self.active_atm = self.atmospheres[self.atmospherenames.index(new_atm)]
        self.atm_current_name.set(new_atm)
        self.atm_cn2.set(self.active_atm.structure_constant)
        self.atm_precipitation.set(self.active_atm.precipitation)
        self.atm_temperature.set(self.active_atm.temperature)
        self.atm_visibility.set(self.active_atm.visibility)

        self.atm_cn2_seriesmode.set(self.active_atm.cn2_seriesmode)
        self.atm_cn2_ts.set(self.active_atm.cn2_series)
        self.refresh_atm_cn2()

        self.atm_precipitation_seriesmode.set(self.active_atm.precipitation_seriesmode)
        self.atm_precipitation_ts.set(self.active_atm.precipitation_series)
        self.refresh_atm_precipitation()

        self.atm_temperature_seriesmode.set(self.active_atm.temperature_seriesmode)
        self.atm_temperature_ts.set(self.active_atm.temperature_series)
        self.refresh_atm_temperature()

        self.atm_visibility_seriesmode.set(self.active_atm.visibility_seriesmode)
        self.atm_visibility_ts.set(self.active_atm.visibility_series)
        self.refresh_atm_visibility()

        self.changing_atm = False
        self.exit_atm_namechange()
        self.complete_atm_action(removed=removed)

    def enter_atm_namechange(self):
        self.atm_new_name.set(self.active_atm.name)
        self.atmnamedisplay.grid_remove()
        self.edit_atm_name_button.grid_remove()
        self.save_atm_name_button.grid(row=0, column=0)
        self.cancel_atm_name_button.grid(row=0, column=1)
        self.atm_new_name_field.grid(row=0, column=1)
        self.clear_atm_error()
        return

    def save_atm_namechange(self):
        new_name = self.atm_new_name.get()
        if new_name in self.atmospherenames:
            self.show_atm_error("Error: Receiver name in use.")
            return
        elif new_name in BannedWords:
            self.show_atm_error("Error: Invalid name.")
            return
        old_name = self.active_atm.name
        if self.calculation_atmosphere.get() == old_name:
            self.calculation_atmosphere.set(new_name)
        self.atmospherenames[self.atmospherenames.index(old_name)] = new_name
        self.active_atm.name = new_name
        self.reload_atm_list()
        self.exit_atm_namechange()

    def exit_atm_namechange(self):
        self.save_atm_name_button.grid_remove()
        self.cancel_atm_name_button.grid_remove()
        self.atm_new_name_field.grid_remove()
        self.edit_atm_name_button.grid(row=0, column=0)
        self.atmnamedisplay.grid(row=0, column=1)
        self.complete_atm_action()
        return

    def complete_atm_action(self, removed=None):
        self.clear_atm_error()
        self.refresh_atm_lists(removed=removed)

    def clear_atm_error(self):
        self.atm_error.set("")
        self.atm_error_display.grid_remove()

    def show_atm_error(self, error_string):
        self.atm_error.set(error_string)
        self.atm_error_display.grid(row=1, column=0)

    def reload_atm_list(self):
        if len(self.atmospheres) == 0:
            new_atm = None
        else:
            new_atm = self.active_atm.name
        self.atm_dropdown.grid_remove()
        self.atm_dropdown = ttk.OptionMenu(self.atm_dropdown_frame,
                                           self.atm_current_name,
                                           new_atm,
                                           *self.atmospherenames,
                                           command=self.change_active_atm)
        self.atm_dropdown.grid(row=1, column=0)

    def refresh_atm_lists(self, removed = None):
        old_atm = self.calculation_atmosphere.get()
        if old_atm == removed:
            new_atm = self.atmospherenames[0]
        else:
            new_atm = old_atm
        self.calc_atm_dropdown.grid_remove()
        self.calc_atm_dropdown = ttk.OptionMenu(self.calculations_frame, self.calculation_atmosphere, new_atm,
                                                *self.atmospherenames)
        self.calculation_atmosphere.set(new_atm)
        self.calc_atm_dropdown.grid(row=4, column=1)

    def atm_var_change(self, stringvar, func, scaling_factor=1):
        if self.changing_atm:
            return
        string = stringvar.get()
        try:
            val = float(string)
        except ValueError:
            return
        val = scaling_factor * val
        func(val)

    def atm_cn2_toggle(self):
        self.active_atm.cn2_seriesmode = self.atm_cn2_seriesmode.get()
        self.refresh_atm_cn2()

    def refresh_atm_cn2(self):
        seriesmode = self.active_atm.cn2_seriesmode
        if seriesmode:
            self.atm_cn2_field.grid_remove()
            self.atm_cn2_ts_dropdown.grid(row=1, column=1)
        else:
            self.atm_cn2_ts_dropdown.grid_remove()
            self.atm_cn2_field.grid(row=1, column=1)

    def atm_change_cn2_ts(self, new_ts):
        self.active_atm.cn2_series = new_ts

    def atm_precipitation_toggle(self):
        self.active_atm.precipitation_seriesmode = self.atm_precipitation_seriesmode.get()
        self.refresh_atm_precipitation()

    def refresh_atm_precipitation(self):
        seriesmode = self.active_atm.precipitation_seriesmode
        if seriesmode:
            self.atm_precipitation_field.grid_remove()
            self.atm_precipitation_ts_dropdown.grid(row=2, column=1)
        else:
            self.atm_precipitation_ts_dropdown.grid_remove()
            self.atm_precipitation_field.grid(row=2, column=1)

    def atm_change_precipitation_ts(self, new_ts):
        self.active_atm.precipitation_series = new_ts

    def atm_temperature_toggle(self):
        self.active_atm.temperature_seriesmode = self.atm_temperature_seriesmode.get()
        self.refresh_atm_temperature()

    def refresh_atm_temperature(self):
        seriesmode = self.active_atm.temperature_seriesmode
        if seriesmode:
            self.atm_temperature_field.grid_remove()
            self.atm_temperature_ts_dropdown.grid(row=3, column=1)
        else:
            self.atm_temperature_ts_dropdown.grid_remove()
            self.atm_temperature_field.grid(row=3, column=1)

    def atm_change_temperature_ts(self, new_ts):
        self.active_atm.temperature_series = new_ts

    def atm_visibility_toggle(self):
        self.active_atm.visibility_seriesmode = self.atm_visibility_seriesmode.get()
        self.refresh_atm_visibility()

    def refresh_atm_visibility(self):
        seriesmode = self.active_atm.visibility_seriesmode
        if seriesmode:
            self.atm_visibility_field.grid_remove()
            self.atm_visibility_ts_dropdown.grid(row=4, column=1)
        else:
            self.atm_visibility_ts_dropdown.grid_remove()
            self.atm_visibility_field.grid(row=4, column=1)

    def atm_change_visibility_ts(self, new_ts):
        self.active_atm.visibility_series = new_ts

    def atm_update_ts_data(self, atm):
        if atm.cn2_series != None:
            atm.cn2_ts_data = self.timeseries[self.timeseriesnames.index(atm.cn2_series)].data
        if atm.precipitation_series !=None:
            atm.precipitation_ts_data = self.timeseries[self.timeseriesnames.index(atm.precipitation_series)].data
        if atm.temperature_series !=None:
            atm.temperature_ts_data = self.timeseries[self.timeseriesnames.index(atm.temperature_series)].data
        if atm.visibility_series !=None:
            atm.visibility_ts_data = self.timeseries[self.timeseriesnames.index(atm.visibility_series)].data

    def delete_current_atm(self):
        current_atm_name = self.active_atm.name
        atm_count = len(self.atmospheres)
        current_idx = self.atmospherenames.index(current_atm_name)
        if current_idx == atm_count - 1:
            self.atmospheres = self.atmospheres[:current_idx]
            self.atmospherenames = self.atmospherenames[:current_idx]
        else:
            self.atmospheres = self.atmospheres[:current_idx] + self.atmospheres[current_idx + 1:]
            self.atmospherenames = self.atmospherenames[:current_idx] + self.atmospherenames[current_idx + 1:]
        if atm_count == 1:
            self.active_atm = None
            self.refresh_atm_lists()
            self.atmdisplayframe.grid_remove()
            self.atmdisplay_active = False
            self.atm_current_name.set(None)
            self.reload_atm_list()
        else:
            self.change_active_atm(self.atmospherenames[0], removed=current_atm_name)
            self.reload_atm_list()
#CALC PAGE FUNCTIONS
    def do_calc(self):
        input_name = self.laser_ts.get()
        input_idx = self.timeseriesnames.index(input_name)
        input_ts = self.timeseries[input_idx]
        laser_raw = input_ts()

        load_name = self.load_ts.get()
        load_idx = self.timeseriesnames.index(load_name)
        load_ts = self.timeseries[load_idx]
        load_raw = load_ts()
        if input_ts.sample_time != load_ts.sample_time:
            return
        else:
            sample_time = input_ts.sample_time
        transmitter_name = self.calculation_transmitter.get()
        tx_idx = self.transmitternames.index(transmitter_name)
        tx = self.transmitters[tx_idx]
        receiver_name = self.calculation_receiver.get()
        rx_idx = self.receivernames.index(receiver_name)
        rx = self.receivers[rx_idx]
        atmosphere_name = self.calculation_atmosphere.get()
        atm_idx = self.atmospherenames.index(atmosphere_name)
        atm = self.atmospheres[atm_idx]
        self.atm_update_ts_data(atm)


        battery_ts, rx_ts, corrected_load_ts, corrected_laser_ts, laser_battery = get_battery_energy(laser_raw, load_raw,
                                                                                                     sample_time, tx, rx,
                                                                                                     atm)
        self.calc_rx_ts = rx_ts
        self.calc_load_ts = corrected_load_ts
        self.calc_battery_ts = battery_ts
        self.calc_sample_time = sample_time
        self.calc_laser_ts = corrected_laser_ts
        self.calc_laser_battery_ts = laser_battery
 #       plot_4_ts(laser_raw, rx_ts, load_raw, corrected_load_ts, battery_ts, sample_time)

        self.laser_raw = laser_raw
        self.rx_ts = rx_ts
        self.load_raw = load_raw
        self.corrected_load_ts = corrected_load_ts
        self.battery_ts = battery_ts
        self.sample_time = sample_time
        self.laser_corr = corrected_laser_ts
        self.laser_battery = laser_battery
        self.update_calc_plot()

    def update_calc_plot(self):
        laser_ts = self.laser_raw
        rx_ts = self.rx_ts
        load_ts = self.load_raw
        corrected_load_ts = self.corrected_load_ts
        battery_ts = self.battery_ts
        sample_time = self.sample_time
        laser_corr = self.laser_corr
        laser_battery = self.laser_battery
        if not self.is_calc_plot:
            self.is_calc_plot = True
            self.calc_plot_frame.grid(row=0, column=0)
            self.save_output_button.state(["!disabled"])

        self.calc_ax[0, 0].clear()
        self.calc_ax[0, 0].plot(sample_time * np.arange(laser_ts.size), laser_ts)
        self.calc_ax[0, 0].set_title('Requested Laser Power')
        self.calc_ax[0, 0].set_xlabel('Time (s)')
        self.calc_ax[0, 0].set_ylabel('Power (W)')

        self.calc_ax[1, 0].clear()
        self.calc_ax[1, 0].plot(sample_time * np.arange(laser_corr.size), laser_corr)
        self.calc_ax[1, 0].set_title('Corrected Laser Power')
        self.calc_ax[1, 0].set_xlabel('Time (s)')
        self.calc_ax[1, 0].set_ylabel('Power (W)')

        self.calc_ax[2, 0].clear()
        self.calc_ax[2, 0].plot(sample_time * np.arange(rx_ts.size), rx_ts)
        self.calc_ax[2, 0].set_title('Power Delivered to Receiver')
        self.calc_ax[2, 0].set_xlabel('Time (s)')
        self.calc_ax[2, 0].set_ylabel('Power (W)')

        self.calc_ax[3, 0].clear()
        self.calc_ax[3, 0].plot(sample_time * np.arange(laser_battery.size), laser_battery)
        self.calc_ax[3, 0].set_title('Laser Energy')
        self.calc_ax[3, 0].set_xlabel('Time (s)')
        self.calc_ax[3, 0].set_ylabel('Energy (J)')

        self.calc_ax[0, 1].clear()
        self.calc_ax[0, 1].plot(sample_time * np.arange(load_ts.size), load_ts)
        self.calc_ax[0, 1].set_title('Requested Load Power')
        self.calc_ax[0, 1].set_xlabel('Time (s)')
        self.calc_ax[0, 1].set_ylabel('Power (W)')

        self.calc_ax[1, 1].clear()
        self.calc_ax[1, 1].plot(sample_time * np.arange(corrected_load_ts.size), corrected_load_ts)
        self.calc_ax[1, 1].set_title('Corrected Load Power')
        self.calc_ax[1, 1].set_xlabel('Time (s)')
        self.calc_ax[1, 1].set_ylabel('Power (W)')

        self.calc_ax[3, 1].clear()
        self.calc_ax[3, 1].plot(sample_time * np.arange(battery_ts.size), battery_ts)
        self.calc_ax[3, 1].set_title('Battery Energy')
        self.calc_ax[3, 1].set_xlabel('Time (s)')
        self.calc_ax[3, 1].set_ylabel('Energy (J)')

        self.calc_canvas.draw()
        self.calc_fig.tight_layout()

    def calc_plot_shrink(self):
        self.calc_x -= 1 * GrowFactor
        self.calc_y -= 5/8 * GrowFactor
        self.calc_re_init_plot()

    def calc_plot_grow(self):
        self.calc_x += 1 * GrowFactor
        self.calc_y += 5/8 * GrowFactor
        self.calc_re_init_plot()

    def calc_re_init_plot(self):
        self.calc_canvas.get_tk_widget().grid_remove()
        self.calc_toolbar.grid_remove()
        plt.close(self.calc_fig)

        self.calc_fig, self.calc_ax = plt.subplots(self.calc_rows, self.calc_cols)
        self.calc_fig.patch.set_facecolor("#F0F0F0")
        self.calc_fig.set_size_inches(self.calc_x, self.calc_y)
        self.calc_canvas = FigureCanvasTkAgg(self.calc_fig, master=self.calc_plot_frame)  # A tk.DrawingArea.
        #       self.calc_canvas.mpl_connect("key_press_event", self.on_key_press)
        self.calc_toolbar = NavigationToolbar2Tk(self.calc_canvas, self.calc_plot_frame, pack_toolbar=False)
        self.calc_toolbar.update()
        self.calc_canvas.get_tk_widget().grid(row=0, column=0)
        self.calc_toolbar.grid(row=1, column=0)

        self.update_calc_plot()
    def open_calc_add_menu(self):
        win = tk.Toplevel()
        win.wm_title("Save Output Time Series")

        windowlabel = ttk.Label(win, text='Save Output Time Series')
        windowlabel.grid(row=0, column=0)

        optionframe1 = ttk.Frame(win)
        optionframe1.grid(row=1, column=0)

        savebatteryenergy = tk.IntVar()
        batteryenergycheckbox = ttk.Checkbutton(optionframe1, variable=savebatteryenergy, text='Battery Energy')
        batteryenergycheckbox.grid(row=8, column=1)
        batteryenergyname = tk.StringVar()
        i = 1
        batteryenergyname.set("BatteryEnergy1")
        while batteryenergyname.get() in self.timeseriesnames:
            i += 1
            batteryenergyname.set(f"BatteryPower{i}")
        batteryenergynamelabel = ttk.Label(optionframe1, text='Name:')
        batteryenergynamelabel.grid(row=9, column=0)
        batteryenergynamefield = ttk.Entry(optionframe1, textvariable=batteryenergyname, justify='center')
        batteryenergynamefield.grid(row=9, column=1)

        savereceiverpower = tk.IntVar()
        receiverpowercheckbox = ttk.Checkbutton(optionframe1, variable=savereceiverpower, text='Power Delivered to Receiver')
        receiverpowercheckbox.grid(row=2, column=1)
        receiverpowername = tk.StringVar()
        i = 1
        receiverpowername.set("ReceiverPower1")
        while receiverpowername.get() in self.timeseriesnames:
            i += 1
            receiverpowername.set(f"ReceiverPower{i}")
        receiverpowernamelabel = ttk.Label(optionframe1, text='Name:')
        receiverpowernamelabel.grid(row=3, column=0)
        receiverpowernamefield = ttk.Entry(optionframe1, textvariable=receiverpowername, justify='center')
        receiverpowernamefield.grid(row=3, column=1)

        saveloadpower = tk.IntVar()
        loadpowercheckbox = ttk.Checkbutton(optionframe1, variable=saveloadpower, text='Corrected Load Power')
        loadpowercheckbox.grid(row=4, column=1)
        loadpowername = tk.StringVar()
        loadpowername.set("LoadPower1")
        i = 1
        while loadpowername.get() in self.timeseriesnames:
            i += 1
            loadpowername.set(f"LoadPower{i}")
        loadpowernamelabel = ttk.Label(optionframe1, text='Name:')
        loadpowernamelabel.grid(row=5, column=0)
        loadpowernamefield = ttk.Entry(optionframe1, textvariable=loadpowername, justify='center')
        loadpowernamefield.grid(row=5, column=1)

        savecorrectedlaser = tk.IntVar()
        correctedlasercheckbox = ttk.Checkbutton(optionframe1, variable=savecorrectedlaser, text='Corrected Laser Power')
        correctedlasercheckbox.grid(row=0, column=1)
        correctedlasername = tk.StringVar()
        correctedlasername.set("CorrectedLaser1")
        i = 1
        while correctedlasername.get() in self.timeseriesnames:
            i += 1
            correctedlasername.set(f"CorrectedLaser{i}")
        correctedlasernamelabel = ttk.Label(optionframe1, text='Name:')
        correctedlasernamelabel.grid(row=1, column=0)
        correctedlasernamefield = ttk.Entry(optionframe1, textvariable=correctedlasername, justify='center')
        correctedlasernamefield.grid(row=1, column=1)

        savelaserenergy = tk.IntVar()
        laserenergycheckbox = ttk.Checkbutton(optionframe1, variable=savelaserenergy, text='Laser Energy')
        laserenergycheckbox.grid(row=6, column=1)
        laserenergyname = tk.StringVar()
        laserenergyname.set("LaserEnergy1")
        i = 1
        while laserenergyname.get() in self.timeseriesnames:
            i += 1
            laserenergyname.set(f"LaserEnergy{i}")
        laserenergynamelabel = ttk.Label(optionframe1, text='Name:')
        laserenergynamelabel.grid(row=7, column=0)
        laserenergynamefield = ttk.Entry(optionframe1, textvariable=laserenergyname, justify='center')
        laserenergynamefield.grid(row=7, column=1)

        errorframe = ttk.Frame(win)
        errorframe.grid(row=2, column=0)
        errortext = tk.StringVar()
        errorlabel = tk.Label(errorframe, textvariable=errortext)
        errorlabel.grid(row=0, column=0)

        buttonframe = ttk.Frame(win)
        buttonframe.grid(row=3, column=0)
        cancelbutton = ttk.Button(buttonframe, text='Cancel', command=win.destroy)
        cancelbutton.grid(row=0, column=1)
        okaybutton = ttk.Button(buttonframe, text='Save',
                                command=lambda: self.save_calc_outputs(savebatteryenergy, batteryenergyname,
                                                                       savereceiverpower, receiverpowername,
                                                                       saveloadpower, loadpowername,
                                                                       savecorrectedlaser, correctedlasername,
                                                                       savelaserenergy, laserenergyname,
                                                                       errortext, win))
  #                              command=lambda: self.add_ts(nametext, sampletimetext, ylabeltext, errortext, win))
        okaybutton.grid(row=0, column=0)

        return
    def save_calc_outputs(self, savebatteryenergy, batteryenergyname, savereceiverpower, receiverpowername,
                          saveloadpower, loadpowername, savecorrectedlaser, correctedlasername, savelaserenergy,
                          laserenergyname, err, win):
        save_be = False
        if savebatteryenergy.get():
            if batteryenergyname.get() in self.timeseriesnames:
                err.set("Error: Battery energy name in use.")
                return
            elif batteryenergyname.get() in BannedWords:
                err.set("Error: Invalid battery energy name.")
                return
            save_be = True

        save_rp = False
        if savereceiverpower.get():
            if receiverpowername.get() in self.timeseriesnames:
                err.set("Error: Receiver power name in use.")
                return
            elif receiverpowername.get() in BannedWords:
                err.set("Error: Invalid receiver power name.")
                return
            save_rp = True

        save_lp = False
        if saveloadpower.get():
            if loadpowername.get() in self.timeseriesnames:
                err.set("Error: Load power name in use.")
                return
            elif loadpowername.get() in BannedWords:
                err.set("Error: Invalid load power name.")
                return
            save_lp = True

        save_cl = False
        if savecorrectedlaser.get():
            if correctedlasername.get() in self.timeseriesnames:
                err.set("Error: Laser power name in use.")
                return
            elif correctedlasername.get() in BannedWords:
                err.set("Error: Invalid laser power name.")
                return
            save_cl = True

        save_le = False
        if savelaserenergy.get():
            if laserenergyname.get() in self.timeseriesnames:
                err.set("Error: Laser energy name in use.")
                return
            elif laserenergyname.get() in BannedWords:
                err.set("Error: Invalid laser energy name.")
                return
            save_le = True

        if not save_be and not save_rp and not save_lp and not save_cl and not save_le:
            err.set("Error: No time series selected.")
            return

        if save_be:
            self.add_calc_ts(batteryenergyname, self.calc_sample_time, "EnergyJ", self.calc_battery_ts)
        if save_rp:
            self.add_calc_ts(receiverpowername, self.calc_sample_time, "PowerW", self.calc_rx_ts)
        if save_lp:
            self.add_calc_ts(loadpowername, self.calc_sample_time, "PowerW", self.calc_load_ts)
        if save_cl:
            self.add_calc_ts(correctedlasername, self.calc_sample_time, "PowerW", self.calc_laser_ts)
        if save_le:
            self.add_calc_ts(laserenergyname, self.calc_sample_time, "EnergyJ", self.calc_laser_battery_ts)
        win.destroy()


    def add_calc_ts(self, name, sampletime, ylabel, ts_data):
        ts_name = name.get()
        ts_sample_time = sampletime

        new_time_series = TimeSeries(ts_name, data=ts_data, sample_time=ts_sample_time, ylabel=ylabel)
        self.timeseries.append(new_time_series)
        self.timeseriesnames.append(ts_name)

        self.reload_ts_list()
        self.complete_ts_action()


root = tk.Tk()
app = Application(master=root)
app.mainloop()