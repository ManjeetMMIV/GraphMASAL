# Document: Chapter 6. Mechanism Limieted Direct Execution (Pages 1 to 22)

## Page 1

Process Execution Mechanism
Chap 6. of Operating System: Three Easy Pieces
1Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 2

Questions?
 Is OS code always running on CPU?
 If yes, then when/how any other process gets chance to run on CPU?
 If not, then how does OS controls the system?
 Where does an OS reside? When does it run? 
 When and how other processes run? How OS services are invoked?
2Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 3

Separation of policy and mechanism
 Re-occuring theme in OS
 Policy: high level decision-making to optimize some workload perf-
ormance metric
 Answer to “which” question
 Ex: Which process should OS run right now?
 Process Scheduler: Future lecture
 Mechanism: Low-level code/implementation of the decision
 Answer to a “How” question?
 Ex: how does an OS run a process or switches from one to another?
 Today’s lecture
 Separation allows one easily to change policies without having  
to rethink the mechanism and is thus a form of modularity
3Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 4

The Crux: How to efficiently virtualize the CPU with control?
 The OS needs to share the physical CPU by time sharing.
 Issue
 Performance: How can we implement virtualization without adding 
excessive overhead to the system?
 Control: How can we run processes efficiently while retaining control over 
the CPU?
4Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 5

 Just run the program directly on the CPU.
Direct Execution
OS Program
1. Create entry for process list
2. Allocate memory for program
3. Load program into memory
4. Set up stack with argc / argv
5. Clear registers
6. Execute call main()
9. Free memory of process
10. Remove from process list
7. Run main()
8. Execute return from main()
5
Without limits on running programs,
the OS wouldn’t be in control of anything and 
thus would be “just a library”
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 6

Problem 1: Restricted Operation
 What if a process wishes to perform some kind of restricted operation 
such as …
 Issuing an I/O request to a disk
 Gaining access to more system resources such as CPU or memory
 Solution: Using protected control transfer
 User mode: Applications do not have full access to hardware resources.
 Kernel mode: The OS has access to the full resources of the machine
6Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 7

System Call
 Allow the kernel to carefully expose certain key pieces of functionality 
to user program, such as …
 Accessing the file system
 Creating and destroying processes
 Communicating with other processes
 Allocating more memory
7Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 8

How is system call different from function call ?
 If it looks just like a procedure call, how does the system know it’s a    
system call?
 A Process can only see its own memory because of user mode (other   
areas, including kernel, are hidden) – then how can it call any Kernel    
code ?
8Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 9

How is System Call different (Cont.)?
 kernel address space of process - Some virtual addresses in the address 
space of every process are made to point to the kernel code.
 Every user process has 2 stacks - a user stack (resides in user address   
space) and a dedicated kernel stack (resides in kernel address space)
 When a process is running code in kernel mode, all data it needs to     
save is pushed on to the kernel stack (kernel does not trust user stack)
 Kernel does not trust user provided addresses to jump to 
 Kernel sets up Interrupt Descriptor Table (IDT) at boot time
 IDT has addresses of kernel functions to run for system calls and other      
events
9Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 10

Mechanism of system call
 A special Trap instruction is run (usually hidden from user by library)
 Raise the privilege level to kernel mode
 Switch to kernel stack
 Save context (old PC, registers) on kernel stack
 Look up address in IDT and jump to trap handler function in OS code
 Return-from-trap instruction
 Restore context of CPU registers from kernel stack
 Reduce CPU privilege from kernel mode to user mode
 Restore PC and jump to user code after trap
10Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 11

More on the trap instruction
 Trap instruction is executed on hardware in following cases:
 System call (program needs OS service)
 Program fault ( e.g program does illegal memory access)
 Interrupt (external device needs attention of OS, e.g., a network packet has 
arrived on network card)
 Across all cases, the mechanism is: save context on kernel stack and   
switch to OS address in IDT
 IDT has many entries: which to use?
 System calls/interrupts store a number in a CPU register before calling      
trap, to identify which IDT entry to use
11Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 12

