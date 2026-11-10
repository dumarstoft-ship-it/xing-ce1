"""Generic competing-rule search for number-sequence questions.
Values are Fractions; the unknown is None.
A 'family' is a callable fam(seq)->bool that must accept seqs with None
(returning False only if the concrete part is already inconsistent).
"""
from fractions import Fraction as F
import itertools, math

# ---------- known sequences ----------
def _primes(n):
    out=[];k=2
    while len(out)<n:
        if all(k%p for p in out if p*p<=k): out.append(k)
        k+=1
    return out
KNOWN={}
KNOWN['primes']=_primes(60)
KNOWN['squares']=[i*i for i in range(0,80)]
KNOWN['cubes']=[i**3 for i in range(0,40)]
KNOWN['pow2']=[2**i for i in range(0,30)]
KNOWN['pow3']=[3**i for i in range(0,20)]
KNOWN['fact']=[math.factorial(i) for i in range(0,12)]
fib=[0,1]
while len(fib)<40: fib.append(fib[-1]+fib[-2])
KNOWN['fib']=fib
KNOWN['tri']=[i*(i+1)//2 for i in range(0,60)]
luc=[2,1]
while len(luc)<30: luc.append(luc[-1]+luc[-2])
KNOWN['lucas']=luc
KNOWN['composite']=[k for k in range(4,300) if any(k%p==0 for p in range(2,int(k**0.5)+1))]
KNOWN['pow2m1']=[2**i-1 for i in range(0,30)]
KNOWN['pow2p1']=[2**i+1 for i in range(0,30)]

# ---------- transforms (propagate None) ----------
def _bin(a,b,op):
    if a is None or b is None: return None
    return op(a,b)
def t_id(s): return list(s)
def t_d1(s): return [_bin(s[i+1],s[i],lambda x,y:x-y) for i in range(len(s)-1)]
def t_d2(s): return t_d1(t_d1(s))
def t_d3(s): return t_d1(t_d2(s))
def t_g2(s): return [_bin(s[i+2],s[i],lambda x,y:x-y) for i in range(len(s)-2)]
def t_sum2(s): return [_bin(s[i+1],s[i],lambda x,y:x+y) for i in range(len(s)-1)]
def t_sum3(s):
    out=[]
    for i in range(len(s)-2):
        a,b,c=s[i],s[i+1],s[i+2]
        out.append(None if None in (a,b,c) else a+b+c)
    return out
def t_prod2(s): return [_bin(s[i+1],s[i],lambda x,y:x*y) for i in range(len(s)-1)]
def _div(x,y):
    if y==0: return 'BAD'
    return F(x)/F(y)
def t_ratio(s):
    out=[]
    for i in range(len(s)-1):
        if s[i] is None or s[i+1] is None: out.append(None)
        elif s[i]==0: out.append('BAD')
        else: out.append(F(s[i+1])/F(s[i]))
    return out
def t_d1ratio(s):
    d=t_d1(s); return t_ratio(d) if 'BAD' not in d else ['BAD']
def t_odd(s): return s[0::2]
def t_even(s): return s[1::2]
def t_sum2ratio(s): return t_ratio(t_sum2(s))
def t_sum2d1(s): return t_d1(t_sum2(s))
def t_g2d1(s): return t_d1(t_g2(s))
def t_prod2d1(s): return t_d1(t_prod2(s))
def t_ratiod1(s):
    r=t_ratio(s)
    if 'BAD' in r: return ['BAD']
    return t_d1(r)
def t_d1d1ratio(s):
    d=t_d2(s); return t_ratio(d)

TRANSFORMS={
 'id':t_id,'d1':t_d1,'d2':t_d2,'d3':t_d3,'g2':t_g2,'sum2':t_sum2,'sum3':t_sum3,
 'prod2':t_prod2,'ratio':t_ratio,'d1ratio':t_d1ratio,'sum2d1':t_sum2d1,'g2d1':t_g2d1,
 'prod2d1':t_prod2d1,'ratiod1':t_ratiod1,'d2ratio':t_d1d1ratio,
}

# ---------- recognizers (on lists with None) ----------
def _conc(d): return [(i,v) for i,v in enumerate(d) if v is not None]
def r_const(d):
    if 'BAD' in d: return False
    c=[v for v in d if v is not None]
    return all(v==c[0] for v in c)
def r_arith(d):
    if 'BAD' in d: return False
    c=_conc(d)
    if len(c)<2: return True
    (i0,v0),(i1,v1)=c[0],c[1]
    step=F(v1-v0)/(i1-i0)
    return all(v==v0+step*(i-i0) for i,v in c)
def r_quad(d):
    if 'BAD' in d: return False
    c=_conc(d)
    if len(c)<3: return True
    pts=c[:3]
    def L(x):
        tot=F(0)
        for j,(xj,yj) in enumerate(pts):
            term=F(yj)
            for k,(xk,_) in enumerate(pts):
                if k!=j: term*=F(x-xk,xj-xk)
            tot+=term
        return tot
    return all(L(i)==v for i,v in c)
def r_geom(d):
    if 'BAD' in d: return False
    c=_conc(d)
    if any(v==0 for _,v in c): return False
    r=None
    for (i0,v0),(i1,v1) in zip(c,c[1:]):
        if i1==i0+1:
            rr=F(v1)/F(v0)
            if r is None: r=rr
            elif rr!=r: return False
    if r is None: return True
    i0,v0=c[0]
    return all(v==v0*r**(i-i0) for i,v in c)
def make_window(K,sign=1,scaled=False,shift=False):
    def rec(d):
        if 'BAD' in d: return False
        c=_conc(d)
        if not c: return True
        n=len(d)
        for o in range(0,len(K)-n+1):
            if scaled:
                m=None;ok=True
                for i,v in c:
                    k=K[o+i]
                    if k==0:
                        if v!=0: ok=False;break
                        continue
                    mm=F(v)/k
                    if m is None: m=mm
                    elif mm!=m: ok=False;break
                if ok and m is not None and m not in (0,): return True
            elif shift:
                cc=None;ok=True
                for i,v in c:
                    x=v-sign*K[o+i]
                    if cc is None: cc=x
                    elif x!=cc: ok=False;break
                if ok: return True
            else:
                if all(v==sign*K[o+i] for i,v in c): return True
        return False
    return rec
RECOG={'const':(r_const,1),'arith':(r_arith,2),'geom':(r_geom,2),'quad':(r_quad,3)}
for nm,K in KNOWN.items():
    RECOG['win:'+nm]=(make_window(K),1)
    RECOG['win:-'+nm]=(make_window(K,sign=-1),1)
    RECOG['winx:'+nm]=(make_window(K,scaled=True),2)
    RECOG['win+c:'+nm]=(make_window(K,shift=True),2)
    RECOG['win-+c:'+nm]=(make_window(K,sign=-1,shift=True),2)

# ---------- family builders ----------
FAMILIES=[]  # (name, func(seq)->bool, strength_func(L, unk_idx)->int, complexity)

def add_tr_family(tname, rname):
    tf=TRANSFORMS[tname]; rf,np_=RECOG[rname]
    def fam(s): return rf(tf(s))
    def strength(L, u):
        s=[F(1)]*L; s[u]=None
        d=tf(s)
        n=len(d)
        dep=sum(1 for v in d if v is None)
        return n-np_-(1 if dep else 0)
    cx={'id':0,'d1':1,'d2':2,'d3':3,'g2':1,'sum2':1,'sum3':2,'prod2':2,'ratio':1,'d1ratio':2,
        'sum2d1':2,'g2d1':2,'prod2d1':3,'ratiod1':2,'d2ratio':3}[tname]
    cr=0 if rname in('const','arith','geom') else (1 if rname.startswith('win:') or rname.startswith('win:-') or rname=='quad' else 2)
    FAMILIES.append((tname+'|'+rname, fam, strength, cx+cr))

for t in TRANSFORMS:
    for r in RECOG:
        add_tr_family(t,r)

# interleaved: odd/even subsequences each with (transform,recognizer) from a small set
SUB=[('id','arith'),('id','geom'),('d1','arith'),('d1','geom'),('ratio','arith'),('id','quad'),
     ('d1','win:primes'),('id','win:primes'),('id','win:squares'),('id','win+c:squares'),('id','win+c:cubes'),('id','win+c:pow2'),
     ('id','win-+c:squares'),('d1','win:-primes'),('id','const'),('d1','const')]
def add_interleave(sa, sb):
    (ta,ra),(tb,rb)=sa,sb
    fa=TRANSFORMS[ta]; fb=TRANSFORMS[tb]; ga,na=RECOG[ra]; gb,nb=RECOG[rb]
    def fam(s): return ga(fa(t_odd(s))) and gb(fb(t_even(s)))
    def strength(L,u):
        s=[F(1)]*L; s[u]=None
        o=fa(t_odd(s)); e=fb(t_even(s))
        so=len(o)-na-(1 if None in o else 0)
        se=len(e)-nb-(1 if None in e else 0)
        if so<0 or se<0: return -1
        return min(so+se, 9)
    FAMILIES.append(('odd['+ta+'|'+ra+']&even['+tb+'|'+rb+']',fam,strength,3))
for sa in SUB:
    for sb in SUB:
        add_interleave(sa,sb)

# recurrences
P=[F(-3),F(-2),F(-1),F(-1,2),F(0),F(1,2),F(1),F(2),F(3),F(3,2),F(-3,2),F(1,3),F(-1,3)]
def add_rec2(p,q,with_t):
    def fam(s):
        eqs=[]
        for n in range(2,len(s)):
            a,b,c=s[n],s[n-1],s[n-2]
            if None in (a,b,c): continue
            eqs.append((n, a-p*b-q*c))
        if with_t:
            if len(eqs)<2: return True
            (n0,r0),(n1,r1)=eqs[0],eqs[1]
            t=F(r1-r0)/(n1-n0)
            return all(r==r0+t*(n-n0) for n,r in eqs)
        else:
            return all(r==eqs[0][1] for n,r in eqs) if eqs else True
    def strength(L,u): return (L-2)-(2 if with_t else 1)-1
    nm='a(n)=%s*a(n-1)+%s*a(n-2)+r%s'%(p,q,'+t*n' if with_t else '')
    FAMILIES.append((nm,fam,strength,2 if (abs(p)<=2 and abs(q)<=2 and p.denominator==1 and q.denominator==1) else 4))
for p in P:
    for q in P:
        if q==0 and p==1: continue
        add_rec2(p,q,False); add_rec2(p,q,True)

def add_rec1_geomterm(p,k):
    def fam(s):
        cs=[]
        for n in range(1,len(s)):
            a,b=s[n],s[n-1]
            if None in (a,b): continue
            cs.append(F(a-p*b)/F(k)**n)
        return all(c==cs[0] for c in cs) if cs else True
    def strength(L,u): return (L-1)-1-1
    FAMILIES.append(('a(n)=%s*a(n-1)+c*%s^n'%(p,k),fam,strength,3))
for p in [F(1),F(2),F(3),F(-1),F(-2),F(1,2)]:
    for k in [F(2),F(3),F(-1),F(-2),F(1,2),F(4),F(5)]:
        add_rec1_geomterm(p,k)

def add_rec1_nmul(k,with_t):
    def fam(s):
        eqs=[]
        for n in range(1,len(s)):
            a,b=s[n],s[n-1]
            if None in (a,b): continue
            eqs.append((n,a-(n+1+k)*b))   # n+1 = 1-based index of a
        if not eqs: return True
        if with_t:
            if len(eqs)<2: return True
            (n0,r0),(n1,r1)=eqs[0],eqs[1]
            t=F(r1-r0)/(n1-n0)
            return all(r==r0+t*(n-n0) for n,r in eqs)
        return all(r==eqs[0][1] for _,r in eqs)
    def strength(L,u): return (L-1)-(2 if with_t else 1)-1
    FAMILIES.append(('a(n)=(n%+d)*a(n-1)+r%s'%(k,'+t*n' if with_t else ''),fam,strength,3))
for k in [-2,-1,0,1,2]:
    add_rec1_nmul(k,False); add_rec1_nmul(k,True)

def add_prod(p,with_t):
    def fam(s):
        eqs=[]
        for n in range(2,len(s)):
            a,b,c=s[n],s[n-1],s[n-2]
            if None in (a,b,c): continue
            eqs.append((n,a-p*b*c))
        if not eqs: return True
        if with_t:
            if len(eqs)<2: return True
            (n0,r0),(n1,r1)=eqs[0],eqs[1]
            t=F(r1-r0)/(n1-n0)
            return all(r==r0+t*(n-n0) for n,r in eqs)
        return all(r==eqs[0][1] for _,r in eqs)
    def strength(L,u): return (L-2)-(2 if with_t else 1)-1
    FAMILIES.append(('a(n)=%s*a(n-1)*a(n-2)+r%s'%(p,'+t*n' if with_t else ''),fam,strength,3))
for p in [F(1),F(-1),F(1,2),F(2)]:
    add_prod(p,False); add_prod(p,True)
def add_quot(with_t):
    def fam(s):
        eqs=[]
        for n in range(2,len(s)):
            a,b,c=s[n],s[n-1],s[n-2]
            if None in (a,b,c): continue
            if b==0: return False
            eqs.append((n,a-F(c)/F(b)))
        if not eqs: return True
        if with_t:
            if len(eqs)<2: return True
            (n0,r0),(n1,r1)=eqs[0],eqs[1]
            t=F(r1-r0)/(n1-n0)
            return all(r==r0+t*(n-n0) for n,r in eqs)
        return all(r==eqs[0][1] for _,r in eqs)
    def strength(L,u): return (L-2)-(2 if with_t else 1)-1
    FAMILIES.append(('a(n)=a(n-2)/a(n-1)+r%s'%('+t*n' if with_t else ''),fam,strength,3))
add_quot(False); add_quot(True)
def add_sq(p,with_t):
    def fam(s):
        eqs=[]
        for n in range(1,len(s)):
            a,b=s[n],s[n-1]
            if None in (a,b): continue
            eqs.append((n,a-p*b*b))
        if not eqs: return True
        if with_t:
            if len(eqs)<2: return True
            (n0,r0),(n1,r1)=eqs[0],eqs[1]
            t=F(r1-r0)/(n1-n0)
            return all(r==r0+t*(n-n0) for n,r in eqs)
        return all(r==eqs[0][1] for _,r in eqs)
    def strength(L,u): return (L-1)-(2 if with_t else 1)-1
    FAMILIES.append(('a(n)=%s*a(n-1)^2+r%s'%(p,'+t*n' if with_t else ''),fam,strength,3))
for p in [F(1),F(-1)]:
    add_sq(p,False); add_sq(p,True)
def add_rec3(x,y,z):
    def fam(s):
        eqs=[]
        for n in range(3,len(s)):
            a,b,c,d=s[n],s[n-1],s[n-2],s[n-3]
            if None in (a,b,c,d): continue
            eqs.append(a-x*b-y*c-z*d)
        return all(r==eqs[0] for r in eqs) if eqs else True
    def strength(L,u): return (L-3)-1-1
    FAMILIES.append(('a(n)=%s*a(n-1)+%s*a(n-2)+%s*a(n-3)+r'%(x,y,z),fam,strength,3))
for x,y,z in itertools.product([-1,0,1,2],[-1,0,1,2],[-1,1,2]):
    add_rec3(F(x),F(y),F(z))

# power forms on the whole sequence: v_i = (a+b i)^k + c ; v_i = base(i)^exp(i)
def add_powshift(k,b):
    def fam(s):
        c=_conc(s)
        if not c: return True
        for a in range(-40,60):
            cc=None;ok=True
            for i,v in c:
                x=v-F(a+b*i)**k
                if cc is None: cc=x
                elif x!=cc: ok=False;break
            if ok: return True
        return False
    def strength(L,u): return L-2-1
    FAMILIES.append(('a_i=(a+%d i)^%d+c'%(b,k),fam,strength,1))
for k in [2,3]:
    for b in [1,2,3,4,-1]:
        add_powshift(k,b)
def add_powshift_t(k,b):
    def fam(s):
        c=_conc(s)
        if len(c)<2: return True
        for a in range(-40,60):
            res=[(i,v-F(a+b*i)**k) for i,v in c]
            (i0,r0),(i1,r1)=res[0],res[1]
            t=F(r1-r0)/(i1-i0)
            if all(r==r0+t*(i-i0) for i,r in res): return True
        return False
    def strength(L,u): return L-3-1
    FAMILIES.append(('a_i=(a+%d i)^%d+c+t*i'%(b,k),fam,strength,3))
for k in [2,3]:
    for b in [1,2]:
        add_powshift_t(k,b)
def add_expshift(base,with_t):
    def fam(s):
        c=_conc(s)
        if len(c)<2: return True
        for a in range(-5,15):
            res=[(i,v-F(base)**(a+i)) for i,v in c]
            if with_t:
                (i0,r0),(i1,r1)=res[0],res[1]
                t=F(r1-r0)/(i1-i0)
                if all(r==r0+t*(i-i0) for i,r in res): return True
            else:
                if all(r==res[0][1] for _,r in res): return True
        return False
    def strength(L,u): return L-(3 if with_t else 2)-1
    FAMILIES.append(('a_i=%s^(a+i)+c%s'%(base,'+t*i' if with_t else ''),fam,strength,2 if not with_t else 3))
for base in [2,3,4,5,-2]:
    add_expshift(base,False); add_expshift(base,True)
def add_powtower(sb,se):
    def fam(s):
        c=_conc(s)
        if not c: return True
        for a in range(-6,12):
            for e in range(-6,8):
                ok=True
                for i,v in c:
                    bb=a+sb*i; ee=e+se*i
                    if bb==0 and ee<=0: ok=False;break
                    if F(bb)**ee!=v: ok=False;break
                if ok: return True
        return False
    def strength(L,u): return L-2-1
    FAMILIES.append(('a_i=(b%+d i)^(e%+d i)'%(sb,se),fam,strength,1))
for sb in [1,-1,2]:
    for se in [1,-1,0]:
        add_powtower(sb,se)
# n-th power with fixed exponent pattern  a_i = m_i^k * sign? (m arithmetic) handled by powshift with c=0.

def search(seq, options, cand_values, min_strength=1, max_cx=99, verbose=True, show_outside=True, outside_top=60):
    """seq: list with None at unknown. options: dict letter->value(F)."""
    L=len(seq); u=seq.index(None)
    res_opts={k:[] for k in options}
    outside=[]
    for name,fam,strength,cx in FAMILIES:
        st=strength(L,u)
        if st<min_strength or cx>max_cx: continue
        try:
            if not fam(seq): continue
        except ZeroDivisionError:
            continue
        hits=[]
        for k,v in options.items():
            s=list(seq); s[u]=v
            try:
                if fam(s): res_opts[k].append((cx,st,name))
            except ZeroDivisionError: pass
        if show_outside:
            sols=[]
            for v in cand_values:
                s=list(seq); s[u]=v
                try:
                    if fam(s):
                        sols.append(v)
                        if len(sols)>3: break
                except ZeroDivisionError: pass
            if sols and len(sols)<=3:
                ins=[x for x in sols if x in options.values()]
                if len(ins)<len(sols):
                    outside.append((cx,-st,name,sols))
    if verbose:
        for k in options:
            lst=sorted(res_opts[k])
            print('  option',k,options[k],': %d rules'%len(lst))
            for cx,st,nm in lst[:25]:
                print('     cx=%d st=%d %s'%(cx,st,nm))
        if show_outside:
            outside.sort()
            print('  rules giving values outside options (cx,strength,name,solutions):')
            for cx,mst,nm,sols in outside[:outside_top]:
                print('     cx=%d st=%d %s -> %s'%(cx,-mst,nm,[str(x) for x in sols]))
    return res_opts, outside
