# Document: operating_systems_three_easy_pieces (Pages 201 to 240)

## Page 201

FREE -S PACE MANAGEMENT 165
The ﬁrst-ﬁt strategy , in this example, does the same thing as worst-ﬁt,
also ﬁnding the ﬁrst free block that can satisfy the request. The difference
is in the search cost; both best-ﬁt and worst-ﬁt look through the entire list;
ﬁrst-ﬁt only examines free chunks until it ﬁnds one that ﬁts, thus reducing
search cost.
These examples just scratch the surface of allocation polic ies. More
detailed analysis with real workloads and more complex allo cator behav-
iors (e.g., coalescing) are required for a deeper understan ding. Perhaps
something for a homework section, you say?
17.4 Other Approaches
Beyond the basic approaches described above, there have bee n a host
of suggested techniques and algorithms to improve memory al location in
some way . We list a few of them here for your consideration (i.e., to make
you think about a little more than just best-ﬁt allocation).
Segregated Lists
One interesting approach that has been around for some time i s the use
of segregated lists . The basic idea is simple: if a particular application
has one (or a few) popular-sized request that it makes, keep a separate
list just to manage objects of that size; all other requests a re forwarded to
a more general memory allocator.
The beneﬁts of such an approach are obvious. By having a chunk of
memory dedicated for one particular size of requests, fragm entation is
much less of a concern; moreover, allocation and free reques ts can be
served quite quickly when they are of the right size, as no com plicated
search of a list is required.
Just like any good idea, this approach introduces new compli cations
into a system as well. For example, how much memory should one ded-
icate to the pool of memory that serves specialized requests of a given
size, as opposed to the general pool? One particular allocat or, the slab
allocator by uber-engineer Jeff Bonwick (which was designed for use in
the Solaris kernel), handles this issue in a rather nice way [ B94].
Speciﬁcally , when the kernel boots up, it allocates a number of object
caches for kernel objects that are likely to be requested frequently (such as
locks, ﬁle-system inodes, etc.); the object caches thus are each segregated
free lists of a given size and serve memory allocation and fre e requests
quickly . When a given cache is running low on free space, it re quests
some slabs of memory from a more general memory allocator (the to-
tal amount requested being a multiple of the page size and the object in
question). Conversely , when the reference counts of the obj ects within
a given slab all go to zero, the general allocator can reclaim them from
the specialized allocator, which is often done when the VM sy stem needs
more memory .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 202

166 FREE -S PACE MANAGEMENT
ASIDE : GREAT ENGINEERS ARE REALLY GREAT
Engineers like Jeff Bonwick (who not only wrote the slab allo cator men-
tioned herein but also was the lead of an amazing ﬁle system, Z FS) are
the heart of Silicon Valley . Behind almost any great product or technol-
ogy is a human (or small group of humans) who are way above aver age
in their talents, abilities, and dedication. As Mark Zucker berg (of Face-
book) says: “Someone who is exceptional in their role is not j ust a little
better than someone who is pretty good. They are 100 times bet ter.” This
is why , still today , one or two people can start a company that changes
the face of the world forever (think Google, Apple, or Facebo ok). Work
hard and you might become such a “100x” person as well. Failin g that,
work with such a person; you’ll learn more in day than most learn in a
month. Failing that, feel sad.
The slab allocator also goes beyond most segregated list app roaches
by keeping free objects on the lists in a pre-initialized sta te. Bonwick
shows that initialization and destruction of data structur es is costly [B94];
by keeping freed objects in a particular list in their initia lized state, the
slab allocator thus avoids frequent initialization and des truction cycles
per object and thus lowers overheads noticeably .
Buddy Allocation
Because coalescing is critical for an allocator, some appro aches have been
designed around making coalescing simple. One good example is found
in the binary buddy allocator [K65].
In such a system, free memory is ﬁrst conceptually thought of as one
big space of size 2N . When a request for memory is made, the search for
free space recursively divides free space by two until a bloc k that is big
enough to accommodate the request is found (and a further spl it into two
would result in a space that is too small). At this point, the r equested
block is returned to the user. Here is an example of a 64KB free space
getting divided in the search for a 7KB block:
64 KB
32 KB 32 KB
16 KB 16 KB
8 KB 8 KB
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 203

FREE -S PACE MANAGEMENT 167
In the example, the leftmost 8KB block is allocated (as indic ated by the
darker shade of gray) and returned to the user; note that this scheme can
suffer from internal fragmentation , as you are only allowed to give out
power-of-two-sized blocks.
The beauty of buddy allocation is found in what happens when t hat
block is freed. When returning the 8KB block to the free list, the allocator
checks whether the “buddy” 8KB is free; if so, it coalesces th e two blocks
into a 16KB block. The allocator then checks if the buddy of th e 16KB
block is still free; if so, it coalesces those two blocks. Thi s recursive coa-
lescing process continues up the tree, either restoring the entire free space
or stopping when a buddy is found to be in use.
The reason buddy allocation works so well is that it is simple to de-
termine the buddy of a particular block. How , you ask? Think a bout the
addresses of the blocks in the free space above. If you think c arefully
enough, you’ll see that the address of each buddy pair only di ffers by
a single bit; which bit is determined by the level in the buddy tree. And
thus you have a basic idea of how binary buddy allocation schemes work.
For more detail, as always, see the Wilson survey [W+95].
Other Ideas
One major problem with many of the approaches described abov e is their
lack of scaling. Speciﬁcally , searching lists can be quite slow . Thus,
advanced allocators use more complex data structures to add ress these
costs, trading simplicity for performance. Examples inclu de balanced bi-
nary trees, splay trees, or partially-ordered trees [W+95] .
Given that modern systems often have multiple processors an d run
multi-threaded workloads (something you’ll learn about in great detail
in the section of the book on Concurrency), it is not surprisi ng that a lot
of effort has been spent making allocators work well on multi processor-
based systems. Two wonderful examples are found in Berger et al. [B+00]
and Evans [E06]; check them out for the details.
These are but two of the thousands of ideas people have had ove r time
about memory allocators. Read on your own if you are curious.
17.5 Summary
In this chapter, we’ve discussed the most rudimentary forms of mem-
ory allocators. Such allocators exist everywhere, linked i nto every C pro-
gram you write, as well as in the underlying OS which is managi ng mem-
ory for its own data structures. As with many systems, there a re many
trade-offs to be made in building such a system, and the more y ou know
about the exact workload presented to an allocator, the moreyou could do
to tune it to work better for that workload. Making a fast, spa ce-efﬁcient,
scalable allocator that works well for a broad range of workl oads remains
an on-going challenge in modern computer systems.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 204

168 FREE -S PACE MANAGEMENT
References
[B+00] “Hoard: A Scalable Memory Allocator for Multithread ed Applications”
Emery D. Berger, Kathryn S. McKinley , Robert D. Blumofe, and Paul R. Wilson
ASPLOS-IX, November 2000
Berger and company’s excellent allocator for multiprocess or systems. Beyond just being a fun paper,
also used in practice!
[B94] “The Slab Allocator: An Object-Caching Kernel Memory Allocator”
Jeff Bonwick
USENIX ’94
A cool paper about how to build an allocator for an operating s ystem kernel, and a great example of how
to specialize for particular common object sizes.
[E06] “A Scalable Concurrent malloc(3) Implementation for FreeBSD”
Jason Evans
http://people.freebsd.org/˜jasone/jemalloc/bsdcan2006/jemalloc.pdf
April 2006
A detailed look at how to build a real modern allocator for use in multiprocessors. The “jemalloc”
allocator is in widespread use today, within FreeBSD, NetBS D, Mozilla Firefox, and within Facebook.
[K65] “A Fast Storage Allocator”
Kenneth C. Knowlton
Communications of the ACM, V olume 8, Number 10, October 1965
The common reference for buddy allocation. Random strange f act: Knuth gives credit for the idea to not
to Knowlton but to Harry Markowitz, a Nobel-prize winning ec onomist. Another strange fact: Knuth
communicates all of his emails via a secretary; he doesn’t se nd email himself, rather he tells his secretary
what email to send and then the secretary does the work of emai ling. Last Knuth fact: he created TeX,
the tool used to typeset this book. It is an amazing piece of so ftware4.
[W+95] “Dynamic Storage Allocation: A Survey and Critical R eview”
Paul R. Wilson, Mark S. Johnstone, Michael Neely , David Boles
International Workshop on Memory Management
Kinross, Scotland, September 1995
An excellent and far-reaching survey of many facets of memor y allocation. Far too much detail to go
into in this tiny chapter!
4Actually we use LaTeX, which is based on Lamport’s additions to TeX, but close enough.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 205

18
Paging: Introduction
Remember our goal: to virtualize memory . Segmentation (a ge neraliza-
tion of dynamic relocation) helped us do this, but has some pr oblems; in
particular, managing free space becomes quite a pain as memory becomes
fragmented and segmentation is not as ﬂexible as we might lik e. Is there
a better solution?
THE CRUX :
HOW TO VIRTUALIZE MEMORY WITHOUT SEGMENTS
How can we virtualize memory in a way as to avoid the problems o f
segmentation? What are the basic techniques? How do we make t hose
techniques work well?
Thus comes along the idea of paging, which goes back to the earliest
of computer systems, namely the Atlas [KE+62,L78]. Instead of splitting
up our address space into three logical segments (each of var iable size),
we split up our address space into ﬁxed-sized units we call a page. Here
in Figure 18.1 an example of a tiny address space, only 64 bytes total in
size, with 16 byte pages (real address spaces are much bigger , of course,
commonly 32 bits and thus 4-GB of address space, or even 64 bit s). We’ll
use tiny examples to make them easier to digest (at ﬁrst).
64
48
32
16
0
(page 3)
(page 2)
(page 1)
(page 0 of the address space)
Figure 18.1: A Simple 64-byte Address Space
169

