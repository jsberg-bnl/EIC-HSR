from math import *
import numpy

# RHIC
alpha=0.0
lbfl3=1.539020
lbq1=0.3369448
lbq3=0.47142826+0.597968
lbsk3ly=0.048769
lcend0=3.58870392002
lcendx=3.700000
lcendxd0=7.00564755673002
lcenxdx=9.800000
ld0fla=0.1589964
lflq1x=0.2015744
lpld0q1=1.26464856138
lplq1q2=1.6766315
lplq2q3=1.8607395
lq1=1.440000
lq2=3.391633
lq3=2.100484
rhod0=236.329952479
rhodx=196.1858025048003

lbeld0q1=lpld0q1-ld0fla-lflq1x-lbq1
thd0=asin(sin(alpha) + lcendx/rhodx - lcend0/rhod0)
thdx=asin(sin(alpha) + lcendx/rhodx)

# 
lwdl = 6.0
lwds = 4.4
lwc = 2
lc2w_wd = 1.36941
lgv = 0.11
lgvfl = 0.2

# IR4
lhjet = 2
lpc = 2.5
l3hjpc = 0.35
l3wqhj = 0.5
lv50 = 0.25
lcav50 = 1.443
li50 = 0.5
ldw50 = 0.5

lw3 = lpld0q1+lq1+lplq1q2+lq2+lplq2q3+lq3+lbq3+lbfl3+2*lbsk3ly+lhjet+lpc+l3hjpc+l3wqhj+lwds
lw4 = lc2w_wd+lgv+2*lgvfl+lv50+2*lcav50+li50+ldw50-lpld0q1
# IR12
lw12 = lwc-lpld0q1
# IR10
lgvwd = 0.42
lh10 = 1.1
l09_0 = (lcenxdx+lcendx+lcendxd0+lcend0-0.5*lh10-lwds*cos(0.5*thd0))/cos(thd0)
l10_0 = lc2w_wd+lgv+lgvfl+lgvwd-lpld0q1

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

print(f"thc04 = {find_thc(0.5*(lw4-lw3),lwds):+24.17e}")
print(f"thl10 = {find_thc(0.5*(l09_0+l10_0),lwds):+24.17e}")
print(f"thh12 = {find_thc(lw12,lwdl):+24.17e}")
