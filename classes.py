import numpy as np

DEFAULT_ARRAY = np.array([])

Wavelength_Dict = {
    808 : 0,
    976 : 1,
    1075 : 2,
    '808': 0,
    '976': 1,
    '1075': 2
}

# global laser-PV values, corresponding to laser wavelength
Wavelengths = np.array([808, 976, 1075])
PV_Efficiencies = np.array([0.65, 0.49, 0.43])  # sourced from Efficiency & Sizing Model 2017
Laser_Efficiencies = np.array([0.48, 0.50, 0.41])
Laser_Brightnesses = np.array([0.04e12, 0.1e12, 30e12])
# globals associated with laser beam calculations--may be modified as laser dependent as model becomes more complex

# duty-safety factor constants
Safety_Percent = 0.01  # assume powering system deactivated by safety feature for this fraction of time
Slew_Time = 2  # assume it takes on average this amount of time, in minutes, to transfer between devices

# used in atmospheric factor calculations
Threshold_Const = 2.9

# RX factor values
DCDC_Conversion = 0.90  # 95% is a good goal,DC/DC boost conversion
MPPT_Array_Efficiency = 0.96  # some losses due to voltage/current mismatch
PV_Active_Area_Factor = 0.98  # TBD
Concentrator_Reflectivity_Losses = 0.96  # TBD
PV_Shadowing = 1  # due to structural stuff or baffles or whatever
Coverglass_Reflective_Dirt_Factor = 0.96  # TBD:quality of anti-reflective coating plus scattering/dirt
Beam_Spill_Factor = 0.99  # might include overfill AND beam jitter

#scintillation
Power_Per_Cell = 20  # W
Cell_Width = 2.5 # cm

V_mpp = 0.64
RX_diam = 0.025
f_PV = 0.1
I_nom = 12.8

# TX factor values
Aperture_Window = 0.970  # TBD: quality of anti-refl. coating, plus scattering due to dirt
Transmission_Per_Optical_Surface = 0.9970  # assuming less than perfect cleanliness
Internal_Optical_Surfaces = 10  # This is a guess. FSM, Dichroics, beam shaping.
Fringe_Light_Factor = 0.99  # are we throwing away any “low intensity” light around the edges?
Laser_PS_Efficiency = 0.96  # Lumina claims power factor >98%; is this DC->DC or AC->DC ??
TX_Diameter = 0.12

# Chiller values
Chiller_CoP = 2.50  # Input power vs heat transported; includes fans, pump, drive electronics.
Chiller_Overcapacity = 1.50  # chiller is oversized to allow for initial chilldown

# Auxiliary power draws
Computers = 3  # W. PH
Warning_Lights = 0  # W. PH
Safety_Curtain = 5  # W. PH
LIDAR_1 = 2  # W. PH
LIDAR_2 = 2  # W. PH
Miscellaneous = 8  # W. PH

# slightly modified w cool matrix math to return an array of scint factors with array of Cn2 values as input
# this code is also robust to return an array of scint factors with Cn2 kept constant and dist as an array, thanks numpy

DEFAULT_TX_MAX_CHARGE = 1000
DEFAULT_TX_MAX_DISCHARGE = 1000
DEFAULT_TX_INIT_ENERGY = 0
DEFAULT_TX_MAX_ENERGY = 1000

class Receiver:
    def __init__(self, name, distance, max_charge_rate, max_discharge_rate, initial_charge):
        self.name = name
        self.distance = distance
        self.max_charge_rate = max_charge_rate
        self.max_discharge_rate = max_discharge_rate
        self.initial_charge = initial_charge

        #efficiencies
        self.dcdc_conversion = DCDC_Conversion
        self.mppt_array_efficiency = MPPT_Array_Efficiency
        self.pv_active_area_factor = PV_Active_Area_Factor
        self.concentrator_reflectivity_losses = Concentrator_Reflectivity_Losses
        self.pv_shadowing = PV_Shadowing
        self.coverglass_reflective_dirt_factor = Coverglass_Reflective_Dirt_Factor
        self.beam_spill_factor = Beam_Spill_Factor

        #scintillation
        self.power_per_cell = Power_Per_Cell
        self.v_mpp = V_mpp
        self.rx_diam = RX_diam
        self.f_pv = f_PV
        self.i_nom = I_nom

    def set_distance(self, input):
        self.distance = input
    def set_max_charge(self, input):
        self.max_charge_rate = input
    def set_max_discharge(self, input):
        self.max_discharge_rate = input
    def set_init_charge(self, input):
        self.initial_charge = input

    def set_dcdc_conversion(self, input):
        self.dcdc_conversion = input
    def set_mppt_array(self, input):
        self.mppt_array_efficiency = input
    def set_pv_active_area(self, input):
        self.pv_active_area_factor = input
    def set_concentrator_reflectivity(self, input):
        self.concentrator_reflectivity_losses = input
    def set_pv_shadowing(self, input):
        self.pv_shadowing = input
    def set_coverglass_reflective_dirt(self, input):
        self.coverglass_reflective_dirt_factor = input
    def set_beam_spill(self, input):
        self.beam_spill_factor = input

    def set_power_per_cell(self, input):
        self.power_per_cell = input
    def set_v_mpp(self, input):
        self.v_mpp = input
    def set_rx_diam(self, input):
        self.rx_diam = input
    def set_f_pv(self, input):
        self.f_pv = input
    def set_i_nom(self, input):
        self.i_nom = input

