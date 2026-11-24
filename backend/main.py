"""
FastAPI Server for FORMULA RACER – Mathematical Racing Simulator
Course: Numerical and Symbolic Computing

STRICT MATHEMATICAL REQUIREMENT:
f(x) = x^4 - 3x^3 + 2x
Never replace this equation with another function.
"""

import os
import sys
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Add backend directory to sys.path so direct imports work regardless of working directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from symbolic import (
    get_full_symbolic_summary,
    get_exact_roots,
    get_exact_critical_points,
    get_inflection_points,
    compute_tangent_and_normal,
    compute_taylor_series,
    get_exact_definite_integral
)
from numerical import (
    compare_differentiation_methods,
    compare_integration_methods,
    solve_root_bisection,
    solve_root_newton_raphson,
    solve_root_secant
)
from calculations import (
    get_track,
    calculate_vehicle_telemetry,
    step_simulation,
    get_complete_mathematical_analysis,
    update_engine_config,
    get_engine_config,
    TRACK_X_MIN,
    TRACK_X_MAX
)

app = FastAPI(
    title="FORMULA RACER – Mathematical Racing Simulator",
    description="Numerical and Symbolic Computing Real-Time Simulator for f(x) = x^4 - 3x^3 + 2x",
    version="1.0.0"
)

# Enable CORS for local and web testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# REQUEST SCHEMAS
# ==========================================

class TaylorRequest(BaseModel):
    x0: float = Field(0.0, description="Expansion center point")
    order: int = Field(3, ge=1, le=6, description="Polynomial degree (1 to 6)")

class TangentNormalRequest(BaseModel):
    x0: float = Field(1.0, description="Evaluation point")

class DifferentiationRequest(BaseModel):
    x: float = Field(1.0, description="Coordinate to evaluate derivative")
    h_list: Optional[List[float]] = Field(None, description="Step sizes for finite differences")

class IntegrationRequest(BaseModel):
    a: float = Field(0.0, description="Lower integration bound")
    b: float = Field(2.0, description="Upper integration bound")
    n: int = Field(60, ge=2, le=1000, description="Number of subintervals")

class RootFindingRequest(BaseModel):
    method: str = Field("newton", description="'newton', 'bisection', or 'secant'")
    x0: Optional[float] = Field(0.5, description="Initial guess or start")
    x1: Optional[float] = Field(1.5, description="Second guess (for secant method)")
    a: Optional[float] = Field(-1.0, description="Interval left bound (for bisection)")
    b: Optional[float] = Field(0.5, description="Interval right bound (for bisection)")
    tol: float = Field(1e-6, description="Tolerance for convergence")
    max_iter: int = Field(50, ge=1, le=200, description="Maximum iterations")

class TelemetryRequest(BaseModel):
    x: float = Field(0.0, description="Vehicle x-position")
    velocity: float = Field(10.0, description="Vehicle velocity in m/s")
    throttle: float = Field(0.0, ge=0.0, le=1.0)
    brake: float = Field(0.0, ge=0.0, le=1.0)

class StepRequest(BaseModel):
    x: float = Field(0.0, description="Vehicle x-position")
    velocity: float = Field(0.0, description="Vehicle velocity in m/s")
    throttle: float = Field(0.0, ge=0.0, le=1.0)
    brake: float = Field(0.0, ge=0.0, le=1.0)
    dt: float = Field(0.016, ge=0.001, le=0.1)
    integrator: str = Field("rk4", description="'rk4' or 'euler'")

class SettingsRequest(BaseModel):
    K: Optional[float] = Field(None, description="Velocity scale parameter K")
    T: Optional[float] = Field(None, description="Time scale parameter T (seconds)")
    h: Optional[float] = Field(None, description="Central difference step size h (default 0.001)")
    n: Optional[int] = Field(None, ge=2, le=5000, description="Trapezoidal intervals count n (default 100)")
    eval_x: Optional[float] = Field(None, description="Evaluation coordinate x (default 2.0)")
    integral_a: Optional[float] = Field(None, description="Lower integration bound (default 0.0)")
    integral_b: Optional[float] = Field(None, description="Upper integration bound (default 2.0)")
    n_points: Optional[int] = Field(None, ge=10, le=1000, description="Points in numerical arrays (default 101)")


# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/api/health")
def get_health():
    """Health check endpoint returning engine status."""
    return {
        "status": "healthy",
        "service": "FORMULA RACER – Mathematical Engine",
        "course": "Numerical and Symbolic Computing",
        "strict_function": "f(x) = x^4 - 3x^3 + 2x",
        "version": "1.0.0"
    }


@app.get("/api/analysis")
def get_analysis():
    """
    Complete mathematical engine endpoint returning:
    - SymPy calculations (exact function, f'(x), F(x), f(2)=-4, f'(2)=-2, definite integral=-1.6)
    - Central difference method with error analysis (default h = 0.001)
    - Composite trapezoidal rule with error analysis (default n = 100)
    - Racing model (v_model = K*f(x), a_model = (K/T)*f'(x), s_model = K*T*∫f(u)du)
    - NumPy numerical arrays
    """
    return get_complete_mathematical_analysis()


@app.post("/api/settings")
def update_settings(req: SettingsRequest):
    """
    Update configurable engine and racing model parameters (K, T, h, n, etc.)
    and return recalculated analysis.
    """
    update_engine_config(
        K=req.K,
        T=req.T,
        h=req.h,
        n=req.n,
        eval_x=req.eval_x,
        integral_a=req.integral_a,
        integral_b=req.integral_b,
        n_points=req.n_points
    )
    return {
        "status": "success",
        "message": "Mathematical engine settings updated successfully",
        "current_settings": get_engine_config().to_dict(),
        "analysis": get_complete_mathematical_analysis()
    }

@app.get("/api/info")
def get_project_info():
    """Project metadata and strict mathematical formulation."""
    return {
        "project": "FORMULA RACER – Mathematical Racing Simulator",
        "course": "Numerical and Symbolic Computing",
        "strict_function": {
            "equation": "f(x) = x^4 - 3x^3 + 2x",
            "latex": "f(x) = x^{4} - 3x^{3} + 2x",
            "domain_recommended": [TRACK_X_MIN, TRACK_X_MAX],
            "note": "Strict mathematical invariant: used everywhere in simulation and analysis."
        },
        "features": {
            "symbolic": ["SymPy Exact Derivatives", "Exact Roots", "Critical Points", "Inflection Points", "Indefinite Integral", "Taylor Series", "Tangent & Normal"],
            "numerical": ["NumPy Vectorization", "Finite Differences (Forward, Backward, Central)", "Composite Trapezoidal", "Simpson's 1/3 & 3/8", "Newton-Raphson", "Bisection", "Secant", "Runge-Kutta 4th Order (RK4)", "Euler ODE"],
            "game": ["HTML5 Canvas 60 FPS Engine", "Interactive HUD", "Real-Time Telemetry", "Live Chart.js Graphs", "Dynamic Physics & Traction"]
        }
    }


@app.get("/api/symbolic/analysis")
def get_symbolic_analysis():
    """Complete symbolic computation package using SymPy."""
    return get_full_symbolic_summary()


@app.get("/api/symbolic/roots")
def get_symbolic_roots():
    """Exact analytical roots using SymPy solve."""
    return {"roots": get_exact_roots()}


@app.get("/api/symbolic/critical-points")
def get_symbolic_critical_points():
    """Exact critical points classified by second derivative test."""
    return {"critical_points": get_exact_critical_points()}


@app.get("/api/symbolic/inflection-points")
def get_symbolic_inflection_points():
    """Exact inflection points where f''(x) = 0."""
    return {"inflection_points": get_inflection_points()}


@app.post("/api/symbolic/taylor")
def calculate_taylor(req: TaylorRequest):
    """Compute exact Taylor polynomial around x0."""
    return compute_taylor_series(req.x0, req.order)


