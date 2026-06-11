'''
    Tessera Manual Sanity Test
    --------------------------
    A script that runs through all major Tessera components to verify correct output
    from traditional usage. This is not a PyTest file — it is a manual integration
    test that exercises the full transpiler pipeline end to end.

    Update and add new sections as new features are added to Tessera.

    Sections:
        1. Converter Tests         — from_qiskit() and to_qiskit()
        2. Pass Manager Test       — IdentityPass through TesseraPassManager
        3. Basis Translation Test  — Full gate set through BasisTranslationPass
        4. Layout Pass Test        — TrivialPass vs DenseLayoutPass comparison
        5. Swap Router Test        — BasicSwapRouter on non-adjacent circuit
        6. Full Pipeline Test      — End to end through TesseraTranspiler
        7. Optimization Passes Test — CancelAdjacentPass, MergeRotationsPass, RemoveBarriersPass
        8. Top-Level Transpile API Test — transpile() function, coupling map resolution, error handling
        9. IonQ Backend Test — IonQ basis, all-to-all coupling, coupling map override
       10. Rigetti Backend Test — Rigetti basis, CX-via-CZ decomposition, coupling map override
       11. Commutative Mode Deep Dive — strict vs commutative on a tangled multi-qubit circuit
       12. Optimization Loop Test — iterations=1 vs N vs -1 (convergence) on a circuit that chains optimizations
        *. Full Optimization Comparison — Tessera at max vs Qiskit at optimization_level=3 (always last; curiosity-only)
'''
import numpy as np
import time
from qiskit import QuantumCircuit
from tessera.converters import from_qiskit, to_qiskit
from tessera.pass_manager import TesseraPassManager
from tessera.passes.identity_pass import IdentityPass
from tessera.passes.dense_layout_pass import DenseLayoutPass
from tessera.passes.trivial_pass import TrivialPass
from tessera.passes.basic_swap_router import BasicSwapRouter
from tessera.transpiler import TesseraTranspiler
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction

pi = np.pi

def log_before(pass_, circuit):
    print(f"  [Tessera] Running pass: {pass_.name} | Gates: {len(circuit.instructions)}")

