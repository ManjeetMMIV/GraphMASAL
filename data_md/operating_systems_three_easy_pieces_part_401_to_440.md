# Document: operating_systems_three_easy_pieces (Pages 401 to 440)

## Page 401

COMMON CONCURRENCY PROBLEMS 365
Conditions for Deadlock
Four conditions need to hold for a deadlock to occur [C+71]:
• Mutual exclusion: Threads claim exclusive control of resources that
they require (e.g., a thread grabs a lock).
• Hold-and-wait: Threads hold resources allocated to them (e.g., locks
that they have already acquired) while waiting for addition al re-
sources (e.g., locks that they wish to acquire).
• No preemption: Resources (e.g., locks) cannot be forcibly removed
from threads that are holding them.
• Circular wait: There exists a circular chain of threads such that
each thread holds one more resources (e.g., locks) that are b eing
requested by the next thread in the chain.
If any of these four conditions are not met, deadlock cannot o ccur.
Thus, we ﬁrst explore techniques to prevent deadlock; each of these strate-
gies seeks to prevent one of the above conditions from arisin g and thus is
one approach to handling the deadlock problem.
Prevention
Circular Wait
Probably the most practical prevention technique (and cert ainly one that
is used frequently) is to write your locking code such that yo u never in-
duce a circular wait. The way to do that is to provide a total ordering on
lock acquisition. For example, if there are only two locks in the system (L1
and L2), we can prevent deadlock by always acquiring L1 before L2. Such
strict ordering ensures that no cyclical wait arises; hence , no deadlock.
As you can imagine, this approach requires careful design of global
locking strategies and must be done with great care. Further , it is just a
convention, and a sloppy programmer can easily ignore the lo cking pro-
tocol and potentially cause deadlock. Finally , it requires a deep under-
standing of the code base, and how various routines are calle d; just one
mistake could result in the wrong ordering of lock acquisiti on, and hence
deadlock.
Hold-and-wait
The hold-and-wait requirement for deadlock can be avoided by acquiring
all locks at once, atomically . In practice, this could be achieved as follows:
1 lock(prevention);
2 lock(L1);
3 lock(L2);
4 ...
5 unlock(prevention);
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 402

366 COMMON CONCURRENCY PROBLEMS
By ﬁrst grabbing the lock prevention, this code guarantees that no
untimely thread switch can occur in the midst of lock acquisition and thus
deadlock can once again be avoided. Of course, it requires th at any time
any thread grabs a lock, it ﬁrst acquires the global preventi on lock. For
example, if another thread was trying to grab locks L1 and L2 i n a dif-
ferent order, it would be OK, because it would be holding the p revention
lock while doing so.
Note that the solution is problematic for a number of reasons . As be-
fore, encapsulation works against us: this approach requir es us to know
when calling a routine exactly which locks must be held and to acquire
them ahead of time. Further, the approach likely decreases c oncurrency
as all locks must be acquired early on (at once) instead of whe n they are
truly needed.
No Preemption
Because we generally view locks as held until unlock is calle d, multiple
lock acquisition often gets us into trouble because when wai ting for one
lock we are holding another. Many thread libraries provide a more ﬂexi-
ble set of interfaces to help avoid this situation. Speciﬁcally , atrylock()
routine will grab the lock (if it is available) or return -1 in dicating that the
lock is held right now and that you should try again later if yo u want to
grab that lock.
Such an interface could be used as follows to build a deadlock -free,
ordering-robust lock acquisition protocol:
1 top:
2 lock(L1);
3 if (trylock(L2) == -1) {
4 unlock(L1);
5 goto top;
6 }
Note that another thread could follow the same protocol but g rab the
locks in the other order (L2 then L1) and the program would sti ll be dead-
lock free. One new problem does arise, however: livelock. It is possible
(though perhaps unlikely) that two threads could both be rep eatedly at-
tempting this sequence and repeatedly failing to acquire bo th locks. In
this case, both systems are running through this code sequen ce over and
over again (and thus it is not a deadlock), but progress is not being made,
hence the name livelock. There are solutions to the livelock problem, too:
for example, one could add a random delay before looping back and try-
ing the entire thing over again, thus decreasing the odds of r epeated in-
terference among competing threads.
One ﬁnal point about this solution: it skirts around the hard parts of
using a trylock approach. The ﬁrst problem that would likely exist again
arises due to encapsulation: if one of these locks is buried i n some routine
that is getting called, the jump back to the beginning become s more com-
plex to implement. If the code had acquired some resources (o ther than
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 403

COMMON CONCURRENCY PROBLEMS 367
L1) along the way , it must make sure to carefully release them as well;
for example, if after acquiring L1, the code had allocated so me memory ,
it would have to release that memory upon failure to acquire L 2, before
jumping back to the top to try the entire sequence again. Howe ver, in
limited circumstances (e.g., the Java vector method above) , this type of
approach could work well.
Mutual Exclusion
The ﬁnal prevention technique would be to avoid the need for m utual
exclusion at all. In general, we know this is difﬁcult, becau se the code we
wish to run does indeed have critical sections. So what can we do?
Herlihy had the idea that one could design various data struc tures to
be wait-free [H91]. The idea here is simple: using powerful hardware in-
structions, you can build data structures in a manner that does not require
explicit locking.
As a simple example, let us assume we have a compare-and-swap in-
struction, which as you may recall is an atomic instruction p rovided by
the hardware that does the following:
1 int CompareAndSwap(int *address, int expected, int new) {
2 if ( *address == expected) {
3 *address = new;
4 return 1; // success
5 }
6 return 0; // failure
7 }
Imagine we now wanted to atomically increment a value by a cer tain
amount. We could do it as follows:
1 void AtomicIncrement(int *value, int amount) {
2 do {
3 int old = *value;
4 } while (CompareAndSwap(value, old, old + amount) == 0);
5 }
Instead of acquiring a lock, doing the update, and then relea sing it, we
have instead built an approach that repeatedly tries to update the value to
the new amount and uses the compare-and-swap to do so. In this manner,
no lock is acquired, and no deadlock can arise (though livelo ck is still a
possibility).
Let us consider a slightly more complex example: list insert ion. Here
is code that inserts at the head of a list:
1 void insert(int value) {
2 node_t *n = malloc(sizeof(node_t));
3 assert(n != NULL);
4 n->value = value;
5 n->next = head;
6 head = n;
7 }
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 404

368 COMMON CONCURRENCY PROBLEMS
This code performs a simple insertion, but if called by multiple threads
at the “same time”, has a race condition (see if you can ﬁgure out why). Of
course, we could solve this by surrounding this code with a lo ck acquire
and release:
1 void insert(int value) {
2 node_t *n = malloc(sizeof(node_t));
3 assert(n != NULL);
4 n->value = value;
5 lock(listlock); // begin critical section
6 n->next = head;
7 head = n;
8 unlock(listlock); // end of critical section
9 }
In this solution, we are using locks in the traditional manne r1. Instead,
let us try to perform this insertion in a wait-free manner sim ply using the
compare-and-swap instruction. Here is one possible approa ch:
1 void insert(int value) {
2 node_t *n = malloc(sizeof(node_t));
3 assert(n != NULL);
4 n->value = value;
5 do {
6 n->next = head;
7 } while (CompareAndSwap(&head, n->next, n));
8 }
The code here updates the next pointer to point to the current head,
and then tries to swap the newly-created node into position a s the new
head of the list. However, this will fail if some other thread successfully
swapped in a new head in the meanwhile, causing this thread to retry
again with the new head.
Of course, building a useful list requires more than just a li st insert,
and not surprisingly building a list that you can insert into , delete from,
and perform lookups on in a wait-free manner is non-trivial. Read the
rich literature on wait-free synchronization if you ﬁnd thi s interesting.
Deadlock Avoidance via Scheduling
Instead of deadlock prevention, in some scenarios deadlock avoidance
is preferable. A voidance requires some global knowledge of which locks
various threads might grab during their execution, and subsequently sched-
ules said threads in a way as to guarantee no deadlock can occu r.
For example, assume we have two processors and four threads w hich
must be scheduled upon them. Assume further we know that Thre ad
1 (T1) grabs locks L1 and L2 (in some order, at some point durin g its
execution), T2 grabs L1 and L2 as well, T3 grabs just L2, and T4 grabs no
1The astute reader might be asking why we grabbed the lock so la te, instead of right when
entering the insert() routine; can you, astute reader, ﬁgure out why that is likely OK?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 405

