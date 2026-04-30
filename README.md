# Tessera
A lightweight, modular quantum circuit transpiler built in Python. Tessera is designed as a minimal but functional alternative to Qiskit's built-in transpiler, with a focus on simplicity, readability, and iterability.

Tessera takes a logical quantum circuit and transforms it into one that can run on a specific backend by running it through a sequential pipeline of transformation passes.

---

## Project Structure

```
Tessera/
├── api/
│   └── transpile.py            # Top-level transpile() entry point
├── backends/
│   ├── backend_registry.py     # Maps backend names to gate sets and coupling maps
│   ├── basis_gate_sets.py      # Supported gate sets per backend
│   ├── decomposition_maps.py   # Gate decomposition sequences per backend
│   └── coupling_maps.py        # Real hardware coupling maps from Qiskit fake providers
├── hardware/
│   └── coupling_map.py         # TesseraCouplingMap — directed graph over networkx
├── passes/
│   ├── basis_translation_pass.py
│   ├── dense_layout_pass.py
│   ├── basic_swap_router.py
│   ├── remove_barriers_pass.py
│   ├── cancel_adjacent_pass.py
│   ├── merge_rotations_pass.py
│   ├── trivial_pass.py
│   └── identity_pass.py
├── benchmarks/
│   ├── benchmarks.py           # Tessera vs Qiskit comparison script
│   ├── regression_tests.py     # Pytest regression tests locked to benchmark baselines
│   └── benchmark.md            # Historical benchmark results and known issues
├── tests/                      # Full pytest suite (100% coverage target)
├── circuit.py                  # TesseraCircuit dataclass
├── instruction.py              # TesseraInstruction dataclass
├── converters.py               # from_qiskit() and to_qiskit()
├── gate_library.py             # Gate name to Qiskit gate object mapping
├── transpiler.py               # TesseraTranspiler class
├── transpiler_pass.py          # Abstract base class for all passes
├── pass_manager.py             # Sequential pass pipeline runner
└── test.py                     # Manual end-to-end sanity test script
```

---

## Core Concepts

### Intermediate Representation (IR)
Tessera uses its own internal circuit representation that is independent of Qiskit. This means passes can be written, tested, and reasoned about without any knowledge of Qiskit internals.

- **`TesseraInstruction`** — holds a gate name, the qubits it acts on, any classical bits, and any parameters (e.g. rotation angles)
- **`TesseraCircuit`** — an ordered list of `TesseraInstruction` objects plus qubit and classical bit counts

### Passes
A pass is a single transformation step on a circuit. Each pass takes a `TesseraCircuit` in and returns a `TesseraCircuit` out. Passes are intentionally kept small and single-purpose so they are easy to test, swap out, and reorder.

### PassManager
The `TesseraPassManager` chains passes together sequentially. Each pass receives the output of the previous one. Optional `before` and `after` hooks can be passed to `run()` for logging or debugging.

```python
manager = TesseraPassManager([PassA(), PassB(), PassC()])
result = manager.run(circuit)
```

---

## Getting Started

### Requirements
Install runtime dependencies:
```bash
pip install -r requirements.txt
```

To also run the test suite and benchmarks:
```bash
pip install -r requirements-dev.txt
```

### Quick Start
```python
from qiskit import QuantumCircuit
from api.transpile import transpile

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

transpiled = transpile(qc, backend="IBM")
print(transpiled)
```

### Advanced Usage
```python
from qiskit import QuantumCircuit
from api.transpile import transpile
from hardware.coupling_map import TesseraCouplingMap

# Custom coupling map
cm = TesseraCouplingMap(3, [(0, 1), (1, 0), (1, 2), (2, 1)])

transpiled = transpile(
    qc,
    backend="IBM",
    coupling_map=cm,       # or pass a string key like "IBM_BRISBANE"
    strict=False,          # use commutative optimization mode
    epsilon=1e-6,          # custom rotation merge threshold
    debug_on=True          # print per-pass gate counts
)
```

---

## Transpiler Pipeline

```
BasisTranslation -> DenseLayout -> BasicSwapRouter -> RemoveBarriers -> CancelAdjacent -> MergeRotations
```

