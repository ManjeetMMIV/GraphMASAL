# Document: operating_systems_three_easy_pieces (Pages 121 to 160)

## Page 121

SCHEDULING : P ROPORTIONAL SHARE 85
TIP : U SE TICKETS TO REPRESENT SHARES
One of the most powerful (and basic) mechanisms in the design of lottery
(and stride) scheduling is that of the ticket. The ticket is used to represent
a process’s share of the CPU in these examples, but can be appl ied much
more broadly . For example, in more recent work on virtual memory man-
agement for hypervisors, Waldspurger shows how tickets can be used to
represent a guest operating system’s share of memory [W02]. Thus, if you
are ever in need of a mechanism to represent a proportion of ow nership,
this concept just might be ... (wait for it) ... the ticket.
9.2 Ticket Mechanisms
Lottery scheduling also provides a number of mechanisms to m anip-
ulate tickets in different and sometimes useful ways. One wa y is with
the concept of ticket currency. Currency allows a user with a set of tick-
ets to allocate tickets among their own jobs in whatever curr ency they
would like; the system then automatically converts said cur rency into the
correct global value.
For example, assume users A and B have each been given 100 tick ets.
User A is running two jobs, A1 and A2, and gives them each 500 ti ckets
(out of 1000 total) in User A’s own currency . User B is running only 1 job
and gives it 10 tickets (out of 10 total). The system will conv ert A1’s and
A2’s allocation from 500 each in A’s currency to 50 each in the global cur-
rency; similarly , B1’s 10 tickets will be converted to 100 tickets. The lottery
will then be held over the global ticket currency (200 total) to determine
which job runs.
User A -> 500 (A’s currency) to A1 -> 50 (global currency)
-> 500 (A’s currency) to A2 -> 50 (global currency)
User B -> 10 (B’s currency) to B1 -> 100 (global currency)
Another useful mechanism is ticket transfer. With transfers, a process
can temporarily hand off its tickets to another process. Thi s ability is
especially useful in a client/server setting, where a clien t process sends
a message to a server asking it to do some work on the client’s b ehalf.
To speed up the work, the client can pass the tickets to the ser ver and
thus try to maximize the performance of the server while the s erver is
handling the client’s request. When ﬁnished, the server the n transfers the
tickets back to the client and all is as before.
Finally , ticket inﬂation can sometimes be a useful technique. With
inﬂation, a process can temporarily raise or lower the numbe r of tickets
it owns. Of course, in a competitive scenario with processes that do not
trust one another, this makes little sense; one greedy proce ss could give
itself a vast number of tickets and take over the machine. Rat her, inﬂation
can be applied in an environment where a group of processes tr ust one
another; in such a case, if any one process knows it needs more CPU time,
it can boost its ticket value as a way to reﬂect that need to the system, all
without communicating with any other processes.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 122

86 SCHEDULING : P ROPORTIONAL SHARE
1 // counter: used to track if we’ve found the winner yet
2 int counter = 0;
3
4 // winner: use some call to a random number generator to
5 // get a value, between 0 and the total # of tickets
6 int winner = getrandom(0, totaltickets);
7
8 // current: use this to walk through the list of jobs
9 node_t *current = head;
10
11 // loop until the sum of ticket values is > the winner
12 while (current) {
13 counter = counter + current->tickets;
14 if (counter > winner)
15 break; // found the winner
16 current = current->next;
17 }
18 // ’current’ is the winner: schedule it...
Figure 9.1: Lottery Scheduling Decision Code
9.3 Implementation
Probably the most amazing thing about lottery scheduling is the sim-
plicity of its implementation. All you need is a good random n umber
generator to pick the winning ticket, a data structure to tra ck the pro-
cesses of the system (e.g., a list), and the total number of ti ckets.
Let’s assume we keep the processes in a list. Here is an exampl e com-
prised of three processes, A, B, and C, each with some number o f tickets.
head Job:A
Tix:100
Job:B
Tix:50
Job:C
Tix:250 NULL
To make a scheduling decision, we ﬁrst have to pick a random number
(the winner) from the total number of tickets (400) 2 Let’s say we pick the
number 300. Then, we simply traverse the list, with a simple c ounter
used to help us ﬁnd the winner (Figure 9.1).
The code walks the list of processes, adding each ticket value to counter
until the value exceeds winner. Once that is the case, the current list el-
ement is the winner. With our example of the winning ticket be ing 300,
the following takes place. First, counter is incremented to 100 to ac-
count for A’s tickets; because 100 is less than 300, the loop c ontinues.
Then counter would be updated to 150 (B’s tickets), still less than 300
and thus again we continue. Finally , counter is updated to 400 (clearly
greater than 300), and thus we break out of the loop with current point-
ing at C (the winner).
To make this process most efﬁcient, it might generally be bes t to or-
ganize the list in sorted order, from the highest number of ti ckets to the
2Surprisingly , as pointed out by Bj ¨ orn Lindberg, this can be challenging to do
correctly; for more details, see http://stackoverflow.com/questions/2509679/
how-to-generate-a-random-number-from-within-a-range .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 123

SCHEDULING : P ROPORTIONAL SHARE 87
1 10 100 1000
0.0
0.2
0.4
0.6
0.8
1.0
Job Length
Unfairness (Average)
Figure 9.2: Lottery Fairness Study
lowest. The ordering does not affect the correctness of the a lgorithm;
however, it does ensure in general that the fewest number of l ist itera-
tions are taken, especially if there are a few processes that possess most
of the tickets.
9.4 An Example
To make the dynamics of lottery scheduling more understanda ble, we
now perform a brief study of the completion time of two jobs co mpeting
against one another, each with the same number of tickets (10 0) and same
run time (R, which we will vary).
In this scenario, we’d like for each job to ﬁnish at roughly th e same
time, but due to the randomness of lottery scheduling, somet imes one
job ﬁnishes before the other. To quantify this difference, w e deﬁne a
simple unfairness metric , U which is simply the time the ﬁrst job com-
pletes divided by the time that the second job completes. For example,
if R = 10 , and the ﬁrst job ﬁnishes at time 10 (and the second job at 20),
U = 10
20 = 0 .5. When both jobs ﬁnish at nearly the same time, U will be
quite close to 1. In this scenario, that is our goal: a perfect ly fair scheduler
would achieve U = 1.
Figure 9.2 plots the average unfairness as the length of the two jobs
(R) is varied from 1 to 1000 over thirty trials (results are gene rated via the
simulator provided at the end of the chapter). As you can see f rom the
graph, when the job length is not very long, average unfairne ss can be
quite severe. Only as the jobs run for a signiﬁcant number of t ime slices
does the lottery scheduler approach the desired outcome.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 124

88 SCHEDULING : P ROPORTIONAL SHARE
9.5 How To Assign Tickets?
One problem we have not addressed with lottery scheduling is : how
to assign tickets to jobs? This problem is a tough one, becaus e of course
how the system behaves is strongly dependent on how tickets a re allo-
cated. One approach is to assume that the users know best; in s uch a
case, each user is handed some number of tickets, and a user ca n allocate
tickets to any jobs they run as desired. However, this soluti on is a non-
solution: it really doesn’t tell you what to do. Thus, given a set of jobs,
the “ticket-assignment problem” remains open.
9.6 Why Not Deterministic?
You might also be wondering: why use randomness at all? As we s aw
above, while randomness gets us a simple (and approximately correct)
scheduler, it occasionally will not deliver the exact right proportions, es-
pecially over short time scales. For this reason, Waldspurg er invented
stride scheduling, a deterministic fair-share scheduler [W95].
Stride scheduling is also straightforward. Each job in the s ystem has
a stride, which is inverse in proportion to the number of tick ets it has. In
our example above, with jobs A, B, and C, with 100, 50, and 250 t ickets,
respectively , we can compute the stride of each by dividing s ome large
number by the number of tickets each process has been assigne d. For
example, if we divide 10,000 by each of those ticket values, w e obtain
the following stride values for A, B, and C: 100, 200, and 40. W e call
this value the stride of each process; every time a process runs, we will
increment a counter for it (called its pass value) by its stride to track its
global progress.
The scheduler then uses the stride and pass to determine whic h pro-
cess should run next. The basic idea is simple: at any given ti me, pick
the process to run that has the lowest pass value so far; when y ou run
a process, increment its pass counter by its stride. A pseudo code imple-
mentation is provided by Waldspurger [W95]:
current = remove_min(queue); // pick client with minimum pa ss
schedule(current); // use resource for quantum
current->pass += current->stride; // compute next pass usi ng stride
insert(queue, current); // put back into the queue
In our example, we start with three processes (A, B, and C), wi th stride
values of 100, 200, and 40, and all with pass values initially at 0. Thus, at
ﬁrst, any of the processes might run, as their pass values are equally low .
Assume we pick A (arbitrarily; any of the processes with equa l low pass
values can be chosen). A runs; when ﬁnished with the time slic e, we
update its pass value to 100. Then we run B, whose pass value is then
set to 200. Finally , we run C, whose pass value is incremented to 40. At
this point, the algorithm will pick the lowest pass value, wh ich is C’s, and
run it, updating its pass to 80 (C’s stride is 40, as you recall ). Then C will
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 125

