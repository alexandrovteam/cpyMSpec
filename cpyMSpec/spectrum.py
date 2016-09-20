import cffi

from .utils import shared_lib, full_filename

import numbers

ffi = cffi.FFI()
ffi.cdef(open(full_filename("ims.h")).read())
ims = ffi.dlopen(full_filename(shared_lib("ms_cffi")))

try:
    import numpy as np
    _has_numpy = True
    _dtypes = {'f': np.float32, 'd': np.float64}
except:
    _has_numpy = False

_full_types = {'f': 'float', 'd': 'double'}

def _as_buffer(array, numtype):
    if _has_numpy:
        return np.asarray(array, dtype=_dtypes[numtype])
    else:
        from array import array as make_array
        a = make_array(numtype)
        a.extend(array)
        return a

class _cffi_buffer(object):
    def __init__(self, n, numtype):
        if _has_numpy:
            self.buf = np.zeros(n, dtype=_dtypes[numtype])
            self.ptr = ffi.cast('void *', self.buf.__array_interface__['data'][0])
        else:
            self.buf = None
            self.ptr = ffi.new(_full_types[numtype] + "[]", n)

    def python_data(self):
        return self.buf if _has_numpy else list(self.ptr)

def _raise_ims_exception():
    raise Exception(ffi.string(ims.ims_strerror()))

def _raise_ims_exception_if_null(arg):
    if arg == ffi.NULL:
        _raise_ims_exception()

