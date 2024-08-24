import py_dss_interface
import random
import functions

# Properties of HC method
circuit_pu = 1.045
load_mult = 0.2
percent = 0.2
p_step = 10
kva_to_kw = 1
location = 114
pf = 1
v_limit = 1.05
receb = 0

dss_file = r"C:\py_dss_interface_Mini_Curso\Hosting_Capacity_Com_OpenDSS\Master_ckt5.dss"

dss = py_dss_interface.DSSDLL()
dss.text(f'compile [{dss_file}]')
dss.text('edit Reactor.MDV_SUB_1_HSB r=0.0000001 x=0.0000001')
dss.text('edit Transformer.MDV_SUB_1 %loadloss=0.0000001 xhl=0.0000001')
dss.text(f"edit Vsource.SOURCE pu={circuit_pu}")
dss.text(f'set loadmult={load_mult}')
dss.solution_solve()


# 1
# dss.text('Plot Profile Phases=All')

# 2
voltages = dss.circuit_all_bus_vmag_pu()
v_min = min(dss.circuit_all_bus_vmag_pu())
v_max = max(dss.circuit_all_bus_vmag_pu())

# 3

feederhead_KW = -1 * dss.circuit_total_power()[0]
feederhead_Kvar = -1 * dss.circuit_total_power()[1]

# Parte 2
# 1 Buses
mv_buses = list()
bus_voltage_dict = dict()

buses = dss.circuit_all_bus_names()
for bus in buses:
    dss.circuit_set_active_bus(bus)
    kv_bus = dss.bus_kv_base()
    num_phases = len(dss.bus_nodes())

    if kv_bus > 1.0 and num_phases == 3 and bus != 'sourcebus':
        mv_buses.append(bus)
        bus_voltage_dict[bus] = kv_bus

random.seed(location)
selected_buses = random.sample(mv_buses, int(percent * len(mv_buses)))

for bus in selected_buses:
    functions.add_bus_marker(dss, bus, 'green', 4, 15)

    functions.define_3ph_system(dss, bus, bus_voltage_dict[bus], kva_to_kw * p_step, p_step)
dss.solution_solve()
dss.text('interpolate')
#dss.text('plot circuit Power max=2000 n n C1=$00FF0000')

ov_violation = False
thermal_violation = False

i = 0
while not ov_violation and not thermal_violation and i < 20 :
    i += 1

    functions.increment_pv_size(dss, p_step, kva_to_kw, pf, i)
    dss.solution_solve()
    voltages = dss.circuit_all_bus_vmag_pu()
    v_max = max(voltages)
    if v_max > v_limit:
        ov_violation = True


    dss.lines_first()
    for _ in range(dss.lines_count()):
        dss.circuit_set_active_element(f'line.{dss.lines_read_name()}')
        current = dss.cktelement_currents_mag_ang()
        rating_current = dss.cktelement_read_norm_amps()

        if max(current[0:12:2]) > rating_current:
            thermal_violation = True
            break
        dss.lines_next()

functions.increment_pv_size(dss, p_step, kva_to_kw, pf, i - 1)
dss.solution_solve()

penetration_level = (i - 1) * len(selected_buses) * p_step

total_p_feederhead, total_q_feederhead, voltage_min, voltage_max = functions.get_powerflow_results(dss)

total_pv_p, total_pv_q = functions.get_total_pv_powers(dss)


print("here")
