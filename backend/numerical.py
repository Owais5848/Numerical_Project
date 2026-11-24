"""
Numerical Computing Module for FORMULA RACER
Course: Numerical and Symbolic Computing

STRICT MATHEMATICAL REQUIREMENT:
f(x) = x^4 - 3x^3 + 2x
Never replace this equation with another function.
Uses NumPy for numerical evaluations, finite differences, numerical integration,
root finding algorithms, and ODE solvers.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Callable


def f_numpy(x_arr: np.ndarray | float) -> np.ndarray | float:
    """Exact function f(x) = x^4 - 3x^3 + 2x vectorized with NumPy."""
    x = np.asarray(x_arr, dtype=np.float64)
    return x**4 - 3.0 * (x**3) + 2.0 * x


def f_prime_numpy(x_arr: np.ndarray | float) -> np.ndarray | float:
    """Exact analytical derivative f'(x) = 4x^3 - 9x^2 + 2 vectorized with NumPy."""
    x = np.asarray(x_arr, dtype=np.float64)
    return 4.0 * (x**3) - 9.0 * (x**2) + 2.0


def f_double_prime_numpy(x_arr: np.ndarray | float) -> np.ndarray | float:
    """Exact analytical second derivative f''(x) = 12x^2 - 18x vectorized with NumPy."""
    x = np.asarray(x_arr, dtype=np.float64)
    return 12.0 * (x**2) - 18.0 * x


# ==========================================
# 1. NUMERICAL DIFFERENTIATION
# ==========================================

def central_difference_derivative(x: float, h: float = 0.001) -> float:
    """
    Central Difference Method: [f(x+h) - f(x-h)] / (2h).
    Default h = 0.001. Truncation error O(h^2).
    """
    step = abs(float(h)) if abs(float(h)) > 1e-12 else 1e-12
    return float((f_numpy(x + step) - f_numpy(x - step)) / (2.0 * step))


def finite_difference_forward(x: float, h: float = 1e-4) -> float:
    """Forward difference: (f(x+h) - f(x)) / h. Truncation error O(h)."""
    return float((f_numpy(x + h) - f_numpy(x)) / h)


def finite_difference_backward(x: float, h: float = 1e-4) -> float:
    """Backward difference: (f(x) - f(x-h)) / h. Truncation error O(h)."""
    return float((f_numpy(x) - f_numpy(x - h)) / h)


def finite_difference_central(x: float, h: float = 1e-4) -> float:
    """Central difference: (f(x+h) - f(x-h)) / (2h). Truncation error O(h^2)."""
    return float((f_numpy(x + h) - f_numpy(x - h)) / (2.0 * h))


def finite_difference_second(x: float, h: float = 1e-4) -> float:
    """Second-order central difference: (f(x+h) - 2f(x) + f(x-h)) / h^2. Truncation error O(h^2)."""
    return float((f_numpy(x + h) - 2.0 * f_numpy(x) + f_numpy(x - h)) / (h**2))


def compare_differentiation_methods(x: float, h_list: List[float] = None) -> Dict[str, Any]:
    """
    Compare analytical derivative with forward, backward, and central differences.
    Demonstrates error scaling O(h) vs O(h^2).
    """
    if h_list is None:
        h_list = [1e-1, 5e-2, 1e-2, 5e-3, 1e-3, 5e-4, 1e-4, 1e-5]

    exact_val = float(f_prime_numpy(x))
    comparison_data = []

    for h in h_list:
        forward_val = finite_difference_forward(x, h)
        backward_val = finite_difference_backward(x, h)
        central_val = finite_difference_central(x, h)

        err_fwd = abs(forward_val - exact_val)
        err_bwd = abs(backward_val - exact_val)
        err_cnt = abs(central_val - exact_val)

        comparison_data.append({
            "h": h,
            "forward": round(forward_val, 8),
            "forward_error": round(err_fwd, 10),
            "backward": round(backward_val, 8),
            "backward_error": round(err_bwd, 10),
            "central": round(central_val, 8),
            "central_error": round(err_cnt, 10)
        })

    return {
        "x": x,
        "exact_derivative": round(exact_val, 8),
        "steps": comparison_data
    }