class Spectrum(object):
    def __init__(self, mzs, intensities):
        n = len(mzs)
        assert len(mzs) == len(intensities)
        mzs = ffi.from_buffer(_as_buffer(mzs, 'd'))
        intensities = ffi.from_buffer(_as_buffer(intensities, 'd'))
        p = ims.spectrum_new(n, mzs, intensities)
        _raise_ims_exception_if_null(p)
        self.ptr = ffi.gc(p, ims.spectrum_free)
        self.sortByMass()

    def sortByMass(self):
        ims.spectrum_sort_by_mass(self.ptr)

    def sortByIntensity(self):
        ims.spectrum_sort_by_intensity(self.ptr)

    def _copy(self, modifier):
        obj = self.copy()
        modifier(obj)
        return obj

    def sortedByMass(self):
        return self._copy(Spectrum.sortByMass)

    def sortedByIntensity(self):
        return self._copy(Spectrum.sortByIntensity)

    def __str__(self):
        assert self.ptr != ffi.NULL
        tmp = self.sortedByMass()
        peaks = zip(tmp.masses, tmp.intensities)
        return "{\n  " +\
            ",\n  ".join("{0: >9.4f}: {1: >8.4f}%".format(x[0], x[1] * 100) for x in peaks) +\
            "\n}"

    def envelopeCentroids(self, resolution, min_abundance=1e-4, points_per_fwhm=25):
        assert self.ptr != ffi.NULL
        centroids = ims.spectrum_envelope_centroids(self.ptr, resolution,
                                                    min_abundance, points_per_fwhm)
        return Spectrum._new(centroids)

    @staticmethod
    def _new(raw_ptr):
        _raise_ims_exception_if_null(raw_ptr)
        obj = object.__new__(Spectrum)
        obj.ptr = ffi.gc(raw_ptr, ims.spectrum_free)
        return obj

    def copy(self):
        """
        :returns: a (deep) copy of the instance
        :rtype: Spectrum
        """
        return Spectrum._new(ims.spectrum_copy(self.ptr))

    def centroids(self, resolution, min_abundance=1e-4, points_per_fwhm=25):
        """
        Estimates centroided peaks at a given resolution.

        :param resolution: peak resolution, i.e. m/z value divided by FWHM
        :param min_abundance: minimum abundance for including a peak
        :param points_per_fwhm: grid density used for envelope calculation
        :returns: peaks visible at the specified resolution
        :rtype: Spectrum
        """
        return self.envelopeCentroids(resolution, min_abundance, points_per_fwhm)

    def size(self):
        """
        :returns: number of peaks in the spectrum
        :rtype: int
        """
        return ims.spectrum_size(self.ptr)

    @property
    def masses(self):
        """
        :returns: peak masses
        :rtype: list of floats
        """
        buf = ffi.new("double[]", self.size())
        ims.spectrum_masses(self.ptr, buf)
        return list(buf)

    @property
    def intensities(self):
        """
        :returns: peak intensities
        :rtype: list of floats
        """
        buf = ffi.new("double[]", self.size())
        ims.spectrum_intensities(self.ptr, buf)
        return list(buf)

    # deprecated
    @property
    def abundances(self):
        return self.intensities

    def addCharge(self, charge):
        """
        Adds/subtracts mass of electrons in-place.
        such that the charge increases by the specified amount.

        :param charge: number of electrons to add
        :type charge: integer
        """
        ims.spectrum_add_charge(self.ptr, charge)

    def __mul__(self, factor):
        """
        Multiplies all intensities by the factor
        """
        s = self.copy()
        ims.spectrum_multiply_inplace(s.ptr, factor)
        return s

    def __add__(self, other):
        if type(other) is not Spectrum:
            raise TypeError("can't add Spectrum and {}".format(str(type(other))))
        s = self.copy()
        ims.spectrum_add_inplace(s.ptr, other.ptr)
        return s

    def charged(self, charge):
        """
        Adds/subtracts electrons and returns a new object.

        :param charge: number of electrons to add
        :type charge: integer
        :returns: a spectrum with appropriately shifted masses
        :rtype: Spectrum

        """
        result = self.copy()
        result.addCharge(charge)
        return result

    def trim(self, n_peaks):
        """
        Removes low-intensity peaks from the spectrum.

        :param n_peaks: number of peaks to keep
        """
        self.sortByIntensity()
        ims.spectrum_trim(self.ptr, n_peaks)

    def trimmed(self, n_peaks):
        """
        :param n_peaks: number of peaks to keep
        :returns: an isotope pattern with removed low-intensity peaks
        :rtype: Spectrum
        """
        result = self.copy()
        result.trim(n_peaks)
        return result

    def removeIntensitiesBelow(self, min_intensity):
        ims.spectrum_trim_intensity(self.ptr, min_intensity)

    def envelope(self, resolution):
        """
        Computes isotopic envelope at a specified resolution

        :param resolution: peak resolution
        :returns: isotopic envelope as a function of mass
        :rtype: function float(mz: float)

        """
        def envelopeFunc(mz):
            if isinstance(mz, numbers.Number):
                return ims.spectrum_envelope(self.ptr, resolution, mz)
            mzs = _as_buffer(mz, 'd')
            ptr = ffi.from_buffer(mzs)
            n = len(mz)
            buf = _cffi_buffer(n, 'f')
            ret = ims.spectrum_envelope_plot(self.ptr, resolution, ptr, n, buf.ptr)
            if ret < 0:
                _raise_ims_exception()
            return buf.python_data()

        return envelopeFunc

def isotopePattern(sum_formula, threshold=1e-4, fft_threshold=1e-8):
    """
    Calculates isotopic peaks for a sum formula.

    :param sum_formula: text representation of an atomic composition
    :type sum_formula: str
    :param threshold: minimal abundance to keep in the final results
    :param fft_threshold: minimal abundance to keep in intermediate
    results (for each of the distinct atomic species)
    """
    s = ims.spectrum_new_from_sf(sum_formula, threshold, fft_threshold)
    return Spectrum._new(s)

# deprecated
IsotopePattern = isotopePattern

def centroidize(mzs, intensities, window_size=5):
    """
    Detects peaks in raw data.

    :param mzs: sorted array of m/z values
    :param intensities: array of corresponding intensities
    :param window_size: size of m/z averaging window

    :returns: isotope pattern containing the centroids
    :rtype: Spectrum
    """
    assert len(mzs) == len(intensities)
    n = len(mzs)
    mzs = ffi.from_buffer(_as_buffer(mzs, 'd'))
    ints = ffi.from_buffer(_as_buffer(intensities, 'f'))
    p = ims.spectrum_new_from_raw(n, mzs, ints, window_size)
    return Spectrum._new(p)
