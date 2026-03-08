# Document: operating_systems_three_easy_pieces (Pages 361 to 400)

## Page 361

30
Condition Variables
Thus far we have developed the notion of a lock and seen how one can be
properly built with the right combination of hardware and OS support.
Unfortunately , locks are not the only primitives that are ne eded to build
concurrent programs.
In particular, there are many cases where a thread wishes to c heck
whether a condition is true before continuing its execution. For example,
a parent thread might wish to check whether a child thread hascompleted
before continuing (this is often called a join()); how should such a wait
be implemented? Let’s look at Figure 30.1.
1 void *child(void *arg) {
2 printf("child\n");
3 // XXX how to indicate we are done?
4 return NULL;
5 }
6
7 int main(int argc, char *argv[]) {
8 printf("parent: begin\n");
9 pthread_t c;
10 Pthread_create(&c, NULL, child, NULL); // create child
11 // XXX how to wait for child?
12 printf("parent: end\n");
13 return 0;
14 }
Figure 30.1: A Parent Waiting For Its Child
What we would like to see here is the following output:
parent: begin
child
parent: end
We could try using a shared variable, as you see in Figure
30.2. This
solution will generally work, but it is hugely inefﬁcient as the parent spins
and wastes CPU time. What we would like here instead is some wa y to
put the parent to sleep until the condition we are waiting for (e.g., the
child is done executing) comes true.
325

## Page 362

326 CONDITION VARIABLES
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
12 Pthread_create(&c, NULL, child, NULL); // create child
13 while (done == 0)
14 ; // spin
15 printf("parent: end\n");
16 return 0;
17 }
Figure 30.2: Parent Waiting For Child: Spin-based Approach
THE CRUX : H OW TO WAIT FOR A C ONDITION
In multi-threaded programs, it is often useful for a thread t o wait for
some condition to become true before proceeding. The simple approach,
of just spinning until the condition becomes true, is grossl y inefﬁcient
and wastes CPU cycles, and in some cases, can be incorrect. Th us, how
should a thread wait for a condition?
30.1 Deﬁnition and Routines
To wait for a condition to become true, a thread can make use of what
is known as a condition variable . A condition variable is an explicit
queue that threads can put themselves on when some state of ex ecution
(i.e., some condition) is not as desired (by waiting on the condition);
some other thread, when it changes said state, can then wake o ne (or
more) of those waiting threads and thus allow them to continu e (by sig-
naling on the condition). The idea goes back to Dijkstra’s use of “pr ivate
semaphores” [D68]; a similar idea was later named a “condition variable”
by Hoare in his work on monitors [H74].
To declare such a condition variable, one simply writes some thing
like this: pthread cond t c; , which declares c as a condition variable
(note: proper initialization is also required). A conditio n variable has two
operations associated with it: wait() and signal(). The wait() call
is executed when a thread wishes to put itself to sleep; the signal() call
is executed when a thread has changed something in the progra m and
thus wants to wake a sleeping thread waiting on this conditio n. Speciﬁ-
cally , the POSIX calls look like this:
pthread_cond_wait(pthread_cond_t *c, pthread_mutex_t *m);
pthread_cond_signal(pthread_cond_t *c);
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 363

CONDITION VARIABLES 327
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
24
25 int main(int argc, char *argv[]) {
26 printf("parent: begin\n");
27 pthread_t p;
28 Pthread_create(&p, NULL, child, NULL);
29 thr_join();
30 printf("parent: end\n");
31 return 0;
32 }
Figure 30.3: Parent Waiting For Child: Use A Condition V ariable
We will often refer to these as wait() and signal() for simplicity .
One thing you might notice about the wait() call is that it also takes a
mutex as a parameter; it assumes that this mutex is locked whe n wait()
is called. The responsibility of wait() is to release the lock and put the
calling thread to sleep (atomically); when the thread wakes up (after some
other thread has signaled it), it must re-acquire the lock be fore returning
to the caller. This complexity stems from the desire to preve nt certain
race conditions from occurring when a thread is trying to put itself to
sleep. Let’s take a look at the solution to the join problem (F igure
30.3) to
understand this better.
There are two cases to consider. In the ﬁrst, the parent creat es the child
thread but continues running itself (assume we have only a si ngle pro-
cessor) and thus immediately calls into thr join() to wait for the child
thread to complete. In this case, it will acquire the lock, ch eck if the child
is done (it is not), and put itself to sleep by calling wait() (hence releas-
ing the lock). The child will eventually run, print the messa ge “child”,
and call thr exit() to wake the parent thread; this code just grabs the
lock, sets the state variable done, and signals the parent thus waking it.
Finally , the parent will run (returning from wait() with the lock held),
unlock the lock, and print the ﬁnal message “parent: end”.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 364

328 CONDITION VARIABLES
In the second case, the child runs immediately upon creation , sets
done to 1, calls signal to wake a sleeping thread (but there is none , so
it just returns), and is done. The parent then runs, calls thr join(), sees
that done is 1, and thus does not wait and returns.
One last note: you might observe the parent uses a while loop instead
of just an if statement when deciding whether to wait on the condition.
While this does not seem strictly necessary per the logic of t he program,
it is always a good idea, as we will see below .
To make sure you understand the importance of each piece of th e
thr exit() and thr join() code, let’s try a few alternate implemen-
tations. First, you might be wondering if we need the state va riable done.
What if the code looked like the example below? Would this wor k?
1 void thr_exit() {
2 Pthread_mutex_lock(&m);
3 Pthread_cond_signal(&c);
4 Pthread_mutex_unlock(&m);
5 }
6
7 void thr_join() {
8 Pthread_mutex_lock(&m);
9 Pthread_cond_wait(&c, &m);
10 Pthread_mutex_unlock(&m);
11 }
Unfortunately this approach is broken. Imagine the case whe re the
child runs immediately and calls thr
exit() immediately; in this case,
the child will signal, but there is no thread asleep on the con dition. When
the parent runs, it will simply call wait and be stuck; no thre ad will ever
wake it. From this example, you should appreciate the import ance of
the state variable done; it records the value the threads are interested in
knowing. The sleeping, waking, and locking all are built aro und it.
Here is another poor implementation. In this example, we ima gine
that one does not need to hold a lock in order to signal and wait . What
problem could occur here? Think about it!
1 void thr_exit() {
2 done = 1;
3 Pthread_cond_signal(&c);
4 }
5
6 void thr_join() {
7 if (done == 0)
8 Pthread_cond_wait(&c);
9 }
The issue here is a subtle race condition. Speciﬁcally , if the parent calls
thr
join() and then checks the value of done, it will see that it is 0 and
thus try to go to sleep. But just before it calls wait to go to sleep, the parent
is interrupted, and the child runs. The child changes the sta te variable
done to 1 and signals, but no thread is waiting and thus no thread is
woken. When the parent runs again, it sleeps forever, which i s sad.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 365

CONDITION VARIABLES 329
TIP : A LWAYS HOLD THE LOCK WHILE SIGNALING
Although it is strictly not necessary in all cases, it is like ly simplest and
best to hold the lock while signaling when using condition va riables. The
example above shows a case where you must hold the lock for correct-
ness; however, there are some other cases where it is likely O K not to, but
probably is something you should avoid. Thus, for simplicit y ,hold the
lock when calling signal .
The converse of this tip, i.e., hold the lock when calling wai t, is not just
a tip, but rather mandated by the semantics of wait, because w ait always
(a) assumes the lock is held when you call it, (b) releases sai d lock when
putting the caller to sleep, and (c) re-acquires the lock jus t before return-
ing. Thus, the generalization of this tip is correct: hold the lock when
calling signal or wait , and you will always be in good shape.
Hopefully , from this simple join example, you can see some of the ba-
sic requirements of using condition variables properly . To make sure you
understand, we now go through a more complicated example: th e pro-
ducer/consumer or bounded-buffer problem.
30.2 The Producer/Consumer (Bound Buffer) Problem
The next synchronization problem we will confront in this ch apter is
known as the producer/consumer problem, or sometimes as the bounded
buffer problem, which was ﬁrst posed by Dijkstra [D72]. Indeed, it w as
this very producer/consumer problem that led Dijkstra and his co-workers
to invent the generalized semaphore (which can be used as eit her a lock
or a condition variable) [D01]; we will learn more about semaphores later.
Imagine one or more producer threads and one or more consumer
threads. Producers produce data items and wish to place them in a buffer;
consumers grab data items out of the buffer consume them in so me way .
This arrangement occurs in many real systems. For example, i n a
multi-threaded web server, a producer puts HTTP requests in to a work
queue (i.e., the bounded buffer); consumer threads take req uests out of
this queue and process them.
A bounded buffer is also used when you pipe the output of one pr o-
gram into another, e.g., grep foo file.txt | wc -l . This example
runs two processes concurrently; grep writes lines from file.txt with
the string foo in them to what it thinks is standard output; the U NIX
shell redirects the output to what is called a U NIX pipe (created by the
pipe system call). The other end of this pipe is connected to the st an-
dard input of the process wc, which simply counts the number of lines in
the input stream and prints out the result. Thus, the grep process is the
producer; the wc process is the consumer; between them is an in-kernel
bounded buffer; you, in this example, are just the happy user .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 366

