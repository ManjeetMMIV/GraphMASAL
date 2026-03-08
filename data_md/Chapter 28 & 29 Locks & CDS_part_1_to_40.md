# Document: Chapter 28 & 29 Locks & CDS (Pages 1 to 40)

## Page 1

28 & 29. Locks & Concurrent DS
Operating System: Three Easy Pieces
1Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 2

Review: What is needed for CORRECTNESS?
 Ensure that any critical section executes as if it were a single atomic 
instruction.
 An example: the canonical update of a shared variable
 More general: Need mutual exclusion for critical sections
 if process A is in a critical section C, process B can’t
(okay if other processes do unrelated work)
2
balance = balance + 1;
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 3

Implementing Synchronization
 Build higher-level synchronization primitives in OS
 Operations that ensure correct ordering of instructions across    
threads
 Motivation: Build them once and get them right
Monitors Semaphores
Condition Variables
Locks
Loads Stores Test&Set
Disable Interrupts
3Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 4

Implementation Goals
 Correctness 
 Mutual exclusion
 Only one thread in critical section at a time
 Progress (deadlock-free)
 If several simultaneous requests, must allow one to proceed
 Bounded (starvation-free)
 Must eventually allow each waiting thread to enter
 Fairness
Each thread waits for same amount of time
 Performance
CPU is not used unnecessarily (e.g., spinning)
4Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 5

Using Locks: The Basic Idea
 Lock is just a variable which holds the state of the lock.
 available (or unlocked or free)
 No thread holds the lock.
 acquired (or locked or held)
 Exactly one thread holds the lock and presumably is in a critical section.
 We could store other information such as which thread holds the lock 
or a queue for ordering lock acquisition but information like that is 
hidden from the user of the lock
6Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 6

The semantics of the lock()
 lock()
 Try to acquire the lock.
 If no other thread holds the lock, the thread will acquire the lock.
 Enter the critical section.
 This thread is said to be the owner of the lock.
 Other threads are prevented from entering the critical section while the 
first thread that holds the lock is in there.
 Unlock()
 Called by the owner of lock and the state of lock is changed to free
 If there are waiting threads, one of them will notice( be informed) of this 
change and will acquire the lock and enter the CS.
7Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 7

Building locks: option 1
 Just Disable Interrupts for critical sections
 Prevents dispatcher from running another thread
 Code between interrupts executes atomically
 Problem:
 Require too much trust in applications
◼ Greedy (or malicious) program could monopolize the processor.
 Do not work on multiprocessors
 Cannot perform other necessary work
