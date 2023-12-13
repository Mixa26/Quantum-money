from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.quantum_info import state_fidelity
import random

class Issuer:
    def __init__(self):
        self.all_money = {}
        self.last_money_id = 0 

    def create_money(self, num_qubits):
        #We create a quantum circuit
        qc = QuantumCircuit(num_qubits)

        #Go through all the qubits
        for i in num_qubits:
            #The cubit takes a random state
            quantum_state = QuantumCircuit(2)
            quantum_state.h(0)
            quantum_state.h(1)
            quantum_state.measure(0, 0)
            quantum_state.measure(1, 1)

            # Choose the simulator backend
            simulator = Aer.get_backend('qasm_simulator')

            # Transpile the circuit for the simulator
            compiled_circuit = transpile(quantum_state, simulator)

            # Run the circuit on the simulator
            result = simulator.run(assemble(compiled_circuit)).result()

            # Get the measurement outcome
            gate = int(result.get_counts(quantum_state).most_frequent(), 2)

            if gate == 0:
                pass
            elif gate == 1:
                qc.y(i)
            elif gate == 2:
                qc.h(i)
            else:
                qc.y(i)
                qc.h(i)

        return (self.last_money_id+1, qc.qubits)

    def land_money(self):
        return self.create_money(1)
    
    def verify_money(self, money_note):
        original = self.all_money[money_note[0]]

        simulator = Aer.get_backend('statevector_simulator')

        # Transpile the circuits for the simulator
        compiled_circuit1 = transpile(original, simulator)
        compiled_circuit2 = transpile(money_note[1], simulator)

        # Run the circuits on the simulator to obtain state vectors
        result1 = simulator.run(assemble(compiled_circuit1)).result()
        result2 = simulator.run(assemble(compiled_circuit2)).result()

        # Extract the state vectors
        state_vector1 = result1.get_statevector(original)
        state_vector2 = result2.get_statevector(money_note[1])

        # Calculate the state fidelity
        fidelity = state_fidelity(state_vector1, state_vector2)

        if fidelity == 1:
            return True
        return False

    def save_money_data(self):
        pass