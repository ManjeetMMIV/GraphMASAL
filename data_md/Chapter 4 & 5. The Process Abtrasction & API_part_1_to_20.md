# Document: Chapter 4 & 5. The Process Abtrasction & API (Pages 1 to 20)

## Page 1

The Process Abstraction & API
Ch. 4 & 5 of Operating System: Three Easy Pieces
1Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 2

A Process
 Program: Static code and static data
 Process: Dynamic instance of code and data
 Can have multiple process instances of same program
 What constitutes a process?
 A unique identifier (PID)
 Memory (address space)
 Instructions
 Data section
 CPU context: Registers
 Program counter, Stack pointer, Current operands
 File descriptors - Pointers to open files and devices
2
A process is a running program.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 3

How does OS create a process?
3
code
static data
heap
stack
Process
Memory
code
static data
heap
Program
Disk
Loading:
Takes on-disk program
and reads it into the 
address space of 
process
CPU
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 4

Process Creation
1. Load a program code into memory, into the address space of the 
process.
 Programs initially reside on disk in executable format.
 OS perform the loading process lazily.
 Loading pieces of code or data only as they are needed during program 
execution.
2. The program’s run-time stack is allocated.
 Use the stack for local variables, function parameters, and return address.
 Initialize the stack with arguments → argc and the argv array of main() 
function
4Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 5

Process Creation (Cont.)
3. The program’s heap is created.
 Used for explicitly requested dynamically allocated data.
 Program request such space by calling malloc() and free it by calling 
free().
4. The OS do some other initialization tasks.
 input/output (I/O) setup
 Each process by default has three open file descriptors.
 Standard input, output and error
5. Start the program running at the entry point, namely main().
 The OS transfers control of the CPU to the newly-created process.
5Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 6

Problem Crux: How to provide the illusion of many CPUs?
 CPU virtualizing
 Give each process impression it alone is actively using CPU
 Resources can be shared in time and space
 Time sharing: Running one process, then stopping it and running another
 Assume single uniprocessor (multi-processors: advanced issue)
 Memory?
 Space-sharing (later)
 Disk? 
 Space-sharing (later)
6Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 7

Process States
 A process can be one of three states.
 Running : currently executing on CPU
 Ready: waiting to be scheduled
 A process is ready to run but for some reason the OS has chosen not to run it 
at this given moment.
 Blocked: suspended, not ready to run
 A process has performed some kind of operation.
 When a process initiates an I/O request to a disk, it becomes blocked and thus 
some other process can use the processor.
7Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 8

Process State Transition
8
Running Ready
Blocked
Descheduled
Scheduled
I/O: doneI/O: initiate
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 9

Example: Tracing process state
 CPU only
9
 CPU & I/O
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 10

Data structures
 The OS has some key data structures that track various relevant pieces 
of information
 Process list
 Ready processes
 Blocked processes
 Current running process
 Register context
 PCB (Process Control Block)
 A C-structure that contains information about each process.
10Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 11

Example) The xv6 kernel Proc Structure
11
// the registers xv6 will save and restore
// to stop and subsequently restart a process
struct context {
int eip; // Index pointer register
int esp; // Stack pointer register
int ebx; // Called the base register
int ecx; // Called the counter register
int edx; // Called the data register
int esi; // Source index register
int edi; // Destination index register
int ebp; // Stack base pointer register
};
// the different states a process can be in
enum proc_state { UNUSED, EMBRYO, SLEEPING,
RUNNABLE, RUNNING, ZOMBIE };
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 12

Example) The xv6 kernel Proc Structure (Cont.)
12
// the information xv6 tracks about each process
// including its register context and state
struct proc {
char *mem; // Start of process memory
uint sz; // Size of process memory
char *kstack; // Bottom of kernel stack
// for this process
enum proc_state state; // Process state
int pid; // Process ID
struct proc *parent; // Parent process
void *chan; // If non-zero, sleeping on chan
int killed; // If non-zero, have been killed
struct file *ofile[NOFILE]; // Open files
struct inode *cwd; // Current directory
struct context context; // Switch here to run process
struct trapframe *tf; // Trap frame for the
// current interrupt
};
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 13

Process API
 API = Application Programming Interface 
= functions available to write user programs 
 API provided by OS is a set of “system calls”
 System call is a function call into OS code that runs at a higher privilege  l
evel of the CPU 
 Sensitive operations (e.g., access to hardware) are allowed only at a higher 
privilege level 
 Some “blocking” system calls cause the process to be blocked and desche
-duled (e.g., read from disk)
 POSIX API: a standard set of system calls that an OS must implement
 Program language libraries hide the details of invoking system calls
13Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 14

Process API (contd.)
 These APIs are available on any modern OS.
 Create
 Create a new process to run a program
 Destroy
 Halt a runaway process
 Wait
 Wait for a process to stop running
 Execute
 makes a process execute a given executable
 Status
 Get some status info about a process
14Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 15

Process API in Unix
 fork() creates a new child process 
 All processes are created by forking from a parent 
 The init process is ancestor of all processes 
 exit() terminates a process 
 wait() causes a parent to block until child terminates 
 exec() makes a process execute a given executable 
 Many variants exist of the above system calls with different arguments
15Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 16

What happens during a fork?
 A new process is created by making a copy of parent’s memory image
 The new process is added to the OS process list and scheduled 
 Parent and child start execution just after fork (with different return val
ues) 
 Parent and child execute and modify the memory data independently
 Demo..
16Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 17

Waiting for children to die ..
 Process termination scenarios 
 By calling exit() (exit is called automatically when end of main is reached) 
 OS terminates a misbehaving process 
 wait() blocks in parent until child terminates (non-blocking ways to     
invoke wait exist) 
 What if parent terminates before child? init process adopts orphans   
and cleans up
 Demo 
17Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 18

What happens during exec()?
 After fork, parent and child are running same code 
– Not too useful! 
 A process can run exec() to load another executable to its memory im-
age
– So, a child can run a different program from parent 
 Variants of exec(), e.g., to pass commandline arguments to new execut
-able
 Demo
18Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 19

Case study: How does a shell work?
 In a basic OS, the init process is created after initialization of hardware
 The init process spawns a shell like bash 
 Shell reads user command, forks a child, execs the command executab
-le, waits for it to finish, and reads next command 
 Common commands like ls are all executables that are simply exec’ed
by the shell
 Can manipulate the child to do more funky things
 Suppose you want to redirect output from a command to a file
 Shell spawns a child, rewires its standard output to a file, then calls exec  
on the child
 Demo
19Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 20

 Disclaimer: This slide set has been adapted from the lecture slides for Operating System 
course in Computer Science Dept. at Hanyang University. This lecture slide set is for 
OSTEP book written by Remzi and Andrea at University of Wisconsin.
20Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

