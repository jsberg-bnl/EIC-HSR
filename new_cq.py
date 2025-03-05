import os
import sys
import re
import ast
import copy
import itertools
import sybpydb
import getpass

class db_parser:
    def __init__(self):
        user = input('Username: ')
        pw = getpass.getpass()
        conn = sybpydb.connect(user=user,password=pw,servername='OPSYB1')
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
                    self.slots[m].append((row[1],row[1] if re.match(r'g\d+_dx',row[0]) else row[0],[]))
                    eles = eles[:]
                    ix_ele = 0
                    # First pass, expand beamlines that aren't correctors
                    while ix_ele < len(eles):
                        while eles[ix_ele] in self.beam_line and eles[ix_ele][0:3] != 'lmp':
                            eles[ix_ele:ix_ele+1] = self.beam_line[eles[ix_ele]]
                        ix_ele += 1
                    remove_ap = re.match('^str[0-9]{2}('+m+'3|g0)$',s)
                    if remove_ap:
                        oapid = 0
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
                            # Remove apertures from du3 slots
                            elif remove_ap and ( re.match('^ap[0-9]+p[0-9]+[BGY]$',eles[ix_ele]) or
                                                 re.match('^o(3'+m+'|x)[0-9]+[al][0-9]+$',eles[ix_ele]) ):
                                len_exprs = []
                                while ix_ele < len(eles) and (
                                        re.match('^ap[0-9]+p[0-9]+[BGY]$',eles[ix_ele]) or
                                        re.match('^o(3'+m+'|x)[0-9]+[al][0-9]+$',eles[ix_ele]) ):
                                    mat = re.match('^(o(3'+m+'|x)[0-9]+)[al][0-9]+$',eles[ix_ele])
                                    if mat:
                                        stem = mat[1]
                                        len_exprs.append(self.eles['drift'][eles[ix_ele]]['l'])
                                    ix_atom += 1
                                    while row[2] > 0 and row[2] <= ix_atom and row[1] != eles[ix_ele]:
                                        row = self.nl_row(cur)
                                    eles[ix_ele:ix_ele+1] = []
                                if len(len_exprs):
                                    eles[ix_ele:ix_ele] = [stem+'c'+str(oapid)]
                                    oapid += 1
                                    self.magnet_piece[eles[ix_ele]] = 'drift'
                                    self.eles['drift'][eles[ix_ele]] = {'l':'+'.join(len_exprs)}
                                elif ix_ele >= len(eles):
                                    # End of the slot
                                    break
                                else:
                                    # Only removed a marker, don't output anything or advance ix_ele
                                    continue
                            else:
                                ix_atom += 1
                                while row[2] > 0 and row[2] <= ix_atom and row[1] != eles[ix_ele]:
                                    row = self.nl_row(cur)
                            # BPMs without a SiteWideName aren't real
                            if eles[ix_ele] != row[1] and eles[ix_ele][:3] == 'bpm':
                                eles[ix_ele:ix_ele+1] = []
                            else:
                                if eles[ix_ele] == row[1]:
                                    if re.match(r'g\d+_dhx',row[0]):
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

    def output_sorted(self,file_bmad,file_madx):
        dt = copy.deepcopy(dict(self))
        while len(dt) > 0:
            leaves = sorted(v for v in dt if len(dt[v]['c'])==0)
            for l in leaves:
                if l not in ('pi'):
                    print_both(l+'='+dt[l]['e'],file_bmad,file_madx)
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
        self.coil_types = set()
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

def factorial(n):
    f = 1
    i = 2
    while i <= n:
        f *= i
        i += 1
    return f

def gencor(lnm,coil,db):
    kind = db.magnet_piece[lnm]
    if kind == 'hkicker':
        mp = +1
    elif kind == 'vkicker':
        mp = -1
    elif kind == 'quadrupole':
        mp = -2 if 'tilt' in db.eles['quadrupole'][lnm] and db.eles['quadrupole'][lnm]['tilt'] else +2
    elif kind == 'sextupole':
        mp = +3
    else:
        mpe = db.eles['multipole'][lnm]
        mp = mpe['order']+1
        if mpe['skew']:
            mp = -mp
    return (mp,coil)

