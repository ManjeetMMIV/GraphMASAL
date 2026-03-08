# Document: operating_systems_three_easy_pieces (Pages 521 to 560)

## Page 521

LOCALITY AND THE FAST FILE SYSTEM 485
Here is the depiction of FFS without the large-ﬁle exception :
G0 G1 G2 G3 G4 G5 G6 G7 G8 G9
0 1 2 3 4
5 6 7 8 9
With the large-ﬁle exception, we might see something more like this, with
the ﬁle spread across the disk in chunks:
G0 G1 G2 G3 G4 G5 G6 G7 G8 G9
0 1 2 3 4 5 6 78 9
The astute reader will note that spreading blocks of a ﬁle acr oss the
disk will hurt performance, particularly in the relatively common case
of sequential ﬁle access (e.g., when a user or application re ads chunks 0
through 9 in order). And you are right! It will. We can help thi s a little,
by choosing our chunk size carefully .
Speciﬁcally , if the chunk size is large enough, we will still spend most
of our time transferring data from disk and just a relatively little time
seeking between chunks of the block. This process of reducin g an over-
head by doing more work per overhead paid is called amortization and
is a common technique in computer systems.
Let’s do an example: assume that the average positioning tim e (i.e.,
seek and rotation) for a disk is 10 ms. Assume further that the disk trans-
fers data at 40 MB/s. If our goal was to spend half our time seek ing be-
tween chunks and half our time transferring data (and thus ac hieve 50%
of peak disk performance), we would thus need to spend 10 ms tr ansfer-
ring data for every 10 ms positioning. So the question become s: how big
does a chunk have to be in order to spend 10 ms in transfer? Easy , just
use our old friend, math, in particular the dimensional anal ysis we spoke
of in the chapter on disks:
40 M B
sec · 1024 KB
1 M B · 1 sec
1000 ms · 10 ms = 409.6 KB (41.1)
Basically , what this equation says is this: if you transfer d ata at 40
MB/s, you need to transfer only 409.6 KB every time you seek in order to
spend half your time seeking and half your time transferring . Similarly ,
you can compute the size of the chunk you would need to achieve 90%
of peak bandwidth (turns out it is about 3.69 MB), or even 99% o f peak
bandwidth (40.6 MB!). As you can see, the closer you want to ge t to peak,
the bigger these chunks get (see Figure 41.2 for a plot of these values).
FFS did not use this type of calculation in order to spread lar ge ﬁles
across groups, however. Instead, it took a simple approach, based on the
structure of the inode itself. The ﬁrst twelve direct blocks were placed
in the same group as the inode; each subsequent indirect bloc k, and all
the blocks it pointed to, was placed in a different group. Wit h a block
size of 4-KB, and 32-bit disk addresses, this strategy impli es that every
1024 blocks of the ﬁle (4 MB) were placed in separate groups, t he lone
exception being the ﬁrst 48-KB of the ﬁle as pointed to by dire ct pointers.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 522

486 LOCALITY AND THE FAST FILE SYSTEM
0% 25% 50% 75% 100%
1K
32K
1M
10M
The Challenges of Amortization
Percent Bandwidth (Desired)
Log(Chunk Size Needed)
50%, 409.6K
90%, 3.69M
Figure 41.2: Amortization: How Big Do Chunks Have T o Be?
We should note that the trend in disk drives is that transfer r ate im-
proves fairly rapidly , as disk manufacturers are good at cra mming more
bits into the same surface, but the mechanical aspects of dri ves related
to seeks (disk arm speed and the rate of rotation) improve rat her slowly
[P98]. The implication is that over time, mechanical costs b ecome rel-
atively more expensive, and thus, to amortize said costs, yo u have to
transfer more data between seeks.
41.7 A Few Other Things About FFS
FFS introduced a few other innovations too. In particular, t he design-
ers were extremely worried about accommodating small ﬁles; as it turned
out, many ﬁles were 2 KB or so in size back then, and using 4-KB b locks,
while good for transferring data, was not so good for space ef ﬁciency .
This internal fragmentation could thus lead to roughly half the disk be-
ing wasted for a typical ﬁle system.
The solution the FFS designers hit upon was simple and solved the
problem. They decided to introduce sub-blocks, which were 512-byte lit-
tle blocks that the ﬁle system could allocate to ﬁles. Thus, i f you created a
small ﬁle (say 1 KB in size), it would occupy two sub-blocks an d thus not
waste an entire 4-KB block. As the ﬁle grew , the ﬁle system wil l continue
allocating 512-byte blocks to it until it acquires a full 4-K B of data. At that
point, FFS will ﬁnd a 4-KB block, copy the sub-blocks into it, and free the
sub-blocks for future use.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 523

LOCALITY AND THE FAST FILE SYSTEM 487
0
11
1098
7
6
5
4 3 2
1
Spindle
0
11
5104
9
3
8
2 7 1
6
Spindle
Figure 41.3: FFS: Standard V ersus Parameterized Placement
You might observe that this process is inefﬁcient, requirin g a lot of ex-
tra work for the ﬁle system (in particular, a lot of extra I/O t o perform the
copy). And you’d be right again! Thus, FFS generally avoided this pes-
simal behavior by modifying the libc library; the library would buffer
writes and then issue them in 4-KB chunks to the ﬁle system, th us avoid-
ing the sub-block specialization entirely in most cases.
A second neat thing that FFS introduced was a disk layout that was
optimized for performance. In those times (before SCSI and o ther more
modern device interfaces), disks were much less sophistica ted and re-
quired the host CPU to control their operation in a more hands -on way .
A problem arose in FFS when a ﬁle was placed on consecutive sec tors of
the disk, as on the left in Figure 41.3.
In particular, the problem arose during sequential reads. F FS would
ﬁrst issue a read to block 0; by the time the read was complete, and FFS
issued a read to block 1, it was too late: block 1 had rotated un der the
head and now the read to block 1 would incur a full rotation.
FFS solved this problem with a different layout, as you can se e on the
right in Figure 41.3. By skipping over every other block (in the example),
FFS has enough time to request the next block before it went pa st the
disk head. In fact, FFS was smart enough to ﬁgure out for a part icular
disk how many blocks it should skip in doing layout in order to avoid the
extra rotations; this technique was called parameterization, as FFS would
ﬁgure out the speciﬁc performance parameters of the disk and use those
to decide on the exact staggered layout scheme.
You might be thinking: this scheme isn’t so great after all. I n fact, you
will only get 50% of peak bandwidth with this type of layout, b ecause
you have to go around each track twice just to read each block o nce. For-
tunately , modern disks are much smarter: they internally re ad the entire
track in and buffer it in an internal disk cache (often called a track buffer
for this very reason). Then, on subsequent reads to the track , the disk will
just return the desired data from its cache. File systems thu s no longer
have to worry about these incredibly low-level details. Abs traction and
higher-level interfaces can be a good thing, when designed p roperly .
Some other usability improvements were added as well. FFS wa s one
of the ﬁrst ﬁle systems to allow for long ﬁle names , thus enabling more
expressive names in the ﬁle system instead of a the tradition al ﬁxed-size
approach (e.g., 8 characters). Further, a new concept was in troduced
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 524

488 LOCALITY AND THE FAST FILE SYSTEM
TIP : M AKE THE SYSTEM USABLE
Probably the most basic lesson from FFS is that not only did it intro-
duce the conceptually good idea of disk-aware layout, but it also added
a number of features that simply made the system more usable. Long ﬁle
names, symbolic links, and a rename operation that worked at omically
all improved the utility of a system; while hard to write a res earch pa-
per about (imagine trying to read a 14-pager about “The Symbo lic Link:
Hard Link’s Long Lost Cousin”), such small features made FFS more use-
ful and thus likely increased its chances for adoption. Maki ng a system
usable is often as or more important than its deep technical i nnovations.
called a symbolic link. As discussed in a previous chapter, hard links are
limited in that they both could not point to directories (for fear of intro-
ducing loops in the ﬁle system hierarchy) and that they can on ly point to
ﬁles within the same volume (i.e., the inode number must stil l be mean-
ingful). Symbolic links allow the user to create an “alias” t o any other
ﬁle or directory on a system and thus are much more ﬂexible. FF S also
introduced an atomic rename() operation for renaming ﬁles. Usabil-
ity improvements, beyond the basic technology , also likely gained FFS a
stronger user base.
41.8 Summary
The introduction of FFS was a watershed moment in ﬁle system h is-
tory , as it made clear that the problem of ﬁle management was o ne of the
most interesting issues within an operating system, and sho wed how one
might begin to deal with that most important of devices, the h ard disk.
Since that time, hundreds of new ﬁle systems have developed, but still
today many ﬁle systems take cues from FFS (e.g., Linux ext2 an d ext3 are
obvious intellectual descendants). Certainly all modern s ystems account
for the main lesson of FFS: treat the disk like it’s a disk.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 525

LOCALITY AND THE FAST FILE SYSTEM 489
References
[MJLF84] “A Fast File System for U NIX”
Marshall K. McKusick, William N. Joy , Sam J. Lefﬂer, Robert S. Fabry
ACM Transactions on Computing Systems.
August, 1984. V olume 2, Number 3.
pages 181-197.
McKusick was recently honored with the IEEE Reynold B. Johns on award for his contributions to ﬁle
systems, much of which was based on his work building FFS. In h is acceptance speech, he discussed the
original FFS software: only 1200 lines of code! Modern versi ons are a little more complex, e.g., the BSD
FFS descendant now is in the 50-thousand lines-of-code rang e.
[P98] “Hardware Technology Trends and Database Opportunities”
David A. Patterson
Keynote Lecture at the ACM SIGMOD Conference (SIGMOD ’98)
June, 1998
A great and simple overview of disk technology trends and how they change over time.
[K94] “The Design of the SEER Predictive Caching System”
G. H. Kuenning
MOBICOMM ’94, Santa Cruz, California, December 1994
According to Kuenning, this is the best overview of the SEER p roject, which led to (among other things)
the collection of these traces.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 527

42
Crash Consistency: FSCK and Journaling
As we’ve seen thus far, the ﬁle system manages a set of data str uctures to
implement the expected abstractions: ﬁles, directories, and all of the other
metadata needed to support the basic abstraction that we exp ect from a
ﬁle system. Unlike most data structures (for example, those found in
memory of a running program), ﬁle system data structures mus t persist,
i.e., they must survive over the long haul, stored on devices that retain
data despite power loss (such as hard disks or ﬂash-based SSD s).
One major challenge faced by a ﬁle system is how to update pers is-
tent data structures despite the presence of a power loss or system crash.
Speciﬁcally , what happens if, right in the middle of updatin g on-disk
structures, someone trips over the power cord and the machin e loses
power? Or the operating system encounters a bug and crashes? Because
of power losses and crashes, updating a persistent data stru cture can be
quite tricky , and leads to a new and interesting problem in ﬁl e system
implementation, known as the crash-consistency problem.
This problem is quite simple to understand. Imagine you have to up-
date two on-disk structures, A and B, in order to complete a particular
operation. Because the disk only services a single request a t a time, one
of these requests will reach the disk ﬁrst (either A or B). If the system
crashes or loses power after one write completes, the on-dis k structure
will be left in an inconsistent state. And thus, we have a problem that all
ﬁle systems need to solve:
THE CRUX : H OW TO UPDATE THE DISK DESPITE CRASHES
The system may crash or lose power between any two writes, and
thus the on-disk state may only partially get updated. After the crash,
the system boots and wishes to mount the ﬁle system again (in o rder to
access ﬁles and such). Given that crashes can occur at arbitr ary points
in time, how do we ensure the ﬁle system keeps the on-disk imag e in a
reasonable state?
491