| Stage | Pass | Description |
|-------|------|-------------|
| 1 | `BasisTranslationPass` | Decomposes non-basis gates into backend-supported gate set |
| 2 | `DenseLayoutPass` | Greedily maps logical qubits to physical qubits based on interaction frequency |
| 3 | `BasicSwapRouter` | Applies layout and inserts SWAP gates for non-adjacent two-qubit gates |
| 4 | `RemoveBarriersPass` | Strips barrier instructions before optimization |
| 5 | `CancelAdjacentPass` | Removes pairs of adjacent self-inverse gates (X X, H H, CX CX, etc.) |
| 6 | `MergeRotationsPass` | Combines consecutive rotation gates (Rz(a) Rz(b) -> Rz(a+b)) |

---

## Supported Backends

| Backend Key | Device | Qubits | Basis Gates |
|-------------|--------|--------|-------------|
| `IBM` | FakeNairobiV2 (default) | 7 | cx, rz, sx, x, u |

## Supported Coupling Maps

| Key | Device | Qubits |
|-----|--------|--------|
| `IBM_DEFAULT` | FakeNairobiV2 | 7 |
| `IBM_BRISBANE` | FakeBrisbane | 127 |
| `IBM_SHERBROOKE` | FakeSherbrooke | 127 |

---

## Supported Gates

### Single-Qubit (no parameters)
`h` `x` `y` `z` `s` `sdg` `t` `tdg` `sx`

### Single-Qubit (with parameters)
`rx` `ry` `rz` `p` `u`

### Two-Qubit
`cx` `cnot` `cz` `cy` `swap` `cp`

### Three-Qubit
`ccx`

### Measurement
`measure`

---

## Running Tests

```bash
# Full test suite with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Regression tests only
pytest benchmarks/regression_tests.py

# Manual sanity test
python test.py
```

See `tests/TEST.md` for full test suite documentation and coverage targets.

---

## Benchmarks

```bash
python benchmarks/benchmarks.py
```

Compares Tessera against Qiskit's transpiler on gate count, circuit depth, transpile time, and simulation correctness. Results are tracked in `benchmarks/benchmark.md`.

### Run 1 Results (FakeNairobiV2, Qiskit optimization level 1)

| Circuit | Gates In | Gates (Tessera) | Gates (Qiskit) | Depth (Tessera) | Depth (Qiskit) | Sim Match |
|---------|----------|-----------------|----------------|-----------------|----------------|-----------|
| Bell State | 4 | 6 | 6 | 5 | 5 | Yes |
| GHZ State | 6 | 8 | 8 | 6 | 6 | Yes |
| QFT-like | 22 | 29 | 27 | 13 | 11 | Yes |
| Stress Test | 18 | 33 | 35 | 16 | 18 | No* |

*Stress Test simulation mismatch is a known issue — see `benchmarks/benchmark.md`.

---

## Adding a New Pass

1. Create a new file in `passes/` (e.g. `passes/my_pass.py`)
2. Inherit from `TranspilerPass` and implement `run()`

```python
from circuit import TesseraCircuit
from transpiler_pass import TranspilerPass

class MyPass(TranspilerPass):
    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        # transform circuit here
        return circuit
```

3. Add it to the pass list in `transpiler.py`
4. Add a corresponding `tests/test_my_pass.py`

---

## Roadmap

- [x] Core IR (`TesseraCircuit`, `TesseraInstruction`)
- [x] Qiskit converter (round-trip)
- [x] Pass infrastructure (`TranspilerPass`, `TesseraPassManager`)
- [x] Test suite with 100% coverage
- [x] Basis translation pass
- [x] Coupling map representation
- [x] Trivial and dense qubit layout passes
- [x] SWAP routing pass (BFS, pluggable path-finder)
- [x] Gate cancellation optimization pass
- [x] Rotation merging optimization pass
- [x] Barrier removal pass
- [x] Backend registry with real IBM hardware topologies
- [x] Top-level `transpile(circuit, backend)` entry point
- [x] Benchmark suite vs Qiskit
- [x] Regression test suite
- [ ] Commutative gate rewriting (improve CancelAdjacentPass)
- [ ] Multi-pass optimization loop
- [ ] Noise-aware layout
- [ ] Additional backend support
- [ ] Fix Stress Test simulation mismatch (see known issues)
- [ ] SABRE or A* routing algorithm