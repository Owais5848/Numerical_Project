/**
 * FORMULA RACER - Chart.js Visualizations Module
 * Course: Numerical and Symbolic Computing
 *
 * STRICT MATHEMATICAL REQUIREMENT:
 * f(x) = x^4 - 3x^3 + 2x
 * Never replace this equation with another function.
 *
 * THREE LIVE MATHEMATICAL GRAPHS:
 * 1. Target Velocity vs Time: v_model(t) = K * f(t/T) & Actual Vehicle Speed
 * 2. Target Acceleration vs Time: a_model(t) = (K/T) * f'(t/T)
 * 3. Target Displacement vs Time: s_model(t) = K * T * ∫_0^{t/T} f(u) du
 *
 * REQUIREMENTS:
 * - Real-time updates during gameplay synchronized with race time
 * - Continuous moving current-time indicator line and marker point
 * - Target and actual velocity curves displayed side-by-side
 * - Fast linear interpolation of precomputed FastAPI NumPy arrays
 * - Zero API network calls during animation frames for peak 60 FPS performance
 * - Seamless pause, resume, and reset handling
 */

class SimulationCharts {
    constructor(physicsEngine) {
        this.physics = physicsEngine;

        // 3 Primary Live Mathematical Charts
        this.velocityChart = null;
        this.accelerationChart = null;
        this.displacementChart = null;

        // Secondary Track & Laboratory Charts
        this.elevationChart = null;
        this.derivativesChart = null;
        this.telemetryChart = null;
        this.numericalLabChart = null;

        // Precomputed NumPy arrays from FastAPI backend
        this.precomputedTime = [];
        this.precomputedNormX = [];
        this.precomputedVelocity = [];
        this.precomputedAcceleration = [];
        this.precomputedDisplacement = [];

        // Parameters (synchronized with backend configuration)
        this.K = 20.0;
        this.T = 10.0;
        this.tMax = 20.0;
        this.xMax = 2.0;

        // Min/Max bounds for cursor line rendering
        this.vMin = -90.0;
        this.vMax = 25.0;
        this.aMin = -6.0;
        this.aMax = 6.0;
        this.sMin = -350.0;
        this.sMax = 50.0;

        // Actual vehicle speed trajectory recording
        this.actualSpeedTrajectory = []; // [{ x: t, y: v_actual_mps }]
        this.lastRecordedTime = -1.0;
        this.isPaused = false;
        this.currentTime = 0.0;

        // Telemetry history buffers for rolling chart
        this.maxHistory = 50;
        this.historyLabels = [];
        this.speedHistory = [];
        this.gForceHistory = [];
        this.kineticEnergyHistory = [];
        this.potentialEnergyHistory = [];
        this.frameCount = 0;

        // Track profile for secondary charts
        this.trackData = null;
    }

    async init() {
        if (typeof Chart === "undefined") {
            console.error("Chart.js not loaded!");
            return;
        }

        // High-tech dark theme defaults
        Chart.defaults.color = "#94a3b8";
        Chart.defaults.borderColor = "rgba(51, 65, 85, 0.6)";
        Chart.defaults.font.family = "'JetBrains Mono', 'Segoe UI', monospace";
        Chart.defaults.plugins.tooltip.backgroundColor = "rgba(15, 23, 42, 0.95)";
        Chart.defaults.plugins.tooltip.borderColor = "#38bdf8";
        Chart.defaults.plugins.tooltip.borderWidth = 1;

        // 1. Fetch precomputed NumPy arrays from FastAPI (once at startup!)
        await this.loadRacingModelArrays();

        // 2. Prepare track profile for secondary charts
        await this.prepareTrackData();

        // 3. Initialize the 3 Primary Live Mathematical Graphs
        this.initVelocityChart();
        this.initAccelerationChart();
        this.initDisplacementChart();

        // 4. Initialize Secondary Profile & Laboratory Charts
        this.initElevationChart();
        this.initDerivativesChart();
        this.initTelemetryChart();
        this.initNumericalLabChart();

        // Initial zero-state render
        this.updateRealtime(0.0, 0.0, 0.0, "ready");
        console.log("SimulationCharts: 3 Real-Time Mathematical Graphs Initialized Successfully.");
    }