## Page 528

492 C RASH CONSISTENCY : FSCK AND JOURNALING
In this chapter, we’ll describe this problem in more detail, and look
at some methods ﬁle systems have used to overcome it. We’ll be gin by
examining the approach taken by older ﬁle systems, known as fsck or the
ﬁle system checker . We’ll then turn our attention to another approach,
known as journaling (also known as write-ahead logging ), a technique
which adds a little bit of overhead to each write but recovers more quickly
from crashes or power losses. We will discuss the basic machi nery of
journaling, including a few different ﬂavors of journaling that Linux ext3
[T98,P AA05] (a relatively modern journaling ﬁle system) implements.
42.1 A Detailed Example
To kick off our investigation of journaling, let’s look at an example.
We’ll need to use a workload that updates on-disk structures in some
way . Assume here that the workload is simple: the append of a s ingle
data block to an existing ﬁle. The append is accomplished by o pening the
ﬁle, calling lseek() to move the ﬁle offset to the end of the ﬁle, and then
issuing a single 4KB write to the ﬁle before closing it.
Let’s also assume we are using standard simple ﬁle system str uctures
on the disk, similar to ﬁle systems we have seen before. This t iny example
includes an inode bitmap (with just 8 bits, one per inode), a data bitmap
(also 8 bits, one per data block), inodes (8 total, numbered 0 to 7, and
spread across four blocks), and data blocks (8 total, number ed 0 to 7).
Here is a diagram of this ﬁle system:
Inode
Bmap
Data
Bmap Inodes Data Blocks
I[v1] Da
If you look at the structures in the picture, you can see that a single inode
is allocated (inode number 2), which is marked in the inode bi tmap, and a
single allocated data block (data block 4), also marked in th e data bitmap.
The inode is denoted I[v1], as it is the ﬁrst version of this in ode; it will
soon be updated (due to the workload described above).
Let’s peek inside this simpliﬁed inode too. Inside of I[v1], we see:
owner : remzi
permissions : read-only
size : 1
pointer : 4
pointer : null
pointer : null
pointer : null
In this simpliﬁed inode, the size of the ﬁle is 1 (it has one block al-
located), the ﬁrst direct pointer points to block 4 (the ﬁrst data block of
the ﬁle, Da), and all three other direct pointers are set to null (indicating
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 529

CRASH CONSISTENCY : FSCK AND JOURNALING 493
that they are not used). Of course, real inodes have many more ﬁelds; see
previous chapters for more information.
When we append to the ﬁle, we are adding a new data block to it, a nd
thus must update three on-disk structures: the inode (which must point
to the new block as well as have a bigger size due to the append) , the
new data block Db, and a new version of the data bitmap (call it B[v2]) to
indicate that the new data block has been allocated.
Thus, in the memory of the system, we have three blocks which w e
must write to disk. The updated inode (inode version 2, or I[v 2] for short)
now looks like this:
owner : remzi
permissions : read-only
size : 2
pointer : 4
pointer : 5
pointer : null
pointer : null
The updated data bitmap (B[v2]) now looks like this: 0000110 0. Finally ,
there is the data block (Db), which is just ﬁlled with whateve r it is users
put into ﬁles. Stolen music perhaps?
What we would like is for the ﬁnal on-disk image of the ﬁle syst em to
look like this:
Inode
Bmap
Data
Bmap Inodes Data Blocks
I[v2] Da Db
To achieve this transition, the ﬁle system must perform thre e sepa-
rate writes to the disk, one each for the inode (I[v2]), bitma p (B[v2]), and
data block (Db). Note that these writes usually don’t happen immedi-
ately when the user issues a write() system call; rather, the dirty in-
ode, bitmap, and new data will sit in main memory (in the page cache
or buffer cache ) for some time ﬁrst; then, when the ﬁle system ﬁnally
decides to write them to disk (after say 5 seconds or 30 second s), the ﬁle
system will issue the requisite write requests to the disk. U nfortunately ,
a crash may occur and thus interfere with these updates to the disk. In
particular, if a crash happens after one or two of these write s have taken
place, but not all three, the ﬁle system could be left in a funn y state.
Crash Scenarios
To understand the problem better, let’s look at some example crash sce-
narios. Imagine only a single write succeeds; there are thus three possible
outcomes, which we list here:
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 530

494 C RASH CONSISTENCY : FSCK AND JOURNALING
• Just the data block (Db) is written to disk. In this case, the data is
on disk, but there is no inode that points to it and no bitmap th at
even says the block is allocated. Thus, it is as if the write ne ver
occurred. This case is not a problem at all, from the perspect ive of
ﬁle-system crash consistency 1.
• Just the updated inode (I[v2]) is written to disk. In this case, the
inode points to the disk address (5) where Db was about to be wr it-
ten, but Db has not yet been written there. Thus, if we trust th at
pointer, we will read garbage data from the disk (the old contents
of disk address 5).
Further, we have a new problem, which we call a ﬁle-system incon-
sistency. The on-disk bitmap is telling us that data block 5 has not
been allocated, but the inode is saying that it has. This disa gree-
ment in the ﬁle system data structures is an inconsistency in the
data structures of the ﬁle system; to use the ﬁle system, we mu st
somehow resolve this problem (more on that below).
• Just the updated bitmap (B[v2]) is written to disk. In this case, the
bitmap indicates that block 5 is allocated, but there is no in ode that
points to it. Thus the ﬁle system is inconsistent again; if le ft unre-
solved, this write would result in a space leak , as block 5 would
never be used by the ﬁle system.
There are also three more crash scenarios in this attempt to w rite three
blocks to disk. In these cases, two writes succeed and the las t one fails:
• The inode (I[v2]) and bitmap (B[v2]) are written to disk, but not
data (Db). In this case, the ﬁle system metadata is completely con-
sistent: the inode has a pointer to block 5, the bitmap indica tes that
5 is in use, and thus everything looks OK from the perspective of
the ﬁle system’s metadata. But there is one problem: 5 has gar bage
in it again.
• The inode (I[v2]) and the data block (Db) are written, but not the
bitmap (B[v2]). In this case, we have the inode pointing to the cor-
rect data on disk, but again have an inconsistency between th e in-
ode and the old version of the bitmap (B1). Thus, we once again
need to resolve the problem before using the ﬁle system.
• The bitmap (B[v2]) and data block (Db) are written, but not th e
inode (I[v2]). In this case, we again have an inconsistency between
the inode and the data bitmap. However, even though the block
was written and the bitmap indicates its usage, we have no ide a
which ﬁle it belongs to, as no inode points to the ﬁle.
1However, it might be a problem for the user, who just lost some data!
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 531

CRASH CONSISTENCY : FSCK AND JOURNALING 495
The Crash Consistency Problem
Hopefully , from these crash scenarios, you can see the many p roblems
that can occur to our on-disk ﬁle system image because of crashes: we can
have inconsistency in ﬁle system data structures; we can have space leaks;
we can return garbage data to a user; and so forth. What we’d li ke to do
ideally is move the ﬁle system from one consistent state (e.g ., before the
ﬁle got appended to) to another atomically (e.g., after the inode, bitmap,
and new data block have been written to disk). Unfortunately , we can’t
do this easily because the disk only commits one write at a tim e, and
crashes or power loss may occur between these updates. We cal l this
general problem the crash-consistency problem (we could also call it the
consistent-update problem).
42.2 Solution #1: The File System Checker
Early ﬁle systems took a simple approach to crash consistenc y . Basi-
cally , they decided to let inconsistencies happen and then ﬁ x them later
(when rebooting). A classic example of this lazy approach is found in a
tool that does this: fsck2. fsck is a U NIX tool for ﬁnding such inconsis-
tencies and repairing them [M86]; similar tools to check and repair a disk
partition exist on different systems. Note that such an appr oach can’t ﬁx
all problems; consider, for example, the case above where th e ﬁle system
looks consistent but the inode points to garbage data. The on ly real goal
is to make sure the ﬁle system metadata is internally consist ent.
The tool fsck operates in a number of phases, as summarized in
McKusick and Kowalski’s paper [MK96]. It is run before the ﬁle system
is mounted and made available ( fsck assumes that no other ﬁle-system
activity is on-going while it runs); once ﬁnished, the on-di sk ﬁle system
should be consistent and thus can be made accessible to users .
Here is a basic summary of what fsck does:
• Superblock: fsck ﬁrst checks if the superblock looks reasonable,
mostly doing sanity checks such as making sure the ﬁle system size
is greater than the number of blocks allocated. Usually the g oal of
these sanity checks is to ﬁnd a suspect (corrupt) superblock ; in this
case, the system (or administrator) may decide to use an alte rnate
copy of the superblock.
• Free blocks: Next, fsck scans the inodes, indirect blocks, double
indirect blocks, etc., to build an understanding of which bl ocks are
currently allocated within the ﬁle system. It uses this know ledge
to produce a correct version of the allocation bitmaps; thus , if there
is any inconsistency between bitmaps and inodes, it is resol ved by
trusting the information within the inodes. The same type of check
is performed for all the inodes, making sure that all inodes that look
like they are in use are marked as such in the inode bitmaps.
2Pronounced either “eff-ess-see-kay”, “eff-ess-check”, o r, if you don’t like the tool, “eff-
suck”. Yes, serious professional people use this term.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 532

