from cpyMSpec import isotopePattern, centroidize

# layer of compatibility with the original pyMSpec.pyisocalc module

from pyMSpec.pyisocalc import pyisocalc
from pyMSpec.mass_spectrum import MassSpectrum

import numpy as np

def complete_isodist(sf, sigma=0.001, cutoff_perc=0.1, charge=None, pts_per_mz=10000, **kwargs):
    if charge is None:
        charge = sf.charge()

    cutoff = cutoff_perc / 100.0
    fwhm = sigma * 2.3548200450309493  # the exact ratio is 2 \sqrt{2 \log 2}
    abs_charge = max(1, abs(charge))
    p = isotopePattern(str(sf), cutoff / 10.0).charged(charge)

    mz = min(p.masses) / abs_charge
    resolution = mz / fwhm

    mzs = np.arange(min(p.masses) / abs_charge - 1,
                    max(p.masses) / abs_charge + 1, 1.0/pts_per_mz)
    intensities = np.asarray(p.envelope(resolution)(mzs * abs_charge))
    intensities *= 100.0 / intensities.max()

    ms = MassSpectrum()
    ms.add_spectrum(mzs, intensities)

    p = centroidize(mzs, intensities, 5)
    p *= 100
    p.removeIntensitiesBelow(cutoff_perc)
    p.sortByMass()
    ms.add_centroids(p.masses, p.intensities)
    return ms
