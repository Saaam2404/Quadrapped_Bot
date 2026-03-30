#!/usr/bin/env python3

import math
import rclpy

from rclpy.node import Node
from geometry_msgs.msg import PoseArray
from geometry_msgs.msg import Pose2D


class GazeboPosePublisher(Node):

    def __init__(self):

        super().__init__("gazebo_pose_publisher")

        self.publisher = self.create_publisher(Pose2D, "/robot_pose", 10)

        self.create_subscription(
            PoseArray,
            "/model/pet_bot_test5/pose",
            self.pose_callback,
            10
        )

        self.get_logger().info("Listening to Gazebo pose...")


    def pose_callback(self, msg):

        if len(msg.poses) == 0:
            return

        pose = msg.poses[0]

        x = pose.position.x
        y = pose.position.y

        z = pose.orientation.z
        w = pose.orientation.w

        theta = math.atan2(
            2*(w*z),
            1 - 2*(z*z)
        )

        out = Pose2D()

        out.x = x
        out.y = y
        out.theta = theta

        self.publisher.publish(out)

        self.get_logger().info(
            f"Pose -> x:{x:.3f} y:{y:.3f} theta:{theta:.2f}"
        )


def main():

    rclpy.init()

    node = GazeboPosePublisher()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()