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
lwd2 = 2.0
lww2 = 0.4
lwc = 2
lc2w_wd = 1.36941
lgv = 0.11
lgvfl = 0.2

# IR4
lq3bpm = 5.06*0.0254
lvalve = 3.84*0.0254
lbelw7 = 7.67*0.0254
lk10hz = 2.45*0.0254
lpc = 82.92*0.0254
lwpump = 13.12*0.0254
ljettrans = 12.625*0.0254
ljetfl = 0.97*0.0254
ljet = 24.5*0.0254
ljetall = ljet+2*ljetfl+2*ljettrans
lwdtrans = 0.438
lwdfl = 0.198

lv50 = 0.25
lcav50 = 1.443
li50 = 0.5
ldw50 = 0.5

lw3 = lpld0q1+lq1+lplq1q2+lq2+lplq2q3+lq3+lbq3+lbfl3 \
 +lq3bpm+4*lvalve+7*lbelw7+lk10hz+lpc+3*lwpump+2*ljetall \
 +lwdtrans+lwdfl+2*lwd2+lww2
lw4 = lbq1+lflq1x+lq3bpm+2*lvalve+2*lbelw7+2*lcav50+li50+2*lv50+lwdfl+lwdtrans-lpld0q1
# IR12
lw12 = lwc-lpld0q1
# IR10
lgvwd = 0.42
lh10 = 1.1
l09_0 = (lcenxdx+lcendx+lcendxd0+lcend0-0.5*lh10-lwds*cos(0.5*thd0))/cos(thd0)
l10_0 = lc2w_wd+lgv+lgvfl+lgvwd-lpld0q1

def fth2(th,lw0,n):
    return lcenxdx*sin(thd0+n*th) + lcendx*sin(thd0+n*th-0.5*thdx)/cos(0.5*thdx) \
        + lcendxd0*sin(thd0+n*th-thdx)/cos(thdx) + lcend0*sin(n*th-0.5*(thdx-thd0))/cos(0.5*(thdx+thd0)) \
        - lw0*sin(n*th) - lwd2*fsum([sin((k+0.5)*th) for k in range(0,n)]) - lww2*fsum([sin(k*th) for k in range(1,n)])

def dth2(th,lw0,n):
    return n*lcenxdx*cos(thd0+n*th) + n*lcendx*cos(thd0+n*th-0.5*thdx)/cos(0.5*thdx) \
        + n*lcendxd0*cos(thd0+n*th-thdx)/cos(thdx) + n*lcend0*cos(n*th-0.5*(thdx-thd0))/cos(0.5*(thdx+thd0)) \
        - n*lw0*cos(n*th) \
        - lwd2*fsum([(k+0.5)*cos((k+0.5)*th) for k in range(0,n)]) \
        - lww2*fsum([k*cos(k*th) for k in range(1,n)])

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


def find_th2(lw0,n,chatty=False):
    th = 0.0
    e1 = fth2(th,lw0,n)
    if chatty:
        print(f"{e1:+24.17e}")
    decline = False
    while not decline or abs(e1) < abs(e0):
        th -= fth2(th,lw0,n)/dth2(th,lw0,n)
        e0 = e1
        e1 = fth2(th,lw0,n)
        if chatty:
            print(f"{e1:+24.17e}")
        if abs(e1) < abs(e0):
            decline = True
    return th

print(f"thw04 = {find_th2(0.5*(lw4-lw3),2):+24.17e}")
print(f"thl10 = {find_thc(0.5*(l09_0+l10_0),lwds):+24.17e}")
print(f"thh12 = {find_thc(lw12,lwdl):+24.17e}")
print(f"thw08 = {find_th2(l10_0,3):+24.17e}")
