import sys
import re
import ast
import copy
import itertools
import sybpydb

class db_parser:
    def __init__(self):
        conn = sybpydb.connect(user='harmless',password='harmless',servername='OPSYB1')
        cur = conn.cursor()
        cur.execute('use rhic')
        # geometry
        cur.execute('select name, definition from geometry')
        self.geometry = { e1[0].rstrip() : e1[1].rstrip() for e1 in cur.fetchall() }
        self.geometry['l3y1lsum'] = self.geometry['l3y1lsum'].replace('26.993950','26.993951')
        self.geometry['l3y3l41']  = self.geometry['l3y3l41' ].replace('27.945422','27.945421')
        self.geometry['l3y5l17']  = self.geometry['l3y5l17' ].replace('17.415237','17.415238')
        self.geometry['l3y6l17']  = self.geometry['l3y6l17' ].replace('21.526077','21.526076')
        self.geometry['l3b11l22'] = self.geometry['l3b11l22'].replace('33.21384' ,'33.213841')
        self.geometry['l3b4l31']  = self.geometry['l3b4l31' ].replace('21.077741','21.077740')
        # lines, slots, magnet types
        cur.execute('select name, elements from beam_line')
        self.beam_line = { record[0].rstrip() : record[1].rstrip().split() for record in cur.fetchall() }
        cur.execute('select name, pieces from slot')
        self.slot = { record[0].rstrip() : record[1].rstrip().split() for record in cur.fetchall() }
        cur.execute('select name, type from magnet_piece')
        self.magnet_piece = { e1[0].rstrip() : e1[1].rstrip() for e1 in cur.fetchall() }
        # Device tables
        self.eles = {}
        cur.execute('select name, length from drift')
        self.eles['drift'] = { e1[0].rstrip() : { 'l' : e1[1].rstrip() } for e1 in cur.fetchall() }
        cur.execute('select name, length from solenoid')
        self.eles['solenoid'] = { e1[0].rstrip() : { 'l' : e1[1].rstrip() } for e1 in cur.fetchall() }
        cur.execute('select name, length, angle, tilt from bend')
        self.eles['bend'] = {}
        for e1 in cur.fetchall():
            self.eles['bend'][e1[0].rstrip()] = { 'l' : e1[1].rstrip() }
            if all((name in self.geometry for name in expr_dependents(ast.parse(e1[2].rstrip(),mode='eval')))):
                self.eles['bend'][e1[0].rstrip()]['angle'] = e1[2].rstrip()
            if e1[3]:
                self.eles['bend'][e1[0].rstrip()]['tilt'] = e1[3].rstrip()
        cur.execute('select name, length, strength, tilt from quadrupole')
        self.eles['quadrupole'] = {}
        for e1 in cur.fetchall():
            self.eles['quadrupole'][e1[0].rstrip()] = { 'l' : e1[1].rstrip(), 'k1' : e1[2].rstrip() }
            if e1[3]:
                self.eles['quadrupole'][e1[0].rstrip()]['tilt'] = True
        cur.execute('select name, length, strength from sextupole')
        self.eles['sextupole'] = { e1[0].rstrip() : { 'l' : e1[1].rstrip(), 'k2' : e1[2].rstrip() } for e1 in cur.fetchall() }
        cur.execute('select name, K1L from multipole where K1L is not null')
        self.eles['multipole'] = { e1[0].rstrip() : { 'order' : 1, 'skew': False, 'kl' : e1[1].rstrip() } for e1 in cur.fetchall() }
        cur.execute('select name, K2L, T2 from multipole where K2L is not null')
        self.eles['multipole'].update(
            { e1[0].rstrip() : { 'order' : 2, 'skew' : bool(e1[2]) } for e1 in cur.fetchall() })
        cur.execute('select name, K3L, T3 from multipole where K3L is not null')
        self.eles['multipole'].update(
            { e1[0].rstrip() : { 'order' : 3, 'skew': bool(e1[2]) } for e1 in cur.fetchall() })
        cur.execute('select name, K4L from multipole where K4L is not null')
        self.eles['multipole'].update(
            { e1[0].rstrip() : { 'order' : 4, 'skew': False } for e1 in cur.fetchall() })
        cur.execute('select name, K5L, T5 from multipole where K5L is not null')
        self.eles['multipole'].update(
            { e1[0].rstrip() : { 'order' : 5, 'skew': bool(e1[2]) } for e1 in cur.fetchall() })
        cur.execute('select name, K1L from multipole where K1L is null and K2L is null'
                    ' and K3L is null and K4L is null and K5L is null')
        self.eles['multipole'].update({ e1[0].rstrip() : {} for e1 in cur.fetchall() })
        cur.execute('select name, harmonic_number, voltage from rfcavity')
        self.eles['rfcavity'] = {
            e1[0].rstrip() : { 'harmon' : e1[1].rstrip(), 'voltage' : e1[2].rstrip() } for e1 in cur.fetchall() }
        cur.execute('select name from closed_orbit_corrector where length is null')
        self.eles['kicker'] = { e1[0].rstrip() : {} for e1 in cur.fetchall() }
        cur.execute('select name, length from closed_orbit_corrector where length is not null')
        self.eles['kicker'].update({ e1[0].rstrip() : { 'l' : e1[1].rstrip() } for e1 in cur.fetchall() })
        cur.execute('select name, length, xsize, ysize from collimator')
        self.eles['rcollimator'] = {}
        for e1 in cur.fetchall():
            self.eles['rcollimator'][e1[0].rstrip()] = { 'l' : e1[1].rstrip() }
            if e1[2] is not None:
                self.eles['rcollimator'][e1[0].rstrip()]['x_limit'] = e1[2].rstrip()
            if e1[3] is not None:
                self.eles['rcollimator'][e1[0].rstrip()]['y_limit'] = e1[3].rstrip()

        # Strengths
        cur.execute('select name, definition from strength')
        self.strength = { e1[0].rstrip() : e1[1].rstrip() for e1 in cur.fetchall() }
        
        # SiteWideName mapping
        cur.execute('use RHICgddb')
        cur.execute(
            "select Machine, beamline from NLkeys group by Machine, beamline")
        self.machs = { m[0] : m[1].rstrip() for m in cur.fetchall() }
        # slots is dictionary of lists, keyed on machine
        # each list is an ordered list of slots
        # each slot is a 3-element tuple: (LatticeName,SiteWideName,list of elements)
        # each element is either a string (drift)
        # a two-element tiple of (CorrectorName,CoilList)
        # where CoilList is a list of 3-element tuples of (LatticeName,SiteWideName,Coil)
        # or a 3-element tuple of (LatticeName,SiteWideName,Coil), where Coil is a string or None
        self.slots = {}
        for m in self.machs:
            cur.execute(
                "select NLkeys.SiteWideName, LatticeName, atom_index, fieldMul.FieldName"
                " from (NLoptic inner join NLkeys on NLoptic.NLindex = NLkeys.NLindex"
                "  inner join NLstatic on NLoptic.NLindex = NLstatic.NLindex)"
                " left join (component inner join magnet_data on component.SerialName = magnet_data.SerialName"
                "  inner join fieldMul on magnet_data.FieldName = fieldMul.Element)"
                " on NLkeys.SiteWideName = component.SiteWideName and NLstatic.DeviceName = fieldMul.DeviceName"
                " where Machine = '"+m+"'"
                " order by lattice_index")
            self.slots[m] = []
            ix_atom = 0
            row = self.nl_row(cur)
            for s in self.slot_list(self.machs[m]):
                while row[1] != s:
                    row = self.nl_row(cur)
                # If this is a slot, go through its elements
                eles = self.slot.get(row[1])
                if eles:
                    self.slots[m].append((row[1],row[1] if re.match('g\d+_dx',row[0]) else row[0],[]))
                    eles = eles[:]
                    ix_ele = 0
                    row = self.nl_row(cur)
                    while ix_ele < len(eles):
                        # Special handling of correctors
                        if eles[ix_ele] in self.beam_line and eles[ix_ele][0:3] == 'lmp':
                            coils = []
                            for coil in self.beam_line[eles[ix_ele]]:
                                ix_atom += 1
                                while row[2] > 0 and row[2] <= ix_atom and row[1] != coil:
                                    row = self.nl_row(cur)
                                if row[1] == coil and self.magnet_piece[coil] != 'drift':
                                    coils.append((row[1],row[0],row[3]))
                            self.slots[m][-1][2].append((eles[ix_ele],coils))
                            ix_ele += 1
                        # Not a corrector
                        else:
                            # If it's a beam line, insert the beam line and work on the first element
                            if eles[ix_ele] in self.beam_line:
                                eles[ix_ele:ix_ele+1] = self.beam_line[eles[ix_ele]]
                            # Remove edge multipoles
                            if self.magnet_piece[eles[ix_ele]] == 'multipole' \
                               and eles[ix_ele][0] == 'e' and eles[ix_ele][1] in 'lr' \
                               and ix_ele+2 < len(eles) \
                               and self.magnet_piece[eles[ix_ele+2]] == 'multipole' \
                               and eles[ix_ele+2][0:2] == ('el' if eles[ix_ele][1] == 'r' else 'er'):
                                if self.magnet_piece[eles[ix_ele+1]] == 'sbend' and\
                                   'order' in self.eles['multipole'][eles[ix_ele]] and \
                                   self.eles['multipole'][eles[ix_ele]]['order'] == 1:
                                    # Replace end multipoles on DX elements with edge angles
                                    if self.eles['bend'][eles[ix_ele+1]]['angle'] == 'thdx - alpha':
                                        if eles[ix_ele][0:2] == 'el':
                                            self.eles['bend'][eles[ix_ele+1]]['e1'] = '-alpha'
                                            self.eles['bend'][eles[ix_ele+1]]['e2'] = '+thdx'
                                        else:
                                            self.eles['bend'][eles[ix_ele+1]]['e1'] = '+thdx'
                                            self.eles['bend'][eles[ix_ele+1]]['e2'] = '-alpha'
                                    else:
                                        if eles[ix_ele][0:2] == 'el':
                                            self.eles['bend'][eles[ix_ele+1]]['e1'] = '+alpha'
                                            self.eles['bend'][eles[ix_ele+1]]['e2'] = '-thdx'
                                        else:
                                            self.eles['bend'][eles[ix_ele+1]]['e1'] = '-thdx'
                                            self.eles['bend'][eles[ix_ele+1]]['e2'] = '+alpha'
                                # Remove edge multipoles
                                eles[ix_ele:ix_ele+3] = eles[ix_ele+1:ix_ele+2]
                                ix_atom += 3
                                while row[2] > 0 and row[2] <= ix_atom and row[1] != eles[ix_ele]:
                                    row = self.nl_row(cur)
                            # Replace thin kicker surrounded by drifts with finite length kicker
                            elif eles[ix_ele] == 'olmp0' and ix_ele+2 < len(eles) \
                                 and 'kick' in self.magnet_piece[eles[ix_ele+1]] \
                                 and eles[ix_ele+2] == 'olmp0':
                                eles[ix_ele:ix_ele+3] = eles[ix_ele+1:ix_ele+2]
                                self.eles['kicker'][eles[ix_ele]]['l'] = 'lcor'
                                ix_atom += 3
                                while row[2] > 0 and row[2] <= ix_atom and row[1] != eles[ix_ele]:
                                    row = self.nl_row(cur)
                            else:
                                ix_atom += 1
                                while row[2] > 0 and row[2] <= ix_atom and row[1] != eles[ix_ele]:
                                    row = self.nl_row(cur)
                            # BPMs without a SiteWideName aren't real
                            if eles[ix_ele] != row[1] and eles[ix_ele][:3] == 'bpm':
                                eles[ix_ele:ix_ele+1] = []
                            else:
                                if eles[ix_ele] == row[1]:
                                    if re.match('g\d+_dhx',row[0]):
                                        self.slots[m][-1][2].append((row[1],row[1],row[3]))
                                    else:
                                        self.slots[m][-1][2].append((row[1],row[0],row[3]))
                                else:
                                    self.slots[m][-1][2].append((eles[ix_ele]))
                                ix_ele += 1
                # Wasn't actually a slot
                else:
                    ix_atom += 1

        # Transfer functions
        cur.execute(
            "select trans.FieldName, avg(fudge.Fudge*trans.Transfunc)"
            " from RHICgddb..magnet_field trans join RHICgddb..fieldfudge fudge"
            " on trans.FieldName = fudge.FieldName"
            " group by trans.FieldName")
        self.trans = { t[0].rstrip() : t[1] for t in cur.fetchall() }

        # Power supply lookup tables
        self.ps_to_swn = {}
        self.swn_to_ps = {}
        cur.execute("select Magnet_Name, Name, Polarity from PS_Mag_Wireup")
        for w in cur.fetchall():
            swn = w[0].rstrip().replace('-','_').replace('.','_')
            psn = w[1].rstrip().replace('-','_').replace('.','_')
            pol = w[2]
            if swn in self.swn_to_ps:
                self.swn_to_ps[swn].append((psn,pol))
            else:
                self.swn_to_ps[swn] = [(psn,pol)]
            if psn in self.ps_to_swn:
                self.ps_to_swn[psn].append((swn,pol))
            else:
                self.ps_to_swn[psn] = [(swn,pol)]

    def geometry_expressions(self,lattice_name):
        key = self.magnet_piece[lattice_name]
        if key == 'sbend':
            attrib = self.eles['bend'][lattice_name]
            exprs = [attrib['l']]
            if 'angle' in attrib:
                exprs.append(attrib['angle'])
            if 'e1' in attrib:
                exprs.append(attrib['e1'])
            if 'e2' in attrib:
                exprs.append(attrib['e2'])
            if 'tilt' in attrib:
                exprs.append(attrib['tilt'])
            return exprs
        elif key == 'multipole' and 'order' in self.eles['multipole'][lattice_name] and \
             self.eles['multipole'][lattice_name]['order'] == 1 and 'kl' in self.eles['multipole'][lattice_name]:
            return [ self.eles[key][lattice_name]['kl'] ]
        elif key in self.eles and 'l' in self.eles[key][lattice_name]:
            return [ self.eles[key][lattice_name]['l'] ]
        else:
            return []

    strength_map = { 'quadrupole': 'k1', 'sextupole': 'k2' }
    field_map = { 'quadrupole': 'b1_gradient', 'sextupole': 'b2_gradient' }

    def strength_expression(self,lattice_name):
        key = self.magnet_piece[lattice_name]
        if key == 'quadrupole' or key == 'sextupole':
            return self.eles[key][lattice_name][self.strength_map[key]]
        else:
            return None

    @staticmethod
    def nl_row(cur):
        r = cur.fetchone()
        return (
            r[0].rstrip().replace('-','_').replace('.','_'),
            r[1].rstrip(),
            r[2],
            r[3].rstrip() if r[3] is not None else r[3])

    @staticmethod
    def advance_to_atom(cur,row,ix_atom,lnm):
        while row[2] > 0 and row[2] <= ix_atom and row[1] != lnm:
            row[:] = self.nl_row(cur)
            
    def slot_list(self,name):
        if name in self.beam_line:
            return itertools.chain(*map(lambda n: self.slot_list(n),self.beam_line[name]))
        else:
            return [name]

