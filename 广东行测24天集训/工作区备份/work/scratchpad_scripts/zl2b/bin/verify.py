# Independent verification for ZL2B questions. Each function returns (answer, detail dict).
from datetime import date, timedelta
R = {}
def nearest(v, opts):
    d = {k: abs(v - x) for k, x in opts.items()}
    s = sorted(d, key=d.get); return s[0], d
def reg(k):
    def w(f): R[k] = f; return f
    return w

# ---------------- HB2023 M4 雨季 ----------------
Y=2021
S = {'华南':(date(Y,4,26),date(Y,7,2),67,494.6,(+20,-4,-24,-31)),
     '西南':(date(Y,6,4),date(Y,10,4),122,634.5,(+9,-10,-19,-15)),
     '华北':(date(Y,7,12),date(Y,9,9),59,276.4,(-6,+22,+28,+103)),
     '东北':(date(Y,6,5),date(Y,8,29),85,364.3,(-17,+4,+21,+23)),
     '华西':(date(Y,8,23),None,77,379.9,(-8,+7,+15,+87))}
# (start offset vs normal: +late/-early, end offset: +late/-early, length offset, rain %)
@reg('HB2023-126')
def _():
    for k,v in S.items():
        if v[1]: assert (v[1]-v[0]).days==v[2], k
    starts=sorted(S.items(), key=lambda kv: kv[1][0])
    a,b=starts[-1],starts[-2]
    diff=(a[1][0]-b[1][0]).days
    ans,_=nearest(diff,{'A':34,'B':35,'C':41,'D':42}); return ans, dict(latest=[a[0],b[0]], diff=diff)
@reg('HB2023-127')
def _():
    normal=379.9/1.87; inc=379.9-normal
    ans,d=nearest(inc,{'A':153.4,'B':176.7,'C':203.2,'D':232.5}); return ans, dict(normal=normal,inc=inc,trap_C_is_normal=round(normal,1))
@reg('HB2023-128')
def _():
    nl={k:v[2]-v[4][2] for k,v in S.items()}
    best=max(nl,key=nl.get); m={'华南':'A','西南':'B','东北':'C','华西':'D'}
    return m[best], nl
@reg('HB2023-129')
def _():
    daily={k:v[3]/v[2] for k,v in S.items()}
    cand={'A':'西南','B':'华北','C':'东北','D':'华西'}
    best=max(cand,key=lambda c:daily[cand[c]]); return best, {k:round(x,3) for k,x in daily.items()}
@reg('HB2023-130')
def _():
    A = date(Y,10,7) <= S['西南'][1]
    normal_mei=267.2/0.78; B_val=780.9/normal_mei-1   # 高出 = 1.279 -> 127.9%, option says 227.9%
    B = abs(B_val-2.279)<0.01
    C = False  # 2021 华西 rain is max since 1961 -> 2020 <= 379.9 ; "超过379.9" cannot hold
    nl_db=S['东北'][2]-S['东北'][4][2]; nl_hb=S['华北'][2]-S['华北'][4][2]
    D = 2 < nl_db/nl_hb < 3
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(B_ratio=780.9/normal_mei, B_gaochu=B_val, D_ratio=nl_db/nl_hb, normal_mei=normal_mei)
@reg('ZL2B-ADP-HB2023')
def _():
    # adapted: 可以判断属实
    A = False  # 华北雨季长度为1961年以来第二长, not 最长
    B = False  # 江南出梅偏晚3天 -> not all earlier
    n_dongbei = S['东北'][0] + timedelta(days=17); n_xinan = S['西南'][0] - timedelta(days=9)
    C = n_dongbei < n_xinan
    end_huaxi = S['华西'][0] + timedelta(days=77)
    D = end_huaxi.month == 11
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(normal_dongbei_start=str(n_dongbei), normal_xinan_start=str(n_xinan), huaxi_end=str(end_huaxi), huaxi_end_inclusive=str(end_huaxi-timedelta(days=1)))

