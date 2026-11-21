"""Explicitly assumed installed-capacity and hourly-energy sensitivity designs.

The ReEDS county supply curve is developable resource *potential*, not
actual or projected installed capacity. The ReEDS CF is instantaneous on
the hour, not a publisher-validated hour-averaged generation profile.

This code produces sensitivity cases only, never "observed" generation.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def scenario_installed_capacity_mw(resource_potential_mw, *,
                                  installed_capacity_mw=None,
                                  fraction_of_potential=None):
    """Require an explicit scenario scale; never interpret full potential as fleet."""
    p=float(resource_potential_mw)
    if not np.isfinite(p) or p<=0:
        raise ValueError("Positive resource potential in MW is required")
    if (installed_capacity_mw is None)==(fraction_of_potential is None):
        raise ValueError("Exactly one scenario installed MW or fraction must be specified")
    if installed_capacity_mw is not None:
        k=float(installed_capacity_mw)
    else:
        f=float(fraction_of_potential)
        if not np.isfinite(f) or not 0<=f<=1:
            raise ValueError("Scenario resource potential fraction outside [0,1]")
        k=p*f
    if not np.isfinite(k) or not 0<=k<=p:
        raise ValueError("Scenario installed MW must be within developable potential")
    return k


def instantaneous_cf_hour_ending_sensitivities(cf, *, prior_hour_cf=None):
    """Construct approximations to (t-1h,t] energy without cyclic wrapping.

    End-point hold: E[k]/MW = CF(t_k) * 1h.
    Linear interpolation/trapezoid: E[k]/MW = 0.5*(CF(t_{k-1})+CF(t_k))*1h.
    They are explicitly modeling assumptions, NOT publisher-certified
    hourly integrated renewable energy. For k=0, require a separately
    authenticated preceding-hour measurement or return NaN.
    """
    a=np.asarray(cf,dtype=float)
    if a.ndim!=1 or a.size!=8760:
        raise ValueError("Expected native 2012 8760-hour 1-D CF series")
    if not np.isfinite(a).all() or (a<0).any() or (a>1+1e-8).any():
        raise ValueError("CF values must be finite and in [0,1]")
    endpoint=a.copy()
    trapezoid=np.full(8760,np.nan)
    trapezoid[1:]=(a[:-1]+a[1:])/2
    first_certified=prior_hour_cf is not None
    if first_certified:
        x=float(prior_hour_cf)
        if not np.isfinite(x) or not 0<=x<=1:
            raise ValueError("Invalid preceding-hour CF")
        trapezoid[0]=(x+a[0])/2
    return pd.DataFrame({
        "endpoint_hold_mwh_per_mw_assumed":endpoint,
        "trapezoidal_mwh_per_mw_assumed":trapezoid,
        "first_hour_preceding_sample_certified":[first_certified]*8760,
    })


def assumed_state_hourly_energy_mwh(cf, *, scenario_installed_mw,
                                   reference_potential_mw,
                                   assumption):
    """Return assumed MWh for input CF whose denominator matches capacity MW.

    For utility PV, the caller must confirm DC vs AC installed-capacity
    basis before this operation. Physical source-hour join is not certified.
    """
    mw=scenario_installed_capacity_mw(reference_potential_mw,
                                      installed_capacity_mw=scenario_installed_mw)
    profiles=instantaneous_cf_hour_ending_sensitivities(cf)
    field={
        "endpoint_hold":"endpoint_hold_mwh_per_mw_assumed",
        "trapezoid":"trapezoidal_mwh_per_mw_assumed",
    }.get(assumption)
    if field is None:
        raise ValueError("Unsupported hourly integration assumption")
    return profiles[field].to_numpy()*mw
