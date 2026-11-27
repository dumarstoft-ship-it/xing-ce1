"""每天50题计划的粗算：在不同起始日和正确率下，到考前能学到第几道题、每道题平均见几次。

用法：python3 广东行测18套模拟/备考资料/马哲辨析/精选/simulate.py
计划规则（与网页的“今日计划”一致）：
- 每天固定题数，按顺序填满：①上次答错、今天到期的；②只答对过一次、今天到期的（第一次间隔复习）；
  ③没做过的核心题（按价值顺序）；④答对两次以上、今天到期的；⑤没做过的备选题。
- 答错次日再出；答对后隔2天、4天、7天再出。
- 考前两天（12月4日、5日）先做①②，再做“考前回顾”（错过的、只见过一次的，最久没见的在前），最后才是新题。
"""
import random
from datetime import date, timedelta

EXAM = date(2026, 12, 6)
INTERVALS = [1, 2, 4, 7, 14, 30]


def run(start, daily=50, p_new=0.75, p_rev=0.9, n_core=10**6, seed=1):
    rnd = random.Random(seed)
    P = {}          # id -> dict(n, c, b, due, last, wrong)
    next_new = 0
    day = start
    log = []
    while day < EXAM:
        final = (EXAM - day).days <= 2
        due = [i for i, p in P.items() if p["due"] <= day]
        a = [i for i in due if not P[i]["l"]]
        b = [i for i in due if P[i]["l"] and P[i]["b"] == 1]
        d = sorted([i for i in due if P[i]["l"] and P[i]["b"] >= 2], key=lambda i: P[i]["due"])
        picked = []
        seen_today = set()

        def take(ids):
            for i in ids:
                if len(picked) >= daily:
                    break
                if i not in seen_today:
                    picked.append(i)
                    seen_today.add(i)

        take(a)
        take(b)
        if final:
            look = sorted([i for i, p in P.items() if (p["c"] < p["n"] or p["n"] == 1) and p["last"] < day - timedelta(days=1)],
                          key=lambda i: P[i]["last"])
            take(look)
        n_fresh = 0
        while len(picked) < daily and next_new < n_core:
            picked.append(next_new)
            seen_today.add(next_new)
            next_new += 1
            n_fresh += 1
        take(d)
        if len(picked) < daily:      # 还有空位：最久没见的
            take(sorted(P, key=lambda i: P[i]["last"]))
        for i in picked:
            p = P.setdefault(i, {"n": 0, "c": 0, "b": 0, "l": 0, "due": day, "last": day})
            ok = rnd.random() < (p_rev if p["n"] else p_new)
            p["n"] += 1
            p["c"] += ok
            p["l"] = ok
            p["last"] = day
            if ok:
                p["b"] = min(p["b"] + 1, len(INTERVALS) - 1)
                p["due"] = day + timedelta(days=INTERVALS[p["b"]])
            else:
                p["b"] = 0
                p["due"] = day + timedelta(days=1)
        log.append((day.strftime("%m-%d"), n_fresh, len(picked) - n_fresh))
        day += timedelta(days=1)
    seen = len(P)
    once = sum(1 for p in P.values() if p["n"] == 1)
    weak = sum(1 for p in P.values() if not p["l"])
    avg = sum(p["n"] for p in P.values()) / max(seen, 1)
    return seen, avg, once, weak, log


if __name__ == "__main__":
    for start in (date(2026, 11, 27), date(2026, 11, 28)):
        for p_new in (0.6, 0.75, 0.85):
            res = [run(start, p_new=p_new, seed=s) for s in range(20)]
            seen = sum(r[0] for r in res) / len(res)
            avg = sum(r[1] for r in res) / len(res)
            once = sum(r[2] for r in res) / len(res)
            weak = sum(r[3] for r in res) / len(res)
            print(f"从{start:%m-%d}起 首次正确率{p_new:.0%}：学到 {seen:.0f} 道，每道平均见 {avg:.2f} 次，只见过一次 {once:.0f} 道，考前最后一次仍答错 {weak:.0f} 道")
        print("  逐日（新题/复习）：", " ".join(f"{d}:{n}/{r}" for d, n, r in run(start)[4]))
    print()
    for n_core in (150, 170, 190, 210):
        for start in (date(2026, 11, 27), date(2026, 11, 28)):
            res = [run(start, n_core=n_core, seed=s) for s in range(20)]
            print(f"核心{n_core}道 从{start:%m-%d}起：学到 {sum(r[0] for r in res)/20:.0f}，平均见 {sum(r[1] for r in res)/20:.2f} 次，只见一次 {sum(r[2] for r in res)/20:.0f}，最后仍错 {sum(r[3] for r in res)/20:.0f}；逐日 "
                  + " ".join(f"{n}/{r}" for d, n, r in run(start, n_core=n_core)[4]))
