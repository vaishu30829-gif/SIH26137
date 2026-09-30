"""Explicit Quantum-QPSO VRP wrapper.

The implementation lives in qpso_vrp.QPSOVRP. Setting quantum_weight > 0
activates the Qiskit-guided component.
"""

from src.vrp.qpso_vrp import QPSOVRP


class QuantumQPSOVRP(QPSOVRP):
    def __init__(self, *args, quantum_weight=0.30, **kwargs):
        kwargs["quantum_weight"] = quantum_weight
        super().__init__(*args, **kwargs)