class Laser:
    def __init__(self, name, type, max_charge_rate, max_discharge_rate, initial_charge, max_energy):
        self.type = type
        self.name = name
        self.max_charge_rate = max_charge_rate
        self.max_discharge_rate = max_discharge_rate
        self.initial_charge = initial_charge
        self.max_energy = max_energy

    def set_max_charge(self, input):
        self.max_charge_rate = input
    def set_max_discharge(self, input):
        self.max_discharge_rate = input
    def set_init_charge(self, input):
        self.initial_charge = input
    def set_max_energy(self, input):
        self.max_energy = input

class Atmosphere:
    def __init__(self, name, structure_constant, precipitation, temperature, visibility):
        self.name = name
        self.structure_constant = structure_constant
        self.precipitation = precipitation
        self.temperature = temperature
        self.visibility = visibility

        self.cn2_seriesmode = 0
        self.precipitation_seriesmode = 0
        self.temperature_seriesmode = 0
        self.visibility_seriesmode = 0

        self.cn2_series = None
        self.precipitation_series = None
        self.temperature_series = None
        self.visibility_series = None

        self.cn2_ts_data = None
        self.precipitation_ts_data = None
        self.temperature_ts_data = None
        self.visibility_ts_data = None

    def set_cn2(self, val):
        self.structure_constant = val

    def set_visibility(self, val):
        self.visibility = val

    def set_temperature(self, val):
        self.temperature = val

    def set_precipitation(self, val):
        self.precipitation = val

class TimeSeries:
    def __init__(self, name, data=DEFAULT_ARRAY, sample_time=1, ylabel=None):
        self.name = name
        self.data = data
        self.sample_time = sample_time
        if np.size(data) == 0:
            self.sequences = []
            self.intervals = []
        else:
            self.sequences = [data]
            self.intervals = [(0,np.size(data))]
        self.empty_check()
        self.ylabel = ylabel

    def __call__(self):
        return self.data

    def empty_check(self):
        self.is_empty = np.size(self.data) == 0
        return self.is_empty

    def append_right(self, new_data):
        is_first_data = self.empty_check()
        self.data = np.concatenate((self.data, new_data))
        self.sequences.append(new_data)
        if is_first_data:
            self.intervals.append((0,np.size(new_data)))
        else:
            a,b = self.intervals[-1]
            self.intervals.append((b, b+np.size(new_data)))
        self.empty_check()

    def add_downtime(self, idx_from, idx_to):
        self.data[idx_from:idx_to] = 0
        for idx, interval in enumerate(self.intervals):
            a,b = interval
            if a <= idx_from and idx_from < b:
                interval_from = idx
                a_from = a
                b_from = b
                break
        for idx, interval in enumerate(self.intervals[interval_from:]):
            a,b = interval
            if a <= idx_to and idx_to < b:
                interval_to = idx
                a_to = a
                b_to = b
                break
        idx_from_adj = idx_from - a_from
        self.sequences[interval_from][idx_from_adj:] = 0
        for idx, sequence in enumerate(self.sequences[interval_from + 1:interval_to]):
            zeros = np.zeros_like(sequence)
            self.sequences[idx] = zeros
        idx_to_adj = idx_to - a_to
        self.sequences[interval_to][:idx_to_adj] = 0
        self.empty_check()

    def append_left(self, new_data):
        self.data = np.concatenate((new_data, self.data))

    def change_sample_time(self, new_sample_time):
        self.sample_time = new_sample_time

    def replace(self, replacement_data):
        self.data = replacement_data

    def remove_left(self, size):
        self.data = self.data[size:]

    def remove_right(self, size):
        self.data = self.data[:-size]

    def remove_sequence_right(self):
        length = np.size(self.sequences[-1])
        self.data = self.data[:-length]
        self.sequences = self.sequences[:-1]
        self.empty_check()

    def clear_data(self):
        self.data = DEFAULT_ARRAY
        self.sequences = []
        self.empty_check()

    def get_tvals(self):
        return self.sample_time * np.arange(self.data.size)



