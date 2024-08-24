import py_dss_interface

dss_file = r"C:\py_dss_interface_Mini_Curso\pythonProject7\8500-Node\Master-unbal.dss"

dss = py_dss_interface.DSSDLL()

dss.text('compile [{}]'.format(dss_file))
dss.text('New Energymeter.m1 Line.ln5815900-1 1')
dss.text('Set Maxiterations=20')

dss.solution_solve()

# Q1 - 1
p_mw = -1 * dss.circuit_total_power()[0] /10 ** 3
q_mvar = -1 * dss.circuit_total_power()[1] /10 ** 3

# Q1 - 2
losses_mw = dss.circuit_losses()[0] / 10 ** 6
losses_mvar = dss.circuit_losses()[1] / 10 ** 6

# Q1 - 3
losses_line_mw = dss.circuit_line_losses()[0] / 10 ** 3
losses_line_mvar = dss.circuit_line_losses()[1] / 10 ** 3

transformes_losses_mw = losses_mw - losses_line_mw
transformes_losses_mvar = losses_mvar - losses_line_mvar

# Q1 - 4
# a)
dss.lines_write_name('LN6379462-3')
bus1 = dss.lines_read_bus1()
bus2 = dss.lines_read_bus2()

# b)
dss.circuit_set_active_element('line.LN6379462-3')
voltages = dss.cktelement_voltages_mag_ang()
correntes = dss.cktelement_currents_mag_ang()

# c)
powers_into = dss.cktelement_powers()[0:6]

# Q1 - 5
dss.circuit_set_active_bus(bus1)
voltage_bus1 = dss.bus_vmag_angle()

dss.loads_first()
kw_loads_max = 0.0

for i in range(dss.loads_count()):

    kw_load = dss.loads_read_kw()
    if kw_load > kw_loads_max:
        load_name = dss.loads_read_name()
        kw_loads_max = kw_load
        kw_load_powerflow = dss.cktelement_powers()[0]

    dss.loads_next()

# dss.circuit_set_active_element('LOAD.{}'.format(load_name))
# kw_load_powerflow = dss. cktelement_powers()[0]

# Q1 - 7
dss.text('Plot Profile phases=All')



print('here')