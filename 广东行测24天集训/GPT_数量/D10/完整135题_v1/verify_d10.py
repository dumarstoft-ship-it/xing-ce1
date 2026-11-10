"""D10 数量135题的数值/结构核验，Python 3.10+，仅标准库。
运行：python verify_d10.py
固定表达式只编码本题本的计算模型，不读取或执行用户输入。
程序能核算模型和检查书面答案同步，不能代替自然语言歧义、难度及题源审查。
"""
from fractions import Fraction
F = Fraction
from math import ceil, floor, factorial
from itertools import product, permutations
from functools import lru_cache, reduce
from operator import mul
from pathlib import Path
import json, re

@lru_cache(None)
def max_exchange(e,c):
    choices=[0]
    if e>=4: choices.append(1+max_exchange(e-3,c+1))
    if c>=6: choices.append(1+max_exchange(e+1,c-5))
    return max(choices)

def chain_coupon_cost(order):
    coupon=0;total=0
    for price in order:
        net=price-coupon
        total+=net+(20 if net<300 else 0)
        coupon=60 if net>=300 else 0
    return total

def checkout21():
    vals=[260,240,180]
    splits=[(sum(vals),)]+[(sum(vals[i] for i in range(3) if mask>>i&1),sum(vals[i] for i in range(3) if not(mask>>i&1))) for mask in range(1,7)]
    costs=[]
    for orders in splits:
        for coupons in product(range(3), repeat=len(orders)):
            if coupons.count(1)>1 or coupons.count(2)>1: continue
            total=0
            for x,c in zip(orders,coupons):
                if (c==1 and x<400) or (c==2 and x<200): break
                net=x-({0:0,1:80,2:30}[c])
                total+=net+(10 if net<300 else 0)
            else: costs.append(total)
    return min(costs)

def grow(seed,n,f):
    x=list(seed)
    while len(x)<n:x.append(f(x))
    return x

def cumulative(start,increments):
    x=[start]
    for d in increments:x.append(x[-1]+d)
    return x

def fib(a,b,n):return grow([a,b],n,lambda s:s[-1]+s[-2])

def weave(a,b):
    out=[]
    for i in range(max(len(a),len(b))):
        if i<len(a):out.append(a[i])
        if i<len(b):out.append(b[i])
    return out

def digit_product(n):return reduce(mul,map(int,str(abs(n))),1)

def canon_math(x):
 chinese={'七五折':F(15,2),'八折':F(8),'八五折':F(17,2),'九折':F(9),'相同':F(0)}
 if x in chinese:return chinese[x]
 if x.startswith('少'):return F(x[1:].removesuffix('元'))
 if x.startswith('多'):return -F(x[1:].removesuffix('元'))
 if x.endswith('%'):return F(x[:-1])/100
 return F(x)

