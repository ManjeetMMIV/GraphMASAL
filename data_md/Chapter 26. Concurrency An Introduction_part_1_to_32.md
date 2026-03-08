# Document: Chapter 26. Concurrency An Introduction (Pages 1 to 32)

## Page 1

26. Concurrency: An Introduction
Operating System: Three Easy Pieces
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 2

Review: Easy Piece 1
Virtualization
CPU
Memory
Context Switch
Schedulers
Segmentation
Paging
TLBs
Multilevel
Swapping
Allocation
System calls
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 3

Concurrency
 Concurrency simply means doing more than one thing at a time by  
Interleaving/overlapping/sharing of resources 
 Operating systems (and application programs) often need to be able   
to handle multiple things happening at the same time. 
 In the Past:
 OS - Process execution, interrupts, background tasks, sys. maintenance 
 Servers – handle multiple client connections (different tasks) simultaneously
 Programs with GUI – To achieve event responsiveness while doing comput-
ation. 
 Network and disk bound programs – To hide network/disk latency
 Now: Parallel and/or multi-threaded programs for scalability and perfor
-mance in multicore era 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 4

Motivation (contd..)
CPU Trend now: Same speed, but multiple cores 
Goal: Write applications that fully utilize many cores
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 5

Concurrency: Option 1
 Build applications from many communicating/cooperative processes.
 Ex. Chrome browser – each tab is separate process. 
 Older browser ran as single process - if one web site causes trouble,      
entire browser can hang or crash
 Processes are cooperating if they can affect each other like one proc
-ess may be writing to a file, while another is reading from the file.
 Requires mechanisms that allow processes to communicate data bet-
ween each other and synchronize their actions
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 6

Inter Process Communication (IPC) mechanisms
1. Shared Memory
2. Message passing
3. Pipes
4. Sockets
5. Signals
(a) Message passing.  (b) shared memory. 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 7

Message passing
 If processes P and Q wish to communicate, they need to establish a   
communication link (message queue, mailbox etc.) between them
 Exchange messages via send/receive
 send (P, message) – send a message to process P
 receive(Q, message) – receive a message from process Q
 Message passing may be either blocking or non-blocking
 Blocking is considered synchronous
 Blocking send -- the sender is blocked until the message is received
 Blocking receive -- the receiver is  blocked until a message is available
 Non-blocking is considered asynchronous
 Non-blocking send -- the sender sends the message and continue
 Non-blocking receive -- the receiver receives either valid or null message
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 8

Pipes
 Pipe system call returns two file descriptors (fd)
 Read and write handle: Data written through one fd can be read from other
 A pipe is a half-duplex communication
 Regular pipes: both fd are in same process (how it is useful?)
 Parent and child share fd after fork
 Parent uses one end and child uses other end
 Named pipes: two endpoints of a pipe can be in  different processes
 OS buffers Pipe data between write and read


## Page 9

Shared Memory
 Processes can both access same region of  memory via shmget () sys-
tem call
int shmget ( key_t key, int size, int shmflg )
 By providing same key, two processes can get  same segment of      
memory which they can read/write in order to communicate
 Need to take care that one is not overwriting other’s data: Later?
 Ex. Bounded buffer producer-consumer problem
Shared data:
#define BUFFER_SIZE 10
typedef struct { . . . } item;
item buffer[BUFFER_SIZE];
int in = 0;
int out = 0;
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 10

Producer and consumer code using shared memory
 Producer: 
 Consumer:
item next_produced; 
while (true) { 
/* produce an item in next produced */ 
while (((in + 1) % BUFFER_SIZE) == out) 
; /* do nothing */ 
buffer[in] = next_produced; 
in = (in + 1) % BUFFER_SIZE; 
} 
item next_consumed; 
while (true) {
while (in == out) 
; /* do nothing */
next_consumed = buffer[out]; 
out = (out + 1) % BUFFER_SIZE;
/* consume the item in next consumed */ 
} 
Can only use BUFFER_SIZE-1 elements!
Try to modify it to use full capacity?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 11

Pros and Cons of option 1
 Pros?
 Don’t need new abstractions; 
 Good for security/isolation
 Appropriate for logically separate tasks where little sharing of data in mem
-ory is needed
 Cons?
 Cumbersome programming
 High communication overheads
 Expensive context switching
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 12

Concurrency: Option 2
 A new abstraction Thread: a (lightweight) copy of a process that 
executes independently
 In a Multi-threaded program
 Threads share the same address space but have its own point of execution 
i.e can be running different part of the program 
 Each thread has its own stack, program counter and set of registers.


## Page 13

Process vs. threads
 Process P forks a child C 
 P and C do not share any memory 
 Extra copies of code, data in memory 
 Need complicated IPC mechanisms to communicate
 Process P executes two threads T1 and T2 
 T1 and T2 share parts of the address space 
 Each has its own stack 
 Global variables can be used for communication 
 Smaller memory footprint
P C
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 14

Scheduling threads
 OS schedules threads that are ready to run independently, much like   
processes
 The context/state of a thread (PC, registers) is saved into/restored from 
thread control block (TCB)
 Every PCB has one or more linked TCBs
 When switching from running one (T1) to running the other (T2),
 The register state of T1 be saved.
 The register state of T2 restored.
 The address space remains the same.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 15

