import random
import string


class DecoyCodeGenerator:
    """
    A collection of static methods to generate random, plausible-looking
    Python code snippets for use as decoys in obfuscation.
    """
    @staticmethod
    def _get_random_identifier(prefix: str = "var", length: int = 8) -> str:
        """Generates a random, safe Python identifier."""
        letters = string.ascii_letters + string.digits
        suffix = ''.join(random.choice(letters) for _ in range(length))
        return f"{prefix}_{suffix}"

    @staticmethod
    def generate_random_method() -> str:
        """
        Generates a random dummy Python function as a string.
        """
        func_name = DecoyCodeGenerator._get_random_identifier("func", 6)
        var1 = DecoyCodeGenerator._get_random_identifier("tmp", 4)
        var2 = DecoyCodeGenerator._get_random_identifier("tmp", 4)

        code = f"""
def {func_name}():
    {var1} = random.randint(1, 999)
    {var2} = hashlib.sha256(str({var1}).encode()).hexdigest()
    return {var2}[:8]
"""
        return code.strip()

    @staticmethod
    def generate_random_variable_assignment() -> str:
        """
        Generates a random variable assignment snippet as a string.
        """
        var_name = DecoyCodeGenerator._get_random_identifier("data", 5)
        expr = random.choice([
            "random.randint(1, 1000)",
            "time.time()",
            "hashlib.md5(str(random.random()).encode()).hexdigest()",
            "datetime.datetime.utcnow().isoformat()"
        ])
        return f"{var_name} = {expr}"