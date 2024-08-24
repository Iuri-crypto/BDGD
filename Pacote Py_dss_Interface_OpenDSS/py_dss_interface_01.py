import csv
import random, math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tic
import py_dss_interface

# OpenDSS Obj
dss = py_dss_interface.DSSDLL()

# Configuração do Sistema
#   Passo 1
#   Para cada capacidade de acomodação de VEs,
#   determinar a energia a ser consumida pelos mesmos.
EConsRede = 1373.059 #MWh/30 dias - Dado obtido através do Energy Meter na barra de saída da subestação
CapdeAcom = 15 #Capacidade de acomodação da rede em porcentagem
EConsVEs = (EConsRede*(CapdeAcom/100))*10**6 #Wh

#   Passo 2
#   Para cada capacidade de acomodação de VEs,
#   determinar a quantidade de VEs.
EArmaz = 0.85 #85% de carga para preservação da vida útil da bateria
EArmaz *= 60 #Tesla Model Y (kWh)
CarrComp = (EArmaz / 0.92)*10**3 #Eficiência de roundtrip = 0,92 ; Energia p/ carregamento completo dos VEs


#   Passo 3
#   Para cada capacidade de acomodação de VEs,
#   determinar a localização dos VEs.
#   Distribuir aleatoriamente.
Rede = [701, 702, 703, 730, 709, 708, 733, 734, 737, 738,
        711, 741, 724, 707, 720, 706, 725, 722, 704, 714,
        718, 713, 731, 740, 712, 705, 727, 775, 732, 736,
        710, 735, 742, 744, 728, 729]

if CapdeAcom == 0:
    QtdVEs = 0
else:
    QtdVEs = int(math.ceil(EConsVEs / CarrComp))

    Local_VE = random.choices(Rede, k = QtdVEs) #Randomiza o sistema para distribuição de VEs

    Distr_0 = [Local_VE.count(bus) for bus in Rede] #Distribui os VEs na rede IEEE 37 bus

    size = len(Distr_0)

    Distr = [round(bus) for bus in Distr_0]

dss.text("Clear")
data_path = r"C:\Users\muril\Downloads\2024-20240720T131141Z-001\SIMUL-08-07-2024"
dss.text("set datapath = " + data_path)

dss.text("New object=circuit.ieee37 basekv=230 pu=1.00 MVAsc3=200000 MVAsc1=210000")

#! Substation Transformer
dss.text("New Transformer.SubXF Phases=3 Windings=2 Xhl=0.05 wdg=1 bus=sourcebus conn=Delta kv=230 kva=2500 %r=0.01 wdg=2 bus=799 conn=Delta kv=4.8 kva=2500 %r=0.01")

#! Load shape
dss.text("new loadshape.dailyAD npts=720 interval=1.0 csvfile= demand_daily_AD.txt")
dss.text("new loadshape.dailyBE npts=720 interval=1.0 csvfile= demand_daily_BE.txt")
dss.text("new loadshape.dailyCF npts=720 interval=1.0 csvfile= demand_daily_CF.txt")

for ev in range(144):
      dss.text(f"new loadshape.evloadshape{ev+1} npts=720 interval=1.0 csvfile= evloadshape{ev+1}.dat")

#! Load Transformer
dss.text("New Transformer.XFM1 Phases=3 Windings=2 Xhl=1.81 wdg=1 bus=709 conn=Delta kv=4.80  kva=500 %r=0.045 wdg=2 bus=775 conn=Delta kv=0.48 kva=500 %r=0.045")

#! import line codes with phase impedance matrices
dss.text("Redirect        IEEELineCodes.dss")