## Page 206

170 PAGING : I NTRODUCTION
128
112
96
80
64
48
32
16
0
page frame 7
page frame 6
page frame 5
page frame 4
page frame 3
page frame 2
page frame 1
page frame 0 of physical memoryreserved for OS
(unused)
page 3 of AS
page 0 of AS
(unused)
page 2 of AS
(unused)
page 1 of AS
Figure 18.2: 64-Byte Address Space Placed In Physical Memory
Thus, we have an address space that is split into four pages (0 through
3). With paging, physical memory is also split into some numb er of pages
as well; we sometimes will call each page of physical memory a page
frame. For an example, let’s examine Figure 18.2.
Paging, as we will see, has a number of advantages over our pre vious
approaches. Probably the most important improvement will b e ﬂexibility:
with a fully-developed paging approach, the system will be a ble to sup-
port the abstraction of an address space effectively , regardless of how the
processes uses the address space; we won’t, for example, hav e to make
assumptions about how the heap and stack grow and how they are used.
Another advantage is the simplicity of free-space management that pag-
ing affords. For example, when the OS wishes to place our tiny 64-byte
address space from above into our 8-page physical memory , it simply
ﬁnds four free pages; perhaps the OS keeps a free list of all free pages for
this, and just grabs the ﬁrst four free pages off of this list. In the exam-
ple above, the OS has placed virtual page 0 of the address spac e (AS) in
physical page 3, virtual page 1 of the AS on physical page 7, pa ge 2 on
page 5, and page 3 on page 2.
To record where each virtual page of the address space is plac ed in
physical memory , the operating system keeps a per-process data structure
known as a page table. The major role of the page table is to store address
translations for each of the virtual pages of the address space, thus letting
us know where in physical memory they live. For our simple exa mple
above (Figure 18.2), the page table would thus have the following entries:
(Virtual Page 0 → Physical Frame 3), (VP 1 → PF 7), (VP 2 → PF 5), and
(VP 3 → PF 2).
It is important to remember that this page table is a per-process data
structure (most page table structures we discuss are per-pr ocess struc-
tures; an exception we’ll touch on is the inverted page table ). If another
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 207

PAGING : I NTRODUCTION 171
process were to run in our example above, the OS would have to m anage
a different page table for it, as its virtual pages obviously map to different
physical pages (modulo any sharing going on).
Now , we know enough to perform an address-translation examp le.
Let’s imagine the process with that tiny address space (64 by tes) is per-
forming a memory access:
movl <virtual address>, %eax
Speciﬁcally , let’s pay attention to the explicit load of thedata at <virtual
address> into the register eax (and thus ignore the instruction fetch that
must have happened prior).
To translate this virtual address that the process generated, we have to
ﬁrst split it into two components: the virtual page number (VPN) , and
the offset within the page. For this example, because the virtual addre ss
space of the process is 64 bytes, we need 6 bits total for our virtual address
(26 = 64 ). Thus, our virtual address:
Va5 Va4 Va3 Va2 Va1 Va0
where Va5 is the highest-order bit of the virtual address, an d Va0 the
lowest order bit. Because we know the page size (16 bytes), we can further
divide the virtual address as follows:
Va5 Va4 Va3 Va2 Va1 Va0
VPN offset
The page size is 16 bytes in a 64-byte address space; thus we ne ed to
be able to select 4 pages, and the top 2 bits of the address do ju st that.
Thus, we have a 2-bit virtual page number (VPN). The remainin g bits tell
us which byte of the page we are interested in, 4 bits in this ca se; we call
this the offset.
When a process generates a virtual address, the OS and hardwa re
must combine to translate it into a meaningful physical addr ess. For ex-
ample, let us assume the load above was to virtual address 21:
movl 21, %eax
Turning “21” into binary form, we get “010101”, and thus we ca n ex-
amine this virtual address and see how it breaks down into a vi rtual page
number (VPN) and offset:
0 1 0 1 0 1
VPN offset
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 208

172 PAGING : I NTRODUCTION
0 1 0 1 0 1
VPN offset
1 1 1 0 1 0 1
Address
Translation
PFN offset
Virtual
Address
Physical
Address
Figure 18.3: The Address T ranslation Process
Thus, the virtual address “21” is on the 5th (“0101”th) byte o f vir-
tual page “01” (or 1). With our virtual page number, we can now index
our page table and ﬁnd which physical page that virtual page 1 resides
within. In the page table above the physical page number (PPN ) (a.k.a.
physical frame number or PFN) is 7 (binary 111). Thus, we can t ranslate
this virtual address by replacing the VPN with the PFN and the n issue
the load to physical memory (Figure 18.3).
Note the offset stays the same (i.e., it is not translated), b ecause the
offset just tells us which byte within the page we want. Our ﬁnal physical
address is 1110101 (117 in decimal), and is exactly where we w ant our
load to fetch data from (Figure 18.2).
18.1 Where Are Page Tables Stored?
Page tables can get awfully large, much bigger than the small segment
table or base/bounds pair we have discussed previously . For example,
imagine a typical 32-bit address space, with 4-KB pages. Thi s virtual ad-
dress splits into a 20-bit VPN and 12-bit offset (recall that 10 bits would
be needed for a 1-KB page size, and just add two more to get to 4 K B).
A 20-bit VPN implies that there are 220 translations that the OS would
have to manage for each process (that’s roughly a million); a ssuming we
need 4 bytes per page table entry (PTE) to hold the physical translation
plus any other useful stuff, we get an immense 4MB of memory ne eded
for each page table! That is pretty big. Now imagine there are 100 pro-
cesses running: this means the OS would need 400MB of memory j ust for
all those address translations! Even in the modern era, wher e machines
have gigabytes of memory , it seems a little crazy to use a larg e chunk of
if just for translations, no?
Because page tables are so big, we don’t keep any special on-c hip hard-
ware in the MMU to store the page table of the currently-running process.
Instead, we store the page table for each process in memory somewhere.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 209

PAGING : I NTRODUCTION 173
128
112
96
80
64
48
32
16
0
page frame 7
page frame 6
page frame 5
page frame 4
page frame 3
page frame 2
page frame 1
page frame 0 of physical memory
(unused)
page 3 of AS
page 0 of AS
(unused)
page 2 of AS
(unused)
page 1 of AS
page table:
3 7 5 2
Figure 18.4: Example: Page T able in Kernel Physical Memory
Let’s assume for now that the page tables live in physical mem ory that
the OS manages. In Figure 18.4 is a picture of what that might look like.
18.2 What’s Actually In The Page Table?
Let’s talk a little about page table organization. The page t able is just a
data structure that is used to map virtual addresses (or really , virtual page
numbers) to physical addresses (physical page numbers). Th us, any data
structure could work. The simplest form is called a linear page table ,
which is just an array . The OS indexes the array by the VPN, and looks up
the page-table entry (PTE) at that index in order to ﬁnd the de sired PFN.
For now , we will assume this simple linear structure; in late r chapters,
we will make use of more advanced data structures to help solv e some
problems with paging.
As for the contents of each PTE, we have a number of different b its
in there worth understanding at some level. A valid bit is common to
indicate whether the particular translation is valid; for e xample, when
a program starts running, it will have code and heap at one end of its
address space, and the stack at the other. All the unused space in-between
will be marked invalid, and if the process tries to access such memory , it
will generate a trap to the OS which will likely terminate the process.
Thus, the valid bit is crucial for supporting a sparse addres s space; by
simply marking all the unused pages in the address space inva lid, we
remove the need to allocate physical frames for those pages and thus save
a great deal of memory .
We also might have protection bits, indicating whether the page could
be read from, written to, or executed from. Again, accessing a page in a
way not allowed by these bits will generate a trap to the OS.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 210

174 PAGING : I NTRODUCTION
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
PFN
G
PAT
D
A
PCD
PWT
U/S
R/W
P
Figure 18.5: An x86 Page T able Entry (PTE)
There are a couple of other bits that are important but we won’ t talk
about much for now . Apresent bit indicates whether this page is in phys-
ical memory or on disk (swapped out); we will understand this in more
detail when we study how to move parts of the address space to d isk
and back in order to support address spaces that are larger th an physical
memory and allow for the pages of processes that aren’t activ ely being
run to be swapped out. A dirty bit is also common, indicating whether
the page has been modiﬁed since it was brought into memory .
A reference bit (a.k.a. accessed bit) is sometimes used to track whether
a page has been accessed, and is useful in determining which p ages are
popular and thus should be kept in memory; such knowledge is c ritical
during page replacement, a topic we will study in great detail in subse-
quent chapters.
Figure 18.5 shows an example page table entry from the x86 architec-
ture [I09]. It contains a present bit (P); a read/write bit (R /W) which
determines if writes are allowed to this page; a user/superv isor bit (U/S)
which determines if user-mode processes can access the page ; a few bits
(PWT, PCD, P AT, and G) that determine how hardware caching works for
these pages; an accessed bit (A) and a dirty bit (D); and ﬁnall y , the page
frame number (PFN) itself.
Read the Intel Architecture Manuals [I09] for more details o n x86 pag-
ing support. Be forewarned, however; reading manuals such a s these,
while quite informative (and certainly necessary for those who write code
to use such page tables in the OS), can be challenging at ﬁrst. A little pa-
tience, and a lot of desire, is required.
18.3 Paging: Also Too Slow
With page tables in memory , we already know that they might be too
big. Turns out they can slow things down too. For example, tak e our
simple instruction:
movl 21, %eax
Again, let’s just examine the explicit reference to address 21 and not
worry about the instruction fetch. In this example, we will a ssume the
hardware performs the translation for us. To fetch the desir ed data, the
system must ﬁrst translate the virtual address (21) into the correct physi-
cal address (117). Thus, before issuing the load to address 1 17, the system
must ﬁrst fetch the proper page table entry from the process’ s page ta-
ble, perform the translation, and then ﬁnally get the desire d data from
physical memory .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 211

