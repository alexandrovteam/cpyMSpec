from cpyMSpec import isotopePattern

import pytest

def test_invalid_sum_formula():
    for sf in ["UnknownElements", "C2HzO3", "C5:H2", "C2(H3O"]:
        with pytest.raises(Exception):
            isotopePattern(sf)

def test_too_many_combinations():
    for sf in ["Ru36", "H100000"]:
        with pytest.raises(Exception):
            isotopePattern(sf)

def test_too_few_points():
    with pytest.raises(Exception):
        isotopePattern("C2H5OH").centroids(100000, points_per_fwhm=3)

def test_invalid_min_abundance():
    with pytest.raises(Exception):
        isotopePattern("C5H5N5O").centroids(100000, min_abundance=1)

def test_unsorted_envelope_input():
    with pytest.raises(Exception):
        isotopePattern("C5H7O12").envelope(100000)([3, 1, 2])