def expr_dependents(expr):
    if type(expr) is ast.Name:
        return [expr.id]
    elif type(expr) is ast.Call:
        return itertools.chain.from_iterable(expr_dependents(a) for a in expr.args)
    else:
        return itertools.chain.from_iterable(
            expr_dependents(e) for e in (getattr(expr,a) for a in expr._fields) if issubclass(type(e),ast.AST))

class deptree(dict):
    def __init__(self,exprs,variables):
        vars0 = set(itertools.chain(*(expr_dependents(ast.parse(al,mode='eval')) for al in exprs)))
        super().__init__({ v : { 'e' : variables[v] } for v in vars0 })
        while len(vars0) > 0:
            vars1 = set()
            for v in vars0:
                self[v]['c'] = set(expr_dependents(ast.parse(variables[v],mode='eval')))
                for d in self[v]['c']:
                    if d not in self:
                        vars1.add(d)
                        self[d] = { 'e' : variables[d], 'p': {v} }
                    elif 'p' in self[d]:
                        self[d]['p'].add(v)
                    else:
                        self[d]['p'] = {v}
            vars0 = vars1

    def bmad_sorted(self,file=sys.stdout):
        dt = copy.deepcopy(dict(self))
        while len(dt) > 0:
            leaves = sorted(v for v in dt if len(dt[v]['c'])==0)
            for l in leaves:
                if l not in ('pi'):
                    print(l+'='+dt[l]['e'],file=file)
                if 'p' in dt[l]:
                    for p in dt[l]['p']:
                        dt[p]['c'].remove(l)
                del dt[l]