COMMON CONCURRENCY PROBLEMS 369
locks at all. We can show these lock acquisition demands of th e threads
in tabular form:
T1 T2 T3 T4
L1 yes yes no no
L2 yes yes yes no
A smart scheduler could thus compute that as long as T1 and T2 a re
not run at the same time, no deadlock could ever arise. Here is one such
schedule:
CPU 1
CPU 2
T1 T2
T3 T4
Note that it is OK for (T3 and T1) or (T3 and T2) to overlap. Even
though T3 grabs lock L2, it can never cause a deadlock by runni ng con-
currently with other threads because it only grabs one lock.
Let’s look at one more example. In this one, there is more cont ention
for the same resources (again, locks L1 and L2), as indicated by the fol-
lowing contention table:
T1 T2 T3 T4
L1 yes yes yes no
L2 yes yes yes no
In particular, threads T1, T2, and T3 all need to grab both loc ks L1 and
L2 at some point during their execution. Here is a possible sc hedule that
guarantees that no deadlock could ever occur:
CPU 1
CPU 2
T1 T2 T3
T4
As you can see, static scheduling leads to a conservative app roach
where T1, T2, and T3 are all run on the same processor, and thus the
total time to complete the jobs is lengthened considerably . Though it may
have been possible to run these tasks concurrently , the fear of deadlock
prevents us from doing so, and the cost is performance.
One famous example of an approach like this is Dijkstra’s Ban ker’s Al-
gorithm [D64], and many similar approaches have been descri bed in the
literature. Unfortunately , they are only useful in very lim ited environ-
ments, for example, in an embedded system where one has full k nowl-
edge of the entire set of tasks that must be run and the locks th at they
need. Further, such approaches can limit concurrency , as we saw in the
second example above. Thus, avoidance of deadlock via sched uling is
not a widely-used general-purpose solution.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 406

370 COMMON CONCURRENCY PROBLEMS
TIP : D ON ’ T ALWAYS DO IT PERFECTLY (T OM WEST ’ S LAW)
Tom West, famous as the subject of the classic computer-industry book
“Soul of a New Machine” [K81], says famously: “Not everythin g worth
doing is worth doing well”, which is a terriﬁc engineering ma xim. If a
bad thing happens rarely , certainly one should not spend a gr eat deal of
effort to prevent it, particularly if the cost of the bad thin g occurring is
small.
Detect and Recover
One ﬁnal general strategy is to allow deadlocks to occasiona lly occur, and
then take some action once such a deadlock has been detected. For exam-
ple, if an OS froze once a year, you would just reboot it and get happily (or
grumpily) on with your work. If deadlocks are rare, such a non -solution
is indeed quite pragmatic.
Many database systems employ deadlock detection and recovery tech-
niques. A deadlock detector runs periodically , building a r esource graph
and checking it for cycles. In the event of a cycle (deadlock) , the system
needs to be restarted. If more intricate repair of data struc tures is ﬁrst
required, a human being may be involved to ease the process.
32.4 Summary
In this chapter, we have studied the types of bugs that occur i n con-
current programs. The ﬁrst type, non-deadlock bugs, are sur prisingly
common, but often are easier to ﬁx. They include atomicity vi olations,
in which a sequence of instructions that should have been exe cuted to-
gether was not, and order violations, in which the needed ord er between
two threads was not enforced.
We have also brieﬂy discussed deadlock: why it occurs, and wh at can
be done about it. The problem is as old as concurrency itself, and many
hundreds of papers have been written about the topic. The bes t solu-
tion in practice is to be careful, develop a lock acquisition total order,
and thus prevent deadlock from occurring in the ﬁrst place. W ait-free
approaches also have promise, as some wait-free data struct ures are now
ﬁnding their way into commonly-used libraries and critical systems, in-
cluding Linux. However, their lack of generality and the com plexity to
develop a new wait-free data structure will likely limit the overall util-
ity of this approach. Perhaps the best solution is to develop new concur-
rent programming models: in systems such as MapReduce (from Google)
[GD02], programmers can describe certain types of parallel computations
without any locks whatsoever. Locks are problematic by thei r very na-
ture; perhaps we should seek to avoid using them unless we tru ly must.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 407

COMMON CONCURRENCY PROBLEMS 371
References
[C+71] “System Deadlocks”
E.G. Coffman, M.J. Elphick, A. Shoshani
ACM Computing Surveys, 3:2, June 1971
The classic paper outlining the conditions for deadlock and how you might go about dealing with it.
There are certainly some earlier papers on this topic; see th e references within this paper for details.
[D64] “Een algorithme ter voorkoming van de dodelijke omarm ing”
Circulated privately , around 1964
Available: http://www.cs.utexas.edu/users/EWD/ewd01xx/EWD108.PDF
Indeed, not only did Dijkstra come up with a number of solutio ns to the deadlock problem, he was the
ﬁrst to note its existence, at least in written form. However , he called it the “deadly embrace”, which
(thankfully) did not catch on.
[GD02] “MapReduce: Simpliﬁed Data Processing on Large Clus ters”
Sanjay Ghemawhat and Jeff Dean
OSDI ’04, San Francisco, CA, October 2004
The MapReduce paper ushered in the era of large-scale data pr ocessing, and proposes a framework for
performing such computations on clusters of generally unre liable machines.
[H91] “Wait-free Synchronization”
Maurice Herlihy
ACM TOPLAS, 13(1), pages 124-149, January 1991
Herlihy’s work pioneers the ideas behind wait-free approac hes to writing concurrent programs. These
approaches tend to be complex and hard, often more difﬁcult than using locks correctly, probably limiting
their success in the real world.
[J+08] “Deadlock Immunity: Enabling Systems To Defend Agai nst Deadlocks”
Horatiu Jula, Daniel Tralamazza, Cristian Zamﬁr, George Ca ndea
OSDI ’08, San Diego, CA, December 2008
An excellent recent paper on deadlocks and how to avoid getti ng caught in the same ones over and over
again in a particular system.
[K81] “Soul of a New Machine”
Tracy Kidder, 1980
A must-read for any systems builder or engineer, detailing t he early days of how a team inside Data
General (DG), led by Tom West, worked to produce a “new machin e.” Kidder’s other book are also
excellent, in particular, “Mountains beyond Mountains”. O r maybe you don’t agree with me, comma?
[L+08] “Learning from Mistakes – A Comprehensive Study on
Real World Concurrency Bug Characteristics”
Shan Lu, Soyeon Park, Eunsoo Seo, Yuanyuan Zhou
ASPLOS ’08, March 2008, Seattle, Washington
The ﬁrst in-depth study of concurrency bugs in real software , and the basis for this chapter. Look at Y.Y.
Zhou’s or Shan Lu’s web pages for many more interesting paper s on bugs.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 409

33
Event-based Concurrency (Advanced)
Thus far, we’ve written about concurrency as if the only way t o build
concurrent applications is to use threads. Like many things in life, this
is not completely true. Speciﬁcally , a different style of co ncurrent pro-
gramming is often used in both GUI-based applications [O96] as well as
some types of internet servers [PDZ99]. This style, known as event-based
concurrency, has become popular in some modern systems, including
server-side frameworks such as node.js [N13], but its roots are found in
C/UNIX systems that we’ll discuss below .
The problem that event-based concurrency addresses is two- fold. The
ﬁrst is that managing concurrency correctly in multi-threa ded applica-
tions can be challenging; as we’ve discussed, missing locks , deadlock,
and other nasty problems can arise. The second is that in a multi-threaded
application, the developer has little or no control over wha t is scheduled
at a given moment in time; rather, the programmer simply creates threads
and then hopes that the underlying OS schedules them in a reas onable
manner across available CPUs. Given the difﬁculty of buildi ng a general-
purpose scheduler that works well in all cases for all worklo ads, some-
times the OS will schedule work in a manner that is less than op timal.
The crux:
THE CRUX :
HOW TO BUILD CONCURRENT SERVERS WITHOUT THREADS
How can we build a concurrent server without using threads, and thus
retain control over concurrency as well as avoid some of the p roblems
that seem to plague multi-threaded applications?
33.1 The Basic Idea: An Event Loop
The basic approach we’ll use, as stated above, is called event-based
concurrency. The approach is quite simple: you simply wait for some-
thing (i.e., an “event”) to occur; when it does, you check wha t type of
373

## Page 410

374 EVENT -BASED CONCURRENCY (A DVANCED )
event it is and do the small amount of work it requires (which m ay in-
clude issuing I/O requests, or scheduling other events for f uture han-
dling, etc.). That’s it!
Before getting into the details, let’s ﬁrst examine what a ca nonical
event-based server looks like. Such applications are based around a sim-
ple construct known as the event loop . Pseudocode for an event loop
looks like this:
while (1) {
events = getEvents();
for (e in events)
processEvent(e);
}
It’s really that simple. The main loop simply waits for somet hing to do
(by calling getEvents() in the code above) and then, for each event re-
turned, processes them, one at a time; the code that processe s each event
is known as an event handler . Importantly , when a handler processes
an event, it is the only activity taking place in the system; t hus, deciding
which event to handle next is equivalent to scheduling. This explicit con-
trol over scheduling is one of the fundamental advantages of the event-
based approach.
But this discussion leaves us with a bigger question: how exa ctly does
an event-based server determine which events are taking pla ce, in par-
ticular with regards to network and disk I/O? Speciﬁcally , h ow can an
event server tell if a message has arrived for it?
33.2 An Important API: select() (or poll())
With that basic event loop in mind, we next must address the qu estion
of how to receive events. In most systems, a basic API is avail able, via
either the select() or poll() system calls.
What these interfaces enable a program to do is simple: check whether
there is any incoming I/O that should be attended to. For exam ple, imag-
ine that a network application (such as a web server) wishes t o check
whether any network packets have arrived, in order to servic e them.
These system calls let you do exactly that.
Take select() for example. The manual page (on Mac OS X) de-
scribes the API in this manner:
int select(int nfds,
fd_set *restrict readfds,
fd_set *restrict writefds,
fd_set *restrict errorfds,
struct timeval *restrict timeout);
The actual description from the man page: select() examines the I/O de-
scriptor sets whose addresses are passed in readfds, writef ds, and errorfds to see
if some of their descriptors are ready for reading, are ready for writing, or have
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 411

