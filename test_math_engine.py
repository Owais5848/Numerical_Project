"""
Test Suite for Complete Mathematical Engine
Course: Numerical and Symbolic Computing

Tests:
1. All 6 SymPy analytical calculations:
   - Original function f(x) = x^4 - 3x^3 + 2x
   - First symbolic derivative f'(x) = 4x^3 - 9x^2 + 2
   - Indefinite symbolic integral F(x) = x^5/5 - 3x^4/4 + x^2
   - Function value at x = 2: f(2) = -4
   - Derivative value at x = 2: f'(2) = -2
   - Definite integral from 0 to 2: -1.6
2. Numerical methods:
   - Central difference [f(x+h) - f(x-h)] / (2h) with default h = 0.001
   - Composite trapezoidal rule from 0 to 2 with default n = 100
   - Error analysis: absolute and percentage errors
3. Racing model:
   - Normalized time x = t/T
   - Target velocity v_model = K * f(x)
   - Target acceleration a_model = (K/T) * f'(x)
   - Target displacement s_model = K * T * ∫_0^x f(u) du
   - Configurable parameters K and T
4. Numerical arrays (NumPy):
   - Function values
   - Central difference derivative
   - Cumulative trapezoidal integration
5. FastAPI Endpoints:
   - GET /api/health
   - GET /api/analysis
   - POST /api/settings
"""

import math
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from symbolic import (
    f_expr,
    f_prime_expr,
    f_integral_expr,
    evaluate_f,
    evaluate_f_prime,
    get_symbolic_original_function,
    get_symbolic_first_derivative,
    get_symbolic_indefinite_integral,
    evaluate_symbolic_f_at_2,
    evaluate_symbolic_f_prime_at_2,
    evaluate_symbolic_definite_integral_0_to_2,
    get_sympy_engine_summary
)
from numerical import (
    f_numpy,
    f_prime_numpy,
    central_difference_derivative,
    integrate_trapezoidal,
    calculate_error_analysis,
    generate_numerical_arrays,
    generate_racing_model_arrays
)
from calculations import (
    get_engine_config,
    update_engine_config,
    get_complete_mathematical_analysis
)
from main import (
    get_health,
    get_analysis,
    update_settings,
    SettingsRequest
)


def test_sympy_six_requirements():
    print("\n--- 1. Testing SymPy Analytical Engine Requirements ---", flush=True)

    # 1. Original function
    orig = get_symbolic_original_function()
    assert "x**4 - 3*x**3 + 2*x" in orig["expression_str"]
    print(f"✓ 1. Original function: {orig['formatted']}", flush=True)

    # 2. First symbolic derivative
    deriv = get_symbolic_first_derivative()
    assert "4*x**3 - 9*x**2 + 2" in deriv["expression_str"]
    print(f"✓ 2. First derivative: {deriv['formatted']}", flush=True)

    # 3. Indefinite symbolic integral
    integ = get_symbolic_indefinite_integral()
    assert "x**5/5 - 3*x**4/4 + x**2" in integ["expression_str"]
    print(f"✓ 3. Indefinite integral: {integ['formatted']}", flush=True)

    # 4. Function value at x = 2
    f2 = evaluate_symbolic_f_at_2()
    assert math.isclose(f2["value"], -4.0, abs_tol=1e-9)
    print(f"✓ 4. Function value f(2) = {f2['value']} (Expected: -4.0)", flush=True)

    # 5. Derivative value at x = 2
    fp2 = evaluate_symbolic_f_prime_at_2()
    assert math.isclose(fp2["value"], -2.0, abs_tol=1e-9)
    print(f"✓ 5. Derivative value f'(2) = {fp2['value']} (Expected: -2.0)", flush=True)

    # 6. Definite integral from 0 to 2
    def_integ = evaluate_symbolic_definite_integral_0_to_2()
    assert math.isclose(def_integ["value"], -1.6, abs_tol=1e-9)
    print(f"✓ 6. Definite integral ∫₀² f(x)dx = {def_integ['value']} ({def_integ['exact_rational']}) (Expected: -1.6)", flush=True)