330 CONDITION VARIABLES
1 int buffer;
2 int count = 0; // initially, empty
3
4 void put(int value) {
5 assert(count == 0);
6 count = 1;
7 buffer = value;
8 }
9
10 int get() {
11 assert(count == 1);
12 count = 0;
13 return buffer;
14 }
Figure 30.4: The Put and Get Routines (V ersion 1)
1 void *producer(void *arg) {
2 int i;
3 int loops = (int) arg;
4 for (i = 0; i < loops; i++) {
5 put(i);
6 }
7 }
8
9 void *consumer(void *arg) {
10 int i;
11 while (1) {
12 int tmp = get();
13 printf("%d\n", tmp);
14 }
15 }
Figure 30.5: Producer/Consumer Threads (V ersion 1)
Because the bounded buffer is a shared resource, we must of co urse
require synchronized access to it, lest 1 a race condition arise. To begin to
understand this problem better, let us examine some actual c ode.
The ﬁrst thing we need is a shared buffer, into which a produce r puts
data, and out of which a consumer takes data. Let’s just use a s ingle
integer for simplicity (you can certainly imagine placing a pointer to a
data structure into this slot instead), and the two inner rou tines to put
a value into the shared buffer, and to get a value out of the buf fer. See
Figure
30.4 for details.
Pretty simple, no? The put() routine assumes the buffer is empty
(and checks this with an assertion), and then simply puts a va lue into the
shared buffer and marks it full by setting count to 1. The get() routine
does the opposite, setting the buffer to empty (i.e., settin g count to 0)
and returning the value. Don’t worry that this shared buffer has just a
single entry; later, we’ll generalize it to a queue that can h old multiple
entries, which will be even more fun than it sounds.
Now we need to write some routines that know when it is OK to access
the buffer to either put data into it or get data out of it. The c onditions for
1This is where we drop some serious Old English on you, and the s ubjunctive form.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 367

CONDITION VARIABLES 331
1 cond_t cond;
2 mutex_t mutex;
3
4 void *producer(void *arg) {
5 int i;
6 for (i = 0; i < loops; i++) {
7 Pthread_mutex_lock(&mutex); // p1
8 if (count == 1) // p2
9 Pthread_cond_wait(&cond, &mutex); // p3
10 put(i); // p4
11 Pthread_cond_signal(&cond); // p5
12 Pthread_mutex_unlock(&mutex); // p6
13 }
14 }
15
16 void *consumer(void *arg) {
17 int i;
18 for (i = 0; i < loops; i++) {
19 Pthread_mutex_lock(&mutex); // c1
20 if (count == 0) // c2
21 Pthread_cond_wait(&cond, &mutex); // c3
22 int tmp = get(); // c4
23 Pthread_cond_signal(&cond); // c5
24 Pthread_mutex_unlock(&mutex); // c6
25 printf("%d\n", tmp);
26 }
27 }
Figure 30.6: Producer/Consumer: Single CV and If Statement
this should be obvious: only put data into the buffer when count is zero
(i.e., when the buffer is empty), and only get data from the bu ffer when
count is one (i.e., when the buffer is full). If we write the synchro nization
code such that a producer puts data into a full buffer, or a con sumer gets
data from an empty one, we have done something wrong (and in th is
code, an assertion will ﬁre).
This work is going to be done by two types of threads, one set of which
we’ll call the producer threads, and the other set which we’ll call con-
sumer threads. Figure
30.5 shows the code for a producer that puts an
integer into the shared buffer loops number of times, and a consumer
that gets the data out of that shared buffer (forever), each t ime printing
out the data item it pulled from the shared buffer.
A Broken Solution
Now imagine that we have just a single producer and a single co nsumer.
Obviously the put() and get() routines have critical sections within
them, as put() updates the buffer, and get() reads from it. However,
putting a lock around the code doesn’t work; we need somethin g more.
Not surprisingly , that something more is some condition variables. In this
(broken) ﬁrst try (Figure
30.6), we have a single condition variable cond
and associated lock mutex.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 368

332 CONDITION VARIABLES
Tc1 State T c2 State Tp State Count Comment
c1 Running Ready Ready 0
c2 Running Ready Ready 0
c3 Sleep Ready Ready 0 Nothing to get
Sleep Ready p1 Running 0
Sleep Ready p2 Running 0
Sleep Ready p4 Running 1 Buffer now full
Ready Ready p5 Running 1 T c1 awoken
Ready Ready p6 Running 1
Ready Ready p1 Running 1
Ready Ready p2 Running 1
Ready Ready p3 Sleep 1 Buffer full; sleep
Ready c1 Running Sleep 1 T c2 sneaks in ...
Ready c2 Running Sleep 1
Ready c4 Running Sleep 0 ... and grabs data
Ready c5 Running Ready 0 T p awoken
Ready c6 Running Ready 0
c4 Running Ready Ready 0 Oh oh! No data
Table 30.1: Thread T race: Broken Solution (V ersion 1)
Let’s examine the signaling logic between producers and con sumers.
When a producer wants to ﬁll the buffer, it waits for it to be em pty (p1–
p3). The consumer has the exact same logic, but waits for a dif ferent
condition: fullness (c1–c3).
With just a single producer and a single consumer, the code in Figure
30.6 works. However, if we have more than one of these threads (e.g .,
two consumers), the solution has two critical problems. Wha t are they?
... (pause here to think) ...
Let’s understand the ﬁrst problem, which has to do with the if state-
ment before the wait. Assume there are two consumers ( Tc1 and Tc2) and
one producer ( Tp). First, a consumer ( Tc1) runs; it acquires the lock (c1),
checks if any buffers are ready for consumption (c2), and ﬁnd ing that
none are, waits (c3) (which releases the lock).
Then the producer ( Tp) runs. It acquires the lock (p1), checks if all
buffers are full (p2), and ﬁnding that not to be the case, goes ahead and
ﬁlls the buffer (p4). The producer then signals that a buffer has been
ﬁlled (p5). Critically , this moves the ﬁrst consumer ( Tc1) from sleeping
on a condition variable to the ready queue; Tc1 is now able to run (but
not yet running). The producer then continues until realizi ng the buffer
is full, at which point it sleeps (p6, p1–p3).
Here is where the problem occurs: another consumer ( Tc2) sneaks in
and consumes the one existing value in the buffer (c1, c2, c4, c5, c6, skip-
ping the wait at c3 because the buffer is full). Now assume Tc1 runs; just
before returning from the wait, it re-acquires the lock and t hen returns. It
then calls get() (c4), but there are no buffers to consume! An assertion
triggers, and the code has not functioned as desired. Clearl y , we should
have somehow prevented Tc1 from trying to consume because Tc2 snuck
in and consumed the one value in the buffer that had been produ ced. Ta-
ble
30.1 shows the action each thread takes, as well as its scheduler s tate
(Ready , Running, or Sleeping) over time.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 369

CONDITION VARIABLES 333
1 cond_t cond;
2 mutex_t mutex;
3
4 void *producer(void *arg) {
5 int i;
6 for (i = 0; i < loops; i++) {
7 Pthread_mutex_lock(&mutex); // p1
8 while (count == 1) // p2
9 Pthread_cond_wait(&cond, &mutex); // p3
10 put(i); // p4
11 Pthread_cond_signal(&cond); // p5
12 Pthread_mutex_unlock(&mutex); // p6
13 }
14 }
15
16 void *consumer(void *arg) {
17 int i;
18 for (i = 0; i < loops; i++) {
19 Pthread_mutex_lock(&mutex); // c1
20 while (count == 0) // c2
21 Pthread_cond_wait(&cond, &mutex); // c3
22 int tmp = get(); // c4
23 Pthread_cond_signal(&cond); // c5
24 Pthread_mutex_unlock(&mutex); // c6
25 printf("%d\n", tmp);
26 }
27 }
Figure 30.7: Producer/Consumer: Single CV and While
The problem arises for a simple reason: after the producer wo ke Tc1,
but before Tc1 ever ran, the state of the bounded buffer changed (thanks to
Tc2). Signaling a thread only wakes them up; it is thus a hint that the state
of the world has changed (in this case, that a value has been pl aced in the
buffer), but there is no guarantee that when the woken thread runs, the
state will still be as desired. This interpretation of what a signal means
is often referred to as Mesa semantics , after the ﬁrst research that built
a condition variable in such a manner [LR80]; the contrast, r eferred to as
Hoare semantics , is harder to build but provides a stronger guarantee
that the woken thread will run immediately upon being woken [ H74].
Virtually every system ever built employs Mesa semantics.
Better, But Still Broken: While, Not If
Fortunately , this ﬁx is easy (Figure
30.7): change the if to a while. Think
about why this works; now consumer Tc1 wakes up and (with the lock
held) immediately re-checks the state of the shared variabl e (c2). If the
buffer is empty at that point, the consumer simply goes back t o sleep
(c3). The corollary if is also changed to a while in the producer (p2).
Thanks to Mesa semantics, a simple rule to remember with cond ition
variables is to always use while loops . Sometimes you don’t have to re-
check the condition, but it is always safe to do so; just do it a nd be happy .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 370

