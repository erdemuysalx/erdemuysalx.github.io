# SLAM and Navigation in ROS

2023-03-07

Can you imagine a robot that cannot locate itself, map its surroundings, or navigate? Such a robot would hardly be useful. These essential capabilities make robots indispensable in many applications. But does every robotics software developer need to be an expert in SLAM (Simultaneous Localization and Mapping) and navigation, which are distinct research areas, to implement these features? Fortunately, the answer is no, thanks to ROS.

In this article, we will explore how to tackle complex tasks such as SLAM and navigation using ROS. Even if these topics are not directly applicable to your specific robot, I believe this guide will serve as a valuable starting point and help you build a solid technical foundation.

## SLAM and Navigation Using ROS

While SLAM and navigation are complex and challenging fields, ROS simplifies them conceptually and provides algorithms that can be integrated into your robotics application with minimal adjustments. Some commonly used algorithms and nodes include:

* [amcl](http://wiki.ros.org/amcl)
* [gmapping](http://wiki.ros.org/gmapping)
* [move_base](http://wiki.ros.org/move_base)

Behind the scenes, ROS processes data from odometry and sensors, such as LiDAR or cameras, converting this information into velocity commands that are sent to the robot's controller. However, implementing ROS's navigation algorithms on an arbitrary robot can be more involved. Before starting navigation, the robot must be running ROS, have a properly configured TF transform tree, and publish odometry and sensor data using the appropriate ROS message types.

## Essential Requirements for Effective Robot Navigation

Before a robot can navigate effectively, several prerequisites must be met to ensure smooth operation and accurate performance. These include:

* **URDF (Universal Robot Description File)**: The robot's URDF must be error-free, as it provides a detailed description of the robot's physical structure, which is essential for proper navigation.
* **Localization:** The robot needs to know its exact position relative to its environment. This can be achieved using various sensors, such as LiDAR or cameras, to accurately localize the robot.
* **Obstacle Avoidance:** During navigation, unexpected obstacles may appear. The robot should be capable of detecting and dynamically avoiding these obstacles in real-time.
* **Path Planning:** To move from point A to point B, the robot must be able to calculate an efficient and collision-free route using path planning algorithms.

## Configuring the Robot for the ROS Navigation Stack
The ROS Navigation Stack comprises several essential components that work together to enable a robot to move autonomously. Each component plays a critical role in ensuring accurate localization, path planning, and motion control. Below is an explanation of the key components in the navigation stack:

* **Sensor Transforms (tf):** The data collected from various sensors must be referenced to a common frame, typically base_link, to accurately compare information from different sensors. The robot should publish the relationship between its main coordinate frame and its sensors' frames using ROS tf.
* **Sensor Sources:** Sensors serve two main purposes in navigation: localizing the robot on the map (e.g., using a laser scanner) and detecting obstacles in its path (using lasers, sonars, or point clouds).
* **Odometry Source:** Odometry data provides the robot's position relative to its starting point. The main sources of odometry are wheel encoders, IMUs, and 2D/3D cameras (for visual odometry). The odometry value must be published to the navigation stack using the nav_msgs/Odometry message type, which can contain both the robot's position and velocity.
* **Base Controller:** The base controller's primary function is to take the output of the navigation stack (a geometry_msgs/Twist message) and convert it into motor commands, setting the robot's velocity to execute the desired motion.

![ROS navigation stack](https://wiki.ros.org/navigation/Tutorials/RobotSetup?action=AttachFile&do=get&target=overview_tf_small.png)

If you haven't done so already, create a new package named robot_navigation inside the workspace ros_ws:

    cd .../ros_ws/src
    catkin_create_pkg robot_navigation std_msgs roscpp

### Implementing SLAM Using the gmapping ROS Node

ROS provides powerful tools to assist in the SLAM process, such as acml and gmapping, for enabling robots to understand and navigate their environments which uses SLAM techniques to build a map from sensor data. Below are the steps required to configure and run the gmappingnode for SLAM purposes.

**Step 1.** Create a new file named `gmapping.launch` in the package `robot_navigation`, located in the folder `.../robot_navigation/launch`. Paste the code below into gmapping.launch:

    <launch>

    <arg name="use_gazebo" default="false" />

    <!-- Gazebo -->
    <group if="$(arg use_gazebo)">
        <param name="use_sim_time" value="true" />
        <include file="$(find robot_bringup)/launch/robot.launch">
            <arg name="world" value="maze" />
        </include>
    </group>

    <!-- SLAM -->
    <node pkg="gmapping" type="slam_gmapping" name="gmapping">
        <param name="base_frame"            value="base_link"/>
        <param name="odom_frame"            value="odom" />
        <param name="map_update_interval"   value="3.0"/>
        <param name="maxUrange"             value="15.0"/>
    </node>

    <!-- Teleoperation - keyboard control -->
    <node pkg="teleop_twist_keyboard" type="teleop_twist_keyboard.py" name="teleop_twist_keyboard" output="screen"/>

    </launch>

**Step 2.** Configure parameters such as `base_frame, odom_frame, map_update_interval, maxUrange` manually in the launch file according to your hardware. Alternatively, you can write parameters into the gmapping.yaml file and link it to the launch file:

    <rosparam file="$(find gmapping_package)/launch/gmapping.yaml" command="load"/>

**Step 3.** Launch the gmapping node:

    roslaunch robot_navigation gmapping.launch

**Step 4.** Track the map in RViz: 

    rosrun rviz rviz

**Step 5.** Using the teleop_twist_keyboard node and your PC's keyboard, drive the mobile robot around to build a complete map of the environment in which it operates.

**Step 6.** Once the mapping is complete, save the map:

    rosrun map_server map_saver -f map

This will generate two files:

* A PGM image file of the map
* A YAML file containing metadata about the map

**Step 7.** To make the map available to other nodes, serve the map data by running the following ROS service:

    rosrun map_server map_server map.yaml

This will create two topics: `/map` and `/map_metadata`, which other nodes can subscribe to.

### Implementing Navigation Using move_base ROS Node

In ROS, path planning is performed using the occupancy map, previously generated by the gmapping node. The next step is to create a cost map, which allows for the calculation of an optimal trajectory. Once the best path is identified, appropriate control mechanisms can be applied to follow the path efficiently. Both path planning and velocity control are managed by the move_base node. This node utilizes two cost maps-one for the global planner and another for the local planner (from the [costmap_2d](https://wiki.ros.org/costmap_2d) package). These components need to be properly configured to enable the move_base node to function effectively. Below are the steps to configure and run the move_base node for navigation.

**Step 1.** The first component of the move_base node is the cost map. The cost map is a grid where each cell is assigned a value representing the "cost" based on its distance from obstacles. The closer the obstacle, the higher the cost. Two types of costs are used:

* Global Cost Map: Helps the global planner calculate the shortest path between two points using previously gathered sensor data.
* Local Cost Map: Assists the local planner in dynamically controlling smaller sections of the path.

To configure the costmap parameters, create and edit the following files.

`/robot_navigation/config/costmap_common.yaml` for common cost map parameters:

    global_frame: map
    robot_base_frame: base_link
    footprint: [[0.14, 0.14], [0.14, -0.14], [-0.14, -0.14], [-0.14, 0.14]]
    rolling_window: true

    inflation_radius: 0.5
    cost_scaling_factor: 4.0

    track_unknown_space: true
    observation_sources: scan
    scan: {sensor_frame: laser, data_type: LaserScan, topic: scan, marking: true, clearing: true}

`/robot_navigation/config/costmap_global.yaml` for global cost map parameters:

    global_costmap:
        update_frequency: 2.0
        publish_frequency: 1.0

        obstacle_range: 5.0
        raytrace_range: 5.0
        static_map: true

        width: 15.0
        height: 15.0

`/robot_navigation/config/costmap_local.yaml` for local cost map parameters:

    local_costmap:
        update_frequency: 5.0
        publish_frequency: 2.0

        obstacle_range: 2.5
        raytrace_range: 2.5
        static_map: false

        width: 2.5
        height: 2.5
        resolution: 0.02

**Step 2.** The second component of the move_base node is the planner. The planner's role is to reach the target position while avoiding obstacles within a user-defined tolerance. It uses the costmap to generate a path through the cells with the lowest cost. The move_base node utilizes two planners:

* Global Planner: Finds the optimal path using the global costmap.
* Local Planner: Selects controls to guide the robot along the path by adjusting velocities.

Configure the planner parameters in the following files:

`/robot_navigation/config/planner_global.yaml` for global planner parameters:

    base_global_planner : navfn/NavfnROS

`/robot_navigation/config/planner_local.yaml` for local planner parameters:

    base_local_planner: base_local_planner/TrajectoryPlannerROS

    TrajectoryPlannerROS:
        min_vel_x: 0.1
        max_vel_x: 0.3
        min_vel_theta: -0.7
        max_vel_theta: 0.7
        min_in_place_vel_theta: 0.4
        escape_vel: -0.1

        acc_lim_theta: 1.0
        acc_lim_x: 1.0

        holonomic_robot: false

        xy_goal_tolerance: 0.1
        yaw_goal_tolerance: 0.2

        meter_scoring: true
        path_distance_bias: 20
        goal_distance_bias: 15
        occdist_scale:  0.01

        sim_time: 2.0

**Step 3.** Now that the cost maps and planners are configured, create a new file named `move_base.launch` in the `robot_navigation` package, located in the folder `.../robot_navigation/launch`. Insert the following code into `move_base.launch`:

    <launch>

    <arg name="use_gazebo" default="false" />
    <arg name="map_name" default="map.yaml"/>

    <!-- Localization -->
    <include file="$(find robot_navigation)/launch/gmapping.launch">
        <arg name="use_gazebo" value="$(arg use_gazebo)" />
        <arg name="map_name" default="$(arg map_name)"/>
    </include>

    <!-- Path planning -->
    <node pkg="move_base" type="move_base" respawn="false" name="move_base" output="screen">
        <rosparam file="$(find robot_navigation)/config/move_base.yaml" command="load" />
        <rosparam file="$(find robot_navigation)/config/costmap_common.yaml" command="load" ns="global_costmap" />
        <rosparam file="$(find robot_navigation)/config/costmap_common.yaml" command="load" ns="local_costmap" />
        <rosparam file="$(find robot_navigation)/config/costmap_global.yaml" command="load" />
        <rosparam file="$(find robot_navigation)/config/costmap_local.yaml" command="load" />
        <rosparam file="$(find robot_navigation)/config/planner_global.yaml" command="load" />
        <rosparam file="$(find robot_navigation)/config/planner_local.yaml" command="load" />
    </node>

    <node pkg="rviz" type="rviz" name="rviz" args="-d $(find robot_navigation)/rviz/move_base.rviz"/>

    </launch>

**Step 4.** Launch the move_base node:

    roslaunch robot_navigation move_base.launch

In this article, we covered the essential steps to set up SLAM and navigation in ROS using the gmappingand the move_base nodes. By leveraging ROS's navigation stack, you can create autonomous robots capable of localization, mapping, and navigation in dynamic environments. While additional tuning might be required for specific applications, this guide provides an introductory foundation to get you started on your ROS navigation journey.

## References

* [1] [https://wiki.ros.org/navigation/Tutorials/RobotSetup](https://wiki.ros.org/navigation/Tutorials/RobotSetup)
* [2] [https://wiki.ros.org/map_server](https://wiki.ros.org/map_server)
* [3] [http://wiki.ros.org/costmap_2d](http://wiki.ros.org/costmap_2d)
* [4] [https://husarion.com/tutorials/ros-tutorials/8-slam/](https://husarion.com/tutorials/ros-tutorials/8-slam/)
* [5] [https://husarion.com/tutorials/ros-tutorials/9-navigation/#cost-map](https://husarion.com/tutorials/ros-tutorials/9-navigation/#cost-map)
* [6] [https://web.fs.uni-lj.si/lampa/rosin/ROS%20Summer%20School/Day%203/mapping/#](https://web.fs.uni-lj.si/lampa/rosin/ROS%20Summer%20School/Day%203/mapping/#)