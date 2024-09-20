# ROS File System

2023-03-02

The Robot Operating System (ROS) is a flexible and powerful platform for developing software components for robotic systems. At its core, ROS operates through a network of nodes that communicate with each other, with these nodes organized into packages. These packages follow a specific file system convention recommended by Open Robotics, the organization behind ROS. A package serves as a root directory containing all the ROS-related files necessary for a particular project. In this article, we will explore the ROS file system and what you can expect to find within these packages. Understanding the ROS file system is crucial for the efficient development and organization of robotic software.

## ROS Package

At the most fundamental level, nodes are the smallest executable building blocks of ROS. These nodes are designed to carry out specific tasks, such as control, navigation, and more, and they communicate with each other through messages. Nodes that serve similar purposes are typically grouped within a ROS package. A node generally consists of source code, messages, and services.

## Manifest Files

ROS packages contain important files known as manifests, such as `package.xml` and `CMakeLists.txt`, which provide metadata and essential information about the ROS node.

### package.xml

This file defines properties about the package such as the package name, version numbers, authors, maintainers, and dependencies on other catkin packages. Every single ROS node must contain one `package.xml` file.

### CMakeLists.txt

This file serves as an input to the CMake build system, which is used for building software packages. Any CMake-compliant package contains one or more `CMakeLists.txt` files that describe how to compile the code and where to install it. The `CMakeLists.txt` file used in a Catkin project is essentially a standard CMakeLists file with a few additional constraints. Like package.xml, every ROS package must include a `CMakeLists.txt` file.

## Source Code and Assets

Source code files that are part of ROS nodes, typically written in C++ or Python, should be placed in a folder named `src`, which is specifically designated for source code. Any script files that are not directly part of a node should be stored in a separate `scripts` folder.

Descriptions of request and response data structures for services provided by each ROS process are stored in the `srv` folder. Similarly, custom messages used by nodes should be placed in the `msg` folder.

Files that define how to start a ROS node are called launch files, and these are essential for initiating ROS nodes as specified. The ROS core uses these launch files to start the nodes.

The Gazebo simulation tool requires certain asset files, such as `.world` files and .urdf files. The `.world` files define the 3D simulation environment, while the `.urdf` files specify the robot model. These files should be placed in the `worlds` folder.

The overall folder structure typically looks as follows:


    └── dummy_ros_pkg
    ├── README.md
    ├── CMakeLists.txt
    ├── package.xml
    ├── launch
    │   └── robot.launch
    ├── worlds
    │   └── sim.world
    └── src
        ├── foo_node.cpp
        └── bar_node.py
    │
    └── scripts
            ├── foo_scipt.py
            └── bar_script.py
    │
    ├── msg
            └── dummy.msg

## References
*   [1] [https://hub.packtpub.com/ros-architecture-and-concepts/#:~:text=Similar%20to%20an%20operating%20system,create%20a%20program%20within%20ROS.](https://hub.packtpub.com/ros-architecture-and-concepts/#:~:text=Similar%20to%20an%20operating%20system,create%20a%20program%20within%20ROS.)