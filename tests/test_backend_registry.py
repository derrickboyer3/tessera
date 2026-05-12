# tests/test_backend_registry.py
from tessera.backends.backend_registry import BACKEND_REGISTRY

def test_ibm_in_registry():
    assert "IBM" in BACKEND_REGISTRY

def test_ibm_has_basis_gates():
    assert "basis_gates" in BACKEND_REGISTRY["IBM"]

def test_ibm_has_decomp_map():
    assert "decomp_map" in BACKEND_REGISTRY["IBM"]

def test_registry_values_are_not_empty():
    assert len(BACKEND_REGISTRY["IBM"]["basis_gates"]) > 0
    assert len(BACKEND_REGISTRY["IBM"]["decomp_map"]) > 0

def test_ionq_in_registry():
    assert "IONQ" in BACKEND_REGISTRY

def test_rigetti_in_registry():
    assert "RIGETTI" in BACKEND_REGISTRY

def test_ionq_has_required_fields():
    for field in ("basis_gates", "decomp_map", "coupling_map"):
        assert field in BACKEND_REGISTRY["IONQ"]

def test_rigetti_has_required_fields():
    for field in ("basis_gates", "decomp_map", "coupling_map"):
        assert field in BACKEND_REGISTRY["RIGETTI"]

def test_ionq_default_coupling_map_is_aria():
    assert BACKEND_REGISTRY["IONQ"]["coupling_map"] == "IONQ_ARIA"

def test_rigetti_default_coupling_map_is_ankaa():
    assert BACKEND_REGISTRY["RIGETTI"]["coupling_map"] == "RIGETTI_ANKAA"