334 CONDITION VARIABLES
Tc1 State T c2 State Tp State Count Comment
c1 Running Ready Ready 0
c2 Running Ready Ready 0
c3 Sleep Ready Ready 0 Nothing to get
Sleep c1 Running Ready 0
Sleep c2 Running Ready 0
Sleep c3 Sleep Ready 0 Nothing to get
Sleep Sleep p1 Running 0
Sleep Sleep p2 Running 0
Sleep Sleep p4 Running 1 Buffer now full
Ready Sleep p5 Running 1 T c1 awoken
Ready Sleep p6 Running 1
Ready Sleep p1 Running 1
Ready Sleep p2 Running 1
Ready Sleep p3 Sleep 1 Must sleep (full)
c2 Running Sleep Sleep 1 Recheck condition
c4 Running Sleep Sleep 0 T c1 grabs data
c5 Running Ready Sleep 0 Oops! Woke T c2
c6 Running Ready Sleep 0
c1 Running Ready Sleep 0
c2 Running Ready Sleep 0
c3 Sleep Ready Sleep 0 Nothing to get
Sleep c2 Running Sleep 0
Sleep c3 Sleep Sleep 0 Everyone asleep...
Table 30.2: Thread T race: Broken Solution (V ersion 2)
However, this code still has a bug, the second of two problems men-
tioned above. Can you see it? It has something to do with the fa ct that
there is only one condition variable. Try to ﬁgure out what th e problem
is, before reading ahead. DO IT!
... (another pause for you to think, or close your eyes for a bi t) ...
Let’s conﬁrm you ﬁgured it out correctly , or perhaps let’s co nﬁrm that
you are now awake and reading this part of the book. The proble m oc-
curs when two consumers run ﬁrst ( Tc1 and Tc2), and both go to sleep
(c3). Then, a producer runs, put a value in the buffer, wakes o ne of the
consumers (say Tc1), and goes back to sleep. Now we have one consumer
ready to run ( Tc1), and two threads sleeping on a condition ( Tc2 and Tp).
And we are about to cause a problem to occur: things are gettin g exciting!
The consumer Tc1 then wakes by returning from wait() (c3), re-checks
the condition (c2), and ﬁnding the buffer full, consumes the value (c4).
This consumer then, critically , signals on the condition (c 5), waking one
thread that is sleeping. However, which thread should it wak e?
Because the consumer has emptied the buffer, it clearly shou ld wake
the producer. However, if it wakes the consumer Tc2 (which is deﬁnitely
possible, depending on how the wait queue is managed), we hav e a prob-
lem. Speciﬁcally , the consumer Tc2 will wake up and ﬁnd the buffer
empty (c2), and go back to sleep (c3). The producer Tp, which has a value
to put into the buffer, is left sleeping. The other consumer t hread, Tc1,
also goes back to sleep. All three threads are left sleeping, a clear bug; see
Table 30.2 for the brutal step-by-step of this terrible calamity .
Signaling is clearly needed, but must be more directed. A con sumer
should not wake other consumers, only producers, and vice-v ersa.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 371

CONDITION VARIABLES 335
1 cond_t empty, fill;
2 mutex_t mutex;
3
4 void *producer(void *arg) {
5 int i;
6 for (i = 0; i < loops; i++) {
7 Pthread_mutex_lock(&mutex);
8 while (count == 1)
9 Pthread_cond_wait(&empty, &mutex);
10 put(i);
11 Pthread_cond_signal(&fill);
12 Pthread_mutex_unlock(&mutex);
13 }
14 }
15
16 void *consumer(void *arg) {
17 int i;
18 for (i = 0; i < loops; i++) {
19 Pthread_mutex_lock(&mutex);
20 while (count == 0)
21 Pthread_cond_wait(&fill, &mutex);
22 int tmp = get();
23 Pthread_cond_signal(&empty);
24 Pthread_mutex_unlock(&mutex);
25 printf("%d\n", tmp);
26 }
27 }
Figure 30.8: Producer/Consumer: Two CVs and While
The Single Buffer Producer/Consumer Solution
The solution here is once again a small one: use two condition variables,
instead of one, in order to properly signal which type of thre ad should
wake up when the state of the system changes. Figure
30.8 shows the
resulting code.
In the code above, producer threads wait on the condition empty, and
signals ﬁll. Conversely , consumer threads wait on ﬁll and signal empty.
By doing so, the second problem above is avoided by design: a c onsumer
can never accidentally wake a consumer, and a producer can ne ver acci-
dentally wake a producer.
The Final Producer/Consumer Solution
We now have a working producer/consumer solution, albeit no t a fully
general one. The last change we make is to enable more concurr ency and
efﬁciency; speciﬁcally , we add more buffer slots, so that mu ltiple values
can be produced before sleeping, and similarly multiple val ues can be
consumed before sleeping. With just a single producer and consumer, this
approach is more efﬁcient as it reduces context switches; wi th multiple
producers or consumers (or both), it even allows concurrent producing
or consuming to take place, thus increasing concurrency . Fo rtunately , it
is a small change from our current solution.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 372

336 CONDITION VARIABLES
1 int buffer[MAX];
2 int fill = 0;
3 int use = 0;
4 int count = 0;
5
6 void put(int value) {
7 buffer[fill] = value;
8 fill = (fill + 1) % MAX;
9 count++;
10 }
11
12 int get() {
13 int tmp = buffer[use];
14 use = (use + 1) % MAX;
15 count--;
16 return tmp;
17 }
Figure 30.9: The Final Put and Get Routines
1 cond_t empty, fill;
2 mutex_t mutex;
3
4 void *producer(void *arg) {
5 int i;
6 for (i = 0; i < loops; i++) {
7 Pthread_mutex_lock(&mutex); // p1
8 while (count == MAX) // p2
9 Pthread_cond_wait(&empty, &mutex); // p3
10 put(i); // p4
11 Pthread_cond_signal(&fill); // p5
12 Pthread_mutex_unlock(&mutex); // p6
13 }
14 }
15
16 void *consumer(void *arg) {
17 int i;
18 for (i = 0; i < loops; i++) {
19 Pthread_mutex_lock(&mutex); // c1
20 while (count == 0) // c2
21 Pthread_cond_wait(&fill, &mutex); // c3
22 int tmp = get(); // c4
23 Pthread_cond_signal(&empty); // c5
24 Pthread_mutex_unlock(&mutex); // c6
25 printf("%d\n", tmp);
26 }
27 }
Figure 30.10: The Final Working Solution
The ﬁrst change for this ﬁnal solution is within the buffer st ructure
itself and the corresponding put() and get() (Figure
30.9). We also
slightly change the conditions that producers and consumer s check in or-
der to determine whether to sleep or not. Figure 30.10 shows the ﬁnal
waiting and signaling logic. A producer only sleeps if all bu ffers are cur-
rently ﬁlled (p2); similarly , a consumer only sleeps if all b uffers are cur-
rently empty (c2). And thus we solve the producer/consumer p roblem.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 373

CONDITION VARIABLES 337
TIP : U SE WHILE (N OT IF) F OR CONDITIONS
When checking for a condition in a multi-threaded program, u sing
a while loop is always correct; using an if statement only might be,
depending on the semantics of signaling. Thus, always use while and
your code will behave as expected.
Using while loops around conditional checks also handles th e case
where spurious wakeups occur. In some thread packages, due to de-
tails of the implementation, it is possible that two threads get woken up
though just a single signal has taken place [L11]. Spurious w akeups are
further reason to re-check the condition a thread is waiting on.
30.3 Covering Conditions
We’ll now look at one more example of how condition variables can
be used. This code study is drawn from Lampson and Redell’s pa per on
Pilot [LR80], the same group who ﬁrst implemented the Mesa semantics
described above (the language they used was Mesa, hence the n ame).
The problem they ran into is best shown via simple example, in this
case in a simple multi-threaded memory allocation library . Figure 30.11
shows a code snippet which demonstrates the issue.
As you might see in the code, when a thread calls into the memor y
allocation code, it might have to wait in order for more memor y to be-
come free. Conversely , when a thread frees memory , it signal s that more
memory is free. However, our code above has a problem: which w aiting
thread (there can be more than one) should be woken up?
Consider the following scenario. Assume there are zero byte s free;
thread Ta calls allocate(100), followed by thread Tb which asks for
less memory by calling allocate(10). Both Ta and Tb thus wait on the
condition and go to sleep; there aren’t enough free bytes to s atisfy either
of these requests.
At that point, assume a third thread, Tc, calls free(50). Unfortu-
nately , when it calls signal to wake a waiting thread, it migh t not wake
the correct waiting thread, Tb, which is waiting for only 10 bytes to be
freed; Ta should remain waiting, as not enough memory is yet free. Thus ,
the code in the ﬁgure does not work, as the thread waking other threads
does not know which thread (or threads) to wake up.
The solution suggested by Lampson and Redell is straightfor ward: re-
place the pthread cond signal() call in the code above with a call to
pthread cond broadcast(), which wakes up all waiting threads. By
doing so, we guarantee that any threads that should be woken a re. The
downside, of course, can be a negative performance impact, a s we might
needlessly wake up many other waiting threads that shouldn’ t (yet) be
awake. Those threads will simply wake up, re-check the condi tion, and
then go immediately back to sleep.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 374

338 CONDITION VARIABLES
1 // how many bytes of the heap are free?
2 int bytesLeft = MAX_HEAP_SIZE;
3
4 // need lock and condition too
5 cond_t c;
6 mutex_t m;
7
8 void *
9 allocate(int size) {
10 Pthread_mutex_lock(&m);
11 while (bytesLeft < size)
12 Pthread_cond_wait(&c, &m);
13 void *ptr = ...; // get mem from heap
14 bytesLeft -= size;
15 Pthread_mutex_unlock(&m);
16 return ptr;
17 }
18
19 void free(void *ptr, int size) {
20 Pthread_mutex_lock(&m);
21 bytesLeft += size;
22 Pthread_cond_signal(&c); // whom to signal??
23 Pthread_mutex_unlock(&m);
24 }
Figure 30.11: Covering Conditions: An Example
Lampson and Redell call such a condition a covering condition , as it
covers all the cases where a thread needs to wake up (conserva tively);
the cost, as we’ve discussed, is that too many threads might b e woken.
The astute reader might also have noticed we could have used t his ap-
proach earlier (see the producer/consumer problem with onl y a single
condition variable). However, in that case, a better soluti on was avail-
able to us, and thus we used it. In general, if you ﬁnd that your program
only works when you change your signals to broadcasts (but yo u don’t
think it should need to), you probably have a bug; ﬁx it! But in cases like
the memory allocator above, broadcast may be the most straig htforward
solution available.
30.4 Summary
We have seen the introduction of another important synchron ization
primitive beyond locks: condition variables. By allowing t hreads to sleep
when some program state is not as desired, CVs enable us to nea tly solve
a number of important synchronization problems, including the famous
(and still important) producer/consumer problem, as well a s covering
conditions. A more dramatic concluding sentence would go he re, such as
“He loved Big Brother” [O49].
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 375

