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
lwdl = 6.0
lwds = 4.4
lwc = 2
# IR12
lw12 = lwc-lpld0q1
# IR10
lc2w_wd = 1.36941
lvalve_wd = 0.11
lvalvegap_wd = 0.2
lh10 = 1.1
l09_0 = (lcenxdx+lcendx+lcendxd0+lcend0-0.5*lh10-lwds*cos(0.5*thd0))/cos(thd0)
l10_0 = lc2w_wd+2*lvalvegap_wd+lvalve_wd-lpld0q1

def fth(thc,lw0,lwd):
    return lw0*sin(thc-thd0) + lwd*sin(0.5*(thc-thd0)) \
        - lcenxdx*sin(thc) - lcendx*sin(thc-0.5*thdx)/cos(0.5*thdx) \
        - lcendxd0*sin(thc-thdx)/cos(thdx) - lcend0*sin(thc-0.5*(thdx+thd0))/cos(0.5*(thdx+thd0))

def dth(thc,lw0,lwd):
    return lw0*cos(thc-thd0) + 0.5*lwd*cos(0.5*(thc-thd0)) \
        - lcenxdx*cos(thc) - lcendx*cos(thc-0.5*thdx)/cos(0.5*thdx) \
        - lcendxd0*cos(thc-thdx)/cos(thdx) - lcend0*cos(thc-0.5*(thdx+thd0))/cos(0.5*(thdx+thd0))

def find_thc(lw0,lwd,chatty=False):
    thc = thd0
    e1 = fth(thc,lw0,lwd)
    if chatty:
        print(f"{e1:+24.17e}")
    decline = False
    while not decline or abs(e1) < abs(e0):
        thc -= fth(thc,lw0,lwd)/dth(thc,lw0,lwd)
        e0 = e1
        e1 = fth(thc,lw0,lwd)
        if chatty:
            print(f"{e1:+24.17e}")
        if abs(e1) < abs(e0):
            decline = True
    return thc

print(f"thl10 = {find_thc(0.5*(l09_0+l10_0),lwds):+24.17e}")
print(f"thh12 = {find_thc(lw12,lwdl):+24.17e}")