def log_after(pass_, circuit):
    print(f"  [Tessera] Finished pass: {pass_.name} | Gates: {len(circuit.instructions)}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

print("Imports done.")

# =============================================================
# 1. CONVERTER TESTS
# =============================================================
section("1. Converter Tests")

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

tessera_circuit = from_qiskit(qc)
print(f"  from_qiskit() -> {tessera_circuit.num_qubits} qubits, {len(tessera_circuit.instructions)} instructions")

qiskit_circuit = to_qiskit(tessera_circuit)
print(f"  to_qiskit() -> {qiskit_circuit.num_qubits} qubits, {len(qiskit_circuit.data)} instructions")
print("  OK")

# =============================================================
# 2. PASS MANAGER TEST
# =============================================================
section("2. Pass Manager Test")

manager = TesseraPassManager([IdentityPass()])
result = manager.run(tessera_circuit, before=log_before, after=log_after)
print(f"  Circuit unchanged after IdentityPass: {result == tessera_circuit}")
print("  OK")

# =============================================================
# 3. BASIS TRANSLATION TEST
# =============================================================
section("3. Basis Translation Test")

qc_full = QuantumCircuit(4, 4)
qc_full.h(0)
qc_full.x(1)
qc_full.y(2)
qc_full.z(3)
qc_full.s(0)
qc_full.sdg(1)
qc_full.t(2)
qc_full.tdg(3)
qc_full.sx(0)
qc_full.rx(pi / 3, 1)
qc_full.ry(pi / 4, 2)
qc_full.rz(pi / 6, 3)
qc_full.p(pi / 2, 0)
qc_full.cx(0, 1)
qc_full.cz(1, 2)
qc_full.cy(2, 3)
qc_full.swap(0, 3)
qc_full.cp(pi / 4, 0, 1)
qc_full.ccx(0, 1, 2)
qc_full.measure([0, 1, 2, 3], [0, 1, 2, 3])

tessera_full = from_qiskit(qc_full)
print(f"  Input:  {len(tessera_full.instructions)} gates")

cm_full = TesseraCouplingMap(4, [(0,1), (1,2), (2,3), (3,0)])
transpiler = TesseraTranspiler(qc_full, cm_full, backend="IBM", debug_on=True)
start = time.perf_counter()
translated = transpiler.execute()
elapsed = time.perf_counter() - start
print(f"  Output: {len(translated.data)} gates")
print(f"  Time:   {elapsed:.4f}s")
print("  OK")

# =============================================================
# 4. LAYOUT PASS TEST
# =============================================================
section("4. Layout Pass Test")

layout_circuit = TesseraCircuit(3, 0, [
    TesseraInstruction("cx", [0, 2], [], []),
    TesseraInstruction("cx", [0, 2], [], []),
    TesseraInstruction("cx", [0, 2], [], []),
    TesseraInstruction("cx", [0, 1], [], []),
])
cm_layout = TesseraCouplingMap(5, [(0,1), (1,2), (2,3), (3,4)])

trivial_result = TrivialPass(cm_layout).run(layout_circuit)
dense_result = DenseLayoutPass(cm_layout).run(layout_circuit)

print(f"  Trivial Layout: {trivial_result.layout}")
print(f"  Dense Layout:   {dense_result.layout}")
print(f"  q0 and q2 distance (trivial): {cm_layout.distance(trivial_result.layout[0], trivial_result.layout[2])}")
print(f"  q0 and q2 distance (dense):   {cm_layout.distance(dense_result.layout[0], dense_result.layout[2])}")
print("  OK")

# =============================================================
# 5. SWAP ROUTER TEST
# =============================================================
section("5. Swap Router Test")

router_circuit = TesseraCircuit(3, 0, [
    TesseraInstruction("cx", [0, 2], [], []),
], layout={0: 0, 1: 1, 2: 2})
cm_router = TesseraCouplingMap(4, [(0,1), (1,2), (2,3)])

routed = BasicSwapRouter(cm_router).run(router_circuit)
print("  Input:  cx(q0, q2) — q0 at p0, q2 at p2, not adjacent")
print("  Output:")
for ins in routed.instructions:
    print(f"    {ins.name} {ins.qubits}")
print("  OK")

# =============================================================
# 6. FULL PIPELINE TEST
# =============================================================
section("6. Full Pipeline Test")

# 5-qubit circuit designed to stress all three passes:
# - Many non-basis gates force BasisTranslationPass to work hard
# - Frequent interactions between specific pairs force DenseLayoutPass
#   to produce a non-trivial layout
# - Non-adjacent gates after layout force BasicSwapRouter to insert swaps
qc_pipeline = QuantumCircuit(5, 5)

# Single qubit gates
qc_pipeline.h(0)
qc_pipeline.h(1)
qc_pipeline.h(2)
qc_pipeline.t(3)
qc_pipeline.s(4)

# q0 and q4 interact frequently — DenseLayout should place them close
qc_pipeline.cx(0, 4)
qc_pipeline.cz(0, 4)
qc_pipeline.cx(0, 4)
qc_pipeline.swap(0, 4)

# q1 and q3 interact frequently
qc_pipeline.cx(1, 3)
qc_pipeline.cy(1, 3)
qc_pipeline.cx(1, 3)

# q2 interacts with everyone — forces swap insertion
qc_pipeline.cx(2, 0)
qc_pipeline.cx(2, 4)
qc_pipeline.ccx(0, 1, 2)

qc_pipeline.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])

# Linear 5-qubit coupling map — deliberately restrictive to force swaps
# 0->1->2->3->4 with bidirectional edges
cm_pipeline = TesseraCouplingMap(5, [
    (0,1), (1,0),
    (1,2), (2,1),
    (2,3), (3,2),
    (3,4), (4,3)
])

print(f"  Input: {qc_pipeline.num_qubits} qubits, {len(qc_pipeline.data)} gates")
print(f"  Initial Circuit:\n{qc_pipeline}")

transpiler = TesseraTranspiler(qc_pipeline, cm_pipeline, backend="IBM", debug_on=True)
start = time.perf_counter()
final = transpiler.execute()
elapsed = time.perf_counter() - start

