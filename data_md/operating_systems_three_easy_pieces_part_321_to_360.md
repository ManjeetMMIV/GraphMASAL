# Document: operating_systems_three_easy_pieces (Pages 321 to 360)

## Page 321

INTERLUDE : T HREAD API 285
// Use this to keep your code clean but check for failures
// Only use if exiting program is OK upon failure
void Pthread_mutex_lock(pthread_mutex_t *mutex) {
int rc = pthread_mutex_lock(mutex);
assert(rc == 0);
}
Figure 27.4: An Example Wrapper
The lock and unlock routines are not the only routines that pt hreads
has to interact with locks. In particular, here are two more r outines which
may be of interest:
int pthread_mutex_trylock(pthread_mutex_t *mutex);
int pthread_mutex_timedlock(pthread_mutex_t *mutex,
struct timespec *abs_timeout);
These two calls are used in lock acquisition. The trylock version re-
turns failure if the lock is already held; the timedlock version of acquir-
ing a lock returns after a timeout or after acquiring the lock , whichever
happens ﬁrst. Thus, the timedlock with a timeout of zero dege nerates
to the trylock case. Both of these versions should generally be avoided;
however, there are a few cases where avoiding getting stuck ( perhaps in-
deﬁnitely) in a lock acquisition routine can be useful, as we’ll see in future
chapters (e.g., when we study deadlock).
27.4 Condition Variables
The other major component of any threads library , and certai nly the
case with POSIX threads, is the presence of a condition variable . Con-
dition variables are useful when some kind of signaling must take place
between threads, if one thread is waiting for another to do so mething be-
fore it can continue. Two primary routines are used by progra ms wishing
to interact in this way:
int pthread_cond_wait(pthread_cond_t *cond, pthread_mutex_t *mutex);
int pthread_cond_signal(pthread_cond_t *cond);
To use a condition variable, one has to in addition have a lock that is
associated with this condition. When calling either of the a bove routines,
this lock should be held.
The ﬁrst routine, pthread
cond wait(), puts the calling thread to
sleep, and thus waits for some other thread to signal it, usua lly when
something in the program has changed that the now-sleeping thread might
care about. For example, a typical usage looks like this:
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t init = PTHREAD_COND_INITIALIZER;
Pthread_mutex_lock(&lock);
while (initialized == 0)
Pthread_cond_wait(&init, &lock);
Pthread_mutex_unlock(&lock);
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 322

286 INTERLUDE : T HREAD API
In this code, after initialization of the relevant lock and c ondition3,
a thread checks to see if the variable initialized has yet been set to
something other than zero. If not, the thread simply calls th e wait routine
in order to sleep until some other thread wakes it.
The code to wake a thread, which would run in some other thread ,
looks like this:
Pthread_mutex_lock(&lock);
initialized = 1;
Pthread_cond_signal(&init);
Pthread_mutex_unlock(&lock);
A few things to note about this code sequence. First, when sig nal-
ing (as well as when modifying the global variable initialized), we
always make sure to have the lock held. This ensures that we do n’t acci-
dentally introduce a race condition into our code.
Second, you might notice that the wait call takes a lock as its second
parameter, whereas the signal call only takes a condition. T he reason
for this difference is that the wait call, in addition to putt ing the call-
ing thread to sleep, releases the lock when putting said caller to sleep.
Imagine if it did not: how could the other thread acquire the l ock and
signal it to wake up? However, before returning after being woken, the
pthread
cond wait() re-acquires the lock, thus ensuring that any time
the waiting thread is running between the lock acquire at the beginning
of the wait sequence, and the lock release at the end, it holds the lock.
One last oddity: the waiting thread re-checks the condition in a while
loop, instead of a simple if statement. We’ll discuss this is sue in detail
when we study condition variables in a future chapter, but in general,
using a while loop is the simple and safe thing to do. Although it rechecks
the condition (perhaps adding a little overhead), there are some pthread
implementations that could spuriously wake up a waiting thread; in such
a case, without rechecking, the waiting thread will continu e thinking that
the condition has changed even though it has not. It is safer t hus to view
waking up as a hint that something might have changed, rather than an
absolute fact.
Note that sometimes it is tempting to use a simple ﬂag to signa l be-
tween two threads, instead of a condition variable and assoc iated lock.
For example, we could rewrite the waiting code above to look m ore like
this in the waiting code:
while (initialized == 0)
; // spin
The associated signaling code would look like this:
initialized = 1;
3Note that one could use pthread cond init() (and correspond-
ing the pthread cond destroy() call) instead of the static initializer
PTHREAD COND INITIALIZER. Sound like more work? It is.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 323

INTERLUDE : T HREAD API 287
Don’t ever do this, for the following reasons. First, it perf orms poorly
in many cases (spinning for a long time just wastes CPU cycles ). Sec-
ond, it is error prone. As recent research shows [X+10], it is surprisingly
easy to make mistakes when using ﬂags (as above) to synchroni ze be-
tween threads; roughly half the uses of these ad hoc synchronizations were
buggy! Don’t be lazy; use condition variables even when you t hink you
can get away without doing so.
27.5 Compiling and Running
All of the code examples in this chapter are relatively easy t o get up
and running. To compile them, you must include the header pthread.h
in your code. On the link line, you must also explicitly link w ith the
pthreads library , by adding the -pthread ﬂag.
For example, to compile a simple multi-threaded program, al l you
have to do is the following:
prompt> gcc -o main main.c -Wall -pthread
As long as main.c includes the pthreads header, you have now suc-
cessfully compiled a concurrent program. Whether it works o r not, as
usual, is a different matter entirely .
27.6 Summary
We have introduced the basics of the pthread library , including thread
creation, building mutual exclusion via locks, and signali ng and waiting
via condition variables. You don’t need much else to write ro bust and
efﬁcient multi-threaded code, except patience and a great d eal of care!
We now end the chapter with a set of tips that might be useful to you
when you write multi-threaded code (see the aside on the foll owing page
for details). There are other aspects of the API that are inte resting; if you
want more information, type man -k pthread on a Linux system to
see over one hundred APIs that make up the entire interface. H owever,
the basics discussed herein should enable you to build sophi sticated (and
hopefully , correct and performant) multi-threaded progra ms. The hard
part with threads is not the APIs, but rather the tricky logic of how you
build concurrent programs. Read on to learn more.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 324

288 INTERLUDE : T HREAD API
ASIDE : THREAD API G UIDELINES
There are a number of small but important things to remember w hen
you use the POSIX thread library (or really , any thread libra ry) to build a
multi-threaded program. They are:
• Keep it simple. Above all else, any code to lock or signal between
threads should be as simple as possible. Tricky thread inter actions
lead to bugs.
• Minimize thread interactions. Try to keep the number of ways
in which threads interact to a minimum. Each interaction sho uld
be carefully thought out and constructed with tried and true ap-
proaches (many of which we will learn about in the coming chap -
ters).
• Initialize locks and condition variables. Failure to do so will lead
to code that sometimes works and sometimes fails in very stra nge
ways.
• Check your return codes. Of course, in any C and U NIX program-
ming you do, you should be checking each and every return code ,
and it’s true here as well. Failure to do so will lead to bizarr e and
hard to understand behavior, making you likely to (a) scream , (b)
pull some of your hair out, or (c) both.
• Be careful with how you pass arguments to, and return values
from, threads. In particular, any time you are passing a reference to
a variable allocated on the stack, you are probably doing som ething
wrong.
• Each thread has its own stack. As related to the point above, please
remember that each thread has its own stack. Thus, if you have a
locally-allocated variable inside of some function a threa d is exe-
cuting, it is essentially private to that thread; no other thread can
(easily) access it. To share data between threads, the value s must be
in the heap or otherwise some locale that is globally accessible.
• Always use condition variables to signal between threads. While
it is often tempting to use a simple ﬂag, don’t do it.
• Use the manual pages. On Linux, in particular, the pthread man
pages are highly informative and discuss much of the nuances pre-
sented here, often in even more detail. Read them carefully!
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 325

INTERLUDE : T HREAD API 289
References
[B97] “Programming with POSIX Threads”
David R. Butenhof
Addison-Wesley , May 1997
Another one of these books on threads.
[B+96] “PThreads Programming:
A POSIX Standard for Better Multiprocessing”
Dick Buttlar, Jacqueline Farrell, Bradford Nichols
O’Reilly , September 1996
A reasonable book from the excellent, practical publishing house O’Reilly. Our bookshelves certainly
contain a great deal of books from this company, including so me excellent offerings on Perl, Python, and
Javascript (particularly Crockford’s “Javascript: The Go od Parts”.)
[K+96] “Programming With Threads”
Steve Kleiman, Devang Shah, Bart Smaalders
Prentice Hall, January 1996
Probably one of the better books in this space. Get it at your l ocal library.
[X+10] “Ad Hoc Synchronization Considered Harmful”
Weiwei Xiong, Soyeon Park, Jiaqi Zhang, Yuanyuan Zhou, Zhiq iang Ma
OSDI 2010, Vancouver, Canada
This paper shows how seemingly simple synchronization code can lead to a surprising number of bugs.
Use condition variables and do the signaling correctly!
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 327

