from cpyMSpec import isotopePattern

import pytest

formulas = ["H", "O", "C", "S", "P", "N", "Fe", "Na", "K"]
spectra = [isotopePattern(f) for f in formulas]

@pytest.mark.parametrize("s1", spectra)
@pytest.mark.parametrize("s2", spectra)
def test_addition(s1, s2):
    s = s1 + s2
    assert sorted(s1.masses + s2.masses) == s.sortedByMass().masses
    assert sorted(s1.intensities + s2.intensities) == s.sortedByIntensity().intensities[::-1]

@pytest.mark.parametrize("s", spectra)
def test_scaling(s):
    s2 = s * 42
    assert max(s.intensities) == 1
    assert max(s2.intensities) == 42