PAGING : I NTRODUCTION 175
To do so, the hardware must know where the page table is for the
currently-running process. Let’s assume for now that a sing le page-table
base register contains the physical address of the starting location of th e
page table. To ﬁnd the location of the desired PTE, the hardwa re will thus
perform the following functions:
VPN = (VirtualAddress & VPN_MASK) >> SHIFT
PTEAddr = PageTableBaseRegister + (VPN * sizeof(PTE))
In our example, VPN
MASK would be set to 0x30 (hex 30, or binary
110000) which picks out the VPN bits from the full virtual address; SHIFT
is set to 4 (the number of bits in the offset), such that we move the VPN
bits down to form the correct integer virtual page number. Fo r exam-
ple, with virtual address 21 (010101), and masking turns thi s value into
010000; the shift turns it into 01, or virtual page 1, as desir ed. We then use
this value as an index into the array of PTEs pointed to by the p age table
base register.
Once this physical address is known, the hardware can fetch t he PTE
from memory , extract the PFN, and concatenate it with the off set from
the virtual address to form the desired physical address. Sp eciﬁcally , you
can think of the PFN being left-shifted by SHIFT, and then logically OR’d
with the offset to form the ﬁnal address as follows:
offset = VirtualAddress & OFFSET_MASK
PhysAddr = (PFN << SHIFT) | offset
1 // Extract the VPN from the virtual address
2 VPN = (VirtualAddress & VPN_MASK) >> SHIFT
3
4 // Form the address of the page-table entry (PTE)
5 PTEAddr = PTBR + (VPN * sizeof(PTE))
6
7 // Fetch the PTE
8 PTE = AccessMemory(PTEAddr)
9
10 // Check if process can access the page
11 if (PTE.Valid == False)
12 RaiseException(SEGMENTATION_FAULT)
13 else if (CanAccess(PTE.ProtectBits) == False)
14 RaiseException(PROTECTION_FAULT)
15 else
16 // Access is OK: form physical address and fetch it
17 offset = VirtualAddress & OFFSET_MASK
18 PhysAddr = (PTE.PFN << PFN_SHIFT) | offset
19 Register = AccessMemory(PhysAddr)
Figure 18.6: Accessing Memory With Paging
Finally , the hardware can fetch the desired data from memory and put
it into register eax. The program has now succeeded at loading a value
from memory!
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 212

176 PAGING : I NTRODUCTION
ASIDE : DATA STRUCTURE – T HE PAGE TABLE
One of the most important data structures in the memory manag ement
subsystem of a modern OS is the page table . In general, a page table
stores virtual-to-physical address translations , thus letting the system
know where each page of an address space actually resides in p hysical
memory . Because each address space requires such translati ons, in gen-
eral there is one page table per process in the system. The exa ct structure
of the page table is either determined by the hardware (older systems) or
can be more ﬂexibly managed by the OS (modern systems).
To summarize, we now describe the initial protocol for what h appens
on each memory reference. Figure 18.6 shows the basic approach. For
every memory reference (whether an instruction fetch or an e xplicit load
or store), paging requires us to perform one extra memory ref erence in
order to ﬁrst fetch the translation from the page table. That is a lot of
work! Extra memory references are costly , and in this case wi ll likely
slow down the process by a factor of two or more.
And now you can hopefully see that there are two real problems that
we must solve. Without careful design of both hardware and so ftware,
page tables will cause the system to run too slowly , as well as take up
too much memory . While seemingly a great solution for our mem ory
virtualization needs, these two crucial problems must ﬁrst be overcome.
18.4 A Memory Trace
Before closing, we now trace through a simple memory access e xam-
ple to demonstrate all of the resulting memory accesses that occur when
using paging. The code snippet (in C, in a ﬁle called array.c) that are
interested in is as follows:
int array[1000];
...
for (i = 0; i < 1000; i++)
array[i] = 0;
We could then compile array.c and run it with the following com-
mands:
prompt> gcc -o array array.c -Wall -O
prompt> ./array
Of course, to truly understand what memory accesses this cod e snip-
pet (which simply initializes an array) will make, we’ll hav e to know (or
assume) a few more things. First, we’ll have to disassemble the result-
ing binary (using objdump on Linux, or otool on a Mac) to see what
assembly instructions are used to initialize the array in a l oop. Here it the
resulting assembly code:
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 213

PAGING : I NTRODUCTION 177
0x1024 movl $0x0,(%edi,%eax,4)
0x1028 incl %eax
0x102c cmpl $0x03e8,%eax
0x1030 jne 0x1024
The code, if you know a little x86, is actually quite easy to understand.
The ﬁrst instruction moves the value zero (shown as $0x0) into the vir-
tual memory address of the location of the array; this address is computed
by taking the contents of %edi and adding %eax multiplied by four to it.
Thus, %edi holds the base address of the array , whereas %eax holds the
array index (i); we multiply by four because the array is an array of inte-
gers, each size four bytes (note we are cheating a little bit h ere, assuming
each instruction is four bytes in size for simplicity; in act uality , x86 in-
structions are variable-sized).
The second instruction increments the array index held in %eax, and
the third instruction compares the contents of that registe r to the hex
value 0x03e8, or decimal 1000. If the comparison shows that that two
values are not yet equal (which is what the jne instruction tests), the
fourth instruction jumps back to the top of the loop.
To understand which memory accesses this instruction sequence makes
(at both the virtual and physical levels), we’ll have assume something
about where in virtual memory the code snippet and array are f ound, as
well as the contents and location of the page table.
For this example, we assume a virtual address space of size 64 KB
(unrealistically small). We also assume a page size of 1 KB.
All we need to know now are the contents of the page table, and i ts
location in physical memory . Let’s assume we have a linear (a rray-based)
page table and that it is located at physical address 1 KB (102 4).
As for its contents, there are just a few virtual pages we need to worry
about having mapped for this example. First, there is the vir tual page the
code lives on. Because the page size is 1 KB, virtual address 1 024 resides
on the the second page of the virtual address space (VPN=1, as VPN=0 is
the ﬁrst page). Let’s assume this virtual page maps to physic al frame 4
(VPN 1 → PFN 4).
Next, there is the array itself. Its size is 4000 bytes (1000 i ntegers), and
it lives at virtual addresses 40000 through 44000 (not inclu ding the last
byte). The virtual pages for this decimal range is VPN=39 ... VPN=42.
Thus, we need mappings for these pages. Let’s assume these vi rtual-to-
physical mappings for the example: (VPN 39 → PFN 7), (VPN 40 → PFN 8),
(VPN 41 → PFN 9), (VPN 42 → PFN 10).
We are now ready to trace the memory references of the program .
When it runs, each instruction fetch will generate two memory references:
one to the page table to ﬁnd the physical frame that the instruction resides
within, and one to the instruction itself to fetch it to the CP U for process-
ing. In addition, there is one explicit memory reference in t he form of
the mov instruction; this adds another page table access ﬁrst (to tr anslate
the array virtual address to the correct physical one) and th en the array
access itself.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 214

178 PAGING : I NTRODUCTION
0 10 20 30 40 50
1024
1074
1124
Memory Access
Code (VA)
40000
40050
40100
Array (VA)
1024
1074
1124
1174
1224
Page Table (PA)
4096
4146
4196
Code (PA)
7232
7282
7132
Array (PA)
mov
inc
cmp
jne
mov
PageTable[1]
PageTable[39]
Figure 18.7: A Virtual (And Physical) Memory T race
The entire process, for the ﬁrst ﬁve loop iterations, is depi cted in Fig-
ure 18.7. The bottom most graph shows the instruction memory refer-
ences on the y-axis in black (with virtual addresses on the le ft, and the
actual physical addresses on the right); the middle graph sh ows array
accesses in dark gray (again with virtual on left and physica l on right); ﬁ-
nally , the topmost graph shows page table memory accesses in light gray
(just physical, as the page table in this example resides in p hysical mem-
ory). The x-axis, for the entire trace, shows memory accesse s across the
ﬁrst ﬁve iterations of the loop (there are 10 memory accesses per loop,
which includes four instruction fetches, one explicit upda te of memory ,
and ﬁve page table accesses to translate those four fetches and one explicit
update).
See if you can make sense of the patterns that show up in this vi su-
alization. In particular, what will change as the loop conti nues to run
beyond these ﬁrst ﬁve iterations? Which new memory location s will be
accessed? Can you ﬁgure it out?
This has just been the simplest of examples (only a few lines of C code),
and yet you might already be able to sense the complexity of un derstand-
ing the actual memory behavior of real applications. Don’t w orry: it deﬁ-
nitely gets worse, because the mechanisms we are about to introduce only
complicate this already complex machinery . Sorry!
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 215

PAGING : I NTRODUCTION 179
18.5 Summary
We have introduced the concept of paging as a solution to our chal-
lenge of virtualizing memory . Paging has many advantages ov er previ-
ous approaches (such as segmentation). First, it does not le ad to external
fragmentation, as paging (by design) divides memory into ﬁx ed-sized
units. Second, it is quite ﬂexible, enabling the sparse use o f virtual ad-
dress spaces.
However, implementing paging support without care will lea d to a
slower machine (with many extra memory accesses to access th e page
table) as well as memory waste (with memory ﬁlled with page ta bles in-
stead of useful application data). We’ll thus have to think a little harder
to come up with a paging system that not only works, but works w ell.
The next two chapters, fortunately , will show us how to do so.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 216

