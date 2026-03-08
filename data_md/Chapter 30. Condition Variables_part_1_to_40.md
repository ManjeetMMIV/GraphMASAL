# Document: Chapter 30. Condition Variables (Pages 1 to 40)

## Page 1

30. Condition Variables
Operating System: Three Easy Pieces
1Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 2

Concurrency/Sychronization Objectives
 Mutual exclusion (e.g., A and B don’t run a critical section 
at the same time) - solved with locks
 Ordering (e.g., B runs/continues execution after A does 
something). Example:
 A parent thread might wish to check whether a child thread has 
completed. - This is often called a join().
 Producer/Consumer threads may wish to check whether a condition
is true before continuing their job/execution.
2Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 3

Ordering Example: Join
3
1 void *child(void *arg) {
2 printf("child\n");
3 // XXX how to indicate we are done?
4 return NULL;
5 }
6
7 int main(int argc, char *argv[]) {
8 printf("parent: begin\n");
9 pthread_t c;
10 Pthread_create(&c, NULL, child, NULL); 
11 // XXX how to wait for child?
12 printf("parent: end\n");
13 return 0;
14 }
parent: begin
child
parent: end
A Parent Waiting For Its Child
What we would like to see here is:
how to implement join()?
how to implement exit()?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 4

Parent waiting for child: Spin-based Approach
 This is hugely inefficient as the parent spins and wastes CPU time.
4
1 volatile int done = 0;
2
3 void *child(void *arg) {
4 printf("child\n");
5 done = 1;
6 return NULL;
7 }
8
9 int main(int argc, char *argv[]) {
10 printf("parent: begin\n");
11 pthread_t c;
12 Pthread_create(&c, NULL, child, NULL); 
13 while (done == 0)
14 ; // spin
15 printf("parent: end\n");
16 return 0;
17 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 5

Condition Variables
 Need a new synchronization primitive: Condition Variables
 A Condition Variable (CV) is a DS with an explicit queue where  
threads can put themselves to sleep (block), when waiting until 
a condition is not true: wait(&CV, …)
 Another thread that makes the condition true can signal the CV 
to wake up a waiting thread: signal(&CV)
 Remember the problem encountered earlier: if you go to sleep 
while holding the lock or if you release it before sleep, in either 
case you can end up deadlock or sleeping forever
 CV allows to atomically release the lock with wait
5Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 6

Join Implementation: Attempt 1
void thread_exit() {
Cond_signal(&c);
}
void thread_join() {
Cond_wait(&c);
}
Parent: Child:
Will it Work?
No. If child runs before parent calls joins, it will sleep forever
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 6

## Page 7

Rule of Thumb 1
 Need to Keep state in addition to CV’s!
 CV’s are used to signal threads when state changes
 If state is already as needed, thread shouldn’t wait for a signal!
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 7

## Page 8

Join Implementation: Attempt 2
void thread_join() {
Mutex_lock(&m); // w
if (done == 0) // x
Cond_wait(&c, &m); // y
Mutex_unlock(&m); // z
}
Parent:
 x
 (y wont be executed)
Child:
 a
 b
Fixes previous broken ordering:
void thread_exit() {
done = 1; // a
Cond_signal(&c); // b
}
void thread_join() {
if (done == 0) // x
Cond_wait(&c); // y
}
Parent: Child:
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 8

## Page 9

Parent:
 x
 y
Child:
 a
 b
… sleep forever …
Can you construct ordering that does not work?
Join Implementation: Attempt 2
void thread_join() {
Mutex_lock(&m); // w
if (done == 0) // x
Cond_wait(&c, &m); // y
Mutex_unlock(&m); // z
}
void thread_exit() {
done = 1; // a
Cond_signal(&c); // b
}
void thread_join() {
if (done == 0) // x
Cond_wait(&c ); // y
}
Parent: Child:
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 9

## Page 10

Join Implementation: Attempt 3 using locks
void thread_join() {
Mutex_lock(&m); // w
if (done == 0) // x
Cond_wait(&c, &m); // y
Mutex_unlock(&m); // z
}
void thread_exit() {
Mutex_lock(&m); // a
done =1; // b
Cond_signal(&c); // c
Mutex_unlock(&m);// d
}
void thread_join() {
Mutex_lock(&m); // w
if (done == 0) // x
Cond_wait(&c); // y
Mutex_unlock(&m); // z
}
Parent: Child:
• Fixes previous problem but the parent should rele-
ase lock before calling wait otherwise child can not 
change the state and  signal.
• However releasing the lock before wait() brings     
back the earlier issue of sleeping forever if context 
switch happens just between lock release & wait()
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 10

## Page 11

Join Implementation: Correct one!
void thread_join() {
Mutex_lock(&m); // w
if (done == 0) // x
Cond_wait(&c, &m); // y
Mutex_unlock(&m); // z
}
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
• Therefore, the wait() operation on condition variable 
also takes the lock as another argument and it relea-
ses the lock before putting thread to sleep, so lock is 
available for child thread to signal. 
• when awoken, it reacquires the lock before returning
• Rule of thumb 2: Always do wait/signal with lock held
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 11

## Page 12

Definition and Routines
 Declare a condition variable with static initialization (dynamic possible).
 Operations:
pthread_cond_signal(pthread_cond_t *c);
 wakes a single waiting thread (if >= 1 thread is waiting)
 if there is no waiting thread, just return, doing nothing
pthread_cond_wait(pthread_cond_t *c, pthread_mutex_t *m)
 A single lock is associated with each CV. The wait() call takes a mutex lock 
as a parameter and assumes the lock is held when wait() is called
 puts caller to sleep + releases the lock (atomically)
 When the thread wakes up, it must re-acquire the lock before returning.
12
Pthread_cond_t c= PTHREAD_COND_INITIALIZER;
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 13

Parent waiting for Child: Use a condition variable
13
1 int done = 0;
2 pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
3 pthread_cond_t c = PTHREAD_COND_INITIALIZER;
4
5 void thr_exit() {
6 Pthread_mutex_lock(&m);
7 done = 1;
8 Pthread_cond_signal(&c);
9 Pthread_mutex_unlock(&m);
10 }
11
12 void *child(void *arg) {
13 printf("child\n");
14 thr_exit();
15 return NULL;
16 }
17
18 void thr_join() {
19 Pthread_mutex_lock(&m);
20 while (done == 0)
21 Pthread_cond_wait(&c, &m);
22 Pthread_mutex_unlock(&m);
23 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 14

Parent waiting for Child: Use a condition variable
14
(cont.)
25 int main(int argc, char *argv[]) {
26 printf("parent: begin\n");
27 pthread_t p;
28 Pthread_create(&p, NULL, child, NULL);
29 thr_join();
30 printf("parent: end\n");
31 return 0;
32 }
Q) How to wait for N Children?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 15

The Producer / Consumer (Bounded Buffer) Problem
 Producer
 Produce data items
 Wish to place data items in a buffer
 Consumer
 Grab data items out of the buffer consume them in some way
 Example: Multi-threaded web server
 Client (producer) thread puts HTTP requests in to a work queue
 Server (Consumer) threads take requests out of this queue for processing
 When you pipe the output of one program into another.
 Example: grep foo file.txt | wc –l
 The grep process is the producer and wc process is the consumer.
 Between them is an in-kernel bounded buffer
15Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 16

The Put and Get Routines (Version 1)
 General strategy is to make producers wait when buffers are full and 
make consumers wait when there is nothing to consume
 We will start with easy case:  1 producer thread, 1 consumer thread, 1 
shared buffer slot to fill/consume i.e Max = 1
16
1 int buffer;
2 int numfull = 0; // initially, empty
3
4 void do_fill(int value) {
5 assert(numfull == 0);
6 numfull = 1;
7 buffer = value;
8 }
9
10 int do_get() {
11 assert(numfull == 1);
12 numfull = 0;
13 return buffer;
14 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 17

Producer/Consumer Threads (version 1) 
 Producer puts an integer into the shared buffer loops number of times.
 Consumer gets the data out of that shared buffer.
 Try yourself writing the synchronized code…
17
1 void *producer(void *arg) {
2 int i;
3 int loops = (int) arg;
4 for (i = 0; i < loops; i++) {
5
6 
7 do_fill(i); //critical section
8
9 }
10 }
11 void *consumer(void *arg) {
12 int i;
13 while (1) {
14
15 
16 int tmp = do_get(); //critical section
17
18 printf("%d\n", tmp);
19 }
20 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 18

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNABLE] [RUNNING]
numfull=0
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 18

## Page 19

[RUNNABLE] [RUNNING]
numfull=0
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 19

## Page 20

[RUNNABLE] [RUNNING]
numfull=0
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 20

## Page 21

[RUNNABLE] [RUNNING]
numfull=0
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 21

## Page 22

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNABLE] [SLEEPING]
numfull=0
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 22

## Page 23

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNING] [SLEEPING]
numfull=0
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 23

