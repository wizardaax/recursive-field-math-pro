from .utils import lucas

def harmonic_balance(digests):
    balanced = []
    for i, d in enumerate(digests):
        h = lucas(i)
        b = bytes((x + h) % 256 for x in d)
        balanced.append(b)
    return balanced
