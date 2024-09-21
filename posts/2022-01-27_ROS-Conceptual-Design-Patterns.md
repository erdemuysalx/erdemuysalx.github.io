# ROS Conceptual Design Patters

2022-01-27

Throughout my career, I've had the opportunity to work with robotics on several occasions, and it has become a passion of mine. This enthusiasm has inspired me to start a new series of articles focused on robotics. In this series, I will primarily concentrate on robotics software and control, rather than the hardware aspects.

To kick off this series, I decided to write an introductory article on the Robot Operating System (ROS). Although there are already many resources available on ROS, I believe that providing an overview will be a fitting way to begin this journey into robotics.

The content of this article will cover the following topics:

*   Overview of ROS
*   ROS Concepts and Design Patterns
*   ROS vs ROS 2

![NASA Opportunity Mars Exploration Rover. The figure is taken from https://www.jpl.nasa.gov/missions/mars-exploration-rover-opportunity-mer/](https://cdn-images-1.medium.com/max/800/1*9qtOzaq_LiIJ33lqaw5X8g.jpeg)

## Overview of ROS

What exactly is ROS? Despite what its name might suggest, ROS is not a traditional operating system. While it provides utility functions similar to those of a general-purpose operating system - such as hardware abstraction, low-level hardware control, interprocess message-passing, and package management - it is a middleware suite, not a true operating system.

As a middleware suite, ROS offers developers a collection of software frameworks, libraries, and tools designed to facilitate the development of robust robotics applications that can integrate with diverse hardware and software clusters.ROS Concepts and Design Patterns

## Understanding ROS Conceptual Design Patterns

This subtitle introduces the reader to the conceptual design patterns within the ROS framework and provides context for the detailed explanations that follow.

### Nodes

In ROS, the fundamental building blocks are called nodes. Each node is responsible for specific tasks, such as controlling devices and sensors or executing computational algorithms. Ideally, each node handles a separate task, whether it's for low-level processes like hardware control or high-level processes like decision-making algorithms. Nodes communicate with each other through topics or services, enabling a modular and distributed architecture.

There are two primary types of nodes: publishers and subscribers. As the names suggest, publishers are responsible for sending messages to topics, while subscribers receive messages from these topics by subscribing to them. This structure allows ROS to efficiently manage and distribute software across different nodes.

### Topics

Inter-node communication in ROS is facilitated through topics. A topic is a communication channel that describes a data stream used to exchange information between different nodes. Topics are used to send streams of messages of a single type, such as sensor data or camera images. Nodes can publish messages to topics or subscribe to them to receive messages.

The number of nodes that can publish to or subscribe to a topic is generally limited by system resources, particularly RAM. Each topic has a unique name and a defined message type, ensuring that the correct data is routed to the appropriate nodes. In ROS 1, the relationship between nodes and topics is managed by the ROS master, while in ROS 2, this role is handled by the Data Distribution Service (DDS), a management middleware.

### Services

Services in ROS provide an alternative communication method between nodes, resembling the server-client architecture model, similar to a remote procedure call (RPC). In this setup, a client node sends a request, and a server node responds to that request. This establishes a bidirectional communication channel between the client and server nodes. However, unlike topics, which allow continuous data streaming, services are designed for one-time communication and are typically used to invoke specific actions.

### Actions

For tasks that require time-extended operations, ROS introduces the concept of actions. Actions are designed to handle more complex tasks that go beyond the immediate request-response model of services. A ROS action is defined by three key messages: goal, result, and feedback.

*   **Goal**: This message represents the desired state or objective that the action aims to achieve.
*   **Result**: This message provides the actual output or outcome after the action has been completed.
*   **Feedback**: This message is sent periodically during the execution of the action to track and report the progress of the task.

### Parameters

In ROS, the robot's environment and runtime variables are stored on the ROS parameter server. These parameters are organized as key-value pairs, similar to dictionary data structures. Since the parameter server is not optimized for high-performance operations, it is best suited for managing configuration parameters, such as static, and non-binary data.

### ROS Package

A ROS package is typically developed to perform a specific task, such as control or navigation. A package can contain one or multiple nodes, and it may also include related messages and services. Each package is designed to encapsulate all the necessary components to accomplish its designated task.

## ROS vs ROS 2

In recent years, intensive efforts have been made within the Open Source Robotics Foundation's (OSRF) ROS community to enhance the durability and real-time sensitivity of ROS. These efforts are now bearing fruit, leading to the release of a new generation of ROS, known as ROS 2.

The primary difference between ROS 2 and its predecessor, ROS, lies in the underlying communication architecture. In ROS 2, the publisher/subscriber communication model has shifted from the TCP/UDP multicast-based ROS master to the Data Distribution Service (DDS). DDS provides powerful features that significantly strengthen ROS 2's capabilities, making it more suitable for designing production-grade, real-time robotic systems.

Moreover, ROS 2 offers broader compatibility with operating systems, including Windows, macOS, and Real-Time Operating Systems (RTOS), expanding its usability across different platforms.

![ROS vs ROS 2 component stack](https://cdn-images-1.medium.com/max/800/1*S2Aeb4GlN-Y7QKMcU1t5Bg.png)

## ROS Computation Graph

Let's consider designing a robot that follows a particular object using its onboard sensors. The system we need to build involves several components:

*   Camera Device: To capture images of the object, the robot requires a camera.
*   Perception System: This system processes the camera images to determine the object's location. It analyzes the visual data to extract relevant information about the object's position.
*   Control System: Based on the information from the perception system, the control system makes decisions about the direction in which the robot should move. It translates the object's location into movement commands.
*   Motors: To execute these commands, the robot uses motors that drive the wheels and allow the robot to move toward the object.

Using ROS, we might construct this system as follows:

![Example computation graph](https://cdn-images-1.medium.com/max/800/1*PnKf4vFYdGXq8h0VDFr-cQ.png)

Each subsystem in our robot design can be represented as a ROS node. Therefore, we will have four distinct nodes, each handling a specific executable function:

*   Camera Driver Node: This node is responsible for fetching raw images from the camera device and publishing these images to the relevant topic.
*   Object Detector Node: This node subscribes to the topic where raw images are published. It processes these frames to extract useful information about the object being followed, such as its location. The node then publishes this information to another topic with an appropriate message type.
*   Target Follower Node: Based on the object location data received from the object detector node, this node calculates the commands required to steer the robot toward the object. It subscribes to the object location topic, processes the information, and publishes movement commands to a separate topic.
*   Motor Driver Node: This low-level control node receives movement commands from the target follower node and uses them to control the motors, thereby steering the robot's wheels.

This concludes the discussion on ROS Conceptual Design Patterns, which is the first article in our robotics series. In my next posts, I plan to delve into the ROS file system and the ROS navigation stack. Stay tuned!

## References

* [1] [http://wiki.ros.org/](http://wiki.ros.org/)
* [2] [https://index.ros.org/doc/ros2/](https://index.ros.org/doc/ros2/)
* [3] [http://wiki.ros.org/gazebo](http://wiki.ros.org/gazebo)
* [4] Quigley, Morgan, et al. “ROS: an open-source Robot Operating System.” ICRA workshop on open source software. Vol. 3. №3.2. 2009.