# Day 0 = June 30 (watered 12:00). July days 1..31. Choose hot/not for each July day.
# After a watering at day w (ends 12:30), streak counts hot noons on w+1, w+2,...
# Water at day d if streak reaches 3 at day d, or if d-w==5 (120h) without trigger.
# Count waterings on days 1..31; need exactly 8. Minimize hot days among days 1..31.
from functools import lru_cache
INF=10**9
def solve(include_w_day=False, timeout=5, need=8, ndays=31):
    # state: day index processed, k=days since last watering, streak, count
    @lru_cache(None)
    def f(day, k, streak, cnt):
        if cnt>need: return INF
        if day>ndays:
            return 0 if cnt==need else INF
        best=INF
        for hot in (0,1):
            s=streak+1 if hot else 0
            kk=k+1
            water = (s>=3) or (kk>=timeout)
            if water:
                r=f(day+1,0,(1 if (include_w_day and hot) else 0),cnt+1)
            else:
                r=f(day+1,kk,s,cnt)
            best=min(best,r+hot)
        return best
    return f(1,0,0,0)
print('base (streak restarts after watering, timeout 5 days):',solve())
print('variant: watering-day heat counts toward next streak:',solve(include_w_day=True))
# reconstruct one optimal schedule for base
def recon():
    from functools import lru_cache
    need=8;ndays=31;timeout=5
    @lru_cache(None)
    def f(day,k,streak,cnt):
        if cnt>need: return INF
        if day>ndays: return 0 if cnt==need else INF
        best=INF
        for hot in (0,1):
            s=streak+1 if hot else 0; kk=k+1
            water=(s>=3) or (kk>=timeout)
            r=f(day+1,0,0,cnt+1) if water else f(day+1,kk,s,cnt)
            best=min(best,r+hot)
        return best
    day,k,streak,cnt=1,0,0,0; hots=[];waters=[]
    while day<=ndays:
        for hot in (0,1):
            s=streak+1 if hot else 0; kk=k+1
            water=(s>=3) or (kk>=timeout)
            nxt=(day+1,0,0,cnt+1) if water else (day+1,kk,s,cnt)
            if f(*nxt)+hot==f(day,k,streak,cnt):
                if hot: hots.append(day)
                if water: waters.append(day)
                day,k,streak,cnt=nxt;break
    return hots,waters
print(recon())
# brute-force check of interval reasoning: intervals in {3,4,5}
from itertools import product
best=None
for iv in product([3,4,5],repeat=8):
    d=0;days=[]
    for x in iv: d+=x;days.append(d)
    if days[-1]>31: continue
    if days[-1]+3<=31: continue  # a 9th could be forced by timeout? next watering at most +5; min +3
    # need 9th not in July: next watering happens at latest last+5; if last+5<=31 a 9th is unavoidable
    hot=sum(3 for x in iv if x in (3,4))
    if best is None or hot<best[0]: best=(hot,iv,days)
print('interval enumeration (requires last+5>31):',best)
best=None
for iv in product([3,4,5],repeat=8):
    d=0;days=[]
    for x in iv: d+=x;days.append(d)
    if days[-1]>31: continue
    if days[-1]+5<=31: continue
    hot=sum(3 for x in iv if x in (3,4))
    if best is None or hot<best[0]: best=(hot,iv,days)
print('interval enumeration (last+5>31):',best)
