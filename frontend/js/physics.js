/**
 * FORMULA RACER - Physics & Mathematical Calculation Engine
 * Course: Numerical and Symbolic Computing
 *
 * STRICT MATHEMATICAL REQUIREMENT:
 * f(x) = x^4 - 3x^3 + 2x
 * Never replace this equation with another function.
 *
 * Provides:
 * 1. Exact mathematical calculus on f(x)
 * 2. Mathematical Target Velocity Profile connected to f(x)
 * 3. 2D top-down car dynamics (acceleration, braking, steering, drift, collision)
 */

class MathPhysicsEngine {
    constructor() {
        // Physical Constants (Top-Down Sports Car Specifications)
        this.MASS = 750.0;                 // kg
        this.GRAVITY = 9.81;              // m/s^2
        this.MAX_FORWARD_SPEED = 68.0;     // m/s (~245 km/h)
        this.MAX_REVERSE_SPEED = -12.0;    // m/s (~-43 km/h)
        this.MAX_ENGINE_ACCEL = 16.5;      // m/s^2 (0-100 km/h in ~3.2s)
        this.BRAKE_DECEL = 28.0;           // m/s^2 (racing carbon brakes)
        this.HANDBRAKE_DECEL = 38.0;       // m/s^2
        this.ROLLING_FRICTION = 0.85;      // m/s^2
        this.AIR_DRAG = 0.0016;            // Aerodynamic drag factor
        this.STEER_SENSITIVITY = 2.4;      // rad/s at optimal speed
        this.LATERAL_GRIP = 0.88;          // Grip factor (1.0 = on rails, 0.7 = drift)
        this.GRASS_DRAG_FACTOR = 4.2;      // Extra drag on grass
        this.TURBO_BOOST_ACCEL = 12.0;     // Extra m/s^2 when turbo is active

        // Mathematical Target Velocity Parameters
        this.K = 26.0;                     // Velocity scaling factor
        this.T = 10.0;                    // Time scale
        this.V_BASE = 50.0;                // Base target speed in km/h

        // Normalized Domain
        this.X_MIN = 0.0;
        this.X_MAX = 2.0;

        // Landmarks for f(x) = x^4 - 3x^3 + 2x on [0, 2]
        this.ROOTS = [
            { x: 0.0, label: "Root 2 (x = 0)", value: 0.0 },
            { x: 1.0, label: "Root 3 (x = 1)", value: 1.0 }
        ];

        this.CRITICAL_POINTS = [
            { x: 0.540877, type: "Summit (Peak)", label: "Peak Straight", y: this.f(0.540877) },
            { x: 2.000000, type: "Hairpin (Valley)", label: "Hairpin Apex", y: this.f(2.0) }
        ];

        this.INFLECTION_POINTS = [
            { x: 0.0, label: "Inflection 1 (x = 0)", y: 0.0 },
            { x: 1.5, label: "Inflection 2 (x = 1.5)", y: this.f(1.5) }
        ];
    }

    // ==========================================
    // EXACT MATHEMATICAL INVARIANT: f(x) = x^4 - 3x^3 + 2x
    // ==========================================

    /** STRICT ORIGINAL FUNCTION: f(x) = x^4 - 3x^3 + 2x */
    f(x) {
        return Math.pow(x, 4) - 3.0 * Math.pow(x, 3) + 2.0 * x;
    }

    /** EXACT FIRST DERIVATIVE: f'(x) = 4x^3 - 9x^2 + 2 */
    fPrime(x) {
        return 4.0 * Math.pow(x, 3) - 9.0 * Math.pow(x, 2) + 2.0;
    }

    /** EXACT SECOND DERIVATIVE: f''(x) = 12x^2 - 18x = 6x(2x - 3) */
    fDoublePrime(x) {
        return 12.0 * Math.pow(x, 2) - 18.0 * x;
    }

