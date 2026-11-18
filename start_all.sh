#!/bin/bash

# ==========================================
# OBSTACLE AVOIDANCE ROBOT STARTUP
# ROS 2 Jazzy + Gazebo Harmonic
# ==========================================

PROJECT_DIR="$HOME/my_obstacle_robot"

echo "=================================="
echo " Starting Obstacle Avoidance Robot "
echo "=================================="

# Check project files
if [ ! -f "$PROJECT_DIR/world.sdf" ] ||
   [ ! -f "$PROJECT_DIR/avoid_fsm.py" ]; then
    echo "ERROR: Robot project files not found!"
    exit 1
fi

# ------------------------------------------
# TERMINAL 1: START GAZEBO
# ------------------------------------------

echo "Starting Gazebo..."

gnome-terminal -- bash -c "
cd '$PROJECT_DIR'
gz sim world.sdf
exec bash
"

# Allow Gazebo some startup time
sleep 5

# ------------------------------------------
# TERMINAL 2: START ROS-GAZEBO BRIDGE
# ------------------------------------------

echo "Starting ROS-Gazebo Bridge..."

gnome-terminal -- bash -c "
source /opt/ros/jazzy/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
'/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan' \
'/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'

exec bash
"

sleep 3

# ------------------------------------------
# TERMINAL 3: START FSM CONTROLLER
# ------------------------------------------

echo "Starting FSM Controller..."

gnome-terminal -- bash -c "
source /opt/ros/jazzy/setup.bash
cd '$PROJECT_DIR'

python3 avoid_fsm.py

exec bash
"

echo "=================================="
echo " Robot startup commands launched! "
echo "=================================="