class line:
    def __init__(self,machine,slot0,slot1,db):
        # Dictionary of Lattice Names to list SiteWideName's.
        # List element is either a name of a tuple with (name,coil)
        self.lnms={}
        # Ordered list of slots in the lattice.
        self.slot_list = []
        # Dictionary of slot names to a list of names (SiteWideNames or LatticeNames as appropriate)
        self.slots = {}
        # Dictionary of corrector names to a list of coil SiteWideNames
        self.correctors = {}
        # Dictionary of corrector coil SiteWideNames to coil names
        self.ele_geometry=set()
        self.ele_strength=set()
        state = 0
        for slot in db.slots[machine]:
            if state == 0 and slot[1] == slot0:
                state = 1
            if state == 1:
                self.slot_list.append(slot[1])
                # If slot has only one drift, make the slot a drift rather than a line
                if len(slot[2]) == 1 and slot[2][0] in db.magnet_piece and db.magnet_piece[slot[2][0]] == 'drift':
                    self.update_swns(slot[2][0],slot[1])
                    self.ele_geometry.update(db.geometry_expressions(slot[2][0]))
                else:
                    self.slots[slot[1]] = []
                    for e in slot[2]:
                        # Drift
                        if type(e) is str:
                            self.slots[slot[1]].append(e)
                            self.update_swns(e,None)
                            self.ele_geometry.update(db.geometry_expressions(e))
                        # Corrector
                        elif len(e) == 2:
                            self.slots[slot[1]].append(e[0])
                            self.ele_geometry.add('lcor')
                            self.correctors[e[0]] = e[1]
                            for coil in e[1]:
                                self.ele_geometry.update(db.geometry_expressions(coil[0]))
                                st = db.strength_expression(coil[0])
                                if st:
                                    self.ele_strength.add(st)
                        # Other object (magnet, BPM, etc.)
                        else:
                            self.slots[slot[1]].append(e[1])
                            self.ele_geometry.update(db.geometry_expressions(e[0]))
                            st = db.strength_expression(e[0])
                            if st:
                                self.ele_strength.add(st)
                            self.update_swns(e[0],e[1:3])
            if state == 1 and slot[1] == slot1:
                state = 2

    def update_swns(self,lnm,swn):
        if lnm in self.lnms:
            if swn is not None:
                self.lnms[lnm].add(swn)
        elif swn is None:
            self.lnms[lnm] = set()
        else:
            self.lnms[lnm] = { swn }
            
