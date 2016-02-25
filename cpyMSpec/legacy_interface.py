from cpyMSpec import IsotopePattern, centroidize

# layer of compatibility with the original pyMS.pyisocalc module

from pyMS.pyisocalc import pyisocalc
from pyMS.mass_spectrum import MassSpectrum

import numpy as np

def complete_isodist(sf, sigma=0.001, cutoff_perc=0.1, charge=None, pts_per_mz=10000, **kwargs):
    if charge is None:
        charge = sf.charge()

    cutoff = cutoff_perc / 100.0
    fwhm = sigma * 2.3548200450309493  # the exact ratio is 2 \sqrt{2 \log 2}
    abs_charge = max(1, abs(charge))
    p = IsotopePattern(str(sf), cutoff / 10.0).charged(charge)

    mz = min(p.masses) / abs_charge
    resolution = mz / fwhm

    mzs = np.arange(min(p.masses) / abs_charge - 1,
                    max(p.masses) / abs_charge + 1, 1.0/pts_per_mz)
    intensities = p.envelope(resolution)(mzs * abs_charge)

    ms = MassSpectrum()
    ms.add_spectrum(np.asarray(mzs), np.asarray(intensities) * 100.0)

    p = centroidize(mzs, intensities, 5)
    mzs, intensities = np.asarray(p.masses), 100.0 * np.asarray(p.abundances)
    order = np.argsort(mzs)
    mzs, intensities = mzs[order], intensities[order]
    retain = intensities > cutoff_perc
    ms.add_centroids(mzs[retain], intensities[retain])
    return ms
