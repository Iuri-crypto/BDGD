import py_dss_interface
import matplotlib.pyplot as plt
import numpy as np
import random
import functions

random.seed(114)

dss_file = r"C:\py_dss_interface_Mini_Curso\pythonProject7\8500-Node\Master-unbal.dss"

dss = py_dss_interface.DSSDLL()

dss.text('compile [{}]'.format(dss_file))


dss.text('New Energymeter.m1 Line.ln5815900-1 1')
dss.text('New Monitor.m1 Line.ln5815900-1 terminal=1 mode=1 ppolar=false')
dss.text('Set Maxiterations=20')
dss.text('Set maxcontrolit=100')

dss.text('Batchedit Load..* daily=default')

# Q3 PVs
bus_list = dss.circuit_all_bus_names()

bus_3ph_list = list()
bus_kvbase_dict = dict()

for index, bus in enumerate(bus_list):
    dss.circuit_set_active_bus(bus)
    num_phases = len(dss.bus_nodes())
    kv_base = dss.bus_kv_base()

    if num_phases == 3 and kv_base > 1.0:
        bus_3ph_list.append(bus)
        bus_kvbase_dict[bus] = kv_base


pv_buses_list = random.sample(bus_3ph_list, 5)

for pv_bus in pv_buses_list:
    functions.define_3ph_pvsystem_with_transformer(dss, pv_bus, bus_kvbase_dict[pv_bus], 1100, 1000)
    functions.add_bus_marker(dss, pv_bus, 'red')

dss.text('Set mode=daily')
dss.text('Set number=24')
dss.text('Set stepsize=1h')
dss.text('Solve')

toda_as_pvsystem = dss.pvsystems_count()

dss.text('plot circuit power max=2000 dots=n labels=n c1=blue 1ph=3')

# Q3 - 2
dss.monitors_write_name('m1')
pa = dss.monitors_channel(1)
qa = dss.monitors_channel(2)
pb = dss.monitors_channel(3)
qb = dss.monitors_channel(4)
pc = dss.monitors_channel(5)
qc = dss.monitors_channel(6)

pt = np.array(pa) + np.array(pb) + np.array(pc)
qt = np.array(qa) + np.array(qb) + np.array(qc)

plt.plot(list(range(1, len(pt) + 1)), pt, 'g', label='P')
plt.plot(list(range(1, len(pt) + 1)), qt, 'b', label='Q')
plt.title('Daily Active and Reactive Power at Feeder Head with PVs')
plt.legend()
plt.ylabel('KW, kvar')
plt.xlabel('hour')
plt.xlim(1, 24)
plt.grid(True)
plt.show()
plt.savefig(r'C:\py_dss_interface_Mini_Curso\pythonProject7\demanda\com pv')


# Q3 - 2
power_ativa_max = pt.max()
peak_hour = pt.argmax() + 1
dss.meters_write_name('m1')

feeder_kwh = dss.meters_register_values()[0]
loads_kwh =  dss.meters_register_values()[4]
lossees_kwh = dss.meters_register_values()[12]



print("here")