180 PAGING : I NTRODUCTION
References
[KE+62] “One-level Storage System”
T. Kilburn, and D.B.G. Edwards and M.J. Lanigan and F.H. Sumn er
IRE Trans. EC-11, 2 (1962), pp. 223-235
(Reprinted in Bell and Newell, “Computer Structures: Readi ngs and Examples” McGraw-Hill,
New York, 1971).
The Atlas pioneered the idea of dividing memory into ﬁxed-si zed pages and in many senses was an early
form of the memory-management ideas we see in modern compute r systems.
[I09] “Intel 64 and IA-32 Architectures Software Developer ’s Manuals”
Intel, 2009
Available: http://www.intel.com/products/processor/manuals
In particular, pay attention to “Volume 3A: System Programm ing Guide Part 1” and “Volume 3B:
System Programming Guide Part 2”
[L78] “The Manchester Mark I and atlas: a historical perspec tive”
S. H. Lavington
Communications of the ACM archive
V olume 21, Issue 1 (January 1978), pp. 4-12
Special issue on computer architecture
This paper is a great retrospective of some of the history of t he development of some important computer
systems. As we sometimes forget in the US, many of these new id eas came from overseas.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 217

PAGING : I NTRODUCTION 181
Homework
In this homework, you will use a simple program, which is know n as
paging-linear-translate.py, to see if you understand how simple
virtual-to-physical address translation works with linea r page tables. See
the README for details.
Questions
• Before doing any translations, let’s use the simulator to st udy how
linear page tables change size given different parameters. Compute
the size of linear page tables as different parameters chang e. Some
suggested inputs are below; by using the -v flag , you can see
how many page-table entries are ﬁlled.
First, to understand how linear page table size changes as th e ad-
dress space grows:
paging-linear-translate.py -P 1k -a 1m -p 512m -v -n 0
paging-linear-translate.py -P 1k -a 2m -p 512m -v -n 0
paging-linear-translate.py -P 1k -a 4m -p 512m -v -n 0
Then, to understand how linear page table size changes as page size
grows:
paging-linear-translate.py -P 1k -a 1m -p 512m -v -n 0
paging-linear-translate.py -P 2k -a 1m -p 512m -v -n 0
paging-linear-translate.py -P 4k -a 1m -p 512m -v -n 0
Before running any of these, try to think about the expected t rends.
How should page-table size change as the address space grows ? As
the page size grows? Why shouldn’t we just use really big page s in
general?
• Now let’s do some translations. Start with some small exampl es,
and change the number of pages that are allocated to the addre ss
space with the -u flag . For example:
paging-linear-translate.py -P 1k -a 16k -p 32k -v -u 0
paging-linear-translate.py -P 1k -a 16k -p 32k -v -u 25
paging-linear-translate.py -P 1k -a 16k -p 32k -v -u 50
paging-linear-translate.py -P 1k -a 16k -p 32k -v -u 75
paging-linear-translate.py -P 1k -a 16k -p 32k -v -u 100
What happens as you increase the percentage of pages that are al-
located in each address space?
• Now let’s try some different random seeds, and some differen t (and
sometimes quite crazy) address-space parameters, for vari ety:
paging-linear-translate.py -P 8 -a 32 -p 1024 -v -s 1
paging-linear-translate.py -P 8k -a 32k -p 1m -v -s 2
paging-linear-translate.py -P 1m -a 256m -p 512m -v -s 3
Which of these parameter combinations are unrealistic? Why ?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 218

182 PAGING : I NTRODUCTION
• Use the program to try out some other problems. Can you ﬁnd the
limits of where the program doesn’t work anymore? For exampl e,
what happens if the address-space size is bigger than physical mem-
ory?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 219

19
Paging: Faster Translations (TLBs)
Using paging as the core mechanism to support virtual memory can lead
to high performance overheads. By chopping the address space into small,
ﬁxed-sized units (i.e., pages), paging requires a large amo unt of mapping
information. Because that mapping information is generall y stored in
physical memory , paging logically requires an extra memory lookup for
each virtual address generated by the program. Going to memo ry for
translation information before every instruction fetch or explicit load or
store is prohibitively slow . And thus our problem:
THE CRUX :
HOW TO SPEED UP ADDRESS TRANSLATION
How can we speed up address translation, and generally avoid the
extra memory reference that paging seems to require? What ha rdware
support is required? What OS involvement is needed?
When we want to make things fast, the OS usually needs some hel p.
And help often comes from the OS’s old friend: the hardware. T o speed
address translation, we are going to add what is called (for h istorical rea-
sons [CP78]) a translation-lookaside buffer , or TLB [C68, C95]. A TLB
is part of the chip’s memory-management unit (MMU), and is simply a
hardware cache of popular virtual-to-physical address translations; thu s,
a better name would be an address-translation cache. Upon each virtual
memory reference, the hardware ﬁrst checks the TLB to see if t he desired
translation is held therein; if so, the translation is perfo rmed (quickly)
without having to consult the page table (which has all translations ). Be-
cause of their tremendous performance impact, TLBs in a real sense make
virtual memory possible [C95].
19.1 TLB Basic Algorithm
Figure 19.1 shows a rough sketch of how hardware might handle a
virtual address translation, assuming a simple linear page table (i.e., the
page table is an array) and a hardware-managed TLB (i.e., the hardware
handles much of the responsibility of page table accesses; w e’ll explain
more about this below).
183

## Page 220

184 PAGING : F ASTER TRANSLATIONS (TLB S)
1 VPN = (VirtualAddress & VPN_MASK) >> SHIFT
2 (Success, TlbEntry) = TLB_Lookup(VPN)
3 if (Success == True) // TLB Hit
4 if (CanAccess(TlbEntry.ProtectBits) == True)
5 Offset = VirtualAddress & OFFSET_MASK
6 PhysAddr = (TlbEntry.PFN << SHIFT) | Offset
7 AccessMemory(PhysAddr)
8 else
9 RaiseException(PROTECTION_FAULT)
10 else // TLB Miss
11 PTEAddr = PTBR + (VPN * sizeof(PTE))
12 PTE = AccessMemory(PTEAddr)
13 if (PTE.Valid == False)
14 RaiseException(SEGMENTATION_FAULT)
15 else if (CanAccess(PTE.ProtectBits) == False)
16 RaiseException(PROTECTION_FAULT)
17 else
18 TLB_Insert(VPN, PTE.PFN, PTE.ProtectBits)
19 RetryInstruction()
Figure 19.1: TLB Control Flow Algorithm
The algorithm the hardware follows works like this: ﬁrst, ex tract the
virtual page number (VPN) from the virtual address (Line 1 inFigure 19.1),
and check if the TLB holds the translation for this VPN (Line 2 ). If it does,
we have a TLB hit, which means the TLB holds the translation. Success!
We can now extract the page frame number (PFN) from the releva nt TLB
entry , concatenate that onto the offset from the original vi rtual address,
and form the desired physical address (P A), and access memor y (Lines
5–7), assuming protection checks do not fail (Line 4).
If the CPU does not ﬁnd the translation in the TLB (a TLB miss), we
have some more work to do. In this example, the hardware acces ses the
page table to ﬁnd the translation (Lines 11–12), and, assumi ng that the
virtual memory reference generated by the process is valid a nd accessi-
ble (Lines 13, 15), updates the TLB with the translation (Lin e 18). These
set of actions are costly , primarily because of the extra mem ory reference
needed to access the page table (Line 12). Finally , once the T LB is up-
dated, the hardware retries the instruction; this time, the translation is
found in the TLB, and the memory reference is processed quick ly .
The TLB, like all caches, is built on the premise that in the co mmon
case, translations are found in the cache (i.e., are hits). I f so, little over-
head is added, as the TLB is found near the processing core and is de-
signed to be quite fast. When a miss occurs, the high cost of pa ging is
incurred; the page table must be accessed to ﬁnd the translat ion, and an
extra memory reference (or more, with more complex page tables) results.
If this happens often, the program will likely run noticeabl y more slowly;
memory accesses, relative to most CPU instructions, are qui te costly , and
TLB misses lead to more memory accesses. Thus, it is our hope t o avoid
TLB misses as much as we can.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 221

PAGING : F ASTER TRANSLATIONS (TLB S) 185
VPN = 15
VPN = 14
VPN = 13
VPN = 12
VPN = 11
VPN = 10
VPN = 09
VPN = 08
VPN = 07
VPN = 06
VPN = 05
VPN = 04
VPN = 03
VPN = 02
VPN = 01
VPN = 00
00 04 08 12 16
Offset
a[0] a[1] a[2]
a[3] a[4] a[5] a[6]
a[7] a[8] a[9]
Figure 19.2: Example: An Array In A Tiny Address Space
19.2 Example: Accessing An Array
To make clear the operation of a TLB, let’s examine a simple vi rtual
address trace and see how a TLB can improve its performance. I n this
example, let’s assume we have an array of 10 4-byte integers i n memory ,
starting at virtual address 100. Assume further that we have a small 8-bit
virtual address space, with 16-byte pages; thus, a virtual a ddress breaks
down into a 4-bit VPN (there are 16 virtual pages) and a 4-bit o ffset (there
are 16 bytes on each of those pages).
Figure 19.2 shows the array laid out on the 16 16-byte pages of the sys-
tem. As you can see, the array’s ﬁrst entry ( a[0]) begins on (VPN=06, off-
set=04); only three 4-byte integers ﬁt onto that page. The ar ray continues
onto the next page (VPN=07), where the next four entries ( a[3] ... a[6])
are found. Finally , the last three entries of the 10-entry array (a[7] ... a[9])
are located on the next page of the address space (VPN=08).
Now let’s consider a simple loop that accesses each array ele ment,
something that would look like this in C:
int sum = 0;
for (i = 0; i < 10; i++) {
sum += a[i];
}
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 222

