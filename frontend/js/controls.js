/**
 * FORMULA RACER - Controls & Input Handler
 * Course: Numerical and Symbolic Computing
 *
 * KEYBOARD CONTROLS:
 * Arrow Up / W = Throttle
 * Arrow Down / S = Brake / Reverse
 * Arrow Left / A = Steer Left
 * Arrow Right / D = Steer Right
 * Space = Emergency Brake
 * R = Restart / Reset
 * P / Escape = Pause / Resume
 */

class ControlsHandler {
    constructor() {
        this.keys = {
            up: false,
            down: false,
            left: false,
            right: false,
            space: false,
            turbo: false
        };

        this.throttle = 0.0;
        this.brake = 0.0;
        this.steer = 0.0; // -1 (left) to +1 (right)
        this.handbrake = false;
        this.turbo = false;

        this.resetRequested = false;
        this.pauseRequested = false;
        this.startRequested = false;
        this.integratorToggleRequested = false;

        this.initKeyboardListeners();
    }

    initKeyboardListeners() {
        window.addEventListener("keydown", (e) => {
            switch (e.code) {
                case "ArrowUp":
                case "KeyW":
                    this.keys.up = true;
                    e.preventDefault();
                    break;
                case "ArrowDown":
                case "KeyS":
                    this.keys.down = true;
                    e.preventDefault();
                    break;
                case "ArrowLeft":
                case "KeyA":
                    this.keys.left = true;
                    e.preventDefault();
                    break;
                case "ArrowRight":
                case "KeyD":
                    this.keys.right = true;
                    e.preventDefault();
                    break;
                case "Space":
                    this.keys.space = true;
                    e.preventDefault();
                    break;
                case "KeyT":
                case "ShiftLeft":
                case "ShiftRight":
                    this.keys.turbo = true;
                    break;
                case "KeyR":
                    this.resetRequested = true;
                    break;
                case "KeyP":
                case "Escape":
                    this.pauseRequested = true;
                    break;
                case "KeyM":
                    this.integratorToggleRequested = true;
                    break;
            }
            this.updateInputState();
        });

        window.addEventListener("keyup", (e) => {
            switch (e.code) {
                case "ArrowUp":
                case "KeyW":
                    this.keys.up = false;
                    break;
                case "ArrowDown":
                case "KeyS":
                    this.keys.down = false;
                    break;
                case "ArrowLeft":
                case "KeyA":
                    this.keys.left = false;
                    break;
                case "ArrowRight":
                case "KeyD":
                    this.keys.right = false;
                    break;
                case "Space":
                    this.keys.space = false;
                    break;
                case "KeyT":
                case "ShiftLeft":
                case "ShiftRight":
                    this.keys.turbo = false;
                    break;
            }
            this.updateInputState();
        });
    }

    updateInputState() {
        this.handbrake = this.keys.space;

        if (this.keys.space) {
            this.throttle = 0.0;
            this.brake = 1.0;
        } else {
            this.throttle = this.keys.up ? 1.0 : 0.0;
            this.brake = this.keys.down ? 1.0 : 0.0;
        }

        // Steer: -1 (left) to +1 (right)
        let s = 0.0;
        if (this.keys.left) s -= 1.0;
        if (this.keys.right) s += 1.0;
        this.steer = s;

        this.turbo = this.keys.turbo;
    }

    // Touch and button bindings
    bindButton(btnElement, pressCallback, releaseCallback) {
        if (!btnElement) return;
        const start = (e) => {
            e.preventDefault();
            pressCallback();
        };
        const end = (e) => {
            e.preventDefault();
            if (releaseCallback) releaseCallback();
        };
        btnElement.addEventListener("pointerdown", start);
        btnElement.addEventListener("pointerup", end);
        btnElement.addEventListener("pointerleave", end);
        btnElement.addEventListener("pointercancel", end);
    }

    getState() {
        const state = {
            throttle: this.throttle,
            brake: this.brake,
            steer: this.steer,
            handbrake: this.handbrake,
            turbo: this.turbo,
            reset: this.resetRequested,
            pause: this.pauseRequested,
            start: this.startRequested,
            toggleIntegrator: this.integratorToggleRequested
        };
        // Reset single-frame event triggers
        this.resetRequested = false;
        this.pauseRequested = false;
        this.startRequested = false;
        this.integratorToggleRequested = false;
        return state;
    }
}

window.ControlsHandler = ControlsHandler;
