import math

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def quantum_sample(num_qubits=4, shots=100):
    """
    Generate candidate bitstrings using a quantum circuit.
    """

    qc = QuantumCircuit(num_qubits)

    # Create equal superposition
    for qubit in range(num_qubits):
        qc.h(qubit)

    qc.measure_all()

    sampler = StatevectorSampler()
    job = sampler.run([qc], shots=shots)

    result = job.result()
    counts = result[0].data.meas.get_counts()

    return counts


def bitstring_to_position(bitstring):
    """
    Convert a binary state into a normalized value in [0, 1].
    """

    integer_value = int(bitstring, 2)
    max_value = (2 ** len(bitstring)) - 1

    return integer_value / max_value


def quantum_guidance(
    dimensions,
    num_qubits=None,
    shots=100
):
    """
    Generate exactly `dimensions` quantum-derived values
    in the range [0, 1].

    The number of qubits automatically scales with the
    requested number of dimensions.
    """

    if dimensions < 1:
        raise ValueError(
            "dimensions must be at least 1."
        )

    # Automatically choose enough qubits.
    required_qubits = math.ceil(
        math.log2(dimensions)
    )

    if num_qubits is None:
        num_qubits = max(4, required_qubits)
    else:
        num_qubits = max(
            num_qubits,
            required_qubits
        )

    # Collect quantum measurement results.
    counts = {}

    # Repeat sampling if necessary until enough
    # unique quantum states are available.
    attempts = 0
    max_attempts = 5

    while (
        len(counts) < dimensions
        and attempts < max_attempts
    ):

        new_counts = quantum_sample(
            num_qubits=num_qubits,
            shots=shots
        )

        for state, count in new_counts.items():
            counts[state] = (
                counts.get(state, 0)
                + count
            )

        attempts += 1

    # Convert states into normalized positions.
    candidates = []

    for state, count in counts.items():

        position = bitstring_to_position(
            state
        )

        candidates.append(
            (position, count)
        )

    # Stronger measurement frequency =
    # stronger quantum signal.
    candidates.sort(
        key=lambda item: item[1],
        reverse=True
    )

    # Take exactly the requested number
    # of quantum-derived values.
    values = [
        position
        for position, count in candidates[:dimensions]
    ]

    # Safety fallback.
    # This should rarely be needed because the
    # number of qubits is automatically increased.
    if len(values) < dimensions:

        additional_values = [
            i / (dimensions - 1)
            if dimensions > 1
            else 0.5
            for i in range(dimensions)
        ]

        while len(values) < dimensions:

            index = len(values)

            values.append(
                additional_values[index]
            )

    return values


if __name__ == "__main__":

    for dimensions in [8, 12, 16, 20]:

        guidance = quantum_guidance(
            dimensions=dimensions,
            shots=100
        )

        required_qubits = max(
            4,
            math.ceil(
                math.log2(dimensions)
            )
        )

        print()
        print("=" * 50)
        print(
            f"Dimensions: {dimensions}"
        )
        print(
            f"Qubits used: {required_qubits}"
        )
        print(
            f"Guidance values: {len(guidance)}"
        )
        print("=" * 50)

        for i, value in enumerate(guidance):

            print(
                f"Dimension {i + 1}: "
                f"{value:.4f}"
            )