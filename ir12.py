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
# 
lwd = 6
lwc = 2
lw12 = lwc-lpld0q1

def fth(thh):
    return lw12*sin(thh-thd0) + lwd*sin(0.5*(thh-thd0)) \
        - lcenxdx*sin(thh) - lcendx*sin(thh-0.5*thdx)/cos(0.5*thdx) \
        - lcendxd0*sin(thh-thdx)/cos(thdx) - lcend0*sin(thh-0.5*(thdx+thd0))/cos(0.5*(thdx+thd0))

def dth(thh):
    return lw12*cos(thh-thd0) + 0.5*lwd*cos(0.5*(thh-thd0)) \
        - lcenxdx*cos(thh) - lcendx*cos(thh-0.5*thdx)/cos(0.5*thdx) \
        - lcendxd0*cos(thh-thdx)/cos(thdx) - lcend0*cos(thh-0.5*(thdx+thd0))/cos(0.5*(thdx+thd0))

thh = thd0
e1 = fth(thh)
print(f"{e1:+24.17e}")
decline = False
while not decline or abs(e1) < abs(e0):
    thh -= fth(thh)/dth(thh)
    e0 = e1
    e1 = fth(thh)
    print(f"{e1:+24.17e}")
    if abs(e1) < abs(e0):
        decline = True
print(f"thh12 = {thh:+24.17e}")
