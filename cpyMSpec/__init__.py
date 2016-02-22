import cffi

from .utils import shared_lib, full_filename

ffi = cffi.FFI()
ffi.cdef(open(full_filename("ims.h")).read())
ims = ffi.dlopen(full_filename(shared_lib("ms_cffi")))

def _raise_ims_exception():
    raise Exception(ffi.string(ims.ims_strerror()))

def _raise_ims_exception_if_null(arg):
    if arg == ffi.NULL:
        _raise_ims_exception()

class IsotopePattern(object):
    """
    Stores information about isotopic peaks of a molecule.

    Example of usage:

    ::

        p = IsotopePattern("C5H5N5O").charged(1)
        print p.centroids(resolution=200000).trimmed(5)
    """

    def __init__(self, sum_formula, threshold=1e-4, fft_threshold=1e-8):
        """
        Calculates isotopic peaks for a sum formula.

        :param sum_formula: text representation of an atomic composition
        :type sum_formula: str
        :param threshold: minimal abundance to keep in the final results
        :param fft_threshold: minimal abundance to keep in intermediate
        results (for each of the distinct atomic species)
        """
        p = ims.isotope_pattern_new_from_sf(sum_formula, threshold, fft_threshold)
        _raise_ims_exception_if_null(p)
        self.ptr = ffi.gc(p, ims.isotope_pattern_free)

    def __str__(self):
        assert self.ptr != ffi.NULL
        peaks = sorted(zip(self.masses, self.abundances),
                       key=lambda x: x[0])
        return "{\n  " +\
            ",\n  ".join("{0: >9.4f}: {1: >8.4f}%".format(x[0], x[1] * 100) for x in peaks) +\
            "\n}"

    def copy(self):
        """
        :returns: a (deep) copy of the instance
        :rtype: IsotopePattern
        """
        obj = object.__new__(IsotopePattern)
        obj.ptr = ffi.gc(ims.isotope_pattern_copy(self.ptr),
                         ims.isotope_pattern_free)
        return obj

    def centroids(self, resolution, min_abundance=1e-4, points_per_fwhm=25):
        """
        Estimates centroided peaks at a given resolution.

        :param resolution: peak resolution, i.e. m/z value divided by FWHM
        :param min_abundance: minimum abundance for including a peak
        :param points_per_fwhm: grid density used for envelope calculation
        :returns: peaks visible at the specified resolution
        :rtype: IsotopePattern
        """
        obj = object.__new__(IsotopePattern)
        centroids = ims.isotope_pattern_centroids(self.ptr, resolution,
                                                  min_abundance, points_per_fwhm)
        _raise_ims_exception_if_null(centroids)
        obj.ptr = ffi.gc(centroids, ims.isotope_pattern_free)
        return obj

    def size(self):
        """
        :returns: number of peaks in the pattern
        :rtype: int
        """
        return ims.isotope_pattern_size(self.ptr)

    @property
    def masses(self):
        """
        :returns: masses of isotopes
        :rtype: list of floats
        """
        buf = ffi.new("double[]", self.size())
        ims.isotope_pattern_masses(self.ptr, buf)
        return list(buf)

    @property
    def abundances(self):
        """
        Returns isotopic abundances for each peak,
        sorted in descending order, with largest abundancy
        scaled to 1.0.

        :returns: isotopic abundances
        :rtype: list of floats
        """
        buf = ffi.new("double[]", self.size())
        ims.isotope_pattern_abundances(self.ptr, buf)
        return list(buf)

    def addCharge(self, charge):
        """
        Adds/subtracts electrons in-place.

        :param charge: number of electrons to add
        :type charge: integer
        """
        ims.isotope_pattern_add_charge(self.ptr, charge)

    def charged(self, charge):
        """
        Adds/subtracts electrons and returns a new object.

        :param charge: number of electrons to add
        :type charge: integer
        :returns: an isotope pattern with appropriately shifted masses
        :rtype: IsotopePattern

        """
        result = self.copy()
        result.addCharge(charge)
        return result

    def trim(self, n_peaks):
        """
        Removes low-intensity peaks from the pattern.

        :param n_peaks: number of peaks to keep
        """
        ims.isotope_pattern_trim(self.ptr, n_peaks)

    def trimmed(self, n_peaks):
        """
        :param n_peaks: number of peaks to keep
        :returns: an isotope pattern with removed low-intensity peaks
        :rtype: IsotopePattern
        """
        result = self.copy()
        result.trim(n_peaks)
        return result

    def envelope(self, resolution):
        """
        Computes isotopic envelope at a specified resolution

        :param resolution: peak resolution
        :returns: isotopic envelope as a function of mass
        :rtype: function float(mz: float)

        """
        def envelopeFunc(mz):
            return ims.isotope_pattern_envelope(self.ptr, resolution, mz)
        return envelopeFunc
