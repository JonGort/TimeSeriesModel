import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import time
from classes import *

# slightly modified w cool matrix math to return an array of scint factors with array of Cn2 values as input
# this code is also robust to return an array of scint factors with Cn2 kept constant and dist as an array, thanks numpy
def scintillation_rx_factor(wavelength, nominal_power, nominal_eff, dist, Cn2, V_mpp=0.64, RX_diam=0.025, f_PV=0.1,
                            I_nom=12.8, do_modify=True):
    wavelength_m = wavelength * 10 ** (-9)
    intensity = np.arange(start=0.05, stop=3.2, step=0.05)
    current = nominal_power * nominal_eff / V_mpp * intensity
    # OLD VERSION
    # p_out = current*(V_mpp - R_PV * current)
    # NEW VERSION
    R_PV = f_PV * V_mpp / I_nom
    p_out = current*(V_mpp - R_PV * (current - I_nom))
    rytov = 0.124 * Cn2 * (2 * np.pi / wavelength_m) ** (7/6) * dist**(11/6)
    if do_modify:
        rytov = rytov * ((1 + rytov ** (6/5)) ** (-7/6) + (1 + rytov ** (6/5)) ** (-5/6))  # modification to rytov
    # variance to make it valid for both weak and strong fluctuation regimes (?)
    avg_factor = 1 / (1 + 1.07 * (np.pi * RX_diam**2 / (wavelength_m * dist)) ** (7/6))
    irr_var = avg_factor * (np.exp(4 * rytov) - 1)
    raw_prob = (1 / (intensity * np.sqrt(2 * np.pi * irr_var)) * np.exp(-1 / (2 * irr_var) *
                                                                        (np.log(intensity) + irr_var / 2)**2))
    prob = 1 / np.sum(raw_prob) * raw_prob
    p_out_weighted = p_out * prob
    eff_net = 1 / p_out[19] * np.sum(p_out_weighted)
    return eff_net


# slightly modified w cool matrix math to return an array of scint factors with array of Cn2 values as input
# this code is also robust to return an array of scint factors with Cn2 kept constant and dist as an array, thanks numpy
def scint_factor_vary_struct(wavelength, nominal_power, nominal_eff, dist, Cn2, V_mpp=0.64, RX_diam=0.025, f_PV=0.1,
                             I_nom=12.8, do_modify=True):
    wavelength_m = wavelength * 10 ** (-9)
    intensity = np.arange(start=0.05, stop=3.2, step=0.05)
    current = nominal_power * nominal_eff / V_mpp * intensity
    R_PV = f_PV * V_mpp / I_nom
    # OLD eq
    # p_out = current*(V_mpp - R_PV * current)
    p_out = current*(V_mpp - R_PV * (current - I_nom))
    rytov = 0.124 * Cn2 * (2 * np.pi / wavelength_m) ** (7/6) * dist**(11/6)
    if do_modify:
        rytov = rytov * ((1 + rytov ** (6/5)) ** (-7/6) + (1 + rytov ** (6/5)) ** (-5/6))  # modification to rytov
    # variance to make it valid for both weak and strong fluctuation regimes (?)
    avg_factor = 1 / (1 + 1.07 * (np.pi * RX_diam**2 / (wavelength_m * dist)) ** (7/6))
    irr_var = avg_factor * (np.exp(4 * rytov) - 1)
    # transform p_out, intensity, and irr_var into x invariant, x invariant, and y invariant matrices
    x_ones = np.ones_like(irr_var)
    y_ones = np.ones_like(intensity)
    irr_var = np.outer(irr_var, y_ones)
    intensity = np.outer(x_ones, intensity)
    p_out_matrix = np.outer(x_ones, p_out)
    raw_prob = (1 / (intensity * np.sqrt(2 * np.pi * irr_var)) * np.exp(-1 / (2 * irr_var) *
                                                                        (np.log(intensity) + irr_var / 2)**2))
    prob = np.outer(1 / np.sum(raw_prob, axis=1), y_ones) * raw_prob
    p_out_weighted = p_out_matrix * prob
    effs_net = 1 / p_out[19] * np.sum(p_out_weighted, axis=1)
    return effs_net

