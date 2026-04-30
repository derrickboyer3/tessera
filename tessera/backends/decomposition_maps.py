'''
    Tessera Backend Decomposition Maps
    ----------------------------------
    This file houses our decomposition maps. This allows us to break down gates into their basis forms for specific backends based on the
    backend-specific basis gate sets
'''
from tessera.instruction import TesseraInstruction
import numpy as np
pi = np.pi

# IBM Backend Decomposition Map
IBM_DECOMP_MAP = {
    # Single Qubit No Params
    "h": [
        TesseraInstruction("rz", [0], [], [pi / 2]),
        TesseraInstruction("sx", [0], [], []),
        TesseraInstruction("rz", [0], [], [pi / 2])
    ],
    "y": [
        TesseraInstruction("rz", [0], [], [pi]),
        TesseraInstruction("x", [0], [], [])
    ],
    "z": [
        TesseraInstruction("rz", [0], [], [pi])
    ],
    "s": [
        TesseraInstruction("rz", [0], [], [pi / 2])
    ],
    "sdg": [
        TesseraInstruction("rz", [0], [], [-pi / 2])
    ],
    "t": [
        TesseraInstruction("rz", [0], [], [pi / 4])
    ],
    "tdg": [
        TesseraInstruction("rz", [0], [], [-pi / 4])
    ],

    # Single Qubit With Params
    "p": lambda params : [
        TesseraInstruction("rz", [0], [], [params[0]])
    ],
    "rx": lambda params: [
        TesseraInstruction("rz", [0], [], [-pi / 2]),
        TesseraInstruction("sx", [0], [], []),
        TesseraInstruction("rz", [0], [], [params[0] - pi / 2]),
        TesseraInstruction("sx", [0], [], []),
        TesseraInstruction("rz", [0], [], [pi / 2])
    ],
    "ry": lambda params: [
        TesseraInstruction("rz", [0], [], [-pi / 2]),
        TesseraInstruction("sx", [0], [], []),
        TesseraInstruction("rz", [0], [], [pi / 2]),
        TesseraInstruction("sx", [0], [], []),
        TesseraInstruction("rz", [0], [], [pi / 2])
    ],

    # Two Qubit No Params
    "cz": [
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("sx", [1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("sx", [1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2])
    ],
    "cy": [
        TesseraInstruction("rz", [1], [], [-pi / 2]),
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2])
    ],
    "swap": [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("cx", [1, 0], [], []),
        TesseraInstruction("cx", [0, 1], [], [])
    ],

    # Two Qubit With Params
    "cp": lambda params : [
        TesseraInstruction("rz", [0], [], [params[0] / 2]),
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [-params[0] / 2]),
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [params[0] / 2])
    ],

    # Three Qubit
    "ccx": [
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("sx", [2], [], []),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("rz", [2], [], [-pi / 4]),
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("rz", [2], [], [pi / 4]),
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("rz", [2], [], [-pi / 4]),
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("rz", [1], [], [pi / 4]),
        TesseraInstruction("rz", [2], [], [pi / 4]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("sx", [2], [], []),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("rz", [0], [], [pi / 4]),
        TesseraInstruction("rz", [1], [], [-pi / 4]),
        TesseraInstruction("cx", [0, 1], [], [])
    ]
}
