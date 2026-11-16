"""Q40: electricity 0.79 yuan/kWh; idle fee after full charge:
  first 30 min free; the part in (30, 60] min: 1.7 yuan per 10 min;
  the part beyond 60 min: 3 yuan per 10 min; partial 10 min counts as 10 min.
50 kWh charged, total paid 56.6 yuan. Longest possible time since full charge when leaving?
options A 40min  B 1h30  C 1h40  D 1h50
Work in fen (0.01 yuan) to avoid float error; scan time in seconds."""
import math

def idle_fee_fen(t_sec):
    """idle fee in fen for t_sec seconds after full charge"""
    fee = 0
    mid = min(max(t_sec - 30 * 60, 0), 30 * 60)       # part in (30, 60] min
    fee += math.ceil(mid / 600) * 170
    late = max(t_sec - 60 * 60, 0)                    # part beyond 60 min
    fee += math.ceil(late / 600) * 300
    return fee

elec = 50 * 79           # fen
paid = 5660              # fen
idle = paid - elec
print("electricity", elec / 100, "yuan; idle fee", idle / 100, "yuan")
assert idle == 1710

ok = [t for t in range(0, 4 * 3600 + 1) if idle_fee_fen(t) == idle]
lo, hi = min(ok), max(ok)
print(f"fee 17.1 when t in [{lo/60:.4f}, {hi/60:.4f}] minutes (contiguous: {hi - lo + 1 == len(ok)})")
assert hi == 100 * 60 and lo == 90 * 60 + 1 and hi - lo + 1 == len(ok)
print("breakdown at 100 min:", "30-60 min ->", 3 * 1.7, "yuan; 60-100 min ->", 4 * 3, "yuan")

opts = {"A": 40, "B": 90, "C": 100, "D": 110}
for k, m in opts.items():
    print(k, m, "min -> idle fee", idle_fee_fen(m * 60) / 100)
matches = [k for k, v in opts.items() if v * 60 == hi]
assert matches == ["C"], matches
print("ANSWER:", matches[0])