class line_info:
    def __init__(self,lines):
        self.ele_geometry = set.union(*map(lambda x:x.ele_geometry,lines))
        self.ele_strength = set.union(*map(lambda x:x.ele_strength,lines))
        self.slots = { k:v for l in lines for (k,v) in l.slots.items() }
        self.correctors = { k:v for l in lines for (k,v) in l.correctors.items() }
        self.lnms = { k1 :
                      set.union(*(l1.lnms[k1] for l1 in lines if k1 in l1.lnms))
                      for k1 in { k for l0 in lines for k in l0.lnms } }

def slot_key(s):
    if s[0] in 'by' and s[1] in 'io':
        s = s[0]+s[2:]
    s = re.sub(r'([^0-9])([0-9])([^0-9])',r'\g<1>0\2\3',s)
    return re.sub(r'([^0-9])([0-9])$',r'\g<1>0\2',s)
        
def write_swns(t,db,lnms,file_out):
    if type(t) is str:
        tl = (t,)
    else:
        tl = t
    for (l,s) in sorted(lnms.items(),key=lambda i:slot_key(i[0])):
        if db.magnet_piece[l] in tl:
            for swn in sorted(s,key=lambda s:slot_key(s[0])):
                if swn[0] != l:
                    print(swn[0]+':'+l,file=file_out)

