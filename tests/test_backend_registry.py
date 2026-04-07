# tests/test_backend_registry.py
from backends.backend_registry import BACKEND_REGISTRY

def test_ibm_in_registry():
    assert "IBM" in BACKEND_REGISTRY

def test_ibm_has_basis_gates():
    assert "basis_gates" in BACKEND_REGISTRY["IBM"]

def test_ibm_has_decomp_map():
    assert "decomp_map" in BACKEND_REGISTRY["IBM"]

def test_registry_values_are_not_empty():
    assert len(BACKEND_REGISTRY["IBM"]["basis_gates"]) > 0
    assert len(BACKEND_REGISTRY["IBM"]["decomp_map"]) > 0