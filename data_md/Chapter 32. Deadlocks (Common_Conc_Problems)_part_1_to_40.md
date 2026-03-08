# Document: Chapter 32. Deadlocks (Common_Conc_Problems) (Pages 1 to 40)

## Page 1

Concurrency Bugs (on Deadlocks).
chap 32 of Operating System: Three Easy Pieces
Chap 7 of Operating System concepts: Silberschatz
1Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 2

Source:: http://pages.cs.wisc.edu/~shanlu/paper/asplos122-lu.pdf
Concurrency Study by Lu et.al. (2008)
OpenOfficeApache
0
15
30
45
60
75
MySQL Mozilla
Bugs
Atomicity Order Deadlock Other
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 2

## Page 3

Operating Systems by Dr. Praveen K
umar @ CSED, VNIT Nagpur 3
Think of few Deadlock example’s encountered in   
real life!

## Page 4

STOP
STOP
STOP
STOP
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 4

## Page 5

STOP
STOP
STOP
STOP
A
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 5

## Page 6

STOP
STOP
STOP
STOP
A
B
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 6

## Page 7

STOP
STOP
STOP
STOP
A
B
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 7

## Page 8

STOP
STOP
STOP
STOP
A
B
who goes?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 8

## Page 9

STOP
STOP
STOP
STOP
A
B
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 9

## Page 10

STOP
STOP
STOP
STOP
A
B
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 10

## Page 11

STOP
STOP
STOP
STOP
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 11

## Page 12

STOP
STOP
STOP
STOP
A
B
C
D
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 12

## Page 13

STOP
STOP
STOP
STOP
A
B
C
D
who goes?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 13

## Page 14

STOP
STOP
STOP
STOP
AB
CD
who goes?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 14

## Page 15

STOP
STOP
STOP
STOP
AB
CD
Deadlock!
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 15

## Page 16

Code Example
Thread 2:
lock(&B);
lock(&A);
Thread 1:
lock(&A);
lock(&B);
Can deadlock happen with these two threads?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 16

## Page 17

Circular Dependency
Lock A
Lock B
Thread 1
Thread 2
holds
holds
Requests Requests
Resource allocation graph
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 17

## Page 18

Fix Deadlocked Code
Thread 2
lock(&A);
lock(&B);
Thread 1
lock(&A);
lock(&B);
Thread 2:
lock(&B);
lock(&A);
Thread 1:
lock(&A);
lock(&B);
How would you fix this code?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 18

## Page 19

Non-circular Dependency (fine)
Lock A
Lock B
Thread 1
Thread 2
holds
Requests Requests
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 19

## Page 20

Why Do Deadlock occur?
 In large code bases, complex dependencies arise 
between components 
 For example - operating system
 The virtual memory system might need to access the 
file system in order to page in a block from disk; 
 The file system might subsequently require a page of  
memory to read the block into and thus contact the vir-
tual memory system.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 20

## Page 21

Why Do Deadlock occur?
 Encapsulation/Modularity can make it harder to  
see deadlocks
void transaction(Account from, Account to, double amount){ 
mutex lock1, lock2; 
lock1 = get_lock(from); 
lock2 = get_lock(to); 
acquire(lock1); 
acquire(lock2); 
withdraw(from, amount); 
deposit(to, amount); 
release(lock2); 
release(lock1); 
} 
Transactions 1 and 2 execute concurrently.  Transaction  1 transfers $25 from acc-
ount A to account B, and Transaction 2 transfers $50 from account B to account A
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 21

## Page 22

Deadlock
A broad definition of Deadlock: A set of processes is dead-
locked if each process in the set is waiting for an event that 
only another process in the set can cause.
Necessary Conditions:
 Mutual Exclusion: process claim exclusive control of resources  
that they require (e.g., thread grabs a lock)
 Hold and wait:Threads hold resources allocated to them (e.g.  
locks they have already acquired) while waiting for additional   
resources (e.g., locks they wish to acquire).
 No preemption: Resources cannot be preempted
 Circular wait: There must be a cycle of dependency among 
a set of processes and resources.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 22

## Page 23

Deadlock Prevention
Since Deadlocks can only happen with these four condi-
tions:
- mutual exclusion
- hold-and-wait
- no preemption
- circular wait
Eliminate deadlock by eliminating any one condition
STOP
STOP
STOP
STOP
AB
CD
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 23

## Page 24

Eliminating Circular Wait
Strategy: provide a total (or partial) ordering on lock 
acquisition
- decide which locks should be acquired before others
- ex. if only two locks, always acquire A before B
- a clever programmer can use the address of each lock  
as a way of ordering lock acquisition
Do_something(mutex *m1,mutex *m2) {
if(m1>m2) {
lock(m1);
lock(m2);
} 
else {
lock(m2);
lock(m1);
} …
}
- Works well if such distinct ordering is possible
- Requires careful design
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 24

## Page 25

Eliminate Hold-and-Wait
Strategy: Acquire all locks atomically once
Can release locks over time, but cannot acquire again until all 
have been released
How to do this?  Use a meta lock, like this:
lock(&meta);
lock(&L1);
lock(&L2);
…
unlock(&meta);
// Critical section code
unlock(…);
Disadvantages?
Must know ahead of time which locks will be needed
Must be conservative (acquire any lock possibly needed)
Degenerates to just having one big lock
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 25

## Page 26

