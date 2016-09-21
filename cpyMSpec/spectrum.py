from .utils import init_ffi, load_shared_lib

import numbers

ffi = init_ffi()
ims = load_shared_lib(ffi)

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
            self.ptr = ffi.cast(_full_types[numtype] + '*',
                                self.buf.__array_interface__['data'][0])
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

def _new_spectrum(class_, raw_ptr):
    _raise_ims_exception_if_null(raw_ptr)
    obj = object.__new__(class_)
    obj.ptr = ffi.gc(raw_ptr, ims.spectrum_free)
    return obj

class SpectrumBase(object):
    def sortByMass(self):
        ims.spectrum_sort_by_mass(self.ptr)

    def sortByIntensity(self):
        ims.spectrum_sort_by_intensity(self.ptr)

    def _copy(self, modifier):
        obj = self.copy()
        modifier(obj)
        return obj

    def sortedByMass(self):
        return self._copy(SpectrumBase.sortByMass)

    def sortedByIntensity(self):
        return self._copy(SpectrumBase.sortByIntensity)

    def __str__(self):
        assert self.ptr != ffi.NULL
        tmp = self.sortedByMass()
        peaks = zip(tmp.masses, tmp.intensities)
        return "{\n  " +\
            ",\n  ".join("{0: >9.4f}: {1: >8.4f}%".format(x[0], x[1] * 100) for x in peaks) +\
            "\n}"

    @property
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
        buf = ffi.new("double[]", self.size)
        ims.spectrum_masses(self.ptr, buf)
        return list(buf)

    @property
    def intensities(self):
        """
        :returns: peak intensities
        :rtype: list of floats
        """
        buf = ffi.new("double[]", self.size)
        ims.spectrum_intensities(self.ptr, buf)
        return list(buf)

    def addCharge(self, charge):
        """
        Adds/subtracts mass of electrons in-place.
        such that the charge increases by the specified amount.

        :param charge: number of electrons to add
        :type charge: integer
        """
        ims.spectrum_add_charge(self.ptr, charge)

    def trim(self, n_peaks):
        """
        Sorts mass and intensities arrays in descending intensity order,
        then removes low-intensity peaks from the spectrum.

        :param n_peaks: number of peaks to keep
        """
        self.sortByIntensity()
        ims.spectrum_trim(self.ptr, n_peaks)

class ProfileSpectrum(SpectrumBase):
    """
    Represents profile spectrum data, which means:
    * neighbor mass differences are supposed to be locally approximately equal;
    * occasional gaps might be present, indicating zero-intensity regions
    """
    def __init__(self, mzs, intensities):
        n = len(mzs)
        assert len(mzs) == len(intensities)
        mzs = ffi.from_buffer(_as_buffer(mzs, 'd'))
        intensities = ffi.from_buffer(_as_buffer(intensities, 'd'))
        p = ims.spectrum_new(n, mzs, intensities)
        _raise_ims_exception_if_null(p)
        self.ptr = ffi.gc(p, ims.spectrum_free)
        self.sortByMass()

    def copy(self):
        """
        :returns: a (deep) copy of the instance
        :rtype: ProfileSpectrum
        """
        return _new_spectrum(ProfileSpectrum, ims.spectrum_copy(self.ptr))

    def centroids(self, window_size=5):
        """
        Detects peaks in raw data.

        :param mzs: sorted array of m/z values
        :param intensities: array of corresponding intensities
        :param window_size: size of m/z averaging window

        :returns: isotope pattern containing the centroids
        :rtype: CentroidedSpectrum
        """
        self.sortByMass()
        mzs = ffi.from_buffer(_as_buffer(self.masses, 'd'))
        intensities = ffi.from_buffer(_as_buffer(self.intensities, 'f'))
        n = self.size
        p = ims.spectrum_new_from_raw(n, mzs, intensities, int(window_size))
        return _new_spectrum(CentroidedSpectrum, p)

