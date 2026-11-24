"""
Physics and Mathematical Calculations Module for FORMULA RACER
Course: Numerical and Symbolic Computing

STRICT MATHEMATICAL REQUIREMENT:
f(x) = x^4 - 3x^3 + 2x
Never replace this equation with another function.

Integrates symbolic derivatives with numerical ODE solvers and finite differences
to provide complete vehicle dynamics and track telemetry.
"""

import os
import sys
import math
import numpy as np
from typing import Dict, Any, List, Optional

# Add backend directory to sys.path so direct imports work regardless of working directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from symbolic import (
    evaluate_f,
    evaluate_f_prime,
    evaluate_f_double_prime,
    evaluate_curvature,
    get_exact_roots,
    get_exact_critical_points,
    get_inflection_points,
    compute_tangent_and_normal,
    get_exact_definite_integral,
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
    f_double_prime_numpy,
    compute_numerical_arc_length,
    integrate_trapezoidal,
    central_difference_derivative,
    calculate_error_analysis,
    generate_numerical_arrays,
    generate_racing_model_arrays,
    rk4_step,
    euler_step
)

# Physical constants
GRAVITY = 9.81               # m/s^2
AIR_DENSITY = 1.225          # kg/m^3
DRAG_COEFFICIENT = 0.35      # Aerodynamic drag factor Cd * A
ROLLING_RESISTANCE = 0.015   # Crr
TIRE_FRICTION_COEFF = 1.1    # mu (racing slick tires)
CAR_MASS = 750.0             # kg (F1 spec car mass)
ENGINE_MAX_FORCE = 6500.0    # Newtons (~750 HP equivalent)
BRAKE_MAX_FORCE = 12000.0    # Newtons

# Track configuration
TRACK_X_MIN = -1.2
TRACK_X_MAX = 3.2
TRACK_SAMPLES = 400


class TrackManager:
    """Manages precomputed high-precision track profile and telemetry."""

    def __init__(self, x_min: float = TRACK_X_MIN, x_max: float = TRACK_X_MAX, n_samples: int = TRACK_SAMPLES):
        self.x_min = x_min
        self.x_max = x_max
        self.n_samples = n_samples
        self.x_grid = np.linspace(x_min, x_max, n_samples)
        self.y_grid = f_numpy(self.x_grid)
        self.dy_grid = f_prime_numpy(self.x_grid)
        self.d2y_grid = f_double_prime_numpy(self.x_grid)

        # Precompute curvature kappa
        denom = (1.0 + self.dy_grid**2)**1.5
        self.kappa_grid = np.abs(self.d2y_grid) / np.maximum(denom, 1e-12)

        # Precompute cumulative arc length
        self.s_grid = np.zeros(n_samples)
        cum_s = 0.0
        for i in range(1, n_samples):
            dx = self.x_grid[i] - self.x_grid[i - 1]
            dy = self.y_grid[i] - self.y_grid[i - 1]
            cum_s += math.hypot(dx, dy)
            self.s_grid[i] = cum_s

        self.total_length = float(self.s_grid[-1])
        self.roots = get_exact_roots()
        self.critical_points = get_exact_critical_points()
        self.inflection_points = get_inflection_points()

    def get_track_profile(self) -> Dict[str, Any]:
        """Return full discretized track data for frontend rendering and Chart.js."""
        return {
            "x": self.x_grid.tolist(),
            "y": self.y_grid.tolist(),
            "slope": self.dy_grid.tolist(),
            "second_derivative": self.d2y_grid.tolist(),
            "curvature": self.kappa_grid.tolist(),
            "arc_length": self.s_grid.tolist(),
            "total_arc_length": round(self.total_length, 4),
            "x_min": self.x_min,
            "x_max": self.x_max,
            "roots": self.roots,
            "critical_points": self.critical_points,
            "inflection_points": self.inflection_points
        }


# Singleton instance
_track_instance = TrackManager()


def get_track() -> TrackManager:
    return _track_instance


