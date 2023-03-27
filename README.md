
 # ROS-EDGE-ORCHESTRATION #

A utility-aware dynamic task offloading framework based on a multi-edge-robot system that takes into account computation, communication, and task execution load at the edge devices to minimize the overall service time for delay-sensitive applications.
Requirement: 

This package is distributed as follows:
* 3 Edge devices(SBCs) - Nvidia Jetson nanos 
* 3 Turtlebot3s spawned on Gazebo Simulator - Local Machine


## Overview ##
Continuous device, network and task profilers are continuously running on edge devices. For each task assigned, an edge with maximum utility is derived using a utility maximization technique with weights variation and a system reward assignment for task connectivity or sensitivity. A scheduler is in charge of task assignment, whereas an executor is responsible for task offloading on edge devices. 

Credit for the use of ROS-Yolov5 package goes to [mats-robotics](https://github.com/mats-robotics/yolov5_ros "YOLOv5 ROS")


## Installation Prerequisites ## 
The following code is exectuted in ROS Melodic in Ubuntu 20.04 LTS
The following libraries are required to install before proceeding to run the code

```
$ sudo apt-get install ros-noetic-gmapping
$ sudo apt-get install ros-noetic-navigation
$ sudo apt-get install python-numpy
$ sudo apt-get install python-scikits-learn
$ sudo apt-get install ros-noetic-teb-local-planner
$ sudo apt-get install ros-noetic-multirobot-map-merge
```

## Installation Process ## 
For interoperability, all the edge devices and the robots should have the same operating system. The following package should be installed on all four machines in the syste,. 
```
$ sudo mkdir -p ~/catkin_ws/src
$ cd ~/catkin_ws/src/
$ git clone https://github.com/herolab-uga/ros-edge-orchestration.git
$ cd ~/catkin_ws
$ catkin_make
```
