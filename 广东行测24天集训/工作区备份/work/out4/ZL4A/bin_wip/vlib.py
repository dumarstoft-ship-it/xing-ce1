"""Shared helpers for ZL3A verification."""
INF = 1e18
def gr(cur, base):            # growth rate in %
    return (cur / base - 1) * 100
def inc(cur, r):              # increment from current value and growth rate (%)
    return cur * r / (100 + r)
def base(cur, r):
    return cur / (1 + r / 100)
def f(x, n=2):
    return f'{x:.{n}f}'
def nearest(v, opts):
    """opts: letter->number. returns (letter, relative gap between the true value's distance to the best option and to the 2nd best)."""
    best = min(opts, key=lambda k: abs(opts[k] - v))
    others = sorted(abs(opts[k] - v) for k in opts if k != best)
    return best, (others[0] - abs(opts[best] - v)) / abs(v)
def interval(v, bounds):
    """bounds: list of (letter, lo, hi); returns (letter, relative distance to nearest finite boundary)."""
    for k, lo, hi in bounds:
        if lo <= v < hi:
            ds = [abs(v - b) for b in (lo, hi) if abs(b) < INF / 10]
            return k, (min(ds) / abs(v)) if ds else 1.0
    raise ValueError(v)
def rank_margin(vals):
    """vals: name->value; returns (sorted names desc, min relative gap between adjacent values)."""
    order = sorted(vals, key=lambda n: -vals[n])
    gaps = [abs(vals[order[i]] - vals[order[i + 1]]) / max(abs(vals[order[i]]), abs(vals[order[i + 1]]), 1e-12) for i in range(len(order) - 1)]
    return order, min(gaps) if gaps else 1.0
def prec(m):
    """precision band from relative margin."""
    if m is None: return None
    if m >= 0.08: return '粗估'
    if m >= 0.02: return '估到前三位'
    return '须精算'