def write_corrector_str_bmad(name,coils,db,file):
    for c in coils:
        if db.magnet_piece[c[0]] == 'quadrupole' and 'k1' in db.eles['quadrupole'][c[0]]:
            ele = db.eles['quadrupole'][c[0]]
            if 'tilt' in ele and ele['tilt']:
                print(name+'[a1]=('+ele['k1']+')*('+ele['l']+')',file=file)
            else:
                print(name+'[b1]=('+ele['k1']+')*('+ele['l']+')',file=file)

def write_attrs(et,e):
    s = ''
    if et == 'bend':
        attrs = (('l','l'),('angle','angle'),('e1','e1'),('e2','e2'),('tilt','ref_tilt'))
    elif et == 'quadrupole':
        attrs = (('l','l'),('tilt','tilt'))
    elif et == 'rfcavity':
        attrs = (('harmon','harmon'),)
    elif et == 'rcollimator':
        attrs = (('l','l'),('x_limit','x_limit'),('y_limit','y_limit'))
    elif et == 'multipole' and 'order' in e and e['order'] == 1 and 'kl' in e:
        attrs = (('kl','k1l'),)
    else:
        attrs = (('l','l'),)
    for a in attrs:
        if a[0] in e:
            s += ','+a[1]
            if type(e[a[0]]) is not bool:
                s += '='+e[a[0]]
    return s

