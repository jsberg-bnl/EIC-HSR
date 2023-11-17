import pytao
import os
import re
import sys
import numpy

def optimize(tao,method='lmdif',chatty=False):
    m0 = float(tao.cmd('python merit')[0])
    if chatty:
        print(m0,file=sys.stderr)
    tao.cmd(f'run {method}',raises=False)
    m1 = float(tao.cmd('python merit')[0])
    if chatty:
        print(m1,file=sys.stderr)
    while m1 > 0 and m1 < m0:
        m0 = m1
        tao.cmd(f'run {method}',raises=False)
        m1 = float(tao.cmd('python merit')[0])
        if chatty:
            print(m1,file=sys.stderr)
    return m1

def replace(filename):
    vars = tao.cmd('sho var -bmad -good')
    v = [ re.match(r'^([a-z]\w*)\[([a-z]\w*)\]',l,re.I).group(1,2) for l in vars ]
    with open(filename,'r') as bmad0, open(filename+'+','w') as bmad1:
        for l0 in bmad0:
            for iv, vv in enumerate(v):
                if re.match('^'+vv[0]+r'\['+vv[1]+r'\] *=',l0,re.I):
                    bmad1.write(vars[iv]+'\n')
                    break
            else:
                bmad1.write(l0)
    os.replace(filename,filename+'-')
    os.rename(filename+'+',filename)
    
ir_var = ['use var '+v for v in (
    'ir6w[7:12]',
    'ir6d[5,6,8:11]',
    'ir8[1:5,7,9,11,12,14,17]',
    'ir10[2,4,5,6,10,12,14,15,16,20]',
    'ir12[2,4:6,8:10]',
    'ir2',
    'ir4[1:5,7,9,11:12,14,17]',
    'sx')]

def strength_map(tao):
    tao.cmd('set universe 1 on')
    tao.cmd('veto var *')
    for v in ir_var:
        tao.cmd(v)
    eav = { x[0] : (x[1],float(x[2])) for x in 
            [ re.match(r'^([a-z]\w*)\[([a-z]\w*)\] *= *([-+0-9e.]+)',l,re.I).group(1,2,3)
              for l in tao.cmd('sho var -bmad -good') ] }
    eav |= {
        'QMAIN_PS' : ('I',tao.evaluate('1@ele::qmain_ps[i]')[0]),
        'QTRIM_PS' : ('I',tao.evaluate('1@ele::qtrim_ps[i]')[0])}
    if 'Y4_Q6_PS' in eav:
        eav['YI3_QD6_PS'] = eav.pop('Y4_Q6_PS')
    if 'Y4_Q7_PS' in eav:
        eav['YI3_QF7_PS'] = eav.pop('Y4_Q7_PS')
    eav['YI3_SXD1_PS'] = eav.pop('SXD_PS')
    eav['YI3_SXF1_PS'] = eav.pop('SXF_PS')
    tao.cmd('veto var *')
    tao.cmd('set universe 1 off')
    return eav

def replace_bmad(filename,eav):
    with open(filename,'r') as bmad0, open(filename+'+','w') as bmad1:
        for l0 in bmad0:
            leav = re.match(r'^([a-z]\w*)\[([a-z]\w*)\] *= *([-+0-9e.]+)',l0,re.I)
            if leav and leav.group(1).upper() in eav:
                e = leav.group(1).upper()
                av = eav[e]
                bmad1.write(f'{e}[{av[0]}] = {av[1]:+24.17e}\n')
            else:
                bmad1.write(l0)
    os.replace(filename,filename+'-')
    os.rename(filename+'+',filename)

def replace_madx(filename,eav):
    with open(filename,'r') as madx0, open(filename+'+','w') as madx1:
        for l0 in madx0:
            leav = re.match(r'^([a-z]\w*)[, =]',l0,re.I)
            if leav and leav.group(1).upper() in eav:
                e = leav.group(1).upper()
                av = eav[e]
                if av[0] == 'I':
                    madx1.write(f'{e} = {av[1]:+24.17e};\n')
                else:
                    madx1.write(f'{e}, {av[0]} = {av[1]:+24.17e};\n')
            else:
                madx1.write(l0)
    os.replace(filename,filename+'-')
    os.rename(filename+'+',filename)

