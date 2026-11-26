import math
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple


@dataclass
class PhysicsParams:
    c_rad: float = 500.0      # Radiator heat capacity [J/K]
    c_room: float = 10000.0   # Room heat capacity [J/K]
    k_rad_room: float = 25.0  # Heat transfer coeff radiator -> room [W/K]
    k_room_amb: float = 10.0  # Heat transfer coeff room -> ambient [W/K]
    max_power: float = 2000.0 # Maximum radiator heating power [W]
    t_amb: float = 10.0       # Ambient outside temperature [°C]


class RadiatorRoomModel:
    def __init__(self, params: PhysicsParams, t_room_init: float = 15.0, t_rad_init: float = 15.0):
        self.p = params
        self.t_room = t_room_init
        self.t_rad = t_rad_init

    def step(self, u: float, dt: float) -> Tuple[float, float]:
        u_clamped = max(0.0, min(1.0, u))
        q_in = u_clamped * self.p.max_power
        q_rad_room = self.p.k_rad_room * (self.t_rad - self.t_room)
        q_room_amb = self.p.k_room_amb * (self.t_room - self.p.t_amb)

        # Differential equations
        dt_rad_dt = (q_in - q_rad_room) / self.p.c_rad
        dt_room_dt = (q_rad_room - q_room_amb) / self.p.c_room

        self.t_rad += dt_rad_dt * dt
        self.t_room += dt_room_dt * dt
        return self.t_room, self.t_rad


class BangBangController:
    def __init__(self, setpoint: float, hysteresis: float = 0.5):
        self.setpoint = setpoint
        self.hysteresis = hysteresis
        self.state = 0.0

    def compute(self, t_current: float, dt: float) -> float:
        if t_current < self.setpoint - self.hysteresis:
            self.state = 1.0
        elif t_current > self.setpoint + self.hysteresis:
            self.state = 0.0
        return self.state


class PIDController:
    def __init__(self, kp: float, ki: float, kd: float, setpoint: float, output_limits: Tuple[float, float] = (0.0, 1.0)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.min_out, self.max_out = output_limits
        self.integral = 0.0
        self.prev_error = 0.0

    def compute(self, t_current: float, dt: float) -> float:
        error = self.setpoint - t_current
        self.integral += error * dt
        # Anti-windup clamping on integral
        self.integral = max(-1000.0, min(1000.0, self.integral))
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error

        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        return max(self.min_out, min(self.max_out, output))


def run_simulation(controller, params: PhysicsParams, setpoint: float, steps: int = 1200, dt: float = 5.0) -> Dict[str, Any]:
    model = RadiatorRoomModel(params, t_room_init=setpoint - 5.0, t_rad_init=setpoint - 5.0)
    times, room_temps, rad_temps, controls = [], [], [], []
    
    total_error_sq = 0.0
    for step in range(steps):
        t = step * dt
        u = controller.compute(model.t_room, dt)
        t_room, t_rad = model.step(u, dt)
        
        times.append(t)
        room_temps.append(t_room)
        rad_temps.append(t_rad)
        controls.append(u)
        
        total_error_sq += (setpoint - t_room) ** 2

    rms_error = math.sqrt(total_error_sq / steps)
    return {
        "times": times,
        "room_temps": room_temps,
        "rad_temps": rad_temps,
        "controls": controls,
        "rms_error": rms_error
    }


if __name__ == "__main__":
    params = PhysicsParams(t_amb=5.0)
    setpoint = 21.0
    
    bb = BangBangController(setpoint=setpoint, hysteresis=0.3)
    pid = PIDController(kp=1.5, ki=0.01, kd=50.0, setpoint=setpoint)
    
    bb_res = run_simulation(bb, params, setpoint)
    pid_res = run_simulation(pid, params, setpoint)
    
    print("Simulated Radiator Heat Dynamics & Control Loop")
    print(f"Bang-Bang Controller RMS Error: {bb_res['rms_error']:.3f}°C")
    print(f"PID Controller RMS Error:       {pid_res['rms_error']:.3f}°C")