    // =========================================================================
    // 1. FETCH PRECOMPUTED NUMPY ARRAYS FROM FASTAPI
    // =========================================================================
    async loadRacingModelArrays() {
        try {
            const res = await API.getAnalysis();
            if (res && res.numerical_arrays && res.numerical_arrays.racing_model_time_t) {
                const na = res.numerical_arrays;
                this.precomputedTime = na.racing_model_time_t;
                this.precomputedNormX = na.racing_model_normalized_time_x;
                this.precomputedVelocity = na.racing_model_velocity_v;
                this.precomputedAcceleration = na.racing_model_acceleration_a;
                this.precomputedDisplacement = na.racing_model_displacement_s;

                if (res.racing_model && res.racing_model.parameters) {
                    this.K = res.racing_model.parameters.K || 20.0;
                    this.T = res.racing_model.parameters.T || 10.0;
                }
                this.tMax = this.precomputedTime[this.precomputedTime.length - 1] || 20.0;
                this.calculateBounds();
                return;
            }
        } catch (e) {
            console.warn("Could not fetch precomputed arrays from FastAPI, falling back to local exact generator.", e);
        }

        // Fallback generator using exact equations if backend endpoint is initializing
        this.generateLocalPrecomputedArrays();
    }

    generateLocalPrecomputedArrays() {
        const nPoints = 101;
        this.tMax = this.xMax * this.T;
        this.precomputedTime = [];
        this.precomputedNormX = [];
        this.precomputedVelocity = [];
        this.precomputedAcceleration = [];
        this.precomputedDisplacement = [];

        for (let i = 0; i < nPoints; i++) {
            const t = (i / (nPoints - 1)) * this.tMax;
            const x = t / this.T;
            const fx = this.physics.f(x);
            const fpx = this.physics.fPrime(x);
            const Fx = this.physics.integral(x);

            this.precomputedTime.push(t);
            this.precomputedNormX.push(x);
            this.precomputedVelocity.push(this.K * fx);
            this.precomputedAcceleration.push((this.K / this.T) * fpx);
            this.precomputedDisplacement.push(this.K * this.T * Fx);
        }
        this.calculateBounds();
    }

    calculateBounds() {
        if (this.precomputedVelocity.length > 0) {
            const vMin = Math.min(...this.precomputedVelocity);
            const vMax = Math.max(...this.precomputedVelocity);
            const vPad = Math.max(10.0, (vMax - vMin) * 0.15);
            this.vMin = Math.floor(vMin - vPad);
            this.vMax = Math.ceil(vMax + vPad);

            const aMin = Math.min(...this.precomputedAcceleration);
            const aMax = Math.max(...this.precomputedAcceleration);
            const aPad = Math.max(1.0, (aMax - aMin) * 0.15);
            this.aMin = Math.floor(aMin - aPad);
            this.aMax = Math.ceil(aMax + aPad);

            const sMin = Math.min(...this.precomputedDisplacement);
            const sMax = Math.max(...this.precomputedDisplacement);
            const sPad = Math.max(20.0, (sMax - sMin) * 0.15);
            this.sMin = Math.floor(sMin - sPad);
            this.sMax = Math.ceil(sMax + sPad);
        }
    }

    // =========================================================================
    // 2. FAST IN-MEMORY JAVASCRIPT LINEAR INTERPOLATION (O(1))
    // =========================================================================
    interpolate(timeArr, valArr, t) {
        if (!timeArr || timeArr.length === 0) return 0.0;
        if (t <= timeArr[0]) return valArr[0];
        const n = timeArr.length;
        if (t >= timeArr[n - 1]) return valArr[n - 1];

        // Uniform grid direct index calculation (precomputed array is linspace)
        const t0 = timeArr[0];
        const tEnd = timeArr[n - 1];
        const ratio = (t - t0) / (tEnd - t0);
        let idx = Math.floor(ratio * (n - 1));
        idx = Math.max(0, Math.min(n - 2, idx));

        // Refine bracket if needed
        while (idx < n - 1 && timeArr[idx + 1] < t) idx++;
        while (idx > 0 && timeArr[idx] > t) idx--;

        const t1 = timeArr[idx];
        const t2 = timeArr[idx + 1];
        const v1 = valArr[idx];
        const v2 = valArr[idx + 1];

        if (t2 === t1) return v1;
        const factor = (t - t1) / (t2 - t1);
        return v1 + factor * (v2 - v1);
    }

