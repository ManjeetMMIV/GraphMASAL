# Document: operating_systems_three_easy_pieces (Pages 441 to 480)

## Page 441

HARD DISK DRIVES 405
Head
Arm
0
11
1098
7
6
5
4 3 2
1
Spindle
Rotates this way
Figure 37.2: A Single T rack Plus A Head
This track has just 12 sectors, each of which is 512 bytes in si ze (our
typical sector size, recall) and addressed therefore by thenumbers 0 through
11. The single platter we have here rotates around the spindl e, to which
a motor is attached. Of course, the track by itself isn’t too i nteresting; we
want to be able to read or write those sectors, and thus we need a disk
head, attached to a disk arm, as we now see (Figure 37.2).
In the ﬁgure, the disk head, attached to the end of the arm, is p osi-
tioned over sector 6, and the surface is rotating counter-cl ockwise.
Single-track Latency: The Rotational Delay
To understand how a request would be processed on our simple, one-
track disk, imagine we now receive a request to read block 0. H ow should
the disk service this request?
In our simple disk, the disk doesn’t have to do much. In partic ular, it
must just wait for the desired sector to rotate under the disk head. This
wait happens often enough in modern drives, and is an important enough
component of I/O service time, that it has a special name: rotational de-
lay (sometimes rotation delay, though that sounds weird). In the exam-
ple, if the full rotational delay is R, the disk has to incur a rotational delay
of about R
2 to wait for 0 to come under the read/write head (if we start at
6). A worst-case request on this single track would be to sect or 5, causing
nearly a full rotational delay in order to service such a requ est.
Multiple T racks: Seek Time
So far our disk just has a single track, which is not too realis tic; modern
disks of course have many millions. Let’s thus look at ever-s o-slightly
more realistic disk surface, this one with three tracks (Fig ure
37.3, left).
In the ﬁgure, the head is currently positioned over the inner most track
(which contains sectors 24 through 35); the next track over c ontains the
next set of sectors (12 through 23), and the outermost track c ontains the
ﬁrst sectors (0 through 11).
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 442

406 HARD DISK DRIVES
0
11
10
9
8
7
6
5
4
3
2
1
12
23
22
21
20
19
18
17
16
15
14
13
24
35
343332
31
30
29
28 27 26
25
Spindle
Rotates this way
SeekRemaining rotation
3
2
1
0
11
10
9
8
7
6
5
4
15
14
13
12
23
22
21
20
19
18
17
16
27
26
252435
34
33
32
31 30 29
28
Spindle
Rotates this way
Figure 37.3: Three T racks Plus A Head (Right: With Seek)
To understand how the drive might access a given sector, we now trace
what would happen on a request to a distant sector, e.g., a rea d to sector
11. To service this read, the drive has to ﬁrst move the disk ar m to the cor-
rect track (in this case, the outermost one), in a process kno wn as a seek.
Seeks, along with rotations, are one of the most costly disk o perations.
The seek, it should be noted, has many phases: ﬁrst an acceleration
phase as the disk arm gets moving; then coasting as the arm is moving
at full speed, then deceleration as the arm slows down; ﬁnally settling as
the head is carefully positioned over the correct track. The settling time
is often quite signiﬁcant, e.g., 0.5 to 2 ms, as the drive must be certain to
ﬁnd the right track (imagine if it just got close instead!).
After the seek, the disk arm has positioned the head over the r ight
track. A depiction of the seek is found in Figure 37.3 (right).
As we can see, during the seek, the arm has been moved to the des ired
track, and the platter of course has rotated, in this case abo ut 3 sectors.
Thus, sector 9 is just about to pass under the disk head, and we must
only endure a short rotational delay to complete the transfe r.
When sector 11 passes under the disk head, the ﬁnal phase of I/ O
will take place, known as the transfer, where data is either read from or
written to the surface. And thus, we have a complete picture o f I/O time:
ﬁrst a seek, then waiting for the rotational delay , and ﬁnall y the transfer.
Some Other Details
Though we won’t spend too much time on it, there are some other inter-
esting details about how hard drives operate. Many drives em ploy some
kind of track skew to make sure that sequential reads can be properly
serviced even when crossing track boundaries. In our simple example
disk, this might appear as seen in Figure
37.4.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 443

HARD DISK DRIVES 407
Track skew: 2 blocks
0
11
10
9
8
7
6
5
4
3
2
1
22
21
20
19
18
17
16
15
14
13
12
23
32
31
302928
27
26
25
24 35 34
33
Spindle
Rotates this way
Figure 37.4: Three T racks: T rack Skew Of 2
Sectors are often skewed like this because when switching fr om one
track to another, the disk needs time to reposition the head (even to neigh-
boring tracks). Without such skew , the head would be moved to the next
track but the desired next block would have already rotated u nder the
head, and thus the drive would have to wait almost the entire r otational
delay to access the next block.
Another reality is that outer tracks tend to have more sector s than
inner tracks, which is a result of geometry; there is simply m ore room
out there. These tracks are often referred to as multi-zoned disk drives,
where the disk is organized into multiple zones, and where a z one is con-
secutive set of tracks on a surface. Each zone has the same num ber of
sectors per track, and outer zones have more sectors than inn er zones.
Finally , an important part of any modern disk drive is its cache, for
historical reasons sometimes called a track buffer. This cache is just some
small amount of memory (usually around 8 or 16 MB) which the dr ive
can use to hold data read from or written to the disk. For examp le, when
reading a sector from the disk, the drive might decide to read in all of the
sectors on that track and cache them in its memory; doing so al lows the
drive to quickly respond to any subsequent requests to the sa me track.
On writes, the drive has a choice: should it acknowledge the w rite has
completed when it has put the data in its memory , or after the w rite has
actually been written to disk? The former is called write back caching
(or sometimes immediate reporting), and the latter write through. Write
back caching sometimes makes the drive appear “faster”, but can be dan-
gerous; if the ﬁle system or applications require that data b e written to
disk in a certain order for correctness, write-back caching can lead to
problems (read the chapter on ﬁle-system journaling for det ails).
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 444

408 HARD DISK DRIVES
ASIDE : DIMENSIONAL ANALYSIS
Remember in Chemistry class, how you solved virtually every prob-
lem by simply setting up the units such that they canceled out , and some-
how the answers popped out as a result? That chemical magic is known
by the highfalutin name of dimensional analysis and it turns out it is
useful in computer systems analysis too.
Let’s do an example to see how dimensional analysis works and why
it is useful. In this case, assume you have to ﬁgure out how lon g, in mil-
liseconds, a single rotation of a disk takes. Unfortunately , you are given
only the RPM of the disk, or rotations per minute . Let’s assume we’re
talking about a 10K RPM disk (i.e., it rotates 10,000 times pe r minute).
How do we set up the dimensional analysis so that we get time pe r rota-
tion in milliseconds?
To do so, we start by putting the desired units on the left; in t his case,
we wish to obtain the time (in milliseconds) per rotation, so that is ex-
actly what we write down: T ime (ms)
1 Rotation . We then write down everything
we know , making sure to cancel units where possible. First, w e obtain
1 minute
10,000 Rotations (keeping rotation on the bottom, as that’s where it is on
the left), then transform minutes into seconds with 60 seconds
1 minute , and then
ﬁnally transform seconds in milliseconds with 1000 ms
1 second . The ﬁnal result is
this equation, with units nicely canceled, is:
T ime (ms)
1 Rot. = 1 minute
10,000 Rot. · 60 seconds
1 minute · 1000 ms
1 second = 60,000 ms
10,000 Rot. = 6 ms
Rotation
As you can see from this example, dimensional analysis makes what
seems obvious into a simple and repeatable process. Beyond t he RPM
calculation above, it comes in handy with I/O analysis regul arly . For
example, you will often be given the transfer rate of a disk, e .g.,
100 MB/second, and then asked: how long does it take to transf er a
512 KB block (in milliseconds)? With dimensional analysis, it’s easy:
T ime (ms)
1 Request = 512 KB
1 Request · 1 M B
1024 KB · 1 second
100 M B · 1000 ms
1 second = 5 ms
Request
37.4 I/O Time: Doing The Math
Now that we have an abstract model of the disk, we can use a litt le
analysis to better understand disk performance. In particu lar, we can
now represent I/O time as the sum of three major components:
TI/O = Tseek + Trotation + Ttransf er (37.1)
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 445

HARD DISK DRIVES 409
Cheetah 15K.5 Barracuda
Capacity 300 GB 1 TB
RPM 15,000 7,200
Average Seek 4 ms 9 ms
Max Transfer 125 MB/s 105 MB/s
Platters 4 4
Cache 16 MB 16/32 MB
Connects via SCSI SATA
Table 37.1: Disk Drive Specs: SCSI V ersus SA TA
Note that the rate of I/O ( RI/O ), which is often more easily used for
comparison between drives (as we will do below), is easily co mputed
from the time. Simply divide the size of the transfer by the ti me it took:
RI/O = Size T ransf er
TI/O
(37.2)
To get a better feel for I/O time, let us perform the following calcu-
lation. Assume there are two workloads we are interested in. The ﬁrst,
known as the random workload, issues small (e.g., 4KB) reads to random
locations on the disk. Random workloads are common in many im por-
tant applications, including database management systems . The second,
known as the sequential workload, simply reads a large number of sec-
tors consecutively from the disk, without jumping around. S equential
access patterns are quite common and thus important as well.
To understand the difference in performance between random and se-
quential workloads, we need to make a few assumptions about t he disk
drive ﬁrst. Let’s look at a couple of modern disks from Seagat e. The ﬁrst,
known as the Cheetah 15K.5 [S09b], is a high-performance SCS I drive.
The second, the Barracuda [S09a], is a drive built for capaci ty . Details on
both are found in Table 37.1.
As you can see, the drives have quite different characterist ics, and
in many ways nicely summarize two important components of th e disk
drive market. The ﬁrst is the “high performance” drive marke t, where
drives are engineered to spin as fast as possible, deliver lo w seek times,
and transfer data quickly . The second is the “capacity” mark et, where
cost per byte is the most important aspect; thus, the drives a re slower but
pack as many bits as possible into the space available.
From these numbers, we can start to calculate how well the dri ves
would do under our two workloads outlined above. Let’s start by looking
at the random workload. Assuming each 4 KB read occurs at a ran dom
location on disk, we can calculate how long each such read wou ld take.
On the Cheetah:
Tseek = 4 ms, T rotation = 2 ms, T transf er = 30 microsecs (37.3)
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 446

