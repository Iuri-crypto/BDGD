def define_3ph_pvsystem_with_transformer(dss, bus, kv, kva, pmpp):

    dss.text('New line.pv_{} phases=3 bus1={} bus2=pv_sec_{} switch=yes'.format(bus, bus, bus))
    dss.text('New transformer.pv_{} phases=3 windings=2 buses=(v_sec_{}, pv_ter_{}) conns=(wye, wye) kvs=({}, 0.48) xhl=5.67 %r=0.4726 kvas=({}, {})'.format(bus, bus, bus, kv, kva, kva))

    dss.text('makebuslist')
    dss.text('setkvbase bus=pv_sec_{} kvll={}'.format(bus, kv))
    dss.text('setkvbase bus=pv_ter_{} kvll=0.48'.format(bus))

    dss.text('New xycurve.mypvst npts=4 xarray=[0 25 75 100] yarray=[1.2 1.0 0.8 0.6]')
    dss.text('new xycurve.myeff npts=4 xarray=[.1 .2 .4 1.0] yarray=[.86 .9 .93 .97]')
    dss.text('new loadshape.myirrad npts=24 interval=1 mult=[0 0 0 0 0 0 .1 .2 .3 .5 .8 .9 1.0 1.0 .99 .9 .7 .4 .1 0 0 0 0 0]')
    dss.text('new tshape.mytemp npts=24 interval=1 temp=[25 25 25 25 25 25 25 25 35 40 45 58 60 68 55 40 35 25 25 25 25 25]')

    dss.text('new pvsystem.pv_{} phases=3 conn=wye bus1=pv_ter_{} kv=0.48 kva={} pmpp={} pf=1 %cutin=0.00005 %cutout=0.00005 varfollowinverter=yes effcurve=myeff p-tcurve=mypvst daily=myirrad tdaily=mytemp'.format(bus, bus, kva, pmpp))
    dss.text('new monitor.pv_{}_v element=transformer.pv_{} terminal=2 mode=0'.format(bus, bus))
    dss.text('new monitor.pv_{}_p element=transformer.pv_{} terminal=2 mode=1 ppolar=no'.format(bus, bus))
    dss.text('new monitor.pv_{}_m element=pvsystem.pv_{} terminal=1 mode=3'.format(bus, bus))

def add_bus_marker(dss, bus, color, size_marker=8, code=15):
    dss.text('addbusmarker bus={} color={} size={} code={}'.format(bus, color, size_marker, code))
