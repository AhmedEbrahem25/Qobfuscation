import json
import os
from numpy import pi, exp
from qiskit import QuantumCircuit


def load_data_from_json(filename):
    """
    Loads a gate data bank from a JSON file.
    Provides error handling and fallback paths for robustness.
    """
    try:
        # Path to the directory containing this script (utils.py)
        lib_dir = os.path.dirname(os.path.abspath(__file__))

        # Assume the 'data' directory is a sibling of the 'Qobfuscation_lib' directory
        data_dir = os.path.join(lib_dir, '..', 'data')
        file_path = os.path.join(data_dir, filename)

        # Fallback: if the script is run from the project root, check 'data' there
        if not os.path.exists(file_path):
            project_root_data_path = os.path.join('data', filename)
            if os.path.exists(project_root_data_path):
                file_path = project_root_data_path
            else:
                # If the file cannot be found in either location, raise an error
                raise FileNotFoundError(f"Data file '{filename}' not found in expected paths.")

        # Load JSON contents from the file
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except FileNotFoundError as e:
        # Handle the case when the file cannot be found
        print(f"❌ Error loading data: {e}")
        print("   Make sure the 'data' directory exists alongside 'Qobfuscation_lib' and contains the required files.")
        # Return a safe empty structure to avoid crashes
        return {} if 'gates' in filename else []
    except json.JSONDecodeError:
        # Handle the case when JSON cannot be decoded (file is corrupted or invalid)
        print(f"❌ Error: Could not decode JSON from file '{filename}'. The file may be corrupted.")
        return {} if 'gates' in filename else []



#"rx(pi/4)" or "cx" to

def apply_gate_from_token(qc, token, qubits_indices):
    """
    Parses a text token and applies the corresponding gate to the QuantumCircuit.
    Enhanced:
      - Supports parameterized and multi-qubit gates.
      - Randomly chooses target qubits from `qubits_indices` (not always the first).
    """
    token = token.lower().strip()
    name = token
    angle = None

    # Parse parametric gates like rx(pi/4)
    if '(' in token and token.endswith(')'):
        try:
            name, arg_str = token.split('(', 1)
            arg_str = arg_str[:-1]  # remove ')'
            angle = eval(arg_str, {"__builtins__": None}, {"pi": pi, "exp": exp})
        except Exception:
            return

    GATE_PROPERTIES = {
        # Single qubit, non-parameterized
        'x': (qc.x, 1, False), 'y': (qc.y, 1, False), 'z': (qc.z, 1, False),
        'h': (qc.h, 1, False), 's': (qc.s, 1, False), 'sdg': (qc.sdg, 1, False),
        't': (qc.t, 1, False), 'tdg': (qc.tdg, 1, False), 'sx': (qc.sx, 1, False),
        'sxdg': (qc.sxdg, 1, False), 'id': (qc.id, 1, False),

        # Single qubit, parameterized
        'p': (qc.p, 1, True), 'rx': (qc.rx, 1, True), 'ry': (qc.ry, 1, True),
        'rz': (qc.rz, 1, True),

        # Multi-qubit, non-parameterized
        'cx': (qc.cx, 2, False), 'cz': (qc.cz, 2, False), 'swap': (qc.swap, 2, False),
        'ccx': (qc.ccx, 3, False), 'cswap': (qc.cswap, 3, False),

        # Multi-qubit, parameterized
        'cp': (qc.cp, 2, True),
        'crx': (qc.crx, 2, True), 'cry': (qc.cry, 2, True), 'crz': (qc.crz, 2, True),
        'rxx': (qc.rxx, 2, True), 'ryy': (qc.ryy, 2, True), 'rzz': (qc.rzz, 2, True),
    }

    if name not in GATE_PROPERTIES:
        return

    gate_func, required_qubits, needs_angle = GATE_PROPERTIES[name]

    if len(qubits_indices) < required_qubits:
        return

    q_args = qubits_indices[:required_qubits]

    try:
        if needs_angle:
            if angle is None:
                return
            gate_func(angle, *q_args)
        else:
            if angle is not None:
                return
            gate_func(*q_args)
    except Exception:
        return
def export_circuit_to_py(qc: QuantumCircuit, func_name="build_obfuscated_circuit"):
    """
    Converts a Qiskit QuantumCircuit into a self-contained Python script string.
    This script can be saved and executed to deterministically rebuild the circuit.
    """
    circuit_name = qc.name if qc.name else 'circuit'

    code = [
        "# Auto-generated file to rebuild a quantum circuit.",
        "import qiskit",
        "from numpy import pi, exp\n",
        f"def {func_name}():",
        f"    \"\"\"Builds and returns the quantum circuit named '{circuit_name}'.\"\"\"",
        f"    qc = qiskit.QuantumCircuit({qc.num_qubits}, {qc.num_clbits}, name='{circuit_name}')\n"
    ]

    # Iterate through the circuit's operations and recreate them
    for instruction in qc.data:
        gate_name = instruction.operation.name
        qubits = [qc.qubits.index(q) for q in instruction.qubits]
        clbits = [qc.clbits.index(c) for c in instruction.clbits]
        params = instruction.operation.params

        # Format parameters as Python code strings
        formatted_params = [f"{p}" for p in params]

        args = []
        args.extend(formatted_params)
        args.extend(map(str, qubits))
        args.extend(map(str, clbits))

        args_str = ", ".join(args)

        code.append(f"    qc.{gate_name}({args_str})")

    code.append("\n    return qc")
    return "\n".join(code)