# Document: Chapter 31. Semaphore (Pages 1 to 40)

## Page 1

31. Semaphore
Operating System: Three Easy Pieces
1Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 2

Condition Variables vs Semaphores
 Condition variables have no state (other than waiting queue)
 Programmer must track additional state
 Semaphores have state: track integer value
 State cannot be directly accessed by user program, but state determin
-es  behavior of semaphore operations
 Allocation and Initialization
sem_t sem;
sem_init(sem_t *s, int initval) {
s->value = initval;
}
2Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 3

Semaphore: Interaction with semaphore
 sem_wait()
 So it either return right away if the value of the semaphore was one or 
higher when we called sem_wait()or
 It will cause the caller to suspend execution waiting for a subsequent post.
 Multiple threads may call into sem_wait() and thus all be queued 
waiting to be woken up.
 sem_post()
3
1  int sem_wait(sem_t *s) { 
2 Waits until value of sem is > 0
3 then decrements sem s value by one  
4 } 
1  int sem_post(sem_t *s) { 
2   increment the value of semaphore s by one 
3   if there are one or more threads waiting, wake one of them
4  } 
wait and post are atomic
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 4

void thread_exit() {
sem_post(&s)
}
void thread_join() {
sem_wait(&s);
}
sem_t s;
sem_init(&s, ???);
Semaphores: Sem_wait(): Waits until value > 0, then decrement
Sem_post(): Increment value, then wake a single waiter
Initialize to 0 (so sem_wait() must wait…)
Join with CV vs Semaphores
void thread_join() {
Mutex_lock(&m); // w
if (done == 0) // x
Cond_wait(&c, &m); // y
Mutex_unlock(&m); // z
void thread_exit() {
Mutex_lock(&m); // a
done =1; // b
Cond_signal(&c); // c
Mutex_unlock(&m);// d
}
void thread_join() {
Mutex_lock(&m); // w
if (done == 0) // x
Cond_wait(&c, &m); // y
Mutex_unlock(&m); // z
}
Parent: Child:
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 4

## Page 5

Equivalence Claim
 Semaphores are equally powerful to Locks+CVs
- what does this mean?
 Equivalence means each can be built from the other
 One might be more convenient for a specific problem
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 5

## Page 6

Proof Steps
Want to show we can do these three things:
Locks
Semaphores
CV’s
Semaphores Locks
Semaphores
CV’s
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 6

## Page 7

Build Lock from Semaphore
typedef struct __lock_t { 
// whatever data structs you need go here
} lock_t;
void init(lock_t *lock) {
}
void lock(lock_t *lock) {
} 
void unlock(lock_t *lock) { 
}
Locks
Semaphores
Sem_wait(): Waits until value > 0, then decrement
Sem_post(): Increment value, then wake a single waiter
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 7

## Page 8

Build Lock from Semaphore
typedef struct __lock_t { 
sem_t sem;
} lock_t;
void init(lock_t *lock) {
sem_init(&lock->sem, ??);
}
void lock(lock_t *lock) {
sem_wait(&lock->sem);
} 
void unlock (lock_t *lock) {
sem_post(&lock->sem); 
}
Locks
Semaphores
1 → 1 thread can grab lock
Such a semaphore is also 
known popularly as binary  
semaphore
General rule for semaphore initialization
Consider the number of resources   
you are willing to give away immedia
-tely after initialization. 
Sem_wait(): Waits until value > 0, then decrement
Sem_post(): Increment value, then wake a single waiter
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 8

## Page 9

Build Semaphore from Lock and CV
Typedef struct {
// what goes here?
} sem_t;
Void sem_init(sem_t *s, int value) {
// what goes here?
}
Locks
Semaphores
CV’sSem_wait(): Waits until value > 0, then decrement
Sem_post(): Increment value, then wake a single waiter
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 9

## Page 10

Build Semaphore from Lock and CV
Typedef struct {
int value;
cond_t cond;
mutex_t lock;
} sem_t;
Void sem_init(sem_t *s, int value) {
s->value = value;
cond_init(&s->cond);
mutex_init(&s->lock);
}
Locks
Semaphores
CV’sSem_wait(): Waits until value > 0, then decrement
Sem_post(): Increment value, then wake a single waiter
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 10

## Page 11

Build Semaphore from Lock and CV
Sem_wait{sem_t *s) {
// what goes here?
}
Sem_post{sem_t *s) {
// what goes here?
}
Locks
Semaphores
CV’sSem_wait(): Waits until value > 0, then decrement
Sem_post(): Increment value, then wake a single waiter
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 11

## Page 12

Build Semaphore from Lock and CV
Sem_wait{sem_t *s) {
mutex_lock(&s->lock);
// this stuff is atomic
mutex_unlock(&s->lock);
}
Sem_post{sem_t *s) {
mutex_lock(&s->lock);
// this stuff is atomic
mutex_unlock(&s->lock);
}
Locks
Semaphores
CV’sSem_wait(): Waits until value > 0, then decrement
Sem_post(): Increment value, then wake a single waiter
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 12

## Page 13

Build Semaphore from Lock and CV
Sem_wait{sem_t *s) {
mutex_lock(&s->lock);
while (s->value <= 0)
cond_wait(&s->cond,& s->lock);
s->value--;
mutex_unlock(&s->lock);
}
Sem_post{sem_t *s) {
mutex_lock(&s->lock);
// this stuff is atomic
mutex_unlock(&s->lock);
}
Locks
Semaphores
CV’sSem_wait(): Waits until value > 0, then decrement
Sem_post(): Increment value, then wake a single waiter
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 13

## Page 14

Build Semaphore from Lock and CV
Sem_wait{sem_t *s) {
mutex_lock(&s->lock);
while (s->value <= 0)
cond_wait(&s->cond,&s->lock);
s->value--;
mutex_unlock(&s->lock);
}
Sem_post{sem_t *s) {
mutex_lock(&s->lock);
s->value++;
cond_signal(&s->cond);
mutex_unlock(&s->lock);
}
Locks
Semaphores
CV’sSem_wait(): Waits until value > 0, then decrement
Sem_post(): Increment value, then wake a single waiter
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 14

## Page 15

Building CV’s over Semaphores
CV’s
Semaphores
typedef struct __cond_t { sem_t s; } cond_t; 
void cond_init(cond_t *c) {    sem_init(&c->s, 0);  } 
void cond_signal(cond_t *c) { 
sem_post(&c->s); // wake up a sleeping thread (if any) 
}
void cond_wait(cond_t *c, mutex_t *m) {
// assumes that lock 'm' is held 
mutex_unlock(&m); // release lock and go to sleep
sem_wait(&c->s); 
mutex_lock(&m); // grab lock before returning
}
Wrong !!
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 15

## Page 16

Building CV’s over Semaphores
Possible, but really hard to do right
Read about Microsoft Research’s attempts:
http://research.microsoft.com/pubs/64242/ImplementingCVs.pdf
CV’s
Semaphores
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 16

## Page 17

Producer/Consumer: Semaphores #1
Simplest case:
 Single producer thread, single consumer thread
 Shared buffer with one element between producer and consumer
Requirements
 Consumer must wait for producer to fill buffer
 Producer must wait for consumer to empty buffer (if filled)
Requires 2 semaphores
 emptyBuffer: Initialize to ???
 fullBuffer: Initialize to ???
Producer
While (1) {
-------------------------
buffer=value;
--------------------------
}
Consumer
While (1) {
-------------------------
value=buffer;
-------------------------
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 17

## Page 18

Producer/Consumer: Semaphores #1
Simplest case:
 Single producer thread, single consumer thread
 Shared buffer with one element between producer and consumer
Requirements
 Consumer must wait for producer to fill buffer
 Producer must wait for consumer to empty buffer (if filled)
Requires 2 semaphores
 emptyBuffer: Initialize to ???
 fullBuffer: Initialize to ???
Producer
While (1) {
sem_wait(&emptyBuffer);
buffer=value;
sem_post(&fullBuffer);
}
Consumer
While (1) {
sem_wait(&fullBuffer);
value=buffer;
sem_post(&emptyBuffer);
}
1 → 1 empty buffer; producer can run 1 time first
0 → 0 full buffers; consumer can run 0 times first
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 18

## Page 19

Producer/Consumer: Semaphores #2
Next case: Circular Buffer
 Single producer thread, single consumer thread
 Shared buffer with N elements between producer and consumer
Requires 2 semaphores
 emptyBuffer: Initialize to ???
 fullBuffer: Initialize to ???
Producer
i = 0;
While (1) {
sem_wait(&emptyBuffer);
buffer[i]=value;
i = (i+1)%N;
sem_post(&fullBuffer);
}
Consumer
j = 0;
While (1) {
sem_wait(&fullBuffer);
value=buffer[j];
j = (j+1)%N;
sem_post(&emptyBuffer);
}
N → N empty buffers; producer can run N times first
0 → 0 full buffers; consumer can run 0 times first
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 19

## Page 20

Producer/Consumer: Semaphore #3
Final case:
 Multiple producer threads, multiple consumer threads
 Shared buffer with N elements between producer and consumer
Requirements
 Each consumer must grab unique filled element
 Each producer must grab unique empty element
 Why will previous code (shown below) not work???
Producer
i = 0;
While (1) {
sem_wait(&emptyBuffer);
buffer[i]=value;
i = (i+1)%N;
sem_post(&fullBuffer);
}
Consumer
j = 0;
While (1) {
sem_wait(&fullBuffer);
value=buffer[j];
j = (j+1)%N;
sem_post(&emptyBuffer);
}
Are i and j private or shared?  
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 20

## Page 21

Producer/Consumer: Semaphore # 4
Final case:
• Multiple producer threads, multiple consumer threads
• Shared buffer with N elements between producer and consumer
Requirements
• Each consumer must grab unique filled element
• Each producer must fill in unique empty slot
Producer
i = 0;
While (1) {
sem_wait(&mutex_p);
sem_wait(&emptyBuffer);
buffer[i]=value;
i = (i+1)%N;
sem_post(&fullBuffer);
sem_post(&mutex_p); 
}
Consumer
j = 0;
While (1) {
sem_wait(&mutex_c);
sem_wait(&fullBuffer);
value=buffer[j]);
j = (j+1)%N;
sem_post(&emptyBuffer);
sem_post(&mutex_c);
}
May work for array based buffer? But if some other DS like linked list then?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 21

## Page 22

Producer/Consumer: Semaphore # 4
Final case:
• Multiple producer threads, multiple consumer threads
• Shared buffer with N elements between producer and consumer
Requirements
• Each consumer must grab unique filled element
• Each producer must fill in unique empty slot
Producer
i = 0;
While (1) {
sem_wait(&mutex);
sem_wait(&emptyBuffer);
buffer[i]=value;
i = (i+1)%N;
sem_post(&fullBuffer);
sem_post(&mutex); 
}
Consumer
j = 0;
While (1) {
sem_wait(&mutex);
sem_wait(&fullBuffer);
value=buffer[j]);
j = (j+1)%N;
sem_post(&emptyBuffer);
sem_post(&mutex);
}
Will it work? Deadlock
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 22

