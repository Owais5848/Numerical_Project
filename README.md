# FORMULA RACER – Mathematical Racing Simulator
**Course:** Numerical and Symbolic Computing

A playable browser-based mathematical racing simulator demonstrating real-time symbolic calculus and numerical computing.

---

## Strict Mathematical Invariant

The entire track profile, elevation, derivatives, curvature, and physics forces are strictly governed everywhere by:

$$f(x) = x^4 - 3x^3 + 2x$$

### Exact Analytical Properties (SymPy):
- **First Derivative (Slope / Track Incline):**  
  $$f'(x) = 4x^3 - 9x^2 + 2$$
- **Second Derivative (Convexity / Track Crests & Valleys):**  
  $$f''(x) = 12x^2 - 18x = 6x(2x - 3)$$
- **Third Derivative (Track Jerk & Transition):**  
  $$f'''(x) = 24x - 18$$
- **Exact Roots ($f(x) = 0$):**  
  $$x_1 = 1 - \sqrt{3} \approx -0.732051, \quad x_2 = 0.0, \quad x_3 = 1.0, \quad x_4 = 1 + \sqrt{3} \approx 2.732051$$
- **Critical Points ($f'(x) = 0$):**  
  Three real roots representing valleys (local minimums) and hill crests (local maximums):  
  $x \approx -0.4948$ (Valley), $x \approx 0.6475$ (Crest / Peak), $x \approx 2.0972$ (Valley).
- **Inflection Points ($f''(x) = 0$):**  
  $$x = 0 \quad \text{and} \quad x = \frac{3}{2} = 1.5$$
- **Exact Curvature Formula:**  
  $$\kappa(x) = \frac{|f''(x)|}{\left(1 + (f'(x))^2\right)^{3/2}} = \frac{|12x^2 - 18x|}{\left(1 + (4x^3 - 9x^2 + 2)^2\right)^{3/2}}$$
- **Exact Indefinite Integral (Arc Potential Energy):**  
  $$\int f(x) dx = \frac{x^5}{5} - \frac{3x^4}{4} + x^2 + C$$

---

## Numerical Computing Implementations (NumPy)

1. **Numerical Differentiation:**
   - Forward Difference: $f'(x) \approx \frac{f(x+h) - f(x)}{h}$ ($O(h)$ truncation error)
   - Backward Difference: $f'(x) \approx \frac{f(x) - f(x-h)}{h}$ ($O(h)$ truncation error)
   - Central Difference: $f'(x) \approx \frac{f(x+h) - f(x-h)}{2h}$ ($O(h^2)$ truncation error)
   - Real-time log-log error study comparing finite differences against exact SymPy derivative.

2. **Numerical Integration:**
   - Composite Trapezoidal Rule
   - Composite Simpson's 1/3 Rule
   - Composite Simpson's 3/8 Rule
   - Arc Length Quadrature: $S = \int \sqrt{1 + (f'(x))^2} dx$

3. **Root Finding Algorithms:**
   - **Newton-Raphson Method:** $x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$ with tangent line visualization
   - **Bisection Method:** Interval halving on $[a, b]$ with error bound $(b-a)/2$
   - **Secant Method:** Finite difference secant approximation

4. **Vehicle Dynamics & Numerical ODE Solvers:**
   - **Runge-Kutta 4th Order (RK4):** 4-stage coupled numerical integration for position and velocity
   - **Euler's Method:** 1st-order numerical stepping
   - Live toggling between RK4 and Euler to observe energy conservation and drift.

---

## Project Architecture

```
new_racing/
├── frontend/
│   ├── index.html             # Main simulator interface and Math Lab
│   ├── css/
│   │   └── style.css          # F1 telemetry styling & dark UI
│   ├── js/
│   │   ├── game.js            # 60 FPS Canvas racing simulator engine
│   │   ├── physics.js         # Mathematical calculation & physics engine
│   │   ├── charts.js          # Chart.js live telemetry & error graphs
│   │   ├── controls.js        # Keyboard & touch input handling
│   │   └── api.js             # FastAPI REST client
│   └── assets/
│       └── chart.min.js       # Local Chart.js library bundle
├── backend/
│   ├── main.py                # FastAPI server, endpoints & static serving
│   ├── symbolic.py            # SymPy analytical calculus module
│   ├── numerical.py           # NumPy numerical methods module
│   ├── calculations.py        # Telemetry & ODE integration bridge
│   └── requirements.txt       # Python dependencies
├── verify_backend.py          # Synchronous unit test suite
├── test_e2e.py                # End-to-end HTTP integration test suite
└── README.md                  # Project documentation
```

---

## How to Run

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Start the Simulator Server (from inside the backend folder)
```bash
cd backend
uvicorn main:app --reload
```

*(Alternatively from project root: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`)*

### 3. Open in Browser
Navigate to:
[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Controls
- **Accelerate / Throttle:** `[W]` or `[Up Arrow]`
- **Brake / Reverse:** `[S]` or `[Down Arrow]`
- **Handbrake:** `[Space]`
- **Turbo Boost:** `[T]` or `[Shift]`
- **Reset Vehicle:** `[R]`
- **Toggle ODE Integrator (RK4 / Euler):** `[M]`
- **Toggle Camera (Follow / Overview):** `[C]` or Camera button
- **Touch / Mobile:** On-screen gas, brake, and turbo pedals
