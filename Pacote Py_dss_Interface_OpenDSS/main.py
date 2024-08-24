import py_dss_interface

# OpenDSS Obj
dss = py_dss_interface.DSSDLL()

dss_file = r"C:\MeuTcc\Paulo_Example\DSSFiles\MASTER_RedeTeste13Barras.dss"

dss.text("compile {}".format(dss_file))

dss.text("solve")
# dss.text("show powers kva elem")
dss.text("show voltage ln nodes")