# similarly modified to allow for an array of nominal efficiency values (corresponding to different temperatures) as
# input
def scint_factor_vary_temp(wavelength, nominal_power, nominal_eff, dist, Cn2, V_mpp=0.64, RX_diam=0.025, f_PV=0.1,
                           I_nom=12.8, do_modify=True):
    wavelength_m = wavelength * 10 ** (-9)
    intensity = np.arange(start=0.05, stop=3.2, step=0.05)
    x_ones = np.ones_like(nominal_eff)
    y_ones = np.ones_like(intensity)
    intensity = np.outer(x_ones, intensity)
    nominal_eff = np.outer(nominal_eff, y_ones)
    current = nominal_power * nominal_eff / V_mpp * intensity
    R_PV = f_PV * V_mpp / I_nom
    p_out = current*(V_mpp - R_PV * (current - I_nom))
    rytov = 0.124 * Cn2 * (2 * np.pi / wavelength_m) ** (7/6) * dist**(11/6)
    if do_modify:
        rytov = rytov * ((1 + rytov ** (6/5)) ** (-7/6) + (1 + rytov ** (6/5)) ** (-5/6))  # modification to rytov
    # variance to make it valid for both weak and strong fluctuation regimes (?)
    avg_factor = 1 / (1 + 1.07 * (np.pi * RX_diam**2 / (wavelength_m * dist)) ** (7/6))
    irr_var = avg_factor * (np.exp(4 * rytov) - 1)
    raw_prob = (1 / (intensity * np.sqrt(2 * np.pi * irr_var)) * np.exp(-1 / (2 * irr_var) *
                                                                        (np.log(intensity) + irr_var / 2)**2))
    prob = np.outer(1 / np.sum(raw_prob, axis=1), y_ones) * raw_prob
    p_out_weighted = p_out * prob
    effs_net = 1 / p_out[:,19] * np.sum(p_out_weighted, axis=1)
    return effs_net

#similar to above, varies both
def scint_factor_vary_both(wavelength, nominal_power, nominal_eff, dist, Cn2, V_mpp=0.64, RX_diam=0.025, f_PV=0.1,
                           I_nom=12.8, do_modify=True):
    wavelength_m = wavelength * 10 ** (-9)
    intensity = np.arange(start=0.05, stop=3.2, step=0.05)
    x_ones = np.ones_like(nominal_eff)
    y_ones = np.ones_like(intensity)
    intensity = np.outer(x_ones, intensity)
    nominal_eff = np.outer(nominal_eff, y_ones)
    current = nominal_power * nominal_eff / V_mpp * intensity
    R_PV = f_PV * V_mpp / I_nom
    p_out = current*(V_mpp - R_PV * (current - I_nom))
    rytov = 0.124 * Cn2 * (2 * np.pi / wavelength_m) ** (7/6) * dist**(11/6)
    if do_modify:
        rytov = rytov * ((1 + rytov ** (6/5)) ** (-7/6) + (1 + rytov ** (6/5)) ** (-5/6))  # modification to rytov
    # variance to make it valid for both weak and strong fluctuation regimes (?)
    avg_factor = 1 / (1 + 1.07 * (np.pi * RX_diam**2 / (wavelength_m * dist)) ** (7/6))
    irr_var = avg_factor * (np.exp(4 * rytov) - 1)
    irr_var = np.outer(irr_var, y_ones)
    raw_prob = (1 / (intensity * np.sqrt(2 * np.pi * irr_var)) * np.exp(-1 / (2 * irr_var) *
                                                                        (np.log(intensity) + irr_var / 2)**2))
    prob = np.outer(1 / np.sum(raw_prob, axis=1), y_ones) * raw_prob
    p_out_weighted = p_out * prob
    effs_net = 1 / p_out[:,19] * np.sum(p_out_weighted, axis=1)
    return effs_net

# estimates atmospheric extinction from precipitation rate and visibility measurements. formula is based on Atlas/1953
# paper. calculates two extinction coefficients both directly from visibility and from precipitation rate; the larger
# of the two coefficients is used to calculate an atmospheric extinction factor.
# by default, assumes non-orographic rainfall as precipitation type. provides support for orographic rainfall as well
# with further research, different precipitation types such as snow, drizzle, hail, etc. can also be included. GUI
# will need further work to integrate a precipitation type choice
# NOTE: If any input is an array, this function will return an array of outputs

def get_atmospheric_factor(precip_rate, visibility, distance, precip_type="non-orographic"):
    if np.size(precip_rate) == 1 and np.size(visibility) > 1:
        precip_rate = precip_rate * np.ones_like(visibility)
    elif np.size(visibility) == 1 and np.size(precip_rate) > 1:
        visibility = visibility * np.ones_like(precip_rate)
    if precip_type == "non-orographic":
        extinction_coeff_precip = 0.001 * 0.25 * precip_rate**0.63
    elif precip_type == "orographic":
        extinction_coeff_precip = 0.001 * 1.2 * precip_rate**0.33
    else:
        extinction_coeff_precip = 0
    extinction_coeff_vis = Threshold_Const / visibility
    extinction_coeff = np.maximum(extinction_coeff_precip, extinction_coeff_vis)
    extinction_factor = np.exp(-1 * extinction_coeff * distance)
    return extinction_factor