EVENT -BASED CONCURRENCY (A DVANCED ) 375
ASIDE : BLOCKING VS . N ON -BLOCKING INTERFACES
Blocking (or synchronous) interfaces do all of their work before returning
to the caller; non-blocking (or asynchronous) interfaces begin some work
but return immediately , thus letting whatever work that needs to be done
get done in the background.
The usual culprit in blocking calls is I/O of some kind. For ex ample, if a
call must read from disk in order to complete, it might block, waiting for
the I/O request that has been sent to the disk to return.
Non-blocking interfaces can be used in any style of programm ing (e.g.,
with threads), but are essential in the event-based approac h, as a call that
blocks will halt all progress.
an exceptional condition pending, respectively. The ﬁrst n fds descriptors are
checked in each set, i.e., the descriptors from 0 through nfd s-1 in the descriptor
sets are examined. On return, select() replaces the given de scriptor sets with
subsets consisting of those descriptors that are ready for t he requested operation.
select() returns the total number of ready descriptors in al l the sets.
A couple of points about select(). First, note that it lets you check
whether descriptors can be read from as well as written to; the former
lets a server determine that a new packet has arrived and is in need of
processing, whereas the latter lets the service know when it is OK to reply
(i.e., the outbound queue is not full).
Second, note the timeout argument. One common usage here is t o
set the timeout to NULL, which causes select() to block indeﬁnitely ,
until some descriptor is ready . However, more robust servers will usually
specify some kind of timeout; one common technique is to set t he timeout
to zero, and thus use the call to select() to return immediately .
The poll() system call is quite similar. See its manual page, or Stevens
and Rago [SR05], for details.
Either way , these basic primitives give us a way to build a non-blocking
event loop, which simply checks for incoming packets, reads from sockets
with messages upon them, and replies as needed.
33.3 Using select()
To make this more concrete, let’s examine how to use select() to see
which network descriptors have incoming messages upon them . Figure
33.1 shows a simple example.
This code is actually fairly simple to understand. After som e initial-
ization, the server enters an inﬁnite loop. Inside the loop, it uses the
FD ZERO() macro to ﬁrst clear the set of ﬁle descriptors, and then uses
FD SET() to include all of the ﬁle descriptors from minFD to maxFD in
the set. This set of descriptors might represent, for exampl e, all of the net-
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 412

376 EVENT -BASED CONCURRENCY (A DVANCED )
1 #include <stdio.h>
2 #include <stdlib.h>
3 #include <sys/time.h>
4 #include <sys/types.h>
5 #include <unistd.h>
6
7 int main(void) {
8 // open and set up a bunch of sockets (not shown)
9 // main loop
10 while (1) {
11 // initialize the fd_set to all zero
12 fd_set readFDs;
13 FD_ZERO(&readFDs);
14
15 // now set the bits for the descriptors
16 // this server is interested in
17 // (for simplicity, all of them from min to max)
18 int fd;
19 for (fd = minFD; fd < maxFD; fd++)
20 FD_SET(fd, &readFDs);
21
22 // do the select
23 int rc = select(maxFD+1, &readFDs, NULL, NULL, NULL);
24
25 // check which actually have data using FD_ISSET()
26 int fd;
27 for (fd = minFD; fd < maxFD; fd++)
28 if (FD_ISSET(fd, &readFDs))
29 processFD(fd);
30 }
31 }
Figure 33.1: Simple Code using select()
work sockets to which the server is paying attention. Finall y , the server
calls select() to see which of the connections have data available upon
them. By then using FD
ISSET() in a loop, the event server can see
which of the descriptors have data ready and process the inco ming data.
Of course, a real server would be more complicated than this, and
require logic to use when sending messages, issuing disk I/O , and many
other details. For further information, see Stevens and Rag o [SR05] for
API information, or Pai et. al or Welsh et al. for a good overvi ew of the
general ﬂow of event-based servers [PDZ99, WCB01].
33.4 Why Simpler? No Locks Needed
With a single CPU and an event-based application, the problems found
in concurrent programs are no longer present. Speciﬁcally , because only
one event is being handled at a time, there is no need to acquir e or release
locks; the event-based server cannot be interrupted by anot her thread be-
cause it is decidedly single threaded. Thus, concurrency bu gs common in
threaded programs do not manifest in the basic event-based a pproach.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 413

EVENT -BASED CONCURRENCY (A DVANCED ) 377
TIP : D ON ’ T BLOCK IN EVENT -BASED SERVERS
Event-based servers enable ﬁne-grained control over sched uling of tasks.
However, to maintain such control, no call that blocks the ex ecution the
caller can ever be made; failing to obey this design tip will r esult in a
blocked event-based server, frustrated clients, and serious questions as to
whether you ever read this part of the book.
33.5 A Problem: Blocking System Calls
Thus far, event-based programming sounds great, right? You program
a simple loop, and handle events as they arise. You don’t even need to
think about locking! But there is an issue: what if an event re quires that
you issue a system call that might block?
For example, imagine a request comes from a client into a serv er to
read a ﬁle from disk and return its contents to the requesting client (much
like a simple HTTP request). To service such a request, some e vent han-
dler will eventually have to issue an open() system call to open the ﬁle,
followed by a series of read() calls to read the ﬁle. When the ﬁle is read
into memory , the server will likely start sending the result s to the client.
Both the open() and read() calls may issue I/O requests to the stor-
age system (when the needed metadata or data is not in memory already),
and thus may take a long time to service. With a thread-based s erver, this
is no issue: while the thread issuing the I/O request suspend s (waiting
for the I/O to complete), other threads can run, thus enablin g the server
to make progress. Indeed, this natural overlap of I/O and other computa-
tion is what makes thread-based programming quite natural and straight-
forward.
With an event-based approach, however, there are no other th reads to
run: just the main event loop. And this implies that if an even t handler
issues a call that blocks, the entire server will do just that: block until the
call completes. When the event loop blocks, the system sits i dle, and thus
is a huge potential waste of resources. We thus have a rule tha t must be
obeyed in event-based systems: no blocking calls are allowe d.
33.6 A Solution: Asynchronous I/O
To overcome this limit, many modern operating systems have i ntro-
duced new ways to issue I/O requests to the disk system, refer red to
generically as asynchronous I/O. These interfaces enable an application
to issue an I/O request and return control immediately to the caller, be-
fore the I/O has completed; additional interfaces enable an application to
determine whether various I/Os have completed.
For example, let us examine the interface provided on Mac OS X (other
systems have similar APIs). The APIs revolve around a basic s tructure,
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 414

378 EVENT -BASED CONCURRENCY (A DVANCED )
the struct aiocb or AIO control block in common terminology . A
simpliﬁed version of the structure looks like this (see the m anual pages
for more information):
struct aiocb {
int aio_fildes; / * File descriptor */
off_t aio_offset; / * File offset */
volatile void *aio_buf; / * Location of buffer */
size_t aio_nbytes; / * Length of transfer */
};
To issue an asynchronous read to a ﬁle, an application should ﬁrst
ﬁll in this structure with the relevant information: the ﬁle descriptor of
the ﬁle to be read ( aio
fildes), the offset within the ﬁle ( aio offset)
as well as the length of the request ( aio nbytes), and ﬁnally the tar-
get memory location into which the results of the read should be copied
(aio buf).
After this structure is ﬁlled in, the application must issue the asyn-
chronous call to read the ﬁle; on Mac OS X, this API is simply th e asyn-
chronous read API:
int aio_read(struct aiocb *aiocbp);
This call tries to issue the I/O; if successful, it simply ret urns right
away and the application (i.e., the event-based server) can continue with
its work.
There is one last piece of the puzzle we must solve, however. H ow can
we tell when an I/O is complete, and thus that the buffer (poin ted to by
aio buf) now has the requested data within it?
One last API is needed. On Mac OS X, it is referred to (somewhat
confusingly) as aio error(). The API looks like this:
int aio_error(const struct aiocb *aiocbp);
This system call checks whether the request referred to by aiocbp has
completed. If it has, the routine returns success (indicate d by a zero);
if not, EINPROGRESS is returned. Thus, for every outstandin g asyn-
chronous I/O, an application can periodically poll the system via a call
to aio error() to determine whether said I/O has yet completed.
One thing you might have noticed is that it is painful to check whether
an I/O has completed; if a program has tens or hundreds of I/Os issued
at a given point in time, should it simply keep checking each o f them
repeatedly , or wait a little while ﬁrst, or ... ?
To remedy this issue, some systems provide an approach based on the
interrupt. This method uses U NIX signals to inform applications when
an asynchronous I/O completes, thus removing the need to rep eatedly
ask the system. This polling vs. interrupts issue is seen in d evices too, as
you will see (or already have seen) in the chapter on I/O devic es.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 415