496 C RASH CONSISTENCY : FSCK AND JOURNALING
• Inode state: Each inode is checked for corruption or other prob-
lems. For example, fsck makes sure that each allocated inode has
a valid type ﬁeld (e.g., regular ﬁle, directory , symbolic li nk, etc.). If
there are problems with the inode ﬁelds that are not easily ﬁxed, the
inode is considered suspect and cleared by fsck; the inode bitmap
is correspondingly updated.
• Inode links: fsck also veriﬁes the link count of each allocated in-
ode. As you may recall, the link count indicates the number of dif-
ferent directories that contain a reference (i.e., a link) t o this par-
ticular ﬁle. To verify the link count, fsck scans through the en-
tire directory tree, starting at the root directory , and bui lds its own
link counts for every ﬁle and directory in the ﬁle system. If t here
is a mismatch between the newly-calculated count and that fo und
within an inode, corrective action must be taken, usually by ﬁxing
the count within the inode. If an allocated inode is discover ed but
no directory refers to it, it is moved to the lost+found directory .
• Duplicates: fsck also checks for duplicate pointers, i.e., cases where
two different inodes refer to the same block. If one inode is o bvi-
ously bad, it may be cleared. Alternately , the pointed-to block could
be copied, thus giving each inode its own copy as desired.
• Bad blocks: A check for bad block pointers is also performed while
scanning through the list of all pointers. A pointer is consi dered
“bad” if it obviously points to something outside its valid r ange,
e.g., it has an address that refers to a block greater than the parti-
tion size. In this case, fsck can’t do anything too intelligent; it just
removes (clears) the pointer from the inode or indirect bloc k.
• Directory checks: fsck does not understand the contents of user
ﬁles; however, directories hold speciﬁcally formatted inf ormation
created by the ﬁle system itself. Thus, fsck performs additional
integrity checks on the contents of each directory , making s ure that
“.” and “..” are the ﬁrst entries, that each inode referred to in a
directory entry is allocated, and ensuring that no director y is linked
to more than once in the entire hierarchy .
As you can see, building a working fsck requires intricate knowledge
of the ﬁle system; making sure such a piece of code works corre ctly in all
cases can be challenging [G+08]. However, fsck (and similar approaches)
have a bigger and perhaps more fundamental problem: they are too slow.
With a very large disk volume, scanning the entire disk to ﬁnd all the
allocated blocks and read the entire directory tree may takemany minutes
or hours. Performance of fsck, as disks grew in capacity and RAIDs
grew in popularity , became prohibitive (despite recent advances [M+13]).
At a higher level, the basic premise of fsck seems just a tad irra-
tional. Consider our example above, where just three blocks are written
to the disk; it is incredibly expensive to scan the entire dis k to ﬁx prob-
lems that occurred during an update of just three blocks. Thi s situation is
akin to dropping your keys on the ﬂoor in your bedroom, and the n com-
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 533

CRASH CONSISTENCY : FSCK AND JOURNALING 497
mencing a search-the-entire-house-for-keys recovery algorithm, starting in
the basement and working your way through every room. It work s but is
wasteful. Thus, as disks (and RAIDs) grew , researchers and p ractitioners
started to look for other solutions.
42.3 Solution #2: Journaling (or Write-Ahead Logging)
Probably the most popular solution to the consistent update problem
is to steal an idea from the world of database management syst ems. That
idea, known as write-ahead logging, was invented to address exactly this
type of problem. In ﬁle systems, we usually call write-ahead logging jour-
naling for historical reasons. The ﬁrst ﬁle system to do this was Ced ar
[H87], though many modern ﬁle systems use the idea, includin g Linux
ext3 and ext4, reiserfs, IBM’s JFS, SGI’s XFS, and Windows NT FS.
The basic idea is as follows. When updating the disk, before o ver-
writing the structures in place, ﬁrst write down a little not e (somewhere
else on the disk, in a well-known location) describing what y ou are about
to do. Writing this note is the “write ahead” part, and we writ e it to a
structure that we organize as a “log”; hence, write-ahead lo gging.
By writing the note to disk, you are guaranteeing that if a cra sh takes
places during the update (overwrite) of the structures you a re updating,
you can go back and look at the note you made and try again; thus , you
will know exactly what to ﬁx (and how to ﬁx it) after a crash, in stead
of having to scan the entire disk. By design, journaling thus adds a bit
of work during updates to greatly reduce the amount of work re quired
during recovery .
We’ll now describe how Linux ext3, a popular journaling ﬁle system,
incorporates journaling into the ﬁle system. Most of the on- disk struc-
tures are identical to Linux ext2, e.g., the disk is divided into block groups,
and each block group has an inode and data bitmap as well as ino des and
data blocks. The new key structure is the journal itself, whi ch occupies
some small amount of space within the partition or on another device.
Thus, an ext2 ﬁle system (without journaling) looks like thi s:
Super Group 0 Group 1 . . . Group N
Assuming the journal is placed within the same ﬁle system ima ge
(though sometimes it is placed on a separate device, or as a ﬁl e within
the ﬁle system), an ext3 ﬁle system with a journal looks like t his:
Super Journal Group 0 Group 1 . . . Group N
The real difference is just the presence of the journal, and o f course,
how it is used.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 534

498 C RASH CONSISTENCY : FSCK AND JOURNALING
Data Journaling
Let’s look at a simple example to understand how data journaling works.
Data journaling is available as a mode with the Linux ext3 ﬁle system,
from which much of this discussion is based.
Say we have our canonical update again, where we wish to write the
‘inode (I[v2]), bitmap (B[v2]), and data block (Db) to disk a gain. Before
writing them to their ﬁnal disk locations, we are now ﬁrst goi ng to write
them to the log (a.k.a. journal). This is what this will look l ike in the log:
Journal
TxB I[v2] B[v2] Db TxE
You can see we have written ﬁve blocks here. The transaction b egin
(TxB) tells us about this update, including information abo ut the pend-
ing update to the ﬁle system (e.g., the ﬁnal addresses of the b locks I[v2],
B[v2], and Db), as well as some kind of transaction identiﬁer (TID). The
middle three blocks just contain the exact contents of the bl ocks them-
selves; this is known as physical logging as we are putting the exact
physical contents of the update in the journal (an alternate idea, logi-
cal logging , puts a more compact logical representation of the update in
the journal, e.g., “this update wishes to append data block D b to ﬁle X”,
which is a little more complex but can save space in the log and perhaps
improve performance). The ﬁnal block (TxE) is a marker of the end of this
transaction, and will also contain the TID.
Once this transaction is safely on disk, we are ready to overw rite the
old structures in the ﬁle system; this process is called checkpointing.
Thus, to checkpoint the ﬁle system (i.e., bring it up to date with the pend-
ing update in the journal), we issue the writes I[v2], B[v2], and Db to
their disk locations as seen above; if these writes complete successfully ,
we have successfully checkpointed the the ﬁle system and are basically
done. Thus, our initial sequence of operations:
1. Journal write: Write the transaction, including a transaction-begin
block, all pending data and metadata updates, and a transact ion-
end block, to the log; wait for these writes to complete.
2. Checkpoint: Write the pending metadata and data updates to their
ﬁnal locations in the ﬁle system.
In our example, we would write TxB, I[v2], B[v2], Db, and TxE t o the
journal ﬁrst. When these writes complete, we would complete the update
by checkpointing I[v2], B[v2], and Db, to their ﬁnal locatio ns on disk.
Things get a little trickier when a crash occurs during the wr ites to
the journal. Here, we are trying to write the set of blocks in t he transac-
tion (e.g., TxB, I[v2], B[v2], Db, TxE) to disk. One simple wa y to do this
would be to issue each one at a time, waiting for each to comple te, and
then issuing the next. However, this is slow . Ideally , we’d l ike to issue
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 535

CRASH CONSISTENCY : FSCK AND JOURNALING 499
ASIDE : FORCING WRITES TO DISK
To enforce ordering between two disk writes, modern ﬁle syst ems have
to take a few extra precautions. In olden times, forcing orde ring between
two writes, A and B, was easy: just issue the write of A to the disk, wait
for the disk to interrupt the OS when the write is complete, and then issue
the write of B.
Things got slightly more complex due to the increased use of write caches
within disks. With write buffering enabled (sometimes call ed immediate
reporting), a disk will inform the OS the write is complete when it simpl y
has been placed in the disk’s memory cache, and has not yet rea ched
disk. If the OS then issues a subsequent write, it is not guara nteed to
reach the disk after previous writes; thus ordering between writes is not
preserved. One solution is to disable write buffering. Howe ver, more
modern systems take extra precautions and issue explicit write barriers;
such a barrier, when it completes, guarantees that all write s issued before
the barrier will reach disk before any writes issued after th e barrier.
All of this machinery requires a great deal of trust in the cor rect oper-
ation of the disk. Unfortunately , recent research shows tha t some disk
manufacturers, in an effort to deliver “higher performing” disks, explic-
itly ignore write-barrier requests, thus making the disks s eemingly run
faster but at the risk of incorrect operation [C+13, R+11]. A s Kahan said,
the fast almost always beats out the slow , even if the fast is w rong.
all ﬁve block writes at once, as this would turn ﬁve writes int o a single
sequential write and thus be faster. However, this is unsafe , for the fol-
lowing reason: given such a big write, the disk internally ma y perform
scheduling and complete small pieces of the big write in any o rder. Thus,
the disk internally may (1) write TxB, I[v2], B[v2], and TxE a nd only later
(2) write Db. Unfortunately , if the disk loses power between (1) and (2),
this is what ends up on disk:
Journal
TxB
id=1
I[v2] B[v2] ?? TxE
id=1
Why is this a problem? Well, the transaction looks like a vali d trans-
action (it has a begin and an end with matching sequence numbe rs). Fur-
ther, the ﬁle system can’t look at that fourth block and know i t is wrong;
after all, it is arbitrary user data. Thus, if the system now r eboots and
runs recovery , it will replay this transaction, and ignorantly copy the con-
tents of the garbage block ’??’ to the location where Db is sup posed to
live. This is bad for arbitrary user data in a ﬁle; it is much wo rse if it hap-
pens to a critical piece of ﬁle system, such as the superblock , which could
render the ﬁle system unmountable.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 536

500 C RASH CONSISTENCY : FSCK AND JOURNALING
ASIDE : OPTIMIZING LOG WRITES
You may have noticed a particular inefﬁciency of writing to t he log.
Namely , the ﬁle system ﬁrst has to write out the transaction- begin block
and contents of the transaction; only after these writes com plete can the
ﬁle system send the transaction-end block to disk. The perfo rmance im-
pact is clear, if you think about how a disk works: usually an e xtra rota-
tion is incurred (think about why).
One of our former graduate students, Vijayan Prabhakaran, h ad a simple
idea to ﬁx this problem [P+05]. When writing a transaction to the journal,
include a checksum of the contents of the journal in the begin and end
blocks. Doing so enables the ﬁle system to write the entire tr ansaction at
once, without incurring a wait; if, during recovery , the ﬁle system sees
a mismatch in the computed checksum versus the stored checks um in
the transaction, it can conclude that a crash occurred durin g the write
of the transaction and thus discard the ﬁle-system update. T hus, with a
small tweak in the write protocol and recovery system, a ﬁle s ystem can
achieve faster common-case performance; on top of that, the system is
slightly more reliable, as any reads from the journal are now protected by
a checksum.
This simple ﬁx was attractive enough to gain the notice of Lin ux ﬁle sys-
tem developers, who then incorporated it into the next gener ation Linux
ﬁle system, called (you guessed it!) Linux ext4 . It now ships on mil-
lions of machines worldwide, including the Android handhel d platform.
Thus, every time you write to disk on many Linux-based system s, a little
code developed at Wisconsin makes your system a little faste r and more
reliable.
To avoid this problem, the ﬁle system issues the transaction al write in
two steps. First, it writes all blocks except the TxE block to the journal,
issuing these writes all at once. When these writes complete , the journal
will look something like this (assuming our append workload again):
Journal
TxB
id=1
I[v2] B[v2] Db
When those writes complete, the ﬁle system issues the write of the TxE
block, thus leaving the journal in this ﬁnal, safe state:
Journal
TxB
id=1
I[v2] B[v2] Db TxE
id=1
An important aspect of this process is the atomicity guarant ee pro-
vided by the disk. It turns out that the disk guarantees that a ny 512-byte
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 537