# currently able to calculate arrays for distance, structure_const, precip_rate, temperature, or visibility as array ins
# will likely not work correctly if more than one inputs are arrays, and will certainly throw an error if those arrays
# are not the same size
def laser_to_rx(laser_ts, laser, receiver, atmosphere):
    #ignore aux power draw for now
    #aux_power_draw = Computers + Warning_Lights + Safety_Curtain + LIDAR_1 + LIDAR_2 + Miscellaneous
    #ignore chiller power draw for now, not yet written (complicated, differential relationship)

    distance = receiver.distance

    vary_cn2 = False
    if not atmosphere.cn2_seriesmode:
        structure_const = atmosphere.structure_constant
    else:
        structure_const = atmosphere.cn2_ts_data
        difference = np.size(laser_ts) - np.size(structure_const)
        if difference > 0:
            structure_const = np.concatenate((structure_const, structure_const[-1]*np.ones(difference)))
        elif difference < 0:
            structure_const= structure_const[:np.size(laser_ts)]
        vary_cn2 = True

    vary_temp = False
    if not atmosphere.temperature_seriesmode:
        temperature = atmosphere.temperature
    else:
        temperature = atmosphere.temperature_ts_data
        difference = np.size(laser_ts) - np.size(temperature)
        if difference > 0:
            temperature = np.concatenate((temperature, temperature[-1]*np.ones(difference)))
        elif difference < 0:
            temperature = temperature[:np.size(laser_ts)]
        vary_temp = True

    if not atmosphere.visibility_seriesmode:
        visibility = atmosphere.visibility*1000
    else:
        visibility = atmosphere.visibility_ts_data*1000
        difference = np.size(laser_ts) - np.size(visibility)
        if difference > 0:
            visibility = np.concatenate((visibility, visibility[-1]*np.ones(difference)))
        elif difference < 0:
            visibility = visibility[:np.size(laser_ts)]

    if not atmosphere.precipitation_seriesmode:
        precip_rate = atmosphere.precipitation
    else:
        precip_rate = atmosphere.precipitation_ts_data
        difference = np.size(laser_ts) - np.size(precip_rate)
        if difference > 0:
            precip_rate = np.concatenate((precip_rate, precip_rate[-1]*np.ones(difference)))
        elif difference < 0:
            precip_rate = precip_rate[:np.size(laser_ts)]

    laser_type = laser.type
    #ignore transmitter factors for now
    laser_beam = laser_ts
    '''
    #tx efficiency losses
    laser_ps_input = laser_ts
    input_power_to_laser = laser_ps_input * Laser_PS_Efficiency
    laser_diode_efficiency = Laser_Efficiencies[laser_type]
    laser_module_rated_output = input_power_to_laser * laser_diode_efficiency
    optics_factor = Transmission_Per_Optical_Surface ** Internal_Optical_Surfaces
    laser_beam = laser_module_rated_output * Aperture_Window * optics_factor * Fringe_Light_Factor

    #chiller perturbation to laser beam power
    waste_heat = input_power_to_laser - laser_beam
    chiller_power = waste_heat / Chiller_CoP  # a single perturbation --> overestimate?
    #laser_beam = laser_beam - chiller_power
    '''

    atmospheric_factor = get_atmospheric_factor(precip_rate, visibility, distance)
    required_incident_laser_energy = laser_beam * atmospheric_factor
    pv_temperature = temperature + 40  # for now, just add 40 degrees C to (max) ambient temperature
    pv_temperature_effect = 1 - (0.0018 * (pv_temperature - 20))  # 0.2% per degree C (or should it be 0.25%?)
    pv_cell_efficiency = PV_Efficiencies[laser_type]  # depends on laser wavelength
    nominal_pv_eff = pv_cell_efficiency * pv_temperature_effect
    wavelength = Wavelengths[laser_type]
    if not vary_cn2 and not vary_temp:
        pv_scintillation_factor = scintillation_rx_factor(wavelength, receiver.power_per_cell, nominal_pv_eff, distance,
                                                      structure_const, V_mpp=receiver.v_mpp, RX_diam=receiver.rx_diam,
                                                      f_PV=receiver.f_pv, I_nom=receiver.i_nom)
    elif not vary_cn2:
        pv_scintillation_factor = scint_factor_vary_temp(wavelength, receiver.power_per_cell, nominal_pv_eff, distance,
                                                      structure_const, V_mpp=receiver.v_mpp, RX_diam=receiver.rx_diam,
                                                      f_PV=receiver.f_pv, I_nom=receiver.i_nom)
    elif not vary_temp:
        pv_scintillation_factor = scint_factor_vary_struct(wavelength, receiver.power_per_cell, nominal_pv_eff, distance,
                                                      structure_const, V_mpp=receiver.v_mpp, RX_diam=receiver.rx_diam,
                                                      f_PV=receiver.f_pv, I_nom=receiver.i_nom)
    else:
        pv_scintillation_factor = scint_factor_vary_both(wavelength, receiver.power_per_cell, nominal_pv_eff, distance,
                                                      structure_const, V_mpp=receiver.v_mpp, RX_diam=receiver.rx_diam,
                                                      f_PV=receiver.f_pv, I_nom=receiver.i_nom)

    rx_factors = (receiver.dcdc_conversion * receiver.mppt_array_efficiency * pv_cell_efficiency *
                  pv_temperature_effect * pv_scintillation_factor * receiver.pv_active_area_factor *
                  receiver.concentrator_reflectivity_losses * receiver.pv_shadowing *
                  receiver.coverglass_reflective_dirt_factor * receiver.beam_spill_factor)
    rx_ts = required_incident_laser_energy * rx_factors
    return rx_ts