Limited Direction Execution Protocol
12
OS @ boot
(kernel mode)
Hardware
initialize trap table
remember address of …
syscall handler
OS @ run
(kernel mode)
Hardware Program
(user mode)
Run main()
…
Call system
trap into OS
restore regs from kernel stack
move to user mode
jump to main
Create entry for process list
Allocate memory for program
Load program into memory
Setup user stack with argv
Fill kernel stack with reg/PC
return-from -trap
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 13

Limited Direction Execution Protocol (Cont.)
13
Free memory of process
Remove from process list 
…
return from main
trap (via exit()) 
restore regs from kernel stack
move to user mode
jump to PC after trap
Handle trap
Do work of syscall
return-from-trap
save regs to kernel stack
move to kernel mode
jump to trap handler
OS @ run
(kernel mode)
Hardware Program
(user mode)
(Cont.)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 14

Problem 2: Switching Between Processes
 Sometimes when OS is in kernel mode, it cannot return back to the    
same process it left
 Process has exited or must be terminated (e.g., segfault)
 Process has made a blocking system call
 Sometimes, the process has run for too long and OS must timeshare 
CPU with other processes
 When it is time to switch to some other process, OS should just stop 
one process and start another. But…
14Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 15

Problem 2: Switching Between Processes
 If a process is running on the CPU, this by definition means the OS is 
not running. If the OS is not running, how can it do anything at all ?
 Problem crux: How can the OS regain control of the CPU so that it 
can switch between processes?
 A cooperative Approach: Wait for system calls
 A Non-Cooperative Approach: The OS takes control
15Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 16

A cooperative Approach: Wait for system calls
 Processes periodically give up the CPU by making system calls such 
as yield.
 Application also transfer control to the OS when they do something illegal.
 Divide by zero
 Try to access memory that it shouldn’t be able to access
 When the OS gets back CPU control, it can decide to run some other task.
 Ex) Early versions of the Macintosh OS, The old Xerox Alto system
16
A process gets stuck in an infinite loop. 
→ Reboot the machine
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 17

A Non-Cooperative Approach: OS Takes Control
 A timer interrupt
 During the boot sequence, the OS start the timer.
 The timer raise an interrupt every so many milliseconds.
 When the interrupt is raised :
 The currently running process is halted.
 Save enough of the state of the program
 A pre-configured interrupt handler in the OS runs.
17
A timer interrupt gives OS the ability to 
run again on a CPU.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 18

Saving and Restoring Context
 Scheduler makes a decision:
 Whether to continue running the current process, or switch to a different 
one.
 If the decision is made to switch, the OS executes context switch.
18Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 19

Mechanism of Context Switch
 Example: process A has moved from user to kernel mode, OS decides  
it must switch from A to B
 Save context (a few register values) of A onto its kernel stack
 General purpose registers
 PC
 kernel stack pointer
 Restore context from B’s kernel stack
 Switch to the kernel stack (change the stack pointer) of B
 Now, CPU is running B in kernel mode
 Who has saved registers on B’s kernel stack?
 OS did, when it switched out B in the past.
19Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 20

Limited Direction Execution Protocol (Timer interrupt)
20
OS @ boot
(kernel mode) Hardware
initialize trap table
OS @ run
(kernel mode) Hardware Program
(user mode)
start interrupt timer
Process A
…
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur
Periodically send timer 
interrupt in X ms
remember address of …
syscall handler
timer handler
timer interrupt
Save user context/regs(A) 
to k-stack(A)
move to kernel mode
jump to trap handler

## Page 21

Limited Direction Execution Protocol (Timer interrupt)
21
OS @ run
(kernel mode) Hardware Program
(user mode)
(Cont.)
Handle the trap
Call switch() routine
save kernel context/regs(A) to PCB(A)
restore kernel context/regs(B) from PCB(B)
switch to k-stack(B)
return-from-trap (into B)
restore user context/regs(B) from         
k-stack(B)
move to user mode
jump to B’s PC Process B
…
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 22

Worried About Concurrency?
 What happens if, during interrupt or trap handling, another interrupt 
occurs?
 OS handles these situations:
 Disable interrupts during interrupt processing
 Use a number of sophisticate locking schemes to protect concurrent 
access to internal data structures.
22Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

