/**
 * FORMULA RACER - Professional Top-Down 2D Racing Game Engine
 * Course: Numerical and Symbolic Computing
 *
 * STRICT MATHEMATICAL REQUIREMENT:
 * Target velocity profile is governed by:
 * f(x) = x^4 - 3x^3 + 2x
 *
 * FEATURES:
 * 1. Realistic asphalt racing track with apex kerbs and borders
 * 2. Road lane markings (centerline dashes, edge lines, grid slots)
 * 3. High-detail player sports car with steerable wheels and headlights
 * 4. Checkered finish line with overhead start gantry
 * 5. Track boundaries & barrier collision with elastic rebound
 * 6. Roadside objects (grandstands, tire walls, trees, distance boards)
 * 7. Smooth car movement (acceleration, braking, steering, drift)
 * 8. High-precision race timer (MM:SS.mmm)
 * 9. Start, Pause, and Restart buttons & state machine
 * 10. Finish race results screen with mathematical accuracy rating
 */

class FormulaRacerGame {
    constructor() {
        this.canvas = document.getElementById("gameCanvas");
        this.ctx = this.canvas.getContext("2d");

        this.physics = new MathPhysicsEngine();
        this.controls = new ControlsHandler();
        this.charts = new SimulationCharts(this.physics);

        // Game State: 'ready', 'countdown', 'racing', 'paused', 'finished'
        this.state = "ready";
        this.countdownValue = 3;
        this.countdownTimer = 0;

        // Race Timer & Scoring
        this.raceTime = 0.0;
        this.bestTime = parseFloat(localStorage.getItem("formula_racer_best_time")) || null;
        this.speedMatchingHistory = []; // Tracks |actualSpeed - targetSpeed|
        this.topSpeedReached = 0.0;

        // Track Path Definition (Grand Prix Circuit Waypoints in World Pixels)
        this.initTrackGeometry();

        // Player Sports Car State (Starts on the Grid facing forward)
        const startNode = this.trackWaypoints[0];
        const nextNode = this.trackWaypoints[1];
        const initialAngle = Math.atan2(nextNode.y - startNode.y, nextNode.x - startNode.x);

        this.car = {
            x: startNode.x,
            y: startNode.y,
            angle: initialAngle,
            speed: 0.0,
            speedKmh: 0.0,
            vx: 0.0,
            vy: 0.0,
            steerAngle: 0.0,
            isDrifting: false,
            onGrass: false,
            collided: false,
            trackDistance: 0.0,
            normalizedX: 0.0,
            lapCompleted: false
        };

        // Camera Tracking
        this.camera = {
            x: this.car.x,
            y: this.car.y,
            zoom: 1.0,
            targetZoom: 1.0
        };

        // Skid marks & Particles
        this.skidmarks = [];
        this.particles = [];

        // Audio
        this.initAudio();

        // Resize Canvas
        this.handleResize();
        window.addEventListener("resize", () => this.handleResize());
    }

    async init() {
        // Initialize Chart.js
        await this.charts.init();

        // Connect UI Controls & Buttons
        this.bindUIControls();

        // Start requestAnimationFrame loop
        this.lastTime = performance.now();
        this.gameLoop();

        console.log("Formula Racer 2D Top-Down Racing Engine Initialized!");
    }

    handleResize() {
        const parent = this.canvas ? this.canvas.parentElement : null;
        const rect = parent ? parent.getBoundingClientRect() : { width: 1200, height: 800 };
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.ctx.scale(dpr, dpr);
        this.displayWidth = rect.width;
        this.displayHeight = rect.height;
    }