# ==========================================
# 2. NUMERICAL INTEGRATION
# ==========================================

def integrate_trapezoidal(a: float, b: float, n: int = 100) -> float:
    """
    Composite Trapezoidal Rule:
    Integral ~ h/2 * [f(a) + 2*sum(f(x_i)) + f(b)]
    """
    if n < 1:
        n = 1
    x_grid = np.linspace(a, b, n + 1)
    y_grid = f_numpy(x_grid)
    h = (b - a) / n
    # np.trapz / trapezoid
    result = (h / 2.0) * (y_grid[0] + 2.0 * np.sum(y_grid[1:-1]) + y_grid[-1])
    return float(result)


def integrate_simpsons_13(a: float, b: float, n: int = 100) -> float:
    """
    Composite Simpson's 1/3 Rule (requires even number of subintervals n):
    Integral ~ h/3 * [f(x_0) + 4*sum(odd) + 2*sum(even) + f(x_n)]
    """
    if n % 2 != 0:
        n += 1
    if n < 2:
        n = 2
    x_grid = np.linspace(a, b, n + 1)
    y_grid = f_numpy(x_grid)
    h = (b - a) / n
    result = (h / 3.0) * (y_grid[0] + 4.0 * np.sum(y_grid[1:-1:2]) + 2.0 * np.sum(y_grid[2:-1:2]) + y_grid[-1])
    return float(result)


def integrate_simpsons_38(a: float, b: float, n: int = 99) -> float:
    """
    Composite Simpson's 3/8 Rule (requires n divisible by 3):
    Integral ~ 3h/8 * [f(x_0) + 3*f(x_1) + 3*f(x_2) + 2*f(x_3) + ...]
    """
    if n % 3 != 0:
        n = n + (3 - (n % 3))
    if n < 3:
        n = 3
    x_grid = np.linspace(a, b, n + 1)
    y_grid = f_numpy(x_grid)
    h = (b - a) / n

    weights = np.ones(n + 1)
    weights[0] = 1.0
    weights[-1] = 1.0
    for i in range(1, n):
        if i % 3 == 0:
            weights[i] = 2.0
        else:
            weights[i] = 3.0

    result = (3.0 * h / 8.0) * np.sum(weights * y_grid)
    return float(result)


def compute_numerical_arc_length(a: float, b: float, n: int = 500) -> float:
    """
    Arc length S = int_a^b sqrt(1 + (f'(x))^2) dx.
    Evaluated with composite Simpson's rule.
    """
    if a > b:
        a, b = b, a
    if abs(b - a) < 1e-9:
        return 0.0
    if n % 2 != 0:
        n += 1

    x_grid = np.linspace(a, b, n + 1)
    f_p = f_prime_numpy(x_grid)
    integrand = np.sqrt(1.0 + f_p**2)
    h = (b - a) / n

    s = (h / 3.0) * (integrand[0] + 4.0 * np.sum(integrand[1:-1:2]) + 2.0 * np.sum(integrand[2:-1:2]) + integrand[-1])
    return float(s)


def compare_integration_methods(a: float, b: float, n_intervals: int = 60, exact_val: float = None) -> Dict[str, Any]:
    """Compare Trapezoidal, Simpson 1/3, and Simpson 3/8 against analytical integral."""
    trap_val = integrate_trapezoidal(a, b, n_intervals)
    s13_n = n_intervals if n_intervals % 2 == 0 else n_intervals + 1
    s13_val = integrate_simpsons_13(a, b, s13_n)
    s38_n = n_intervals if n_intervals % 3 == 0 else n_intervals + (3 - (n_intervals % 3))
    s38_val = integrate_simpsons_38(a, b, s38_n)

    res = {
        "a": a,
        "b": b,
        "trapezoidal": {"n": n_intervals, "value": round(trap_val, 8)},
        "simpsons_13": {"n": s13_n, "value": round(s13_val, 8)},
        "simpsons_38": {"n": s38_n, "value": round(s38_val, 8)},
    }

    if exact_val is not None:
        res["exact"] = round(exact_val, 8)
        res["trapezoidal"]["error"] = round(abs(trap_val - exact_val), 10)
        res["simpsons_13"]["error"] = round(abs(s13_val - exact_val), 10)
        res["simpsons_38"]["error"] = round(abs(s38_val - exact_val), 10)

    return res