EVENT -BASED CONCURRENCY (A DVANCED ) 379
ASIDE : UNIX SIGNALS
A huge and fascinating infrastructure known as signals is present in all mod-
ern U NIX variants. At its simplest, signals provide a way to communic ate with a
process. Speciﬁcally , a signal can be delivered to an application; doing so stops the
application from whatever it is doing to run a signal handler , i.e., some code in
the application to handle that signal. When ﬁnished, the pro cess just resumes its
previous behavior.
Each signal has a name, such as HUP (hang up), INT (interrupt), SEGV (seg-
mentation violation), etc; see the manual page for details. Interestingly , sometimes
it is the kernel itself that does the signaling. For example, when your program en-
counters a segmentation violation, the OS sends it a SIGSEGV (prepending SIG
to signal names is common); if your program is conﬁgured to ca tch that signal,
you can actually run some code in response to this erroneous p rogram behavior
(which can be useful for debugging). When a signal is sent to a process not conﬁg-
ured to handle that signal, some default behavior is enacted ; for SEGV , the process
is killed.
Here is a simple program that goes into an inﬁnite loop, but ha s ﬁrst set up a
signal handler to catch SIGHUP:
#include <stdio.h>
#include <signal.h>
void handle(int arg) {
printf("stop wakin’ me up...\n");
}
int main(int argc, char *argv[]) {
signal(SIGHUP, handle);
while (1)
; // doin’ nothin’ except catchin’ some sigs
return 0;
}
You can send signals to it with the kill command line tool (yes, this is an odd
and aggressive name). Doing so will interrupt the main while loop in the program
and run the handler code handle():
prompt> ./main &
[3] 36705
prompt> kill -HUP 36705
stop wakin’ me up...
prompt> kill -HUP 36705
stop wakin’ me up...
prompt> kill -HUP 36705
stop wakin’ me up...
There is a lot more to learn about signals, so much that a singl e page, much
less a single chapter, does not nearly sufﬁce. As always, the re is one great source:
Stevens and Rago [SR05]. Read more if interested.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 416

380 EVENT -BASED CONCURRENCY (A DVANCED )
In systems without asynchronous I/O, the pure event-based a pproach
cannot be implemented. However, clever researchers have de rived meth-
ods that work fairly well in their place. For example, Pai et a l. [PDZ99]
describe a hybrid approach in which events are used to proces s network
packets, and a thread pool is used to manage outstanding I/Os . Read
their paper for details.
33.7 Another Problem: State Management
Another issue with the event-based approach is that such cod e is gen-
erally more complicated to write than traditional thread-b ased code. The
reason is as follows: when an event handler issues an asynchr onous I/O,
it must package up some program state for the next event handl er to use
when the I/O ﬁnally completes; this additional work is not ne eded in
thread-based programs, as the state the program needs is on t he stack of
the thread. Adya et al. call this work manual stack management , and it
is fundamental to event-based programming [A+02].
To make this point more concrete, let’s look at a simple examp le in
which a thread-based server needs to read from a ﬁle descript or (fd) and,
once complete, write the data that it read from the ﬁle to a net work socket
descriptor (sd). The code (ignoring error checking) looks like this:
int rc = read(fd, buffer, size);
rc = write(sd, buffer, size);
As you can see, in a multi-threaded program, doing this kind o f work
is trivial; when the read() ﬁnally returns, the code immediately knows
which socket to write to because that information is on the st ack of the
thread (in the variable sd).
In an event-based system, life is not so easy . To perform the same task,
we’d ﬁrst issue the read asynchronously , using the AIO calls described
above. Let’s say we then periodically check for completion o f the read
using the aio
error() call; when that call informs us that the read is
complete, how does the event-based server know what to do?
The solution, as described by Adya et al. [A+02], is to use an o ld pro-
gramming language construct known as a continuation [FHK84]. Though
it sounds complicated, the idea is rather simple: basically , record the
needed information to ﬁnish processing this event in some da ta struc-
ture; when the event happens (i.e., when the disk I/O complet es), look
up the needed information and process the event.
In this speciﬁc case, the solution would be to record the sock et de-
scriptor ( sd) in some kind of data structure (e.g., a hash table), indexed
by the ﬁle descriptor ( fd). When the disk I/O completes, the event han-
dler would use the ﬁle descriptor to look up the continuation , which will
return the value of the socket descriptor to the caller. At th is point (ﬁ-
nally), the server can then do the last bit of work to write the data to the
socket.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 417

EVENT -BASED CONCURRENCY (A DVANCED ) 381
33.8 What Is Still Difﬁcult With Events
There are a few other difﬁculties with the event-based appro ach that
we should mention. For example, when systems moved from a sin gle
CPU to multiple CPUs, some of the simplicity of the event-bas ed ap-
proach disappeared. Speciﬁcally , in order to utilize more t han one CPU,
the event server has to run multiple event handlers in parall el; when do-
ing so, the usual synchronization problems (e.g., critical sections) arise,
and the usual solutions (e.g., locks) must be employed. Thus , on mod-
ern multicore systems, simple event handling without locks is no longer
possible.
Another problem with the event-based approach is that it doe s not
integrate well with certain kinds of systems activity , such as paging. For
example, if an event-handler page faults, it will block, and thus the server
will not make progress until the page fault completes. Even t hough the
server has been structured to avoid explicit blocking, this type of implicit
blocking due to page faults is hard to avoid and thus can lead t o large
performance problems when prevalent.
A third issue is that event-based code can be hard to manage over time,
as the exact semantics of various routines changes [A+02]. F or example,
if a routine changes from non-blocking to blocking, the even t handler
that calls that routine must also change to accommodate its n ew nature,
by ripping itself into two pieces. Because blocking is so dis astrous for
event-based servers, a programmer must always be on the look out for
such changes in the semantics of the APIs each event uses.
Finally , though asynchronous disk I/O is now possible on mos t plat-
forms, it has taken a long time to get there [PDZ99], and it nev er quite
integrates with asynchronous network I/O in as simple and un iform a
manner as you might think. For example, while one would simpl y like
to use the select() interface to manage all outstanding I/Os, usually
some combination of select() for networking and the AIO calls for
disk I/O are required.
33.9 Summary
We’ve presented a bare bones introduction to a different sty le of con-
currency based on events. Event-based servers give control of schedul-
ing to the application itself, but do so at some cost in comple xity and
difﬁculty of integration with other aspects of modern syste ms (e.g., pag-
ing). Because of these challenges, no single approach has em erged as
best; thus, both threads and events are likely to persist as t wo different
approaches to the same concurrency problem for many years to come.
Read some research papers (e.g., [A+02, PDZ99, vB+03, WCB01 ]) or bet-
ter yet, write some event-based code, to learn more.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 418

382 EVENT -BASED CONCURRENCY (A DVANCED )
References
[A+02] “Cooperative Task Management Without Manual Stack M anagement”
Atul Adya, Jon Howell, Marvin Theimer, William J. Bolosky , John R. Douceur
USENIX ATC ’02, Monterey , CA, June 2002
This gem of a paper is the ﬁrst to clearly articulate some of th e difﬁculties of event-based concurrency,
and suggests some simple solutions, as well explores the eve n crazier idea of combining the two types of
concurrency management into a single application!
[FHK84] “Programming With Continuations”
Daniel P . Friedman, Christopher T. Haynes, Eugene E. Kohlbecker
In Program Transformation and Programming Environments, S pringer V erlag, 1984
The classic reference to this old idea from the world of progr amming languages. Now increasingly
popular in some modern languages.
[N13] “Node.js Documentation”
By the folks who build node.js
Available: http://nodejs.org/api/
One of the many cool new frameworks that help you readily buil d web services and applications. Every
modern systems hacker should be proﬁcient in frameworks suc h as this one (and likely, more than one).
Spend the time and do some development in one of these worlds a nd become an expert.
[O96] “Why Threads Are A Bad Idea (for most purposes)”
John Ousterhout
Invited Talk at USENIX ’96, San Diego, CA, January 1996
A great talk about how threads aren’t a great match for GUI-ba sed applications (but the ideas are more
general). Ousterhout formed many of these opinions while he was developing Tcl/Tk, a cool scripting
language and toolkit that made it 100x easier to develop GUI- based applications than the state of the
art at the time. While the Tk GUI toolkit lives on (in Python fo r example), Tcl seems to be slowly dying
(unfortunately).
[PDZ99] “Flash: An Efﬁcient and Portable Web Server”
Vivek S. Pai, Peter Druschel, Willy Zwaenepoel
USENIX ’99, Monterey , CA, June 1999
A pioneering paper on how to structure web servers in the then -burgeoning Internet era. Read it to
understand the basics as well as to see the authors’ ideas on h ow to build hybrids when support for
asynchronous I/O is lacking.
[SR05] “Advanced Programming in the U NIX Environment”
W. Richard Stevens and Stephen A. Rago
Addison-Wesley , 2005
Once again, we refer to the classic must-have-on-your-book shelf book of UNIX systems programming.
If there is some detail you need to know, it is in here.
[vB+03] “Capriccio: Scalable Threads for Internet Service s”
Rob von Behren, Jeremy Condit, Feng Zhou, George C. Necula, E ric Brewer
SOSP ’03, Lake George, New York, October 2003
A paper about how to make threads work at extreme scale; a coun ter to all the event-based work ongoing
at the time.
[WCB01] “SEDA: An Architecture for Well-Conditioned, Scal able Internet Services”
Matt Welsh, David Culler, and Eric Brewer
SOSP ’01, Banff, Canada, October 2001
A nice twist on event-based serving that combines threads, q ueues, and event-based hanlding into one
streamlined whole. Some of these ideas have found their way i nto the infrastructures of companies such
as Google, Amazon, and elsewhere.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 419

