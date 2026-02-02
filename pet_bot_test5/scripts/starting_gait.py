#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import sys
import termios
import tty
import time

# ==============================================================================
# 🛠️ --- TUNING CONSTANTS (EDIT THESE!) --- 🛠️
# ==============================================================================

# ------------------------------------------------------------------------------
# SIT POSE (FIXED SYMMETRY)
# ------------------------------------------------------------------------------

# Front legs should move the SAME but mirrored
R_FRONT_SIT_THIGH = 0.0    
R_FRONT_SIT_KNEE  = -0.8  

L_FRONT_SIT_THIGH = 0.0    
L_FRONT_SIT_KNEE  = 0.8    # <-- MIRRORED SIGN

# Rear legs should bend opposite directions
R_REAR_SIT_THIGH  = 0.0  
R_REAR_SIT_KNEE   = -0.8 

L_REAR_SIT_THIGH  = -0.0   
L_REAR_SIT_KNEE   = 0.8   

# ------------------------------------------------------------------------------
# CROUCH POSE (FIXED — LEFT SIDE MUST BE MIRROR OF RIGHT)
# ------------------------------------------------------------------------------
R_FRONT_CROUCH_HEIGHT = 0.0
R_FRONT_CROUCH_KNEE   = -0.4

R_REAR_CROUCH_HEIGHT  = 0.0
R_REAR_CROUCH_KNEE    = -0.8

# Mirror signs for LEFT legs
L_FRONT_CROUCH_HEIGHT = 0.0
L_FRONT_CROUCH_KNEE   = 0.4

L_REAR_CROUCH_HEIGHT  = 0.0
L_REAR_CROUCH_KNEE    = 0.8

# Duration
MOVE_DURATION = 0.5

# ==============================================================================
# POSE DEFINITIONS
# ==============================================================================

POSE_STAND = [0.0] * 12

POSE_SIT = [
    # Front Left  (hip=0 always)
    0.0, L_FRONT_SIT_THIGH, L_FRONT_SIT_KNEE,
    # Front Right
    0.0, R_FRONT_SIT_THIGH, R_FRONT_SIT_KNEE,
    # Rear Left
    0.0, L_REAR_SIT_THIGH, L_REAR_SIT_KNEE,
    # Rear Right
    0.0, R_REAR_SIT_THIGH, R_REAR_SIT_KNEE
]

POSE_CROUCH = [
    # Front Left
    0.0, L_FRONT_CROUCH_HEIGHT, L_FRONT_CROUCH_KNEE,
    # Front Right
    0.0, R_FRONT_CROUCH_HEIGHT, R_FRONT_CROUCH_KNEE,
    # Rear Left
    0.0, L_REAR_CROUCH_HEIGHT, L_REAR_CROUCH_KNEE,
    # Rear Right
    0.0, R_REAR_CROUCH_HEIGHT, R_REAR_CROUCH_KNEE
]

class PetBotCommander(Node):
    def __init__(self):
        super().__init__('pet_bot_commander')
        self.publisher_ = self.create_publisher(
            Float64MultiArray, 
            '/forward_position_controller/commands', 
            10
        )
        self.current_pose = list(POSE_STAND)
        
        print("\n🐶 PET BOT CONTROLLER INITIALIZED 🐶")
        print("-------------------------------------")
        print(f"Movement Speed: {MOVE_DURATION} seconds")
        print("Controls:")
        print("  [W] - Stand Up")
        print("  [S] - Sit Down")
        print("  [C] - Crouch")
        print("  [Q] - Quit")
        print("-------------------------------------")

    def publish_command(self, position_array):
        msg = Float64MultiArray()
        msg.data = position_array
        self.publisher_.publish(msg)

    def smooth_move(self, target_pose_name, target_pose):
        self.get_logger().info(f"Moving to {target_pose_name} over {MOVE_DURATION}s...")
        
        start_pose = self.current_pose
        rate = 50.0
        steps = int(MOVE_DURATION * rate)
        
        for step in range(steps):
            alpha = (step + 1) / steps
            interp_pose = [
                start_pose[i] + (target_pose[i] - start_pose[i]) * alpha
                for i in range(len(target_pose))
            ]
            self.publish_command(interp_pose)
            time.sleep(1.0 / rate)
            
        self.publish_command(target_pose)
        self.current_pose = list(target_pose)
        self.get_logger().info(f"Reached {target_pose_name}.")

def get_key():
    settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main(args=None):
    rclpy.init(args=args)
    node = PetBotCommander()

    try:
        while rclpy.ok():
            key = get_key().lower()
            if key == 'w':
                node.smooth_move("STAND", POSE_STAND)
            elif key == 's':
                node.smooth_move("SIT", POSE_SIT)
            elif key == 'c':
                node.smooth_move("CROUCH", POSE_CROUCH)
            elif key == 'q':
                break
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()