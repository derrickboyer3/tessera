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
        TesseraInstruction("u", [0], [], [params[0], 0, 0])
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

# IonQ Backend Decomposition Map
IONQ_DECOMP_MAP = {
    # Single Qubit No Params
    "h": [
        TesseraInstruction("rz", [0], [], [pi / 2]),
        TesseraInstruction("rx", [0], [], [pi / 2]),
        TesseraInstruction("rz", [0], [], [pi / 2])
    ],
    "x": [
        TesseraInstruction("rx", [0], [], [pi])
    ],
    "y": [
        TesseraInstruction("ry", [0], [], [pi])
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
    "sx": [
        TesseraInstruction("rx", [0], [], [pi / 2])
    ],

    # Single Qubit With Params
    "p": lambda params: [
        TesseraInstruction("rz", [0], [], [params[0]])
    ],
    "u": lambda params: [
        TesseraInstruction("rz", [0], [], [params[1]]),
        TesseraInstruction("ry", [0], [], [params[0]]),
        TesseraInstruction("rz", [0], [], [params[2]])
    ],

    # Two Qubit No Params
    "cz": [
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
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
    "cp": lambda params: [
        TesseraInstruction("rz", [0], [], [params[0] / 2]),
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [-params[0] / 2]),
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [params[0] / 2])
    ],

    # Three Qubit
    "ccx": [
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
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
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("rz", [0], [], [pi / 4]),
        TesseraInstruction("rz", [1], [], [-pi / 4]),
        TesseraInstruction("cx", [0, 1], [], [])
    ]
}

# Rigetti Backend Decomposition Map
RIGETTI_DECOMP_MAP = {
    # Single Qubit No Params
    "h": [
        TesseraInstruction("rz", [0], [], [pi / 2]),
        TesseraInstruction("rx", [0], [], [pi / 2]),
        TesseraInstruction("rz", [0], [], [pi / 2])
    ],
    "x": [
        TesseraInstruction("rx", [0], [], [pi])
    ],
    "y": [
        TesseraInstruction("rz", [0], [], [pi]),
        TesseraInstruction("rx", [0], [], [pi])
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
    "sx": [
        TesseraInstruction("rx", [0], [], [pi / 2])
    ],

    # Single Qubit With Params
    "ry": lambda params: [
        TesseraInstruction("rz", [0], [], [pi / 2]),
        TesseraInstruction("rx", [0], [], [params[0]]),
        TesseraInstruction("rz", [0], [], [-pi / 2])
    ],
    "p": lambda params: [
        TesseraInstruction("rz", [0], [], [params[0]])
    ],
    "u": lambda params: [
        TesseraInstruction("rz", [0], [], [params[1] + pi / 2]),
        TesseraInstruction("rx", [0], [], [params[0]]),
        TesseraInstruction("rz", [0], [], [params[2] - pi / 2])
    ],

    # Two Qubit No Params
    "cx": [
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2])
    ],
    "cy": [
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi])
    ],
    "swap": [
        # CX(0,1) = H(1) CZ H(1)
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        # CX(1,0) = H(0) CZ H(0)
        TesseraInstruction("rz", [0], [], [pi / 2]),
        TesseraInstruction("rx", [0], [], [pi / 2]),
        TesseraInstruction("rz", [0], [], [pi / 2]),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("rz", [0], [], [pi / 2]),
        TesseraInstruction("rx", [0], [], [pi / 2]),
        TesseraInstruction("rz", [0], [], [pi / 2]),
        # CX(0,1) = H(1) CZ H(1)
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2])
    ],

    # Two Qubit With Params
    "cp": lambda params: [
        TesseraInstruction("rz", [0], [], [params[0] / 2]),
        # CX(0,1) = H(1) CZ H(1)
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [-params[0] / 2]),
        # CX(0,1) = H(1) CZ H(1)
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [params[0] / 2])
    ],

    # Three Qubit
    "ccx": [
        # H on q2
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        # CX(1,2) = H(2) CZ(1,2) H(2)
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("cz", [1, 2], [], []),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [-pi / 4]),
        # CX(0,2) = H(2) CZ(0,2) H(2)
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("cz", [0, 2], [], []),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 4]),
        # CX(1,2) = H(2) CZ(1,2) H(2)
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("cz", [1, 2], [], []),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [-pi / 4]),
        # CX(0,2) = H(2) CZ(0,2) H(2)
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("cz", [0, 2], [], []),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 4]),
        TesseraInstruction("rz", [2], [], [pi / 4]),
        # H on q2
        TesseraInstruction("rz", [2], [], [pi / 2]),
        TesseraInstruction("rx", [2], [], [pi / 2]),
        TesseraInstruction("rz", [2], [], [pi / 2]),
        # CX(0,1) = H(1) CZ(0,1) H(1)
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rz", [0], [], [pi / 4]),
        TesseraInstruction("rz", [1], [], [-pi / 4]),
        # CX(0,1) = H(1) CZ(0,1) H(1)
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("rz", [1], [], [pi / 2]),
        TesseraInstruction("rx", [1], [], [pi / 2]),
        TesseraInstruction("rz", [1], [], [pi / 2])
    ]
}