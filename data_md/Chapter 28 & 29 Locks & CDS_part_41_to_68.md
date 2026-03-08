# Document: Chapter 28 & 29 Locks & CDS (Pages 41 to 68)

## Page 41

Using Queues: Sleeping Instead of Spinning
43
1 typedef struct __lock_t {
2 int flag; //state of lock 1 = held, 0=free
3 int guard; //use to protect flag, queue
4 queue_t *q; // explicit queue of waiters
5 } lock_t;
6
7 void lock_init(lock_t *m) {
8 m->flag = 0; 
9 m->guard = 0;
10 queue_init(m->q); }
11
12 void lock(lock_t *m) {
13 while (TestAndSet(&m->guard, 1) == 1)
14 ; // acquire guard lock by spinning
15 if (m->flag == 0) {// lock is free: grab it
16 m->flag = 1; // lock is acquired
17 m->guard = 0; // release guard
18 } else { // lock not free
19 queue_add(m->q, gettid()); // add self to the queue
20 m->guard = 0; // release guard
21 park(); // put self to sleep and yield CPU
22 }
23 } Lock With Queues, Test-and-set, Yield, And Wakeup
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 42

Using Queues: Sleeping Instead of Spinning
44
22 void unlock(lock_t *m) {
23 while (TestAndSet(&m->guard, 1) == 1)
24 ; // acquire guard lock by spinning
25 if (queue_empty(m->q))
26 m->flag = 0; // let go of lock; no one wants it
27 else
28 unpark(queue_remove(m->q)); // hold lock (for 
next thread!)
29 m->guard = 0;
30 } Lock With Queues, Test-and-set, Yield, And Wakeup (Cont.)
Questions:
(a) Why is guard used? 
(b) Why okay to spin on guard?
(c) In lock() why release of guard is done before the park
()?
(d) In unlock(), why not set flag=0 when unpark?
(e) What is the race condition here?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 43