CRASH CONSISTENCY : FSCK AND JOURNALING 501
write will either happen or not (and never be half-written); thus, to make
sure the write of TxE is atomic, one should make it a single 512-byte block.
Thus, our current protocol to update the ﬁle system, with eac h of its three
phases labeled:
1. Journal write: Write the contents of the transaction (including TxB,
metadata, and data) to the log; wait for these writes to compl ete.
2. Journal commit: Write the transaction commit block (containing
TxE) to the log; wait for write to complete; transaction is sa id to be
committed.
3. Checkpoint: Write the contents of the update (metadata and data)
to their ﬁnal on-disk locations.
Recovery
Let’s now understand how a ﬁle system can use the contents of t he jour-
nal to recover from a crash. A crash may happen at any time during this
sequence of updates. If the crash happens before the transac tion is writ-
ten safely to the log (i.e., before Step 2 above completes), t hen our job
is easy: the pending update is simply skipped. If the crash ha ppens af-
ter the transaction has committed to the log, but before the c heckpoint is
complete, the ﬁle system can recover the update as follows. When the
system boots, the ﬁle system recovery process will scan the l og and look
for transactions that have committed to the disk; these tran sactions are
thus replayed (in order), with the ﬁle system again attempting to write
out the blocks in the transaction to their ﬁnal on-disk locat ions. This form
of logging is one of the simplest forms there is, and is called redo logging.
By recovering the committed transactions in the journal, th e ﬁle system
ensures that the on-disk structures are consistent, and thu s can proceed
by mounting the ﬁle system and readying itself for new reques ts.
Note that it is ﬁne for a crash to happen at any point during che ck-
pointing, even after some of the updates to the ﬁnal locations of the blocks
have completed. In the worst case, some of these updates are s imply per-
formed again during recovery . Because recovery is a rare operation (only
taking place after an unexpected system crash), a few redund ant writes
are nothing to worry about 3.
Batching Log Updates
You might have noticed that the basic protocol could add a lot of extra
disk trafﬁc. For example, imagine we create two ﬁles in a row , called
file1 and file2, in the same directory . To create one ﬁle, one has to
update a number of on-disk structures, minimally including : the inode
bitmap (to allocated a new inode), the newly-created inode o f the ﬁle, the
3Unless you worry about everything, in which case we can’t hel p you. Stop worrying so
much, it is unhealthy! But now you’re probably worried about over-worrying.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 538

502 C RASH CONSISTENCY : FSCK AND JOURNALING
data block of the parent directory containing the new direct ory entry , as
well as the parent directory inode (which now has a new modiﬁc ation
time). With journaling, we logically commit all of this info rmation to
the journal for each of our two ﬁle creations; because the ﬁle s are in the
same directory , and let’s assume even have inodes within the same inode
block, this means that if we’re not careful, we’ll end up writ ing these same
blocks over and over.
To remedy this problem, some ﬁle systems do not commit each update
to disk one at a time (e.g., Linux ext3); rather, one can buffe r all updates
into a global transaction. In our example above, when the two ﬁles are
created, the ﬁle system just marks the in-memory inode bitma p, inodes
of the ﬁles, directory data, and directory inode as dirty , and adds them to
the list of blocks that form the current transaction. When it is ﬁnally time
to write these blocks to disk (say , after a timeout of 5 second s), this single
global transaction is committed containing all of the updat es described
above. Thus, by buffering updates, a ﬁle system can avoid exc essive write
trafﬁc to disk in many cases.
Making The Log Finite
We thus have arrived at a basic protocol for updating ﬁle-sys tem on-disk
structures. The ﬁle system buffers updates in memory for som e time;
when it is ﬁnally time to write to disk, the ﬁle system ﬁrst car efully writes
out the details of the transaction to the journal (a.k.a. wri te-ahead log);
after the transaction is complete, the ﬁle system checkpoin ts those blocks
to their ﬁnal locations on disk.
However, the log is of a ﬁnite size. If we keep adding transact ions to
it (as in this ﬁgure), it will soon ﬁll. What do you think happe ns then?
Journal
Tx1 Tx2 Tx3 Tx4 Tx5 ...
Two problems arise when the log becomes full. The ﬁrst is simp ler,
but less critical: the larger the log, the longer recovery wi ll take, as the
recovery process must replay all the transactions within th e log (in order)
to recover. The second is more of an issue: when the log is full (or nearly
full), no further transactions can be committed to the disk, thus making
the ﬁle system “less than useful” (i.e., useless).
To address these problems, journaling ﬁle systems treat the log as a
circular data structure, re-using it over and over; this is w hy the journal is
sometimes referred to as a circular log. To do so, the ﬁle system must take
action some time after a checkpoint. Speciﬁcally , once a tra nsaction has
been checkpointed, the ﬁle system should free the space it wa s occupying
within the journal, allowing the log space to be reused. Ther e are many
ways to achieve this end; for example, you could simply mark t he oldest
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 539

CRASH CONSISTENCY : FSCK AND JOURNALING 503
and newest transactions in the log in a journal superblock; all other space
is free. Here is a graphical depiction of such a mechanism:
Journal
Journal
Super Tx1 Tx2 Tx3 Tx4 Tx5 ...
In the journal superblock (not to be confused with the main ﬁl e system
superblock), the journaling system records enough informa tion to know
which transactions have not yet been checkpointed, and thus reduces re-
covery time as well as enables re-use of the log in a circular f ashion. And
thus we add another step to our basic protocol:
1. Journal write: Write the contents of the transaction (containing TxB
and the contents of the update) to the log; wait for these writ es to
complete.
2. Journal commit: Write the transaction commit block (containing
TxE) to the log; wait for the write to complete; the transacti on is
now committed.
3. Checkpoint: Write the contents of the update to their ﬁnal locations
within the ﬁle system.
4. Free: Some time later, mark the transaction free in the journal by
updating the journal superblock.
Thus we have our ﬁnal data journaling protocol. But there is s till a
problem: we are writing each data block to the disk twice, which is a
heavy cost to pay , especially for something as rare as a system crash. Can
you ﬁgure out a way to retain consistency without writing dat a twice?
Metadata Journaling
Although recovery is now fast (scanning the journal and repl aying a few
transactions as opposed to scanning the entire disk), norma l operation
of the ﬁle system is slower than we might desire. In particula r, for each
write to disk, we are now also writing to the journal ﬁrst, thu s doubling
write trafﬁc; this doubling is especially painful during se quential write
workloads, which now will proceed at half the peak write band width of
the drive. Further, between writes to the journal and writes to the main
ﬁle system, there is a costly seek, which adds noticeable ove rhead for
some workloads.
Because of the high cost of writing every data block to disk tw ice, peo-
ple have tried a few different things in order to speed up perf ormance.
For example, the mode of journaling we described above is oft en called
data journaling (as in Linux ext3), as it journals all user data (in addition
to the metadata of the ﬁle system). A simpler (and more common ) form
of journaling is sometimes called ordered journaling (or just metadata
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 540

504 C RASH CONSISTENCY : FSCK AND JOURNALING
journaling), and it is nearly the same, except that user data is not writ-
ten to the journal. Thus, when performing the same update as a bove, the
following information would be written to the journal:
Journal
TxB I[v2] B[v2] TxE
The data block Db, previously written to the log, would inste ad be
written to the ﬁle system proper, avoiding the extra write; given that most
I/O trafﬁc to the disk is data, not writing data twice substan tially reduces
the I/O load of journaling. The modiﬁcation does raise an int eresting
question, though: when should we write data blocks to disk?
Let’s again consider our example append of a ﬁle to understan d the
problem better. The update consists of three blocks: I[v2], B[v2], and
Db. The ﬁrst two are both metadata and will be logged and then c heck-
pointed; the latter will only be written once to the ﬁle syste m. When
should we write Db to disk? Does it matter?
As it turns out, the ordering of the data write does matter formetadata-
only journaling. For example, what if we write Db to disk after the trans-
action (containing I[v2] and B[v2]) completes? Unfortunat ely , this ap-
proach has a problem: the ﬁle system is consistent but I[v2] m ay end up
pointing to garbage data. Speciﬁcally , consider the case wh ere I[v2] and
B[v2] are written but Db did not make it to disk. The ﬁle system will then
try to recover. Because Db is not in the log, the ﬁle system will replay
writes to I[v2] and B[v2], and produce a consistent ﬁle syste m (from the
perspective of ﬁle-system metadata). However, I[v2] will b e pointing to
garbage data, i.e., at whatever was in the the slot where Db wa s headed.
To ensure this situation does not arise, some ﬁle systems (e. g., Linux
ext3) write data blocks (of regular ﬁles) to the disk ﬁrst, before related
metadata is written to disk. Speciﬁcally , the protocol is as follows:
1. Data write: Write data to ﬁnal location; wait for completion
(the wait is optional; see below for details).
2. Journal metadata write: Write the begin block and metadata to the
log; wait for writes to complete.
3. Journal commit: Write the transaction commit block (containing
TxE) to the log; wait for the write to complete; the transacti on (in-
cluding data) is now committed.
4. Checkpoint metadata: Write the contents of the metadata update
to their ﬁnal locations within the ﬁle system.
5. Free: Later, mark the transaction free in journal superblock.
By forcing the data write ﬁrst, a ﬁle system can guarantee that a pointer
will never point to garbage. Indeed, this rule of “write the p ointed to ob-
ject before the object with the pointer to it” is at the core of crash consis-
tency , and is exploited even further by other crash consiste ncy schemes
[GP94] (see below for details).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 541

