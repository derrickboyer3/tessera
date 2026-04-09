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
'''
import numpy as np
import time
from qiskit import QuantumCircuit
from converters import from_qiskit, to_qiskit
from pass_manager import TesseraPassManager
from passes.identity_pass import IdentityPass
from passes.dense_layout_pass import DenseLayoutPass
from passes.trivial_pass import TrivialPass
from passes.basic_swap_router import BasicSwapRouter
from transpiler import TesseraTranspiler
from hardware.coupling_map import TesseraCouplingMap
from circuit import TesseraCircuit
from instruction import TesseraInstruction

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
from passes.dense_layout_pass import DenseLayoutPass
layout = DenseLayoutPass(cm_pipeline).run(tes).layout
print(f"\n  Dense Layout chosen: {layout}")
print(f"  (q0 and q4 should be close — they interact 4 times)")
print(f"  q0<->q4 distance: {cm_pipeline.distance(layout[0], layout[4])}")
print(f"  q1<->q3 distance: {cm_pipeline.distance(layout[1], layout[3])}")

print(f"\n  Output: {len(final.data)} gates (includes basis decomposition + swaps)")
print(f"  Final circuit:\n{final}")
print(f"\n  Time: {elapsed:.4f}s")
print("  OK")