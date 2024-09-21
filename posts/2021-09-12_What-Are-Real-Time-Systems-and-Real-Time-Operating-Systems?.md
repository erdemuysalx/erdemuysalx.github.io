# What Are Real Time Systems and Real Time Operating Systems?

2021-09-12

![The figure is taken from https://www.wallpaperbetter.com/de/hd-wallpaper-fuhzp](https://cdn-images-1.medium.com/max/800/1*wc2mgaPW9wianNSrXf951Q.jpeg)

Hello, everyone. In this article, I will talk about what is a real-time, real-time system, and real-time operating system means. This article will be relatively different from the others and I will be explaining the meanings of a few terms. I think it is a big plus for us to be developing our technical thesaurus because; even if we do not use these terms directly, someday if we are involved in a project that uses some of these terms, and if we encounter a problem when the day comes, we can easily find out which term it originated from and find the relevant solution by researching this term. In summary, when we have a wide technical term treasury, it saves us time and speed in our projects and makes it easier for us to detect errors. Now let’s move on to our main topic.

## What is a Real-Time System?

In fact, we can summarize it as follows; the systems that produce an output in a certain time to the inputs from outside are called real-time systems. For example; unmanned aerial vehicles react in a very short time to the commands we give from the radio controller. Therefore, unmanned aerial vehicles are real-time systems, in the same way, the airbags in our cars are real systems since they produce instantaneous responses to the given input. Examples of non-real-time systems would be computers or washing machines. Because in these systems, there is no concern about producing instant output to the given input. It is an important distinction in terms of design that the system we will design is real-time or not real-time because there are differences between designing real-time systems and designing non-real-time systems.

There are two types of real-time systems;

*   **Hard Real-Time:** The degree of tolerance of a possible delay in the completion of the tasks to be performed by the system is very low (zero or a manufacturer-defined threshold). Tasks that cannot be completed on time are critical to the system and have devastating effects.
*   **Soft Real-Time:** The completion time of the tasks to be performed by the system is not as critical as in hard real-time or the system can tolerate it during the latency period.

Response time does not determine whether a system is hard or soft in real time. The criterion that determines this is what happens if the system does not respond. For example, a video game that we play at 60 FPS will draw the graphics in 1/60th of a second after our commands, but if the drawing process is delayed for any reason, this will not have a devastating effect. Of course, it will affect the efficiency of playing the game, but it is not a critical problem, it can be ignored depending on the situation. But if we are talking about a competitive esports game, the consequences of delays in the game can be seen as devastating, so we can also assume it is as a hard real-time system. Unlike video games, if surgical robots or airbag systems respond later than the threshold response time set by the manufacturer, it can cause that patient or driver injury or even death, so such situations are very critical.

Below are examples of hard real-time and soft real-time.

*   **Hard Real-Time:** A medical robot, a surgical robot. If it cannot respond to the inputs given by the doctor within the specified time (milliseconds, microseconds), it is very inefficient, and devastating results may occur. The response time must be under a certain limit.
*   **Soft Real-Time:** In a video game, when we give input from the keyboard to give the jump command to the character, the jump animation graphics drawn on the screen, based on 30 FPS, should be drawn on the screen in 1/30th of a second after the command we give, which is soft real-time.

### Throughput vs Latency

It is very important to understand these two terms. In a team discussion or product demonstration, we need to understand what is meant when the statement “We made concessions from delay to increase the transfer speed”. Now let’s try to understand these two terms.

**Latency:** The time it takes for a package to be transported to its destination.

For example, if we consider the package as a physical product on the conveyor belt, the time taken for the package to complete its operations on the conveyor belt and exit the belt is equivalent to a delay. Or, when we click to open a new page on a website, the time it takes for the data packet of the page to be opened from the server to the client is called latency.

**Throughput:** The number of packets sent and received per unit time.

If we continue with the conveyor belt example, the number of packages that will leave the conveyor belt at one time, let’s say one minute, after the first package reaches the destination, gives the transfer rate. Likewise, the total amount of packets that a web server sends to the client in one minute is also called the transfer rate.

Below is a visualization of the terms latency and throughput in the web server-client example.

![Latency vs throughput. The figure is taken from https://www.comparitech.com/net-admin/latency-vs-throughput/](https://cdn-images-1.medium.com/max/800/0*R7LoaJr0M-l0jILV.jpeg)

### OS and RTOS

### What is an Operating System (OS)?

An operating system is a computer program that supports the basic functions of the computer and serves other programs and applications running on the computer. Applications provide the functionality that the computer user wants or needs, while the services provided by the operating system make the execution of applications faster, simpler, and easier. For example, if you are reading a web page, you are using a web browser, which can be thought of as an application program that provides the functionality you are interested in, and that will run in an operating system-provided environment.

## What is a Real-Time Operating System (RTOS)?

Most operating systems seem to allow multiple programs to run simultaneously. This is called multitasking. In reality, each processor core can only run a single program, thread, or task thread at any one time. The component called the task scheduler, which is part of the operating system, is responsible for deciding which program to run when and quickly switches between each program, giving the user the illusion of simultaneous execution.

The type of operating system is determined by the way the task scheduler decides in what order to run the programs to be executed. For example, in a multi-user operating system, like Unix, the scheduler used ensures that each user gets a fair amount of processing time. For another example, on a desktop operating system, like Windows, the task scheduler tries to keep the computer responsive to its user.

The programmer in a real-time operating system (RTOS) is designed to provide a predictable (deterministic) execution pattern. This is especially important for embedded systems because embedded systems often have real-time requirements. Real-time requirements are requirements that specify that the embedded system must respond to a specific event within a certain threshold time. A guarantee of fulfilling real-time requirements can only be made if the behavior of the operating system’s scheduler is predictable, that is, deterministic. Some of the most widely used RTOS are LynxOS, OSE, QNX, RTLinux, VxWorks, Windows CE, eCos, and FreeRTOS.

**Deterministic System:** In mathematics and physics, it is defined as systems that do not have randomness in the development of their future states. Therefore a deterministic system always produces the same output from a given initial condition or initial state.

### Classification of RTOS

RTOS can be divided into three types:

*   **Hard RTOS:** The degree of tolerance of the delay in the completion of tasks is quite small (zero or close to zero). Tasks not done on time have a devastating effect on the system.
*   **Firm RTOS:** Delays in the completion of tasks are unacceptable, but tasks that cannot be completed on time do not have a devastating effect on the system, they may cause a quality reduction.
*   **Soft RTOS:** Delays in the completion of tasks may not be significant and losses in this time can be tolerated. Decreases in system quality due to delays are acceptable.

### What is a Task Scheduler?

Task Scheduler keeps status logs of each task and selects the task that is ready to be executed, then allocates the processor to that task. The task scheduler ensures the most efficient use of the CPU in multi-tasking programs. Thus, it reduces the waiting time. There are generally two types of task schedulers.

*   **Non-Preemptive Scheduling:** There is no priority order between tasks and all tasks are considered with the same priority. When a task begins to be executed, another task begins to be executed upon the completion of this task.
*   **Preemptive Scheduling:** Always the processor checks for high-priority tasks. If a high-priority task is ready to be processed, the task on the processor is immediately suspended and control of the processor is given to the higher-priority task.
*   **Dispatcher:** It is used to give control of the processor to the task selected by the task scheduler. In this way, the execution flow is changed. Anytime an RTOS is running, its execution flow passes through the task program code, and interrupts the service routine (ISR), or kernel.

## References

* [1] Fan, Xiaocong. Real-Time Embedded Systems: Design Principles and
Engineering Practices. Newnes, 2015.
* [2] Jane Liu. Real-Time Systems. Integre Technical Publishing Co., Inc., 2000.