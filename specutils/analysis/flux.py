from __future__ import division

import numpy as np
from astropy.modeling import Model
from astropy.units.quantity import Quantity
from .utils import computation_wrapper


__all__ = ['line_flux', 'equivalent_width']


def line_flux(spectrum, region=None):
    """
    Computes the line flux over a spectrum. Applies a region if given.

    Parameters
    ----------
    spectrum : Spectrum1D
        The spectrum object over which the line flux will be calculated.

    Returns
    -------
    flux : `~astropy.units.Quantity`
        line flux result
    """
    return computation_wrapper(_compute_line_flux, spectrum, region)


def equivalent_width(spectrum, continuum=1, region=None):
    """
    Does a naive equivalent width measures on the spectrum object.

    Parameters
    ----------
    spectrum : Spectrum1D
        The spectrum object overwhich the equivalent width will be calculated.

    continuum : `~astropy.units.Quantity`, optional
        Constant continuum value

    Returns
    -------
    ew : `~astropy.units.Quantity`
        Equivalent width calculation.

    TODO:  what frame of reference do you want the spectral_axis to be in ???
    """

    if isinstance(continuum, Model):
        continuum = continuum(spectrum.spectral_axis)

    kwargs = dict(continuum=continuum)
    return computation_wrapper(_compute_equivalent_width, spectrum, region, **kwargs)


def _compute_line_flux(spectrum, region=None):

    if region is not None:
        calc_spectrum = region.extract(spectrum)
    else:
        calc_spectrum = spectrum

    # Average dispersion in the line region
    avg_dx = np.diff(spectrum.spectral_axis)

    line_flux = np.sum(calc_spectrum.flux[1:] * avg_dx)

    # TODO: we may want to consider converting to erg / cm^2 / sec by default
    return line_flux


def _compute_equivalent_width(spectrum, continuum=1, region=None):

    if region is not None:
        calc_spectrum = region.extract(spectrum)
    else:
        calc_spectrum = spectrum

    if continuum == 1:
        continuum = 1*calc_spectrum.flux.unit

    spectral_axis = calc_spectrum.spectral_axis
    dx = spectral_axis[-1] - spectral_axis[0]

    line_flux = _compute_line_flux(spectrum/continuum, region)

    # Calculate equivalent width
    ew =  dx - line_flux

    return ew
