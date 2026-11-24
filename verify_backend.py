"""
Synchronous Verification Suite for FORMULA RACER Backend
Validates every endpoint and strictly checks f(x) = x^4 - 3x^3 + 2x.
"""

import math
import sys
from backend.main import (
    get_project_info,
    get_symbolic_analysis,
    get_symbolic_roots,
    get_symbolic_critical_points,
    get_symbolic_inflection_points,
    calculate_taylor,
    calculate_tangent_normal,
    get_numerical_track,
    analyze_differentiation,
    analyze_integration,
    run_root_finding,
    get_telemetry,
    step_physics,
    serve_index,
    TaylorRequest,
    TangentNormalRequest,
    DifferentiationRequest,
    IntegrationRequest,
    RootFindingRequest,
    TelemetryRequest,
    StepRequest
)

def test_suite():
    print("==================================================================", flush=True)
    print("FORMULA RACER - VERIFYING ALL BACKEND MODULES & API ENDPOINTS", flush=True)
    print("STRICT FUNCTION: f(x) = x^4 - 3x^3 + 2x", flush=True)
    print("==================================================================", flush=True)

    # 1. Info endpoint
    info = get_project_info()
    assert "x^4 - 3x^3 + 2x" in info["strict_function"]["equation"]
    print("✓ 1. GET /api/info -> Strict equation verified", flush=True)

    # 2. Symbolic Analysis
    sym = get_symbolic_analysis()
    assert "4*x**3 - 9*x**2 + 2" in sym["derivatives"]["first"]["str"]
    assert "12*x**2 - 18*x" in sym["derivatives"]["second"]["str"]
    assert len(sym["roots"]) == 4
    root_vals = [r["value"] for r in sym["roots"]]
    assert math.isclose(root_vals[0], 1 - math.sqrt(3), abs_tol=1e-3)
    assert math.isclose(root_vals[1], 0.0, abs_tol=1e-3)
    assert math.isclose(root_vals[2], 1.0, abs_tol=1e-3)
    assert math.isclose(root_vals[3], 1 + math.sqrt(3), abs_tol=1e-3)
    print(f"✓ 2. GET /api/symbolic/analysis -> Derivatives & 4 roots verified: {root_vals}", flush=True)

    # 3. Critical points & Inflection points
    crit = get_symbolic_critical_points()
    assert len(crit["critical_points"]) == 3
    inflec = get_symbolic_inflection_points()
    assert len(inflec["inflection_points"]) == 2
    assert math.isclose(inflec["inflection_points"][0]["x"], 0.0, abs_tol=1e-3)
    assert math.isclose(inflec["inflection_points"][1]["x"], 1.5, abs_tol=1e-3)
    print(f"✓ 3. GET /api/symbolic/critical-points & inflection-points -> 3 extrema, 2 inflection points (x=0, 1.5)", flush=True)

    # 4. Taylor series
    taylor = calculate_taylor(TaylorRequest(x0=0.0, order=4))
    assert "x**4 - 3*x**3 + 2*x" in taylor["taylor_polynomial_str"]
    print(f"✓ 4. POST /api/symbolic/taylor -> Taylor polynomial expansion degree 4 verified", flush=True)

    # 5. Tangent and Normal
    tn = calculate_tangent_normal(TangentNormalRequest(x0=1.0))
    assert math.isclose(tn["slope"], -3.0, abs_tol=1e-4)
    assert math.isclose(tn["tangent"]["m"], -3.0, abs_tol=1e-4)
    assert math.isclose(tn["normal"]["m"], 1.0/3.0, abs_tol=1e-4)
    print(f"✓ 5. POST /api/symbolic/tangent-normal -> Tangent m={tn['slope']}, Normal m={tn['normal']['m']:.4f}", flush=True)

    # 6. Track Profile
    track = get_numerical_track()
    assert len(track["x"]) == 400
    assert len(track["y"]) == 400
    assert len(track["curvature"]) == 400
    assert track["total_arc_length"] > 0
    print(f"✓ 6. GET /api/numerical/track -> 400 discretized nodes, length={track['total_arc_length']:.2f}m", flush=True)

    # 7. Numerical Differentiation
    diff = analyze_differentiation(DifferentiationRequest(x=1.0, h_list=[0.1, 0.01, 0.001]))
    assert math.isclose(diff["exact_derivative"], -3.0, abs_tol=1e-4)
    for s in diff["steps"]:
        assert s["central_error"] <= s["forward_error"] + 1e-9
    print(f"✓ 7. POST /api/numerical/differentiation -> Finite differences O(h) vs O(h^2) verified", flush=True)

    # 8. Numerical Integration
    integ = analyze_integration(IntegrationRequest(a=0.0, b=2.0, n=100))
    assert math.isclose(integ["exact"], -1.6, abs_tol=1e-4)
    assert math.isclose(integ["trapezoidal"]["value"], -1.6, abs_tol=1e-3)
    assert math.isclose(integ["simpsons_13"]["value"], -1.6, abs_tol=1e-5)
    assert math.isclose(integ["simpsons_38"]["value"], -1.6, abs_tol=1e-5)
    print(f"✓ 8. POST /api/numerical/integration -> Exact -1.6 vs Simpson 1/3: {integ['simpsons_13']['value']:.6f}", flush=True)

    # 9. Root Finding
    nr = run_root_finding(RootFindingRequest(method="newton", x0=0.8, tol=1e-6))
    assert nr["success"] is True and math.isclose(nr["root"], 1.0, abs_tol=1e-4)
    bis = run_root_finding(RootFindingRequest(method="bisection", a=0.5, b=1.5, tol=1e-5))
    assert bis["success"] is True and math.isclose(bis["root"], 1.0, abs_tol=1e-4)
    sec = run_root_finding(RootFindingRequest(method="secant", x0=0.8, x1=1.2, tol=1e-5))
    assert sec["success"] is True and math.isclose(sec["root"], 1.0, abs_tol=1e-4)
    print(f"✓ 9. POST /api/numerical/roots -> Newton (steps={nr['iterations_count']}), Bisection (steps={bis['iterations_count']}), Secant (steps={sec['iterations_count']}) converged to root 1.0000", flush=True)

    # 10. Vehicle Telemetry
    telem = get_telemetry(TelemetryRequest(x=1.0, velocity=15.0, throttle=0.8, brake=0.0))
    assert telem["speed_kmh"] == 54.0
    assert "forces" in telem and "energy" in telem
    print(f"✓ 10. POST /api/physics/telemetry -> Speed: 54 km/h, Normal force: {telem['forces']['normal_force']} N", flush=True)

    # 11. Physics Stepping
    rk4 = step_physics(StepRequest(x=0.0, velocity=5.0, throttle=1.0, brake=0.0, dt=0.016, integrator="rk4"))
    assert rk4["x"] > 0.0
    euler = step_physics(StepRequest(x=0.0, velocity=5.0, throttle=1.0, brake=0.0, dt=0.016, integrator="euler"))
    assert euler["x"] > 0.0
    print(f"✓ 11. POST /api/physics/step -> RK4 (x={rk4['x']:.4f}) and Euler (x={euler['x']:.4f}) integration verified", flush=True)

    print("==================================================================", flush=True)
    print("ALL 11 BACKEND API TESTS PASSED PERFECTLY!", flush=True)
    print("==================================================================", flush=True)

if __name__ == "__main__":
    test_suite()
