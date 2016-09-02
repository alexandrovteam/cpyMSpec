from cpyMSpec import isotopePattern
import pytest

elements = ["Be", "H", "O", "S", "Fe", "Ni", "Kr"]

@pytest.mark.parametrize("e", elements)
def test_doubling(e):
    m1 = isotopePattern(e).masses[0]
    m2 = isotopePattern(e + "2").masses[0]
    assert abs(2 * m1 - m2) < 1e-5

print isotopePattern("Fe")
print isotopePattern("Fe2")

print isotopePattern("Fe").masses
print isotopePattern("Fe2").masses

print isotopePattern("Fe").abundances
print isotopePattern("Fe2").abundances