# ---------------- HB2025 M1 著作权 ----------------
@reg('HB2025-111')
def _():
    g23=0.4046; g22=g23-0.39; v21=8923901/(1+g23)/(1+g22)
    return nearest(v21/1e4,{'A':626,'B':656,'C':685,'D':728})[0], dict(g22=g22, v21=v21, trap_D_onestep=8923901/1.4046/1e4*1.146)
@reg('HB2025-112')
def _():
    bj22=1101072-53802; tot22=6428277/1.423; s=bj22/tot22
    return nearest(s*100,{'A':10,'B':13,'C':18,'D':23})[0], dict(bj22=bj22,tot22=tot22,share=s, trap_2023share=1101072/6428277)
@reg('HB2025-113')
def _():
    tot22=6428277/1.423; sh22=0.9532-0.0486; v=tot22*sh22/1e4
    return nearest(v,{'A':369,'B':389,'C':409,'D':429})[0], dict(v=v, trap_2023=(3296437+2501968+329128)/1e4, check_95_32=(3296437+2501968+329128)/6428277, trap_samepct=tot22*0.9532/1e4)
@reg('HB2025-114')
def _():
    v=917149.06/361-78668.34/50
    return nearest(v,{'A':1135,'B':1056,'C':967,'D':825})[0], dict(v=v)
@reg('HB2025-115')
def _():
    A_val=8923901-6428277-411; A = A_val==2495213
    inc=6428277-6428277/1.423; B = inc>2e6
    tot22=411/1.1743; zp22=50/(1-0.2647); sw22=tot22-zp22
    C = 361/411 > sw22/tot22
    avg23=78668.34/50; avg22=(78668.34/(1-0.5513))/zp22; D = avg23<avg22
    # question: 不能推出 -> the false/undeterminable one
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if not v]; assert len(ans)==1
    return ans[0], dict(A_val=A_val, inc=inc, sw_share23=361/411, sw_share22=sw22/tot22, avg23=avg23, avg22=avg22)

# ---------------- HB2025 M4 纸及纸板 ----------------
@reg('HB2025-126')
def _():
    g22=0.0435-0.0171; v21=12425/(1+g22)
    return nearest(v21,{'A':11715,'B':12105,'C':12762,'D':13227})[0], dict(g22=g22, v21=v21, chk_g23=12965/12425-1, trap_D=12965/(1-0.0171)+0, trap_samerate=12425/1.0435)
@reg('HB2025-127')
def _():
    c22=0.0614-0.0808; p22=0.0435-0.0171; d=(c22-p22)*100
    return nearest(d,{'A':-4.58,'B':-0.5,'C':5.37,'D':1.79})[0], dict(c22=c22,p22=p22,diff_pp=d)
@reg('HB2025-128')
def _():
    nat=12965/12425-1; r={'东部':0.0544,'中部':0.0251,'西部':0.0143}
    hi=[k for k,v in r.items() if v>nat]; m={('东部',):'A',('中部',):'B',('东部','中部'):'C',('东部','西部'):'D'}
    return m[tuple(hi)], dict(nat=nat, hi=hi)
@reg('HB2025-129')
def _():
    ratio=68.2/19.2; more=ratio-1
    opts={'A':(4,99),'B':(3,4),'C':(2,3),'D':(1,2)}
    ans=[k for k,(lo,hi) in opts.items() if lo<=more<hi]; assert len(ans)==1
    return ans[0], dict(ratio=ratio, more=more, chk_east=8843/12965)