410 HARD DISK DRIVES
TIP : U SE DISKS SEQUENTIALLY
When at all possible, transfer data to and from disks in a sequ ential man-
ner. If sequential is not possible, at least think about tran sferring data
in large chunks: the bigger, the better. If I/O is done in litt le random
pieces, I/O performance will suffer dramatically . Also, us ers will suffer.
Also, you will suffer, knowing what suffering you have wroug ht with
your careless random I/Os.
The average seek time (4 milliseconds) is just taken as the average time
reported by the manufacturer; note that a full seek (from one end of the
surface to the other) would likely take two or three times lon ger. The
average rotational delay is calculated from the RPM directl y . 15000 RPM
is equal to 250 RPS (rotations per second); thus, each rotati on takes 4 ms.
On average, the disk will encounter a half rotation and thus 2 ms is the
average time. Finally , the transfer time is just the size of t he transfer over
the peak transfer rate; here it is vanishingly small (30 microseconds; note
that we need 1000 microseconds just to get 1 millisecond!).
Thus, from our equation above, TI/O for the Cheetah roughly equals
6 ms. To compute the rate of I/O, we just divide the size of the t ransfer
by the average time, and thus arrive at RI/O for the Cheetah under the
random workload of about 0.66 MB/s. The same calculation for the Bar-
racuda yields a TI/O of about 13.2 ms, more than twice as slow , and thus
a rate of about 0.31 MB/s.
Now let’s look at the sequential workload. Here we can assume there
is a single seek and rotation before a very long transfer. For simplicity ,
assume the size of the transfer is 100 MB. Thus, TI/O for the Barracuda
and Cheetah is about 800 ms and 950 ms, respectively . The rate s of I/O
are thus very nearly the peak transfer rates of 125 MB/s and 10 5 MB/s,
respectively . Table37.2 summarizes these numbers.
The table shows us a number of important things. First, and mo st
importantly , there is a huge gap in drive performance betwee n random
and sequential workloads, almost a factor of 200 or so for the Cheetah
and more than a factor 300 difference for the Barracuda. And t hus we
arrive at the most obvious design tip in the history of comput ing.
A second, more subtle point: there is a large difference in pe rformance
between high-end “performance” drives and low-end “capaci ty” drives.
For this reason (and others), people are often willing to pay top dollar for
the former while trying to get the latter as cheaply as possib le.
Cheetah Barracuda
RI/O Random 0.66 MB/s 0.31 MB/s
RI/O Sequential 125 MB/s 105 MB/s
Table 37.2: Disk Drive Performance: SCSI V ersus SA TA
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 447

HARD DISK DRIVES 411
ASIDE : COMPUTING THE “AVERAGE ” S EEK
In many books and papers, you will see average disk-seek time cited
as being roughly one-third of the full seek time. Where does t his come
from?
Turns out it arises from a simple calculation based on averag e seek
distance, not time. Imagine the disk as a set of tracks, from 0 to N . The
seek distance between any two tracks x and y is thus computed as the
absolute value of the difference between them: |x − y|.
To compute the average seek distance, all you need to do is to ﬁ rst add
up all possible seek distances:
N∑
x=0
N∑
y=0
|x − y|. (37.4)
Then, divide this by the number of different possible seeks: N 2. To
compute the sum, we’ll just use the integral form:
∫ N
x=0
∫ N
y=0
|x − y|dy dx. (37.5)
To compute the inner integral, let’s break out the absolute v alue:
∫ x
y=0
(x − y) dy +
∫ N
y=x
(y − x) dy. (37.6)
Solving this leads to (xy − 1
2 y2)
⏐
⏐x
0 + ( 1
2 y2 − xy)
⏐
⏐N
x which can be sim-
pliﬁed to (x2 − N x + 1
2 N 2). Now we have to compute the outer integral:
∫ N
x=0
(x2 − N x + 1
2 N 2) dx, (37.7)
which results in:
( 1
3 x3 − N
2 x2 + N 2
2 x)
⏐
⏐
⏐
⏐
N
0
= N 3
3 . (37.8)
Remember that we still have to divide by the total number of se eks
(N 2) to compute the average seek distance: ( N 3
3 )/(N 2) = 1
3 N . Thus the
average seek distance on a disk, over all possible seeks, is o ne-third the
full distance. And now when you hear that an average seek is on e-third
of a full seek, you’ll know where it came from.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 448

412 HARD DISK DRIVES
0
11
10
9
8
7
6
5
4
3
2
1
12
23
22
21
20
19
18
17
16
15
14
13
24
35
343332
31
30
29
28 27 26
25
Spindle
Rotates this way
Figure 37.5: SSTF: Scheduling Requests 21 And 2
37.5 Disk Scheduling
Because of the high cost of I/O, the OS has historically playe d a role in
deciding the order of I/Os issued to the disk. More speciﬁcal ly , given a
set of I/O requests, the disk scheduler examines the requests and decides
which one to schedule next [SCO90, JW91].
Unlike job scheduling, where the length of each job is usuall y un-
known, with disk scheduling, we can make a good guess at how lo ng
a “job” (i.e., disk request) will take. By estimating the see k and possible
the rotational delay of a request, the disk scheduler can kno w how long
each request will take, and thus (greedily) pick the one that will take the
least time to service ﬁrst. Thus, the disk scheduler will try to follow the
principle of SJF (shortest job ﬁrst) in its operation.
SSTF: Shortest Seek Time First
One early disk scheduling approach is known as shortest-seek-time-ﬁrst
(SSTF) (also called shortest-seek-ﬁrst or SSF). SSTF orders the queue of
I/O requests by track, picking requests on the nearest track to complete
ﬁrst. For example, assuming the current position of the head is over the
inner track, and we have requests for sectors 21 (middle trac k) and 2
(outer track), we would then issue the request to 21 ﬁrst, wai t for it to
complete, and then issue the request to 2 (Figure
37.5).
SSTF works well in this example, seeking to the middle track ﬁ rst and
then the outer track. However, SSTF is not a panacea, for the f ollowing
reasons. First, the drive geometry is not available to the ho st OS; rather,
it sees an array of blocks. Fortunately , this problem is rath er easily ﬁxed.
Instead of SSTF, an OS can simply implement nearest-block-ﬁrst (NBF),
which schedules the request with the nearest block address n ext.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 449

HARD DISK DRIVES 413
The second problem is more fundamental: starvation. Imagine in
our example above if there were a steady stream of requests to the in-
ner track, where the head currently is positioned. Requests to any other
tracks would then be ignored completely by a pure SSTF approa ch. And
thus the crux of the problem:
CRUX : H OW TO HANDLE DISK STARVATION
How can we implement SSTF-like scheduling but avoid starvat ion?
Elevator (a.k.a. SCAN or C-SCAN)
The answer to this query was developed some time ago (see [CKR 72]
for example), and is relatively straightforward. The algor ithm, originally
called SCAN, simply moves across the disk servicing requests in order
across the tracks. Let us call a single pass across the disk a sweep. Thus, if
a request comes for a block on a track that has already been ser viced on
this sweep of the disk, it is not handled immediately , but rat her queued
until the next sweep.
SCAN has a number of variants, all of which do about the same th ing.
For example, Coffman et al. introduced F-SCAN, which freezes the queue
to be serviced when it is doing a sweep [CKR72]; this action pl aces re-
quests that come in during the sweep into a queue to be service d later.
Doing so avoids starvation of far-away requests, by delayin g the servic-
ing of late-arriving (but nearer by) requests.
C-SCAN is another common variant, short for Circular SCAN . In-
stead of sweeping in one direction across the disk, the algor ithm sweeps
from outer-to-inner, and then inner-to-outer, etc.
For reasons that should now be obvious, this algorithm (and i ts vari-
ants) is sometimes referred to as the elevator algorithm, because it be-
haves like an elevator which is either going up or down and not just ser-
vicing requests to ﬂoors based on which ﬂoor is closer. Imagi ne how an-
noying it would be if you were going down from ﬂoor 10 to 1, and s ome-
body got on at 3 and pressed 4, and the elevator went up to 4 beca use it
was “closer” than 1! As you can see, the elevator algorithm, w hen used
in real life, prevents ﬁghts from taking place on elevators. In disks, it just
prevents starvation.
Unfortunately , SCAN and its cousins do not represent the best schedul-
ing technology . In particular, SCAN (or SSTF even) do not actually adhere
as closely to the principle of SJF as they could. In particula r, they ignore
rotation. And thus, another crux:
CRUX : H OW TO ACCOUNT FOR DISK ROTATION COSTS
How can we implement an algorithm that more closely approxim ates SJF
by taking both seek and rotation into account?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 450

414 HARD DISK DRIVES
0
11
10
9
8
7
6
5
4
3
2
1
12
23
22
21
20
19
18
17
16
15
14
13
24
35
343332
31
30
29
28 27 26
25
Spindle
Rotates this way
Figure 37.6: SSTF: Sometimes Not Good Enough
SPTF: Shortest Positioning Time First
Before discussing shortest positioning time ﬁrst or SPTF scheduling (some-
times also called shortest access time ﬁrst or SA TF), which is the solution
to our problem, let us make sure we understand the problem in m ore de-
tail. Figure
37.6 presents an example.
In the example, the head is currently positioned over sector 30 on the
inner track. The scheduler thus has to decide: should it sche dule sector 16
(on the middle track) or sector 8 (on the outer track) for its n ext request.
So which should it service next?
The answer, of course, is “it depends”. In engineering, it tu rns out
“it depends” is almost always the answer, reﬂecting that tra de-offs are
part of the life of the engineer; such maxims are also good in a pinch,
e.g., when you don’t know an answer to your boss’s question, y ou might
want to try this gem. However, it is almost always better to kn ow why it
depends, which is what we discuss here.
What it depends on here is the relative time of seeking as comp ared
to rotation. If, in our example, seek time is much higher than rotational
delay , then SSTF (and variants) are just ﬁne. However, imagi ne if seek is
quite a bit faster than rotation. Then, in our example, it wou ld make more
sense to seek further to service request 8 on the outer track than it would
to perform the shorter seek to the middle track to service 16, which has to
rotate all the way around before passing under the disk head.
On modern drives, as we saw above, both seek and rotation are roughly
equivalent (depending, of course, on the exact requests), a nd thus SPTF
is useful and improves performance. However, it is even more difﬁcult
to implement in an OS, which generally does not have a good ide a where
track boundaries are or where the disk head currently is (in a rotational
sense). Thus, SPTF is usually performed inside a drive, desc ribed below .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 451