def write_eles(t,bt,et,db,lnms,file_out):
    if type(t) is str:
        tl = (t,)
        btl = (bt,)
    else:
        tl = t
        btl = bt
    for l in sorted(lnms,key=lambda s:slot_key(s)):
        if db.magnet_piece[l] in tl:
            b = btl[tl.index(db.magnet_piece[l])]
            s = l+':'+b;
            if et is not None:
                s += write_attrs(et,db.eles[et][l])
            print(s,file=file_out)

def write_strs(t,db,lnms,file_out):
    for (lnm,swns) in sorted(lnms.items(),key=lambda s:slot_key(s[0])):
        if db.magnet_piece[lnm] == t:
            for swn in sorted(swns,key=lambda s:slot_key(s[0])):
                print(swn[0]+'['+db.strength_map[t]+']='+db.strength_expression(lnm),file=file_out)

def write_ps_to_i(psset,swnset,db,file_out):
    for ps in sorted(psset,key=lambda s:slot_key(s)):
        print(ps+":overlay={",file=file_out)
        print(' '+',\n '.join([swn+'_i[i]:'+('+i' if sgn==1 else '-i')
                           for (swn,sgn) in sorted(db.ps_to_swn[ps],key=lambda s:slot_key(s[0])) if swn in swnset])
              +'},var={i}',file=file_out)

def write_ps(mag_type,field_attr,db,lnms,file_out):
    psset = set()
    swnset = set()
    for (lnm,swns) in sorted(lnms.items(),key=lambda s:slot_key(s[0])):
        if db.magnet_piece[lnm] == mag_type:
            for (swn,coil) in sorted(swns,key=lambda s:slot_key(s[0])):
                if coil:
                    print(swn+'[field_master]=t',file=file_out)
                    print(swn+'_i:overlay={'+swn+'['+field_attr+']:'+f'{db.trans[coil]}'+
                          ('' if 'kick' in mag_type else '/'+swn+'[l]')+'*i}, var={i}',file=file_out)
                    swnset.add(swn)
                    for (ps,sgn) in db.swn_to_ps[swn]:
                        psset.add(ps)
    write_ps_to_i(psset,swnset,db,file_out)

def factorial(n):
    f = n
    while n != 2:
        n -= 1
        f *= n
    return f

def write_ps_cors(db,cors,file_out):
    psset = set()
    swnset = set()
    for (cor,coils) in sorted(cors.items(),key=lambda s:slot_key(s[0])):
        print(cor+'[field_master]=t',file=file_out)
        for (lnm,swn,coiltyp) in coils:
            swnset.add(swn)
            magtyp = db.magnet_piece[lnm]
            if magtyp == 'hkicker':
                print(swn+'_i:overlay={'+cor+'[bl_hkick]:'+f'{db.trans[coiltyp]}'+'*i},var={i}',file=file_out)
            elif magtyp == 'vkicker':
                print(swn+'_i:overlay={'+cor+'[bl_vkick]:'+f'{db.trans[coiltyp]}'+'*i},var={i}',file=file_out)
            elif magtyp == 'quadrupole':
                if 'tilt' in db.eles['quadrupole'][lnm]:
                    print(swn+'_i:overlay={'+cor+'[a1]:'+f'{db.trans[coiltyp]}'+'*i},var={i}',file=file_out)
                else:
                    print(swn+'_i:overlay={'+cor+'[b1]:'+f'{db.trans[coiltyp]}'+'*i},var={i}',file=file_out)
            else: # multipole
                m = db.eles['multipole'][lnm]
                print(swn+'_i:overlay={'+cor
                      +('[b' if m['skew'] else '[a')+f"{m['order']}]:{db.trans[coiltyp]}/{factorial(m['order'])}"
                      +"*i},var={i}",
                      file=file_out)
            if swn in db.swn_to_ps:
                for (ps,sgn) in db.swn_to_ps[swn]:
                    psset.add(ps)
    write_ps_to_i(psset,swnset,db,file_out)

