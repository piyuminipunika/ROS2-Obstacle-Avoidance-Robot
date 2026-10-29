#ROS 2 Jazzy / Gazebo Harmonic / Obstacle avoiding Robot


## Files
- world.sdf: Gazebo Harmonic world, with gray floor, perimeter walls, blocks, partitions, and unchanged balanced robot
- avoid.py: unchanged ROS 2 obstacle avoidance controller

## Run
Terminal 1: `cd ~/my_obstacle_robot && gz sim -r world.sdf`
Terminal 2: `ros2 run ros_gz_bridge parameter_bridge '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan' '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'`
Terminal 3: `cd ~/my_obstacle_robot && python3 avoid.py`

Backup your working project before replacing any files. This world is XML-validated but has not been simulated on your computer.