SCHEDULING : P ROPORTIONAL SHARE 89
Pass(A) Pass(B) Pass(C) Who Runs?
(stride=100) (stride=200) (stride=40)
0 0 0 A
100 0 0 B
100 200 0 C
100 200 40 C
100 200 80 C
100 200 120 A
200 200 120 C
200 200 160 C
200 200 200 ...
Table 9.1: Stride Scheduling: A T race
run again (still the lowest pass value), raising its pass to 1 20. A will run
now , updating its pass to 200 (now equal to B’s). Then C will ru n twice
more, updating its pass to 160 then 200. At this point, all pas s values are
equal again, and the process will repeat, ad inﬁnitum. Table 9.1 traces the
behavior of the scheduler over time.
As we can see from the table, C ran ﬁve times, A twice, and B just once,
exactly in proportion to their ticket values of 250, 100, and 50. Lottery
scheduling achieves the proportions probabilistically ov er time; stride
scheduling gets them exactly right at the end of each schedul ing cycle.
So you might be wondering: given the precision of stride sche duling,
why use lottery scheduling at all? Well, lottery scheduling has one nice
property that stride scheduling does not: no global state. I magine a new
job enters in the middle of our stride scheduling example abo ve; what
should its pass value be? Should it be set to 0? If so, it will mo nopolize
the CPU. With lottery scheduling, there is no global state pe r process;
we simply add a new process with whatever tickets it has, upda te the
single global variable to track how many total tickets we hav e, and go
from there. In this way , lottery makes it much easier to incor porate new
processes in a sensible manner.
9.7 Summary
We have introduced the concept of proportional-share scheduling and
brieﬂy discussed two implementations: lottery and stride s cheduling.
Lottery uses randomness in a clever way to achieve proportio nal share;
stride does so deterministically . Although both are concep tually inter-
esting, they have not achieved wide-spread adoption as CPU s chedulers
for a variety of reasons. One is that such approaches do not pa rticularly
mesh well with I/O [AC97]; another is that they leave open thehard prob-
lem of ticket assignment, i.e., how do you know how many ticke ts your
browser should be allocated? General-purpose schedulers ( such as the
MLFQ we discussed previously , and other similar Linux sched ulers) do
so more gracefully and thus are more widely deployed.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 126

90 SCHEDULING : P ROPORTIONAL SHARE
As a result, proportional-share schedulers are more useful in domains
where some of these problems (such as assignment of shares) a re rela-
tively easy to solve. For example, in a virtualized data center, where you
might like to assign one-quarter of your CPU cycles to the Win dows VM
and the rest to your base Linux installation, proportional s haring can be
simple and effective. See Waldspurger [W02] for further det ails on how
such a scheme is used to proportionally share memory in VMWar e’s ESX
Server.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 127

SCHEDULING : P ROPORTIONAL SHARE 91
References
[AC97] “Extending Proportional-Share Scheduling to a Netw ork of Workstations”
Andrea C. Arpaci-Dusseau and David E. Culler
PDPTA’97, June 1997
A paper by one of the authors on how to extend proportional-sh are scheduling to work better in a
clustered environment.
[D82] “Why Numbering Should Start At Zero”
Edsger Dijkstra, August 1982
http://www.cs.utexas.edu/users/EWD/ewd08xx/EWD831.PDF
A short note from E. Dijkstra, one of the pioneers of computer science. We’ll be hearing much more
on this guy in the section on Concurrency. In the meanwhile, e njoy this note, which includes this
motivating quote: “One of my colleagues – not a computing sci entist – accused a number of younger
computing scientists of ’pedantry’ because they started nu mbering at zero.” The note explains why
doing so is logical.
[KL88] “A Fair Share Scheduler”
J. Kay and P . Lauder
CACM, V olume 31 Issue 1, January 1988
An early reference to a fair-share scheduler.
[WW94] “Lottery Scheduling: Flexible Proportional-Share Resource Management”
Carl A. Waldspurger and William E. Weihl
OSDI ’94, November 1994
The landmark paper on lottery scheduling that got the system s community re-energized about schedul-
ing, fair sharing, and the power of simple randomized algori thms.
[W95] “Lottery and Stride Scheduling: Flexible
Proportional-Share Resource Management”
Carl A. Waldspurger
Ph.D. Thesis, MIT, 1995
The award-winning thesis of Waldspurger’s that outlines lo ttery and stride scheduling. If you’re think-
ing of writing a Ph.D. dissertation at some point, you should always have a good example around, to
give you something to strive for: this is such a good one.
[W02] “Memory Resource Management in VMware ESX Server”
Carl A. Waldspurger
OSDI ’02, Boston, Massachusetts
The paper to read about memory management in VMMs (a.k.a., hy pervisors). In addition to being
relatively easy to read, the paper contains numerous cool id eas about this new type of VMM-level
memory management.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 128

92 SCHEDULING : P ROPORTIONAL SHARE
Homework
This program, lottery.py, allows you to see how a lottery scheduler
works. See the README for details.
Questions
1. Compute the solutions for simulations with 3 jobs and rand om seeds
of 1, 2, and 3.
2. Now run with two speciﬁc jobs: each of length 10, but one (jo b 0)
with just 1 ticket and the other (job 1) with 100 (e.g.,-l 10:1,10:100 ).
What happens when the number of tickets is so imbalanced? Wil l
job 0 ever run before job 1 completes? How often? In general, w hat
does such a ticket imbalance do to the behavior of lottery sch edul-
ing?
3. When running with two jobs of length 100 and equal ticket al loca-
tions of 100 (-l 100:100,100:100 ), how unfair is the scheduler?
Run with some different random seeds to determine the (probabilis-
tic) answer; let unfairness be determined by how much earlie r one
job ﬁnishes than the other.
4. How does your answer to the previous question change as the quan-
tum size ( -q) gets larger?
5. Can you make a version of the graph that is found in the chapt er?
What else would be worth exploring? How would the graph look
with a stride scheduler?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 129

10
Multiprocessor Scheduling (Advanced)
This chapter will introduce the basics of multiprocessor scheduling . As
this topic is relatively advanced, it may be best to cover it after you have
studied the topic of concurrency in some detail (i.e., the se cond major
“easy piece” of the book).
After years of existence only in the high-end of the computin g spec-
trum, multiprocessor systems are increasingly commonplace, and have
found their way into desktop machines, laptops, and even mob ile de-
vices. The rise of the multicore processor, in which multiple CPU cores
are packed onto a single chip, is the source of this prolifera tion; these
chips have become popular as computer architects have had a d ifﬁcult
time making a single CPU much faster without using (way) too m uch
power. And thus we all now have a few CPUs available to us, whic h is a
good thing, right?
Of course, there are many difﬁculties that arise with the arrival of more
than a single CPU. A primary one is that a typical application (i.e., some C
program you wrote) only uses a single CPU; adding more CPUs do es not
make that single application run faster. To remedy this prob lem, you’ll
have to rewrite your application to run in parallel, perhaps using threads
(as discussed in great detail in the second piece of this book ). Multi-
threaded applications can spread work across multiple CPUs and thus
run faster when given more CPU resources.
ASIDE : ADVANCED CHAPTERS
Advanced chapters require material from a broad swath of the book to
truly understand, while logically ﬁtting into a section tha t is earlier than
said set of prerequisite materials. For example, this chapt er on multipro-
cessor scheduling makes much more sense if you’ve ﬁrst read t he middle
piece on concurrency; however, it logically ﬁts into the par t of the book
on virtualization (generally) and CPU scheduling (speciﬁc ally). Thus, it
is recommended such chapters be covered out of order; in this case, after
the second piece of the book.
93

## Page 130

94 MULTIPROCESSOR SCHEDULING (A DVANCED )
Memory
CPU
Cache
Figure 10.1: Single CPU With Cache
Beyond applications, a new problem that arises for the opera ting sys-
tem is (not surprisingly!) that of multiprocessor scheduling . Thus far
we’ve discussed a number of principles behind single-proce ssor schedul-
ing; how can we extend those ideas to work on multiple CPUs? Wh at
new problems must we overcome? And thus, our problem:
CRUX : H OW TO SCHEDULE JOBS ON MULTIPLE CPU S
How should the OS schedule jobs on multiple CPUs? What new pro b-
lems arise? Do the same old techniques work, or are new ideas r equired?
10.1 Background: Multiprocessor Architecture
To understand the new issues surrounding multiprocessor sc hedul-
ing, we have to understand a new and fundamental difference b etween
single-CPU hardware and multi-CPU hardware. This differen ce centers
around the use of hardware caches (e.g., Figure 10.1), and exactly how
data is shared across multiple processors. We now discuss th is issue fur-
ther, at a high level. Details are available elsewhere [CSG9 9], in particular
in an upper-level or perhaps graduate computer architectur e course.
In a system with a single CPU, there are a hierarchy of hardware
caches that in general help the processor run programs faster. Cach es
are small, fast memories that (in general) hold copies of popular data that
is found in the main memory of the system. Main memory , in cont rast,
holds all of the data, but access to this larger memory is slower. By kee p-
ing frequently accessed data in a cache, the system can make t he large,
slow memory appear to be a fast one.
As an example, consider a program that issues an explicit load instruc-
tion to fetch a value from memory , and a simple system with only a single
CPU; the CPU has a small cache (say 64 KB) and a large main memor y .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 131