Thread Benefits
 Divide large task across several cooperative threads and communicate 
through shared address space
 Benefits: 
1. Scalability/Parallelism – multi-threaded program can take advantage 
of multicore/multiprocessor architectures
2. Resource Sharing – threads share resources of process. So global var
-iables can be used for communication (lot easy than IPC mechanism)
3. Responsiveness – may allow continued progress if part of a process  
is blocked (due to I/O); especially important for user interfaces
4. Economy – cheaper than process creation and thread switching has   
lower overhead than context switching between processes
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 16

Concurrency vs. Parallelism
 Concurrency: running multiple threads/processes at  the same time,  
even on single CPU core, by interleaving their executions.
 Parallelism: running multiple threads/processes in parallel on different 
processors/CPU cores
Concurrent execution on single-core system
Parallelism on a multi-core system
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 17

User Threads and Kernel Threads
 Kernel threads – Managed and scheduled independently by OS
 User threads - management done by user-level threads library like    P
OSIX Pthreads
 User program sees multiple threads but kernel is 
not aware of their existence
 Library multiplexes large number of user threads 
over a smaller number of kernel threads
 Low overhead of switching between user threads  
(no expensive context switch)
 In case of many to one mapping, multiple user    
threads cannot run in parallel
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 18

Thread APIs
 Variety of thread APIs exist 
 POSIX Pthreads
 Windows threads
 Java threads
 Common thread operations 
 Create 
 Exit 
 Join (instead of wait() for processes)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 19

Creating threads using pthreads API
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 20

Thread Trace
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 21

Thread Trace
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 22

Thread Trace
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 23

It Gets worse with Shared Data
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 24

Output?
 What do we expect? Two threads, each  increments counter by 10^7, so 2X10^7
 Sometimes, a lower value.
 At other times, an altogether different result! Aren’t computers supposed to        
produce deterministicresults?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 25

 Consider the assembly code sequence for update to counter
What is happening? Uncontrolled scheduling
OS Thread1 Thread2 PC %eax counter
before critical section
mov 0x8049a1c, %eax
add $0x1, %eax
100
105
108
0
50
51
50
50
50
interrupt
save T1’s state
restore T2’s state
mov 0x8049a1c, %eax
add $0x1, %eax
mov %eax, 0x8049a1c
100
105
108
113
0
50
51
51
50
50
50
51
interrupt
save T2’s state
restore T1’s state
mov %eax, 0x8049a1c
108
113
51
51
50
51
(after instruction)
Initially say counter is 50
100 mov 0x8049a1c, %eax
105 add $0x1, %eax
108 mov %eax, 0x8049a1c
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 26

Race condition and Critical section
 What just happened is called a race condition and the portion of 
code that can lead to race conditions is called Critical section 
 Concurrent modification of shared data leads to non-deterministic result
 What we need? mutual exclusion: Only one thread should be 
executing critical section at  any instant of time
 How it is achieved? atomicity of the critical section: The critical section 
should execute like one uninterruptible instruction
 Mechanisms? Locks
1    lock_t mutex;
2    . . .
3    lock(&mutex);
4    counter = counter + 1;
5    unlock(&mutex);
Critical section
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 27

Quiz
 Identify the critical section in the producer consumer code
 Producer: 
 Consumer:
item next_produced; 
while (true) { 
/* produce an item in next produced */ 
while (((in + 1) % BUFFER_SIZE) == out) 
; /* do nothing */ 
buffer[in] = next_produced; 
in = (in + 1) % BUFFER_SIZE; 
} 
item next_consumed; 
while (true) {
while (in == out) 
; /* do nothing */
next_consumed = buffer[out]; 
out = (out + 1) % BUFFER_SIZE;
/* consume the item in next consumed */ 
} 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 28

Quiz
 Identify the critical section in the modified producer consumer code
 Producer: 
 Consumer:
item next_produced; 
while (true) {
/* produce an item in next produced */ 
while (counter == BUFFER_SIZE) ; 
/* do nothing */ 
buffer[in] = next_produced; 
in = (in + 1) % BUFFER_SIZE; 
counter++; } 
item next_consumed; 
while (true) {
while (counter == 0) 
; /* do nothing */ 
next_consumed = buffer[out]; 
out = (out + 1) % BUFFER_SIZE; 
counter--; } 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 29

Quiz
 Lets say initial value of counter = 5. what are the possible values of     
counter after the completion of one iteration each of producer and 
consumer?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 30

Timeline View
producer consumer 
mov 0x123, %eax
add %0x1, %eax
mov %eax, 0x123
mov 0x123, %eax
sub %0x1, %eax
mov %eax, 0x123
Value of counter? 5: correct!
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 31

Timeline View
producer consumer
mov 0x123, %eax
add %0x1, %eax
mov 0x123, %eax
mov %eax, 0x123
sub %0x1, %eax
mov %eax, 0x123
Value of counter? 4: incorrect!
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 32

Timeline View
producer consumer
mov 0x123, %eax
mov 0x123, %eax
add %0x1, %eax
sub %0x1, %eax
mov %eax, 0x123
mov %eax, 0x123
Value of counter? 6: incorrect!
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

