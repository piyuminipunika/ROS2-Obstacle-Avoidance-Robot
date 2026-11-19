
# 🤖 Autonomous Obstacle Avoidance Robot Using ROS 2 and Finite State Machine
## ROS 2 Jazzy / Gazebo Harmonic / Obstacle avoiding Robot
### ROS 2 Jazzy | Gazebo Harmonic | Python | LiDAR | Finite State Machine (FSM)

## 📌 Project Overview

This project demonstrates the development of an **autonomous mobile robot capable of detecting and avoiding obstacles in a simulated environment** using ROS 2 Jazzy and Gazebo Harmonic.

The robot uses a LiDAR sensor to continuously monitor its surroundings and make real-time movement decisions.

A **Finite State Machine (FSM)** is implemented to organize the robot's navigation behavior into predefined states, allowing it to move forward, stop, reverse, turn, and perform recovery maneuvers when necessary.

The project also incorporates **adaptive speed control**, enabling the robot to adjust its velocity based on the distance to nearby obstacles.

The robot operates autonomously without requiring manual control.

### 🎯 Project Objectives

- Develop an autonomous obstacle avoidance robot using ROS 2.
- Simulate the robot in a custom Gazebo Harmonic environment.
- Detect obstacles using LiDAR sensor measurements.
- Implement a Finite State Machine for robot decision-making.
- Develop adaptive speed control based on obstacle proximity.
- Implement recovery behavior when normal obstacle avoidance fails.
- Demonstrate autonomous robot movement in simulation.

---

## 🛠️ Technologies Used

| Technology | Description |
|---|---|
| **Ubuntu 24.04** | Operating system |
| **ROS 2 Jazzy** | Robot Operating System |
| **Gazebo Harmonic** | Robotics simulation environment |
| **Python 3** | Robot control programming |
| **LiDAR** | Obstacle detection |
| **Finite State Machine** | Robot behavior and decision-making |
| **ROS–Gazebo Bridge** | Communication between ROS 2 and Gazebo |
| **SDF** | Robot simulation world description |

---

## ⚙️ System Architecture

The robot follows a sensor-based reactive navigation architecture.

```text
              Gazebo Harmonic
                    |
                    v
               LiDAR Sensor
                    |
                    v
             /scan (LaserScan)
                    |
                    v
            ROS–Gazebo Bridge
                    |
                    v
          Obstacle Avoidance FSM
                    |
          +---------+---------+
          |                   |
          v                   v
    Obstacle Detection   Speed Control
          |                   |
          +---------+---------+
                    |
                    v
             FSM Decision
                    |
                    v
            /cmd_vel (Twist)
                    |
                    v
            ROS–Gazebo Bridge
                    |
                    v
             Robot Movement
```

The controller receives LiDAR data through the `/scan` topic and publishes velocity commands to `/cmd_vel`.

---

## 🧠 Finite State Machine (FSM)

The robot uses a **six-state Finite State Machine** to control its movement.

| State | Function |
|---|---|
| `FORWARD` | Moves forward when the path is clear |
| `STOP` | Stops the robot when an obstacle is detected |
| `BACKWARD` | Moves backward when an obstacle is critically close |
| `TURN_LEFT` | Rotates left to avoid obstacles |
| `TURN_RIGHT` | Rotates right to avoid obstacles |
| `RECOVERY` | Performs a recovery maneuver when normal turning is unsuccessful |

### FSM Decision-Making Process

1. The robot initially enters the `STOP` state.
2. LiDAR measurements are collected from the surrounding environment.
3. If the forward path is clear, the robot transitions to `FORWARD`.
4. When an obstacle is detected, the robot transitions to `STOP`.
5. If the obstacle is critically close, the robot enters `BACKWARD`.
6. Otherwise, the robot compares available space on the left and right.
7. The robot turns toward the direction with greater clearance.
8. Once the forward path becomes sufficiently clear, the robot resumes forward movement.
9. If the turning maneuver exceeds its maximum duration, the robot enters `RECOVERY`.
10. After recovery, the robot reevaluates its surroundings.

### Simplified FSM Flow

```text
                     START
                       |
                       v
                      STOP
                       |
                 Path Clear?
                       |
                 +-----+-----+
                 |           |
                YES          NO
                 |           |
                 v           v
              FORWARD    Check Distance
                 |           |
                 |     +-----+------+
                 |     |            |
                 |   Critical    Obstacle
                 |     |            |
                 |     v            v
                 |  BACKWARD   Choose Direction
                 |                  |
                 |            +-----+-----+
                 |            |           |
                 |            v           v
                 |        TURN_LEFT   TURN_RIGHT
                 |            |           |
                 |            +-----+-----+
                 |                  |
                 |             Path Clear?
                 |              /       \
                 |            YES        NO
                 |             |          |
                 |             v          v
                 +<-------- FORWARD    RECOVERY
                                           |
                                           v
                                          STOP
```

---

## 📡 LiDAR-Based Obstacle Detection

The robot continuously receives LiDAR measurements through:

**ROS 2 Topic:** `/scan`  
**Message Type:** `sensor_msgs/msg/LaserScan`

The LiDAR scan is divided into three detection regions.

| Region | Angular Range |
|---|---|
| Front | −30° to +30° |
| Left | +30° to +110° |
| Right | −110° to −30° |

The controller calculates the minimum valid distance within each region.

These measurements are used to determine the robot's movement decisions.

### Obstacle Detection Thresholds

| Parameter | Distance |
|---|---|
| Obstacle detection distance | 0.50 m |
| Safe distance | 0.70 m |
| Critical obstacle distance | 0.25 m |

When an obstacle is detected within 0.50 m, the robot stops moving forward and initiates obstacle avoidance.

---

## 🚀 Adaptive Speed Control