MULTIPROCESSOR SCHEDULING (A DVANCED ) 95
Memory
CPU CPU
Cache Cache
Bus
Figure 10.2: Two CPUs With Caches Sharing Memory
The ﬁrst time a program issues this load, the data resides in m ain mem-
ory , and thus takes a long time to fetch (perhaps in the tens of nanosec-
onds, or even hundreds). The processor, anticipating that t he data may
be reused, puts a copy of the loaded data into the CPU cache. If the pro-
gram later fetches this same data item again, the CPU ﬁrst che cks for it in
the cache; because it ﬁnds it there, the data is fetched much m ore quickly
(say , just a few nanoseconds), and thus the program runs fast er.
Caches are thus based on the notion of locality, of which there are
two kinds: temporal locality and spatial locality . The idea behind tem-
poral locality is that when a piece of data is accessed, it is l ikely to be
accessed again in the near future; imagine variables or even instructions
themselves being accessed over and over again in a loop. The i dea be-
hind spatial locality is that if a program accesses a data ite m at address
x, it is likely to access data items near x as well; here, think of a program
streaming through an array , or instructions being executed one after the
other. Because locality of these types exist in many program s, hardware
systems can make good guesses about which data to put in a cach e and
thus work well.
Now for the tricky part: what happens when you have multiple p ro-
cessors in a single system, with a single shared main memory , as we see
in Figure 10.2?
As it turns out, caching with multiple CPUs is much more compl i-
cated. Imagine, for example, that a program running on CPU 1 r eads
a data item (with value D) at address A; because the data is not in the
cache on CPU 1, the system fetches it from main memory , and get s the
value D. The program then modiﬁes the value at address A, just updat-
ing its cache with the new value D′; writing the data through all the way
to main memory is slow , so the system will (usually) do that la ter. Then
assume the OS decides to stop running the program and move it t o CPU
2. The program then re-reads the value at address A; there is no such data
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 132

96 MULTIPROCESSOR SCHEDULING (A DVANCED )
CPU 2’s cache, and thus the system fetches the value from main memory ,
and gets the old value D instead of the correct value D′. Oops!
This general problem is called the problem of cache coherence , and
there is a vast research literature that describes many diff erent subtleties
involved with solving the problem [SHW11]. Here, we will ski p all of the
nuance and make some major points; take a computer architect ure class
(or three) to learn more.
The basic solution is provided by the hardware: by monitorin g mem-
ory accesses, hardware can ensure that basically the “right thing” hap-
pens and that the view of a single shared memory is preserved. One way
to do this on a bus-based system (as described above) is to use an old
technique known as bus snooping [G83]; each cache pays attention to
memory updates by observing the bus that connects them to mai n mem-
ory . When a CPU then sees an update for a data item it holds in it s cache,
it will notice the change and either invalidate its copy (i.e., remove it
from its own cache) or update it (i.e., put the new value into its cache
too). Write-back caches, as hinted at above, make this more c omplicated
(because the write to main memory isn’t visible until later) , but you can
imagine how the basic scheme might work.
10.2 Don’t Forget Synchronization
Given that the caches do all of this work to provide coherence , do pro-
grams (or the OS itself) have to worry about anything when the y access
shared data? The answer, unfortunately , is yes, and is docum ented in
great detail in the second piece of this book on the topic of co ncurrency .
While we won’t get into the details here, we’ll sketch/revie w some of the
basic ideas here (assuming you’re familiar with concurrenc y).
When accessing (and in particular, updating) shared data it ems or
structures across CPUs, mutual exclusion primitives (such as locks) should
likely be used to guarantee correctness (other approaches, such as build-
ing lock-free data structures, are complex and only used on occasion;
see the chapter on deadlock in the piece on concurrency for de tails). For
example, assume we have a shared queue being accessed on mult iple
CPUs concurrently . Without locks, adding or removing eleme nts from
the queue concurrently will not work as expected, even with t he under-
lying coherence protocols; one needs locks to atomically up date the data
structure to its new state.
To make this more concrete, imagine this code sequence, which is used
to remove an element from a shared linked list, as we see in Fig ure 10.3.
Imagine if threads on two CPUs enter this routine at the same t ime. If
Thread 1 executes the ﬁrst line, it will have the current valu e of head
stored in its tmp variable; if Thread 2 then executes the ﬁrst line as well,
it also will have the same value of head stored in its own private tmp
variable ( tmp is allocated on the stack, and thus each thread will have
its own private storage for it). Thus, instead of each thread removing
an element from the head of the list, each thread will try to re move the
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 133

MULTIPROCESSOR SCHEDULING (A DVANCED ) 97
1 typedef struct __Node_t {
2 int value;
3 struct __Node_t *next;
4 } Node_t;
5
6 int List_Pop() {
7 Node_t *tmp = head; // remember old head ...
8 int value = head->value; // ... and its value
9 head = head->next; // advance head to next pointer
10 free(tmp); // free old head
11 return value; // return value at head
12 }
Figure 10.3: Simple List Delete Code
same head element, leading to all sorts of problems (such as a n attempted
double free of the head element at line 4, as well as potential ly returning
the same data value twice).
The solution, of course, is to make such routines correct via lock-
ing. In this case, allocating a simple mutex (e.g., pthread
mutex t
m;) and then adding a lock(&m) at the beginning of the routine and
an unlock(&m) at the end will solve the problem, ensuring that the code
will execute as desired. Unfortunately , as we will see, suchan approach is
not without problems, in particular with regards to perform ance. Speciﬁ-
cally , as the number of CPUs grows, access to a synchronized shared data
structure becomes quite slow .
10.3 One Final Issue: Cache Afﬁnity
One ﬁnal issue arises in building a multiprocessor cache sch eduler,
known as cache afﬁnity. This notion is simple: a process, when run on a
particular CPU, builds up a fair bit of state in the caches (an d TLBs) of the
CPU. The next time the process runs, it is often advantageous to run it on
the same CPU, as it will run faster if some of its state is alrea dy present in
the caches on that CPU. If, instead, one runs a process on a dif ferent CPU
each time, the performance of the process will be worse, as it will have to
reload the state each time it runs (note it will run correctly on a different
CPU thanks to the cache coherence protocols of the hardware) . Thus, a
multiprocessor scheduler should consider cache afﬁnity wh en making its
scheduling decisions, perhaps preferring to keep a process on the same
CPU if at all possible.
10.4 Single-Queue Scheduling
With this background in place, we now discuss how to build a sc hed-
uler for a multiprocessor system. The most basic approach is to simply
reuse the basic framework for single processor scheduling, by putting all
jobs that need to be scheduled into a single queue; we call thi s single-
queue multiprocessor scheduling or SQMS for short. This approach
has the advantage of simplicity; it does not require much wor k to take an
existing policy that picks the best job to run next and adapt i t to work on
more than one CPU (where it might pick the best two jobs to run, if there
are two CPUs, for example).
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 134

98 MULTIPROCESSOR SCHEDULING (A DVANCED )
However, SQMS has obvious shortcomings. The ﬁrst problem is a lack
of scalability. To ensure the scheduler works correctly on multiple CPUs,
the developers will have inserted some form of locking into the code, as
described above. Locks ensure that when SQMS code accesses t he single
queue (say , to ﬁnd the next job to run), the proper outcome ari ses.
Locks, unfortunately , can greatly reduce performance, par ticularly as
the number of CPUs in the systems grows [A91]. As contention f or such
a single lock increases, the system spends more and more time in lock
overhead and less time doing the work the system should be doi ng (note:
it would be great to include a real measurement of this in here someday).
The second main problem with SQMS is cache afﬁnity . For examp le,
let us assume we have ﬁve jobs to run (A, B, C, D, E) and four processors.
Our scheduling queue thus looks like this:
Queue A B C D E NULL
Over time, assuming each job runs for a time slice and then ano ther
job is chosen, here is a possible job schedule across CPUs:
CPU 3
CPU 2
CPU 1
CPU 0
D C B A E
C B A E D
B A E D C
A E D C B
 ... (repeat) ...
 ... (repeat) ...
 ... (repeat) ...
 ... (repeat) ...
Because each CPU simply picks the next job to run from the glob ally-
shared queue, each job ends up bouncing around from CPU to CPU , thus
doing exactly the opposite of what would make sense from the s tand-
point of cache afﬁnity .
To handle this problem, most SQMS schedulers include some ki nd of
afﬁnity mechanism to try to make it more likely that process will continue
to run on the same CPU if possible. Speciﬁcally , one might pro vide afﬁn-
ity for some jobs, but move others around to balance load. For example,
imagine the same ﬁve jobs scheduled as follows:
CPU 3
CPU 2
CPU 1
CPU 0
D D D D E
C C C E C
B B E B B
A E A A A
 ... (repeat) ...
 ... (repeat) ...
 ... (repeat) ...
 ... (repeat) ...
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 135