    /** EXACT INDEFINITE INTEGRAL: F(x) = x^5/5 - 3x^4/4 + x^2 */
    integral(x) {
        return Math.pow(x, 5) / 5.0 - (3.0 * Math.pow(x, 4)) / 4.0 + Math.pow(x, 2);
    }

    /** EXACT CURVATURE FORMULA: kappa(x) = |f''(x)| / (1 + (f'(x))^2)^(3/2) */
    curvature(x) {
        const dy = this.fPrime(x);
        const d2y = this.fDoublePrime(x);
        const denom = Math.pow(1.0 + dy * dy, 1.5);
        return denom > 1e-12 ? Math.abs(d2y) / denom : 0.0;
    }

    // ==========================================
    // MATHEMATICAL TARGET VELOCITY PROFILE
    // ==========================================

    /**
     * Target Velocity v_target(x) in km/h derived directly from f(x):
     * On x in [0, 2], f(x) reaches minimum of -4 at x = 2 and maximum of +0.65 at x ~ 0.54.
     * v_target = V_BASE + K * (f(x) + 4.5)
     */
    getTargetVelocityKmh(normX) {
        const clampedX = Math.max(0.0, Math.min(2.0, normX));
        const fx = this.f(clampedX);
        const targetKmh = this.V_BASE + this.K * (fx + 4.5);
        return Math.max(35.0, Math.min(235.0, targetKmh));
    }

    /**
     * Target Acceleration a_target(x) in m/s^2:
     * a_target = (K / T) * f'(x)
     */
    getTargetAcceleration(normX) {
        const clampedX = Math.max(0.0, Math.min(2.0, normX));
        return (this.K / this.T) * this.fPrime(clampedX);
    }

    /**
     * Target Displacement s_target(x) in meters:
     * s_target = K * T * ∫_0^x f(u) du
     */
    getTargetDisplacement(normX) {
        const clampedX = Math.max(0.0, Math.min(2.0, normX));
        return this.K * this.T * (this.integral(clampedX) - this.integral(0.0));
    }

    // ==========================================
    // 2D TOP-DOWN CAR PHYSICS SIMULATION
    // ==========================================

