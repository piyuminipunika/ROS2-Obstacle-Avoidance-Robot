#!/usr/bin/env python3
"""ROS 2 Jazzy reactive LiDAR obstacle-avoidance controller for our custom robot."""
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class Avoider(Node):
    def __init__(self):
        super().__init__('my_obstacle_avoider')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(LaserScan, '/scan', self.on_scan, qos_profile_sensor_data)
        self.front = None
        self.left = None
        self.right = None
        self.last_scan = None
        self.turning = False
        self.turn_direction = 1.0
        self.timer = self.create_timer(0.1, self.step)
        self.get_logger().info('Custom obstacle avoidance started')

    def on_scan(self, scan):
        sectors = {'front': [], 'left': [], 'right': []}
        for i, r in enumerate(scan.ranges):
            if math.isnan(r) or r < scan.range_min:
                continue
            if math.isinf(r):
                if r < 0:
                    continue
                r = scan.range_max
            r = min(r, scan.range_max)
            angle = math.degrees(math.atan2(
                math.sin(scan.angle_min + i * scan.angle_increment),
                math.cos(scan.angle_min + i * scan.angle_increment)))
            if abs(angle) <= 30:
                sectors['front'].append(r)
            elif 30 < angle <= 110:
                sectors['left'].append(r)
            elif -110 <= angle < -30:
                sectors['right'].append(r)
        self.front = min(sectors['front']) if sectors['front'] else None
        self.left = min(sectors['left']) if sectors['left'] else None
        self.right = min(sectors['right']) if sectors['right'] else None
        self.last_scan = time.monotonic()

    def step(self):
        cmd = Twist()
        if self.last_scan is None or time.monotonic() - self.last_scan > 1.0 or self.front is None:
            self.pub.publish(cmd)  # Sensor failure: stop.
            return
        if self.turning and self.front >= 0.70:
            self.turning = False
        if not self.turning and self.front < 0.50:
            self.turning = True
            left = self.left if self.left is not None else 0.0
            right = self.right if self.right is not None else 0.0
            self.turn_direction = 1.0 if left >= right else -1.0
            self.get_logger().info('Obstacle: turning ' + ('left' if self.turn_direction > 0 else 'right'))
        if self.turning:
            cmd.angular.z = 0.75 * self.turn_direction
        else:
            cmd.linear.x = 0.50
        self.pub.publish(cmd)

    def stop(self):
        self.pub.publish(Twist())


def main():
    rclpy.init()
    node = Avoider()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