MULTIPROCESSOR SCHEDULING (A DVANCED ) 99
In this arrangement, jobs A through D are not moved across proces-
sors, with only job E migrating from CPU to CPU, thus preserving afﬁn-
ity for most. You could then decide to migrate a different job the next
time through, thus achieving some kind of afﬁnity fairness a s well. Im-
plementing such a scheme, however, can be complex.
Thus, we can see the SQMS approach has its strengths and weak-
nesses. It is straightforward to implement given an existin g single-CPU
scheduler, which by deﬁnition has only a single queue. Howev er, it does
not scale well (due to synchronization overheads), and it do es not readily
preserve cache afﬁnity .
10.5 Multi-Queue Scheduling
Because of the problems caused in single-queue schedulers, some sys-
tems opt for multiple queues, e.g., one per CPU. We call this a pproach
multi-queue multiprocessor scheduling (or MQMS).
In MQMS, our basic scheduling framework consists of multiple schedul-
ing queues. Each queue will likely follow a particular sched uling disci-
pline, such as round robin, though of course any algorithm ca n be used.
When a job enters the system, it is placed on exactly one sched uling
queue, according to some heuristic (e.g., random, or pickin g one with
fewer jobs than others). Then it is scheduled essentially in dependently ,
thus avoiding the problems of information sharing and synch ronization
found in the single-queue approach.
For example, assume we have a system where there are just two C PUs
(labeled CPU 0 and CPU 1), and some number of jobs enter the sys tem:
A, B, C, and D for example. Given that each CPU has a scheduling queue
now , the OS has to decide into which queue to place each job. It might do
something like this:
Q0 A C Q1 B D
Depending on the queue scheduling policy , each CPU now has tw o
jobs to choose from when deciding what should run. For exampl e, with
round robin, the system might produce a schedule that looks like this:
CPU 1
CPU 0 A A C C A A C C A A C C
B B D D B B D D B B D D  ... 
 ... 
MQMS has a distinct advantage of SQMS in that it should be inhe r-
ently more scalable. As the number of CPUs grows, so too does t he num-
ber of queues, and thus lock and cache contention should not b ecome a
central problem. In addition, MQMS intrinsically provides cache afﬁnity;
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 136

100 MULTIPROCESSOR SCHEDULING (A DVANCED )
jobs stay on the same CPU and thus reap the advantage of reusin g cached
contents therein.
But, if you’ve been paying attention, you might see that we ha ve a new
problem, which is fundamental in the multi-queue based appr oach: load
imbalance. Let’s assume we have the same set up as above (four jobs,
two CPUs), but then one of the jobs (say C) ﬁnishes. We now have the
following scheduling queues:
Q0 A Q1 B D
If we then run our round-robin policy on each queue of the syst em, we
will see this resulting schedule:
CPU 1
CPU 0 A A A A A A A A A A A A
B B D D B B D D B B D D  ... 
 ... 
As you can see from this diagram, A gets twice as much CPU as B and
D, which is not the desired outcome. Even worse, let’s imagine that both
A and C ﬁnish, leaving just jobs B and D in the system. The scheduling
queues will look like this:
Q0 Q1 B D
As a result, CPU 0 will be left idle! (insert dramatic and sinister music here)
And hence our CPU usage timeline looks sad:
CPU 0
CPU 1
B B D D B B D D B B D D  ... 
So what should a poor multi-queue multiprocessor schedulerdo? How
can we overcome the insidious problem of load imbalance and d efeat the
evil forces of ... the Decepticons 1? How do we stop asking questions that
are hardly relevant to this otherwise wonderful book?
1Little known fact is that the home planet of Cybertron was des troyed by bad CPU
scheduling decisions. And now let that be the ﬁrst and last re ference to Transformers in this
book, for which we sincerely apologize.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 137

MULTIPROCESSOR SCHEDULING (A DVANCED ) 101
CRUX : H OW TO DEAL WITH LOAD IMBALANCE
How should a multi-queue multiprocessor scheduler handle l oad im-
balance, so as to better achieve its desired scheduling goal s?
The obvious answer to this query is to move jobs around, a tech nique
which we (once again) refer to as migration. By migrating a job from one
CPU to another, true load balance can be achieved.
Let’s look at a couple of examples to add some clarity . Once ag ain, we
have a situation where one CPU is idle and the other has some jo bs.
Q0 Q1 B D
In this case, the desired migration is easy to understand: the OS should
simply move one of B or D to CPU 0. The result of this single job migra-
tion is evenly balanced load and everyone is happy .
A more tricky case arises in our earlier example, where A was left
alone on CPU 0 and B and D were alternating on CPU 1:
Q0 A Q1 B D
In this case, a single migration does not solve the problem. W hat
would you do in this case? The answer, alas, is continuous mig ration
of one or more jobs. One possible solution is to keep switchin g jobs, as
we see in the following timeline. In the ﬁgure, ﬁrst A is alone on CPU 0,
and B and D alternate on CPU 1. After a few time slices, B is moved to
compete with A on CPU 0, while D enjoys a few time slices alone on CPU
1. And thus load is balanced:
CPU 0
CPU 1
A A A A B A B A B B B B
B D B D D D D D A D A D  ... 
 ... 
Of course, many other possible migration patterns exist. Bu t now for
the tricky part: how should the system decide to enact such a m igration?
One basic approach is to use a technique known as work stealing
[FLR98]. With a work-stealing approach, a (source) queue th at is low
on jobs will occasionally peek at another (target) queue, to see how full
it is. If the target queue is (notably) more full than the sour ce queue, the
source will “steal” one or more jobs from the target to help ba lance load.
Of course, there is a natural tension in such an approach. If y ou look
around at other queues too often, you will suffer from high ov erhead and
have trouble scaling, which was the entire purpose of implem enting the
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 138

102 MULTIPROCESSOR SCHEDULING (A DVANCED )
multiple queue scheduling in the ﬁrst place! If, on the other hand, you
don’t look at other queues very often, you are in danger of suf fering from
severe load balances. Finding the right threshold remains, as is common
in system policy design, a black art.
10.6 Linux Multiprocessor Schedulers
Interestingly , in the Linux community , no common solution h as ap-
proached to building a multiprocessor scheduler. Over time , three dif-
ferent schedulers arose: the O(1) scheduler, the Completel y Fair Sched-
uler (CFS), and the BF Scheduler (BFS) 2. See Meehean’s dissertation for
an excellent overview of the strengths and weaknesses of sai d schedulers
[M11]; here we just summarize a few of the basics.
Both O(1) and CFS uses multiple queues, whereas BFS uses a sin gle
queue, showing that both approaches can be successful. Of co urse, there
are many other details which separate these schedulers. For example, the
O(1) scheduler is a priority-based scheduler (similar to th e MLFQ dis-
cussed before), changing a process’s priority over time and then schedul-
ing those with highest priority in order to meet various sche duling objec-
tives; interactivity is a particular focus. CFS, in contras t, is a deterministic
proportional-share approach (more like Stride scheduling , as discussed
earlier). BFS, the only single-queue approach among the thr ee, is also
proportional-share, but based on a more complicated scheme known as
Earliest Eligible Virtual Deadline First (EEVDF) [SA96]. R ead more about
these modern algorithms on your own; you should be able to und erstand
how they work now!
10.7 Summary
We have seen various approaches to multiprocessor scheduli ng. The
single-queue approach (SQMS) is rather straightforward to build and bal-
ances load well but inherently has difﬁculty with scaling to many pro-
cessors and cache afﬁnity . The multiple-queue approach (MQ MS) scales
better and handles cache afﬁnity well, but has trouble with l oad imbal-
ance and is more complicated. Whichever approach you take, t here is no
simple answer: building a general purpose scheduler remain s a daunting
task, as small code changes can lead to large behavioral diff erences. Only
undertake such an exercise if you know exactly what you are do ing, or,
at least, are getting paid a large amount of money to do so.
2Look up what BF stands for on your own; be forewarned, it is not for the faint of heart.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 139