HARD DISK DRIVES 415
TIP : I T ALWAYS DEPENDS (L IVNY ’ S LAW)
Almost any question can be answered with “it depends”, as our colleague
Miron Livny always says. However, use with caution, as if you answer
too many questions this way , people will stop asking you ques tions alto-
gether. For example, somebody asks: “want to go to lunch?” Yo u reply:
“it depends, are you coming along?”
Other Scheduling Issues
There are many other issues we do not discuss in this brief des cription
of basic disk operation, scheduling, and related topics. On e such is-
sue is this: where is disk scheduling performed on modern systems? In
older systems, the operating system did all the scheduling; after looking
through the set of pending requests, the OS would pick the bes t one, and
issue it to the disk. When that request completed, the next on e would be
chosen, and so forth. Disks were simpler then, and so was life .
In modern systems, disks can accommodate multiple outstand ing re-
quests, and have sophisticated internal schedulers themselves (which can
implement SPTF accurately; inside the disk controller, all relevant details
are available, including exact head position). Thus, the OS scheduler usu-
ally picks what it thinks the best few requests are (say 16) and issues them
all to disk; the disk then uses its internal knowledge of head position and
detailed track layout information to service said requests in the best pos-
sible (SPTF) order.
Another important related task performed by disk scheduler s is I/O
merging. For example, imagine a series of requests to read blocks 33,
then 8, then 34, as in Figure
37.6. In this case, the scheduler should merge
the requests for blocks 33 and 34 into a single two-block requ est; any re-
ordering that the scheduler does is performed upon the merge d requests.
Merging is particularly important at the OS level, as it redu ces the num-
ber of requests sent to the disk and thus lowers overheads.
One ﬁnal problem that modern schedulers address is this: how long
should the system wait before issuing an I/O to disk? One migh t naively
think that the disk, once it has even a single I/O, should imme diately
issue the request to the drive; this approach is called work-conserving, as
the disk will never be idle if there are requests to serve. However, research
on anticipatory disk scheduling has shown that sometimes it is better to
wait for a bit [ID01], in what is called a non-work-conserving approach.
By waiting, a new and “better” request may arrive at the disk, and thus
overall efﬁciency is increased. Of course, deciding when to wait, and for
how long, can be tricky; see the research paper for details, o r check out
the Linux kernel implementation to see how such ideas are tra nsitioned
into practice (if you are the ambitious sort).
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 452

416 HARD DISK DRIVES
37.6 Summary
We have presented a summary of how disks work. The summary is
actually a detailed functional model; it does not describe t he amazing
physics, electronics, and material science that goes into a ctual drive de-
sign. For those interested in even more details of that natur e, we suggest
a different major (or perhaps minor); for those that are happ y with this
model, good! We can now proceed to using the model to build mor e in-
teresting systems on top of these incredible devices.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 453

HARD DISK DRIVES 417
References
[ADR03] “More Than an Interface: SCSI vs. ATA”
Dave Anderson, Jim Dykes, Erik Riedel
FAST ’03, 2003
One of the best recent-ish references on how modern disk driv es really work; a must read for anyone
interested in knowing more.
[CKR72] “Analysis of Scanning Policies for Reducing Disk Se ek Times”
E.G. Coffman, L.A. Klimko, B. Ryan
SIAM Journal of Computing, September 1972, V ol 1. No 3.
Some of the early work in the ﬁeld of disk scheduling.
[ID01] “Anticipatory Scheduling: A Disk-scheduling Frame work
To Overcome Deceptive Idleness In Synchronous I/O”
Sitaram Iyer, Peter Druschel
SOSP ’01, October 2001
A cool paper showing how waiting can improve disk scheduling : better requests may be on their way!
[JW91] “Disk Scheduling Algorithms Based On Rotational Pos ition”
D. Jacobson, J. Wilkes
Technical Report HPL-CSP-91-7rev1, Hewlett-Packard (February 1991)
A more modern take on disk scheduling. It remains a technical report (and not a published paper)
because the authors were scooped by Seltzer et al. [SCO90].
[RW92] “An Introduction to Disk Drive Modeling”
C. Ruemmler, J. Wilkes
IEEE Computer, 27:3, pp. 17-28, March 1994
A terriﬁc introduction to the basics of disk operation. Some pieces are out of date, but most of the basics
remain.
[SCO90] “Disk Scheduling Revisited”
Margo Seltzer, Peter Chen, John Ousterhout
USENIX 1990
A paper that talks about how rotation matters too in the world of disk scheduling.
[SG04] “MEMS-based storage devices and standard disk inter faces: A square peg in a round
hole?”
Steven W. Schlosser, Gregory R. Ganger
FAST ’04, pp. 87-100, 2004
While the MEMS aspect of this paper hasn’t yet made an impact, the discussion of the contract between
ﬁle systems and disks is wonderful and a lasting contributio n.
[S09a] “Barracuda ES.2 data sheet”
http://www.seagate.com/docs/pdf/datasheet/disc/ds
cheetah 15k 5.pdf A data
sheet; read at your own risk. Risk of what? Boredom.
[S09b] “Cheetah 15K.5”
http://www.seagate.com/docs/pdf/datasheet/disc/ds
barracuda es.pdf See above
commentary on data sheets.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 454

418 HARD DISK DRIVES
Homework
This homework uses disk.py to familiarize you with how a modern
hard drive works. It has a lot of different options, and unlik e most of
the other simulations, has a graphical animator to show you e xactly what
happens when the disk is in action. See the README for details .
1. Compute the seek, rotation, and transfer times for the fol lowing
sets of requests: -a 0 , -a 6 , -a 30 , -a 7,30,8 , and ﬁnally -a
10,11,12,13.
2. Do the same requests above, but change the seek rate to diff erent
values: -S 2 , -S 4 , -S 8 , -S 10 , -S 40 , -S 0.1 . How do the
times change?
3. Do the same requests above, but change the rotation rate: -R 0.1 ,
-R 0.5 , -R 0.01 . How do the times change?
4. You might have noticed that some request streams would be b et-
ter served with a policy better than FIFO. For example, with t he
request stream -a 7,30,8 , what order should the requests be pro-
cessed in? Now run the shortest seek-time ﬁrst (SSTF) schedu ler
(-p SSTF ) on the same workload; how long should it take (seek,
rotation, transfer) for each request to be served?
5. Now do the same thing, but using the shortest access-time ﬁ rst
(SATF) scheduler ( -p SATF ). Does it make any difference for the
set of requests as speciﬁed by -a 7,30,8 ? Find a set of requests
where SATF does noticeably better than SSTF; what are the con di-
tions for a noticeable difference to arise?
6. You might have noticed that the request stream -a 10,11,12,13
wasn’t particularly well handled by the disk. Why is that? Ca n you
introduce a track skew to address this problem ( -o skew , where
skew is a non-negative integer)? Given the default seek rate, wha t
should the skew be to minimize the total time for this set of re -
quests? What about for different seek rates (e.g., -S 2 , -S 4 )? In
general, could you write a formula to ﬁgure out the skew , given the
seek rate and sector layout information?
7. Multi-zone disks pack more sectors into the outer tracks. To conﬁg-
ure this disk in such a way , run with the -z ﬂag. Speciﬁcally , try
running some requests against a disk run with -z 10,20,30 (the
numbers specify the angular space occupied by a sector, per t rack;
in this example, the outer track will be packed with a sector e very
10 degrees, the middle track every 20 degrees, and the inner t rack
with a sector every 30 degrees). Run some random requests (e. g.,
-a -1 -A 5,-1,0 , which speciﬁes that random requests should
be used via the -a -1 ﬂag and that ﬁve requests ranging from 0 to
the max be generated), and see if you can compute the seek, rot a-
tion, and transfer times. Use different random seeds ( -s 1 , -s 2 ,
etc.). What is the bandwidth (in sectors per unit time) on the outer,
middle, and inner tracks?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 455

HARD DISK DRIVES 419
8. Scheduling windows determine how many sector requests a d isk
can examine at once in order to determine which sector to serv e
next. Generate some random workloads of a lot of requests (e. g.,
-A 1000,-1,0 , with different seeds perhaps) and see how long
the SATF scheduler takes when the scheduling window is chang ed
from 1 up to the number of requests (e.g., -w 1 up to -w 1000 ,
and some values in between). How big of scheduling window is
needed to approach the best possible performance? Make a gra ph
and see. Hint: use the -c ﬂag and don’t turn on graphics with -G
to run these more quickly . When the scheduling window is set t o 1,
does it matter which policy you are using?
9. A voiding starvation is important in a scheduler. Can you t hink of a
series of requests such that a particular sector is delayed f or a very
long time given a policy such as SATF? Given that sequence, ho w
does it perform if you use a bounded SA TF or BSA TFscheduling
approach? In this approach, you specify the scheduling wind ow
(e.g., -w 4 ) as well as the BSATF policy ( -p BSATF ); the scheduler
then will only move onto the next window of requests when all of
the requests in the current window have been serviced. Does t his
solve the starvation problem? How does it perform, as compar ed
to SATF? In general, how should a disk make this trade-off between
performance and starvation avoidance?
10. All the scheduling policies we have looked at thus far are greedy,
in that they simply pick the next best option instead of looki ng for
the optimal schedule over a set of requests. Can you ﬁnd a set o f
requests in which this greedy approach is not optimal?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 457

