import math

# ==========================
# Class Example
# ==========================
class Calculator:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def add(self):
        return self.a + self.b

    def multiply(self):
        return self.a * self.b

    def sine_of_sum(self):
        return math.sin(self.a + self.b)


# ==========================
# Function Examples
# ==========================
def generate_numbers():
    """Return fixed numbers"""
    return [10, 20]  # fixed numbers, same every run


def print_squares(n=5):
    """Print squares of the first n numbers"""
    print(f"Squares of first {n} numbers:")
    for i in range(1, n + 1):
        print(f"{i}^2 = {i * i}")


# ==========================
# Main Test Function
# ==========================
def main_test():
    print("=== Test Program: Functions, Classes, Variables ===")

    a, b = generate_numbers()
    print(f"Generated numbers: a={a}, b={b}")

    calc = Calculator(a, b)
    print(f"{a} + {b} = {calc.add()}")
    print(f"{a} * {b} = {calc.multiply()}")
    print(f"sin({a}+{b}) = {calc.sine_of_sum():.3f}")

    print_squares(5)
    print("=== End of Test Program ===")


# ==========================
# Run the Test
# ==========================
if __name__ == "__main__":
    main_test()