MULTIPROCESSOR SCHEDULING (A DVANCED ) 103
References
[A90] “The Performance of Spin Lock Alternatives for Shared -Memory Multiprocessors”
Thomas E. Anderson
IEEE TPDS V olume 1:1, January 1990
A classic paper on how different locking alternatives do and don’t scale. By Tom Anderson, very well
known researcher in both systems and networking. And author of a very ﬁne OS textbook, we must say.
[B+10] “An Analysis of Linux Scalability to Many Cores Abstr act”
Silas Boyd-Wickizer, Austin T. Clements, Yandong Mao, Aleksey Pesterev , M. Frans Kaashoek,
Robert Morris, Nickolai Zeldovich
OSDI ’10, Vancouver, Canada, October 2010
A terriﬁc modern paper on the difﬁculties of scaling Linux to many cores.
[CSG99] “Parallel Computer Architecture: A Hardware/Soft ware Approach”
David E. Culler, Jaswinder Pal Singh, and Anoop Gupta
Morgan Kaufmann, 1999
A treasure ﬁlled with details about parallel machines and al gorithms. As Mark Hill humorously ob-
serves on the jacket, the book contains more information tha n most research papers.
[FLR98] “The Implementation of the Cilk-5 Multithreaded La nguage”
Matteo Frigo, Charles E. Leiserson, Keith Randall
PLDI ’98, Montreal, Canada, June 1998
Cilk is a lightweight language and runtime for writing paral lel programs, and an excellent example of
the work-stealing paradigm.
[G83] “Using Cache Memory To Reduce Processor-Memory Trafﬁ c”
James R. Goodman
ISCA ’83, Stockholm, Sweden, June 1983
The pioneering paper on how to use bus snooping, i.e., paying attention to requests you see on the bus, to
build a cache coherence protocol. Goodman’s research over m any years at Wisconsin is full of cleverness,
this being but one example.
[M11] “Towards Transparent CPU Scheduling”
Joseph T. Meehean
Doctoral Dissertation at University of Wisconsin–Madison , 2011
A dissertation that covers a lot of the details of how modern L inux multiprocessor scheduling works.
Pretty awesome! But, as co-advisors of Joe’s, we may be a bit b iased here.
[SHW11] “A Primer on Memory Consistency and Cache Coherence ”
Daniel J. Sorin, Mark D. Hill, and David A. Wood
Synthesis Lectures in Computer Architecture
Morgan and Claypool Publishers, May 2011
A deﬁnitive overview of memory consistency and multiproces sor caching. Required reading for anyone
who likes to know way too much about a given topic.
[SA96] “Earliest Eligible Virtual Deadline First: A Flexib le and Accurate Mechanism for Pro-
portional Share Resource Allocation”
Ion Stoica and Hussein Abdel-Wahab
Technical Report TR-95-22, Old Dominion University , 1996
A tech report on this cool scheduling idea, from Ion Stoica, n ow a professor at U.C. Berkeley and world
expert in networking, distributed systems, and many other t hings.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 141

11
Summary Dialogue on CPU Virtualization
Professor: So, Student, did you learn anything?
Student: Well, Professor, that seems like a loaded question. I think y ou only
want me to say “yes.”
Professor: That’s true. But it’s also still an honest question. Come on, give a
professor a break, will you?
Student: OK, OK. I think I did learn a few things. First, I learned a litt le about
how the OS virtualizes the CPU. There are a bunch of important mechanisms
that I had to understand to make sense of this: traps and trap h andlers, timer
interrupts, and how the OS and the hardware have to carefully save and restore
state when switching between processes.
Professor: Good, good!
Student: All those interactions do seem a little complicated though; how can I
learn more?
Professor: Well, that’s a good question. I think there is no substitute f or doing;
just reading about these things doesn’t quite give you the pr oper sense. Do the
class projects and I bet by the end it will all kind of make sens e.
Student: Sounds good. What else can I tell you?
Professor: Well, did you get some sense of the philosophy of the OS in your
quest to understand its basic machinery?
Student: Hmm... I think so. It seems like the OS is fairly paranoid. It w ants
to make sure it stays in charge of the machine. While it wants a program to run
as efﬁciently as possible (and hence the whole reasoning beh ind limited direct
execution), the OS also wants to be able to say “Ah! Not so fast my friend”
in case of an errant or malicious process. Paranoia rules the day, and certainly
keeps the OS in charge of the machine. Perhaps that is why we th ink of the OS
as a resource manager.
Professor: Y es indeed – sounds like you are starting to put it together! N ice.
Student: Thanks.
105

## Page 142

106 S UMMARY DIALOGUE ON CPU V IRTUALIZATION
Professor: And what about the policies on top of those mechanisms – any in ter-
esting lessons there?
Student: Some lessons to be learned there for sure. Perhaps a little ob vious, but
obvious can be good. Like the notion of bumping short jobs to t he front of the
queue – I knew that was a good idea ever since the one time I was b uying some
gum at the store, and the guy in front of me had a credit card tha t wouldn’t work.
He was no short job, let me tell you.
Professor: That sounds oddly rude to that poor fellow. What else?
Student: Well, that you can build a smart scheduler that tries to be lik e SJF and
RR all at once – that MLFQ was pretty neat. Building up a real sc heduler seems
difﬁcult.
Professor: Indeed it is. That’s why there is still controversy to this da y over
which scheduler to use; see the Linux battles between CFS, BF S, and the O(1)
scheduler, for example. And no, I will not spell out the full n ame of BFS.
Student: And I won’t ask you to! These policy battles seem like they cou ld rage
forever; is there really a right answer?
Professor: Probably not. After all, even our own metrics are at odds: if y our
scheduler is good at turnaround time, it’s bad at response ti me, and vice versa.
As Lampson said, perhaps the goal isn’t to ﬁnd the best soluti on, but rather to
avoid disaster.
Student: That’s a little depressing.
Professor: Good engineering can be that way. And it can also be uplifting !
It’s just your perspective on it, really. I personally think being pragmatic is a
good thing, and pragmatists realize that not all problems ha ve clean and easy
solutions. Anything else that caught your fancy?
Student: I really liked the notion of gaming the scheduler; it seems li ke that
might be something to look into when I’m next running a job on A mazon’s EC2
service. Maybe I can steal some cycles from some other unsusp ecting (and more
importantly, OS-ignorant) customer!
Professor: It looks like I might have created a monster! Professor Frank enstein
is not what I’d like to be called, you know.
Student: But isn’t that the idea? T o get us excited about something, so much so
that we look into it on our own? Lighting ﬁres and all that?
Professor: I guess so. But I didn’t think it would work!
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 143

12
A Dialogue on Memory Virtualization
Student: So, are we done with virtualization?
Professor: No!
Student: Hey, no reason to get so excited; I was just asking a question. Students
are supposed to do that, right?
Professor: Well, professors do always say that, but really they mean thi s: ask
questions, if they are good questions, and you have actually put a little thought
into them.
Student: Well, that sure takes the wind out of my sails.
Professor: Mission accomplished. In any case, we are not nearly done wit h
virtualization! Rather, you have just seen how to virtualiz e the CPU, but really
there is a big monster waiting in the closet: memory. Virtual izing memory is
complicated and requires us to understand many more intrica te details about
how the hardware and OS interact.
Student: That sounds cool. Why is it so hard?
Professor: Well, there are a lot of details, and you have to keep them stra ight
in your head to really develop a mental model of what is going o n. We’ll start
simple, with very basic techniques like base/bounds, and sl owly add complexity
to tackle new challenges, including fun topics like TLBs and multi-level page
tables. Eventually, we’ll be able to describe the workings o f a fully-functional
modern virtual memory manager.
Student: Neat! Any tips for the poor student, inundated with all of thi s infor-
mation and generally sleep-deprived?
Professor: For the sleep deprivation, that’s easy: sleep more (and part y less).
For understanding virtual memory, start with this: every address generated
by a user program is a virtual address . The OS is just providing an illusion
to each process, speciﬁcally that it has its own large and pri vate memory; with
some hardware help, the OS will turn these pretend virtual ad dresses into real
physical addresses, and thus be able to locate the desired in formation.
107

## Page 144

108 A D IALOGUE ON MEMORY VIRTUALIZATION
Student: OK, I think I can remember that... (to self) every address fro m a user
program is virtual, every address from a user program is virt ual, every ...
Professor: What are you mumbling about?
Student: Oh nothing.... (awkward pause) ... Anyway, why does the OS wa nt
to provide this illusion again?
Professor: Mostly ease of use : the OS will give each program the view that it
has a large contiguous address space to put its code and data into; thus, as a
programmer, you never have to worry about things like “where should I store this
variable?” because the virtual address space of the program is large and has lots
of room for that sort of thing. Life, for a programmer, become s much more tricky
if you have to worry about ﬁtting all of your code data into a sm all, crowded
memory.
Student: Why else?
Professor: Well, isolation and protection are big deals, too. We don’t want
one errant program to be able to read, or worse, overwrite, so me other program’s
memory, do we?
Student: Probably not. Unless it’s a program written by someone you do n’t
like.
Professor: Hmmm.... I think we might need to add a class on morals and ethi cs
to your schedule for next semester. Perhaps OS class isn’t ge tting the right mes-
sage across.
Student: Maybe we should. But remember, it’s not me who taught us that t he
proper OS response to errant process behavior is to kill the o ffending process!
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 145

13
The Abstraction: Address Spaces
In the early days, building computer systems was easy . Why , y ou ask?
Because users didn’t expect much. It is those darned users wi th their
expectations of “ease of use”, “high performance”, “reliab ility”, etc., that
really have led to all these headaches. Next time you meet one of those
computer users, thank them for all the problems they have cau sed.
13.1 Early Systems
From the perspective of memory , early machines didn’t provi de much
of an abstraction to users. Basically , the physical memory o f the machine
looked something like what you see in Figure 13.1.
The OS was a set of routines (a library , really) that sat in memory (start-
ing at physical address 0 in this example), and there would be one run-
ning program (a process) that currently sat in physical memo ry (starting
at physical address 64k in this example) and used the rest of m emory .
There were few illusions here, and the user didn’t expect muc h from the
OS. Life was sure easy for OS developers in those days, wasn’t it?
max
64KB
0KB
Current Program
(code, data, etc.)
Operating System
(code, data, etc.)
Figure 13.1: Operating Systems: The Early Days
109