186 PAGING : F ASTER TRANSLATIONS (TLB S)
For the sake of simplicity , we will pretend that the only memo ry ac-
cesses the loop generates are to the array (ignoring the vari ables i and
sum, as well as the instructions themselves). When the ﬁrst arra y element
(a[0]) is accessed, the CPU will see a load to virtual address 100. T he
hardware extracts the VPN from this (VPN=06), and uses that t o check
the TLB for a valid translation. Assuming this is the ﬁrst tim e the pro-
gram accesses the array , the result will be a TLB miss.
The next access is to a[1], and there is some good news here: a TLB
hit! Because the second element of the array is packed next to the ﬁrst, it
lives on the same page; because we’ve already accessed this p age when
accessing the ﬁrst element of the array , the translation is a lready loaded
into the TLB. And hence the reason for our success. Access to a[2] en-
counters similar success (another hit), because it too live s on the same
page as a[0] and a[1].
Unfortunately , when the program accesses a[3], we encounter an-
other TLB miss. However, once again, the next entries ( a[4] ... a[6])
will hit in the TLB, as they all reside on the same page in memor y .
Finally , access to a[7] causes one last TLB miss. The hardware once
again consults the page table to ﬁgure out the location of thi s virtual page
in physical memory , and updates the TLB accordingly . The ﬁna l two ac-
cesses (a[8] and a[9]) receive the beneﬁts of this TLB update; when the
hardware looks in the TLB for their translations, two more hi ts result.
Let us summarize TLB activity during our ten accesses to the a rray:
miss, hit, hit, miss, hit, hit, hit, miss, hit, hit. Thus, our TLB hit rate ,
which is the number of hits divided by the total number of acce sses, is
70%. Although this is not too high (indeed, we desire hit rate s that ap-
proach 100%), it is non-zero, which may be a surprise. Even th ough this
is the ﬁrst time the program accesses the array , TLB performa nce gains
beneﬁt from spatial locality. The elements of the array are packed tightly
into pages (i.e., they are close to one another in space), and thus only the
ﬁrst access to an element on a page yields a TLB miss.
Also note the role that page size plays in this example. If the page size
had simply been twice as big (32 bytes, not 16), the array acce ss would
suffer even fewer misses. As typical page sizes are more like 4KB, these
types of dense, array-based accesses achieve excellent TLB performance,
encountering only a single miss per page of accesses.
One last point about TLB performance: if the program, soon af ter this
loop completes, accesses the array again, we’d likely see an even bet-
ter result, assuming that we have a big enough TLB to cache the needed
translations: hit, hit, hit, hit, hit, hit, hit, hit, hit, hi t. In this case, the
TLB hit rate would be high because of temporal locality , i.e., the quick
re-referencing of memory items in time. Like any cache, TLBs rely upon
both spatial and temporal locality for success, which are pr ogram proper-
ties. If the program of interest exhibits such locality (and many programs
do), the TLB hit rate will likely be high.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 223

PAGING : F ASTER TRANSLATIONS (TLB S) 187
TIP : U SE CACHING WHEN POSSIBLE
Caching is one of the most fundamental performance techniqu es in com-
puter systems, one that is used again and again to make the “co mmon-
case fast” [HP06]. The idea behind hardware caches is to take advantage
of locality in instruction and data references. There are usually two ty pes
of locality: temporal locality and spatial locality. With temporal locality ,
the idea is that an instruction or data item that has been rece ntly accessed
will likely be re-accessed soon in the future. Think of loop v ariables or in-
structions in a loop; they are accessed repeatedly over time . With spatial
locality , the idea is that if a program accesses memory at address x, it will
likely soon access memory near x. Imagine here streaming through an
array of some kind, accessing one element and then the next. O f course,
these properties depend on the exact nature of the program, a nd thus are
not hard-and-fast laws but more like rules of thumb.
Hardware caches, whether for instructions, data, or addres s translations
(as in our TLB) take advantage of locality by keeping copies o f memory in
small, fast on-chip memory . Instead of having to go to a (slow ) memory
to satisfy a request, the processor can ﬁrst check if a nearby copy exists
in a cache; if it does, the processor can access it quickly (i. e., in a few cy-
cles) and avoid spending the costly time it takes to access me mory (many
nanoseconds).
You might be wondering: if caches (like the TLB) are so great, why don’t
we just make bigger caches and keep all of our data in them? Unf or-
tunately , this is where we run into more fundamental laws lik e those of
physics. If you want a fast cache, it has to be small, as issues like the
speed-of-light and other physical constraints become rele vant. Any large
cache by deﬁnition is slow , and thus defeats the purpose. Thu s, we are
stuck with small, fast caches; the question that remains is h ow to best use
them to improve performance.
19.3 Who Handles The TLB Miss?
One question that we must answer: who handles a TLB miss? Two a n-
swers are possible: the hardware, or the software (OS). In th e olden days,
the hardware had complex instruction sets (sometimes calle d CISC, for
complex-instruction set computers) and the people who buil t the hard-
ware didn’t much trust those sneaky OS people. Thus, the hard ware
would handle the TLB miss entirely . To do this, the hardware h as to
know exactly where the page tables are located in memory (via a page-
table base register , used in Line 11 in Figure
19.1), as well as their exact
format; on a miss, the hardware would “walk” the page table, ﬁnd the c or-
rect page-table entry and extract the desired translation, update the TLB
with the translation, and retry the instruction. An example of an “older”
architecture that has hardware-managed TLBs is the Intel x86 architec-
ture, which uses a ﬁxed multi-level page table (see the next chapter for
details); the current page table is pointed to by the CR3 regi ster [I09].
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 224

188 PAGING : F ASTER TRANSLATIONS (TLB S)
1 VPN = (VirtualAddress & VPN_MASK) >> SHIFT
2 (Success, TlbEntry) = TLB_Lookup(VPN)
3 if (Success == True) // TLB Hit
4 if (CanAccess(TlbEntry.ProtectBits) == True)
5 Offset = VirtualAddress & OFFSET_MASK
6 PhysAddr = (TlbEntry.PFN << SHIFT) | Offset
7 Register = AccessMemory(PhysAddr)
8 else
9 RaiseException(PROTECTION_FAULT)
10 else // TLB Miss
11 RaiseException(TLB_MISS)
Figure 19.3: TLB Control Flow Algorithm (OS Handled)
More modern architectures (e.g., MIPS R10k [H93] or Sun’s SP ARC v9
[WG00], both RISC or reduced-instruction set computers) have what is
known as a software-managed TLB . On a TLB miss, the hardware sim-
ply raises an exception (line 11 in Figure 19.3), which pauses the current
instruction stream, raises the privilege level to kernel mo de, and jumps
to a trap handler . As you might guess, this trap handler is code within
the OS that is written with the express purpose of handling TL B misses.
When run, the code will lookup the translation in the page tab le, use spe-
cial “privileged” instructions to update the TLB, and return from the trap;
at this point, the hardware retries the instruction (result ing in a TLB hit).
Let’s discuss a couple of important details. First, the retu rn-from-trap
instruction needs to be a little different than the return-f rom-trap we saw
before when servicing a system call. In the latter case, the r eturn-from-
trap should resume execution at the instruction after the trap into the OS,
just as a return from a procedure call returns to the instruct ion imme-
diately following the call into the procedure. In the former case, when
returning from a TLB miss-handling trap, the hardware must r esume ex-
ecution at the instruction that caused the trap; this retry thus lets the in-
struction run again, this time resulting in a TLB hit. Thus, d epending on
how a trap or exception was caused, the hardware must save a di fferent
PC when trapping into the OS, in order to resume properly when the time
to do so arrives.
Second, when running the TLB miss-handling code, the OS needs to be
extra careful not to cause an inﬁnite chain of TLB misses to oc cur. Many
solutions exist; for example, you could keep TLB miss handle rs in physi-
cal memory (where they are unmapped and not subject to address trans-
lation), or reserve some entries in the TLB for permanently- valid transla-
tions and use some of those permanent translation slots for t he handler
code itself; these wired translations always hit in the TLB.
The primary advantage of the software-managed approach is ﬂexibil-
ity: the OS can use any data structure it wants to implement the pa ge
table, without necessitating hardware change. Another adv antage is sim-
plicity; as you can see in the TLB control ﬂow (line 11 in Figure 19.3, in
contrast to lines 11–19 in Figure 19.1), the hardware doesn’t have to do
much on a miss; it raises an exception, and the OS TLB miss hand ler does
the rest.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 225