#! Lines
dss.text("New Line.L1     Phases=3 Bus1=701.1.2.3  Bus2=702.1.2.3  LineCode=722  Length=0.96")
dss.text("New Line.L2     Phases=3 Bus1=702.1.2.3  Bus2=705.1.2.3  LineCode=724  Length=0.4")
dss.text("New Line.L3     Phases=3 Bus1=702.1.2.3  Bus2=713.1.2.3  LineCode=723  Length=0.36")
dss.text("New Line.L4     Phases=3 Bus1=702.1.2.3  Bus2=703.1.2.3  LineCode=722  Length=1.32")
dss.text("New Line.L5     Phases=3 Bus1=703.1.2.3  Bus2=727.1.2.3  LineCode=724  Length=0.24")
dss.text("New Line.L6     Phases=3 Bus1=703.1.2.3  Bus2=730.1.2.3  LineCode=723  Length=0.6")
dss.text("New Line.L7     Phases=3 Bus1=704.1.2.3  Bus2=714.1.2.3  LineCode=724  Length=0.08")
dss.text("New Line.L8     Phases=3 Bus1=704.1.2.3  Bus2=720.1.2.3  LineCode=723  Length=0.8")
dss.text("New Line.L9     Phases=3 Bus1=705.1.2.3  Bus2=742.1.2.3  LineCode=724  Length=0.32")
dss.text("New Line.L10    Phases=3 Bus1=705.1.2.3  Bus2=712.1.2.3  LineCode=724  Length=0.24")
dss.text("New Line.L11    Phases=3 Bus1=706.1.2.3  Bus2=725.1.2.3  LineCode=724  Length=0.28")
dss.text("New Line.L12    Phases=3 Bus1=707.1.2.3  Bus2=724.1.2.3  LineCode=724  Length=0.76")
dss.text("New Line.L13    Phases=3 Bus1=707.1.2.3  Bus2=722.1.2.3  LineCode=724  Length=0.12")
dss.text("New Line.L14    Phases=3 Bus1=708.1.2.3  Bus2=733.1.2.3  LineCode=723  Length=0.32")
dss.text("New Line.L15    Phases=3 Bus1=708.1.2.3  Bus2=732.1.2.3  LineCode=724  Length=0.32")
dss.text("New Line.L16    Phases=3 Bus1=709.1.2.3  Bus2=731.1.2.3  LineCode=723  Length=0.6")
dss.text("New Line.L17    Phases=3 Bus1=709.1.2.3  Bus2=708.1.2.3  LineCode=723  Length=0.32")
dss.text("New Line.L18    Phases=3 Bus1=710.1.2.3  Bus2=735.1.2.3  LineCode=724  Length=0.2")
dss.text("New Line.L19    Phases=3 Bus1=710.1.2.3  Bus2=736.1.2.3  LineCode=724  Length=1.28")
dss.text("New Line.L20    Phases=3 Bus1=711.1.2.3  Bus2=741.1.2.3  LineCode=723  Length=0.4")
dss.text("New Line.L21    Phases=3 Bus1=711.1.2.3  Bus2=740.1.2.3  LineCode=724  Length=0.2")
dss.text("New Line.L22    Phases=3 Bus1=713.1.2.3  Bus2=704.1.2.3  LineCode=723  Length=0.52")
dss.text("New Line.L23    Phases=3 Bus1=714.1.2.3  Bus2=718.1.2.3  LineCode=724  Length=0.52")
dss.text("New Line.L24    Phases=3 Bus1=720.1.2.3  Bus2=707.1.2.3  LineCode=724  Length=0.92")
dss.text("New Line.L25    Phases=3 Bus1=720.1.2.3  Bus2=706.1.2.3  LineCode=723  Length=0.6")
dss.text("New Line.L26    Phases=3 Bus1=727.1.2.3  Bus2=744.1.2.3  LineCode=723  Length=0.28")
dss.text("New Line.L27    Phases=3 Bus1=730.1.2.3  Bus2=709.1.2.3  LineCode=723  Length=0.2")
dss.text("New Line.L28    Phases=3 Bus1=733.1.2.3  Bus2=734.1.2.3  LineCode=723  Length=0.56")
dss.text("New Line.L29    Phases=3 Bus1=734.1.2.3  Bus2=737.1.2.3  LineCode=723  Length=0.64")
dss.text("New Line.L30    Phases=3 Bus1=734.1.2.3  Bus2=710.1.2.3  LineCode=724  Length=0.52")
dss.text("New Line.L31    Phases=3 Bus1=737.1.2.3  Bus2=738.1.2.3  LineCode=723  Length=0.4")
dss.text("New Line.L32    Phases=3 Bus1=738.1.2.3  Bus2=711.1.2.3  LineCode=723  Length=0.4")
dss.text("New Line.L33    Phases=3 Bus1=744.1.2.3  Bus2=728.1.2.3  LineCode=724  Length=0.2")
dss.text("New Line.L34    Phases=3 Bus1=744.1.2.3  Bus2=729.1.2.3  LineCode=724  Length=0.28")
dss.text("New Line.L35    Phases=3 Bus1=799r.1.2.3 Bus2=701.1.2.3  LineCode=721  Length=1.85")

