'''
    Tessera Transpiler Pass (Base Class)
    ------------------------------------
    Abstract base class that all Tessera transpiler passes must inherit from.
    Enforces a consistent interface across all passes:

        run(circuit: TesseraCircuit) -> TesseraCircuit

    Each pass should do one specific job (decomposition, routing, optimization, etc.)
    and return a new circuit reflecting its changes. Passes are executed by the
    TesseraPassManager in the order they are added.
'''
from abc import ABC, abstractmethod
from circuit import TesseraCircuit

class TranspilerPass(ABC):

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        pass