34
Summary Dialogue on Concurrency
Professor: So, does your head hurt now?
Student: (taking two Motrin tablets) Well, some. It’s hard to think ab out all the
ways threads can interleave.
Professor: Indeed it is. I am always amazed at how so few line of code, when
concurrent execution is involved, can become nearly imposs ible to understand.
Student: Me too! It’s kind of embarrassing, as a Computer Scientist, n ot to be
able to make sense of ﬁve lines of code.
Professor: Oh, don’t feel too badly. If you look through the ﬁrst papers o n con-
current algorithms, they are sometimes wrong! And the authors often professors!
Student: (gasps) Professors can be ... umm... wrong?
Professor: Y es, it is true. Though don’t tell anybody – it’s one of our tra de
secrets.
Student: I am sworn to secrecy. But if concurrent code is so hard to thin k about,
and so hard to get right, how are we supposed to write correct c oncurrent code?
Professor: Well that is the real question, isn’t it? I think it starts wit h a few
simple things. First, keep it simple! Avoid complex interac tions between threads,
and use well-known and tried-and-true ways to manage thread interactions.
Student: Like simple locking, and maybe a producer-consumer queue?
Professor: Exactly! Those are common paradigms, and you should be able t o
produce the working solutions given what you’ve learned. Se cond, only use con-
currency when absolutely needed; avoid it if at all possible . There is nothing
worse than premature optimization of a program.
Student: I see – why add threads if you don’t need them?
Professor: Exactly. Third, if you really need parallelism, seek it in ot her sim-
pliﬁed forms. For example, the Map-Reduce method for writin g parallel data
analysis code is an excellent example of achieving parallel ism without having to
handle any of the horriﬁc complexities of locks, condition v ariables, and the other
nasty things we’ve talked about.
383

## Page 420

384 SUMMARY DIALOGUE ON CONCURRENCY
Student: Map-Reduce, huh? Sounds interesting – I’ll have to read more about
it on my own.
Professor: Good! Y ou should. In the end, you’ll have to do a lot of that, as
what we learn together can only serve as the barest introduct ion to the wealth of
knowledge that is out there. Read, read, and read some more! A nd then try things
out, write some code, and then write some more too. As Gladwel l talks about in
his book “Outliers”, you need to put roughly 10,000 hours int o something in
order to become a real expert. Y ou can’t do that all inside of c lass time!
Student: Wow, I’m not sure if that is depressing, or uplifting. But I’l l assume
the latter, and get to work! Time to write some more concurren t code...
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 421

Part III
Persistence
385

## Page 423

35
A Dialogue on Persistence
Professor: And thus we reach the third of our four ... err... three pillar s of
operating systems: persistence.
Student: Did you say there were three pillars, or four? What is the four th?
Professor: No. Just three, young student, just three. T rying to keep it s imple
here.
Student: OK, ﬁne. But what is persistence, oh ﬁne and noble professor?
Professor: Actually, you probably know what it means in the traditional sense,
right? As the dictionary would say: “a ﬁrm or obstinate conti nuance in a course
of action in spite of difﬁculty or opposition.”
Student: It’s kind of like taking your class: some obstinance require d.
Professor: Ha! Y es. But persistence here means something else. Let me ex plain.
Imagine you are outside, in a ﬁeld, and you pick a –
Student: (interrupting) I know! A peach! From a peach tree!
Professor: I was going to say apple, from an apple tree. Oh well; we’ll do i t your
way, I guess.
Student: (stares blankly)
Professor: Anyhow, you pick a peach; in fact, you pick many many peaches,
but you want to make them last for a long time. Winter is hard an d cruel in
Wisconsin, after all. What do you do?
Student: Well, I think there are some different things you can do. Y ou can pickle
it! Or bake a pie. Or make a jam of some kind. Lots of fun!
Professor: Fun? Well, maybe. Certainly, you have to do a lot more work to m ake
the peach persist. And so it is with information as well; making information
persist, despite computer crashes, disk failures, or power outages is a tough and
interesting challenge.
Student: Nice segue; you’re getting quite good at that.
Professor: Thanks! A professor can always use a few kind words, you know.
387

## Page 424

388 A D IALOGUE ON PERSISTENCE
Student: I’ll try to remember that. I guess it’s time to stop talking pe aches, and
start talking computers?
Professor: Y es, it is that time...
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 425

36
I/O Devices
Before delving into the main content of this part of the book ( on persis-
tence), we ﬁrst introduce the concept of an input/output (I/O) device and
show how the operating system might interact with such an ent ity . I/O is
quite critical to computer systems, of course; imagine a pro gram without
any input (it produces the same result each time); now imagin e a pro-
gram with no output (what was the purpose of it running?). Cle arly , for
computer systems to be interesting, both input and output ar e required.
And thus, our general problem:
CRUX : H OW TO INTEGRATE I/O I NTO SYSTEMS
How should I/O be integrated into systems? What are the gener al
mechanisms? How can we make them efﬁcient?
36.1 System Architecture
To begin our discussion, let’s look at the structure of a typi cal system
(Figure 36.1). The picture shows a single CPU attached to the main mem-
ory of the system via some kind of memory bus or interconnect. Some
devices are connected to the system via a general I/O bus, which in many
modern systems would be PCI (or one if its many derivatives); graph-
ics and some other higher-performance I/O devices might be f ound here.
Finally , even lower down are one or more of what we call a peripheral
bus, such as SCSI, SA TA, or USB. These connect the slowest devices to
the system, including disks, mice, and other similar components.
One question you might ask is: why do we need a hierarchical st ruc-
ture like this? Put simply: physics, and cost. The faster a bu s is, the
shorter it must be; thus, a high-performance memory bus does not have
much room to plug devices and such into it. In addition, engin eering
a bus for high performance is quite costly . Thus, system desi gners have
adopted this hierarchical approach, where components thatdemands high
performance (such as the graphics card) are nearer the CPU. L ower per-
389

## Page 426

390 I/O D EVICES
Graphics
MemoryCPU
Memory Bus
(proprietary)
General I/O Bus
(e.g., PCI)
Peripheral I/O Bus
(e.g., SCSI, SATA, USB)
Figure 36.1: Prototypical System Architecture
formance components are further away . The beneﬁts of placing disks and
other slow devices on a peripheral bus are manifold; in parti cular, you
can place a large number of devices on it.
36.2 A Canonical Device
Let us now look at a canonical device (not a real one), and use t his
device to drive our understanding of some of the machinery re quired
to make device interaction efﬁcient. From Figure 36.2, we can see that a
device has two important components. The ﬁrst is the hardware interface
it presents to the rest of the system. Just like a piece of soft ware, hardware
must also present some kind of interface that allows the syst em software
to control its operation. Thus, all devices have some speciﬁ ed interface
and protocol for typical interaction.
The second part of any device is its internal structure . This part of
the device is implementation speciﬁc and is responsible for implement-
ing the abstraction the device presents to the system. V ery simple devices
will have one or a few hardware chips to implement their funct ionality;
more complex devices will include a simple CPU, some general purpose
memory , and other device-speciﬁc chips to get their job done . For exam-
ple, modern RAID controllers might consist of hundreds of th ousands of
lines of ﬁrmware (i.e., software within a hardware device) to implement
its functionality .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 427

