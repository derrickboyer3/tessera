'''
    Tessera Regression Tests
    ------------------------
    Locks in gate count and depth ceilings based on Run 1 benchmark results.
    These tests fail if a future change causes Tessera to produce more gates
    or deeper circuits than the established baselines.

    Simulation correctness is also verified for circuits where the output
    is deterministic or well-understood (Bell State, GHZ State, QFT-like).
    Stress Test simulation match is excluded — see benchmark.md Known Issues.

    Run with:
        pytest Tessera/benchmarks/regression_tests.py
'''
import sys
import os
import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.transpile import transpile as tessera_transpile

pi = np.pi
SHOTS = 4096
SIM_TOLERANCE = 0.05

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
    assert len(result.data) <= 6

def test_bell_state_depth():
    result = tessera_transpile(make_bell_state())
    assert result.depth() <= 5

def test_bell_state_simulation():
    original = make_bell_state()
    result = tessera_transpile(original)
    original_dist = simulate(original)
    result_dist = simulate(result)
    assert distributions_match(original_dist, result_dist)

# ── GHZ State ─────────────────────────────────────────────────────────────────

def test_ghz_state_gate_count():
    result = tessera_transpile(make_ghz_state())
    assert len(result.data) <= 8

def test_ghz_state_depth():
    result = tessera_transpile(make_ghz_state())
    assert result.depth() <= 6

def test_ghz_state_simulation():
    original = make_ghz_state()
    result = tessera_transpile(original)
    original_dist = simulate(original)
    result_dist = simulate(result)
    assert distributions_match(original_dist, result_dist)

# ── QFT-like ──────────────────────────────────────────────────────────────────

def test_qft_like_gate_count():
    result = tessera_transpile(make_qft_like())
    assert len(result.data) <= 29

def test_qft_like_depth():
    result = tessera_transpile(make_qft_like())
    assert result.depth() <= 13

def test_qft_like_simulation():
    original = make_qft_like()
    result = tessera_transpile(original)
    original_dist = simulate(original)
    result_dist = simulate(result)
    assert distributions_match(original_dist, result_dist)

# ── Stress Test ───────────────────────────────────────────────────────────────

def test_stress_test_gate_count():
    result = tessera_transpile(make_stress_test())
    assert len(result.data) <= 33

def test_stress_test_depth():
    result = tessera_transpile(make_stress_test())
    assert result.depth() <= 16

# Note: simulation match intentionally excluded for Stress Test
# See benchmark.md Known Issues for details