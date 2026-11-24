#!/usr/bin/env python3
"""
Check exported DATA_OUT against test_plan.csv.

Usage:  python3 check_sram.py test_plan.csv dataout.csv [--vdd 1.1] [--invert]
dataout.csv: two columns, time(s), voltage(V)  (header lines/non-numeric rows are skipped;
             also accepts whitespace- or comma-separated; time in seconds).
Each read op's DATA_OUT is interpolated at its 'sample_ns' time and thresholded at VDD/2.
"""
import argparse, csv, re, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("plan")
ap.add_argument("wave")
ap.add_argument("--vdd", type=float, default=1.1)
ap.add_argument("--invert", action="store_true", help="DATA_OUT is the complement of the stored bit")
ap.add_argument("--margin", type=float, default=0.2, help="flag samples within +-margin*VDD of VDD/2 as marginal")
a = ap.parse_args()

t, v = [], []
for line in open(a.wave):
    parts = [p for p in re.split(r"[,\s;]+", line.strip()) if p]
    if len(parts) < 2:
        continue
    try:
        t.append(float(parts[0])); v.append(float(parts[1]))
    except ValueError:
        continue
t, v = np.array(t), np.array(v)
if len(t) < 2:
    sys.exit("could not parse any numeric (time, value) rows from " + a.wave)
order = np.argsort(t); t, v = t[order], v[order]

fails = marginal = n = 0
cur = None
print(f"{'test':7s} {'pass':>4s} {'row':>3s} {'col':>3s} {'A<4:0>':>6s} {'exp':>3s} {'Vout(V)':>8s} {'got':>3s}  result")
for row in csv.DictReader(open(a.plan)):
    if row["kind"] != "read":
        continue
    ts = float(row["sample_ns"]) * 1e-9
    if ts > t[-1]:
        print(f"sample time {ts:.3e} s is beyond the waveform end ({t[-1]:.3e} s)"); fails += 1; continue
    vo = float(np.interp(ts, t, v))
    got = int(vo > a.vdd / 2)
    if a.invert:
        got ^= 1
    exp = int(row["expected_DATA_OUT"])
    ok = got == exp
    marg = abs(vo - a.vdd / 2) < a.margin * a.vdd
    n += 1; fails += (not ok); marginal += marg
    print(f"{row['test']:7s} {row['read_pass']:>4s} {row['row']:>3s} {row['col']:>3s} {row['A<4:0>']:>6s} {exp:>3d} {vo:8.3f} {got:>3d}  "
          f"{'PASS' if ok else 'FAIL'}{'  (marginal level)' if marg else ''}")

print(f"\n{n} reads checked, {fails} failed, {marginal} marginal")
sys.exit(1 if fails else 0)
