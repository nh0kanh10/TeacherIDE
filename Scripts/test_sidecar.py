# Test file for sidecar lesson feature
def calculate_sum(a, b):
    # Intentional bug: using multiplication instead of addition
    return a * b  # Line 4: Bug here

if __name__ == "__main__":
    result = calculate_sum(5, 3)
    print(f"Sum: {result}")  # Expected 8, got 15
