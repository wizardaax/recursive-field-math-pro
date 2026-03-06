from recursive_field_math import (
    ROOT_SCALE,
    F,
    L,
    egypt_4_7_11,
    r_theta,
    ratio,
    ratio_error_bounds,
    signature_summary,
)

# Expected Lucas numbers L(0)..L(5): initial conditions L(0)=2, L(1)=1, recurrence L(n)=L(n-1)+L(n-2)
EXPECTED_LUCAS = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11}


def test_basic_sequences():
    assert F(0) == 0
    assert F(1) == 1
    for n, val in EXPECTED_LUCAS.items():
        assert L(n) == val


def test_field():
    r1, th1 = r_theta(1)
    assert r1 == ROOT_SCALE  # r1 == ROOT_SCALE * sqrt(1)


def test_ratio_bounds():
    r = ratio(5)
    lo, hi = ratio_error_bounds(5)
    assert lo > 0 and hi > lo
    assert r > 1


def test_egypt_and_signature():
    num, den = egypt_4_7_11()
    sig = signature_summary()
    # 1/4 + 1/7 + 1/11 = pair_sum / product  (149/308)
    assert num == sig["pair_sum"]
    assert den == sig["product"]
    assert sig["L3"] == EXPECTED_LUCAS[3]
    assert sig["L4"] == EXPECTED_LUCAS[4]
    assert sig["L5"] == EXPECTED_LUCAS[5]
