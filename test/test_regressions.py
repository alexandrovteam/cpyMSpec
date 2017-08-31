import cpyMSpec
import numpy as np

def test_duplicate_peaks():
    p = cpyMSpec.isotopePattern("OBr")
    assert len(p.masses) == len(np.unique(p.masses))
