from cpyMSpec import IsotopePattern, centroidize

import pytest

def assert_patterns_almost_equal(p1, p2):
    peaks1 = zip(p1.masses, p1.abundances)
    peaks2 = zip(p2.masses, p2.abundances)
    assert_peaks_almost_equal(peaks1[:5], peaks2[:5])

def assert_peaks_almost_equal(peaks1, peaks2):
    for (m1, a1), (m2, a2) in zip(peaks1, peaks2):
        assert abs(m1 - m2) < 1e-4
        assert abs(a1 - a2) < 1e-3

formulas = ["C5H8O13Cl", "C3H5O7", "Fe2Cl3K5H7", "C44H28O32K", "C18Cl5Na3H22"]

@pytest.mark.parametrize("f", formulas)
@pytest.mark.parametrize("resolution", [10000, 30000, 50000, 80000, 100000])
def test_centroiding(f, resolution):
    p = IsotopePattern(f, threshold=1e-7)
    p1 = p.centroids(resolution, points_per_fwhm=500)
    min_mz = min(p1.masses)
    max_mz = max(p1.masses)
    step = 5e-5
    n_pts = int((max_mz + 2 - min_mz) / step)
    mzs = [min_mz - 1 + step * i for i in range(n_pts)]
    p2 = centroidize(mzs, p.envelope(resolution)(mzs), window_size=15)
    assert_patterns_almost_equal(p1, p2)

@pytest.mark.parametrize("f", formulas)
def test_centroids_at_large_resolution(f):
    p1 = IsotopePattern(f)
    p2 = p1.centroids(1e7)
    assert_patterns_almost_equal(p1, p2)

@pytest.mark.parametrize("f", formulas)
@pytest.mark.parametrize("threshold", [1e-7, 1e-5, 1e-3])
def test_thresholding(f, threshold):
    p = IsotopePattern(f).centroids(100000, min_abundance=threshold)
    for a in p.abundances:
        assert a >= threshold
