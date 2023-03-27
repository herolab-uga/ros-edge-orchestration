
 # ROS-EDGE-ORCHESTRATION #

A ROS-based package for utility-aware dynamic task offloading framework based on a multi-edge-robot system that takes into account computation, communication, and task execution load at the edge devices to minimize the overall service time for delay-sensitive applications.

#### Requirement: ####
This package is distributed on following nodes:
* 3 Edge devices(SBCs) - Nvidia Jetson nanos 
* 3 Turtlebot3s spawned on Gazebo Simulator - Local Machine


## Overview ##
Continuous device, network and task profilers are continuously running on edge devices. For each task assigned, an edge with maximum utility is derived using a utility maximization technique with weights variation and a system reward assignment for task connectivity or sensitivity. A scheduler is in charge of task assignment, whereas an executor is responsible for task offloading on edge devices. 

* Credit for spawning multiple turtlebot3 in Gazebo ROS Noetic goes to [hikashi](https://github.com/hikashi/multi-robot-rrt-exploration-noetic/tree/main/ros_multi_tb3 "multi-robot-rrt-exploration-noetic") 
* Credit for the use of ROS-Yolov5 package goes to [mats-robotics](https://github.com/mats-robotics/yolov5_ros "YOLOv5 ROS")


## Installation Prerequisites ## 
This package is built and tested on Ubuntu 20.04 LTS and ROS Noetic with Python 3.8.
The following libraries are required to install before proceeding to run the code

```
$ sudo apt-get install ros-noetic-gmapping
$ sudo apt-get install ros-noetic-navigation
$ sudo apt-get install python-numpy
$ sudo apt-get install python-scikits-learn
$ sudo apt-get install ros-noetic-teb-local-planner
$ sudo apt-get install ros-noetic-multirobot-map-merge
$ sudo apt-get install ros-noetic-yolov5-ros
```

## Installation Process ## 
For interoperability, all the edge devices and the robots should have the same operating system. The following package should be installed on all four machines in the system. 

```
$ sudo mkdir -p ~/catkin_ws/src
$ cd ~/catkin_ws/src/
$ git clone https://github.com/herolab-uga/ros-edge-orchestration.git
$ cd ~/catkin_ws
$ catkin_make
```

## Execution for Collaborative Multirobots Object Detection and Pose Estimation ##

### Launching robots in Gazebo - Local Machine ###

```
 $ source ~/catkin_explore/devel/setup.bash 
 # export TURTLEBOT3_MODEL=waffle_pi
 $ roscore 
```
The following launch file would launch three turtlebot3s with gmapping in Gazebo world. 
```
roslaunch edge_robot task_setup.launch
```
For pose publishing and way points for navigation 
```
roslaunch edge_robot all_pose_publishers.launch
roslaunch edge_robot all_wps.launch
``` 

### Task profilers - Edge Devices ### 
To be launched on each edge device. 

e.g. on edge 1, use the following launch file:
```
roslaunch edge_robot e1_profilers.launch
```
on edge 2:
```
roslaunch edge_robot e2_profilers.launch
```
on edge 3: 
```
roslaunch edge_robot e3_profilers.launch
```
### Preinitialized tasks on edge devices ###
on edge 1:
```
roslaunch edge_robot tb3_0_nav.launch
roslaunch edge_robot tb3_0_yolov5.launch
```
on edge 2: 
```
roslaunch edge_robot tb3_1_nav.launch
roslaunch edge_robot tb3_1_yolov5.launch
```
on edge 3:
```
roslaunch edge_robot tb3_2_nav.launch
roslaunch edge_robot tb3_2_yolov5.launch
```
## Scheduler on local Machine ## 
Launch the following for setting the mode of the scheduler variant. This launch file takes in the parameters from the config/task_req_yolo_obj.yaml which are predefined for the task tested. It launches the python scripts for Gateway, Scheduler and the Executor. 
```
roslaunch edge_robot scheduler.launch
``` 
## Contributors ## 
* Nazish Tahir - PhD Candidate
* Dr. Ramviyas Parasuraman - Lab Director

## Heterogeneous Robotics (HeRoLab) ##
#### Heterogeneous Robotics Lab (HeRoLab), School of Computing, University of Georgia. ####

For further information, contact Nazish Tahir nazish.tahir@uga.edu or Dr. Ramviyas Parasuraman ramviyas@uga.edu

https://hero.uga.edu/