def calculate_vehicle_telemetry(
    x_pos: float,
    velocity: float,
    throttle: float = 0.0,
    brake: float = 0.0,
    mass: float = CAR_MASS
) -> Dict[str, Any]:
    """
    Calculate instantaneous physical & mathematical values at vehicle coordinate x_pos.
    All calculations strictly use f(x) = x^4 - 3x^3 + 2x.
    """
    # Exact function and derivatives at current position
    y_pos = evaluate_f(x_pos)
    dy = evaluate_f_prime(x_pos)
    d2y = evaluate_f_double_prime(x_pos)
    kappa = evaluate_curvature(x_pos)

    # Track angle theta = arctan(dy)
    theta = math.atan(dy)
    theta_deg = math.degrees(theta)

    # Unit Tangent T and Unit Normal N
    speed = abs(velocity)
    ds_dx = math.sqrt(1.0 + dy**2)
    t_x = 1.0 / ds_dx
    t_y = dy / ds_dx

    # Tangential forces:
    # 1. Gravity component along slope: F_gravity = -m * g * sin(theta)
    # When going uphill (theta > 0), gravity opposes motion
    f_gravity = -mass * GRAVITY * math.sin(theta)

    # 2. Aerodynamic drag: F_drag = -0.5 * rho * Cd * v^2 * sign(v)
    f_drag = -0.5 * AIR_DENSITY * DRAG_COEFFICIENT * (velocity**2) * (1.0 if velocity >= 0 else -1.0)

    # 3. Rolling resistance: F_rr = -Crr * m * g * cos(theta) * sign(v)
    f_rr = -ROLLING_RESISTANCE * mass * GRAVITY * math.cos(theta) * (1.0 if velocity > 0 else (-1.0 if velocity < 0 else 0.0))

    # 4. Engine tractive force
    throttle_clamped = max(0.0, min(1.0, throttle))
    f_engine = throttle_clamped * ENGINE_MAX_FORCE

    # 5. Braking force
    brake_clamped = max(0.0, min(1.0, brake))
    f_brake = -brake_clamped * BRAKE_MAX_FORCE * (1.0 if velocity > 0 else (-1.0 if velocity < 0 else 0.0))

    # Normal Force FN:
    # FN = m * (g * cos(theta) + v^2 * (curvature signed by d2y))
    # If d2y > 0 (concave up, valley): centripetal force pushes car down into track
    # If d2y < 0 (concave down, crest): centripetal force lifts car away from track
    curvature_signed = kappa if d2y >= 0 else -kappa
    centripetal_accel = (velocity**2) * curvature_signed
    normal_force = mass * (GRAVITY * math.cos(theta) + centripetal_accel)

    is_airborne = normal_force <= 0.0
    effective_normal_force = max(0.0, normal_force)

    # Traction limit
    max_traction = TIRE_FRICTION_COEFF * effective_normal_force

    # Net engine/brake force limited by traction
    f_drive_brake = f_engine + f_brake
    if abs(f_drive_brake) > max_traction and not is_airborne:
        f_drive_brake = math.copysign(max_traction, f_drive_brake)
        wheel_spin = True
    elif is_airborne:
        f_drive_brake = 0.0
        wheel_spin = False
    else:
        wheel_spin = False

    # Net force along track tangent
    f_net = f_drive_brake + f_gravity + f_drag + f_rr
    tangential_accel = f_net / mass

    # Energies
    kinetic_energy = 0.5 * mass * (velocity**2)
    potential_energy = mass * GRAVITY * y_pos
    total_energy = kinetic_energy + potential_energy

    # G-Forces
    g_tangential = tangential_accel / GRAVITY
    g_vertical = (effective_normal_force / mass) / GRAVITY
    g_lateral = abs(velocity**2 * kappa) / GRAVITY

    return {
        "x": round(x_pos, 5),
        "y": round(y_pos, 5),
        "velocity": round(velocity, 4),
        "speed_kmh": round(abs(velocity) * 3.6, 2),
        "slope": round(dy, 5),
        "slope_deg": round(theta_deg, 2),
        "second_derivative": round(d2y, 5),
        "curvature": round(kappa, 6),
        "tangent_vector": {"x": round(t_x, 4), "y": round(t_y, 4)},
        "forces": {
            "gravity_tangential": round(f_gravity, 2),
            "aerodynamic_drag": round(f_drag, 2),
            "rolling_resistance": round(f_rr, 2),
            "engine_thrust": round(f_engine, 2),
            "braking_force": round(f_brake, 2),
            "normal_force": round(normal_force, 2),
            "net_force": round(f_net, 2)
        },
        "acceleration": round(tangential_accel, 4),
        "g_force": {
            "tangential": round(g_tangential, 2),
            "vertical": round(g_vertical, 2),
            "lateral": round(g_lateral, 2)
        },
        "energy": {
            "kinetic_joules": round(kinetic_energy, 2),
            "potential_joules": round(potential_energy, 2),
            "total_joules": round(total_energy, 2)
        },
        "is_airborne": is_airborne,
        "wheel_spin": wheel_spin
    }