CONDITION VARIABLES 339
References
[D72] “Information Streams Sharing a Finite Buffer”
E.W. Dijkstra
Information Processing Letters 1: 179180, 1972
Available: http://www.cs.utexas.edu/users/EWD/ewd03xx/EWD329.PDF
The famous paper that introduced the producer/consumer pro blem.
[D01] “My recollections of operating system design”
E.W. Dijkstra
April, 2001
Available: http://www.cs.utexas.edu/users/EWD/ewd13xx/EWD1303.PDF
A fascinating read for those of you interested in how the pion eers of our ﬁeld came up with some very
basic and fundamental concepts, including ideas like “inte rrupts” and even “a stack”!
[H74] “Monitors: An Operating System Structuring Concept”
C.A.R. Hoare
Communications of the ACM, 17:10, pages 549–557, October 19 74
Hoare did a fair amount of theoretical work in concurrency. H owever, he is still probably most known
for his work on Quicksort, the coolest sorting algorithm in t he world, at least according to these authors.
[L11] “Pthread
cond signal Man Page”
Available: http://linux.die.net/man/3/pthread cond signal
March, 2011
The Linux man page shows a nice simple example of why a thread m ight get a spurious wakeup, due to
race conditions within the signal/wakeup code.
[LR80] “Experience with Processes and Monitors in Mesa”
B.W. Lampson, D.R. Redell
Communications of the ACM. 23:2, pages 105-117, February 19 80
A terriﬁc paper about how to actually implement signaling an d condition variables in a real system,
leading to the term “Mesa” semantics for what it means to be wo ken up; the older semantics, developed
by Tony Hoare [H74], then became known as “Hoare” semantics, which is hard to say out loud in class
with a straight face.
[O49] “1984”
George Orwell, 1949, Secker and Warburg
A little heavy-handed, but of course a must read. That said, w e kind of gave away the ending by quoting
the last sentence. Sorry! And if the government is reading th is, let us just say that we think that the
government is “double plus good”. Hear that, our pals at the N SA?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 377

31
Semaphores
As we know now , one needs both locks and condition variables t o solve
a broad range of relevant and interesting concurrency probl ems. One of
the ﬁrst people to realize this years ago was Edsger Dijkstra (though it
is hard to know the exact history [GR92]), known among other t hings for
his famous “shortest paths” algorithm in graph theory [D59] , an early
polemic on structured programming entitled “Goto Statemen ts Consid-
ered Harmful” [D68a] (what a great title!), and, in the case w e will study
here, the introduction of a synchronization primitive called the semaphore
[D68b,D72]. Indeed, Dijkstra and colleagues invented the s emaphore as a
single primitive for all things related to synchronization ; as you will see,
one can use semaphores as both locks and condition variables .
THE CRUX : H OW TO USE SEMAPHORES
How can we use semaphores instead of locks and condition vari ables?
What is the deﬁnition of a semaphore? What is a binary semapho re?
Is it straightforward to build a semaphore out of locks and co ndition
variables? What about building locks and condition variabl es out of
semaphores?
31.1 Semaphores: A Deﬁnition
A semaphore is as an object with an integer value that we can ma -
nipulate with two routines; in the POSIX standard, these rou tines are
sem wait() and sem post()1. Because the initial value of the semaphore
determines its behavior, before calling any other routine t o interact with
the semaphore, we must ﬁrst initialize it to some value, as th e code in
Figure 31.1 does.
1Historically ,sem wait() was ﬁrst called P() by Dijkstra (for the Dutch word “to probe” )
and sem post() was called V() (for the Dutch word “to test”). Sometimes, peo ple call them
down and up, too. Use the Dutch versions to impress your frien ds.
341

## Page 378

342 SEMAPHORES
1 #include <semaphore.h>
2 sem_t s;
3 sem_init(&s, 0, 1);
Figure 31.1: Initializing A Semaphore
In the ﬁgure, we declare a semaphore s and initialize it to the value 1
by passing 1 in as the third argument. The second argument to sem init()
will be set to 0 in all of the examples we’ll see; this indicate s that the
semaphore is shared between threads in the same process. See the man
page for details on other usages of semaphores (namely , how t hey can
be used to synchronize access across different processes), which require a
different value for that second argument.
After a semaphore is initialized, we can call one of two funct ions to
interact with it, sem wait() or sem post(). The behavior of these two
functions is seen in Figure 31.2.
For now , we are not concerned with the implementation of thes e rou-
tines, which clearly requires some care; with multiple thre ads calling into
sem wait() and sem post(), there is the obvious need for managing
these critical sections. We will now focus on how to use these primitives;
later we may discuss how they are built.
We should discuss a few salient aspects of the interfaces here. First, we
can see that sem wait() will either return right away (because the value
of the semaphore was one or higher when we called sem wait()), or it
will cause the caller to suspend execution waiting for a subs equent post.
Of course, multiple calling threads may call into sem wait(), and thus
all be queued waiting to be woken.
Second, we can see that sem post() does not wait for some particular
condition to hold like sem wait() does. Rather, it simply increments the
value of the semaphore and then, if there is a thread waiting t o be woken,
wakes one of them up.
Third, the value of the semaphore, when negative, is equal to the num-
ber of waiting threads [D68b]. Though the value generally is n’t seen by
users of the semaphores, this invariant is worth knowing and perhaps
can help you remember how a semaphore functions.
Don’t worry (yet) about the seeming race conditions possibl e within
the semaphore; assume that the actions they make are perform ed atomi-
cally . We will soon use locks and condition variables to do ju st this.
1 int sem_wait(sem_t *s) {
2 decrement the value of semaphore s by one
3 wait if value of semaphore s is negative
4 }
5
6 int sem_post(sem_t *s) {
7 increment the value of semaphore s by one
8 if there are one or more threads waiting, wake one
9 }
Figure 31.2: Semaphore: Deﬁnitions of Wait and Post
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 379

SEMAPHORES 343
1 sem_t m;
2 sem_init(&m, 0, X); // initialize semaphore to X; what shoul d X be?
3
4 sem_wait(&m);
5 // critical section here
6 sem_post(&m);
Figure 31.3: A Binary Semaphore, a.k.a. a Lock
31.2 Binary Semaphores (Locks)
We are now ready to use a semaphore. Our ﬁrst use will be one wit h
which we are already familiar: using a semaphore as a lock. Se e Figure
31.3 for a code snippet; therein, you’ll see that we simply surrou nd the
critical section of interest with a sem wait()/sem post() pair. Criti-
cal to making this work, though, is the initial value of the se maphore m
(initialized to X in the ﬁgure). What should X be?
... (T ry thinking about it before going on) ...
Looking back at deﬁnition of the sem
wait() and sem post() rou-
tines above, we can see that the initial value should be 1.
To make this clear, let’s imagine a scenario with two threads . The ﬁrst
thread (Thread 0) calls sem wait(); it will ﬁrst decrement the value of
the semaphore, changing it to 0. Then, it will wait only if the value is
not greater than or equal to 0; because the value is 0, the calling thread
will simply return and continue; Thread 0 is now free to enter the critical
section. If no other thread tries to acquire the lock while Th read 0 is inside
the critical section, when it calls sem post(), it will simply restore the
value of the semaphore to 1 (and not wake any waiting thread, b ecause
there are none). Table 31.1 shows a trace of this scenario.
A more interesting case arises when Thread 0 “holds the lock” (i.e.,
it has called sem wait() but not yet called sem post()), and another
thread (Thread 1) tries to enter the critical section by calling sem wait().
In this case, Thread 1 will decrement the value of the semaphore to -1, and
thus wait (putting itself to sleep and relinquishing the pro cessor). When
Thread 0 runs again, it will eventually call sem post(), incrementing the
value of the semaphore back to zero, and then wake the waiting thread
(Thread 1), which will then be able to acquire the lock for its elf. When
Thread 1 ﬁnishes, it will again increment the value of the sem aphore,
restoring it to 1 again.
V alue of Semaphore Thread 0 Thread 1
1
1 call sem
wait()
0 sem wait() returns
0 (crit sect)
0 call sem post()
1 sem post() returns
Table 31.1: Thread T race: Single Thread Using A Semaphore
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 380

344 SEMAPHORES
V alue Thread 0 State Thread 1 State
1 Running Ready
1 call sem
wait() Running Ready
0 sem wait() returns Running Ready
0 (crit sect: begin) Running Ready
0 Interrupt; Switch→T1 Ready Running
0 Ready call sem wait() Running
-1 Ready decrement sem Running
-1 Ready (sem<0)→sleep Sleeping
-1 Running Switch→T0 Sleeping
-1 (crit sect: end) Running Sleeping
-1 call sem post() Running Sleeping
0 increment sem Running Sleeping
0 wake(T1) Running Ready
0 sem post() returns Running Ready
0 Interrupt; Switch→T1 Ready Running
0 Ready sem wait() returns Running
0 Ready (crit sect) Running
0 Ready call sem post() Running
1 Ready sem post() returns Running
Table 31.2: Thread T race: Two Threads Using A Semaphore
Table 31.2 shows a trace of this example. In addition to thread actions,
the table shows the scheduler state of each thread: Running, Ready (i.e.,
runnable but not running), and Sleeping. Note in particular that Thread 1
goes into the sleeping state when it tries to acquire the alre ady-held lock;
only when Thread 0 runs again can Thread 1 be awoken and potent ially
run again.
If you want to work through your own example, try a scenario wh ere
multiple threads queue up waiting for a lock. What would the v alue of
the semaphore be during such a trace?
Thus we are able to use semaphores as locks. Because locks onl y have
two states (held and not held), this usage is sometimes known as a binary
semaphore and in fact can be implemented in a more simpliﬁed manner
than discussed here; we instead use the generalized semapho re as a lock.
31.3 Semaphores As Condition Variables
Semaphores are also useful when a thread wants to halt its pro gress
waiting for a condition to become true. For example, a thread may wish
to wait for a list to become non-empty , so it can delete an elem ent from it.
In this pattern of usage, we often ﬁnd a thread waiting for something to
happen, and a different thread making that something happen and then
signaling that it has happened, thus waking the waiting thread. Becaus e
the waiting thread (or threads) is waiting for some condition in the pro-
gram to change, we are using the semaphore as a condition variable.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 381

