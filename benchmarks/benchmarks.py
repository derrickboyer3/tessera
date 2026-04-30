'''
    Tessera Benchmarks
    ------------------
    Compares Tessera's transpiler output against Qiskit's transpiler across
    a set of benchmark circuits. Measures gate counts, circuit depth, and
    simulation correctness for each circuit.

    After running the circuits, the script prints a diff chart against
    benchmark_store.json so you can see how this run compared to the stored
    baselines, including any new bests on gate count or depth.

    Flags:
        --write          Update benchmark_store.json with this run's numbers.
                         Refuses to write if any metric on any circuit got
                         worse than the stored ceiling, or if any simulation
                         distribution mismatches Qiskit. best_max_* fields
                         only ever ratchet downward.
        --allow-loosen   Update benchmark_store.json even if some metrics
                         regressed. best_max_* fields are still preserved as
                         monotonic watermarks. Use this when you intentionally
                         trade one metric for another.

    Run with:
        python Tessera/benchmarks/benchmarks.py
        python Tessera/benchmarks/benchmarks.py --write
        python Tessera/benchmarks/benchmarks.py --allow-loosen

    Update benchmarks.md with results after each run.
'''
import argparse
import datetime
import json
import time
import numpy as np
from qiskit import QuantumCircuit, transpile as qiskit_transpile
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2
from qiskit_aer import AerSimulator

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tessera.api.transpile import transpile as tessera_transpile
from tessera.backends.coupling_maps import IBM_DEFAULT_COUPLING_MAP

pi = np.pi
SHOTS = 4096
SIM_TOLERANCE = 0.05

STORE_PATH = os.path.join(os.path.dirname(__file__), 'benchmark_store.json')

# ── Helpers ───────────────────────────────────────────────────────────────────

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def simulate(circuit, shots=SHOTS):
    sim = AerSimulator()
    job = sim.run(circuit, shots=shots)
    counts = job.result().get_counts()
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()}

def distributions_match(dist1, dist2, tolerance=SIM_TOLERANCE):
    all_keys = set(dist1.keys()) | set(dist2.keys())
    for key in all_keys:
        p1 = dist1.get(key, 0)
        p2 = dist2.get(key, 0)
        if abs(p1 - p2) > tolerance:
            return False
    return True

def run_benchmark(name, qc, qiskit_backend, tessera_coupling_map_key="IBM_DEFAULT"):
    print(f"\n  Circuit: {name}")
    print(f"  Input gates: {len(qc.data)} | Qubits: {qc.num_qubits}")

    # ── Tessera ───────────────────────────────────────────────────────────────
    start = time.perf_counter()
    tessera_result = tessera_transpile(qc, coupling_map=tessera_coupling_map_key)
    tessera_time = time.perf_counter() - start
    tessera_gates = len(tessera_result.data)
    tessera_depth = tessera_result.depth()

    # ── Qiskit ────────────────────────────────────────────────────────────────
    start = time.perf_counter()
    qiskit_result = qiskit_transpile(qc, backend=qiskit_backend, optimization_level=1)
    qiskit_time = time.perf_counter() - start
    qiskit_gates = len(qiskit_result.data)
    qiskit_depth = qiskit_result.depth()

    # ── Simulation ────────────────────────────────────────────────────────────
    tessera_dist = simulate(tessera_result)
    qiskit_dist = simulate(qiskit_result)
    match = distributions_match(tessera_dist, qiskit_dist)

    # ── Output ────────────────────────────────────────────────────────────────
    print(f"  {'Metric':<25} {'Tessera':>10} {'Qiskit':>10}")
    print(f"  {'-'*45}")
    print(f"  {'Gate Count':<25} {tessera_gates:>10} {qiskit_gates:>10}")
    print(f"  {'Circuit Depth':<25} {tessera_depth:>10} {qiskit_depth:>10}")
    print(f"  {'Transpile Time (s)':<25} {tessera_time:>10.4f} {qiskit_time:>10.4f}")
    print(f"  {'Simulation Match':<25} {str(match):>10}")

    if not match:
        print(f"\n  WARNING: Simulation distributions do not match within tolerance {SIM_TOLERANCE}")
        print(f"  Tessera: {tessera_dist}")
        print(f"  Qiskit:  {qiskit_dist}")

    return {
        "name": name,
        "gates_in": len(qc.data),
        "tessera_gates": tessera_gates,
        "qiskit_gates": qiskit_gates,
        "tessera_depth": tessera_depth,
        "qiskit_depth": qiskit_depth,
        "tessera_time": tessera_time,
        "qiskit_time": qiskit_time,
        "sim_match": match
    }