Support Preemption
Strategy: if thread can’t get what it wants, release what it      
holds
 trylock()
 Grabs the lock (if it is available) or return -1: you should try again later.
 Doesn’t really add preemption but allows process to back out.
Example –
top:
lock(A);
if (trylock(B) == -1) {
unlock(A);
goto top;
}
…
Disadvantages?
Livelock: 
no processes make progress, but the state 
of involved processes constantly changes
Exponential back-off may be needed
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 26

## Page 27

Eliminate locks!
Strategy: design various DS/algo without locks (Wait/lock-Free!) 
Try to replace locks with atomic primitive:
int CompAndSwap(int *addr, int expected, int new)
Returns 0: fail, 1: success
void add (int *val, int amt) {
do {
int old = *val;
} while(!CompAndSwap(val,??,old+amt));
}
void add (int *val, int amt)
{
Mutex_lock(&m);
*val += amt;
Mutex_unlock(&m);
}
?? → old
1 int CompAndSwap(int *addr, int expected, int new) {
2 if (*addr == expected){
3 *addr = new;
4 return 1; //success }
5 return 0; // failure
6 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 27

## Page 28

Lock-Free: Linked List Insert
void insert (int val) {
node_t *n = Malloc(sizeof(*n));
n->val = val;
lock(&m);
n->next = head;
head = n;
unlock(&m);
}
void insert (int val) {
node_t *n = Malloc(sizeof(*n));
n->val = val;
do {
n->next = head;
} while (!CompAndSwap(&head, 
n->next, n));
}
Strategy:  design various DS/algo without locks (Wait/lock-Free!) 
Try to replace locks with atomic primitive:
int CompAndSwap(int *addr, int expected, int new)
Returns 0: fail, 1: success
Limited utility due to lack of generality and 
complexityOperating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 28

## Page 29

Deadlock Avoidance
 Since direct approaches to prevent the necessary deadlock 
conditions has their limitations, in some scenarios 
deadlock avoidance may be preferable.
 Avoidance methods (indirect) makes judicious choices 
dynamically to ensure that deadlock point is never reached
 Global knowledge of future requests is required: Which lock/resources various 
threads might grab/require during their execution.
 May lead to a more conservative approach (i.e low resource utilization)
29Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 30

Example of Deadlock Avoidance via Scheduling (1) 
 Using knowledge of future request, schedule threads in a way as to 
guarantee no deadlock can occur.
 We have two processors and four threads.
 Lock acquisition demands of the threads:
 A smart scheduler could compute that as long as T1 and T2 are not run at 
the same time, no deadlock could ever arise.
30
T1 T2 T3 T4
L1 yes yes no no
L2 yes yes yes no
CPU 1
CPU 2
T3 T4
T1 T2
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 31

Example of Deadlock Avoidance via Scheduling (2) 
 More contention for the same resources
 A possible schedule that guarantees that no deadlock could ever occur.
 The total time to complete the jobs is lengthened considerably.
31
T1 T2 T3 T4
L1 yes yes yes no
L2 yes yes yes no
CPU 1
CPU 2 T3
T4
T1 T2
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 32

Deadlock Avoidance in General
 A general Algorithm for Deadlock Avoidance involves:
 Apriori knowledge of the entire set of tasks that must be 
run and the resources that are available
 each process declare the maximum number of resources 
of each type that it may need
 Before any request for resource allocation is granted to a 
process, ensure that the allocation will not leave the       
system in a (unsafe) state where a deadlock can occur.
 Safe state: if the system can allocate resources to each  
process (up to its maximum) in some order and still avoid 
a deadlock.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 32

## Page 33

Determination of Safe State
 A system is in a safe state if there exists a sequence of    
resource assignments such that each process can be      
allocated its maximum request, thus enabling the process  
to complete and then release the resources, and then      
allow remaining processes to do the same.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 33

## Page 34

Determination of Safe State
 An Example of multiple instances of a resource
Process   Max Needs       Allocated Total
P0 10 5 12
P1 4 2 Avail
P2 9 2 3
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 34

## Page 35

Determination of Safe State
 An Example of multiple instances of a resource
Process   Max Needs       Allocated Total
P0 10 5 12
P1 4 2→4 Avail
P2 9 2 3→1
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 35

## Page 36

Determination of Safe State
 An Example of multiple instances of a resource
Process   Max Needs       Allocated Total
P0 10 5 12
P1 0 4→0 Avail
P2 9 2 1→5
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 36

## Page 37

Determination of Safe State
 An Example of multiple instances of a resource
Process   Max Needs       Allocated Total
P0 10 5→10 12
P1 0 0 Avail
P2 9 2 5→0
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 37

## Page 38

Banker's Algorithm
 Use vectors and matrices to identify resource requi-
rements
 Available[j] = k;  //resource j has k instances available
 Max[i,j] =k;//Process i may need k instances of resource j
 Allocation [i,j] = k;  //Process i is currently allocated k ins-
tances of resource j
 Need[i,j] = k; // Process i may need as many as k more  
of resource j.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 38

## Page 39

Banker's Example
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2
P1 2  0  0 3  2  2
P2 3  0  2 9  0  2
P3 2  1  1 2  2  2
P4 0  0  2 4  3  3
Is the system in a safe state? Yes. Possible ordering- P3, P1, P4,P2,P0
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 39

## Page 40

Banker's Example (change 1)
P1 requests (1  0  2)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2
P1 2  0  0 3  2  2
P2 3  0  2 9  0  2
P3 2  1  1 2  2  2
P4 0  0  2 4  3  3
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 40