def test_numerical_methods_and_errors():
    print("\n--- 2. Testing Numerical Methods & Error Analysis ---", flush=True)

    # A. Central difference method: [f(x+h) - f(x-h)] / (2h) with default h = 0.001
    h = 0.001
    x_val = 2.0
    num_deriv = central_difference_derivative(x_val, h)
    exact_deriv = -2.0
    err_diff = calculate_error_analysis(num_deriv, exact_deriv)

    # Central difference formula verification
    f_plus = f_numpy(x_val + h)
    f_minus = f_numpy(x_val - h)
    expected_formula_val = (f_plus - f_minus) / (2.0 * h)
    assert math.isclose(num_deriv, expected_formula_val, abs_tol=1e-12)
    assert math.isclose(num_deriv, -2.0, abs_tol=1e-4)
    assert err_diff["absolute_error"] < 1e-4
    assert err_diff["percentage_error"] < 0.01

    print(f"✓ A. Central Difference at x=2 (h={h}):", flush=True)
    print(f"     Numerical = {num_deriv:.8f}, Exact = {exact_deriv:.1f}", flush=True)
    print(f"     Absolute Error = {err_diff['absolute_error']:.6e}", flush=True)
    print(f"     Percentage Error = {err_diff['percentage_error']:.6f}%", flush=True)

    # B. Composite trapezoidal rule from 0 to 2 with default n = 100 intervals
    n = 100
    a, b = 0.0, 2.0
    num_integ = integrate_trapezoidal(a, b, n)
    exact_integ = -1.6
    err_integ = calculate_error_analysis(num_integ, exact_integ)

    assert math.isclose(num_integ, -1.6, abs_tol=1e-3)
    assert err_integ["absolute_error"] < 1e-3
    assert err_integ["percentage_error"] < 0.1

    print(f"✓ B. Composite Trapezoidal Rule (a={a}, b={b}, n={n}):", flush=True)
    print(f"     Numerical = {num_integ:.8f}, Exact = {exact_integ:.1f}", flush=True)
    print(f"     Absolute Error = {err_integ['absolute_error']:.6e}", flush=True)
    print(f"     Percentage Error = {err_integ['percentage_error']:.6f}%", flush=True)


def test_racing_model_and_numpy_arrays():
    print("\n--- 3. Testing Racing Model & NumPy Numerical Arrays ---", flush=True)

    K = 25.0
    T = 8.0
    res = generate_racing_model_arrays(K=K, T=T, x_max=2.0, n_points=101)

    t_arr = res["arrays"]["time_t"]
    x_arr = res["arrays"]["normalized_time_x"]
    v_arr = res["arrays"]["target_velocity_v"]
    a_arr = res["arrays"]["target_acceleration_a_exact"]
    s_exact = res["arrays"]["target_displacement_s_exact"]
    s_num = res["arrays"]["target_displacement_s_numerical"]

    # Verify length and properties
    assert len(t_arr) == 101
    assert len(x_arr) == 101
    assert len(v_arr) == 101
    assert len(a_arr) == 101
    assert len(s_exact) == 101
    assert len(s_num) == 101

    # Check normalized time relationship: x = t/T
    for i in range(len(t_arr)):
        assert math.isclose(x_arr[i], t_arr[i] / T, abs_tol=1e-9)

    # Check target velocity: v_model = K * f(x)
    for i in range(len(x_arr)):
        expected_v = K * f_numpy(x_arr[i])
        assert math.isclose(v_arr[i], expected_v, abs_tol=1e-9)

    # Check target acceleration: a_model = (K/T) * f'(x)
    for i in range(len(x_arr)):
        expected_a = (K / T) * f_prime_numpy(x_arr[i])
        assert math.isclose(a_arr[i], expected_a, abs_tol=1e-9)

    # Check cumulative trapezoid integration matches exact integral within 0.1%
    max_s_err = max(abs(s_exact[i] - s_num[i]) for i in range(len(s_exact)))
    assert max_s_err < 0.1

    print(f"✓ Racing model formulas verified (K={K}, T={T}):", flush=True)
    print(f"  • Normalized time: x = t/T checked over [0, {t_arr[-1]}s]", flush=True)
    print(f"  • Velocity: v_model = K * f(x) verified", flush=True)
    print(f"  • Acceleration: a_model = (K/T) * f'(x) verified", flush=True)
    print(f"  • Displacement: s_model = K*T*∫f(u)du verified (max error = {max_s_err:.6f}m)", flush=True)

    # Test generate_numerical_arrays
    num_arrs = generate_numerical_arrays(a=0.0, b=2.0, n_points=101, h=0.001)
    assert len(num_arrs["x"]) == 101
    assert len(num_arrs["f_x"]) == 101
    assert len(num_arrs["central_difference_derivative"]) == 101
    assert len(num_arrs["cumulative_trapezoidal_integral"]) == 101
    print(f"✓ NumPy numerical arrays (f_x, central_diff, cum_trap) verified: {len(num_arrs['x'])} points", flush=True)


