# Control a mobile robot to move across multiple points using ROS

This project implements a differential drive mobile robot using ROS for
autonomous navigation and control.

My Project: https://youtu.be/UYOfr4wLCoU
## Features

- Differential drive robot
- SLAM mapping
- AMCL localization
- Navigation using DWA and A*
- Simulation in Gazebo
- Visualization in RViz

## System Architecture

ROS nodes:

- robot_state_publisher
- controller_node
- slam_toolbox
- navigation_stack

Extended Kalman Filter - EKF

## Hardware

- Raspberry Pi4
- Arduino Mega
- LiDAR
- IMU
- Encoder

## Simulation

Gazebo + RViz

## Run
```bash
catkin build
source devel/setup.bash
roslaunch mobile nav2.launch
```

![z7592480760724_782c67b5b85e69946a96587810b7c8fa](https://github.com/user-attachments/assets/a3f0c3b5-cc5c-4765-b17e-283b071e3138)

