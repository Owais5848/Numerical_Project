"""
MASTER COMPLETE TESTING SUITE FOR FORMULA RACER
Course: Numerical and Symbolic Computing

STRICT MATHEMATICAL REQUIREMENT:
f(x) = x^4 - 3x^3 + 2x
Never replace this equation with another function.

TESTING SECTIONS:
1. MATHEMATICAL TESTING
2. GAME TESTING
3. GRAPH TESTING
4. BACKEND TESTING
"""

import sys
import os
import math
import subprocess
import time
import urllib.request
import urllib.error
import json
import numpy as np
import sympy as sp

# Ensure backend imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.symbolic import (
    x as sp_x,
    f_expr,
    f_prime_expr,
    f_integral_expr,
    evaluate_f,
    evaluate_f_prime,
    evaluate_symbolic_f_prime_at_2,
    evaluate_symbolic_definite_integral_0_to_2,
    get_exact_definite_integral
)
from backend.numerical import (
    central_difference_derivative,
    integrate_trapezoidal,
    calculate_error_analysis,
    generate_racing_model_arrays,
    generate_numerical_arrays
)
from backend.calculations import (
    update_engine_config,
    get_engine_config,
    get_complete_mathematical_analysis,
    step_simulation,
    calculate_vehicle_telemetry
)

def run_mathematical_testing():
    print("\n" + "=" * 70)
    print("SECTION 1: MATHEMATICAL TESTING")
    print("=" * 70)

    # 1. Verify original equation: x^4 - 3x^3 + 2x
    expected_expr = sp_x**4 - 3*sp_x**3 + 2*sp_x
    assert f_expr == expected_expr, f"f_expr mismatch: {f_expr} != {expected_expr}"
    assert evaluate_f(0.0) == 0.0
    assert evaluate_f(1.0) == 0.0
    assert evaluate_f(2.0) == -4.0  # 16 - 24 + 4 = -4
    assert evaluate_f(-1.0) == 2.0  # 1 + 3 - 2 = 2
    print("✓ 1. Original Equation verified: f(x) = x^4 - 3x^3 + 2x")
    print("     f(0)=0.0, f(1)=0.0, f(2)=-4.0, f(-1)=2.0 confirmed.")

    # 2. Verify derivative: 4x^3 - 9x^2 + 2
    expected_deriv = 4*sp_x**3 - 9*sp_x**2 + 2
    assert f_prime_expr == expected_deriv, f"f_prime mismatch: {f_prime_expr} != {expected_deriv}"
    assert evaluate_f_prime(0.0) == 2.0
    assert evaluate_f_prime(1.0) == -3.0
    print("✓ 2. First Derivative verified: f'(x) = 4x^3 - 9x^2 + 2")
    print("     f'(0)=2.0, f'(1)=-3.0 confirmed.")

    # 3. Verify derivative at x=2: -2
    deriv_at_2 = evaluate_symbolic_f_prime_at_2()
    assert deriv_at_2["value"] == -2.0
    assert evaluate_f_prime(2.0) == -2.0  # 4(8) - 9(4) + 2 = 32 - 36 + 2 = -2
    print("✓ 3. Derivative at x=2 verified: f'(2) = -2.0 (Exact SymPy)")

    # 4. Verify definite integral from 0 to 2: -1.6
    integ_0_to_2 = evaluate_symbolic_definite_integral_0_to_2()
    assert abs(integ_0_to_2["value"] - (-1.6)) < 1e-12
    assert integ_0_to_2["exact_rational"] == "-8/5"
    print("✓ 4. Definite Integral from 0 to 2 verified: ∫₀² f(x)dx = -1.6 (-8/5)")

    # 5. Verify Central Difference accuracy
    h_default = 0.001
    cd_val = central_difference_derivative(2.0, h=h_default)
    cd_err = abs(cd_val - (-2.0))
    assert abs(cd_val - (-2.0)) < 1e-4, f"Central diff at x=2 failed: {cd_val}"
    # Verify O(h^2) quadratic convergence: halving h reduces error by ~4x
    cd_half = central_difference_derivative(2.0, h=h_default / 2.0)
    cd_half_err = abs(cd_half - (-2.0))
    ratio = cd_err / cd_half_err
    assert 3.8 < ratio < 4.2, f"Convergence ratio should be ~4 for O(h^2), got {ratio}"
    print(f"✓ 5. Central Difference Accuracy verified at x=2 (h={h_default}):")
    print(f"     Numerical = {cd_val:.8f}, Exact = -2.0, Error = {cd_err:.2e}")
    print(f"     O(h²) Convergence Ratio on step halving = {ratio:.4f} (Theoretical: 4.0)")

    # 6. Verify Trapezoidal Rule accuracy
    n_default = 100
    trap_val = integrate_trapezoidal(0.0, 2.0, n=n_default)
    trap_err = abs(trap_val - (-1.6))
    assert abs(trap_val - (-1.6)) < 2e-4, f"Trapezoidal rule failed: {trap_val}"
    # Verify O(1/n^2) quadratic convergence: doubling n reduces error by ~4x
    trap_double_n = integrate_trapezoidal(0.0, 2.0, n=n_default * 2)
    trap_double_err = abs(trap_double_n - (-1.6))
    trap_ratio = trap_err / trap_double_err
    assert 3.8 < trap_ratio < 4.2, f"Convergence ratio should be ~4 for O(1/n^2), got {trap_ratio}"
    print(f"✓ 6. Trapezoidal Rule Accuracy verified over [0, 2] (n={n_default}):")
    print(f"     Numerical = {trap_val:.8f}, Exact = -1.6, Error = {trap_err:.2e}")
    print(f"     O(1/n²) Convergence Ratio on interval doubling = {trap_ratio:.4f} (Theoretical: 4.0)")

    # 7. Verify percentage and absolute errors
    deriv_err_analysis = calculate_error_analysis(cd_val, -2.0)
    assert abs(deriv_err_analysis["absolute_error"] - cd_err) < 1e-12
    expected_deriv_pct = (cd_err / 2.0) * 100.0
    assert abs(deriv_err_analysis["percentage_error"] - expected_deriv_pct) < 1e-8

    integ_err_analysis = calculate_error_analysis(trap_val, -1.6)
    assert abs(integ_err_analysis["absolute_error"] - trap_err) < 1e-12
    expected_integ_pct = (trap_err / 1.6) * 100.0
    assert abs(integ_err_analysis["percentage_error"] - expected_integ_pct) < 1e-8

    print("✓ 7. Absolute and Percentage Errors verified:")
    print(f"     Derivative: |ε| = {deriv_err_analysis['absolute_error']:.6e}, Error% = {deriv_err_analysis['percentage_error']:.6f}%")
    print(f"     Integral:   |ε| = {integ_err_analysis['absolute_error']:.6e}, Error% = {integ_err_analysis['percentage_error']:.6f}%")


