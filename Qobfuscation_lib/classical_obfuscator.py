import os
import random
import datetime
import textwrap
from typing import Tuple, Dict, Any, List

from qiskit import QuantumCircuit

try:
    from Qobfuscation_lib.quantum_engines import SmartNoiseGenerator, generate_deterministic_circuit
    from Qobfuscation_lib.utils import load_data_from_json
    from Qobfuscation_lib.code_splitter import IntelligentCodeSplitter
    from Qobfuscation_lib.identifier_manager import IdentifierManager
    from Qobfuscation_lib.decoy_generator import DecoyCodeGenerator

except ImportError:
    from quantum_engines import SmartNoiseGenerator, generate_deterministic_circuit
    from utils import load_data_from_json
    from code_splitter import IntelligentCodeSplitter
    from identifier_manager import IdentifierManager
    from decoy_generator import DecoyCodeGenerator


class ObfuscationError(Exception):
    """Raised when obfuscation fails."""
    pass


def _load_inverse_pairs_bank() -> str:
    try:
        data = load_data_from_json("inverse.json") or []
        return repr(data)
    except Exception:
        return "[]"


def _generate_deterministic_circuit_instructions(qc_var_name: str) -> Tuple[str, str, int, int]:
    """
    Generates Python code instructions for a deterministic circuit.

    Uses the simplified `generate_deterministic_circuit()` to get a circuit,
    then converts it to executable Python code lines ready for template injection.

    Returns:
        tuple:
            instructions (str): indented code lines for circuit gates
            expected_outcome (str): deterministic target bitstring
            num_qubits (int): number of qubits
            num_clbits (int): number of classical bits
    """
    try:
        qc, expected_outcome = generate_deterministic_circuit()
        num_qubits = qc.num_qubits
        num_clbits = qc.num_clbits

        code_lines = _sequence_to_code_lines(qc, var_name=qc_var_name)
        instructions = "    " + "\n    ".join(code_lines)

        return instructions, expected_outcome, num_qubits, num_clbits

    except Exception as e:
        fallback_instructions = f"    # [!] CRITICAL: Failed to generate circuit instructions. Error: {e}"
        return fallback_instructions, "0", 1, 1



def _prepare_injected_code(src: str, algo: str, indent_part1: int = 8, indent_part2: int = 12) -> Dict[str, Any]:
    """
    Prepare code for injection, now using the robust AST-based splitter.
    """
    indented_code = textwrap.indent(src.rstrip() + "\n", " " * indent_part1)

    if algo == "shroud":
        splitter = IntelligentCodeSplitter()
        part1, part2 = splitter.split(src)
        return {
            "indented_code": indented_code,
            "indented_code_part1": textwrap.indent(part1 + "\n", " " * indent_part1),
            "indented_code_part2": textwrap.indent(part2 + "\n", " " * indent_part2),
        }

    return {
        "indented_code": indented_code,
        "indented_code_part1": indented_code,
        "indented_code_part2": indented_code,
    }

def _format_param(p) -> str:
    """
    Formats gate parameters as high-precision floating-point numbers
    to increase obscurity for human analysis.
    """
    if not isinstance(p, (float, int)):
        return str(p)

    try:
        return f"{float(p):.15f}"
    except Exception:
        return str(p)

def _sequence_to_code_lines(qc: QuantumCircuit, var_name: str = "qc") -> List[str]:
    """
    Convert QuantumCircuit instructions (qc.data) into executable Python code lines.
    Example:
        qc.h(0)
        qc.rx(pi/2, 1)
        qc.cx(0, 1)
    Args:
        qc (QuantumCircuit): circuit to export
        var_name (str): variable name to use instead of 'qc'
    """
    lines = []
    for instr, qargs, cargs in qc.data:
        if hasattr(instr, "operation"):
            op = instr.operation
        else:
            op = instr

        opname = getattr(op, "name", str(op))
        qubit_indices = [qc.qubits.index(q) for q in qargs]
        clbit_indices = [qc.clbits.index(c) for c in cargs]

        params = []
        if getattr(op, "params", None):
            params = [_format_param(p) for p in op.params]

        args = params + [str(q) for q in qubit_indices] + [str(c) for c in clbit_indices]

        arg_str = ", ".join(args)
        if arg_str:
            lines.append(f"{var_name}.{opname}({arg_str})")
        else:
            lines.append(f"{var_name}.{opname}()")

    return lines



def _generate_noise(target_qubits=None, repeats: int = 1, level: str = None,var_name: str = "qc") -> str:
    if target_qubits is None:
        target_qubits = [0]
    if isinstance(target_qubits, int):
        target_qubits = [target_qubits]

    noise_generator = SmartNoiseGenerator()
    snippets = []

    for _ in range(max(1, repeats)):
        chosen_level = level or random.choice(['light', 'medium', 'heavy'])
        num_qubits = max(target_qubits) + 1 if target_qubits else 1
        qc_tmp = QuantumCircuit(num_qubits)

        try:
            noise_generator.inject(qc_tmp, list(target_qubits), level=chosen_level)
        except Exception:
            for q in target_qubits:
                qc_tmp.h(q)

        lines = _sequence_to_code_lines(qc_tmp, var_name=var_name)
        snippets.append("\n    ".join(lines))

    final = "\n    ".join(snippets)

    return final



