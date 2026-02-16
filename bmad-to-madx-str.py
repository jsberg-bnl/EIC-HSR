import os
import re

def bmad_to_madx(bmad,madx):
    for l in bmad:
        m = re.match(r'^([a-z]\w*)\[([a-z]\w*)\] *= *(.*)$',l,re.I)
        if m:
            e,a,v = m.group(1,2,3)
            v = v.replace('[I]','');
            v = v.replace('[K1]','->K1');
            v = v.replace('c_light','clight');
            v = v.replace('C_LIGHT','CLIGHT');
            if re.match('^ *[-+.eE0-9]+ *$',v):
                assign = ' = '
            else:
                assign = ' := '
            if a.upper() == 'I':
                print(e+assign+v+';',file=madx)
            elif a.upper() == 'DB_FIELD':
                print(e+', K0 := -('+v+')/beam->brho;',file=madx)
            elif a.upper() == 'DG':
                sgn='+';
                if v[0] == '-':
                    sgn='-';
                    v = v[1:]
                elif v[0] == '+':
                    v = v[1:]
                print(e+', K0 = G'+e.upper()+sgn+v+';',file=madx)
            else:
                print(e+', '+a+assign+v+';',file=madx)

for name in os.listdir():
    m = re.fullmatch(r'(ir[0-9]+[cn]?|rhic)\.bmad',name)
    if m:
        stem = m.group(1)
        if stem == 'ir6':
            kb0pf = None
            with open(stem+'.madx','r') as madx:
                for l in madx:
                    if re.match(r'kb0pf',l):
                        kb0pf = l.rstrip()
        with open(stem+'.bmad','r') as bmad, open(stem+'.madx','w') as madx:
            bmad_to_madx(bmad,madx)
            if stem == 'ir6' and not kb0pf is None:
                print(kb0pf,file=madx)
