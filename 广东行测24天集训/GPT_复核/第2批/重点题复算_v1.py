"""复算第2批指定题的数值与排列；文字结论和原图真实性不由本脚本证明。"""
from fractions import Fraction as F
from itertools import permutations
from datetime import date, timedelta
import json


def nearest(value, options):
    distances = [abs(value - F(str(v))) for v in options]
    minimum = min(distances)
    assert distances.count(minimum) == 1, '最近选项不唯一'
    return 'ABCD'[distances.index(minimum)]


def main():
    out = {}
    def verify(qid, value, options, answer):
        observed = nearest(value, options)
        assert observed == answer, (qid, value, observed, answer)
        out[qid] = {'value': float(value), 'nearest_answer': observed}
    verify('D05-ZL-002', F('80.1')-F('80.1')/(F('1.154')*F('1.16')), [10.7,19.1,20.3,21.7], 'C')
    verify('D05-ZL-077', 30002*F('.192')-26015*F('.191'), [438,624,792,912], 'C')
    verify('D05-ZL-080', (F('56108.32')*F('51.92')/F('151.92'))/(F('9538.15')*F('30.72')/F('130.72')), [4.4,5.9,7.3,8.6], 'D')
    verify('D05-ZL-087', F(10)/F('.1921'), [52,68,100,120], 'A')
    verify('D05-ZL-098', F(12425)/F('1.0264'), [11715,12105,12762,13227], 'B')
    verify('D05-ZL-099', (F('6.14')-F('8.08'))-(F('4.35')-F('1.71')), [-4.58,-.5,5.37,1.79], 'A')
    verify('D05-ZL-111', (F('1728.7')/F('.0159'))/(F('2180.4')/F('.0249')), [.6,.8,1.2,1.6], 'C')
    assert all((date(2021,8,23)+timedelta(days=n)).month == 11 for n in (76,77))
    assert date(2021,6,5)+timedelta(days=17) > date(2021,6,4)-timedelta(days=9)
    assert F('19.21')-F('14.72') == F('4.49')
    assert F('34.2')/F('62.5') > F(1,2)
    assert F('62.5')/F('2.1') < 30
    assert [r>F('4.35') for r in map(F,['5.44','2.51','1.43'])] == [True,False,False]
    assert 2 < F('68.2')/F('19.2')-1 < 3
    assert F('93.37')/F('1.063') < 90
    assert F('.874')*12965 < 12597
    assert F(8019)/269 < 30
    assert F('7400.9')/18400 > F('.4')
    assert F('1.08')/F('1.84') < F('.6')
    base=[]
    for row in permutations('甲乙丙丁戊己庚辛'):
        p={x:row.index(x)+1 for x in row}
        if abs(p['甲']-p['丙'])==4 and abs(p['乙']-p['己'])==3 and p['庚']-p['丁']==3 and abs(p['辛']-p['戊'])==2:
            base.append(p)
    assert len(base)==32
    a=[p for p in base if abs(p['庚']-p['辛'])==1]
    c=[sum(p[k]==v for p in a) for k,v in [('甲',2),('乙',5),('丁',1),('己',4)]]
    assert len(a)==4 and c==[0,0,0,2]
    out['D06-PD-103']={'base':32,'conditioned':4,'option_true_counts':c}
    a=[p for p in base if abs(p['乙']-p['戊'])==1]
    c=[sum(min(p['甲'],p['丙'])<p[k]<max(p['甲'],p['丙']) for p in a) for k in '丁戊庚辛']
    assert len(a)==4 and c==[2,4,2,0]
    out['D06-PD-104']={'conditioned':4,'option_true_counts':c}
    # 科推：在报告列出的对称、平放、准静态模型条件下计算。
    outer=F(4,2)
    interface12=outer-1
    interface23=interface12-1
    assert interface23==0
    assert F('1.2')/(1000*F('.04'))==F('.03')
    out['D06-PD-129']={'pressures_at_cm':{str(h):max(0,12-4*h) for h in [0,1,2,3,4,5,20]}}
    # 另查3.55%与3.9%的近似区别。
    decrease=100*(1-F('14.8')/(F('18.6')/F('.97')-F('3.8')/F('.992')))
    assert nearest(decrease,[2.9,3.9,5,11.3])=='B'
    out['D05-ZL-108']={'decline_percent':float(decrease)}
    # D04两种读法；这里只验证报告反例，不改动原题。
    assert F(90,8)+F(140-12*F(90,8),20)==F('11.5')
    exact=min(x for x in range(1,20) if 72-7*x>=0 and (72-7*x)%3==0 and x+(72-7*x)//3<=19)
    fractional=min(x for x in range(1,20) if 72-7*x>=0 and x+F(72-7*x,3)<=19)
    assert (exact,fractional)==(6,4)
    assert 21+(9+3)==33 and 12+21+3==36
    assert 36+48+108==33+64+95==192
    print(json.dumps({'status':'assertions_passed','scope':'所列数值与排列核验；不含全部390题或自然语言唯一性证明','results':out}, ensure_ascii=False, indent=2))


if __name__=='__main__':
    main()
