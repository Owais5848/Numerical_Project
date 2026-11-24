"""
Symbolic Computing Module for FORMULA RACER
Course: Numerical and Symbolic Computing

STRICT MATHEMATICAL REQUIREMENT:
f(x) = x^4 - 3x^3 + 2x
Never replace this equation with another function.
Uses SymPy for exact analytical calculations, symbolic derivatives, integrals,
roots, and Taylor expansions.
"""

import math
from functools import lru_cache
from typing import Dict, Any, List
import sympy as sp

# Define symbolic variable
x = sp.Symbol('x', real=True)

# STRICT ORIGINAL FUNCTION
f_expr = x**4 - 3*x**3 + 2*x

# Analytical Derivatives
f_prime_expr = sp.diff(f_expr, x)            # 4*x**3 - 9*x**2 + 2
f_double_prime_expr = sp.diff(f_expr, x, 2)  # 12*x**2 - 18*x
f_triple_prime_expr = sp.diff(f_expr, x, 3)  # 24*x - 18

# Analytical Indefinite Integral: F(x) = x^5/5 - 3x^4/4 + x^2
f_integral_expr = sp.integrate(f_expr, x)

# Curvature expression
kappa_expr = sp.Abs(f_double_prime_expr) / ((1 + f_prime_expr**2)**(sp.Rational(3, 2)))

# Lambdified functions for high-speed evaluation
_f_func = sp.lambdify(x, f_expr, 'numpy')
_f_prime_func = sp.lambdify(x, f_prime_expr, 'numpy')
_f_double_prime_func = sp.lambdify(x, f_double_prime_expr, 'numpy')
_f_triple_prime_func = sp.lambdify(x, f_triple_prime_expr, 'numpy')
_f_integral_func = sp.lambdify(x, f_integral_expr, 'numpy')


def evaluate_f(val: float) -> float:
    """Evaluate f(x) = x^4 - 3x^3 + 2x at val."""
    return float(_f_func(val))


def evaluate_f_prime(val: float) -> float:
    """Evaluate f'(x) = 4x^3 - 9x^2 + 2 at val."""
    return float(_f_prime_func(val))


def evaluate_f_double_prime(val: float) -> float:
    """Evaluate f''(x) = 12x^2 - 18x at val."""
    return float(_f_double_prime_func(val))


def evaluate_f_triple_prime(val: float) -> float:
    """Evaluate f'''(x) = 24x - 18 at val."""
    return float(_f_triple_prime_func(val))


def evaluate_curvature(val: float) -> float:
    """Evaluate track curvature kappa(x) at val."""
    dy = evaluate_f_prime(val)
    d2y = evaluate_f_double_prime(val)
    denom = (1.0 + dy**2) ** 1.5
    return abs(d2y) / denom if denom > 1e-12 else 0.0


# ==============================================================================
# SPECIFIC SYMPY ENGINE CALCULATIONS (REQUIREMENTS 1 - 6)
# ==============================================================================

def get_symbolic_original_function() -> Dict[str, Any]:
    """1. Original symbolic function f(x) = x^4 - 3x^3 + 2x."""
    return {
        "expression_str": str(f_expr),
        "string": str(f_expr),
        "latex": sp.latex(f_expr),
        "formatted": "f(x) = x^4 - 3x^3 + 2x",
        "equation": "f(x) = x^4 - 3x^3 + 2x"
    }


def get_symbolic_first_derivative() -> Dict[str, Any]:
    """2. First symbolic derivative f'(x) = 4x^3 - 9x^2 + 2."""
    return {
        "expression_str": str(f_prime_expr),
        "string": str(f_prime_expr),
        "latex": sp.latex(f_prime_expr),
        "formatted": "f'(x) = 4x^3 - 9x^2 + 2",
        "equation": "f'(x) = 4x^3 - 9x^2 + 2"
    }


def get_symbolic_indefinite_integral() -> Dict[str, Any]:
    """3. Indefinite symbolic integral F(x) = x^5/5 - 3x^4/4 + x^2."""
    return {
        "expression_str": str(f_integral_expr),
        "string": str(f_integral_expr),
        "latex": sp.latex(f_integral_expr),
        "formatted": "F(x) = x^5/5 - 3x^4/4 + x^2 + C",
        "equation": "F(x) = x^5/5 - 3x^4/4 + x^2 + C"
    }


def evaluate_symbolic_f_at_2() -> Dict[str, Any]:
    """4. Function value at x = 2 using SymPy: f(2) = -4."""
    exact_sym = f_expr.subs(x, 2)
    return {
        "x": 2.0,
        "exact_expression": str(exact_sym),
        "value": float(exact_sym),
        "expected": -4.0
    }