## Page 146

110 THE ABSTRACTION : A DDRESS SPACES
512KB
448KB
384KB
320KB
256KB
192KB
128KB
64KB
0KB
(free)
(free)
(free)
(free)
Operating System
(code, data, etc.)
Process A
(code, data, etc.)
Process B
(code, data, etc.)
Process C
(code, data, etc.)
Figure 13.2: Three Processes: Sharing Memory
13.2 Multiprogramming and Time Sharing
After a time, because machines were expensive, people began to share
machines more effectively . Thus the era of multiprogramming was born
[DV66], in which multiple processes were ready to run at a giv en time,
and the OS would switch between them, for example when one dec ided
to perform an I/O. Doing so increased the effective utilization of the
CPU. Such increases in efﬁciency were particularly important in those
days where each machine cost hundreds of thousands or even mi llions of
dollars (and you thought your Mac was expensive!).
Soon enough, however, people began demanding more of machin es,
and the era of time sharing was born [S59, L60, M62, M83]. Speciﬁcally ,
many realized the limitations of batch computing, particul arly on pro-
grammers themselves [CV65], who were tired of long (and henc e ineffec-
tive) program-debug cycles. The notion of interactivity became impor-
tant, as many users might be concurrently using a machine, ea ch waiting
for (or hoping for) a timely response from their currently-e xecuting tasks.
One way to implement time sharing would be to run one process f or
a short while, giving it full access to all memory (as in Figur e 13.1), then
stop it, save all of its state to some kind of disk (including a ll of physical
memory), load some other process’s state, run it for a while, and thus
implement some kind of crude sharing of the machine [M+63].
Unfortunately , this approach has a big problem: it is way tooslow , par-
ticularly as memory grew . While saving and restoring regist er-level state
(e.g., the PC, general-purpose registers, etc.) is relativ ely fast, saving the
entire contents of memory to disk is brutally non-performant. Thus, what
we’d rather do is leave processes in memory while switching b etween
them, allowing the OS to implement time sharing efﬁciently (Figure 13.2).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 147

THE ABSTRACTION : A DDRESS SPACES 111
16KB
15KB
2KB
1KB
0KB
Stack
(free)
Heap
Program Code the code segment:
where instructions live
the heap segment:
contains malloc’d data
dynamic data structures
(it grows downward)
(it grows upward)
the stack segment:
contains local variables
arguments to routines, 
return values, etc.
Figure 13.3: An Example Address Space
In the diagram, there are three processes (A, B, and C) and eac h of
them have a small part of the 512-KB physical memory carved ou t for
them. Assuming a single CPU, the OS chooses to run one of the pr ocesses
(say A), while the others (B and C) sit in the ready queue waiti ng to run.
As time sharing became more popular, you can probably guess t hat
new demands were placed on the operating system. In particul ar, allow-
ing multiple programs to reside concurrently in memory make s protec-
tion an important issue; you don’t want a process to be able to read , or
worse, write some other process’s memory .
13.3 The Address Space
However, we have to keep those pesky users in mind, and doing s o
requires the OS to create an easy to use abstraction of physical memory .
We call this abstraction the address space, and it is the running program’s
view of memory in the system. Understanding this fundamenta l OS ab-
straction of memory is key to understanding how memory is vir tualized.
The address space of a process contains all of the memory stat e of the
running program. For example, the code of the program (the instruc-
tions) have to live in memory somewhere, and thus they are in t he ad-
dress space. The program, while it is running, uses a stack to keep track
of where it is in the function call chain as well as to allocate local variables
and pass parameters and return values to and from routines. F inally , the
heap is used for dynamically-allocated, user-managed memory , s uch as
that you might receive from a call to malloc() in C or new in an object-
oriented language such as C++ or Java. Of course, there are ot her things
in there too (e.g., statically-initialized variables), bu t for now let us just
assume those three components: code, stack, and heap.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 148

112 THE ABSTRACTION : A DDRESS SPACES
In the example in Figure 13.3, we have a tiny address space (only 16
KB)1. The program code lives at the top of the address space (start ing at
0 in this example, and is packed into the ﬁrst 1K of the address space).
Code is static (and thus easy to place in memory), so we can pla ce it at
the top of the address space and know that it won’t need any mor e space
as the program runs.
Next, we have the two regions of the address space that may gro w
(and shrink) while the program runs. Those are the heap (at th e top) and
the stack (at the bottom). We place them like this because eac h wishes to
be able to grow , and by putting them at opposite ends of the add ress
space, we can allow such growth: they just have to grow in oppo site
directions. The heap thus starts just after the code (at 1KB) and grows
downward (say when a user requests more memory via malloc()); the
stack starts at 16KB and grows upward (say when a user makes a p roce-
dure call). However, this placement of stack and heap is just a convention;
you could arrange the address space in a different way if you’ d like (as
we’ll see later, when multiple threads co-exist in an address space, no
nice way to divide the address space like this works anymore, alas).
Of course, when we describe the address space, what we are des crib-
ing is the abstraction that the OS is providing to the running program.
The program really isn’t in memory at physical addresses 0 th rough 16KB;
rather it is loaded at some arbitrary physical address(es). Examine pro-
cesses A, B, and C in Figure 13.2; there you can see how each process is
loaded into memory at a different address. And hence the prob lem:
THE CRUX : H OW TO VIRTUALIZE MEMORY
How can the OS build this abstraction of a private, potential ly large
address space for multiple running processes (all sharing m emory) on
top of a single, physical memory?
When the OS does this, we say the OS is virtualizing memory, because
the running program thinks it is loaded into memory at a parti cular ad-
dress (say 0) and has a potentially very large address space ( say 32-bits or
64-bits); the reality is quite different.
When, for example, process A in Figure 13.2 tries to perform a load
at address 0 (which we will call a virtual address ), somehow the OS, in
tandem with some hardware support, will have to make sure the load
doesn’t actually go to physical address 0 but rather to physi cal address
320KB (where A is loaded into memory). This is the key to virtu alization
of memory , which underlies every modern computer system in the world.
1We will often use small examples like this because it is a pain to represent a 32-bit address
space and the numbers start to become hard to handle.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 149

THE ABSTRACTION : A DDRESS SPACES 113
TIP : T HE PRINCIPLE OF ISOLATION
Isolation is a key principle in building reliable systems. I f two entities are
properly isolated from one another, this implies that one ca n fail with-
out affecting the other. Operating systems strive to isolat e processes from
each other and in this way prevent one from harming the other. By using
memory isolation, the OS further ensures that running progr ams cannot
affect the operation of the underlying OS. Some modern OS’s t ake iso-
lation even further, by walling off pieces of the OS from othe r pieces of
the OS. Such microkernels [BH70, R+89, S+03] thus may provide greater
reliability than typical monolithic kernel designs.
13.4 Goals
Thus we arrive at the job of the OS in this set of notes: to virtu alize
memory . The OS will not only virtualize memory , though; it wi ll do so
with style. To make sure the OS does so, we need some goals to gu ide us.
We have seen these goals before (think of the Introduction), and we’ll see
them again, but they are certainly worth repeating.
One major goal of a virtual memory (VM) system is transparency2.
The OS should implement virtual memory in a way that is invisi ble to
the running program. Thus, the program shouldn’t be aware of the fact
that memory is virtualized; rather, the program behaves as i f it has its
own private physical memory . Behind the scenes, the OS (and h ardware)
does all the work to multiplex memory among many different jo bs, and
hence implements the illusion.
Another goal of VM is efﬁciency. The OS should strive to make the
virtualization as efﬁcient as possible, both in terms of time (i.e., not mak-
ing programs run much more slowly) and space (i.e., not using too much
memory for structures needed to support virtualization). I n implement-
ing time-efﬁcient virtualization, the OS will have to rely o n hardware
support, including hardware features such as TLBs (which we will learn
about in due course).
Finally , a third VM goal is protection. The OS should make sure to
protect processes from one another as well as the OS itself from pro-
cesses. When one process performs a load, a store, or an instr uction fetch,
it should not be able to access or affect in any way the memory c ontents
of any other process or the OS itself (that is, anything outside its address
space). Protection thus enables us to deliver the property o f isolation
among processes; each process should be running in its own is olated co-
coon, safe from the ravages of other faulty or even malicious processes.
2This usage of transparency is sometimes confusing; some stu dents think that “being
transparent” means keeping everything out in the open, i.e. , what government should be like.
Here, it means the opposite: that the illusion provided by th e OS should not be visible to ap-
plications. Thus, in common usage, a transparent system is o ne that is hard to notice, not one
that responds to requests as stipulated by the Freedom of Inf ormation Act.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 150