The robot implements a distance-based speed control mechanism.

Instead of moving at a constant speed, the robot adjusts its forward velocity according to the available distance.

| Distance to Obstacle | Robot Speed |
|---|---|
| Greater than 2.0 m | 0.50 m/s |
| 1.0 m – 2.0 m | 0.25 m/s |
| 0.50 m – 1.0 m | 0.13 m/s |
| Less than 0.50 m | 0.00 m/s |

### Advantages

- Faster movement in open spaces
- Reduced speed near obstacles
- More controlled obstacle avoidance
- Improved responsiveness to changing environments

---

## 🔄 Recovery Mechanism

The FSM includes a `RECOVERY` state designed to provide an additional maneuver when normal obstacle avoidance is unsuccessful.

### How Recovery Works

During normal operation, the robot turns left or right depending on the available space.

If the robot cannot find a sufficiently clear path within the maximum turning duration:

1. The current turning maneuver ends.
2. The FSM transitions to `RECOVERY`.
3. The robot rotates in the opposite direction.
4. The recovery rotation continues for a predefined duration.
5. The FSM returns to `STOP`.
6. The controller evaluates the environment again and selects the next movement.

### Recovery Parameters

| Parameter | Value |
|---|---|
| Maximum normal turning duration | 4.0 seconds |
| Recovery rotation duration | 1.5 seconds |
| Angular turning speed | 0.75 rad/s |

The recovery mechanism helps the robot attempt an alternative maneuver when the normal turning behavior is unsuccessful.

**Note:** The recovery mechanism is a timed rotation strategy. It does not guarantee that the robot can escape every trapped situation.

---

## 📁 Project Structure

```text
ROS2-Obstacle-Avoidance-Robot/
│
├── world.sdf
│   └── Custom Gazebo simulation environment
│
├── avoid.py
│   └── Original reactive obstacle avoidance controller
│
├── avoid_fsm.py
│   └── FSM-based obstacle avoidance with recovery
│
├── start_all.sh
│   └── Automatic simulation startup script
│
├── README.md
│   └── Project documentation
│
└── videos/
    └── fsm_obstacle_avoidance_demo.mp4
```

---

## ▶️ How to Run the Project

### Prerequisites

The following software is required:

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- ROS–Gazebo Bridge
- Python 3
- `rclpy`

### Step 1: Clone the Repository

```bash
git clone https://github.com/piyuminipunika/ROS2-Obstacle-Avoidance-Robot.git
```

### Step 2: Navigate to the Project

```bash
cd ROS2-Obstacle-Avoidance-Robot
```

### Step 3: Configure the Project Directory

The startup script uses:

```bash
PROJECT_DIR="$HOME/my_obstacle_robot"
```

Update this variable in `start_all.sh` to match the directory where you cloned the repository.

### Step 4: Start the Robot

```bash
bash start_all.sh
```

The startup script automatically opens three terminals.

**Terminal 1 — Gazebo Harmonic**

Launches the custom simulation environment.

**Terminal 2 — ROS–Gazebo Bridge**

Establishes communication between the Gazebo simulation and ROS 2 topics.

**Terminal 3 — FSM Controller**

Executes `avoid_fsm.py`, which controls the robot using LiDAR measurements.

Once the simulation and controller are running, the robot begins autonomous obstacle avoidance.

---

## 🎥 Demonstration Video

The following video demonstrates the robot performing autonomous obstacle avoidance in Gazebo Harmonic.

### ▶️ FSM Obstacle Avoidance Demonstration

[Watch Demonstration Video](videos/fsm_obstacle_avoidance_demo.mp4)




The demonstration focuses on normal obstacle avoidance behavior, including:

- LiDAR-based obstacle detection
- Autonomous forward movement
- Adaptive speed control
- Obstacle avoidance through turning
- FSM-based movement decisions

**Note:** The video demonstrates normal FSM operation. Activation of the recovery state has not been specifically verified in this recording.

---

## 📊 Project Outcomes

The project demonstrates:

- Implementation of autonomous obstacle avoidance in a simulated environment.
- Integration of ROS 2 Jazzy with Gazebo Harmonic.
- Processing of LiDAR sensor data for robot navigation.
- FSM-based robot movement decisions.
- Adaptive speed control based on obstacle distance.
- Implementation of an additional recovery behavior.

The simulation provides a foundation for developing more advanced autonomous mobile robot navigation systems.

---

## 🔮 Future Improvements

Potential future developments include:

- Testing recovery behavior in complex obstacle configurations
- Implementing rear obstacle detection for safer reversing
- Adding stuck detection using odometry
- Visualizing FSM states in RViz
- Integrating SLAM for environment mapping
- Implementing autonomous goal-based navigation using Nav2
- Testing the controller on a physical robot

---

## 📚 Key Concepts

This project explores several fundamental robotics concepts:

**Robot Operating System (ROS 2)** — Communication between robotic software components.

**LiDAR Perception** — Detecting nearby obstacles using laser range measurements.

**Finite State Machine (FSM)** — Structuring robot behavior using states and transitions.

**Reactive Navigation** — Making movement decisions based on current sensor measurements.

**Adaptive Speed Control** — Adjusting robot velocity according to obstacle proximity.

**Recovery Behavior** — Attempting an alternative maneuver when normal obstacle avoidance is unsuccessful.

---

## 👩‍💻 Author

**Piyumi Nipunika**

Robotics and ROS 2 Project

---

⭐ If you find this project useful, consider giving the repository a star!


## Run (controller with classes)
Terminal 1: `cd ~/my_obstacle_robot && gz sim -r world.sdf`
Terminal 2: `ros2 run ros_gz_bridge parameter_bridge '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan' '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'`
Terminal 3: `cd ~/my_obstacle_robot && python3 avoid.py`