MATH = [
    ('D10-M001', '2100', 'C', ['2000', '2050', '2100', '2200'], 'F(1520)/F("0.76")+100'),
    ('D10-M002', '8', 'B', ['七五折', '八折', '八五折', '九折'], '(F(8400)*F("1.2")-120*60)/60/60*10'),
    ('D10-M003', '3260', 'A', ['3260', '3310', '3350', '3800'], '9800-F("0.05")*9800-50-6000'),
    ('D10-M004', '6/25', 'B', ['20%', '24%', '25%', '29.2%'], 'F(30*3*50+120*40-7500,7500)'),
    ('D10-M005', '150', 'D', ['120', '130', '140', '150'], 'next(x for x in range(171) if 16*x-F("4.8")*(170-x)==F(".16")*(80*x+120*(170-x)))'),
    ('D10-M006', '85', 'B', ['84', '85', '89', '90'], 'min(x for x in range(101) if F("47.5")*x-3000>=1000)'),
    ('D10-M007', '28', 'B', ['27', '28', '30', '32'], 'min(x for x in range(121) if (120-x)%2==0 and 8400+30*x>=F(7680)*F("1.2"))'),
    ('D10-M008', '60', 'C', ['54', '56.25', '60', '62.5'], 'F(4800+600,24*4-6)'),
    ('D10-M009', '100', 'C', ['80', '90', '100', '120'], 'F(1540+660,22)'),
    ('D10-M010', '100', 'C', ['75', '90', '100', '120'], 'F(880+400,294-230)*5'),
    ('D10-M011', '53000', 'C', ['51000', '52000', '53000', '54000'], '50000+F(160-100,F(".04")-F(".02"))'),
    ('D10-M012', '800', 'B', ['700', '800', '1000', '1200'], '2000*F(".25")+3500-1000+3500*F(".8")*F(2,7)*F(".75")-3500*F(".8")'),
    ('D10-M013', '300', 'C', ['240', '270', '300', '330'], 'F(77-19,F(".29"))*F("1.5")'),
    ('D10-M014', '104', 'C', ['96', '100', '104', '120'], '(F(200)*F(".8")-30+20-(F(200)*F(".8")-30)*F(".05")-F("13.5"))/F("1.25")'),
    ('D10-M015', '88', 'C', ['86', '87', '88', '90'], 'ceil(F(7590,F("86.5")))'),
    ('D10-M016', '100', 'A', ['100', '125', '150', '200'], 'F(640,F("6.4"))'),
    ('D10-M017', '56', 'C', ['52', '54', '56', '58'], 'max(60-2*k for k in range(11) if (30-2*k)*(100+10*k)-120==max((30-2*j)*(100+10*j)-120 for j in range(11)))'),
    ('D10-M018', '617', 'C', ['600', '616', '617', '625'], 'min(p for p in range(1,1001) if min(F(".08")*p,30)+15<F(".06")*p+8)'),
    ('D10-M019', '460', 'B', ['450', '460', '540', '550'], 'next(90*n-(80 if 90*n>=500 else 0) for n in range(2,11) if (90*n-(80 if 90*n>=500 else 0))-(90*(n-1)-(80 if 90*(n-1)>=500 else 0))==10)'),
    ('D10-M020', '20', 'A', ['20', '21', '23', '25'], 'max(k for k in range(101) if k%5==0 and 3000-F(k,5)*340>=1600)'),
    ('D10-M021', '580', 'C', ['560', '570', '580', '600'], 'checkout21()'),
    ('D10-M022', '2480', 'C', ['2400', '2440', '2480', '2560'], 'min((5*min(x,100)+8*max(0,min(x-100,100))+12*max(0,x-200)+100)+(5*min(350-x,100)+8*max(0,min(250-x,100))+12*max(0,150-x)+100) for x in range(220,271))'),
    ('D10-M023', '8', 'C', ['4', '6', '8', '12'], '(12+20)-(12+4*3)'),
    ('D10-M024', '90', 'C', ['60', '78', '90', '102'], '3*60+(150+90)*F(".8")-(3*90+20*F(".6"))'),
    ('D10-M025', '603', 'B', ['576', '603', '608', '638'], 'min([9*n+(0 if 9*n>=600 else 80) for n in range(64,81)]+[F("9.5")*n+30 for n in range(64,81)])'),
    ('D10-M026', '8', 'C', ['6', '7', '8', '9'], 'max(n for n in range(1,31) if ((80*min(n,3)+60*max(0,n-3)) if n<=7 else 50*n)+230<=650)'),
    ('D10-M027', '34', 'C', ['30', '32', '34', '36'], 'next(59-x for x in range(19,41) if (6*min(x,20)+8*min(max(x-20,0),10)+10*max(x-30,0)+50)==(6*min(59-x,20)+8*min(max(39-x,0),10)+10*max(29-x,0)-30))'),
    ('D10-M028', '1200', 'C', ['0', '800', '1200', '2000'], 'F(".4")*(F(4000+24000,F(".4"))*F(".9"))-24000'),
    ('D10-M029', '1887', 'B', ['1860', '1887', '1896', '2220'], 'min(min(60*n+36 for n in range(1,51) if n+n//5>=37),37*60*F(".85"))'),
    ('D10-M030', '750', 'C', ['650', '700', '750', '850'], 'next(p for p in range(600,900) if abs((p-50*(p//300))-F(".9")*p)==25)'),
    ('D10-M031', '32', 'B', ['24', '32', '48', '80'], '1000-200+(12*80+12*320)*F(".1")-(24*30+12*(320-100)*F(".2"))'),
    ('D10-M032', '200', 'C', ['100', '150', '200', '250'], 'F("1.5")/F(".0075")'),
    ('D10-M033', '2490', 'B', ['2400', '2490', '2580', '2660'], 'min(600*a+430*b for a in range(4) for b in range(6) if a+b<=5 and 45*a+30*b>=170)'),
    ('D10-M034', '90', 'B', ['88', '90', '92', '94'], 'min(16*a+10*b for a in range(1,8) for b in range(1,8) if a+b<=8 and 20*a+12*b>=110)'),
    ('D10-M035', '6330', 'B', ['6300', '6330', '6370', '6740'], 'min(410*a+100+860*b for a in range(8,13) for b in range(9) if 10*a+20*b>=150)'),
    ('D10-M036', '60', 'B', ['50', '60', '70', '80'], 'F(350-320,F(".5"))'),
    ('D10-M037', '30', 'B', ['20', '30', '50', '80'], '(350+350)-(ceil(F(90+20+75,30))*100+50-80)'),
    ('D10-M038', '900', 'B', ['880', '900', '930', '940'], 'min(80*a+50*b for a in range(13) for b in range(1,22) if 9*a+5*b>=100)'),
    ('D10-M039', '2000', 'C', ['1000', '1500', '2000', '3000'], 'F(2,3)*F(9000,F(".1"))*F(".1")-(2000+(F(2,3)*90000-50000)*F(".2"))'),
    ('D10-M040', '560', 'C', ['530', '550', '560', '590'], '620-30*max(sum(t>=40 for t in (a,b,c,100-a-b-c)) for a in range(10,71) for b in range(10,81-a) for c in range(10,91-a-b) if 100-a-b-c>=10)'),
    ('D10-M041', '13/5', 'C', ['2.1', '2.5', '2.6', '3.0'], 'F(50)*F(".01")/10*50/20*20+10*F(".01")'),
    ('D10-M042', '40', 'C', ['20', '30', '40', '50'], 'next(x for x in range(201) if 40*(F(200-x,200))**2==F("25.6"))'),
    ('D10-M043', '50', 'B', ['40', '50', '60', '80'], 'F(36-28,F(".30")-F(".14"))'),
    ('D10-M044', '100', 'B', ['80', '100', '120', '150'], 'next(x for x in range(1,301) if F(24)+F(24*x,200+x)==32)'),
    ('D10-M045', '150', 'C', ['100', '120', '150', '180'], 'F(".16")/(F(".2")*(F(1,500)+F(1,300)))'),
    ('D10-M046', '11/40', 'C', ['25%', '26.4%', '27.5%', '30%'], '((F(".54")*3-F("1.12"))/5 + (F("1.12")*2-F(".54"))/5)/2/F(".8")'),
    ('D10-M047', '11/50', 'C', ['18.75%', '20%', '22%', '25%'], '(F(200)*F(".15")*(1-F(32,160))+20)/(128+52+20)'),
    ('D10-M048', '3/2', 'B', ['1', '1.5', '2', '2.5'], '30*F(80,100)-30*F(60,80)'),
    ('D10-M049', '50', 'C', ['0', '25', '50', '100'], 'min(500-(F(60)-F(".05")*b)/F(".2")-b for b in range(201))'),
    ('D10-M050', '160', 'C', ['120', '140', '160', '180'], 'F(2*360-240,3)'),
    ('D10-M051', '15', 'C', ['10', '12', '15', '20'], '(24*(1-F(25,100)))/F(".2")-75'),
    ('D10-M052', '100', 'D', ['60', '75', '90', '100'], 'next(x for x in range(150) if F(15,150-x)/F(40,200-x)==F(3,4))'),
    ('D10-M053', '7/8', 'C', ['75%', '80%', '87.5%', '90%'], 'F(40-10+5,40)'),
    ('D10-M054', '250', 'C', ['150', '200', '250', '300'], 'F(500*(F(".22")-F(".18")),F(".30")-F(".22"))'),
    ('D10-M055', '25', 'B', ['20', '25', '30', '35'], 'next(5*n for n in range(101) if F(1,5)<=F(12+5*n,150+5*n)<=F(23,100))'),
    ('D10-M056', '4', 'B', ['3', '4', '5', '6'], 'min(n for n in range(20) if F(".2")-F(".12")*F(".9")**n>=F(".12"))'),
    ('D10-M057', '150', 'C', ['100', '120', '150', '200'], 'F(600*(F(".12")-F(".10")),F(600*F(".1")-400*F(".06"),200)-F(".1"))'),
    ('D10-M058', '40/49', 'B', ['4/5', '40/49', '41/50', '5/6'], 'F(250*F(".7")+250*F(".9"),500-(250*F(".3")+250*F(".1"))*F(".1"))'),
    ('D10-M059', '115', 'C', ['100', '110', '115', '120'], '75+F(80,2)'),
    ('D10-M060', '42', 'C', ['36', '40', '42', '48'], '60*(1-F(50)*F(".12")/(80-500*F(".12")))'),
    ('D10-M061', '76', 'C', ['70', '75', '76', '80'], 'ceil((200*12+200*2+(200*F(".2")*F(".9")/F(".75"))*5)*F("1.2")/(200*F(".2")*F(".9")/F(".75")))'),
    ('D10-M062', '420', 'C', ['360', '400', '420', '480'], '60*30-(60*F(".5")/F(".15"))*6-60*3'),
    ('D10-M063', '690', 'C', ['600', '660', '690', '720'], '(200*F(".25")+100*F(".4"))*F(".95")/F(".9")/5*120-1400-(200*F(".25")+100*F(".4"))*F(".95")/F(".9")*2'),
    ('D10-M064', '1120', 'B', ['960', '1120', '1200', '1280'], '(160+40*F(".75")*F(".8"))*40-200*30-40*F(".75")*8'),
    ('D10-M065', '43/200', 'B', ['20%', '21.5%', '24%', '26.5%'], 'F((80*F(".95")+20*F(".25"))*18-1200,1200)'),
    ('D10-M066', '100', 'A', ['少100元', '少200元', '相同', '多100元'], '(400*8+400-250)-(500*6+500-250)'),
    ('D10-M067', '43/2', 'B', ['15', '21.5', '24', '35'], '(20*F(".15")+10*F(".45"))*F(".9")/F(".2")*(4-F(".4"))-40-10*6'),
    ('D10-M068', '890', 'C', ['875', '880', '890', '900'], 'next((100-b)*8+b*11 for b in range(0,101,10) if F(20)+F(".2")*b>=25 and F(5)+F(".15")*b<=10)'),
    ('D10-M069', '1254', 'B', ['1218', '1254', '1289', '1324'], 'max((85+3*k)*35-2000-12*k for k in range(15//4+1))'),
    ('D10-M070', '2', 'B', ['1', '2', '3', '4'], 'floor(F("66.6")/F(".65")-100)'),
    ('D10-M071', '28', 'B', ['25', '28', '31', '40'], 'max(((1000+20*n)//200)*20-60-3*n for n in range(50) if F(".18")<=F(120+20*n,1000+20*n)<=F(".2"))'),
    ('D10-M072', '2620', 'C', ['2420', '2500', '2620', '2700'], '60*(75-50)+80*(70-F(40*50+60*60,100))'),
    ('D10-M073', '2220', 'C', ['1720', '2120', '2220', '2720'], '120*70+80*60*F(".9")-100*(40+60)-500'),
    ('D10-M074', '408', 'B', ['384', '408', '432', '468'], '((next(a for a in range(14) if 84*a+120*(13-a)==1272)*12+(13-next(a for a in range(14) if 84*a+120*(13-a)==1272))*20)//7)*6*10-1272'),
    ('D10-M075', '49', 'B', ['48', '49', '50', '52'], 'floor(F(120*(70-5)-450,150))'),
    ('D10-M076', '1020', 'C', ['1000', '1010', '1020', '1040'], 'min(12*a+6*(100-a) for a in range(0,101,5) if F(".8")*a+F(".5")*(100-a)>=70)'),
    ('D10-M077', '140', 'B', ['130', '140', '150', '160'], '10*floor((F(500)*F(".17")+F(200)*F(".08"))/F(".12")/10-70)'),
    ('D10-M078', '20', 'B', ['15', '20', '25', '30'], '320-F(270,F(".9"))'),
    ('D10-M079', '4', 'A', ['4', '5', '6', '7'], 'floor((180+F(".1")*600)/F(".2")/250)'),
    ('D10-M080', '5255', 'B', ['5250', '5255', '5260', '5300'], 'min(40*a+55*b+80*(100-a-b) for a in range(20,101) for b in range(51) if 100-a-b>=0 and 60*a+80*b+100*(100-a-b)==7500)'),
    ('D10-M081', '80000', 'B', ['79900', '80000', '80286', '85900'], 'max(1000*a+1700*b-(6000 if b else 0) for a in range(101) for b in range(41) if 2*a+5*b<=200 and 3*a+4*b<=240)'),
    ('D10-M082', '785', 'C', ['778', '780', '785', '900'], 'max(75*a+82*b for a in range(9) for b in range(9) if 12*a+6*b<=100 and 8*a+15*b<=120)'),
    ('D10-M083', '3', 'B', ['2', '3', '4', '5'], 'max(min(r,y,b) for r in range(1,24) for y in range(1,14) for b in range(1,11) if 17*r+30*y+40*b==406)'),
    ('D10-M084', '2', 'A', ['2', '18', '26', '52'], 'next((52*a+34*b-50)-(52*(a-1)+34*b) for a in range(1,7) for b in range(1,14) if 13*a+6*b==83)'),
    ('D10-M085', '130', 'B', ['129', '130', '131', '150'], 'sum((F(".9") if n>=100 else 1)*(500+6*n)<min(300+8*n,1000+3*n) for n in range(1,301))'),
    ('D10-M086', '57', 'C', ['55', '56', '57', '60'], 'max(range(40,61),key=lambda p:(p-20)*(200-2*p)-200+(300 if p*(200-2*p)>=4900 else 0))'),
    ('D10-M087', '19', 'B', ['18', '19', '20', '21'], '12+max_exchange(12,12)'),
    ('D10-M088', '26', 'C', ['22', '24', '26', '28'], 'min(max(2*(66-y)+y-100,0)+2*max((66-y)+2*y-80,0) for y in range(22,67))'),
    ('D10-M089', '114', 'B', ['113', '114', '120', '130'], 'max(range(100,161),key=lambda n:min(5000-20*n,45*n-2400))'),
    ('D10-M090', '1600', 'C', ['1500', '1550', '1600', '1650'], 'max((40 if a>=60 else 30)*a+45*b-20*min(a+b,60)-35*max(a+b-60,0) for a in range(30,71) for b in range(30,51) if a+b<=100)'),
    ('D10-M091', '57', 'C', ['55', '56', '57', '58'], 'max(min((10*a+15*b)//2,8*a+5*b) for a in range(1,11) for b in range(1,9) if 100*a+120*b<=1000)'),
    ('D10-M092', '7200', 'D', ['6000', '6600', '7000', '7200'], 'F(12100)*F(72,121)'),
    ('D10-M093', '7/10', 'C', ['50%', '60%', '70%', '80%'], 'F(400-next(x for x in range(601) if 50*x+70*(600-x)==F(1,2)*(60*x+150*(600-x))),400)'),
    ('D10-M094', '275', 'B', ['270', '275', '282', '304'], 'min(36*a+58*b+87*c for a in range(2,6) for b in range(6) for c in range(6) if a+b+c<=5 and 6*a+10*b+15*c>=47)'),
    ('D10-M095', '225', 'C', ['204', '210', '225', '240'], 'max(45*(a+c)+33*(b+d)-120 for a in range(5) for b in range(6) for c in range(5) for d in range(6) if 5*a+4*b<=20 and 5*c+4*d<=20 and a+c>=2 and b+d>=3)'),
    ('D10-M096', '920', 'C', ['800', '880', '920', '960'], 'sum([100,100,60,60,120,0])+2*(100+60)+(40+120)'),
    ('D10-M097', '41', 'C', ['39', '40', '41', '42'], 'max(a+b+c for a in range(10,50) for b in range(4,34) for c in range(2,24) if 24*a+35*b+50*c==1184)'),
    ('D10-M098', '1872', 'C', ['1728', '1800', '1872', '1920'], '((F(156)-144)/F(".01")+100)*F("1.44")'),
    ('D10-M099', '4', 'B', ['3', '4', '5', '6'], 'sum(3*x+5*y+8*(36-x-y)==145 for x in range(1,35) for y in range(1,36-x))'),
    ('D10-M100', '3/14', 'B', ['1/6', '3/14', '1/4', '3/11'], '(F("1.2")*7-F("1.1")*6)/(F("1.2")*7)'),
    ('D10-M101', '204', 'C', ['202', '203', '204', '205'], 'min(p for p in range(180,241) if F(".95")*min(2*p-100,F("1.5")*p)-210>=80)'),
    ('D10-M102', '19', 'B', ['18.5', '19', '20', '20.5'], 'min(a+F("3.5")*b+F(".5")*(a+b-10) for a in range(13) for b in range(13) if 10<=a+b<=12 and 200<=10*a+40*b<=220)'),
    ('D10-M103', '1040', 'B', ['1020', '1040', '1080', '1100'], 'min(chain_coupon_cost(p) for p in permutations([240,360,540]))'),
    ('D10-M104', '4980', 'C', ['4870', '4900', '4980', '5100'], 'max(60*(200-b)+90*b-((40*(200-b)+60*b)*(F(".95") if 200-b>=120 else 1)+300) for b in range(70,101) if (40*(200-b)+60*b)*(F(".95") if 200-b>=120 else 1)+300<=10300)'),
    ('D10-M105', '2300', 'B', ['2280', '2300', '2360', '2380'], 'min(140*a+200*b for a in range(8) for b in range(11) if 4*a+5*b>=60 and 20*a+10*b<=210)'),
]