#! Regulator - open delta with C leading, A lagging, base LDC setting is 1.5 + j3
dss.text('new transformer.reg1a phases=1 windings=2 buses=(799.1.2 799r.1.2) conns="delta delta" kvs="4.8 4.8" kvas="2000 2000" XHL=1')
dss.text("new regcontrol.creg1a transformer=reg1a winding=2 vreg=120 band=2 ptratio=40 ctprim=350 R=-0.201 X=3.348")
dss.text("new transformer.reg1c like=reg1a buses=(799.3.2 799r.3.2)")
dss.text("new regcontrol.creg1c like=creg1a transformer=reg1c R=2.799 X=1.848")
dss.text("New Line.Jumper Phases=1 Bus1=799.2 Bus2=799r.2 r0=1e-3 r1=1e-3 x0=0 x1=0 c0=0 c1=0")

#! spot loads
dss.text("New Load.S701a      Bus1=701.1.2 Phases=1 Conn=Delta Model=1 kV=  4.800 kW= 140.0 kVAR=  70.0 daily=dailyAD status=variable")
dss.text("New Load.S701b      Bus1=701.2.3 Phases=1 Conn=Delta Model=1 kV=  4.800 kW= 140.0 kVAR=  70.0 daily=dailyBE status=variable")
dss.text("New Load.S701c      Bus1=701.3.1 Phases=1 Conn=Delta Model=1 kV=  4.800 kW= 350.0 kVAR= 175.0 daily=dailyAD status=variable")
dss.text("New Load.S712c      Bus1=712.3.1 Phases=1 Conn=Delta Model=1 kV=  4.800 kW=  85.0 kVAR=  40.0 daily=dailyAD status=variable")
dss.text("New Load.S713c      Bus1=713.3.1 Phases=1 Conn=Delta Model=1 kV=  4.800 kW=  85.0 kVAR=  40.0 daily=dailyCF status=variable")
dss.text("New Load.S714a      Bus1=714.1.2 Phases=1 Conn=Delta Model=4 kV=  4.800 kW=  17.0 kVAR=   8.0 daily=dailyAD status=variable")
dss.text("New Load.S714b      Bus1=714.2.3 Phases=1 Conn=Delta Model=4 kV=  4.800 kW=  21.0 kVAR=  10.0 daily=dailyBE status=variable")
dss.text("New Load.S718a      Bus1=718.1.2 Phases=1 Conn=Delta Model=2 kV=  4.800 kW=  85.0 kVAR=  40.0 daily=dailyAD status=variable")
dss.text("New Load.S720c      Bus1=720.3.1 Phases=1 Conn=Delta Model=1 kV=  4.800 kW=  85.0 kVAR=  40.0 daily=dailyCF status=variable")
dss.text("New Load.S722b      Bus1=722.2.3 Phases=1 Conn=Delta Model=4 kV=  4.800 kW= 140.0 kVAR=  70.0 daily=dailyAD status=variable")
dss.text("New Load.S722c      Bus1=722.3.1 Phases=1 Conn=Delta Model=4 kV=  4.800 kW=  21.0 kVAR=  10.0 daily=dailyAD status=variable")
dss.text("New Load.S724b      Bus1=724.2.3 Phases=1 Conn=Delta Model=2 kV=  4.800 kW=  42.0 kVAR=  21.0 daily=dailyBE status=variable")
dss.text("New Load.S725b      Bus1=725.2.3 Phases=1 Conn=Delta Model=1 kV=  4.800 kW=  42.0 kVAR=  21.0 daily=dailyCF status=variable")
dss.text("New Load.S727c      Bus1=727.3.1 Phases=1 Conn=Delta Model=1 kV=  4.800 kW=  42.0 kVAR=  21.0 daily=dailyAD status=variable")
dss.text("New Load.S728       Bus1=728   Phases=3 Conn=Delta Model=1 kV=  4.800 kW= 126.0 kVAR=  63.0 daily=dailyCF status=variable")
dss.text("New Load.S729a      Bus1=729.1.2 Phases=1 Conn=Delta Model=4 kV=  4.800 kW=  42.0 kVAR=  21.0 daily=dailyAD status=variable")
dss.text("New Load.S730c      Bus1=730.3.1 Phases=1 Conn=Delta Model=2 kV=  4.800 kW=  85.0 kVAR=  40.0 daily=dailyBE status=variable")
dss.text("New Load.S731b      Bus1=731.2.3 Phases=1 Conn=Delta Model=2 kV=  4.800 kW=  85.0 kVAR=  40.0 daily=dailyCF status=variable")
dss.text("New Load.S732c      Bus1=732.3.1 Phases=1 Conn=Delta Model=1 kV=  4.800 kW=  42.0 kVAR=  21.0 daily=dailyAD status=variable")
dss.text("New Load.S733a      Bus1=733.1.2 Phases=1 Conn=Delta Model=4 kV=  4.800 kW=  85.0 kVAR=  40.0 daily=dailyBE status=variable")
dss.text("New Load.S734c      Bus1=734.3.1 Phases=1 Conn=Delta Model=1 kV=  4.800 kW=  42.0 kVAR=  21.0 daily=dailyAD status=variable")
dss.text("New Load.S735c      Bus1=735.3.1 Phases=1 Conn=Delta Model=1 kV=  4.800 kW=  85.0 kVAR=  40.0 daily=dailyCF status=variable")
dss.text("New Load.S736b      Bus1=736.2.3 Phases=1 Conn=Delta Model=2 kV=  4.800 kW=  42.0 kVAR=  21.0 daily=dailyBE status=variable")
dss.text("New Load.S737a      Bus1=737.1.2 Phases=1 Conn=Delta Model=4 kV=  4.800 kW= 140.0 kVAR=  70.0 daily=dailyAD status=variable")
dss.text("New Load.S738a      Bus1=738.1.2 Phases=1 Conn=Delta Model=1 kV=  4.800 kW= 126.0 kVAR=  62.0 daily=dailyCF status=variable")
dss.text("New Load.S740c      Bus1=740.3.1 Phases=1 Conn=Delta Model=1 kV=  4.800 kW=  85.0 kVAR=  40.0 daily=dailyAD status=variable")
dss.text("New Load.S741c      Bus1=741.3.1 Phases=1 Conn=Delta Model=4 kV=  4.800 kW=  42.0 kVAR=  21.0 daily=dailyBE status=variable")
dss.text("New Load.S742a      Bus1=742.1.2 Phases=1 Conn=Delta Model=2 kV=  4.800 kW=   8.0 kVAR=   4.0 daily=dailyAD status=variable")
dss.text("New Load.S742b      Bus1=742.2.3 Phases=1 Conn=Delta Model=2 kV=  4.800 kW=  85.0 kVAR=  40.0 daily=dailyCF status=variable")
dss.text("New Load.S744a      Bus1=744.1.2 Phases=1 Conn=Delta Model=1 kV=  4.800 kW=  42.0 kVAR=  21.0 daily=dailyAD status=variable")
if CapdeAcom != 0:
    for k in range(size):
        faseR = random.choice([1, 3])
        if faseR == 1:
            faseS = random.choice([2, 3])
        elif faseR == 3:
            faseS = random.choice([1, 2])
        else:
            faseS = 2
        faseR = str(faseR)
        faseS = str(faseS)
        dss.text(f"New Load.EV{k} Bus1={str(Rede[(random.randrange(1, size))])}.{faseR}.{faseS} Phases=1 Conn=Delta Model=1 kV=4.800 kW={(Distr[k])*3.7} kVAR=0 daily=evloadshape{str(random.randrange(1, 127))} status=variable")
        print(f"New Load.EV{k} Bus1={str(Rede[(random.randrange(1, size))])}.{faseR}.{faseS} Phases=1 Conn=Delta Model=1 kV=4.800 kW={(Distr[k])*3.7} kVAR=0 daily=evloadshape{str(random.randrange(1, 127))} status=variable")