# Show layout that DenseLayoutPass chose
tes = from_qiskit(qc_pipeline)
from tessera.passes.dense_layout_pass import DenseLayoutPass
layout = DenseLayoutPass(cm_pipeline).run(tes).layout
print(f"\n  Dense Layout chosen: {layout}")
print(f"  (q0 and q4 should be close — they interact 4 times)")
print(f"  q0<->q4 distance: {cm_pipeline.distance(layout[0], layout[4])}")
print(f"  q1<->q3 distance: {cm_pipeline.distance(layout[1], layout[3])}")

print(f"\n  Output: {len(final.data)} gates (includes basis decomposition + swaps)")
print(f"  Final circuit:\n{final}")
print(f"\n  Time: {elapsed:.4f}s")
print("  OK")

# =============================================================
# 7. OPTIMIZATION PASSES TEST
# =============================================================
section("7. Optimization Passes Test")

qc_opt = QuantumCircuit(3, 3)
qc_opt.h(0)
qc_opt.h(0)
qc_opt.x(1)
qc_opt.x(1)
qc_opt.rz(pi / 4, 2)
qc_opt.rz(pi / 4, 2)
qc_opt.barrier()
qc_opt.cx(0, 1)
qc_opt.measure([0, 1, 2], [0, 1, 2])

cm_opt = TesseraCouplingMap(3, [(0,1), (1,0), (1,2), (2,1)])

print(f"  Input:  {len(qc_opt.data)} gates (includes cancellable pairs, mergeable rotations, and a barrier)")
print(f"  Input circuit:\n{qc_opt}")

transpiler_opt = TesseraTranspiler(qc_opt, cm_opt, backend="IBM", debug_on=True)
start = time.perf_counter()
result_opt = transpiler_opt.execute()
elapsed = time.perf_counter() - start

gate_names = [ins.operation.name for ins in result_opt.data]
print(f"  Output: {len(result_opt.data)} gates")
print(f"  Output circuit:\n{result_opt}")
print(f"  Gates:  {gate_names}")
print(f"  Barriers removed: {'barrier' not in gate_names}")
print(f"  Gate count reduced: {len(result_opt.data) < len(qc_opt.data)}")
print(f"  Time: {elapsed:.4f}s")
print("  OK")

# Commutative mode
qc_commutative = QuantumCircuit(2, 2)
qc_commutative.x(0)
qc_commutative.rz(pi / 4, 1)
qc_commutative.x(0)
qc_commutative.rz(pi / 4, 1)
qc_commutative.measure([0, 1], [0, 1])

cm_commutative = TesseraCouplingMap(2, [(0,1), (1,0)])

print(f"\n  Commutative mode input: {len(qc_commutative.data)} gates")
print(f"  Input circuit:\n{qc_commutative}")

transpiler_commutative = TesseraTranspiler(qc_commutative, cm_commutative, backend="IBM", strict=False, debug_on=True)
start = time.perf_counter()
result_commutative = transpiler_commutative.execute()
elapsed = time.perf_counter() - start

print(f"  Output: {len(result_commutative.data)} gates")
print(f"  Output circuit:\n{result_commutative}")
print(f"  Gate count reduced: {len(result_commutative.data) < len(qc_commutative.data)}")
print(f"  Time: {elapsed:.4f}s")

# Custom epsilon
qc_epsilon = QuantumCircuit(1, 1)
qc_epsilon.rz(0.005, 0)
qc_epsilon.rz(-0.005, 0)
qc_epsilon.measure(0, 0)

cm_epsilon = TesseraCouplingMap(1, [])

print(f"\n  Custom epsilon input: {len(qc_epsilon.data)} gates")
print(f"  Input circuit:\n{qc_epsilon}")

transpiler_epsilon = TesseraTranspiler(qc_epsilon, cm_epsilon, backend="IBM", epsilon=0.1, debug_on=True)
start = time.perf_counter()
result_epsilon = transpiler_epsilon.execute()
elapsed = time.perf_counter() - start

gate_names_epsilon = [ins.operation.name for ins in result_epsilon.data]
print(f"  Output: {len(result_epsilon.data)} gates")
print(f"  Output circuit:\n{result_epsilon}")
print(f"  Rz dropped by custom epsilon: {'rz' not in gate_names_epsilon}")
print(f"  Time: {elapsed:.4f}s")
print("  OK")