38
Redundant Arrays of Inexpensive Disks
(RAIDs)
When we use a disk, we sometimes wish it to be faster; I/O opera tions
are slow and thus can be the bottleneck for the entire system. When we
use a disk, we sometimes wish it to be larger; more and more data is being
put online and thus our disks are getting fuller and fuller. W hen we use
a disk, we sometimes wish for it to be more reliable; when a dis k fails, if
our data isn’t backed up, all that valuable data is gone.
CRUX : H OW TO MAKE A L ARGE , FAST, R ELIABLE DISK
How can we make a large, fast, and reliable storage system? Wh at are
the key techniques? What are trade-offs between different a pproaches?
In this chapter, we introduce the Redundant Array of Inexpensive
Disks better known as RAID [P+88], a technique to use multiple disks in
concert to build a faster, bigger, and more reliable disk sys tem. The term
was introduced in the late 1980s by a group of researchers at U .C. Berke-
ley (led by Professors David Patterson and Randy Katz and the n student
Garth Gibson); it was around this time that many different re searchers si-
multaneously arrived upon the basic idea of using multiple d isks to build
a better storage system [BG88, K86,K88,PB86,SG86].
Externally , a RAID looks like a disk: a group of blocks one can read
or write. Internally , the RAID is a complex beast, consistin g of multiple
disks, memory (both volatile and non-), and one or more proce ssors to
manage the system. A hardware RAID is very much like a compute r
system, specialized for the task of managing a group of disks .
RAIDs offer a number of advantages over a single disk. One adv an-
tage is performance. Using multiple disks in parallel can greatly speed
up I/O times. Another beneﬁt is capacity. Large data sets demand large
disks. Finally , RAIDs can improve reliability; spreading data across mul-
tiple disks (without RAID techniques) makes the data vulner able to the
loss of a single disk; with some form of redundancy, RAIDs can tolerate
the loss of a disk and keep operating as if nothing were wrong.
421

## Page 458

422 R EDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S)
TIP : T RANSPARENCY ENABLES DEPLOYMENT
When considering how to add new functionality to a system, on e should
always consider whether such functionality can be added transparently,
in a way that demands no changes to the rest of the system. Requ iring a
complete rewrite of the existing software (or radical hardw are changes)
lessens the chance of impact of an idea. RAID is a perfect exam ple, and
certainly its transparency contributed to its success; adm inistrators could
install a SCSI-based RAID storage array instead of a SCSI dis k, and the
rest of the system (host computer, OS, etc.) did not have to ch ange one bit
to start using it. By solving this problem of deployment, RAID was made
more successful from day one.
Amazingly , RAIDs provide these advantagestransparently to systems
that use them, i.e., a RAID just looks like a big disk to the host system. The
beauty of transparency , of course, is that it enables one to s imply replace
a disk with a RAID and not change a single line of software; the operat-
ing system and client applications continue to operate with out modiﬁca-
tion. In this manner, transparency greatly improves the deployability of
RAID, enabling users and administrators to put a RAID to use w ithout
worries of software compatibility .
We now discuss some of the important aspects of RAIDs. We begi n
with the interface, fault model, and then discuss how one can evaluate a
RAID design along three important axes: capacity , reliabil ity , and perfor-
mance. We then discuss a number of other issues that are impor tant to
RAID design and implementation.
38.1 Interface And RAID Internals
To a ﬁle system above, a RAID looks like a big, (hopefully) fas t, and
(hopefully) reliable disk. Just as with a single disk, it pre sents itself as
a linear array of blocks, each of which can be read or written b y the ﬁle
system (or other client).
When a ﬁle system issues a logical I/O request to the RAID, the RAID
internally must calculate which disk (or disks) to access in order to com-
plete the request, and then issue one or more physical I/Os to do so. The
exact nature of these physical I/Os depends on the RAID level , as we will
discuss in detail below . However, as a simple example, consi der a RAID
that keeps two copies of each block (each one on a separate dis k); when
writing to such a mirrored RAID system, the RAID will have to perform
two physical I/Os for every one logical I/O it is issued.
A RAID system is often built as a separate hardware box, with a stan-
dard connection (e.g., SCSI, or SATA) to a host. Internally , however,
RAIDs are fairly complex, consisting of a microcontroller that runs ﬁrmware
to direct the operation of the RAID, volatile memory such as D RAM
to buffer data blocks as they are read and written, and in some cases,
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 459

REDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S) 423
non-volatile memory to buffer writes safely and perhaps eve n special-
ized logic to perform parity calculations (useful in some RA ID levels, as
we will also see below). At a high level, a RAID is very much a sp ecial-
ized computer system: it has a processor, memory , and disks; however,
instead of running applications, it runs specialized softw are designed to
operate the RAID.
38.2 Fault Model
To understand RAID and compare different approaches, we must have
a fault model in mind. RAIDs are designed to detect and recove r from
certain kinds of disk faults; thus, knowing exactly which fa ults to expect
is critical in arriving upon a working design.
The ﬁrst fault model we will assume is quite simple, and has be en
called the fail-stop fault model [S84]. In this model, a disk can be in
exactly one of two states: working or failed. With a working d isk, all
blocks can be read or written. In contrast, when a disk has fai led, we
assume it is permanently lost.
One critical aspect of the fail-stop model is what it assumes about fault
detection. Speciﬁcally , when a disk has failed, we assume th at this is
easily detected. For example, in a RAID array , we would assum e that the
RAID controller hardware (or software) can immediately obs erve when a
disk has failed.
Thus, for now , we do not have to worry about more complex “sile nt”
failures such as disk corruption. We also do not have to worry about a sin-
gle block becoming inaccessible upon an otherwise working d isk (some-
times called a latent sector error). We will consider these m ore complex
(and unfortunately , more realistic) disk faults later.
38.3 How To Evaluate A RAID
As we will soon see, there are a number of different approache s to
building a RAID. Each of these approaches has different char acteristics
which are worth evaluating, in order to understand their str engths and
weaknesses.
Speciﬁcally , we will evaluate each RAID design along three a xes. The
ﬁrst axis is capacity; given a set of N disks, how much useful capacity is
available to systems that use the RAID? Without redundancy , the answer
is obviously N; however, if we have a system that keeps a two co pies of
each block, we will obtain a useful capacity of N/2. Differen t schemes
(e.g., parity-based ones) tend to fall in between.
The second axis of evaluation is reliability. How many disk faults can
the given design tolerate? In alignment with our fault model , we assume
only that an entire disk can fail; in later chapters (i.e., on data integrity),
we’ll think about how to handle more complex failure modes.
Finally , the third axis is performance. Performance is somewhat chal-
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 460

424 R EDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S)
lenging to evaluate, because it depends heavily on the workl oad pre-
sented to the disk array . Thus, before evaluating performan ce, we will
ﬁrst present a set of typical workloads that one should consi der.
We now consider three important RAID designs: RAID Level 0 (s trip-
ing), RAID Level 1 (mirroring), and RAID Levels 4/5 (parity- based re-
dundancy). The naming of each of these designs as a “level” st ems from
the pioneering work of Patterson, Gibson, and Katz at Berkel ey [P+88].
38.4 RAID Level 0: Striping
The ﬁrst RAID level is actually not a RAID level at all, in that there is
no redundancy . However, RAID level 0, or striping as it is better known,
serves as an excellent upper-bound on performance and capac ity and
thus is worth understanding.
The simplest form of striping will stripe blocks across the disks of the
system as follows (assume here a 4-disk array):
Disk 0 Disk 1 Disk 2 Disk 3
0 1 2 3
4 5 6 7
8 9 10 11
12 13 14 15
Table 38.1: RAID-0: Simple Striping
From Table
38.1, you get the basic idea: spread the blocks of the array
across the disks in a round-robin fashion. This approach is d esigned to
extract the most parallelism from the array when requests ar e made for
contiguous chunks of the array (as in a large, sequential rea d, for exam-
ple). We call the blocks in the same row a stripe; thus, blocks 0, 1, 2, and
3 are in the same stripe above.
In the example, we have made the simplifying assumption that only 1
block (each of say size 4KB) is placed on each disk before movi ng on to
the next. However, this arrangement need not be the case. For example,
we could arrange the blocks across disks as in Table 38.2:
Disk 0 Disk 1 Disk 2 Disk 3
0 2 4 6 chunk size:
1 3 5 7 2 blocks
8 10 12 14
9 11 13 15
Table 38.2: Striping with a Bigger Chunk Size
In this example, we place two 4KB blocks on each disk before mo ving
on to the next disk. Thus, the chunk size of this RAID array is 8KB, and
a stripe thus consists of 4 chunks or 32KB of data.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 461

REDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S) 425
ASIDE : THE RAID M APPING PROBLEM
Before studying the capacity , reliability , and performance characteristics
of the RAID, we ﬁrst present an aside on what we call the mapping prob-
lem. This problem arises in all RAID arrays; simply put, given a l ogical
block to read or write, how does the RAID know exactly which ph ysical
disk and offset to access?
For these simple RAID levels, we do not need much sophisticat ion in
order to correctly map logical blocks onto their physical lo cations. Take
the ﬁrst striping example above (chunk size = 1 block = 4KB). I n this case,
given a logical block address A, the RAID can easily compute t he desired
disk and offset with two simple equations:
Disk = A % number_of_disks
Offset = A / number_of_disks
Note that these are all integer operations (e.g., 4 / 3 = 1 not 1 .33333...).
Let’s see how these equations work for a simple example. Imag ine in the
ﬁrst RAID above that a request arrives for block 14. Given tha t there are
4 disks, this would mean that the disk we are interested in is ( 14 % 4 = 2):
disk 2. The exact block is calculated as (14 / 4 = 3): block 3. Th us, block
14 should be found on the fourth block (block 3, starting at 0) of the third
disk (disk 2, starting at 0), which is exactly where it is.
You can think about how these equations would be modiﬁed to su pport
different chunk sizes. Try it! It’s not too hard.
Chunk Sizes
Chunk size mostly affects performance of the array . For exam ple, a small
chunk size implies that many ﬁles will get striped across many disks, thus
increasing the parallelism of reads and writes to a single ﬁle; however, the
positioning time to access blocks across multiple disks inc reases, because
the positioning time for the entire request is determined by the maximum
of the positioning times of the requests across all drives.
A big chunk size, on the other hand, reduces such intra-ﬁle pa ral-
lelism, and thus relies on multiple concurrent requests to a chieve high
throughput. However, large chunk sizes reduce positioning time; if, for
example, a single ﬁle ﬁts within a chunk and thus is placed on a single
disk, the positioning time incurred while accessing it will just be the po-
sitioning time of a single disk.
Thus, determining the “best” chunk size is hard to do, as it re quires a
great deal of knowledge about the workload presented to the d isk system
[CL95]. For the rest of this discussion, we will assume that t he array uses
a chunk size of a single block (4KB). Most arrays use larger ch unk sizes
(e.g., 64 KB), but for the issues we discuss below , the exact c hunk size
does not matter; thus we use a single block for the sake of simp licity .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 462

