#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import time, sys, termios, tty

# ==================================================
# TIMING
# ==================================================

RATE = 50
ACTION_TIME = 0.2   # slower = stable

# ==================================================
# LEG INDICES
# ==================================================

LEG = {
    'FL': 0,
    'FR': 3,
    'RL': 6,
    'RR': 9
}

# ==================================================
# HIP ANGLES
# ==================================================

HIP_NEUTRAL = {
    'FL': -0.2,
    'FR':  0.2,
    'RL':  0.2,
    'RR': -0.2
}

# small forward swing (critical)
HIP_SWING = {
    'FL': -0.1,
    'FR':  0.1,
    'RL':  0.1,
    'RR': -0.1
}

# ==================================================
# THIGH + KNEE ANGLES
# ==================================================

THIGH_FWD  = {'FL':  0.5, 'FR': -0.5, 'RL': -0.5, 'RR': -0.5}
THIGH_BACK = {'FL':  0.0, 'FR':  0.0, 'RL':  0.0, 'RR':  0.0}

# IMPORTANT: knees are NEVER zero now
KNEE_STANCE = {'FL':  0.15, 'FR': -0.15, 'RL':  0.15, 'RR': -0.15}
KNEE_LIFT   = {'FL':  0.25, 'FR': -0.25, 'RL':  0.20, 'RR': -0.20}

# ==================================================

class DiagonalTrot(Node):

    def __init__(self):
        super().__init__('diagonal_trot')

        self.pub = self.create_publisher(
            Float64MultiArray,
            '/forward_position_controller/commands',
            10
        )

        self.pose = [0.0] * 12

        print("\n🐕 STABLE DIAGONAL TROT")
        print("W : start trot")
        print("Q : quit")

        self.go_to_neutral()

    # ------------------------------------------------
    def publish(self):
        msg = Float64MultiArray()
        msg.data = self.pose
        self.pub.publish(msg)
        print([round(x, 3) for x in self.pose])

    # ------------------------------------------------
    def interpolate(self, joints, targets):
        start = self.pose.copy()
        steps = int(ACTION_TIME * RATE)

        for i in range(steps):
            a = (i + 1) / steps
            for j in joints:
                self.pose[j] = start[j] + (targets[j] - start[j]) * a
            self.publish()
            time.sleep(1 / RATE)

    # ------------------------------------------------
    def go_to_neutral(self):
        for leg in LEG:
            i = LEG[leg]
            self.pose[i+0] = HIP_NEUTRAL[leg]
            self.pose[i+1] = THIGH_BACK[leg]
            self.pose[i+2] = KNEE_STANCE[leg]
        self.publish()
        time.sleep(1.0)

    # ------------------------------------------------
    def diagonal_step(self, swing, support):

        # LOCK SUPPORT LEGS COMPLETELY
        for leg in support:
            i = LEG[leg]
            self.pose[i+0] = HIP_NEUTRAL[leg]
            self.pose[i+1] = THIGH_BACK[leg]
            self.pose[i+2] = KNEE_STANCE[leg]

        self.publish()
        time.sleep(0.05)

        # ---- LIFT (knees only)
        joints = []
        targets = {}
        for leg in swing:
            j = LEG[leg] + 2
            joints.append(j)
            targets[j] = KNEE_LIFT[leg]
        self.interpolate(joints, targets)

        # ---- SWING (hip + thigh)
        joints = []
        targets = {}
        for leg in swing:
            i = LEG[leg]
            joints += [i, i+1]
            targets[i]   = HIP_SWING[leg]
            targets[i+1] = THIGH_FWD[leg]
        self.interpolate(joints, targets)

        # ---- PLACE (knees only)
        joints = []
        targets = {}
        for leg in swing:
            j = LEG[leg] + 2
            joints.append(j)
            targets[j] = KNEE_STANCE[leg]
        self.interpolate(joints, targets)

    # ------------------------------------------------
    def run(self):
        while rclpy.ok():
            self.diagonal_step(['FL','RR'], ['FR','RL'])
            self.diagonal_step(['FR','RL'], ['FL','RR'])

# ==================================================
# KEYBOARD
# ==================================================

def get_key():
    s = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, s)

# ==================================================
def main():
    rclpy.init()
    node = DiagonalTrot()

    try:
        while rclpy.ok():
            k = get_key().lower()
            if k == 'w':
                node.run()
            elif k == 'q':
                break
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

# ==================================================
if __name__ == '__main__':
    main()
