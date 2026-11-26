# Thermodynamic Radiator Dynamics & PID Controller Simulator

An offline Python experimental simulation modeling thermodynamic radiator dissipation, room heat loss dynamics, and comparing traditional Bang-Bang vs. Proportional-Integral-Derivative (PID) thermostat control loops.

## How It Works
- **Physics Model**: Uses a lumped-capacitance thermal model. The radiator heats up based on control input power and loses heat to the room. The room absorbs heat from the radiator and loses heat to the outside ambient environment.
- **Bang-Bang Controller**: Simple hysteresis thermostat that turns the radiator fully on or off.
- **PID Controller**: Modulates the radiator heating power smoothly using proportional, integral, and derivative gains to minimize overshoot and steady-state error.

## Running the Simulation & Tests
