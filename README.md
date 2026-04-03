# Tessera
A lightweight, modular quantum circuit transpiler built in Python. Tessera is designed as a minimal but functional alternative to Qiskit's built-in transpiler, with a focus on simplicity, readability, and iterability.

Tessera takes a logical quantum circuit and transforms it into one that can run on a specific backend by running it through a sequential pipeline of transformation passes.

---

## Project Structure

```
Tessera/
├── circuit.py              # TesseraCircuit — core circuit data structure
├── instruction.py          # TesseraInstruction — single gate application
├── converters.py           # Converts between Qiskit and Tessera formats
├── gate_library.py         # Maps gate name strings to Qiskit gate objects
├── transpiler_pass.py      # Abstract base class for all transpiler passes
├── pass_manager.py         # Runs a sequential pipeline of passes
├── passes/
│   └── identity_pass.py    # No-op pass for smoke testing
└── tests/
    ├── TEST.md             # Test suite documentation
    ├── __init__.py
    ├── test_circuit.py
    ├── test_instruction.py
    ├── test_converters.py
    ├── test_pass_manager.py
    └── test_identity_pass.py
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
```bash
pip install qiskit pytest pytest-cov
```

### Basic Usage
```python
from qiskit import QuantumCircuit
from converters import from_qiskit, to_qiskit
from pass_manager import TesseraPassManager
from passes.identity_pass import IdentityPass

# Build a Qiskit circuit
qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 2)
qc.measure([0, 1, 2], [0, 1, 2])

# Convert to Tessera IR
tessera_circuit = from_qiskit(qc)

# Run through the pass pipeline
manager = TesseraPassManager([IdentityPass()])
result = manager.run(tessera_circuit)

# Convert back to Qiskit
output = to_qiskit(result)
print(output)
```

### Running Tests
```bash
pytest Tessera/tests/ --cov=. --cov-report=term-missing
```

See `tests/TEST.md` for full test suite documentation.

---

## Transpiler Pipeline

The full transpiler pipeline Tessera is being built toward, in order:

| Stage | Pass | Status | Description |
|-------|------|--------|-------------|
| 1 | Basis Translation | 🔜 Planned | Decompose gates into a target basis set |
| 2 | Layout | 🔜 Planned | Map logical qubits to physical qubits |
| 3 | Routing | 🔜 Planned | Insert SWAPs to satisfy coupling map constraints |
| 4 | Optimization | 🔜 Planned | Cancel redundant gates, merge rotations |

---

## Supported Gates

Tessera currently supports the following gates in its gate library:

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

3. Add it to your `TesseraPassManager` pipeline
4. Add a corresponding `tests/test_my_pass.py`

---

## Roadmap

- [x] Core IR (`TesseraCircuit`, `TesseraInstruction`)
- [x] Qiskit converter (round-trip)
- [x] Pass infrastructure (`TranspilerPass`, `TesseraPassManager`)
- [x] Test suite with coverage reporting
- [ ] Basis translation pass
- [ ] Coupling map representation
- [ ] Qubit layout pass
- [ ] SWAP routing pass
- [ ] Gate cancellation optimization pass
- [ ] Rotation merging optimization pass
- [ ] Noise-aware layout
- [ ] Full `transpile(circuit, backend)` entry point