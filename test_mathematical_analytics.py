"""
Automated Verification Suite for Mathematical Analytics Panel & Dynamic Recalculation
Course: Numerical and Symbolic Computing
Tests that all 8 mathematical analytics requirements, comparison table,
and controls (h, n, T, K) function dynamically without hardcoding.
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.calculations import (
    get_complete_mathematical_analysis,
    update_engine_config,
    get_engine_config
)
from backend.symbolic import get_full_symbolic_summary
from backend.numerical import (
    central_difference_derivative,
    integrate_trapezoidal,
    calculate_error_analysis,
    generate_racing_model_arrays
)

def main():
    print("==================================================================")
    print("MATHEMATICAL ANALYTICS PANEL & RECALCULATION VERIFICATION")
    print("Course: Numerical and Symbolic Computing")
    print("Strict Invariant: f(x) = x^4 - 3x^3 + 2x")
    print("==================================================================")

    # 1. Reset to standard parameters
    update_engine_config(K=20.0, T=10.0, h=0.001, n=100, eval_x=2.0, integral_a=0.0, integral_b=2.0)
    analysis = get_complete_mathematical_analysis()

    print("\n--- 1. Testing Default Mathematical Analytics Output ---")
    sym = analysis["sympy_calculations"]
    cd = analysis["numerical_methods"]["central_difference"]
    ct = analysis["numerical_methods"]["composite_trapezoidal"]

    # 1. Original mathematical equation
    assert "x**4 - 3*x**3 + 2*x" in sym["original_function"]["string"] or "x^4 - 3*x^3 + 2*x" in sym["original_function"]["equation"]
    print("✓ 1. Original Equation:         ", sym["original_function"]["equation"])

    # 2. Symbolic derivative using SymPy
    assert sym["first_derivative"]["string"] == "4*x**3 - 9*x**2 + 2"
    assert sym["f_prime_at_2"]["value"] == -2.0
    print("✓ 2. Symbolic Derivative:       ", sym["first_derivative"]["equation"], f"-> f'(2) = {sym['f_prime_at_2']['value']}")

    # 3. Numerical derivative using Central Difference
    assert abs(cd["numerical_value"] - (-2.0)) < 1e-4
    print("✓ 3. Numerical Derivative (CD): ", f"Value = {cd['numerical_value']:.8f} (h = {cd['h']})")

    # 4. Symbolic indefinite integral
    assert "x**5/5 - 3*x**4/4 + x**2" in sym["indefinite_integral"]["string"]
    print("✓ 4. Symbolic Indefinite Integ: ", sym["indefinite_integral"]["equation"])

    # 5. Symbolic definite integral
    assert sym["definite_integral_0_to_2"]["value"] == -1.6
    print("✓ 5. Symbolic Definite Integ:   ", f"∫₀² f(x)dx = {sym['definite_integral_0_to_2']['value']} ({sym['definite_integral_0_to_2']['exact_fraction']})")

    # 6. Numerical integral using Trapezoidal Rule
    assert abs(ct["numerical_value"] - (-1.6)) < 1e-3
    print("✓ 6. Numerical Integral (Trap): ", f"Value = {ct['numerical_value']:.8f} (n = {ct['n_intervals']})")

    # 7. Absolute error
    assert cd["absolute_error"] > 0
    assert ct["absolute_error"] > 0
    print("✓ 7. Absolute Errors:            Derivative |ε| =", cd["absolute_error"], "| Integral |ε| =", ct["absolute_error"])

    # 8. Percentage error
    assert cd["percentage_error"] > 0
    assert ct["percentage_error"] > 0
    print("✓ 8. Percentage Errors:          Derivative % =", cd["percentage_error"], "| Integral % =", ct["percentage_error"])

    # --- 2. Testing Dynamic Parameter Changes via Controls ---
    print("\n--- 2. Testing Dynamic Parameter Tuning (h, n, T, K) ---")

    # Test A: Changing h to finer step (0.0001)
    update_engine_config(h=0.0001)
    recalc_h = get_complete_mathematical_analysis()
    cd_fine = recalc_h["numerical_methods"]["central_difference"]
    assert cd_fine["h"] == 0.0001
    assert cd_fine["absolute_error"] < cd["absolute_error"], "Error must decrease with smaller h"
    print(f"✓ Control 'h' changed 0.001 -> 0.0001: Error reduced from {cd['absolute_error']:.2e} to {cd_fine['absolute_error']:.2e} (O(h²))")

    # Test B: Changing n to higher intervals (500)
    update_engine_config(n=500)
    recalc_n = get_complete_mathematical_analysis()
    ct_fine = recalc_n["numerical_methods"]["composite_trapezoidal"]
    assert ct_fine["n_intervals"] == 500
    assert ct_fine["absolute_error"] < ct["absolute_error"], "Error must decrease with larger n"
    print(f"✓ Control 'n' changed 100 -> 500: Error reduced from {ct['absolute_error']:.2e} to {ct_fine['absolute_error']:.2e} (O(1/n²))")

    # Test C: Changing T (duration) and K (speed scale)
    update_engine_config(K=35.0, T=15.0)
    recalc_kinematics = get_complete_mathematical_analysis()
    racing_params = recalc_kinematics["racing_model"]["parameters"]
    arrays = recalc_kinematics["numerical_arrays"]

    assert racing_params["K"] == 35.0
    assert racing_params["T"] == 15.0
    # t_max should now be 2.0 * 15.0 = 30.0 s
    assert abs(arrays["racing_model_time_t"][-1] - 30.0) < 1e-4
    # Peak target velocity should scale with K = 35.0
    max_v = max(arrays["racing_model_velocity_v"])
    assert max_v > 0 and abs(max_v - (35.0 * 0.6926)) < 1.0
    print(f"✓ Controls 'K' & 'T' changed (K=35.0, T=15.0s): Numerical arrays regenerated (t_max = {arrays['racing_model_time_t'][-1]}s)")

    # Test D: Resetting back to default parameters
    update_engine_config(K=20.0, T=10.0, h=0.001, n=100)
    recalc_default = get_complete_mathematical_analysis()
    assert recalc_default["racing_model"]["parameters"]["K"] == 20.0
    assert recalc_default["numerical_methods"]["central_difference"]["h"] == 0.001
    print("✓ Reset Defaults: Engine successfully restored to course defaults (K=20, T=10, h=0.001, n=100)")

    print("\n==================================================================")
    print("ALL MATHEMATICAL ANALYTICS REQUIREMENTS PASSED (100%)!")
    print("==================================================================")
    return True

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)