SEMAPHORES 345
1 sem_t s;
2
3 void *
4 child(void *arg) {
5 printf("child\n");
6 sem_post(&s); // signal here: child is done
7 return NULL;
8 }
9
10 int
11 main(int argc, char *argv[]) {
12 sem_init(&s, 0, X); // what should X be?
13 printf("parent: begin\n");
14 pthread_t c;
15 Pthread_create(c, NULL, child, NULL);
16 sem_wait(&s); // wait here for child
17 printf("parent: end\n");
18 return 0;
19 }
Figure 31.4: A Parent Waiting For Its Child
A simple example is as follows. Imagine a thread creates anot her
thread and then wants to wait for it to complete its execution (Figure
31.4). When this program runs, we would like to see the following:
parent: begin
child
parent: end
The question, then, is how to use a semaphore to achieve this e ffect,
and is it turns out, it is relatively easy to understand. As yo u can see in
the code, the parent simply calls sem
wait() and the child sem post()
to wait for the condition of the child ﬁnishing its execution to become
true. However, this raises the question: what should the ini tial value of
this semaphore be?
(Again, think about it here, instead of reading ahead)
The answer, of course, is that the value of the semaphore shou ld be
set to is 0. There are two cases to consider. First, let us assu me that the
parent creates the child but the child has not run yet (i.e., i t is sitting in
a ready queue but not running). In this case (Table
31.3), the parent will
call sem wait() before the child has called sem post(); we’d like the
parent to wait for the child to run. The only way this will happ en is if the
value of the semaphore is not greater than 0; hence, 0 is the in itial value.
The parent runs, decrements the semaphore (to -1), then wait s (sleeping).
When the child ﬁnally runs, it will call sem post(), increment the value
of the semaphore to 0, and wake the parent, which will then ret urn from
sem wait() and ﬁnish the program.
The second case (Table 31.4) occurs when the child runs to comple-
tion before the parent gets a chance to call sem wait(). In this case,
the child will ﬁrst call sem post(), thus incrementing the value of the
semaphore from 0 to 1. When the parent then gets a chance to run , it
will call sem wait() and ﬁnd the value of the semaphore to be 1; the
parent will thus decrement the value (to 0) and return from sem wait()
without waiting, also achieving the desired effect.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 382

346 SEMAPHORES
V alue Parent State Child State
0 create(Child) Running (Child exists; is runnable) Ready
0 call sem wait() Running Ready
-1 decrement sem Running Ready
-1 (sem<0)→sleep Sleeping Ready
-1 Switch→Child Sleeping child runs Running
-1 Sleeping call sem post() Running
0 Sleeping increment sem Running
0 Ready wake(Parent) Running
0 Ready sem post() returns Running
0 Ready Interrupt; Switch→Parent Ready
0 sem wait() returns Ready Ready
Table 31.3: Thread T race: Parent Waiting For Child (Case 1)
V alue Parent State Child State
0 create(Child) Running (Child exists; is runnable) Ready
0 Interrupt; Switch→Child Ready child runs Running
0 Ready call sem post() Running
1 Ready increment sem Running
1 Ready wake(nobody) Running
1 Ready sem post() returns Running
1 parent runs Running Interrupt; Switch→Parent Ready
1 call sem wait() Running Ready
0 decrement sem Running Ready
0 (sem≥0)→awake Running Ready
0 sem wait() returns Running Ready
Table 31.4: Thread T race: Parent Waiting For Child (Case 2)
31.4 The Producer/Consumer (Bounded-Buffer) Problem
The next problem we will confront in this chapter is known as t he pro-
ducer/consumer problem, or sometimes as the bounded buffer problem
[D72]. This problem is described in detail in the previous ch apter on con-
dition variables; see there for details.
First Attempt
Our ﬁrst attempt at solving the problem introduces two semaphores, empty
and full, which the threads will use to indicate when a buffer entry ha s
been emptied or ﬁlled, respectively . The code for the put and get routines
is in Figure
31.5, and our attempt at solving the producer and consumer
problem is in Figure 31.6.
In this example, the producer ﬁrst waits for a buffer to becom e empty
in order to put data into it, and the consumer similarly waits for a buffer
to become ﬁlled before using it. Let us ﬁrst imagine that MAX=1 (there is
only one buffer in the array), and see if this works.
Imagine again there are two threads, a producer and a consume r. Let
us examine a speciﬁc scenario on a single CPU. Assume the cons umer
gets to run ﬁrst. Thus, the consumer will hit line c1 in the ﬁgu re above,
calling sem wait(&full). Because full was initialized to the value 0,
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 383

SEMAPHORES 347
1 int buffer[MAX];
2 int fill = 0;
3 int use = 0;
4
5 void put(int value) {
6 buffer[fill] = value; // line f1
7 fill = (fill + 1) % MAX; // line f2
8 }
9
10 int get() {
11 int tmp = buffer[use]; // line g1
12 use = (use + 1) % MAX; // line g2
13 return tmp;
14 }
Figure 31.5: The Put and Get Routines
1 sem_t empty;
2 sem_t full;
3
4 void *producer(void *arg) {
5 int i;
6 for (i = 0; i < loops; i++) {
7 sem_wait(&empty); // line P1
8 put(i); // line P2
9 sem_post(&full); // line P3
10 }
11 }
12
13 void *consumer(void *arg) {
14 int i, tmp = 0;
15 while (tmp != -1) {
16 sem_wait(&full); // line C1
17 tmp = get(); // line C2
18 sem_post(&empty); // line C3
19 printf("%d\n", tmp);
20 }
21 }
22
23 int main(int argc, char *argv[]) {
24 // ...
25 sem_init(&empty, 0, MAX); // MAX buffers are empty to begin w ith...
26 sem_init(&full, 0, 0); // ... and 0 are full
27 // ...
28 }
Figure 31.6: Adding the Full and Empty Conditions
the call will decrement full (to -1), block the consumer, and wait for
another thread to call sem
post() on full, as desired.
Assume the producer then runs. It will hit line P1, thus calli ng the
sem wait(&empty) routine. Unlike the consumer, the producer will
continue through this line, because empty was initialized t o the value
MAX (in this case, 1). Thus, empty will be decremented to 0 and the
producer will put a data value into the ﬁrst entry of buffer (l ine P2). The
producer will then continue on to P3 and call sem post(&full), chang-
ing the value of the full semaphore from -1 to 0 and waking the c onsumer
(e.g., move it from blocked to ready).
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 384

348 SEMAPHORES
In this case, one of two things could happen. If the producer c ontin-
ues to run, it will loop around and hit line P1 again. This time , how-
ever, it would block, as the empty semaphore’s value is 0. If t he producer
instead was interrupted and the consumer began to run, it wou ld call
sem wait(&full) (line c1) and ﬁnd that the buffer was indeed full and
thus consume it. In either case, we achieve the desired behav ior.
You can try this same example with more threads (e.g., multip le pro-
ducers, and multiple consumers). It should still work.
Let us now imagine that MAX is greater than 1 (say MAX = 10). For this
example, let us assume that there are multiple producers and multiple
consumers. We now have a problem: a race condition. Do you see where
it occurs? (take some time and look for it) If you can’t see it, here’s a hint:
look more closely at the put() and get() code.
OK, let’s understand the issue. Imagine two producers (Pa an d Pb)
both calling into put() at roughly the same time. Assume producer Pa gets
to run ﬁrst, and just starts to ﬁll the ﬁrst buffer entry (ﬁll = 0 at line f1).
Before Pa gets a chance to increment the ﬁll counter to 1, it is interrupted.
Producer Pb starts to run, and at line f1 it also puts its data i nto the 0th
element of buffer, which means that the old data there is over written!
This is a no-no; we don’t want any data from the producer to be l ost.
A Solution: Adding Mutual Exclusion
As you can see, what we’ve forgotten here is mutual exclusion . The
ﬁlling of a buffer and incrementing of the index into the buff er is a critical
section, and thus must be guarded carefully . So let’s use our friend the
binary semaphore and add some locks. Figure 31.7 shows our attempt.
Now we’ve added some locks around the entire put()/get() par ts of
the code, as indicated by the NEW LINE comments. That seems like the
right idea, but it also doesn’t work. Why? Deadlock. Why does deadlock
occur? Take a moment to consider it; try to ﬁnd a case where dea dlock
arises. What sequence of steps must happen for the program to deadlock?
Avoiding Deadlock
OK, now that you ﬁgured it out, here is the answer. Imagine two threads,
one producer and one consumer. The consumer gets to run ﬁrst. It ac-
quires the mutex (line c0), and then calls sem
wait() on the full semaphore
(line c1); because there is no data yet, this call causes the c onsumer to
block and thus yield the CPU; importantly , though, the consu mer still
holds the lock.
A producer then runs. It has data to produce and if it were able to run,
it would be able to wake the consumer thread and all would be go od.
Unfortunately , the ﬁrst thing it does is call sem wait() on the binary
mutex semaphore (line p0). The lock is already held. Hence, t he producer
is now stuck waiting too.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 385

