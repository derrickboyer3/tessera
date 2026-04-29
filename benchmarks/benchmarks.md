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

# Update benchmark_store.json with this run's numbers (refuses if any metric
# regressed against the stored ceiling, or if any simulation mismatched Qiskit)
python Tessera/benchmarks/benchmarks.py --write

# Update benchmark_store.json even if some metrics regressed. Best-seen
# watermarks (best_max_*) are still preserved as monotonic minimums.
python Tessera/benchmarks/benchmarks.py --allow-loosen
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
Exercises the SWAP router on logical qubits that the layout pass cannot pack
adjacent — historically caught a routing/measurement bug (now resolved, see
Resolved Issues).

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
- Simulation mismatch on Stress Test was a known issue at the time of this run — see Resolved Issues for the post-fix state in Run 2

### Run 2
- **Date:** 2026-04-29
- **Tessera Phase:** Post-Phase-7 (BasicSwapRouter measurement-after-SWAP fix)
- **Coupling Map:** FakeNairobiV2 (7 qubits, heavy-hex)
- **Qiskit Optimization Level:** 1
- **Shots per Simulation:** 4096
- **Simulation Tolerance:** 0.05

| Circuit | Gates In | Gates (Tessera) | Gates (Qiskit) | Depth (Tessera) | Depth (Qiskit) | Sim Match | Time (Tessera) | Time (Qiskit) |
|---------|----------|-----------------|----------------|-----------------|----------------|-----------|----------------|---------------|
| Bell State | 4 | 6 | 6 | 5 | 5 | Yes | 0.0012s | 0.0436s |
| GHZ State | 6 | 8 | 8 | 6 | 6 | Yes | 0.0008s | 0.0065s |
| QFT-like | 22 | 29 | 27 | 13 | 11 | Yes | 0.0013s | 0.0064s |
| Stress Test | 18 | 33 | 35 | 16 | 18 | Yes | 0.0012s | 0.0092s |

**Notes:**
- Stress Test simulation now matches Qiskit — the routing/measurement bug from Run 1 is resolved
- Gate count and depth are unchanged from Run 1 across all four circuits, confirming the fix corrected only the measurement targets and post-SWAP gate qubit indices, not the structural routing decisions
- All four circuits now meet the simulation-correctness floor

---

## How to Add a New Run
1. Run `python Tessera/benchmarks/benchmarks.py` (no flags) and copy the printed numbers into a new `### Run N` section above
2. Note the Qiskit and qiskit-ibm-runtime versions
3. Add any relevant notes about what changed since the last run
4. If this run improved on the stored ceilings, also run `python Tessera/benchmarks/benchmarks.py --write` to ratchet `benchmark_store.json`. Use `--allow-loosen` instead if you intentionally accepted a regression on one metric in exchange for tightening another

---

## Resolved Issues

### Stress Test Simulation Mismatch — RESOLVED 2026-04-29
**Branch:** `issue/stress-test-simulation-mismatch`
**Affected Circuit:** Stress Test (5 qubits)
**Original Hypothesis (incorrect):** cz and cy gates decompose into multiple basis gates, and layout/routing differences between Tessera and Qiskit produce logically divergent circuits. The cz/cy decompositions were verified mathematically and turned out to be correct (modulo global phase, which doesn't affect measurement).
**Actual Root Cause:** `BasicSwapRouter` had a two-step structure: Step 1 pre-remapped every instruction's qubit indices to physical addresses using the initial layout, then Step 2 inserted SWAPs along BFS paths and updated `current_positions` / `inverse_positions` tracking dicts — but those tracking dicts were never used to retranslate subsequent instructions in the pre-remapped list. After any SWAP, follow-up gates and measurements still pointed at stale physical addresses.

For the Stress Test specifically, logical qubit 2 was placed late by DenseLayoutPass (only two single-count interactions), and the trailing `cx(2,0)` and `cx(2,4)` triggered SWAPs that moved logical 2 away from its initial physical address. The measurement of logical 2 still pointed at the original physical-2 location, which was now an unused qubit (constant 0). This caused four of the eight expected bitstrings to map to wrong outputs (those where logical q2 should have measured 1).

**Fix:** Replaced the two-step structure with a single-pass router. For each instruction we translate its logical qubits to physical addresses at iteration time using `current_positions`, which is mutated whenever a SWAP is inserted. All subsequent instructions — including measurements — now see the up-to-date mapping. The SWAP bookkeeping was already correct; it just wasn't being consulted.

**Verification:** Stress Test simulation now matches Qiskit. Gate count and depth are unchanged from Run 1, confirming the fix corrected only the qubit indices on measurements and post-SWAP gates, not the structural routing decisions.

---

## Known Limitations
- Tessera uses strict adjacency mode by default. Commutative mode may produce lower gate counts.
- Tessera's single-pass MergeRotationsPass may leave one unmerged Rz in chains of 3+ consecutive rotations.
- Qiskit optimization level 1 is used as the reference. Higher Qiskit optimization levels will outperform Tessera more significantly.
- Gate counts include SWAP overhead from routing and basis decomposition expansion.
- Tessera does not yet support all IBM basis gate decompositions — unsupported gates will raise a ValueError.

---

## Regression Targets

The authoritative gate count and depth ceilings live in `benchmark_store.json`,
next to `regression_tests.py`. The regression test suite reads from that file
and fails any test whose metric exceeds its stored ceiling. The table below
mirrors the current state of the store.

To update ceilings after improving Tessera, run benchmarks with one of the
write flags:

- `--write` ratchets ceilings monotonically downward and refuses to write if
  any metric on any circuit regressed against its current ceiling, or if any
  simulation distribution mismatched Qiskit.
- `--allow-loosen` accepts an intentional tradeoff (e.g., gate count down,
  depth up) and writes the new ceilings even if some metrics regressed. The
  `best_max_*` watermarks are still preserved as monotonic minimums so the
  prior best is never lost.

Simulation match is required for all four circuits as a correctness floor,
not a moving ceiling.

| Circuit | Max Gates | Best Max Gates | Max Depth | Best Max Depth | Sim Match Required |
|---------|-----------|----------------|-----------|----------------|-------------------|
| Bell State | 6 | 6 | 5 | 5 | Yes |
| GHZ State | 8 | 8 | 6 | 6 | Yes |
| QFT-like | 29 | 29 | 13 | 13 | Yes |
| Stress Test | 33 | 33 | 16 | 16 | Yes |