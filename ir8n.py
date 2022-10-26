from math import *

# RHIC
alpha=0.0
l7dummy=11.368024
l9dummy=5.458968
lcend0=3.58870392002
lcendx=3.700000
lcendxd0=7.00564755673002
lcenxdx=9.800000
ldip=9.440656
ldps=2.94942686017e+00
ldptot=2.31467343482e+01
ldum1fl=0.377825
ldum2fl=0.365633
lpld0q1=1.26464856138
na=11.0
rhod0=236.329952479
rhodx=196.1858025048003

ldp5=ldptot - 2.0 * ldps - ldip
thd0=asin(sin(alpha) + lcendx/rhodx - lcend0/rhod0)
thdx=asin(sin(alpha) + lcendx/rhodx)

rho=6.0 * ( ldip * ( na + 1.0 ) + ldp5 + 2.0 * ldps ) / pi

thcell=ldip / rho
thd5=ldp5 / rho
thds=ldps / rho

ltrpwd = 2
lwd8 = 7.5
ldd = 0.5

# EIC
ldl8d = l7dummy+ldum1fl-(l9dummy+ldum2fl)
thavg8d = thd5+thds+0.5*thcell

def fthetac(thc):
    return 2*(lcenxdx*sin(thc)
              +lcendx*sin(thc-0.5*thdx)/cos(0.5*thdx)
              +lcendxd0*sin(thc-thdx)/cos(thdx)
              +lcend0*sin(thc-0.5*(thd0+thdx))/cos(0.5*(thd0+thdx))
              -(ltrpwd-lpld0q1)*sin(thc-thd0)) \
              -2*ldl8d*sin(0.5*thcell)*cos(thavg8d+thc) \
              -4*lwd8*sin(0.5*(thc-thd0))*cos(0.25*(thc-thd0)) \
              -2*ldd*sin(0.5*(thc-thd0))

def dthetac(thc):
    return 2*(lcenxdx*cos(thc)
              +lcendx*cos(thc-0.5*thdx)/cos(0.5*thdx)
              +lcendxd0*cos(thc-thdx)/cos(thdx)
              +lcend0*cos(thc-0.5*(thd0+thdx))/cos(0.5*(thd0+thdx))
              -(ltrpwd-lpld0q1)*cos(thc-thd0)) \
              +2*ldl8d*sin(0.5*thcell)*sin(thavg8d+thc) \
              -0.5*lwd8*(cos(0.25*(thc-thd0))+3*cos(0.75*(thc-thd0))) \
              -ldd*cos(0.5*(thc-thd0))

thc = 0.0
e1 = fthetac(thc)
decline = False
while not decline or abs(e1) < abs(e0):
    thc -= e1/dthetac(thc)
    e0 = e1
    e1 = fthetac(thc)
    if abs(e1) < abs(e0):
        decline = True
print(f"thc8 = {thc:+24.17e}")

ldx8w = 2*ldl8d*sin(0.5*thcell)*cos(thavg8d)
ldz8w = 2*ldl8d*sin(0.5*thcell)*sin(thavg8d)

dz8 = 2*(lcenxdx+lcendx+lcendxd0+lcend0+(lpld0q1-ltrpwd)*cos(thd0))+ldz8w
dx8 = 2*(lcendx*tan(0.5*thdx)+lcendxd0*tan(thdx)+lcend0*tan(0.5*(thd0+thdx))+(lpld0q1-ltrpwd)*sin(thd0))+ldx8w

