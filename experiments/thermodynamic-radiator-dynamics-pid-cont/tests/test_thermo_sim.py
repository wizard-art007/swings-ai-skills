import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from thermo_sim import PhysicsParams, RadiatorRoomModel, BangBangController, PIDController, run_simulation


def test_radiator_room_model_physics():
    params = PhysicsParams(t_amb=0.0)
    model = RadiatorRoomModel(params, t_room_init=20.0, t_rad_init=25.0)
    t_room, t_rad = model.step(u=0.0, dt=10.0)
    assert t_room < 20.0
    assert t_rad < 25.0


def test_bang_bang_controller():
    ctrl = BangBangController(setpoint=20.0, hysteresis=1.0)
    # Below lower bound -> turn ON
    assert ctrl.compute(18.5, 1.0) == 1.0
    # Inside hysteresis band -> retain state
    assert ctrl.compute(20.0, 1.0) == 1.0
    # Above upper bound -> turn OFF
    assert ctrl.compute(21.5, 1.0) == 0.0


def test_pid_controller():
    ctrl = PIDController(kp=1.0, ki=0.1, kd=0.1, setpoint=20.0)
    # Below setpoint -> positive control output
    out = ctrl.compute(18.0, 1.0)
    assert out > 0.0
    # At setpoint -> minimal/zero proportional output
    out_at_target = ctrl.compute(20.0, 1.0)
    assert 0.0 <= out_at_target <= 1.0


def test_controller_comparison():
    params = PhysicsParams(t_amb=10.0)
    setpoint = 21.0
    steps = 1500
    
    bb_ctrl = BangBangController(setpoint=setpoint, hysteresis=0.2)
    bb_res = run_simulation(bb_ctrl, params, setpoint, steps=steps, dt=2.0)
    
    pid_ctrl = PIDController(kp=2.5, ki=0.02, kd=80.0, setpoint=setpoint)
    pid_res = run_simulation(pid_ctrl, params, setpoint, steps=steps, dt=2.0)
    
    assert pid_res["rms_error"] < bb_res["rms_error"]