#!! meters (to check energy exports/imports, losses)
#dss.text("new energymeter.MTRSub element=transformer.SubXF terminal=1")

dss.text('Set VoltageBases = "230,4.8,0.48"')
dss.text("CalcVoltageBases")
dss.text("BusCoords IEEE37_BusXY.csv")

# Increase the max control iterations to avoid warning
dss.text('Set MaxControlIter=1000')

dss.cktelement_currents()

# Listas vazias para armazenar os dados
voltage_magnitudes = []
current_magnitudes = []
power_magnitudes = []
tap_commutations = []

# Loop through time steps
for time_step in range(720):
    # Set the mode and solve
    dss.text(f"Set Mode=daily stepsize=1.0h number={time_step + 1}")
    dss.solution_solve()

    # Obtaining voltage magnitudes and tap position
    voltages = dss.circuit_all_bus_vmag_pu()
    voltage_magnitudes.append([np.abs(complex(v)) for v in voltages])
    tap_position = dss.regcontrols_read_tap_number()
    tap_commutations.append(tap_position)

    # Sample, export currents and powers
    dss.text('Sample')
    dss.text('export currents')
    dss.text('export powers')

    # Read current magnitudes and power magnitudes from the exported files
    with open('ieee37_EXP_CURRENTS.csv', 'r', encoding="utf-8") as current_file:
        current_data = list(csv.reader(current_file, delimiter=','))
        current_magnitudes.append([np.abs(complex(current_data[i][1])) for i in range(1, len(current_data))])

    with open('ieee37_EXP_POWERS.csv', 'r', encoding="utf-8") as power_file:
        power_data = list(csv.reader(power_file, delimiter=','))
        power_magnitudes.append([np.abs(complex(power_data[i][2])) for i in range(1, len(power_data))])

