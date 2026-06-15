'''
    Dense Layout Pass (Deprecated)
    ------------------------------
    Backwards-compatibility shim. The dense layout algorithm now lives in
    tessera/layouts/dense.py and is registered in LAYOUT_REGISTRY under the
    key "dense". Prefer LayoutPass(coupling_map, "dense") in new code.

    This class still works — it delegates to LayoutPass internally — but
    emits a DeprecationWarning on construction. It may be removed in a
    future release.
'''
import warnings
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.passes.layout_pass import LayoutPass


class DenseLayoutPass(LayoutPass):
    def __init__(self, coupling_map: TesseraCouplingMap):
        warnings.warn(
            "DenseLayoutPass is deprecated and may be removed in a future release. "
            "Use LayoutPass(coupling_map, 'dense') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(coupling_map, layout_algorithm="dense")