def step_simulation(
    x_pos: float,
    velocity: float,
    throttle: float,
    brake: float,
    dt: float = 0.016,  # ~60 fps
    integrator: str = "rk4"
) -> Dict[str, Any]:
    """
    Simulate one time step dt of the vehicle along the curve f(x).
    Uses numerical ODE solver (RK4 or Euler) from numerical.py.
    """
    clamped_dt = max(0.001, min(0.1, dt))

    def net_acceleration(curr_x: float, curr_v: float) -> float:
        # Calculate instantaneous acceleration at (curr_x, curr_v)
        dy = evaluate_f_prime(curr_x)
        d2y = evaluate_f_double_prime(curr_x)
        kappa = evaluate_curvature(curr_x)
        theta = math.atan(dy)

        # Gravitational force along slope
        f_g = -CAR_MASS * GRAVITY * math.sin(theta)

        # Drag & rolling resistance
        f_d = -0.5 * AIR_DENSITY * DRAG_COEFFICIENT * (curr_v**2) * (1.0 if curr_v >= 0 else -1.0)
        f_r = -ROLLING_RESISTANCE * CAR_MASS * GRAVITY * math.cos(theta) * (1.0 if curr_v > 0 else (-1.0 if curr_v < 0 else 0.0))

        # Engine & brake
        f_eng = max(0.0, min(1.0, throttle)) * ENGINE_MAX_FORCE
        f_brk = -max(0.0, min(1.0, brake)) * BRAKE_MAX_FORCE * (1.0 if curr_v > 0 else (-1.0 if curr_v < 0 else 0.0))

        # Normal force & traction limit
        curv_signed = kappa if d2y >= 0 else -kappa
        fn = CAR_MASS * (GRAVITY * math.cos(theta) + (curr_v**2) * curv_signed)
        effective_fn = max(0.0, fn)
        max_trac = TIRE_FRICTION_COEFF * effective_fn

        f_drive = f_eng + f_brk
        if abs(f_drive) > max_trac and fn > 0:
            f_drive = math.copysign(max_trac, f_drive)
        elif fn <= 0:
            f_drive = 0.0

        f_total = f_drive + f_g + f_d + f_r
        return f_total / CAR_MASS

    # Tangential arc length velocity is v_tangent.
    # The rate of change of coordinate x is: dx/dt = v / sqrt(1 + (f'(x))^2)
    def x_velocity(curr_x: float, curr_v: float) -> float:
        dy = evaluate_f_prime(curr_x)
        ds_dx = math.sqrt(1.0 + dy**2)
        return curr_v / ds_dx

    # Perform integration step
    if integrator.lower() == "euler":
        a = net_acceleration(x_pos, velocity)
        v_next = velocity + a * clamped_dt
        x_rate = x_velocity(x_pos, velocity)
        x_next = x_pos + x_rate * clamped_dt
    else:  # RK4
        # RK4 for coupled system (x, v)
        k1_v = net_acceleration(x_pos, velocity)
        k1_x = x_velocity(x_pos, velocity)

        k2_v = net_acceleration(x_pos + 0.5 * clamped_dt * k1_x, velocity + 0.5 * clamped_dt * k1_v)
        k2_x = x_velocity(x_pos + 0.5 * clamped_dt * k1_x, velocity + 0.5 * clamped_dt * k1_v)

        k3_v = net_acceleration(x_pos + 0.5 * clamped_dt * k2_x, velocity + 0.5 * clamped_dt * k2_v)
        k3_x = x_velocity(x_pos + 0.5 * clamped_dt * k2_x, velocity + 0.5 * clamped_dt * k2_v)

        k4_v = net_acceleration(x_pos + clamped_dt * k3_x, velocity + clamped_dt * k3_v)
        k4_x = x_velocity(x_pos + clamped_dt * k3_x, velocity + clamped_dt * k3_v)

        x_next = x_pos + (clamped_dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
        v_next = velocity + (clamped_dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)

    # Check bounds
    if x_next < TRACK_X_MIN:
        x_next = TRACK_X_MIN
        v_next = 0.0
    elif x_next > TRACK_X_MAX:
        x_next = TRACK_X_MAX
        v_next = 0.0

    telemetry = calculate_vehicle_telemetry(x_next, v_next, throttle, brake)
    telemetry["integrator_used"] = integrator
    telemetry["dt"] = clamped_dt
    return telemetry


# ==============================================================================
# COMPLETE MATHEMATICAL ENGINE ORCHESTRATION & CONFIGURATION
# ==============================================================================

class MathEngineConfig:
    """Configurable parameters for the mathematical engine and racing model."""
    def __init__(
        self,
        K: float = 20.0,
        T: float = 10.0,
        h: float = 0.001,
        n: int = 100,
        eval_x: float = 2.0,
        integral_a: float = 0.0,
        integral_b: float = 2.0,
        n_points: int = 101
    ):
        self.K = float(K)
        self.T = float(T)
        self.h = float(h)
        self.n = int(n)
        self.eval_x = float(eval_x)
        self.integral_a = float(integral_a)
        self.integral_b = float(integral_b)
        self.n_points = int(n_points)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "K": self.K,
            "T": self.T,
            "h": self.h,
            "n": self.n,
            "eval_x": self.eval_x,
            "integral_a": self.integral_a,
            "integral_b": self.integral_b,
            "n_points": self.n_points
        }