class cqslot :
    def __init__(self,db):
        good_flanges = ('obfl','oflq1x','oflq2a','obfl3')
        qtypes = set()
        for s in db.slots['y']+db.slots['b']:
            if any((type(e) is tuple and len(e) == 3 and db.magnet_piece[e[0]] == 'quadrupole' for e in s[2])) \
               and (s[2][0] in good_flanges or s[2][-1] in good_flanges):
                qtype = tuple((((db.eles[db.magnet_piece[e[0]]][e[0]]['l'] if db.magnet_piece[e[0]] in db.eles else 'lcor',
                                 gencor(e[0],e[2],db)) if len(e) == 3 and type(e[2]) is str \
                                else (0, e[0]) if len(e) == 3 and e[2] is None
                                else ('lcor',tuple((gencor(c[0],c[2],db) for c in e[1])))) if type(e) is tuple
                               else e for e in s[2]))
                if s[2][0] not in good_flanges:
                    qtype = qtype[::-1]
                qtypes.add(qtype)
        self.cqlist = {}
        for cq in qtypes:
            if cq[0] == 'oflq1x':
                name = 'tp1'
            elif cq[0] == 'oflq2a':
                name = 'tp2'+cq[3][1][0][1][1].lower()
            elif cq[0] == 'obfl3':
                name = 'tp3'+cq[3][1][0][1][1].lower()
            elif cq[3][1][1] == 'SRE':
                if type(cq[7][1][0]) is int:
                    name = 'cqs'+cq[7][1][1][1].lower()
                else:
                    name = 'cqs'+cq[7][1][0][1][1].lower()
            elif cq[3][1][1] == 'QRT':
                if cq[5][1][1] == 'QR4':
                    name = 'cq4'+cq[7][1][0][1][1].lower()
                else:
                    name = 'cqt'+cq[7][1][0][1][1].lower()
            elif cq[3][1][1] == 'QR7':
                name = 'cq7'+cq[5][1][0][1][1].lower()
            elif cq[2] == 'oqbms':
                name = 'cq8'+cq[5][1][0][1][1].lower()
            else:
                name = 'cqb'+cq[5][1][0][1][1].lower()
            self.cqlist[name] = cq

    # id is a 2-element sequence of str: (line,index).
    # Example: ('h5','9')
    # list(cqs.cqlist) gives the possible values for kind
    def print_cq(self,id,kind,reverse,db,file_bmad,file_madx):
        l = []
        for e in self.cqlist[kind][::-1] if reverse else self.cqlist[kind]:
            if type(e) is str:
                l.append(e)
            elif type(e[0]) is int:
                name=id[0]+'_b'+('h' if db.magnet_piece[e[1]]=='hmonitor'
                                 else 'v' if db.magnet_piece[e[1]]=='vmonitor' else '')+id[1]
                print(name+':monitor',file=file_bmad)
                print(name+':'+db.magnet_piece[e[1]]+';',file=file_madx)
                l.append(name)
            else:
                if type(e[1][0]) is int:
                    if e[1][0] == 1:
                        name = id[0]+'_th'+id[1]
                        print(name+':hkicker,l=lcor,field_master=t',file=file_bmad)
                        print(name+'_i:overlay={'+name+'[bl_kick]:'+f'{db.trans[e[1][1]]}'+'*i},var={i}',file=file_bmad)
                        print(name+':hkicker,l=lcor;',file=file_madx)
                        print(name+f',kick:={-db.trans[e[1][1]]}*'+name+'_i/beam->brho;',file=file_madx)
                    elif e[1][0] == -1:
                        name = id[0]+'_tv'+id[1]
                        print(name+':vkicker, l=lcor,field_master=t',file=file_bmad)
                        print(name+'_i:overlay={'+name+'[bl_kick]:'+f'{db.trans[e[1][1]]}'+'*i},var={i}',file=file_bmad)
                        print(name+':vkicker, l=lcor;',file=file_madx)
                        print(name+f',kick:={-db.trans[e[1][1]]}*'+name+'_i/beam->brho;',file=file_madx)
                    elif e[1][0] == 2:
                        name = id[0]+('_tq' if e[0]=='lsxt' else '_q')+id[1]
                        print(name+':quadrupole,l='+e[0]+',field_master=t',file=file_bmad)
                        print(name+'_i:overlay={'+name+'[b1_gradient]:'+f'{db.trans[e[1][1]]}'+'*i/'+e[0]+'},var={i}',
                              file=file_bmad)
                        print(name+':quadrupole,l='+e[0]+';',file=file_madx)
                        print(name+f',k1:={-db.trans[e[1][1]]}/'+e[0]+'*'+name+'_i/beam->brho;',file=file_madx)
                    elif e[1][0] == 3:
                        name = id[0]+'_sx'+id[1]
                        print(name+':sextupole,l='+e[0]+',field_master=t',file=file_bmad)
                        print(name+'_i:overlay={'+name+'[b2_gradient]:'+f'{db.trans[e[1][1]]}'+'*i/'+e[0]+'},var={i}',
                              file=file_bmad)
                        print(name+':sextupole,l='+e[0]+';',file=file_madx)
                        print(name+f',k2:={-db.trans[e[1][1]]}/'+e[0]+'*'+name+'_i/beam->brho;',file=file_madx)
                else:
                    name = id[0]+'_cor'+id[1]
                    print(name+': kicker, l=lcor',file=file_bmad)
                    coils = []
                    for coil in e[1]:
                        if coil[0] == 1:
                            f = 'bl_hkick'
                            n = 'th'
                            madtype = 'hkicker'
                        elif coil[0] == -1:
                            f = 'bl_vkick'
                            n = 'tv'
                            madtype = 'vkicker'
                        else:
                            f = ('b' if coil[0] > 0 else 'a')+f'{abs(coil[0])-1}'
                            n = f
                            madtype = 'multipole'
                        swn = id[0]+'_'+n+id[1]
                        coils.append(swn)
                        print(swn+'_i:overlay={'+name+'['+f+']:'+
                              f'{db.trans[coil[1]]/factorial(abs(coil[0])-1)}'+'*i},var={i}',file=file_bmad)
                        if n[0] == 't':
                            print(swn + ':' + madtype + ',kick:=' + f'{-db.trans[coil[1]]}*'+swn+'_i/beam->brho;', file=file_madx)
                        else:
                            print(swn + ':' + madtype + (',knl:={' if coil[0]>0 else ',ksl:={') + (abs(coil[0])-1)*'0,'
                                  + f'{-db.trans[coil[1]]}*'+swn+'_i/beam->brho};',file=file_madx)
                    print(name+':line=(olmp0,'+','.join(coils)+',olmp0);',file=file_madx)
                l.append(name)
        print(id[0]+'_'+kind+id[1]+':line=('+','.join(l)+')',file=file_bmad)
        print(id[0]+'_'+kind+id[1]+':line=('+','.join(l)+');',file=file_madx)

def usage():
    print('Usage:')
    print('  python new_cq.py ls')
    print('  python new_cq.py id idx type rev')
    print('    id:   an arbitrary string for the region')
    print('    idx:  a number indicating which slot in the sequence')
    print('    type: one of the types returned by "ls"')
    print('    rev:  b or c, depending on which end is first')
    exit(1)

db = db_parser()
cqs = cqslot(db)

if len(sys.argv) == 1:
    usage()
elif sys.argv[1] == 'ls':
    for cq in sorted(cqs.cqlist):
        print(cq)
elif len(sys.argv) <= 4:
    usage()
else:
    if sys.argv[3] in cqs.cqlist and sys.argv[4] in ('b','c'):
        if len(sys.argv) == 7:
            bmad = open(sys.argv[5],'a')
            madx = open(sys.argv[6],'a')
        else:
            bmad = sys.stdout
            madx = sys.stdout
        null = open(os.devnull,'w')
        cqs.print_cq((sys.argv[1],sys.argv[2]),sys.argv[3],sys.argv[4]=='c',db,bmad,null)
        cqs.print_cq((sys.argv[1],sys.argv[2]),sys.argv[3],sys.argv[4]=='c',db,null,madx)
    else:
        usage()