8
1 void lock() {
2 DisableInterrupts();
3 }
4 void unlock() {
5 EnableInterrupts();
6 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 8

Building locks: option 2
 Software based solution
 First attempt: Using a single shared variable denoting whether the 
lock is held or not
Boolean lock = false; // shared variable
Void lock(Boolean *lock) {
while (*lock) /* wait */ ;
*lock = true; }
Void unlock(Boolean *lock) {
*lock = false; }
 Why doesn’t this work?  Example schedule that fails with 2 threads?
10Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 9

Problem: No Mutual exclusion
*lock == 0 initially
Thread 1 Thread 2    
while(*lock == 1)
while(*lock == 1)
*lock = 1
*lock = 1
Both threads grab lock!
Problem: Testing lock and setting lock are not atomic. 
Race condition has moved to the lock  acquisition code!
11Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 10

Peterson’s Algorithm
 Uses more shared variables. Assume only two threads (tid = 0, 1) here
int turn = 0; // shared
Boolean lock[2] = {false, false};
Void lock() {
lock[tid] = true;
turn = 1-tid;
while (lock[1-tid] && turn == 1-tid) /* wait */ ;
}
Void unlock() {
lock[tid] = false;
}
12Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 11

Different Cases: 
Lock[0] = true;
turn = 1;
while (lock[1] && turn ==1);
Only thread 0 wants lock
Lock[0] = true;
turn = 1;
while (lock[1] && turn ==1);
Thread 0 and thread 1 both want lock; 
Lock[1] = true;
turn = 0;
while (lock[0] && turn == 0);
13Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 12

Different Cases:
Lock[0] = true;
turn = 1;
while (lock[1] && turn ==1);
Thread 0 and thread 1 both want lock
Lock[1] = true;
turn = 0;
while (lock[0] && turn == 0);
14Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 13

Different Cases:
Lock[0] = true;
turn = 1;
while (lock[1] && turn ==1);
while (lock[1] && turn ==1);
Thread 0 and thread 1 both want lock; 
Lock[1] = true;
turn = 0;
while (lock[0] && turn == 0);
15Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 14

Peterson’s Algorithm: Intuition
 Mutual exclusion: Enter critical section if and only if
Other thread does not want to enter
Other thread wants to enter, but your turn
 Progress: Both threads cannot wait forever at while() loop
Completes if other process does not want to enter
Other process (matching turn) will eventually finish
 Bounded waiting (not shown in examples)
Each process waits at most one critical section
Problem: doesn’t work on modern hardware
(cache-consistency issues)
16Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 15

Building locks: option 3
 Hardware support: Modern architectures provide some basic atomic 
instructions at hardware level to support the creation of simple locks
 Example: Test And Set (Atomic Exchange) 
 return(testing) old value pointed to by the ptr.
 Simultaneously update(setting) ptr value to new.
 This sequence of operations is performed atomically.
17
1 int TestAndSet(int *ptr, int new) {
2 int old = *ptr; // fetch old value at ptr
3 *ptr = new; // store ‘new’ into ptr
4 return old; // return the old value
5 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 16

A Simple Spin Lock using test-and-set
 Note: To work correctly on a single processor, it requires a preemptive 
scheduler.
18
1 typedef struct __lock_t {
2 int flag;
3 } lock_t;
4
5 void init(lock_t *lock) {
6 // 0 indicates that lock is available,
7 // 1 that it is held
8 lock->flag = 0;
9 }
10
11 void lock(lock_t *lock) {
12 while (TestAndSet(&lock->flag, 1) == 1)
13 ; // spin-wait
14 }
15
16 void unlock(lock_t *lock) {
17 lock->flag = 0;
18 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 17

Another atomic instruction: Compare-And-Swap
 Test whether the value at the address(ptr) is equal to expected.
 If so, update the memory location pointed to by ptr with the new value.
 In either case, return the actual value at that memory location.
19
1 int CompareAndSwap(int *ptr, int expected, int new) {
2 int actual = *ptr;
3 if (actual == expected)
4 *ptr = new;
5 return actual;
6 }
Compare-and-Swap hardware atomic instruction (C-style)
1 void lock(lock_t *lock) {
2 while (CompareAndSwap(&lock->flag, 0, 1) == 1)
3 ; // spin
4 }
Spin lock with compare-and-swap
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 18

Evaluating Spin Locks
 Correctness: yes as the spin lock only allows a single thread to entry 
the critical section.
 Fairness: Spin locks don’t provide any fairness guarantees.
 Indeed, a thread spinning may spin forever.
 Performance: In the single CPU, performance overheads can be quite 
painful.
20
spin spin spin spin
A B
0 20 40 60 80 100 120 140 160
A B A B A B
lock
lockunlock lockunlock lockunlock lockunlock
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 19

Fetch-And-Add
 Atomically increment a value while returning the old value at a 
particular address.
21
1 int FetchAndAdd(int *ptr) {
2 int old = *ptr;
3 *ptr = old + 1;
4 return old;
5 }
Fetch-And-Add Hardware atomic instruction (C-style)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 20

Ticket Lock
 Ticket lock can be built with fetch-and add.
 Ensure progress for all threads. → fairness
 Idea: reserve each thread’s turn to use a lock.
22
1 typedef struct __lock_t {
2 int ticket; int turn;
3 } lock_t;
4
5 void lock_init(lock_t *lock) {
6 lock->ticket = 0;
7 lock->turn = 0; }
8
9 void lock(lock_t *lock) {
10 int myturn = FetchAndAdd(&lock->ticket);
11 while (lock->turn != myturn)
12 ; // spin
13 }
14 void unlock(lock_t *lock) {
15 FetchAndAdd(&lock->turn); }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 21

Ticket Lock Example
0
1
2
3
4
5
6
7
A lock(): 
B lock():
C lock():
A unlock(): 
B runs
A lock():
B unlock(): 
C runs
C unlock(): 
A runs
A unlock(): 
C lock():
Ticket Turn
23Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 22

Ticket Lock Example
0
1
2
3
4
5
6
7
A lock():
B lock():
C lock():
A unlock(): 
B runs
A lock():
B unlock(): 
C runs
C unlock(): 
A runs
A unlock(): 
C lock():
Ticket 
 Turngets ticket 0, spins until turn = 0 →runs
gets ticket 1, spins until turn=1
gets ticket 2, spins until turn=2
turn++ (turn = 1)
gets ticket 3, spins until turn=3
turn++ (turn = 2)
turn++ (turn = 3)
turn++ (turn = 4)
gets ticket 4, runs immediately
24Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 23

Too Much Spinning
 Hardware-based spin locks are simple and they work.
 In some cases, these solutions can be quite inefficient.
 Any time a thread gets caught spinning, it wastes an entire time 
slice doing nothing but checking a value.
25
How To Avoid Spinning?
We’ll need OS Support too!
spinspin spin spin spin
A B
0 20 40 60 80 100 120 140 160
C D A B C D
lock unlock lock
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 24

A Simple Approach: Just Yield!
 When you are going to spin, give up the CPU to another 
thread.
 Yield( ) system call moves the caller from the running state to the 
ready state.
26
1 void init() {
2 flag = 0;
3 }
4
5 void lock() {
6 while (TestAndSet(&flag, 1) == 1)
7 yield(); // give up the CPU
8 }
9
10 void unlock() {
11 flag = 0;
12 } Lock with Test-and-set and Yield
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 25

Yield Instead of Spin
27
A
0 20 40 60 80 100 120 140 160
A B
lock unlock lock
yield:
spinspin spin spin spin
A B
0 20 40 60 80 100 120 140 160
C D A B C D
lock unlock lock
no yield:
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 26

Yield Performance
 Waste…
 Without yield: O(threads * time_slice)
 With yield: O(threads * context_switch) 
 So even with yield, spinning is slow with high thread conten-ti
on
 The cost of a context switch can be substantial and the     
starvation problem still exists
 Next improvement: Block and put thread on waiting queue 
instead of spinning 
28Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 27

Using Queues: Sleeping Instead of Spinning
 Queue to keep track of which threads are waiting (and 
their turn) to acquire the lock.
 Little more OS support to be able to remove waiting        
threads from scheduler ready queue
 Ex. Solaris provides following two calls
 park(): Put a calling thread to sleep
 unpark(threadID): Wake a particular thread as designated by 
threadID.
29Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 28

RUNNABLE: 
RUNNING: 
WAITING: 
A, B, C, D
<empty> 
<empty> 
0 20 40 60 80 100 120 140 160
Example Demo
30Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 29

RUNNABLE: 
RUNNING: 
WAITING: 
B, C, D
A
<empty> 
0 20 40 60 80 100 120 140 160
A
lock
Example Demo
31Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 30

32
Example Demo
RUNNABLE: 
RUNNING: 
WAITING: 
C, D, A
B
<empty> 
0 20 40 60 80 100 120 140 160
A
lock
B
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 31

RUNNABLE: 
RUNNING: 
WAITING: 
C, D, A
B
0 20 40 60 80 100 120 140 160
A
lock
B
try lock
(sleep)
Example Demo
33Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 32

RUNNABLE: 
RUNNING: 
WAITING: 
D, A
C
B
0 20 40 60 80 100 120 140 160
A
lock
B
try lock
(sleep)
C
Example Demo
34Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 33

RUNNABLE: 
RUNNING: 
WAITING: 
A, C
D
B
0 20 40 60 80 100 120 140 160
A
lock
B
try lock
(sleep)
C D
Example Demo
35Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 34

RUNNABLE: 
RUNNING: 
WAITING: 
A, C
B, D
0 20 40 60 80 100 120 140 160
A
lock
B
try lock
(sleep)
C D
try lock
(sleep)
Example Demo
36Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 35

RUNNABLE: 
RUNNING: 
WAITING: 
C
A
B, D
0 20 40 60 80 100 120 140 160
A
lock
B
try lock
(sleep)
C D
try lock
(sleep)
A
Example Demo
37Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 36

RUNNABLE: 
RUNNING: 
WAITING: 
A
C
B, D
0 20 40 60 80 100 120 140 160
A
lock
B
try lock
(sleep)
C D
try lock
(sleep)
A C
Example Demo
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 38

## Page 37

RUNNABLE: 
RUNNING: 
WAITING: 
C
A
B, D
0 20 40 60 80 100 120 140 160
A
lock
B
try lock
(sleep)
C D
try lock
(sleep)
A C A
Example Demo
39Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 38

RUNNABLE: 
RUNNING: 
WAITING: 
B, C
A
0 20 40 60 80 100 120 140 160
A
lock
B
try lock
(sleep)
C D
try lock
(sleep)
A C A
unlock
D
Example Demo
40Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 39

RUNNABLE: 
RUNNING: 
WAITING: 
B, C
A
0 20 40 60 80 100 120 140 160
A
lock
B
try lock
(sleep)
C D
try lock
(sleep)
A C A
unlock
D
Example Demo
41Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 40

RUNNABLE: 
RUNNING: 
WAITING: 
C, A
B
0 20 40 60 80 100 120 140 160
A
lock
B
try lock
(sleep)
C D
try lock
(sleep)
A C A
unlock
B
lock
D
Example Demo
42Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

