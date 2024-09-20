# Introduction to ARM Architecture

2019-01-24

![The figure is taken from https://en.m.wikipedia.org/wiki/File:Acorn-ARM-Evaluation-System.jpg](https://cdn-images-1.medium.com/max/800/1*yVLT0ywWHW_PJ5VsiXNW9w.jpeg)

Anyone interested in embedded systems started to hear these two terms frequently. These are ARM and Embedded Linux. No longer, does everyone go towards work in these areas. Writing code in a free medium, when merging with the ease of getting rid of software licenses that cost millions, Embedded Linux started to gain popularity. As you all know, ARM architecture is very popular in the world and most projects use ARM-based processors with embedded systems.

Throughout this article series, I would like to share my knowledge about ARM architecture and microprocessors that I learned during my exchange period at the Tampere University of Technology. While sharing the pieces of information I have learned, of course, I can make mistakes, also sometimes I can give incomplete information. Please feel free to contact me if you can correct the places you see wrong. After making our first explanations, let's get into the main topic.

## What is ARM?

ARM is an architecture and its name refers to a company that invented ARM. This architecture was designed in 1983 by Acorn Computers Ltd. under the name of ARM1 (Acorn RISC Machine 1) and released in 1985. The following year, the company released 32-bit ARM2 and it created a tremendous impression with its simple and practical structure. In 1990, the company changed its name to Advanced RISC Machines Ltd. Later in 1998, the company changed its name again and ARM Ltd. is used today.

In addition to its 32-bit architecture, its low cost has resulted in the creation of processor cores that are very popular today. ARM has been able to license the cores produced by various companies, thus enabling them to perform various applications. In other words, ARM does not produce an integrated circuit. Instead, many companies, such as Apple, Samsung, Hewlett-Packard, Qualcomm, Texas Instruments, NXP, Atmel, and STM have developed ARM kernels and improved their implementation, or launched their ARM-based processors.

We will talk about ARM commands in our article series. C programming examples with ARM might take place, but for now, we will continue with the ARM instruction set. To get to know a microprocessor, I think it is possible to learn its instruction set and registers. If you already know C programming, you can use this information more effectively.

ARM command sets are divided into 2 sub-sections, 16-bit THUMB, and 32-bit ARM instruction sets. We will first refer to 32-bit instruction sets. I do not intend to use any computer or board during this process, but if I can find the time, I can do a few complementary applications and share the images. The development kit I have in ARM applications is shown below.

![](https://cdn-images-1.medium.com/max/800/1*yIQPbYsexgheFMqO-n3lfA.jpeg)

## ARM’s Features

ARM is a RISC (Reduced Instruction Set Computer) class processor, ie the command set is a reduced processor. Let's explain why it's not exactly the RISC processor. Firstly it has 32-bit registers from r1 to r16, and we can control all instruction sets conditionally. Also, it has a 32-bit barrel shifter, which is known as a combinational circuit, ie it allows several operations in a clock pulse independent from the clock signal. All these features do not make the ARM processors fully RISC-class microprocessors.
The ARM has a total of seven operating modes.

*   1.  Use Mode
*   2.  Fast Interrupt (FIQ) Mode
*   3.  Interrupt (IRQ) Mode
*   4.  Supervisor Mode
*   5.  Abort Mode
*   6.  System Mode
*   7.  Undefined Mode

The ARM consists of thirty-seven registers. The registers are arranged in partially overlapping banks. There is a different register bank for each processor mode. These registers are not all accessible at the same time. The processor state and operating mode determine which registers are available to the programmer.

*   Thirty-one of these registers have 32-bit general-purpose registers,
*   Six are status registers,
*   The ARM-state register set contains sixteen directly accessible (programmer-capable) registers, r0 to r15.

In general, ARM has a small-endian system but can be set as big-endian if desired.

I think it’s enough for today. In the next article, we will touch on technical issues. In order to better understand, it is useful for the readers to reinforce their knowledge by repeating terms such as RISC, Registers, Little Endian and Big Endian. See you in our next articles.

Continue reading this series of articles:

*   [ARM Development Environment Installation: ARM Keil & Code Composer Studio](https://erdo.dev/posts/2019-01-24_ARM-Development-Environment-Installation-ARM-Keil-Code-Composer-Studio)
*   [ARM Architecture Instruction Set](https://erdo.dev/posts/2019-07-06_ARM-Architecture-Instruction-Set)

## References

*   [1]   [https://en.wikipedia.org/wiki/ARM\_architecture](https://en.wikipedia.org/wiki/ARM_architecture)
*   [2]   [https://en.wikipedia.org/wiki/Arm\_Holdings](https://en.wikipedia.org/wiki/Arm_Holdings)
*   [3]   [http://www.keil.com/support/man/docs/armasm/armasm\_dom1359731128950.htm](http://www.keil.com/support/man/docs/armasm/armasm_dom1359731128950.htm)
*   [4]   [http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.ddi0210c/Cihhcjia.html](http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.ddi0210c/Cihhcjia.html)