@app.post("/api/symbolic/tangent-normal")
def calculate_tangent_normal(req: TangentNormalRequest):
    """Compute exact tangent and normal equations at x0."""
    return compute_tangent_and_normal(req.x0)


@app.get("/api/numerical/track")
def get_numerical_track():
    """Get discretized track profile for rendering and HUD."""
    track = get_track()
    return track.get_track_profile()


@app.post("/api/numerical/differentiation")
def analyze_differentiation(req: DifferentiationRequest):
    """Finite differences vs exact derivative error analysis."""
    return compare_differentiation_methods(req.x, req.h_list)


@app.post("/api/numerical/integration")
def analyze_integration(req: IntegrationRequest):
    """Composite Trapezoidal, Simpson 1/3, and Simpson 3/8 vs exact analytical integral."""
    exact_res = get_exact_definite_integral(req.a, req.b)
    comp = compare_integration_methods(req.a, req.b, req.n, exact_res["value"])
    comp["exact_symbolic_expression"] = exact_res["exact_expression"]
    comp["exact_latex"] = exact_res["latex"]
    return comp


@app.post("/api/numerical/roots")
def run_root_finding(req: RootFindingRequest):
    """Step-by-step root finding with Newton-Raphson, Bisection, or Secant."""
    method = req.method.lower().strip()
    if method == "bisection":
        if req.a is None or req.b is None:
            raise HTTPException(status_code=400, detail="Bisection requires bounds 'a' and 'b'.")
        return solve_root_bisection(req.a, req.b, req.tol, req.max_iter)
    elif method == "secant":
        if req.x0 is None or req.x1 is None:
            raise HTTPException(status_code=400, detail="Secant requires 'x0' and 'x1'.")
        return solve_root_secant(req.x0, req.x1, req.tol, req.max_iter)
    elif method in ["newton", "newton-raphson"]:
        if req.x0 is None:
            raise HTTPException(status_code=400, detail="Newton requires initial guess 'x0'.")
        return solve_root_newton_raphson(req.x0, req.tol, req.max_iter)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method '{req.method}'. Choose 'newton', 'bisection', or 'secant'.")


@app.post("/api/physics/telemetry")
def get_telemetry(req: TelemetryRequest):
    """Compute instantaneous telemetry at (x, v)."""
    return calculate_vehicle_telemetry(req.x, req.velocity, req.throttle, req.brake)


@app.post("/api/physics/step")
def step_physics(req: StepRequest):
    """Step the vehicle physics simulation forward by dt."""
    return step_simulation(req.x, req.velocity, req.throttle, req.brake, req.dt, req.integrator)


# ==========================================
# STATIC FILES AND FRONTEND SERVING
# ==========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

assets_dir = os.path.join(FRONTEND_DIR, "assets")
css_dir = os.path.join(FRONTEND_DIR, "css")
js_dir = os.path.join(FRONTEND_DIR, "js")

os.makedirs(assets_dir, exist_ok=True)
os.makedirs(css_dir, exist_ok=True)
os.makedirs(js_dir, exist_ok=True)

app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
app.mount("/css", StaticFiles(directory=css_dir), name="css")
app.mount("/js", StaticFiles(directory=js_dir), name="js")

@app.get("/")
def serve_index():
    """Serve main game HTML interface."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "FORMULA RACER Backend Running. Frontend index.html ready to be loaded."}


@app.get("/favicon.ico", include_in_schema=False)
def serve_favicon():
    """Serve favicon to avoid browser 404s."""
    fav_path = os.path.join(FRONTEND_DIR, "assets", "favicon.ico")
    if os.path.exists(fav_path):
        return FileResponse(fav_path, media_type="image/x-icon")
    fav_root = os.path.join(FRONTEND_DIR, "favicon.ico")
    if os.path.exists(fav_root):
        return FileResponse(fav_root, media_type="image/x-icon")
    return Response(status_code=204)