I/O D EVICES 391
Other Hardware-specific Chips
Memory (DRAM or SRAM or both)
Micro-controller (CPU)
Registers Status Command Data Interface
Internals
Figure 36.2: A Canonical Device
36.3 The Canonical Protocol
In the picture above, the (simpliﬁed) device interface is co mprised of
three registers: a status register, which can be read to see the current sta-
tus of the device; a command register, to tell the device to perform a cer-
tain task; and a data register to pass data to the device, or get data from
the device. By reading and writing these registers, the oper ating system
can control device behavior.
Let us now describe a typical interaction that the OS might ha ve with
the device in order to get the device to do something on its beh alf. The
protocol is as follows:
While (STATUS == BUSY)
; // wait until device is not busy
Write data to DATA register
Write command to COMMAND register
(Doing so starts the device and executes the command)
While (STATUS == BUSY)
; // wait until device is done with your request
The protocol has four steps. In the ﬁrst, the OS waits until th e device is
ready to receive a command by repeatedly reading the status r egister; we
call this polling the device (basically , just asking it what is going on). Sec-
ond, the OS sends some data down to the data register; one can i magine
that if this were a disk, for example, that multiple writes wo uld need to
take place to transfer a disk block (say 4KB) to the device. Wh en the main
CPU is involved with the data movement (as in this example pro tocol),
we refer to it as programmed I/O (PIO). Third, the OS writes a command
to the command register; doing so implicitly lets the device know that
both the data is present and that it should begin working on th e com-
mand. Finally , the OS waits for the device to ﬁnish by again po lling it
in a loop, waiting to see if it is ﬁnished (it may then get an err or code to
indicate success or failure).
This basic protocol has the positive aspect of being simple a nd work-
ing. However, there are some inefﬁciencies and inconveniences involved.
The ﬁrst problem you might notice in the protocol is that poll ing seems
inefﬁcient; speciﬁcally , it wastes a great deal of CPU time j ust waiting for
the (potentially slow) device to complete its activity , instead of switching
to another ready process and thus better utilizing the CPU.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 428

392 I/O D EVICES
THE CRUX : H OW TO AVOID THE COSTS OF POLLING
How can the OS check device status without frequent polling, and
thus lower the CPU overhead required to manage the device?
36.4 Lowering CPU Overhead With Interrupts
The invention that many engineers came upon years ago to impr ove
this interaction is something we’ve seen already: the interrupt. Instead
of polling the device repeatedly , the OS can issue a request, put the call-
ing process to sleep, and context switch to another task. Whe n the device
is ﬁnally ﬁnished with the operation, it will raise a hardwar e interrupt,
causing the CPU to jump into the OS at a pre-determined interrupt ser-
vice routine (ISR) or more simply an interrupt handler . The handler is
just a piece of operating system code that will ﬁnish the requ est (for ex-
ample, by reading data and perhaps an error code from the devi ce) and
wake the process waiting for the I/O, which can then proceed a s desired.
Interrupts thus allow for overlap of computation and I/O, which is
key for improved utilization. This timeline shows the probl em:
CPU
Disk 1 1 1 1 1
1 1 1 1 1 p p p p p 1 1 1 1 1
In the diagram, Process 1 runs on the CPU for some time (indica ted by
a repeated 1 on the CPU line), and then issues an I/O request to the disk
to read some data. Without interrupts, the system simply spi ns, polling
the status of the device repeatedly until the I/O is complete (indicated by
a p). The disk services the request and ﬁnally Process 1 can run a gain.
If instead we utilize interrupts and allow for overlap, the O S can do
something else while waiting for the disk:
CPU
Disk 1 1 1 1 1
1 1 1 1 1 2 2 2 2 2 1 1 1 1 1
In this example, the OS runs Process 2 on the CPU while the disk ser-
vices Process 1’s request. When the disk request is ﬁnished, an interrupt
occurs, and the OS wakes up Process 1 and runs it again. Thus, both the
CPU and the disk are properly utilized during the middle stre tch of time.
Note that using interrupts is not always the best solution. For example,
imagine a device that performs its tasks very quickly: the ﬁrst poll usually
ﬁnds the device to be done with task. Using an interrupt in thi s case will
actually slow down the system: switching to another process, handling the
interrupt, and switching back to the issuing process is expe nsive. Thus, if
a device is fast, it may be best to poll; if it is slow , interrup ts, which allow
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 429

I/O D EVICES 393
TIP : I NTERRUPTS NOT ALWAYS BETTER THAN PIO
Although interrupts allow for overlap of computation and I/ O, they only
really make sense for slow devices. Otherwise, the cost of in terrupt han-
dling and context switching may outweigh the beneﬁts interr upts pro-
vide. There are also cases where a ﬂood of interrupts may over load a sys-
tem and lead it to livelock [MR96]; in such cases, polling pro vides more
control to the OS in its scheduling and thus is again useful.
overlap, are best. If the speed of the device is not known, or s ometimes
fast and sometimes slow , it may be best to use a hybrid that polls for a
little while and then, if the device is not yet ﬁnished, uses i nterrupts. This
two-phased approach may achieve the best of both worlds.
Another reason not to use interrupts arises in networks [MR9 6]. When
a huge stream of incoming packets each generate an interrupt , it is pos-
sible for the OS to livelock, that is, ﬁnd itself only processing interrupts
and never allowing a user-level process to run and actually s ervice the
requests. For example, imagine a web server that suddenly ex periences
a high load due to the “slashdot effect”. In this case, it is be tter to occa-
sionally use polling to better control what is happening in t he system and
allow the web server to service some requests before going ba ck to the
device to check for more packet arrivals.
Another interrupt-based optimization is coalescing. In such a setup, a
device which needs to raise an interrupt ﬁrst waits for a bit b efore deliv-
ering the interrupt to the CPU. While waiting, other request s may soon
complete, and thus multiple interrupts can be coalesced int o a single in-
terrupt delivery , thus lowering the overhead of interrupt p rocessing. Of
course, waiting too long will increase the latency of a reque st, a common
trade-off in systems. See Ahmad et al. [A+11] for an excellen t summary .
36.5 More Efﬁcient Data Movement With DMA
Unfortunately , there is one other aspect of our canonical pr otocol that
requires our attention. In particular, when using programm ed I/O (PIO)
to transfer a large chunk of data to a device, the CPU is once ag ain over-
burdened with a rather trivial task, and thus wastes a lot of t ime and
effort that could better be spent running other processes. T his timeline
illustrates the problem:
CPU
Disk 1 1 1 1 1
1 1 1 1 1 c c c 2 2 2 2 2 1 1
In the timeline, Process 1 is running and then wishes to write some data to
the disk. It then initiates the I/O, which must copy the data f rom memory
to the device explicitly , one word at a time (marked c in the diagram).
When the copy is complete, the I/O begins on the disk and the CP U can
ﬁnally be used for something else.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 430

394 I/O D EVICES
THE CRUX : H OW TO LOWER PIO O VERHEADS
With PIO, the CPU spends too much time moving data to and from
devices by hand. How can we ofﬂoad this work and thus allow the CPU
to be more effectively utilized?
The solution to this problem is something we refer to as Direct Mem-
ory Access (DMA) . A DMA engine is essentially a very speciﬁc device
within a system that can orchestrate transfers between devi ces and main
memory without much CPU intervention.
DMA works as follows. To transfer data to the device, for exam ple, the
OS would program the DMA engine by telling it where the data li ves in
memory , how much data to copy , and which device to send it to. A t that
point, the OS is done with the transfer and can proceed with ot her work.
When the DMA is complete, the DMA controller raises an interr upt, and
the OS thus knows the transfer is complete. The revised timel ine:
CPU
DMA
Disk 1 1 1 1 1
1 1 1 1 1 2 2 2 2 2 2 2 2 1 1
c c c
From the timeline, you can see that the copying of data is now handled
by the DMA controller. Because the CPU is free during that tim e, the OS
can do something else, here choosing to run Process 2. Proces s 2 thus gets
to use more CPU before Process 1 runs again.
36.6 Methods Of Device Interaction
Now that we have some sense of the efﬁciency issues involved w ith
performing I/O, there are a few other problems we need to hand le to
incorporate devices into modern systems. One problem you ma y have
noticed thus far: we have not really said anything about how t he OS ac-
tually communicates with the device! Thus, the problem:
THE CRUX : H OW TO COMMUNICATE WITH DEVICES
How should the hardware communicate with a device? Should th ere
be explicit instructions? Or are there other ways to do it?
Over time, two primary methods of device communication have de-
veloped. The ﬁrst, oldest method (used by IBM mainframes for many
years) is to have explicit I/O instructions . These instructions specify a
way for the OS to send data to speciﬁc device registers and thu s allow the
construction of the protocols described above.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 431