    // ==========================================
    // TRACK GEOMETRY & WAYPOINTS
    // ==========================================
    initTrackGeometry() {
        // Circuit dimensions in world pixels
        this.roadWidth = 140;       // Asphalt width
        this.vergeWidth = 35;       // Kerb / Grass verge width
        this.barrierDist = 105;     // Boundary barrier distance from centerline

        // Waypoints creating a technical Grand Prix Circuit
        this.trackWaypoints = [
            { x: 400,  y: 1200, label: "Start/Finish Straight" },
            { x: 900,  y: 1200, label: "Main Straight" },
            { x: 1400, y: 1200, label: "Turn 1 Braking Zone" },
            { x: 1900, y: 1100, label: "Turn 1 Fast Sweeper" },
            { x: 2300, y: 800,  label: "Turn 2 Sweeper Exit" },
            { x: 2200, y: 400,  label: "Chicane Entry" },
            { x: 1800, y: 350,  label: "Chicane Apex" },
            { x: 1400, y: 450,  label: "Back Straight Entry" },
            { x: 800,  y: 450,  label: "Back Straight DRS Zone" },
            { x: 300,  y: 550,  label: "Hairpin Approach" },
            { x: 150,  y: 850,  label: "Hairpin Apex" },
            { x: 250,  y: 1050, label: "Final Turn into Straight" }
        ];

        // Generate fine interpolated centerline samples for smooth collision & rendering
        this.trackCenterline = [];
        this.totalTrackLength = 0;
        const nWaypoints = this.trackWaypoints.length;

        for (let i = 0; i < nWaypoints; i++) {
            const p0 = this.trackWaypoints[(i - 1 + nWaypoints) % nWaypoints];
            const p1 = this.trackWaypoints[i];
            const p2 = this.trackWaypoints[(i + 1) % nWaypoints];
            const p3 = this.trackWaypoints[(i + 2) % nWaypoints];

            // Catmull-Rom spline interpolation (30 segments per waypoint)
            const segments = 30;
            for (let t = 0; t < segments; t++) {
                const u = t / segments;
                const u2 = u * u;
                const u3 = u2 * u;

                const x = 0.5 * (
                    (2 * p1.x) +
                    (-p0.x + p2.x) * u +
                    (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * u2 +
                    (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * u3
                );
                const y = 0.5 * (
                    (2 * p1.y) +
                    (-p0.y + p2.y) * u +
                    (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * u2 +
                    (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * u3
                );

                if (this.trackCenterline.length > 0) {
                    const prev = this.trackCenterline[this.trackCenterline.length - 1];
                    const dist = Math.hypot(x - prev.x, y - prev.y);
                    this.totalTrackLength += dist;
                }

                this.trackCenterline.push({
                    x,
                    y,
                    cumulativeDist: this.totalTrackLength
                });
            }
        }

        // Generate roadside scenery objects along the circuit
        this.roadsideObjects = [];
        this.initRoadsideObjects();
    }

    initRoadsideObjects() {
        this.roadsideObjects = [
            // Grandstands along the Main Straight
            { type: "grandstand", x: 650,  y: 1040, angle: 0, width: 260, length: 70 },
            { type: "grandstand", x: 1100, y: 1040, angle: 0, width: 280, length: 70 },

            // Distance marker boards before Turn 1
            { type: "marker", x: 1250, y: 1115, text: "200m" },
            { type: "marker", x: 1350, y: 1115, text: "100m" },
            { type: "marker", x: 1450, y: 1115, text: "50m" },

            // Distance marker boards before Hairpin
            { type: "marker", x: 450, y: 470, text: "150m" },
            { type: "marker", x: 350, y: 500, text: "50m" },

            // Trees and decorative greenery
            { type: "tree", x: 600,  y: 750,  radius: 28 },
            { type: "tree", x: 900,  y: 700,  radius: 35 },
            { type: "tree", x: 1150, y: 780,  radius: 32 },
            { type: "tree", x: 1450, y: 720,  radius: 38 },
            { type: "tree", x: 1700, y: 680,  radius: 30 },
            { type: "tree", x: 1950, y: 650,  radius: 34 },
            { type: "tree", x: 1300, y: 220,  radius: 36 },
            { type: "tree", x: 1600, y: 180,  radius: 40 },
            { type: "tree", x: 700,  y: 300,  radius: 32 },
            { type: "tree", x: 380,  y: 320,  radius: 34 },
            { type: "tree", x: 80,   y: 650,  radius: 30 },
            { type: "tree", x: 60,   y: 1150, radius: 36 },
            { type: "tree", x: 450,  y: 1380, radius: 34 },
            { type: "tree", x: 1000, y: 1380, radius: 38 },
            { type: "tree", x: 1500, y: 1380, radius: 35 },

            // Tire barriers on outer corners
            { type: "tire_wall", x: 2150, y: 1250, count: 6 },
            { type: "tire_wall", x: 2450, y: 800,  count: 8 },
            { type: "tire_wall", x: 2350, y: 350,  count: 7 },
            { type: "tire_wall", x: 100,  y: 850,  count: 9 }
        ];
    }

    // ==========================================
    // TRACK BOUNDARY & SURFACE CHECKER
    // ==========================================
    checkTrackSurface(x, y) {
        let minDist = Infinity;
        let nearestIdx = 0;

        // Find closest point on centerline
        for (let i = 0; i < this.trackCenterline.length; i += 2) {
            const pt = this.trackCenterline[i];
            const d = Math.hypot(x - pt.x, y - pt.y);
            if (d < minDist) {
                minDist = d;
                nearestIdx = i;
            }
        }

        const centerPt = this.trackCenterline[nearestIdx];
        const halfRoad = this.roadWidth / 2.0;
        const barrierDist = this.barrierDist;

        const onRoad = minDist <= halfRoad;
        const onGrass = minDist > halfRoad && minDist <= barrierDist;
        const hitBarrier = minDist > barrierDist;

        let pushback = null;
        let normal = null;

        if (hitBarrier && centerPt) {
            // Compute normal pointing from centerPt to (x, y)
            const dx = x - centerPt.x;
            const dy = y - centerPt.y;
            const len = Math.hypot(dx, dy) || 1.0;
            normal = { x: dx / len, y: dy / len };

            // Push car back inside the barrier boundary
            const penetration = minDist - barrierDist;
            pushback = {
                x: -normal.x * (penetration + 2.0),
                y: -normal.y * (penetration + 2.0)
            };
        }

        return {
            onRoad,
            onGrass,
            hitBarrier,
            minDist,
            nearestIdx,
            nearestPoint: centerPt,
            normal,
            pushback
        };
    }

    // ==========================================
    // GAME STATE MACHINE (START, PAUSE, RESTART)
    // ==========================================
    startRace() {
        if (this.state === "racing") return;
        this.state = "countdown";
        this.countdownValue = 3;
        this.countdownTimer = 1.0; // 1 second per count
        this.startAudio();
    }

    togglePause() {
        if (this.state === "racing") {
            this.state = "paused";
            document.getElementById("pauseOverlay")?.classList.remove("hidden");
            if (this.charts) this.charts.setPaused(true);
        } else if (this.state === "paused") {
            this.state = "racing";
            document.getElementById("pauseOverlay")?.classList.add("hidden");
            if (this.charts) this.charts.setPaused(false);
        }
    }

    restartRace() {
        this.state = "ready";
        this.raceTime = 0.0;
        this.speedMatchingHistory = [];
        this.skidmarks = [];
        this.particles = [];

        // Reset car to starting grid
        const startNode = this.trackWaypoints[0];
        const nextNode = this.trackWaypoints[1];
        const initialAngle = Math.atan2(nextNode.y - startNode.y, nextNode.x - startNode.x);

        this.car.x = startNode.x;
        this.car.y = startNode.y;
        this.car.angle = initialAngle;
        this.car.speed = 0.0;
        this.car.speedKmh = 0.0;
        this.car.vx = 0.0;
        this.car.vy = 0.0;
        this.car.trackDistance = 0.0;
        this.car.normalizedX = 0.0;
        this.car.lapCompleted = false;

        document.getElementById("pauseOverlay")?.classList.add("hidden");
        document.getElementById("finishOverlay")?.classList.add("hidden");

        const startBtn = document.getElementById("btnStartRace");
        if (startBtn) startBtn.innerText = "▶ START TIME TRIAL";

        // Reset the 3 Live Mathematical Graphs
        if (this.charts) {
            this.charts.reset();
        }
    }

    finishRace() {
        this.state = "finished";
        this.car.speed *= 0.3; // Gentle coast down

        // Update Best Time
        let isNewRecord = false;
        if (!this.bestTime || this.raceTime < this.bestTime) {
            this.bestTime = this.raceTime;
            localStorage.setItem("formula_racer_best_time", this.bestTime.toString());
            isNewRecord = true;
        }

        // Calculate Mathematical Target Accuracy
        let avgDelta = 0.0;
        if (this.speedMatchingHistory.length > 0) {
            const sum = this.speedMatchingHistory.reduce((a, b) => a + b, 0);
            avgDelta = sum / this.speedMatchingHistory.length;
        }
        // Accuracy percentage: 100% - (avgDelta / 120 * 100) clamped to [0, 100]
        const accuracyPct = Math.max(0.0, Math.min(100.0, 100.0 - (avgDelta / 80.0) * 100.0));

        // Rating
        let rating = "🥉 BRONZE";
        if (accuracyPct >= 90.0) rating = "🏆 GOLD (Formula Master)";
        else if (accuracyPct >= 78.0) rating = "🥈 SILVER (Precision Driver)";

        // Populate Finish Screen
        document.getElementById("finishTime").innerText = this.formatTime(this.raceTime);
        document.getElementById("finishBestTime").innerText = this.formatTime(this.bestTime);
        document.getElementById("finishAccuracy").innerText = `${accuracyPct.toFixed(1)}%`;
        document.getElementById("finishTopSpeed").innerText = `${this.topSpeedReached.toFixed(0)} km/h`;
        document.getElementById("finishRating").innerText = rating;

        // Synchronize Dedicated Results View
        if (document.getElementById("resFinalTime")) document.getElementById("resFinalTime").innerText = this.formatTime(this.raceTime);
        if (document.getElementById("resBestTime")) document.getElementById("resBestTime").innerText = this.formatTime(this.bestTime);
        if (document.getElementById("resAccuracyPct")) document.getElementById("resAccuracyPct").innerText = `${accuracyPct.toFixed(1)}%`;
        if (document.getElementById("resTopSpeed")) document.getElementById("resTopSpeed").innerText = `${this.topSpeedReached.toFixed(0)} km/h`;
        if (document.getElementById("resRatingBadge")) document.getElementById("resRatingBadge").innerText = rating;

        const recordBadge = document.getElementById("finishRecordBadge");
        if (recordBadge) recordBadge.style.display = isNewRecord ? "inline-block" : "none";

        document.getElementById("finishOverlay")?.classList.remove("hidden");
    }

    formatTime(seconds) {
        if (!seconds || seconds <= 0) return "--:--.---";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        const ms = Math.floor((seconds % 1) * 1000);
        return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}.${String(ms).padStart(3, '0')}`;
    }

    // ==========================================
    // PROCEDURAL ENGINE SOUND (WEB AUDIO API)
    // ==========================================
    initAudio() {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioCtx = new AudioContext();
            this.oscillator = null;
            this.gainNode = null;
        } catch (e) {
            this.audioCtx = null;
        }
    }

    startAudio() {
        if (!this.audioCtx || this.oscillator) return;
        if (this.audioCtx.state === "suspended") {
            this.audioCtx.resume();
        }
        this.oscillator = this.audioCtx.createOscillator();
        this.gainNode = this.audioCtx.createGain();
        this.oscillator.type = "sawtooth";
        this.oscillator.frequency.value = 70;
        this.gainNode.gain.value = 0.025;
        this.oscillator.connect(this.gainNode);
        this.gainNode.connect(this.audioCtx.destination);
        this.oscillator.start();
    }

    updateAudio(speedKmh, throttle) {
        if (!this.oscillator || !this.gainNode) return;
        const rpmFreq = 65 + (speedKmh * 2.8) + (throttle * 35);
        this.oscillator.frequency.setTargetAtTime(Math.min(rpmFreq, 580), this.audioCtx.currentTime, 0.05);
        const targetGain = throttle > 0 ? 0.035 : 0.015;
        this.gainNode.gain.setTargetAtTime(targetGain, this.audioCtx.currentTime, 0.05);
    }

    // ==========================================
    // MAIN 60 FPS GAME LOOP
    // ==========================================
    gameLoop() {
        const now = performance.now();
        const dt = Math.min((now - this.lastTime) / 1000.0, 0.033);
        this.lastTime = now;

        // 1. Process Input
        const input = this.controls.getState();

        if (input.reset) {
            this.restartRace();
        }
        if (input.pause) {
            this.togglePause();
        }

        // 2. State Logic
        if (this.state === "countdown") {
            this.countdownTimer -= dt;
            if (this.countdownTimer <= 0) {
                this.countdownValue--;
                this.countdownTimer = 1.0;
                if (this.countdownValue <= 0) {
                    this.state = "racing";
                }
            }
        } else if (this.state === "racing") {
            this.raceTime += dt;

            // Physics step
            const updated = this.physics.step2D(
                this.car,
                input,
                dt,
                (x, y) => this.checkTrackSurface(x, y)
            );

            // Update car properties
            this.car.x = updated.x;
            this.car.y = updated.y;
            this.car.angle = updated.angle;
            this.car.speed = updated.speed;
            this.car.speedKmh = updated.speedKmh;
            this.car.vx = updated.vx;
            this.car.vy = updated.vy;
            this.car.steerAngle = updated.steerAngle;
            this.car.isDrifting = updated.isDrifting;
            this.car.onGrass = updated.onGrass;

            if (this.car.speedKmh > this.topSpeedReached) {
                this.topSpeedReached = this.car.speedKmh;
            }

            // Update Track Progress & Normalized Coordinate x in [0, 2]
            const surface = this.checkTrackSurface(this.car.x, this.car.y);
            const nearestCenter = surface.nearestPoint;
            if (nearestCenter) {
                this.car.trackDistance = nearestCenter.cumulativeDist;
                this.car.normalizedX = (this.car.trackDistance / this.totalTrackLength) * 2.0;

                // Check finish line crossing (near end of track)
                if (this.car.trackDistance > this.totalTrackLength * 0.94 && !this.car.lapCompleted) {
                    this.car.lapCompleted = true;
                    this.finishRace();
                }
            }

            // Target mathematical velocity from f(x) = x^4 - 3x^3 + 2x
            const targetKmh = this.physics.getTargetVelocityKmh(this.car.normalizedX);
            const deltaSpeed = Math.abs(this.car.speedKmh - targetKmh);
            this.speedMatchingHistory.push(deltaSpeed);

            // Audio & Particles
            this.updateAudio(this.car.speedKmh, input.throttle);
            this.updateParticlesAndSkidmarks(input, updated);
        }

        // 3. Camera Smooth Following
        this.updateCamera();

        // 4. Render 2D Top-Down Scene
        this.render();

        // 5. Update HUD and Charts
        this.updateHUD();

        // 6. Request Next Frame
        requestAnimationFrame(() => this.gameLoop());
    }

    // ==========================================
    // CAMERA SMOOTH FOLLOW
    // ==========================================
    updateCamera() {
        const targetX = this.car.x;
        const targetY = this.car.y;
        this.camera.x += (targetX - this.camera.x) * 0.12;
        this.camera.y += (targetY - this.camera.y) * 0.12;

        // Dynamic speed zoom out
        const speedRatio = Math.min(this.car.speedKmh / 220.0, 1.0);
        const targetZoom = 1.05 - speedRatio * 0.22;
        this.camera.zoom += (targetZoom - this.camera.zoom) * 0.08;
    }

    worldToScreen(x, y) {
        const scale = this.camera.zoom;
        const screenX = this.displayWidth / 2 + (x - this.camera.x) * scale;
        const screenY = this.displayHeight / 2 + (y - this.camera.y) * scale;
        return { x: screenX, y: screenY };
    }

    // ==========================================
    // SKIDMARKS & PARTICLES
    // ==========================================
    updateParticlesAndSkidmarks(input, updated) {
        // Lay tire skidmarks when drifting or emergency braking
        if (this.car.isDrifting && Math.abs(this.car.speed) > 4.0) {
            const rearOffsetX = -20;
            const rearWidth = 14;
            const cos = Math.cos(this.car.angle);
            const sin = Math.sin(this.car.angle);

            // Left and right rear tire positions
            const t1 = {
                x: this.car.x + cos * rearOffsetX - sin * rearWidth,
                y: this.car.y + sin * rearOffsetX + cos * rearWidth
            };
            const t2 = {
                x: this.car.x + cos * rearOffsetX + sin * rearWidth,
                y: this.car.y + sin * rearOffsetX - cos * rearWidth
            };

            this.skidmarks.push({ x: t1.x, y: t1.y, alpha: 0.65 });
            this.skidmarks.push({ x: t2.x, y: t2.y, alpha: 0.65 });

            if (this.skidmarks.length > 400) {
                this.skidmarks.splice(0, 20);
            }

            // Tire smoke particles
            for (let i = 0; i < 2; i++) {
                this.particles.push({
                    x: (t1.x + t2.x) / 2 + (Math.random() - 0.5) * 8,
                    y: (t1.y + t2.y) / 2 + (Math.random() - 0.5) * 8,
                    vx: (Math.random() - 0.5) * 15,
                    vy: (Math.random() - 0.5) * 15,
                    color: "rgba(241, 245, 249, 0.45)",
                    size: Math.random() * 8 + 4,
                    life: 1.0,
                    decay: 0.05
                });
            }
        }

        // Exhaust flame particles when boosting
        if (input.turbo && Math.abs(this.car.speed) > 2.0) {
            const cos = Math.cos(this.car.angle);
            const sin = Math.sin(this.car.angle);
            this.particles.push({
                x: this.car.x - cos * 26,
                y: this.car.y - sin * 26,
                vx: -cos * (Math.random() * 30 + 20) + (Math.random() - 0.5) * 10,
                vy: -sin * (Math.random() * 30 + 20) + (Math.random() - 0.5) * 10,
                color: Math.random() > 0.4 ? "#f97316" : "#38bdf8",
                size: Math.random() * 6 + 3,
                life: 1.0,
                decay: 0.1
            });
        }

        // Barrier collision sparks
        if (updated.collided) {
            for (let i = 0; i < 5; i++) {
                this.particles.push({
                    x: this.car.x,
                    y: this.car.y,
                    vx: (Math.random() - 0.5) * 60,
                    vy: (Math.random() - 0.5) * 60,
                    color: "#fef08a",
                    size: 3,
                    life: 1.0,
                    decay: 0.12
                });
            }
        }

        // Update particle lifetimes
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.vx * 0.016;
            p.y += p.vy * 0.016;
            p.life -= p.decay;
            if (p.life <= 0) this.particles.splice(i, 1);
        }
    }

    // ==========================================
    // TOP-DOWN RENDERING PIPELINE
    // ==========================================
    render() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.displayWidth, this.displayHeight);

        // 1. Draw Infield & Outfield Grass Terrain
        this.renderGrassTerrain(ctx);

        // 2. Draw Roadside Kerbs & Run-off Areas
        this.renderKerbsAndVerges(ctx);

        // 3. Draw Asphalt Track Body
        this.renderAsphaltTrack(ctx);

        // 4. Draw Road Lane Markings (Center dashes & Edges)
        this.renderLaneMarkings(ctx);

        // 5. Draw Start & Finish Line Grid
        this.renderStartFinishLine(ctx);

        // 6. Draw Tire Skidmarks
        this.renderSkidmarks(ctx);

        // 7. Draw Roadside Objects (Grandstands, Barriers, Trees)
        this.renderRoadsideObjects(ctx);

        // 8. Draw Particles (Smoke & Sparks)
        this.renderParticles(ctx);

        // 9. Draw Player Sports Car
        this.renderPlayerCar(ctx);

        // 10. Draw Countdown Overlay if active
        this.renderCountdownOverlay(ctx);
    }

    renderGrassTerrain(ctx) {
        ctx.fillStyle = "#152e1d"; // Deep grass green
        ctx.fillRect(0, 0, this.displayWidth, this.displayHeight);

        // Subtle grid pattern for sense of motion
        ctx.strokeStyle = "rgba(22, 101, 52, 0.25)";
        ctx.lineWidth = 1;
        const spacing = 100 * this.camera.zoom;
        const offsetX = (this.displayWidth / 2 - this.camera.x * this.camera.zoom) % spacing;
        const offsetY = (this.displayHeight / 2 - this.camera.y * this.camera.zoom) % spacing;

        ctx.beginPath();
        for (let x = offsetX; x < this.displayWidth; x += spacing) {
            ctx.moveTo(x, 0);
            ctx.lineTo(x, this.displayHeight);
        }
        for (let y = offsetY; y < this.displayHeight; y += spacing) {
            ctx.moveTo(0, y);
            ctx.lineTo(this.displayWidth, y);
        }
        ctx.stroke();
    }

    renderKerbsAndVerges(ctx) {
        ctx.save();
        const zoom = this.camera.zoom;

        // Outer gravel / grass verge border
        ctx.beginPath();
        for (let i = 0; i < this.trackCenterline.length; i++) {
            const pt = this.worldToScreen(this.trackCenterline[i].x, this.trackCenterline[i].y);
            if (i === 0) ctx.moveTo(pt.x, pt.y);
            else ctx.lineTo(pt.x, pt.y);
        }
        ctx.closePath();
        ctx.strokeStyle = "#854d0e"; // Gravel brown verge
        ctx.lineWidth = (this.roadWidth + this.vergeWidth * 2) * zoom;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.stroke();

        // Red and White Alternating Curbs along the edges
        ctx.strokeStyle = "#dc2626"; // Red kerb
        ctx.lineWidth = (this.roadWidth + 18) * zoom;
        ctx.setLineDash([16 * zoom, 16 * zoom]);
        ctx.stroke();

        ctx.strokeStyle = "#f8fafc"; // White kerb
        ctx.lineDashOffset = 16 * zoom;
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.restore();
    }

    renderAsphaltTrack(ctx) {
        ctx.save();
        const zoom = this.camera.zoom;

        // Dark realistic asphalt surface
        ctx.beginPath();
        for (let i = 0; i < this.trackCenterline.length; i++) {
            const pt = this.worldToScreen(this.trackCenterline[i].x, this.trackCenterline[i].y);
            if (i === 0) ctx.moveTo(pt.x, pt.y);
            else ctx.lineTo(pt.x, pt.y);
        }
        ctx.closePath();

        ctx.strokeStyle = "#1e222a"; // Asphalt grey
        ctx.lineWidth = this.roadWidth * zoom;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.stroke();

        ctx.restore();
    }

    renderLaneMarkings(ctx) {
        ctx.save();
        const zoom = this.camera.zoom;

        // Solid White Outer Track Boundaries
        ctx.beginPath();
        for (let i = 0; i < this.trackCenterline.length; i++) {
            const pt = this.worldToScreen(this.trackCenterline[i].x, this.trackCenterline[i].y);
            if (i === 0) ctx.moveTo(pt.x, pt.y);
            else ctx.lineTo(pt.x, pt.y);
        }
        ctx.closePath();

        // White edge boundary line left and right
        ctx.strokeStyle = "rgba(255, 255, 255, 0.9)";
        ctx.lineWidth = (this.roadWidth - 8) * zoom;
        ctx.stroke();

        // Re-cover center to leave 4px white edge lines
        ctx.strokeStyle = "#1e222a";
        ctx.lineWidth = (this.roadWidth - 16) * zoom;
        ctx.stroke();

        // Dashed Centerline Lane Markings
        ctx.beginPath();
        for (let i = 0; i < this.trackCenterline.length; i++) {
            const pt = this.worldToScreen(this.trackCenterline[i].x, this.trackCenterline[i].y);
            if (i === 0) ctx.moveTo(pt.x, pt.y);
            else ctx.lineTo(pt.x, pt.y);
        }
        ctx.closePath();

        ctx.strokeStyle = "rgba(250, 204, 21, 0.75)"; // Racing yellow dashes
        ctx.lineWidth = 3 * zoom;
        ctx.setLineDash([22 * zoom, 18 * zoom]);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.restore();
    }

    renderStartFinishLine(ctx) {
        ctx.save();
        const p1 = this.trackWaypoints[0];
        const p2 = this.trackWaypoints[1];
        const angle = Math.atan2(p2.y - p1.y, p2.x - p1.x);

        const screenPt = this.worldToScreen(p1.x, p1.y);
        ctx.translate(screenPt.x, screenPt.y);
        ctx.rotate(angle);

        const zoom = this.camera.zoom;
        const halfW = (this.roadWidth / 2) * zoom;
        const boxSize = 8 * zoom;

        // Checkered Black and White Pattern across the road
        for (let y = -halfW; y < halfW; y += boxSize) {
            for (let col = 0; col < 2; col++) {
                const isBlack = (Math.floor(y / boxSize) + col) % 2 === 0;
                ctx.fillStyle = isBlack ? "#0f172a" : "#ffffff";
                ctx.fillRect(col * boxSize - boxSize, y, boxSize, boxSize);
            }
        }

        // Start Gantry Arch
        ctx.strokeStyle = "#38bdf8";
        ctx.lineWidth = 4 * zoom;
        ctx.beginPath();
        ctx.moveTo(-15 * zoom, -halfW - 12 * zoom);
        ctx.lineTo(15 * zoom, -halfW - 12 * zoom);
        ctx.lineTo(15 * zoom, halfW + 12 * zoom);
        ctx.lineTo(-15 * zoom, halfW + 12 * zoom);
        ctx.stroke();

        ctx.fillStyle = "#38bdf8";
        ctx.font = `bold ${10 * zoom}px 'JetBrains Mono', monospace`;
        ctx.textAlign = "center";
        ctx.fillText("FINISH LINE / START", 0, -halfW - 16 * zoom);

        ctx.restore();
    }

    renderSkidmarks(ctx) {
        ctx.save();
        const zoom = this.camera.zoom;
        ctx.fillStyle = "rgba(15, 23, 42, 0.35)";

        this.skidmarks.forEach(sm => {
            const pt = this.worldToScreen(sm.x, sm.y);
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, 4 * zoom, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.restore();
    }

    renderRoadsideObjects(ctx) {
        const zoom = this.camera.zoom;

        this.roadsideObjects.forEach(obj => {
            const pt = this.worldToScreen(obj.x, obj.y);

            if (obj.type === "grandstand") {
                ctx.save();
                ctx.translate(pt.x, pt.y);
                ctx.rotate(obj.angle);
                // Grandstand building base
                ctx.fillStyle = "#334155";
                ctx.fillRect(-obj.width * zoom / 2, -obj.length * zoom / 2, obj.width * zoom, obj.length * zoom);
                // Roof canopy
                ctx.fillStyle = "#0284c7";
                ctx.fillRect(-obj.width * zoom / 2, -obj.length * zoom / 2, obj.width * zoom, 18 * zoom);
                // Spectator crowd dots
                for (let i = -obj.width * zoom / 2 + 10; i < obj.width * zoom / 2 - 10; i += 12 * zoom) {
                    for (let j = 5 * zoom; j < obj.length * zoom / 2 - 5; j += 10 * zoom) {
                        ctx.fillStyle = ["#f87171", "#fbbf24", "#34d399", "#60a5fa"][Math.floor((i + j) % 4)];
                        ctx.fillRect(i, j, 4 * zoom, 4 * zoom);
                    }
                }
                ctx.restore();
            } else if (obj.type === "tree") {
                // Tree shadow
                ctx.fillStyle = "rgba(0, 0, 0, 0.35)";
                ctx.beginPath();
                ctx.arc(pt.x + 8 * zoom, pt.y + 8 * zoom, obj.radius * zoom, 0, Math.PI * 2);
                ctx.fill();
                // Tree crown
                ctx.fillStyle = "#166534";
                ctx.beginPath();
                ctx.arc(pt.x, pt.y, obj.radius * zoom, 0, Math.PI * 2);
                ctx.fill();
                // Tree highlight
                ctx.fillStyle = "#22c55e";
                ctx.beginPath();
                ctx.arc(pt.x - 4 * zoom, pt.y - 4 * zoom, obj.radius * zoom * 0.55, 0, Math.PI * 2);
                ctx.fill();
            } else if (obj.type === "marker") {
                ctx.fillStyle = "#f8fafc";
                ctx.fillRect(pt.x - 18 * zoom, pt.y - 10 * zoom, 36 * zoom, 20 * zoom);
                ctx.fillStyle = "#0f172a";
                ctx.font = `bold ${9 * zoom}px 'JetBrains Mono', monospace`;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(obj.text, pt.x, pt.y);
            } else if (obj.type === "tire_wall") {
                // Stack of tires
                for (let k = 0; k < obj.count; k++) {
                    const tx = pt.x + (k - obj.count / 2) * 14 * zoom;
                    ctx.fillStyle = k % 2 === 0 ? "#ef4444" : "#ffffff";
                    ctx.beginPath();
                    ctx.arc(tx, pt.y, 6 * zoom, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = "#0f172a";
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        });
    }

    renderParticles(ctx) {
        const zoom = this.camera.zoom;
        this.particles.forEach(p => {
            const pt = this.worldToScreen(p.x, p.y);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.life;
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, p.size * zoom, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.globalAlpha = 1.0;
    }

    renderPlayerCar(ctx) {
        ctx.save();
        const pt = this.worldToScreen(this.car.x, this.car.y);
        ctx.translate(pt.x, pt.y);
        ctx.rotate(this.car.angle);

        const zoom = this.camera.zoom;
        const scale = 1.0 * zoom;

        // 1. Dual Headlight Beams casting light ahead
        ctx.save();
        const grad = ctx.createRadialGradient(28 * scale, 0, 10 * scale, 120 * scale, 0, 140 * scale);
        grad.addColorStop(0, "rgba(255, 255, 255, 0.35)");
        grad.addColorStop(1, "rgba(255, 255, 255, 0.0)");
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.moveTo(25 * scale, -10 * scale);
        ctx.lineTo(160 * scale, -60 * scale);
        ctx.lineTo(160 * scale, 60 * scale);
        ctx.lineTo(25 * scale, 10 * scale);
        ctx.closePath();
        ctx.fill();
        ctx.restore();

        // 2. Soft Car Shadow
        ctx.fillStyle = "rgba(0, 0, 0, 0.45)";
        ctx.beginPath();
        ctx.roundRect(-24 * scale + 4 * scale, -13 * scale + 4 * scale, 48 * scale, 26 * scale, 8 * scale);
        ctx.fill();

        // 3. Wheels (Front wheels rotate with steerAngle)
        const renderWheel = (wx, wy, steer) => {
            ctx.save();
            ctx.translate(wx * scale, wy * scale);
            if (steer) ctx.rotate(this.car.steerAngle);
            ctx.fillStyle = "#18181b"; // Rubber black
            ctx.beginPath();
            ctx.roundRect(-7 * scale, -3.5 * scale, 14 * scale, 7 * scale, 2 * scale);
            ctx.fill();
            // Yellow racing rim
            ctx.fillStyle = "#eab308";
            ctx.fillRect(-3 * scale, -1 * scale, 6 * scale, 2 * scale);
            ctx.restore();
        };

        // Front left & right wheels (steerable)
        renderWheel(15, -13, true);
        renderWheel(15, 13, true);
        // Rear left & right wheels (fixed)
        renderWheel(-16, -13, false);
        renderWheel(-16, 13, false);

        // 4. Aerodynamic Sports Car Chassis
        ctx.fillStyle = "#ef4444"; // Formula Crimson Red
        ctx.beginPath();
        ctx.moveTo(24 * scale, 0);
        ctx.lineTo(18 * scale, -11 * scale);
        ctx.lineTo(-18 * scale, -11 * scale);
        ctx.lineTo(-24 * scale, -8 * scale);
        ctx.lineTo(-24 * scale, 8 * scale);
        ctx.lineTo(-18 * scale, 11 * scale);
        ctx.lineTo(18 * scale, 11 * scale);
        ctx.closePath();
        ctx.fill();

        // White racing center livery stripe
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(-22 * scale, -3 * scale, 44 * scale, 6 * scale);

        // Carbon Front Splitter
        ctx.fillStyle = "#0f172a";
        ctx.fillRect(20 * scale, -11 * scale, 5 * scale, 22 * scale);

        // Cockpit Tinted Canopy
        ctx.fillStyle = "#090d16";
        ctx.beginPath();
        ctx.roundRect(-6 * scale, -7 * scale, 18 * scale, 14 * scale, 4 * scale);
        ctx.fill();
        // Glass cyan reflection
        ctx.fillStyle = "#38bdf8";
        ctx.fillRect(-2 * scale, -5 * scale, 10 * scale, 3 * scale);

        // Rear Wing / Spoiler
        ctx.fillStyle = "#0f172a";
        ctx.fillRect(-26 * scale, -13 * scale, 4 * scale, 26 * scale);

        // LED Headlights
        ctx.fillStyle = "#fef08a";
        ctx.fillRect(22 * scale, -9 * scale, 3 * scale, 4 * scale);
        ctx.fillRect(22 * scale, 5 * scale, 3 * scale, 4 * scale);

        // LED Brake Lights (Glow bright when braking)
        const isBraking = this.controls.keys.down || this.controls.keys.space;
        ctx.fillStyle = isBraking ? "#ff0000" : "#7f1d1d";
        ctx.shadowColor = isBraking ? "#ef4444" : "transparent";
        ctx.shadowBlur = isBraking ? 10 : 0;
        ctx.fillRect(-24 * scale, -8 * scale, 2 * scale, 4 * scale);
        ctx.fillRect(-24 * scale, 4 * scale, 2 * scale, 4 * scale);
        ctx.shadowBlur = 0;

        ctx.restore();
    }

    renderCountdownOverlay(ctx) {
        if (this.state !== "countdown") return;
        ctx.save();
        ctx.fillStyle = "rgba(15, 23, 42, 0.75)";
        ctx.fillRect(0, 0, this.displayWidth, this.displayHeight);

        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 72px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        const text = this.countdownValue > 0 ? this.countdownValue : "GO!";
        ctx.fillStyle = this.countdownValue > 0 ? "#f59e0b" : "#10b981";
        ctx.fillText(text, this.displayWidth / 2, this.displayHeight / 2);

        ctx.restore();
    }

    // ==========================================
    // HUD & TELEMETRY STREAM READOUT
    // ==========================================
    updateHUD() {
        const speed = this.car.speedKmh;
        const normX = this.car.normalizedX;

        // Mathematical Target Speed calculated strictly from f(x) = x^4 - 3x^3 + 2x
        const targetSpeed = this.physics.getTargetVelocityKmh(normX);
        const fx = this.physics.f(normX);
        const fPrime = this.physics.fPrime(normX);
        const targetAccel = this.physics.getTargetAcceleration(normX);

        // 1. Digital Speedometers (Actual vs Target)
        const speedEl = document.getElementById("hudSpeed");
        if (speedEl) speedEl.innerText = Math.round(speed);

        const targetSpeedEl = document.getElementById("hudTargetSpeed");
        if (targetSpeedEl) targetSpeedEl.innerText = Math.round(targetSpeed);

        const miniSpeed = document.getElementById("hudSpeedMini");
        if (miniSpeed) miniSpeed.innerText = Math.round(speed);
        const miniTarget = document.getElementById("hudTargetSpeedMini");
        if (miniTarget) miniTarget.innerText = Math.round(targetSpeed);

        const speedKmhVal = document.getElementById("hudSpeedValKmh");
        if (speedKmhVal) speedKmhVal.innerText = Math.round(speed);
        const speedMpsVal = document.getElementById("hudSpeedValMps");
        if (speedMpsVal) speedMpsVal.innerText = (speed / 3.6).toFixed(1);
        const targetMpsVal = document.getElementById("hudTargetSpeedMps");
        if (targetMpsVal) targetMpsVal.innerText = (targetSpeed / 3.6).toFixed(1);

        // Speedometer Arc & Needle SVG Visualizations
        const needle = document.getElementById("speedoNeedle");
        if (needle) {
            const angle = -90 + (Math.min(speed, 220) / 220) * 180;
            needle.setAttribute("transform", `rotate(${angle.toFixed(1)} 100 105)`);
        }
        const actualArc = document.getElementById("speedoActualArc");
        if (actualArc) {
            const offset = 235.6 * (1 - Math.min(speed, 220) / 220);
            actualArc.style.strokeDashoffset = offset.toFixed(1);
        }
        const targetArc = document.getElementById("speedoTargetArc");
        if (targetArc) {
            const tOffset = 235.6 * (1 - Math.min(targetSpeed, 220) / 220);
            targetArc.style.strokeDashoffset = tOffset.toFixed(1);
        }

        // Speed Delta Indicator
        const deltaSpeed = speed - targetSpeed;
        const deltaIndicator = document.getElementById("hudSpeedDelta");
        if (deltaIndicator) {
            if (Math.abs(deltaSpeed) <= 8.0) {
                deltaIndicator.innerText = "✓ ON TARGET";
                deltaIndicator.className = "status-banner status-normal";
            } else if (deltaSpeed > 8.0) {
                deltaIndicator.innerText = `▲ +${Math.round(deltaSpeed)} KM/H (TOO FAST)`;
                deltaIndicator.className = "status-banner status-danger";
            } else {
                deltaIndicator.innerText = `▼ ${Math.round(deltaSpeed)} KM/H (TOO SLOW)`;
                deltaIndicator.className = "status-banner status-warning";
            }
        }

        // 2. Race Timer
        const timerEl = document.getElementById("hudTimer");
        if (timerEl) timerEl.innerText = this.formatTime(this.raceTime);

        // Best Lap
        const bestEl = document.getElementById("hudBestLap");
        if (bestEl) bestEl.innerText = this.formatTime(this.bestTime);

        // 3. Track Progression & Formula Values
        const progressPct = Math.min(100, (this.car.trackDistance / this.totalTrackLength) * 100);
        const progBar = document.getElementById("hudProgressBar");
        if (progBar) progBar.style.width = `${progressPct.toFixed(1)}%`;
        const progText = document.getElementById("hudProgressText");
        if (progText) progText.innerText = `${Math.round(progressPct)}%`;

        const gearEl = document.getElementById("hudGear");
        if (gearEl) {
            const gear = speed < 2 ? "N" : speed < 55 ? "1" : speed < 105 ? "2" : speed < 155 ? "3" : speed < 205 ? "4" : "5";
            gearEl.innerText = gear;
        }

        const normXEl = document.getElementById("hudNormX");
        if (normXEl) normXEl.innerText = normX.toFixed(3);

        const fxEl = document.getElementById("hudFx");
        if (fxEl) fxEl.innerText = fx.toFixed(3);

        const fPrimeEl = document.getElementById("hudFPrime");
        if (fPrimeEl) fPrimeEl.innerText = fPrime.toFixed(3);

        const targetAccelEl = document.getElementById("hudTargetAccel");
        if (targetAccelEl) targetAccelEl.innerText = `${targetAccel.toFixed(2)} m/s²`;

        const hudX = document.getElementById("hudX");
        if (hudX) hudX.innerText = `${this.car.x.toFixed(1)} px`;

        const hudY = document.getElementById("hudY");
        if (hudY) hudY.innerText = `${this.car.y.toFixed(1)} px`;

        // Surface alert
        const surfaceAlert = document.getElementById("hudSurfaceStatus");
        if (surfaceAlert) {
            if (this.car.onGrass) {
                surfaceAlert.innerText = "⚠ OFF-TRACK (GRASS SLOWDOWN)";
                surfaceAlert.style.color = "#f59e0b";
            } else if (this.car.isDrifting) {
                surfaceAlert.innerText = "⚡ LATERAL SLIP (DRIFTING)";
                surfaceAlert.style.color = "#38bdf8";
            } else {
                surfaceAlert.innerText = "ASPHALT GRIP OPTIMAL";
                surfaceAlert.style.color = "#10b981";
            }
        }

        // 4. Synchronize 3 Live Mathematical Graphs (Chart.js)
        if (this.charts) {
            this.charts.updateRealtime(this.raceTime, this.car.speedKmh, this.car.speed, this.state);
        }
    }

    // ==========================================
    // UI BUTTONS BINDINGS
    // ==========================================
    bindUIControls() {
        const btnStart = document.getElementById("btnStartRace");
        const btnPause = document.getElementById("btnPauseRace");
        const btnRestart = document.getElementById("btnRestartRace");

        if (btnStart) btnStart.addEventListener("click", () => this.startRace());
        if (btnPause) btnPause.addEventListener("click", () => this.togglePause());
        if (btnRestart) btnRestart.addEventListener("click", () => this.restartRace());

        // Modal finish screen restart button
        const btnFinishRestart = document.getElementById("btnFinishRestart");
        if (btnFinishRestart) btnFinishRestart.addEventListener("click", () => this.restartRace());

        // Touch pedals and steering buttons
        const btnGas = document.getElementById("btnGas");
        const btnBrake = document.getElementById("btnBrake");
        const btnSteerLeft = document.getElementById("btnSteerLeft");
        const btnSteerRight = document.getElementById("btnSteerRight");
        const btnHandbrake = document.getElementById("btnHandbrake");

        if (btnGas) this.controls.bindButton(btnGas, () => this.controls.keys.up = true, () => this.controls.keys.up = false);
        if (btnBrake) this.controls.bindButton(btnBrake, () => this.controls.keys.down = true, () => this.controls.keys.down = false);
        if (btnSteerLeft) this.controls.bindButton(btnSteerLeft, () => this.controls.keys.left = true, () => this.controls.keys.left = false);
        if (btnSteerRight) this.controls.bindButton(btnSteerRight, () => this.controls.keys.right = true, () => this.controls.keys.right = false);
        if (btnHandbrake) this.controls.bindButton(btnHandbrake, () => this.controls.keys.space = true, () => this.controls.keys.space = false);

        // Canvas click audio start
        this.canvas.addEventListener("click", () => this.startAudio(), { once: true });
    }
}

// Window init
window.addEventListener("DOMContentLoaded", () => {
    window.gameInstance = new FormulaRacerGame();
    window.gameInstance.init();
});