SEMAPHORES 349
1 sem_t empty;
2 sem_t full;
3 sem_t mutex;
4
5 void *producer(void *arg) {
6 int i;
7 for (i = 0; i < loops; i++) {
8 sem_wait(&mutex); // line p0 (NEW LINE)
9 sem_wait(&empty); // line p1
10 put(i); // line p2
11 sem_post(&full); // line p3
12 sem_post(&mutex); // line p4 (NEW LINE)
13 }
14 }
15
16 void *consumer(void *arg) {
17 int i;
18 for (i = 0; i < loops; i++) {
19 sem_wait(&mutex); // line c0 (NEW LINE)
20 sem_wait(&full); // line c1
21 int tmp = get(); // line c2
22 sem_post(&empty); // line c3
23 sem_post(&mutex); // line c4 (NEW LINE)
24 printf("%d\n", tmp);
25 }
26 }
27
28 int main(int argc, char *argv[]) {
29 // ...
30 sem_init(&empty, 0, MAX); // MAX buffers are empty to begin w ith...
31 sem_init(&full, 0, 0); // ... and 0 are full
32 sem_init(&mutex, 0, 1); // mutex=1 because it is a lock (NEW L INE)
33 // ...
34 }
Figure 31.7: Adding Mutual Exclusion (Incorrectly)
There is a simple cycle here. The consumer holds the mutex and is
waiting for the someone to signal full. The producer could signal full but
is waiting for the mutex. Thus, the producer and consumer are each stuck
waiting for each other: a classic deadlock.
Finally , A Working Solution
To solve this problem, we simply must reduce the scope of the l ock. Fig-
ure
31.8 shows the ﬁnal working solution. As you can see, we simply
move the mutex acquire and release to be just around the criti cal section;
the full and empty wait and signal code is left outside. The re sult is a
simple and working bounded buffer, a commonly-used pattern in multi-
threaded programs. Understand it now; use it later. You will thank us for
years to come. Or at least, you will thank us when the same ques tion is
asked on the ﬁnal exam.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 386

350 SEMAPHORES
1 sem_t empty;
2 sem_t full;
3 sem_t mutex;
4
5 void *producer(void *arg) {
6 int i;
7 for (i = 0; i < loops; i++) {
8 sem_wait(&empty); // line p1
9 sem_wait(&mutex); // line p1.5 (MOVED MUTEX HERE...)
10 put(i); // line p2
11 sem_post(&mutex); // line p2.5 (... AND HERE)
12 sem_post(&full); // line p3
13 }
14 }
15
16 void *consumer(void *arg) {
17 int i;
18 for (i = 0; i < loops; i++) {
19 sem_wait(&full); // line c1
20 sem_wait(&mutex); // line c1.5 (MOVED MUTEX HERE...)
21 int tmp = get(); // line c2
22 sem_post(&mutex); // line c2.5 (... AND HERE)
23 sem_post(&empty); // line c3
24 printf("%d\n", tmp);
25 }
26 }
27
28 int main(int argc, char *argv[]) {
29 // ...
30 sem_init(&empty, 0, MAX); // MAX buffers are empty to begin w ith...
31 sem_init(&full, 0, 0); // ... and 0 are full
32 sem_init(&mutex, 0, 1); // mutex=1 because it is a lock
33 // ...
34 }
Figure 31.8: Adding Mutual Exclusion (Correctly)
31.5 Reader-Writer Locks
Another classic problem stems from the desire for a more ﬂexible lock-
ing primitive that admits that different data structure acc esses might re-
quire different kinds of locking. For example, imagine a num ber of con-
current list operations, including inserts and simple look ups. While in-
serts change the state of the list (and thus a traditional cri tical section
makes sense), lookups simply read the data structure; as long as we can
guarantee that no insert is on-going, we can allow many looku ps to pro-
ceed concurrently . The special type of lock we will now devel op to sup-
port this type of operation is known as a reader-writer lock [CHP71]. The
code for such a lock is available in Figure
31.9.
The code is pretty simple. If some thread wants to update the d ata
structure in question, it should call the new pair of synchro nization op-
erations: rwlock acquire writelock(), to acquire a write lock, and
rwlock release writelock(), to release it. Internally , these simply
use the writelock semaphore to ensure that only a single writer can ac-
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 387

SEMAPHORES 351
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
12
13 void rwlock_acquire_readlock(rwlock_t *rw) {
14 sem_wait(&rw->lock);
15 rw->readers++;
16 if (rw->readers == 1)
17 sem_wait(&rw->writelock); // first reader acquires write lock
18 sem_post(&rw->lock);
19 }
20
21 void rwlock_release_readlock(rwlock_t *rw) {
22 sem_wait(&rw->lock);
23 rw->readers--;
24 if (rw->readers == 0)
25 sem_post(&rw->writelock); // last reader releases writel ock
26 sem_post(&rw->lock);
27 }
28
29 void rwlock_acquire_writelock(rwlock_t *rw) {
30 sem_wait(&rw->writelock);
31 }
32
33 void rwlock_release_writelock(rwlock_t *rw) {
34 sem_post(&rw->writelock);
35 }
Figure 31.9: A Simple Reader-Writer Lock
quire the lock and thus enter the critical section to update t he data struc-
ture in question.
More interesting is the pair of routines to acquire and relea se read
locks. When acquiring a read lock, the reader ﬁrst acquires lock and
then increments the readers variable to track how many readers are
currently inside the data structure. The important step the n taken within
rwlock
acquire readlock() occurs when the ﬁrst reader acquires
the lock; in that case, the reader also acquires the write loc k by calling
sem wait() on the writelock semaphore, and then ﬁnally releasing
the lock by calling sem post().
Thus, once a reader has acquired a read lock, more readers wil l be
allowed to acquire the read lock too; however, any thread tha t wishes to
acquire the write lock will have to wait until all readers are ﬁnished; the
last one to exit the critical section calls sem post() on “writelock” and
thus enables a waiting writer to acquire the lock.
This approach works (as desired), but does have some negatives, espe-
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 388

352 SEMAPHORES
TIP : S IMPLE AND DUMB CAN BE BETTER (H ILL ’ S LAW)
You should never underestimate the notion that the simple an d dumb
approach can be the best one. With locking, sometimes a simpl e spin lock
works best, because it is easy to implement and fast. Althoug h something
like reader/writer locks sounds cool, they are complex, and complex can
mean slow . Thus, always try the simple and dumb approach ﬁrst .
This idea, of appealing to simplicity , is found in many place s. One early
source is Mark Hill’s dissertation [H87], which studied how to design
caches for CPUs. Hill found that simple direct-mapped cache s worked
better than fancy set-associative designs (one reason is th at in caching,
simpler designs enable faster lookups). As Hill succinctly summarized
his work: “Big and dumb is better.” And thus we call this simil ar advice
Hill’s Law .
cially when it comes to fairness. In particular, it would be r elatively easy
for readers to starve writers. More sophisticated solution s to this prob-
lem exist; perhaps you can think of a better implementation? Hint: think
about what you would need to do to prevent more readers from en tering
the lock once a writer is waiting.
Finally , it should be noted that reader-writer locks should be used
with some caution. They often add more overhead (especially with more
sophisticated implementations), and thus do not end up spee ding up
performance as compared to just using simple and fast lockin g primi-
tives [CB08]. Either way , they showcase once again how we can use
semaphores in an interesting and useful way .
31.6 The Dining Philosophers
One of the most famous concurrency problems posed, and solve d, by
Dijkstra, is known as the dining philosopher’s problem [DHO71]. The
problem is famous because it is fun and somewhat intellectua lly inter-
esting; however, its practical utility is low . However, its fame forces its
inclusion here; indeed, you might be asked about it on some in terview ,
and you’d really hate your OS professor if you miss that quest ion and
don’t get the job. Conversely , if you get the job, please feel free to send
your OS professor a nice note, or some stock options.
The basic setup for the problem is this (as shown in Figure 31.10): as-
sume there are ﬁve “philosophers” sitting around a table. Be tween each
pair of philosophers is a single fork (and thus, ﬁve total). T he philoso-
phers each have times where they think, and don’t need any for ks, and
times where they eat. In order to eat, a philosopher needs two forks, both
the one on their left and the one on their right. The contentio n for these
forks, and the synchronization problems that ensue, are wha t makes this
a problem we study in concurrent programming.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 389

SEMAPHORES 353
P0
P1
P2
P3
P4
f0
f1
f2
f3
f4
Figure 31.10: The Dining Philosophers
Here is the basic loop of each philosopher:
while (1) {
think();
getforks();
eat();
putforks();
}
The key challenge, then, is to write the routines getforks() and
putforks() such that there is no deadlock, no philosopher starves and
never gets to eat, and concurrency is high (i.e., as many phil osophers can
eat at the same time as possible).
Following Downey’s solutions [D08], we’ll use a few helper f unctions
to get us towards a solution. They are:
int left(int p) { return p; }
int right(int p) { return (p + 1) % 5; }
When philosopher p wishes to refer to the fork on their left, they sim-
ply call left(p). Similarly , the fork on the right of a philosopher p is
referred to by calling right(p); the modulo operator therein handles
the one case where the last philosopher ( p=4) tries to grab the fork on
their right, which is fork 0.
We’ll also need some semaphores to solve this problem. Let us assume
we have ﬁve, one for each fork: sem
t forks[5] .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 390

354 SEMAPHORES
1 void getforks() {
2 sem_wait(forks[left(p)]);
3 sem_wait(forks[right(p)]);
4 }
5
6 void putforks() {
7 sem_post(forks[left(p)]);
8 sem_post(forks[right(p)]);
9 }
Figure 31.11: The getforks() and putforks() Routines
Broken Solution
We attempt our ﬁrst solution to the problem. Assume we initia lize each
semaphore (in the forks array) to a value of 1. Assume also that each
philosopher knows its own number (p). We can thus write the getforks()
and putforks() routine as shown in Figure
31.11.
The intuition behind this (broken) solution is as follows. T o acquire
the forks, we simply grab a “lock” on each one: ﬁrst the one on t he left,
and then the one on the right. When we are done eating, we relea se them.
Simple, no? Unfortunately , in this case, simple means broke n. Can you
see the problem that arises? Think about it.
The problem is deadlock. If each philosopher happens to grab the fork
on their left before any philosopher can grab the fork on thei r right, each
will be stuck holding one fork and waiting for another, forev er. Speciﬁ-
cally , philosopher 0 grabs fork 0, philosopher 1 grabs fork 1 , philosopher
2 grabs fork 2, philosopher 3 grabs fork 3, and philosopher 4 g rabs fork 4;
all the forks are acquired, and all the philosophers are stuc k waiting for
a fork that another philosopher possesses. We’ll study dead lock in more
detail soon; for now , it is safe to say that this is not a workin g solution.
A Solution: Breaking The Dependency
The simplest way to attack this problem is to change how forks are ac-
quired by at least one of the philosophers; indeed, this is ho w Dijkstra
himself solved the problem. Speciﬁcally , let’s assume that philosopher
4 (the highest numbered one) acquires the forks in a different order. The
code to do so is as follows:
1 void getforks() {
2 if (p == 4) {
3 sem_wait(forks[right(p)]);
4 sem_wait(forks[left(p)]);
5 } else {
6 sem_wait(forks[left(p)]);
7 sem_wait(forks[right(p)]);
8 }
9 }
Because the last philosopher tries to grab right before left , there is no
situation where each philosopher grabs one fork and is stuck waiting for
another; the cycle of waiting is broken. Think through the ra miﬁcations
of this solution, and convince yourself that it works.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 391