# ==========================================
# 3. NUMERICAL ROOT FINDING
# ==========================================

def solve_root_bisection(a: float, b: float, tol: float = 1e-6, max_iter: int = 50) -> Dict[str, Any]:
    """
    Bisection method for f(x) = x^4 - 3x^3 + 2x = 0.
    Finds root in [a, b] where f(a)*f(b) < 0.
    """
    fa = float(f_numpy(a))
    fb = float(f_numpy(b))

    if fa * fb > 0:
        return {
            "success": False,
            "message": f"f(a) and f(b) must have opposite signs. f({a})={fa:.4f}, f({b})={fb:.4f}",
            "iterations": []
        }

    iterations = []
    root = (a + b) / 2.0

    for i in range(1, max_iter + 1):
        m = (a + b) / 2.0
        fm = float(f_numpy(m))
        error_est = (b - a) / 2.0

        iterations.append({
            "step": i,
            "a": round(a, 6),
            "b": round(b, 6),
            "midpoint": round(m, 6),
            "f_midpoint": round(fm, 8),
            "error_bound": round(error_est, 8)
        })

        if abs(fm) < tol or error_est < tol:
            root = m
            return {
                "success": True,
                "method": "Bisection",
                "root": round(root, 6),
                "iterations_count": i,
                "iterations": iterations
            }

        if fa * fm < 0:
            b = m
            fb = fm
        else:
            a = m
            fa = fm

    return {
        "success": True,
        "method": "Bisection",
        "root": round(root, 6),
        "iterations_count": max_iter,
        "iterations": iterations
    }


def solve_root_newton_raphson(x0: float, tol: float = 1e-6, max_iter: int = 50) -> Dict[str, Any]:
    """
    Newton-Raphson method for f(x) = x^4 - 3x^3 + 2x = 0.
    Iteration: x_{n+1} = x_n - f(x_n)/f'(x_n).
    Includes tangent lines at each step for live graphic visualizer!
    """
    x_curr = float(x0)
    iterations = []

    for i in range(1, max_iter + 1):
        fx = float(f_numpy(x_curr))
        fpx = float(f_prime_numpy(x_curr))

        if abs(fpx) < 1e-12:
            return {
                "success": False,
                "message": f"Zero derivative encountered at step {i} (x = {x_curr:.4f}). Division by zero.",
                "iterations": iterations
            }

        dx = -fx / fpx
        x_next = x_curr + dx

        # Tangent line equation: y = fpx * (x - x_curr) + fx => y = fpx*x + (fx - fpx*x_curr)
        c_tangent = fx - fpx * x_curr

        iterations.append({
            "step": i,
            "x_n": round(x_curr, 6),
            "f_x_n": round(fx, 8),
            "f_prime_x_n": round(fpx, 8),
            "delta_x": round(dx, 8),
            "x_next": round(x_next, 6),
            "tangent_slope": round(fpx, 6),
            "tangent_intercept": round(c_tangent, 6)
        })

        if abs(fx) < tol or abs(dx) < tol:
            return {
                "success": True,
                "method": "Newton-Raphson",
                "root": round(x_next, 6),
                "iterations_count": i,
                "iterations": iterations
            }

        x_curr = x_next

    return {
        "success": True,
        "method": "Newton-Raphson",
        "root": round(x_curr, 6),
        "iterations_count": max_iter,
        "iterations": iterations
    }