db = db_parser()

arc01b = line('b','bi12_cqs10','bi1_cqs10',db)
# arc05b = line('b','bi4_cqs10','bi5_cqs10',db)
arc11b = line('b','bo10_cqs10','bo11_cqs10',db)

arc03y = line('y','yi2_cqs10','yi3_cqs10',db)
arc05y = line('y','yo4_cqs10','yo5_cqs10',db)
arc07y = line('y','yi6_cqs10','yi7_cqs10',db)
arc09y = line('y','yo8_cqs10','yo9_cqs10',db)
arc11y = line('y','yi10_cqs10','yi11_cqs10',db)

ins10b = line('b','bo10_trp1','bo10_int9_3',db)
ins11b = line('b','bo11_int9_3','bo11_trp1',db)
ins12b = line('b','bi12_trp1','bi12_int9_3',db)

ins03y = line('y','yi3_int9_3','yi3_trp1',db)
ins04y = line('y','yo4_trp1','yo4_int9_3',db)
ins09y = line('y','yo9_int9_3','yo9_trp1',db)
ins10y = line('y','yi10_trp1','yi10_int9_3',db)
ins11y = line('y','yi11_int9_3','yi11_trp1',db)

line_list = (
    arc01b,arc03y,arc05y,arc07y,arc09y,arc11b,arc11y,
    ins03y,ins04y,ins09y,ins10b,ins10y,ins11b,ins11y,ins12b)
for (n,v) in [ (n,v) for (n,v) in globals().items() if type(v) is line and re.match('^[a-z0-9]+$',n) ]:
    v.name = n
all_lines = line_info(line_list)

geometry_deptree = deptree(all_lines.ele_geometry,db.geometry)
strength_deptree = deptree(all_lines.ele_strength,db.strength)

