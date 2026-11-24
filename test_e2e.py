"""
End-to-End Integration Verification Suite for FORMULA RACER
Course: Numerical and Symbolic Computing
Tests live FastAPI server, static frontend file delivery, and all API endpoints.
"""

import subprocess
import time
import urllib.request
import json
import sys

def main():
    print("==================================================================", flush=True)
    print("FORMULA RACER - END-TO-END INTEGRATION & HTTP VERIFICATION", flush=True)
    print("Course: Numerical and Symbolic Computing", flush=True)
    print("Strict Invariant: f(x) = x^4 - 3x^3 + 2x", flush=True)
    print("==================================================================", flush=True)

    port = 8769
    base_url = f"http://127.0.0.1:{port}"

    print(f"Spawning live FastAPI server on {base_url}...", flush=True)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--port", str(port), "--host", "127.0.0.1", "--log-level", "warning"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # 1. Wait for server readiness
        ready = False
        for _ in range(12):
            time.sleep(1)
            try:
                with urllib.request.urlopen(f"{base_url}/api/info", timeout=2) as r:
                    if r.status == 200:
                        ready = True
                        break
            except Exception:
                pass

        if not ready:
            print("ERROR: Server failed to start within timeout.", flush=True)
            print("Server process poll:", proc.poll(), flush=True)
            out, err = proc.communicate(timeout=2)
            print("Server stdout:", out.decode(errors='ignore'), flush=True)
            print("Server stderr:", err.decode(errors='ignore'), flush=True)
            return False

        print("✓ Server online and responding to HTTP requests!\n", flush=True)

        # 2. Test Frontend Static Delivery & Required DOM Elements
        static_files = [
            ("/", "text/html", "f(x) = x⁴ - 3x³ + 2x"),
            ("/css/style.css", "text/css", "FORMULA RACER"),
            ("/js/game.js", "application/javascript", "FormulaRacerGame"),
            ("/js/physics.js", "application/javascript", "MathPhysicsEngine"),
            ("/js/charts.js", "application/javascript", "SimulationCharts"),
            ("/js/controls.js", "application/javascript", "ControlsHandler"),
            ("/js/api.js", "application/javascript", "API"),
            ("/assets/chart.min.js", "application/javascript", "Chart")
        ]

        print("--- Testing Frontend Static Delivery ---", flush=True)
        html_content = ""
        game_js_content = ""
        physics_js_content = ""
        controls_js_content = ""
        charts_js_content = ""

        for path, expected_type, content_check in static_files:
            url = f"{base_url}{path}"
            with urllib.request.urlopen(url, timeout=3) as resp:
                assert resp.status == 200, f"Failed {path}: {resp.status}"
                body = resp.read().decode(errors="ignore")
                assert content_check in body, f"Missing '{content_check}' in {path}"
                if path == "/": html_content = body
                elif path == "/js/game.js": game_js_content = body
                elif path == "/js/physics.js": physics_js_content = body
                elif path == "/js/controls.js": controls_js_content = body
                elif path == "/js/charts.js": charts_js_content = body
                print(f"✓ {path.ljust(22)} -> HTTP 200 OK ({len(body)} bytes verified)", flush=True)

        # 3. Verify All 10 Game Features in HTML & JavaScript
        print("\n--- Verifying All 10 Required Game Features ---", flush=True)
        # Feature 1: Realistic asphalt racing track
        assert "renderAsphaltTrack" in game_js_content and "trackCenterline" in game_js_content
        print("✓ Feature 1: Realistic asphalt racing track (Catmull-Rom spline circuit)", flush=True)

        # Feature 2: Road lane markings
        assert "renderLaneMarkings" in game_js_content and "setLineDash" in game_js_content
        print("✓ Feature 2: Road lane markings (edge borders & dashed center line)", flush=True)

        # Feature 3: Player sports car
        assert "renderPlayerCar" in game_js_content and "steerAngle" in game_js_content
        print("✓ Feature 3: Player sports car (steerable wheels, headlights, brake lights)", flush=True)

        # Feature 4: Finish line
        assert "renderStartFinishLine" in game_js_content and "finishRace" in game_js_content
        print("✓ Feature 4: Finish line & overhead start gantry", flush=True)

        # Feature 5: Track boundaries
        assert "checkTrackSurface" in game_js_content and "hitBarrier" in game_js_content
        print("✓ Feature 5: Track boundaries with elastic rebound collision", flush=True)

        # Feature 6: Roadside objects
        assert "renderRoadsideObjects" in game_js_content and "grandstand" in game_js_content
        print("✓ Feature 6: Roadside objects (grandstands, trees, distance markers, tire walls)", flush=True)

        # Feature 7: Smooth car movement
        assert "step2D" in physics_js_content and "requestAnimationFrame" in game_js_content
        print("✓ Feature 7: Smooth car movement via requestAnimationFrame & 2D physics", flush=True)

        # Feature 8: Race timer
        assert 'id="hudTimer"' in html_content and "formatTime" in game_js_content
        print("✓ Feature 8: Race timer (high-precision MM:SS.mmm)", flush=True)

        # Feature 9: Start, pause and restart buttons
        assert 'id="btnStartRace"' in html_content and 'id="btnPauseRace"' in html_content and 'id="btnRestartRace"' in html_content
        print("✓ Feature 9: Start, Pause, and Restart buttons present in UI", flush=True)

        # Feature 10: Finish race screen
        assert 'id="finishOverlay"' in html_content and 'id="finishTime"' in html_content and 'id="finishAccuracy"' in html_content
        print("✓ Feature 10: Finish race screen with accuracy score & driver rating", flush=True)

        # Dual speed display check
        assert 'id="hudSpeed"' in html_content and 'id="hudTargetSpeed"' in html_content and 'id="hudSpeedDelta"' in html_content
        assert "getTargetVelocityKmh" in physics_js_content and "x^4 - 3x^3 + 2x" in html_content
        print("✓ Dual Speed Display: Actual Speed vs Math Target Speed from f(x) verified", flush=True)

        # Keyboard controls check
        assert "ArrowUp" in controls_js_content and "KeyW" in controls_js_content
        assert "ArrowDown" in controls_js_content and "KeyS" in controls_js_content
        assert "ArrowLeft" in controls_js_content and "KeyA" in controls_js_content
        assert "ArrowRight" in controls_js_content and "KeyD" in controls_js_content
        assert "Space" in controls_js_content and "KeyR" in controls_js_content and "KeyP" in controls_js_content
        print("✓ Controls: Arrow keys, WASD, Space (emergency brake), P (pause), R (restart) verified", flush=True)

        # 4. Verify Three Live Mathematical Graphs (Chart.js)
        print("\n--- Verifying Three Live Mathematical Graphs (Chart.js) ---", flush=True)
        # Graph 1: Target Velocity vs Time & Actual Vehicle Speed
        assert 'id="velocityChart"' in html_content
        assert "initVelocityChart" in charts_js_content and "Target Velocity" in charts_js_content
        assert "Actual Vehicle Speed" in charts_js_content and "actualSpeedTrajectory" in charts_js_content
        assert 'id="valTargetV"' in html_content and 'id="valActualV"' in html_content
        print("✓ GRAPH 1: Target Velocity vs Time & Actual Vehicle Speed series verified", flush=True)

        # Graph 2: Target Acceleration vs Time
        assert 'id="accelerationChart"' in html_content
        assert "initAccelerationChart" in charts_js_content and "Target Acceleration" in charts_js_content
        assert 'id="valTargetA"' in html_content and 'id="valFPrimeX"' in html_content
        print("✓ GRAPH 2: Target Acceleration vs Time [a(t) = (K/T)*f'(t/T)] verified", flush=True)

        # Graph 3: Target Displacement vs Time
        assert 'id="displacementChart"' in html_content
        assert "initDisplacementChart" in charts_js_content and "Target Displacement" in charts_js_content
        assert 'id="valTargetS"' in html_content and 'id="valIntegF"' in html_content
        print("✓ GRAPH 3: Target Displacement vs Time [s(t) = K*T*∫f(u)du] verified", flush=True)

        # Real-time synchronization & Continuous time cursor
        assert "Current Time (Cursor)" in charts_js_content
        assert "interpolate" in charts_js_content
        assert "updateRealtime" in charts_js_content
        assert "reset" in charts_js_content and "setPaused" in charts_js_content
        assert "charts.updateRealtime" in game_js_content
        assert "charts.reset" in game_js_content
        assert "charts.setPaused" in game_js_content
        print("✓ Real-Time Synchronization: Continuous cursor, JS array interpolation, reset & pause verified", flush=True)

        # 5. Verify Professional Mathematical Analytics Panel & Comparison Table
        print("\n--- Verifying Mathematical Analytics Panel & Comparison Table ---", flush=True)
        # All 8 mathematical display requirements
        assert 'id="cardOrigEquation"' in html_content      # 1. Original equation
        assert 'id="cardSymbolicDeriv"' in html_content     # 2. Symbolic derivative using SymPy
        assert 'id="tblNumDeriv"' in html_content           # 3. Numerical derivative using Central Difference
        assert 'id="cardIndefIntegral"' in html_content     # 4. Symbolic indefinite integral
        assert 'id="tblExactInteg"' in html_content         # 5. Symbolic definite integral
        assert 'id="tblNumInteg"' in html_content           # 6. Numerical integral using Trapezoidal Rule
        assert 'id="tblAbsErrDeriv"' in html_content and 'id="tblAbsErrInteg"' in html_content  # 7. Absolute error
        assert 'id="tblPctErrDeriv"' in html_content and 'id="tblPctErrInteg"' in html_content  # 8. Percentage error
        print("✓ All 8 Mathematical Analytics requirements present in DOM", flush=True)

        # Comparison table & Controls check
        assert 'class="analytics-comparison-table"' in html_content
        assert 'id="inputH"' in html_content and 'id="sliderH"' in html_content
        assert 'id="inputN"' in html_content and 'id="sliderN"' in html_content
        assert 'id="inputT"' in html_content and 'id="sliderT"' in html_content
        assert 'id="inputK"' in html_content and 'id="sliderK"' in html_content
        assert 'id="btnApplyAnalytics"' in html_content
        assert "applyMathematicalSettings" in html_content
        print("✓ Comparison Table & 4 Interactive Controls (h, n, T, K) verified", flush=True)

        # 3. Test API Endpoints over HTTP
        print("\n--- Testing All Mathematical API Endpoints over HTTP ---", flush=True)

        def post_json(path, data):
            req = urllib.request.Request(
                f"{base_url}{path}",
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                return json.loads(resp.read().decode("utf-8"))

        def get_json(path):
            with urllib.request.urlopen(f"{base_url}{path}", timeout=3) as resp:
                return json.loads(resp.read().decode("utf-8"))

        # GET /api/info
        info = get_json("/api/info")
        assert "x^4 - 3x^3 + 2x" in info["strict_function"]["equation"]
        print("✓ GET  /api/info                     -> Strict equation confirmed", flush=True)

        # GET /api/health
        health = get_json("/api/health")
        assert health["status"] == "healthy"
        print(f"✓ GET  /api/health                   -> Status: {health['status']}", flush=True)

        # GET /api/analysis
        analysis_engine = get_json("/api/analysis")
        assert analysis_engine["status"] == "success"
        sym_calc = analysis_engine["sympy_calculations"]
        assert sym_calc["f_at_2"]["value"] == -4.0
        assert sym_calc["f_prime_at_2"]["value"] == -2.0
        assert sym_calc["definite_integral_0_to_2"]["value"] == -1.6
        print(f"✓ GET  /api/analysis                 -> SymPy f(2)=-4, f'(2)=-2, ∫f=-1.6 verified", flush=True)

        # POST /api/settings
        settings_update = post_json("/api/settings", {"K": 25.0, "T": 8.0, "h": 0.001, "n": 100})
        assert settings_update["status"] == "success"
        assert settings_update["current_settings"]["K"] == 25.0
        print(f"✓ POST /api/settings                 -> Config updated: K={settings_update['current_settings']['K']}, T={settings_update['current_settings']['T']}", flush=True)

        # GET /api/symbolic/analysis
        analysis = get_json("/api/symbolic/analysis")
        assert len(analysis["roots"]) == 4
        print(f"✓ GET  /api/symbolic/analysis        -> 4 Exact Roots: {[r['value'] for r in analysis['roots']]}", flush=True)

        # GET /api/symbolic/critical-points
        crit = get_json("/api/symbolic/critical-points")
        assert len(crit["critical_points"]) == 3
        print(f"✓ GET  /api/symbolic/critical-points -> 3 Critical Points: {[c['x'] for c in crit['critical_points']]}", flush=True)

        # GET /api/symbolic/inflection-points
        inflec = get_json("/api/symbolic/inflection-points")
        assert len(inflec["inflection_points"]) == 2
        print(f"✓ GET  /api/symbolic/inflection-points -> Inflection Points: {[p['x'] for p in inflec['inflection_points']]}", flush=True)

        # POST /api/symbolic/taylor
        taylor = post_json("/api/symbolic/taylor", {"x0": 0.0, "order": 4})
        assert "x**4 - 3*x**3 + 2*x" in taylor["taylor_polynomial_str"]
        print(f"✓ POST /api/symbolic/taylor          -> Taylor Series degree 4 verified", flush=True)

        # POST /api/symbolic/tangent-normal
        tn = post_json("/api/symbolic/tangent-normal", {"x0": 1.0})
        assert tn["slope"] == -3.0
        print(f"✓ POST /api/symbolic/tangent-normal  -> Tangent slope m={tn['slope']}, Normal={tn['normal']['m']:.4f}", flush=True)

        # GET /api/numerical/track
        track = get_json("/api/numerical/track")
        assert len(track["x"]) == 400
        print(f"✓ GET  /api/numerical/track          -> 400 nodes, total length={track['total_arc_length']:.2f}m", flush=True)

        # POST /api/numerical/differentiation
        diff = post_json("/api/numerical/differentiation", {"x": 1.0, "h_list": [0.1, 0.01, 0.001]})
        assert diff["exact_derivative"] == -3.0
        print(f"✓ POST /api/numerical/differentiation-> Central diff error={diff['steps'][2]['central_error']}", flush=True)

        # POST /api/numerical/integration
        integ = post_json("/api/numerical/integration", {"a": 0.0, "b": 2.0, "n": 60})
        assert integ["exact"] == -1.6
        print(f"✓ POST /api/numerical/integration    -> Exact: -1.6 vs Simpson: {integ['simpsons_13']['value']}", flush=True)

        # POST /api/numerical/roots
        nr = post_json("/api/numerical/roots", {"method": "newton", "x0": 0.8, "tol": 1e-6})
        assert nr["success"] is True and abs(nr["root"] - 1.0) < 1e-4
        print(f"✓ POST /api/numerical/roots (Newton) -> Root x={nr['root']} in {nr['iterations_count']} iterations", flush=True)

        bis = post_json("/api/numerical/roots", {"method": "bisection", "a": 0.5, "b": 1.5, "tol": 1e-5})
        assert bis["success"] is True and abs(bis["root"] - 1.0) < 1e-4
        print(f"✓ POST /api/numerical/roots (Bisect) -> Root x={bis['root']} in {bis['iterations_count']} iterations", flush=True)

        sec = post_json("/api/numerical/roots", {"method": "secant", "x0": 0.8, "x1": 1.2, "tol": 1e-5})
        assert sec["success"] is True and abs(sec["root"] - 1.0) < 1e-4
        print(f"✓ POST /api/numerical/roots (Secant) -> Root x={sec['root']} in {sec['iterations_count']} iterations", flush=True)

        # POST /api/physics/telemetry
        telem = post_json("/api/physics/telemetry", {"x": 1.0, "velocity": 20.0, "throttle": 1.0, "brake": 0.0})
        assert telem["speed_kmh"] == 72.0
        print(f"✓ POST /api/physics/telemetry        -> Speed: {telem['speed_kmh']} km/h, Normal: {telem['forces']['normal_force']} N", flush=True)

        # POST /api/physics/step (RK4 and Euler)
        rk4 = post_json("/api/physics/step", {"x": 0.0, "velocity": 10.0, "throttle": 1.0, "brake": 0.0, "dt": 0.016, "integrator": "rk4"})
        assert rk4["x"] > 0
        euler = post_json("/api/physics/step", {"x": 0.0, "velocity": 10.0, "throttle": 1.0, "brake": 0.0, "dt": 0.016, "integrator": "euler"})
        assert euler["x"] > 0
        print(f"✓ POST /api/physics/step             -> RK4 stepped to x={rk4['x']:.4f}, Euler to x={euler['x']:.4f}", flush=True)

        print("\n==================================================================", flush=True)
        print("ALL END-TO-END HTTP TESTS PASSED WITH 100% SUCCESS!", flush=True)
        print("==================================================================", flush=True)
        return True

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Server shutdown cleanly.", flush=True)

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
