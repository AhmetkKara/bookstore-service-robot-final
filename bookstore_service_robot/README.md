# Bookstore Service Robot - QR Verified Navigation

This project was developed for the Introduction to Robotics final assignment.

The robot operates in the AWS RoboMaker Bookstore Gazebo environment. It uses SLAM for mapping, AMCL and move_base for navigation, and QR code verification for task completion.

## Platform

* ROS1 Noetic
* Gazebo
* TurtleBot3 Waffle Pi
* AWS RoboMaker Bookstore World
* Python
* OpenCV QRCodeDetector

## Project Features

* Gazebo bookstore simulation environment
* TurtleBot3 Waffle Pi robot with RGB camera
* SLAM map creation
* Saved map files in `maps/`
* AMCL localization
* Navigation with `move_base`
* Multi-task waypoint system
* QR verification at each task point
* Timeout and retry handling
* Mission report generation

## Repository Structure

```text
bookstore_service_robot/
├── config/
│   └── mission.yaml
├── launch/
│   ├── simulation.launch
│   ├── slam.launch
│   ├── navigation.launch
│   └── task_manager.launch
├── maps/
│   ├── map.yaml
│   └── map.pgm
├── models/
│   ├── qr_checkout_area/
│   ├── qr_information_desk/
│   ├── qr_novel_section/
│   ├── qr_science_section/
│   └── qr_images/
├── reports/
│   └── mission_report.txt
├── src/
│   ├── task_manager.py
│   └── qr_reader.py
├── CMakeLists.txt
├── package.xml
└── README.md
```

## Task Locations

The mission includes four task locations:

* NOVEL_SECTION
* CHECKOUT_AREA
* SCIENCE_SECTION
* INFORMATION_DESK

The waypoint coordinates and expected QR messages are stored in:

```text
config/mission.yaml
```

## How to Run

### 1. Build the Workspace

```bash
cd ~/bookstore_final_ws
catkin_make
source devel/setup.bash
```

### 2. Start Simulation

```bash
source ~/bookstore_final_ws/devel/setup.bash
roslaunch bookstore_service_robot simulation.launch
```

### 3. Start Navigation

Open a new terminal:

```bash
source ~/bookstore_final_ws/devel/setup.bash
roslaunch bookstore_service_robot navigation.launch
```

After RViz opens, set the robot initial pose using **2D Pose Estimate**.

### 4. Start Task Manager and QR Reader

Open a new terminal:

```bash
source ~/bookstore_final_ws/devel/setup.bash
roslaunch bookstore_service_robot task_manager.launch
```

The task manager sends navigation goals, waits for the robot to reach the target, verifies the QR code, and then continues to the next task.

### 5. Show Mission Report

```bash
cat ~/bookstore_final_ws/src/bookstore_service_robot/reports/mission_report.txt
```

## SLAM and Map Saving

To create a map, run the simulation and SLAM:

```bash
roslaunch bookstore_service_robot simulation.launch
roslaunch bookstore_service_robot slam.launch
```

After mapping, save the map:

```bash
rosrun map_server map_saver -f ~/bookstore_final_ws/src/bookstore_service_robot/maps/map
```

## ROS Topics

Important topics used in the project:

* `/camera/rgb/image_raw`
* `/qr_text`
* `/cmd_vel`
* `/map`
* `/amcl_pose`
* `/move_base/goal`
* `/move_base/status`

## ROS Action

The task manager uses the `/move_base` action server to send navigation goals.

## Nodes

### task_manager.py

* Reads task locations from `mission.yaml`
* Sends goals to `move_base`
* Waits for navigation result
* Verifies QR code after reaching the goal
* Handles timeout and retry logic
* Saves the final report

### qr_reader.py

* Subscribes to the camera image topic
* Detects QR codes using OpenCV
* Publishes detected QR text to `/qr_text`

## Error Handling

The system supports:

* Navigation timeout
* Navigation retry
* QR timeout
* QR retry
* SUCCESS / SKIPPED / FAIL report output

## Demo Video

The demo video should show:

1. Gazebo bookstore world
2. RViz map and localization
3. Navigation to task points
4. QR code verification
5. Final mission report