def obfuscate_file(file_path: str, algo: str) -> Tuple[str, str]:
    """
    Obfuscate a Python file using a quantum-inspired template.

    Args:
        file_path (str): Path to the original Python file.
        algo (str): Template key (simple_entanglement, variable_pairs, shroud, deterministic).

    Returns:
        (output_path, obfuscated_text)
    """
    if algo not in TEMPLATES:
        raise ObfuscationError(
            f"Unknown algo '{algo}'. Available: {list(TEMPLATES.keys())}"
        )

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        manager = IdentifierManager()
        src = manager.rename_identifiers(f.read())
        target = [0]
        target2 = 0
        target3 = 0
        repeats = 1

    if algo == "simple_entanglement":
        target = [0, 1]
        repeats = 2

    elif algo == "variable_pairs":
        target = [0, 1, 2]
        repeats = 2

    elif algo == "shroud":
        target = [0]
        repeats = 1

    elif algo == "deterministic":
        target = 0
        target2 = 1
        target3 = 2
        repeats = 1

    else:
        target = [0]
        repeats = 1

    var_name = DecoyCodeGenerator._get_random_identifier("casss")
    noise_snippet = _generate_noise(target_qubits=target, repeats=repeats, level=None,var_name=var_name)
    noise_snippet2 = _generate_noise(target_qubits=target2, repeats=repeats, level=None,var_name=var_name)
    noise_snippet3 = _generate_noise(target_qubits=target3, repeats=repeats, level=None,var_name=var_name)

    subs: Dict[str, Any] = {
        "NoiseGenerator": noise_snippet,
        "NoiseGenerator2": noise_snippet2,
        "NoiseGenerator3": noise_snippet3,
        "expected_outcome": "0",
        "random_method": DecoyCodeGenerator.generate_random_method(),
        "rand_var1": DecoyCodeGenerator._get_random_identifier(),
        "rand_var2": DecoyCodeGenerator._get_random_identifier("val"),
        "rand_var3": DecoyCodeGenerator._get_random_identifier(),
        "rand_result": DecoyCodeGenerator._get_random_identifier("res"),
        "outcome_var": DecoyCodeGenerator._get_random_identifier("dsa"),
        "trigger_func": DecoyCodeGenerator._get_random_identifier("func"),
        "pattern_var": DecoyCodeGenerator._get_random_identifier("pattern"),
        "qc": var_name,
        "rand_id": DecoyCodeGenerator._get_random_identifier("ctx"),
        "main": DecoyCodeGenerator._get_random_identifier(),

    }
    subs.update(_prepare_injected_code(src, algo))

    if algo == "deterministic":
        (
            instructions,
            outcome,
            qubits,
            clbits,
        ) = _generate_deterministic_circuit_instructions(subs["qc"])

        subs["circuit_build_instructions"] = instructions
        subs["expected_outcome"] = outcome
        subs["num_qubits"] = qubits
        subs["num_clbits"] = clbits
    try:
        filled = TEMPLATES[algo].format(**subs)
    except KeyError as e:
        raise ObfuscationError(f"Template missing key: {e}")

    header = (
        "# ======================================================================\n"
        f"# Obfuscated from: {os.path.basename(file_path)}\n"
        f"# Template: {algo}\n"
        f"# Generated: {datetime.datetime.now().isoformat()}\n"
        "# ======================================================================\n\n"
    )
    obfuscated_text = header + filled

    base, ext = os.path.splitext(file_path)
    output_path = f"{base}_obf_{algo}{ext}"
    with open(output_path, "w", encoding="utf-8") as outf:
        outf.write(obfuscated_text)

    return output_path, obfuscated_text


SIMPLE_ENTANGLEMENT_TEMPLATE = """
# OBFUSCATED SCRIPT (Control Flow: Simple Entanglement with Deceptive Branches)
import qiskit, random, math,time, datetime, hashlib
from qiskit_aer import AerSimulator

{random_method}

def {trigger_func}():
    {qc} = qiskit.QuantumCircuit(2, 2)
    {NoiseGenerator}
    {qc}.h(0)
    {NoiseGenerator}
    
    {qc}.cx(0, 1)
    {qc}.measure([0, 1], [0, 1])
    {rand_result} = AerSimulator().run(qiskit.transpile({qc}, AerSimulator()), shots=1).result()
    return list({rand_result}.get_counts().keys())[0]

def {main}():
    {outcome_var} = {trigger_func}()
    if {outcome_var} == '00':
{indented_code}
    elif {outcome_var} == '11':
{indented_code}
    elif {outcome_var} == '10':
        print("!!! CRITICAL_ERROR_LOG detected.")
        time.sleep(random.uniform(1, 2.5))
    elif {outcome_var} == '01':
        for i in range(101):
            time.sleep(0.01)
            print(f"\\r[SCAN] {{i}}%", end="")
        print("\\n!!! Process halted !!!")

if __name__ == "__main__":
    {main}()
"""