# =============================================================
# 8. TOP-LEVEL TRANSPILE API TEST
# =============================================================
section("8. Top-Level Transpile API Test")

from tessera.api.transpile import transpile as tessera_transpile

# Default usage — no coupling map, defaults to IBM_DEFAULT (FakeNairobiV2, 7 qubits)
qc_api = QuantumCircuit(3, 3)
qc_api.h(0)
qc_api.cx(0, 1)
qc_api.cx(1, 2)
qc_api.measure([0, 1, 2], [0, 1, 2])

print(f"  Input: {len(qc_api.data)} gates")
print(f"  Input circuit:\n{qc_api}")

start = time.perf_counter()
result_api = tessera_transpile(qc_api, debug_on=True)
elapsed = time.perf_counter() - start

print(f"  Output: {len(result_api.data)} gates")
print(f"  Output circuit qubits: {result_api.num_qubits} (physical qubits used from FakeNairobiV2 topology)")
print(f"  Time: {elapsed:.4f}s")
print("  OK")

# String coupling map key
print(f"\n  Testing with string coupling map key 'IBM_DEFAULT'...")
result_string_key = tessera_transpile(qc_api, coupling_map="IBM_DEFAULT", debug_on=True)
print(f"  Output: {len(result_string_key.data)} gates")
print("  OK")

# Custom TesseraCouplingMap
print(f"\n  Testing with custom TesseraCouplingMap...")
cm_custom = TesseraCouplingMap(3, [(0,1), (1,0), (1,2), (2,1)])
result_custom = tessera_transpile(qc_api, coupling_map=cm_custom, debug_on=True)
print(f"  Output: {len(result_custom.data)} gates")
print("  OK")

# Invalid backend
print(f"\n  Testing invalid backend raises ValueError...")
try:
    tessera_transpile(qc_api, backend="FAKE_BACKEND")
    print("  FAIL — should have raised ValueError")
except ValueError as e:
    print(f"  Correctly raised ValueError: {e}")
print("  OK")

# Circuit too large
print(f"\n  Testing circuit too large raises ValueError...")
qc_large = QuantumCircuit(10, 10)
qc_large.h(0)
qc_large.measure_all()
cm_small = TesseraCouplingMap(2, [(0,1), (1,0)])
try:
    tessera_transpile(qc_large, coupling_map=cm_small)
    print("  FAIL — should have raised ValueError")
except ValueError as e:
    print(f"  Correctly raised ValueError: {e}")
print("  OK")

# =============================================================
# 9. IONQ BACKEND TEST
# =============================================================
section("9. IonQ Backend Test")

qc_ionq = QuantumCircuit(4, 4)
qc_ionq.h(0)
qc_ionq.cx(0, 1)
qc_ionq.cy(1, 2)
qc_ionq.swap(2, 3)
qc_ionq.rz(pi / 4, 0)
qc_ionq.ry(pi / 3, 1)
qc_ionq.ccx(0, 1, 2)
qc_ionq.measure([0, 1, 2, 3], [0, 1, 2, 3])

print(f"  Input: {qc_ionq.num_qubits} qubits, {len(qc_ionq.data)} gates")
print(f"  Input circuit:\n{qc_ionq}")

start = time.perf_counter()
result_ionq = tessera_transpile(qc_ionq, backend="IONQ", debug_on=True)
elapsed = time.perf_counter() - start

ionq_basis = {"rx", "ry", "rz", "cx"}
gate_names_ionq = [ins.operation.name for ins in result_ionq.data if ins.operation.name != "measure"]
print(f"\n  Output: {len(result_ionq.data)} gates")
print(f"  Output gate types: {set(gate_names_ionq)}")
print(f"  All gates in IonQ basis {{rx, ry, rz, cx}}: {all(g in ionq_basis for g in gate_names_ionq)}")
swap_count = sum(1 for g in gate_names_ionq if g == "swap")
print(f"  SWAP gates inserted: {swap_count} (expected 0 — IonQ Aria is all-to-all)")
print(f"  Time: {elapsed:.4f}s")

