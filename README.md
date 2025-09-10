<div align="center">
<br />
<h1>Qobfuscation</h1>
<strong>A powerful, quantum-inspired obfuscation framework for Python scripts and quantum circuits.</strong>
<br />
<br />
</div>

Qobfuscation is a state-of-the-art framework designed to apply sophisticated obfuscation techniques derived from quantum computing principles. It provides a dual-mode command-line interface (CLI) to secure both classical Python scripts and quantum circuits, enhancing their complexity to deter reverse engineering and analysis.

## Key Features

### Dual-Mode Obfuscation

- **Quantum Circuit Obfuscation**: Increases the complexity of quantum circuits (.qasm, .py) by applying noise and gate substitution without altering the final state vector.

- **Classical Script Obfuscation**: Wraps standard Python code within a quantum-inspired control-flow guard, making execution contingent on the outcome of a simulated quantum circuit.

### Layered Security
Apply multiple, distinct obfuscation algorithms sequentially to a single quantum circuit for exponentially increased complexity.

### Fine-Grained Control
A professional CLI allows for precise customization of algorithm parameters (e.g., noise density, gate substitution probability) to tailor the obfuscation level.

### Advanced Techniques
Implements a variety of obfuscation methods, from simple noise injection to complex, deterministic quantum checksums that act as a trigger for code execution.

### Extensible & Professional
Built with a clean architecture, a rich CLI experience, and detailed feedback for professional use cases.

## Installation
Ensure you have Python 3.8+ installed. Then, follow these steps to set up the framework.

Clone the Repository:

```bash
git clone https://github.com/AhmedEbrahem25/Qobfuscation.git
cd Qobfuscation
```

Install Dependencies:

```bash
pip install -r requirements.txt
```

The tool is now ready for use.

## Usage Guide
The framework is operated via `qobfuscator_cli.py`. All commands follow a standard syntax.

### 🔷 Quantum Circuit Obfuscation
Used to obfuscate quantum circuits. Activate this mode with the `-q` or `--quantum` flag.

**Example 1: Single-Layer Obfuscation**
```bash
# Apply the 'cloaked' algorithm to a QASM file
python qobfuscator_cli.py -q -f my_circuit.qasm -a cloaked
```

**Example 2: Multi-Layer Obfuscation with Custom Parameters**
```bash
# Apply two layers with specified density and probability, enabling verbose output
python qobfuscator_cli.py -q -f circuit.py -a "inverse:density=0.4" -a "cloaked:probability=0.8" -v
```

### 🔶 Classical Script Obfuscation
Used to wrap and protect Python scripts. Activate this mode with the `-c` or `--classical` flag.

**Example 1: Using a Simple Entanglement Guard**
```bash
# Obfuscate a Python script using the 'simple_entanglement' wrapper
python qobfuscator_cli.py -c -f my_script.py -a simple_entanglement
```

**Example 2: Using a Deterministic Checksum Guard**
```bash
# Obfuscate critical logic with a deterministic guard and specify an output file
python qobfuscator_cli.py -c -f critical_logic.py -a deterministic -o secured_logic.py
```

### 📖 Global Options
- **Full Help & Algorithm List:**
```bash
python qobfuscator_cli.py --help
```

- **Verbose Mode**: Enable detailed execution logging with the `-v` flag.

- **Specify Output File**: Use the `-o <path/to/output_file.py>` argument to define a custom output path.

## Available Obfuscation Techniques

| Mode      | Technique Name       | Description |
|-----------|----------------------|-------------|
| Quantum   | cloaked              | Replaces gates with equivalent but functionally obscure sequences. |
| Quantum   | inverse              | Injects inverse gate pairs (structured noise) to increase circuit depth. |
| Quantum   | delayed              | Substitutes gates with more complex identity sequences. |
| Quantum   | composite            | Inserts composite identity sequences at random insertion points. |
| Classical | simple_entanglement  | Execution depends on the measurement outcome of a simple Bell state. |
| Classical | variable_pairs       | Creates a complex entangled state to use as a conditional trigger. |
| Classical | shroud               | Utilizes superposition to ensure two separate code blocks are executed. |
| Classical | deterministic        | Executes the payload only if a quantum circuit's output matches a hardcoded checksum. |

## License
This project is distributed under the MIT License. See the LICENSE file for more information.
