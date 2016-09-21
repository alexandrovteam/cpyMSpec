from cpyMSpec import isotopePattern
import pytest

elements = ["Be", "H", "O", "S", "Fe", "Ni", "Kr"]

@pytest.mark.parametrize("e", elements)
def test_doubling(e):
    m1 = isotopePattern(e).masses[0]
    m2 = isotopePattern(e + "2").masses[0]
    assert abs(2 * m1 - m2) < 1e-5