114 THE ABSTRACTION : A DDRESS SPACES
ASIDE : EVERY ADDRESS YOU SEE IS VIRTUAL
Ever write a C program that prints out a pointer? The value you see
(some large number, often printed in hexadecimal), is a virtual address.
Ever wonder where the code of your program is found? You can pr int
that out too, and yes, if you can print it, it also is a virtual a ddress. In
fact, any address you can see as a programmer of a user-level p rogram
is a virtual address. It’s only the OS, through its tricky tec hniques of
virtualizing memory , that knows where in the physical memor y of the
machine these instructions and data values lie. So never for get: if you
print out an address in a program, it’s a virtual one, an illus ion of how
things are laid out in memory; only the OS (and the hardware) k nows the
real truth.
Here’s a little program that prints out the locations of the main() rou-
tine (where code lives), the value of a heap-allocated value returned from
malloc(), and the location of an integer on the stack:
1 #include <stdio.h>
2 #include <stdlib.h>
3 int main(int argc, char *argv[]) {
4 printf("location of code : %p\n", (void *) main);
5 printf("location of heap : %p\n", (void *) malloc(1));
6 int x = 3;
7 printf("location of stack : %p\n", (void *) &x);
8 return x;
9 }
When run on a 64-bit Mac OS X machine, we get the following outp ut:
location of code : 0x1095afe50
location of heap : 0x1096008c0
location of stack : 0x7fff691aea64
From this, you can see that code comes ﬁrst in the address spac e, then
the heap, and the stack is all the way at the other end of this la rge virtual
space. All of these addresses are virtual, and will be transl ated by the OS
and hardware in order to fetch values from their true physica l locations.
In the next chapters, we’ll focus our exploration on the basi c mecha-
nisms needed to virtualize memory , including hardware and operat ing
systems support. We’ll also investigate some of the more rel evant poli-
cies that you’ll encounter in operating systems, including how t o manage
free space and which pages to kick out of memory when you run lo w on
space. In doing so, we’ll build up your understanding of how a modern
virtual memory system really works 3.
3Or, we’ll convince you to drop the course. But hold on; if you m ake it through VM, you’ll
likely make it all the way!
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 151

THE ABSTRACTION : A DDRESS SPACES 115
13.5 Summary
We have seen the introduction of a major OS subsystem: virtua l mem-
ory . The VM system is responsible for providing the illusion of a large,
sparse, private address space to programs, which hold all of their instruc-
tions and data therein. The OS, with some serious hardware he lp, will
take each of these virtual memory references, and turn them i nto physi-
cal addresses, which can be presented to the physical memory in order to
fetch the desired information. The OS will do this for many pr ocesses at
once, making sure to protect programs from one another, as we ll as pro-
tect the OS. The entire approach requires a great deal of mech anism (lots
of low-level machinery) as well as some critical policies to work; we’ll
start from the bottom up, describing the critical mechanism s ﬁrst. And
thus we proceed!
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 152

116 THE ABSTRACTION : A DDRESS SPACES
References
[BH70] “The Nucleus of a Multiprogramming System”
Per Brinch Hansen
Communications of the ACM, 13:4, April 1970
The ﬁrst paper to suggest that the OS, or kernel, should be a mi nimal and ﬂexible substrate for building
customized operating systems; this theme is revisited thro ughout OS research history.
[CV65] “Introduction and Overview of the Multics System”
F. J. Corbato and V . A. Vyssotsky
Fall Joint Computer Conference, 1965
A great early Multics paper. Here is the great quote about tim e sharing: “The impetus for time-sharing
ﬁrst arose from professional programmers because of their c onstant frustration in debugging programs
at batch processing installations. Thus, the original goal was to time-share computers to allow simulta-
neous access by several persons while giving to each of them t he illusion of having the whole machine at
his disposal.”
[DV66] “Programming Semantics for Multiprogrammed Comput ations”
Jack B. Dennis and Earl C. Van Horn
Communications of the ACM, V olume 9, Number 3, March 1966
An early paper (but not the ﬁrst) on multiprogramming.
[L60] “Man-Computer Symbiosis”
J. C. R. Licklider
IRE Transactions on Human Factors in Electronics, HFE-1:1, March 1960
A funky paper about how computers and people are going to ente r into a symbiotic age; clearly well
ahead of its time but a fascinating read nonetheless.
[M62] “Time-Sharing Computer Systems”
J. McCarthy
Management and the Computer of the Future, MIT Press, Cambri dge, Mass, 1962
Probably McCarthy’s earliest recorded paper on time sharin g. However, in another paper [M83], he
claims to have been thinking of the idea since 1957. McCarthy left the systems area and went on to be-
come a giant in Artiﬁcial Intelligence at Stanford, includi ng the creation of the LISP programming lan-
guage. See McCarthy’s home page for more info: http://www-formal.stanford.edu/jmc/
[M+63] “A Time-Sharing Debugging System for a Small Compute r”
J. McCarthy , S. Boilen, E. Fredkin, J. C. R. Licklider
AFIPS ’63 (Spring), May , 1963, New York, USA
A great early example of a system that swapped program memory to the “drum” when the program
wasn’t running, and then back into “core” memory when it was a bout to be run.
[M83] “Reminiscences on the History of Time Sharing”
John McCarthy
Winter or Spring of 1983
Available: http://www-formal.stanford.edu/jmc/history/timesharing/timesharing.html
A terriﬁc historical note on where the idea of time-sharing might have come from, including some doubts
towards those who cite Strachey’s work [S59] as the pioneeri ng work in this area.
[R+89] “Mach: A System Software kernel”
Richard Rashid, Daniel Julin, Douglas Orr, Richard Sanzi, R obert Baron, Alessandro Forin,
David Golub, Michael Jones
COMPCON 89, February 1989
Although not the ﬁrst project on microkernels per se, the Mac h project at CMU was well-known and
inﬂuential; it still lives today deep in the bowels of Mac OS X .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 153

THE ABSTRACTION : A DDRESS SPACES 117
[S59] “Time Sharing in Large Fast Computers”
C. Strachey
Proceedings of the International Conference on Informatio n Processing, UNESCO, June 1959
One of the earliest references on time sharing.
[S+03] “Improving the Reliability of Commodity Operating S ystems”
Michael M. Swift, Brian N. Bershad, Henry M. Levy
SOSP 2003
The ﬁrst paper to show how microkernel-like thinking can imp rove operating system reliability.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 155

14
Interlude: Memory API
In this interlude, we discuss the memory allocation interfa ces in U NIX
systems. The interfaces provided are quite simple, and henc e the chapter
is short and to the point 1. The main problem we address is this:
CRUX : H OW TO ALLOCATE AND MANAGE MEMORY
In U NIX /C programs, understanding how to allocate and manage
memory is critical in building robust and reliable software . What inter-
faces are commonly used? What mistakes should be avoided?
14.1 Types of Memory
In running a C program, there are two types of memory that are a llo-
cated. The ﬁrst is called stack memory , and allocations and deallocations
of it are managed implicitly by the compiler for you, the programmer; for
this reason it is sometimes called automatic memory .
Declaring memory on the stack in C is easy . For example, let’s say you
need some space in a function func() for an integer, called x. To declare
such a piece of memory , you just do something like this:
void func() {
int x; // declares an integer on the stack
...
}
The compiler does the rest, making sure to make space on the st ack
when you call into func(). When your return from the function, the
compiler deallocates the memory for you; thus, if you want so me infor-
mation to live beyond the call invocation, you had better not leave that
information on the stack.
It is this need for long-lived memory that gets us to the secon d type
of memory , called heap memory , where all allocations and deallocations
1Indeed, we hope all chapters are! But this one is shorter and p ointier, we think.
119

## Page 156

120 INTERLUDE : M EMORY API
are explicitly handled by you, the programmer. A heavy responsibility ,
no doubt! And certainly the cause of many bugs. But if you are c areful
and pay attention, you will use such interfaces correctly an d without too
much trouble. Here is an example of how one might allocate a po inter to
an integer on the heap:
void func() {
int *x = (int *) malloc(sizeof(int));
...
}
A couple of notes about this small code snippet. First, you mi ght no-
tice that both stack and heap allocation occur on this line: ﬁ rst the com-
piler knows to make room for a pointer to an integer when it see s your
declaration of said pointer ( int *x); subsequently , when the program
calls malloc(), it requests space for an integer on the heap; the routine
returns the address of such an integer (upon success, or NULL on failure),
which is then stored on the stack for use by the program.
Because of its explicit nature, and because of its more varie d usage,
heap memory presents more challenges to both users and syste ms. Thus,
it is the focus of the remainder of our discussion.
14.2 The malloc() Call
The malloc() call is quite simple: you pass it a size asking for some
room on the heap, and it either succeeds and gives you back a po inter to
the newly-allocated space, or fails and returns NULL2.
The manual page shows what you need to do to use malloc; type man
malloc at the command line and you will see:
#include <stdlib.h>
...
void *malloc(size_t size);
From this information, you can see that all you need to do is in clude
the header ﬁle stdlib.h to use malloc. In fact, you don’t really need to
even do this, as the C library , which all C programs link with b y default,
has the code for malloc() inside of it; adding the header just lets the
compiler check whether you are calling malloc() correctly (e.g., passing
the right number of arguments to it, of the right type).
The single parameter malloc() takes is of type size
t which sim-
ply describes how many bytes you need. However, most program mers
do not type in a number here directly (such as 10); indeed, it w ould be
considered poor form to do so. Instead, various routines and macros are
utilized. For example, to allocate space for a double-preci sion ﬂoating
point value, you simply do this:
double *d = (double *) malloc(sizeof(double));
2Note that NULL in C isn’t really anything special at all, just a macro for the value zero.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 157