CRASH CONSISTENCY : FSCK AND JOURNALING 505
In most systems, metadata journaling (akin to ordered journ aling of
ext3) is more popular than full data journaling. For example , Windows
NTFS and SGI’s XFS both use non-ordered metadata journaling . Linux
ext3 gives you the option of choosing either data, ordered, o r unordered
modes (in unordered mode, data can be written at any time). Al l of these
modes keep metadata consistent; they vary in their semantic s for data.
Finally , note that forcing the data write to complete (Step 1 ) before
issuing writes to the journal (Step 2) is not required for cor rectness, as
indicated in the protocol above. Speciﬁcally , it would be ﬁne to issue data
writes as well as the transaction-begin block and metadata t o the journal;
the only real requirement is that Steps 1 and 2 complete befor e the issuing
of the journal commit block (Step 3).
T ricky Case: Block Reuse
There are some interesting corner cases that make journalin g more tricky ,
and thus are worth discussing. A number of them revolve aroun d block
reuse; as Stephen Tweedie (one of the main forces behind ext3 ) said:
“What’s the hideous part of the entire system? ... It’s delet ing ﬁles.
Everything to do with delete is hairy . Everything to do with d elete...
you have nightmares around what happens if blocks get delete d and
then reallocated.” [T00]
The particular example Tweedie gives is as follows. Suppose you are
using some form of metadata journaling (and thus data blocks for ﬁles
are not journaled). Let’s say you have a directory called foo. The user
adds an entry to foo (say by creating a ﬁle), and thus the contents of
foo (because directories are considered metadata) are written to the log;
assume the location of the foo directory data is block 1000. The log thus
contains something like this:
Journal
TxB
id=1
I[foo]
ptr:1000
D[foo]
[final addr:1000]
TxE
id=1
At this point, the user deletes everything in the directory a s well as the
directory itself, freeing up block 1000 for reuse. Finally , the user creates a
new ﬁle (say foobar), which ends up reusing the same block (1000) that
used to belong to foo. The inode of foobar is committed to disk, as is
its data; note, however, because metadata journaling is in u se, only the
inode of foobar is committed to the journal; the newly-written data in
block 1000 in the ﬁle foobar is not journaled.
Journal
TxB
id=1
I[foo]
ptr:1000
D[foo]
[final addr:1000]
TxE
id=1
TxB
id=2
I[foobar]
ptr:1000
TxE
id=2
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 542

506 C RASH CONSISTENCY : FSCK AND JOURNALING
Journal File System
TxB Contents TxE Metadata Data
(metadata) (data)
issue issue issue
complete
complete
complete
issue
complete
issue issue
complete
complete
Table 42.1: Data Journaling Timeline
Now assume a crash occurs and all of this information is still in the
log. During replay , the recovery process simply replays eve rything in
the log, including the write of directory data in block 1000; the replay
thus overwrites the user data of current ﬁle foobar with old directory
contents! Clearly this is not a correct recovery action, and certainly it will
be a surprise to the user when reading the ﬁle foobar.
There are a number of solutions to this problem. One could, fo r ex-
ample, never reuse blocks until the delete of said blocks is c heckpointed
out of the journal. What Linux ext3 does instead is to add a new type
of record to the journal, known as a revoke record. In the case above,
deleting the directory would cause a revoke record to be writ ten to the
journal. When replaying the journal, the system ﬁrst scans f or such re-
voke records; any such revoked data is never replayed, thus a voiding the
problem mentioned above.
Wrapping Up Journaling: A Timeline
Before ending our discussion of journaling, we summarize th e protocols
we have discussed with timelines depicting each of them. Tab le
42.1
shows the protocol when journaling data as well as metadata, whereas
Table 42.2 shows the protocol when journaling only metadata.
In each table, time increases in the downward direction, and each row
in the table shows the logical time that a write can be issued o r might
complete. For example, in the data journaling protocol ( 42.1), the writes
of the transaction begin block (TxB) and the contents of the t ransaction
can logically be issued at the same time, and thus can be compl eted in
any order; however, the write to the transaction end block (T xE) must not
be issued until said previous writes complete. Similarly , t he checkpoint-
ing writes to data and metadata blocks cannot begin until the transaction
end block has committed. Horizontal dashed lines show where write-
ordering requirements must be obeyed.
A similar timeline is shown for the metadata journaling protocol. Note
that the data write can logically be issued at the same time as the writes
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 543

CRASH CONSISTENCY : FSCK AND JOURNALING 507
Journal File System
TxB Contents TxE Metadata Data
(metadata)
issue issue issue
complete
complete
complete
issue
complete
issue
complete
Table 42.2: Metadata Journaling Timeline
to the transaction begin and the contents of the journal; how ever, it must
be issued and complete before the transaction end has been is sued.
Finally , note that the time of completion marked for each wri te in the
timelines is arbitrary . In a real system, completion time is determined by
the I/O subsystem, which may reorder writes to improve perfo rmance.
The only guarantees about ordering that we have are those tha t must
be enforced for protocol correctness (and are shown via the h orizontal
dashed lines in the tables).
42.4 Solution #3: Other Approaches
We’ve thus far described two options in keeping ﬁle system me tadata
consistent: a lazy approach based on fsck, and a more active approach
known as journaling. However, these are not the only two appr oaches.
One such approach, known as Soft Updates [GP94], was introdu ced by
Ganger and Patt. This approach carefully orders all writes t o the ﬁle sys-
tem to ensure that the on-disk structures are never left in an inconsis-
tent state. For example, by writing a pointed-to data block t o disk before
the inode that points to it, we can ensure that the inode never points to
garbage; similar rules can be derived for all the structures of the ﬁle sys-
tem. Implementing Soft Updates can be a challenge, however; whereas
the journaling layer described above can be implemented wit h relatively
little knowledge of the exact ﬁle system structures, Soft Up dates requires
intricate knowledge of each ﬁle system data structure and thus adds a fair
amount of complexity to the system.
Another approach is known as copy-on-write (yes, COW), and is used
in a number of popular ﬁle systems, including Sun’s ZFS [B07] . This tech-
nique never overwrites ﬁles or directories in place; rather , it places new
updates to previously unused locations on disk. After a numb er of up-
dates are completed, COW ﬁle systems ﬂip the root structure o f the ﬁle
system to include pointers to the newly updated structures. Doing so
makes keeping the ﬁle system consistent straightforward. W e’ll be learn-
ing more about this technique when we discuss the log-struct ured ﬁle
system (LFS) in a future chapter; LFS is an early example of a C OW.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 544

508 C RASH CONSISTENCY : FSCK AND JOURNALING
Another approach is one we just developed here at Wisconsin. In this
technique, entitled backpointer-based consistency (or BBC), no ordering
is enforced between writes. To achieve consistency , an addi tional back
pointer is added to every block in the system; for example, each data
block has a reference to the inode to which it belongs. When ac cessing
a ﬁle, the ﬁle system can determine if the ﬁle is consistent by checking if
the forward pointer (e.g., the address in the inode or direct block) points
to a block that refers back to it. If so, everything must have s afely reached
disk and thus the ﬁle is consistent; if not, the ﬁle is inconsi stent, and an
error is returned. By adding back pointers to the ﬁle system, a new form
of lazy crash consistency can be attained [C+12].
Finally , we also have explored techniques to reduce the numb er of
times a journal protocol has to wait for disk writes to comple te. Entitled
optimistic crash consistency [C+13], this new approach issues as many
writes to disk as possible and uses a generalized form of the transaction
checksum [P+05], as well as a few other techniques, to detect inconsis ten-
cies should they arise. For some workloads, these optimisti c techniques
can improve performance by an order of magnitude. However, t o truly
function well, a slightly different disk interface is requi red [C+13].
42.5 Summary
We have introduced the problem of crash consistency , and dis cussed
various approaches to attacking this problem. The older app roach of
building a ﬁle system checker works but is likely too slow to r ecover on
modern systems. Thus, many ﬁle systems now use journaling. J ournaling
reduces recovery time from O(size-of-the-disk-volume) to O(size-of-the-
log), thus speeding recovery substantially after a crash an d restart. For
this reason, many modern ﬁle systems use journaling. We have also seen
that journaling can come in many different forms; the most co mmonly
used is ordered metadata journaling, which reduces the amou nt of trafﬁc
to the journal while still preserving reasonable consistency guarantees for
both ﬁle system metadata as well as user data.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 545

CRASH CONSISTENCY : FSCK AND JOURNALING 509
References
[B07] “ZFS: The Last Word in File Systems”
Jeff Bonwick and Bill Moore
Available: http://opensolaris.org/os/community/zfs/docs/zfs
last.pdf
ZFS uses copy-on-write and journaling, actually, as in some cases, logging writes to disk will perform
better.
[C+12] “Consistency Without Ordering”
Vijay Chidambaram, Tushar Sharma, Andrea C. Arpaci-Dussea u, Remzi H. Arpaci-Dusseau
FAST ’12, San Jose, California
A recent paper of ours about a new form of crash consistency ba sed on back pointers. Read it for the
exciting details!
[C+13] “Optimistic Crash Consistency”
Vijay Chidambaram, Thanu S. Pillai, Andrea C. Arpaci-Dusse au, Remzi H. Arpaci-Dusseau
SOSP ’13, Nemacolin Woodlands Resort, PA, November 2013
Our work on a more optimistic and higher performance journal ing protocol. For workloads that call
fsync() a lot, performance can be greatly improved.
[GP94] “Metadata Update Performance in File Systems”
Gregory R. Ganger and Yale N. Patt
OSDI ’94
A clever paper about using careful ordering of writes as the m ain way to achieve consistency. Imple-
mented later in BSD-based systems.
[G+08] “SQCK: A Declarative File System Checker”
Haryadi S. Gunawi, Abhishek Rajimwale, Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau
OSDI ’08, San Diego, California
Our own paper on a new and better way to build a ﬁle system check er using SQL queries. We also show
some problems with the existing checker, ﬁnding numerous bu gs and odd behaviors, a direct result of
the complexity of fsck.
[H87] “Reimplementing the Cedar File System Using Logging a nd Group Commit”
Robert Hagmann
SOSP ’87, Austin, Texas, November 1987
The ﬁrst work (that we know of) that applied write-ahead logg ing (a.k.a. journaling) to a ﬁle system.
[M+13] “ffsck: The Fast File System Checker”
Ao Ma, Chris Dragga, Andrea C. Arpaci-Dusseau, Remzi H. Arpa ci-Dusseau
FAST ’13, San Jose, California, February 2013
A recent paper of ours detailing how to make fsck an order of ma gnitude faster. Some of the ideas have
already been incorporated into the BSD ﬁle system checker [M K96] and are deployed today.
[MK96] “Fsck - The U NIX File System Check Program”
Marshall Kirk McKusick and T. J. Kowalski
Revised in 1996
Describes the ﬁrst comprehensive ﬁle-system checking tool , the eponymous fsck. Written by some of
the same people who brought you FFS.
[MJLF84] “A Fast File System for UNIX”
Marshall K. McKusick, William N. Joy , Sam J. Lefﬂer, Robert S. Fabry
ACM Transactions on Computing Systems.
August 1984, V olume 2:3
Y ou already know enough about FFS, right? But yeah, it is OK to reference papers like this more than
once in a book.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 546

