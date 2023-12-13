from qiskit import QuantumCircuit, ClassicalRegister, Aer, transpile
from qiskit.quantum_info import state_fidelity
import json

class Issuer:
    def __init__(self):
        self.file_path = 'quantum_money.json'
        self.all_money = {}
        self.last_money_id = sorted(self.all_money.keys)[len(self.all_money.keys)-1] if len(self.all_money) > 0 else 0

        #Load all the money notes and its corresponding ids
        with open(self.file_path, 'r') as file:
            loaded_data = json.load(file)

        for key, qasm_code in loaded_data.items():
            self.all_money[int(key)] = QuantumCircuit.from_qasm_str(qasm_code)

    def create_money(self, num_qubits):
        #We create a quantum circuit
        qc = QuantumCircuit(num_qubits)

        #Go through all the qubits
        for i in range(num_qubits):
            #The cubit takes a random state
            quantum_state = QuantumCircuit(2, 2)
            quantum_state.h(0)
            quantum_state.h(1)
            quantum_state.measure(0, 0)
            quantum_state.measure(1, 1)

            # Choose the simulator backend
            simulator = Aer.get_backend('qasm_simulator')

            # Transpile the circuit for the simulator
            compiled_circuit = transpile(quantum_state, simulator)

            # Run the circuit on the simulator
            result = simulator.run(compiled_circuit).result()

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

        self.last_money_id += 1
        self.all_money[self.last_money_id] = qc
        return (self.last_money_id, qc)

    def land_money(self):
        return self.create_money(1)
    
    def verify_money(self, money_note):
        original = self.all_money[money_note[0]]

        simulator = Aer.get_backend('statevector_simulator')

        # Transpile the circuits for the simulator
        compiled_circuit1 = transpile(original, simulator)
        compiled_circuit2 = transpile(money_note[1], simulator)

        # Run the circuits on the simulator to obtain state vectors
        result1 = simulator.run(compiled_circuit1).result()
        result2 = simulator.run(compiled_circuit2).result()

        # Extract the state vectors
        state_vector1 = result1.get_statevector(original)
        state_vector2 = result2.get_statevector(money_note[1])

        # Calculate the state fidelity
        fidelity = state_fidelity(state_vector1, state_vector2)
        print(fidelity)

        if int(fidelity) == 1:
            return True
        return False

    def save_money_data(self):
        with open(self.file_path, 'w') as file:
            json.dump({str(key): val.qasm() for key, val in self.all_money.items()}, file)

class User:
    def __init__(self):
        self.money = []

    def see_balance(self):
        money_ids = ""

        for money in self.money:
            money_ids += str(money[0]) + " "

        return money_ids

    def request_money(self, issuer):
        self.money.append(issuer.land_money())

    def check_money_validity(self, issuer, money_id):

        for money in self.money:
            if money[0] == money_id:
                return issuer.verify_money(money)
        return False
    
class Falsificator:
    def __init__(self):
        pass
    
    def bank_attack(self, issuer, money_id_to_try, num_of_qubits):
        false_quantum_circuit = QuantumCircuit(num_of_qubits)

        #Go through all the qubits
        for i in range(num_of_qubits):
            #The cubit takes a random state
            quantum_state = QuantumCircuit(2, 2)
            quantum_state.h(0)
            quantum_state.h(1)
            quantum_state.measure(0, 0)
            quantum_state.measure(1, 1)

            # Choose the simulator backend
            simulator = Aer.get_backend('qasm_simulator')

            # Transpile the circuit for the simulator
            compiled_circuit = transpile(quantum_state, simulator)

            # Run the circuit on the simulator
            result = simulator.run(compiled_circuit).result()

            # Get the measurement outcome
            gate = int(result.get_counts(quantum_state).most_frequent(), 2)

            if gate == 0:
                pass
            elif gate == 1:
                false_quantum_circuit.y(i)
            elif gate == 2:
                false_quantum_circuit.h(i)
            else:
                false_quantum_circuit.y(i)
                false_quantum_circuit.h(i)

        #Try to varify randomly generated qubit
        return issuer.verify_money((money_id_to_try, false_quantum_circuit))
    
#USER INTERFACE

def is_number(input_str):
    try:
        # Attempt to convert the input string to an integer
        int(input_str)
        return True
    except ValueError:
        # If conversion fails, it's not a number
        return False

user = User()
issuer = Issuer()
falsificator = Falsificator()

while(True):
    print("Welcome to the Quantum bank!")
    print("Chose an action:")
    print("1. See all your quantum money.")
    print("2. Request a money note from the bank.")
    print("3. Verify your money note.")
    print("4. Try falsification of money.")
    print("5. Exit")

    user_input = input("Enter a number of an action:")
    if is_number(user_input) and int(user_input) >= 1 and int(user_input) <= 5:
        user_input = int(user_input)
        if user_input == 1:
            print("Available money notes: ", user.see_balance())
        elif user_input == 2:
            user.request_money(issuer)
            print("Bank note added to the wallet.")
        elif user_input == 3:
            money_id = input("Enter money note id:")

            if is_number(money_id):
                if user.check_money_validity(issuer, int(money_id)):
                    print("Valid!")
                else:
                    print("FAKE!")
            else:
                print("Bad input, try again!\n")
                continue
        elif user_input == 4:
            money_id = input("Enter money note id to try falsification:")

            if is_number(money_id):
                if falsificator.bank_attack(issuer, int(money_id), 1):
                    print("Valid!")
                else:
                    print("Falsification failed.")
            else:
                print("Bad input, try again!\n")
                continue
        elif user_input == 5:
            break
    else:
        print("Bad input, try again!\n")
    print('\n')