Race Condition
45
Thread 1
else {
queue_add(m->q,gettid());
m->guard = 0;
park();    // block
(in unlock)(in lock)
 Thread 2
while (TestAndSet(&m->guard, 1) == 1)
; // acquire guard lock by spinnin
g
if (queue_empty(m->q))
m->flag = 0; // let go of lock; 
else
unpark(queue_remove(m->q));
m->guard = 0;
Problem: Guard not held when call park()
Unlocking thread may unpark() before other park() 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 44

Wakeup/waiting race
 In case of releasing the lock (thread A) just before the call to park() 
(thread B) → Thread B would sleep forever (potentially).
 Solaris solves this problem by adding a third system call: setpark().
 By calling this routine, a thread can indicate it is about to park.
 If it happens to be interrupted and another thread calls unpark before 
park is actually called, the subsequent park returns immediately instead 
of sleeping.
46
1 queue_add(m->q, gettid());
2 setpark(); // new code
3 m->guard = 0;
4 park();
Code modification inside of lock()
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 45

Futex
 Linux provides a futex (similar to Solaris’s park and 
unpark)
 futex_wait(address, expected)
 Put the calling thread to sleep
 If the value at address is not equal to expected, the call returns 
immediately.
 futex_wake(address)
 Wake one thread that is waiting on the queue.
47Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 46

Spin-Waiting vs Blocking
 Each approach is better under different circumstances. In  
uniprocessor case, blocking is advisable
 In multiprocessor case, Spin or block depends on how      
long (t) before lock is released and the overhead cost of  
putting a thread to sleep and waking it up again (C)
 What is the best action when t<C (Lock released quickly)
Spin-wait
 When t>C (Lock released slowly)? 
Block
48Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 47

Two-Phase/hybrid Locks
 A two-phase/hybrid lock Spin-wait for C then 
blocks.
 First phase
 The lock spins for a while (C) , hoping that it can acquire the 
lock.
 If the lock is not acquired during the first spin phase, a second 
phase is entered, 
 Second phase
 The caller is put to sleep.
 The caller is only woken up when the lock becomes free later.
49Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 48

Pthread API
 Pthread provides both spinlock and mutex (blocking)
 pthread_spinlock_t spinlock;
 pthread_mutex_t mutex;
 For lock and unlock:
 pthread_spin_lock(&spinlock);
 pthread_spin_unlock(&spinlock);
 pthread_mutex_lock(&mutex);
 pthread_mutex_unlock(&mutex);
 Initialization done to specify attributes and type of lock
 pthread_spin_init(&spinlock, 0);
 pthread_mutex_init(&mutex, NULL);
50Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 49

Lock-based Concurrent Data structure
 Adding locks to a data structure makes the structure 
thread safe.
 How locks are added determine both the correctness and 
performance of the data structure.
51Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 50

Example: Concurrent Counters without Locks
 Simple but not scalable
52
1 typedef struct __counter_t {
2 int value;
3 } counter_t;
4
5 void init(counter_t *c) {
6 c->value = 0;
7 }
8
9 void increment(counter_t *c) {
10 c->value++;
11 }
12
13 void decrement(counter_t *c) {
14 c->value--;
15 }
16
17 int get(counter_t *c) {
18 return c->value;
19 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 51

Example: Concurrent Counters with Locks
 Add a single lock.
 The lock is acquired when calling a routine that manipulates the 
data structure.
53
1 typedef struct __counter_t {
2 int value;
3 pthread_lock_t lock;
4 } counter_t;
5
6 void init(counter_t *c) {
7 c->value = 0;
8 Pthread_mutex_init(&c->lock, NULL);
9 }
10
11 void increment(counter_t *c) {
12 Pthread_mutex_lock(&c->lock);
13 c->value++;
14 Pthread_mutex_unlock(&c->lock);
15 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 52

Example: Concurrent Counters with Locks (Cont.)
54
(Cont.)
17 void decrement(counter_t *c) {
18 Pthread_mutex_lock(&c->lock);
19 c->value--;
20 Pthread_mutex_unlock(&c->lock);
21 }
22
23 int get(counter_t *c) {
24 Pthread_mutex_lock(&c->lock);
25 int rc = c->value;
26 Pthread_mutex_unlock(&c->lock);
27 return rc;
28 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 53

The performance costs of the simple approach
 Each thread updates a single shared counter.
 Each thread updates the counter one million times.
 iMac with four Intel 2.7GHz i5 CPUs.
55
Performance of
Traditional vs. Sloppy Counters
(Threshold of Sloppy, S, is set to 
1024)
Synchronized counter scales poorly.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 54

Sloppy counter
 The sloppy counter works by representing …
 A single logical counter via numerous local physical counters, one 
per CPU core
 A single global counter
 There are locks:
 One for each local counter and one for the global counter
 Example: on a machine with four CPUs
 Four local counters
 One global counter
56Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 55

The basic idea of sloppy counting
 When a thread running on a core wishes to increment the 
counter.
 It increment its local counter.
 Each CPU has its own local counter:
 Threads across CPUs can update local counters without contention.
 Thus counter updates are scalable.
 The local values are periodically transferred to the global counter.
 Acquire the global lock
 Increment it by the local counter’s value
 The local counter is then reset to zero.
57Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 56

The basic idea of sloppy counting (Cont.)
 How often the local-to-global transfer occurs is 
determined by a threshold, S (sloppiness).
 The smaller S: more the counter behaves like the traditional one
 The bigger S: More scalable the counter, less precise global value
58
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 57

Sloppy Counter Implementation
59
1      typedef struct __counter_t {
2          int global; // global count
3          pthread_mutex_t glock; // global lock
4          int local[NUMCPUS]; // local count (per cpu)
5          pthread_mutex_t llock[NUMCPUS]; // ... and locks
6          int threshold; // update frequency
7      } counter_t;
8
9      // init: record threshold, init locks, init values
10     //       of all local counts and global count
11     void init(counter_t *c, int threshold) {
12         c->thres hold = threshold;
13         c->global = 0;
15         pthread_mutex_init(&c->glock, NULL);
16         int i;
18         for (i = 0; i < NUMCPUS; i++) {
19             c->local[i] = 0;
20             pthread_mutex_init(&c->llock[i], NULL);
21         }
22     }
23
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 58

Sloppy Counter Implementation (Cont.)
60
24 // update: usually, just grab local lock and update local amount
25 //       once local count has risen by ’threshold’, grab global
26     //         lock and transfer local values to it
27     void update(counter_t *c, int threadID, int amt) {
28         pthread_mutex_lock(&c->llock[threadID]);
29         c->local[threadID] += amt; // assumes amt > 0
30         if (c->local[threadID]>= c->threshold){//send to global
31             pthread_mutex_lock(&c->glock);
32             c->global += c->local[threadID];
33             pthread_mutex_unlock(&c->glock);
34             c->local[threadID] = 0;
35         }
36         pthread_mutex_unlock(&c->llock[threadID]);
37     }
38
39     // get: just return global amount (which may not be perfect)
40     int get(counter_t *c) {
41         pthread_mutex_lock(&c->glock);
42         int val = c->global;
43         pthread_mutex_unlock(&c->glock);
44         return val; // only approximate!
45     }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 59

Concurrent Linked List
 Let us consider multi-threaded applications that do more  
than increment shared variable
 Multi-threaded application with shared linked-list
 All concurrent:
 Thread A inserting element a
 Thread B inserting element b
 Thread C looking up element c
61Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 60

Void List_Insert(list_t *L, 
int key) { 
node_t *new = 
malloc(sizeof(node_t)); 
assert(new);
new->key = key;
new->next = L->head;
L->head = new; 
}
int List_Lookup(list_t *L, int key) { 
node_t *tmp = L->head;
while (tmp) { 
if (tmp->key == key) 
return 1; 
tmp = tmp->next; 
} 
return 0; 
}
typedef struct __node_t { 
int key; 
struct __node_t *next;
} node_t;
Typedef struct __list_t {
node_t *head;
} list_t;
Void List_Init(list_t *L) {
L->head = NULL;
}
What can go wrong?
Find schedule that leads t
o problem?
Shared Linked List
Operating Systems by Dr. Praveen K
umar @ CSED, VNIT Nagpur 62

## Page 61

Linked-List Race
Thread 1 Thread 2    
new->key = key
new->next = L->head
new->key = key
new->next = L->head
L->head = new
L->head = new
Both entries point to old head
Only one entry (which one?) can be the new head.
63Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 62

head
T1’s
node
old
head n3 n4 …
T2’s
node
Resulting Linked List
[orphan node]
64Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 63

Void List_Insert(list_t *L, 
int key) { 
node_t *new = 
malloc(sizeof(node
_t)); 
assert(new);
new->key = key;
new->next = L->head;
L->head = new; 
}
int List_Lookup(list_t *L, int
key) { 
node_t *tmp = L->head;
while (tmp) { 
if (tmp->key == ke
y) return 
1; 
tmp = tmp->next; 
} 
return 0; 
} 
typedef struct __node_t { 
int key; 
struct __node_t *next;
} node_t;
Typedef struct __list_t {
node_t *head;
} list_t;
Void List_Init(list_t *L) {
L->head = NULL;
}
How to add locks?
Locking Linked Lists
Operating Systems by Dr. Praveen K
umar @ CSED, VNIT Nagpur 65

## Page 64

typedef struct __node_t { 
int key; 
struct __node_t *next;
} node_t;
Typedef struct __list_t {
node_t *head;
} list_t;
Void List_Init(list_t *L) {
L->head = NULL;
}
How to add locks?
typedef struct __node_t { 
int key; 
struct __node_t *next;
} node_t;
Typedef struct __list_t {
node_t *head;
pthread_mutex_t lock;
} list_t;
Void List_Init(list_t *L) {
L->head = NULL;
pthread_mutex_init(&L->lock,
NULL);
}
One lock per list
pthread_mutex_t lock;
Locking Linked Lists
Operating Systems by Dr. Praveen K
umar @ CSED, VNIT Nagpur 66

## Page 65

Void List_Insert(list_t *L, 
int key) { 
node_t *new = 
malloc(sizeof(node_t)); 
assert(new);
new->key = key;
new->next = L->head;
L->head = new; 
}
int List_Lookup(list_t *L, 
int key) { 
node_t *tmp = L->head;
while (tmp) { 
if (tmp->key == key) 
return 1; 
tmp = tmp->next; 
} 
return 0; 
}
Consider everything critical section
Pthread_mutex_lock(&L->lock);
Pthread_mutex_unlock(&L->lock);
Pthread_mutex_lock(&L->lock);
Pthread_mutex_unlock(&L->lock);
Can critical section be smaller?
Locking Linked Lists: #1
Operating Systems by Dr. Praveen K
umar @ CSED, VNIT Nagpur 67

## Page 66

Void List_Insert(list_t *L, 
int key) { 
node_t *new = 
malloc(sizeof(node_t)); 
assert(new);
new->key = key;
new->next = L->head;
L->head = new; 
}
int List_Lookup(list_t *L,      
int key) { 
node_t *tmp = L->head;
while (tmp) { 
if (tmp->key == key) 
return 1; 
tmp = tmp->next; 
} 
return 0; 
}
Critical section small as possible
Pthread_mutex_lock(&L->lock);
Pthread_mutex_unlock(&L->lock);
Pthread_mutex_lock(&L->lock);
Pthread_mutex_unlock(&L->lock);
Locking Linked Lists: #2
Operating Systems by Dr. Praveen K
umar @ CSED, VNIT Nagpur 68

## Page 67

Void List_Insert(list_t *L, 
int key) { 
node_t *new = 
malloc(sizeof(node_t)); 
assert(new);
new->key = key;
new->next = L->head;
L->head = new; 
}
int List_Lookup(list_t *L,      
int key) { 
node_t *tmp = L->head;
while (tmp) { 
if (tmp->key == key) 
return 1; 
tmp = tmp->next; 
} 
return 0; 
}
What about Lookup()?
Pthread_mutex_lock(&L->lock);
Pthread_mutex_unlock(&L->lock);
Pthread_mutex_lock(&L->lock);
Pthread_mutex_unlock(&L->lock);
If no List_Delete(), locks not needed
Locking Linked Lists: #3
Operating Systems by Dr. Praveen K
umar @ CSED, VNIT Nagpur 69

## Page 68

H/W Reading exercise
 Study about concurrent queues and hash table from chapter 29 
of the book 
70Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

