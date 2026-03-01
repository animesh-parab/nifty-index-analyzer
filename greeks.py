"""
greeks.py
Black-Scholes Greeks calculator for Nifty options.
Calculates Delta, Gamma, Theta, Vega, Rho from market data.
"""

import numpy as np
from scipy.stats import norm
from datetime import datetime, date
import pytz
from config import TIMEZONE

IST = pytz.timezone(TIMEZONE)


def days_to_expiry(expiry_str: str) -> float:
    """Calculate calendar days to expiry as fraction of year."""
    try:
        # NSE format: "27-Feb-2025"
        expiry_date = datetime.strptime(expiry_str, "%d-%b-%Y").date()
        today = datetime.now(IST).date()
        days = (expiry_date - today).days
        return max(days / 365.0, 1 / 365.0)  # At least 1 day
    except Exception:
        return 7 / 365.0  # Default 1 week


def black_scholes_price(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "CE") -> float:
    """Calculate Black-Scholes option price."""
    if T <= 0 or sigma <= 0:
        return max(0, S - K) if option_type == "CE" else max(0, K - S)

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "CE":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return max(0, price)


def calculate_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "CE") -> dict:
    """
    Calculate all option Greeks using Black-Scholes.

    S     = Current Nifty price
    K     = Strike price
    T     = Time to expiry in years
    r     = Risk-free rate (India ~0.065)
    sigma = Implied volatility (as decimal, e.g. 0.15 for 15%)
    """
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0, "price": 0}

    try:
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        nd1 = norm.cdf(d1)
        nd2 = norm.cdf(d2)
        n_neg_d1 = norm.cdf(-d1)
        n_neg_d2 = norm.cdf(-d2)
        phi_d1 = norm.pdf(d1)

        if option_type == "CE":
            delta = nd1
            price = S * nd1 - K * np.exp(-r * T) * nd2
            rho = K * T * np.exp(-r * T) * nd2 / 100
        else:
            delta = nd1 - 1
            price = K * np.exp(-r * T) * n_neg_d2 - S * n_neg_d1
            rho = -K * T * np.exp(-r * T) * n_neg_d2 / 100

        gamma = phi_d1 / (S * sigma * np.sqrt(T))
        theta = (-(S * phi_d1 * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * nd2) / 365
        vega = S * phi_d1 * np.sqrt(T) / 100

        return {
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta": round(theta, 4),   # Per day
            "vega":  round(vega, 4),    # Per 1% IV change
            "rho":   round(rho, 4),
            "price": round(max(0, price), 2),
        }

    except Exception:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0, "price": 0}


def get_atm_greeks(spot_price: float, vix: float, expiry_str: str) -> dict:
    """
    Calculate Greeks for ATM options at current spot price.
    Uses India VIX as proxy for implied volatility.
    Risk-free rate = India repo rate ~6.5%
    """
    K = round(spot_price / 50) * 50  # Round to nearest 50 (Nifty strike interval)
    T = days_to_expiry(expiry_str) if expiry_str else 7 / 365.0
    r = 0.065  # India risk-free rate
    sigma = vix / 100 if vix > 0 else 0.15  # VIX to decimal

    ce_greeks = calculate_greeks(spot_price, K, T, r, sigma, "CE")
    pe_greeks = calculate_greeks(spot_price, K, T, r, sigma, "PE")

    return {
        "strike": K,
        "spot": spot_price,
        "days_to_expiry": round(T * 365, 1),
        "iv_used": round(sigma * 100, 2),
        "CE": ce_greeks,
        "PE": pe_greeks,
        "interpretation": _interpret_greeks(ce_greeks, pe_greeks, T, vix),
    }


def _interpret_greeks(ce: dict, pe: dict, T: float, vix: float) -> dict:
    """Plain English interpretation of Greeks for the dashboard."""
    days = T * 365
    theta_daily = ce["theta"]

    return {
        "delta": f"For every 100pt Nifty move, ATM CE gains ₹{abs(ce['delta']) * 100:.0f}, PE gains ₹{abs(pe['delta']) * 100:.0f}",
        "theta": f"Each day, ATM options lose ≈ ₹{abs(theta_daily) * 75:.0f} per lot (Theta decay)",
        "gamma": f"Gamma is {'HIGH (near expiry, big price swings possible)' if days < 3 else 'NORMAL'}",
        "vega":  f"If VIX moves 1%, option premium changes by ₹{ce['vega'] * 75:.0f} per lot",
        "expiry_warning": "⚠️ EXPIRY DAY - Gamma risk extreme, avoid naked options!" if days < 1 else (
            "⚡ Near expiry - Theta accelerating" if days < 3 else "Normal Greeks regime"
        ),
    }
