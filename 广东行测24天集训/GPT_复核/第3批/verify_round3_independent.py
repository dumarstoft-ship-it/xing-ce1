"""独立复核：Claude第3批43道改编及若干风险点。
原始数值由审阅者从冻结快照的题干、材料正文/转录抄录，未调用Claude核验程序。
只验证已编码的数值、条件和图关系；不证明图片转录、全部自然语言语义正确。
Python 3.10+，标准库。运行会在同目录写入 independent_results.json。
"""
from fractions import Fraction as F
from itertools import product
from math import sqrt
from pathlib import Path
import json, statistics
SNAPSHOT='a73eac50d0db6d165297d69e05103d916ffe9a83'
R={}; issues={}
def f(x): return F(str(x))
def record(n,key,expected,value,why):
    q=f'D08-ZL-{n:03d}' if isinstance(n,int) else n
    assert key==expected,(q,key,expected,value)
    R[q]={'answer':key,'matches_submitted_key':True,'value':value,'reason':why}
def nearest(n,value,options,expected,why):
    ds=[abs(float(value)-float(v)) for v in options]
    m=min(ds); inds=[i for i,d in enumerate(ds) if abs(d-m)<1e-10]
    assert len(inds)==1,(n,ds)
    record(n,'ABCD'[inds[0]],expected,float(value),why)
def unique(n,truths,expected,why,detail=None):
    assert sum(bool(x) for x in truths)==1,(n,truths)
    record(n,'ABCD'[truths.index(True)],expected,detail if detail is not None else truths,why)
