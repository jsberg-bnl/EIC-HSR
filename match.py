import pytao
import os
import re
import sys

def optimize(tao,chatty=False):
    m0 = float(tao.cmd('python merit')[0])
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
    tao.cmd('veto var *')
    tao.cmd('veto dat *@*')
    tao.cmd('set universe 2 on')
    tao.cmd('set def uni=2')
    tao.cmd('use var ir6w[4:]')
    tao.cmd('use dat ir6w.arc')
    tao.cmd('use dat ir6w.opt[1,2,5]')
    optimize(tao)
    tao.cmd('veto dat ir6w.opt[1,2]')
    print('IR6W: '+format(optimize(tao),'+23.16e'))
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
    print('IR6D: '+format(optimize(tao),'+23.16e'))
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
    print('IR8W: '+format(optimize(tao),'+23.16e'))
    tao.cmd('set universe 4 off')
    tao.cmd('veto var *')
    tao.cmd('veto dat *')
    tao.cmd('set universe 5 on')
    tao.cmd('set def uni=5')
    tao.cmd('use var ir8d[6,8,9,11,13:16]')
    tao.cmd('use dat ir8d.arc')
    tao.cmd('use dat ir8d.ir')
    print('IR8D: '+format(optimize(tao),'+23.16e'))
    tao.cmd('set universe 5 off')
    
tao = pytao.Tao()
tao.init('-quiet -noplot -startup hsr-init.tao')
tao.cmd('set universe 1 off')
tao.cmd('set ele *@b_qmain_ps[i] = -5050')
tao.cmd('set ele *@y_qmain_ps[i] = +5050')
tao.cmd('set global lattice_calc_on=f')
tao.cmd('call set-match.tao')
tao.cmd('set global lattice_calc_on=t')

match_hsr(tao)