def get_battery_energy(laser_ts, load_ts, sample_time, laser, receiver, atmosphere):
    #first, tx checks
    tx_max_charge = laser.max_charge_rate
    tx_max_discharge = laser.max_discharge_rate
    tx_init_energy = laser.initial_charge
    tx_max_energy = laser.max_energy

    if np.size(laser_ts) > 0:
        max_output = tx_max_discharge * np.ones_like(laser_ts)
        corrected_laser_ts = np.minimum(laser_ts, max_output)

        laser_battery_delta = tx_max_charge * np.ones_like(laser_ts) - corrected_laser_ts
        count = np.arange(np.size(laser_ts)-1)
        laser_battery = np.zeros_like(laser_ts)
        laser_battery[0] = np.minimum(tx_init_energy + sample_time*laser_battery_delta[0], tx_max_energy)

        for i in count:
            laser_battery[i+1] = np.minimum(laser_battery[i] + sample_time*laser_battery_delta[i+1], tx_max_energy)

    else:
        corrected_laser_ts = np.array([])
        laser_battery = np.array([])

    rx_ts = laser_to_rx(corrected_laser_ts, laser, receiver, atmosphere)
    max_discharge = receiver.max_discharge_rate
    max_charge = receiver.max_charge_rate
    init_battery_charge = receiver.initial_charge

    if rx_ts.size > load_ts.size:
        zeros = np.zeros(rx_ts.size - load_ts.size)
        load_ts = np.concatenate((load_ts, zeros))
    elif rx_ts.size < load_ts.size:
        zeros = np.zeros(load_ts.size - rx_ts.size)
        rx_ts = np.concatenate((rx_ts, zeros))

    start_load_correction = time.time()
    #correct load power (unable to power if rx power + battery discharge rate  < load power)
    battery_load = load_ts - rx_ts
    max_load = max_discharge * np.ones_like(battery_load)
    true_battery_load = np.minimum(battery_load, max_load)
    corrected_load_ts = true_battery_load + rx_ts
    load_ts = corrected_load_ts # comment out to disable discharge rate checking
    corrected_load_ts = load_ts

    end_load_correction = time.time()
    lc_time = end_load_correction - start_load_correction
    #print(f"Time for load correction: {lc_time}")

    battery_power = (rx_ts - load_ts)

    #now, correct for max charge rate
    start_battery_correction = time.time()
    total_spillover = 0
    for i, val in enumerate(battery_power):
        if val > max_charge:
            spillover = val - max_charge
            battery_power[i] = max_charge
            total_spillover += spillover
        elif total_spillover > 0:
            pushed = max_charge - val
            if total_spillover < pushed:
                battery_power[i] = val + total_spillover
                total_spillover = 0
            else:
                battery_power[i] = max_charge
                total_spillover -= pushed
    if total_spillover > 0:
        div = int(np.floor(total_spillover / max_charge))
        if div > 0:
            first_spillover = max_charge * np.ones(div)
            battery_power = np.concatenate((battery_power, first_spillover))
        r = total_spillover % max_charge
        battery_power = np.append(battery_power, r)
    end_battery_correction = time.time()
    bc_time = end_battery_correction - start_battery_correction
    #print(f"Time for battery correction: {bc_time}")

    delta_energy = battery_power * sample_time
    battery_ts = init_battery_charge + np.cumsum(delta_energy)
    return battery_ts, rx_ts, corrected_load_ts, corrected_laser_ts, laser_battery