28
Locks
From the introduction to concurrency , we saw one of the funda mental
problems in concurrent programming: we would like to execut e a series
of instructions atomically , but due to the presence of interrupts on a single
processor (or multiple threads executing on multiple proce ssors concur-
rently), we couldn’t. In this chapter, we thus attack this pr oblem directly ,
with the introduction of something referred to as a lock. Programmers
annotate source code with locks, putting them around critic al sections,
and thus ensure that any such critical section executes as if it were a sin-
gle atomic instruction.
28.1 Locks: The Basic Idea
As an example, assume our critical section looks like this, the canonical
update of a shared variable:
balance = balance + 1;
Of course, other critical sections are possible, such as add ing an ele-
ment to a linked list or other more complex updates to shared s tructures,
but we’ll just keep to this simple example for now . To use a loc k, we add
some code around the critical section like this:
1 lock_t mutex; // some globally-allocated lock ’mutex’
2 ...
3 lock(&mutex);
4 balance = balance + 1;
5 unlock(&mutex);
A lock is just a variable, and thus to use one, you must declare a lock
variable of some kind (such as mutex above). This lock variable (or just
“lock” for short) holds the state of the lock at any instant in time. It is ei-
ther available (or unlocked or free) and thus no thread holds the lock, or
acquired (or locked or held), and thus exactly one thread holds the lock
and presumably is in a critical section. We could store other information
291

## Page 328

292 LOCKS
in the data type as well, such as which thread holds the lock, o r a queue
for ordering lock acquisition, but information like that is hidden from the
user of the lock.
The semantics of the lock() and unlock() routines are simple. Call-
ing the routine lock() tries to acquire the lock; if no other thread holds
the lock (i.e., it is free), the thread will acquire the lock a nd enter the crit-
ical section; this thread is sometimes said to be the owner of the lock. If
another thread then calls lock() on that same lock variable ( mutex in
this example), it will not return while the lock is held by ano ther thread;
in this way , other threads are prevented from entering the cr itical section
while the ﬁrst thread that holds the lock is in there.
Once the owner of the lock calls unlock(), the lock is now available
(free) again. If no other threads are waiting for the lock (i. e., no other
thread has called lock() and is stuck therein), the state of the lock is
simply changed to free. If there are waiting threads (stuck i n lock()),
one of them will (eventually) notice (or be informed of) this change of the
lock’s state, acquire the lock, and enter the critical secti on.
Locks provide some minimal amount of control over schedulin g to
programmers. In general, we view threads as entities create d by the pro-
grammer but scheduled by the OS, in any fashion that the OS cho oses.
Locks yield some of that control back to the programmer; by pu tting
a lock around a section of code, the programmer can guarantee that no
more than a single thread can ever be active within that code. Thus locks
help transform the chaos that is traditional OS scheduling i nto a more
controlled activity .
28.2 Pthread Locks
The name that the POSIX library uses for a lock is a mutex, as it is used
to provide mutual exclusion between threads, i.e., if one thread is in the
critical section, it excludes the others from entering unti l it has completed
the section. Thus, when you see the following POSIX threads c ode, you
should understand that it is doing the same thing as above (we again use
our wrappers that check for errors upon lock and unlock):
1 pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
2
3 Pthread_mutex_lock(&lock); // wrapper for pthread_mutex _lock()
4 balance = balance + 1;
5 Pthread_mutex_unlock(&lock);
You might also notice here that the POSIX version passes a var iable
to lock and unlock, as we may be using different locks to protect different
variables. Doing so can increase concurrency: instead of on e big lock that
is used any time any critical section is accessed (a coarse-grained locking
strategy), one will often protect different data and data st ructures with
different locks, thus allowing more threads to be in locked c ode at once
(a more ﬁne-grained approach).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 329

LOCKS 293
28.3 Building A Lock
By now , you should have some understanding of how a lock works ,
from the perspective of a programmer. But how should we build a lock?
What hardware support is needed? What OS support? It is this s et of
questions we address in the rest of this chapter.
The Crux: H OW TO BUILD A L OCK
How can we build an efﬁcient lock? Efﬁcient locks provided mu tual
exclusion at low cost, and also might attain a few other prope rties we
discuss below . What hardware support is needed? What OS supp ort?
To build a working lock, we will need some help from our old fri end,
the hardware, as well as our good pal, the OS. Over the years, a num-
ber of different hardware primitives have been added to the i nstruction
sets of various computer architectures; while we won’t stud y how these
instructions are implemented (that, after all, is the topic of a computer
architecture class), we will study how to use them in order to build a mu-
tual exclusion primitive like a lock. We will also study how t he OS gets
involved to complete the picture and enable us to build a soph isticated
locking library .
28.4 Evaluating Locks
Before building any locks, we should ﬁrst understand what ou r goals
are, and thus we ask how to evaluate the efﬁcacy of a particula r lock
implementation. To evaluate whether a lock works (and works well), we
should ﬁrst establish some basic criteria. The ﬁrst is whether the lock does
its basic task, which is to provide mutual exclusion . Basically , does the
lock work, preventing multiple threads from entering a crit ical section?
The second is fairness. Does each thread contending for the lock get
a fair shot at acquiring it once it is free? Another way to look at this is
by examining the more extreme case: does any thread contendi ng for the
lock starve while doing so, thus never obtaining it?
The ﬁnal criterion is performance, speciﬁcally the time overheads added
by using the lock. There are a few different cases that are wor th con-
sidering here. One is the case of no contention; when a single thread
is running and grabs and releases the lock, what is the overhe ad of do-
ing so? Another is the case where multiple threads are conten ding for
the lock on a single CPU; in this case, are there performance c oncerns? Fi-
nally , how does the lock perform when there are multiple CPUsinvolved,
and threads on each contending for the lock? By comparing the se differ-
ent scenarios, we can better understand the performance imp act of using
various locking techniques, as described below .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 330

294 LOCKS
28.5 Controlling Interrupts
One of the earliest solutions used to provide mutual exclusi on was
to disable interrupts for critical sections; this solution was invented for
single-processor systems. The code would look like this:
1 void lock() {
2 DisableInterrupts();
3 }
4 void unlock() {
5 EnableInterrupts();
6 }
Assume we are running on such a single-processor system. By t urn-
ing off interrupts (using some kind of special hardware inst ruction) be-
fore entering a critical section, we ensure that the code ins ide the critical
section will not be interrupted, and thus will execute as if it were atomic.
When we are ﬁnished, we re-enable interrupts (again, via a ha rdware in-
struction) and thus the program proceeds as usual.
The main positive of this approach is its simplicity . You certainly don’t
have to scratch your head too hard to ﬁgure out why this works. Without
interruption, a thread can be sure that the code it executes w ill execute
and that no other thread will interfere with it.
The negatives, unfortunately , are many . First, this approa ch requires
us to allow any calling thread to perform a privileged operation (turning
interrupts on and off), and thus trust that this facility is not abused. As
you already know , any time we are required to trust an arbitra ry pro-
gram, we are probably in trouble. Here, the trouble manifest s in numer-
ous ways: a greedy program could call lock() at the beginning of its
execution and thus monopolize the processor; worse, an erra nt or mali-
cious program could call lock() and go into an endless loop. In this
latter case, the OS never regains control of the system, and t here is only
one recourse: restart the system. Using interrupt disablin g as a general-
purpose synchronization solution requires too much trust in applications.
Second, the approach does not work on multiprocessors. If mu ltiple
threads are running on different CPUs, and each try to enter t he same
critical section, it does not matter whether interrupts are disabled; threads
will be able to run on other processors, and thus could enter t he critical
section. As multiprocessors are now commonplace, our gener al solution
will have to do better than this.
Third, and probably least important, this approach can be in efﬁcient.
Compared to normal instruction execution, code that masks o r unmasks
interrupts tends to be executed slowly by modern CPUs.
For these reasons, turning off interrupts is only used in lim ited con-
texts as a mutual-exclusion primitive. For example, in some cases an
operating system itself will sometimes use interrupt maski ng to guaran-
tee atomicity when accessing its own data structures, or at l east to pre-
vent certain messy interrupt handling situations from aris ing. This usage
makes sense, as the trust issue disappears inside the OS, whi ch always
trusts itself to perform privileged operations anyhow .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 331

LOCKS 295
ASIDE : DEKKER ’ S AND PETERSON ’ S ALGORITHMS
In the 1960’s, Dijkstra posed the concurrency problem to his friends,
and one of them, a mathematician named Theodorus Jozef Dekke r, came
up with a solution [D68]. Unlike the solutions we discuss her e, which use
special hardware instructions and even OS support, Dekker’ s approach
uses just loads and stores (assuming they are atomic with res pect to each
other, which was true on early hardware).
Dekker’s approach was later reﬁned by Peterson [P81] (and th us “Pe-
terson’s algorithm”), shown here. Once again, just loads an d stores are
used, and the idea is to ensure that two threads never enter a c ritical sec-
tion at the same time. Here is Peterson’s algorithm (for two t hreads); see
if you can understand it.
int flag[2];
int turn;
void init() {
flag[0] = flag[1] = 0; // 1->thread wants to grab lock
turn = 0; // whose turn? (thread 0 or 1?)
}
void lock() {
flag[self] = 1; // self: thread ID of caller
turn = 1 - self; // make it other thread’s turn
while ((flag[1-self] == 1) && (turn == 1 - self))
; // spin-wait
}
void unlock() {
flag[self] = 0; // simply undo your intent
}
For some reason, developing locks that work without special hard-
ware support became all the rage for a while, giving theory-t ypes a lot
of problems to work on. Of course, this all became quite usele ss when
people realized it is much easier to assume a little hardware support (and
indeed that support had been around from the very earliest days of multi-
processing). Further, algorithms like the ones above don’t work on mod-
ern hardware (due to relaxed memory consistency models), th us making
them even less useful than they were before. Yet more researc h relegated
to the dustbin of history ...
28.6 Test And Set (Atomic Exchange)
Because disabling interrupts does not work on multiple proc essors,
system designers started to invent hardware support for loc king. The
earliest multiprocessor systems, such as the Burroughs B50 00 in the early
1960’s [M82], had such support; today all systems provide th is type of
support, even for single CPU systems.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 332