SERIES = [
    ('D10-N001', 'number', [20, 21, 17, 26, 10, 35, -1, 48], 7, [42, 45, 48, 50], 'C', 'grow([20],8,lambda s:s[-1]+(-1)**(len(s)+1)*len(s)**2)', ['42', '45', '48', '50']),
    ('D10-N002', 'number', [Fraction(2, 3), Fraction(4, 7), Fraction(8, 13), Fraction(16, 21), Fraction(32, 31), Fraction(64, 43)], 5, [Fraction(64, 41), Fraction(64, 43), Fraction(64, 45), Fraction(32, 43)], 'B', '[F(2**n,n*n+n+1) for n in range(1,7)]', ['64/41', '64/43', '64/45', '32/43']),
    ('D10-N003', 'number', [3, 8, 21, 58, 167, 492], 5, [490, 492, 494, 501], 'B', 'grow([3],6,lambda s:3*s[-1]-(2*len(s)-1))', ['490', '492', '494', '501']),
    ('D10-N004', 'number', [2, 6, 1, 9, 15, 12, 22, 30], 6, [20, 21, 22, 24], 'C', 'grow([2,6],8,lambda s:(len(s)+1)**2-s[-1]-s[-2])', ['20', '21', '22', '24']),
    ('D10-N005', 'number', [6, -6, 12, -36, 144, -720, 4320], 6, [-5040, -4320, 4320, 5040], 'C', '[6*(-1)**k*factorial(k) for k in range(7)]', ['−5040', '−4320', '4320', '5040']),
    ('D10-N006', 'number', [3, 12, 35, 80, 157, 280], 5, [248, 264, 272, 280], 'D', '[n**3+2**n for n in range(1,7)]', ['248', '264', '272', '280']),
    ('D10-N007', 'square', [2, 7, 20, 61, 182, 547], 4, [180, 181, 182, 184], 'C', 'grow([2],6,lambda s:3*s[-1]+(-1)**(len(s)+1))', ['√180', '√181', '√182', '√184']),
    ('D10-N008', 'number', [Fraction(1, 2), Fraction(4, 3), Fraction(11, 7), Fraction(29, 18), Fraction(76, 47), Fraction(199, 123)], 5, [Fraction(199, 123), Fraction(123, 199), Fraction(197, 123), Fraction(199, 121)], 'A', 'grow([F(1,2)],6,lambda s:(2*s[-1]+1)/(s[-1]+1))', ['199/123', '123/199', '197/123', '199/121']),
    ('D10-N009', 'number', [6, 12, 21, 35, 57, 92, 148], 6, [140, 146, 148, 150], 'C', 'cumulative(6,cumulative(6,fib(3,5,5)))', ['140', '146', '148', '150']),
    ('D10-N010', 'tuple', [(2, 5, 21), (3, 7, 40), (4, 9, 65), (5, 11, 96), (6, 13, 133)], 4, [(6, 13, 169), (6, 13, 133), (6, 12, 108), (7, 15, 176)], 'B', '[(a,2*a+1,(2*a+1)**2-a*a) for a in range(2,7)]', ['（6，13，169）', '（6，13，133）', '（6，12，108）', '（7，15，176）']),
    ('D10-N011', 'number', [6, 15, 35, 77, 143, 221], 5, [187, 209, 221, 247], 'C', '[a*b for a,b in zip([2,3,5,7,11,13],[3,5,7,11,13,17])]', ['187', '209', '221', '247']),
    ('D10-N012', 'number', [5, 2, 9, 6, 17, 12, 33, 20, 65], 7, [18, 20, 22, 24], 'B', 'weave([2**(k+2)+1 for k in range(5)],[n*(n+1) for n in range(1,5)])', ['18', '20', '22', '24']),
    ('D10-N013', 'number', [18, 26, 38, 62, 74, 102], 5, [92, 98, 102, 110], 'C', 'grow([18],6,lambda s:s[-1]+digit_product(s[-1]))', ['92', '98', '102', '110']),
    ('D10-N014', 'number', [2, 5, 7, 19, 26, 71, 97, 265], 6, [90, 93, 97, 101], 'C', 'grow([2,5],8,lambda s:s[-2]+(1 if len(s)%2==0 else 2)*s[-1])', ['90', '93', '97', '101']),
    ('D10-N015', 'number', [4, 36, 144, 400, 900, 1764], 5, [1444, 1600, 1764, 2025], 'C', '[(n*(n+1))**2 for n in range(1,7)]', ['1444', '1600', '1764', '2025']),
    ('D10-N016', 'number', [Fraction(1, 2), Fraction(1, 5), Fraction(1, 10), Fraction(1, 17), Fraction(1, 28), Fraction(1, 41)], 5, [Fraction(1, 39), Fraction(1, 40), Fraction(1, 41), Fraction(1, 43)], 'C', '[F(1,d) for d in cumulative(2,[3,5,7,11,13])]', ['1/39', '1/40', '1/41', '1/43']),
    ('D10-N017', 'number', [47, 65, 61, 37, 58, 89], 5, [85, 87, 89, 93], 'C', 'grow([47],6,lambda s:sum(int(c)**2 for c in str(s[-1])))', ['85', '87', '89', '93']),
    ('D10-N018', 'number', [4, 7, 9, 4, 25, 441], 5, [400, 416, 441, 484], 'C', 'grow([4,7],6,lambda s:(s[-1]-s[-2])**2)', ['400', '416', '441', '484']),
    ('D10-N019', 'number', [2, 3, 7, 16, 65, 321, 4546], 6, [4225, 4481, 4546, 4600], 'C', 'grow([2,3],7,lambda s:s[-1]+s[-2]**2)', ['4225', '4481', '4546', '4600']),
    ('D10-N020', 'number', [Fraction(-2, 1), Fraction(2, 1), Fraction(-8, 3), Fraction(4, 1), Fraction(-32, 5), Fraction(32, 3), Fraction(-128, 7)], 6, [Fraction(-128, 7), Fraction(-64, 7), Fraction(64, 7), Fraction(128, 7)], 'A', '[(-1)**n*F(2**n,n) for n in range(1,8)]', ['−128/7', '−64/7', '64/7', '128/7']),
    ('D10-N021', 'number', [15, 80, 255, 624, 1295], 4, [1249, 1295, 1296, 1330], 'B', '[n**4-1 for n in range(2,7)]', ['1249', '1295', '1296', '1330']),
    ('D10-N022', 'number', [Fraction(77, 25), Fraction(163, 20), Fraction(381, 25), Fraction(487, 20), Fraction(887, 25)], 4, [Fraction(862, 25), Fraction(3547, 100), Fraction(887, 25), Fraction(3649, 100)], 'C', '[F(f"{n*n-1}.{(n+1)**2-1:02d}") for n in range(2,7)]', ['34.48', '35.47', '35.48', '36.49']),
    ('D10-N023', 'number', [Fraction(100, 1), Fraction(52, 1), Fraction(29, 1), Fraction(37, 2), Fraction(57, 4), Fraction(105, 8)], 5, [Fraction(97, 8), Fraction(103, 8), Fraction(105, 8), Fraction(53, 4)], 'C', 'grow([F(100)],6,lambda s:s[-1]/2+len(s)+1)', ['12.125', '12.875', '13.125', '13.25']),
    ('D10-N024', 'number', [1, 8, 36, 128, 400, 1152], 5, [1000, 1152, 1200, 1296], 'B', '[n*n*2**(n-1) for n in range(1,7)]', ['1000', '1152', '1200', '1296']),
    ('D10-N025', 'number', [3, 4, 5, 11, 14, 107, 89], 6, [88, 89, 90, 91], 'B', 'grow([3,4],7,lambda s:s[-2]**2-s[-1])', ['88', '89', '90', '91']),
    ('D10-N026', 'tuple', [(2, 4, 10), (3, 5, 18), (5, 7, 40), (7, 9, 70), (11, 13, 154), (13, 15, 208)], 5, [(13, 15, 195), (13, 15, 208), (12, 14, 180), (13, 17, 234)], 'B', '[(p,p+2,p*(p+3)) for p in [2,3,5,7,11,13]]', ['（13，15，195）', '（13，15，208）', '（12，14，180）', '（13，17，234）']),
    ('D10-N027', 'number', [1, 4, 16, 49, 144, 400], 5, [324, 361, 400, 441], 'C', '[x*x for x in cumulative(1,fib(1,2,5))]', ['324', '361', '400', '441']),
    ('D10-N028', 'number', [2, 4, 7, 14, 19, 38, 45, 90], 6, [43, 45, 47, 49], 'B', 'grow([2],8,lambda s:2*s[-1] if len(s)%2 else s[-1]+[3,5,7][len(s)//2-1])', ['43', '45', '47', '49']),
    ('D10-N029', 'square', [2, 12, 45, 144, 425, 1188], 5, [1116, 1188, 1584, 1260], 'B', '[(i+1)**2*x for i,x in enumerate(grow([2],6,lambda s:2*s[-1]-1))]', ['6√31', '6√33', '12√11', '6√35']),
    ('D10-N030', 'number', [Fraction(2, 1), Fraction(3, 1), Fraction(8, 1), Fraction(30, 1), Fraction(144, 1), Fraction(840, 1)], 5, [720, 780, 840, 900], 'C', '[F(factorial(n+1),n) for n in range(1,7)]', ['720', '780', '840', '900']),
]

