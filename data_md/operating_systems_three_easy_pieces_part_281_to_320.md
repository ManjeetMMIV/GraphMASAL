# Document: operating_systems_three_easy_pieces (Pages 281 to 320)

## Page 281

23
The VAX/VMS Virtual Memory System
Before we end our study of virtual memory , let us take a closerlook at one
particularly clean and well done virtual memory manager, th at found in
the V AX/VMS operating system [LL82]. In this note, we will di scuss the
system to illustrate how some of the concepts brought forth i n earlier
chapters together in a complete memory manager.
23.1 Background
The V AX-11 minicomputer architecture was introduced in thelate 1970’s
by Digital Equipment Corporation (DEC). DEC was a massive player
in the computer industry during the era of the mini-computer ; unfortu-
nately , a series of bad decisions and the advent of the PC slow ly (but
surely) led to their demise [C03]. The architecture was real ized in a num-
ber of implementations, including the V AX-11/780 and the less powerful
V AX-11/750.
The OS for the system was known as V AX/VMS (or just plain VMS),
one of whose primary architects was Dave Cutler, who later le d the effort
to develop Microsoft’s Windows NT [C93]. VMS had the general prob-
lem that it would be run on a broad range of machines, includin g very
inexpensive V AXen (yes, that is the proper plural) to extrem ely high-end
and powerful machines in the same architecture family . Thus, the OS had
to have mechanisms and policies that worked (and worked well ) across
this huge range of systems.
THE CRUX : H OW TO AVOID THE CURSE OF GENERALITY
Operating systems often have a problem known as “the curse of gen-
erality”, where they are tasked with general support for a br oad class of
applications and systems. The fundamental result of the cur se is that the
OS is not likely to support any one installation very well. In the case of
VMS, the curse was very real, as the V AX-11 architecture was r ealized in
a number of different implementations. Thus, how can an OS be built so
as to run effectively on a wide range of systems?
245

## Page 282