426 R EDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S)
Back T o RAID-0 Analysis
Let us now evaluate the capacity , reliability , and performance of striping.
From the perspective of capacity , it is perfect: given N disk s, striping de-
livers N disks worth of useful capacity . From the standpoint of reliability ,
striping is also perfect, but in the bad way: any disk failure will lead to
data loss. Finally , performance is excellent: all disks are utilized, often in
parallel, to service user I/O requests.
Evaluating RAID Performance
In analyzing RAID performance, one can consider two differe nt perfor-
mance metrics. The ﬁrst is single-request latency . Understanding the la-
tency of a single I/O request to a RAID is useful as it reveals h ow much
parallelism can exist during a single logical I/O operation . The second
is steady-state throughput of the RAID, i.e., the total bandwidth of many
concurrent requests. Because RAIDs are often used in high-p erformance
environments, the steady-state bandwidth is critical, and thus will be the
main focus of our analyses.
To understand throughput in more detail, we need to put forth some
workloads of interest. We will assume, for this discussion, that there
are two types of workloads: sequential and random. With a sequential
workload, we assume that requests to the array come in large c ontiguous
chunks; for example, a request (or series of requests) that a ccesses 1 MB
of data, starting at block (B) and ending at block (B + 1 MB), wo uld be
deemed sequential. Sequential workloads are common in many environ-
ments (think of searching through a large ﬁle for a keyword), and thus
are considered important.
For random workloads, we assume that each request is rather s mall,
and that each request is to a different random location on dis k. For exam-
ple, a random stream of requests may ﬁrst access 4KB at logica l address
10, then at logical address 550,000, then at 20,100, and so fo rth. Some im-
portant workloads, such as transactional workloads on a dat abase man-
agement system (DBMS), exhibit this type of access pattern, and thus it is
considered an important workload.
Of course, real workloads are not so simple, and often have a m ix
of sequential and random-seeming components as well as beha viors in-
between the two. For simplicity , we just consider these two p ossibilities.
As you can tell, sequential and random workloads will result in widely
different performance characteristics from a disk. With se quential access,
a disk operates in its most efﬁcient mode, spending little time seeking and
waiting for rotation and most of its time transferring data. With random
access, just the opposite is true: most time is spent seeking and waiting
for rotation and relatively little time is spent transferri ng data. To capture
this difference in our analysis, we will assume that a disk ca n transfer
data at S MB/s under a sequential workload, and R MB/s when und er a
random workload. In general, S is much greater than R.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 463

REDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S) 427
To make sure we understand this difference, let’s do a simple exer-
cise. Speciﬁcally , lets calculate S and R given the followin g disk charac-
teristics. Assume a sequential transfer of size 10 MB on aver age, and a
random transfer of 10 KB on average. Also, assume the followi ng disk
characteristics:
A verage seek time 7 ms
A verage rotational delay 3 ms
Transfer rate of disk 50 MB/s
To compute S, we need to ﬁrst ﬁgure out how time is spent in a typ ical
10 MB transfer. First, we spend 7 ms seeking, and then 3 ms rota ting.
Finally , transfer begins; 10 MB @ 50 MB/s leads to 1/5th of a se cond, or
200 ms, spent in transfer. Thus, for each 10 MB request, we spe nd 210 ms
completing the request. To compute S, we just need to divide:
S = Amount of Data
T ime to access = 10 M B
210 ms = 47.62 M B/s
As we can see, because of the large time spent transferring da ta, S is
very near the peak bandwidth of the disk (the seek and rotatio nal costs
have been amortized).
We can compute R similarly . Seek and rotation are the same; we then
compute the time spent in transfer, which is 10 KB @ 50 MB/s, or 0.195
ms.
R = Amount of Data
T ime to access = 10 KB
10.195 ms = 0.981 M B/s
As we can see, R is less than 1 MB/s, and S/R is almost 50.
Back T o RAID-0 Analysis, Again
Let’s now evaluate the performance of striping. As we said ab ove, it is
generally good. From a latency perspective, for example, th e latency of a
single-block request should be just about identical to that of a single disk;
after all, RAID-0 will simply redirect that request to one of its disks.
From the perspective of steady-state throughput, we’d expe ct to get
the full bandwidth of the system. Thus, throughput equals N (the number
of disks) multiplied by S (the sequential bandwidth of a sing le disk). For
a large number of random I/Os, we can again use all of the disks , and
thus obtain N · R MB/s. As we will see below , these values are both
the simplest to calculate and will serve as an upper bound in c omparison
with other RAID levels.
38.5 RAID Level 1: Mirroring
Our ﬁrst RAID level beyond striping is known as RAID level 1, o r
mirroring. With a mirrored system, we simply make more than o ne copy
of each block in the system; each copy should be placed on a sep arate
disk, of course. By doing so, we can tolerate disk failures.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 464

428 R EDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S)
In a typical mirrored system, we will assume that for each log ical
block, the RAID keeps two physical copies of it. Here is an exa mple:
Disk 0 Disk 1 Disk 2 Disk 3
0 0 1 1
2 2 3 3
4 4 5 5
6 6 7 7
Table 38.3: Simple RAID-1: Mirroring
In the example, disk 0 and disk 1 have identical contents, and disk 2
and disk 3 do as well; the data is striped across these mirror p airs. In fact,
you may have noticed that there are a number of different ways to place
block copies across the disks. The arrangement above is a com mon one
and is sometimes called RAID-10 or (RAID 1+0) because it uses mirrored
pairs (RAID-1) and then stripes (RAID-0) on top of them; anot her com-
mon arrangement is RAID-01 (or RAID 0+1), which contains two large
striping (RAID-0) arrays, and then mirrors (RAID-1) on top o f them. For
now , we will just talk about mirroring assuming the above lay out.
When reading a block from a mirrored array , the RAID has a choice: it
can read either copy . For example, if a read to logical block 5 is issued to
the RAID, it is free to read it from either disk 2 or disk 3. When writing
a block, though, no such choice exists: the RAID must update both copies
of the data, in order to preserve reliability . Do note, thoug h, that these
writes can take place in parallel; for example, a write to log ical block 5
could proceed to disks 2 and 3 at the same time.
RAID-1 Analysis
Let us assess RAID-1. From a capacity standpoint, RAID-1 is e xpensive;
with the mirroring level = 2, we only obtain half of our peak us eful ca-
pacity . Thus, with N disks, the useful capacity of mirroring is N/2.
From a reliability standpoint, RAID-1 does well. It can tole rate the fail-
ure of any one disk. You may also notice RAID-1 can actually do better
than this, with a little luck. Imagine, in the ﬁgure above, th at disk 0 and
disk 2 both failed. In such a situation, there is no data loss! More gen-
erally , a mirrored system (with mirroring level of 2) can tol erate 1 disk
failure for certain, and up to N/2 failures depending on whic h disks fail.
In practice, we generally don’t like to leave things like thi s to chance; thus
most people consider mirroring to be good for handling a sing le failure.
Finally , we analyze performance. From the perspective of th e latency
of a single read request, we can see it is the same as the latenc y on a single
disk; all the RAID-1 does is direct the read to one of its copie s. A write
is a little different: it requires two physical writes to com plete before it
is done. These two writes happen in parallel, and thus the tim e will be
roughly equivalent to the time of a single write; however, be cause the
logical write must wait for both physical writes to complete , it suffers the
worst-case seek and rotational delay of the two requests, an d thus (on
average) will be slightly higher than a write to a single disk .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 465

REDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S) 429
ASIDE : THE RAID C ONSISTENT -U PDATE PROBLEM
Before analyzing RAID-1, let us ﬁrst discuss a problem that a rises in
any multi-disk RAID system, known as the consistent-update problem
[DAA05]. The problem occurs on a write to any RAID that has to u p-
date multiple disks during a single logical operation. In th is case, let us
assume we are considering a mirrored disk array .
Imagine the write is issued to the RAID, and then the RAID deci des that
it must be written to two disks, disk 0 and disk 1. The RAID then issues
the write to disk 0, but just before the RAID can issue the requ est to disk
1, a power loss (or system crash) occurs. In this unfortunate case, let us
assume that the request to disk 0 completed (but clearly the r equest to
disk 1 did not, as it was never issued).
The result of this untimely power loss is that the two copies o f the block
are now inconsistent; the copy on disk 0 is the new version, and the copy
on disk 1 is the old. What we would like to happen is for the stat e of both
disks to change atomically, i.e., either both should end up as the new
version or neither.
The general way to solve this problem is to use a write-ahead log of some
kind to ﬁrst record what the RAID is about to do (i.e., update t wo disks
with a certain piece of data) before doing it. By taking this a pproach, we
can ensure that in the presence of a crash, the right thing wil l happen; by
running a recovery procedure that replays all pending transactions to the
RAID, we can ensure that no two mirrored copies (in the RAID-1 case)
are out of sync.
One last note: because logging to disk on every write is prohi bitively
expensive, most RAID hardware includes a small amount of non -volatile
RAM (e.g., battery-backed) where it performs this type of lo gging. Thus,
consistent update is provided without the high cost of loggi ng to disk.
To analyze steady-state throughput, let us start with the se quential
workload. When writing out to disk sequentially , each logical write must
result in two physical writes; for example, when we write log ical block
0 (in the ﬁgure above), the RAID internally would write it to b oth disk
0 and disk 1. Thus, we can conclude that the maximum bandwidth ob-
tained during sequential writing to a mirrored array is ( N
2 · S), or half the
peak bandwidth.
Unfortunately , we obtain the exact same performance during a se-
quential read. One might think that a sequential read could d o better,
because it only needs to read one copy of the data, not both. Ho wever,
let’s use an example to illustrate why this doesn’t help much . Imagine we
need to read blocks 0, 1, 2, 3, 4, 5, 6, and 7. Let’s say we issue t he read of
0 to disk 0, the read of 1 to disk 2, the read of 2 to disk 1, and the read of
3 to disk 3. We continue by issuing reads to 4, 5, 6, and 7 to disk s 0, 2, 1,
and 3, respectively . One might naively think that because we are utilizing
all disks, we are achieving the full bandwidth of the array .
To see that this is not the case, however, consider the reques ts a single
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 466