SEMAPHORES 355
1 typedef struct __Zem_t {
2 int value;
3 pthread_cond_t cond;
4 pthread_mutex_t lock;
5 } Zem_t;
6
7 // only one thread can call this
8 void Zem_init(Zem_t *s, int value) {
9 s->value = value;
10 Cond_init(&s->cond);
11 Mutex_init(&s->lock);
12 }
13
14 void Zem_wait(Zem_t *s) {
15 Mutex_lock(&s->lock);
16 while (s->value <= 0)
17 Cond_wait(&s->cond, &s->lock);
18 s->value--;
19 Mutex_unlock(&s->lock);
20 }
21
22 void Zem_post(Zem_t *s) {
23 Mutex_lock(&s->lock);
24 s->value++;
25 Cond_signal(&s->cond);
26 Mutex_unlock(&s->lock);
27 }
Figure 31.12: Implementing Zemaphores with Locks and CVs
There are other “famous” problems like this one, e.g., the cigarette
smoker’s problem or the sleeping barber problem . Most of them are
just excuses to think about concurrency; some of them have fa scinating
names. Look them up if you are interested in learning more, or just get-
ting more practice thinking in a concurrent manner [D08].
31.7 How To Implement Semaphores
Finally , let’s use our low-level synchronization primitiv es, locks and
condition variables, to build our own version of semaphores called ...
(drum roll here) ... Zemaphores. This task is fairly straightforward, as
you can see in Figure
31.12.
As you can see from the ﬁgure, we use just one lock and one condi tion
variable, plus a state variable to track the value of the sema phore. Study
the code for yourself until you really understand it. Do it!
One subtle difference between our Zemaphore and pure semaph ores
as deﬁned by Dijkstra is that we don’t maintain the invariant that the
value of the semaphore, when negative, reﬂects the number of waiting
threads; indeed, the value will never be lower than zero. Thi s behavior is
easier to implement and matches the current Linux implement ation.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 392

356 SEMAPHORES
TIP : B E CAREFUL WITH GENERALIZATION
The abstract technique of generalization can thus be quite u seful in sys-
tems design, where one good idea can be made slightly broader and thus
solve a larger class of problems. However, be careful when ge neralizing;
as Lampson warns us “Don’t generalize; generalizations are generally
wrong” [L83].
One could view semaphores as a generalization of locks and co ndition
variables; however, is such a generalization needed? And, g iven the dif-
ﬁculty of realizing a condition variable on top of a semaphor e, perhaps
this generalization is not as general as you might think.
Curiously , building locks and condition variables out of se maphores
is a much trickier proposition. Some highly experienced con current pro-
grammers tried to do this in the Windows environment, and man y differ-
ent bugs ensued [B04]. Try it yourself, and see if you can ﬁgur e out why
building condition variables out of semaphores is more chal lenging than
it might appear.
31.8 Summary
Semaphores are a powerful and ﬂexible primitive for writing concur-
rent programs. Some programmers use them exclusively , shunning locks
and condition variables, due to their simplicity and utilit y .
In this chapter, we have presented just a few classic problems and solu-
tions. If you are interested in ﬁnding out more, there are man y other ma-
terials you can reference. One great (and free reference) is Allen Downey’s
book on concurrency and programming with semaphores [D08]. This
book has lots of puzzles you can work on to improve your unders tand-
ing of both semaphores in speciﬁc and concurrency in general . Becoming
a real concurrency expert takes years of effort; going beyon d what you
learn in this class is undoubtedly the key to mastering such a topic.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 393

SEMAPHORES 357
References
[B04] “Implementing Condition Variables with Semaphores”
Andrew Birrell
December 2004
An interesting read on how difﬁcult implementing CVs on top o f semaphores really is, and the mistakes
the author and co-workers made along the way. Particularly r elevant because the group had done a ton
of concurrent programming; Birrell, for example, is known f or (among other things) writing various
thread-programming guides.
[CB08] “Real-world Concurrency”
Bryan Cantrill and Jeff Bonwick
ACM Queue. V olume 6, No. 5. September 2008
A nice article by some kernel hackers from a company formerly known as Sun on the real problems faced
in concurrent code.
[CHP71] “Concurrent Control with Readers and Writers”
P .J. Courtois, F. Heymans, D.L. Parnas
Communications of the ACM, 14:10, October 1971
The introduction of the reader-writer problem, and a simple solution. Later work introduced more
complex solutions, skipped here because, well, they are pre tty complex.
[D59] “A Note on Two Problems in Connexion with Graphs”
E. W. Dijkstra
Numerische Mathematik 1, 269271, 1959
Available: http://www-m3.ma.tum.de/twiki/pub/MN0506/WebHome/dijkstra.pdf
Can you believe people worked on algorithms in 1959? We can’t . Even before computers were any fun
to use, these people had a sense that they would transform the world...
[D68a] “Go-to Statement Considered Harmful”
E.W. Dijkstra
Communications of the ACM, volume 11(3): pages 147148, Marc h 1968
Available: http://www.cs.utexas.edu/users/EWD/ewd02xx/EWD215.PDF
Sometimes thought as the beginning of the ﬁeld of software en gineering.
[D68b] “The Structure of the THE Multiprogramming System”
E.W. Dijkstra
Communications of the ACM, volume 11(5), pages 341346, 1968
One of the earliest papers to point out that systems work in co mputer science is an engaging intellectual
endeavor. Also argues strongly for modularity in the form of layered systems.
[D72] “Information Streams Sharing a Finite Buffer”
E.W. Dijkstra
Information Processing Letters 1: 179180, 1972
Available: http://www.cs.utexas.edu/users/EWD/ewd03xx/EWD329.PDF
Did Dijkstra invent everything? No, but maybe close. He cert ainly was the ﬁrst to clearly write down
what the problems were in concurrent code. However, it is tru e that practitioners in operating system
design knew of many of the problems described by Dijkstra, so perhaps giving him too much credit
would be a misrepresentation of history.
[D08] “The Little Book of Semaphores”
A.B. Downey
Available: http://greenteapress.com/semaphores/
A nice (and free!) book about semaphores. Lots of fun problem s to solve, if you like that sort of thing.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 394

358 SEMAPHORES
[DHO71] “Hierarchical ordering of sequential processes”
E.W. Dijkstra
Available: http://www.cs.utexas.edu/users/EWD/ewd03xx/EWD310.PDF
Presents numerous concurrency problems, including the Din ing Philosophers. The wikipedia page
about this problem is also quite informative.
[GR92] “Transaction Processing: Concepts and Techniques”
Jim Gray and Andreas Reuter
Morgan Kaufmann, September 1992
The exact quote that we ﬁnd particularly humorous is found on page 485, at the top of Section 8.8:
“The ﬁrst multiprocessors, circa 1960, had test and set inst ructions ... presumably the OS imple-
mentors worked out the appropriate algorithms, although Di jkstra is generally credited with inventing
semaphores many years later.”
[H87] “Aspects of Cache Memory and Instruction Buffer Perfo rmance”
Mark D. Hill
Ph.D. Dissertation, U.C. Berkeley , 1987
Hill’s dissertation work, for those obsessed with caching i n early systems. A great example of a quanti-
tative dissertation.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 395

32
Common Concurrency Problems
Researchers have spent a great deal of time and effort lookin g into con-
currency bugs over many years. Much of the early work focused on
deadlock, a topic which we’ve touched on in the past chapters but will
now dive into deeply [C+71]. More recent work focuses on stud ying
other types of common concurrency bugs (i.e., non-deadlock bugs). In
this chapter, we take a brief look at some example concurrenc y problems
found in real code bases, to better understand what problems to look out
for. And thus our problem:
CRUX : H OW TO HANDLE COMMON CONCURRENCY BUGS
Concurrency bugs tend to come in a variety of common patterns .
Knowing which ones to look out for is the ﬁrst step to writing m ore ro-
bust, correct concurrent code.
32.1 What Types Of Bugs Exist?
The ﬁrst, and most obvious, question is this: what types of co ncur-
rency bugs manifest in complex, concurrent programs? This q uestion is
difﬁcult to answer in general, but fortunately , some others have done the
work for us. Speciﬁcally , we rely upon a study by Lu et al. [L+0 8], which
analyzes a number of popular concurrent applications in gre at detail to
understand what types of bugs arise in practice.
The study focuses on four major and important open-source ap plica-
tions: MySQL (a popular database management system), Apach e (a well-
known web server), Mozilla (the famous web browser), and Ope nOfﬁce
(a free version of the MS Ofﬁce suite, which some people actua lly use).
In the study , the authors examine concurrency bugs that havebeen found
and ﬁxed in each of these code bases, turning the developers’ work into a
quantitative bug analysis; understanding these results ca n help you un-
derstand what types of problems actually occur in mature cod e bases.
359

## Page 396