class InstrumentModel(object):
    def __init__(self, instrument_type, resolving_power, at_mz=200):
        """
        :param type: instrument type, must be one of 'orbitrap', 'fticr', 'tof'.
        :param resolving_power: instrument resolving power
        :param at_mz: value at which the resolving power is specified
        """
        p = ims.instrument_profile_new(instrument_type.lower(), resolving_power, at_mz)
        _raise_ims_exception_if_null(p)
        self.ptr = ffi.gc(p, ims.instrument_profile_free)

    def resolvingPowerAt(self, mz):
        """
        Calculates resolving power at a given m/z value
        """
        return ims.instrument_resolving_power_at(self.ptr, mz)

class TheoreticalSpectrum(SpectrumBase):
    """
    A bag of isotopic peaks computed for a single or multiple sum formulas.
    """

    def copy(self):
        """
        :returns: a (deep) copy of the instance
        :rtype: Spectrum
        """
        return _new_spectrum(TheoreticalSpectrum, ims.spectrum_copy(self.ptr))

    def centroids(self, instrument, min_abundance=1e-4, points_per_fwhm=25):
        """
        Estimates centroided peaks for a given instrument model.

        :param instrument: instrument model
        :param min_abundance: minimum abundance for including a peak
        :param points_per_fwhm: grid density used for envelope calculation
        :returns: peaks visible with the instrument used
        :rtype: TheoreticalSpectrum
        """
        assert self.ptr != ffi.NULL
        centroids = ims.spectrum_envelope_centroids(self.ptr, instrument.ptr,
                                                    min_abundance, points_per_fwhm)
        return _new_spectrum(CentroidedSpectrum, centroids)

    def __mul__(self, factor):
        """
        Multiplies all intensities by the factor
        """
        s = self.copy()
        ims.spectrum_multiply_inplace(s.ptr, factor)
        return s

    def __add__(self, other):
        """
        Adds two theoretical spectra by simply merging masses and intensities of both.
        """
        if type(other) is not TheoreticalSpectrum:
            raise TypeError("can't add TheoreticalSpectrum and {}".format(str(type(other))))
        s = self.copy()
        ims.spectrum_add_inplace(s.ptr, other.ptr)
        return s

    def envelope(self, instrument):
        """
        Computes isotopic envelope for a given instrument model

        :param instrument: instrument model to use
        :returns: isotopic envelope as a function of mass
        :rtype: function float(mz: float)

        """
        def envelopeFunc(mz):
            if isinstance(mz, numbers.Number):
                return ims.spectrum_envelope(self.ptr, instrument.ptr, mz)
            mzs = _as_buffer(mz, 'd')
            ptr = ffi.cast("double*", ffi.from_buffer(mzs))
            n = len(mz)
            buf = _cffi_buffer(n, 'f')
            ret = ims.spectrum_envelope_plot(self.ptr, instrument.ptr, ptr, n, buf.ptr)
            if ret < 0:
                _raise_ims_exception()
            return buf.python_data()

        return envelopeFunc

class CentroidedSpectrum(SpectrumBase):
    """
    Centroided peaks of a profile/theoretical spectrum
    """

    def copy(self):
        """
        :returns: a (deep) copy of the instance
        :rtype: CentroidedSpectrum
        """
        return _new_spectrum(CentroidedSpectrum, ims.spectrum_copy(self.ptr))

    def charged(self, charge):
        """
        Adds/subtracts electrons and returns a new object.

        :param charge: number of electrons to add
        :type charge: integer
        :returns: a spectrum with appropriately shifted masses
        :rtype: CentroidedSpectrum

        """
        result = self.copy()
        result.addCharge(charge)
        return result

    def trimmed(self, n_peaks):
        """
        :param n_peaks: number of peaks to keep
        :returns: an isotope pattern with removed low-intensity peaks
        :rtype: CentroidedSpectrum
        """
        result = self.copy()
        result.trim(n_peaks)
        return result

    def removeIntensitiesBelow(self, min_intensity):
        ims.spectrum_trim_intensity(self.ptr, min_intensity)

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
    return _new_spectrum(TheoreticalSpectrum, s)