# 001,003: HB2022 公共充电桩原图转录，万台；广东为台。
charge=list(map(f,[5.7,15,21.4,30,51.6,80.7,114.7])); rates=[b/a-1 for a,b in zip(charge,charge[1:])]
s0=f(181846)/1147000; g=rates[-1]-f(.10); ds=100*(s0*f(1.4)/(1+g)-s0)
unique(1,[0<ds<1,ds>1,-1<ds<0,ds<-1],'A','回落10个百分点后，按两期比重差比较',float(ds))
inc=[b-a for a,b in zip(charge,charge[1:])]
years=[2016+i for i in range(1,6) if inc[i]>inc[i-1] and rates[i]<rates[i-1]]
nearest(3,len(years),[1,2,3,4],'C',f'同时满足的年份={years}')
nearest(7,(f(2890.40)/f(7.36))/(f(1187.80)/f(8.36))-1,[1.4,1.8,2.8,.6],'B','人均基金支出的增长倍数，不是现期倍数')
vals8={'人数降幅':1-f(7.36)/f(8.02),'人次增速':f(19.42)/f(17.45)-1,'基金增速':f(2908)/2408-1,'比重降幅':f(2637)/2853-f(2566)/2852,'筹资四年倍数':f(410.89)/f(156.60)}
unique(8,[vals8['人数降幅']<f(.05),vals8['人次增速']>vals8['基金增速'],vals8['比重降幅']>f(.02),vals8['筹资四年倍数']>f(1.3)**4],'C','分别检查降幅、混合指标、百分点、年均增长', {k:float(v) for k,v in vals8.items()})
ds=100*(f(46503)/332316-(f(46503)/f(1.109))/300931)
unique(9,[0<ds<f(.1),ds>f(.1),-f(.1)<ds<0,ds<-f(.1)],'A','乡村与全部社零两期比重',float(ds))
v10=(f(51556)-41944)/(f(51556)/f(1.262)-f(41944)/f(1.256))-1
nearest(10,100*v10,[25.6,26.8,29,33],'C','逐年分别扣除商品部分，不能直接相减增速')
issues['D08-ZL-010']={'type':'错误排除理由','fact':'26.8%>26.2%，仅凭其余部分增速高于26.2%，不能排除B。计算后的C仍正确。'}
nearest(13,100*(f(1.063)*3112/3117-1),[5.1,6.1,6.3,6.5],'B','面积增长因子除以馆数增长因子')
nearest(15,100*((f(4.67)/f(5.30))/(f(3.32)/f(4.34))-1),[15,19,41,-15],'A','每人次外借册次的隔期增速')
nearest(25,100*(f(22.9)/59-f(16)/f(122.5)),[13,21,26,39],'C','合计增速以合计基期为分母，再与咨询增速相减')
freight0=list(map(f,[1.4,1.5,1.6,1.7])); freight1=list(map(f,[1.6,1.7,1.9,1.9]))
turn0=list(map(f,[288,322.6,342.4,397.9]));turn1=list(map(f,[312.9,338.8,367.9,442.5]))
nearest(27,100*((sum(turn1)/sum(freight1))/(sum(turn0)/sum(freight0))-1),[-5.5,-6.3,5.5,6.3],'A','全年周转量与货运量分别合计，再比较平均运距')
travel0=[342,370,442,442];travel1=[335,387,443,440]
t0=list(map(f,[1.9,2,2.3,2.3]));t1=list(map(f,[1.9,2.1,2.3,2.3]))
up=[i+1 for i in range(4) if t1[i]*travel0[i]>t0[i]*travel1[i]]
nearest(28,len(up),[1,2,3,4],'C',f'按卷面精确数值比较，季度={up}；不据此声称真实未舍入值也同方向')
fiscal=[103874,117254,129210,140370,152269,159605,172593,183360]
taxes=[89738,100614,110531,119175,124922,130361,144370,156403]
years=[2011+i for i in range(1,8) if taxes[i]*fiscal[i-1]>taxes[i-1]*fiscal[i]]
nearest(33,len(years),[1,2,3,4],'B',f'直接交叉相乘比较税收比重，年份={years}')
nearest(38,f(37020)*f(1.121)-f(28304)**2/22386,[5100,5700,6300,7200],'B','全省增速回落，西翼维持原增速，两者分别外推')
ds=100*(f(4538)/37864-(f(4538)/f(1.231))/(f(37864)/f(1.191)))
nearest(41,ds,[.4,4,-.4,-4],'A','汽车收入占全省工业主营收入比重的百分点差')
unique(42,[x>26.4 for x in [19.9,18.8,23.8,38.1]],'D','利润比重应对照全省利润增速，不对照收入增速')
v=[12048,131,7668];g=list(map(f,[.004,.027,.028]))
nearest(50,100*(f(sum(v))/sum(f(a)/(1+b) for a,b in zip(v,g))-1),[.4,1.3,2,2.8],'B','三个运输类型的基期分别回推再合计')
nearest(52,sum(x>26.9 for x in [-1.5,18,32.2,4.1,-3.9]),[1,2,3,4],'A','比重上升与总体周转量增速比较')
clean=[4146,4321,4903,5943,7177];total=[22800,24300,28800,32400,33900]
ys=[2008+i for i in range(1,5) if clean[i]*total[i-1]>clean[i-1]*total[i]]
nearest(54,len(ys),[1,2,3,4],'B',f'清洁能源增速超过全部的年份={ys}')
nearest(56,100*(f(5518)/7177-f(4373)/5943),[3.3,5.4,-3.3,-5.4],'A','水电占清洁能源上网电量的百分点差')
nearest(58,100*f(384-242)/((44260-384)-(34343-242)),[.7,.9,1.5,2.4],'C','乡镇文化站之外的机构，增量与基期都扣除对应部分')
avgr=[(1+f(a))/(1+f(b))-1 for a,b in zip([.032,-.018,.205,.205],[.204,.076,.135,.009])]
record(59,'ABCD'[avgr.index(max(avgr))],'D',[float(x) for x in avgr],'平均每次参加人数的增速比较')
trade=list(map(f,[10.03,8.57,14.58,9.54,6.22,18.26]));gr=list(map(f,[.22,-.159,.387,.575,-.496,.242]))
nearest(62,100*(sum(trade)/sum(a/(1+b) for a,b in zip(trade,gr))-1),[-8,8,13,21],'B','半年累计同比：逐月回推基期，再合计')
u0=[6796,5712,5918,6138];u1=[7427,6222,6520,6786];r0=[2560,1744,2475,3009];r1=[2871,1947,2810,3356]
nearest(68,100*(f(sum(u1))/sum(u0)-f(sum(r1))/sum(r0)),[-2.5,-1,2.5,1],'A','四季度合成年总量，再相减两类增速')
nearest(71,100*(f(30193-4124)/(f(30193)/f(.944)-f(4124)/f(.804))-1),[-3,-5.6,-9,3],'A','两期均用累计扣当月，基期分别还原')
p=[f(x) for x in [45,43.8,44.9,46.8,48.1]];allp=list(map(f,[32.3,32.9,34.7,35.4,36.7]))
ys=[2018+i for i in range(1,5) if p[i]/p[i-1]>allp[i]/allp[i-1]]
nearest(81,len(ys),[1,2,3,4],'A',f'产业化率自身增长率比较，年份={ys}')
size0=list(map(f,[45.9,46.8,46.1,32.4]));size1=list(map(f,[50.9,55.4,45.3,22.0]));z=[b/a-1 for a,b in zip(size0,size1)]
record(84,'ABCD'[z.index(max(z))],'B',[float(x) for x in z],'四类企业2022/2020的隔期增速')
nearest(91,100*(f(2707-125)/(2774-195)-1),[-2.4,.1,1.7,4.1],'B','总产业收入扣除制造业后比较')
old=f(2690)-f(195)/f(1.258)-(f(49)/f(.79))/f(1.348);new=f(2774)-195-f(49)/f(.79)
nearest(92,100*(new/old-1),[1.1,3.1,5.3,7.2],'A','制造、发射分别链式回推；在两年同口径扣除')
v2016=[[56.15,4.73,20.52,33.9],[75.8,3.75,28.97,41.58]];v2017=[[78.61,6.45,41.48,47.76],[109.24,3.68,49.29,21.7]]
s16=sum(f(row[2]) for row in v2016)/sum(f(v) for row in v2016 for v in row);s17=sum(f(row[2]) for row in v2017)/sum(f(v) for row in v2017 for v in row)
nearest(96,100*(s17-s16),[6.7,7.5,-6.7,83],'A','上半年各两季合计；83为分子增速不是比重百分点差')
gdp=f(29319.97)/f(.514);nationmax=gdp*10/10000
unique(101,[False,False,nationmax<=58,f(13.3)/f(9.8)>=f(1.5)],'C','首破年份、增长倍数、全国GDP上界及增速比',float(nationmax))
taxother=f(6467.82)/f(.491)-f(6467.82)
nearest(102,100*taxother/gdp,[11.3,11.8,23.1,24.2],'B','税收扣民营，与GDP（非税收）比较')
y=2012
while 5524+(y-2012)*(5524-5049)<=7000:y+=1
nearest(103,y,[2014,2015,2016,2017],'C','保持增量，严格首次超过7000')
water=[n for n in range(392) if f(66.95)<=100*F(n,391)<f(67.05)];road=[n for n in range(392) if f(59.75)<=100*F(n,391)<f(59.85)]
assert water==[262] and road==[234]
nearest(107,water[0]+road[0]-391,[28,105,234,262],'B','按百分率四舍五入还原唯一整数；交集下界可由并集覆盖391村达到')
share=f(2107.7)/2349;diff=100*share*(1-f(1.069)/f(1.089))
nearest(110,diff,[1.6,1.9,2,-1.6],'A','前十企业与汽车整体的两期比重差')
nearest(112,100*(f(277)/f(.826))/(f(757)/f(1.041)),[28,36.6,40.5,46.1],'D','中国品牌内部比重；不能用全部轿车占有率')
carold=f(1238)/f(1.031);pvold=f(1970)/f(1.0989);gcombined=f(1238+408)/(carold+f(408)/f(1.364))-1
unique(113,[f(.911)>f(.935),f(.628)+f(.042)<f(.60),gcombined>f(.15),pvold-carold<600],'D','逐项比重、基期与合计增长；不使用矛盾MPV数据',{'合计增速':float(gcombined),'非轿车基期':float(pvold-carold)})
unique(121,[False,f(336.7)/f(.75)>f(336.7)/f(1.3052),False,f(1.3052)>f(1.3074)],'B','同环比基期分别推；A扩大范围、C换时间基准；文字判断人工检查')
unique(128,[False,f(4997.3)/f(.92)-f(4997.3)>400,False,f(.93)>f(.94)],'B','累计非当月、成本非销售费用、下降时的比重方向')
addlocal=f(322462.3)*f(.137)/f(1.137);addtotal=f(685766.3)*f(.119)/f(1.119);s=addlocal/addtotal
unique(130,[s<f(.45),f(.45)<=s<f(.50),f(.50)<=s<f(.55),s>=f(.55)],'C','地方负债增量/全部负债增量，不能用存量',float(s))
avg=(28*878-18*711)/10
nearest(133,avg,[795,1179,1250,1320],'B','28年总增量扣18年总增量，剩10年')
p2000=f(11.4)+(28*878-18*711)/f(10000);p2010=p2000+f(10*711)/10000
nearest(134,(f(.089)*p2010)/(f(.036)*p2000)-1,[1.5,1.6,2.5,2.6],'B','按题干约定将年均增量用于人口推算；增长倍数须减1')
# 科推125：令r=Rt，RL=灯阻，R0正。D=R0*RL+r*(R0+RL)。
# It=U*RL/D，VL=U*RL*r/D，I=U*(RL+r)/D。
# r下降时It增、VL减、I增（dI/dr=-U*RL**2/D**2），故R0电压与总功率增。
for U,R0,RL,rsmall,ratio in product([1,3,12],[1,4,10],[1,5,20],[1,2,8],[2,3,5]):
    def circuit(r):
        d=R0*RL+r*(R0+RL)
        return (F(U*RL,d),F(U*RL*r,d),F(U*(RL+r),d))
    a=circuit(rsmall*ratio);b=circuit(rsmall)
    assert b[0]>a[0] and b[1]<a[1] and b[2]>a[2]
