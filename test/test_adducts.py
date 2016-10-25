from cpyMSpec import isotopePattern

import pytest

formula = "C5H3OH"

def mz(formula):
    return isotopePattern(formula).masses[0]

def test_adducts():
    assert (mz(formula + "+H") - mz(formula) - mz("H")) < 1e-6
    assert (mz(formula + "+H-C") - mz(formula) - mz("H") + mz("C")) < 1e-6
