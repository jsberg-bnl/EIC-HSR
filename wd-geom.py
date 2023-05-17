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

lbeld0q1=lpld0q1-ld0fla-lflq1x-lbq1
thd0=asin(sin(alpha) + lcendx/rhodx - lcend0/rhod0)
thdx=asin(sin(alpha) + lcendx/rhodx)

# 
lwd = 6
lwc = 2
# IR12
lw12 = lwc-lpld0q1
# IR10
lcav = 5.211
ltrpcav = 0.370
lw10 = ltrpcav+lcav+lwc+lflq1x+lbq1-lpld0q1

def fth(thc,lw0):
    return lw0*sin(thc-thd0) + lwd*sin(0.5*(thc-thd0)) \
        - lcenxdx*sin(thc) - lcendx*sin(thc-0.5*thdx)/cos(0.5*thdx) \
        - lcendxd0*sin(thc-thdx)/cos(thdx) - lcend0*sin(thc-0.5*(thdx+thd0))/cos(0.5*(thdx+thd0))

def dth(thc,lw0):
    return lw0*cos(thc-thd0) + 0.5*lwd*cos(0.5*(thc-thd0)) \
        - lcenxdx*cos(thc) - lcendx*cos(thc-0.5*thdx)/cos(0.5*thdx) \
        - lcendxd0*cos(thc-thdx)/cos(thdx) - lcend0*cos(thc-0.5*(thdx+thd0))/cos(0.5*(thdx+thd0))

def find_thc(lw0,chatty=False):
    thc = thd0
    e1 = fth(thc,lw0)
    if chatty:
        print(f"{e1:+24.17e}")
    decline = False
    while not decline or abs(e1) < abs(e0):
        thc -= fth(thc,lw0)/dth(thc,lw0)
        e0 = e1
        e1 = fth(thc,lw0)
        if chatty:
            print(f"{e1:+24.17e}")
        if abs(e1) < abs(e0):
            decline = True
    return thc

print(f"thl10 = {find_thc(lw10):+24.17e}")
print(f"thh12 = {find_thc(lw12):+24.17e}")
