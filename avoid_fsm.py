#!/usr/bin/env python3

import math
from enum import Enum

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


# ==========================================
# 1. DEFINE ROBOT STATES
# ==========================================

class RobotState(Enum):

    FORWARD = 1
    STOP = 2
    BACKWARD = 3
    TURN_LEFT = 4
    TURN_RIGHT = 5
    RECOVERY = 6


# ==========================================
# 2. OBSTACLE AVOIDANCE FSM
# ==========================================

class ObstacleAvoidanceFSM(Node):

    def __init__(self):

        super().__init__('obstacle_avoidance_fsm')

        # ROS 2 Subscriber
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile_sensor_data
        )

        # ROS 2 Publisher
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Initial FSM state
        self.state = RobotState.STOP

        # ==================================
        # ROBOT SPEED PARAMETERS
        # ==================================

        self.max_speed = 0.50
        self.medium_speed = 0.25
        self.slow_speed = 0.13

        self.backward_speed = -0.10
        self.turn_speed = 0.75

        # ==================================
        # OBSTACLE DISTANCE PARAMETERS
        # ==================================

        self.obstacle_distance = 0.50
        self.safe_distance = 0.70
        self.critical_distance = 0.25

        # LiDAR distances
        self.front = None
        self.left = None
        self.right = None

        # State timing
        self.state_start_time = self.now_seconds()
        self.last_scan_time = None

        # Recovery durations
        self.backward_duration = 0.8
        self.minimum_turn_duration = 0.6
        self.maximum_turn_duration = 4.0

        # Recovery: rotate in the opposite direction after a timed-out turn
        self.recovery_duration = 1.5
        self.recovery_direction = 1.0

        # Store last speed for logging
        self.last_speed = None

        # Control loop: 10 Hz
        self.timer = self.create_timer(
            0.1,
            self.control_loop
        )

        self.get_logger().info(
            'FSM with Smart Speed Control Started'
        )

    # ======================================
    # 3. TIME HELPER
    # ======================================

    def now_seconds(self):

        return (
            self.get_clock().now().nanoseconds / 1e9
        )

    # ======================================
    # 4. CHANGE STATE
    # ======================================

    def change_state(self, new_state):

        if self.state != new_state:

            self.get_logger().info(
                f'{self.state.name} -> {new_state.name}'
            )

            self.state = new_state

            self.state_start_time = self.now_seconds()

    # ======================================
    # 5. LIDAR CALLBACK
    # ======================================

    def scan_callback(self, msg):

        front_ranges = []
        left_ranges = []
        right_ranges = []

        for i, distance in enumerate(msg.ranges):

            if math.isnan(distance):
                continue

            if distance < msg.range_min:
                continue

            if math.isinf(distance):

                if distance < 0:
                    continue

                distance = msg.range_max

            if distance > msg.range_max:
                distance = msg.range_max

            angle = (
                msg.angle_min +
                i * msg.angle_increment
            )

            angle_deg = math.degrees(
                math.atan2(
                    math.sin(angle),
                    math.cos(angle)
                )
            )

            # Front region
            if -30 <= angle_deg <= 30:

                front_ranges.append(distance)

            # Left region
            if 30 < angle_deg <= 110:

                left_ranges.append(distance)

            # Right region
            if -110 <= angle_deg < -30:

                right_ranges.append(distance)

        self.front = (
            min(front_ranges)
            if front_ranges else None
        )

        self.left = (
            min(left_ranges)
            if left_ranges else None
        )

        self.right = (
            min(right_ranges)
            if right_ranges else None
        )

        self.last_scan_time = self.now_seconds()

    # ======================================
    # 6. MOVE ROBOT
    # ======================================

    def move_robot(self, linear=0.0, angular=0.0):

        cmd = Twist()

        cmd.linear.x = float(linear)
        cmd.angular.z = float(angular)

        self.cmd_pub.publish(cmd)

    # ======================================
    # 7. SMART SPEED CONTROL
    # ======================================

    def calculate_speed(self):

        if self.front is None:
            return 0.0

        if self.front > 2.0:

            speed = self.max_speed

        elif self.front > 1.0:

            speed = self.medium_speed

        elif self.front >= self.obstacle_distance:

            speed = self.slow_speed

        else:

            speed = 0.0

        return speed

    # ======================================
    # 8. CHOOSE TURN DIRECTION
    # ======================================

    def choose_direction(self):

        if self.left is None or self.right is None:

            self.change_state(RobotState.STOP)
            return

        if self.left >= self.right:

            self.change_state(RobotState.TURN_LEFT)

        else:

            self.change_state(RobotState.TURN_RIGHT)

    # ======================================
    # 9. MAIN FSM CONTROL LOOP
    # ======================================

    def control_loop(self):

        now = self.now_seconds()

        # Stop if LiDAR is unavailable or stale
        if (
            self.last_scan_time is None
            or now - self.last_scan_time > 1.0
            or self.front is None
            or self.left is None
            or self.right is None
        ):

            self.move_robot()
            self.change_state(RobotState.STOP)
            return

        elapsed = now - self.state_start_time

        # ----------------------------------
        # STATE 1: FORWARD
        # ----------------------------------

        if self.state == RobotState.FORWARD:

            if self.front < self.obstacle_distance:

                self.move_robot()

                self.last_speed = None

                self.change_state(
                    RobotState.STOP
                )

            else:

                # SMART SPEED CONTROL
                speed = self.calculate_speed()

                self.move_robot(
                    linear=speed
                )

                # Print only when speed changes
                if speed != self.last_speed:

                    self.get_logger().info(
                        f'Front: {self.front:.2f} m | '
                        f'Speed: {speed:.2f} m/s'
                    )

                    self.last_speed = speed

        # ----------------------------------
        # STATE 2: STOP
        # ----------------------------------

        elif self.state == RobotState.STOP:

            self.move_robot()

            if self.front < self.critical_distance:

                self.change_state(
                    RobotState.BACKWARD
                )

            elif self.front < self.obstacle_distance:

                self.choose_direction()

            else:

                self.change_state(
                    RobotState.FORWARD
                )

        # ----------------------------------
        # STATE 3: BACKWARD
        # ----------------------------------

        elif self.state == RobotState.BACKWARD:

            if elapsed < self.backward_duration:

                self.move_robot(
                    linear=self.backward_speed
                )

            else:

                self.move_robot()

                self.choose_direction()

        # ----------------------------------
        # STATE 4: TURN LEFT
        # ----------------------------------

        elif self.state == RobotState.TURN_LEFT:

            if (
                elapsed >= self.minimum_turn_duration
                and self.front >= self.safe_distance
            ):

                self.move_robot()

                self.change_state(
                    RobotState.FORWARD
                )

            elif elapsed >= self.maximum_turn_duration:

                self.move_robot()

                self.recovery_direction = -1.0
                self.change_state(
                    RobotState.RECOVERY
                )

            else:

                self.move_robot(
                    angular=self.turn_speed
                )

        # ----------------------------------
        # STATE 5: TURN RIGHT
        # ----------------------------------

        elif self.state == RobotState.TURN_RIGHT:

            if (
                elapsed >= self.minimum_turn_duration
                and self.front >= self.safe_distance
            ):

                self.move_robot()

                self.change_state(
                    RobotState.FORWARD
                )

            elif elapsed >= self.maximum_turn_duration:

                self.move_robot()

                self.recovery_direction = 1.0
                self.change_state(
                    RobotState.RECOVERY
                )

            else:

                self.move_robot(
                    angular=-self.turn_speed
                )


        # ----------------------------------
        # STATE 6: RECOVERY
        # ----------------------------------

        elif self.state == RobotState.RECOVERY:

            if elapsed < self.recovery_duration:

                self.move_robot(
                    angular=self.turn_speed * self.recovery_direction
                )

            else:

                self.move_robot()

                self.change_state(
                    RobotState.STOP
                )


# ==========================================
# 10. MAIN FUNCTION
# ==========================================

def main(args=None):

    rclpy.init(args=args)

    node = ObstacleAvoidanceFSM()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.move_robot()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()