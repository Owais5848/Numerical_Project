"""
Verification of Mathematical Interpolation for Chart.js Live Graphs
Course: Numerical and Symbolic Computing
Tests that JavaScript-side linear interpolation of precomputed NumPy arrays
faithfully reproduces f(x), f'(x), and the integral without API polling.
"""

import math
import sys
import os

# Ensure backend can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.numerical import generate_racing_model_arrays, f_numpy, f_prime_numpy

def js_interpolate(time_arr, val_arr, t):
    """Exact Python mirror of the JavaScript linear interpolation implementation in charts.js."""
    if not time_arr or len(time_arr) == 0:
        return 0.0
    if t <= time_arr[0]:
        return val_arr[0]
    n = len(time_arr)
    if t >= time_arr[n - 1]:
        return val_arr[n - 1]

    t0 = time_arr[0]
    t_end = time_arr[n - 1]
    ratio = (t - t0) / (t_end - t0)
    idx = math.floor(ratio * (n - 1))
    idx = max(0, min(n - 2, idx))

    while idx < n - 1 and time_arr[idx + 1] < t:
        idx += 1
    while idx > 0 and time_arr[idx] > t:
        idx -= 1

    t1 = time_arr[idx]
    t2 = time_arr[idx + 1]
    v1 = val_arr[idx]
    v2 = val_arr[idx + 1]

    if t2 == t1:
        return v1
    factor = (t - t1) / (t2 - t1)
    return v1 + factor * (v2 - v1)

def exact_integral_f(x):
    """Exact indefinite integral: F(x) = x^5/5 - 3x^4/4 + x^2."""
    return (x**5) / 5.0 - 0.75 * (x**4) + (x**2)

def main():
    print("==================================================================")
    print("CHART.JS LIVE MATHEMATICAL GRAPHS - INTERPOLATION VERIFICATION")
    print("Course: Numerical and Symbolic Computing")
    print("Strict Invariant: f(x) = x^4 - 3x^3 + 2x")
    print("==================================================================")

    K = 20.0
    T = 10.0
    res = generate_racing_model_arrays(K=K, T=T, x_max=2.0, n_points=101, h=0.001)
    arrays = res["arrays"]

    time_arr = arrays["time_t"]
    v_arr = arrays["target_velocity_v"]
    a_arr = arrays["target_acceleration_a_exact"]
    s_arr = arrays["target_displacement_s_exact"]

    print(f"✓ Precomputed NumPy arrays loaded: {len(time_arr)} points over t in [0, {time_arr[-1]}s]")

    # Test test times across the time trial domain
    test_times = [0.0, 1.25, 2.5, 5.0, 7.33, 10.0, 12.8, 15.0, 17.5, 20.0]

    max_v_err = 0.0
    max_a_err = 0.0
    max_s_err = 0.0

    print("\n--- Verifying Exact Mathematical Accuracy of Interpolated Graphs ---")
    for t in test_times:
        x = t / T
        # Exact values
        exact_f = float(f_numpy(x))
        exact_fprime = float(f_prime_numpy(x))
        exact_integ = exact_integral_f(x)

        exact_v = K * exact_f
        exact_a = (K / T) * exact_fprime
        exact_s = K * T * exact_integ

        # Interpolated values from precomputed NumPy arrays
        interp_v = js_interpolate(time_arr, v_arr, t)
        interp_a = js_interpolate(time_arr, a_arr, t)
        interp_s = js_interpolate(time_arr, s_arr, t)

        err_v = abs(interp_v - exact_v)
        err_a = abs(interp_a - exact_a)
        err_s = abs(interp_s - exact_s)

        if err_v > max_v_err: max_v_err = err_v
        if err_a > max_a_err: max_a_err = err_a
        if err_s > max_s_err: max_s_err = err_s

        print(f"t={t:5.2f}s (x={x:4.2f}): v_err={err_v:.4e} | a_err={err_a:.4e} | s_err={err_s:.4e}")

    # Maximum errors must be tiny (linear interpolation on 101 points has O(h^2) error ~ 0.01)
    assert max_v_err < 0.05, f"Velocity interpolation error too large: {max_v_err}"
    assert max_a_err < 0.05, f"Acceleration interpolation error too large: {max_a_err}"
    assert max_s_err < 0.1, f"Displacement interpolation error too large: {max_s_err}"

    print(f"\n✓ Max Velocity error:     {max_v_err:.6f} m/s (Passed < 0.05)")
    print(f"✓ Max Acceleration error: {max_a_err:.6f} m/s² (Passed < 0.05)")
    print(f"✓ Max Displacement error: {max_s_err:.6f} m (Passed < 0.10)")

    print("\n==================================================================")
    print("ALL CHART INTERPOLATION & MATHEMATICAL PROFILES PASSED (100%)!")
    print("==================================================================")
    return True

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
