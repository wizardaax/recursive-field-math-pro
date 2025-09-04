import math

PHI = (1 + math.sqrt(5)) / 2
GOLDEN_ANGLE_RAD = 2 * math.pi * (1 - 1 / PHI)

def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a