PAGING : F ASTER TRANSLATIONS (TLB S) 189
ASIDE : RISC VS . CISC
In the 1980’s, a great battle took place in the computer archi tecture com-
munity . On one side was the CISC camp, which stood for Complex
Instruction Set Computing ; on the other side was RISC, for Reduced
Instruction Set Computing [PS81]. The RISC side was spear-headed by
David Patterson at Berkeley and John Hennessy at Stanford (w ho are also
co-authors of some famous books [HP06]), although later John Cocke was
recognized with a Turing award for his earliest work on RISC [ CM00].
CISC instruction sets tend to have a lot of instructions in th em, and each
instruction is relatively powerful. For example, you might see a string
copy , which takes two pointers and a length and copies bytes from source
to destination. The idea behind CISC was that instructions s hould be
high-level primitives, to make the assembly language itsel f easier to use,
and to make code more compact.
RISC instruction sets are exactly the opposite. A key observ ation behind
RISC is that instruction sets are really compiler targets, a nd all compil-
ers really want are a few simple primitives that they can use t o gener-
ate high-performance code. Thus, RISC proponents argued, l et’s rip out
as much from the hardware as possible (especially the microc ode), and
make what’s left simple, uniform, and fast.
In the early days, RISC chips made a huge impact, as they were noticeably
faster [BC91]; many papers were written; a few companies wer e formed
(e.g., MIPS and Sun). However, as time progressed, CISC manu facturers
such as Intel incorporated many RISC techniques into the cor e of their
processors, for example by adding early pipeline stages tha t transformed
complex instructions into micro-instructions which could then be pro-
cessed in a RISC-like manner. These innovations, plus a grow ing number
of transistors on each chip, allowed CISC to remain competit ive. The end
result is that the debate died down, and today both types of pr ocessors
can be made to run fast.
19.4 TLB Contents: What’s In There?
Let’s look at the contents of the hardware TLB in more detail. A typical
TLB might have 32, 64, or 128 entries and be what is called fully associa-
tive. Basically , this just means that any given translation can be anywhere
in the TLB, and that the hardware will search the entire TLB in parallel to
ﬁnd the desired translation. A typical TLB entry might look l ike this:
VPN PFN other bits
Note that both the VPN and PFN are present in each entry , as a tr ans-
lation could end up in any of these locations (in hardware ter ms, the TLB
is known as a fully-associative cache). The hardware searches the entries
in parallel to see if there is a match.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 226

190 PAGING : F ASTER TRANSLATIONS (TLB S)
ASIDE : TLB V ALID BIT ̸= PAGE TABLE VALID BIT
A common mistake is to confuse the valid bits found in a TLB wit h
those found in a page table. In a page table, when a page-table entry
(PTE) is marked invalid, it means that the page has not been al located by
the process, and should not be accessed by a correctly-worki ng program.
The usual response when an invalid page is accessed is to trap to the OS,
which will respond by killing the process.
A TLB valid bit, in contrast, simply refers to whether a TLB en try has a
valid translation within it. When a system boots, for exampl e, a common
initial state for each TLB entry is to be set to invalid, becau se no address
translations are yet cached there. Once virtual memory is en abled, and
once programs start running and accessing their virtual add ress spaces,
the TLB is slowly populated, and thus valid entries soon ﬁll t he TLB.
The TLB valid bit is quite useful when performing a context switch too,
as we’ll discuss further below . By setting all TLB entries to invalid, the
system can ensure that the about-to-be-run process does not accidentally
use a virtual-to-physical translation from a previous proc ess.
More interesting are the “other bits”. For example, the TLB c ommonly
has a valid bit, which says whether the entry has a valid translation or
not. Also common are protection bits, which determine how a page can
be accessed (as in the page table). For example, code pages mi ght be
marked read and execute , whereas heap pages might be marked read and
write. There may also be a few other ﬁelds, including an address-space
identiﬁer, a dirty bit, and so forth; see below for more information.
19.5 TLB Issue: Context Switches
With TLBs, some new issues arise when switching between proc esses
(and hence address spaces). Speciﬁcally , the TLB contains virtual-to-physical
translations that are only valid for the currently running p rocess; these
translations are not meaningful for other processes. As a re sult, when
switching from one process to another, the hardware or OS (or both) must
be careful to ensure that the about-to-be-run process does not accidentally
use translations from some previously run process.
To understand this situation better, let’s look at an exampl e. When one
process (P1) is running, it assumes the TLB might be caching t ranslations
that are valid for it, i.e., that come from P1’s page table. As sume, for this
example, that the 10th virtual page of P1 is mapped to physical frame 100.
In this example, assume another process (P2) exists, and the OS soon
might decide to perform a context switch and run it. Assume he re that
the 10th virtual page of P2 is mapped to physical frame 170. If entries for
both processes were in the TLB, the contents of the TLB would b e:
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 227

PAGING : F ASTER TRANSLATIONS (TLB S) 191
VPN PFN valid prot
10 100 1 rwx
— — 0 —
10 170 1 rwx
— — 0 —
In the TLB above, we clearly have a problem: VPN 10 translates to
either PFN 100 (P1) or PFN 170 (P2), but the hardware can’t dis tinguish
which entry is meant for which process. Thus, we need to do som e more
work in order for the TLB to correctly and efﬁciently support virtualiza-
tion across multiple processes. And thus, a crux:
THE CRUX :
HOW TO MANAGE TLB C ONTENTS ON A C ONTEXT SWITCH
When context-switching between processes, the translatio ns in the TLB
for the last process are not meaningful to the about-to-be-r un process.
What should the hardware or OS do in order to solve this proble m?
There are a number of possible solutions to this problem. One ap-
proach is to simply ﬂush the TLB on context switches, thus emptying
it before running the next process. On a software-based syst em, this
can be accomplished with an explicit (and privileged) hardw are instruc-
tion; with a hardware-managed TLB, the ﬂush could be enacted when the
page-table base register is changed (note the OS must change the PTBR
on a context switch anyhow). In either case, the ﬂush operati on simply
sets all valid bits to 0, essentially clearing the contents o f the TLB.
By ﬂushing the TLB on each context switch, we now have a workin g
solution, as a process will never accidentally encounter th e wrong trans-
lations in the TLB. However, there is a cost: each time a proce ss runs, it
must incur TLB misses as it touches its data and code pages. If the OS
switches between processes frequently , this cost may be high.
To reduce this overhead, some systems add hardware support t o en-
able sharing of the TLB across context switches. In particul ar, some hard-
ware systems provide an address space identiﬁer (ASID) ﬁeld in the
TLB. You can think of the ASID as a process identiﬁer (PID), but usu-
ally it has fewer bits (e.g., 8 bits for the ASID versus 32 bits for a PID).
If we take our example TLB from above and add ASIDs, it is clear
processes can readily share the TLB: only the ASID ﬁeld is nee ded to dif-
ferentiate otherwise identical translations. Here is a dep iction of a TLB
with the added ASID ﬁeld:
VPN PFN valid prot ASID
10 100 1 rwx 1
— — 0 — —
10 170 1 rwx 2
— — 0 — —
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 228

192 PAGING : F ASTER TRANSLATIONS (TLB S)
Thus, with address-space identiﬁers, the TLB can hold trans lations
from different processes at the same time without any confus ion. Of
course, the hardware also needs to know which process is curr ently run-
ning in order to perform translations, and thus the OS must, o n a context
switch, set some privileged register to the ASID of the curre nt process.
As an aside, you may also have thought of another case where tw o
entries of the TLB are remarkably similar. In this example, t here are two
entries for two different processes with two different VPNs that point to
the same physical page:
VPN PFN valid prot ASID
10 101 1 r-x 1
— — 0 — —
50 101 1 r-x 2
— — 0 — —
This situation might arise, for example, when two processes share a
page (a code page, for example). In the example above, Proces s 1 is shar-
ing physical page 101 with Process 2; P1 maps this page into th e 10th
page of its address space, whereas P2 maps it to the 50th page o f its ad-
dress space. Sharing of code pages (in binaries, or shared li braries) is
useful as it reduces the number of physical pages in use, thus reducing
memory overheads.
19.6 Issue: Replacement Policy
As with any cache, and thus also with the TLB, one more issue th at we
must consider is cache replacement. Speciﬁcally , when we are installing
a new entry in the TLB, we have to replace an old one, and thus the
question: which one to replace?
THE CRUX : H OW TO DESIGN TLB R EPLACEMENT POLICY
Which TLB entry should be replaced when we add a new TLB entry?
The goal, of course, being to minimize the miss rate (or increase hit rate)
and thus improve performance.
We will study such policies in some detail when we tackle the problem
of swapping pages to disk in a virtual memory system; here we’ ll just
highlight a few of typical policies. One common approach is t o evict the
least-recently-used or LRU entry . The idea here is to take advantage of
locality in the memory-reference stream; thus, it is likely that an entry that
has not recently been used is a good candidate for eviction as (perhaps)
it won’t soon be referenced again. Another typical approach is to use a
random policy . Randomness sometimes makes a bad decision but has the
nice property that there are not any weird corner case behavi ors that can
cause pessimal behavior, e.g., think of a loop accessing n + 1 pages, a TLB
of size n, and an LRU replacement policy .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 229

PAGING : F ASTER TRANSLATIONS (TLB S) 193
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
VPN G ASID
PFN C D V
Figure 19.4: A MIPS TLB Entry
19.7 A Real TLB Entry
Finally , let’s brieﬂy look at a real TLB. This example is from the MIPS
R4000 [H93], a modern system that uses software-managed TLB s. All 64
bits of this TLB entry can be seen in Figure 19.4.
The MIPS R4000 supports a 32-bit address space with 4KB pages. Thus,
we would expect a 20-bit VPN and 12-bit offset in our typical v irtual ad-
dress. However, as you can see in the TLB, there are only 19 bit s for the
VPN; as it turns out, user addresses will only come from half t he address
space (the rest reserved for the kernel) and hence only 19 bit s of VPN
are needed. The VPN translates to up to a 24-bit physical fram e number
(PFN), and hence can support systems with up to 64GB of (physical) main
memory (224 4KB pages).
There are a few other interesting bits in the MIPS TLB. We see a global
bit (G), which is used for pages that are globally-shared amo ng processes.
Thus, if the global bit is set, the ASID is ignored. We also see the 8-bit
ASID, which the OS can use to distinguish between address spaces ( as
described above). One question for you: what should the OS do if there
are more than 256 ( 28) processes running at a time? Finally , we see 3
Coherence (C) bits, which determine how a page is cached by the hardware
(a bit beyond the scope of these notes); a dirty bit which is marked when
the page has been written to (we’ll see the use of this later); a valid bit
which tells the hardware if there is a valid translation pres ent in the entry .
There is also a page mask ﬁeld (not shown), which supports multiple page
sizes; we’ll see later why having larger pages might be usefu l. Finally ,
some of the 64 bits are unused (shaded gray in the diagram).
MIPS TLBs usually have 32 or 64 of these entries, most of which are
used by user processes as they run. However, a few are reserve d for the
OS. A wired register can be set by the OS to tell the hardware how many
slots of the TLB to reserve for the OS; the OS uses these reserv ed map-
pings for code and data that it wants to access during critical times, where
a TLB miss would be problematic (e.g., in the TLB miss handler ).
Because the MIPS TLB is software managed, there needs to be in struc-
tions to update the TLB. The MIPS provides four such instruct ions: TLBP,
which probes the TLB to see if a particular translation is in t here; TLBR,
which reads the contents of a TLB entry into registers; TLBWI, which re-
places a speciﬁc TLB entry; and TLBWR, which replaces a random TLB
entry . The OS uses these instructions to manage the TLB’s con tents. It is
of course critical that these instructions are privileged; imagine what a
user process could do if it could modify the contents of the TL B (hint: just
about anything, including take over the machine, run its own malicious
“OS”, or even make the Sun disappear).
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 230