def solve_root_secant(x0: float, x1: float, tol: float = 1e-6, max_iter: int = 50) -> Dict[str, Any]:
    """
    Secant method for f(x) = x^4 - 3x^3 + 2x = 0.
    Iteration: x_{n+1} = x_n - f(x_n) * (x_n - x_{n-1}) / (f(x_n) - f(x_{n-1})).
    """
    x_prev = float(x0)
    x_curr = float(x1)
    iterations = []

    for i in range(1, max_iter + 1):
        f_prev = float(f_numpy(x_prev))
        f_curr = float(f_numpy(x_curr))

        denom = f_curr - f_prev
        if abs(denom) < 1e-12:
            return {
                "success": False,
                "message": f"Denominator too close to zero at step {i}.",
                "iterations": iterations
            }

        x_next = x_curr - f_curr * (x_curr - x_prev) / denom
        dx = abs(x_next - x_curr)

        iterations.append({
            "step": i,
            "x_prev": round(x_prev, 6),
            "x_curr": round(x_curr, 6),
            "f_curr": round(f_curr, 8),
            "x_next": round(x_next, 6),
            "error_est": round(dx, 8)
        })

        if abs(f_curr) < tol or dx < tol:
            return {
                "success": True,
                "method": "Secant",
                "root": round(x_next, 6),
                "iterations_count": i,
                "iterations": iterations
            }

        x_prev = x_curr
        x_curr = x_next

    return {
        "success": True,
        "method": "Secant",
        "root": round(x_curr, 6),
        "iterations_count": max_iter,
        "iterations": iterations
    }


# ==========================================
# 4. NUMERICAL ODE SOLVER (VEHICLE DYNAMICS)
# ==========================================

