# ARM Architecture Instruction Set

2019-07-06

In this article, finally, we will start to take a glance at ARM’s arithmetical, logical, data transfer, and branching instructions. But before that, you should check your microprocessor’s model and serial number. Instructions might differ according to these two numbers. The reason for this is that ARM has updated its designs due to technological developments.

## Instruction Set

The arm instructions process data in the register. Therefore, the data must be transferred to the registers before arithmetic, logic, or other types of processing. This information is very important to us. The way to do this is to load data into registers by using load/store instructions. ARM instructions generally take three or two operands. To explain this with an example let’s check the syntax of Instructions:

    INS Operan1, Operand2, Operand3

where:
*   INS: Name of the instruction
*   Operand1: Destination register (Operand getting result)
*   Operand2: First register for operation (Operand getting 1st source)
*   Operand3: Second register for operation (Operand getting 2nd source)

Quick example;

    ADD(INS) r0(Operand1), r1(Operand2), r2(Operand3)  
    // This_ instructions _set is basically adds r1 and r2 registers and writes the results into the r0 register.  
    // ! r0 = r1+r2;  (in C)

Some ARM instructions may also take some prefixes and suffixes.

## Types of Instructions

ARM (Advanced RISC Machine) instructions can be broadly categorized into two primary types: **Data Transfer and Process, Arithmetic and Logical Computation, and Barrel Control** operations. These categories encompass the fundamental operations that ARM processors perform to manipulate data and control the flow of information within a system.

### Data Transfer and Process Instructions

These instructions are almost available in every microprocessor as well as in ARM microprocessors. These are very simple to use. Basically, provide to load or store the desired initial values to the register before processing. The instruction duty and usage structure are as follows.

**MOV:** The `MOV` instruction copies the value of `Operand2` into `Rd`.

**MVN:** The `MVN` instruction takes the value of `Operand2`, performs a bitwise logical NOT operation on the value and places the result into `Rd`.

**Syntax:**

    MOV{S}{cond} Rd, Operand2
    MOV{cond} Rd, #imm16
    MVN{S}{cond} Rd, Operand2

**Example:**
We can assign a register value as well as we can assign a constant number.

    MOV r0, r1    
    MOV r0, 5  
    MVN r0, r1  // r0 = NOT(r1)

where:

*   S: is an optional suffix. If S is specified, the condition code flags are updated on the result of the operation
*   cond: is an optional condition code.
*   Rd: is the destination register.
*   Operand2: is a flexible second operand.
*   imm 16: is any value in the range 0–65535. Immediate numbers are numerical constants.

### Arithmetic and Logical Computation Instructions

#### Arithmetic Computation Instructions

These instructions are fundamental arithmetic operations for all kinds of processors. They compute the sum (or difference), multiplication (or division)of two registers, and store the result in a register. Multiplication and division operations can also be performed via barrel shift.

**ADD:** The `ADD` instruction adds the value of `Register1` to`Register2`.

**SUB:** The `SUB` instruction subtracts the value of `Register2` from `Register1`.

**MUL:** The `MUL` instruction multiplies the value of `Register1` by`Register2`.

**SDIV:** The `SDIV` instruction divides the value of `Register1` by`Register2`.

    Note: Division with a constant number might not be supported by all ARM processors.

**Syntax:**

    ADD{S}{cond} Register0, Register1, Register2
    ADD Register1, #imm16  // 5
    SUB{S}{cond} Register3, Register4, Register5
    MUL Register0, Register1, Register2
    SDIV Register3, Register4, Register5

**Example:**

Given the following operations in the pseudocode:

    result = (a + b) - (c + d);
    a = b \* b;
    c = d / e;

We can do the same operations with ARM instructions as follows:

    // result = (a + b) - (c + d);
    ADD   r0, r2, r3  // result = a + b;  (in C)
    ADD   r1, r4, r5  // temp= c + d;  (in C)
    SUB   r0, r0, r1  // result = result - temp;  (in C)
    MUL r0, r2, r3    // a = b * c; (only 32 bits stored)  (in C)
    SDIV  r0, r2, r4  // c = d / e; (signed divide)  (in C)

#### Logic Computation Instructions
The ARM instruction set provides instructions such as AND, OR, XOR, and BIC, which sets, and clears the bits according to the need of the program. Usually, you find these as part of if-else, while statements in high-level languages.

**AND:** The `AND` instruction adds the value of `Register1` to `Register2`.

**OR:** The `OR` instruction subtracts the value of `Register2` from `Register1`.

**XOR:** The `XOR` instruction multiplies the value of `Register1` by `Register2`.

**BIC:** The `BIC` instruction divides the value of `Register1` by `Register2`.

**Syntax:**

    AND Register0, Register1, Register2  // r0 = r1 & r2;  (in C)   
    ORR Register3, Register4, Register5  // r3 = r4 | r5;  (in C)   
    EOR Register0, Register1, Register2  // r0 = r1 ^ r2;  (in C)  
    BIC Register3, Register4, Register5  // r3 = r4 & (!r5);  (in C)

**Example:**

    //  r0 = 01101001    
    //  r1 = 11000111  
    AND r3, r0, r1; r3  // 01000001  
    ORR r3, r0, r1; r3  // 11101111   
    EOR r3, r0, r1; r3  // 10101110   
    BIC r3, r0, r1; r3  // 00101000

### Branch Control Instructions
These instructions change the flow of execution via jumping to another instruction or subroutine  such as conditional jump e.g., branch if register == 0.

**Barrel Shifter:** As we mentioned in our first articles, the ARM’s arithmetic logic unit has a 32-bit barrel shifter that is capable of shifting and rotating operations. To be able to do this, the value must be in the register Rm. Briefly, the results are pre-processed by the barrel shifter before being processed in ALU.

    MOV r0, r0, LSL #1  // Multiply r0 by two  
    MOV r1, r1, LSR #2  // Divide r1 by four  
    MOV r2, r2, ASR #2  // Divide r2 by four(signed).

If you remember from digital electronic circuits, shifting a number 1 step left is equal to multiplying the number by 2. Shifting the number to 2 steps right means dividing the number by 4.

The last column specifies how many cycle times each command takes. Although the basic logic of all barrel shifter instructions is the same, the only direction of shifting may vary. There are two types of usage of barrel shifters. These uses may be shifting by the value of any register or shifting by a specified fixed number.

In the next article, I am planning to focus on the registers, CPU, and memory structure. Until then, I wish you no blue screen of death.

Continue reading this series of articles:

*   [Introduction to ARM Architecture](https://erdo.dev/posts/2019-01-24_Introduction-to-ARM-Architecture)
*   [ARM Development Environment Installation: ARM Keil Code & Code Composer Studio](https://erdo.dev/posts/2019-01-24_ARM-Development-Environment-Installation-ARM-Keil-Code-Composer-Studio)

## References

*   [1]   [https://cseweb.ucsd.edu/classes/fa15/cse30/lectures/lec7\_detailed.pdf](https://cseweb.ucsd.edu/classes/fa15/cse30/lectures/lec7_detailed.pdf)
*   [2]   [http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.kui0100a/armasm\_cihcjfjg.htm](http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.kui0100a/armasm_cihcjfjg.htm)
*   [3]   [http://www.davespace.co.uk/arm/introduction-to-arm/barrel-shifter.html](http://www.davespace.co.uk/arm/introduction-to-arm/barrel-shifter.html)
