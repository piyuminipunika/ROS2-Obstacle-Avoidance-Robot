# GitHub-inspired obstacle course for ROS 2 Jazzy / Gazebo Harmonic

This is NOT an exact copy of saharshleo/obstacleAvoidanceRobot world. It is a gray-walled indoor obstacle course inspired by the reference, retaining the validated balanced robot from V1.1.

## Files
- world.sdf: Gazebo Harmonic world, with gray floor, perimeter walls, blocks, partitions, and unchanged balanced robot
- avoid.py: unchanged ROS 2 obstacle avoidance controller

## Run
Terminal 1: `cd ~/my_obstacle_robot && gz sim -r world.sdf`
Terminal 2: `ros2 run ros_gz_bridge parameter_bridge '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan' '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'`
Terminal 3: `cd ~/my_obstacle_robot && python3 avoid.py`

Backup your working project before replacing any files. This world is XML-validated but has not been simulated on your computer.
