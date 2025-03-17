from math import *
import numpy

# RHIC
alpha=0.0
lbfl3=1.539020
lbfl4=0.612790
lbq1=0.3369448
lbq3=0.47142826+0.597968
lbsk3ly=0.048769
lcend0=3.58870392002
lcend0d5=66.0000298158
lcendx=3.700000
lcendxd0=7.00564755673002
lcenxdx=9.800000
lcor=0.50000
ld0fla=0.1589964
lflq1x=0.2015744
lpld0q1=1.26464856138
lplq1q2=1.6766315
lplq2q3=1.8607395
lq=1.110000
lq1=1.440000
lq2=3.391633
lq3=2.100484
lq4=1.811949
lqb=1.1072776
lqb4=1.1326896
lsxt=0.750000
rhod0=236.329952479
rhodx=196.1858025048003

lbeld0q1=lpld0q1-ld0fla-lflq1x-lbq1
lbc3=0.47142826 - lcor / 2.0
lcq=0.54525 - lcor / 2.0
lcq3a=0.597968 - lcor / 2.0
lcq4=0.5442755 - lcor / 2.0
lplq5q6=14.8110470957 - lq
lqs=0.506050 - lsxt/2.0
lqs4=0.5050755 - lsxt/2.0
thd0=asin(sin(alpha) + lcendx/rhodx - lcend0/rhod0)
thdx=asin(sin(alpha) + lcendx/rhodx)

lsb=lqb - lqs - lsxt
lsb4=lqb4 - lqs - lsxt
lplq4q5=6.0190255-lcq4-lqs-lsxt-lsb-lcor
lplq5d5=lplq5q6/2.0 - lcq - lcor
lpld0d5=lcend0d5/cos(thd0)
lpltemp=lpld0d5-lpld0q1-lplq1q2-lplq2q3-lplq4q5-lplq5d5
lplq3q4=lpltemp-lq1-lq2-lq3-lq4-lq-lsb4-lsb-lqs4-lqs-lcq-lcq4-2*(lsxt+lcor)
l3space = lplq3q4 - lbfl3 - lbc3 - lcor - lcq3a - lbfl4

# 
lwdl = 6.0
lwds = 4.4
lwd2 = 2.0
lww2 = 0.4
lwc = 2
lc2w_wd = 1.36941
lgv = 0.11
lgvfl = 0.2
lwdtrans = 0.438
lwdfl = 0.198

# Common warm items
ltrpbpm = 5.06*0.0254
lbelw7 = 7.67*0.0254
lbelw11 = 11.52*0.0254
lwpump = 13.12*0.0254
ltrpx1=lbq1+lflq1x
ltrp13=lq1+lplq1q2+lq2+lplq2q3+lq3+lbc3+lcor+lcq3a+lbfl3

# IR4
lvalve = 3.84*0.0254
lk10hz = 2.45*0.0254
lpc = 82.92*0.0254
ljettrans = 12.625*0.0254
ljetfl = 0.97*0.0254
ljet = 24.5*0.0254
ljetall = ljet+2*ljetfl+2*ljettrans

lcav50 = 2.05
li50 = lbelw7

lw3 = lpld0q1+ltrp13+ltrpbpm+4*lvalve+7*lbelw7+lk10hz+lpc+3*lwpump+2*ljetall+lwdtrans+lwdfl+2*lwd2+lww2
lw4 = ltrpx1+ltrpbpm+2*lvalve+4*lbelw7+2*lwpump+3*lcav50+2*li50+lwdfl+lwdtrans-lpld0q1

# IR12
lw12 = lwc-lpld0q1
# IR10
lval88 = 0.085
l4trans = 8.5*0.0254
l4trans_new = 72e-3
lgvwd = 0.42
l10_du3_4 = lwdfl+lwdtrans+lbelw11+lwpump+lbelw7+l4trans+ltrpbpm+lval88+l4trans_new
lw09 = lc2w_wd+lgvfl+lgv+lgvwd-lpld0q1
lw10 = lpld0q1+ltrp13+l3space-l10_du3_4

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
print(f"thw08 = {find_th2(lw10,3):+24.17e}")
print(f"thw10 = {find_th2(0.5*(lw09-lw10),2):+24.17e}")
