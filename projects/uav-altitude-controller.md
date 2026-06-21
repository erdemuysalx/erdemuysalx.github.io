# UAV Altitude Controller
2026-06-01
GitHub: https://github.com/erdemuysalx/uav-altitude-controller
Paper: 
Image: /public/images/uav-altitude-controller.gif
Sprite: /public/images/me-pixel-uav.png
Order: 5

A PD-based altitude controller for a quadcopter UAV, developed at the University of Stuttgart's Institute of Flight Mechanics and Controls. The project covers the full control design pipeline: evaluating height-sensing options, deriving the system's transfer function via Laplace transform and block diagram reduction, and tuning a PD controller with a complementary low-pass/high-pass filter structure to suppress derivative noise while maintaining fast response. The controller was modeled in Simulink, characterized as a second-order (PT2) system, and validated through simulation with multiple damping/frequency configurations (e.g., ζ=0.9, ω=4) showing stable hover tracking with minimal steady-state error. Final validation included closed-loop testing in a Gazebo simulation environment with a simulated RC interface.