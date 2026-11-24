/**
 * FORMULA RACER - API Client Module
 * Course: Numerical and Symbolic Computing
 *
 * STRICT MATHEMATICAL REQUIREMENT:
 * f(x) = x^4 - 3x^3 + 2x
 * Never replace this equation with another function.
 */

const API = {
    baseUrl: window.location.origin.includes('http') ? window.location.origin : 'http://127.0.0.1:8000',

    async getHealth() {
        try {
            const res = await fetch(`${this.baseUrl}/api/health`);
            return await res.json();
        } catch (e) {
            console.warn("API getHealth fallback:", e);
            return { status: "offline", service: "Formula Racer Mathematical Engine" };
        }
    },

    async getAnalysis() {
        try {
            const res = await fetch(`${this.baseUrl}/api/analysis`);
            return await res.json();
        } catch (e) {
            console.warn("API getAnalysis fallback:", e);
            return null;
        }
    },

    async postSettings(settings = {}) {
        try {
            const res = await fetch(`${this.baseUrl}/api/settings`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(settings)
            });
            return await res.json();
        } catch (e) {
            console.warn("API postSettings fallback:", e);
            return null;
        }
    },

    async getInfo() {
        try {
            const res = await fetch(`${this.baseUrl}/api/info`);
            return await res.json();
        } catch (e) {
            console.warn("API getInfo fallback:", e);
            return {
                project: "FORMULA RACER – Mathematical Racing Simulator",
                strict_function: { equation: "f(x) = x^4 - 3x^3 + 2x" }
            };
        }
    },

    async getSymbolicAnalysis() {
        try {
            const res = await fetch(`${this.baseUrl}/api/symbolic/analysis`);
            return await res.json();
        } catch (e) {
            console.warn("API getSymbolicAnalysis fallback:", e);
            return null;
        }
    },

    async getTaylorSeries(x0 = 0.0, order = 4) {
        try {
            const res = await fetch(`${this.baseUrl}/api/symbolic/taylor`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ x0, order })
            });
            return await res.json();
        } catch (e) {
            console.warn("API getTaylorSeries fallback:", e);
            return null;
        }
    },

    async getTangentNormal(x0 = 1.0) {
        try {
            const res = await fetch(`${this.baseUrl}/api/symbolic/tangent-normal`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ x0 })
            });
            return await res.json();
        } catch (e) {
            console.warn("API getTangentNormal fallback:", e);
            return null;
        }
    },

    async getTrackProfile() {
        try {
            const res = await fetch(`${this.baseUrl}/api/numerical/track`);
            return await res.json();
        } catch (e) {
            console.warn("API getTrackProfile fallback:", e);
            return null;
        }
    },

    async getDifferentiation(x = 1.0, hList = [0.1, 0.05, 0.01, 0.005, 0.001, 0.0001]) {
        try {
            const res = await fetch(`${this.baseUrl}/api/numerical/differentiation`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ x, h_list: hList })
            });
            return await res.json();
        } catch (e) {
            console.warn("API getDifferentiation fallback:", e);
            return null;
        }
    },

    async getIntegration(a = 0.0, b = 2.0, n = 60) {
        try {
            const res = await fetch(`${this.baseUrl}/api/numerical/integration`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ a, b, n })
            });
            return await res.json();
        } catch (e) {
            console.warn("API getIntegration fallback:", e);
            return null;
        }
    },

    async getRootFinding(method = "newton", params = {}) {
        try {
            const body = { method, ...params };
            const res = await fetch(`${this.baseUrl}/api/numerical/roots`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });
            return await res.json();
        } catch (e) {
            console.warn("API getRootFinding fallback:", e);
            return null;
        }
    },

    async getTelemetry(x, velocity, throttle = 0, brake = 0) {
        try {
            const res = await fetch(`${this.baseUrl}/api/physics/telemetry`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ x, velocity, throttle, brake })
            });
            return await res.json();
        } catch (e) {
            return null;
        }
    },

    async stepSimulation(x, velocity, throttle = 0, brake = 0, dt = 0.016, integrator = "rk4") {
        try {
            const res = await fetch(`${this.baseUrl}/api/physics/step`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ x, velocity, throttle, brake, dt, integrator })
            });
            return await res.json();
        } catch (e) {
            return null;
        }
    }
};

window.API = API;