    /**
     * Update 2D vehicle dynamics over timestep dt:
     * @param {Object} car Current car state { x, y, angle, speed, vx, vy, isDrifting, onGrass }
     * @param {Object} input Player controls { throttle, brake, steer, handbrake, turbo }
     * @param {Number} dt Delta time in seconds (clamped to 0.033)
     * @param {Function} boundaryChecker Function (x, y) => { onRoad, onGrass, hitBarrier, nearestPoint, normal }
     */
    step2D(car, input, dt, boundaryChecker) {
        const clampedDt = Math.min(dt, 0.033);

        // Check track surface condition at current position
        const surface = boundaryChecker ? boundaryChecker(car.x, car.y) : { onRoad: true, onGrass: false, hitBarrier: false };
        const isOnGrass = surface.onGrass;
        const hitBarrier = surface.hitBarrier;

        // 1. Throttle and Engine Thrust
        let forwardAccel = 0.0;
        if (input.throttle > 0) {
            forwardAccel += input.throttle * this.MAX_ENGINE_ACCEL;
            if (input.turbo) forwardAccel += this.TURBO_BOOST_ACCEL;
        }

        // 2. Braking
        let brakeDecel = 0.0;
        if (input.handbrake) {
            brakeDecel += this.HANDBRAKE_DECEL;
        } else if (input.brake > 0) {
            if (car.speed > 0.5) {
                brakeDecel += input.brake * this.BRAKE_DECEL;
            } else {
                // Reverse
                forwardAccel -= input.brake * (this.MAX_ENGINE_ACCEL * 0.4);
            }
        }

        // 3. Rolling & Aerodynamic Resistance
        const dragCoeff = isOnGrass ? (this.AIR_DRAG * this.GRASS_DRAG_FACTOR) : this.AIR_DRAG;
        const rollingCoeff = isOnGrass ? (this.ROLLING_FRICTION * this.GRASS_DRAG_FACTOR) : this.ROLLING_FRICTION;

        const aeroDrag = dragCoeff * (car.speed * car.speed);
        const netDrag = rollingCoeff + aeroDrag;

        // 4. Update Forward Speed
        let speed = car.speed;
        if (speed > 0) {
            speed += (forwardAccel - brakeDecel - netDrag) * clampedDt;
            if (speed < 0 && !input.brake) speed = 0;
        } else if (speed < 0) {
            speed += (forwardAccel + brakeDecel + netDrag) * clampedDt;
            if (speed > 0 && !input.throttle) speed = 0;
        } else {
            speed += (forwardAccel - brakeDecel) * clampedDt;
        }

        // Clamping speed limits
        const maxSpeed = isOnGrass ? (this.MAX_FORWARD_SPEED * 0.38) : (input.turbo ? this.MAX_FORWARD_SPEED * 1.15 : this.MAX_FORWARD_SPEED);
        speed = Math.max(this.MAX_REVERSE_SPEED, Math.min(maxSpeed, speed));

        // 5. Steering Handling
        // Can only steer effectively when moving; reduces sensitivity at very high speed
        const speedRatio = Math.abs(speed) / this.MAX_FORWARD_SPEED;
        const steerSpeedFactor = Math.min(1.0, Math.abs(speed) / 3.0) * (1.1 - speedRatio * 0.35);
        const steerDirection = speed >= 0 ? 1.0 : -1.0;

        let angle = car.angle;
        if (Math.abs(input.steer) > 0.01) {
            angle += input.steer * this.STEER_SENSITIVITY * steerSpeedFactor * steerDirection * clampedDt;
        }

        // 6. Drift / Lateral Slide Physics
        const headingX = Math.cos(angle);
        const headingY = Math.sin(angle);
        const lateralX = -Math.sin(angle);
        const lateralY = Math.cos(angle);

        // Lateral grip: handbrake breaks traction
        const grip = input.handbrake ? 0.35 : (isOnGrass ? 0.6 : this.LATERAL_GRIP);
        const isDrifting = (Math.abs(input.steer) > 0.4 && speedRatio > 0.4) || input.handbrake;

        // Smooth velocity vector interpolation
        const forwardVx = speed * headingX;
        const forwardVy = speed * headingY;

        let vx = car.vx || forwardVx;
        let vy = car.vy || forwardVy;

        vx += (forwardVx - vx) * (grip * 12.0 * clampedDt);
        vy += (forwardVy - vy) * (grip * 12.0 * clampedDt);

        // 7. Update World Coordinate Position
        let newX = car.x + vx * 20.0 * clampedDt; // Scale: 1 meter = 20 pixels
        let newY = car.y + vy * 20.0 * clampedDt;

        // 8. Track Boundary & Barrier Collision
        let collided = false;
        if (boundaryChecker) {
            const check = boundaryChecker(newX, newY);
            if (check.hitBarrier) {
                // Elastic collision bounce off barrier
                collided = true;
                const normal = check.normal || { x: -headingX, y: -headingY };
                // Reflect velocity along normal
                const dot = vx * normal.x + vy * normal.y;
                vx = (vx - 1.5 * dot * normal.x) * 0.45;
                vy = (vy - 1.5 * dot * normal.y) * 0.45;
                speed = Math.sqrt(vx * vx + vy * vy) * (speed > 0 ? 1 : -1) * 0.5;

                // Push car back inside track
                if (check.pushback) {
                    newX += check.pushback.x;
                    newY += check.pushback.y;
                }
            }
        }

        return {
            x: newX,
            y: newY,
            angle: angle,
            speed: speed,
            speedKmh: Math.abs(speed) * 3.6,
            vx: vx,
            vy: vy,
            isDrifting: isDrifting,
            onGrass: isOnGrass,
            collided: collided,
            steerAngle: input.steer * 0.35 // Visual front wheel rotation
        };
    }
}

window.MathPhysicsEngine = MathPhysicsEngine;