194 PAGING : F ASTER TRANSLATIONS (TLB S)
TIP : RAM I SN ’ T ALWAYS RAM (C ULLER ’ S LAW)
The term random-access memory , or RAM, implies that you can access
any part of RAM just as quickly as another. While it is general ly good to
think of RAM in this way , because of hardware/OS features suc h as the
TLB, accessing a particular page of memory may be costly , par ticularly if
that page isn’t currently mapped by your TLB. Thus, it is alwa ys good to
remember the implementation tip: RAM isn’t always RAM . Sometimes
randomly accessing your address space, particular if the number of pages
accessed exceeds the TLB coverage, can lead to severe performance penal-
ties. Because one of our advisors, David Culler, used to alwa ys point to
the TLB as the source of many performance problems, we name th is law
in his honor: Culler’s Law .
19.8 Summary
We have seen how hardware can help us make address translatio n
faster. By providing a small, dedicated on-chip TLB as an address-translation
cache, most memory references will hopefully be handled without having
to access the page table in main memory . Thus, in the common ca se,
the performance of the program will be almost as if memory isn ’t being
virtualized at all, an excellent achievement for an operati ng system, and
certainly essential to the use of paging in modern systems.
However, TLBs do not make the world rosy for every program tha t
exists. In particular, if the number of pages a program acces ses in a short
period of time exceeds the number of pages that ﬁt into the TLB , the pro-
gram will generate a large number of TLB misses, and thus run q uite a
bit more slowly . We refer to this phenomenon as exceeding the TLB cov-
erage, and it can be quite a problem for certain programs. One solut ion,
as we’ll discuss in the next chapter, is to include support fo r larger page
sizes; by mapping key data structures into regions of the pro gram’s ad-
dress space that are mapped by larger pages, the effective co verage of the
TLB can be increased. Support for large pages is often exploi ted by pro-
grams such as a database management system (a DBMS), which have
certain data structures that are both large and randomly-ac cessed.
One other TLB issue worth mentioning: TLB access can easily b e-
come a bottleneck in the CPU pipeline, in particular with wha t is called a
physically-indexed cache. With such a cache, address translation has to
take place before the cache is accessed, which can slow things down quite
a bit. Because of this potential problem, people have looked into all sorts
of clever ways to access caches with virtual addresses, thus avoiding the
expensive step of translation in the case of a cache hit. Such a virtually-
indexed cache solves some performance problems, but introduces new
issues into hardware design as well. See Wiggins’s ﬁne surve y for more
details [W03].
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 231

PAGING : F ASTER TRANSLATIONS (TLB S) 195
References
[BC91] “Performance from Architecture: Comparing a RISC an d a CISC
with Similar Hardware Organization”
D. Bhandarkar and Douglas W. Clark
Communications of the ACM, September 1991
A great and fair comparison between RISC and CISC. The bottom line: on similar hardware, RISC was
about a factor of three better in performance.
[CM00] “The evolution of RISC technology at IBM”
John Cocke and V . Markstein
IBM Journal of Research and Development, 44:1/2
A summary of the ideas and work behind the IBM 801, which many c onsider the ﬁrst true RISC micro-
processor.
[C95] “The Core of the Black Canyon Computer Corporation”
John Couleur
IEEE Annals of History of Computing, 17:4, 1995
In this fascinating historical note, Couleur talks about ho w he invented the TLB in 1964 while working
for GE, and the fortuitous collaboration that thus ensued wi th the Project MAC folks at MIT.
[CG68] “Shared-access Data Processing System”
John F. Couleur and Edward L. Glaser
Patent 3412382, November 1968
The patent that contains the idea for an associative memory t o store address translations. The idea,
according to Couleur, came in 1964.
[CP78] “The architecture of the IBM System/370”
R.P . Case and A. Padegs
Communications of the ACM. 21:1, 73-96, January 1978
Perhaps the ﬁrst paper to use the term translation lookaside buffer . The name arises from the his-
torical name for a cache, which was a lookaside buffer as called by those developing the Atlas system
at the University of Manchester; a cache of address translat ions thus became a translation lookaside
buffer. Even though the term lookaside buffer fell out of favor, TLB seems to have stuck, for whatever
reason.
[H93] “MIPS R4000 Microprocessor User’s Manual”.
Joe Heinrich, Prentice-Hall, June 1993
Available: http://cag.csail.mit.edu/raw/
documents/R4400
Uman book Ed2.pdf
[HP06] “Computer Architecture: A Quantitative Approach”
John Hennessy and David Patterson
Morgan-Kaufmann, 2006
A great book about computer architecture. We have a particul ar attachment to the classic ﬁrst edition.
[I09] “Intel 64 and IA-32 Architectures Software Developer ’s Manuals”
Intel, 2009
Available: http://www.intel.com/products/processor/manuals
In particular, pay attention to “Volume 3A: System Programm ing Guide Part 1” and “Volume 3B:
System Programming Guide Part 2”
[PS81] “RISC-I: A Reduced Instruction Set VLSI Computer”
D.A. Patterson and C.H. Sequin
ISCA ’81, Minneapolis, May 1981
The paper that introduced the term RISC, and started the aval anche of research into simplifying com-
puter chips for performance.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 232

196 PAGING : F ASTER TRANSLATIONS (TLB S)
[SB92] “CPU Performance Evaluation and Execution Time Pred iction
Using Narrow Spectrum Benchmarking”
Rafael H. Saavedra-Barrera
EECS Department, University of California, Berkeley
Technical Report No. UCB/CSD-92-684, February 1992
www.eecs.berkeley .edu/Pubs/TechRpts/1992/CSD-92-684.pdf
A great dissertation about how to predict execution time of a pplications by breaking them down into
constituent pieces and knowing the cost of each piece. Proba bly the most interesting part that comes out
of this work is the tool to measure details of the cache hierar chy (described in Chapter 5). Make sure to
check out the wonderful diagrams therein.
[W03] “A Survey on the Interaction Between Caching, Transla tion and Protection”
Adam Wiggins
University of New South Wales TR UNSW-CSE-TR-0321, August, 2003
An excellent survey of how TLBs interact with other parts of the CPU pipeline, namely hardware caches.
[WG00] “The SPARC Architecture Manual: V ersion 9”
David L. Weaver and Tom Germond, September 2000
SPARC International, San Jose, California
Available: http://www.sparc.org/standards/SPARCV9.pdf
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 233

PAGING : F ASTER TRANSLATIONS (TLB S) 197
Homework (Measurement)
In this homework, you are to measure the size and cost of acces sing
a TLB. The idea is based on work by Saavedra-Barrera [SB92], w ho de-
veloped a simple but beautiful method to measure numerous as pects of
cache hierarchies, all with a very simple user-level progra m. Read his
work for more details.
The basic idea is to access some number of pages within large d ata
structure (e.g., an array) and to time those accesses. For ex ample, let’s say
the TLB size of a machine happens to be 4 (which would be very sm all,
but useful for the purposes of this discussion). If you write a program
that touches 4 or fewer pages, each access should be a TLB hit, and thus
relatively fast. However, once you touch 5 pages or more, rep eatedly in a
loop, each access will suddenly jump in cost, to that of a TLB m iss.
The basic code to loop through an array once should look like t his:
int jump = PAGESIZE / sizeof(int);
for (i = 0; i < NUMPAGES * jump; i += jump) {
a[i] += 1;
}
In this loop, one integer per page of the the array a is updated, up
to the number of pages speciﬁed by NUMPAGES. By timing such a loop
repeatedly (say , a few hundred million times in another loop around this
one, or however many loops are needed to run for a few seconds) , you
can time how long each access takes (on average). By looking f or jumps
in cost as NUMPAGES increases, you can roughly determine how big the
ﬁrst-level TLB is, determine whether a second-level TLB exi sts (and how
big it is if it does), and in general get a good sense of how TLB h its and
misses can affect performance.
Here is an example graph:
As you can see in the graph, when just a few pages are accessed ( 8
or fewer), the average access time is roughly 5 nanoseconds. When 16
or more pages are accessed, there is a sudden jump to about 20 n anosec-
onds per access. A ﬁnal jump in cost occurs at around 1024 page s, at
which point each access takes around 70 nanoseconds. From th is data,
we can conclude that there is a two-level TLB hierarchy; the ﬁ rst is quite
small (probably holding between 8 and 16 entries); the secon d is larger
but slower (holding roughly 512 entries). The overall diffe rence between
hits in the ﬁrst-level TLB and misses is quite large, roughly a factor of
fourteen. TLB performance matters!
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 234