430 R EDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S)
disk receives (say disk 0). First, it gets a request for block 0; then, it gets a
request for block 4 (skipping block 2). In fact, each disk rec eives a request
for every other block. While it is rotating over the skipped b lock, it is
not delivering useful bandwidth to the client. Thus, each di sk will only
deliver half its peak bandwidth. And thus, the sequential re ad will only
obtain a bandwidth of ( N
2 · S) MB/s.
Random reads are the best case for a mirrored RAID. In this cas e, we
can distribute the reads across all the disks, and thus obtai n the full pos-
sible bandwidth. Thus, for random reads, RAID-1 delivers N · R MB/s.
Finally , random writes perform as you might expect: N
2 ·R MB/s. Each
logical write must turn into two physical writes, and thus wh ile all the
disks will be in use, the client will only perceive this as hal f the available
bandwidth. Even though a write to logical block X turns into t wo parallel
writes to two different physical disks, the bandwidth of man y small re-
quests only achieves half of what we saw with striping. As we w ill soon
see, getting half the available bandwidth is actually prett y good!
38.6 RAID Level 4: Saving Space With Parity
We now present a different method of adding redundancy to a disk ar-
ray known as parity. Parity-based approaches attempt to use less capac-
ity and thus overcome the huge space penalty paid by mirrored systems.
They do so at a cost, however: performance.
In a ﬁve-disk RAID-4 system, we might observe the following l ayout:
Disk 0 Disk 1 Disk 2 Disk 3 Disk 4
0 1 2 3 P0
4 5 6 7 P1
8 9 10 11 P2
12 13 14 15 P3
As you can see, for each stripe of data, we have added a single par-
ity block that stores the redundant information for that stripe of blocks.
For example, parity block P1 has redundant information that it calculated
from blocks 4, 5, 6, and 7.
To compute parity , we need to use a mathematical function tha t en-
ables us to withstand the loss of any one block from our stripe . It turns
out the simple function XOR does the trick quite nicely . For a given set of
bits, the XOR of all of those bits returns a 0 if there are an eve n number of
1’s in the bits, and a 1 if there are an odd number of 1’s. For exa mple:
C0 C1 C2 C3 P
0 0 1 1 XOR(0,0,1,1) = 0
0 1 0 0 XOR(0,1,0,0) = 1
In the ﬁrst row (0,0,1,1), there are two 1’s (C2, C3), and thus XOR of
all of those values will be 0 (P); similarly , in the second row there is only
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 467

REDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S) 431
one 1 (C1), and thus the XOR must be 1 (P). You can remember this in a
very simple way: that the number of 1’s in any row must be an eve n (not
odd) number; that is the invariant that the RAID must maintain in order
for parity to be correct.
From the example above, you might also be able to guess how par ity
information can be used to recover from a failure. Imagine th e column la-
beled C2 is lost. To ﬁgure out what values must have been in the column,
we simply have to read in all the other values in that row (incl uding the
XOR’d parity bit) and reconstruct the right answer. Speciﬁcally , assume
the ﬁrst row’s value in column C2 is lost (it is a 1); by reading the other
values in that row (0 from C0, 0 from C1, 1 from C3, and 0 from the parity
column P), we get the values 0, 0, 1, and 0. Because we know that XOR
keeps an even number of 1’s in each row , we know what the missin g data
must be: a 1. And that is how reconstruction works in a XOR-bas ed par-
ity scheme! Note also how we compute the reconstructed value : we just
XOR the data bits and the parity bits together, in the same way that we
calculated the parity in the ﬁrst place.
Now you might be wondering: we are talking about XORing all of
these bits, and yet above we know that the RAID places 4KB (or l arger)
blocks on each disk; how do we apply XOR to a bunch of blocks to c om-
pute the parity? It turns out this is easy as well. Simply perf orm a bitwise
XOR across each bit of the data blocks; put the result of each b itwise XOR
into the corresponding bit slot in the parity block. For exam ple, if we had
blocks of size 4 bits (yes, this is still quite a bit smaller th an a 4KB block,
but you get the picture), they might look something like this :
Block0 Block1 Block2 Block3 Parity
00 10 11 10 11
10 01 00 01 10
As you can see from the ﬁgure, the parity is computed for each b it of
each block and the result placed in the parity block.
RAID-4 Analysis
Let us now analyze RAID-4. From a capacity standpoint, RAID- 4 uses 1
disk for parity information for every group of disks it is pro tecting. Thus,
our useful capacity for a RAID group is (N-1).
Reliability is also quite easy to understand: RAID-4 tolera tes 1 disk
failure and no more. If more than one disk is lost, there is sim ply no way
to reconstruct the lost data.
Finally , there is performance. This time, let us start by analyzing steady-
state throughput. Sequential read performance can utilize all of the disks
except for the parity disk, and thus deliver a peak effective bandwidth of
(N − 1) · S MB/s (an easy case).
To understand the performance of sequential writes, we must ﬁrst un-
derstand how they are done. When writing a big chunk of data to disk,
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 468

432 R EDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S)
RAID-4 can perform a simple optimization known as a full-stripe write.
For example, imagine the case where the blocks 0, 1, 2, and 3 ha ve been
sent to the RAID as part of a write request (Table 38.4).
Disk 0 Disk 1 Disk 2 Disk 3 Disk 4
0 1 2 3 P0
4 5 6 7 P1
8 9 10 11 P2
12 13 14 15 P3
Table 38.4: Full-stripe Writes In RAID-4
In this case, the RAID can simply calculate the new value of P0 (by
performing an XOR across the blocks 0, 1, 2, and 3) and then wri te all of
the blocks (including the parity block) to the ﬁve disks abov e in parallel
(highlighted in gray in the ﬁgure). Thus, full-stripe write s are the most
efﬁcient way for RAID-4 to write to disk.
Once we understand the full-stripe write, calculating the p erformance
of sequential writes on RAID-4 is easy; the effective bandwi dth is also
(N − 1) · S MB/s. Even though the parity disk is constantly in use during
the operation, the client does not gain performance advanta ge from it.
Now let us analyze the performance of random reads. As you can also
see from the ﬁgure above, a set of 1-block random reads will be spread
across the data disks of the system but not the parity disk. Th us, the
effective performance is: (N − 1) · R MB/s.
Random writes, which we have saved for last, present the most in-
teresting case for RAID-4. Imagine we wish to overwrite bloc k 1 in the
example above. We could just go ahead and overwrite it, but th at would
leave us with a problem: the parity block P0 would no longer ac curately
reﬂect the correct parity value for the stripe. Thus, in this example, P0
must also be updated. But how can we update it both correctly a nd efﬁ-
ciently?
It turns out there are two methods. The ﬁrst, known as additive parity,
requires us to do the following. To compute the value of the ne w parity
block, read in all of the other data blocks in the stripe in par allel (in the
example, blocks 0, 2, and 3) and XOR those with the new block (1 ). The
result is your new parity block. To complete the write, you ca n then write
the new data and new parity to their respective disks, also in parallel.
The problem with this technique is that it scales with the num ber of
disks, and thus in larger RAIDs requires a high number of read s to com-
pute parity . Thus, the subtractive parity method.
For example, imagine this string of bits (4 data bits, one par ity):
C0 C1 C2 C3 P
0 0 1 1 XOR(0,0,1,1) = 0
Let’s imagine that we wish to overwrite bit C2 with a new value which
we will call C2(new). The subtractive method works in three s teps. First,
we read in the old data at C2 (C2(old) = 1) and the old parity (P( old) =
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 469

REDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S) 433
0). Then, we compare the old data and the new data; if they are t he same
(e.g., C2(new) = C2(old)), then we know the parity bit will al so remain
the same (i.e., P(new) = P(old)). If, however, they are diffe rent, then we
must ﬂip the old parity bit to the opposite of its current stat e, that is, if
(P(old) == 1), P(new) will be set to 0; if (P(old) == 0), P(new) will be set to
1. We can express this whole mess neatly with XOR as it turns ou t (if you
understand XOR, this will now make sense to you):
P(new) = (C(old) XOR C(new)) XOR P(old)
Because we are dealing with blocks, not bits, we perform this calcula-
tion over all the bits in the block (e.g., 4096 bytes in each bl ock multiplied
by 8 bits per byte). Thus, in most cases, the new block will be d ifferent
than the old block and thus the new parity block will too.
You should now be able to ﬁgure out when we would use the additi ve
parity calculation and when we would use the subtractive method. Think
about how many disks would need to be in the system so that the additive
method performs fewer I/Os than the subtractive method; wha t is the
cross-over point?
For this performance analysis, let us assume we are using the subtrac-
tive method. Thus, for each write, the RAID has to perform 4 ph ysical
I/Os (two reads and two writes). Now imagine there are lots of writes
submitted to the RAID; how many can RAID-4 perform in paralle l? To
understand, let us again look at the RAID-4 layout (Figure 38.5).
Disk 0 Disk 1 Disk 2 Disk 3 Disk 4
0 1 2 3 P0
∗4 5 6 7 +P1
8 9 10 11 P2
12 ∗13 14 15 +P3
Table 38.5: Example: Writes T o 4, 13, And Respective Parity Blocks
Now imagine there were 2 small writes submitted to the RAID-4 at
about the same time, to blocks 4 and 13 (marked with ∗ in the diagram).
The data for those disks is on disks 0 and 1, and thus the read an d write
to data could happen in parallel, which is good. The problem t hat arises
is with the parity disk; both the requests have to read the rel ated parity
blocks for 4 and 13, parity blocks 1 and 3 (marked with +). Hopefully , the
issue is now clear: the parity disk is a bottleneck under this type of work-
load; we sometimes thus call this the small-write problem for parity-
based RAIDs. Thus, even though the data disks could be access ed in
parallel, the parity disk prevents any parallelism from mat erializing; all
writes to the system will be serialized because of the parity disk. Because
the parity disk has to perform two I/Os (one read, one write) p er logical
I/O, we can compute the performance of small random writes in RAID-4
by computing the parity disk’s performance on those two I/Os , and thus
we achieve (R/2) MB/s. RAID-4 throughput under random small writes
is terrible; it does not improve as you add disks to the system .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 470