360 COMMON CONCURRENCY PROBLEMS
Application What it does Non-Deadlock Deadlock
MySQL Database Server 14 9
Apache Web Server 13 4
Mozilla Web Browser 41 16
OpenOfﬁce Ofﬁce Suite 6 2
Total 74 31
Table 32.1: Bugs In Modern Applications
Table
32.1 shows a summary of the bugs Lu and colleagues studied.
From the table, you can see that there were 105 total bugs, mos t of which
were not deadlock (74); the remaining 31 were deadlock bugs. Further,
you can see that the number of bugs studied from each applicat ion; while
OpenOfﬁce only had 8 total concurrency bugs, Mozilla had nea rly 60.
We now dive into these different classes of bugs (non-deadlo ck, dead-
lock) a bit more deeply . For the ﬁrst class of non-deadlock bu gs, we use
examples from the study to drive our discussion. For the seco nd class of
deadlock bugs, we discuss the long line of work that has been d one in
either preventing, avoiding, or handling deadlock.
32.2 Non-Deadlock Bugs
Non-deadlock bugs make up a majority of concurrency bugs, ac cord-
ing to Lu’s study . But what types of bugs are these? How do they arise?
How can we ﬁx them? We now discuss the two major types of non-
deadlock bugs found by Lu et al.: atomicity violation bugs and order
violation bugs.
Atomicity-Violation Bugs
The ﬁrst type of problem encountered is referred to as an atomicity vi-
olation. Here is a simple example, found in MySQL. Before reading the
explanation, try ﬁguring out what the bug is. Do it!
1 Thread 1::
2 if (thd->proc_info) {
3 ...
4 fputs(thd->proc_info, ...);
5 ...
6 }
7
8 Thread 2::
9 thd->proc_info = NULL;
In the example, two different threads access the ﬁeld proc
info in
the structure thd. The ﬁrst thread checks if the value is non-NULL and
then prints its value; the second thread sets it to NULL. Clea rly , if the
ﬁrst thread performs the check but then is interrupted befor e the call to
fputs, the second thread could run in-between, thus setting the po inter
to NULL; when the ﬁrst thread resumes, it will crash, as a NULL pointer
will be dereferenced by fputs.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 397

COMMON CONCURRENCY PROBLEMS 361
The more formal deﬁnition of an atomicity violation, accord ing to Lu
et al, is this: “The desired serializability among multiple memory accesses
is violated (i.e. a code region is intended to be atomic, but t he atomicity
is not enforced during execution).” In our example above, th e code has
an atomicity assumption (in Lu’s words) about the check for non-NULL
of proc info and the usage of proc info in the fputs() call; when
assumption is broken, the code will not work as desired.
Finding a ﬁx for this type of problem is often (but not always) straight-
forward. Can you think of how to ﬁx the code above?
In this solution, we simply add locks around the shared-vari able ref-
erences, ensuring that when either thread accesses the proc info ﬁeld,
it has a lock held. Of course (not shown), any other code that a ccesses the
structure should also acquire this lock before doing so.
1 pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
2
3 Thread 1::
4 pthread_mutex_lock(&lock);
5 if (thd->proc_info) {
6 ...
7 fputs(thd->proc_info, ...);
8 ...
9 }
10 pthread_mutex_unlock(&lock);
11
12 Thread 2::
13 pthread_mutex_lock(&lock);
14 thd->proc_info = NULL;
15 pthread_mutex_unlock(&lock);
Order-Violation Bugs
Another common type of non-deadlock bug found by Lu et al. is k nown
as an order violation. Here is another simple example; once again, see if
you can ﬁgure out why the code below has a bug in it.
1 Thread 1::
2 void init() {
3 ...
4 mThread = PR_CreateThread(mMain, ...);
5 ...
6 }
7
8 Thread 2::
9 void mMain(...) {
10 ...
11 mState = mThread->State;
12 ...
13 }
As you probably ﬁgured out, the code in Thread 2 seems to assum e
that the variable mThread has already been initialized (and is not NULL);
however, if Thread 1 does not happen to run ﬁrst, we are out of l uck, and
Thread 2 will likely crash with a NULL pointer dereference (a ssuming
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 398

362 COMMON CONCURRENCY PROBLEMS
that the value of mThread is initially NULL; if not, even stranger things
could happen as arbitrary memory locations are read through the deref-
erence in Thread 2).
The more formal deﬁnition of an order violation is this: “The desired
order between two (groups of) memory accesses is ﬂipped (i.e ., A should
always be executed before B, but the order is not enforced during execu-
tion).” [L+08]
The ﬁx to this type of bug is generally to enforce ordering. As we
discussed in detail previously , using condition variables is an easy and
robust way to add this style of synchronization into modern c ode bases.
In the example above, we could thus rewrite the code as follow s:
1 pthread_mutex_t mtLock = PTHREAD_MUTEX_INITIALIZER;
2 pthread_cond_t mtCond = PTHREAD_COND_INITIALIZER;
3 int mtInit = 0;
4
5 Thread 1::
6 void init() {
7 ...
8 mThread = PR_CreateThread(mMain, ...);
9
10 // signal that the thread has been created...
11 pthread_mutex_lock(&mtLock);
12 mtInit = 1;
13 pthread_cond_signal(&mtCond);
14 pthread_mutex_unlock(&mtLock);
15 ...
16 }
17
18 Thread 2::
19 void mMain(...) {
20 ...
21 // wait for the thread to be initialized...
22 pthread_mutex_lock(&mtLock);
23 while (mtInit == 0)
24 pthread_cond_wait(&mtCond, &mtLock);
25 pthread_mutex_unlock(&mtLock);
26
27 mState = mThread->State;
28 ...
29 }
In this ﬁxed-up code sequence, we have added a lock ( mtLock) and
corresponding condition variable ( mtCond), as well as a state variable
(mtInit). When the initialization code runs, it sets the state of mtInit
to 1 and signals that it has done so. If Thread 2 had run before t his point,
it will be waiting for this signal and corresponding state ch ange; if it runs
later, it will check the state and see that the initializatio n has already oc-
curred (i.e., mtInit is set to 1), and thus continue as is proper. Note that
we could likely use mThread as the state variable itself, but do not do so
for the sake of simplicity here. When ordering matters betwe en threads,
condition variables (or semaphores) can come to the rescue.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 399

COMMON CONCURRENCY PROBLEMS 363
Non-Deadlock Bugs: Summary
A large fraction (97%) of non-deadlock bugs studied by Lu et al. are either
atomicity or order violations. Thus, by carefully thinking about these
types of bug patterns, programmers can likely do a better job of avoiding
them. Moreover, as more automated code-checking tools deve lop, they
should likely focus on these two types of bugs as they constit ute such a
large fraction of non-deadlock bugs found in deployment.
Unfortunately , not all bugs are as easily ﬁxable as the examp les we
looked at above. Some require a deeper understanding of what the pro-
gram is doing, or a larger amount of code or data structure reorganization
to ﬁx. Read Lu et al.’s excellent (and readable) paper for mor e details.
32.3 Deadlock Bugs
Beyond the concurrency bugs mentioned above, a classic prob lem that
arises in many concurrent systems with complex locking protocols is known
as deadlock. Deadlock occurs, for example, when a thread (say Thread
1) is holding a lock (L1) and waiting for another one (L2); unf ortunately ,
the thread (Thread 2) that holds lock L2 is waiting for L1 to be released.
Here is a code snippet that demonstrates such a potential dea dlock:
Thread 1: Thread 2:
lock(L1); lock(L2);
lock(L2); lock(L1);
Note that if this code runs, deadlock does not necessarily oc cur; rather,
it may occur, if, for example, Thread 1 grabs lock L1 and then a context
switch occurs to Thread 2. At that point, Thread 2 grabs L2, an d tries to
acquire L1. Thus we have a deadlock, as each thread is waiting for the
other and neither can run. See Figure
32.1 for details; the presence of a
cycle in the graph is indicative of the deadlock.
The ﬁgure should make clear the problem. How should programm ers
write code so as to handle deadlock in some way?
CRUX : H OW TO DEAL WITH DEADLOCK
How should we build systems to prevent, avoid, or at least det ect and
recover from deadlock? Is this a real problem in systems toda y?
Why Do Deadlocks Occur?
As you may be thinking, simple deadlocks such as the one above seem
readily avoidable. For example, if Thread 1 and 2 both made su re to grab
locks in the same order, the deadlock would never arise. So wh y do dead-
locks happen?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 400

364 COMMON CONCURRENCY PROBLEMS
Thread 1
Thread 2
Lock L1
Lock L2
Holds
Holds
Wanted by
Wanted by
Figure 32.1: The Deadlock Dependency Graph
One reason is that in large code bases, complex dependencies arise
between components. Take the operating system, for example . The vir-
tual memory system might need to access the ﬁle system in orde r to page
in a block from disk; the ﬁle system might subsequently requi re a page
of memory to read the block into and thus contact the virtual m emory
system. Thus, the design of locking strategies in large syst ems must be
carefully done to avoid deadlock in the case of circular depe ndencies that
may occur naturally in the code.
Another reason is due to the nature of encapsulation. As software de-
velopers, we are taught to hide details of implementations a nd thus make
software easier to build in a modular way . Unfortunately , such modular-
ity does not mesh well with locking. As Jula et al. point out [J +08], some
seemingly innocuous interfaces almost invite you to deadlo ck. For exam-
ple, take the Java V ector class and the method AddAll(). This routine
would be called as follows:
Vector v1, v2;
v1.AddAll(v2);
Internally , because the method needs to be multi-thread safe, locks for
both the vector being added to (v1) and the parameter (v2) nee d to be
acquired. The routine acquires said locks in some arbitrary order (say v1
then v2) in order to add the contents of v2 to v1. If some other t hread
calls v2.AddAll(v1) at nearly the same time, we have the potential for
deadlock, all in a way that is quite hidden from the calling ap plication.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