print(f"\n  Testing IonQ Forte coupling map override (IONQ_FORTE, 36 qubits, all-to-all)...")
start = time.perf_counter()
result_forte = tessera_transpile(qc_ionq, backend="IONQ", coupling_map="IONQ_FORTE", debug_on=True)
elapsed = time.perf_counter() - start
print(f"  Output: {len(result_forte.data)} gates")
print(f"  Time: {elapsed:.4f}s")
print("  OK")

# =============================================================
# 10. RIGETTI BACKEND TEST
# =============================================================
section("10. Rigetti Backend Test")

qc_rigetti = QuantumCircuit(3, 3)
qc_rigetti.h(0)
qc_rigetti.cx(0, 1)
qc_rigetti.ry(pi / 3, 2)
qc_rigetti.cz(1, 2)
qc_rigetti.swap(0, 2)
qc_rigetti.measure([0, 1, 2], [0, 1, 2])

print(f"  Input: {qc_rigetti.num_qubits} qubits, {len(qc_rigetti.data)} gates")
print(f"  Input circuit:\n{qc_rigetti}")

start = time.perf_counter()
result_rigetti = tessera_transpile(qc_rigetti, backend="RIGETTI", coupling_map="RIGETTI_ANKAA_9Q", debug_on=True)
elapsed = time.perf_counter() - start

rigetti_basis = {"rx", "rz", "cz"}
gate_names_rigetti = [ins.operation.name for ins in result_rigetti.data if ins.operation.name != "measure"]
print(f"\n  Output: {len(result_rigetti.data)} gates (Ankaa-9Q-3, 9 qubits)")
print(f"  Output gate types: {set(gate_names_rigetti)}")
print(f"  All gates in Rigetti basis {{rx, rz, cz}}: {all(g in rigetti_basis for g in gate_names_rigetti)}")
print(f"  CX decomposed to CZ-based sequence: {'cx' not in gate_names_rigetti}")
print(f"  Time: {elapsed:.4f}s")

print(f"\n  Testing Rigetti Ankaa-2 default map (RIGETTI_ANKAA, 84 qubits)...")
start = time.perf_counter()
result_ankaa = tessera_transpile(qc_rigetti, backend="RIGETTI", debug_on=True)
elapsed = time.perf_counter() - start
gate_names_ankaa = [ins.operation.name for ins in result_ankaa.data if ins.operation.name != "measure"]
print(f"  Output: {len(result_ankaa.data)} gates")
print(f"  All gates in Rigetti basis: {all(g in rigetti_basis for g in gate_names_ankaa)}")
print(f"  Time: {elapsed:.4f}s")
print("  OK")

# =============================================================
# 11. COMMUTATIVE MODE DEEP DIVE
# =============================================================
section("11. Commutative Mode Deep Dive")

# A tangled circuit where many cancellations and merges are blocked in strict
# mode by interleaved instructions on disjoint qubits — but legal under commutation.
qc_comm = QuantumCircuit(4, 4)
qc_comm.h(0)
qc_comm.x(1)
qc_comm.h(2)
qc_comm.rz(pi / 4, 3)
qc_comm.h(0)               # cancels with h(0) above (commutative only — gates between disjoint from q0)
qc_comm.x(1)               # cancels with x(1) above (commutative only — gates between disjoint from q1)
qc_comm.cx(2, 3)
qc_comm.cx(0, 1)
qc_comm.rz(pi / 8, 2)
qc_comm.x(3)
qc_comm.x(3)               # adjacent — cancels in both modes
qc_comm.rz(pi / 8, 2)      # merges with rz(pi/8, 2) above (commutative only — x(3)x(3) disjoint from q2)
qc_comm.cx(0, 1)           # cancels with cx(0,1) above (commutative only — rz(2), x(3)x(3) disjoint from q0/q1)
qc_comm.h(3)
qc_comm.h(3)               # adjacent — cancels in both modes
qc_comm.measure([0, 1, 2, 3], [0, 1, 2, 3])

cm_comm = TesseraCouplingMap(4, [(0,1),(1,0),(1,2),(2,1),(2,3),(3,2)])

print(f"  Input: {len(qc_comm.data)} gates")
print(f"  Input circuit:\n{qc_comm}")

print(f"\n  --- Strict mode (strict=True) ---")
start = time.perf_counter()
result_strict = tessera_transpile(qc_comm, coupling_map=cm_comm, strict=True, debug_on=True)
elapsed_strict = time.perf_counter() - start
print(f"  Output: {len(result_strict.data)} gates | Time: {elapsed_strict:.4f}s")

