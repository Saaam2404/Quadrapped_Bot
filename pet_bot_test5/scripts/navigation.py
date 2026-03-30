#!/usr/bin/env python3

import math
import time
import rclpy
import cv2
import numpy as np

from rclpy.node import Node
from geometry_msgs.msg import Pose2D

from forward_gait import HybridIKTrot
from backward_gait import HybridIKTrot_Backward
from sideward_gait import SideWalk


GOAL_TOL = 0.05

ALIGN_TOL = 0.25   # ~14 degrees


class Navigator(Node):

    def __init__(self, gx, gy):

        super().__init__("quadruped_navigator")

        self.goal_x = gx
        self.goal_y = gy

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.goal_reached = False

        # OpenCV visualization
        self.canvas = np.zeros((700, 700, 3), dtype=np.uint8)
        self.prev_point = None

        self.scale = 80
        self.origin = (350, 350)

        cv2.namedWindow("Quadruped Path", cv2.WINDOW_NORMAL)

        goal_pixel = self.world_to_pixel(self.goal_x, self.goal_y)
        cv2.circle(self.canvas, goal_pixel, 6, (255, 0, 0), -1)

        self.create_subscription(
            Pose2D,
            "/robot_pose",
            self.pose_callback,
            10
        )

        self.get_logger().info(f"Navigating to ({gx},{gy})")


    def world_to_pixel(self, x, y):

        px = int(self.origin[0] + x * self.scale)
        py = int(self.origin[1] - y * self.scale)

        return (px, py)


    def pose_callback(self, msg):

        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta

        current = self.world_to_pixel(self.x, self.y)

        if self.prev_point is not None:
            cv2.line(self.canvas, self.prev_point, current, (0, 255, 0), 2)

        self.prev_point = current

        cv2.circle(self.canvas, current, 4, (0, 0, 255), -1)

        cv2.imshow("Quadruped Path", self.canvas)
        cv2.waitKey(1)

        dist = math.sqrt(
            (self.goal_x - self.x) ** 2 +
            (self.goal_y - self.y) ** 2
        )

        if dist < GOAL_TOL:

            self.goal_reached = True
            self.get_logger().info("Goal reached")


def run_gait(gait_node):

    while rclpy.ok() and not gait_node.timer.is_canceled():

        rclpy.spin_once(gait_node)

    gait_node.destroy_node()


def navigate_to(goal_x, goal_y):

    nav = Navigator(goal_x, goal_y)

    while rclpy.ok() and not nav.goal_reached:

        rclpy.spin_once(nav)

        dx = goal_x - nav.x
        dy = goal_y - nav.y

        distance = math.sqrt(dx**2 + dy**2)

        if distance < GOAL_TOL:
            break

        angle_to_goal = math.atan2(dy, dx)

        heading_error = angle_to_goal - nav.theta

        heading_error = math.atan2(
            math.sin(heading_error),
            math.cos(heading_error)
        )

        if abs(heading_error) > ALIGN_TOL:

            # Need to align with goal first
            if heading_error > 0:
                gait = SideWalk(1)   # step left
            else:
                gait = HybridIKTrot(2)   # step right/back

        else:
            # Robot is aligned → move forward
            gait = HybridIKTrot_Backward(2)

        run_gait(gait)

        time.sleep(0.1)

    nav.destroy_node()

    return "Navigation complete"


def main():

    rclpy.init()

    gx = float(input("Goal X: "))
    gy = float(input("Goal Y: "))

    result = navigate_to(gx, gy)

    print(result)

    rclpy.shutdown()


if __name__ == "__main__":
    main()