# Converte listas para arrays numpy
voltage_magnitudes_array = np.array(voltage_magnitudes)
current_magnitudes_array = np.array(current_magnitudes)
power_magnitudes_array = np.array(power_magnitudes)
tap_commutations_array = np.array(tap_commutations)

# Definindo função para extrair os valores máximos e mínimos das linhas plotadas
def extract_max_min_from_plot(ax):
    max_values = []
    min_values = []

    # Iterando através de cada linha do plot
    for line in ax.get_lines():
        # Extraindo os pontos de dados da linha
        # x_data = line.get_xdata()
        y_data = line.get_ydata()

        # Achando os valores máximos e mínimos nos dados
        max_value = np.max(y_data)
        min_value = np.min(y_data)

        # Acrescentando os valores máximos e mínimos para suas respectivas listas
        max_values.append(max_value)
        min_values.append(min_value)

    # Retornando os valores máximo e mínimo gerais
    return np.max(max_values), np.min(min_values)

# Plots
fig, ax = plt.subplots(2, 2, figsize=(12, 8))

# Plotar tensão
for i in range(36):
    ax[0, 0].plot(voltage_magnitudes_array[:, i], label=f'Bus {i + 1}')
ax[0, 0].set_title('Tensão')
ax[0, 0].set_xlabel('Tempo (h)')
ax[0, 0].set_ylabel('Magnitude (pu)')
ax[0, 0].yaxis.set_major_locator(tic.MaxNLocator(15))

# Plotar corrente
for i in range(36):
    ax[0, 1].plot(current_magnitudes_array[:, i], label=f'Bus {i + 1}')
ax[0, 1].set_title('Corrente')
ax[0, 1].set_xlabel('Tempo (h)')
ax[0, 1].set_ylabel('Magnitude (A)')

# Plotar potência
for i in range(36):
    ax[1, 0].plot(power_magnitudes_array[:, i], label=f'Bus {i + 1}')
ax[1, 0].set_title('Potência')
ax[1, 0].set_xlabel('Tempo (h)')
ax[1, 0].set_ylabel('Magnitude (kW)')

# Plotar a posição do tap
ax[1, 1].plot(tap_commutations_array)
ax[1, 1].set_title('Comutações do Tap')
ax[1, 1].set_xlabel('Tempo (h)')
ax[1, 1].set_ylabel('Posição do Tap')

# Extraindo os valores máximo e mínimo do plot de tensão
exact_max_voltage, exact_min_voltage = extract_max_min_from_plot(ax[0, 0])

# Extraindo os valores máximo e mínimo do plot de corrente
exact_max_current, exact_min_current = extract_max_min_from_plot(ax[0, 1])

# Extraindo os valores máximo e mínimo do plot de potência
exact_max_power, exact_min_power = extract_max_min_from_plot(ax[1, 0])

# Contar quantas vezes o tap comuta
tap_changes_count = sum(1 for i in range(1, len(tap_commutations_array)) if tap_commutations_array[i] != tap_commutations_array[i - 1])

# Printando os resultados
print("Maximum Voltage:", exact_max_voltage)
print("Minimum Voltage:", exact_min_voltage)

print("Maximum Current:", exact_max_current)
print("Minimum Current:", exact_min_current)

print("Maximum Power:", exact_max_power)
print("Minimum Power:", exact_min_power)

print("Tap Changes Count:", tap_changes_count)

plt.tight_layout()
plt.show()

print("here")


dss.cktelement_currents()