296 LOCKS
1 typedef struct __lock_t { int flag; } lock_t;
2
3 void init(lock_t *mutex) {
4 // 0 -> lock is available, 1 -> held
5 mutex->flag = 0;
6 }
7
8 void lock(lock_t *mutex) {
9 while (mutex->flag == 1) // TEST the flag
10 ; // spin-wait (do nothing)
11 mutex->flag = 1; // now SET it!
12 }
13
14 void unlock(lock_t *mutex) {
15 mutex->flag = 0;
16 }
Figure 28.1: First Attempt: A Simple Flag
The simplest bit of hardware support to understand is what is known
as a test-and-set instruction, also known as atomic exchange. To under-
stand how test-and-set works, let’s ﬁrst try to build a simpl e lock without
it. In this failed attempt, we use a simple ﬂag variable to den ote whether
the lock is held or not.
In this ﬁrst attempt (Figure
28.1), the idea is quite simple: use a simple
variable to indicate whether some thread has possession of a lock. The
ﬁrst thread that enters the critical section will call lock(), which tests
whether the ﬂag is equal to 1 (in this case, it is not), and then sets the ﬂag
to 1 to indicate that the thread now holds the lock. When ﬁnished with
the critical section, the thread calls unlock() and clears the ﬂag, thus
indicating that the lock is no longer held.
If another thread happens to call lock() while that ﬁrst thread is in
the critical section, it will simply spin-wait in the while loop for that
thread to call unlock() and clear the ﬂag. Once that ﬁrst thread does
so, the waiting thread will fall out of the while loop, set the ﬂag to 1 for
itself, and proceed into the critical section.
Unfortunately , the code has two problems: one of correctness, and an-
other of performance. The correctness problem is simple to s ee once you
get used to thinking about concurrent programming. Imagine the code
interleaving in Table 28.1 (assume flag=0 to begin).
Thread 1 Thread 2
call lock()
while (ﬂag == 1)
interrupt: switch to Thread 2
call lock()
while (ﬂag == 1)
ﬂag = 1;
interrupt: switch to Thread 1
ﬂag = 1; // set ﬂag to 1 (too!)
Table 28.1: T race: No Mutual Exclusion
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 333

LOCKS 297
TIP : T HINK ABOUT CONCURRENCY AS MALICIOUS SCHEDULER
What we also get from this example is a sense of the approach we
need to take when trying to understand concurrent execution . What you
are really trying to do is to pretend you are a malicious scheduler , one
that interrupts threads at the most inopportune of times in o rder to foil
their feeble attempts at building synchronization primiti ves. Although
the exact sequence of interrupts may be improbable, it is possible, and that
is all we need to show to demonstrate that a particular approa ch does not
work.
As you can see from this interleaving, with timely (untimely ?) inter-
rupts, we can easily produce a case where both threads set their ﬂags to 1
and both threads are thus able to enter the critical section. This is bad! We
have obviously failed to provide the most basic requirement : providing
mutual exclusion.
The performance problem, which we will address more later on , is the
fact that the way a thread waits to acquire a lock that is alrea dy held:
it endlessly checks the value of ﬂag, a technique known as spin-waiting.
Spin-waiting wastes time waiting for another thread to release a lock. The
waste is exceptionally high on a uniprocessor, where the thr ead that the
waiter is waiting for cannot even run (at least, until a conte xt switch oc-
curs)! Thus, as we move forward and develop more sophisticat ed solu-
tions, we should also consider ways to avoid this kind of wast e.
28.7 Building A Working Spin Lock
While the idea behind the example above is a good one, it is not possi-
ble to implement without some support from the hardware. For tunately ,
some systems provide an instruction to support the creation of simple
locks based on this concept. This more powerful instruction has differ-
ent names – on SP ARC, it is the load/store unsigned byte instr uction
(ldstub), whereas on x86, it is the atomic exchange instruction ( xchg)
– but basically does the same thing across platforms, and is u sually gen-
erally referred to as test-and-set. We deﬁne what the test-and-set instruc-
tion does with the following C code snippet:
1 int TestAndSet(int *ptr, int new) {
2 int old = *ptr; // fetch old value at ptr
3 *ptr = new; // store ’new’ into ptr
4 return old; // return the old value
5 }
What the test-and-set instruction does is as follows. It ret urns the old
value pointed to by the ptr, and simultaneously updates said value to
new. The key , of course, is that this sequence of operations is pe rformed
atomically. The reason it is called “test and set” is that it enables you
to “test” the old value (which is what is returned) while simu ltaneously
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 334

298 LOCKS
1 typedef struct __lock_t {
2 int flag;
3 } lock_t;
4
5 void init(lock_t *lock) {
6 // 0 indicates that lock is available, 1 that it is held
7 lock->flag = 0;
8 }
9
10 void lock(lock_t *lock) {
11 while (TestAndSet(&lock->flag, 1) == 1)
12 ; // spin-wait (do nothing)
13 }
14
15 void unlock(lock_t *lock) {
16 lock->flag = 0;
17 }
Figure 28.2: A Simple Spin Lock Using T est-and-set
“setting” the memory location to a new value; as it turns out, this slightly
more powerful instruction is enough to build a simple spin lock , as we
now examine in Figure
28.2.
Let’s make sure we understand why this works. Imagine ﬁrst th e case
where a thread calls lock() and no other thread currently holds the lock;
thus, flag should be 0. When the thread then calls TestAndSet(flag,
1), the routine will return the old value of flag, which is 0; thus, the call-
ing thread, which is testing the value of ﬂag, will not get caught spinning
in the while loop and will acquire the lock. The thread will al so atomi-
cally set the value to 1, thus indicating that the lock is now held. When
the thread is ﬁnished with its critical section, it calls unlock() to set the
ﬂag back to zero.
The second case we can imagine arises when one thread already has
the lock held (i.e., flag is 1). In this case, this thread will call lock() and
then call TestAndSet(flag, 1) as well. This time, TestAndSet()
will return the old value at ﬂag, which is 1 (because the lock i s held),
while simultaneously setting it to 1 again. As long as the loc k is held by
another thread, TestAndSet() will repeatedly return 1, and thus this
thread will spin and spin until the lock is ﬁnally released. When the ﬂag is
ﬁnally set to 0 by some other thread, this thread will call TestAndSet()
again, which will now return 0 while atomically setting the v alue to 1 and
thus acquire the lock and enter the critical section.
By making both the test (of the old lock value) and set (of the new
value) a single atomic operation, we ensure that only one thr ead acquires
the lock. And that’s how to build a working mutual exclusion p rimitive!
You may also now understand why this type of lock is usually referred
to as a spin lock. It is the simplest type of lock to build, and simply spins,
using CPU cycles, until the lock becomes available. To work c orrectly
on a single processor, it requires a preemptive scheduler (i.e., one that
will interrupt a thread via a timer, in order to run a differen t thread, from
time to time). Without preemption, spin locks don’t make muc h sense on
a single CPU, as a thread spinning on a CPU will never relinqui sh it.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 335

LOCKS 299
28.8 Evaluating Spin Locks
Given our basic spin lock, we can now evaluate how effective i t is
along our previously described axes. The most important asp ect of a lock
is correctness: does it provide mutual exclusion? The answer here is ob-
viously yes: the spin lock only allows a single thread to ente r the critical
section at a time. Thus, we have a correct lock.
The next axis is fairness. How fair is a spin lock to a waiting thread?
Can you guarantee that a waiting thread will ever enter the cr itical sec-
tion? The answer here, unfortunately , is bad news: spin lock s don’t pro-
vide any fairness guarantees. Indeed, a thread spinning may spin forever,
under contention. Spin locks are not fair and may lead to star vation.
The ﬁnal axis is performance. What are the costs of using a spin lock?
To analyze this more carefully , we suggest thinking about a f ew different
cases. In the ﬁrst, imagine threads competing for the lock on a single
processor; in the second, consider the threads as spread out across many
processors.
For spin locks, in the single CPU case, performance overhead s can
be quite painful; imagine the case where the thread holding t he lock is
pre-empted within a critical section. The scheduler might t hen run every
other thread (imagine there are N − 1 others), each of which tries to ac-
quire the lock. In this case, each of those threads will spin f or the duration
of a time slice before giving up the CPU, a waste of CPU cycles.
However, on multiple CPUs, spin locks work reasonably well ( if the
number of threads roughly equals the number of CPUs). The thi nking
goes as follows: imagine Thread A on CPU 1 and Thread B on CPU 2,
both contending for a lock. If Thread A (CPU 1) grabs the lock, and then
Thread B tries to, B will spin (on CPU 2). However, presumably the crit-
ical section is short, and thus soon the lock becomes availab le, and is ac-
quired by Thread B. Spinning to wait for a lock held on another processor
doesn’t waste many cycles in this case, and thus can be quite e ffective.
28.9 Compare-And-Swap
Another hardware primitive that some systems provide is kno wn as
the compare-and-swap instruction (as it is called on SP ARC, for exam-
ple), or compare-and-exchange (as it called on x86). The C pseudocode
for this single instruction is found in Figure
28.3.
The basic idea is for compare-and-swap to test whether the value at the
1 int CompareAndSwap(int *ptr, int expected, int new) {
2 int actual = *ptr;
3 if (actual == expected)
4 *ptr = new;
5 return actual;
6 }
Figure 28.3: Compare-and-swap
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 336