record('D09-PD-125','B','B',{'parameter_cases':3**5,'symbolic_signs':'It增，VL减，I增'},'先给有理式一般证明，网格仅补充检查；串反并同口诀不代替推导')
edges=[('草','螺'),('草','鲫'),('螺','鲫'),('藻','浮'),('藻','虾'),('浮','虾'),('浮','小鱼'),('虾','小鱼'),('虾','鳜'),('小鱼','鳜'),('小鱼','鹭'),('鲫','鳜'),('鲫','鹭')]
adj={}
for a,b in edges:adj.setdefault(a,[]).append(b)
paths=[]
def visit(p):
    if p[-1] not in adj:paths.append(p);return
    for v in adj[p[-1]]:
        assert v not in p
        visit(p+[v])
for root in ['草','藻']:visit([root])
levels=sorted({p.index('小鱼')+1 for p in paths if '小鱼' in p})
assert len(paths)==12 and levels==[3,4]
record('D09-PD-135','A','A',{'paths':paths,'小鱼营养级':levels},'枚举指定图的生产者到终消费者路径；不外推题外生态事实')
# 额外重点：资料127。“正相关”不等于“任意两点都同向”。
x=[86,36,9,8,4,3];y=[58.5,18.9,10.2,5.0,2.2,4.1]
xbar=sum(x)/6;ybar=sum(y)/6
cov=sum((a-xbar)*(b-ybar) for a,b in zip(x,y))
r=cov/sqrt(sum((a-xbar)**2 for a in x)*sum((b-ybar)**2 for b in y))
# 若7类平均时间可加总，则购买商品/服务为162-sum(x)=16；其参与率记z∈[0,100]。
missing=162-sum(x)
intercept=sum(a*f(b) for a,b in zip(x,y))-F(162,7)*sum(map(f,y))
slope=F(missing)-F(162,7)
minimum=min(intercept,intercept+100*slope)
assert cov>0 and minimum>0
weight=F(264-199,290-199);rest=(F(162)-weight*154)/(1-weight)
issues['D08-ZL-127']={'type':'实质歧义/解释错误','A按给定数值推算的分钟':float(rest),'六个完整类别的Pearson_r':r,'购买活动分钟_需类别可加总假设':missing,'七类未标准化协方差分子最小值_参与率0至100':float(minimum),'action':'不能用4分钟/2.2%与3分钟/4.1%的反向对否定正相关。保留原键于来源，正式计分题需明确单调措辞或隔离；不直接改原题标答。'}
assert len(R)==43,len(R)
OUT={'source_snapshot':SNAPSHOT,'scope':'41道资料改编＋2道科推改编。依据题干、材料正文及转录；未逐图重核PDF。','verified_count':len(R),'all_encoded_keys_match':all(x['matches_submitted_key'] for x in R.values()),'results':R,'issues':issues}
Path(__file__).with_name('independent_results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'verified':len(R),'all_keys_match':True,'issues':issues},ensure_ascii=False,indent=2))