INTERLUDE : M EMORY API 121
TIP : W HEN IN DOUBT , T RY IT OUT
If you aren’t sure how some routine or operator you are using b ehaves,
there is no substitute for simply trying it out and making sur e it behaves
as you expect. While reading the manual pages or other docume ntation
is useful, how it works in practice is what matters. Write som e code and
test it! That is no doubt the best way to make sure your code beh aves as
you desire. Indeed, that is what we did to double-check the th ings we
were saying about sizeof() were actually true!
Wow , that’s lot of double-ing! This invocation of malloc() uses the
sizeof() operator to request the right amount of space; in C, this is
generally thought of as a compile-time operator, meaning that the actual
size is known at compile time and thus a number (in this case, 8, for a
double) is substituted as the argument to malloc(). For this reason,
sizeof() is correctly thought of as an operator and not a function call
(a function call would take place at run time).
You can also pass in the name of a variable (and not just a type) to
sizeof(), but in some cases you may not get the desired results, so be
careful. For example, let’s look at the following code snipp et:
int *x = malloc(10 * sizeof(int));
printf("%d\n", sizeof(x));
In the ﬁrst line, we’ve declared space for an array of 10 integ ers, which
is ﬁne and dandy . However, when we use sizeof() in the next line,
it returns a small value, such as 4 (on 32-bit machines) or 8 (o n 64-bit
machines). The reason is that in this case, sizeof() thinks we are sim-
ply asking how big a pointer to an integer is, not how much memory we
have dynamically allocated. However, sometimes sizeof() does work
as you might expect:
int x[10];
printf("%d\n", sizeof(x));
In this case, there is enough static information for the comp iler to
know that 40 bytes have been allocated.
Another place to be careful is with strings. When declaring s pace for a
string, use the following idiom: malloc(strlen(s) + 1) , which gets
the length of the string using the function strlen(), and adds 1 to it
in order to make room for the end-of-string character. Using sizeof()
may lead to trouble here.
You might also notice that malloc() returns a pointer to type void.
Doing so is just the way in C to pass back an address and let the p ro-
grammer decide what to do with it. The programmer further hel ps out
by using what is called a cast; in our example above, the programmer
casts the return type of malloc() to a pointer to a double. Casting
doesn’t really accomplish anything, other than tell the com piler and other
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 158

122 INTERLUDE : M EMORY API
programmers who might be reading your code: “yeah, I know wha t I’m
doing.” By casting the result of malloc(), the programmer is just giving
some reassurance; the cast is not needed for the correctness .
14.3 The free() Call
As it turns out, allocating memory is the easy part of the equa tion;
knowing when, how , and even if to free memory is the hard part. To free
heap memory that is no longer in use, programmers simply call free():
int *x = malloc(10 * sizeof(int));
...
free(x);
The routine takes one argument, a pointer that was returned by malloc().
Thus, you might notice, the size of the allocated region is no t passed in
by the user, and must be tracked by the memory-allocation lib rary itself.
14.4 Common Errors
There are a number of common errors that arise in the use ofmalloc()
and free(). Here are some we’ve seen over and over again in teaching
the undergraduate operating systems course. All of these ex amples com-
pile and run with nary a peep from the compiler; while compili ng a C
program is necessary to build a correct C program, it is far fr om sufﬁ-
cient, as you will learn (often in the hard way).
Correct memory management has been such a problem, in fact, t hat
many newer languages have support for automatic memory manage-
ment. In such languages, while you call something akin to malloc()
to allocate memory (usually new or something similar to allocate a new
object), you never have to call something to free space; rath er, a garbage
collector runs and ﬁgures out what memory you no longer have refer-
ences to and frees it for you.
Forgetting T o Allocate Memory
Many routines expect memory to be allocated before you call t hem. For
example, the routine strcpy(dst, src) copies a string from a source
pointer to a destination pointer. However, if you are not car eful, you
might do this:
char *src = "hello";
char *dst; // oops! unallocated
strcpy(dst, src); // segfault and die
When you run this code, it will likely lead to a segmentation fault 3,
which is a fancy term for YOU DID SOMETHING WRONG WITH
MEMORY YOU FOOLISH PROGRAMMER AND I AM ANGRY.
3Although it sounds arcane, you will soon learn why such an ill egal memory access is
called a segmentation fault; if that isn’t incentive to read on, what is?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 159

INTERLUDE : M EMORY API 123
TIP : I T COMPILED OR IT RAN ̸= IT IS CORRECT
Just because a program compiled(!) or even ran once or many ti mes cor-
rectly does not mean the program is correct. Many events may h ave con-
spired to get you to a point where you believe it works, but the n some-
thing changes and it stops. A common student reaction is to sa y (or yell)
“But it worked before!” and then blame the compiler, operati ng system,
hardware, or even (dare we say it) the professor. But the prob lem is usu-
ally right where you think it would be, in your code. Get to wor k and
debug it before you blame those other components.
In this case, the proper code might instead look like this:
char *src = "hello";
char *dst = (char *) malloc(strlen(src) + 1);
strcpy(dst, src); // work properly
Alternately , you could use strdup() and make your life even easier.
Read the strdup man page for more information.
Not Allocating Enough Memory
A related error is not allocating enough memory , sometimes called a buffer
overﬂow. In the example above, a common error is to make almost enough
room for the destination buffer.
char *src = "hello";
char *dst = (char *) malloc(strlen(src)); // too small!
strcpy(dst, src); // work properly
Oddly enough, depending on how malloc is implemented and man y
other details, this program will often run seemingly correc tly . In some
cases, when the string copy executes, it writes one byte too f ar past the
end of the allocated space, but in some cases this is harmless , perhaps
overwriting a variable that isn’t used anymore. In some case s, these over-
ﬂows can be incredibly harmful, and in fact are the source of m any secu-
rity vulnerabilities in systems [W06]. In other cases, the m alloc library
allocated a little extra space anyhow , and thus your program actually
doesn’t scribble on some other variable’s value and works qu ite ﬁne. In
even other cases, the program will indeed fault and crash. An d thus we
learn another valuable lesson: even though it ran correctly once, doesn’t
mean it’s correct.
Forgetting to Initialize Allocated Memory
With this error, you call malloc() properly , but forget to ﬁll in some val-
ues into your newly-allocated data type. Don’t do this! If yo u do forget,
your program will eventually encounter an uninitialized read, where it
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 160

124 INTERLUDE : M EMORY API
reads from the heap some data of unknown value. Who knows what
might be in there? If you’re lucky , some value such that the pr ogram still
works (e.g., zero). If you’re not lucky , something random an d harmful.
Forgetting T o Free Memory
Another common error is known as a memory leak, and it occurs when
you forget to free memory . In long-running applications or systems (such
as the OS itself), this is a huge problem, as slowly leaking me mory even-
tually leads one to run out of memory , at which point a restartis required.
Thus, in general, when you are done with a chunk of memory , youshould
make sure to free it. Note that using a garbage-collected lan guage doesn’t
help here: if you still have a reference to some chunk of memor y , no
garbage collector will ever free it, and thus memory leaks re main a prob-
lem even in more modern languages.
Note that not all memory need be freed, at least, in certain ca ses. For
example, when you write a short-lived program, you might allocate some
space using malloc(). The program runs and is about to complete: is
there need to call free() a bunch of times just before exiting? While
it seems wrong not to, it is in this case quite ﬁne to simply exi t. After
all, when your program exits, the OS will clean up everything about this
process, including any memory it has allocated. Calling free() a bunch
of times and then exiting is thus pointless, and, if you do so i ncorrectly ,
will cause the program to crash. Just call exit and be happy in stead.
Freeing Memory Before You Are Done With It
Sometimes a program will free memory before it is ﬁnished usi ng it; such
a mistake is called a dangling pointer, and it, as you can guess, is also a
bad thing. The subsequent use can crash the program, or overw rite valid
memory (e.g., you called free(), but then called malloc() again to
allocate something else, which then recycles the errantly- freed memory).
Freeing Memory Repeatedly
Programs also sometimes free memory more than once; this is k nown as
the double free. The result of doing so is undeﬁned. As you can imag-
ine, the memory-allocation library might get confused and d o all sorts of
weird things; crashes are a common outcome.
Calling free() Incorrectly
One last problem we discuss is the call of free() incorrectly . After all,
free() expects you only to pass to it one of the pointers you received
from malloc() earlier. When you pass in some other value, bad things
can (and do) happen. Thus, such invalid frees are dangerous and of
course should also be avoided.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