300 LOCKS
address speciﬁed by ptr is equal to expected; if so, update the memory
location pointed to by ptr with the new value. If not, do nothing. In
either case, return the actual value at that memory location, thus allowing
the code calling compare-and-swap to know whether it succee ded or not.
With the compare-and-swap instruction, we can build a lock i n a man-
ner quite similar to that with test-and-set. For example, we could just
replace the lock() routine above with the following:
1 void lock(lock_t *lock) {
2 while (CompareAndSwap(&lock->flag, 0, 1) == 1)
3 ; // spin
4 }
The rest of the code is the same as the test-and-set example ab ove.
This code works quite similarly; it simply checks if the ﬂag i s 0 and if
so, atomically swaps in a 1 thus acquiring the lock. Threads t hat try to
acquire the lock while it is held will get stuck spinning unti l the lock is
ﬁnally released.
If you want to see how to really make a C-callable x86-version of
compare-and-swap, this code sequence might be useful (from [S05]):
1 char CompareAndSwap(int *ptr, int old, int new) {
2 unsigned char ret;
3
4 // Note that sete sets a ’byte’ not the word
5 __asm__ __volatile__ (
6 " lock\n"
7 " cmpxchgl %2,%1\n"
8 " sete %0\n"
9 : "=q" (ret), "=m" ( *ptr)
10 : "r" (new), "m" ( *ptr), "a" (old)
11 : "memory");
12 return ret;
13 }
Finally , as you may have sensed, compare-and-swap is a more power-
ful instruction than test-and-set. We will make some use of t his power in
the future when we brieﬂy delve into wait-free synchronization [H91].
However, if we just build a simple spin lock with it, its behav ior is iden-
tical to the spin lock we analyzed above.
28.10 Load-Linked and Store-Conditional
Some platforms provide a pair of instructions that work in co ncert to
help build critical sections. On the MIPS architecture [H93 ], for example,
the load-linked and store-conditional instructions can be used in tandem
to build locks and other concurrent structures. The C pseudo code for
these instructions is as found in Figure
28.4. Alpha, PowerPC, and ARM
provide similar instructions [W09].
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 337

LOCKS 301
1 int LoadLinked(int *ptr) {
2 return *ptr;
3 }
4
5 int StoreConditional(int *ptr, int value) {
6 if (no one has updated *ptr since the LoadLinked to this address) {
7 *ptr = value;
8 return 1; // success!
9 } else {
10 return 0; // failed to update
11 }
12 }
Figure 28.4: Load-linked And Store-conditional
1 void lock(lock_t *lock) {
2 while (1) {
3 while (LoadLinked(&lock->flag) == 1)
4 ; // spin until it’s zero
5 if (StoreConditional(&lock->flag, 1) == 1)
6 return; // if set-it-to-1 was a success: all done
7 // otherwise: try it all over again
8 }
9 }
10
11 void unlock(lock_t *lock) {
12 lock->flag = 0;
13 }
Figure 28.5: Using LL/SC T o Build A Lock
The load-linked operates much like a typical load instruction, and sim-
ply fetches a value from memory and places it in a register. The key differ-
ence comes with the store-conditional, which only succeeds (and updates
the value stored at the address just load-linked from) if no i ntermittent
store to the address has taken place. In the case of success, t he store-
conditional returns 1 and updates the value at ptr to value; if it fails,
the value at ptr is not updated and 0 is returned.
As a challenge to yourself, try thinking about how to build a lock using
load-linked and store-conditional. Then, when you are ﬁnis hed, look at
the code below which provides one simple solution. Do it! The solution
is in Figure
28.5.
The lock() code is the only interesting piece. First, a thread spins
waiting for the ﬂag to be set to 0 (and thus indicate the lock is not held).
Once so, the thread tries to acquire the lock via the store-co nditional; if it
succeeds, the thread has atomically changed the ﬂag’s value to 1 and thus
can proceed into the critical section.
Note how failure of the store-conditional might arise. One t hread calls
lock() and executes the load-linked, returning 0 as the lock is not h eld.
Before it can attempt the store-conditional, it is interrup ted and another
thread enters the lock code, also executing the load-linked instruction,
and also getting a 0 and continuing. At this point, two thread s have
each executed the load-linked and each are about to attempt t he store-
conditional. The key feature of these instructions is that o nly one of these
threads will succeed in updating the ﬂag to 1 and thus acquire the lock;
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 338

302 LOCKS
TIP : L ESS CODE IS BETTER CODE (L AUER ’ S LAW)
Programmers tend to brag about how much code they wrote to do s ome-
thing. Doing so is fundamentally broken. What one should bra g about,
rather, is how little code one wrote to accomplish a given task. Short,
concise code is always preferred; it is likely easier to unde rstand and has
fewer bugs. As Hugh Lauer said, when discussing the construc tion of
the Pilot operating system: “If the same people had twice as m uch time,
they could produce as good of a system in half the code.” [L81] We’ll call
this Lauer’s Law , and it is well worth remembering. So next time you’re
bragging about how much code you wrote to ﬁnish the assignmen t, think
again, or better yet, go back, rewrite, and make the code as cl ear and con-
cise as possible.
the second thread to attempt the store-conditional will fai l (because the
other thread updated the value of ﬂag between its load-linke d and store-
conditional) and thus have to try to acquire the lock again.
In class a few years ago, undergraduate student David Capel s ug-
gested a more concise form of the above, for those of you who en joy
short-circuiting boolean conditionals. See if you can ﬁgur e out why it
is equivalent. It certainly is shorter!
1 void lock(lock_t *lock) {
2 while (LoadLinked(&lock->flag)||!StoreConditional(&l ock->flag, 1))
3 ; // spin
4 }
28.11 Fetch-And-Add
One ﬁnal hardware primitive is the fetch-and-add instruction, which
atomically increments a value while returning the old value at a partic-
ular address. The C pseudocode for the fetch-and-add instru ction looks
like this:
1 int FetchAndAdd(int *ptr) {
2 int old = *ptr;
3 *ptr = old + 1;
4 return old;
5 }
In this example, we’ll use fetch-and-add to build a more inte resting
ticket lock , as introduced by Mellor-Crummey and Scott [MS91]. The
lock and unlock code looks like what you see in Figure
28.6.
Instead of a single value, this solution uses a ticket and turn variable in
combination to build a lock. The basic operation is pretty si mple: when
a thread wishes to acquire a lock, it ﬁrst does an atomic fetch -and-add
on the ticket value; that value is now considered this thread ’s “turn”
(myturn). The globally shared lock->turn is then used to determine
which thread’s turn it is; when (myturn == turn) for a given thread,
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 339

LOCKS 303
1 typedef struct __lock_t {
2 int ticket;
3 int turn;
4 } lock_t;
5
6 void lock_init(lock_t *lock) {
7 lock->ticket = 0;
8 lock->turn = 0;
9 }
10
11 void lock(lock_t *lock) {
12 int myturn = FetchAndAdd(&lock->ticket);
13 while (lock->turn != myturn)
14 ; // spin
15 }
16
17 void unlock(lock_t *lock) {
18 FetchAndAdd(&lock->turn);
19 }
Figure 28.6: Ticket Locks
it is that thread’s turn to enter the critical section. Unloc k is accomplished
simply by incrementing the turn such that the next waiting th read (if
there is one) can now enter the critical section.
Note one important difference with this solution versus our previous
attempts: it ensures progress for all threads. Once a thread is assigned its
ticket value, it will be scheduled at some point in the future (once those in
front of it have passed through the critical section and rele ased the lock).
In our previous attempts, no such guarantee existed; a threa d spinning
on test-and-set (for example) could spin forever even as oth er threads
acquire and release the lock.
28.12 Summary: So Much Spinning
Our simple hardware-based locks are simple (only a few lines of code)
and they work (you could even prove that if you’d like to, by wr iting
some code), which are two excellent properties of any system or code.
However, in some cases, these solutions can be quite inefﬁci ent. Imagine
you are running two threads on a single processor. Now imagin e that
one thread (thread 0) is in a critical section and thus has a lo ck held, and
unfortunately gets interrupted. The second thread (thread 1) now tries to
acquire the lock, but ﬁnds that it is held. Thus, it begins to s pin. And spin.
Then it spins some more. And ﬁnally , a timer interrupt goes of f, thread
0 is run again, which releases the lock, and ﬁnally (the next t ime it runs,
say), thread 1 won’t have to spin so much and will be able to acq uire the
lock. Thus, any time a thread gets caught spinning in a situat ion like this,
it wastes an entire time slice doing nothing but checking a va lue that isn’t
going to change! The problem gets worse with N threads contending
for a lock; N − 1 time slices may be wasted in a similar manner, simply
spinning and waiting for a single thread to release the lock. And thus,
our next problem:
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 340

304 LOCKS
THE CRUX : H OW TO AVOID SPINNING
How can we develop a lock that doesn’t needlessly waste time s pin-
ning on the CPU?
Hardware support alone cannot solve the problem. We’ll need OS sup-
port too! Let’s now ﬁgure out just how that might work.
28.13 A Simple Approach: Just Yield, Baby
Hardware support got us pretty far: working locks, and even ( as with
the case of the ticket lock) fairness in lock acquisition. Ho wever, we still
have a problem: what to do when a context switch occurs in a cri tical
section, and threads start to spin endlessly , waiting for the interrupt (lock-
holding) thread to be run again?
Our ﬁrst try is a simple and friendly approach: when you are go ing to
spin, instead give up the CPU to another thread. Or, as Al Davi s might
say , “just yield, baby!” [D91]. Figure 28.7 presents the approach.
In this approach, we assume an operating system primitive yield()
which a thread can call when it wants to give up the CPU and let a n-
other thread run. Because a thread can be in one of three state s (running,
ready , or blocked), you can think of this as an OS system call t hat moves
the caller from the running state to the ready state, and thus promotes
another thread to running.
Think about the example with two threads on one CPU; in this ca se,
our yield-based approach works quite well. If a thread happe ns to call
lock() and ﬁnd a lock held, it will simply yield the CPU, and thus the
other thread will run and ﬁnish its critical section. In this simple case, the
yielding approach works well.
Let us now consider the case where there are many threads (say 100)
contending for a lock repeatedly . In this case, if one thread acquires
the lock and is preempted before releasing it, the other 99 wi ll each call
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
12 }
Figure 28.7: Lock With T est-and-set And Yield
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 341