# ── Benchmark Circuits ────────────────────────────────────────────────────────

def make_bell_state():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def make_ghz_state():
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

def make_qft_like():
    qc = QuantumCircuit(5, 5)
    for i in range(5):
        qc.h(i)
    for i in range(4):
        qc.rz(pi / (2 ** i), i)
        qc.rz(pi / (2 ** i), i)  # intentional duplicate — tests MergeRotationsPass
        qc.cx(i, i + 1)
    qc.measure(list(range(5)), list(range(5)))
    return qc

def make_stress_test():
    qc = QuantumCircuit(5, 5)
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.t(3)
    qc.s(4)
    qc.cx(0, 4)
    qc.cz(0, 4)
    qc.cx(0, 4)
    qc.cx(1, 3)
    qc.cy(1, 3)
    qc.cx(1, 3)
    qc.cx(2, 0)
    qc.cx(2, 4)
    qc.measure(list(range(5)), list(range(5)))
    return qc

# ── Store IO ──────────────────────────────────────────────────────────────────

def load_store():
    if not os.path.exists(STORE_PATH):
        return {}
    with open(STORE_PATH) as f:
        return json.load(f)

def save_store(store):
    with open(STORE_PATH, 'w') as f:
        json.dump(store, f, indent=2)
        f.write('\n')

def status_for(current, stored, best):
    if stored is None:
        return "no baseline"
    if current > stored:
        return "REGRESSED"
    if best is not None and current < best:
        return "NEW BEST!"
    if current < stored:
        return "tightened"
    return "same"

def print_diff_chart(results, store):
    section("Diff vs benchmark_store.json")

    if not store:
        print("\n  No benchmark_store.json found — nothing to diff against.")
        return

    print(f"\n  {'Circuit':<14} {'Metric':<7} {'Current':>8} {'Stored':>8} {'Best':>6} {'Delta':>7}  {'Status':<12}")
    print(f"  {'-'*70}")

    for r in results:
        entry = store.get(r['name'], {})
        for label, current, stored_key, best_key in (
            ("Gates", r['tessera_gates'], 'max_gates', 'best_max_gates'),
            ("Depth", r['tessera_depth'], 'max_depth', 'best_max_depth'),
        ):
            stored = entry.get(stored_key)
            best = entry.get(best_key)
            if stored is None:
                delta_str = "-"
            else:
                delta = current - stored
                delta_str = f"{delta:+d}" if delta != 0 else "0"
            stored_str = str(stored) if stored is not None else "-"
            best_str = str(best) if best is not None else "-"
            status = status_for(current, stored, best)
            print(f"  {r['name']:<14} {label:<7} {current:>8} {stored_str:>8} {best_str:>6} {delta_str:>7}  {status:<12}")

def find_regressions(results, store):
    out = []
    for r in results:
        entry = store.get(r['name'], {})
        for label, current, stored_key in (
            ("gates", r['tessera_gates'], 'max_gates'),
            ("depth", r['tessera_depth'], 'max_depth'),
        ):
            stored = entry.get(stored_key)
            if stored is not None and current > stored:
                out.append((r['name'], label, current, stored))
    return out

