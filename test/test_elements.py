from cpyMSpec import IsotopePattern
import pytest

elements = ["Be", "H", "O", "S", "Fe", "Ni", "Kr"]

@pytest.mark.parametrize("e", elements)
def test_doubling(e):
    m1 = IsotopePattern(e).masses[0]
    m2 = IsotopePattern(e + "2").masses[0]
    assert abs(2 * m1 - m2) < 1e-5

print IsotopePattern("Fe")
print IsotopePattern("Fe2")

print IsotopePattern("Fe").masses
print IsotopePattern("Fe2").masses

print IsotopePattern("Fe").abundances
print IsotopePattern("Fe2").abundances
