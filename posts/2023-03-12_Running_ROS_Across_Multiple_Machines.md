# Running ROS Across Multiple Machines

2023-03-12

The Robot Operating System (ROS) is an open-source framework widely used in robotics research and development for building, developing, and deploying robot software. In both development and deployment, there may be situations where you need to access a robot's computational resources remotely. For example, in multi-robot systems, individual robots often need to communicate over a shared network to collaboratively solve tasks. To enable this, ROS instances running on different machines must be configured to communicate, provided that all machines are connected to the same network.

This tutorial will walk you through the process of setting up ROS to communicate over a local area network (LAN) with multiple machines. This setup is useful for creating a network of machines - whether they represent robots or workstations - working together under ROS.

## Configuring ROS for LAN Communication

To properly configure ROS across multiple machines in a LAN, consider the following key points:
* Only one master is needed, so choose a single machine to run `roscore`.
* All nodes must be set to use the same master by configuring the `ROS_MASTER_URI` environment variable.
* Bi-directional connectivity between all machines is crucial for communication.
* Each machine must advertise itself using a hostname that all other machines can resolve.

For example, let's say you're connecting your workstation to a robot to retrieve and store sensor readings. In this setup, we'll refer to the machines as the robot (master) and the workstation (slave). The robot and workstation will have symbolic IP addresses of `192.168.0.1` and `192.168.0.2`, respectively.

### Testing Network Connectivity

To verify that both the master and slave are connected to the same network, you can use the `ping` command. Open a terminal on either machine and ping the IP address of the other device to check connectivity.

**Robot (master):**
    
    ping 192.168.0.2
**Workstation (slave):**

    ping 192.168.0.1

### Testing Port Connectivity

For full connectivity, machines must be able to communicate over all necessary ports. To ensure this, you can use the `netcat` (`nc`) command in the terminal of either machine as shown below:

**Robot (master):**
    
    netcat -l 1234
    netcat 192.168.0.2

**Workstation (slave):** 

    netcat -l 1234
    netcat 192.168.0.1

### Configuring Name Resolution

For machines to communicate effectively over the network, they must have addressable names, typically in the form of hostnames. Follow the steps below to configure name resolution from the terminal of each machine:

**Robot (master):**

    export ROS_IP=192.168.0.1
    export ROS_HOSTNAME=192.168.0.1

**Workstation (slave):**

    export ROS_IP=192.168.0.2
    export ROS_HOSTNAME=192.168.0.2

Alternatively, you can modify the `/etc/hosts` file on each machine to manually associate hostnames with their corresponding IP addresses. This file serves as a local directory that instructs each machine on how to resolve specific hostnames into IP addresses, ensuring reliable communication between machines on the network.

    sudo nano /etc/hosts
    192.168.0.1 robot
    192.168.0.2 workstation

Now, we can refer to the machines by their hostnames, robot and workstation, for communication.

## Connecting Machines in LAN

Once all configurations are in place, the machines are ready to communicate with each other over the network, enabling seamless interaction and data exchange.

**Robot (master):**

    export ROS_MASTER_URI=http://robot:11311 
    roscore && rosrun rospy_tutorials listener.py

**Workstation (slave):**

    export ROS_MASTER_URI=http://robot:11311 
    rosrun rospy_tutorials talker.py

In this article, we covered how to configure ROS to run across multiple machines, enabling seamless communication over a network. I hope this guide proves useful in setting up your ROS projects and facilitates efficient multi-machine operations.

## References

* [1] https://wiki.ros.org/ROS/Tutorials/MultipleMachines
* [2] https://wiki.ros.org/ROS/NetworkSetup#Configuring_.2Fetc.2Fhosts