434 R EDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S)
We conclude by analyzing I/O latency in RAID-4. As you now kno w ,
a single read (assuming no failure) is just mapped to a single disk, and
thus its latency is equivalent to the latency of a single disk request. The
latency of a single write requires two reads and then two writes; the reads
can happen in parallel, as can the writes, and thus total late ncy is about
twice that of a single disk (with some differences because we have to wait
for both reads to complete and thus get the worst-case positi oning time,
but then the updates don’t incur seek cost and thus may be a bet ter-than-
average positioning cost).
38.7 RAID Level 5: Rotating Parity
To address the small-write problem (at least, partially), Patterson, Gib-
son, and Katz introduced RAID-5. RAID-5 works almost identi cally to
RAID-4, except that it rotates the parity block across drives (Figure 38.6).
Disk 0 Disk 1 Disk 2 Disk 3 Disk 4
0 1 2 3 P0
5 6 7 P1 4
10 11 P2 8 9
15 P3 12 13 14
P4 16 17 18 19
Table 38.6: RAID-5 With Rotated Parity
As you can see, the parity block for each stripe is now rotated across
the disks, in order to remove the parity-disk bottleneck for RAID-4.
RAID-5 Analysis
Much of the analysis for RAID-5 is identical to RAID-4. For ex ample, the
effective capacity and failure tolerance of the two levels a re identical. So
are sequential read and write performance. The latency of a single request
(whether a read or a write) is also the same as RAID-4.
Random read performance is a little better, because we can utilize all of
the disks. Finally , random write performance improves noti ceably over
RAID-4, as it allows for parallelism across requests. Imagi ne a write to
block 1 and a write to block 10; this will turn into requests to disk 1 and
disk 4 (for block 1 and its parity) and requests to disk 0 and di sk 2 (for
block 10 and its parity). Thus, they can proceed in parallel. In fact, we
can generally assume that that given a large number of random requests,
we will be able to keep all the disks about evenly busy . If that is the case,
then our total bandwidth for small writes will be N
4 · R MB/s. The factor
of four loss is due to the fact that each RAID-5 write still gen erates 4 total
I/O operations, which is simply the cost of using parity-bas ed RAID.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 471

REDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S) 435
RAID-0 RAID-1 RAID-4 RAID-5
Capacity N N/ 2 N − 1 N − 1
Reliability 0 1 (for sure) 1 1
N
2 (if lucky)
Throughput
Sequential Read N · S (N/2) · S (N − 1) · S (N − 1) · S
Sequential Write N · S (N/2) · S (N − 1) · S (N − 1) · S
Random Read N · R N · R (N − 1) · R N · R
Random Write N · R (N/2) · R 1
2 · R N
4 R
Latency
Read D D D D
Write D D 2D 2D
Table 38.7: RAID Capacity, Reliability, and Performance
Because RAID-5 is basically identical to RAID-4 except in the few cases
where it is better, it has almost completely replaced RAID-4in the market-
place. The only place where it has not is in systems that know t hey will
never perform anything other than a large write, thus avoidi ng the small-
write problem altogether [HLM94]; in those cases, RAID-4 is sometimes
used as it is slightly simpler to build.
38.8 RAID Comparison: A Summary
We now summarize our simpliﬁed comparison of RAID levels in T a-
ble 38.7. Note that we have omitted a number of details to simplify our
analysis. For example, when writing in a mirrored system, th e average
seek time is a little higher than when writing to just a single disk, because
the seek time is the max of two seeks (one on each disk). Thus, r andom
write performance to two disks will generally be a little les s than random
write performance of a single disk. Also, when updating the p arity disk
in RAID-4/5, the ﬁrst read of the old parity will likely cause a full seek
and rotation, but the second write of the parity will only result in rotation.
However, our comparison does capture the essential differe nces, and
is useful for understanding tradeoffs across RAID levels. W e present a
summary in the table below; for the latency analysis, we simp ly use D to
represent the time that a request to a single disk would take.
To conclude, if you strictly want performance and do not care about
reliability , striping is obviously best. If, however, you w ant random I/O
performance and reliability , mirroring is the best; the cos t you pay is in
lost capacity . If capacity and reliability are your main goa ls, then RAID-
5 is the winner; the cost you pay is in small-write performanc e. Finally ,
if you are always doing sequential I/O and want to maximize ca pacity ,
RAID-5 also makes the most sense.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 472

436 R EDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S)
38.9 Other Interesting RAID Issues
There are a number of other interesting ideas that one could ( and per-
haps should) discuss when thinking about RAID. Here are some things
we might eventually write about.
For example, there are many other RAID designs, including Le vels 2
and 3 from the original taxonomy , and Level 6 to tolerate mult iple disk
faults [C+04]. There is also what the RAID does when a disk fai ls; some-
times it has a hot spare sitting around to ﬁll in for the failed disk. What
happens to performance under failure, and performance duri ng recon-
struction of the failed disk? There are also more realistic f ault models,
to take into account latent sector errors or block corruption [B+08], and
lots of techniques to handle such faults (see the data integr ity chapter for
details). Finally , you can even build raid as a software laye r: such soft-
ware RAID systems are cheaper but have other problems, including the
consistent-update problem [DAA05].
38.10 Summary
We have discussed RAID. RAID transforms a number of independ ent
disks into a large, more capacious, and more reliable single entity; impor-
tantly , it does so transparently , and thus hardware and software above is
relatively oblivious to the change.
There are many possible RAID levels to choose from, and the ex act
RAID level to use depends heavily on what is important to the e nd-user.
For example, mirrored RAID is simple, reliable, and general ly provides
good performance but at a high capacity cost. RAID-5, in cont rast, is
reliable and better from a capacity standpoint, but perform s quite poorly
when there are small writes in the workload. Picking a RAID an d setting
its parameters (chunk size, number of disks, etc.) properly for a particular
workload is challenging, and remains more of an art than a sci ence.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 473

REDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S) 437
References
[B+08] “An Analysis of Data Corruption in the Storage Stack”
Lakshmi N. Bairavasundaram, Garth R. Goodson, Bianca Schroeder, Andrea C. Arpaci-Dusseau,
Remzi H. Arpaci-Dusseau
FAST ’08, San Jose, CA, February 2008
Our own work analyzing how often disks actually corrupt your data. Not often, but sometimes! And
thus something a reliable storage system must consider.
[BJ88] “Disk Shadowing”
D. Bitton and J. Gray
VLDB 1988
One of the ﬁrst papers to discuss mirroring, herein called “s hadowing”.
[CL95] “Striping in a RAID level 5 disk array”
Peter M. Chen, Edward K. Lee
SIGMETRICS 1995
A nice analysis of some of the important parameters in a RAID- 5 disk array.
[C+04] “Row-Diagonal Parity for Double Disk Failure Correc tion”
P . Corbett, B. English, A. Goel, T. Grcanac, S. Kleiman, J. Le ong, S. Sankar
FAST ’04, February 2004
Though not the ﬁrst paper on a RAID system with two disks for pa rity, it is a recent and highly-
understandable version of said idea. Read it to learn more.
[DAA05] “Journal-guided Resynchronization for Software R AID”
Timothy E. Denehy , A. Arpaci-Dusseau, R. Arpaci-Dusseau
FAST 2005
Our own work on the consistent-update problem. Here we solve it for Software RAID by integrating
the journaling machinery of the ﬁle system above with the sof tware RAID beneath it.
[HLM94] “File System Design for an NFS File Server Appliance ”
Dave Hitz, James Lau, Michael Malcolm
USENIX Winter 1994, San Francisco, California, 1994
The sparse paper introducing a landmark product in storage, the write-anywhere ﬁle layout or WAFL
ﬁle system that underlies the NetApp ﬁle server.
[K86] “Synchronized Disk Interleaving”
M.Y . Kim.
IEEE Transactions on Computers, V olume C-35: 11, November 1986
Some of the earliest work on RAID is found here.
[K88] “Small Disk Arrays - The Emerging Approach to High Perf ormance”
F. Kurzweil.
Presentation at Spring COMPCON ’88, March 1, 1988, San Franc isco, California
Another early RAID reference.
[P+88] “Redundant Arrays of Inexpensive Disks”
D. Patterson, G. Gibson, R. Katz.
SIGMOD 1988
This is considered the RAID paper, written by famous authors Patterson, Gibson, an d Katz. The paper
has since won many test-of-time awards and ushered in the RAI D era, including the name RAID itself!
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 474

438 R EDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S)
[PB86] “Providing Fault Tolerance in Parallel Secondary St orage Systems”
A. Park and K. Balasubramaniam
Department of Computer Science, Princeton, CS-TR-O57-86, November 1986
Another early work on RAID.
[SG86] “Disk Striping”
K. Salem and H. Garcia-Molina.
IEEE International Conference on Data Engineering, 1986
And yes, another early RAID work. There are a lot of these, whi ch kind of came out of the woodwork
when the RAID paper was published in SIGMOD.
[S84] “Byzantine Generals in Action: Implementing Fail-St op Processors”
F.B. Schneider.
ACM Transactions on Computer Systems, 2(2):145154, May 198 4
Finally, a paper that is not about RAID! This paper is actuall y about how systems fail, and how to make
something behave in a fail-stop manner.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 475

