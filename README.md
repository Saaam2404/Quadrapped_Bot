# Pet Bot Test5

## Clone the repository

```bash
mkdir -p ~/petbot_ws/src
cd ~/petbot_ws/src

git clone <YOUR_GITHUB_REPO_URL>
```

## Go to the workspace

```bash
cd ~/petbot
```

## Run the installation script

```bash
chmod +x src/pet_bot_test5/requirements.sh
bash src/pet_bot_test5/requirements.sh
```

## Install remaining ROS dependencies

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

## Source the workspace

```bash
source install/setup.bash
```

## Launch

```bash
ros2 launch pet_bot_test5 sim.launch.py
```