def rk4_step(
    x: float,
    v: float,
    dt: float,
    accel_func: Callable[[float, float], float]
) -> Tuple[float, float]:
    """
    4th Order Runge-Kutta numerical integration for vehicle motion:
    dx/dt = v
    dv/dt = a(x, v)
    """
    # k1
    k1_v = accel_func(x, v)
    k1_x = v

    # k2
    k2_v = accel_func(x + 0.5 * dt * k1_x, v + 0.5 * dt * k1_v)
    k2_x = v + 0.5 * dt * k1_v

    # k3
    k3_v = accel_func(x + 0.5 * dt * k2_x, v + 0.5 * dt * k2_v)
    k3_x = v + 0.5 * dt * k2_v

    # k4
    k4_v = accel_func(x + dt * k3_x, v + dt * k3_v)
    k4_x = v + dt * k3_v

    x_new = x + (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
    v_new = v + (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)

    return float(x_new), float(v_new)


def euler_step(
    x: float,
    v: float,
    dt: float,
    accel_func: Callable[[float, float], float]
) -> Tuple[float, float]:
    """Euler method for vehicle motion: dx = v*dt, dv = a*dt."""
    a = accel_func(x, v)
    x_new = x + v * dt
    v_new = v + a * dt
    return float(x_new), float(v_new)


# ==============================================================================
# 5. ERROR ANALYSIS & NUMERICAL ARRAYS GENERATOR (NUMPY)
# ==============================================================================

def calculate_error_analysis(numerical_val: float, exact_val: float) -> Dict[str, float]:
    """
    Error analysis:
    - Absolute error = |numerical - exact|
    - Percentage error = (|numerical - exact| / |exact|) * 100%
    """
    abs_err = abs(numerical_val - exact_val)
    if abs(exact_val) > 1e-12:
        pct_err = (abs_err / abs(exact_val)) * 100.0
    else:
        pct_err = 0.0
    return {
        "absolute_error": float(abs_err),
        "percentage_error": float(pct_err)
    }


def generate_numerical_arrays(
    a: float = 0.0,
    b: float = 2.0,
    n_points: int = 101,
    h: float = 0.001
) -> Dict[str, Any]:
    """
    Generate numerical arrays using NumPy for:
    - Function values: f(x)
    - Central difference derivative: [f(x+h) - f(x-h)] / (2h)
    - Cumulative trapezoidal integration: ∫_0^x f(u) du
    """
    x_grid = np.linspace(a, b, n_points, dtype=np.float64)
    y_grid = f_numpy(x_grid)

    # Central difference derivative array across entire grid with step h
    deriv_grid = (f_numpy(x_grid + h) - f_numpy(x_grid - h)) / (2.0 * h)

    # Cumulative trapezoidal integration array across grid
    dx = np.diff(x_grid)
    trap_slices = 0.5 * dx * (y_grid[:-1] + y_grid[1:])
    cum_trap = np.concatenate(([0.0], np.cumsum(trap_slices)))

    # Analytical exact values for reference
    f_prime_exact = f_prime_numpy(x_grid)
    # F(x) = x^5/5 - 3x^4/4 + x^2. Since a=0, F(a)=0
    exact_integral_grid = (x_grid**5) / 5.0 - (3.0 * (x_grid**4)) / 4.0 + (x_grid**2)

    return {
        "a": a,
        "b": b,
        "n_points": n_points,
        "h": h,
        "x": x_grid.tolist(),
        "f_x": y_grid.tolist(),
        "central_difference_derivative": deriv_grid.tolist(),
        "cumulative_trapezoidal_integral": cum_trap.tolist(),
        "exact_derivative": f_prime_exact.tolist(),
        "exact_integral": exact_integral_grid.tolist()
    }


def generate_racing_model_arrays(
    K: float = 20.0,
    T: float = 10.0,
    x_max: float = 2.0,
    n_points: int = 101,
    h: float = 0.001
) -> Dict[str, Any]:
    """
    Racing Model implementation:
    - Normalized time: x = t / T
    - Target velocity: v_model = K * f(x)
    - Target acceleration: a_model = (K / T) * f'(x)
    - Target displacement: s_model = K * T * ∫_0^x f(u) du
    Parameters K and T are fully configurable.
    """
    t_max = float(x_max * T)
    t_arr = np.linspace(0.0, t_max, n_points, dtype=np.float64)
    x_arr = t_arr / float(T)

    f_arr = f_numpy(x_arr)
    v_model = float(K) * f_arr

    # Analytical f'(x) and numerical central difference
    f_prime_exact = f_prime_numpy(x_arr)
    f_prime_central = (f_numpy(x_arr + h) - f_numpy(x_arr - h)) / (2.0 * h)
    a_model_exact = (float(K) / float(T)) * f_prime_exact
    a_model_num = (float(K) / float(T)) * f_prime_central

    # Analytical ∫_0^x f(u) du and numerical cumulative trapezoid
    f_integ_exact = (x_arr**5) / 5.0 - (3.0 * (x_arr**4)) / 4.0 + (x_arr**2)
    s_model_exact = float(K) * float(T) * f_integ_exact

    # Numerical cumulative trapezoid for displacement
    dx = np.diff(x_arr)
    cum_trap = np.concatenate(([0.0], np.cumsum(0.5 * dx * (f_arr[:-1] + f_arr[1:]))))
    s_model_numerical = float(K) * float(T) * cum_trap

    return {
        "parameters": {
            "K": float(K),
            "T": float(T),
            "x_max": float(x_max),
            "t_max": float(t_max),
            "h": float(h),
            "n_points": n_points
        },
        "formulas": {
            "normalized_time": "x = t / T",
            "velocity": "v_model = K * f(x)",
            "acceleration": "a_model = (K/T) * f'(x)",
            "displacement": "s_model = K * T * integral(f(u), 0, x)"
        },
        "arrays": {
            "time_t": t_arr.tolist(),
            "normalized_time_x": x_arr.tolist(),
            "function_f_x": f_arr.tolist(),
            "target_velocity_v": v_model.tolist(),
            "target_acceleration_a_exact": a_model_exact.tolist(),
            "target_acceleration_a_numerical": a_model_num.tolist(),
            "target_displacement_s_exact": s_model_exact.tolist(),
            "target_displacement_s_numerical": s_model_numerical.tolist()
        }
    }

