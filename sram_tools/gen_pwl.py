#!/usr/bin/env python3
"""
Generate vpwl stimulus files + a test plan to write/read EVERY cell of the
4x6 (24-bit) SRAM:  A<4:0> = {row[1:0], col[2:0]}, DATA_IN/DATA_OUT are 1 bit.

Per test pattern:  write all 24 cells -> read all 24 cells (x READ_PASSES).
Patterns: all 1s, all 0s, random.

One operation = one CLK1 period T:
    t0            CLK1 rises (buffers disabled; tri-state enabled when CLK1=0)
    t0+0.05T      RD/WR of previous op fall   (break-before-make: never both 1)
    t0+0.08T      A<4:0>, DATA_IN change
    t0+0.10T      RD or WR for this op rises
    t0+0.15T..0.45T  CLK2 active (precharge window, CLK1 still high)
    t0+0.50T      CLK1 falls -> buffers enabled -> access happens
    t0+0.95T      DATA_OUT sampled by the checker
Adjust the fractions below if your design needs different phasing.
"""
import argparse, csv, os, random

ap = argparse.ArgumentParser()
ap.add_argument("--vdd", type=float, default=1.1)
ap.add_argument("--period", type=float, default=50e-9, help="CLK1 period (>=10 MHz required)")
ap.add_argument("--tr", type=float, default=100e-12, help="rise/fall time")
ap.add_argument("--read-passes", type=int, default=2, help="read every cell this many times in a row-pass")
ap.add_argument("--rows", type=int, default=4)
ap.add_argument("--cols", type=int, default=6, help="valid column codes are 0..cols-1")
ap.add_argument("--seed", type=int, default=5322)
ap.add_argument("--clk2-active-high", action="store_true",
                help="default assumes CLK2 LOW turns the precharge PMOS on")
ap.add_argument("--no-invert-din-on-read", action="store_true",
                help="by default DATA_IN = ~expected during reads, to prove DATA_OUT comes from the cell")
ap.add_argument("--out", default="/home/claude/sram_tb")
a = ap.parse_args()

T, VDD, TR = a.period, a.vdd, a.tr
os.makedirs(a.out, exist_ok=True)
cells = [(r, c) for r in range(a.rows) for c in range(a.cols)]
addr_of = lambda r, c: (r << 3) | c            # A<4:3>=row, A<2:0>=col  (edit if yours differs)

rng = random.Random(a.seed)
while True:
    rand_pat = [rng.randint(0, 1) for _ in cells]
    # want a real mix, and at least some bits that flip relative to the all-0 test
    if 8 <= sum(rand_pat) <= 16:
        break
patterns = [("ALL_1", [1] * len(cells)), ("ALL_0", [0] * len(cells)), ("RANDOM", rand_pat)]

# ---- build operation list ------------------------------------------------
ops = [dict(test="IDLE", kind="idle", cell=None, addr=0, din=0, exp=None)]
for name, pat in patterns:
    for i, (r, c) in enumerate(cells):
        ops.append(dict(test=name, kind="write", cell=(r, c), addr=addr_of(r, c), din=pat[i], exp=pat[i]))
    for p in range(a.read_passes):
        for i, (r, c) in enumerate(cells):
            din = 0 if a.no_invert_din_on_read else 1 - pat[i]
            ops.append(dict(test=name, kind="read", cell=(r, c), addr=addr_of(r, c), din=din, exp=pat[i], rpass=p + 1))
ops.append(dict(test="IDLE", kind="idle", cell=None, addr=0, din=0, exp=None))
t_stop = T * len(ops)

# ---- level-change event lists (time, level 0/1) --------------------------
ev = {k: [(0.0, 0)] for k in ["CLK1", "CLK2", "RD", "WR", "DATA_IN"] + [f"A{b}" for b in range(5)]}

def setlvl(sig, t, lvl):
    if ev[sig][-1][1] != lvl:
        ev[sig].append((t, lvl))

prev = None
for n, op in enumerate(ops):
    t0 = n * T
    setlvl("CLK1", t0, 1)
    setlvl("CLK1", t0 + 0.50 * T, 0)
    on, off = (1, 0) if a.clk2_active_high else (0, 1)
    setlvl("CLK2", t0, off)
    setlvl("CLK2", t0 + 0.15 * T, on)
    setlvl("CLK2", t0 + 0.45 * T, off)
    setlvl("RD", t0 + 0.05 * T, 0)
    setlvl("WR", t0 + 0.05 * T, 0)
    for b in range(5):
        setlvl(f"A{b}", t0 + 0.08 * T, (op["addr"] >> b) & 1)
    setlvl("DATA_IN", t0 + 0.08 * T, op["din"])
    if op["kind"] == "read":
        setlvl("RD", t0 + 0.10 * T, 1)
    elif op["kind"] == "write":
        setlvl("WR", t0 + 0.10 * T, 1)
    op["t0"] = t0
    op["sample"] = t0 + 0.95 * T

# ---- write PWL files -----------------------------------------------------
def write_pwl(sig, events):
    pts = []
    lvl0 = events[0][1]
    pts.append((0.0, lvl0))
    last = lvl0
    for t, l in events[1:]:
        pts.append((t, last))
        pts.append((t + TR, l))
        last = l
    pts.append((t_stop, last))
    with open(os.path.join(a.out, f"{sig}.pwl"), "w") as f:
        for t, l in pts:
            f.write(f"{t:.6e} {l * VDD:g}\n")

for sig, e in ev.items():
    write_pwl(sig, e)

# ---- test plan -----------------------------------------------------------
with open(os.path.join(a.out, "test_plan.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["op", "test", "kind", "read_pass", "row", "col", "A<4:0>", "DATA_IN",
                "expected_DATA_OUT", "t_start_ns", "CLK1_fall_ns", "sample_ns"])
    for n, op in enumerate(ops):
        r, c = op["cell"] if op["cell"] else ("", "")
        w.writerow([n, op["test"], op["kind"], op.get("rpass", ""), r, c,
                    format(op["addr"], "05b") if op["cell"] else "",
                    op["din"], op["exp"] if op["kind"] == "read" else "",
                    f"{op['t0']*1e9:.1f}", f"{(op['t0']+0.5*T)*1e9:.1f}", f"{op['sample']*1e9:.1f}"])

# ---- human summary -------------------------------------------------------
with open(os.path.join(a.out, "README.txt"), "w") as f:
    f.write(f"CLK1 period {T*1e9:g} ns ({1/T/1e6:g} MHz), VDD {VDD} V, stop time {t_stop*1e6:.3f} us\n")
    f.write("Address map: A<4:3>=row (0..3), A<2:0>=column (0..5 valid). Edit addr_of() if different.\n\n")
    for name, pat in patterns:
        f.write(f"{name:7s} (row-major, rows 0..3, cols 0..5):\n")
        for r in range(a.rows):
            f.write("   row %d: %s\n" % (r, "".join(str(pat[r * a.cols + c]) for c in range(a.cols))))
    f.write("\nPWL files: CLK1 CLK2 RD WR DATA_IN A0..A4 (.pwl)\n")

print(open(os.path.join(a.out, "README.txt")).read())
print(f"{len(ops)} operations, stop = {t_stop*1e6:.3f} us -> {a.out}")