def apply_write(results, store):
    today = datetime.date.today().isoformat()
    for r in results:
        name = r['name']
        entry = store.get(name, {})
        new_gates = r['tessera_gates']
        new_depth = r['tessera_depth']
        prev_best_gates = entry.get('best_max_gates', new_gates)
        prev_best_depth = entry.get('best_max_depth', new_depth)
        store[name] = {
            'max_gates': new_gates,
            'best_max_gates': min(prev_best_gates, new_gates),
            'max_depth': new_depth,
            'best_max_depth': min(prev_best_depth, new_depth),
            'last_updated': today,
        }

# ── Main ──────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(
    description="Run Tessera vs Qiskit benchmarks and optionally update benchmark_store.json"
)
write_group = parser.add_mutually_exclusive_group()
write_group.add_argument(
    '--write',
    action='store_true',
    help="Update benchmark_store.json. Refuses to write if any metric on any circuit regressed against the stored ceiling, or if any simulation distribution mismatched Qiskit."
)
write_group.add_argument(
    '--allow-loosen',
    action='store_true',
    help="Update benchmark_store.json even if some metrics regressed. Best-seen watermarks are preserved."
)
args = parser.parse_args()

section("Tessera vs Qiskit Benchmark")
print(f"  Shots per simulation: {SHOTS}")
print(f"  Simulation tolerance: {SIM_TOLERANCE}")
print(f"  Qiskit optimization level: 1")
print(f"  Tessera coupling map: FakeNairobiV2 (7 qubits)")

qiskit_backend = FakeNairobiV2()

circuits = [
    ("Bell State",   make_bell_state()),
    ("GHZ State",    make_ghz_state()),
    ("QFT-like",     make_qft_like()),
    ("Stress Test",  make_stress_test()),
]

results = []
for name, qc in circuits:
    result = run_benchmark(name, qc, qiskit_backend)
    results.append(result)

# ── Summary ───────────────────────────────────────────────────────────────────
section("Summary")
print(f"\n  {'Circuit':<20} {'Gates In':>10} {'Tessera':>10} {'Qiskit':>10} {'Depth T':>10} {'Depth Q':>10} {'Sim OK':>8}")
print(f"  {'-'*78}")
for r in results:
    print(f"  {r['name']:<20} {r['gates_in']:>10} {r['tessera_gates']:>10} {r['qiskit_gates']:>10} {r['tessera_depth']:>10} {r['qiskit_depth']:>10} {str(r['sim_match']):>8}")

all_match = all(r['sim_match'] for r in results)
print(f"\n  All simulations match: {all_match}")

# ── Diff Chart ────────────────────────────────────────────────────────────────
store = load_store()
print_diff_chart(results, store)

# ── Optional Write ────────────────────────────────────────────────────────────
if args.write or args.allow_loosen:
    section("Store Update")

    if not all_match:
        failing = [r['name'] for r in results if not r['sim_match']]
        print(f"\n  REFUSED: simulation mismatch on: {', '.join(failing)}")
        print(f"  Will not write to benchmark_store.json with broken simulation.")
        sys.exit(1)

    regressions = find_regressions(results, store)

    if regressions and not args.allow_loosen:
        print(f"\n  REFUSED: --write requires every metric to be <= the stored ceiling.")
        print(f"  The following metrics regressed:")
        for name, metric, current, stored in regressions:
            print(f"    {name} {metric}: {current} (stored ceiling: {stored})")
        print(f"\n  Investigate the regression, or rerun with --allow-loosen if intentional.")
        sys.exit(1)

    apply_write(results, store)
    save_store(store)

    print(f"\n  benchmark_store.json updated.")
    if args.allow_loosen and regressions:
        print(f"  Loosened the following ceilings (best_* watermarks preserved):")
        for name, metric, current, stored in regressions:
            print(f"    {name} {metric}: {stored} -> {current}")
else:
    print(f"\n  Copy these results into benchmarks.md under a new Run section.")
    print(f"  To update benchmark_store.json, rerun with --write (or --allow-loosen).")
