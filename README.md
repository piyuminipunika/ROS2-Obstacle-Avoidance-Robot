ROS 2 Jazzy /Gazebo Harmonic/Obstacle avoiding Robot

## Files
- world.sdf: Gazebo Harmonic world, with gray floor, perimeter walls, blocks, partitions, and unchanged balanced robot
- avoid.py: unchanged ROS 2 obstacle avoidance controller

## Run
Terminal 1: `cd ~/my_obstacle_robot && gz sim -r world.sdf`
Terminal 2: `ros2 run ros_gz_bridge parameter_bridge '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan' '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'`
Terminal 3: `cd ~/my_obstacle_robot && python3 avoid.py`
To start fsm controller: `./start_all.sh`

Backup your working project before replacing any files. This world is XML-validated but has not been simulated on your computer.

## FSM-Based Obstacle Avoidance

The robot uses a Finite State Machine (FSM) for autonomous obstacle avoidance.

### FSM States

| State | Description |
|---|---|
| FORWARD | Moves forward using adaptive speed control |
| STOP | Stops when an obstacle is detected |
| BACKWARD | Reverses when an obstacle is critically close |
| TURN_LEFT | Rotates left to avoid obstacles |
| TURN_RIGHT | Rotates right to avoid obstacles |
| RECOVERY | Performs a recovery rotation when normal turning fails |

### Smart Speed Control

The robot adjusts its forward speed based on LiDAR measurements.

- Distance > 2.0 m: 0.50 m/s
- Distance > 1.0 m: 0.25 m/s
- Distance >= 0.50 m: 0.13 m/s
- Distance < 0.50 m: Stop and avoid the obstacle

### Demonstration Video

The following video demonstrates normal FSM-based obstacle avoidance in Gazebo Harmonic.

[Watch the FSM Obstacle Avoidance Demonstration](videos/fsm_obstacle_avoidance_demo.mp4)

**Note:** The demonstration does not specifically verify activation of the RECOVERY state.

