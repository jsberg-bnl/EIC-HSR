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
lcav = 5.211
ltrpcav = 0.370
lwc = 2
lw10 = ltrpcav+lcav+lwc+lflq1x+lbq1-lpld0q1

def fth(thl):
    return lw10*sin(thl-thd0) + lwd*sin(0.5*(thl-thd0)) \
        - lcenxdx*sin(thl) - lcendx*sin(thl-0.5*thdx)/cos(0.5*thdx) \
        - lcendxd0*sin(thl-thdx)/cos(thdx) - lcend0*sin(thl-0.5*(thdx+thd0))/cos(0.5*(thdx+thd0))

def dth(thl):
    return lw10*cos(thl-thd0) + 0.5*lwd*cos(0.5*(thl-thd0)) \
        - lcenxdx*cos(thl) - lcendx*cos(thl-0.5*thdx)/cos(0.5*thdx) \
        - lcendxd0*cos(thl-thdx)/cos(thdx) - lcend0*cos(thl-0.5*(thdx+thd0))/cos(0.5*(thdx+thd0))

thl = thd0
e1 = fth(thl)
print(f"{e1:+24.17e}")
decline = False
while not decline or abs(e1) < abs(e0):
    thl -= fth(thl)/dth(thl)
    e0 = e1
    e1 = fth(thl)
    print(f"{e1:+24.17e}")
    if abs(e1) < abs(e0):
        decline = True
print(f"thl10 = {thl:+24.17e}")