print(f"\n  --- Commutative mode (strict=False) ---")
start = time.perf_counter()
result_comm = tessera_transpile(qc_comm, coupling_map=cm_comm, strict=False, debug_on=True)
elapsed_comm = time.perf_counter() - start
print(f"  Output: {len(result_comm.data)} gates | Time: {elapsed_comm:.4f}s")

print(f"\n  Strict output gates:      {len(result_strict.data)}")
print(f"  Commutative output gates: {len(result_comm.data)}")
print(f"  Reduction from commutation: {len(result_strict.data) - len(result_comm.data)} gates")
print("  OK")

# =============================================================
# 12. OPTIMIZATION LOOP TEST
# =============================================================
section("12. Optimization Loop Test")

# A circuit constructed so optimizations chain: a single pass only catches
# surface-level reductions; further iterations expose new adjacencies as the
# circuit shrinks.
qc_loop = QuantumCircuit(3, 3)
# 8 small rz on q0 — strict merge halves the count each iteration (8 -> 4 -> 2 -> 1)
qc_loop.rz(pi / 16, 0)
qc_loop.rz(pi / 16, 0)
qc_loop.rz(pi / 16, 0)
qc_loop.rz(pi / 16, 0)
qc_loop.rz(pi / 16, 0)
qc_loop.rz(pi / 16, 0)
qc_loop.rz(pi / 16, 0)
qc_loop.rz(pi / 16, 0)
# H-X-X-H-H on q1 — iter 1 cancels X-X leaving H-H-H; iter 2 cancels an H-H leaving H
qc_loop.h(1)
qc_loop.x(1)
qc_loop.x(1)
qc_loop.h(1)
qc_loop.h(1)
# CX, H-H, CX on q1-q2 — iter 1 drops H-H leaving CX-CX adjacent; iter 2 cancels the CX pair
qc_loop.cx(1, 2)
qc_loop.h(2)
qc_loop.h(2)
qc_loop.cx(1, 2)
# 4 rotations on q2 that fold across iterations once surrounding gates collapse
qc_loop.rz(pi / 8, 2)
qc_loop.rz(pi / 8, 2)
qc_loop.rz(pi / 8, 2)
qc_loop.rz(pi / 8, 2)
qc_loop.measure([0, 1, 2], [0, 1, 2])

cm_loop = TesseraCouplingMap(3, [(0,1),(1,0),(1,2),(2,1)])

print(f"  Input: {len(qc_loop.data)} gates")
print(f"  Input circuit:\n{qc_loop}")

print(f"\n  --- optimization_iterations=1 (default, single pass) ---")
start = time.perf_counter()
result_one = tessera_transpile(qc_loop, coupling_map=cm_loop, optimization_iterations=1, debug_on=True)
elapsed_one = time.perf_counter() - start
print(f"  Output: {len(result_one.data)} gates | Time: {elapsed_one:.4f}s")

print(f"\n  --- optimization_iterations=5 (fixed loop) ---")
start = time.perf_counter()
result_five = tessera_transpile(qc_loop, coupling_map=cm_loop, optimization_iterations=5, debug_on=True)
elapsed_five = time.perf_counter() - start
print(f"  Output: {len(result_five.data)} gates | Time: {elapsed_five:.4f}s")

print(f"\n  --- optimization_iterations=-1 (run until convergence) ---")
start = time.perf_counter()
result_conv = tessera_transpile(qc_loop, coupling_map=cm_loop, optimization_iterations=-1, debug_on=True)
elapsed_conv = time.perf_counter() - start
print(f"  Output: {len(result_conv.data)} gates | Time: {elapsed_conv:.4f}s")

print(f"\n  iterations=1:  {len(result_one.data)} gates")
print(f"  iterations=5:  {len(result_five.data)} gates")
print(f"  iterations=-1: {len(result_conv.data)} gates (converged)")
print(f"  Extra reduction from looping: {len(result_one.data) - len(result_conv.data)} gates")