def plot_4_ts(laser_ts, rx_ts, load_ts, corrected_load_ts, battery_ts, sample_time):
    fig, ax = plt.subplots(3, 2)

    ax[0,0].plot(sample_time*np.arange(laser_ts.size), laser_ts)
    ax[0,0].set_title('Laser Power')
    ax[0,0].set_xlabel('Time (s)')
    ax[0,0].set_ylabel('Power (W)')

    ax[1,0].plot(sample_time*np.arange(rx_ts.size), rx_ts)
    ax[1,0].set_title('Power Delivered to Receiver')
    ax[1,0].set_xlabel('Time (s)')
    ax[1,0].set_ylabel('Power (W)')

    ax[0,1].plot(sample_time*np.arange(load_ts.size), load_ts)
    ax[0,1].set_title('Requested Load Power')
    ax[0,1].set_xlabel('Time (s)')
    ax[0,1].set_ylabel('Power (W)')

    ax[1,1].plot(sample_time*np.arange(corrected_load_ts.size), corrected_load_ts)
    ax[1,1].set_title('Received Load Power')
    ax[1,1].set_xlabel('Time (s)')
    ax[1,1].set_ylabel('Power (W)')

    ax[2,1].plot(sample_time*np.arange(battery_ts.size), battery_ts)
    ax[2,1].set_title('Battery Energy')
    ax[2,1].set_xlabel('Time (s)')
    ax[2,1].set_ylabel('Energy (J)')

    plt.tight_layout()
    plt.show()

'''

    # TX
    # Eventually we should separate the surfaces by type (each coating will be different)
    optics_factor = Transmission_Per_Optical_Surface ** Internal_Optical_Surfaces  # each lens and reflector has some
    # loss
    laser_module_rated_output = laser_beam / Aperture_Window / optics_factor / Fringe_Light_Factor
    # this should be worst-case
    laser_diode_efficiency = Laser_Efficiencies[laser_type]  # Dilas direct diode bar: 60.8% documented at
    # several kW
    input_power_to_laser = laser_module_rated_output / laser_diode_efficiency  # big power supply
    heat_from_laser = input_power_to_laser - laser_module_rated_output  # for sizing the chiller. omits optical losses
    heat_from_laser_coupling_optics = input_power_to_laser - laser_beam  # if the chiller must also cool lossy optics
    laser_ps_input = input_power_to_laser / Laser_PS_Efficiency
    # Assuming a chiller designed for cooling a laser at high ambient temperature, NOT a laboratory unit.
    chiller_power_draw = heat_from_laser / Chiller_CoP  # power draw
    # and to avoid running at # 100% capacity indefinitely
    chiller_size = heat_from_laser * Chiller_Overcapacity
    chiller_peak_power_draw = chiller_size / Chiller_CoP
    laser_end_of_life_condition = 0.80  # Not used for calculations yet. Standard practice is for the rated power to
    # be some percentage of the available power when the laser is new. As the laser ages, input power is increased
    # (and cooling requirements increase) until the unit is operating at maximum allowable input power.

    # TOTAL SYSTEM POWER
    aux_power_draw = Computers + Warning_Lights + Safety_Curtain + LIDAR_1 + LIDAR_2 + Miscellaneous
    total_power_draw = laser_ps_input + chiller_power_draw + aux_power_draw  # for efficiency calc
    max_power_draw = laser_ps_input + chiller_peak_power_draw + aux_power_draw  # for sizing of generator

standard_atm = Atmosphere("standard atm", 1e-16, 0, 30, 100000)
def_rx = Receiver("default", 1000, 1000, 1000, 0)
laser = Laser("default", 0)

sample_time = 1
laser_ts = np.concatenate((np.zeros(100), 100*np.ones(50), np.zeros(100), 200*np.ones(20), np.zeros(200), 100*np.ones(20)))
load_ts = np.concatenate((20*np.ones(200), np.zeros(50), 10*np.ones(100), 5*np.ones(50)))

battery_ts, rx_ts, corrected_load_ts = get_battery_energy(laser_ts, load_ts, sample_time, laser, def_rx, standard_atm)
#plot_4_ts(laser_ts, rx_ts, load_ts, corrected_load_ts, battery_ts, sample_time)
'''