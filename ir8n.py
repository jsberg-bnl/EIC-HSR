from math import *
import numpy

# RHIC
alpha=0.0
lbq1=0.3369448
lcend0=3.58870392002
lcendx=3.700000
lcendxd0=7.00564755673002
lcenxdx=9.800000
ld0fla=0.1589964
lflq1x=0.2015744
lpld0q1=1.26464856138
rhod0=236.329952479
rhodx=196.1858025048003

thd0=asin(sin(alpha) + lcendx/rhodx - lcend0/rhod0)
thdx=asin(sin(alpha) + lcendx/rhodx)

# Compute DX strength
# DX is aligned to beam at IP side
# DX strength limited to RHIC strength
e_eic = 275e9
e_rhic = 255e9
mp = 938.27208816e6
p_eic = sqrt(e_eic*e_eic-mp*mp)
p_rhic = sqrt(e_rhic*e_rhic-mp*mp)
thdx_eic = asin(lcendx/rhodx*p_rhic/p_eic)
xdx = lcendx*tan(0.5*thdx_eic)

def fx(a):
    xd0 = lcend0*sin(0.5*(thdx-thdx_eic-a))/(cos(0.5*(thdx+thd0))*cos(thdx-0.5*(thdx_eic+a+thd0)))
    return lcendxd0*sin(thdx-thdx_eic-a)/cos(thdx) + xd0*cos(thdx-thdx_eic-a) - lcenxdx*tan(a)*cos(thdx_eic+a) \
        + lcendx*(sin(thdx_eic)*sin(0.5*a)**2/cos(a) + tan(0.5*thdx_eic) - sin(thdx_eic+a-0.5*thdx)/cos(0.5*thdx))

def dx(a):
    xd0 = lcend0*sin(0.5*(thdx-thdx_eic-a))/(cos(0.5*(thdx+thd0))*cos(thdx-0.5*(thdx_eic+a+thd0)))
    dxd0 = -0.5*lcend0*cos(0.5*(thdx-thd0))/(cos(0.5*(thdx+thd0))*cos(thdx-0.5*(thdx_eic+a+thd0))**2)
    return -lcendxd0*cos(thdx-thdx_eic-a)/cos(thdx) + dxd0*cos(thdx-thdx_eic-a) - xd0*sin(thdx-thdx_eic-a) \
        - lcenxdx*(cos(thdx_eic+a)-sin(a)*cos(a)*sin(thdx_eic+a))/cos(a)**2 \
        + lcendx*(0.5*sin(thdx_eic)*tan(a)/cos(a)-cos(thdx_eic+a-0.5*thdx)/cos(0.5*thdx))

a8 = (0.5*lcendx+lcendxd0+0.5*lcend0)/(lcenxdx+lcendxd0+lcendx+0.5*lcend0)*(thdx-thdx_eic)
e1 = fx(a8)
decline = False
while not decline or abs(e1) < abs(e0):
    a8 -= fx(a8)/dx(a8)
    e0 = e1
    e1 = fx(a8)
    if abs(e1) < abs(e0):
        decline = True
print(f"a8 = {a8:+24.17e}")
