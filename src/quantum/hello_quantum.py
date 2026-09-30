from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

# Create a 2-qubit circuit
qc = QuantumCircuit(2)

# Create superposition
qc.h(0)

# Entangle the two qubits
qc.cx(0, 1)

# Measure both qubits
qc.measure_all()

# Create the sampler
sampler = StatevectorSampler()

# Run the circuit 100 times
job = sampler.run([qc], shots=100)

# Get the result
result = job.result()

# Get the measurement data
pub_result = result[0]

counts = pub_result.data.meas.get_counts()

print("Measurement results:")
print(counts)