import py_dss_interface
import matplotlib.pyplot as plt
import numpy as np

dss_file = r"C:\py_dss_interface_Mini_Curso\pythonProject7\8500-Node\Master-unbal.dss"

dss = py_dss_interface.DSSDLL()

dss.text('compile [{}]'.format(dss_file))
dss.text('New Energymeter.m1 Line.ln5815900-1 1')
dss.text('New Monitor.m1 Line.ln5815900-1 terminal=1 mode=1 ppolar=false')
dss.text('Set Maxiterations=20')
dss.text('Set maxcontrolit=100')

# Q2 - 1
dss.text('Batchedit Load..* daily=default')

dss.text('Set mode=daily')
dss.text('Set number=24')
dss.text('Set stepsize=1h')
dss.text('Solve')

# Q2 - 2
dss.loads_write_name('328365B0a')
loadshape = dss.loads_read_daily()

# Q2 - 3
dss.monitors_write_name('m1')
pa = dss.monitors_channel(1)
qa = dss.monitors_channel(2)
pb = dss.monitors_channel(3)
qb = dss.monitors_channel(4)
pc = dss.monitors_channel(5)
qc = dss.monitors_channel(6)

pt = np.array(pa) + np.array(pb) + np.array(pc)
qt = np.array(qa) + np.array(qb) + np.array(qc)

plt.plot(range(1, len(pt) + 1), pt, 'g', label='P')
plt.plot(range(1, len(pt) + 1), qt, 'b', label='Q')
plt.title('Daily Active and Reactive Power at Feeder Head')
plt.legend()
plt.ylabel('KW, kvar')
plt.xlabel('hour')
plt.xlim(1, 24)
plt.grid(True)
#plt.show()
plt.savefig(r'C:\py_dss_interface_Mini_Curso\pythonProject7\demanda\curva de carga')

# Q2 -4
power_ativa_max = pt.max()
peak_hour = pt.argmax() + 1
dss.meters_write_name('m1')

feeder_kwh = dss.meters_register_values()[0]
loads_kwh =  dss.meters_register_values()[4]
lossees_kwh = dss.meters_register_values()[12]

print('here')

