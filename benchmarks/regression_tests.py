'''
    Tessera Regression Tests
    ------------------------
    Locks in gate count and depth ceilings using values stored in
    benchmark_store.json. These tests fail if a future change causes
    Tessera to produce more gates or deeper circuits than the stored
    baselines.

    The store file is updated by `python benchmarks/benchmarks.py --write`,
    which only allows tightening ceilings. Use `--allow-loosen` to deliberately
    accept a regression on one metric in exchange for a tightening on another.

    Simulation correctness is verified for all four circuits.

    Run with:
        pytest Tessera/benchmarks/regression_tests.py
'''
import sys
import os
import json
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tessera.api.transpile import transpile as tessera_transpile

pi = np.pi
SHOTS = 4096
SIM_TOLERANCE = 0.05

STORE_PATH = os.path.join(os.path.dirname(__file__), 'benchmark_store.json')

if not os.path.exists(STORE_PATH):
    raise RuntimeError(
        f"benchmark_store.json not found at {STORE_PATH}. "
        f"Run `python benchmarks/benchmarks.py --write` to bootstrap it."
    )

with open(STORE_PATH) as f:
    STORE = json.load(f)

# ── Helpers ───────────────────────────────────────────────────────────────────

def simulate(circuit, shots=SHOTS):
    sim = AerSimulator()
    job = sim.run(circuit, shots=shots)
    counts = job.result().get_counts()
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()}

def distributions_match(dist1, dist2, tolerance=SIM_TOLERANCE):
    all_keys = set(dist1.keys()) | set(dist2.keys())
    for key in all_keys:
        if abs(dist1.get(key, 0) - dist2.get(key, 0)) > tolerance:
            return False
    return True

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
        qc.rz(pi / (2 ** i), i)
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

# ── Bell State ────────────────────────────────────────────────────────────────

def test_bell_state_gate_count():
    result = tessera_transpile(make_bell_state())
    assert len(result.data) <= STORE["Bell State"]["max_gates"]

def test_bell_state_depth():
    result = tessera_transpile(make_bell_state())
    assert result.depth() <= STORE["Bell State"]["max_depth"]

def test_bell_state_simulation():
    original = make_bell_state()
    result = tessera_transpile(original)
    assert distributions_match(simulate(original), simulate(result))

# ── GHZ State ─────────────────────────────────────────────────────────────────

def test_ghz_state_gate_count():
    result = tessera_transpile(make_ghz_state())
    assert len(result.data) <= STORE["GHZ State"]["max_gates"]

def test_ghz_state_depth():
    result = tessera_transpile(make_ghz_state())
    assert result.depth() <= STORE["GHZ State"]["max_depth"]

def test_ghz_state_simulation():
    original = make_ghz_state()
    result = tessera_transpile(original)
    assert distributions_match(simulate(original), simulate(result))

# ── QFT-like ──────────────────────────────────────────────────────────────────

def test_qft_like_gate_count():
    result = tessera_transpile(make_qft_like())
    assert len(result.data) <= STORE["QFT-like"]["max_gates"]

def test_qft_like_depth():
    result = tessera_transpile(make_qft_like())
    assert result.depth() <= STORE["QFT-like"]["max_depth"]

def test_qft_like_simulation():
    original = make_qft_like()
    result = tessera_transpile(original)
    assert distributions_match(simulate(original), simulate(result))

# ── Stress Test ───────────────────────────────────────────────────────────────

def test_stress_test_gate_count():
    result = tessera_transpile(make_stress_test())
    assert len(result.data) <= STORE["Stress Test"]["max_gates"]

def test_stress_test_depth():
    result = tessera_transpile(make_stress_test())
    assert result.depth() <= STORE["Stress Test"]["max_depth"]

def test_stress_test_simulation():
    original = make_stress_test()
    result = tessera_transpile(original)
    assert distributions_match(simulate(original), simulate(result))
