import pytao
import os
import re
import sys

def optimize(tao,chatty=False):
    m0 = float(tao.cmd('python merit')[0])
    if chatty:
        print(m0,file=sys.stderr)
    tao.cmd('run lmdif',raises=False)
    m1 = float(tao.cmd('python merit')[0])
    if chatty:
        print(m1,file=sys.stderr)
    while m1 > 0 and m1 < m0:
        m0 = m1
        tao.cmd('run lmdif',raises=False)
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
    
def match_hsr(tao):
    tao.cmd('set universe 2 on')
    tao.cmd('set def uni=2')
    tao.cmd('use var ir6w[4:]')
    tao.cmd('use dat ir6w.arc')
    tao.cmd('use dat ir6w.opt[1,2,5]')
    optimize(tao)
    tao.cmd('veto dat ir6w.opt[1,2]')
    residual = [0.0 for i in range(0,8)]
    residual[0] = optimize(tao)
    tao.cmd('set universe 2 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 3 on')
    tao.cmd('set def uni=3')
    tao.cmd('use var ir6d[5:12]')
    tao.cmd('use dat ir6d.arc')
    tao.cmd('use dat ir6d.opt[1,2,5]')
    optimize(tao)
    tao.cmd('veto dat ir6d.opt[1,2]')
    residual[1] = optimize(tao)
    tao.cmd('set universe 3 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 4 on')
    tao.cmd('set def uni=4')
    tao.cmd('use var ir8w[15:]')
    tao.cmd('use dat ir8w.arc')
    tao.cmd('use dat ir8w.opt[1,2,5]')
    optimize(tao)
    tao.cmd('veto dat ir8w.opt[1,2]')
    residual[2] = optimize(tao)
    tao.cmd('set universe 4 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 5 on')
    tao.cmd('set def uni=5')
    tao.cmd('use var ir8d[6,8,9,11,13:16]')
    tao.cmd('use dat ir8d.arc')
    tao.cmd('use dat ir8d.ir')
    residual[3] = optimize(tao)
    tao.cmd('set universe 5 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set global var_limits_on=f')
    tao.cmd('set universe 6 on')
    tao.cmd('set def uni=6')
    tao.cmd('use var ir10[4:6,8,10]')
    tao.cmd('use dat ir10.fit[2:]')
    residual[4] = optimize(tao)
    tao.cmd('set universe 6 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 7 on')
    tao.cmd('set def uni=7')
    tao.cmd('use var ir12[3:]')
    tao.cmd('use dat ir12.fit')
    tao.cmd('use dat ir12.sym[1:3]')
    residual[5] = optimize(tao)
    tao.cmd('set universe 7 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 8 on')
    tao.cmd('set def uni=8')
    tao.cmd('use var ir2')
    tao.cmd('use dat ir2.kicker')
    tao.cmd('use dat ir2.center')
    residual[6] = optimize(tao)
    tao.cmd('set universe 8 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 9 on')
    tao.cmd('set def uni=9')
    tao.cmd('use var ir4[5:]')
    tao.cmd('use dat ir4.fit')
    tao.cmd('use dat ir4.sym')
    residual[7] = optimize(tao)
    tao.cmd('set universe 9 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    return residual
    
def tunes_hsr(tao,di):
    tao.cmd('set universe * off')
    tao.cmd(f'set ele *@y_qmain_ps i = ele::y_qmain_ps[i]|design+{di[0]}')
    tao.cmd(f'set ele *@b_qmain_ps i = -(ele::y_qmain_ps[i]|design+{di[0]})')
    tao.cmd(f'set ele *@y_qtrim_ps i = ele::y_qtrim_ps[i]|design+{di[1]}')
    tao.cmd(f'set ele *@b_qtrim_ps i = -(ele::y_qtrim_ps[i]|design+{di[1]})')
    tao.cmd('set universe 10:20 recalculate')
    tao.cmd('call set-match.tao')
    residual = match_hsr(tao)
    tao.cmd('set universe 1 on')
    tunes = (
        (
            tao.evaluate('1@lat::phase.a[0&o10int_pr]')[0],
            tao.evaluate('1@lat::phase.a[o10int_pr&yi7_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yi7_int9_3&yo8_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yo8_int9_3&yo9_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[yo9_int9_3&bo10_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[bo10_int9_3&bo11_int9_3]')[0],
            tao.evaluate('1@lat::phase.a[bo11_int9_3&bi12_int9_3]')[0],
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
            tao.evaluate('1@lat::phase.b[yo9_int9_3&bo10_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[bo10_int9_3&bo11_int9_3]')[0],
            tao.evaluate('1@lat::phase.b[bo11_int9_3&bi12_int9_3]')[0],
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

tao = pytao.Tao()
tao.init('-quiet -noplot -startup hsr-init.tao')
tao.cmd('set universe * off')
tao.cmd('veto var *')
tao.cmd('veto dat *@*')
