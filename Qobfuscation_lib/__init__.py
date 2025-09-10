# Qobfuscation_lib/__init__.py

"""
Qobfuscation Library
"""

# Make key classes and functions available at the package level
from .circuit_obfuscator import CircuitObfuscator
from .classical_obfuscator import obfuscate_file as obfuscate_classical_file
from .quantum_engines import SmartNoiseGenerator, generate_deterministic_circuit
from .utils import load_data_from_json, apply_gate_from_token, export_circuit_to_py
from .code_splitter import IntelligentCodeSplitter
from .identifier_manager import IdentifierManager
from .decoy_generator import DecoyCodeGenerator

__version__ = "1.0.0"
__author__ = "0xVnex"