LOCKS 305
lock(), ﬁnd the lock held, and yield the CPU. Assuming some kind
of round-robin scheduler, each of the 99 will execute this ru n-and-yield
pattern before the thread holding the lock gets to run again. While better
than our spinning approach (which would waste 99 time slices spinning),
this approach is still costly; the cost of a context switch ca n be substantial,
and there is thus plenty of waste.
Worse, we have not tackled the starvation problem at all. A th read
may get caught in an endless yield loop while other threads re peatedly
enter and exit the critical section. We clearly will need an a pproach that
addresses this problem directly .
28.14 Using Queues: Sleeping Instead Of Spinning
The real problem with our previous approaches is that they le ave too
much to chance. The scheduler determines which thread runs n ext; if
the scheduler makes a bad choice, a thread runs that must eith er spin
waiting for the lock (our ﬁrst approach), or yield the CPU imm ediately
(our second approach). Either way , there is potential for wa ste and no
prevention of starvation.
Thus, we must explicitly exert some control over who gets to a cquire
the lock next after the current holder releases it. To do this , we will need a
little more OS support, as well as a queue to keep track of whic h threads
are waiting to enter the lock.
For simplicity , we will use the support provided by Solaris, in terms of
two calls: park() to put a calling thread to sleep, and unpark(threadID)
to wake a particular thread as designated by threadID. These two rou-
tines can be used in tandem to build a lock that puts a caller to sleep if it
tries to acquire a held lock and wakes it when the lock is free. Let’s look at
the code in Figure 28.8 to understand one possible use of such primitives.
We do a couple of interesting things in this example. First, we combine
the old test-and-set idea with an explicit queue of lock wait ers to make a
more efﬁcient lock. Second, we use a queue to help control who gets the
lock next and thus avoid starvation.
You might notice how the guard is used, basically as a spin-lock around
the ﬂag and queue manipulations the lock is using. This appro ach thus
doesn’t avoid spin-waiting entirely; a thread might be inte rrupted while
acquiring or releasing the lock, and thus cause other thread s to spin-wait
for this one to run again. However, the time spent spinning is quite lim-
ited (just a few instructions inside the lock and unlock code, instead of the
user-deﬁned critical section), and thus this approach may b e reasonable.
Second, you might notice that in lock(), when a thread can not ac-
quire the lock (it is already held), we are careful to add ours elves to a
queue (by calling the gettid() call to get the thread ID of the current
thread), set guard to 0, and yield the CPU. A question for the r eader:
What would happen if the release of the guard lock cameafter the park(),
and not before? Hint: something bad.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 342

306 LOCKS
1 typedef struct __lock_t {
2 int flag;
3 int guard;
4 queue_t *q;
5 } lock_t;
6
7 void lock_init(lock_t *m) {
8 m->flag = 0;
9 m->guard = 0;
10 queue_init(m->q);
11 }
12
13 void lock(lock_t *m) {
14 while (TestAndSet(&m->guard, 1) == 1)
15 ; //acquire guard lock by spinning
16 if (m->flag == 0) {
17 m->flag = 1; // lock is acquired
18 m->guard = 0;
19 } else {
20 queue_add(m->q, gettid());
21 m->guard = 0;
22 park();
23 }
24 }
25
26 void unlock(lock_t *m) {
27 while (TestAndSet(&m->guard, 1) == 1)
28 ; //acquire guard lock by spinning
29 if (queue_empty(m->q))
30 m->flag = 0; // let go of lock; no one wants it
31 else
32 unpark(queue_remove(m->q)); // hold lock (for next thread !)
33 m->guard = 0;
34 }
Figure 28.8: Lock With Queues, T est-and-set, Yield, And Wakeup
You might also notice the interesting fact that the ﬂag does n ot get set
back to 0 when another thread gets woken up. Why is this? Well, it is not
an error, but rather a necessity! When a thread is woken up, it will be as
if it is returning from park(); however, it does not hold the guard at that
point in the code and thus cannot even try to set the ﬂag to 1. Th us, we
just pass the lock directly from the thread releasing the loc k to the next
thread acquiring it; ﬂag is not set to 0 in-between.
Finally , you might notice the perceived race condition in th e solution,
just before the call to park(). With just the wrong timing, a thread will
be about to park, assuming that it should sleep until the lock is no longer
held. A switch at that time to another thread (say , a thread ho lding the
lock) could lead to trouble, for example, if that thread then released the
lock. The subsequent park by the ﬁrst thread would then sleep forever
(potentially). This problem is sometimes called the wakeup/waiting race;
to avoid it, we need to do some extra work.
Solaris solves this problem by adding a third system call: setpark().
By calling this routine, a thread can indicate it is about to park. If it then
happens to be interrupted and another thread calls unpark be fore park is
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 343

LOCKS 307
actually called, the subsequent park returns immediately instead of sleep-
ing. The code modiﬁcation, inside of lock(), is quite small:
1 queue_add(m->q, gettid());
2 setpark(); // new code
3 m->guard = 0;
A different solution could pass the guard into the kernel. In that case,
the kernel could take precautions to atomically release the lock and de-
queue the running thread.
28.15 Different OS, Different Support
We have thus far seen one type of support that an OS can provide in
order to build a more efﬁcient lock in a thread library . Other OS’s provide
similar support; the details vary .
For example, Linux provides something called a futex which is simi-
lar to the Solaris interface but provides a bit more in-kerne l functionality .
Speciﬁcally , each futex has associated with it a speciﬁc phy sical mem-
ory location; associated with each such memory location is a n in-kernel
queue. Callers can use futex calls (described below) to slee p and wake as
need be.
Speciﬁcally , two calls are available. The call tofutex wait(address,
expected) puts the calling thread to sleep, assuming the value ataddress
is equal to expected. If it is not equal, the call returns immediately . The
call to the routine futex wake(address) wakes one thread that is wait-
ing on the queue. The usage of these in Linux is as found in 28.9.
This code snippet from lowlevellock.h in the nptl library (part of
the gnu libc library) [L09] is pretty interesting. Basicall y , it uses a single
integer to track both whether the lock is held or not (the high bit of the
integer) and the number of waiters on the lock (all the other b its). Thus,
if the lock is negative, it is held (because the high bit is set and that bit
determines the sign of the integer). The code is also interes ting because it
shows how to optimize for the common case where there is no contention:
with only one thread acquiring and releasing a lock, very lit tle work is
done (the atomic bit test-and-set to lock and an atomic add to release the
lock). See if you can puzzle through the rest of this “real-wo rld” lock to
see how it works.
28.16 Two-Phase Locks
One ﬁnal note: the Linux approach has the ﬂavor of an old appro ach
that has been used on and off for years, going at least as far ba ck to Dahm
Locks in the early 1960’s [M82], and is now referred to as a two-phase
lock. A two-phase lock realizes that spinning can be useful, part icularly
if the lock is about to be released. So in the ﬁrst phase, the lo ck spins for
a while, hoping that it can acquire the lock.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 344