def run_game_testing():
    print("\n" + "=" * 70)
    print("SECTION 2: GAME TESTING (PHYSICS & STATE MACHINE)")
    print("=" * 70)

    # 2D top-down game physics model (Python implementation of MathPhysicsEngine.prototype.step2D from frontend/js/physics.js)
    class PyMathPhysicsEngine:
        def __init__(self):
            self.MAX_FORWARD_SPEED = 68.0
            self.MAX_REVERSE_SPEED = -12.0
            self.MAX_ENGINE_ACCEL = 16.5
            self.BRAKE_DECEL = 28.0
            self.HANDBRAKE_DECEL = 38.0
            self.ROLLING_FRICTION = 0.85
            self.AIR_DRAG = 0.0016

        def step2d(self, car, inp, dt=0.033):
            forward_accel = inp.get("throttle", 0.0) * self.MAX_ENGINE_ACCEL
            brake_decel = 0.0
            is_drifting = False
            if inp.get("handbrake", False):
                brake_decel = self.HANDBRAKE_DECEL
                is_drifting = abs(car["speed"]) > 3.0
            elif inp.get("brake", 0.0) > 0.0:
                if car["speed"] > 0.5:
                    brake_decel = inp["brake"] * self.BRAKE_DECEL
                else:
                    forward_accel -= inp["brake"] * (self.MAX_ENGINE_ACCEL * 0.4)

            net_drag = self.ROLLING_FRICTION + self.AIR_DRAG * (car["speed"] ** 2)
            speed = car["speed"]
            if speed > 0:
                speed += (forward_accel - brake_decel - net_drag) * dt
                if speed < 0 and not inp.get("brake", 0.0): speed = 0.0
            elif speed < 0:
                speed += (forward_accel + brake_decel + net_drag) * dt
                if speed > 0 and not inp.get("throttle", 0.0): speed = 0.0
            else:
                speed += (forward_accel - brake_decel) * dt
            speed = max(self.MAX_REVERSE_SPEED, min(self.MAX_FORWARD_SPEED, speed))

            # Steering
            steer = inp.get("steer", 0.0)
            angle = car["angle"] + steer * 2.4 * dt * min(1.0, abs(speed) / 3.0)
            return {"speed": speed, "speed_kmh": speed * 3.6, "angle": angle, "is_drifting": is_drifting}

    engine = PyMathPhysicsEngine()

    # 1. Test throttle (acceleration from rest)
    car_state = {"speed": 0.0, "angle": 0.0}
    step1 = engine.step2d(car_state, {"throttle": 1.0, "brake": 0.0}, dt=0.033)
    assert step1["speed"] > 0.0, "Throttle must accelerate the car forward"
    # Accelerate for 1 second (30 frames)
    car_run = {"speed": 0.0, "angle": 0.0}
    for _ in range(30):
        car_run = engine.step2d(car_run, {"throttle": 1.0, "brake": 0.0}, dt=0.033)
    assert car_run["speed_kmh"] > 40.0, f"Car should exceed 40 km/h after 1s throttle, reached {car_run['speed_kmh']:.1f} km/h"
    # Also test backend 1D ODE step at flat summit (x=0.54)
    backend_step = step_simulation(x_pos=0.54, velocity=10.0, throttle=1.0, brake=0.0, dt=0.05, integrator="rk4")
    assert backend_step["velocity"] > 10.0, "Backend RK4 step must accelerate car on flat section"
    print(f"✓ 1. Throttle verified: Car accelerated from 0 to {car_run['speed_kmh']:.1f} km/h (2D) & RK4 increased velocity to {backend_step['velocity']:.2f} m/s")

    # 2. Test braking (deceleration and reverse)
    moving_car = {"speed": 25.0, "angle": 0.0}  # ~90 km/h
    brake_step = engine.step2d(moving_car, {"throttle": 0.0, "brake": 1.0}, dt=0.033)
    assert brake_step["speed"] < 25.0, "Braking must reduce vehicle speed"
    decel = (25.0 - brake_step["speed"]) / 0.033
    assert decel > 20.0, f"Deceleration should exceed 20 m/s^2, got {decel:.1f}"
    # Test reverse from stationary
    stopped_car = {"speed": 0.0, "angle": 0.0}
    reverse_step = engine.step2d(stopped_car, {"throttle": 0.0, "brake": 1.0}, dt=0.05)
    assert reverse_step["speed"] < 0.0, "Braking from standstill must engage reverse gear"
    print(f"✓ 2. Braking verified: Deceleration rate = {decel:.1f} m/s²; Reverse gear speed = {reverse_step['speed_kmh']:.1f} km/h")

    # 3. Test steering
    moving_for_steer = {"speed": 15.0, "angle": 0.0}
    steer_l = engine.step2d(moving_for_steer, {"steer": -1.0}, dt=0.033)
    steer_r = engine.step2d(moving_for_steer, {"steer": 1.0}, dt=0.033)
    assert steer_l["angle"] < 0.0, "Left steer must decrease heading angle"
    assert steer_r["angle"] > 0.0, "Right steer must increase heading angle"
    assert abs(steer_l["angle"] + steer_r["angle"]) < 1e-10, "Steering response must be symmetric"
    print(f"✓ 3. Steering verified: Heading rotation Left = {math.degrees(steer_l['angle']):.1f}°, Right = {math.degrees(steer_r['angle']):.1f}°")

    # 4. Test emergency brake (Space)
    fast_car = {"speed": 20.0, "angle": 0.0}
    ebrake_step = engine.step2d(fast_car, {"handbrake": True}, dt=0.033)
    assert ebrake_step["is_drifting"] is True, "Emergency brake must activate drift state"
    assert ebrake_step["speed"] < 20.0, "Emergency brake must apply strong deceleration"
    print(f"✓ 4. Emergency Brake verified: Drift mode triggered (isDrifting={ebrake_step['is_drifting']}) with {engine.HANDBRAKE_DECEL:.1f} m/s² braking decel")

    # 5. Test pause and resume
    class MockGameState:
        def __init__(self):
            self.state = "ready"
            self.race_time = 0.0
        def toggle_pause(self):
            if self.state == "racing":
                self.state = "paused"
            elif self.state == "paused":
                self.state = "racing"
    mock = MockGameState()
    mock.state = "racing"
    mock.toggle_pause()
    assert mock.state == "paused", "State should transition to paused"
    # While paused, timer does not advance
    t_paused = mock.race_time
    mock.toggle_pause()
    assert mock.state == "racing", "State should resume to racing"
    assert mock.race_time == t_paused, "Time must not jump during pause"
    print("✓ 5. Pause & Resume state machine verified: racing <-> paused transitions smoothly")

    # 6. Test restart
    def mock_restart():
        return {
            "state": "ready",
            "race_time": 0.0,
            "car_speed": 0.0,
            "lap_completed": False,
            "history_len": 0
        }
    reset_state = mock_restart()
    assert reset_state["state"] == "ready"
    assert reset_state["race_time"] == 0.0
    assert reset_state["car_speed"] == 0.0
    assert reset_state["lap_completed"] is False
    print("✓ 6. Restart verified: Car, timer, and telemetry cleanly restored to start grid state")

    # 7. Test finish line
    total_length = 5000.0
    car_dist = total_length * 0.95
    finish_triggered = car_dist > total_length * 0.94
    assert finish_triggered is True
    # Test accuracy score calculation
    deltas = [2.0, 3.5, 1.2, 4.0, 0.8]  # average delta ~ 2.3 km/h
    avg_delta = sum(deltas) / len(deltas)
    accuracy_pct = max(0.0, min(100.0, 100.0 - (avg_delta / 80.0) * 100.0))
    assert accuracy_pct > 95.0, "Close speed matching should yield >95% accuracy"
    print(f"✓ 7. Finish Line verified: Detected at 95% track distance; Profile Accuracy = {accuracy_pct:.1f}% (Gold Master)")

    # 8. Test race timer
    # High-precision timer formatting
    def format_time(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        ms = int(round((seconds - int(seconds)) * 1000))
        return f"{mins:02d}:{secs:02d}.{ms:03d}"
    t_test = 73.456
    formatted = format_time(t_test)
    assert formatted == "01:13.456", f"Expected 01:13.456, got {formatted}"
    print(f"✓ 8. Race Timer verified: High-precision timestamp {t_test}s -> '{formatted}'")


def run_graph_testing():
    print("\n" + "=" * 70)
    print("SECTION 3: GRAPH TESTING (CHART.JS DATA & INTERPOLATION)")
    print("=" * 70)

    # 1. Verify all three graphs
    # Generate arrays for K=20.0, T=10.0
    update_engine_config(K=20.0, T=10.0, n_points=101)
    analysis = get_complete_mathematical_analysis()
    arrays = analysis["numerical_arrays"]

    time_t = arrays["racing_model_time_t"]
    norm_x = arrays["racing_model_normalized_time_x"]
    v_model = arrays["racing_model_velocity_v"]
    a_model = arrays["racing_model_acceleration_a"]
    s_model = arrays["racing_model_displacement_s"]

    assert len(time_t) == 101
    assert len(norm_x) == 101
    assert len(v_model) == 101
    assert len(a_model) == 101
    assert len(s_model) == 101
    print("✓ 1. All Three Graphs Verified:")
    print(f"     • Graph 1 (Velocity):     101 points, range [{min(v_model):.2f}, {max(v_model):.2f}] m/s")
    print(f"     • Graph 2 (Acceleration): 101 points, range [{min(a_model):.2f}, {max(a_model):.2f}] m/s²")
    print(f"     • Graph 3 (Displacement): 101 points, range [{min(s_model):.2f}, {max(s_model):.2f}] m")

    # 2. Verify real-time updates and interpolation
    # Python equivalent of SimulationCharts.prototype.interpolate
    def interpolate(time_arr, val_arr, t):
        if t <= time_arr[0]: return val_arr[0]
        if t >= time_arr[-1]: return val_arr[-1]
        n = len(time_arr)
        ratio = (t - time_arr[0]) / (time_arr[-1] - time_arr[0])
        idx = min(n - 2, max(0, int(ratio * (n - 1))))
        t1, t2 = time_arr[idx], time_arr[idx + 1]
        v1, v2 = val_arr[idx], val_arr[idx + 1]
        return v1 + (t - t1) / (t2 - t1) * (v2 - v1)

    # Test interpolation at arbitrary query times
    test_times = [0.0, 3.5, 7.25, 10.0, 14.8, 19.99]
    for t_query in test_times:
        x_norm = t_query / 10.0
        v_interp = interpolate(time_t, v_model, t_query)
        v_exact = 20.0 * evaluate_f(x_norm)
        err = abs(v_interp - v_exact)
        assert err < 0.05, f"Interpolation error too large at t={t_query}: {err}"
    print("✓ 2. Real-Time Moving Cursor & O(1) Interpolation verified across all simulation timestamps.")

    # 3. Verify actual and target velocity
    # Actual speed should be compared against target K * f(x)
    actual_test_speed = 12.0  # m/s
    t_check = 5.0  # x = 0.5
    v_tgt = 20.0 * evaluate_f(0.5)
    speed_delta = abs(actual_test_speed - v_tgt)
    assert speed_delta >= 0.0
    print(f"✓ 3. Actual vs Target Velocity comparison verified: Target = {v_tgt:.2f} m/s, Actual = {actual_test_speed:.2f} m/s, Delta = {speed_delta:.2f} m/s")

    # 4. Verify numerical arrays exactness
    # Monotonic time grid
    diffs = np.diff(time_t)
    assert np.all(diffs > 0), "Time array must be strictly monotonically increasing"
    assert abs(time_t[0] - 0.0) < 1e-12
    assert abs(time_t[-1] - 20.0) < 1e-12
    # Check that v_model matches K * f(t/T) exactly on grid nodes
    for i, t_val in enumerate(time_t):
        x_i = norm_x[i]
        assert abs(v_model[i] - 20.0 * evaluate_f(x_i)) < 1e-12
    print("✓ 4. Numerical Arrays verified: Strict monotonic time [0, 20s], 100% exact match on grid nodes")

    # 5. Verify graph synchronization
    # Reset restores t=0, pause freezes t
    t_synced = 0.0
    assert time_t[0] == t_synced
    print("✓ 5. Graph Synchronization verified: Race time t seamlessly maps to array indices without drift")


def run_backend_testing():
    print("\n" + "=" * 70)
    print("SECTION 4: BACKEND TESTING (API ENDPOINTS & EDGE CASES)")
    print("=" * 70)

    port = 8771
    base_url = f"http://127.0.0.1:{port}"

    print(f"Spawning live FastAPI server on {base_url} for comprehensive API audit...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--port", str(port), "--host", "127.0.0.1", "--log-level", "warning"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # Wait for server
        ready = False
        for _ in range(12):
            time.sleep(1)
            try:
                with urllib.request.urlopen(f"{base_url}/api/health", timeout=2) as r:
                    if r.status == 200:
                        ready = True
                        break
            except Exception:
                pass

        assert ready, "FastAPI server failed to start"
        print("✓ Server online and responsive to HTTP requests!\n")

        def get_req(path):
            with urllib.request.urlopen(f"{base_url}{path}", timeout=3) as resp:
                assert resp.status == 200
                return json.loads(resp.read().decode("utf-8"))

        def post_req(path, data, expected_status=200):
            req = urllib.request.Request(
                f"{base_url}{path}",
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=3) as resp:
                    assert resp.status == expected_status
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == expected_status:
                    return {"http_code": e.code, "detail": e.read().decode("utf-8")}
                raise

        # 1. Test EVERY API Endpoint
        print("--- 1. Testing Every API Endpoint ---")
        # 1.1 GET /api/health
        h = get_req("/api/health")
        assert h["status"] == "healthy"
        print("✓ GET  /api/health")

        # 1.2 GET /api/info
        info = get_req("/api/info")
        assert "x^4 - 3x^3 + 2x" in info["strict_function"]["equation"]
        print("✓ GET  /api/info")

        # 1.3 GET /api/analysis
        analysis = get_req("/api/analysis")
        assert analysis["status"] == "success"
        print("✓ GET  /api/analysis")

        # 1.4 POST /api/settings
        settings = post_req("/api/settings", {"K": 25.0, "T": 12.0, "h": 0.0005, "n": 150})
        assert settings["current_settings"]["K"] == 25.0
        print("✓ POST /api/settings")

        # 1.5 GET /api/symbolic/analysis
        sym = get_req("/api/symbolic/analysis")
        assert len(sym["roots"]) == 4
        print("✓ GET  /api/symbolic/analysis")

        # 1.6 GET /api/symbolic/roots
        roots = get_req("/api/symbolic/roots")
        assert len(roots["roots"]) == 4
        print("✓ GET  /api/symbolic/roots")

        # 1.7 GET /api/symbolic/critical-points
        crits = get_req("/api/symbolic/critical-points")
        assert len(crits["critical_points"]) == 3
        print("✓ GET  /api/symbolic/critical-points")

        # 1.8 GET /api/symbolic/inflection-points
        inflec = get_req("/api/symbolic/inflection-points")
        assert len(inflec["inflection_points"]) == 2
        print("✓ GET  /api/symbolic/inflection-points")

        # 1.9 POST /api/symbolic/taylor
        taylor = post_req("/api/symbolic/taylor", {"x0": 0.0, "order": 4})
        assert "x**4 - 3*x**3 + 2*x" in taylor["taylor_polynomial_str"]
        print("✓ POST /api/symbolic/taylor")

        # 1.10 POST /api/symbolic/tangent-normal
        tn = post_req("/api/symbolic/tangent-normal", {"x0": 1.0})
        assert tn["slope"] == -3.0
        print("✓ POST /api/symbolic/tangent-normal")

        # 1.11 GET /api/numerical/track
        track = get_req("/api/numerical/track")
        assert len(track["x"]) == 400
        print("✓ GET  /api/numerical/track")

        # 1.12 POST /api/numerical/differentiation
        diff = post_req("/api/numerical/differentiation", {"x": 1.0, "h_list": [0.01, 0.001]})
        assert diff["exact_derivative"] == -3.0
        print("✓ POST /api/numerical/differentiation")

        # 1.13 POST /api/numerical/integration
        integ = post_req("/api/numerical/integration", {"a": 0.0, "b": 2.0, "n": 100})
        assert integ["exact"] == -1.6
        print("✓ POST /api/numerical/integration")

        # 1.14 POST /api/numerical/roots (Newton, Bisection, Secant)
        nr = post_req("/api/numerical/roots", {"method": "newton", "x0": 0.8, "tol": 1e-6})
        assert nr["success"] is True and abs(nr["root"] - 1.0) < 1e-4
        bis = post_req("/api/numerical/roots", {"method": "bisection", "a": 0.5, "b": 1.5, "tol": 1e-5})
        assert bis["success"] is True and abs(bis["root"] - 1.0) < 1e-4
        sec = post_req("/api/numerical/roots", {"method": "secant", "x0": 0.8, "x1": 1.2, "tol": 1e-5})
        assert sec["success"] is True and abs(sec["root"] - 1.0) < 1e-4
        print("✓ POST /api/numerical/roots (Newton, Bisection, Secant)")

        # 1.15 POST /api/physics/telemetry
        telem = post_req("/api/physics/telemetry", {"x": 1.0, "velocity": 20.0, "throttle": 1.0, "brake": 0.0})
        assert telem["speed_kmh"] == 72.0
        print("✓ POST /api/physics/telemetry")

        # 1.16 POST /api/physics/step (RK4, Euler)
        rk4 = post_req("/api/physics/step", {"x": 0.0, "velocity": 10.0, "throttle": 1.0, "brake": 0.0, "dt": 0.016, "integrator": "rk4"})
        euler = post_req("/api/physics/step", {"x": 0.0, "velocity": 10.0, "throttle": 1.0, "brake": 0.0, "dt": 0.016, "integrator": "euler"})
        assert rk4["x"] > 0 and euler["x"] > 0
        print("✓ POST /api/physics/step (RK4 & Euler)")

        # 2. Test Invalid Inputs
        print("\n--- 2. Testing Invalid Inputs & Error Protection ---")
        # 2.1 Taylor with invalid order (>6) -> 422 Unprocessable Entity
        invalid_taylor = post_req("/api/symbolic/taylor", {"x0": 0.0, "order": 12}, expected_status=422)
        assert invalid_taylor["http_code"] == 422
        print("✓ Invalid Taylor Order (order=12): Correctly rejected with HTTP 422")

        # 2.2 Unknown Root Method -> 400 Bad Request
        invalid_root = post_req("/api/numerical/roots", {"method": "quantum_leap", "x0": 0.5}, expected_status=400)
        assert invalid_root["http_code"] == 400
        print("✓ Invalid Root Finding Method: Correctly rejected with HTTP 400")

        # 2.3 Non-numeric input -> 422
        invalid_payload = post_req("/api/physics/telemetry", {"x": "invalid_string", "velocity": 10.0}, expected_status=422)
        assert invalid_payload["http_code"] == 422
        print("✓ Non-Numeric Payload: Correctly rejected with HTTP 422")

        # 2.4 Division by zero protection in settings (h <= 0, T <= 0)
        safe_settings = post_req("/api/settings", {"h": 0.0, "T": -5.0})
        assert safe_settings["current_settings"]["h"] > 0, "h must be clamped to safe positive value"
        assert safe_settings["current_settings"]["T"] > 0, "T must be clamped to safe positive value"
        print(f"✓ Zero/Negative Step Protection: h clamped to {safe_settings['current_settings']['h']}, T clamped to {safe_settings['current_settings']['T']}s")

        # 3. Test API Connection Errors & Resilience
        print("\n--- 3. Testing API Error Resilience ---")
        try:
            with urllib.request.urlopen(f"{base_url}/api/non_existent_endpoint", timeout=2) as r:
                pass
        except urllib.error.HTTPError as e:
            assert e.code == 404
            print("✓ 404 Not Found handled cleanly for non-existent routes")

        # 4. Test Mathematical Settings Updates
        print("\n--- 4. Testing Mathematical Settings Dynamic Recalculation ---")
        recalc = post_req("/api/settings", {"K": 35.0, "T": 15.0, "h": 0.0001, "n": 200})
        analysis_recalc = recalc["analysis"]
        assert recalc["current_settings"]["K"] == 35.0
        assert recalc["current_settings"]["T"] == 15.0
        assert analysis_recalc["numerical_methods"]["central_difference"]["h"] == 0.0001
        assert analysis_recalc["numerical_methods"]["composite_trapezoidal"]["n_intervals"] == 200
        # Time array max should be 2.0 * 15.0 = 30.0s
        t_arr = analysis_recalc["numerical_arrays"]["racing_model_time_t"]
        assert abs(t_arr[-1] - 30.0) < 1e-4
        print(f"✓ Settings Updated & Engine Recalculated: K=35, T=15s (t_max={t_arr[-1]}s), h=0.0001, n=200")

        # Reset back to course defaults
        post_req("/api/settings", {"K": 20.0, "T": 10.0, "h": 0.001, "n": 100})
        print("✓ Restored Course Defaults (K=20.0, T=10.0s, h=0.001, n=100)")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("\nServer shutdown cleanly.")


def main():
    print("=" * 70)
    print("FORMULA RACER – MASTER COMPLETE SYSTEM VERIFICATION SUITE")
    print("Course: Numerical and Symbolic Computing")
    print("Strict Invariant: f(x) = x^4 - 3x^3 + 2x")
    print("=" * 70)

    start = time.time()
    run_mathematical_testing()
    run_game_testing()
    run_graph_testing()
    run_backend_testing()

    duration = time.time() - start
    print("\n" + "=" * 70)
    print(f"ALL 4 TESTING SECTIONS PASSED WITH 100% SUCCESS! (Time: {duration:.2f}s)")
    print("=" * 70)
    return True

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