_engine_config = MathEngineConfig()


def get_engine_config() -> MathEngineConfig:
    return _engine_config


def update_engine_config(
    K: Optional[float] = None,
    T: Optional[float] = None,
    h: Optional[float] = None,
    n: Optional[int] = None,
    eval_x: Optional[float] = None,
    integral_a: Optional[float] = None,
    integral_b: Optional[float] = None,
    n_points: Optional[int] = None
) -> MathEngineConfig:
    cfg = _engine_config
    if K is not None:
        cfg.K = float(K)
    if T is not None:
        cfg.T = max(0.01, float(T))
    if h is not None:
        cfg.h = max(1e-8, abs(float(h)))
    if n is not None:
        cfg.n = max(1, int(n))
    if eval_x is not None:
        cfg.eval_x = float(eval_x)
    if integral_a is not None:
        cfg.integral_a = float(integral_a)
    if integral_b is not None:
        cfg.integral_b = float(integral_b)
    if n_points is not None:
        cfg.n_points = max(2, int(n_points))
    return cfg


def get_complete_mathematical_analysis(cfg: Optional[MathEngineConfig] = None) -> Dict[str, Any]:
    """
    Generate comprehensive mathematical analysis fulfilling all user requirements:
    1. SymPy calculations:
       - Original function f(x) = x^4 - 3x^3 + 2x
       - First symbolic derivative f'(x) = 4x^3 - 9x^2 + 2
       - Indefinite symbolic integral F(x) = x^5/5 - 3x^4/4 + x^2
       - Function value at x = 2 -> f(2) = -4
       - Derivative value at x = 2 -> f'(2) = -2
       - Definite integral from 0 to 2 -> -1.6
    2. Numerical methods with error analysis:
       - Central difference at x = 2: [f(x+h) - f(x-h)] / (2h)
       - Composite trapezoidal integral from 0 to 2 with n intervals
       - Absolute and percentage error analysis
    3. Racing Model:
       - Normalized time x = t/T
       - Target velocity v_model = K * f(x)
       - Target acceleration a_model = (K/T) * f'(x)
       - Target displacement s_model = K * T * ∫_0^x f(u) du
       - Configurable K and T parameters
    4. Numerical arrays generated using NumPy:
       - Function values
       - Central difference derivative
       - Cumulative trapezoidal integration
       - Racing model arrays (t, x, v, a, s)
    """
    if cfg is None:
        cfg = _engine_config

    # --- 1. SymPy Calculations ---
    sympy_summary = get_sympy_engine_summary()

    # --- 2. Numerical Methods & Error Analysis ---
    # Central difference derivative at eval_x
    num_deriv = central_difference_derivative(cfg.eval_x, cfg.h)
    exact_deriv = evaluate_f_prime(cfg.eval_x)
    deriv_errors = calculate_error_analysis(num_deriv, exact_deriv)

    # Composite trapezoidal rule from integral_a to integral_b
    num_integral = integrate_trapezoidal(cfg.integral_a, cfg.integral_b, cfg.n)
    exact_integral_dict = get_exact_definite_integral(cfg.integral_a, cfg.integral_b)
    exact_integral = exact_integral_dict["value"]
    integ_errors = calculate_error_analysis(num_integral, exact_integral)

    # --- 3 & 4. NumPy Numerical Arrays & Racing Model ---
    num_arrays = generate_numerical_arrays(
        a=cfg.integral_a,
        b=cfg.integral_b,
        n_points=cfg.n_points,
        h=cfg.h
    )

    racing_model = generate_racing_model_arrays(
        K=cfg.K,
        T=cfg.T,
        x_max=cfg.integral_b,
        n_points=cfg.n_points,
        h=cfg.h
    )

    return {
        "status": "success",
        "equation": "f(x) = x^4 - 3x^3 + 2x",
        "course": "Numerical and Symbolic Computing",
        "sympy_calculations": {
            "original_function": sympy_summary["original_function"],
            "first_derivative": sympy_summary["first_derivative"],
            "indefinite_integral": sympy_summary["indefinite_integral"],
            "f_at_2": sympy_summary["f_at_2"],
            "f_prime_at_2": sympy_summary["f_prime_at_2"],
            "definite_integral_0_to_2": sympy_summary["definite_integral_0_to_2"]
        },
        "numerical_methods": {
            "central_difference": {
                "formula": "[f(x+h) - f(x-h)] / (2h)",
                "x": cfg.eval_x,
                "h": cfg.h,
                "numerical_value": round(num_deriv, 8),
                "exact_value": round(exact_deriv, 8),
                "absolute_error": deriv_errors["absolute_error"],
                "percentage_error": deriv_errors["percentage_error"]
            },
            "composite_trapezoidal": {
                "formula": "Composite Trapezoidal Rule",
                "interval": [cfg.integral_a, cfg.integral_b],
                "n_intervals": cfg.n,
                "numerical_value": round(num_integral, 8),
                "exact_value": round(exact_integral, 8),
                "absolute_error": integ_errors["absolute_error"],
                "percentage_error": integ_errors["percentage_error"]
            }
        },
        "racing_model": {
            "parameters": {
                "K": cfg.K,
                "T": cfg.T
            },
            "formulas": {
                "normalized_time": "x = t / T",
                "target_velocity": "v_model = K * f(x)",
                "target_acceleration": "a_model = (K/T) * f'(x)",
                "target_displacement": "s_model = K * T * integral(f(u), 0, x)"
            }
        },
        "numerical_arrays": {
            "x": num_arrays["x"],
            "f_x": num_arrays["f_x"],
            "central_difference_derivative": num_arrays["central_difference_derivative"],
            "cumulative_trapezoidal_integral": num_arrays["cumulative_trapezoidal_integral"],
            "racing_model_time_t": racing_model["arrays"]["time_t"],
            "racing_model_normalized_time_x": racing_model["arrays"]["normalized_time_x"],
            "racing_model_velocity_v": racing_model["arrays"]["target_velocity_v"],
            "racing_model_acceleration_a": racing_model["arrays"]["target_acceleration_a_exact"],
            "racing_model_displacement_s": racing_model["arrays"]["target_displacement_s_exact"]
        }
    }

