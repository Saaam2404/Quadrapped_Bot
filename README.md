# Quadrapped Bot (Pet Bot)

A ROS 2–based **quadruped (pet) robot** project implementing gait control using
**inverse kinematics (IK)**.  
This repository focuses on stable locomotion such as **trot gait**, with future
extensions to trot, sideways, and backward motion.

---

##  Features
-  IK-based leg control (hip, thigh, knee)
-  Stable crawl gait (one leg at a time)
-  Low body-height walking for improved stability
-  Written in Python for ROS 2
-  Modular and extendable gait logic

---

##  Tech Stack
- **ROS 2** (rclpy)
- **Python 3**
- **Gazebo Ignition**
- Designed for simulation & real hardware compatibility

---

---

## 🖥️ Simulation Launch

To start the quadruped robot in **simulation mode**, use the provided launch file.

### 1️⃣ Build and source the workspace
```bash
colcon build
source install/setup.bash
ros2 launch pet_bot_test5 sim.launch.py