@reg('HB2025-130')
def _():
    A=None  # 纸浆产量 not separable: 29139 = 纸浆 + 纸及纸板12965 + 纸制品
    B = 93.37/1.063 > 90
    ec=(0.682+0.192)*12965; C = not (12597 > ec)   # if 18 provinces all east/central, their sum <= ec
    D = 8019/269 <= 30
    t={'A':False,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(B_val=93.37/1.063, east_central_total=ec, D_ratio=8019/269)

# ---------------- SC2020S M3 小微 ----------------
@reg('SC2020S-96')
def _():
    n1=105.39e4/510.63; n2=938.58e4/4547.40; n3=2.30e4/11.16; n4=19.28e4/93.50
    return ('A' if n1<3000 else 'X'), dict(n_rev=n1,n_asset=n2,n_vat=n3,n_pay=n4)
@reg('SC2020S-97')
def _():
    gr17=0.031; gr16=0.031+0.157; ga17=0.042; ga16=0.042+0.009
    ch=(1+gr17)*(1+gr16)/((1+ga17)*(1+ga16))-1
    ans='B' if ch>=0.05 else ('A' if ch>0 else ('C' if ch>-0.05 else 'D'))
    return ans, dict(change=ch)
@reg('SC2020S-99')
def _():
    pay16=19.28e8/1.093; per16=6.64e4-0.60e4; n=pay16/per16
    return nearest(n,{'A':26565,'B':27001,'C':29205,'D':35015})[0], dict(n16=n, trap_rate=19.28e8/1.093/(6.64e4/1.06))
@reg('SC2020S-100')
def _():
    vat16=2.30/1.116; tax16=1.09/(1-0.295); A = vat16 > 2*tax16
    B = None  # 2016 growth of 应付职工薪酬 not given
    C = True  # total +4.2%, 房地产 -3.1% -> others combined > 4.2%
    rev16=105.39/1.031; D = 1.09/105.39 > tax16/rev16
    t={'A':A,'B':False,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(vat16=vat16,tax16=tax16,ratioA=vat16/tax16, tax_per_rev17=1.09/105.39, tax_per_rev16=tax16/rev16)

# ---------------- SD2025 M3 原煤/煤炭进口 (图1增速, 图2进口量) ----------------
IMP={'2023-05':3958,'2023-06':3987,'2023-07':3926,'2023-08':4433,'2023-09':4214,'2023-10':3599,'2023-11':4351,'2023-12':4730,'2024-01~02':7452,'2024-03':4138,'2024-04':4525,'2024-05':4382}
IMPG={'2023-05':92.7,'2023-06':110.1,'2023-07':67.2,'2023-08':50.8,'2023-09':27.8,'2023-10':23.3,'2023-11':34.8,'2023-12':53.0,'2024-01~02':22.9,'2024-03':0.5,'2024-04':11.3,'2024-05':10.7}
OUTG={'2023-05':4.2,'2023-06':2.5,'2023-07':0.1,'2023-08':2.0,'2023-09':0.4,'2023-10':3.8,'2023-11':4.6,'2023-12':1.9,'2024-01~02':-4.2,'2024-03':-4.2,'2024-04':-2.9,'2024-05':-0.8}
@reg('SD2025-112')
def _():
    q1=IMP['2024-01~02']+IMP['2024-03']; q4=IMP['2023-10']+IMP['2023-11']+IMP['2023-12']
    A = (q1-q4)==1090; B = abs((q4-q1)/3-363)<1; C = abs((q1/q4-1)+0.106)<0.002; D = abs((q1/q4-1)-0.086)<0.002
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(q1=q1,q4=q4,diff=q1-q4,ring=q1/q4-1, trap_q1_only_3months=IMP['2024-03']*3)
@reg('SD2025-114')
def _():
    t15=18.6; m5=3.8; b15=t15/0.97; b5=m5/(1-0.008); t14=t15-m5; b14=b15-b5; g=t14/b14-1
    ans,d=nearest(-g*100,{'A':2.9,'B':3.9,'C':5.0,'D':11.3})
    # sensitivity to rounding of 18.6/3.8 (each +-0.05)
    gs=[ (a-b)/((a/0.97)-(b/0.992))-1 for a in (18.55,18.6,18.65) for b in (3.75,3.8,3.85)]
    return ans, dict(g14=g, range=(min(gs),max(gs)), dist=d)
@reg('SD2025-115')
def _():
    sep22=IMP['2023-09']/(1+IMPG['2023-09']/100); aug22=IMP['2023-08']/(1+IMPG['2023-08']/100); A = sep22<aug22
    q3=(IMP['2023-07']+IMP['2023-08']+IMP['2023-09'])/3; q4=(IMP['2023-10']+IMP['2023-11']+IMP['2023-12'])/3; B = q3>q4
    may23=3.8/(1-0.008); may22=may23/(1+0.042); C = may22>3.8
    avg14=(18.6-3.8)/4; D = abs((3.8-avg14)-0.1)<1e-9
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(sep22=sep22,aug22=aug22,q3=q3,q4=q4,may22=may22,avg14=avg14)

# ---------------- SD2025 M4 R&D ----------------
@reg('SD2025-116')
def _():
    v=109.0/0.03; return nearest(v,{'A':3456,'B':3523,'C':3633,'D':3758})[0], dict(v=v)
@reg('SD2025-117')
def _():
    b=89.5/1.214; a=163.8/1.372; e=1927.1/1.10; tot=2180.4/1.121
    sh=(b/tot*100,a/tot*100,e/tot*100)
    opts={'A':(4.10,7.50,88.40),'B':(6.00,9.00,85.00),'C':(3.80,6.10,90.10),'D':(2.00,5.00,93.00)}
    d={k:sum(abs(x-y) for x,y in zip(sh,v)) for k,v in opts.items()}
    return min(d,key=d.get), dict(shares=sh, sum_parts=b+a+e, tot21=tot, dist=d)
@reg('SD2025-119')
def _():
    r22=363.6/0.0386; r21=(363.6/1.337)/(0.0386-0.0047); g=r22/r21-1
    return nearest(g*100,{'A':10,'B':15,'C':20,'D':17})[0], dict(rev22=r22,rev21=r21,g=g, trap_plus=(363.6/1.337)/(0.0386+0.0047))
@reg('SD2025-120')
def _():
    A = abs((3.86-0.47)-4.33)<1e-9
    s3=(400.2+346.8+197.5)/2180.4; B = s3<0.40
    g22=2180.4/0.0249; g21=(2180.4/1.121)/(0.0249-0.0014); C = abs((g22-g21)-4500)<100
    D = 0.884<0.90
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(A_true_2021=3.86-0.47, share3=s3, gdp22=g22, gdp21=g21, inc=g22-g21, D_chk=1927.1/2180.4)
@reg('ZL2B-ADP-SD2025')
def _():
    rev=1728.7/0.0159; gdp=2180.4/0.0249; r=rev/gdp
    ans,d=nearest(r,{'A':0.8,'B':1.2,'C':1.6,'D':2.0})
    return ans, dict(rev=rev,gdp=gdp,ratio=r, trap_C=0.0249/0.0159, trap_A=gdp/rev)

# ---------------- GD2022Z M1 基层群众性自治组织 ----------------
CUN={2015:58.1,2016:55.9,2017:55.4,2018:54.2,2019:53.3,2020:50.2}; JU={2015:10.0,2016:10.3,2017:10.6,2018:10.8,2019:11.0,2020:11.3}
@reg('GD2022Z-87')
def _():
    s19=CUN[2019]/(CUN[2019]+JU[2019]); s20=0.8163; d=(s20-s19)*100
    ans,_=nearest(d,{'A':-1.26,'B':1.26,'C':-12.6,'D':12.6})
    return ans, dict(s19=s19, s20_chart=CUN[2020]/(CUN[2020]+JU[2020]), d=d, chk_total_chg=61.5/64.3-1)
@reg('GD2022Z-89')
def _():
    v=376.1/50.2; return nearest(v,{'A':3.5,'B':5.5,'C':7.5,'D':9.5})[0], dict(v=v, trap=(376.1+123.6)/61.5)
@reg('GD2022Z-90')
def _():
    A = abs(376.1/123.6-5)<0.2; B = 207.3/50.2>4; C = 0.65/1.1>0.6
    cun_down=all(CUN[y]<CUN[y-1] for y in range(2016,2021)); ju_up=all(JU[y]>JU[y-1] for y in range(2016,2021)); D = (cun_down and not ju_up) or (ju_up and not cun_down)==False and False
    D = False if cun_down and ju_up else None
    t={'A':A,'B':B,'C':C,'D':bool(D)}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(A=376.1/123.6, B=207.3/50.2, C=0.65/1.1, cun_down=cun_down, ju_up=ju_up)

# ---------------- GD2022Z M3 基层卫生 ----------------
@reg('GD2022Z-96')
def _():
    g=3.6/144.5; return nearest(g*100,{'A':1.4,'B':2.5,'C':3.6,'D':4.7})[0], dict(g=g, chk=148.1-144.5, trap_C=3.6/100*100, trap_curr=3.6/148.1)
@reg('GD2022Z-98')
def _():
    xz=139.0e4/3.00e4; jd=22.6e4/8773; r=xz/jd
    return nearest(r,{'A':0.5,'B':2,'C':3,'D':4})[0], dict(per_xiangzhen=xz, per_jiedao=jd, ratio=r, trap_per_institution=(139.0e4/35762)/(22.6e4/9826))
@reg('GD2022Z-99')
def _():
    s=52.0/148.1; return nearest(s*100,{'A':25,'B':30,'C':35,'D':40})[0], dict(s=s, trap_tech_base=52.0/126.7)
@reg('GD2022Z-100')
def _():
    A = 126.7>123.2 and 44.4>41.5
    r19=9561/8515; r20=9826/8773; B = abs(r20-r19)<0.01
    C = ((3909+3383)/2)/((339.5+292.7)/2) > 10
    rural19=137.0e4/1.48*1000; rural19b=144.5e4/1.56*1000; D = abs(rural19/1e8-8)<0.5
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if not v]; assert len(ans)==1   # 最不准确
    return ans[0], dict(r19=r19,r20=r20,C=((3909+3383)/2)/((339.5+292.7)/2), rural19=rural19, rural19b=rural19b)

# ---------------- GD2022X M3 民航 ----------------
@reg('GD2022X-96')
def _():
    t19=41777.82/(1-0.367); d19=40821.30/(1-0.303); s19=d19/t19; s20=40821.30/41777.82; ch=(s20-s19)*100
    return nearest(ch,{'A':-9,'B':-15,'C':9,'D':15})[0], dict(s19=s19,s20=s20,ch_pp=ch, chk_sum20=40821.30+956.51)
@reg('GD2022X-98')
def _():
    dom={2016:3055,2017:3615,2018:4096,2019:4568,2020:4686}; intl={2016:739,2017:803,2018:849,2019:953,2020:895}
    more={y:dom[y]/intl[y]-1 for y in dom}; n=sum(1 for y in dom if more[y]>4)
    return {1:'A',2:'B',3:'C',5:'D'}[n], dict(more=more, n=n, trap_shi=sum(1 for y in dom if dom[y]/intl[y]>4))
@reg('GD2022X-99')
def _():
    intl={2016:282.8,2017:324.6,2018:359.9,2019:401.5,2020:382.9}; g={y:intl[y]/intl[y-1]-1 for y in range(2017,2021)}
    m={2017:'A',2018:'B',2019:'C',2020:'D'}; best=max(g,key=g.get)
    rep={2016:339.1,2017:376.3,2018:412.5,2019:445.3,2020:431.8}; g2={y:rep[y]/rep[y-1]-1 for y in range(2017,2021)}
    return m[best], dict(g=g, trap_repeat=g2)
@reg('GD2022X-100')
def _():
    dur19=788.22/(1-0.205); tot19=876.22/(1-0.288); A = dur19/tot19>0.9
    lines={2019:(4568,111,953),2020:(4686,94,895)}
    p20=(40821.30,96.13,956.51); p19=(40821.30/(1-0.303),96.13/(1-0.913),956.51/(1-0.871))
    per20=[p20[i]/lines[2020][i] for i in range(3)]; per19=[p19[i]/lines[2019][i] for i in range(3)]
    B = all(per20[i]<per19[i] for i in range(3))
    C = (1357.7-919.3)/4 < 100
    D = 371.09/(1-0.253) < 400
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(A=dur19/tot19, per19=per19, per20=per20, C=(1357.7-919.3)/4, D=371.09/(1-0.253))
@reg('GD2022Z-90')
def _():
    A = abs(376.1/123.6-5)<0.2; B = 207.3/50.2>4; C = 0.65/1.1>0.6
    yrs=range(2016,2021)
    cun_down=all(CUN[y]<CUN[y-1] for y in yrs); ju_up=all(JU[y]>JU[y-1] for y in yrs)
    D = not (cun_down and ju_up)   # 一减一增 -> 趋势不一致
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(A=376.1/123.6, B=207.3/50.2, C=0.65/1.1, cun_down=cun_down, ju_up=ju_up)

# ---------------- GK2020D 第五则 B市新经济 ----------------
@reg('GK2020D-126')
def _():
    v=7311.4e4/70661  # 万元
    ans=[k for k,(lo,hi) in {'A':(1000,1100),'B':(1100,1e9),'C':(0,900),'D':(900,1000)}.items() if lo<=v<hi]; assert len(ans)==1
    return ans[0], dict(v=v)
@reg('GK2020D-127')
def _():
    gdps=[10057.4/0.332, 6976.8/0.230, 4893.4/0.161]; x=[4940.7/g*100 for g in gdps]
    return nearest(x[0],{'A':15.0,'B':13.7,'C':17.6,'D':16.3})[0], dict(gdps=gdps, x=x)
@reg('GK2020D-129')
def _():
    m=10629.4/0.181/12
    ans=[k for k,(lo,hi) in {'A':(5500,1e9),'B':(4500,5500),'C':(3500,4500),'D':(0,3500)}.items() if lo<=m<hi]; assert len(ans)==1
    return ans[0], dict(monthly=m, trap_tech_only=10629.4/12)
@reg('GK2020D-130')
def _():
    gdp=10057.4/0.332; A = gdp>35000
    s17=0.181-0.018; B = 5 < (1-s17)/s17 < 6
    C = 0.092>0.093
    D = 507.8*0.189/1.189 > 100
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(gdp=gdp, B=(1-s17)/s17, D=507.8*0.189/1.189)

# ---------------- GK2023D 第五则 H省电商 ----------------
@reg('GK2023D-126')
def _():
    v=21.8-2.3; return nearest(v,{'A':17.2,'B':19.5,'C':21.8,'D':24.1})[0], dict(v=v)
@reg('GK2023D-127')
def _():
    s21=2426.4/2948.2; s20=(2426.4/1.101)/(2948.2/1.125); d=(s21-s20)*100
    ans='A' if -3<d<0 else ('B' if d<=-3 else ('C' if d<3 else 'D'))
    return ans, dict(s21=s21,s20=s20,d=d)
@reg('GK2023D-129')
def _():
    v=(5354.93-4239.04)/(87-44); return nearest(v,{'A':5,'B':12,'C':26,'D':62})[0], dict(v=v, trap_all=5354.93/87, trap_Z=4239.04/44)
@reg('GK2023D-130')
def _():
    g=2018.3/(1475.5/1.157+542.8/1.16)-1; A = g>0.16
    B = 0.125>0.218
    s20=(4271.38/1.254)/(11526.13/1.218); C = s20>0.38
    D = 3.17/1.495>2
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(g_cross=g, s20=s20, fee20=3.17/1.495)

# ---------------- GK2025D 第四则 外贸 ----------------
@reg('GK2025D-127')
def _():
    exp=7741.7/0.179/1e4; imp=7.75-exp
    return nearest(imp,{'A':2.2,'B':2.8,'C':3.4,'D':4.0})[0], dict(exp=exp, imp=imp)
@reg('GK2025D-129')
def _():
    s23=7.75/9.89; s22=(7.75/1.029)/(9.89-0.45); d=(s23-s22)*100
    ans='C' if d<=-5 else ('D' if d<0 else ('B' if d<5 else 'A'))
    return ans, dict(s23=s23,s22=s22,d=d, chk_sum=7.75+1.84+0.29754)
@reg('GK2025D-130')
def _():
    # A: 2023年3月东部高技术产品出口额 -> only 3月增速 21%, no level -> no
    # B: 2022Q1 中西部一般贸易 = 1.84/1.126*(0.566-0.049) -> yes
    # C: 全国高技术产品出口额 -> only 东部 given -> no
    # D: 2022年东北汽车制造业出口额同比增量 -> only 2023Q1 增速 -> no
    v=1.84/1.126*(0.566-0.049)
    return 'B', dict(B_value_trillion=v)

# ---------------- HB2020 材料4 12358平台 ----------------
IND={'停车收费':10043,'商品零售':3118,'交通运输':2730,'社会服务':2686,'物业管理':2587,'医药':1790,'资源价格':1764,'房地产':1105,'住宿、餐饮':1060,'教育':927,'网络购物':694,
     '旅游':459,'邮政通信':421,'其他商品价格':206,'机关收费':172,'农产品及农资产品价格':157,'金融服务':105,'律师公证认证检测服务':82,'网络服务收费':28,'协会社团':3}
@reg('HB2020-127')
def _():
    zx=31325/(1-0.0734); jb=4192/(1-0.1906); d=zx-jb
    return nearest(d,{'A':26146,'B':27133,'C':28627,'D':29614})[0], dict(zx4=zx,jb4=jb,d=d, trap_may=31325-4192)
@reg('HB2020-128')
def _():
    less=(1105-421)/1105*100
    return nearest(less,{'A':41.9,'B':51.9,'C':61.9,'D':71.9})[0], dict(less=less, trap_ratio=421/1105*100)
@reg('HB2020-129')
def _():
    tot=sum(IND.values())+7439; assert tot==37576, tot
    top5=sorted(IND.values(),reverse=True)[:5]; s=sum(top5)/37576*100
    with_other=sorted(list(IND.values())+[7439],reverse=True)[:5]
    return nearest(s,{'A':61.4,'B':56.3,'C':51.8,'D':46.5})[0], dict(top5=top5,s=s, trap_with_other=sum(with_other)/37576*100)
@reg('HB2020-130')
def _():
    A=None  # 2018年5月 components unknown (only total 同比)
    B = 0.0734 > max(0.1906,0.1592)
    C = 927 <= 2*459
    D = (5786+3528+2499)/37576 < 0.35
    t={'A':False,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(C=927/459, D=(5786+3528+2499)/37576)

# ---------------- GD2026 M1 改编三题 ----------------
@reg('ZL2B-ADP-GD2026-1')
def _():
    tot=10/0.1921
    opts={'A':40,'B':52,'C':68,'D':100}
    traps=dict(tot_2020share=10/0.1472, quarter_x4=10*4, liucuo=100)
    return nearest(tot,opts)[0], dict(tot=tot, **traps)
@reg('ZL2B-ADP-GD2026-2')
def _():
    pp=19.21-14.72
    A=False  # 4.49 是占比的百分点差，不是人数增速；2020年人数未知
    B=abs(pp-4.49)<1e-9
    C=False  # 四分之一是“其中”——占制造业吸纳的约10万人，不是占全部留粤就业省内毕业生
    D=False  # 2020年总人数未给，不能用10*14.72/19.21
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(pp=pp, rel=19.21/14.72-1, D_naive=10*14.72/19.21)
@reg('ZL2B-ADP-GD2026-3')
def _():
    assert abs(8.6+25.6+28.3-62.5)<1e-9
    A=False  # 20万以上“超6.5万”、50万以上“超5000”均为下限，差值不能确定
    B=(8.6+25.6)/62.5>0.5
    C=62.5/2.1>30
    D=abs((1-26/62.5)-0.4)<0.05
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(B=(8.6+25.6)/62.5, C=62.5/2.1, D=1-26/62.5)

# ======== FINAL option orders for adapted questions (override earlier drafts) ========
@reg('ZL2B-ADP-HB2023')
def _():
    end_huaxi = S['华西'][0] + timedelta(days=S['华西'][2])
    A = end_huaxi.month == 11 and (end_huaxi - timedelta(days=1)).month == 11   # robust to +-1 day counting
    B = False   # 原文“为1961年以来第二长”
    C = False   # 江南“出梅偏晚3天”
    n_dongbei = S['东北'][0] + timedelta(days=17); n_xinan = S['西南'][0] - timedelta(days=9)
    D = n_dongbei < n_xinan
    # sanity: the material's own convention length = end - start
    assert (S['华南'][1]-S['华南'][0]).days == 67
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1, t
    return ans[0], dict(huaxi_end=str(end_huaxi), normal_dongbei=str(n_dongbei), normal_xinan=str(n_xinan))
@reg('ZL2B-ADP-GD2026-1')
def _():
    tot=10/0.1921
    opts={'A':52,'B':68,'C':100,'D':120}
    ans,d=nearest(tot,opts)
    assert abs(tot-52)<1 and abs(10/0.1472-68)<1
    return ans, dict(tot=tot, trap_B=10/0.1472, trap_C='留粤来粤就业创业超100万', trap_D='募集120多万岗位')
@reg('ZL2B-ADP-GD2026-2')
def _():
    pp=round(19.21-14.72,2)
    t={'A':False,   # 人数增速无法判断（2020年人数未知；4.49是百分点）
       'B':False,   # “其中”指制造业吸纳的约10万人
       'C':False,   # 2020年总数未知
       'D':pp==4.49}
    ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(pp=pp, C_naive=10*14.72/19.21, B_true_share=2.5/(10/0.1921))
@reg('ZL2B-ADP-GD2026-3')
def _():
    assert abs(8.6+25.6+28.3-62.5)<1e-9
    A=(8.6+25.6)/62.5>0.5
    B=62.5/2.1>30
    C=False  # 下限数据之差不确定（不能判断属实）
    D=abs((1-26/62.5)-0.4)<0.05
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1
    return ans[0], dict(A=(8.6+25.6)/62.5, B=62.5/2.1, D=1-26/62.5)
@reg('ZL2B-ADP-SD2025')
def _():
    rev=1728.7/0.0159; gdp=2180.4/0.0249; r=rev/gdp
    ans,d=nearest(r,{'A':0.6,'B':0.8,'C':1.2,'D':1.6})
    return ans, dict(ratio=r, trap_D=0.0249/0.0159, trap_B=gdp/rev, trap_A=0.0159/0.0249)

@reg('ZL2B-ADP-GK2025D')
def _():
    A = False   # 9.8%为一季度增速，3月为21%
    B = 1.08/1.84 > 0.6
    C = False   # 9.4%为东北进出口增速，出口增速未给，不能判断准确
    D = all(7400.9/x > 0.4 for x in (18350,18400,18450))
    t={'A':A,'B':B,'C':C,'D':D}; ans=[k for k,v in t.items() if v]; assert len(ans)==1, t
    return ans[0], dict(B=1.08/1.84, D=7400.9/18400)

if __name__=='__main__':
    import json
    out={}
    for k,f in R.items():
        a,d=f(); out[k]=dict(ans=a, detail={kk:(round(v,4) if isinstance(v,float) else v) for kk,v in d.items()} if isinstance(d,dict) else d)
        print(k, a, out[k]['detail'])
    json.dump(out, open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2b/verify_out.json','w'), ensure_ascii=False, indent=1, default=str)