## Page 24

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNING] [SLEEPING]
numfull=0
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 24

## Page 25

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNING] [SLEEPING]
numfull=0
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 25

## Page 26

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNING] [SLEEPING]
numfull=0
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 26

## Page 27

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNING] [SLEEPING]
numfull=1
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 27

## Page 28

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNING] [RUNNABLE]
numfull=1
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 28

## Page 29

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNING] [RUNNABLE]
numfull=1
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 29

## Page 30

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNING] [RUNNABLE]
numfull=1
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 30

## Page 31

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNING] [RUNNABLE]
numfull=1
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 31

## Page 32

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[RUNNING] [RUNNABLE]
numfull=1
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 32

## Page 33

void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
[SLEEPING] [RUNNABLE]
numfull=1
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 33

## Page 34

void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp); 
}
}
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
[SLEEPING] [RUNNING]
numfull=1
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 34

## Page 35

void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
[SLEEPING]
numfull=1
[RUNNING]
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 35

## Page 36

void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
[SLEEPING]
numfull=0
[RUNNING]
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 36

## Page 37

void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
[RUNNABLE]
numfull=0
[RUNNING]
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 37

## Page 38

void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
numfull=0
[RUNNING][RUNNABLE]
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 38

## Page 39

void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
numfull=0
[RUNNING][RUNNABLE]
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 39

## Page 40

void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);
if(numfull == max)
Cond_wait(&cond, &m);
do_fill(i);
Cond_signal(&cond);
Mutex_unlock(&m);
}
}
numfull=0
[RUNNING][RUNNABLE]
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m);
if(numfull == 0)
Cond_wait(&cond, &m);
int tmp = do_get();
Cond_signal(&cond);
Mutex_unlock(&m);
printf(“%d\n”, tmp);
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 40