I/O D EVICES 395
For example, on x86, the in and out instructions can be used to com-
municate with devices. For example, to send data to a device, the caller
speciﬁes a register with the data in it, and a speciﬁc port which names the
device. Executing the instruction leads to the desired beha vior.
Such instructions are usually privileged. The OS controls devices, and
the OS thus is the only entity allowed to directly communicate with them.
Imagine if any program could read or write the disk, for examp le: total
chaos (as always), as any user program could use such a loopho le to gain
complete control over the machine.
The second method to interact with devices is known as memory-
mapped I/O . With this approach, the hardware makes device registers
available as if they were memory locations. To access a particular register,
the OS issues a load (to read) or store (to write) the address; the hardware
then routes the load/store to the device instead of main memo ry .
There is not some great advantage to one approach or the other . The
memory-mapped approach is nice in that no new instructions a re needed
to support it, but both approaches are still in use today .
36.7 Fitting Into The OS: The Device Driver
One ﬁnal problem we will discuss: how to ﬁt devices, each of wh ich
have very speciﬁc interfaces, into the OS, which we would lik e to keep
as general as possible. For example, consider a ﬁle system. W e’d like
to build a ﬁle system that worked on top of SCSI disks, IDE disk s, USB
keychain drives, and so forth, and we’d like the ﬁle system to be relatively
oblivious to all of the details of how to issue a read or write r equest to
these difference types of drives. Thus, our problem:
THE CRUX : H OW TO BUILD A D EVICE -NEUTRAL OS
How can we keep most of the OS device-neutral, thus hiding the de-
tails of device interactions from major OS subsystems?
The problem is solved through the age-old technique of abstraction.
At the lowest level, a piece of software in the OS must know in d etail
how a device works. We call this piece of software a device driver , and
any speciﬁcs of device interaction are encapsulated within .
Let us see how this abstraction might help OS design and imple men-
tation by examining the Linux ﬁle system software stack. Fig ure 36.3 is
a rough and approximate depiction of the Linux software orga nization.
As you can see from the diagram, a ﬁle system (and certainly , a n appli-
cation above) is completely oblivious to the speciﬁcs of whi ch disk class
it is using; it simply issues block read and write requests to the generic
block layer, which routes them to the appropriate device dri ver, which
handles the details of issuing the speciﬁc request. Althoug h simpliﬁed,
the diagram shows how such detail can be hidden from most of th e OS.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 432

396 I/O D EVICES
Application
File System
Generic Block Layer
Device Driver [SCSI, ATA, etc.]
POSIX API [open, read, write, close, etc.]
Generic Block Interface [block read/write]
Specific Block Interface [protocol-specific read/write]
userkernel mode
Figure 36.3: The File System Stack
Note that such encapsulation can have its downside as well. F or ex-
ample, if there is a device that has many special capabilitie s, but has to
present a generic interface to the rest of the kernel, those s pecial capabili-
ties will go unused. This situation arises, for example, in L inux with SCSI
devices, which have very rich error reporting; because othe r block de-
vices (e.g., ATA/IDE) have much simpler error handling, all that higher
levels of software ever receive is a generic EIO (generic IO error) error
code; any extra detail that SCSI may have provided is thus los t to the ﬁle
system [G08].
Interestingly , because device drivers are needed for any de vice you
might plug into your system, over time they have come to repre sent a
huge percentage of kernel code. Studies of the Linux kernel r eveal that
over 70% of OS code is found in device drivers [C01]; for Windo ws-based
systems, it is likely quite high as well. Thus, when people te ll you that the
OS has millions of lines of code, what they are really saying i s that the OS
has millions of lines of device-driver code. Of course, for a ny given in-
stallation, most of that code may not be active (i.e., only a f ew devices are
connected to the system at a time). Perhaps more depressingl y , as drivers
are often written by “amateurs” (instead of full-time kerne l developers),
they tend to have many more bugs and thus are a primary contrib utor to
kernel crashes [S03].
36.8 Case Study: A Simple IDE Disk Driver
To dig a little deeper here, let’s take a quick look at an actua l device: an
IDE disk drive [L94]. We summarize the protocol as described in this ref-
erence [W10]; we’ll also peek at the xv6 source code for a simp le example
of a working IDE driver [CK+08].
An IDE disk presents a simple interface to the system, consis ting of
four types of register: control, command block, status, and error. These
registers are available by reading or writing to speciﬁc “I/ O addresses”
(such as 0x3F6 below) using (on x86) the in and out I/O instructions.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 433

I/O D EVICES 397
Control Register:
Address 0x3F6 = 0x80 (0000 1RE0): R=reset, E=0 means "enable interrupt"
Command Block Registers:
Address 0x1F0 = Data Port
Address 0x1F1 = Error
Address 0x1F2 = Sector Count
Address 0x1F3 = LBA low byte
Address 0x1F4 = LBA mid byte
Address 0x1F5 = LBA hi byte
Address 0x1F6 = 1B1D TOP4LBA: B=LBA, D=drive
Address 0x1F7 = Command/status
Status Register (Address 0x1F7):
7 6 5 4 3 2 1 0
BUSY READY FAULT SEEK DRQ CORR IDDEX ERROR
Error Register (Address 0x1F1): (check when Status ERROR== 1)
7 6 5 4 3 2 1 0
BBK UNC MC IDNF MCR ABRT T0NF AMNF
BBK = Bad Block
UNC = Uncorrectable data error
MC = Media Changed
IDNF = ID mark Not Found
MCR = Media Change Requested
ABRT = Command aborted
T0NF = Track 0 Not Found
AMNF = Address Mark Not Found
Figure 36.4: The IDE Interface
The basic protocol to interact with the device is as follows, assuming
it has already been initialized.
• Wait for drive to be ready. Read Status Register (0x1F7) until drive
is not busy and READY .
• Write parameters to command registers. Write the sector count,
logical block address (LBA) of the sectors to be accessed, an d drive
number (master=0x00 or slave=0x10, as IDE permits just two drives)
to command registers (0x1F2-0x1F6).
• Start the I/O. by issuing read/write to command register. Write
READ—WRITE command to command register (0x1F7).
• Data transfer (for writes): Wait until drive status is READY and
DRQ (drive request for data); write data to data port.
• Handle interrupts. In the simplest case, handle an interrupt for
each sector transferred; more complex approaches allow bat ching
and thus one ﬁnal interrupt when the entire transfer is compl ete.
• Error handling. After each operation, read the status register. If the
ERROR bit is on, read the error register for details.
Most of this protocol is found in the xv6 IDE driver (Figure
36.5),
which (after initialization) works through four primary fu nctions. The
ﬁrst is ide rw(), which queues a request (if there are others pending),
or issues it directly to the disk (via ide start request()); in either
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 434

398 I/O D EVICES
static int ide_wait_ready() {
while (((int r = inb(0x1f7)) & IDE_BSY) || !(r & IDE_DRDY))
; // loop until drive isn’t busy
}
static void ide_start_request(struct buf *b) {
ide_wait_ready();
outb(0x3f6, 0); // generate interrupt
outb(0x1f2, 1); // how many sectors?
outb(0x1f3, b->sector & 0xff); // LBA goes here ...
outb(0x1f4, (b->sector >> 8) & 0xff); // ... and here
outb(0x1f5, (b->sector >> 16) & 0xff); // ... and here!
outb(0x1f6, 0xe0 | ((b->dev&1)<<4) | ((b->sector>>24)&0x 0f));
if(b->flags & B_DIRTY){
outb(0x1f7, IDE_CMD_WRITE); // this is a WRITE
outsl(0x1f0, b->data, 512/4); // transfer data too!
} else {
outb(0x1f7, IDE_CMD_READ); // this is a READ (no data)
}
}
void ide_rw(struct buf *b) {
acquire(&ide_lock);
for (struct buf **pp = &ide_queue; *pp; pp=&( *pp)->qnext)
; // walk queue
*pp = b; // add request to end
if (ide_queue == b) // if q is empty
ide_start_request(b); // send req to disk
while ((b->flags & (B_VALID|B_DIRTY)) != B_VALID)
sleep(b, &ide_lock); // wait for completion
release(&ide_lock);
}
void ide_intr() {
struct buf *b;
acquire(&ide_lock);
if (!(b->flags & B_DIRTY) && ide_wait_ready(1) >= 0)
insl(0x1f0, b->data, 512/4); // if READ: get data
b->flags |= B_VALID;
b->flags &= ˜B_DIRTY;
wakeup(b); // wake waiting process
if ((ide_queue = b->qnext) != 0) // start next request
ide_start_request(ide_queue); // (if one exists)
release(&ide_lock);
}
Figure 36.5: The xv6 IDE Disk Driver (Simpliﬁed)
case, the routine waits for the request to complete and the ca lling pro-
cess is put to sleep. The second is ide
start request(), which is
used to send a request (and perhaps data, in the case of a write ) to the
disk; the in and out x86 instructions are called to read and write device
registers, respectively . The start request routine uses th e third function,
ide wait ready(), to ensure the drive is ready before issuing a request
to it. Finally , ide intr() is invoked when an interrupt takes place; it
reads data from the device (if the request is a read, not a writ e), wakes the
process waiting for the I/O to complete, and (if there are mor e requests
in the I/O queue), launches the next I/O via ide start request().
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 435