VARIABLE_PAIRS_TEMPLATE = """
# OBFUSCATED SCRIPT (Control Flow: Hidden Quantum Trap with Smart Noise)
import qiskit, random, time, math, datetime, base64, hashlib
from qiskit_aer import AerSimulator

{random_method}

def {trigger_func}():
    {rand_var1} = random.randint(3, 5)
    {rand_var2} = {rand_var1} * 2
    {pattern_var} = ''.join(random.choice(['0','1']) for _ in range({rand_var2}))
    {qc} = qiskit.QuantumCircuit({rand_var2}, {rand_var2})
    {NoiseGenerator}
    {NoiseGenerator}
    for i in range({rand_var1}):
        c, t = i*2, i*2+1
        {qc}.h(c); {qc}.cx(c , t)   
    {NoiseGenerator}

    {qc}.measure(range({rand_var2}), range({rand_var2}))
    {rand_result} = AerSimulator().run(qiskit.transpile({qc}, AerSimulator()), shots=1).result()
    {outcome_var} = list({rand_result}.get_counts().keys())[0]
    return {outcome_var}, {pattern_var}, {rand_var1}

def {main}():
    {outcome_var}, {pattern_var}, {rand_var1} = {trigger_func}()
    if {outcome_var} == {pattern_var}:
        _ = sum(math.sqrt(i + random.random()) for i in range(100))
    else:
{indented_code}

if __name__ == "__main__":
    {main}()
"""

SHROUD_TEMPLATE = """
# OBFUSCATED SCRIPT (Control Flow: Advanced Superposition Shroud)
import qiskit, random,math, time, datetime, hashlib
from qiskit_aer import AerSimulator

{random_method}

def {trigger_func}():
    {qc} = qiskit.QuantumCircuit(1)
    {NoiseGenerator}
    {NoiseGenerator}
    {qc}.h(0)
    {NoiseGenerator}

    {qc}.save_statevector()

    backend = AerSimulator(method="statevector")
    job = backend.run(qiskit.transpile({qc}, backend))
    result = job.result(timeout=60)
    statevector = result.get_statevector({qc})  
    return statevector

def {main}():
    {rand_var1} = {trigger_func}()

    {rand_var3} = {{'status': 'unverified', 'data': None, 'timestamp': time.time()}}

    # The first block will always execute due to superposition
    if abs({rand_var1}[0]) > 1e-9:
{indented_code_part1}
        # Simulate a successful first stage
        {rand_var3}['status'] = 'stage1_ok'
        {rand_var3}['data'] = hashlib.md5(str(random.random()).encode()).hexdigest()

    # The second block will also always execute, verifying the context from the first
    if abs({rand_var1}[1]) > 1e-9:
        if {rand_var3}['status'] == 'stage1_ok' and {rand_var3}['data'] is not None:
{indented_code_part2}

if __name__ == "__main__":
    {main}()
"""



DETERMINISTIC_TEMPLATE = """
# OBFUSCATED SCRIPT (Control Flow: Deterministic Quantum Checksum)
import qiskit, random,math, time, datetime, hashlib
from qiskit_aer import AerSimulator

{random_method}

def {trigger_func}():
    {qc} = qiskit.QuantumCircuit({num_qubits}, {num_clbits})
    {NoiseGenerator}
{circuit_build_instructions}
    {NoiseGenerator2}
    {NoiseGenerator3}
    {rand_result} = AerSimulator().run(qiskit.transpile({qc}, AerSimulator()), shots=1).result()
    return list({rand_result}.get_counts().keys())[0]

def {main}():
    {rand_var1} = "SESSION_ID:" + str(random.randint(10000, 99999))
    {rand_var2} = time.time()

    {outcome_var} = {trigger_func}()

    # Payload executes only if checksum matches expected value
    if {outcome_var} == '{expected_outcome}':
{indented_code}
    else:
        # Decoy error handling to mislead analysts
        print(f"Quantum desynchronization error. Checksum mismatch. Expected '{expected_outcome}', got '{{{outcome_var}}}'.")
        print("Dumping quantum core state to 'core_dump.qdat' for analysis.")
        time.sleep(random.uniform(0.5, 1.5))
        with open("core_dump.qdat", "w") as f:
            f.write(f"TIMESTAMP: {{datetime.datetime.now().isoformat()}}\\n")
            f.write(f"SESSION: {{{rand_var1}}}\\n")
            f.write(f"STATUS: FATAL_Q_DESYNC\\n")
            f.write(f"EXPECTED: {expected_outcome}\\n")
            f.write(f"RECEIVED: {{{outcome_var}}}\\n")
            f.write("-- END OF DUMP --\\n")

if __name__ == "__main__":
    {main}()
"""


TEMPLATES = {
    'simple_entanglement': SIMPLE_ENTANGLEMENT_TEMPLATE,
    'variable_pairs': VARIABLE_PAIRS_TEMPLATE,
    'shroud': SHROUD_TEMPLATE,
    'deterministic': DETERMINISTIC_TEMPLATE
}