with open('rhic-lat.bmad',mode='w') as file_lat:
    print("! geometry",file=file_lat)
    geometry_deptree.bmad_sorted(file=file_lat)
    print("! drifts",file=file_lat)
    for (l,s) in sorted(all_lines.lnms.items(),key=lambda s:slot_key(s[0])):
        if db.magnet_piece[l] == 'drift' and not (s and type(next(iter(s))) is not str):
            print(l+':drift,l='+db.eles['drift'][l]['l'],file=file_lat)
    print("! things, acting currently like drifts",file=file_lat)
    for (l,s) in sorted(all_lines.lnms.items(),key=lambda s:slot_key(s[0])):
        if db.magnet_piece[l] == 'drift' and s and type(next(iter(s))) is not str:
            print(l+':pipe,l='+db.eles['drift'][l]['l'],file=file_lat)
    print("! elements, with lattice names",file=file_lat)
    print("! dipoles",file=file_lat)
    write_eles('sbend','sbend','bend',db,all_lines.lnms,file_lat)
    print("! quadrupoles",file=file_lat)
    write_eles('quadrupole','quadrupole','quadrupole',db,all_lines.lnms,file_lat)
    print("! sextupoles",file=file_lat)
    write_eles('sextupole','sextupole','sextupole',db,all_lines.lnms,file_lat)
    print("! solenoids",file=file_lat)
    write_eles('solenoid','solenoid','solenoid',db,all_lines.lnms,file_lat)
    print("! kickers",file=file_lat)
    for l in sorted(all_lines.lnms,key=lambda s:slot_key(s)):
        if 'kick' in db.magnet_piece[l]:
            lattrib = ''
            if l in db.eles['kicker']:
                e = db.eles['kicker'][l]
                if 'l' in db.eles['kicker'][l]:
                    lattrib = ',l='+db.eles['kicker'][l]['l']
                if db.magnet_piece[l][0] == 'h':
                    etype = 'hkicker'
                elif db.magnet_piece[l][0] == 'v':
                    etype = 'vkicker'
                else:
                    etype = 'kicker'
            else:
                etype = 'kicker'
            print(l+':'+etype+lattrib,file=file_lat)
    print("! cavities",file=file_lat)
    write_eles('rfcavity','rfcavity','rfcavity',db,all_lines.lnms,file_lat)
    print("! monitors",file=file_lat)
    write_eles(('hmonitor','monitor','vmonitor'),('monitor','monitor','monitor'),None,db,all_lines.lnms,file_lat)
    print("! instruments",file=file_lat)
    write_eles('instrument','instrument',None,db,all_lines.lnms,file_lat)
    print("! collimators",file=file_lat)
    write_eles('rcollimator','rcollimator','rcollimator',db,all_lines.lnms,file_lat)
    print("! markers",file=file_lat)
    write_eles('marker','marker',None,db,all_lines.lnms,file_lat)

    print("! site-wide names", file=file_lat)
    print("! drifts", file=file_lat)
    for (l,s) in sorted(all_lines.lnms.items(),key=lambda s:slot_key(s[0])):
        if db.magnet_piece[l] == 'drift' and s and type(next(iter(s))) is str:
            for ss in sorted(s,key=lambda s:slot_key(s)):
                print(ss+':'+l, file=file_lat)
    print("! things, acting currently like drifts",file=file_lat)
    for (l,s) in sorted(all_lines.lnms.items(),key=lambda s:slot_key(s[0])):
        if db.magnet_piece[l] == 'drift' and s and type(next(iter(s))) is not str:
            for ss in sorted(s,key=lambda s:slot_key(s[0])):
                if ss[0] != l:
                    print(ss[0]+':'+l, file=file_lat)
    print("! dipoles", file=file_lat)
    write_swns('sbend',db,all_lines.lnms,file_lat)
    print("! quadrupoles", file=file_lat)
    write_swns('quadrupole',db,all_lines.lnms,file_lat)
    print("! sextupoles", file=file_lat)
    write_swns('sextupole',db,all_lines.lnms,file_lat)
    print("! solenoids", file=file_lat)
    write_swns('solenoid',db,all_lines.lnms,file_lat)
    print("! kickers",file=file_lat)
    write_swns(('hkick','hkicker','kicker','vkicker'),db,all_lines.lnms,file_lat)
    print("! correctors", file=file_lat)
    for c in sorted(all_lines.correctors,key=lambda c:slot_key(c)):
        print(c+':kicker,l=lcor,scale_multipoles=f',file=file_lat)
    print("! cavities",file=file_lat)
    write_swns('rfcavity',db,all_lines.lnms,file_lat)
    print("! monitors",file=file_lat)
    write_swns(('hmonitor','monitor','vmonitor'),db,all_lines.lnms,file_lat)
    print("! instruments",file=file_lat)
    write_swns('instrument',db,all_lines.lnms,file_lat)
    print("! collimators",file=file_lat)
    write_swns('rcollimator',db,all_lines.lnms,file_lat)
    print("! markers",file=file_lat)
    write_swns('marker',db,all_lines.lnms,file_lat)

    print("! slots that aren't just drifts",file=file_lat)
    for (s,el) in sorted(all_lines.slots.items(),key=lambda s:slot_key(s[0])):
        print(s+':line=('+',\n '.join(el)+')',file=file_lat)
    print("! sections",file=file_lat)
    for l in line_list:
        print(l.name+':line=('+',\n '.join(l.slot_list)+')',file=file_lat)

with open('rhic-ps.bmad',mode='w') as file_ps:
    print("! quadrupoles",file=file_ps)
    write_ps('quadrupole','b1_gradient',db,all_lines.lnms,file_ps)
    print("! sextupoles",file=file_ps)
    write_ps('sextupole','b2_gradient',db,all_lines.lnms,file_ps)
    print("! kickers",file=file_ps)
    write_ps('hkicker','bl_kick',db,all_lines.lnms,file_ps)
    write_ps('vkicker','bl_kick',db,all_lines.lnms,file_ps)
    print("! correctors",file=file_ps)
    write_ps_cors(db,all_lines.correctors,file_ps)

with open('rhic-str.bmad',mode='w') as file_str:
    strength_deptree.bmad_sorted(file=file_str)
    print("! quadrupoles",file=file_str)
    write_strs('quadrupole',db,all_lines.lnms,file_str)
    print("! sextupoles",file=file_str)
    write_strs('sextupole',db,all_lines.lnms,file_str)
    print("! correctors",file=file_str)
    for (cor,coils) in sorted(all_lines.correctors.items(),key=lambda c:slot_key(c[0])):
        write_corrector_str_bmad(cor,coils,db,file_str)