510 C RASH CONSISTENCY : FSCK AND JOURNALING
[P+05] “IRON File Systems”
Vijayan Prabhakaran, Lakshmi N. Bairavasundaram, Nitin Ag rawal, Haryadi S. Gunawi, An-
drea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau
SOSP ’05, Brighton, England, October 2005
A paper mostly focused on studying how ﬁle systems react to di sk failures. Towards the end, we intro-
duce a transaction checksum to speed up logging, which was ev entually adopted into Linux ext4.
[PAA05] “Analysis and Evolution of Journaling File Systems ”
Vijayan Prabhakaran, Andrea C. Arpaci-Dusseau, Remzi H. Ar paci-Dusseau
USENIX ’05, Anaheim, California, April 2005
An early paper we wrote analyzing how journaling ﬁle systems work.
[R+11] “Coerced Cache Eviction and Discreet-Mode Journali ng”
Abhishek Rajimwale, Vijay Chidambaram, Deepak Ramamurthi ,
Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau
DSN ’11, Hong Kong, China, June 2011
Our own paper on the problem of disks that buffer writes in a me mory cache instead of forcing them to
disk, even when explicitly told not to do that! Our solution t o overcome this problem: if you want A to
be written to disk before B, ﬁrst write A, then send a lot of “dummy” writes to disk, hopefully causing
A to be forced to disk to make room for them in the cache. A neat if impractical solution.
[T98] “Journaling the Linux ext2fs File System”
Stephen C. Tweedie
The Fourth Annual Linux Expo, May 1998
Tweedie did much of the heavy lifting in adding journaling to the Linux ext2 ﬁle system; the result,
not surprisingly, is called ext3. Some nice design decision s include the strong focus on backwards
compatibility, e.g., you can just add a journaling ﬁle to an e xisting ext2 ﬁle system and then mount it
as an ext3 ﬁle system.
[T00] “EXT3, Journaling Filesystem”
Stephen Tweedie
Talk at the Ottawa Linux Symposium, July 2000
olstrans.sourceforge.net/release/OLS2000-ext3/OLS2000-ext3.html
A transcript of a talk given by Tweedie on ext3.
[T01] “The Linux ext2 File System”
Theodore Ts’o, June, 2001.
Available: http://e2fsprogs.sourceforge.net/ext2.html
A simple Linux ﬁle system based on the ideas found in FFS. For a while it was quite heavily used; now
it is really just in the kernel as an example of a simple ﬁle sys tem.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 547

43
Log-structured File Systems
In the early 90’s, a group at Berkeley led by Professor John Ou sterhout
and graduate student Mendel Rosenblum developed a new ﬁle sy stem
known as the log-structured ﬁle system [RO91]. Their motiva tion to do
so was based on the following observations:
• Memory sizes were growing : As memory got bigger, more data
could be cached in memory . As more data is cached, disk trafﬁc
would increasingly consist of writes, as reads would be serv iced in
the cache. Thus, ﬁle system performance would largely be det er-
mined by its performance for writes.
• There was a large and growing gap between random I/O perfor-
mance and sequential I/O performance : Transfer bandwidth in-
creases roughly 50%-100% every year; seek and rotational de lay
costs decrease much more slowly , maybe at 5%-10% per year [P9 8].
Thus, if one is able to use disks in a sequential manner, one ge ts a
huge performance advantage, which grows over time.
• Existing ﬁle systems perform poorly on many common workloads:
For example, FFS [MJLF84] would perform a large number of writes
to create a new ﬁle of size one block: one for a new inode, one to
update the inode bitmap, one to the directory data block that the
ﬁle is in, one to the directory inode to update it, one to the ne w data
block that is apart of the new ﬁle, and one to the data bitmap to
mark the data block as allocated. Thus, although FFS would pl ace
all of these blocks within the same block group, FFS would inc ur
many short seeks and subsequent rotational delays and thus p er-
formance would fall far short of peak sequential bandwidth.
• File systems were not RAID-aware: For example, RAID-4 and RAID-
5 have the small-write problem where a logical write to a single
block causes 4 physical I/Os to take place. Existing ﬁle syst ems do
not try to avoid this worst-case RAID writing behavior.
An ideal ﬁle system would thus focus on write performance, an d try
to make use of the sequential bandwidth of the disk. Further, it would
perform well on common workloads that not only write out data but also
511

## Page 548

512 LOG -STRUCTURED FILE SYSTEMS
update on-disk metadata structures frequently . Finally , i t would work
well on RAIDs as well as single disks.
The new type of ﬁle system Rosenblum and Ousterhout introduc ed
was called LFS, short for the Log-structured File System . When writ-
ing to disk, LFS ﬁrst buffers all updates (including metadat a!) in an in-
memory segment; when the segment is full, it is written to disk in one
long, sequential transfer to an unused part of the disk, i.e. , LFS never
overwrites existing data, but rather always writes segments to free loca-
tions. Because segments are large, the disk is used efﬁcient ly , and perfor-
mance of the ﬁle system approaches its zenith.
THE CRUX :
HOW TO MAKE ALL WRITES SEQUENTIAL WRITES ?
How can a ﬁle system turns all writes into sequential writes? For
reads, this task is impossible, as the desired block to be rea d may be any-
where on disk. For writes, however, the ﬁle system always has a choice,
and it is exactly this choice we hope to exploit.
43.1 Writing To Disk Sequentially
We thus have our ﬁrst challenge: how do we transform all updat es to
ﬁle-system state into a series of sequential writes to disk? To understand
this better, let’s use a simple example. Imagine we are writi ng a data block
D to a ﬁle. Writing the data block to disk might result in the fol lowing
on-disk layout, with D written at disk address A0:
D
A0
However, when a user writes a data block, it is not only data th at gets
written to disk; there is also other metadata that needs to be updated.
In this case, let’s also write the inode (I) of the ﬁle to disk, and have it
point to the data block D. When written to disk, the data block and inode
would look something like this (note that the inode looks as b ig as the
data block, which generally isn’t the case; in most systems, data blocks
are 4 KB in size, whereas an inode is much smaller, around 128 b ytes):
D
A0
I
blk[0]:A0
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 549

LOG -STRUCTURED FILE SYSTEMS 513
TIP : D ETAILS MATTER
All interesting systems are comprised of a few general ideas and a
number of details. Sometimes, when you are learning about th ese sys-
tems, you think to yourself “Oh, I get the general idea; the re st is just de-
tails,” and you use this to only half-learn how things really work. Don’t
do this! Many times, the details are critical. As we’ll see wi th LFS, the
general idea is easy to understand, but to really build a work ing system,
you have to think through all of the tricky cases.
This basic idea, of simply writing all updates (such as data b locks,
inodes, etc.) to the disk sequentially , sits at the heart of L FS. If you un-
derstand this, you get the basic idea. But as with all complic ated systems,
the devil is in the details.
43.2 Writing Sequentially And Effectively
Unfortunately , writing to disk sequentially is not (alone) enough to
guarantee efﬁcient writes. For example, imagine if we wrote a single
block to address A, at time T . We then wait a little while, and write to
the disk at address A + 1 (the next block address in sequential order),
but at time T + δ. In-between the ﬁrst and second writes, unfortunately ,
the disk has rotated; when you issue the second write, it will thus wait
for most of a rotation before being committed (speciﬁcally , if the rotation
takes time Trotation, the disk will wait Trotation − δ before it can commit
the second write to the disk surface). And thus you can hopefu lly see
that simply writing to disk in sequential order is not enough to achieve
peak performance; rather, you must issue a large number of contiguous
writes (or one large write) to the drive in order to achieve go od write
performance.
To achieve this end, LFS uses an ancient technique known as write
buffering1. Before writing to the disk, LFS keeps track of updates in
memory; when it has received a sufﬁcient number of updates, i t writes
them to disk all at once, thus ensuring efﬁcient use of the dis k.
The large chunk of updates LFS writes at one time is referred t o by
the name of a segment. Although this term is over-used in computer
systems, here it just means a large-ish chunk which LFS uses t o group
writes. Thus, when writing to disk, LFS buffers updates in an in-memory
segment, and then writes the segment all at once to the disk. A s long as
the segment is large enough, these writes will be efﬁcient.
Here is an example, in which LFS buffers two sets updates into a small
segment; actual segments are larger (a few MB). The ﬁrst upda te is of
1Indeed, it is hard to ﬁnd a good citation for this idea, since i t was likely invented by many
and very early on in the history of computing. For a study of th e beneﬁts of write buffering,
see Solworth and Orji [SO90]; to learn about its potential ha rms, see Mogul [M94].
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 550

514 LOG -STRUCTURED FILE SYSTEMS
four block writes to ﬁle j; the second is one block being added to ﬁle k.
LFS then commits the entire segment of seven blocks to disk at once. The
resulting on-disk layout of these blocks is as follows:
D[j,0]
A0
D[j,1]
A1
D[j,2]
A2
D[j,3]
A3
blk[0]:A0
blk[1]:A1
blk[2]:A2
blk[3]:A3
Inode[j]
D[k,0]
A5
blk[0]:A5
Inode[k]
43.3 How Much To Buffer?
This raises the following question: how many updates LFS sho uld
buffer before writing to disk? The answer, of course, depend s on the disk
itself, speciﬁcally how high the positioning overhead is in comparison to
the transfer rate; see the FFS chapter for a similar analysis .
For example, assume that positioning (i.e., rotation and se ek over-
heads) before each write takes roughly Tposition seconds. Assume further
that the disk transfer rate is Rpeak MB/s. How much should LFS buffer
before writing when running on such a disk?
The way to think about this is that every time you write, you pa y a
ﬁxed overhead of the positioning cost. Thus, how much do you h ave
to write in order to amortize that cost? The more you write, the better
(obviously), and the closer you get to achieving peak bandwi dth.
To obtain a concrete answer, let’s assume we are writing out D MB.
The time to write out this chunk of data ( Twrite) is the positioning time
Tposition plus the time to transfer D ( D
Rpeak
), or:
Twrite = Tposition + D
Rpeak
(43.1)
And thus the effective rate of writing ( Ref f ective), which is just the
amount of data written divided by the total time to write it, i s:
Ref f ective = D
Twrite
= D
Tposition + D
Rpeak
. (43.2)
What we’re interested in is getting the effective rate ( Ref f ective) close
to the peak rate. Speciﬁcally , we want the effective rate to be some fraction
F of the peak rate, where 0 < F < 1 (a typical F might be 0.9, or 90% of
the peak rate). In mathematical form, this means we want Ref f ective =
F × Rpeak.
At this point, we can solve for D:
Ref f ective = D
Tposition + D
Rpeak
= F × Rpeak (43.3)
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 551