def check(condition, message):
    if not condition:
        raise AssertionError(message)

def run():
    results = []
    for qid, expected, key, options, expression in MATH:
        value = eval(expression, globals())
        vals = [canon_math(v) for v in options]
        check(value == F(expected), (qid, value, expected))
        check(len(set(vals)) == 4, (qid, "duplicate numeric options"))
        check(vals["ABCD".index(key)] == value, (qid, "answer key mismatch"))
        results.append({"id": qid, "answer": key, "value": str(value), "passed": True})
    competitors = []
    scanned = 0
    for qid, mode, full, missing, options, key, generator, display in SERIES:
        calculated = eval(generator, globals())
        check(calculated == full, (qid, "known-term mismatch"))
        check(len(set(options)) == 4, (qid, "duplicate series options"))
        check(options["ABCD".index(key)] == full[missing], (qid, "series key mismatch"))
        if mode == "number":
            scanned += 1
            coeffs = [F(k, 2) for k in range(-10, 11)]
            for i, option in enumerate(options):
                if i == "ABCD".index(key):
                    continue
                seq = list(map(F, full))
                seq[missing] = F(option)
                for a, b in product(coeffs, repeat=2):
                    c = seq[2] - a*seq[1] - b*seq[0]
                    if abs(c) <= 50 and all(seq[j] == a*seq[j-1]+b*seq[j-2]+c for j in range(2, len(seq))):
                        competitors.append({"id": qid, "option": "ABCD"[i], "coefficients": list(map(str, [a,b,c]))})
        results.append({"id": qid, "answer": key, "value": str(full[missing]), "all_known_terms_checked": True, "passed": True})
    check(not competitors, competitors)
    check(len(results) == 135 and len({q["id"] for q in results}) == 135, "ID/count mismatch")
    # Compare the actual book options and answer headings, rather than only a separate key table.
    root = Path(__file__).resolve().parent
    files = []
    for lo, hi in [(1,40), (41,80), (81,105)]:
        stem = f"D10_数学运算{lo:03}-{hi:03}"
        files.append((stem, [(r[0],r[2],r[3]) for r in MATH[lo-1:hi]]))
    files.append(("D10_数字推理001-030", [(r[0],r[5],r[7]) for r in SERIES]))
    checked_books = 0
    for stem, rows in files:
        question = root/(stem+"_题本.md")
        answer = root/(stem+"_答案.md")
        if not question.exists() or not answer.exists():
            raise FileNotFoundError(f"Missing book pair: {stem}; keep this script beside all eight Markdown books")
        qt, at = question.read_text(encoding="utf-8"), answer.read_text(encoding="utf-8")
        blocks = dict(re.findall(r"^### (D10-[MN]\d{3})\n(.*?)(?=^### |\Z)", qt, re.M|re.S))
        keys = dict(re.findall(r"^### (D10-[MN]\d{3})｜([A-D])", at, re.M))
        check(len(blocks) == len(rows) == len(keys), (stem, "book count mismatch"))
        for qid,key,options in rows:
            shown = re.findall(r"^([ABCD])\. (.+?)\s*$", blocks[qid], re.M)
            check(shown == list(zip("ABCD", options)), (qid, "printed options differ from verified options"))
            check(keys.get(qid) == key, (qid, "printed answer differs"))
        checked_books += 2
    report = {"version":"D10-v1-20261110", "math":105, "series":30, "books_checked":checked_books,
              "series_affine_scanned":scanned, "other_option_affine_matches":competitors, "results":results}
    out = root/"D10_核验结果.json"
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"PASS: {len(results)} questions; {checked_books} books; {scanned} finite affine scans; {out.name}")

if __name__ == "__main__":
    run()
