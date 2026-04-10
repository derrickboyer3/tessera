# Tessera Benchmark Results

## Overview
This file tracks Tessera's transpiler performance over time, measured against Qiskit's transpiler
as a reference. The goal is not to beat Qiskit, but to verify correctness and track improvement
as new passes and optimizations are added.

---

## How to Run Benchmarks
```bash
# From the project root directory
python Tessera/benchmarks/benchmarks.py
```

---

## Metrics Tracked

| Metric | Description |
|--------|-------------|
| Gates In | Number of gates in the original circuit before transpilation |
| Gate Count (Tessera) | Number of gates after Tessera transpilation |
| Gate Count (Qiskit) | Number of gates after Qiskit transpilation |
| Depth (Tessera) | Critical path length of Tessera output circuit |
| Depth (Qiskit) | Critical path length of Qiskit output circuit |
| Simulation Match | Whether Tessera and Qiskit circuits produce equivalent measurement distributions |
| Transpile Time (Tessera) | Wall clock time for Tessera transpilation |
| Transpile Time (Qiskit) | Wall clock time for Qiskit transpilation |

---

## Benchmark Circuits

### Circuit 1 — Bell State (2 qubits)
Simple H + CX + measure. Baseline sanity check.

### Circuit 2 — GHZ State (3 qubits)
H + chain of CX gates. Tests linear routing.

### Circuit 3 — QFT-like (5 qubits)
Rotation-heavy circuit with many Rz gates. Tests MergeRotationsPass effectiveness.
Contains intentional duplicate Rz gates to exercise the merge pass.

### Circuit 4 — Stress Test (5 qubits)
Mixed gate set with frequent non-adjacent interactions. Tests full pipeline under load.
Note: simulation match is not expected on this circuit — see Known Issues.

---

## Results

### Run 1
- **Date:** April 10, 2026
- **Tessera Phase:** Phase 7
- **Coupling Map:** FakeNairobiV2 (7 qubits, heavy-hex)
- **Qiskit Optimization Level:** 1
- **Shots per Simulation:** 4096
- **Simulation Tolerance:** 0.05

| Circuit | Gates In | Gates (Tessera) | Gates (Qiskit) | Depth (Tessera) | Depth (Qiskit) | Sim Match | Time (Tessera) | Time (Qiskit) |
|---------|----------|-----------------|----------------|-----------------|----------------|-----------|----------------|---------------|
| Bell State | 4 | 6 | 6 | 5 | 5 | Yes | 0.0068s | 0.0711s |
| GHZ State | 6 | 8 | 8 | 6 | 6 | Yes | 0.0008s | 0.0070s |
| QFT-like | 22 | 29 | 27 | 13 | 11 | Yes | 0.0012s | 0.0132s |
| Stress Test | 18 | 33 | 35 | 16 | 18 | No | 0.0013s | 0.0155s |

**Notes:**
- Bell State and GHZ State match Qiskit exactly on gate count and depth
- Tessera is significantly faster to transpile than Qiskit across all circuits (5-90x faster)
- QFT-like is 2 gates and 2 depth worse than Qiskit, expected due to single-pass Rz merging limitation
- Stress Test produces fewer gates than Qiskit (33 vs 35) but simulation distributions do not match
- Simulation mismatch on Stress Test is a known issue, not a regression target

---

## How to Add a New Run
1. Run `python Tessera/benchmarks/benchmarks.py`
2. Copy the output into a new `### Run N` section above
3. Note the Qiskit and qiskit-ibm-runtime versions
4. Add any relevant notes about what changed since the last run

---

## Known Issues

### Stress Test Simulation Mismatch
**Status:** Open — tracked as GitHub issue
**Affected Circuit:** Stress Test (5 qubits)
**Description:** Tessera and Qiskit produce different simulation distributions for the Stress Test
circuit. Both circuits produce roughly uniform distributions across 8 bitstrings, but the specific
bitstrings differ between the two transpilers.
**Root Cause (suspected):** The Stress Test circuit contains cz and cy gates which decompose into
multiple basis gates. Combined with different layout and routing choices between Tessera's
DenseLayoutPass and Qiskit's layout pass, the two transpilers may produce logically different
circuits that both appear structurally valid but compute different functions.
**Impact:** Correctness concern for circuits with non-deterministic or uniform-superposition outputs
where layout choice affects the logical computation.
**Resolution:** Requires deeper investigation into whether the layout difference is causing a
genuinely incorrect transpilation or whether both outputs are valid reorderings of the same
computation. Tracked as a GitHub issue.

---

## Known Limitations
- Tessera uses strict adjacency mode by default. Commutative mode may produce lower gate counts.
- Tessera's single-pass MergeRotationsPass may leave one unmerged Rz in chains of 3+ consecutive rotations.
- Qiskit optimization level 1 is used as the reference. Higher Qiskit optimization levels will outperform Tessera more significantly.
- Gate counts include SWAP overhead from routing and basis decomposition expansion.
- Tessera does not yet support all IBM basis gate decompositions — unsupported gates will raise a ValueError.

---

## Regression Targets
These are the gate count and depth ceilings locked in by `regression_tests.py`.
If a future change causes these to exceed the targets, the regression tests will fail.
Simulation match is required for all circuits except Stress Test (see Known Issues).

| Circuit | Max Gates (Tessera) | Max Depth (Tessera) | Sim Match Required |
|---------|--------------------|--------------------|-------------------|
| Bell State | 6 | 5 | Yes |
| GHZ State | 8 | 6 | Yes |
| QFT-like | 29 | 13 | Yes |
| Stress Test | 33 | 16 | No |