LOG -STRUCTURED FILE SYSTEMS 515
D = F × Rpeak × (Tposition + D
Rpeak
) (43.4)
D = (F × Rpeak × Tposition) + (F × Rpeak × D
Rpeak
) (43.5)
D = F
1 − F × Rpeak × Tposition (43.6)
Let’s do an example, with a disk with a positioning time of 10 m il-
liseconds and peak transfer rate of 100 MB/s; assume we want a n ef-
fective bandwidth of 90% of peak ( F = 0 .9). In this case, D = 0.9
0.1 ×
100 M B/s × 0.01 seconds = 9 M B. Try some different values to see
how much we need to buffer in order to approach peak bandwidth . How
much is needed to reach 95% of peak? 99%?
43.4 Problem: Finding Inodes
To understand how we ﬁnd an inode in LFS, let us brieﬂy review h ow
to ﬁnd an inode in a typical U NIX ﬁle system. In a typical ﬁle system such
as FFS, or even the old U NIX ﬁle system, ﬁnding inodes is easy , because
they are organized in an array and placed on disk at ﬁxed locat ions.
For example, the old U NIX ﬁle system keeps all inodes at a ﬁxed por-
tion of the disk. Thus, given an inode number and the start add ress, to
ﬁnd a particular inode, you can calculate its exact disk addr ess simply by
multiplying the inode number by the size of an inode, and addi ng that
to the start address of the on-disk array; array-based index ing, given an
inode number, is fast and straightforward.
Finding an inode given an inode number in FFS is only slightly more
complicated, because FFS splits up the inode table into chun ks and places
a group of inodes within each cylinder group. Thus, one must k now how
big each chunk of inodes is and the start addresses of each. Af ter that, the
calculations are similar and also easy .
In LFS, life is more difﬁcult. Why? Well, we’ve managed to sca tter the
inodes all throughout the disk! Worse, we never overwrite in place, and
thus the latest version of an inode (i.e., the one we want) kee ps moving.
43.5 Solution Through Indirection: The Inode Map
To remedy this, the designers of LFS introduced a level of indirection
between inode numbers and the inodes through a data structur e called
the inode map (imap). The imap is a structure that takes an inode number
as input and produces the disk address of the most recent vers ion of the
inode. Thus, you can imagine it would often be implemented as a simple
array, with 4 bytes (a disk pointer) per entry . Any time an inode is written
to disk, the imap is updated with its new location.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 552

516 LOG -STRUCTURED FILE SYSTEMS
TIP : U SE A L EVEL OF INDIRECTION
People often say that the solution to all problems in Compute r Science
is simply a level of indirection . This is clearly not true; it is just the
solution to most problems. You certainly can think of every virtualization
we have studied, e.g., virtual memory , as simply a level of in direction.
And certainly the inode map in LFS is a virtualization of inod e numbers.
Hopefully you can see the great power of indirection in these examples,
allowing us to freely move structures around (such as pages i n the VM
example, or inodes in LFS) without having to change every ref erence to
them. Of course, indirection can have a downside too: extra overhead. So
next time you have a problem, try solving it with indirection . But make
sure to think about the overheads of doing so ﬁrst.
The imap, unfortunately , needs to be kept persistent (i.e., written to
disk); doing so allows LFS to keep track of the locations of in odes across
crashes, and thus operate as desired. Thus, a question: wher e should the
imap reside on disk?
It could live on a ﬁxed part of the disk, of course. Unfortunat ely , as it
gets updated frequently , this would then require updates toﬁle structures
to be followed by writes to the imap, and hence performance would suffer
(i.e., there would be more disk seeks, between each update an d the ﬁxed
location of the imap).
Instead, LFS places chunks of the inode map right next to wher e it is
writing all of the other new information. Thus, when appendi ng a data
block to a ﬁle k, LFS actually writes the new data block, its inode, and a
piece of the inode map all together onto the disk, as follows:
D
A0
I[k]
blk[0]:A0
A1
imap
map[k]:A1
In this picture, the piece of the imap array stored in the bloc k marked
imap tells LFS that the inode k is at disk address A1; this inode, in turn,
tells LFS that its data block D is at address A0.
43.6 The Checkpoint Region
The clever reader (that’s you, right?) might have noticed a p roblem
here. How do we ﬁnd the inode map, now that pieces of it are also now
spread across the disk? In the end, there is no magic: the ﬁle s ystem must
have some ﬁxed and known location on disk to begin a ﬁle lookup.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 553

LOG -STRUCTURED FILE SYSTEMS 517
LFS has just such a ﬁxed place on disk for this, known as the check-
point region (CR) . The checkpoint region contains pointers to (i.e., ad-
dresses of) the latest pieces of the inode map, and thus the in ode map
pieces can be found by reading the CR ﬁrst. Note the checkpoin t region
is only updated periodically (say every 30 seconds or so), and thus perfor-
mance is not ill-affected. Thus, the overall structure of th e on-disk layout
contains a checkpoint region (which points to the latest pie ces of the in-
ode map); the inode map pieces each contain addresses of the i nodes; the
inodes point to ﬁles (and directories) just like typical U NIX ﬁle systems.
Here is an example of the checkpoint region (note it is all the way at
the beginning of the disk, at address 0), and a single imap chu nk, inode,
and data block. A real ﬁle system would of course have a much bi gger
CR (indeed, it would have two, as we’ll come to understand lat er), many
imap chunks, and of course many more inodes, data blocks, etc .
imap
[k...k+N]:
A2
CR
0
D
A0
I[k]
blk[0]:A0
A1
imap
map[k]:A1
A2
43.7 Reading A File From Disk: A Recap
To make sure you understand how LFS works, let us now walk through
what must happen to read a ﬁle from disk. Assume we have nothin g in
memory to begin. The ﬁrst on-disk data structure we must read is the
checkpoint region. The checkpoint region contains pointer s (i.e., disk ad-
dresses) to the entire inode map, and thus LFS then reads in th e entire in-
ode map and caches it in memory . After this point, when given a n inode
number of a ﬁle, LFS simply looks up the inode-number to inode -disk-
address mapping in the imap, and reads in the most recent vers ion of the
inode. To read a block from the ﬁle, at this point, LFS proceed s exactly
as a typical U NIX ﬁle system, by using direct pointers or indirect pointers
or doubly-indirect pointers as need be. In the common case, L FS should
perform the same number of I/Os as a typical ﬁle system when re ading a
ﬁle from disk; the entire imap is cached and thus the extra wor k LFS does
during a read is to look up the inode’s address in the imap.
43.8 What About Directories?
Thus far, we’ve simpliﬁed our discussion a bit by only consid ering in-
odes and data blocks. However, to access a ﬁle in a ﬁle system ( such as
/home/remzi/foo, one of our favorite fake ﬁle names), some directo-
ries must be accessed too. So how does LFS store directory dat a?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 554

518 LOG -STRUCTURED FILE SYSTEMS
Fortunately , directory structure is basically identical t o classic U NIX
ﬁle systems, in that a directory is just a collection of (name, inode number)
mappings. For example, when creating a ﬁle on disk, LFS must both write
a new inode, some data, as well as the directory data and its in ode that
refer to this ﬁle. Remember that LFS will do so sequentially o n the disk
(after buffering the updates for some time). Thus, creating a ﬁle foo in a
directory would lead to the following new structures on disk :
D[k]
A0
I[k]
blk[0]:A0
A1
(foo, k)
D[dir]
A2
I[dir]
blk[0]:A2
A3
map[k]:A1
map[dir]:A3
imap
The piece of the inode map contains the information for the lo cation of
both the directory ﬁle dir as well as the newly-created ﬁle f . Thus, when
accessing ﬁle foo (with inode number f ), you would ﬁrst look in the
inode map (usually cached in memory) to ﬁnd the location of th e inode
of directory dir (A3); you then read the directory inode, which gives you
the location of the directory data ( A2); reading this data block gives you
the name-to-inode-number mapping of ( foo, k). You then consult the
inode map again to ﬁnd the location of inode number k (A1), and ﬁnally
read the desired data block at address A0.
There is one other serious problem in LFS that the inode map so lves,
known as the recursive update problem [Z+12]. The problem arises
in any ﬁle system that never updates in place (such as LFS), bu t rather
moves updates to new locations on the disk.
Speciﬁcally , whenever an inode is updated, its location on disk changes.
If we hadn’t been careful, this would have also entailed an up date to
the directory that points to this ﬁle, which then would have m andated
a change to the parent of that directory , and so on, all the way up the ﬁle
system tree.
LFS cleverly avoids this problem with the inode map. Even tho ugh
the location of an inode may change, the change is never reﬂec ted in the
directory itself; rather, the imap structure is updated whi le the directory
holds the same name-to-inumber mapping. Thus, through indi rection,
LFS avoids the recursive update problem.
43.9 A New Problem: Garbage Collection
You may have noticed another problem with LFS; it keeps writi ng
newer version of a ﬁle, its inode, and in fact all data to new pa rts of the
disk. This process, while keeping writes efﬁcient, implies that LFS leaves
older versions of ﬁle structures all over the disk, scattere d throughout the
disk. We call such old stuff garbage.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 555

LOG -STRUCTURED FILE SYSTEMS 519
For example, let’s imagine the case where we have an existing ﬁle re-
ferred to by inode number k, which points to a single data block D0. We
now overwrite that block, generating both a new inode and a ne w data
block. The resulting on-disk layout of LFS would look someth ing like this
(note we omit the imap and other structures for simplicity; a new chunk
of imap would also have to be written to disk to point to the new inode):
D0
A0
I[k]
blk[0]:A0
(both garbage)
D0
A4
I[k]
blk[0]:A4
In the diagram, you can see that both the inode and data block h ave
two versions on disk, one old (the one on the left) and one curr ent and
thus live (the one on the right). By the simple act of overwriting a data
block, a number of new structures must be persisted by LFS, th us leaving
old versions of said blocks on the disk.
As another example, imagine we instead append a block to that orig-
inal ﬁle k. In this case, a new version of the inode is generated, but the
old data block is still pointed to by the inode. Thus, it is sti ll live and very
much apart of the current ﬁle system:
D0
A0
I[k]
blk[0]:A0
(garbage)
D1
A4
I[k]
blk[0]:A0
blk[1]:A4
So what should we do with these older versions of inodes, data blocks,
and so forth? One could keep those older versions around and a llow
users to restore old ﬁle versions (for example, when they acc identally
overwrite or delete a ﬁle, it could be quite handy to do so); su ch a ﬁle
system is known as a versioning ﬁle system because it keeps track of the
different versions of a ﬁle.
However, LFS instead keeps only the latest live version of a ﬁ le; thus
(in the background), LFS must periodically ﬁnd these old dea d versions
of ﬁle data, inodes, and other structures, and clean them; cleaning should
thus make blocks on disk free again for use in a subsequent wri tes. Note
that the process of cleaning is a form of garbage collection , a technique
that arises in programming languages that automatically free unused mem-
ory for programs.
Earlier we discussed segments as important as they are the mechanism
that enables large writes to disk in LFS. As it turns out, they are also quite
integral to effective cleaning. Imagine what would happen i f the LFS
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 556