## Page 23

A Solution: Adding Mutual Exclusion (Cont.)
 Imagine two thread: one producer and one consumer.
 The consumer acquire the mutex (line c0).
 The consumer calls sem_wait() on the full semaphore (line c1).
 The consumer is blocked and yield the CPU.
 The consumer still holds the mutex!
 The producer calls sem_wait() on the binary mutex semaphore (line p0).
 The producer is now stuck waiting too. a classic deadlock.
23Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 24

Producer/Consumer: Working solution!
Are myi and myj private or shared? Where is mutual exclusion needed???
Final case:
• Multiple producer threads, multiple consumer threads
• Shared buffer with N elements between producer and consumer
Requirements
• Each consumer must grab unique filled element
• Each producer must grab unique empty element
Producer
i = 0;
While (1) {
sem_wait(&emptyBuffer);
sem_wait(&mutex);
buffer[i]=value;
i = (i+1)%N;
sem_post(&mutex);
sem_post(&fullBuffer); 
}
Consumer
j = 0;
While (1) {
sem_wait(&fullBuffer);
sem_wait(&mutex);
value=buffer[j];
j = (j+1)%N;
sem_post(&mutex);
sem_post(&emptyBuffer);
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 24

## Page 25

Reader-Writer Problem
 Imagine a number of concurrent list operations, including 
inserts and simple lookups.
 insert:
 Change the state of the list
 A traditional critical section makes sense.
 lookup:
 Simply read the data structure.
 As long as we can guarantee that no insert is on-going, we can allow 
many lookups to proceed concurrently.
25
This special type of lock is known as a reader-write lock.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 26

A Reader-Writer Locks
 Once a single writer acquires a write lock - any other thread (writer 
or reader) will have to wait.
 Once a reader acquires a lock, 
 More readers will be allowed to acquire the lock too.
 A writer can then be made to wait until all readers are finished.
26
1 typedef struct _rwlock_t { 
2 …… 
3 } rwlock_t; 
4
5 void rwlock_init(rwlock_t *rw) { 
6 …
7 } 
Many Readers can be in critical section 
OR
One writer 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 27

A Reader-Writer Locks
 Once a single writer acquires a write lock - any other thread (writer 
or reader) will have to wait.
 Once a reader acquires a lock, 
 More readers will be allowed to acquire the lock too.
 A writer can then be made to wait until all readers are finished.
27
1 typedef struct _rwlock_t { 
2 sem_t lock; // binary semaphore (basic lock) 
3 sem_t writelock; // used to allow ONE writer or MANY readers 
4 int readers; // count of readers reading in critical section
5 } rwlock_t; 
6
7 void rwlock_init(rwlock_t *rw) { 
8 rw->readers = 0; 
9 sem_init(&rw->lock, 0, 1); 
10 sem_init(&rw->writelock, 0, 1); 
11 } 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 28

A Reader-Writer Locks (Cont.)
28
14 void rwlock_acquire_writelock(rwlock_t *rw) { 
15 …
16 } 
17
18 void rwlock_release_writelock(rwlock_t *rw) { 
19 …
20 }
21
13 void rwlock_acquire_readlock(rwlock_t *rw) { 
14 …
14 } 
15
16 void rwlock_release_readlock(rwlock_t *rw) { 
17 … 
18 } 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 29

A Reader-Writer Locks (Cont.)
29
14 void rwlock_acquire_writelock(rwlock_t *rw) { 
15 sem_wait(&rw->writelock); 
16 } 
17
18 void rwlock_release_writelock(rwlock_t *rw) { 
19 sem_post(&rw->writelock); 
20 }
21
13 void rwlock_acquire_readlock(rwlock_t *rw) { 
…
14 } 
15
16 void rwlock_release_readlock(rwlock_t *rw) { 
17 … 
18 } 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 30

A Reader-Writer Locks (Cont.)
30
14 void rwlock_acquire_writelock(rwlock_t *rw) { 
15 sem_wait(&rw->writelock); 
16 } 
17
18 void rwlock_release_writelock(rwlock_t *rw) { 
19 sem_post(&rw->writelock); 
20 }
21
13 void rwlock_acquire_readlock(rwlock_t *rw) { 
14 sem_wait(&rw->lock); 
15 rw->readers++; 
16 if (rw->readers == 1) 
17 sem_wait(&rw->writelock); // first reader acquires writelock
18 sem_post(&rw->lock); 
19 } 
20
21 void rwlock_release_readlock(rwlock_t *rw) { 
22 …
23 } 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 31

A Reader-Writer Locks (Cont.)
31
14 void rwlock_acquire_writelock(rwlock_t *rw) { 
15 sem_wait(&rw->writelock); 
16 } 
17
18 void rwlock_release_writelock(rwlock_t *rw) { 
19 sem_post(&rw->writelock); 
20 }
21
13 void rwlock_acquire_readlock(rwlock_t *rw) { 
14 sem_wait(&rw->lock); 
15 rw->readers++; 
16 if (rw->readers == 1) 
17 sem_wait(&rw->writelock); // first reader acquires writelock
18 sem_post(&rw->lock); 
19 } 
20
21 void rwlock_release_readlock(rwlock_t *rw) { 
22 sem_wait(&rw->lock); 
23 rw->readers--; 
24 if (rw->readers == 0) 
25 sem_post(&rw->writelock); //last reader releases writelock
26 sem_post(&rw->lock); 
27 } 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 32

A Reader-Writer Locks (Cont.)
 This version of reader-writer lock have fairness problem.
 It would be relatively easy for reader to starve writer.
 How to prevent more readers from entering the lock once a writer 
is waiting?
 H/W exercise
32Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 33

The Dining Philosophers
 Assume there are five “philosophers” sitting around a table.
 Between each pair of philosophers is a single fork (five total).
 The philosophers each have times where they think, and don’t need any 
forks, and times where they eat.
 In order to eat, a philosopher needs two forks, both the one on their left
and the one on their right.
 The contention for these forks.
33
P1
f1
P0
P4
f0
f4
P3
f3
P2
f2
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 34

The Dining Philosophers (Cont.)
 Key challenge
 There should be no deadlock.
 No philosopher starves and never gets to eat.
 Concurrency is high.
 Philosopher p wishes to refer to the fork on their left → call left(p).
 Philosopher p wishes to refer to the fork on their right → call right(p).
34
while (1) {
think();
getforks(p);
eat();
putforks(p);
}
// helper functions
int left(int p) { return p; }
int right(int p) {
return (p + 1) % 5;
}
Basic loop of each philosopher Helper functions (Downey’s solutions)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 35

The Dining Philosophers (Cont.)
 We need some semaphore, one for each fork: sem_t forks[5].
 Deadlock occur!
 If each philosopher happens to grab the fork on their left before any 
philosopher can grab the fork on their right.
 Each will be stuck holding one fork and waiting for another, forever.
35
1 void getforks(int p) { 
2 sem_wait(forks[left(p)]); 
3 sem_wait(forks[right(p)]); 
4 } 
5
6 void putforks(int p) { 
7 sem_post(forks[left(p)]); 
8 sem_post(forks[right(p)]); 
9 } 
The getforks() and putforks() Routines (Broken Solution)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 36

A Solution: Breaking The Dependency
 Change how forks are acquired.
 Let’s assume that philosopher p=4 acquire the forks in a different order.
 There is no situation where each philosopher grabs one fork and is 
stuck waiting for another. The cycle of waiting is broken.
36
1 void getforks(int p) { 
2 if (p == 4) { 
3 sem_wait(forks[right(p)]); 
4 sem_wait(forks[left(p)]); 
5 } else { 
6 sem_wait(forks[left(p)]); 
7 sem_wait(forks[right(p)]); 
8 } 
9 } 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 37

Problem 1:
There are three process P, Q, and R. All of them are executing a loop from 1 to N. You wish to 
enforce the condition that no process may start the execution of (I+1)th iteration until the other  
two processes have completed the Ith iteration. Using a pseudo code, show how this condition  
can be correctly enforced (of course without causing deadlock) using semaphores
Note: up() is basically sem_post operation and down() is sem_wait() operation
37Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur


## Page 38

Problem 2:
Below is the outline for a concurrent program in which the two functions (X and Y) are called
repeatedly by two threads (assume that). Notice that each of statements A, B, C, and D appear
in either X or Y. Also notice that some space has been left before and after each of those state
ments so that you can add code to the processes. You have to add (ONLY) sem_wait and sem
_post statements (you may add one or more) at the designated points so that the order in whic
h statements A, B, C, and D should be executed by this concurrent program is like A;B;C;D;A
;B;C;D;A;B;C;D....... Make use of the following general semaphores.
 s : semaphore initial (1), t : semaphore initial (0)
38Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur


## Page 39

Problem 3:
You have been hired by the Traffic control authority to synchronize traffic over a very narrow,
light-duty bridge on a public highway. Traffic can only cross the bridge in one direction at a ti-
me, and if there are ever more than 3 vehicles on the bridge at one time, it will collapse under
their weight. In this system, each car is represented by one thread, which executes the procedur
e OneVehicle when it arrives at the bridge: OneVehicle(int direc){ ArriveBridge(direc); Cros
sBridge(direc); ExitBridge(direc); }
In the code above, direc is either 0 or 1; it gives the direction in which the vehicle will cross the
bridge. Your task is to implement the procedures ArriveBridge and ExitBridge (the CrossBridg
e procedure would just print out a debug message) using semaphores. ArriveBridge must not re
turn until it is safe for the car to cross the bridge in the given direction (it must guarantee that
there will be no head-on collisions/deadlock or bridge collapses). ExitBridge is called to indica
-te that the caller has finished crossing the bridge; ExitBridge should take steps to let additional
cars cross the bridge. This is a lightly-travelled rural bridge, so you do not need to guarantee fai
-rness or freedom from starvation. Give proper explanation to justify your solution works
39Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 40

Solution 
40Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