def evaluate_symbolic_f_prime_at_2() -> Dict[str, Any]:
    """5. Derivative value at x = 2 using SymPy: f'(2) = -2."""
    exact_sym = f_prime_expr.subs(x, 2)
    return {
        "x": 2.0,
        "exact_expression": str(exact_sym),
        "value": float(exact_sym),
        "expected": -2.0
    }


def evaluate_symbolic_definite_integral_0_to_2() -> Dict[str, Any]:
    """6. Definite integral from 0 to 2 using SymPy: -1.6 (-8/5)."""
    exact_sym = sp.integrate(f_expr, (x, 0, 2))
    return {
        "a": 0.0,
        "b": 2.0,
        "exact_rational": str(exact_sym),  # -8/5
        "exact_fraction": str(exact_sym),  # -8/5
        "latex": sp.latex(exact_sym),
        "value": float(exact_sym),          # -1.6
        "expected": -1.6
    }


def get_sympy_engine_summary() -> Dict[str, Any]:
    """Comprehensive dictionary of the 6 required SymPy calculations."""
    return {
        "original_function": get_symbolic_original_function(),
        "first_derivative": get_symbolic_first_derivative(),
        "indefinite_integral": get_symbolic_indefinite_integral(),
        "f_at_2": evaluate_symbolic_f_at_2(),
        "f_prime_at_2": evaluate_symbolic_f_prime_at_2(),
        "definite_integral_0_to_2": evaluate_symbolic_definite_integral_0_to_2()
    }



@lru_cache(maxsize=1)
def get_exact_roots() -> List[Dict[str, Any]]:
    """
    Exact analytical roots of f(x) = x^4 - 3x^3 + 2x = x(x - 1)(x^2 - 2x - 2) = 0.
    The four exact roots are:
    x1 = 1 - sqrt(3) ~ -0.732051
    x2 = 0
    x3 = 1
    x4 = 1 + sqrt(3) ~ 2.732051
    """
    exact_sympy_roots = [
        1 - sp.sqrt(3),
        sp.Integer(0),
        sp.Integer(1),
        1 + sp.sqrt(3)
    ]
    results = []
    for r in exact_sympy_roots:
        results.append({
            "exact": str(r),
            "latex": sp.latex(r),
            "value": round(float(sp.N(r)), 6)
        })
    results.sort(key=lambda item: item["value"])
    return results


@lru_cache(maxsize=1)
def get_exact_critical_points() -> List[Dict[str, Any]]:
    """
    Find critical points where f'(x) = 4x^3 - 9x^2 + 2 = 0.
    Using Cardano-Viete closed-form trigonometric formula for the 3 real roots:
    x_k = 3/4 + 3/2 * cos((arccos(11/54) - 2*pi*k)/3) for k = 0, 1, 2.
    Classify each point using second derivative test:
    f''(x) > 0 -> Local Minimum (Valley)
    f''(x) < 0 -> Local Maximum (Peak)
    """
    # arccos(11/54)
    alpha = math.acos(11.0 / 54.0)
    raw_roots = []
    for k in [0, 1, 2]:
        yk = 1.5 * math.cos((alpha - 2.0 * math.pi * k) / 3.0)
        xk = yk + 0.75
        raw_roots.append(xk)
    raw_roots.sort()

    results = []
    for val in raw_roots:
        f_val = evaluate_f(val)
        d2y = evaluate_f_double_prime(val)
        if d2y > 1e-6:
            pt_type = "Local Minimum (Valley)"
        elif d2y < -1e-6:
            pt_type = "Local Maximum (Peak)"
        else:
            pt_type = "Inflection Point"

        results.append({
            "x": round(val, 6),
            "y": round(f_val, 6),
            "f_double_prime": round(d2y, 6),
            "type": pt_type,
            "exact": f"3/4 + 3/2*cos((arccos(11/54) - 2*pi*k)/3)",
            "latex": "\\frac{3}{4} + \\frac{3}{2}\\cos\\left(\\frac{\\arccos(11/54) - 2\\pi k}{3}\\right)"
        })

    return results


@lru_cache(maxsize=1)
def get_inflection_points() -> List[Dict[str, Any]]:
    """
    Find inflection points where f''(x) = 12x^2 - 18x = 6x(2x - 3) = 0.
    Exact roots: x = 0 and x = 3/2 (1.5).
    """
    pts = [sp.Integer(0), sp.Rational(3, 2)]
    results = []
    for pt in pts:
        val = float(pt)
        f_val = evaluate_f(val)
        f_prime_val = evaluate_f_prime(val)
        results.append({
            "x": round(val, 6),
            "y": round(f_val, 6),
            "slope": round(f_prime_val, 6),
            "exact": str(pt),
            "latex": sp.latex(pt)
        })
    results.sort(key=lambda item: item["x"])
    return results


