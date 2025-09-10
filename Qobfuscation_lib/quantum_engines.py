import random
from qiskit import QuantumCircuit

# Import utilities from the same package
from .utils import apply_gate_from_token, load_data_from_json


# ==============================================================================
# == ⚙️ 1. THE NOISE ENGINE ⚙️
# ==============================================================================

class SmartNoiseGenerator:
    """
    A context-aware noise generator for quantum circuit obfuscation.
    It loads inverse gate sequences from a JSON database and categorizes them
    into tiers (light, medium, heavy) based on complexity.
    """

    def __init__(self):
        self.full_bank = load_data_from_json('inverse.json')
        if not self.full_bank:
            raise ValueError("Inverse pairs data could not be loaded or is empty.")
        self._categorize_noise()

    def _categorize_noise(self):
        """
        Categorizes noise sequences into tiers based on sequence length:
        - Light:   2–4 gates
        - Medium:  5–8 gates
        - Heavy:   9+ gates
        If a tier is empty, it falls back to the full gate bank.
        """
        self.noise_tiers = {
            'light': [s for s in self.full_bank if 2 <= len(s) <= 4],
            'medium': [s for s in self.full_bank if 5 <= len(s) <= 8],
            'heavy': [s for s in self.full_bank if len(s) > 8]
        }
        for tier in ['light', 'medium', 'heavy']:
            if not self.noise_tiers[tier]:
                self.noise_tiers[tier] = self.full_bank

    def inject(self, qc, target_qubits, level='medium'):
        """
        Injects a noise sequence into the given quantum circuit.
        **Version 2: Now with a robust fallback mechanism.**
        """
        if isinstance(target_qubits, int):
            target_qubits = [target_qubits]

        candidate_bank = self.noise_tiers.get(level, self.noise_tiers['light'])
        num_targets = len(target_qubits)

        # 1. Primary smart selection loop
        sequence = None
        for _ in range(50):  # Try up to 50 times
            candidate_sequence = random.choice(candidate_bank)
            requires_multi_qubit = any('cx' in g or 'cz' in g or 'swap' in g for g in candidate_sequence)

            if requires_multi_qubit and num_targets < 2:
                continue  # Skip if sequence needs 2+ qubits but we only have 1

            sequence = candidate_sequence
            break

        # 2. Robust Fallback Mechanism
        if sequence is None:
            # If the primary loop failed, we now guarantee a valid selection from the light tier.
            fallback_bank = self.noise_tiers['light']

            max_fallback_attempts = 200  # Prevent infinite loops
            for i in range(max_fallback_attempts):
                candidate_sequence = random.choice(fallback_bank)
                requires_multi_qubit = any('cx' in g or 'cz' in g or 'swap' in g for g in candidate_sequence)

                if not requires_multi_qubit or (requires_multi_qubit and num_targets >= 2):
                    sequence = candidate_sequence
                    break

            # If after all attempts we still fail, raise an error to prevent silent corruption
            if sequence is None:
                raise RuntimeError(
                    f"NoiseGenerator failed to find a compatible noise sequence for {num_targets} qubit(s). "
                    "Check your 'inverse.json' data bank."
                )

        # 3. Apply the guaranteed-to-be-valid noise sequence
        for token in sequence:
            apply_gate_from_token(qc, token, target_qubits)




def generate_deterministic_circuit():

    num_qubits = 5
    all_qubit_indices = list(range(num_qubits))

    ancilla_qubit = random.choice(all_qubit_indices)
    main_qubits = [q for q in all_qubit_indices if q != ancilla_qubit]

    qc = QuantumCircuit(num_qubits, num_qubits, name="smart_branch_obfuscator")

    target_bitstring = '1' * num_qubits

    qc.h(all_qubit_indices)
    qc.z(ancilla_qubit)

    random.shuffle(main_qubits)
    for q in main_qubits:
        qc.cx(q, ancilla_qubit)

    qc.h(all_qubit_indices)

    qc.measure(all_qubit_indices, all_qubit_indices)
    return qc, target_bitstring