308 LOCKS
1 void mutex_lock (int *mutex) {
2 int v;
3 /* Bit 31 was clear, we got the mutex (this is the fastpath) */
4 if (atomic_bit_test_set (mutex, 31) == 0)
5 return;
6 atomic_increment (mutex);
7 while (1) {
8 if (atomic_bit_test_set (mutex, 31) == 0) {
9 atomic_decrement (mutex);
10 return;
11 }
12 /* We have to wait now. First make sure the futex value
13 we are monitoring is truly negative (i.e. locked). */
14 v = *mutex;
15 if (v >= 0)
16 continue;
17 futex_wait (mutex, v);
18 }
19 }
20
21 void mutex_unlock (int *mutex) {
22 /* Adding 0x80000000 to the counter results in 0 if and only if
23 there are not other interested threads */
24 if (atomic_add_zero (mutex, 0x80000000))
25 return;
26
27 /* There are other threads waiting for this mutex,
28 wake one of them up. */
29 futex_wake (mutex);
Figure 28.9: Linux-based Futex Locks
However, if the lock is not acquired during the ﬁrst spin phas e, a sec-
ond phase is entered, where the caller is put to sleep, and onl y woken up
when the lock becomes free later. The Linux lock above is a for m of such
a lock, but it only spins once; a generalization of this could spin in a loop
for a ﬁxed amount of time before using futex support to sleep.
Two-phase locks are yet another instance of a hybrid approach, where
combining two good ideas may indeed yield a better one. Of cou rse,
whether it does depends strongly on many things, including t he hard-
ware environment, number of threads, and other workload det ails. As
always, making a single general-purpose lock, good for all p ossible use
cases, is quite a challenge.
28.17 Summary
The above approach shows how real locks are built these days: some
hardware support (in the form of a more powerful instruction ) plus some
operating system support (e.g., in the form of park() and unpark()
primitives on Solaris, or futex on Linux). Of course, the details differ, and
the exact code to perform such locking is usually highly tune d. Check
out the Solaris or Linux open source code bases if you want to s ee more
details; they are a fascinating read [L09, S09].
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 345

LOCKS 309
References
[D91] “Just Win, Baby: Al Davis and His Raiders”
Glenn Dickey , Harcourt 1991
There is even an undoubtedly bad book about Al Davis and his famous “just win” quote. Or, we suppose,
the book is more about Al Davis and the Raiders, and maybe not j ust the quote. Read the book to ﬁnd
out?
[D68] “Cooperating sequential processes”
Edsger W. Dijkstra, 1968
Available: http://www.cs.utexas.edu/users/EWD/ewd01xx/EWD123.PDF
One of the early seminal papers in the area. Discusses how Dij kstra posed the original concurrency
problem, and Dekker’s solution.
[H93] “MIPS R4000 Microprocessor User’s Manual”.
Joe Heinrich, Prentice-Hall, June 1993
Available: http://cag.csail.mit.edu/raw/
documents/R4400
Uman book Ed2.pdf
[H91] “Wait-free Synchronization”
Maurice Herlihy
ACM Transactions on Programming Languages and Systems (TOP LAS)
V olume 13, Issue 1, January 1991
A landmark paper introducing a different approach to buildi ng concurrent data structures. However,
because of the complexity involved, many of these ideas have been slow to gain acceptance in deployed
systems.
[L81] “Observations on the Development of an Operating Syst em”
Hugh Lauer
SOSP ’81
A must-read retrospective about the development of the Pilo t OS, an early PC operating system. Fun
and full of insights.
[L09] “glibc 2.9 (include Linux pthreads implementation)”
Available: http://ftp.gnu.org/gnu/glibc/
In particular, take a look at the nptl subdirectory where you will ﬁnd most of the pthread support in
Linux today.
[M82] “The Architecture of the Burroughs B5000
20 Years Later and Still Ahead of the Times?”
Alastair J.W. Mayer, 1982
www.ajwm.net/amayer/papers/B5000.html
From the paper: “One particularly useful instruction is the RDLK (read-lock). It is an indivisible
operation which reads from and writes into a memory location .” RDLK is thus an early test-and-set
primitive, if not the earliest. Some credit here goes to an en gineer named Dave Dahm, who apparently
invented a number of these things for the Burroughs systems, including a form of spin locks (called
“Buzz Locks” as well as a two-phase lock eponymously called “ Dahm Locks.”)
[MS91] “Algorithms for Scalable Synchronization on Shared -Memory Multiprocessors”
John M. Mellor-Crummey and M. L. Scott
ACM TOCS, February 1991
An excellent survey on different locking algorithms. Howev er, no OS support is used, just fancy hard-
ware instructions.
[P81] “Myths About the Mutual Exclusion Problem”
G.L. Peterson
Information Processing Letters. 12(3) 1981, 115–116
Peterson’s algorithm introduced here.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 346

310 LOCKS
[S05] “Guide to porting from Solaris to Linux on x86”
Ajay Sood, April 29, 2005
Available: http://www.ibm.com/developerworks/linux/library/l-s olar/
[S09] “OpenSolaris Thread Library”
Available: http://src.opensolaris.org/source/xref/onnv/onnv-gate/
usr/src/lib/libc/port/threads/synch.c
This is also pretty interesting to look at, though who knows w hat will happen to it now that Oracle owns
Sun. Thanks to Mike Swift for the pointer to the code.
[W09] “Load-Link, Store-Conditional”
Wikipedia entry on said topic, as of October 22, 2009
http://en.wikipedia.org/wiki/Load-Link/Store-Condit ional
Can you believe we referenced wikipedia? Pretty shabby. But , we found the information there ﬁrst,
and it felt wrong not to cite it. Further, they even listed the instructions for the different architec-
tures: ldl
l/stl c and ldq l/stq c (Alpha), lwarx/stwcx (PowerPC), ll/sc (MIPS), and
ldrex/strex (ARM version 6 and above).
[WG00] “The SPARC Architecture Manual: V ersion 9”
David L. Weaver and Tom Germond, September 2000
SPARC International, San Jose, California
Available: http://www.sparc.org/standards/SPARCV9.pdf
Also see: http://developers.sun.com/solaris/articles/atomic
sparc/ for some
more details on Sparc atomic operations.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 347

29
Lock-based Concurrent Data Structures
Before moving beyond locks, we’ll ﬁrst describe how to use lo cks in some
common data structures. Adding locks to a data structure to m ake it us-
able by threads makes the structure thread safe. Of course, exactly how
such locks are added determines both the correctness and per formance of
the data structure. And thus, our challenge:
CRUX : H OW TO ADD LOCKS TO DATA STRUCTURES
When given a particular data structure, how should we add loc ks to
it, in order to make it work correctly? Further, how do we add l ocks such
that the data structure yields high performance, enabling m any threads
to access the structure at once, i.e., concurrently?
Of course, we will be hard pressed to cover all data structure s or all
methods for adding concurrency , as this is a topic that has be en studied
for years, with (literally) thousands of research papers pu blished about
it. Thus, we hope to provide a sufﬁcient introduction to the t ype of think-
ing required, and refer you to some good sources of material f or further
inquiry on your own. We found Moir and Shavit’s survey to be a g reat
source of information [MS04].
29.1 Concurrent Counters
One of the simplest data structures is a counter. It is a struc ture that
is commonly used and has a simple interface. We deﬁne a simple non-
concurrent counter in Figure 29.1.
Simple But Not Scalable
As you can see, the non-synchronized counter is a trivial dat a structure,
requiring a tiny amount of code to implement. We now have our n ext
challenge: how can we make this code thread safe ? Figure
29.2 shows
how we do so.
311

## Page 348

312 L OCK -BASED CONCURRENT DATA STRUCTURES
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
Figure 29.1: A Counter Without Locks
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
16
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
Figure 29.2: A Counter With Locks
This concurrent counter is simple and works correctly . In fa ct, it fol-
lows a design pattern common to the simplest and most basic co ncurrent
data structures: it simply adds a single lock, which is acqui red when call-
ing a routine that manipulates the data structure, and is rel eased when
returning from the call. In this manner, it is similar to a dat a structure
built with monitors [BH73], where locks are acquired and released auto-
matically as you call and return from object methods.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 349

LOCK -BASED CONCURRENT DATA STRUCTURES 313
1 2 3 4
0
5
10
15
Threads
Time (seconds)
Precise
Sloppy
Figure 29.3: Performance of T raditional vs. Sloppy Counters
At this point, you have a working concurrent data structure. The prob-
lem you might have is performance. If your data structure is t oo slow ,
you’ll have to do more than just add a single lock; such optimi zations, if
needed, are thus the topic of the rest of the chapter. Note tha t if the data
structure is not too slow , you are done! No need to do something fancy if
something simple will work.
To understand the performance costs of the simple approach, we run a
benchmark in which each thread updates a single shared count er a ﬁxed
number of times; we then vary the number of threads. Figure 29.3 shows
the total time taken, with one to four threads active; each th read updates
the counter one million times. This experiment was run upon a n iMac
with four Intel 2.7 GHz i5 CPUs; with more CPUs active, we hope to get
more total work done per unit time.
From the top line in the ﬁgure (labeled precise), you can see that the
performance of the synchronized counter scales poorly . Whereas a single
thread can complete the million counter updates in a tiny amo unt of time
(roughly 0.03 seconds), having two threads each update the c ounter one
million times concurrently leads to a massive slowdown (tak ing over 5
seconds!). It only gets worse with more threads.
Ideally , you’d like to see the threads complete just as quick ly on mul-
tiple processors as the single thread does on one. Achieving this end is
called perfect scaling; even though more work is done, it is done in par-
allel, and hence the time taken to complete the task is not inc reased.
Scalable Counting
Amazingly , researchers have studied how to build more scala ble coun-
ters for years [MS04]. Even more amazing is the fact that scal able coun-
ters matter, as recent work in operating system performance analysis has
shown [B+10]; without scalable counting, some workloads ru nning on
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 350

314 L OCK -BASED CONCURRENT DATA STRUCTURES
Time L1 L2 L3 L4 G
0 0 0 0 0 0
1 0 0 1 1 0
2 1 0 2 1 0
3 2 0 3 1 0
4 3 0 3 2 0
5 4 1 3 3 0
6 5 → 0 1 3 4 5 (from L1)
7 0 2 4 5 → 0 10 (from L4)
Table 29.1: T racing the Sloppy Counters
Linux suffer from serious scalability problems on multicor e machines.
Though many techniques have been developed to attack this pr oblem,
we’ll now describe one particular approach. The idea, intro duced in re-
cent research [B+10], is known as a sloppy counter.
The sloppy counter works by representing a single logical co unter via
numerous local physical counters, one per CPU core, as well as a single
global counter. Speciﬁcally , on a machine with four CPUs, there are four
local counters and one global one. In addition to these count ers, there are
also locks: one for each local counter, and one for the global counter.
The basic idea of sloppy counting is as follows. When a thread running
on a given core wishes to increment the counter, it increment s its local
counter; access to this local counter is synchronized via the corresponding
local lock. Because each CPU has its own local counter, threa ds across
CPUs can update local counters without contention, and thus counter
updates are scalable.
However, to keep the global counter up to date (in case a thread wishes
to read its value), the local values are periodically transferred to the global
counter, by acquiring the global lock and incrementing it by the local
counter’s value; the local counter is then reset to zero.
How often this local-to-global transfer occurs is determined by a thresh-
old, which we call S here (for sloppiness). The smaller S is, the more the
counter behaves like the non-scalable counter above; the bi gger S is, the
more scalable the counter, but the further off the global val ue might be
from the actual count. One could simply acquire all the local locks and
the global lock (in a speciﬁed order, to avoid deadlock) to ge t an exact
value, but that is not scalable.
To make this clear, let’s look at an example (Table 29.1). In this exam-
ple, the threshold S is set to 5, and there are threads on each of four CPUs
updating their local counters L1 ... L4. The global counter value ( G) is
also shown in the trace, with time increasing downward. At ea ch time
step, a local counter may be incremented; if the local value r eaches the
threshold S, the local value is transferred to the global counter and the
local counter is reset.
The lower line in Figure 29.3 (labeled sloppy) shows the performance of
sloppy counters with a threshold S of 1024. Performance is excellent; the
time taken to update the counter four million times on four pr ocessors is
hardly higher than the time taken to update it one million tim es on one
processor.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 351

LOCK -BASED CONCURRENT DATA STRUCTURES 315
1 typedef struct __counter_t {
2 int global; // global count
3 pthread_mutex_t glock; // global lock
4 int local[NUMCPUS]; // local count (per cpu)
5 pthread_mutex_t llock[NUMCPUS]; // ... and locks
6 int threshold; // update frequency
7 } counter_t;
8
9 // init: record threshold, init locks, init values
10 // of all local counts and global count
11 void init(counter_t *c, int threshold) {
12 c->threshold = threshold;
13
14 c->global = 0;
15 pthread_mutex_init(&c->glock, NULL);
16
17 int i;
18 for (i = 0; i < NUMCPUS; i++) {
19 c->local[i] = 0;
20 pthread_mutex_init(&c->llock[i], NULL);
21 }
22 }
23
24 // update: usually, just grab local lock and update local amo unt
25 // once local count has risen by ’threshold’, grab global
26 // lock and transfer local values to it
27 void update(counter_t *c, int threadID, int amt) {
28 pthread_mutex_lock(&c->llock[threadID]);
29 c->local[threadID] += amt; // assumes amt > 0
30 if (c->local[threadID] >= c->threshold) { // transfer to gl obal
31 pthread_mutex_lock(&c->glock);
32 c->global += c->local[threadID];
33 pthread_mutex_unlock(&c->glock);
34 c->local[threadID] = 0;
35 }
36 pthread_mutex_unlock(&c->llock[threadID]);
37 }
38
39 // get: just return global amount (which may not be perfect)
40 int get(counter_t *c) {
41 pthread_mutex_lock(&c->glock);
42 int val = c->global;
43 pthread_mutex_unlock(&c->glock);
44 return val; // only approximate!
45 }
Figure 29.4: Sloppy Counter Implementation
Figure
29.5 shows the importance of the threshold value S, with four
threads each incrementing the counter 1 million times on fou r CPUs. If S
is low , performance is poor (but the global count is always quite accurate);
if S is high, performance is excellent, but the global count lags (by the
number of CPUs multiplied by S). This accuracy/performance trade-off
is what sloppy counters enables.
A rough version of such a sloppy counter is found in Figure 29.4. Read
it, or better yet, run it yourself in some experiments to bett er understand
how it works.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 352

316 L OCK -BASED CONCURRENT DATA STRUCTURES
1 2 4 8 16 32 64 128 256 1024 512
0
5
10
15
Sloppiness
Time (seconds)
Figure 29.5: Scaling Sloppy Counters
29.2 Concurrent Linked Lists
We next examine a more complicated structure, the linked lis t. Let’s
start with a basic approach once again. For simplicity , we’l l omit some of
the obvious routines that such a list would have and just focu s on concur-
rent insert; we’ll leave it to the reader to think about looku p, delete, and
so forth. Figure 29.6 shows the code for this rudimentary data structure.
As you can see in the code, the code simply acquires a lock in the insert
routine upon entry , and releases it upon exit. One small tricky issue arises
if malloc() happens to fail (a rare case); in this case, the code must also
release the lock before failing the insert.
This kind of exceptional control ﬂow has been shown to be quit e error
prone; a recent study of Linux kernel patches found that a huge fraction of
bugs (nearly 40%) are found on such rarely-taken code paths (indeed, this
observation sparked some of our own research, in which we rem oved all
memory-failing paths from a Linux ﬁle system, resulting in a more robust
system [S+11]).
Thus, a challenge: can we rewrite the insert and lookup routi nes to re-
main correct under concurrent insert but avoid the case wher e the failure
path also requires us to add the call to unlock?
The answer, in this case, is yes. Speciﬁcally , we can rearrange the code
a bit so that the lock and release only surround the actual cri tical section
in the insert code, and that a common exit path is used in the lookup code.
The former works because part of the lookup actually need not be locked;
assuming that malloc() itself is thread-safe, each thread can call into it
without worry of race conditions or other concurrency bugs. Only when
updating the shared list does a lock need to be held. See Figur e 29.7 for
the details of these modiﬁcations.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 353

LOCK -BASED CONCURRENT DATA STRUCTURES 317
1 // basic node structure
2 typedef struct __node_t {
3 int key;
4 struct __node_t *next;
5 } node_t;
6
7 // basic list structure (one used per list)
8 typedef struct __list_t {
9 node_t *head;
10 pthread_mutex_t lock;
11 } list_t;
12
13 void List_Init(list_t *L) {
14 L->head = NULL;
15 pthread_mutex_init(&L->lock, NULL);
16 }
17
18 int List_Insert(list_t *L, int key) {
19 pthread_mutex_lock(&L->lock);
20 node_t *new = malloc(sizeof(node_t));
21 if (new == NULL) {
22 perror("malloc");
23 pthread_mutex_unlock(&L->lock);
24 return -1; // fail
25 }
26 new->key = key;
27 new->next = L->head;
28 L->head = new;
29 pthread_mutex_unlock(&L->lock);
30 return 0; // success
31 }
32
33 int List_Lookup(list_t *L, int key) {
34 pthread_mutex_lock(&L->lock);
35 node_t *curr = L->head;
36 while (curr) {
37 if (curr->key == key) {
38 pthread_mutex_unlock(&L->lock);
39 return 0; // success
40 }
41 curr = curr->next;
42 }
43 pthread_mutex_unlock(&L->lock);
44 return -1; // failure
45 }
Figure 29.6: Concurrent Linked List
As for the lookup routine, it is a simple code transformation to jump
out of the main search loop to a single return path. Doing so ag ain re-
duces the number of lock acquire/release points in the code, and thus
decreases the chances of accidentally introducing bugs (su ch as forget-
ting to unlock before returning) into the code.
Scaling Linked Lists
Though we again have a basic concurrent linked list, once aga in we
are in a situation where it does not scale particularly well. One technique
that researchers have explored to enable more concurrency within a list is
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 354

318 L OCK -BASED CONCURRENT DATA STRUCTURES
1 void List_Init(list_t *L) {
2 L->head = NULL;
3 pthread_mutex_init(&L->lock, NULL);
4 }
5
6 void List_Insert(list_t *L, int key) {
7 // synchronization not needed
8 node_t *new = malloc(sizeof(node_t));
9 if (new == NULL) {
10 perror("malloc");
11 return;
12 }
13 new->key = key;
14
15 // just lock critical section
16 pthread_mutex_lock(&L->lock);
17 new->next = L->head;
18 L->head = new;
19 pthread_mutex_unlock(&L->lock);
20 }
21
22 int List_Lookup(list_t *L, int key) {
23 int rv = -1;
24 pthread_mutex_lock(&L->lock);
25 node_t *curr = L->head;
26 while (curr) {
27 if (curr->key == key) {
28 rv = 0;
29 break;
30 }
31 curr = curr->next;
32 }
33 pthread_mutex_unlock(&L->lock);
34 return rv; // now both success and failure
35 }
Figure 29.7: Concurrent Linked List: Rewritten
something called hand-over-hand locking (a.k.a. lock coupling) [MS04].
The idea is pretty simple. Instead of having a single lock for the entire
list, you instead add a lock per node of the list. When travers ing the
list, the code ﬁrst grabs the next node’s lock and then releas es the current
node’s lock (which inspires the name hand-over-hand).
Conceptually , a hand-over-hand linked list makes some sens e; it en-
ables a high degree of concurrency in list operations. Howev er, in prac-
tice, it is hard to make such a structure faster than the simpl e single lock
approach, as the overheads of acquiring and releasing locks for each node
of a list traversal is prohibitive. Even with very large list s, and a large
number of threads, the concurrency enabled by allowing mult iple on-
going traversals is unlikely to be faster than simply grabbi ng a single
lock, performing an operation, and releasing it. Perhaps so me kind of hy-
brid (where you grab a new lock every so many nodes) would be wo rth
investigating.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 355

LOCK -BASED CONCURRENT DATA STRUCTURES 319
TIP : M ORE CONCURRENCY ISN ’ T NECESSARILY FASTER
If the scheme you design adds a lot of overhead (for example, b y acquir-
ing and releasing locks frequently , instead of once), the fact that it is more
concurrent may not be important. Simple schemes tend to work well,
especially if they use costly routines rarely . Adding more l ocks and com-
plexity can be your downfall. All of that said, there is one wa y to really
know: build both alternatives (simple but less concurrent, and complex
but more concurrent) and measure how they do. In the end, you c an’t
cheat on performance; your idea is either faster, or it isn’t .
TIP : B E WARY OF LOCKS AND CONTROL FLOW
A general design tip, which is useful in concurrent code as we ll as
elsewhere, is to be wary of control ﬂow changes that lead to fu nction re-
turns, exits, or other similar error conditions that halt th e execution of
a function. Because many functions will begin by acquiring a lock, al-
locating some memory , or doing other similar stateful opera tions, when
errors arise, the code has to undo all of the state before retu rning, which
is error-prone. Thus, it is best to structure code to minimiz e this pattern.
29.3 Concurrent Queues
As you know by now , there is always a standard method to make a
concurrent data structure: add a big lock. For a queue, we’ll skip that
approach, assuming you can ﬁgure it out.
Instead, we’ll take a look at a slightly more concurrent queu e designed
by Michael and Scott [MS98]. The data structures and code use d for this
queue are found in Figure 29.8 on the following page.
If you study this code carefully , you’ll notice that there ar e two locks,
one for the head of the queue, and one for the tail. The goal of t hese two
locks is to enable concurrency of enqueue and dequeue operat ions. In
the common case, the enqueue routine will only access the tai l lock, and
dequeue only the head lock.
One trick used by the Michael and Scott is to add a dummy node (a llo-
cated in the queue initialization code); this dummy enables the separation
of head and tail operations. Study the code, or better yet, ty pe it in, run
it, and measure it, to understand how it works deeply .
Queues are commonly used in multi-threaded applications. H owever,
the type of queue used here (with just locks) often does not co mpletely
meet the needs of such programs. A more fully developed bound ed
queue, that enables a thread to wait if the queue is either emp ty or overly
full, is the subject of our intense study in the next chapter o n condition
variables. Watch for it!
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 356

320 L OCK -BASED CONCURRENT DATA STRUCTURES
1 typedef struct __node_t {
2 int value;
3 struct __node_t *next;
4 } node_t;
5
6 typedef struct __queue_t {
7 node_t *head;
8 node_t *tail;
9 pthread_mutex_t headLock;
10 pthread_mutex_t tailLock;
11 } queue_t;
12
13 void Queue_Init(queue_t *q) {
14 node_t *tmp = malloc(sizeof(node_t));
15 tmp->next = NULL;
16 q->head = q->tail = tmp;
17 pthread_mutex_init(&q->headLock, NULL);
18 pthread_mutex_init(&q->tailLock, NULL);
19 }
20
21 void Queue_Enqueue(queue_t *q, int value) {
22 node_t *tmp = malloc(sizeof(node_t));
23 assert(tmp != NULL);
24 tmp->value = value;
25 tmp->next = NULL;
26
27 pthread_mutex_lock(&q->tailLock);
28 q->tail->next = tmp;
29 q->tail = tmp;
30 pthread_mutex_unlock(&q->tailLock);
31 }
32
33 int Queue_Dequeue(queue_t *q, int *value) {
34 pthread_mutex_lock(&q->headLock);
35 node_t *tmp = q->head;
36 node_t *newHead = tmp->next;
37 if (newHead == NULL) {
38 pthread_mutex_unlock(&q->headLock);
39 return -1; // queue was empty
40 }
41 *value = newHead->value;
42 q->head = newHead;
43 pthread_mutex_unlock(&q->headLock);
44 free(tmp);
45 return 0;
46 }
Figure 29.8: Michael and Scott Concurrent Queue
29.4 Concurrent Hash Table
We end our discussion with a simple and widely applicable concurrent
data structure, the hash table. We’ll focus on a simple hash t able that does
not resize; a little more work is required to handle resizing , which we
leave as an exercise for the reader (sorry!).
This concurrent hash table is straightforward, is built usi ng the con-
current lists we developed earlier, and works incredibly we ll. The reason
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 357

LOCK -BASED CONCURRENT DATA STRUCTURES 321
1 #define BUCKETS (101)
2
3 typedef struct __hash_t {
4 list_t lists[BUCKETS];
5 } hash_t;
6
7 void Hash_Init(hash_t *H) {
8 int i;
9 for (i = 0; i < BUCKETS; i++) {
10 List_Init(&H->lists[i]);
11 }
12 }
13
14 int Hash_Insert(hash_t *H, int key) {
15 int bucket = key % BUCKETS;
16 return List_Insert(&H->lists[bucket], key);
17 }
18
19 int Hash_Lookup(hash_t *H, int key) {
20 int bucket = key % BUCKETS;
21 return List_Lookup(&H->lists[bucket], key);
22 }
Figure 29.9: A Concurrent Hash T able
for its good performance is that instead of having a single lo ck for the en-
tire structure, it uses a lock per hash bucket (each of which i s represented
by a list). Doing so enables many concurrent operations to ta ke place.
Figure
29.10 shows the performance of the hash table under concur-
rent updates (from 10,000 to 50,000 concurrent updates from each of four
threads, on the same iMac with four CPUs). Also shown, for the sake
of comparison, is the performance of a linked list (with a sin gle lock).
As you can see from the graph, this simple concurrent hash tab le scales
magniﬁcently; the linked list, in contrast, does not.
0 10 20 30 40
0
5
10
15
Inserts (Thousands)
Time (seconds)
Simple Concurrent List
Concurrent Hash Table
Figure 29.10: Scaling Hash T ables
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 358

322 L OCK -BASED CONCURRENT DATA STRUCTURES
TIP : A VOID PREMATURE OPTIMIZATION (K NUTH ’ S LAW)
When building a concurrent data structure, start with the mo st basic ap-
proach, which is to add a single big lock to provide synchroni zed access.
By doing so, you are likely to build a correct lock; if you then ﬁnd that it
suffers from performance problems, you can reﬁne it, thus on ly making
it fast if need be. As Knuth famously stated, “Premature optimization is
the root of all evil.”
Many operating systems added a single lock when transitioni ng to multi-
processors, including Sun OS and Linux. In the latter, it eve n had a name,
the big kernel lock (BKL), and was the source of performance problems
for many years until it was ﬁnally removed in 2011. In SunOS (w hich
was a BSD variant), the notion of removing the single lock pro tecting
the kernel was so painful that the Sun engineers decided on a d ifferent
route: building the entirely new Solaris operating system, which was
multi-threaded from day one. Read the Linux and Solaris kern el books
for more information [BC05, MM00].
29.5 Summary
We have introduced a sampling of concurrent data structures , from
counters, to lists and queues, and ﬁnally to the ubiquitous a nd heavily-
used hash table. We have learned a few important lessons alon g the way:
to be careful with acquisition and release of locks around co ntrol ﬂow
changes; that enabling more concurrency does not necessari ly increase
performance; that performance problems should only be reme died once
they exist. This last point, of avoiding premature optimization , is cen-
tral to any performance-minded developer; there is no value in making
something faster if doing so will not improve the overall per formance of
the application.
Of course, we have just scratched the surface of high perform ance
structures. See Moir and Shavit’s excellent survey for more information,
as well as links to other sources [MS04]. In particular, you m ight be inter-
ested in other structures (such as B-trees); for this knowle dge, a database
class is your best bet. You also might be interested in techniques that don’t
use traditional locks at all; such non-blocking data structures are some-
thing we’ll get a taste of in the chapter on common concurrenc y bugs,
but frankly this topic is an entire area of knowledge requiri ng more study
than is possible in this humble book. Find out more on your own if you
are interested (as always!).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 359

LOCK -BASED CONCURRENT DATA STRUCTURES 323
References
[B+10] “An Analysis of Linux Scalability to Many Cores”
Silas Boyd-Wickizer, Austin T. Clements, Yandong Mao, Aleksey Pesterev , M. Frans Kaashoek,
Robert Morris, Nickolai Zeldovich
OSDI ’10, Vancouver, Canada, October 2010
A great study of how Linux performs on multicore machines, as well as some simple solutions.
[BH73] “Operating System Principles”
Per Brinch Hansen, Prentice-Hall, 1973
Available: http://portal.acm.org/citation.cfm?id=540365
One of the ﬁrst books on operating systems; certainly ahead o f its time. Introduced monitors as a
concurrency primitive.
[BC05] “Understanding the Linux Kernel (Third Edition)”
Daniel P . Bovet and Marco Cesati
O’Reilly Media, November 2005
The classic book on the Linux kernel. Y ou should read it.
[L+13] “A Study of Linux File System Evolution”
Lanyue Lu, Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusse au, Shan Lu
FAST ’13, San Jose, CA, February 2013
Our paper that studies every patch to Linux ﬁle systems over n early a decade. Lots of fun ﬁndings in
there; read it to see! The work was painful to do though; the po or graduate student, Lanyue Lu, had to
look through every single patch by hand in order to understan d what they did.
[MS98] “Nonblocking Algorithms and Preemption-safe Locking on Multiprogrammed Shared-
memory Multiprocessors”
M. Michael and M. Scott
Journal of Parallel and Distributed Computing, V ol. 51, No. 1, 1998
Professor Scott and his students have been at the forefront o f concurrent algorithms and data structures
for many years; check out his web page, numerous papers, or bo oks to ﬁnd out more.
[MS04] “Concurrent Data Structures”
Mark Moir and Nir Shavit
In Handbook of Data Structures and Applications
(Editors D. Metha and S.Sahni)
Chapman and Hall/CRC Press, 2004
Available: www.cs.tau.ac.il/˜shanir/concurrent-data-structures.pdf
A short but relatively comprehensive reference on concurre nt data structures. Though it is missing
some of the latest works in the area (due to its age), it remain s an incredibly useful reference.
[MM00] “Solaris Internals: Core Kernel Architecture”
Jim Mauro and Richard McDougall
Prentice Hall, October 2000
The Solaris book. Y ou should also read this, if you want to lea rn in great detail about something other
than Linux.
[S+11] “Making the Common Case the Only Case with Anticipato ry Memory Allocation”
Swaminathan Sundararaman, Yupu Zhang, Sriram Subramanian ,
Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau
FAST ’11, San Jose, CA, February 2011
Our work on removing possibly-failing calls to malloc from k ernel code paths. The idea is to allocate all
potentially needed memory before doing any of the work, thus avoiding failure deep down in the storage
stack.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