# Demonstrate the max_iterations cap behavior in convergence mode
print(f"\n  --- optimization_iterations=-1 with max_iterations=2 (cap fires early) ---")
start = time.perf_counter()
result_cap = tessera_transpile(qc_loop, coupling_map=cm_loop, optimization_iterations=-1, max_iterations=2, debug_on=True)
elapsed_cap = time.perf_counter() - start
print(f"  Output: {len(result_cap.data)} gates | Time: {elapsed_cap:.4f}s")
print(f"  (Should print 'Reached maximum iterations' notice above if cap was hit)")
print("  OK")

# =============================================================
# FULL OPTIMIZATION COMPARISON (always last)
# =============================================================
# This section is purely for curiosity. Regression tests and the benchmark
# suite compare Tessera-at-default against Qiskit-at-default. Here we crank
# both transpilers to their max optimization settings on the same circuit
# and compare. Should always be the last section of this file.
section("Full Optimization Comparison — Tessera (max) vs Qiskit (level 3)")

from qiskit import transpile as qiskit_transpile
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

# A meaty circuit with cancellable pairs, mergeable rotations, multi-qubit
# entanglement, and non-basis gates — enough surface for both transpilers
# to actually do work.
qc_cmp = QuantumCircuit(5, 5)
qc_cmp.h(0)
qc_cmp.h(0)                      # cancels
qc_cmp.cx(0, 1)
qc_cmp.cx(1, 2)
qc_cmp.cx(2, 3)
qc_cmp.cx(3, 4)
qc_cmp.rz(pi / 8, 0)
qc_cmp.rz(pi / 8, 0)             # merge
qc_cmp.rz(pi / 8, 0)             # merge
qc_cmp.x(2)
qc_cmp.x(2)                      # cancels
qc_cmp.ccx(0, 1, 2)
qc_cmp.swap(3, 4)
qc_cmp.cy(1, 2)
qc_cmp.ry(pi / 3, 3)
qc_cmp.ry(pi / 6, 3)             # merge
qc_cmp.cp(pi / 4, 0, 1)
qc_cmp.h(4)
qc_cmp.h(4)                      # cancels
qc_cmp.cx(0, 4)
qc_cmp.cx(0, 4)                  # cancels
qc_cmp.barrier()
qc_cmp.rz(pi / 16, 2)
qc_cmp.rz(pi / 16, 2)            # merge
qc_cmp.rz(pi / 16, 2)            # merge
qc_cmp.rz(pi / 16, 2)            # merge
qc_cmp.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])

print(f"  Input: {qc_cmp.num_qubits} qubits, {len(qc_cmp.data)} gates")

# Tessera at full optimization: convergence loop + commutative mode
print(f"\n  --- Tessera (optimization_iterations=-1, strict=False) ---")
start = time.perf_counter()
result_tessera_max = tessera_transpile(
    qc_cmp,
    backend="IBM",
    strict=False,
    optimization_iterations=-1,
)
elapsed_tessera = time.perf_counter() - start
tessera_gates = len(result_tessera_max.data)
tessera_depth = result_tessera_max.depth()
print(f"  Output: {tessera_gates} gates | Depth: {tessera_depth} | Time: {elapsed_tessera:.4f}s")

# Qiskit at max optimization: optimization_level=3
print(f"\n  --- Qiskit (optimization_level=3) ---")
qiskit_backend = FakeNairobiV2()
start = time.perf_counter()
result_qiskit_max = qiskit_transpile(qc_cmp, backend=qiskit_backend, optimization_level=3)
elapsed_qiskit = time.perf_counter() - start
qiskit_gates = len(result_qiskit_max.data)
qiskit_depth = result_qiskit_max.depth()
print(f"  Output: {qiskit_gates} gates | Depth: {qiskit_depth} | Time: {elapsed_qiskit:.4f}s")

# Side-by-side
print(f"\n  ───────────────────────────────────────────────")
print(f"                    Tessera     Qiskit")
print(f"  Output gates:     {tessera_gates:<11}{qiskit_gates}")
print(f"  Circuit depth:    {tessera_depth:<11}{qiskit_depth}")
print(f"  Transpile time:   {elapsed_tessera:.4f}s    {elapsed_qiskit:.4f}s")
print(f"  ───────────────────────────────────────────────")
print(f"  (Curiosity-only; regression suite locks default vs default, not max vs max.)")
print("  OK")