    // =========================================================================
    // 3. GRAPH 1: TARGET VELOCITY VS TIME & ACTUAL VEHICLE SPEED
    // =========================================================================
    initVelocityChart() {
        const ctx = document.getElementById("velocityChart");
        if (!ctx) return;

        // Precomputed Target Curve points
        const targetPoints = this.precomputedTime.map((t, i) => ({
            x: t,
            y: this.precomputedVelocity[i]
        }));

        this.velocityChart = new Chart(ctx, {
            type: "line",
            data: {
                datasets: [
                    {
                        label: `Target Velocity v_model(t) = ${this.K}·f(t/${this.T})`,
                        data: targetPoints,
                        borderColor: "#38bdf8", // Sky blue
                        borderWidth: 2.5,
                        pointRadius: 0,
                        tension: 0.1,
                        order: 2
                    },
                    {
                        label: "Actual Vehicle Speed (m/s)",
                        data: this.actualSpeedTrajectory,
                        borderColor: "#10b981", // Emerald green
                        backgroundColor: "rgba(16, 185, 129, 0.12)",
                        borderWidth: 2.2,
                        pointRadius: 0,
                        tension: 0.1,
                        fill: false,
                        order: 1
                    },
                    {
                        label: "Current Time (Cursor)",
                        data: [{ x: 0, y: this.vMin }, { x: 0, y: this.vMax }],
                        borderColor: "rgba(245, 158, 11, 0.9)", // Amber
                        borderWidth: 1.8,
                        borderDash: [5, 4],
                        pointRadius: 0,
                        order: 0
                    },
                    {
                        label: "Target Position (t, v_target)",
                        data: [{ x: 0, y: this.precomputedVelocity[0] || 0 }],
                        borderColor: "#ffffff",
                        backgroundColor: "#38bdf8",
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        showLine: false,
                        order: 0
                    },
                    {
                        label: "Actual Position (t, v_actual)",
                        data: [{ x: 0, y: 0 }],
                        borderColor: "#ffffff",
                        backgroundColor: "#10b981",
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        showLine: false,
                        order: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                interaction: {
                    mode: "nearest",
                    axis: "x",
                    intersect: false
                },
                scales: {
                    x: {
                        type: "linear",
                        min: 0,
                        max: this.tMax,
                        title: { display: true, text: "Time t (seconds)", color: "#94a3b8" }
                    },
                    y: {
                        min: this.vMin,
                        max: this.vMax,
                        title: { display: true, text: "Velocity v (m/s)", color: "#94a3b8" }
                    }
                },
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            boxWidth: 12,
                            padding: 8,
                            filter: (item) => !item.text.includes("Position") && !item.text.includes("Cursor")
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (c) => `${c.dataset.label}: ${c.parsed.y.toFixed(2)} m/s (${(c.parsed.y * 3.6).toFixed(1)} km/h)`
                        }
                    }
                }
            }
        });
    }

    // =========================================================================
    // 4. GRAPH 2: TARGET ACCELERATION VS TIME
    // =========================================================================
    initAccelerationChart() {
        const ctx = document.getElementById("accelerationChart");
        if (!ctx) return;

        const targetAccelPoints = this.precomputedTime.map((t, i) => ({
            x: t,
            y: this.precomputedAcceleration[i]
        }));

        this.accelerationChart = new Chart(ctx, {
            type: "line",
            data: {
                datasets: [
                    {
                        label: `Target Acceleration a_model(t) = (${this.K}/${this.T})·f'(t/${this.T})`,
                        data: targetAccelPoints,
                        borderColor: "#f43f5e", // Rose
                        borderWidth: 2.5,
                        pointRadius: 0,
                        tension: 0.1,
                        order: 2
                    },
                    {
                        label: "Current Time (Cursor)",
                        data: [{ x: 0, y: this.aMin }, { x: 0, y: this.aMax }],
                        borderColor: "rgba(245, 158, 11, 0.9)",
                        borderWidth: 1.8,
                        borderDash: [5, 4],
                        pointRadius: 0,
                        order: 0
                    },
                    {
                        label: "Current Target Acceleration",
                        data: [{ x: 0, y: this.precomputedAcceleration[0] || 0 }],
                        borderColor: "#ffffff",
                        backgroundColor: "#f43f5e",
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        showLine: false,
                        order: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: {
                        type: "linear",
                        min: 0,
                        max: this.tMax,
                        title: { display: true, text: "Time t (seconds)", color: "#94a3b8" }
                    },
                    y: {
                        min: this.aMin,
                        max: this.aMax,
                        title: { display: true, text: "Acceleration a (m/s²)", color: "#94a3b8" }
                    }
                },
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            boxWidth: 12,
                            padding: 8,
                            filter: (item) => !item.text.includes("Current")
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (c) => `${c.dataset.label}: ${c.parsed.y.toFixed(2)} m/s²`
                        }
                    }
                }
            }
        });
    }

    // =========================================================================
    // 5. GRAPH 3: TARGET DISPLACEMENT VS TIME
    // =========================================================================
    initDisplacementChart() {
        const ctx = document.getElementById("displacementChart");
        if (!ctx) return;

        const targetDisplacementPoints = this.precomputedTime.map((t, i) => ({
            x: t,
            y: this.precomputedDisplacement[i]
        }));

        this.displacementChart = new Chart(ctx, {
            type: "line",
            data: {
                datasets: [
                    {
                        label: `Target Displacement s_model(t) = K·T·∫f(u)du`,
                        data: targetDisplacementPoints,
                        borderColor: "#c084fc", // Purple
                        borderWidth: 2.5,
                        pointRadius: 0,
                        tension: 0.1,
                        order: 2
                    },
                    {
                        label: "Current Time (Cursor)",
                        data: [{ x: 0, y: this.sMin }, { x: 0, y: this.sMax }],
                        borderColor: "rgba(245, 158, 11, 0.9)",
                        borderWidth: 1.8,
                        borderDash: [5, 4],
                        pointRadius: 0,
                        order: 0
                    },
                    {
                        label: "Current Target Displacement",
                        data: [{ x: 0, y: this.precomputedDisplacement[0] || 0 }],
                        borderColor: "#ffffff",
                        backgroundColor: "#c084fc",
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        showLine: false,
                        order: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: {
                        type: "linear",
                        min: 0,
                        max: this.tMax,
                        title: { display: true, text: "Time t (seconds)", color: "#94a3b8" }
                    },
                    y: {
                        min: this.sMin,
                        max: this.sMax,
                        title: { display: true, text: "Displacement s (meters)", color: "#94a3b8" }
                    }
                },
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            boxWidth: 12,
                            padding: 8,
                            filter: (item) => !item.text.includes("Current")
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (c) => `${c.dataset.label}: ${c.parsed.y.toFixed(2)} m`
                        }
                    }
                }
            }
        });
    }

    // =========================================================================
    // 6. REAL-TIME 60 FPS GAMEPLAY SYNCHRONIZATION (ZERO API CALLS!)
    // =========================================================================
    updateRealtime(raceTime, actualSpeedKmh, actualSpeedMps, gameState = "racing") {
        this.currentTime = Math.max(0.0, raceTime || 0.0);
        const t = this.currentTime;
        const normX = t / this.T;

        // Interpolate target values from precomputed NumPy arrays in JavaScript
        const vTarget = this.interpolate(this.precomputedTime, this.precomputedVelocity, t);
        const aTarget = this.interpolate(this.precomputedTime, this.precomputedAcceleration, t);
        const sTarget = this.interpolate(this.precomputedTime, this.precomputedDisplacement, t);

        // Calculate exact calculus values
        const fVal = this.physics.f(normX);
        const fPrimeVal = this.physics.fPrime(normX);
        const integVal = this.physics.integral(normX);

        // Record actual vehicle speed history trajectory during active gameplay
        if (gameState === "racing") {
            if (t > this.lastRecordedTime + 0.05) { // record every 50ms for smooth curve
                this.actualSpeedTrajectory.push({ x: t, y: actualSpeedMps });
                this.lastRecordedTime = t;

                // Keep memory bounded to 1500 points
                if (this.actualSpeedTrajectory.length > 1500) {
                    this.actualSpeedTrajectory.shift();
                }
            }
        }

        // ----------------------------------------------------
        // Update GRAPH 1: Target Velocity vs Time
        // ----------------------------------------------------
        if (this.velocityChart) {
            // Update Cursor Line at x = t
            this.velocityChart.data.datasets[2].data = [
                { x: t, y: this.vMin },
                { x: t, y: this.vMax }
            ];
            // Update Target Marker Point
            this.velocityChart.data.datasets[3].data = [{ x: t, y: vTarget }];
            // Update Actual Marker Point
            this.velocityChart.data.datasets[4].data = [{ x: t, y: actualSpeedMps }];

            this.velocityChart.update("none");
        }

        // ----------------------------------------------------
        // Update GRAPH 2: Target Acceleration vs Time
        // ----------------------------------------------------
        if (this.accelerationChart) {
            // Update Cursor Line at x = t
            this.accelerationChart.data.datasets[1].data = [
                { x: t, y: this.aMin },
                { x: t, y: this.aMax }
            ];
            // Update Target Accel Marker Point
            this.accelerationChart.data.datasets[2].data = [{ x: t, y: aTarget }];

            this.accelerationChart.update("none");
        }

        // ----------------------------------------------------
        // Update GRAPH 3: Target Displacement vs Time
        // ----------------------------------------------------
        if (this.displacementChart) {
            // Update Cursor Line at x = t
            this.displacementChart.data.datasets[1].data = [
                { x: t, y: this.sMin },
                { x: t, y: this.sMax }
            ];
            // Update Target Displacement Marker Point
            this.displacementChart.data.datasets[2].data = [{ x: t, y: sTarget }];

            this.displacementChart.update("none");
        }

        // ----------------------------------------------------
        // Update Mathematical Value Badges on Graph Cards
        // ----------------------------------------------------
        this.updateValueBadges(t, normX, vTarget, actualSpeedMps, actualSpeedKmh, aTarget, fPrimeVal, sTarget, integVal, gameState);

        // Update secondary charts if present
        this.updateSecondaryCharts(normX, actualSpeedKmh);
    }

    updateValueBadges(t, normX, vTarget, actualMps, actualKmh, aTarget, fPrime, sTarget, integF, gameState) {
        // Live time pill
        const timePill = document.getElementById("liveTimePill");
        if (timePill) {
            timePill.innerText = `t = ${t.toFixed(2)} s (x = ${normX.toFixed(3)})`;
        }

        // Sync status badge
        const syncStatus = document.getElementById("graphsSyncStatus");
        const liveDot = document.getElementById("liveDot");
        if (syncStatus) {
            if (gameState === "paused") {
                syncStatus.innerText = "SIMULATION PAUSED";
                if (liveDot) liveDot.style.background = "#f59e0b";
            } else if (gameState === "racing") {
                syncStatus.innerText = "SYNCED WITH GAME TIME (60 FPS)";
                if (liveDot) liveDot.style.background = "#10b981";
            } else {
                syncStatus.innerText = "STANDBY / GRID READY";
                if (liveDot) liveDot.style.background = "#38bdf8";
            }
        }

        // Graph 1 readouts
        const elTargetV = document.getElementById("valTargetV");
        if (elTargetV) elTargetV.innerText = `${vTarget.toFixed(2)} m/s`;
        const elTargetVKmh = document.getElementById("valTargetVKmh");
        if (elTargetVKmh) elTargetVKmh.innerText = `(${(vTarget * 3.6).toFixed(1)} km/h)`;

        const elActualV = document.getElementById("valActualV");
        if (elActualV) elActualV.innerText = `${actualMps.toFixed(2)} m/s`;
        const elActualVKmh = document.getElementById("valActualVKmh");
        if (elActualVKmh) elActualVKmh.innerText = `(${actualKmh.toFixed(1)} km/h)`;

        // Graph 2 readouts
        const elTargetA = document.getElementById("valTargetA");
        if (elTargetA) elTargetA.innerText = `${aTarget >= 0 ? "+" : ""}${aTarget.toFixed(2)} m/s²`;
        const elFPrimeX = document.getElementById("valFPrimeX");
        if (elFPrimeX) elFPrimeX.innerText = `${fPrime >= 0 ? "+" : ""}${fPrime.toFixed(3)}`;

        // Graph 3 readouts
        const elTargetS = document.getElementById("valTargetS");
        if (elTargetS) elTargetS.innerText = `${sTarget.toFixed(1)} m`;
        const elIntegF = document.getElementById("valIntegF");
        if (elIntegF) elIntegF.innerText = `${integF.toFixed(3)}`;
    }

    // =========================================================================
    // 7. RESET & PAUSE HANDLING
    // =========================================================================
    reset() {
        this.actualSpeedTrajectory.length = 0;
        this.lastRecordedTime = -1.0;
        this.currentTime = 0.0;
        this.updateRealtime(0.0, 0.0, 0.0, "ready");
    }

    setPaused(paused) {
        this.isPaused = paused;
        const syncStatus = document.getElementById("graphsSyncStatus");
        const liveDot = document.getElementById("liveDot");
        if (syncStatus) {
            syncStatus.innerText = paused ? `PAUSED (t = ${this.currentTime.toFixed(2)}s)` : "SYNCED WITH GAME TIME (60 FPS)";
        }
        if (liveDot) {
            liveDot.style.background = paused ? "#f59e0b" : "#10b981";
        }
    }

    async reloadSettings(K, T) {
        if (K !== undefined) this.K = parseFloat(K);
        if (T !== undefined) this.T = parseFloat(T);
        await this.loadRacingModelArrays();

        // Update Target datasets on all 3 charts
        if (this.velocityChart) {
            this.velocityChart.data.datasets[0].data = this.precomputedTime.map((t, i) => ({
                x: t,
                y: this.precomputedVelocity[i]
            }));
            this.velocityChart.options.scales.x.max = this.tMax;
            this.velocityChart.options.scales.y.min = this.vMin;
            this.velocityChart.options.scales.y.max = this.vMax;
            this.velocityChart.update();
        }

        if (this.accelerationChart) {
            this.accelerationChart.data.datasets[0].data = this.precomputedTime.map((t, i) => ({
                x: t,
                y: this.precomputedAcceleration[i]
            }));
            this.accelerationChart.options.scales.x.max = this.tMax;
            this.accelerationChart.options.scales.y.min = this.aMin;
            this.accelerationChart.options.scales.y.max = this.aMax;
            this.accelerationChart.update();
        }

        if (this.displacementChart) {
            this.displacementChart.data.datasets[0].data = this.precomputedTime.map((t, i) => ({
                x: t,
                y: this.precomputedDisplacement[i]
            }));
            this.displacementChart.options.scales.x.max = this.tMax;
            this.displacementChart.options.scales.y.min = this.sMin;
            this.displacementChart.options.scales.y.max = this.sMax;
            this.displacementChart.update();
        }

        this.reset();
    }

    // =========================================================================
    // 8. SECONDARY CHARTS & TELEMETRY
    // =========================================================================
    async prepareTrackData() {
        let profile = null;
        try {
            profile = await API.getTrackProfile();
        } catch (e) {}

        if (!profile || !profile.x) {
            const samples = 200;
            const xArr = [];
            const yArr = [];
            const dyArr = [];
            const d2yArr = [];
            const kappaArr = [];
            for (let i = 0; i <= samples; i++) {
                const xi = (i / samples) * 2.0;
                xArr.push(Number(xi.toFixed(4)));
                yArr.push(Number(this.physics.f(xi).toFixed(4)));
                dyArr.push(Number(this.physics.fPrime(xi).toFixed(4)));
                d2yArr.push(Number(this.physics.fDoublePrime(xi).toFixed(4)));
                kappaArr.push(Number(this.physics.curvature(xi).toFixed(4)));
            }
            profile = {
                x: xArr,
                y: yArr,
                slope: dyArr,
                second_derivative: d2yArr,
                curvature: kappaArr,
                roots: this.physics.ROOTS,
                critical_points: this.physics.CRITICAL_POINTS
            };
        }
        this.trackData = profile;
    }

    initElevationChart() {
        const ctx = document.getElementById("elevationChart");
        if (!ctx || !this.trackData) return;

        const xyData = this.trackData.x.map((x, i) => ({ x, y: this.trackData.y[i] }));
        const rootPoints = this.physics.ROOTS.map(r => ({ x: r.x, y: 0.0 }));

        this.elevationChart = new Chart(ctx, {
            type: "line",
            data: {
                datasets: [
                    {
                        label: "Track Profile: f(x) = x⁴ - 3x³ + 2x",
                        data: xyData,
                        borderColor: "#06b6d4",
                        borderWidth: 2.5,
                        pointRadius: 0,
                        fill: { target: "origin", above: "rgba(6, 182, 212, 0.08)", below: "rgba(239, 68, 68, 0.08)" },
                        tension: 0.1
                    },
                    {
                        label: "Racer Position (x, y)",
                        data: [{ x: 0.0, y: 0.0 }],
                        borderColor: "#f59e0b",
                        backgroundColor: "#f59e0b",
                        pointRadius: 7,
                        showLine: false
                    },
                    {
                        label: "Tangent Line at Racer",
                        data: [{ x: -0.2, y: 0.0 }, { x: 0.2, y: 0.0 }],
                        borderColor: "#ec4899",
                        borderWidth: 1.8,
                        borderDash: [5, 4],
                        pointRadius: 0
                    },
                    {
                        label: "Exact Roots",
                        data: rootPoints,
                        borderColor: "#10b981",
                        backgroundColor: "#10b981",
                        pointRadius: 5,
                        pointStyle: "rectRot",
                        showLine: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: { type: "linear", min: 0.0, max: 2.0, title: { display: true, text: "Track Coordinate x", color: "#94a3b8" } },
                    y: { title: { display: true, text: "Elevation y = f(x)", color: "#94a3b8" } }
                },
                plugins: { legend: { position: "top", labels: { boxWidth: 12, padding: 8 } } }
            }
        });
    }

    initDerivativesChart() {
        const ctx = document.getElementById("derivativesChart");
        if (!ctx || !this.trackData) return;

        const slopeData = this.trackData.x.map((x, i) => ({ x, y: this.trackData.slope[i] }));
        const d2yData = this.trackData.x.map((x, i) => ({ x, y: this.trackData.second_derivative[i] }));
        const kappaData = this.trackData.x.map((x, i) => ({ x, y: this.trackData.curvature[i] }));

        this.derivativesChart = new Chart(ctx, {
            type: "line",
            data: {
                datasets: [
                    { label: "Slope f'(x) = 4x³ - 9x² + 2", data: slopeData, borderColor: "#3b82f6", borderWidth: 2, pointRadius: 0 },
                    { label: "2nd Deriv f''(x) = 12x² - 18x", data: d2yData, borderColor: "#8b5cf6", borderWidth: 2, pointRadius: 0 },
                    { label: "Curvature κ(x)", data: kappaData, borderColor: "#ef4444", borderWidth: 2, pointRadius: 0 },
                    { label: "Racer Current x", data: [{ x: 0.0, y: -10 }, { x: 0.0, y: 15 }], borderColor: "#e2e8f0", borderWidth: 1.5, borderDash: [4, 4], pointRadius: 0 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: { type: "linear", min: 0.0, max: 2.0, title: { display: true, text: "Coordinate x", color: "#94a3b8" } },
                    y: { title: { display: true, text: "Derivative Magnitude", color: "#94a3b8" } }
                },
                plugins: { legend: { position: "top", labels: { boxWidth: 12, padding: 8 } } }
            }
        });
    }

    initTelemetryChart() {
        const ctx = document.getElementById("telemetryChart");
        if (!ctx) return;

        this.telemetryChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: this.historyLabels,
                datasets: [
                    { label: "Speed (km/h)", data: this.speedHistory, borderColor: "#38bdf8", borderWidth: 2, pointRadius: 0, tension: 0.2, yAxisID: "y" },
                    { label: "G-Force (G)", data: this.gForceHistory, borderColor: "#f43f5e", borderWidth: 2, pointRadius: 0, tension: 0.2, yAxisID: "y1" },
                    { label: "Kinetic Energy (kJ)", data: this.kineticEnergyHistory, borderColor: "#22c55e", borderWidth: 1.5, borderDash: [3, 2], pointRadius: 0, yAxisID: "y" }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: { display: false },
                    y: { type: "linear", position: "left", title: { display: true, text: "Speed (km/h)", color: "#94a3b8" } },
                    y1: { type: "linear", position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "G-Force", color: "#f43f5e" } }
                },
                plugins: { legend: { position: "top", labels: { boxWidth: 10, padding: 6 } } }
            }
        });
    }

    initNumericalLabChart() {
        const ctx = document.getElementById("numericalLabChart");
        if (!ctx) return;

        this.numericalLabChart = new Chart(ctx, {
            type: "line",
            data: { datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 300 },
                plugins: { legend: { position: "top" } }
            }
        });

        this.showDifferentiationErrors();
    }

    updateSecondaryCharts(normX, speedKmh) {
        // Elevation chart
        if (this.elevationChart) {
            const yVal = this.physics.f(normX);
            this.elevationChart.data.datasets[1].data = [{ x: normX, y: yVal }];
            const deltaX = 0.25;
            const m = this.physics.fPrime(normX);
            this.elevationChart.data.datasets[2].data = [
                { x: normX - deltaX, y: yVal - m * deltaX },
                { x: normX + deltaX, y: yVal + m * deltaX }
            ];
            this.elevationChart.update("none");
        }

        // Derivatives chart
        if (this.derivativesChart) {
            this.derivativesChart.data.datasets[3].data = [
                { x: normX, y: -10 },
                { x: normX, y: 15 }
            ];
            this.derivativesChart.update("none");
        }

        // Rolling telemetry stream chart (throttle to 15 fps)
        this.frameCount++;
        if (this.frameCount % 4 === 0 && this.telemetryChart) {
            this.historyLabels.push("");
            this.speedHistory.push(speedKmh);
            this.gForceHistory.push(Number((Math.abs(speedKmh) / 80).toFixed(2)));
            this.kineticEnergyHistory.push(Number((0.5 * 750 * Math.pow(speedKmh / 3.6, 2) / 1000).toFixed(1)));

            if (this.historyLabels.length > this.maxHistory) {
                this.historyLabels.shift();
                this.speedHistory.shift();
                this.gForceHistory.shift();
                this.kineticEnergyHistory.shift();
            }
            this.telemetryChart.update("none");
        }
    }

    async showDifferentiationErrors(x = 1.0) {
        if (!this.numericalLabChart) return;
        const res = await API.getDifferentiation(x);
        if (!res || !res.steps) return;

        this.numericalLabChart.data = {
            datasets: [
                {
                    label: "Forward Difference Error O(h)",
                    data: res.steps.map(s => ({ x: s.h, y: s.forward_error })),
                    borderColor: "#f97316",
                    backgroundColor: "#f97316",
                    pointRadius: 4,
                    showLine: true
                },
                {
                    label: "Central Difference Error O(h²)",
                    data: res.steps.map(s => ({ x: s.h, y: s.central_error })),
                    borderColor: "#3b82f6",
                    backgroundColor: "#3b82f6",
                    pointRadius: 4,
                    showLine: true
                }
            ]
        };

        this.numericalLabChart.options.scales = {
            x: { type: "logarithmic", title: { display: true, text: "Step Size h (log scale)", color: "#94a3b8" } },
            y: { type: "logarithmic", title: { display: true, text: "Absolute Error (log scale)", color: "#94a3b8" } }
        };
        this.numericalLabChart.update();
    }

    async showRootFindingConvergence(method = "newton", x0 = 0.8) {
        if (!this.numericalLabChart) return;
        const res = await API.getRootFinding(method, { x0, a: 0.5, b: 1.5, x1: 1.2 });
        if (!res || !res.iterations) return;

        const stepsData = res.iterations.map(it => ({
            x: it.step,
            y: Math.abs(it.f_x_n !== undefined ? it.f_x_n : (it.f_midpoint !== undefined ? it.f_midpoint : it.f_curr))
        }));

        this.numericalLabChart.data = {
            datasets: [
                {
                    label: `${res.method} Convergence (|f(x)| vs Step)`,
                    data: stepsData,
                    borderColor: "#10b981",
                    backgroundColor: "rgba(16, 185, 129, 0.15)",
                    pointRadius: 5,
                    fill: true
                }
            ]
        };

        this.numericalLabChart.options.scales = {
            x: { type: "linear", title: { display: true, text: "Iteration Step", color: "#94a3b8" } },
            y: { type: "logarithmic", title: { display: true, text: "Residual |f(x_n)|", color: "#94a3b8" } }
        };
        this.numericalLabChart.update();
    }

    async showRacingModelKinematics(K = 20.0, T = 10.0) {
        if (!this.numericalLabChart) return;
        const res = await API.postSettings({ K, T });
        if (!res || !res.analysis || !res.analysis.numerical_arrays) return;

        const arrays = res.analysis.numerical_arrays;
        const timeData = arrays.racing_model_time_t;

        this.numericalLabChart.data = {
            datasets: [
                {
                    label: `Target Velocity v_model = ${K}·f(x) (m/s)`,
                    data: timeData.map((t, i) => ({ x: t, y: arrays.racing_model_velocity_v[i] })),
                    borderColor: "#38bdf8",
                    borderWidth: 2,
                    pointRadius: 0
                },
                {
                    label: `Target Accel a_model = (${K}/${T})·f'(x) (m/s²)`,
                    data: timeData.map((t, i) => ({ x: t, y: arrays.racing_model_acceleration_a[i] })),
                    borderColor: "#f43f5e",
                    borderWidth: 2,
                    pointRadius: 0
                },
                {
                    label: `Displacement s_model (m)`,
                    data: timeData.map((t, i) => ({ x: t, y: arrays.racing_model_displacement_s[i] })),
                    borderColor: "#10b981",
                    borderWidth: 2,
                    borderDash: [4, 4],
                    pointRadius: 0
                }
            ]
        };

        this.numericalLabChart.options.scales = {
            x: { type: "linear", title: { display: true, text: "Time t (seconds)", color: "#94a3b8" } },
            y: { type: "linear", title: { display: true, text: "Magnitude (v, a, s)", color: "#94a3b8" } }
        };
        this.numericalLabChart.update();
    }

    resizeAllCharts() {
        const charts = [
            this.velocityChart,
            this.accelerationChart,
            this.displacementChart,
            this.elevationChart,
            this.derivativesChart,
            this.telemetryChart,
            this.numericalLabChart
        ];
        charts.forEach(c => {
            if (c) {
                try { c.resize(); } catch (e) {}
            }
        });
    }
}

window.SimulationCharts = SimulationCharts;
