# Document: Chapter 30. Condition Variables (Pages 41 to 55)

## Page 41

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
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 41

## Page 42

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
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 42

## Page 43

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
numfull=0
[SLEEPING][RUNNABLE]
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 43

## Page 44

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
numfull=0
[SLEEPING][RUNNING]
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 44

## Page 45

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
numfull=0
[SLEEPING][RUNNING]
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
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 45

## Page 46

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
numfull=1
[SLEEPING][RUNNING]
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
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 46

## Page 47

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
numfull=1
[RUNNABLE][RUNNING]
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
With just a single producer and consumer the code works fine!
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 47

## Page 48

What about 2 consumers?
Can you find a problematic timeline with 2 consumers (still 1 producer)?
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m); //c1
if(numfull == 0) //c2
Cond_wait(&cond, &m); //c3
int tmp = do_get(); //c4
Cond_signal(&cond); //c5
Mutex_unlock(&m); //c6
printf(“%d\n”, tmp); //c7
}
}
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);//p1
if(numfull == max)//p2
Cond_wait(&cond, &m); //p3
do_fill(i); //p4
Cond_signal(&cond); //p5
Mutex_unlock(&m); //p6
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 48

## Page 49

Rule of Thumb 3
 Whenever a lock is acquired, recheck assumptions  
about state! i.e use While loops (not if) with CV’s.
 Possible for another thread to grab lock in between 
signal and wakeup from wait
 Sometimes you don’t need to recheck the condition 
but it is always safe to do so; 
 just do it and be happy!
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 49

## Page 50

The code still has a bug!
Can you find another problematic timeline with 2 consumers (still 1 producer)?
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m); //c1
while(numfull == 0) //c2
Cond_wait(&cond, &m); //c3
int tmp = do_get(); //c4
Cond_signal(&cond); //c5
Mutex_unlock(&m); //c6
printf(“%d\n”, tmp); //c7
}
}
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);//p1
while(numfull == max)//p2
Cond_wait(&cond, &m); //p3
do_fill(i); //p4
Cond_signal(&cond); //p5
Mutex_unlock(&m); //p6
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 50

## Page 51

How to wake the right thread?
 One solution: wake all the threads!
broadcast(cond_t *cv)
- wakes all waiting threads (if >= 1 thread is waiting)
- if there are no waiting thread, just return, doing nothing
 Any disadvantage? 
 Negative performance impact
 Should it be used for producer/consumer problem? 
 Not necessary
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 51

## Page 52

Producer/Consumer: Better solution – Use Two CVs
Is this correct?  Can you find a bad schedule?
Correct!
- no concurrent access to shared state
- every time lock is acquired, assumptions are reevaluated
- a consumer will get to run after every do_fill()
- a producer will get to run after every do_get()
void *consumer(void *arg) {
while(1) {
Mutex_lock(&m); //c1
while(numfull == 0) //c2
Cond_wait(&fill, &m); //c3
int tmp = do_get(); //c4
Cond_signal(&empty); //c5
Mutex_unlock(&m); //c6
printf(“%d\n”, tmp); //c7
}
}
void *producer(void *arg) {
for (int i=0; i<loops; i++) {
Mutex_lock(&m);//p1
while(numfull == max)//p2
Cond_wait(&empty, &m); //p3
do_fill(i); //p4
Cond_signal(&fill); //p5
Mutex_unlock(&m); //p6
}
}
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 52

## Page 53

Summary: rules of thumb for CVs
 Keep state in addition to CV’s
 Always do wait/signal with lock held
 Whenever thread wakes from waiting, recheck state
 Match signal with a corresponding wait call on a CV
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 53

## Page 54

Circular buffer with N elements
 Add more buffer slots → More concurrency and efficiency.
 enables multiple values to be produced or consumed.
 Reduce context switches.
54
1 int buffer[MAX];
2 int in = 0;
3 int out = 0;
4 int count = 0;
5
6 void do_fill(int value) {
7 buffer[in] = value;
8 in = (in + 1) % MAX;
9 count++;
10 }
12 int do_get() {
13 int tmp = buffer[out];
14 out = (out + 1) % MAX;
15 count--;
16 return tmp;
17 }
The do_fill( ) and do_get( ) Routines
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 55

The Final Producer/Consumer Solution (Cont.)
55
1 cond_t empty, fill;
2 mutex_t mutex;
4 void *producer(void *arg) {
5 int i;
6 for (i = 0; i < loops; i++) {
7 Pthread_mutex_lock(&mutex); // p1
8 while (count == MAX) // p2
9 Pthread_cond_wait(&empty, &mutex); // p3
10 do_fill(i); // p4
11 Pthread_cond_signal(&fill); // p5
12 Pthread_mutex_unlock(&mutex); // p6
13 }
14 }
16 void *consumer(void *arg) {
17 int i;
18 for (i = 0; i < loops; i++) {
19 Pthread_mutex_lock(&mutex); // c1
20 while (count == 0) // c2
21 Pthread_cond_wait(&fill, &mutex); // c3
22 int tmp = do_get(); // c4
23 Pthread_cond_signal(&empty); // c5
24 Pthread_mutex_unlock(&mutex); // c6
25 printf("%d\n", tmp);
26 }
27 }
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

