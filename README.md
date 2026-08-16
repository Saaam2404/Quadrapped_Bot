# Pet Bot Test5

## Clone Repository

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone <GITHUB_REPO_URL>
```

## Install Dependencies

```bash
cd ~/ros2_ws
bash src/pet_bot_test5/requirements.sh
```

## Install ROS Dependencies

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

## Build

```bash
colcon build --symlink-install
source install/setup.bash
```

## Launch Simulation

```bash
ros2 launch pet_bot_test5 sim.launch.py
```

## Test Motion Scripts

### Stand Up

```bash
ros2 run pet_bot_test5 starting_gait.py
```

### Forward Walk

```bash
ros2 run pet_bot_test5 forward_gait.py
```

### Backward Walk

```bash
ros2 run pet_bot_test5 backward_gait.py
```

