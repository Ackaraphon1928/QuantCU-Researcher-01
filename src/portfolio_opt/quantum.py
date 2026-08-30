from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from qiskit import QuantumCircuit


@dataclass
class QAOAResult:
    bitstring: tuple[int, ...]
    objective: float
    feasible: bool
    num_qubits: int
    depth: int
    shots: int
    metadata: dict[str, Any]


def qubo_to_ising(qubo: np.ndarray, linear: np.ndarray, offset: float = 0.0) -> tuple[np.ndarray, np.ndarray, float]:
    """Convert a QUBO to Ising form with a simple z-basis mapping."""
    n = len(linear)
    h = np.zeros(n, dtype=float)
    j = np.zeros((n, n), dtype=float)
    for i in range(n):
        h[i] = -0.5 * linear[i]
        for j_idx in range(i + 1, n):
            j[i, j_idx] = -0.25 * qubo[i, j_idx]
    return h, j, offset


def build_qaoa_circuit(num_qubits: int, p: int = 1) -> QuantumCircuit:
    """Build a simple layered QAOA circuit for a small portfolio problem."""
    circuit = QuantumCircuit(num_qubits)
    circuit.h(range(num_qubits))
    for _ in range(p):
        for q in range(num_qubits):
            circuit.rx(0.5, q)
        for q in range(num_qubits - 1):
            circuit.cx(q, q + 1)
    return circuit


def decode_measurement(bitstring: str | np.ndarray | list[int]) -> tuple[int, ...]:
    """Decode a sampled bitstring into a tuple of integer bits."""
    if isinstance(bitstring, str):
        return tuple(int(v) for v in bitstring)
    arr = np.asarray(bitstring, dtype=int).ravel()
    return tuple(int(v) for v in arr)
