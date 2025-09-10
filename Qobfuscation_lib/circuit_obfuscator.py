import random
import importlib.util
import time
import signal
from Qobfuscation_lib.utils import *
from Qobfuscation_lib.quantum_engines import SmartNoiseGenerator


# --- Professional Safeguards: Timeout Handler ---
class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("The obfuscation process exceeded the time limit.")


class CircuitObfuscator:
    """
    Handles the professional, layered obfuscation of quantum circuit files.
    This class orchestrates all circuit-level obfuscation techniques from the
    ObfusQate paper, with advanced features like timeouts, circuit limits,
    and multi-layered application.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        if self.verbose:
            print("[INFO] Initializing Professional Circuit Obfuscator...")

        # --- Load all necessary data banks ---
        self.cloaked_data = load_data_from_json('cloaked_gates.json')
        self.delayed_data = load_data_from_json('delayed_gate.json')
        self.aux_res_data = load_data_from_json('aux_res.json')
        self.noise_generator = SmartNoiseGenerator()

        # --- Map algorithm names to their implementation methods ---
        self._algo_map = {
            'cloaked': self._apply_cloaked_gates,
            'inverse': self._apply_inverse_gates,
            'delayed': self._apply_delayed_gates,
            'composite': self._apply_composite_gates,
        }
        if self.verbose:
            print("[INFO]   -> All obfuscation data banks loaded successfully.")




    def _load_circuit_from_file(self, file_path):
        """Loads a QuantumCircuit from either a .qasm or .py file."""
        if self.verbose: print(f"[INFO]   -> Loading circuit from {file_path}...")

        if file_path.endswith('.qasm'):
            return QuantumCircuit.from_qasm_file(file_path)
        elif file_path.endswith('.py'):
            try:
                spec = importlib.util.spec_from_file_location("circuit_module", file_path)
                circuit_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(circuit_module)
                if hasattr(circuit_module, 'get_circuit'):
                    return circuit_module.get_circuit()
                else:
                    raise AttributeError("Python file must contain a 'get_circuit()' function.")
            except Exception as e:
                raise ImportError(f"Could not load circuit from Python file: {e}")
        else:
            raise ValueError("Unsupported file type. Please use .qasm or .py")



    def _save_circuit_to_file(self, qc, original_path, output_path):
        """Saves the obfuscated circuit back to the appropriate file type."""
        if self.verbose: print(f"[INFO]   -> Saving obfuscated circuit to {output_path}...")

        if original_path.endswith('.qasm'):
            from qiskit.qasm2 import dump
            with open(output_path, 'w') as f:
                dump(qc, f)
        elif original_path.endswith('.py'):
            py_code = export_circuit_to_py(qc)
            with open(output_path, 'w') as f:
                f.write(py_code)

    # --- CORE OBFUSCATION ALGORITHMS ---

    def _apply_cloaked_gates(self, qc, **config):
        probability = config.get('probability', 0.5)
        new_qc = QuantumCircuit(qc.num_qubits, qc.num_clbits, name=f"{qc.name}_cloaked")
        for instr, qargs, cargs in qc.data:
            gate_name = instr.name
            if gate_name in self.cloaked_data and random.random() < probability:
                sequence = random.choice(self.cloaked_data[gate_name])
                qubit_indices = [qc.qubits.index(q) for q in qargs]
                for token in sequence:
                    apply_gate_from_token(new_qc, token, qubit_indices)
            else:
                new_qc.append(instr, qargs, cargs)
        return new_qc

    def _apply_inverse_gates(self, qc, **config):
        density = config.get('density', 0.3)
        num_insertions = int(len(qc.data) * density)
        instructions = list(qc.data)
        insertion_points = sorted(random.sample(range(len(instructions) + 1), num_insertions))

        new_qc = QuantumCircuit(qc.num_qubits, qc.num_clbits, name=f"{qc.name}_noisy")
        instr_idx = 0

        for insert_point in insertion_points:
            while instr_idx < insert_point and instr_idx < len(instructions):
                new_qc.append(instructions[instr_idx])
                instr_idx += 1

            if new_qc.num_qubits > 0:
                num_target_qubits = min(new_qc.num_qubits, random.randint(1, 2))
                target_qubits = random.sample(range(new_qc.num_qubits), num_target_qubits)

                self.noise_generator.inject(new_qc, target_qubits, level=random.choice(['light', 'medium']))

        while instr_idx < len(instructions):
            new_qc.append(instructions[instr_idx])
            instr_idx += 1

        return new_qc

    def _apply_delayed_gates(self, qc, **config):
        """
        Applies obfuscation by replacing gates with equivalent, more complex sequences.
        This is the CORRECTED version.
        """
        probability = config.get('probability', 0.5)
        new_qc = QuantumCircuit(qc.num_qubits, qc.num_clbits, name=f"{qc.name}_delayed")

        for instr, qargs, cargs in qc.data:
            gate_name = instr.name
            qubit_indices = [qc.qubits.index(q) for q in qargs]

            # Check if the gate can be obfuscated and if it passes the random check
            if gate_name in self.delayed_data and random.random() < probability:

                # 1. Choose a full identity sequence randomly
                chosen_identity = random.choice(self.delayed_data[gate_name])

                # 2. Apply each gate from the chosen identity
                for token in chosen_identity:
                    apply_gate_from_token(new_qc, token, qubit_indices)

                # 3. We do NOT append the original instruction (instr)
                # The replacement is now complete.
            else:
                # If not obfuscating, just append the original instruction
                new_qc.append(instr, qargs, cargs)

        return new_qc

    def _apply_composite_gates(self, qc, **config):
        """
        Injects complex identity sequences from aux_res.json into the circuit
        at random points to increase complexity without changing the final output.
        """
        if not self.aux_res_data:
            if self.verbose: print("⚠️ Warning: Composite gate data not found. Skipping.")
            return qc

        density = config.get('density', 0.2)
        num_insertions = int(len(qc.data) * density)
        if num_insertions == 0: return qc

        instructions = list(qc.data)
        insertion_points = sorted(random.sample(range(len(instructions) + 1), num_insertions))

        new_qc = QuantumCircuit(qc.num_qubits, qc.num_clbits, name=f"{qc.name}_composite")
        instr_idx = 0

        for insert_point in insertion_points:
            # Append original instructions up to the insertion point
            while instr_idx < insert_point and instr_idx < len(instructions):
                new_qc.append(instructions[instr_idx])
                instr_idx += 1

            # --- IDENTITY INJECTION LOGIC ---
            aux_seq, res_seq = random.choice(self.aux_res_data)

            # Apply the sequence and its inverse consecutively to all qubits
            for token in aux_seq:
                for i in range(qc.num_qubits):
                    apply_gate_from_token(new_qc, token, [i])

            for token in res_seq:
                for i in range(qc.num_qubits):
                    apply_gate_from_token(new_qc, token, [i])

        # Append the rest of the original instructions
        while instr_idx < len(instructions):
            new_qc.append(instructions[instr_idx])
            instr_idx += 1

        return new_qc

    def obfuscate(self, file_path, techniques, max_qubits=30, max_depth=1000, timeout=60):
        signal.alarm(timeout)

        try:
            current_qc = self._load_circuit_from_file(file_path)

            if self.verbose:
                print(f"[INFO]   -> Circuit '{current_qc.name}' loaded successfully.")
                print(f"[INFO]   -> Properties: {current_qc.num_qubits} qubits, depth {current_qc.depth()}.")

            if current_qc.num_qubits > max_qubits:
                print(f"❌ Error: Circuit exceeds qubit limit ({current_qc.num_qubits} > {max_qubits}). Aborting.")
                signal.alarm(0);
                return
            if current_qc.depth() > max_depth:
                print(f"⚠️ Warning: Circuit depth ({current_qc.depth()}) exceeds recommended limit of {max_depth}.")

            for tech_name, config in techniques:
                if tech_name in self._algo_map:
                    if self.verbose: print(f"--> Applying layer: '{tech_name}' with config: {config}")
                    start_time = time.time()
                    current_qc = self._algo_map[tech_name](current_qc, **config)
                    end_time = time.time()
                    if self.verbose:
                        print(f"    ... Layer '{tech_name}' applied in {end_time - start_time:.2f} seconds.")
                        print(f"    ... New circuit depth: {current_qc.depth()}.")
                else:
                    print(f"⚠️ Warning: Unknown quantum algorithm '{tech_name}'. Skipping.")

            base_name, ext = os.path.splitext(file_path)
            output_path = f"{base_name}_obfuscated{ext}"
            self._save_circuit_to_file(current_qc, file_path, output_path)

            print(f"✅ Success! Obfuscation complete.")

        except TimeoutException as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
        finally:
            signal.alarm(0)

