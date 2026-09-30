from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def quantum_candidates(num_qubits=3, shots=100):
    """Generate candidate solutions using a quantum circuit."""

    qc = QuantumCircuit(num_qubits)

    # Create superposition
    for qubit in range(num_qubits):
        qc.h(qubit)

    # Measure
    qc.measure_all()

    # Run quantum circuit
    sampler = StatevectorSampler()

    job = sampler.run([qc], shots=shots)

    result = job.result()

    counts = result[0].data.meas.get_counts()

    return counts


def decode_binary_state(state):
    """Convert a binary state into an integer."""

    return int(state, 2)


def objective(x):
    """Optimization function."""

    return (x - 3) ** 2


if __name__ == "__main__":

    counts = quantum_candidates(
        num_qubits=3,
        shots=100
    )

    print("Quantum candidates:\n")

    best_state = None
    best_value = float("inf")

    for state, count in sorted(counts.items()):

        x = decode_binary_state(state)

        value = objective(x)

        print(
            f"{state} -> x = {x}, "
            f"fitness = {value}, "
            f"samples = {count}"
        )

        if value < best_value:
            best_value = value
            best_state = state

    print("\nBest quantum candidate:")
    print("State:", best_state)
    print("x:", decode_binary_state(best_state))
    print("Fitness:", best_value)