I/O D EVICES 399
36.9 Historical Notes
Before ending, we include a brief historical note on the orig in of some
of these fundamental ideas. If you are interested in learnin g more, read
Smotherman’s excellent summary [S08].
Interrupts are an ancient idea, existing on the earliest of m achines. For
example, the UNIV AC in the early 1950’s had some form of inter rupt vec-
toring, although it is unclear in exactly which year this fea ture was avail-
able [S08]. Sadly , even in its infancy , we are beginning to lo se the origins
of computing history .
There is also some debate as to which machine ﬁrst introducedthe idea
of DMA. For example, Knuth and others point to the DYSEAC (a “m o-
bile” machine, which at the time meant it could be hauled in a t railer),
whereas others think the IBM SAGE may have been the ﬁrst [S08] . Ei-
ther way , by the mid 50’s, systems with I/O devices that commu nicated
directly with memory and interrupted the CPU when ﬁnished ex isted.
The history here is difﬁcult to trace because the inventions are tied to
real, and sometimes obscure, machines. For example, some th ink that the
Lincoln Labs TX-2 machine was ﬁrst with vectored interrupts [S08], but
this is hardly clear.
Because the ideas are relatively obvious – no Einsteinian le ap is re-
quired to come up with the idea of letting the CPU do something else
while a slow I/O is pending – perhaps our focus on “who ﬁrst?” i s mis-
guided. What is certainly clear: as people built these early machines, it
became obvious that I/O support was needed. Interrupts, DMA , and re-
lated ideas are all direct outcomes of the nature of fast CPUs and slow
devices; if you were there at the time, you might have had simi lar ideas.
36.10 Summary
You should now have a very basic understanding of how an OS int er-
acts with a device. Two techniques, the interrupt and DMA, ha ve been
introduced to help with device efﬁciency , and two approache s to access-
ing device registers, explicit I/O instructions and memory -mapped I/O,
have been described. Finally , the notion of a device driver h as been pre-
sented, showing how the OS itself can encapsulate low-level details and
thus make it easier to build the rest of the OS in a device-neut ral fashion.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 436

400 I/O D EVICES
References
[A+11] “vIC: Interrupt Coalescing for Virtual Machine Stor age Device IO”
Irfan Ahmad, Ajay Gulati, Ali Mashtizadeh
USENIX ’11
A terriﬁc survey of interrupt coalescing in traditional and virtualized environments.
[C01] “An Empirical Study of Operating System Errors”
Andy Chou, Junfeng Yang, Benjamin Chelf, Seth Hallem, Dawso n Engler
SOSP ’01
One of the ﬁrst papers to systematically explore how many bug s are in modern operating systems.
Among other neat ﬁndings, the authors show that device drive rs have something like seven times more
bugs than mainline kernel code.
[CK+08] “The xv6 Operating System”
Russ Cox, Frans Kaashoek, Robert Morris, Nickolai Zeldovic h
From: http://pdos.csail.mit.edu/6.828/2008/index.htm l
See ide.c for the IDE device driver, with a few more details therein.
[D07] “What Every Programmer Should Know About Memory”
Ulrich Drepper
November, 2007
Available: http://www.akkadia.org/drepper/cpumemory .pdf
A fantastic read about modern memory systems, starting at DR AM and going all the way up to virtu-
alization and cache-optimized algorithms.
[G08] “EIO: Error-handling is Occasionally Correct”
Haryadi Gunawi, Cindy Rubio-Gonzalez, Andrea Arpaci-Duss eau, Remzi Arpaci-Dusseau,
Ben Liblit
FAST ’08, San Jose, CA, February 2008
Our own work on building a tool to ﬁnd code in Linux ﬁle systems that does not handle error return
properly. We found hundreds and hundreds of bugs, many of whi ch have now been ﬁxed.
[L94] “AT Attachment Interface for Disk Drives”
Lawrence J. Lamers, X3T10 Technical Editor
Available: ftp://ftp.t10.org/t13/project/d0791r4c-ATA-1.pdf
Reference number: ANSI X3.221 - 1994 A rather dry document about device interfaces. Read it at
your own peril.
[MR96] “Eliminating Receive Livelock in an Interrupt-driv en Kernel”
Jeffrey Mogul and K. K. Ramakrishnan
USENIX ’96, San Diego, CA, January 1996
Mogul and colleagues did a great deal of pioneering work on we b server network performance. This
paper is but one example.
[S08] “Interrupts”
Mark Smotherman, as of July ’08
Available: http://people.cs.clemson.edu/˜mark/interrupts.html
A treasure trove of information on the history of interrupts, DMA, and related early ideas in computing.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 437

I/O D EVICES 401
[S03] “Improving the Reliability of Commodity Operating Sy stems”
Michael M. Swift, Brian N. Bershad, and Henry M. Levy
SOSP ’03
Swift’s work revived interest in a more microkernel-like ap proach to operating systems; minimally, it
ﬁnally gave some good reasons why address-space based prote ction could be useful in a modern OS.
[W10] “Hard Disk Driver”
Washington State Course Homepage
Available: http://eecs.wsu.edu/˜cs460/cs560/HDdriver.html
A nice summary of a simple IDE disk drive’s interface and how t o build a device driver for it.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 439

37
Hard Disk Drives
The last chapter introduced the general concept of an I/O dev ice and
showed you how the OS might interact with such a beast. In this chapter,
we dive into more detail about one device in particular: the hard disk
drive. These drives have been the main form of persistent data stor age in
computer systems for decades and much of the development of ﬁ le sys-
tem technology (coming soon) is predicated on their behavio r. Thus, it
is worth understanding the details of a disk’s operation bef ore building
the ﬁle system software that manages it. Many of these detail s are avail-
able in excellent papers by Ruemmler and Wilkes [RW92] and An derson,
Dykes, and Riedel [ADR03].
CRUX : H OW TO STORE AND ACCESS DATA ON DISK
How do modern hard-disk drives store data? What is the interf ace?
How is the data actually laid out and accessed? How does disk s chedul-
ing improve performance?
37.1 The Interface
Let’s start by understanding the interface to a modern disk d rive. The
basic interface for all modern drives is straightforward. The drive consists
of a large number of sectors (512-byte blocks), each of which can be read
or written. The sectors are numbered from 0 to n − 1 on a disk with n
sectors. Thus, we can view the disk as an array of sectors; 0 to n − 1 is
thus the address space of the drive.
Multi-sector operations are possible; indeed, many ﬁle sys tems will
read or write 4KB at a time (or more). However, when updating t he
disk, the only guarantee drive manufactures make is that a si ngle 512-
byte write is atomic (i.e., it will either complete in its entirety or it won’t
complete at all); thus, if an untimely power loss occurs, onl y a portion of
a larger write may complete (sometimes called a torn write).
403

## Page 440

404 HARD DISK DRIVES
0
11
1098
7
6
5
4 3 2
1
Spindle
Figure 37.1: A Disk With Just A Single T rack
There are some assumptions most clients of disk drives make, but
that are not speciﬁed directly in the interface; Schlosser a nd Ganger have
called this the “unwritten contract” of disk drives [SG04]. Speciﬁcally ,
one can usually assume that accessing two blocks that are near one-another
within the drive’s address space will be faster than accessi ng two blocks
that are far apart. One can also usually assume that accessin g blocks in
a contiguous chunk (i.e., a sequential read or write) is the f astest access
mode, and usually much faster than any more random access pat tern.
37.2 Basic Geometry
Let’s start to understand some of the components of a modern d isk.
We start with a platter, a circular hard surface on which data is stored
persistently by inducing magnetic changes to it. A disk may h ave one
or more platters; each platter has 2 sides, each of which is ca lled a sur-
face. These platters are usually made of some hard material (such as
aluminum), and then coated with a thin magnetic layer that en ables the
drive to persistently store bits even when the drive is power ed off.
The platters are all bound together around the spindle, which is con-
nected to a motor that spins the platters around (while the dr ive is pow-
ered on) at a constant (ﬁxed) rate. The rate of rotation is often measured in
rotations per minute (RPM) , and typical modern values are in the 7,200
RPM to 15,000 RPM range. Note that we will often be interested in the
time of a single rotation, e.g., a drive that rotates at 10,00 0 RPM means
that a single rotation takes about 6 milliseconds (6 ms).
Data is encoded on each surface in concentric circles of sect ors; we call
one such concentric circle a track. A single surface contains many thou-
sands and thousands of tracks, tightly packed together, wit h hundreds of
tracks ﬁtting into the width of a human hair.
To read and write from the surface, we need a mechanism that al lows
us to either sense (i.e., read) the magnetic patterns on the d isk or to in-
duce a change in (i.e., write) them. This process of reading a nd writing is
accomplished by the disk head; there is one such head per surface of the
drive. The disk head is attached to a single disk arm, which moves across
the surface to position the head over the desired track.
37.3 A Simple Disk Drive
Let’s understand how disks work by building up a model one tra ck at
a time. Assume we have a simple disk with a single track (Figur e 37.1).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