198 PAGING : F ASTER TRANSLATIONS (TLB S)
1 4 16 64 256 1024
0
20
40
60
80
TLB Size Measurement
Number Of Pages
Time Per Access (ns)
Figure 19.5: Discovering TLB Sizes and Miss Costs
Questions
• For timing, you’ll need to use a timer such as that made availa ble
by gettimeofday(). How precise is such a timer? How long
does an operation have to take in order for you to time it preci sely?
(this will help determine how many times, in a loop, you’ll ha ve to
repeat a page access in order to time it successfully)
• Write the program, called tlb.c, that can roughly measure the cost
of accessing each page. Inputs to the program should be: the n um-
ber of pages to touch and the number of trials.
• Now write a script in your favorite scripting language (csh, python,
etc.) to run this program, while varying the number of pages a c-
cessed from 1 up to a few thousand, perhaps incrementing by a
factor of two per iteration. Run the script on different mach ines
and gather some data. How many trials are needed to get reliab le
measurements?
• Next, graph the results, making a graph that looks similar to the
one above. Use a good tool like ploticus. Visualization usually
makes the data much easier to digest; why do you think that is?
• One thing to watch out for is compiler optimzation. Compiler s do
all sorts of clever things, including removing loops which i ncre-
ment values that no other part of the program subsequently us es.
How can you ensure the compiler does not remove the main loop
above from your TLB size estimator?
• Another thing to watch out for is the fact that most systems to day
ship with multiple CPUs, and each CPU, of course, has its own T LB
hierarchy . To really get good measurements, you have to run y our
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 235

PAGING : F ASTER TRANSLATIONS (TLB S) 199
code on just one CPU, instead of letting the scheduler bounce it
from one CPU to the next. How can you do that? (hint: look up
“pinning a thread” on Google for some clues) What will happen if
you don’t do this, and the code moves from one CPU to the other?
• Another issue that might arise relates to initialization. I f you don’t
initialize the array a above before accessing it, the ﬁrst time you
access it will be very expensive, due to initial access costs such as
demand zeroing. Will this affect your code and its timing? Wh at
can you do to counterbalance these potential costs?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 237

20
Paging: Smaller Tables
We now tackle the second problem that paging introduces: pag e tables
are too big and thus consume too much memory . Let’s start out w ith
a linear page table. As you might recall 1, linear page tables get pretty
big. Assume again a 32-bit address space ( 232 bytes), with 4KB ( 212 byte)
pages and a 4-byte page-table entry . An address space thus ha s roughly
one million virtual pages in it ( 232
212 ); multiply by the page-table size and
you see that our page table is 4MB in size. Recall also: we usua lly have
one page table for every process in the system! With a hundred active pro-
cesses (not uncommon on a modern system), we will be allocati ng hun-
dreds of megabytes of memory just for page tables! As a result , we are in
search of some techniques to reduce this heavy burden. There are a lot of
them, so let’s get going. But not before our crux:
CRUX : H OW TO MAKE PAGE TABLES SMALLER ?
Simple array-based page tables (usually called linear page tables) are
too big, taking up far too much memory on typical systems. How can we
make page tables smaller? What are the key ideas? What inefﬁc iencies
arise as a result of these new data structures?
20.1 Simple Solution: Bigger Pages
We could reduce the size of the page table in one simple way: us e
bigger pages. Take our 32-bit address space again, but this t ime assume
16KB pages. We would thus have an 18-bit VPN plus a 14-bit offs et. As-
suming the same size for each PTE (4 bytes), we now have 218 entries in
our linear page table and thus a total size of 1MB per page tabl e, a factor
1Or indeed, you might not; this paging thing is getting out of c ontrol, no? That said,
always make sure you understand the problem you are solving before moving onto the solution;
indeed, if you understand the problem, you can often derive t he solution yourself. Here, the
problem should be clear: simple linear (array-based) page t ables are too big.
201

## Page 238

202 PAGING : S MALLER TABLES
ASIDE : MULTIPLE PAGE SIZES
As an aside, do note that many architectures (e.g., MIPS, SP A RC, x86-64)
now support multiple page sizes. Usually , a small (4KB or 8KB ) page
size is used. However, if a “smart” application requests it, a single large
page (e.g., of size 4MB) can be used for a speciﬁc portion of th e address
space, enabling such applications to place a frequently-us ed (and large)
data structure in such a space while consuming only a single T LB en-
try . This type of large page usage is common in database manag ement
systems and other high-end commercial applications. The ma in reason
for multiple page sizes is not to save page table space, howev er; it is to
reduce pressure on the TLB, enabling a program to access more of its ad-
dress space without suffering from too many TLB misses. Howe ver, as
researchers have shown [N+02], using multiple page sizes ma kes the OS
virtual memory manager notably more complex, and thus large pages
are sometimes most easily used simply by exporting a new inte rface to
applications to request large pages directly .
of four reduction in size of the page table (not surprisingly , the reduction
exactly mirrors the factor of four increase in page size).
The major problem with this approach, however, is that big pages lead
to waste within each page, a problem known as internal fragmentation
(as the waste is internal to the unit of allocation). Applications thus end
up allocating pages but only using little bits and pieces of each, and mem-
ory quickly ﬁlls up with these overly-large pages. Thus, mos t systems use
relatively small page sizes in the common case: 4KB (as in x86 ) or 8KB (as
in SP ARCv9). Our problem will not be solved so simply , alas.
20.2 Hybrid Approach: Paging and Segments
Whenever you have two reasonable but different approaches t o some-
thing in life, you should always examine the combination of t he two to
see if you can obtain the best of both worlds. We call such a combination a
hybrid. For example, why eat just chocolate or plain peanut butter w hen
you can instead combine the two in a lovely hybrid known as the Reese’s
Peanut Butter Cup [M28]?
Years ago, the creators of Multics (in particular Jack Denni s) chanced
upon such an idea in the construction of the Multics virtual m emory sys-
tem [M07]. Speciﬁcally , Dennis had the idea of combining pag ing and
segmentation in order to reduce the memory overhead of page t ables.
We can see why this might work by examining a typical linear pa ge ta-
ble in more detail. Assume we have an address space in which th e used
portions of the heap and stack are small. For the example, we u se a tiny
16KB address space with 1KB pages (Figure
20.1); the page table for this
address space is in Table 20.1.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 239

PAGING : S MALLER TABLES 203
code
heap
stack
Virtual Address Space Physical Memory
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
Figure 20.1: A 16-KB Address Space With 1-KB Pages
This example assumes the single code page (VPN 0) is mapped to
physical page 10, the single heap page (VPN 4) to physical pag e 23, and
the two stack pages at the other end of the address space (VPNs 14 and
15) are mapped to physical pages 28 and 4, respectively . As yo u can see
from the picture, most of the page table is unused, full of invalid entries.
What a waste! And this is for a tiny 16KB address space. Imagin e the
page table of a 32-bit address space and all the potential was ted space in
there! Actually , don’t imagine such a thing; it’s far too gru esome.
PFN valid prot present dirty
10 1 r-x 1 0
- 0 — - -
- 0 — - -
- 0 — - -
23 1 rw- 1 1
- 0 — - -
- 0 — - -
- 0 — - -
- 0 — - -
- 0 — - -
- 0 — - -
- 0 — - -
- 0 — - -
- 0 — - -
28 1 rw- 1 1
4 1 rw- 1 1
Table 20.1: A Page T able For 16-KB Address Space
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 240

204 PAGING : S MALLER TABLES
Thus, our hybrid approach: instead of having a single page ta ble for
the entire address space of the process, why not have one per l ogical seg-
ment? In this example, we might thus have three page tables, o ne for the
code, heap, and stack parts of the address space.
Now , remember with segmentation, we had a base register that told
us where each segment lived in physical memory , and a bound or limit
register that told us the size of said segment. In our hybrid, we still have
those structures in the MMU; here, we use the base not to point to the
segment itself but rather to hold the physical address of the page table of that
segment. The bounds register is used to indicate the end of th e page table
(i.e., how many valid pages it has).
Let’s do a simple example to clarify . Assume a 32-bit virtual address
space with 4KB pages, and an address space split into four seg ments.
We’ll only use three segments for this example: one for code, one for
heap, and one for stack.
To determine which segment an address refers to, we’ll use th e top
two bits of the address space. Let’s assume 00 is the unused se gment,
with 01 for code, 10 for the heap, and 11 for the stack. Thus, a v irtual
address looks like this:
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
Seg VPN Offset
In the hardware, assume that there are thus three base/bound s pairs,
one each for code, heap, and stack. When a process is running, the base
register for each of these segments contains the physical ad dress of a lin-
ear page table for that segment; thus, each process in the sys tem now has
three page tables associated with it. On a context switch, these re gisters
must be changed to reﬂect the location of the page tables of th e newly-
running process.
On a TLB miss (assuming a hardware-managed TLB, i.e., where t he
hardware is responsible for handling TLB misses), the hardw are uses the
segment bits ( SN) to determine which base and bounds pair to use. The
hardware then takes the physical address therein and combin es it with
the VPN as follows to form the address of the page table entry ( PTE):
SN = (VirtualAddress & SEG_MASK) >> SN_SHIFT
VPN = (VirtualAddress & VPN_MASK) >> VPN_SHIFT
AddressOfPTE = Base[SN] + (VPN * sizeof(PTE))
This sequence should look familiar; it is virtually identic al to what we
saw before with linear page tables. The only difference, of c ourse, is the
use of one of three segment base registers instead of the sing le page table
base register.
The critical difference in our hybrid scheme is the presence of a bounds
register per segment; each bounds register holds the value o f the maxi-
mum valid page in the segment. For example, if the code segmen t is
using its ﬁrst three pages (0, 1, and 2), the code segment page table will
only have three entries allocated to it and the bounds regist er will be set
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

