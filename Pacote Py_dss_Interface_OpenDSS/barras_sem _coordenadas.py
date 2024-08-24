import py_dss_interface
import pandas as pd
import matplotlib.pyplot as plt

circuit_pu = 1.04
load_mult = 0.3


def process(penetration_kw):
    dss.text(f'compile [{dss_file}]')

    dss.text('New Energymeter.m1 Line.ln5815900-1 1')

    # Thevenin Equivalent
    dss.text(f'edit vsource.source pu={circuit_pu}')
    dss.text('edit reactor.MDV_SUB_1_HSB x=0.0000001')
    dss.text('edit transformer.mdv_sub_1 %loadloss=0.0000001 xhl=0.0000001')

    # Control elements
    dss.text('set controlmode=off')
    dss.text('batchedit capacitor..* enable=no')

    # Load models
    dss.text(f'batchedit load..* model=1')
    dss.text('batchedit load..* vmaxpu=1.25')
    dss.text('batchedit load..* vminpu=0.75')

    # load condition
    dss.text(f'set loadmult={load_mult}')

    dss.text('set maxiterations=100')
    # dss.text('set maxcontrols=100')

    dss.text('addbusmarker bus=l3104830 color=red size=8 code=15')

    dss.text(f'new generator.gen phases=3 bus1=l3104830 kv=12.47 pf=1 kw={penetration_kw}')

    dss.solution_solve()

    # return variables
    total_p_feederhead = -1 * dss.circuit_total_power()[0]
    total_q_feederhead = -1 * dss.circuit_total_power()[1]
    losses_kw = dss.circuit_losses()[0] / 10 ** 3
    losses_kvar = dss.circuit_losses()[1] / 10 ** 3
    voltages = dss.circuit_all_bus_vmag_pu()
    voltage_max = max(voltages)
    voltage_min = min(voltages)

    # dss.text('plot profile phases=all')
    # dss.text('plot circuit power max=2000 n n c1=$00ff0000')

    return total_p_feederhead, total_q_feederhead, losses_kw, losses_kvar, voltages, voltage_max, voltage_min


dss_file = r"C:\OpenDss\OpenDSS\OpenDSS\IEEETestCases\8500-Node\Master.dss"
dss = py_dss_interface.DSSDLL()


penetration_kw_list = [penetration * 1000 for penetration in range(0, 11)]


total_p_feederhead = list()
total_q_feederhead = list()
losses_kw = list()
losses_kvar = list()
voltages = list()
voltage_max = list()
voltage_min = list()


for penetration_kw in penetration_kw_list:
    results = process(penetration_kw)

    total_p_feederhead.append(results[0])
    total_q_feederhead.append(results[1])
    losses_kw.append(results[2])
    losses_kvar.append(results[3])
    voltage_max.append(results[4])
    voltage_min.append(results[5])

dict_to_df = dict()
dict_to_df['penetration_kw'] = penetration_kw_list
dict_to_df['feederhead_kw'] = total_p_feederhead
dict_to_df['feederhead_kvar'] = total_q_feederhead
dict_to_df['losses_kw'] = losses_kw
dict_to_df['losses_kvar'] = losses_kvar
dict_to_df['max_v'] = voltage_max
dict_to_df['min_v'] = voltage_min


df = pd.DataFrame().from_dict(dict_to_df)

print('here')

fig, axes = plt.subplots(nrows=3, ncols=2, sharex=True, sharey=True)


axes[0, 0].plot(df['penetration_kw'], df['feederhead_kw'], color='green', label='feederhead_kw')
axes[0, 1].plot(df['penetration_kw'], df['feederhead_kvar'], color='green', label='feederhead_kvar')
axes[1, 0].plot(df['penetration_kw'], df['losses_kw'], color='red', label='losses_kw')
axes[1, 1].plot(df['penetration_kw'], df['losses_kvar'], color='green', label='losses_kvar')
#axes[2, 0].plot(df['penetration_kw'], df['max_v'], color='blue', label='max_v')
axes[2, 0].plot([df['penetration_kw'].min(), df['penetration_kw'].max()], [1.05, 1.05], color='blue', label='1.05')
axes[2, 1].plot(df['penetration_kw'], df['min_v'], color='black', label='min_v')
axes[2, 1].plot([df['penetration_kw'].min(), df['penetration_kw'].max()], [0.95, 0.95], color='black', label='0.95')

for ax_row in axes:
    for ax in ax_row:
        ax.set_xlabel('Penetration Level (kw)')
        ax.legend()
        ax.grid(True)

fig.tight_layout()
plt.show()