REDUNDANT ARRAYS OF INEXPENSIVE DISKS (RAID S) 439
Homework
This section introduces raid.py, a simple RAID simulator you can
use to shore up your knowledge of how RAID systems work. See th e
README for details.
Questions
1. Use the simulator to perform some basic RAID mapping tests . Run
with different levels (0, 1, 4, 5) and see if you can ﬁgure out t he
mappings of a set of requests. For RAID-5, see if you can ﬁgure out
the difference between left-symmetric and left-asymmetri c layouts.
Use some different random seeds to generate different probl ems
than above.
2. Do the same as the ﬁrst problem, but this time vary the chunk size
with -C. How does chunk size change the mappings?
3. Do the same as above, but use the -r ﬂag to reverse the nature of
each problem.
4. Now use the reverse ﬂag but increase the size of each reques t with
the -S ﬂag. Try specifying sizes of 8k, 12k, and 16k, while varying
the RAID level. What happens to the underlying I/O pattern wh en
the size of the request increases? Make sure to try this with t he
sequential workload too ( -W sequential ); for what request sizes
are RAID-4 and RAID-5 much more I/O efﬁcient?
5. Use the timing mode of the simulator ( -t) to estimate the perfor-
mance of 100 random reads to the RAID, while varying the RAID
levels, using 4 disks.
6. Do the same as above, but increase the number of disks. How d oes
the performance of each RAID level scale as the number of disk s
increases?
7. Do the same as above, but use all writes ( -w 100 ) instead of reads.
How does the performance of each RAID level scale now? Can you
do a rough estimate of the time it will take to complete the workload
of 100 random writes?
8. Run the timing mode one last time, but this time with a seque n-
tial workload (-W sequential ). How does the performance vary
with RAID level, and when doing reads versus writes? How abou t
when varying the size of each request? What size should you wr ite
to a RAID when using RAID-4 or RAID-5?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 477

39
Interlude: File and Directories
Thus far we have seen the development of two key operating sys tem ab-
stractions: the process, which is a virtualization of the CP U, and the ad-
dress space, which is a virtualization of memory . In tandem, these two
abstractions allow a program to run as if it is in its own priva te, isolated
world; as if it has its own processor (or processors); as if it has its own
memory . This illusion makes programming the system much eas ier and
thus is prevalent today not only on desktops and servers but i ncreasingly
on all programmable platforms including mobile phones and t he like.
In this section, we add one more critical piece to the virtualization puz-
zle: persistent storage. A persistent-storage device, such as a classic hard
disk drive or a more modern solid-state storage device , stores informa-
tion permanently (or at least, for a long time). Unlike memor y , whose
contents are lost when there is a power loss, a persistent-st orage device
keeps such data intact. Thus, the OS must take extra care with such a
device: this is where users keep data that they really care ab out.
CRUX : H OW TO MANAGE A P ERSISTENT DEVICE
How should the OS manage a persistent device? What are the API s?
What are the important aspects of the implementation?
Thus, in the next few chapters, we will explore critical tech niques for
managing persistent data, focusing on methods to improve pe rformance
and reliability . We begin, however, with an overview of the A PI: the in-
terfaces you’ll expect to see when interacting with a U NIX ﬁle system.
39.1 Files and Directories
Two key abstractions have developed over time in the virtual ization
of storage. The ﬁrst is the ﬁle. A ﬁle is simply a linear array of bytes,
each of which you can read or write. Each ﬁle has some kind of low-level
441

## Page 478

442 INTERLUDE : F ILE AND DIRECTORIES
name, usually a number of some kind; often, the user is not aware of
this name (as we will see). For historical reasons, the low-l evel name of a
ﬁle is often referred to as its inode number. We’ll be learning a lot more
about inodes in future chapters; for now , just assume that each ﬁle has an
inode number associated with it.
In most systems, the OS does not know much about the structure of
the ﬁle (e.g., whether it is a picture, or a text ﬁle, or C code) ; rather, the
responsibility of the ﬁle system is simply to store such data persistently
on disk and make sure that when you request the data again, you get
what you put there in the ﬁrst place. Doing so is not as simple a s it seems!
The second abstraction is that of a directory. A directory , like a ﬁle,
also has a low-level name (i.e., an inode number), but its con tents are
quite speciﬁc: it contains a list of (user-readable name, lo w-level name)
pairs. For example, let’s say there is a ﬁle with the low-leve l name “10”,
and it is referred to by the user-readable name of “foo”. The d irectory
“foo” resides in thus would have an entry (“foo”, “10”) that m aps the
user-readable name to the low-level name. Each entry in a directory refers
to either ﬁles or other directories. By placing directories within other di-
rectories, users are able to build an arbitrary directory tree (or directory
hierarchy), under which all ﬁles and directories are stored.
/
foo
bar.txt
bar
foobar
bar.txt
Figure 39.1: An Example Directory T ree
The directory hierarchy starts at a root directory (in U NIX -based sys-
tems, the root directory is simply referred to as /) and uses some kind
of separator to name subsequent sub-directories until the desired ﬁle or
directory is named. For example, if a user created a director y foo in the
root directory /, and then created a ﬁle bar.txt in the directory foo,
we could refer to the ﬁle by its absolute pathname , which in this case
would be /foo/bar.txt. See Figure 39.1 for a more complex directory
tree; valid directories in the example are /, /foo, /bar, /bar/bar,
/bar/foo and valid ﬁles are /foo/bar.txt and /bar/foo/bar.txt.
Directories and ﬁles can have the same name as long as they are in dif-
ferent locations in the ﬁle-system tree (e.g., there are two ﬁles named
bar.txt in the ﬁgure, /foo/bar.txt and /bar/foo/bar.txt).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 479

INTERLUDE : F ILE AND DIRECTORIES 443
TIP : T HINK CAREFULLY ABOUT NAMING
Naming is an important aspect of computer systems [SK09]. In UNIX
systems, virtually everything that you can think of is named through the
ﬁle system. Beyond just ﬁles, devices, pipes, and even proce sses [K84]
can be found in what looks like a plain old ﬁle system. This uni formity
of naming eases your conceptual model of the system, and make s the
system simpler and more modular. Thus, whenever creating a s ystem or
interface, think carefully about what names you are using.
You may also notice that the ﬁle name in this example often has two
parts: bar and txt, separated by a period. The ﬁrst part is an arbitrary
name, whereas the second part of the ﬁle name is usually used t o indi-
cate the type of the ﬁle, e.g., whether it is C code (e.g., .c), or an image
(e.g., .jpg), or a music ﬁle (e.g., .mp3). However, this is usually just a
convention: there is usually no enforcement that the data contained in a
ﬁle named main.c is indeed C source code.
Thus, we can see one great thing provided by the ﬁle system: a c onve-
nient way to name all the ﬁles we are interested in. Names are important
in systems as the ﬁrst step to accessing any resource is being able to name
it. In U NIX systems, the ﬁle system thus provides a uniﬁed way to access
ﬁles on disk, USB stick, CD-ROM, many other devices, and in fa ct many
other things, all located under the single directory tree.
39.2 The File System Interface
Let’s now discuss the ﬁle system interface in more detail. We ’ll start
with the basics of creating, accessing, and deleting ﬁles. Y ou may think
this straightforward, but along the way we’ll discover the m ysterious call
that is used to remove ﬁles, known as unlink(). Hopefully , by the end
of this chapter, this mystery won’t be so mysterious to you!
39.3 Creating Files
We’ll start with the most basic of operations: creating a ﬁle . This can be
accomplished with the open system call; by calling open() and passing
it the O CREAT ﬂag, a program can create a new ﬁle. Here is some exam-
ple code to create a ﬁle called “foo” in the current working di rectory .
int fd = open("foo", O_CREAT | O_WRONLY | O_TRUNC);
The routine open() takes a number of different ﬂags. In this exam-
ple, the program creates the ﬁle ( O CREAT), can only write to that ﬁle
while opened in this manner ( O WRONLY), and, if the ﬁle already exists,
ﬁrst truncate it to a size of zero bytes thus removing any exis ting content
(O TRUNC).
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 480

444 INTERLUDE : F ILE AND DIRECTORIES
ASIDE : THE C R E A T() SYSTEM CALL
The older way of creating a ﬁle is to call creat(), as follows:
int fd = creat("foo");
You can think of creat() as open() with the following ﬂags:
O CREAT | O WRONLY | O TRUNC. Because open() can create a ﬁle,
the usage of creat() has somewhat fallen out of favor (indeed, it could
just be implemented as a library call to open()); however, it does hold a
special place in U NIX lore. Speciﬁcally , when Ken Thompson was asked
what he would do differently if he were redesigning U NIX , he replied:
“I’d spell creat with an e.”
One important aspect of open() is what it returns: a ﬁle descriptor. A
ﬁle descriptor is just an integer, private per process, and i s used in U NIX
systems to access ﬁles; thus, once a ﬁle is opened, you use the ﬁle de-
scriptor to read or write the ﬁle, assuming you have permissi on to do so.
In this way , a ﬁle descriptor is a capability [L84], i.e., an opaque handle
that gives you the power to perform certain operations. Anot her way to
think of a ﬁle descriptor is as a pointer to an object of type ﬁl e; once you
have such an object, you can call other “methods” to access th e ﬁle, like
read() and write(). We’ll see just how a ﬁle descriptor is used below .
39.4 Reading and Writing Files
Once we have some ﬁles, of course we might like to read or writethem.
Let’s start by reading an existing ﬁle. If we were typing at a c ommand
line, we might just use the program cat to dump the contents of the ﬁle
to the screen.
prompt> echo hello > foo
prompt> cat foo
hello
prompt>
In this code snippet, we redirect the output of the program echo to
the ﬁle foo, which then contains the word “hello” in it. We then use cat
to see the contents of the ﬁle. But how does the cat program access the
ﬁle foo?
To ﬁnd this out, we’ll use an incredibly useful tool to trace t he system
calls made by a program. On Linux, the tool is called strace; other sys-
tems have similar tools (see dtruss on Mac OS X, or truss on some older
UNIX variants). What strace does is trace every system call made by a
program while it runs, and dump the trace to the screen for you to see.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

