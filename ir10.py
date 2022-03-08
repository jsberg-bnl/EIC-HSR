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
lq1dw_10 = 0.927704
lwd = 5

def fthetac(thc):
    return lwd*(sin(thc-0.5*thd0)+sin(0.5*thc)+sin(0.5*(thc-thd0))) - (2*z0-zc)*sin(thc) + 2*x0*cos(thc)

def dthetac(thc):
    return lwd*(cos(thc-0.5*thd0)+0.5*(cos(0.5*thc)+cos(0.5*(thc-thd0)))) - (2*z0-zc)*cos(thc) - 2*x0*sin(thc)

z0 = lcenxdx+lcendx+lcendxd0+lcend0+(ld0fla+lbeld0q1+lflq1x-lq1dw_10)*cos(thd0)
x0 = lcendx*tan(0.5*thdx) + lcendxd0*tan(thdx) + lcend0*tan(0.5*(thdx+thd0))+(ld0fla+lbeld0q1+lflq1x-lq1dw_10)*sin(thd0)
zc = 5.211+1+1.5

thc = 0.0
e1 = fthetac(thc)
decline = False
while not decline or abs(e1) < abs(e0):
    thc -= e1/dthetac(thc)
    e0 = e1
    e1 = fthetac(thc)
    if abs(e1) < abs(e0):
        decline = True
print(f"{thc:+24.17e}")
