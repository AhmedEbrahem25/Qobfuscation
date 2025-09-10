# -*- coding: utf-8 -*-
import argparse
import os
import sys
from rich.console import Console

# Add the library path to Python's search paths to ensure modules can be imported
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Initialize Rich Console
console = Console()

try:
    from Qobfuscation_lib.circuit_obfuscator import CircuitObfuscator
    from Qobfuscation_lib.classical_obfuscator import obfuscate_file as obfuscate_classical_file
    from Qobfuscation_lib.banner import animated_banner
except ImportError as e:
    console.print(f"❌ [bold red]Error:[/bold red] 'Qobfuscation_lib' library was not found.")
    console.print(f"   [yellow]Hint:[/yellow] Please ensure this script is located in the project root directory, alongside 'Qobfuscation_lib'.")
    console.print(f"   [yellow]Details:[/yellow] {e}")
    sys.exit(1)


def main():
    """
    Main function to run the obfuscation tool from the command line.
    Provides support for both quantum circuit obfuscation and classical script obfuscation.
    """
    # Display the professional animated banner at startup
    animated_banner()

    parser = argparse.ArgumentParser(
        description="tool for obfuscating quantum circuits and classical scripts.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Usage examples:
-----------------
1. Quantum obfuscation of a QASM file using the 'cloaked' algorithm:
         python qobfuscator_cli.py -q -f my_circuit.qasm -a cloaked
         
2. Apply two layers of quantum obfuscation on a Python file with verbose output:
         python qobfuscator_cli.py -q -f my_circuit.py -a cloaked -a inverse -v
         
3. Classical obfuscation of a Python script using 'simple_entanglement':
        python qobfuscator_cli.py -c -f my_script.py -a simple_entanglement

Available algorithms:
- Quantum (-q): cloaked, inverse, delayed, composite
- Classical (-c): simple_entanglement, variable_pairs, shroud, deterministic
"""
    )

    # --- File input and general settings ---
    parser.add_argument('-f', '--file', required=True,
                        help='Path to the file to be obfuscated (.qasm or .py).')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose mode to display detailed information during execution.')

    # --- Obfuscation type selection (Quantum or Classical) ---
    obfuscation_type = parser.add_mutually_exclusive_group(required=True)
    obfuscation_type.add_argument('-q', '--quantum', action='store_true',
                                  help='Apply obfuscation at the quantum circuit level.')
    obfuscation_type.add_argument('-c', '--classical', action='store_true',
                                  help='Apply obfuscation at the classical script level (code wrapping).')

    # --- Algorithm selection ---
    parser.add_argument('-a', '--algo', required=True, action='append',
                        help='Name of the obfuscation algorithm to apply. '
                             'Can be specified multiple times for multi-layer quantum obfuscation.')

    args = parser.parse_args()
    # --- ADD THIS VALIDATION BLOCK ---
    VALID_QUANTUM_ALGOS = ['cloaked', 'inverse', 'delayed', 'composite']
    VALID_CLASSICAL_ALGOS = ['simple_entanglement', 'variable_pairs', 'shroud', 'deterministic']

    if args.quantum:
        for algo in args.algo:
            if algo not in VALID_QUANTUM_ALGOS:
                console.print(
                    f"❌ [bold red]Validation Error:[/bold red] Algorithm '[bold]{algo}[/bold]' is not a valid QUANTUM algorithm.")
                console.print(
                    f"   [yellow]Hint: Available quantum algorithms are:[/yellow] {', '.join(VALID_QUANTUM_ALGOS)}")
                return  # Exit the program

    elif args.classical:
        if args.algo[0] not in VALID_CLASSICAL_ALGOS:
            console.print(
                f"❌ [bold red]Validation Error:[/bold red] Algorithm '[bold]{args.algo[0]}[/bold]' is not a valid CLASSICAL algorithm.")
            console.print(
                f"   [yellow]Hint: Available classical algorithms are:[/yellow] {', '.join(VALID_CLASSICAL_ALGOS)}")
            return  # Exit the program
    # --- Validate that the target file exists ---
    if not os.path.exists(args.file):
        console.print(f"❌ [bold red]Error:[/bold red] File '[bold]{args.file}[/bold]' does not exist.")
        return

    console.print(f"\n[*] [bold bright_blue]Starting obfuscation[/bold bright_blue] for file: [white]{args.file}[/white]")

    # --- Quantum obfuscation logic ---
    if args.quantum:
        console.print(f"[*] [bold bright_cyan]Obfuscation type:[/bold bright_cyan] Quantum Circuit Obfuscation")
        console.print(f"[*] [bold magenta]Applied algorithms:[/bold magenta] {', '.join(args.algo)}")

        # Prepare list of techniques as tuples (name, config_dict)
        techniques = [(algo_name, {}) for algo_name in args.algo]

        try:
            obfuscator = CircuitObfuscator(verbose=args.verbose)
            obfuscator.obfuscate(args.file, techniques)
        except Exception as e:
            console.print(f"❌ [bold red]Unexpected error occurred during quantum obfuscation:[/bold red] {e}")

    # --- Classical obfuscation logic ---
    elif args.classical:
        if len(args.algo) > 1:
            console.print("⚠️ [bold yellow]Warning:[/bold yellow] Classical obfuscation supports only one algorithm at a time. "
                          "Only the first algorithm will be applied.")

        algo_name = args.algo[0]
        console.print(f"[*] [bold bright_cyan]Obfuscation type:[/bold bright_cyan] Classical Script Obfuscation")
        console.print(f"[*] [bold magenta]Applied algorithm:[/bold magenta] {algo_name}")

        try:
            obfuscate_classical_file(args.file, algo_name)
        except Exception as e:
            console.print(f"❌ [bold red]Unexpected error occurred during classical obfuscation:[/bold red] {e}")


if __name__ == '__main__':
    main()