ir_files = ('rhic','ir6','ir8n','ir10','ir12','ir2','ir4')

def replace_all_bmad(eav):
    for h in ir_files:
        fn = h+'.bmad'
        replace_bmad(fn,eav)

def replace_all_madx(eav):
    for h in ir_files:
        fn = h+'.madx'
        replace_madx(fn,eav)

def match_hsr(tao):
    tao.cmd('veto var *')
    tao.cmd('veto dat *@*')
    tao.cmd('set global var_limits_on=f')
    tao.cmd('set universe 2 on')
    tao.cmd('set def uni=2')
    tao.cmd(ir_var[0])
    tao.cmd('use dat ir6w.arc')
    residual = [0.0 for i in range(0,8)]
    residual[0] = optimize(tao)
    tao.cmd('set universe 2 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 3 on')
    tao.cmd('set def uni=3')
    tao.cmd(ir_var[1])
    tao.cmd('use dat ir6d.arc')
    residual[1] = optimize(tao)
    tao.cmd('set universe 3 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 4 on')
    tao.cmd('set def uni=4')
    tao.cmd(ir_var[2])
    tao.cmd('use dat ir8.fit[1:7,12:13,15:16]')
    residual[2] = optimize(tao)
    tao.cmd('set universe 4 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 5 on')
    tao.cmd('set def uni=5')
    tao.cmd(ir_var[3])
    tao.cmd('use dat ir10.fit[1,7:9]')
    tao.cmd('use dat ir10.arc')
    residual[3] = optimize(tao)
    tao.cmd('set universe 5 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 6 on')
    tao.cmd('set def uni=6')
    tao.cmd(ir_var[4])
    tao.cmd('use dat ir12.fit[2,4,6]')
    tao.cmd('use dat ir12.beta')
    residual[4] = optimize(tao)
    tao.cmd('set universe 6 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 7 on')
    tao.cmd('set def uni=7')
    tao.cmd(ir_var[5])
    tao.cmd('use dat ir2.kicker')
    tao.cmd('use dat ir2.center')
    residual[5] = optimize(tao)
    tao.cmd('set universe 7 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 8 on')
    tao.cmd('set def uni=8')
    tao.cmd(ir_var[6])
    tao.cmd('use dat ir4.fit[1:7,12:13,15:16]')
    residual[6] = optimize(tao)
    tao.cmd('set universe 8 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    return residual
    
def tunes_hsr(tao,di):
    tao.cmd('set universe * off')
    tao.cmd(f'set ele *@qmain_ps i = 1@ele::qmain_ps[i]|design+{di[0]}')
    tao.cmd(f'set ele *@qtrim_ps i = 1@ele::qtrim_ps[i]|design+{di[1]}')
    tao.cmd('set universe 9:15 recalculate')
    tao.cmd('call set-match.tao')
    residual = match_hsr(tao)
    tao.cmd('set universe 1 on')
    tunes = (
        (
            tao.evaluate('1@lat::phase.a[0&o10int_pr]')[0],
            tao.evaluate('1@lat::phase.a[o10int_pr&yi7_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yi7_int9_3&yo8_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yo8_int9_3&yo9_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yo9_int9_3&yi10_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yi10_int9_3&yi11_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yi11_int9_3&bi12_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[bi12_int9_3&bi1_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[bi1_int9_3&yi2_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yi2_int9_3&yi3_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yi3_int9_3&yo4_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yo4_int9_3&yo5_int9_6]')[0],
            tao.evaluate('1@lat::phase.a[yo5_int9_6&end]')[0]
        ),
        (
            tao.evaluate('1@lat::phase.b[0&o10int_pr]')[0],
            tao.evaluate('1@lat::phase.b[o10int_pr&yi7_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[yi7_int9_3&yo8_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[yo8_int9_3&yo9_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[yo9_int9_3&yi10_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[yi10_int9_3&yi11_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[yi11_int9_3&bi12_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[bi12_int9_3&bi1_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[bi1_int9_3&yi2_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[yi2_int9_3&yi3_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[yi3_int9_3&yo4_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[yo4_int9_3&yo5_int9_6]')[0],
            tao.evaluate('1@lat::phase.b[yo5_int9_6&end]')[0]
        )
    )
    # tunes = (tao.evaluate('1@lat::tune.a[0]/twopi')[0],tao.evaluate('1@lat::tune.b[0]/twopi')[0])
    tao.cmd('set universe 1 off')
    return (tunes,residual)

# One Newton iteration of a tune fit
# Load meas variables with values after match for I0
# Update I0 with new currents
# returns ((nux,nuy),match_error)
# tao state has variables that generated the returned values
def fit_tune1(tao,tune_goal,I0,dI=(1.0,1.0)):
    nua = numpy.sum(tunes_hsr(tao,I0)[0],1)/(2*numpy.pi)
    tao.cmd('set var *|meas = *|model')
    nu0m = numpy.sum(tunes_hsr(tao,(I0[0]-dI[0],I0[1]))[0],1)
    tao.cmd('set var *|model = *|meas')
    nu0p = numpy.sum(tunes_hsr(tao,(I0[0]+dI[0],I0[1]))[0],1)
    tao.cmd('set var *|model = *|meas')
    nu1m = numpy.sum(tunes_hsr(tao,(I0[0],I0[1]-dI[1]))[0],1)
    tao.cmd('set var *|model = *|meas')
    nu1p = numpy.sum(tunes_hsr(tao,(I0[0],I0[1]+dI[1]))[0],1)
    I1 = (numpy.linalg.inv(numpy.transpose(numpy.matrix(((nu0p-nu0m)/dI[0],(nu1p-nu1m)/dI[1]))/(4*numpy.pi))) @
          (numpy.array(tune_goal)-nua)).A1
    tao.cmd('set var *|model = *|meas')
    I0[0] += I1[0]
    I0[1] += I1[1]
    nub = tunes_hsr(tao,I0)
    return (numpy.sum(nub[0],1)/(2*numpy.pi),numpy.sum(nub[1]))

def fit_tune(tao,tune_goal,chatty=False,I0=(0.0,0.0),dI=(1.0,1.0)):
    I = list(I0)
    r = fit_tune1(tao,tune_goal,I,dI)
    if (chatty):
        print(f'Tune: {r[0][0]-tune_goal[0]:+24.17e} {r[0][1]-tune_goal[1]:+24.17e}, Err: {r[1]:+24.17e}')
    e0 = sum(numpy.array(tune_goal)**2)
    e1 = sum((r[0]-tune_goal)**2)
    while e1 > 0 and e1 < e0:
        e0 = e1
        r = fit_tune1(tao,tune_goal,I,dI)
        if (chatty):
            print(f'Tune: {r[0][0]-tune_goal[0]:+24.17e} {r[0][1]-tune_goal[1]:+24.17e}, Err: {r[1]:+24.17e}')
        e1 = sum((r[0]-tune_goal)**2)
    tao.cmd('set universe 1 on')
    tao.cmd('veto var *')
    tao.cmd('veto dat *@*')
    tao.cmd('use var sx')
    tao.cmd('use dat 1@chrom')
    optimize(tao,method='lm')
    tao.cmd('veto var *')
    tao.cmd('veto dat *@*')
    tao.cmd('set universe 1 off')
    return I

tao = pytao.Tao()
tao.init('-quiet -noplot -startup hsr-init.tao')
tao.cmd('set universe * off')
tao.cmd('veto var *')
tao.cmd('veto dat *@*')
