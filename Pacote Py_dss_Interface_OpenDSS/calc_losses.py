import py_dss_interface

energy_base = 100000.0
# OpenDSS Obj
dss = py_dss_interface.DSSDLL()

dss_file = r"C:\Program Files\OpenDSS\IEEETestCases\123Bus\IEEE123Master.dss"

dss.text("compile [{}]".format(dss_file))
dss.text('Buscoords BusCoords.dat')
dss.text('New EnergyMeter.Feeder Line.L115 1')

dss.text('Set mode=daily')
dss.text('Set number=24')
dss.text('set stepsize=1h')

energy_factor = 0

for j in range(10):

    dss.loads_first()
    for i in range(dss.loads_count()):
        dss.loads_write_kw(dss.loads_read_kw() * (1 + energy_factor))
        dss.loads_write_kvar(dss.loads_read_kw() * (1 + energy_factor))

        dss.loads_next()

    dss.solution_solve()

    dss.meters_write_name('Feeder')
    energy_cal = dss.meters_register_values()[0]
    losses = dss.meters_register_values()[12]
    dss.meters_reset()

    delta_energy = energy_base - energy_cal

    energy_factor = delta_energy / energy_base

    if abs(delta_energy) < 50.0:
        break

print('Lossses kw {}\nEnergy Cal kwh {}\nEnergy Base kwh {}\nNumber iterações {}'.format(losses, energy_cal, energy_base, j))