520 LOG -STRUCTURED FILE SYSTEMS
cleaner simply went through and freed single data blocks, in odes, etc.,
during cleaning. The result: a ﬁle system with some number of free holes
mixed between allocated space on disk. Write performance wo uld drop
considerably , as LFS would not be able to ﬁnd a large contiguo us region
to write to disk sequentially and with high performance.
Instead, the LFS cleaner works on a segment-by-segment basi s, thus
clearing up large chunks of space for subsequent writing. The basic clean-
ing process works as follows. Periodically , the LFS cleaner reads in a
number of old (partially-used) segments, determines which blocks are
live within these segments, and then write out a new set of seg ments
with just the live blocks within them, freeing up the old ones for writing.
Speciﬁcally , we expect the cleaner to read in M existing segments, com-
pact their contents into N new segments (where N < M ), and then write
the N segments to disk in new locations. The old M segments are then
freed and can be used by the ﬁle system for subsequent writes.
We are now left with two problems, however. The ﬁrst is mechan ism:
how can LFS tell which blocks within a segment are live, and wh ich are
dead? The second is policy: how often should the cleaner run, and which
segments should it pick to clean?
43.10 Determining Block Liveness
We address the mechanism ﬁrst. Given a data block D within an o n-
disk segment S, LFS must be able to determine whether D is live . To do
so, LFS adds a little extra information to each segment that d escribes each
block. Speciﬁcally , LFS includes, for each data block D, its inode number
(which ﬁle it belongs to) and its offset (which block of the ﬁl e this is). This
information is recorded in a structure at the head of the segm ent known
as the segment summary block .
Given this information, it is straightforward to determine whether a
block is live or dead. For a block D located on disk at address A , look
in the segment summary block and ﬁnd its inode number N and off set
T. Next, look in the imap to ﬁnd where N lives and read N from dis k
(perhaps it is already in memory , which is even better). Fina lly , using
the offset T, look in the inode (or some indirect block) to see where the
inode thinks the Tth block of this ﬁle is on disk. If it points e xactly to disk
address A, LFS can conclude that the block D is live. If it points anywhere
else, LFS can conclude that D is not in use (i.e., it is dead) an d thus know
that this version is no longer needed. A pseudocode summary o f this
process is shown here:
(N, T) = SegmentSummary[A];
inode = Read(imap[N]);
if (inode[T] == A)
// block D is alive
else
// block D is garbage
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 557

LOG -STRUCTURED FILE SYSTEMS 521
Here is a diagram depicting the mechanism, in which the segme nt
summary block (marked SS ) records that the data block at address A0
is actually a part of ﬁle k at offset 0. By checking the imap for k, you can
ﬁnd the inode, and see that it does indeed point to that locati on.
D
A0
I[k]
blk[0]:A0
A1
imap
map[k]:A1
ss
A0:
(k,0)
There are some shortcuts LFS takes to make the process of determining
liveness more efﬁcient. For example, when a ﬁle is truncated or deleted,
LFS increases its version number and records the new version number in
the imap. By also recording the version number in the on-disk segment,
LFS can short circuit the longer check described above simpl y by compar-
ing the on-disk version number with a version number in the im ap, thus
avoiding extra reads.
43.11 A Policy Question: Which Blocks To Clean, And When?
On top of the mechanism described above, LFS must include a se t of
policies to determine both when to clean and which blocks are worth
cleaning. Determining when to clean is easier; either perio dically , dur-
ing idle time, or when you have to because the disk is full.
Determining which blocks to clean is more challenging, and h as been
the subject of many research papers. In the original LFS pape r [RO91],
the authors describe an approach which tries to segregate hot and cold
segment. A hot segment is one in which the contents are being f requently
over-written; thus, for such a segment, the best policy is to wait a long
time before cleaning it, as more and more blocks are getting o ver-written
(in new segments) and thus being freed for use. A cold segment , in con-
trast, may have a few dead blocks but the rest of its contents a re relatively
stable. Thus, the authors conclude that one should clean col d segments
sooner and hot segments later, and develop a heuristic that d oes exactly
that. However, as with most policies, this is just one approa ch, and by
deﬁnition is not “the best” approach; later approaches show how to do
better [MR+97].
43.12 Crash Recovery And The Log
One ﬁnal problem: what happens if the system crashes while LF S is
writing to disk? As you may recall in the previous chapter abo ut jour-
naling, crashes during updates are tricky for ﬁle systems, a nd thus some-
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 558

522 LOG -STRUCTURED FILE SYSTEMS
thing LFS must consider as well.
During normal operation, LFS buffers writes in a segment, an d then
(when the segment is full, or when some amount of time has elap sed),
writes the segment to disk. LFS organizes these writes in a log, i.e., the
checkpoint region points to a head and tail segment, and each segment
points to the next segment to be written. LFS also periodically updates the
checkpoint region. Crashes could clearly happen during eit her of these
operations (write to a segment, write to the CR). So how does L FS handle
crashes during writes to these structures?
Let’s cover the second case ﬁrst. To ensure that the CR update happens
atomically , LFS actually keeps two CRs, one at either end of t he disk, and
writes to them alternately . LFS also implements a careful pr otocol when
updating the CR with the latest pointers to the inode map and other infor-
mation; speciﬁcally , it ﬁrst writes out a header (with timestamp), then the
body of the CR, and then ﬁnally one last block (also with a time stamp). If
the system crashes during a CR update, LFS can detect this by s eeing an
inconsistent pair of timestamps. LFS will always choose to u se the most
recent CR that has consistent timestamps, and thus consiste nt update of
the CR is achieved.
Let’s now address the ﬁrst case. Because LFS writes the CR eve ry 30
seconds or so, the last consistent snapshot of the ﬁle system may be quite
old. Thus, upon reboot, LFS can easily recover by simply read ing in the
checkpoint region, the imap pieces it points to, and subsequ ent ﬁles and
directories; however, the last many seconds of updates woul d be lost.
To improve upon this, LFS tries to rebuild many of those segme nts
through a technique known as roll forward in the database community .
The basic idea is to start with the last checkpoint region, ﬁn d the end of
the log (which is included in the CR), and then use that to read through
the next segments and see if there are any valid updates withi n it. If there
are, LFS updates the ﬁle system accordingly and thus recover s much of
the data and metadata written since the last checkpoint. See Rosenblum’s
award-winning dissertation for details [R92].
43.13 Summary
LFS introduces a new approach to updating the disk. Instead o f over-
writing ﬁles in places, LFS always writes to an unused portio n of the
disk, and then later reclaims that old space through cleanin g. This ap-
proach, which in database systems is called shadow paging [L77] and in
ﬁle-system-speak is sometimes called copy-on-write, enables highly efﬁ-
cient writing, as LFS can gather all updates into an in-memor y segment
and then write them out together sequentially .
The downside to this approach is that it generates garbage; o ld copies
of the data are scattered throughout the disk, and if one want s to reclaim
such space for subsequent usage, one must clean old segments periodi-
cally . Cleaning became the focus of much controversy in LFS, and con-
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 559

LOG -STRUCTURED FILE SYSTEMS 523
TIP : T URN FLAWS INTO VIRTUES
Whenever your system has a fundamental ﬂaw , see if you can tur n it
around into a feature or something useful. NetApp’s WAFL doe s this
with old ﬁle contents; by making old versions available, WAF L no longer
has to worry about cleaning, and thus provides a cool feature and re-
moves the LFS cleaning problem all in one wonderful twist. Ar e there
other examples of this in systems? Undoubtedly , but you’ll h ave to think
of them yourself, because this chapter is over with a capital “O”. Over.
Done. Kaput. We’re out. Peace!
cerns over cleaning costs [SS+95] perhaps limited LFS’s ini tial impact on
the ﬁeld. However, some modern commercial ﬁle systems, incl uding Ne-
tApp’s WAFL [HLM94], Sun’s ZFS [B07], and Linux btrfs [M07] adopt
a similar copy-on-write approach to writing to disk, and thu s the intel-
lectual legacy of LFS lives on in these modern ﬁle systems. In particular,
WAFL got around cleaning problems by turning them into a feat ure; by
providing old versions of the ﬁle system via snapshots, users could ac-
cess old ﬁles whenever they deleted current ones accidental ly .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 560

524 LOG -STRUCTURED FILE SYSTEMS
References
[B07] “ZFS: The Last Word in File Systems”
Jeff Bonwick and Bill Moore
Available: http://opensolaris.org/os/community/zfs/docs/zfs
last.pdf
Slides on ZFS; unfortunately, there is no great ZFS paper.
[HLM94] “File System Design for an NFS File Server Appliance ”
Dave Hitz, James Lau, Michael Malcolm
USENIX Spring ’94
WAFL takes many ideas from LFS and RAID and puts it into a high- speed NFS appliance for the
multi-billion dollar storage company NetApp.
[L77] “Physical Integrity in a Large Segmented Database”
R. Lorie
ACM Transactions on Databases, 1977, V olume 2:1, pages 91-104
The original idea of shadow paging is presented here.
[M07] “The Btrfs Filesystem”
Chris Mason
September 2007
Available: oss.oracle.com/projects/btrfs/dist/documentation/btrfs-ukuug.pdf
A recent copy-on-write Linux ﬁle system, slowly gaining in i mportance and usage.
[MJLF84] “A Fast File System for UNIX”
Marshall K. McKusick, William N. Joy , Sam J. Lefﬂer, Robert S. Fabry
ACM TOCS, August, 1984, V olume 2, Number 3
The original FFS paper; see the chapter on FFS for more detail s.
[MR+97] “Improving the Performance of Log-structured File Systems with Adaptive Meth-
ods” Jeanna Neefe Matthews, Drew Roselli, Adam M. Costello, Randolph Y . Wang, Thomas E.
Anderson
SOSP 1997, pages 238-251, October, Saint Malo, France
A more recent paper detailing better policies for cleaning i n LFS.
[M94] “A Better Update Policy”
Jeffrey C. Mogul
USENIX ATC ’94, June 1994
In this paper, Mogul ﬁnds that read workloads can be harmed by buffering writes for too long and then
sending them to the disk in a big burst. Thus, he recommends se nding writes more frequently and in
smaller batches.
[P98] “Hardware Technology Trends and Database Opportunities”
David A. Patterson
ACM SIGMOD ’98 Keynote Address, Presented June 3, 1998, Seat tle, Washington
Available: http://www.cs.berkeley .edu/˜pattrsn/talks/keynote.html
A great set of slides on technology trends in computer system s. Hopefully, Patterson will create another
of these sometime soon.
[RO91] “Design and Implementation of the Log-structured Fi le System”
Mendel Rosenblum and John Ousterhout
SOSP ’91, Paciﬁc Grove, CA, October 1991
The original SOSP paper about LFS, which has been cited by hun dreds of other papers and inspired
many real systems.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

