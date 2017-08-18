from cpyMSpec import isotopePattern, ProfileSpectrum, InstrumentModel

import pytest

def assert_patterns_almost_equal(p1, p2, instr):
    peaks1 = list(zip(p1.masses, p1.intensities))
    peaks2 = list(zip(p2.masses, p2.intensities))
    assert_peaks_almost_equal(peaks1[:5], peaks2[:5], instr)

def assert_peaks_almost_equal(peaks1, peaks2, instr):
    for (m1, a1), (m2, a2) in zip(peaks1, peaks2):
        ppm = m1 / instr.resolvingPowerAt(m1)
        assert abs((m1 - m2) / m1) < 0.1 * ppm
        assert abs((a1 - a2) / a2) < 1e-3

formulas = ["C5H8O13Cl", "C3H5O7", "Fe2Cl3K5H7", "C44H28O32K", "C18Cl5Na3H22"]

@pytest.mark.parametrize("f", formulas)
@pytest.mark.parametrize("resolution", [10000, 30000, 50000, 80000, 100000])
def test_centroiding(f, resolution):
    p = isotopePattern(f, 0.9999999)
    instr = InstrumentModel('tof', resolution)
    p1 = p.centroids(instr, points_per_fwhm=500)
    min_mz = min(p1.masses)
    max_mz = max(p1.masses)
    step = 5e-5
    n_pts = int((max_mz + 2 - min_mz) / step)
    mzs = [min_mz - 1 + step * i for i in range(n_pts)]
    p2 = ProfileSpectrum(mzs, p.envelope(instr)(mzs)).centroids(window_size=15)
    assert_patterns_almost_equal(p1, p2, instr)

@pytest.mark.parametrize("f", formulas)
@pytest.mark.parametrize("threshold", [1e-7, 1e-5, 1e-3])
def test_thresholding(f, threshold):
    instr = InstrumentModel('tof', 100000)
    p = isotopePattern(f).centroids(instr, min_abundance=threshold)
    for a in p.intensities:
        assert a >= threshold