def get_exact_definite_integral(a: float, b: float) -> Dict[str, Any]:
    """Compute exact definite integral of f(x) from a to b."""
    # F(x) = x^5/5 - 3x^4/4 + x^2
    val_b = float(_f_integral_func(b))
    val_a = float(_f_integral_func(a))
    diff_val = val_b - val_a
    return {
        "a": a,
        "b": b,
        "exact_expression": f"[{str(f_integral_expr)}]_{{{a}}}^{{{b}}}",
        "latex": f"\\left[\\frac{{x^{{5}}}}{{5}} - \\frac{{3x^{{4}}}}{{4}} + x^{{2}}\\right]_{{{a}}}^{{{b}}}",
        "value": diff_val
    }


def compute_tangent_and_normal(x0: float) -> Dict[str, Any]:
    """
    Compute exact tangent and normal line equations at x = x0.
    Tangent: y = f'(x0)*(x - x0) + f(x0)
    Normal:  y = -1/f'(x0)*(x - x0) + f(x0)
    """
    y0 = evaluate_f(x0)
    slope = evaluate_f_prime(x0)

    c_tangent = y0 - slope * x0
    tangent_eq_str = f"y = {slope:.4f}x + {c_tangent:.4f}" if c_tangent >= 0 else f"y = {slope:.4f}x - {abs(c_tangent):.4f}"

    has_normal = abs(slope) > 1e-9
    if has_normal:
        m_normal = -1.0 / slope
        c_normal = y0 - m_normal * x0
        normal_eq_str = f"y = {m_normal:.4f}x + {c_normal:.4f}" if c_normal >= 0 else f"y = {m_normal:.4f}x - {abs(c_normal):.4f}"
    else:
        m_normal = None
        c_normal = None
        normal_eq_str = f"x = {x0:.4f} (Vertical Line)"

    return {
        "x0": x0,
        "y0": round(y0, 6),
        "slope": round(slope, 6),
        "tangent": {
            "m": round(slope, 6),
            "c": round(c_tangent, 6),
            "equation": tangent_eq_str
        },
        "normal": {
            "m": round(m_normal, 6) if m_normal is not None else None,
            "c": round(c_normal, 6) if c_normal is not None else None,
            "equation": normal_eq_str
        }
    }


def compute_taylor_series(x0: float, order: int = 4) -> Dict[str, Any]:
    """
    Compute exact Taylor Series expansion around point x0 up to specified order.
    """
    clamped_order = max(1, min(order, 6))
    series_poly = sp.series(f_expr, x, x0, n=clamped_order + 1).removeO()
    expanded_poly = sp.expand(series_poly)

    return {
        "x0": x0,
        "order": clamped_order,
        "taylor_polynomial_str": str(expanded_poly),
        "latex": sp.latex(series_poly),
        "expanded_latex": sp.latex(expanded_poly)
    }


@lru_cache(maxsize=1)
def get_full_symbolic_summary() -> Dict[str, Any]:
    """Return comprehensive symbolic analysis dictionary."""
    return {
        "function": {
            "str": "f(x) = x^4 - 3*x^3 + 2*x",
            "latex": "f(x) = x^{4} - 3x^{3} + 2x",
            "degree": 4,
            "type": "Quartic Polynomial"
        },
        "derivatives": {
            "first": {
                "str": str(sp.expand(f_prime_expr)),
                "latex": sp.latex(f_prime_expr)
            },
            "second": {
                "str": str(sp.expand(f_double_prime_expr)),
                "factored": str(f_double_prime_expr),
                "latex": sp.latex(sp.expand(f_double_prime_expr))
            },
            "third": {
                "str": str(sp.expand(f_triple_prime_expr)),
                "latex": sp.latex(f_triple_prime_expr)
            }
        },
        "integral": {
            "str": str(f_integral_expr) + " + C",
            "latex": "\\frac{x^{5}}{5} - \\frac{3x^{4}}{4} + x^{2} + C"
        },
        "curvature_formula": {
            "formula": "\\kappa(x) = \\frac{|12x^2 - 18x|}{(1 + (4x^3 - 9x^2 + 2)^2)^{3/2}}"
        },
        "roots": get_exact_roots(),
        "critical_points": get_exact_critical_points(),
        "inflection_points": get_inflection_points()
    }
