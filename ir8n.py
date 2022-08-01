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
lwd = 5

# EIC
ldl8w = l7dummy+ldum1fl-(l9dummy+ldum2fl)
thavg8w = thd5+thds+0.5*thcell

def fthetac(thc):
    return 2*(lcenxdx*sin(thc)
              +lcendx*sin(thc-0.5*thdx)/cos(0.5*thdx)
              +lcendxd0*sin(thc-thdx)/cos(thdx)
              +lcend0*sin(thc-0.5*(thd0+thdx))/cos(0.5*(thd0+thdx))
              +(lpld0q1-ltrpwd)*sin(thc-thd0)) \
              -2*ldl8w*sin(0.5*thcell)*cos(thavg8w+thc) \
              -2*lwd*sin(0.5*(thc-thd0))
#    return dz8*sin(thc)-dx8*cos(thc)+2*lwd*sin(0.5*(thc-thd0))


def dthetac(thc):
    return 2*(lcenxdx*cos(thc)
              +lcendx*cos(thc-0.5*thdx)/cos(0.5*thdx)
              +lcendxd0*cos(thc-thdx)/cos(thdx)
              +lcend0*cos(thc-0.5*(thd0+thdx))/cos(0.5*(thd0+thdx))
              +(lpld0q1-ltrpwd)*cos(thc-thd0)) \
              +2*ldl8w*sin(0.5*thcell)*sin(thavg8w+thc) \
              -lwd*cos(0.5*(thc-thd0))
#    return dz8*cos(thc)+dx8*sin(thc)+lwd*cos(0.5*(thc-thd0))

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

ldx8w = 2*ldl8w*sin(0.5*thcell)*cos(thavg8w)
ldz8w = 2*ldl8w*sin(0.5*thcell)*sin(thavg8w)

dz8 = 2*(lcenxdx+lcendx+lcendxd0+lcend0+(lpld0q1-ltrpwd)*cos(thd0))+ldz8w
dx8 = 2*(lcendx*tan(0.5*thdx)+lcendxd0*tan(thdx)+lcend0*tan(0.5*(thd0+thdx))+(lpld0q1-ltrpwd)*sin(thd0))+ldx8w