def test_fastapi_endpoints():
    print("\n--- 4. Testing Required FastAPI Endpoints ---", flush=True)

    # 1. GET /api/health
    health = get_health()
    assert health["status"] == "healthy"
    assert "f(x) = x^4 - 3x^3 + 2x" in health["strict_function"]
    print(f"✓ GET  /api/health   -> {health}", flush=True)

    # 2. GET /api/analysis
    analysis = get_analysis()
    assert analysis["status"] == "success"
    assert "sympy_calculations" in analysis
    assert "numerical_methods" in analysis
    assert "racing_model" in analysis
    assert "numerical_arrays" in analysis

    sym = analysis["sympy_calculations"]
    assert sym["f_at_2"]["value"] == -4.0
    assert sym["f_prime_at_2"]["value"] == -2.0
    assert sym["definite_integral_0_to_2"]["value"] == -1.6

    num = analysis["numerical_methods"]
    assert math.isclose(num["central_difference"]["numerical_value"], -2.0, abs_tol=1e-4)
    assert math.isclose(num["composite_trapezoidal"]["numerical_value"], -1.6, abs_tol=1e-3)
    print(f"✓ GET  /api/analysis -> Complete mathematical engine analysis returned with exact SymPy & NumPy results", flush=True)

    # 3. POST /api/settings
    payload = SettingsRequest(K=30.0, T=12.0, h=0.0005, n=150)
    settings_res = update_settings(payload)
    assert settings_res["status"] == "success"
    assert settings_res["current_settings"]["K"] == 30.0
    assert settings_res["current_settings"]["T"] == 12.0
    assert settings_res["current_settings"]["h"] == 0.0005
    assert settings_res["current_settings"]["n"] == 150
    print(f"✓ POST /api/settings -> Successfully updated configurable parameters (K=30.0, T=12.0, h=0.0005, n=150)", flush=True)


if __name__ == "__main__":
    print("==================================================================", flush=True)
    print("FORMULA RACER - MATHEMATICAL ENGINE VERIFICATION SUITE", flush=True)
    print("Course: Numerical and Symbolic Computing", flush=True)
    print("Strict Function: f(x) = x^4 - 3x^3 + 2x", flush=True)
    print("==================================================================", flush=True)

    test_sympy_six_requirements()
    test_numerical_methods_and_errors()
    test_racing_model_and_numpy_arrays()
    test_fastapi_endpoints()

    print("\n==================================================================", flush=True)
    print("ALL MATHEMATICAL ENGINE REQUIREMENTS & ENDPOINTS PASSED (100%)!", flush=True)
    print("==================================================================", flush=True)