246 THE VAX/VMS V IRTUAL MEMORY SYSTEM
As an additional issue, VMS is an excellent example of softwa re inno-
vations used to hide some of the inherent ﬂaws of the architec ture. Al-
though the OS often relies on the hardware to build efﬁcient a bstractions
and illusions, sometimes the hardware designers don’t quit e get every-
thing right; in the V AX hardware, we’ll see a few examples of t his, and
what the VMS operating system does to build an effective, wor king sys-
tem despite these hardware ﬂaws.
23.2 Memory Management Hardware
The V AX-11 provided a 32-bit virtual address space per proce ss, di-
vided into 512-byte pages. Thus, a virtual address consiste d of a 23-bit
VPN and a 9-bit offset. Further, the upper two bits of the VPN w ere used
to differentiate which segment the page resided within; thu s, the system
was a hybrid of paging and segmentation, as we saw previously .
The lower-half of the address space was known as “process space” and
is unique to each process. In the ﬁrst half of process space (k nown as P0),
the user program is found, as well as a heap which grows downwa rd.
In the second half of process space ( P1), we ﬁnd the stack, which grows
upwards. The upper-half of the address space is known as syst em space
(S), although only half of it is used. Protected OS code and data reside
here, and the OS is in this way shared across processes.
One major concern of the VMS designers was the incredibly sma ll size
of pages in the V AX hardware (512 bytes). This size, chosen fo r historical
reasons, has the fundamental problem of making simple linea r page ta-
bles excessively large. Thus, one of the ﬁrst goals of the VMS designers
was to make sure that VMS would not overwhelm memory with page
tables.
The system reduced the pressure page tables place on memory i n two
ways. First, by segmenting the user address space into two, t he V AX-11
provides a page table for each of these regions ( P0 and P1) per process;
thus, no page-table space is needed for the unused portion of the address
space between the stack and the heap. The base and bounds regi sters
are used as you would expect; a base register holds the addres s of the
page table for that segment, and the bounds holds its size (i. e., number of
page-table entries).
Second, the OS reduces memory pressure even further by placi ng user
page tables (for P0 and P1, thus two per process) in kernel virtual mem-
ory . Thus, when allocating or growing a page table, the kerne l allocates
space out of its own virtual memory , in segment S. If memory comes un-
der severe pressure, the kernel can swap pages of these page t ables out to
disk, thus making physical memory available for other uses.
Putting page tables in kernel virtual memory means that address trans-
lation is even further complicated. For example, to transla te a virtual ad-
dress in P0 or P1, the hardware has to ﬁrst try to look up the page-table
entry for that page in its page table (the P0 or P1 page table for that pro-
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 283

THE VAX/VMS V IRTUAL MEMORY SYSTEM 247
Page 0: Invalid
User Code
User Heap
User Stack
Trap Tables
Kernel Data
Kernel Code
Kernel Heap
Unused
System (S)
User (P1)
User (P0)
0
2 30
2 31
2 32
Figure 23.1: The V AX/VMS Address Space
cess); in doing so, however, the hardware may ﬁrst have to con sult the
system page table (which lives in physical memory); with tha t transla-
tion complete, the hardware can learn the address of the page of the page
table, and then ﬁnally learn the address of the desired memor y access.
All of this, fortunately , is made faster by the V AX’s hardwar e-managed
TLBs, which usually (hopefully) circumvent this laborious lookup.
23.3 A Real Address Space
One neat aspect of studying VMS is that we can see how a real add ress
space is constructed (Figure 23.1. Thus far, we have assumed a simple
address space of just user code, user data, and user heap, but as we can
see above, a real address space is notably more complex.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 284

248 THE VAX/VMS V IRTUAL MEMORY SYSTEM
ASIDE : WHY NULL POINTER ACCESSES CAUSE SEG FAULTS
You should now have a good understanding of exactly what happ ens on
a null-pointer dereference. A process generates a virtual a ddress of 0, by
doing something like this:
int *p = NULL; // set p = 0
*p = 10; // try to store value 10 to virtual address 0
The hardware tries to look up the VPN (also 0 here) in the TLB, a nd suf-
fers a TLB miss. The page table is consulted, and the entry for VPN 0
is found to be marked invalid. Thus, we have an invalid access , which
transfers control to the OS, which likely terminates the pro cess (on U NIX
systems, processes are sent a signal which allows them to rea ct to such a
fault; if uncaught, however, the process is killed).
For example, the code segment never begins at page 0. This pag e,
instead, is marked inaccessible, in order to provide some su pport for de-
tecting null-pointer accesses. Thus, one concern when designing an ad-
dress space is support for debugging, which the inaccessibl e zero page
provides here in some form.
Perhaps more importantly , the kernel virtual address space (i.e., its
data structures and code) is a part of each user address space . On a con-
text switch, the OS changes the P0 and P1 registers to point to the ap-
propriate page tables of the soon-to-be-run process; howev er, it does not
change the S base and bound registers, and as a result the “same” kernel
structures are mapped into each user address space.
The kernel is mapped into each address space for a number of re asons.
This construction makes life easier for the kernel; when, fo r example, the
OS is handed a pointer from a user program (e.g., on a write() system
call), it is easy to copy data from that pointer to its own stru ctures. The
OS is naturally written and compiled, without worry of where the data
it is accessing comes from. If in contrast the kernel were loc ated entirely
in physical memory , it would be quite hard to do things like sw ap pages
of the page table to disk; if the kernel were given its own addr ess space,
moving data between user applications and the kernel would a gain be
complicated and painful. With this construction (now used w idely), the
kernel appears almost as a library to applications, albeit a protected one.
One last point about this address space relates to protectio n. Clearly ,
the OS does not want user applications reading or writing OS d ata or
code. Thus, the hardware must support different protection levels for
pages to enable this. The V AX did so by specifying, in protect ion bits
in the page table, what privilege level the CPU must be at in or der to
access a particular page. Thus, system data and code are set t o a higher
level of protection than user data and code; an attempted acc ess to such
information from user code will generate a trap into the OS, a nd (you
guessed it) the likely termination of the offending process .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 285

THE VAX/VMS V IRTUAL MEMORY SYSTEM 249
23.4 Page Replacement
The page table entry (PTE) in V AX contains the following bits : a valid
bit, a protection ﬁeld (4 bits), a modify (or dirty) bit, a ﬁel d reserved for
OS use (5 bits), and ﬁnally a physical frame number (PFN) to st ore the
location of the page in physical memory . The astute reader mi ght note:
no reference bit ! Thus, the VMS replacement algorithm must make do
without hardware support for determining which pages are ac tive.
The developers were also concerned about memory hogs , programs
that use a lot of memory and make it hard for other programs to r un.
Most of the policies we have looked at thus far are susceptibl e to such
hogging; for example, LRU is a global policy that doesn’t share memory
fairly among processes.
Segmented FIFO
To address these two problems, the developers came up with th e seg-
mented FIFO replacement policy [RL81]. The idea is simple: each pro-
cess has a maximum number of pages it can keep in memory , known as
its resident set size (RSS). Each of these pages is kept on a FIFO list; when
a process exceeds its RSS, the “ﬁrst-in” page is evicted. FIF O clearly does
not need any support from the hardware, and is thus easy to imp lement.
Of course, pure FIFO does not perform particularly well, as w e saw
earlier. To improve FIFO’s performance, VMS introduced two second-
chance lists where pages are placed before getting evicted from memory ,
speciﬁcally a global clean-page free list and dirty-page list. When a process
P exceeds its RSS, a page is removed from its per-process FIFO; if clean
(not modiﬁed), it is placed on the end of the clean-page list; if dirty (mod-
iﬁed), it is placed on the end of the dirty-page list.
If another process Q needs a free page, it takes the ﬁrst free page off
of the global clean list. However, if the original process P faults on that
page before it is reclaimed, P reclaims it from the free (or dirty) list, thus
avoiding a costly disk access. The bigger these global secon d-chance lists
are, the closer the segmented FIFO algorithm performs to LRU [RL81].
Page Clustering
Another optimization used in VMS also helps overcome the sma ll page
size in VMS. Speciﬁcally , with such small pages, disk I/O dur ing swap-
ping could be highly inefﬁcient, as disks do better with larg e transfers.
To make swapping I/O more efﬁcient, VMS adds a number of optim iza-
tions, but most important is clustering. With clustering, VMS groups
large batches of pages together from the global dirty list, a nd writes them
to disk in one fell swoop (thus making them clean). Clusterin g is used
in most modern systems, as the freedom to place pages anywher e within
swap space lets the OS group pages, perform fewer and bigger w rites,
and thus improve performance.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 286

250 THE VAX/VMS V IRTUAL MEMORY SYSTEM
ASIDE : EMULATING REFERENCE BITS
As it turns out, you don’t need a hardware reference bit in ord er to get
some notion of which pages are in use in a system. In fact, in th e early
1980’s, Babaoglu and Joy showed that protection bits on the V AX can be
used to emulate reference bits [BJ81]. The basic idea: if you want to gain
some understanding of which pages are actively being used in a system,
mark all of the pages in the page table as inaccessible (but ke ep around
the information as to which pages are really accessible by th e process,
perhaps in the “reserved OS ﬁeld” portion of the page table en try). When
a process accesses a page, it will generate a trap into the OS; the OS will
then check if the page really should be accessible, and if so, revert the
page to its normal protections (e.g., read-only , or read-write). At the time
of a replacement, the OS can check which pages remain marked i nacces-
sible, and thus get an idea of which pages have not been recent ly used.
The key to this “emulation” of reference bits is reducing ove rhead while
still obtaining a good idea of page usage. The OS must not be to o aggres-
sive in marking pages inaccessible, or overhead would be too high. The
OS also must not be too passive in such marking, or all pages wi ll end up
referenced; the OS will again have no good idea which page to e vict.
23.5 Other Neat VM Tricks
VMS had two other now-standard tricks: demand zeroing and co py-
on-write. We now describe these lazy optimizations.
One form of laziness in VMS (and most modern systems) is demand
zeroing of pages. To understand this better, let’s consider the exam ple
of adding a page to your address space, say in your heap. In a na ive
implementation, the OS responds to a request to add a page to y our heap
by ﬁnding a page in physical memory , zeroing it (required for security;
otherwise you’d be able to see what was on the page from when so me
other process used it!), and then mapping it into your addres s space (i.e.,
setting up the page table to refer to that physical page as des ired). But the
naive implementation can be costly , particularly if the pag e does not get
used by the process.
With demand zeroing, the OS instead does very little work whe n the
page is added to your address space; it puts an entry in the pag e table
that marks the page inaccessible. If the process then reads o r writes the
page, a trap into the OS takes place. When handling the trap, t he OS no-
tices (usually through some bits marked in the “reserved for OS” portion
of the page table entry) that this is actually a demand-zero p age; at this
point, the OS then does the needed work of ﬁnding a physical pa ge, ze-
roing it, and mapping it into the process’s address space. If the process
never accesses the page, all of this work is avoided, and thus the virtue of
demand zeroing.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 287

THE VAX/VMS V IRTUAL MEMORY SYSTEM 251
TIP : B E LAZY
Being lazy can be a virtue in both life as well as in operating s ystems.
Laziness can put off work until later, which is beneﬁcial wit hin an OS for
a number of reasons. First, putting off work might reduce the latency of
the current operation, thus improving responsiveness; for example, op-
erating systems often report that writes to a ﬁle succeeded i mmediately ,
and only write them to disk later in the background. Second, a nd more
importantly , laziness sometimes obviates the need to do the work at all;
for example, delaying a write until the ﬁle is deleted remove s the need to
do the write at all. Laziness is also good in life: for example , by putting
off your OS project, you may ﬁnd that the project speciﬁcatio n bugs are
worked out by your fellow classmates; however, the class pro ject is un-
likely to get canceled, so being too lazy may be problematic, leading to a
late project, bad grade, and a sad professor. Don’t make prof essors sad!
Another cool optimization found in VMS (and again, in virtually every
modern OS) is copy-on-write (COW for short). The idea, which goes at
least back to the TENEX operating system [BB+72], is simple: when the
OS needs to copy a page from one address space to another, inst ead of
copying it, it can map it into the target address space and mar k it read-
only in both address spaces. If both address spaces only read the page, no
further action is taken, and thus the OS has affected a fast co py without
actually moving any data.
If, however, one of the address spaces does indeed try to writ e to the
page, it will trap into the OS. The OS will then notice that the page is a
COW page, and thus (lazily) allocate a new page, ﬁll it with th e data, and
map this new page into the address space of the faulting proce ss. The
process then continues and now has its own private copy of the page.
COW is useful for a number of reasons. Certainly any sort of sh ared
library can be mapped copy-on-write into the address spaces of many
processes, saving valuable memory space. In U NIX systems, COW is
even more critical, due to the semantics of fork() and exec(). As
you might recall, fork() creates an exact copy of the address space of
the caller; with a large address space, making such a copy is s low and
data intensive. Even worse, most of the address space is imme diately
over-written by a subsequent call to exec(), which overlays the calling
process’s address space with that of the soon-to-be-exec’d program. By
instead performing a copy-on-write fork(), the OS avoids much of the
needless copying and thus retains the correct semantics whi le improving
performance.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 288

252 THE VAX/VMS V IRTUAL MEMORY SYSTEM
23.6 Summary
You have now seen a top-to-bottom review of an entire virtual mem-
ory system. Hopefully , most of the details were easy to follo w , as you
should have already had a good understanding of most of the basic mech-
anisms and policies. More detail is available in the excelle nt (and short)
paper by Levy and Lipman [LL82]; we encourage you to read it, a great
way to see what the source material behind these chapters is l ike.
You should also learn more about the state of the art by readin g about
Linux and other modern systems when possible. There is a lot o f source
material out there, including some reasonable books [BC05] . One thing
that will amaze you: how classic ideas, found in old papers su ch as
this one on V AX/VMS, still inﬂuence how modern operating systems are
built.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 289

THE VAX/VMS V IRTUAL MEMORY SYSTEM 253
References
[BB+72] “TENEX, A Paged Time Sharing System for the PDP-10”
Daniel G. Bobrow, Jerry D. Burchﬁel, Daniel L. Murphy , Raymond S. Tomlinson
Communications of the ACM, V olume 15, March 1972
An early time-sharing OS where a number of good ideas came fro m. Copy-on-write was just one of
those; inspiration for many other aspects of modern systems , including process management, virtual
memory, and ﬁle systems are found herein.
[BJ81] “Converting a Swap-Based System to do Paging
in an Architecture Lacking Page-Reference Bits”
Ozalp Babaoglu and William N. Joy
SOSP ’81, December 1981, Paciﬁc Grove, California
A clever idea paper on how to exploit existing protection machinery within a machine in order to emulate
reference bits. The idea came from the group at Berkeley work ing on their own version of UNIX, known
as the Berkeley Systems Distribution, or BSD. The group was h eavily inﬂuential in the development of
UNIX, in virtual memory, ﬁle systems, and networking.
[BC05] “Understanding the Linux Kernel (Third Edition)”
Daniel P . Bovet and Marco Cesati
O’Reilly Media, November 2005
One of the many books you can ﬁnd on Linux. They go out of date qu ickly, but many of the basics
remain and are worth reading about.
[C03] “The Innovator’s Dilemma”
Clayton M. Christenson
Harper Paperbacks, January 2003
A fantastic book about the disk-drive industry and how new in novations disrupt existing ones. A good
read for business majors and computer scientists alike. Pro vides insight on how large and successful
companies completely fail.
[C93] “Inside Windows NT”
Helen Custer and David Solomon
Microsoft Press, 1993
The book about Windows NT that explains the system top to bott om, in more detail than you might like.
But seriously, a pretty good book.
[LL82] “Virtual Memory Management in the V AX/VMS Operating System”
Henry M. Levy , Peter H. Lipman
IEEE Computer, V olume 15, Number 3 (March 1982) Read the original source of most of this ma-
terial; tt is a concise and easy read. Particularly importan t if you wish to go to graduate school, where
all you do is read papers, work, read some more papers, work mo re, eventually write a paper, and then
work some more. But it is fun!
[RL81] “Segmented FIFO Page Replacement”
Rollins Turner and Henry Levy
SIGMETRICS ’81
A short paper that shows for some workloads, segmented FIFO c an approach the performance of LRU.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 291

24
Summary Dialogue on Memory Virtualization
Student: (Gulps) Wow, that was a lot of material.
Professor: Y es, and?
Student: Well, how am I supposed to remember it all? Y ou know, for the ex am?
Professor: Goodness, I hope that’s not why you are trying to remember it.
Student: Why should I then?
Professor: Come on, I thought you knew better. Y ou’re trying to learn som e-
thing here, so that when you go off into the world, you’ll unde rstand how systems
actually work.
Student: Hmm... can you give an example?
Professor: Sure! One time back in graduate school, my friends and I were
measuring how long memory accesses took, and once in a while t he numbers
were way higher than we expected; we thought all the data was ﬁ tting nicely into
the second-level hardware cache, you see, and thus should ha ve been really fast
to access.
Student: (nods)
Professor: We couldn’t ﬁgure out what was going on. So what do you do in suc h
a case? Easy, ask a professor! So we went and asked one of our pr ofessors, who
looked at the graph we had produced, and simply said “TLB”. Ah a! Of course,
TLB misses! Why didn’t we think of that? Having a good model of how virtual
memory works helps diagnose all sorts of interesting perfor mance problems.
Student: I think I see. I’m trying to build these mental models of how th ings
work, so that when I’m out there working on my own, I won’t be su rprised when
a system doesn’t quite behave as expected. I should even be ab le to anticipate how
the system will work just by thinking about it.
Professor: Exactly. So what have you learned? What’s in your mental mode l of
how virtual memory works?
Student: Well, I think I now have a pretty good idea of what happens when
memory is referenced by a process, which, as you’ve said many times, happens
255

## Page 292

256 S UMMARY DIALOGUE ON MEMORY VIRTUALIZATION
on each instruction fetch as well as explicit loads and store s.
Professor: Sounds good – tell me more.
Student: Well, one thing I’ll always remember is that the addresses we see in a
user program, written in C for example...
Professor: What other language is there?
Student: (continuing) ... Y es, I know you like C. So do I! Anyhow, as I wa s
saying, I now really know that all addresses that we can observe within a program
are virtual addresses; that I, as a programmer, am just given this illusion of where
data and code are in memory. I used to think it was cool that I co uld print the
address of a pointer, but now I ﬁnd it frustrating – it’s just a virtual address! I
can’t see the real physical address where the data lives.
Professor: Nope, the OS deﬁnitely hides that from you. What else?
Student: Well, I think the TLB is a really key piece, providing the syst em with
a small hardware cache of address translations. Page tables are usually quite
large and hence live in big and slow memories. Without that TL B, programs
would certainly run a great deal more slowly. Seems like the T LB truly makes
virtualizing memory possible. I couldn’t imagine building a system without one!
And I shudder at the thought of a program with a working set tha t exceeds the
coverage of the TLB: with all those TLB misses, it would be har d to watch.
Professor: Y es, cover the eyes of the children! Beyond the TLB, what did y ou
learn?
Student: I also now understand that the page table is one of those data structures
you need to know about; it’s just a data structure, though, an d that means almost
any structure could be used. We started with simple structures, like arrays (a.k.a.
linear page tables), and advanced all the way up to multi-lev el tables (which look
like trees), and even crazier things like pageable page tabl es in kernel virtual
memory. All to save a little space in memory!
Professor: Indeed.
Student: And here’s one more important thing: I learned that the addre ss trans-
lation structures need to be ﬂexible enough to support what p rogrammers want
to do with their address spaces. Structures like the multi-l evel table are perfect
in this sense; they only create table space when the user need s a portion of the
address space, and thus there is little waste. Earlier attem pts, like the simple base
and bounds register, just weren’t ﬂexible enough; the struc tures need to match
what users expect and want out of their virtual memory system .
Professor: That’s a nice perspective. What about all of the stuff we lear ned
about swapping to disk?
Student: Well, it’s certainly fun to study, and good to know how page re place-
ment works. Some of the basic policies are kind of obvious (li ke LRU, for ex-
ample), but building a real virtual memory system seems more interesting, like
we saw in the VMS case study. But somehow, I found the mechanis ms more
interesting, and the policies less so.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 293

SUMMARY DIALOGUE ON MEMORY VIRTUALIZATION 257
Professor: Oh, why is that?
Student: Well, as you said, in the end the best solution to policy probl ems is
simple: buy more memory. But the mechanisms you need to under stand to know
how stuff really works. Speaking of which...
Professor: Y es?
Student: Well, my machine is running a little slowly these days... and memory
certainly doesn’t cost that much...
Professor: Oh ﬁne, ﬁne! Here’s a few bucks. Go and get yourself some DRAM,
cheapskate.
Student: Thanks professor! I’ll never swap to disk again – or, if I do, a t least I’ll
know what’s actually going on!
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 295

Part II
Concurrency
259

## Page 297

25
A Dialogue on Concurrency
Professor: And thus we reach the second of our three pillars of operating sys-
tems: concurrency.
Student: I thought there were four pillars...?
Professor: Nope, that was in an older version of the book.
Student: Umm... OK. So what is concurrency, oh wonderful professor?
Professor: Well, imagine we have a peach –
Student: (interrupting) Peaches again! What is it with you and peache s?
Professor: Ever read T.S. Eliot? The Love Song of J. Alfred Prufrock, “Do I dare
to eat a peach”, and all that fun stuff?
Student: Oh yes! In English class in high school. Great stuff! I really liked the
part where –
Professor: (interrupting) This has nothing to do with that – I just like p eaches.
Anyhow, imagine there are a lot of peaches on a table, and a lot of people who
wish to eat them. Let’s say we did it this way: each eater ﬁrst i dentiﬁes a peach
visually, and then tries to grab it and eat it. What is wrong wi th this approach?
Student: Hmmm... seems like you might see a peach that somebody else al so
sees. If they get there ﬁrst, when you reach out, no peach for y ou!
Professor: Exactly! So what should we do about it?
Student: Well, probably develop a better way of going about this. Mayb e form a
line, and when you get to the front, grab a peach and get on with it.
Professor: Good! But what’s wrong with your approach?
Student: Sheesh, do I have to do all the work?
Professor: Y es.
Student: OK, let me think. Well, we used to have many people grabbing fo r
peaches all at once, which is faster. But in my way, we just go o ne at a time,
which is correct, but quite a bit slower. The best kind of appr oach would be fast
and correct, probably.
261

## Page 298

262 A D IALOGUE ON CONCURRENCY
Professor: Y ou are really starting to impress. In fact, you just told us everything
we need to know about concurrency! Well done.
Student: I did? I thought we were just talking about peaches. Remember , this
is usually a part where you make it about computers again.
Professor: Indeed. My apologies! One must never forget the concrete. We ll,
as it turns out, there are certain types of programs that we ca ll multi-threaded
applications; each thread is kind of like an independent agent running around
in this program, doing things on the program’s behalf. But th ese threads access
memory, and for them, each spot of memory is kind of like one of those peaches. If
we don’t coordinate access to memory between threads, the pr ogram won’t work
as expected. Make sense?
Student: Kind of. But why do we talk about this in an OS class? Isn’t that just
application programming?
Professor: Good question! A few reasons, actually. First, the OS must su pport
multi-threaded applications with primitives such as locks and condition vari-
ables, which we’ll talk about soon. Second, the OS itself was the ﬁr st concurrent
program – it must access its own memory very carefully or many strange and
terrible things will happen. Really, it can get quite grisly .
Student: I see. Sounds interesting. There are more details, I imagine ?
Professor: Indeed there are...
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 299

26
Concurrency: An Introduction
Thus far, we have seen the development of the basic abstracti ons that the
OS performs. We have seen how to take a single physical CPU and turn
it into multiple virtual CPUs, thus enabling the illusion of multiple pro-
grams running at the same time. We have also seen how to create the
illusion of a large, private virtual memory for each process; this abstrac-
tion of the address space enables each program to behave as if it has its
own memory when indeed the OS is secretly multiplexing address spaces
across physical memory (and sometimes, disk).
In this note, we introduce a new abstraction for a single runn ing pro-
cess: that of a thread. Instead of our classic view of a single point of
execution within a program (i.e., a single PC where instruct ions are be-
ing fetched from and executed), a multi-threaded program has more than
one point of execution (i.e., multiple PCs, each of which is b eing fetched
and executed from). Perhaps another way to think of this is th at each
thread is very much like a separate process, except for one di fference:
they share the same address space and thus can access the same data.
The state of a single thread is thus very similar to that of a pr ocess.
It has a program counter (PC) that tracks where the program is fetch-
ing instructions from. Each thread has its own private set of registers it
uses for computation; thus, if there are two threads that are running on
a single processor, when switching from running one (T1) to r unning the
other (T2), a context switch must take place. The context switch between
threads is quite similar to the context switch between proce sses, as the
register state of T1 must be saved and the register state of T2 restored
before running T2. With processes, we saved state to a process control
block (PCB); now , we’ll need one or more thread control blocks (TCBs)
to store the state of each thread of a process. There is one major difference,
though, in the context switch we perform between threads as c ompared
to processes: the address space remains the same (i.e., ther e is no need to
switch which page table we are using).
One other major difference between threads and processes co ncerns
the stack. In our simple model of the address space of a classi c process
(which we can now call a single-threaded process), there is a single stack,
usually residing at the bottom of the address space (Figure 26.1, left).
263

## Page 300

264 CONCURRENCY : A N INTRODUCTION
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
16KB
15KB
2KB
1KB
0KB
Stack (1)
Stack (2)
(free)
(free)
Heap
Program Code
Figure 26.1: A Single-Threaded Address Space
However, in a multi-threaded process, each thread runs independently
and of course may call into various routines to do whatever wo rk it is do-
ing. Instead of a single stack in the address space, there wil l be one per
thread. Let’s say we have a multi-threaded process that has t wo threads
in it; the resulting address space looks different (Figure 26.1, right).
In this ﬁgure, you can see two stacks spread throughout the ad dress
space of the process. Thus, any stack-allocated variables, parameters, re-
turn values, and other things that we put on the stack will be p laced in
what is sometimes called thread-local storage, i.e., the stack of the rele-
vant thread.
You might also notice how this ruins our beautiful address sp ace lay-
out. Before, the stack and heap could grow independently and trouble
only arose when you ran out of room in the address space. Here, we
no longer have such a nice situation. Fortunately , this is us ually OK, as
stacks do not generally have to be very large (the exception b eing in pro-
grams that make heavy use of recursion).
26.1 An Example: Thread Creation
Let’s say we wanted to run a program that created two threads, each
of which was doing some independent work, in this case printi ng “A” or
“B”. The code is shown in Figure 26.2.
The main program creates two threads, each of which will run t he
function mythread(), though with different arguments (the string A or
B). Once a thread is created, it may start running right away (d epending
on the whims of the scheduler); alternately , it may be put in a “ready” but
not “running” state and thus not run yet. After creating the t wo threads
(T1 and T2), the main thread calls pthread join(), which waits for a
particular thread to complete.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 301

CONCURRENCY : A N INTRODUCTION 265
1 #include <stdio.h>
2 #include <assert.h>
3 #include <pthread.h>
4
5 void *mythread(void *arg) {
6 printf("%s\n", (char *) arg);
7 return NULL;
8 }
9
10 int
11 main(int argc, char *argv[]) {
12 pthread_t p1, p2;
13 br int rc;
14 printf("main: begin\n");
15 rc = pthread_create(&p1, NULL, mythread, "A"); assert(rc = = 0);
16 rc = pthread_create(&p2, NULL, mythread, "B"); assert(rc = = 0);
17 // join waits for the threads to finish
18 rc = pthread_join(p1, NULL); assert(rc == 0);
19 rc = pthread_join(p2, NULL); assert(rc == 0);
20 printf("main: end\n");
21 return 0;
22 }
Figure 26.2: Simple Thread Creation Code (t0.c)
Let us examine the possible execution ordering of this littl e program.
In the execution diagram (Table
26.1), time increases in the downwards
direction, and each column shows when a different thread (th e main one,
or Thread 1, or Thread 2) is running.
Note, however, that this ordering is not the only possible or dering. In
fact, given a sequence of instructions, there are quite a few , depending on
which thread the scheduler decides to run at a given point. Fo r example,
once a thread is created, it may run immediately , which wouldlead to the
execution shown in Table 26.2.
We also could even see “B” printed before “A”, if, say , the sch eduler
decided to run Thread 2 ﬁrst even though Thread 1 was created e arlier;
there is no reason to assume that a thread that is created ﬁrst will run ﬁrst.
Table 26.3 shows this ﬁnal execution ordering, with Thread 2 getting to
strut its stuff before Thread 1.
As you might be able to see, one way to think about thread creat ion
is that it is a bit like making a function call; however, inste ad of ﬁrst ex-
ecuting the function and then returning to the caller, the sy stem instead
creates a new thread of execution for the routine that is bein g called, and
it runs independently of the caller, perhaps before returni ng from the cre-
ate, but perhaps much later.
As you also might be able to tell from this example, threads ma ke life
complicated: it is already hard to tell what will run when! Co mputers are
hard enough to understand without concurrency . Unfortunat ely , with
concurrency , it gets worse. Much worse.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 302

266 CONCURRENCY : A N INTRODUCTION
main Thread 1 Thread2
starts running
prints “main: begin”
creates Thread 1
creates Thread 2
waits for T1
runs
prints “A”
returns
waits for T2
runs
prints “B”
returns
prints “main: end”
Table 26.1: Thread T race (1)
main Thread 1 Thread2
starts running
prints “main: begin”
creates Thread 1
runs
prints “A”
returns
creates Thread 2
runs
prints “B”
returns
waits for T1
returns immediately; T1 is done
waits for T2
returns immediately; T2 is done
prints “main: end”
Table 26.2: Thread T race (2)
main Thread 1 Thread2
starts running
prints “main: begin”
creates Thread 1
creates Thread 2
runs
prints “B”
returns
waits for T1
runs
prints “A”
returns
waits for T2
returns immediately; T2 is done
prints “main: end”
Table 26.3: Thread T race (3)
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 303

CONCURRENCY : A N INTRODUCTION 267
1 #include <stdio.h>
2 #include <pthread.h>
3 #include "mythreads.h"
4
5 static volatile int counter = 0;
6
7 //
8 // mythread()
9 //
10 // Simply adds 1 to counter repeatedly, in a loop
11 // No, this is not how you would add 10,000,000 to
12 // a counter, but it shows the problem nicely.
13 //
14 void *
15 mythread(void *arg)
16 {
17 printf("%s: begin\n", (char *) arg);
18 int i;
19 for (i = 0; i < 1e7; i++) {
20 counter = counter + 1;
21 }
22 printf("%s: done\n", (char *) arg);
23 return NULL;
24 }
25
26 //
27 // main()
28 //
29 // Just launches two threads (pthread_create)
30 // and then waits for them (pthread_join)
31 //
32 int
33 main(int argc, char *argv[])
34 {
35 pthread_t p1, p2;
36 printf("main: begin (counter = %d)\n", counter);
37 Pthread_create(&p1, NULL, mythread, "A");
38 Pthread_create(&p2, NULL, mythread, "B");
39
40 // join waits for the threads to finish
41 Pthread_join(p1, NULL);
42 Pthread_join(p2, NULL);
43 printf("main: done with both (counter = %d)\n", counter);
44 return 0;
45 }
Figure 26.3: Sharing Data: Oh Oh (t2)
26.2 Why It Gets Worse: Shared Data
The simple thread example we showed above was useful in showi ng
how threads are created and how they can run in different orders depend-
ing on how the scheduler decides to run them. What it doesn’t s how you,
though, is how threads interact when they access shared data .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 304

268 CONCURRENCY : A N INTRODUCTION
Let us imagine a simple example where two threads wish to upda te a
global shared variable. The code we’ll study is in Figure 26.3.
Here are a few notes about the code. First, as Stevens suggest s [SR05],
we wrap the thread creation and join routines to simply exit o n failure;
for a program as simple as this one, we want to at least notice a n error
occurred (if it did), but not do anything very smart about it ( e.g., just
exit). Thus, Pthread create() simply calls pthread create() and
makes sure the return code is 0; if it isn’t, Pthread create() just prints
a message and exits.
Second, instead of using two separate function bodies for th e worker
threads, we just use a single piece of code, and pass the threa d an argu-
ment (in this case, a string) so we can have each thread print a different
letter before its messages.
Finally , and most importantly , we can now look at what each worker is
trying to do: add a number to the shared variable counter, and do so 10
million times (1e7) in a loop. Thus, the desired ﬁnal result i s: 20,000,000.
We now compile and run the program, to see how it behaves. Some -
times, everything works how we might expect:
prompt> gcc -o main main.c -Wall -pthread
prompt> ./main
main: begin (counter = 0)
A: begin
B: begin
A: done
B: done
main: done with both (counter = 20000000)
Unfortunately , when we run this code, even on a single proces sor, we
don’t necessarily get the desired result. Sometimes, we get :
prompt> ./main
main: begin (counter = 0)
A: begin
B: begin
A: done
B: done
main: done with both (counter = 19345221)
Let’s try it one more time, just to see if we’ve gone crazy . Aft er all,
aren’t computers supposed to produce deterministic results, as you have
been taught?! Perhaps your professors have been lying to you ? (gasp)
prompt> ./main
main: begin (counter = 0)
A: begin
B: begin
A: done
B: done
main: done with both (counter = 19221041)
Not only is each run wrong, but also yields a different result! A big
question remains: why does this happen?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 305

CONCURRENCY : A N INTRODUCTION 269
TIP : K NOW AND USE YOUR TOOLS
You should always learn new tools that help you write, debug, and un-
derstand computer systems. Here, we use a neat tool called a disassem-
bler. When you run a disassembler on an executable, it shows you wha t
assembly instructions make up the program. For example, if w e wish to
understand the low-level code to update a counter (as in our e xample),
we run objdump (Linux) to see the assembly code:
prompt> objdump -d main
Doing so produces a long listing of all the instructions in th e program,
neatly labeled (particularly if you compiled with the -g ﬂag), which in-
cludes symbol information in the program. The objdump program is just
one of many tools you should learn how to use; a debugger like gdb,
memory proﬁlers like valgrind or purify, and of course the compiler
itself are others that you should spend time to learn more about; the better
you are at using your tools, the better systems you’ll be able to build.
26.3 The Heart of the Problem: Uncontrolled Scheduling
To understand why this happens, we must understand the code s e-
quence that the compiler generates for the update to counter. In this
case, we wish to simply add a number (1) to counter. Thus, the code
sequence for doing so might look something like this (in x86) ;
mov 0x8049a1c, %eax
add $0x1, %eax
mov %eax, 0x8049a1c
This example assumes that the variable counter is located at address
0x8049a1c. In this three-instruction sequence, the x86 mov instruction is
used ﬁrst to get the memory value at the address and put it into register
eax. Then, the add is performed, adding 1 (0x1) to the contents of the
eax register, and ﬁnally , the contents ofeax are stored back into memory
at the same address.
Let us imagine one of our two threads (Thread 1) enters this re gion of
code, and is thus about to increment counter by one. It loads the value
of counter (let’s say it’s 50 to begin with) into its register eax. Thus,
eax=50 for Thread 1. Then it adds one to the register; thus eax=51.
Now , something unfortunate happens: a timer interrupt goes off; thus,
the OS saves the state of the currently running thread (its PC , its registers
including eax, etc.) to the thread’s TCB.
Now something worse happens: Thread 2 is chosen to run, and it en-
ters this same piece of code. It also executes the ﬁrst instru ction, getting
the value of counter and putting it into its eax (remember: each thread
when running has its own private registers; the registers ar e virtualized
by the context-switch code that saves and restores them). Th e value of
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 306

270 CONCURRENCY : A N INTRODUCTION
(after instruction)
OS Thread 1 Thread 2 PC %eax counter
before critical section 100 0 50
mov 0x8049a1c, %eax 105 50 50
add $0x1, %eax 108 51 50
interrupt
save T1’s state
restore T2’s state 100 0 50
mov 0x8049a1c, %eax 105 50 50
add $0x1, %eax 108 51 50
mov %eax, 0x8049a1c 113 51 51
interrupt
save T2’s state
restore T1’s state 108 51 50
mov %eax, 0x8049a1c 113 51 51
Table 26.4: The Problem: Up Close and Personal
counter is still 50 at this point, and thus Thread 2 has eax=50. Let’s
then assume that Thread 2 executes the next two instructions , increment-
ing eax by 1 (thus eax=51), and then saving the contents of eax into
counter (address 0x8049a1c). Thus, the global variable counter now
has the value 51.
Finally , another context switch occurs, and Thread 1 resumes running.
Recall that it had just executed the mov and add, and is now about to
perform the ﬁnal mov instruction. Recall also that eax=51. Thus, the ﬁnal
mov instruction executes, and saves the value to memory; the cou nter is
set to 51 again.
Put simply , what has happened is this: the code to incrementcounter
has been run twice, but counter, which started at 50, is now only equal
to 51. A “correct” version of this program should have resulted in counter
equal to 52.
Here is a pictorial depiction of what happened and when in the ex-
ample above. Assume, for this depiction, that the above code is loaded at
address 100 in memory , like the following sequence (note forthose of you
used to nice, RISC-like instruction sets: x86 has variable- length instruc-
tions; the mov instructions here take up 5 bytes of memory , whereas the
add takes only 3):
100 mov 0x8049a1c, %eax
105 add $0x1, %eax
108 mov %eax, 0x8049a1c
With these assumptions, what happens is seen in Table
26.4. Assume
the counter starts at value 50, and trace through this exampl e to make
sure you understand what is going on.
What we have demonstrated here is called a race condition: the results
depend on the timing execution of the code. With some bad luck (i.e.,
context switches that occur at untimely points in the execut ion), we get
the wrong result. In fact, we may get a different result each t ime; thus,
instead of a nice deterministic computation (which we are used to from
computers), we call this result indeterminate, where it is not known what
the output will be and it is indeed likely to be different acro ss runs.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 307

CONCURRENCY : A N INTRODUCTION 271
Because multiple threads executing this code can result in a race con-
dition, we call this code a critical section . A critical section is a piece of
code that accesses a shared variable (or more generally , a shared resource)
and must not be concurrently executed by more than one thread .
What we really want for this code is what we call mutual exclusion .
This property guarantees that if one thread is executing within the critical
section, the others will be prevented from doing so.
Virtually all of these terms, by the way , were coined by Edsge r Dijk-
stra, who was a pioneer in the ﬁeld and indeed won the Turing Aw ard
because of this and other work; see his 1968 paper on “Coopera ting Se-
quential Processes” [D68] for an amazingly clear descripti on of the prob-
lem. We’ll be hearing more about Dijkstra in this section of t he book.
26.4 The Wish For Atomicity
One way to solve this problem would be to have more powerful in -
structions that, in a single step, did exactly whatever we ne eded done
and thus removed the possibility of an untimely interrupt. F or example,
what if we had a super instruction that looked like this?
memory-add 0x8049a1c, $0x1
Assume this instruction adds a value to a memory location, an d the
hardware guarantees that it executes atomically; when the instruction
executed, it would perform the update as desired. It could no t be inter-
rupted mid-instruction, because that is precisely the guarantee we receive
from the hardware: when an interrupt occurs, either the inst ruction has
not run at all, or it has run to completion; there is no in-betw een state.
Hardware can be a beautiful thing, no?
Atomically , in this context, means “as a unit”, which someti mes we
take as “all or none.” What we’d like is to execute the three in struction
sequence atomically:
mov 0x8049a1c, %eax
add $0x1, %eax
mov %eax, 0x8049a1c
As we said, if we had a single instruction to do this, we could j ust
issue that instruction and be done. But in the general case, w e won’t have
such an instruction. Imagine we were building a concurrent B -tree, and
wished to update it; would we really want the hardware to supp ort an
“atomic update of B-tree” instruction? Probably not, at lea st in a sane
instruction set.
Thus, what we will instead do is ask the hardware for a few usef ul
instructions upon which we can build a general set of what we c all syn-
chronization primitives. By using these hardware synchronization prim-
itives, in combination with some help from the operating sys tem, we will
be able to build multi-threaded code that accesses critical sections in a
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 308

272 CONCURRENCY : A N INTRODUCTION
ASIDE : KEY CONCURRENCY TERMS
CRITICAL SECTION , R ACE CONDITION ,
INDETERMINATE , MUTUAL EXCLUSION
These four terms are so central to concurrent code that we tho ught it
worth while to call them out explicitly . See some of Dijkstra ’s early work
[D65,D68] for more details.
• A critical section is a piece of code that accesses a shared resource,
usually a variable or data structure.
• A race condition arises if multiple threads of execution enter the
critical section at roughly the same time; both attempt to up date
the shared data structure, leading to a surprising (and perh aps un-
desirable) outcome.
• An indeterminate program consists of one or more race conditions;
the output of the program varies from run to run, depending on
which threads ran when. The outcome is thus not deterministic,
something we usually expect from computer systems.
• To avoid these problems, threads should use some kind of mutual
exclusion primitives; doing so guarantees that only a single thread
ever enters a critical section, thus avoiding races, and res ulting in
deterministic program outputs.
synchronized and controlled manner, and thus reliably prod uces the cor-
rect result despite the challenging nature of concurrent ex ecution. Pretty
awesome, right?
This is the problem we will study in this section of the book. I t is a
wonderful and hard problem, and should make your mind hurt (a bit).
If it doesn’t, then you don’t understand! Keep working until your head
hurts; you then know you’re headed in the right direction. At that point,
take a break; we don’t want your head hurting too much.
THE CRUX :
HOW TO PROVIDE SUPPORT FOR SYNCHRONIZATION
What support do we need from the hardware in order to build use -
ful synchronization primitives? What support do we need fro m the OS?
How can we build these primitives correctly and efﬁciently? How can
programs use them to get the desired results?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 309

CONCURRENCY : A N INTRODUCTION 273
26.5 One More Problem: Waiting For Another
This chapter has set up the problem of concurrency as if only o ne type
of interaction occurs between threads, that of accessing sh ared variables
and the need to support atomicity for critical sections. As i t turns out,
there is another common interaction that arises, where one t hread must
wait for another to complete some action before it continues . This inter-
action arises, for example, when a process performs a disk I/ O and is put
to sleep; when the I/O completes, the process needs to be rous ed from its
slumber so it can continue.
Thus, in the coming chapters, we’ll be not only studying how t o build
support for synchronization primitives to support atomici ty but also for
mechanisms to support this type of sleeping/waking interac tion that is
common in multi-threaded programs. If this doesn’t make sen se right
now , that is OK! It will soon enough, when you read the chapter on con-
dition variables . If it doesn’t by then, well, then it is less OK, and you
should read that chapter again (and again) until it does make sense.
26.6 Summary: Why in OS Class?
Before wrapping up, one question that you might have is: why a re we
studying this in OS class? “History” is the one-word answer; the OS was
the ﬁrst concurrent program, and many techniques were creat ed for use
within the OS. Later, with multi-threaded processes, application program-
mers also had to consider such things.
For example, imagine the case where there are two processes r unning.
Assume they both call write() to write to the ﬁle, and both wish to
append the data to the ﬁle (i.e., add the data to the end of the ﬁ le, thus in-
creasing its length). To do so, both must allocate a new block, record in the
inode of the ﬁle where this block lives, and change the size of the ﬁle to re-
ﬂect the new larger size (among other things; we’ll learn mor e about ﬁles
in the third part of the book). Because an interrupt may occur at any time,
the code that updates to these shared structures (e.g., a bit map for alloca-
tion, or the ﬁle’s inode) are critical sections; thus, OS des igners, from the
very beginning of the introduction of the interrupt, had to w orry about
how the OS updates internal structures. An untimely interru pt causes all
of the problems described above. Not surprisingly , page tab les, process
lists, ﬁle system structures, and virtually every kernel da ta structure has
to be carefully accessed, with the proper synchronization p rimitives, to
work correctly .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 310

274 CONCURRENCY : A N INTRODUCTION
TIP : U SE ATOMIC OPERATIONS
Atomic operations are one of the most powerful underlying te chniques
in building computer systems, from the computer architecture, to concur-
rent code (what we are studying here), to ﬁle systems (which w e’ll study
soon enough), database management systems, and even distri buted sys-
tems [L+93].
The idea behind making a series of actions atomic is simply expressed
with the phrase “all or nothing”; it should either appear as i f all of the ac-
tions you wish to group together occurred, or that none of them occurred,
with no in-between state visible. Sometimes, the grouping o f many ac-
tions into a single atomic action is called a transaction, an idea devel-
oped in great detail in the world of databases and transactio n processing
[GR92].
In our theme of exploring concurrency , we’ll be using synchr onization
primitives to turn short sequences of instructions into ato mic blocks of
execution, but the idea of atomicity is much bigger than that , as we will
see. For example, ﬁle systems use techniques such as journal ing or copy-
on-write in order to atomically transition their on-disk st ate, critical for
operating correctly in the face of system failures. If that d oesn’t make
sense, don’t worry – it will, in some future chapter.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 311

CONCURRENCY : A N INTRODUCTION 275
References
[D65] “Solution of a problem in concurrent programming cont rol”
E. W. Dijkstra
Communications of the ACM, 8(9):569, September 1965
Pointed to as the ﬁrst paper of Dijkstra’s where he outlines t he mutual exclusion problem and a solution.
The solution, however, is not widely used; advanced hardwar e and OS support is needed, as we will see
in the coming chapters.
[D68] “Cooperating sequential processes”
Edsger W. Dijkstra, 1968
Available: http://www.cs.utexas.edu/users/EWD/ewd01xx/EWD123.PDF
Dijkstra has an amazing number of his old papers, notes, and t houghts recorded (for posterity) on this
website at the last place he worked, the University of Texas. Much of his foundational work, however,
was done years earlier while he was at the Technische Hochshu le of Eindhoven (THE), including this
famous paper on “cooperating sequential processes”, which basically outlines all of the thinking that
has to go into writing multi-threaded programs. Dijkstra di scovered much of this while working on an
operating system named after his school: the “THE” operatin g system (said “T”, “H”, “E”, and not
like the word “the”).
[GR92] “Transaction Processing: Concepts and Techniques”
Jim Gray and Andreas Reuter
Morgan Kaufmann, September 1992
This book is the bible of transaction processing, written by one of the legends of the ﬁeld, Jim Gray. It is,
for this reason, also considered Jim Gray’s “brain dump”, in which he wrote down everything he knows
about how database management systems work. Sadly, Gray pas sed away tragically a few years back,
and many of us lost a friend and great mentor, including the co -authors of said book, who were lucky
enough to interact with Gray during their graduate school ye ars.
[L+93] “Atomic Transactions”
Nancy Lynch, Michael Merritt, William Weihl, Alan Fekete
Morgan Kaufmann, August 1993
A nice text on some of the theory and practice of atomic transa ctions for distributed systems. Perhaps a
bit formal for some, but lots of good material is found herein .
[SR05] “Advanced Programming in the U NIX Environment”
W. Richard Stevens and Stephen A. Rago
Addison-Wesley , 2005
As we’ve said many times, buy this book, and read it, in little chunks, preferably before going to bed.
This way, you will actually fall asleep more quickly; more im portantly, you learn a little more about
how to become a serious UNIX programmer.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 312

276 CONCURRENCY : A N INTRODUCTION
Homework
This program, x86.py, allows you to see how different thread inter-
leavings either cause or avoid race conditions. See the READ ME for de-
tails on how the program works and its basic inputs, then answ er the
questions below .
Questions
1. To start, let’s examine a simple program, “loop.s”. First , just look at
the program, and see if you can understand it: cat loop.s . Then,
run it with these arguments:
./x86.py -p loop.s -t 1 -i 100 -R dx
Tthis speciﬁes a single thread, an interrupt every 100 instr uctions,
and tracing of register %dx. Can you ﬁgure out what the value of
%dx will be during the run? Once you have, run the same above
and use the -c ﬂag to check your answers; note the answers, on
the left, show the value of the register (or memory value) after the
instruction on the right has run.
2. Now run the same code but with these ﬂags:
./x86.py -p loop.s -t 2 -i 100 -a dx=3,dx=3 -R dx
Tthis speciﬁes two threads, and initializes each %dx regist er to 3.
What values will %dx see? Run with the -c ﬂag to see the answers.
Does the presence of multiple threads affect anything about your
calculations? Is there a race condition in this code?
3. Now run the following:
./x86.py -p loop.s -t 2 -i 3 -r -a dx=3,dx=3 -R dx
This makes the interrupt interval quite small and random; us e dif-
ferent seeds with -s to see different interleavings. Does the fre-
quency of interruption change anything about this program?
4. Next we’ll examine a different program ( looping-race-nolock.s).
This program accesses a shared variable located at memory address
2000; we’ll call this variable x for simplicity . Run it with a single
thread and make sure you understand what it does, like this:
./x86.py -p looping-race-nolock.s -t 1 -M 2000
What value is found in x (i.e., at memory address 2000) throughout
the run? Use -c to check your answer.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 313

CONCURRENCY : A N INTRODUCTION 277
5. Now run with multiple iterations and threads:
./x86.py -p looping-race-nolock.s -t 2 -a bx=3 -M 2000
Do you understand why the code in each thread loops three time s?
What will the ﬁnal value of x be?
6. Now run with random interrupt intervals:
./x86.py -p looping-race-nolock.s -t 2 -M 2000 -i 4 -r -s 0
Then change the random seed, setting -s 1 , then -s 2 , etc. Can
you tell, just by looking at the thread interleaving, what th e ﬁnal
value of x will be? Does the exact location of the interrupt matter?
Where can it safely occur? Where does an interrupt cause trou ble?
In other words, where is the critical section exactly?
7. Now use a ﬁxed interrupt interval to explore the program fu rther.
Run:
./x86.py -p looping-race-nolock.s -a bx=1 -t 2 -M 2000 -i 1
See if you can guess what the ﬁnal value of the shared variable
x will be. What about when you change -i 2 , -i 3 , etc.? For
which interrupt intervals does the program give the “correc t” ﬁnal
answer?
8. Now run the same code for more loops (e.g., set -a bx=100 ). What
interrupt intervals, set with the -i ﬂag, lead to a “correct” outcome?
Which intervals lead to surprising results?
9. We’ll examine one last program in this homework ( wait-for-me.s).
Run the code like this:
./x86.py -p wait-for-me.s -a ax=1,ax=0 -R ax -M 2000
This sets the %ax register to 1 for thread 0, and 0 for thread 1, and
watches the value of %ax and memory location 2000 throughout
the run. How should the code behave? How is the value at locati on
2000 being used by the threads? What will its ﬁnal value be?
10. Now switch the inputs:
./x86.py -p wait-for-me.s -a ax=0,ax=1 -R ax -M 2000
How do the threads behave? What is thread 0 doing? How would
changing the interrupt interval (e.g., -i 1000 , or perhaps to use
random intervals) change the trace outcome? Is the program e fﬁ-
ciently using the CPU?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 315

27
Interlude: Thread API
This chapter brieﬂy covers the main portions of the thread AP I. Each part
will be explained further in the subsequent chapters, as we s how how
to use the API. More details can be found in various books and o nline
sources [B97, B+96, K+96]. We should note that the subsequen t chapters
introduce the concepts of locks and condition variables mor e slowly , with
many examples; this chapter is thus better used as a referenc e.
CRUX : H OW TO CREATE AND CONTROL THREADS
What interfaces should the OS present for thread creation and control?
How should these interfaces be designed to enable ease of use as well as
utility?
27.1 Thread Creation
The ﬁrst thing you have to be able to do to write a multi-thread ed
program is to create new threads, and thus some kind of thread creation
interface must exist. In POSIX, it is easy:
#include <pthread.h>
int
pthread_create( pthread_t * thread,
const pthread_attr_t * attr,
void * (*start_routine)(void*),
void * arg);
This declaration might look a little complex (particularly if you haven’t
used function pointers in C), but actually it’s not too bad. T here are
four arguments: thread, attr, start
routine, and arg. The ﬁrst,
thread, is a pointer to a structure of type pthread t; we’ll use this
structure to interact with this thread, and thus we need to pa ss it to
pthread create() in order to initialize it.
279

## Page 316

280 INTERLUDE : T HREAD API
The second argument, attr, is used to specify any attributes this thread
might have. Some examples include setting the stack size or p erhaps in-
formation about the scheduling priority of the thread. An at tribute is
initialized with a separate call to pthread attr init(); see the man-
ual page for details. However, in most cases, the defaults wi ll be ﬁne; in
this case, we will simply pass the value NULL in.
The third argument is the most complex, but is really just asking: which
function should this thread start running in? In C, we call th is a function
pointer, and this one tells us the following is expected: a function n ame
(start routine), which is passed a single argument of type void * (as
indicated in the parentheses after start routine), and which returns a
value of type void * (i.e., a void pointer).
If this routine instead required an integer argument, inste ad of a void
pointer, the declaration would look like this:
int pthread_create(..., // first two args are the same
void * (*start_routine)(int),
int arg);
If instead the routine took a void pointer as an argument, but returned
an integer, it would look like this:
int pthread_create(..., // first two args are the same
int ( *start_routine)(void *),
void * arg);
Finally , the fourth argument,arg, is exactly the argument to be passed
to the function where the thread begins execution. You might ask: why
do we need these void pointers? Well, the answer is quite simp le: having
a void pointer as an argument to the function start
routine allows us
to pass in any type of argument; having it as a return value allows the
thread to return any type of result.
Let’s look at an example in Figure 27.1. Here we just create a thread
that is passed two arguments, packaged into a single type we d eﬁne our-
selves (myarg t). The thread, once created, can simply cast its argument
to the type it expects and thus unpack the arguments as desire d.
And there it is! Once you create a thread, you really have anot her
live executing entity , complete with its own call stack, running within the
same address space as all the currently existing threads in the pr ogram.
The fun thus begins!
27.2 Thread Completion
The example above shows how to create a thread. However, what
happens if you want to wait for a thread to complete? You need t o do
something special in order to wait for completion; in partic ular, you must
call the routine pthread join().
int pthread_join(pthread_t thread, void **value_ptr);
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 317

INTERLUDE : T HREAD API 281
1 #include <pthread.h>
2
3 typedef struct __myarg_t {
4 int a;
5 int b;
6 } myarg_t;
7
8 void *mythread(void *arg) {
9 myarg_t *m = (myarg_t *) arg;
10 printf("%d %d\n", m->a, m->b);
11 return NULL;
12 }
13
14 int
15 main(int argc, char *argv[]) {
16 pthread_t p;
17 int rc;
18
19 myarg_t args;
20 args.a = 10;
21 args.b = 20;
22 rc = pthread_create(&p, NULL, mythread, &args);
23 ...
24 }
Figure 27.1: Creating a Thread
This routine takes only two arguments. The ﬁrst is of type pthread
t,
and is used to specify which thread to wait for. This value is e xactly what
you passed into the thread library during creation; if you he ld onto it,
you can now use it to wait for the thread to stop running.
The second argument is a pointer to the return value you expec t to get
back. Because the routine can return anything, it is deﬁned t o return a
pointer to void; because the pthread join() routine changes the value
of the passed in argument, you need to pass in a pointer to that value, not
just the value itself.
Let’s look at another example (Figure 27.2). In the code, a single thread
is again created, and passed a couple of arguments via the myarg t struc-
ture. To return values, the myret t type is used. Once the thread is
ﬁnished running, the main thread, which has been waiting ins ide of the
pthread join() routine1, then returns, and we can access the values
returned from the thread, namely whatever is in myret t.
A few things to note about this example. First, often times we don’t
have to do all of this painful packing and unpacking of argume nts. For
example, if we just create a thread with no arguments, we can p ass NULL
in as an argument when the thread is created. Similarly , we can pass NULL
into pthread join() if we don’t care about the return value.
Second, if we are just passing in a single value (e.g., an int) , we don’t
have to package it up as an argument. Figure 27.3 shows an example. In
1Note we use wrapper functions here; speciﬁcally , we call Mal loc(), Pthread join(), and
Pthread create(), which just call their similarly-named lower-cas e versions and make sure the
routines did not return anything unexpected.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 318

282 INTERLUDE : T HREAD API
1 #include <stdio.h>
2 #include <pthread.h>
3 #include <assert.h>
4 #include <stdlib.h>
5
6 typedef struct __myarg_t {
7 int a;
8 int b;
9 } myarg_t;
10
11 typedef struct __myret_t {
12 int x;
13 int y;
14 } myret_t;
15
16 void *mythread(void *arg) {
17 myarg_t *m = (myarg_t *) arg;
18 printf("%d %d\n", m->a, m->b);
19 myret_t *r = Malloc(sizeof(myret_t));
20 r->x = 1;
21 r->y = 2;
22 return (void *) r;
23 }
24
25 int
26 main(int argc, char *argv[]) {
27 int rc;
28 pthread_t p;
29 myret_t *m;
30
31 myarg_t args;
32 args.a = 10;
33 args.b = 20;
34 Pthread_create(&p, NULL, mythread, &args);
35 Pthread_join(p, (void **) &m);
36 printf("returned %d %d\n", m->x, m->y);
37 return 0;
38 }
Figure 27.2: Waiting for Thread Completion
this case, life is a bit simpler, as we don’t have to package ar guments and
return values inside of structures.
Third, we should note that one has to be extremely careful wit h how
values are returned from a thread. In particular, never retu rn a pointer
which refers to something allocated on the thread’s call sta ck. If you do,
what do you think will happen? (think about it!) Here is an exa mple of a
dangerous piece of code, modiﬁed from the example in Figure
27.2.
1 void *mythread(void *arg) {
2 myarg_t *m = (myarg_t *) arg;
3 printf("%d %d\n", m->a, m->b);
4 myret_t r; // ALLOCATED ON STACK: BAD!
5 r.x = 1;
6 r.y = 2;
7 return (void *) &r;
8 }
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 319

INTERLUDE : T HREAD API 283
void *mythread(void *arg) {
int m = (int) arg;
printf("%d\n", m);
return (void *) (arg + 1);
}
int main(int argc, char *argv[]) {
pthread_t p;
int rc, m;
Pthread_create(&p, NULL, mythread, (void *) 100);
Pthread_join(p, (void **) &m);
printf("returned %d\n", m);
return 0;
}
Figure 27.3: Simpler Argument Passing to a Thread
In this case, the variable r is allocated on the stack of mythread. How-
ever, when it returns, the value is automatically deallocat ed (that’s why
the stack is so easy to use, after all!), and thus, passing bac k a pointer to
a now deallocated variable will lead to all sorts of bad resul ts. Certainly ,
when you print out the values you think you returned, you’ll p robably
(but not necessarily!) be surprised. Try it and ﬁnd out for yo urself2!
Finally , you might notice that the use ofpthread
create() to create
a thread, followed by an immediate call to pthread join(), is a pretty
strange way to create a thread. In fact, there is an easier way to accom-
plish this exact task; it’s called a procedure call. Clearly , we’ll usually be
creating more than just one thread and waiting for it to compl ete, other-
wise there is not much purpose to using threads at all.
We should note that not all code that is multi-threaded uses t he join
routine. For example, a multi-threaded web server might create a number
of worker threads, and then use the main thread to accept requ ests and
pass them to the workers, indeﬁnitely . Such long-lived prog rams thus
may not need to join. However, a parallel program that create s threads
to execute a particular task (in parallel) will likely use jo in to make sure
all such work completes before exiting or moving onto the nex t stage of
computation.
27.3 Locks
Beyond thread creation and join, probably the next most usef ul set of
functions provided by the POSIX threads library are those fo r providing
mutual exclusion to a critical section via locks. The most basic pair of
routines to use for this purpose is provided by this pair of ro utines:
int pthread_mutex_lock(pthread_mutex_t *mutex);
int pthread_mutex_unlock(pthread_mutex_t *mutex);
2Fortunately the compiler gcc will likely complain when you write code like this, which
is yet another reason to pay attention to compiler warnings.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 320

284 INTERLUDE : T HREAD API
The routines should be easy to understand and use. When you ha ve a
region of code you realize is a critical section, and thus needs to be pro-
tected by locks in order to operate as desired. You can probab ly imagine
what the code looks like:
pthread_mutex_t lock;
pthread_mutex_lock(&lock);
x = x + 1; // or whatever your critical section is
pthread_mutex_unlock(&lock);
The intent of the code is as follows: if no other thread holds t he lock
when pthread
mutex lock() is called, the thread will acquire the lock
and enter the critical section. If another thread does indee d hold the lock,
the thread trying to grab the lock will not return from the cal l until it has
acquired the lock (implying that the thread holding the lock has released
it via the unlock call). Of course, many threads may be stuck w aiting
inside the lock acquisition function at a given time; only th e thread with
the lock acquired, however, should call unlock.
Unfortunately , this code is broken, in two important ways. T he ﬁrst
problem is a lack of proper initialization . All locks must be properly
initialized in order to guarantee that they have the correct values to begin
with and thus work as desired when lock and unlock are called.
With POSIX threads, there are two ways to initialize locks. O ne way
to do this is to use PTHREAD MUTEX INITIALIZER, as follows:
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
Doing so sets the lock to the default values and thus makes the lock
usable. The dynamic way to do it (i.e., at run time) is to make a call to
pthread mutex init(), as follows:
int rc = pthread_mutex_init(&lock, NULL);
assert(rc == 0); // always check success!
The ﬁrst argument to this routine is the address of the lock itself, whereas
the second is an optional set of attributes. Read more about t he attributes
yourself; passing NULL in simply uses the defaults. Either way works, but
we usually use the dynamic (latter) method. Note that a corre sponding
call to pthread
cond destroy() should also be made, when you are
done with the lock; see the manual page for all of details.
The second problem with the code above is that it fails to chec k errors
code when calling lock and unlock. Just like virtually any li brary rou-
tine you call in a U NIX system, these routines can also fail! If your code
doesn’t properly check error codes, the failure will happen silently , which
in this case could allow multiple threads into a critical section. Minimally ,
use wrappers, which assert that the routine succeeded (e.g. , as in Fig-
ure 27.4); more sophisticated (non-toy) programs, which can’t simp ly exit
when something goes wrong, should check for failure and do so mething
appropriate when the lock or unlock does not succeed.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

