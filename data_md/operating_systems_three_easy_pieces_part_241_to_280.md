# Document: operating_systems_three_easy_pieces (Pages 241 to 280)

## Page 241

PAGING : S MALLER TABLES 205
TIP : U SE HYBRIDS
When you have two good and seemingly opposing ideas, you shou ld
always see if you can combine them into a hybrid that manages to achieve
the best of both worlds. Hybrid corn species, for example, ar e known to
be more robust than any naturally-occurring species. Of cou rse, not all
hybrids are a good idea; see the Zeedonk (or Zonkey), which is a cross of
a Zebra and a Donkey . If you don’t believe such a creature exis ts, look it
up, and prepare to be amazed.
to 3; memory accesses beyond the end of the segment will gener ate an ex-
ception and likely lead to the termination of the process. In this manner,
our hybrid approach realizes a signiﬁcant memory savings co mpared to
the linear page table; unallocated pages between the stack a nd the heap
no longer take up space in a page table (just to mark them as not valid).
However, as you might notice, this approach is not without pr oblems.
First, it still requires us to use segmentation; as we discus sed before, seg-
mentation is not quite as ﬂexible as we would like, as it assum es a certain
usage pattern of the address space; if we have a large but spar sely-used
heap, for example, we can still end up with a lot of page table w aste.
Second, this hybrid causes external fragmentation to arise again. While
most of memory is managed in page-sized units, page tables no w can be
of arbitrary size (in multiples of PTEs). Thus, ﬁnding free s pace for them
in memory is more complicated. For these reasons, people con tinued to
look for better approaches to implementing smaller page tab les.
20.3 Multi-level Page Tables
A different approach doesn’t rely on segmentation but attac ks the same
problem: how to get rid of all those invalid regions in the pag e table in-
stead of keeping them all in memory? We call this approach a multi-level
page table, as it turns the linear page table into something like a tree. This
approach is so effective that many modern systems employ it ( e.g., x86
[BOH10]). We now describe this approach in detail.
The basic idea behind a multi-level page table is simple. Fir st, chop up
the page table into page-sized units; then, if an entire page of page-table
entries (PTEs) is invalid, don’t allocate that page of the pa ge table at all.
To track whether a page of the page table is valid (and if valid , where it
is in memory), use a new structure, called the page directory . The page
directory thus either can be used to tell you where a page of th e page
table is, or that the entire page of the page table contains no valid pages.
Figure
20.2 shows an example. On the left of the ﬁgure is the classic
linear page table; even though most of the middle regions of t he address
space are not valid, we still have to have page-table space al located for
those regions (i.e., the middle two pages of the page table). On the right
is a multi-level page table. The page directory marks just tw o pages of
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 242

206 PAGING : S MALLER TABLES
valid
protPFN
1 rx 12
1 rx 13
0 - -
1 rw 100
0 - -
0 - -
0 - -
0 - -
0 - -
0 - -
0 - -
0 - -
0 - -
0 - -
1 rw 86
1 rw 15
Linear Page Table
PTBR 201
PFN 201PFN 202PFN 203PFN 204
valid
protPFN
1 rx 12
1 rx 13
0 - -
1 rw 100
0 - -
0 - -
1 rw 86
1 rw 15
[Page 1 of PT: Not Allocated]
[Page 2 of PT: Not Allocated]
PFN 201PFN 204
Multi-level Page Table
PDBR 200
valid PFN
1 201
0 -
0 -
1 204
PFN 200
The Page Directory
Figure 20.2: Linear (Left) And Multi-Level (Right) Page T ables
the page table as valid (the ﬁrst and last); thus, just those t wo pages of the
page table reside in memory . And thus you can see one way to vis ualize
what a multi-level table is doing: it just makes parts of the l inear page
table disappear (freeing those frames for other uses), and t racks which
pages of the page table are allocated with the page directory .
The page directory , in a simple two-level table, contains on e entry per
page of the page table. It consists of a number of page directory entries
(PDE). A PDE (minimally) has a valid bit and a page frame number
(PFN), similar to a PTE. However, as hinted at above, the mean ing of
this valid bit is slightly different: if the PDE entry is vali d, it means that
at least one of the pages of the page table that the entry point s to (via the
PFN) is valid, i.e., in at least one PTE on that page pointed to by this PDE,
the valid bit in that PTE is set to one. If the PDE entry is not va lid (i.e.,
equal to zero), the rest of the PDE is not deﬁned.
Multi-level page tables have some obvious advantages over approaches
we’ve seen thus far. First, and perhaps most obviously , the m ulti-level ta-
ble only allocates page-table space in proportion to the amount of address
space you are using; thus it is generally compact and support s sparse ad-
dress spaces.
Second, if carefully constructed, each portion of the page t able ﬁts
neatly within a page, making it easier to manage memory; the O S can
simply grab the next free page when it needs to allocate or gro w a page
table. Contrast this to a simple (non-paged) linear page tab le2, which
is just an array of PTEs indexed by VPN; with such a structure, the en-
tire linear page table must reside contiguously in physical memory . For
a large page table (say 4MB), ﬁnding such a large chunk of unus ed con-
tiguous free physical memory can be quite a challenge. With a multi-level
2We are making some assumptions here, i.e., that all page tabl es reside in their entirety in
physical memory (i.e., they are not swapped to disk); we’ll s oon relax this assumption.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 243

PAGING : S MALLER TABLES 207
TIP : U NDERSTAND TIME -S PACE TRADE -OFFS
When building a data structure, one should always consider time-space
trade-offs in its construction. Usually , if you wish to make access to a par-
ticular data structure faster, you will have to pay a space-u sage penalty
for the structure.
structure, we add a level of indirection through use of the page directory ,
which points to pieces of the page table; that indirection allows us to place
page-table pages wherever we would like in physical memory .
It should be noted that there is a cost to multi-level tables; on a TLB
miss, two loads from memory will be required to get the right t ranslation
information from the page table (one for the page directory , and one for
the PTE itself), in contrast to just one load with a linear pag e table. Thus,
the multi-level table is a small example of a time-space trade-off . We
wanted smaller tables (and got them), but not for free; altho ugh in the
common case (TLB hit), performance is obviously identical, a TLB miss
suffers from a higher cost with this smaller table.
Another obvious negative is complexity. Whether it is the hardware or
OS handling the page-table lookup (on a TLB miss), doing so is undoubt-
edly more involved than a simple linear page-table lookup. O ften we are
willing to increase complexity in order to improve performance or reduce
overheads; in the case of a multi-level table, we make page-t able lookups
more complicated in order to save valuable memory .
A Detailed Multi-Level Example
To understand the idea behind multi-level page tables bette r, let’s do an
example. Imagine a small address space of size 16 KB, with 64-byte pages.
Thus, we have a 14-bit virtual address space, with 8 bits for t he VPN and
6 bits for the offset. A linear page table would have 28 (256) entries, even
if only a small portion of the address space is in use. Figure
20.3 presents
one example of such an address space.
stack
stack
(free)
(free)
... all free ...
(free)
(free)
heap
heap
(free)
(free)
code
code
1111 1111
1111 1110
1111 1101
1111 1100
0000 0111
0000 0110
0000 0101
0000 0100
0000 0011
0000 0010
0000 0001
0000 0000
................
Figure 20.3: A 16-KB Address Space With 64-byte Pages
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 244

208 PAGING : S MALLER TABLES
TIP : B E WARY OF COMPLEXITY
System designers should be wary of adding complexity into th eir sys-
tem. What a good systems builder does is implement the least c omplex
system that achieves the task at hand. For example, if disk sp ace is abun-
dant, you shouldn’t design a ﬁle system that works hard to use as few
bytes as possible; similarly , if processors are fast, it is b etter to write a
clean and understandable module within the OS than perhaps t he most
CPU-optimized, hand-assembled code for the task at hand. Be wary of
needless complexity , in prematurely-optimized code or other forms; such
approaches make systems harder to understand, maintain, an d debug.
As Antoine de Saint-Exupery famously wrote: “Perfection is ﬁnally at-
tained not when there is no longer anything to add, but when th ere is no
longer anything to take away .” What he didn’t write: “It’s a l ot easier to
say something about perfection than to actually achieve it. ”
In this example, virtual pages 0 and 1 are for code, virtual pa ges 4 and
5 for the heap, and virtual pages 254 and 255 for the stack; the rest of the
pages of the address space are unused.
To build a two-level page table for this address space, we sta rt with
our full linear page table and break it up into page-sized uni ts. Recall our
full table (in this example) has 256 entries; assume each PTE is 4 bytes in
size. Thus, our page table is 1KB (256 × 4 bytes) in size. Given that we
have 64-byte pages, the 1-KB page table can be divided into 16 64-byte
pages; each page can hold 16 PTEs.
What we need to understand now is how to take a VPN and use it to
index ﬁrst into the page directory and then into the page of the page table.
Remember that each is an array of entries; thus, all we need to ﬁgure out
is how to construct the index for each from pieces of the VPN.
Let’s ﬁrst index into the page directory . Our page table in th is example
is small: 256 entries, spread across 16 pages. The page directory needs one
entry per page of the page table; thus, it has 16 entries. As a r esult, we
need four bits of the VPN to index into the directory; we use th e top four
bits of the VPN, as follows:
13 12 11 10 9 8 7 6 5 4 3 2 1 0
VPN offset
Page Directory Index
Once we extract the page-directory index (PDIndex for short) from
the VPN, we can use it to ﬁnd the address of the page-directory entry
(PDE) with a simple calculation: PDEAddr = PageDirBase + (PDIndex
* sizeof(PDE)). This results in our page directory , which we now ex-
amine to make further progress in our translation.
If the page-directory entry is marked invalid, we know that t he access
is invalid, and thus raise an exception. If, however, the PDE is valid,
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 245

PAGING : S MALLER TABLES 209
we have more work to do. Speciﬁcally , we now have to fetch the p age-
table entry (PTE) from the page of the page table pointed to by this page-
directory entry . To ﬁnd this PTE, we have to index into the por tion of the
page table using the remaining bits of the VPN:
13 12 11 10 9 8 7 6 5 4 3 2 1 0
VPN offset
Page Directory Index Page Table Index
This page-table index (PTIndex for short) can then be used to index
into the page table itself, giving us the address of our PTE:
PTEAddr = (PDE.PFN << SHIFT) + (PTIndex * sizeof(PTE))
Note that the page-frame number (PFN) obtained from the page-directory
entry must be left-shifted into place before combining it wi th the page-
table index to form the address of the PTE.
To see if this all makes sense, we’ll now ﬁll in a multi-level p age ta-
ble with some actual values, and translate a single virtual a ddress. Let’s
begin with the page directory for this example (left side of Table
20.2).
In the ﬁgure, you can see that each page directory entry (PDE) de-
scribes something about a page of the page table for the addre ss space.
In this example, we have two valid regions in the address spac e (at the
beginning and end), and a number of invalid mappings in-betw een.
In physical page 100 (the physical frame number of the 0th pag e of the
page table), we have the ﬁrst page of 16 page table entries for the ﬁrst 16
VPNs in the address space. See Table 20.2 (middle part) for the contents
of this portion of the page table.
Page Directory Page of PT (@PFN:100) Page of PT (@PFN:101)
PFN valid? PFN valid prot PFN valid prot
100 1 10 1 r-x – 0 —
—— 0 23 1 r-x – 0 —
—— 0 – 0 — – 0 —
—— 0 – 0 — – 0 —
—— 0 80 1 rw- – 0 —
—— 0 59 1 rw- – 0 —
—— 0 – 0 — – 0 —
—— 0 – 0 — – 0 —
—— 0 – 0 — – 0 —
—— 0 – 0 — – 0 —
—— 0 – 0 — – 0 —
—— 0 – 0 — – 0 —
—— 0 – 0 — – 0 —
—— 0 – 0 — – 0 —
—— 0 – 0 — 55 1 rw-
101 1 – 0 — 45 1 rw-
Table 20.2: A Page Directory, And Pieces Of Page T able
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 246

210 PAGING : S MALLER TABLES
This page of the page table contains the mappings for the ﬁrst 16
VPNs; in our example, VPNs 0 and 1 are valid (the code segment) , as
are 4 and 5 (the heap). Thus, the table has mapping informatio n for each
of those pages. The rest of the entries are marked invalid.
The other valid page of page table is found inside PFN 101. Thi s page
contains mappings for the last 16 VPNs of the address space; s ee Table
20.2 (right) for details.
In the example, VPNs 254 and 255 (the stack) have valid mappin gs.
Hopefully , what we can see from this example is how much spacesavings
are possible with a multi-level indexed structure. In this e xample, instead
of allocating the full sixteen pages for a linear page table, we allocate only
three: one for the page directory , and two for the chunks of the page table
that have valid mappings. The savings for large (32-bit or 64 -bit) address
spaces could obviously be much greater.
Finally , let’s use this information in order to perform a tra nslation.
Here is an address that refers to the 0th byte of VPN 254: 0x3F80, or
11 1111 1000 0000 in binary .
Recall that we will use the top 4 bits of the VPN to index into th e
page directory . Thus, 1111 will choose the last (15th, if you start at the
0th) entry of the page directory above. This points us to a val id page
of the page table located at address 101. We then use the next 4 bits
of the VPN ( 1110) to index into that page of the page table and ﬁnd
the desired PTE. 1110 is the next-to-last (14th) entry on the page, and
tells us that page 254 of our virtual address space is mapped a t physi-
cal page 55. By concatenating PFN=55 (or hex 0x37) with offset=000000,
we can thus form our desired physical address and issue the re quest to
the memory system: PhysAddr = (PTE.PFN << SHIFT) + offset
= 00 1101 1100 0000 = 0x0DC0 .
You should now have some idea of how to construct a two-level p age
table, using a page directory which points to pages of the pag e table. Un-
fortunately , however, our work is not done. As we’ll now disc uss, some-
times two levels of page table is not enough!
More Than Two Levels
In our example thus far, we’ve assumed that multi-level page tables only
have two levels: a page directory and then pieces of the page t able. In
some cases, a deeper tree is possible (and indeed, needed).
Let’s take a simple example and use it to show why a deeper mult i-
level table can be useful. In this example, assume we have a 30 -bit virtual
address space, and a small (512 byte) page. Thus our virtual a ddress has
a 21-bit virtual page number component and a 9-bit offset.
Remember our goal in constructing a multi-level page table: to make
each piece of the page table ﬁt within a single page. Thus far, we’ve only
considered the page table itself; however, what if the page d irectory gets
too big?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 247

PAGING : S MALLER TABLES 211
To determine how many levels are needed in a multi-level tabl e to
make all pieces of the page table ﬁt within a page, we start by determining
how many page-table entries ﬁt within a page. Given our page s ize of 512
bytes, and assuming a PTE size of 4 bytes, you should see that y ou can ﬁt
128 PTEs on a single page. When we index into a page of the page t able,
we can thus conclude we’ll need the least signiﬁcant 7 bits ( log2128) of
the VPN as an index:
29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
VPN offset
Page Directory Index Page Table Index
What you also might notice from the diagram above is how many b its
are left into the (large) page directory: 14. If our page dire ctory has 214
entries, it spans not one page but 128, and thus our goal of mak ing every
piece of the multi-level page table ﬁt into a page vanishes.
To remedy this problem, we build a further level of the tree, b y split-
ting the page directory itself into multiple pages, and then adding another
page directory on top of that, to point to the pages of the page directory .
We can thus split up our virtual address as follows:
29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
VPN offset
PD Index 0 PD Index 1 Page Table Index
Now , when indexing the upper-level page directory , we use th e very
top bits of the virtual address ( PD Index 0 in the diagram); this index
can be used to fetch the page-directory entry from the top-le vel page di-
rectory . If valid, the second level of the page directory is c onsulted by
combining the physical frame number from the top-level PDE a nd the
next part of the VPN ( PD Index 1 ). Finally , if valid, the PTE address
can be formed by using the page-table index combined with the address
from the second-level PDE. Whew! That’s a lot of work. And all just to
look something up in a multi-level table.
The T ranslation Process: Remember the TLB
To summarize the entire process of address translation usin g a two-level
page table, we once again present the control ﬂow in algorith mic form
(Figure
20.4). The ﬁgure shows what happens in hardware (assuming a
hardware-managed TLB) upon every memory reference.
As you can see from the ﬁgure, before any of the complicated mu lti-
level page table access occurs, the hardware ﬁrst checks the TLB; upon
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 248

212 PAGING : S MALLER TABLES
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
11 // first, get page directory entry
12 PDIndex = (VPN & PD_MASK) >> PD_SHIFT
13 PDEAddr = PDBR + (PDIndex * sizeof(PDE))
14 PDE = AccessMemory(PDEAddr)
15 if (PDE.Valid == False)
16 RaiseException(SEGMENTATION_FAULT)
17 else
18 // PDE is valid: now fetch PTE from page table
19 PTIndex = (VPN & PT_MASK) >> PT_SHIFT
20 PTEAddr = (PDE.PFN << SHIFT) + (PTIndex * sizeof(PTE))
21 PTE = AccessMemory(PTEAddr)
22 if (PTE.Valid == False)
23 RaiseException(SEGMENTATION_FAULT)
24 else if (CanAccess(PTE.ProtectBits) == False)
25 RaiseException(PROTECTION_FAULT)
26 else
27 TLB_Insert(VPN, PTE.PFN, PTE.ProtectBits)
28 RetryInstruction()
Figure 20.4: Multi-level Page T able Control Flow
a hit, the physical address is formed directly without accessing the page
table at all, as before. Only upon a TLB miss does the hardware need to
perform the full multi-level lookup. On this path, you can se e the cost of
our traditional two-level page table: two additional memor y accesses to
look up a valid translation.
20.4 Inverted Page Tables
An even more extreme space savings in the world of page tables is
found with inverted page tables . Here, instead of having many page
tables (one per process of the system), we keep a single page t able that
has an entry for each physical page of the system. The entry tells us which
process is using this page, and which virtual page of that pro cess maps to
this physical page.
Finding the correct entry is now a matter of searching throug h this
data structure. A linear scan would be expensive, and thus a h ash table is
often built over the base structure to speed lookups. The Pow erPC is one
example of such an architecture [JM98].
More generally , inverted page tables illustrate what we’ve said from
the beginning: page tables are just data structures. You can do lots of
crazy things with data structures, making them smaller or bigger, making
them slower or faster. Multi-level and inverted page tables are just two
examples of the many things one could do.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 249

PAGING : S MALLER TABLES 213
20.5 Swapping the Page Tables to Disk
Finally , we discuss the relaxation of one ﬁnal assumption. T hus far,
we have assumed that page tables reside in kernel-owned phys ical mem-
ory . Even with our many tricks to reduce the size of page table s, it is still
possible, however, that they may be too big to ﬁt into memory a ll at once.
Thus, some systems place such page tables in kernel virtual memory ,
thereby allowing the system to swap some of these page tables to disk
when memory pressure gets a little tight. We’ll talk more abo ut this in
a future chapter (namely , the case study on V AX/VMS), once we under-
stand how to move pages in and out of memory in more detail.
20.6 Summary
We have now seen how real page tables are built; not necessari ly just
as linear arrays but as more complex data structures. The tra de-offs such
tables present are in time and space – the bigger the table, th e faster a TLB
miss can be serviced, as well as the converse – and thus the rig ht choice of
structure depends strongly on the constraints of the given e nvironment.
In a memory-constrained system (like many older systems), small struc-
tures make sense; in a system with a reasonable amount of memo ry and
with workloads that actively use a large number of pages, a bi gger ta-
ble that speeds up TLB misses might be the right choice. With s oftware-
managed TLBs, the entire space of data structures opens up to the delight
of the operating system innovator (hint: that’s you). What n ew struc-
tures can you come up with? What problems do they solve? Think of
these questions as you fall asleep, and dream the big dreams t hat only
operating-system developers can dream.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 250

214 PAGING : S MALLER TABLES
References
[BOH10] “Computer Systems: A Programmer’s Perspective”
Randal E. Bryant and David R. O’Hallaron
Addison-Wesley , 2010
We have yet to ﬁnd a good ﬁrst reference to the multi-level pag e table. However, this great textbook by
Bryant and O’Hallaron dives into the details of x86, which at least is an early system that used such
structures. It’s also just a great book to have.
[JM98] “Virtual Memory: Issues of Implementation”
Bruce Jacob and Trevor Mudge
IEEE Computer, June 1998
An excellent survey of a number of different systems and thei r approach to virtualizing memory. Plenty
of details on x86, PowerPC, MIPS, and other architectures.
[LL82] “Virtual Memory Management in the V AX/VMS Operating System”
Hank Levy and P . Lipman
IEEE Computer, V ol. 15, No. 3, March 1982
A terriﬁc paper about a real virtual memory manager in a class ic operating system, VMS. So terriﬁc, in
fact, that we’ll use it to review everything we’ve learned ab out virtual memory thus far a few chapters
from now.
[M28] “Reese’s Peanut Butter Cups”
Mars Candy Corporation.
Apparently these ﬁne confections were invented in 1928 by Ha rry Burnett Reese, a former dairy farmer
and shipping foreman for one Milton S. Hershey. At least, tha t is what it says on Wikipedia. If true,
Hershey and Reese probably hated each other’s guts, as any tw o chocolate barons should.
[N+02] “Practical, Transparent Operating System Support f or Superpages”
Juan Navarro, Sitaram Iyer, Peter Druschel, Alan Cox
OSDI ’02, Boston, Massachusetts, October 2002
A nice paper showing all the details you have to get right to in corporate large pages, or superpages,
into a modern OS. Not as easy as you might think, alas.
[M07] “Multics: History”
Available: http://www.multicians.org/history.html
This amazing web site provides a huge amount of history on the Multics system, certainly one of the
most inﬂuential systems in OS history. The quote from therei n: “Jack Dennis of MIT contributed
inﬂuential architectural ideas to the beginning of Multics , especially the idea of combining paging and
segmentation.” (from Section 1.2.1)
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 251

PAGING : S MALLER TABLES 215
Homework
This fun little homework tests if you understand how a multi- level
page table works. And yes, there is some debate over the use of the term
“fun” in the previous sentence. The program is called, perha ps unsur-
prisingly: paging-multilevel-translate.py; see the README for
details.
Questions
• With a linear page table, you need a single register to locate the
page table, assuming that hardware does the lookup upon a TLB
miss. How many registers do you need to locate a two-level pag e
table? A three-level table?
• Use the simulator to perform translations given random seed s 0,
1, and 2, and check your answers using the -c ﬂag. How many
memory references are needed to perform each lookup?
• Given your understanding of how cache memory works, how do
you think memory references to the page table will behave in t he
cache? Will they lead to lots of cache hits (and thus fast acce sses?)
Or lots of misses (and thus slow accesses)?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 253

21
Beyond Physical Memory: Mechanisms
Thus far, we’ve assumed that an address space is unrealistic ally small
and ﬁts into physical memory . In fact, we’ve been assuming th at every
address space of every running process ﬁts into memory . We wi ll now
relax these big assumptions, and assume that we wish to suppo rt many
concurrently-running large address spaces.
To do so, we require an additional level in the memory hierarchy .
Thus far, we have assumed that all pages reside in physical me mory .
However, to support large address spaces, the OS will need a p lace to
stash away portions of address spaces that currently aren’t in great de-
mand. In general, the characteristics of such a location are that it should
have more capacity than memory; as a result, it is generally s lower (if it
were faster, we would just use it as memory , no?). In modern sy stems,
this role is usually served by a hard disk drive . Thus, in our memory
hierarchy , big and slow hard drives sit at the bottom, with me mory just
above. And thus we arrive at the crux of the problem:
THE CRUX : H OW TO GO BEYOND PHYSICAL MEMORY
How can the OS make use of a larger, slower device to transpare ntly pro-
vide the illusion of a large virtual address space?
One question you might have: why do we want to support a single
large address space for a process? Once again, the answer is c onvenience
and ease of use. With a large address space, you don’t have to w orry
about if there is room enough in memory for your program’s dat a struc-
tures; rather, you just write the program naturally , alloca ting memory as
needed. It is a powerful illusion that the OS provides, and ma kes your
life vastly simpler. You’re welcome! A contrast is found in o lder systems
that used memory overlays , which required programmers to manually
move pieces of code or data in and out of memory as they were nee ded
[D97]. Try imagining what this would be like: before calling a function or
accessing some data, you need to ﬁrst arrange for the code or d ata to be
in memory; yuck!
217

## Page 254

218 BEYOND PHYSICAL MEMORY : M ECHANISMS
ASIDE : STORAGE TECHNOLOGIES
We’ll delve much more deeply into how I/O devices actually wo rk later
(see the chapter on I/O devices). So be patient! And of course the slower
device need not be a hard disk, but could be something more mod ern
such as a Flash-based SSD. We’ll talk about those things too. For now ,
just assume we have a big and relatively-slow device which we can use
to help us build the illusion of a very large virtual memory , e ven bigger
than physical memory itself.
Beyond just a single process, the addition of swap space allo ws the OS
to support the illusion of a large virtual memory for multiple concurrently-
running processes. The invention of multiprogramming (run ning multi-
ple programs “at once”, to better utilize the machine) almos t demanded
the ability to swap out some pages, as early machines clearly could not
hold all the pages needed by all processes at once. Thus, the c ombina-
tion of multiprogramming and ease-of-use leads us to want to support
using more memory than is physically available. It is someth ing that all
modern VM systems do; it is now something we will learn more ab out.
21.1 Swap Space
The ﬁrst thing we will need to do is to reserve some space on the disk
for moving pages back and forth. In operating systems, we generally refer
to such space as swap space, because we swap pages out of memory to it
and swap pages into memory from it. Thus, we will simply assume that
the OS can read from and write to the swap space, in page-sized units. To
do so, the OS will need to remember the disk address of a given page.
The size of the swap space is important, as ultimately it dete rmines
the maximum number of memory pages that can be in use by a syste m at
a given time. Let us assume for simplicity that it is very large for now .
In the tiny example (Figure 21.1), you can see a little example of a 4-
page physical memory and an 8-page swap space. In the example , three
processes (Proc 0, Proc 1, and Proc 2) are actively sharing ph ysical mem-
ory; each of the three, however, only have some of their valid pages in
memory , with the rest located in swap space on disk. A fourth p rocess
(Proc 3) has all of its pages swapped out to disk, and thus clea rly isn’t
currently running. One block of swap remains free. Even from this tiny
example, hopefully you can see how using swap space allows th e system
to pretend that memory is larger than it actually is.
We should note that swap space is not the only on-disk locatio n for
swapping trafﬁc. For example, assume you are running a progr am binary
(e.g., ls, or your own compiled main program). The code pages from this
binary are initially found on disk, and when the program runs , they are
loaded into memory (either all at once when the program starts execution,
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 255

BEYOND PHYSICAL MEMORY : M ECHANISMS 219
Physical
Memory
PFN 0
Proc 0
[VPN 0]
PFN 1
Proc 1
[VPN 2]
PFN 2
Proc 1
[VPN 3]
PFN 3
Proc 2
[VPN 0]
Swap
Space
Proc 0
[VPN 1]
Block 0
Proc 0
[VPN 2]
Block 1
[Free]
Block 2
Proc 1
[VPN 0]
Block 3
Proc 1
[VPN 1]
Block 4
Proc 3
[VPN 0]
Block 5
Proc 2
[VPN 1]
Block 6
Proc 3
[VPN 1]
Block 7
Figure 21.1: Physical Memory and Swap Space
or, as in modern systems, one page at a time when needed). Howe ver, if
the system needs to make room in physical memory for other nee ds, it
can safely re-use the memory space for these code pages, know ing that it
can later swap them in again from the on-disk binary in the ﬁle system.
21.2 The Present Bit
Now that we have some space on the disk, we need to add some ma-
chinery higher up in the system in order to support swapping p ages to
and from the disk. Let us assume, for simplicity , that we have a system
with a hardware-managed TLB.
Recall ﬁrst what happens on a memory reference. The running p ro-
cess generates virtual memory references (for instruction fetches, or data
accesses), and, in this case, the hardware translates them i nto physical
addresses before fetching the desired data from memory .
Remember that the hardware ﬁrst extracts the VPN from the vir tual
address, checks the TLB for a match (a TLB hit), and if a hit, produces the
resulting physical address and fetches it from memory . This is hopefully
the common case, as it is fast (requiring no additional memor y accesses).
If the VPN is not found in the TLB (i.e., a TLB miss ), the hardware
locates the page table in memory (using the page table base register )
and looks up the page table entry (PTE) for this page using the VPN
as an index. If the page is valid and present in physical memor y , the
hardware extracts the PFN from the PTE, installs it in the TLB , and retries
the instruction, this time generating a TLB hit; so far, so go od.
If we wish to allow pages to be swapped to disk, however, we mus t
add even more machinery . Speciﬁcally , when the hardware loo ks in the
PTE, it may ﬁnd that the page is not present in physical memory . The way
the hardware (or the OS, in a software-managed TLB approach) deter-
mines this is through a new piece of information in each page- table entry ,
known as the present bit . If the present bit is set to one, it means the
page is present in physical memory and everything proceeds a s above; if
it is set to zero, the page is not in memory but rather on disk somewhere.
The act of accessing a page that is not in physical memory is co mmonly
referred to as a page fault.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 256

220 BEYOND PHYSICAL MEMORY : M ECHANISMS
ASIDE : SWAPPING TERMINOLOGY AND OTHER THINGS
Terminology in virtual memory systems can be a little confusing and vari-
able across machines and operating systems. For example, a page fault
more generally could refer to any reference to a page table th at generates
a fault of some kind: this could include the type of fault we ar e discussing
here, i.e., a page-not-present fault, but sometimes can refer to illegal mem-
ory accesses. Indeed, it is odd that we call what is deﬁnitely a legal access
(to a page mapped into the virtual address space of a process, but simply
not in physical memory at the time) a “fault” at all; really , i t should be
called a page miss. But often, when people say a program is “page fault-
ing”, they mean that it is accessing parts of its virtual addr ess space that
the OS has swapped out to disk.
We suspect the reason that this behavior became known as a “fa ult” re-
lates to the machinery in the operating system to handle it. W hen some-
thing unusual happens, i.e., when something the hardware do esn’t know
how to handle occurs, the hardware simply transfers control to the OS,
hoping it can make things better. In this case, a page that a pr ocess wants
to access is missing from memory; the hardware does the only t hing it
can, which is raise an exception, and the OS takes over from th ere. As
this is identical to what happens when a process does somethi ng illegal,
it is perhaps not surprising that we term the activity a “faul t.”
Upon a page fault, the OS is invoked to service the page fault. A partic-
ular piece of code, known as a page-fault handler, runs, and must service
the page fault, as we now describe.
21.3 The Page Fault
Recall that with TLB misses, we have two types of systems: har dware-
managed TLBs (where the hardware looks in the page table to ﬁn d the
desired translation) and software-managed TLBs (where the OS does). In
either type of system, if a page is not present, the OS is put in charge to
handle the page fault. The appropriately-named OS page-fault handler
runs to determine what to do. Virtually all systems handle pa ge faults in
software; even with a hardware-managed TLB, the hardware tr usts the
OS to manage this important duty .
If a page is not present and has been swapped to disk, the OS wil l need
to swap the page into memory in order to service the page fault . Thus, a
question arises: how will the OS know where to ﬁnd the desired page? In
many systems, the page table is a natural place to store such i nformation.
Thus, the OS could use the bits in the PTE normally used for dat a such as
the PFN of the page for a disk address. When the OS receives a pa ge fault
for a page, it looks in the PTE to ﬁnd the address, and issues th e request
to disk to fetch the page into memory .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 257

BEYOND PHYSICAL MEMORY : M ECHANISMS 221
ASIDE : WHY HARDWARE DOESN ’ T HANDLE PAGE FAULTS
We know from our experience with the TLB that hardware design ers are
loathe to trust the OS to do much of anything. So why do they tru st the
OS to handle a page fault? There are a few main reasons. First, page
faults to disk are slow; even if the OS takes a long time to handle a fault,
executing tons of instructions, the disk operation itself i s traditionally so
slow that the extra overheads of running software are minima l. Second,
to be able to handle a page fault, the hardware would have to un derstand
swap space, how to issue I/Os to the disk, and a lot of other det ails which
it currently doesn’t know much about. Thus, for both reasons of perfor-
mance and simplicity , the OS handles page faults, and even ha rdware
types can be happy .
When the disk I/O completes, the OS will then update the page t able
to mark the page as present, update the PFN ﬁeld of the page-ta ble entry
(PTE) to record the in-memory location of the newly-fetched page, and
retry the instruction. This next attempt may generate a TLB m iss, which
would then be serviced and update the TLB with the translatio n (one
could alternately update the TLB upon when servicing the pag e fault,
to avoid this step). Finally , a last restart would ﬁnd the tra nslation in
the TLB and thus proceed to fetch the desired data or instruct ion from
memory at the translated physical address.
Note that while the I/O is in ﬂight, the process will be in the blocked
state. Thus, the OS will be free to run other ready processes w hile the
page fault is being serviced. Because I/O is expensive, this overlap of
the I/O (page fault) of one process and the execution of anoth er is yet
another way a multiprogrammed system can make the most effec tive use
of its hardware.
21.4 What If Memory Is Full?
In the process described above, you may notice that we assume d there
is plenty of free memory in which to page in a page from swap space.
Of course, this may not be the case; memory may be full (or clos e to it).
Thus, the OS might like to ﬁrst page out one or more pages to make room
for the new page(s) the OS is about to bring in. The process of p icking a
page to kick out, or replace is known as the page-replacement policy.
As it turns out, a lot of thought has been put into creating a go od page-
replacement policy , as kicking out the wrong page can exact a great cost
on program performance. Making the wrong decision can cause a pro-
gram to run at disk-like speeds instead of memory-like speed s; in cur-
rent technology that means a program could run 10,000 or 100, 000 times
slower. Thus, such a policy is something we should study in so me detail;
indeed, that is exactly what we will do in the next chapter. Fo r now , it is
good enough to understand that such a policy exists, built on top of the
mechanisms described here.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 258

222 BEYOND PHYSICAL MEMORY : M ECHANISMS
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
11 PTEAddr = PTBR + (VPN * sizeof(PTE))
12 PTE = AccessMemory(PTEAddr)
13 if (PTE.Valid == False)
14 RaiseException(SEGMENTATION_FAULT)
15 else
16 if (CanAccess(PTE.ProtectBits) == False)
17 RaiseException(PROTECTION_FAULT)
18 else if (PTE.Present == True)
19 // assuming hardware-managed TLB
20 TLB_Insert(VPN, PTE.PFN, PTE.ProtectBits)
21 RetryInstruction()
22 else if (PTE.Present == False)
23 RaiseException(PAGE_FAULT)
Figure 21.2: Page-Fault Control Flow Algorithm (Hardware)
21.5 Page Fault Control Flow
With all of this knowledge in place, we can now roughly sketch the
complete control ﬂow of memory access. In other words, when s ome-
body asks you “what happens when a program fetches some data f rom
memory?”, you should have a pretty good idea of all the differ ent pos-
sibilities. See the control ﬂow in Figures 21.2 and 21.3 for more details;
the ﬁrst ﬁgure shows what the hardware does during translati on, and the
second what the OS does upon a page fault.
From the hardware control ﬂow diagram in Figure 21.2, notice that
there are now three important cases to understand when a TLB m iss oc-
curs. First, that the page was both present and valid (Lines 18–21); in
this case, the TLB miss handler can simply grab the PFN from th e PTE,
retry the instruction (this time resulting in a TLB hit), and thus continue
as described (many times) before. In the second case (Lines 2 2–23), the
page fault handler must be run; although this was a legitimat e page for
the process to access (it is valid, after all), it is not prese nt in physical
memory . Third (and ﬁnally), the access could be to an invalid page, due
for example to a bug in the program (Lines 13–14). In this case , no other
bits in the PTE really matter; the hardware traps this invali d access, and
the OS trap handler runs, likely terminating the offending p rocess.
From the software control ﬂow in Figure 21.3, we can see what the OS
roughly must do in order to service the page fault. First, the OS must ﬁnd
a physical frame for the soon-to-be-faulted-in page to resi de within; if
there is no such page, we’ll have to wait for the replacement a lgorithm to
run and kick some pages out of memory , thus freeing them for us e here.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 259

BEYOND PHYSICAL MEMORY : M ECHANISMS 223
1 PFN = FindFreePhysicalPage()
2 if (PFN == -1) // no free page found
3 PFN = EvictPage() // run replacement algorithm
4 DiskRead(PTE.DiskAddr, pfn) // sleep (waiting for I/O)
5 PTE.present = True // update page table with present
6 PTE.PFN = PFN // bit and translation (PFN)
7 RetryInstruction() // retry instruction
Figure 21.3: Page-Fault Control Flow Algorithm (Software)
With a physical frame in hand, the handler then issues the I/O request
to read in the page from swap space. Finally , when that slow op eration
completes, the OS updates the page table and retries the inst ruction. The
retry will result in a TLB miss, and then, upon another retry , a TLB hit, at
which point the hardware will be able to access the desired it em.
21.6 When Replacements Really Occur
Thus far, the way we’ve described how replacements occur ass umes
that the OS waits until memory is entirely full, and only then replaces
(evicts) a page to make room for some other page. As you can ima gine,
this is a little bit unrealistic, and there are many reasons for the OS to keep
a small portion of memory free more proactively .
To keep a small amount of memory free, most operating systems thus
have some kind of high watermark (HW ) and low watermark (LW ) to
help decide when to start evicting pages from memory . How this works is
as follows: when the OS notices that there are fewer than LW pages avail-
able, a background thread that is responsible for freeing me mory runs.
The thread evicts pages until there are HW pages available. The back-
ground thread, sometimes called the swap daemon or page daemon 1,
then goes to sleep, happy that is has freed some memory for run ning pro-
cesses and the OS to use.
By performing a number of replacements at once, new performa nce
optimizations become possible. For example, many systems w ill cluster
or group a number of pages and write them out at once to the swap parti-
tion, thus increasing the efﬁciency of the disk [LL82]; as we will see later
when we discuss disks in more detail, such clustering reduce s seek and
rotational overheads of a disk and thus increases performan ce noticeably .
To work with the background paging thread, the control ﬂow inFigure
21.3 should be modiﬁed slightly; instead of performing a replace ment
directly , the algorithm would instead simply check if there are any free
pages available. If not, it would signal that the background paging thread
that free pages are needed; when the thread frees up some pages, it would
re-awaken the original thread, which could then page in the d esired page
and go about its work.
1The word “daemon”, usually pronounced “demon”, is an old ter m for a background
thread or process that does something useful. Turns out (onc e again!) that the source of the
term is Multics [CS94].
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 260

224 BEYOND PHYSICAL MEMORY : M ECHANISMS
TIP : D O WORK IN THE BACKGROUND
When you have some work to do, it is often a good idea to do it in t he
background to increase efﬁciency and to allow for grouping of opera-
tions. Operating systems often do work in the background; fo r example,
many systems buffer ﬁle writes in memory before actually wri ting the
data to disk. Doing so has many possible beneﬁts: increased d isk efﬁ-
ciency , as the disk may now receive many writes at once and thu s better
be able to schedule them; improved latency of writes, as the a pplication
thinks the writes completed quite quickly; the possibility of work reduc-
tion, as the writes may need never to go to disk (i.e., if the ﬁl e is deleted);
and better use of idle time , as the background work may possibly be
done when the system is otherwise idle, thus better utilizin g the hard-
ware [G+95].
21.7 Summary
In this brief chapter, we have introduced the notion of acces sing more
memory than is physically present within a system. To do so re quires
more complexity in page-table structures, as a present bit (of some kind)
must be included to tell us whether the page is present in memo ry or not.
When not, the operating system page-fault handler runs to service the
page fault , and thus arranges for the transfer of the desired page from
disk to memory , perhaps ﬁrst replacing some pages in memory t o make
room for those soon to be swapped in.
Recall, importantly (and amazingly!), that these actions a ll take place
transparently to the process. As far as the process is concerned, it is just
accessing its own private, contiguous virtual memory . Behind the scenes,
pages are placed in arbitrary (non-contiguous) locations in physical mem-
ory , and sometimes they are not even present in memory , requiring a fetch
from disk. While we hope that in the common case a memory acces s is
fast, in some cases it will take multiple disk operations to s ervice it; some-
thing as simple as performing a single instruction can, in th e worst case,
take many milliseconds to complete.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 261

BEYOND PHYSICAL MEMORY : M ECHANISMS 225
References
[CS94] “Take Our Word For It”
F. Corbato and R. Steinberg
Available: http://www.takeourword.com/TOW146/page4.html
Richard Steinberg writes: “Someone has asked me the origin o f the word daemon as it applies to comput-
ing. Best I can tell based on my research, the word was ﬁrst use d by people on your team at Project MAC
using the IBM 7094 in 1963.” Professor Corbato replies: “Our use of the word daemon was inspired
by the Maxwell’s daemon of physics and thermodynamics (my ba ckground is in physics). Maxwell’s
daemon was an imaginary agent which helped sort molecules of different speeds and worked tirelessly
in the background. We fancifully began to use the word daemon to describe background processes which
worked tirelessly to perform system chores.”
[D97] “Before Memory Was Virtual”
Peter Denning
From In the Beginning: Recollections of Software Pioneers , Wiley , November 1997
An excellent historical piece by one of the pioneers of virtu al memory and working sets.
[G+95] “Idleness is not sloth”
Richard Golding, Peter Bosch, Carl Staelin, Tim Sullivan, J ohn Wilkes
USENIX ATC ’95, New Orleans, Louisiana
A fun and easy-to-read discussion of how idle time can be bett er used in systems, with lots of good
examples.
[LL82] “Virtual Memory Management in the V AX/VMS Operating System”
Hank Levy and P . Lipman
IEEE Computer, V ol. 15, No. 3, March 1982
Not the ﬁrst place where such clustering was used, but a clear and simple explanation of how such a
mechanism works.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 263

22
Beyond Physical Memory: Policies
In a virtual memory manager, life is easy when you have a lot of free
memory . A page fault occurs, you ﬁnd a free page on the free-pa ge list,
and assign it to the faulting page. Hey , Operating System, co ngratula-
tions! You did it again.
Unfortunately , things get a little more interesting when li ttle memory
is free. In such a case, this memory pressure forces the OS to start paging
out pages to make room for actively-used pages. Deciding which p age
(or pages) to evict is encapsulated within the replacement policy of the
OS; historically , it was one of the most important decisions the early vir-
tual memory systems made, as older systems had little physic al memory .
Minimally , it is an interesting set of policies worth knowin g a little more
about. And thus our problem:
THE CRUX : H OW TO DECIDE WHICH PAGE TO EVICT
How can the OS decide which page (or pages) to evict from memor y?
This decision is made by the replacement policy of the system, which usu-
ally follows some general principles (discussed below) but also includes
certain tweaks to avoid corner-case behaviors.
22.1 Cache Management
Before diving into policies, we ﬁrst describe the problem we are trying
to solve in more detail. Given that main memory holds some sub set of
all the pages in the system, it can rightly be viewed as a cache for virtual
memory pages in the system. Thus, our goal in picking a replac ement
policy for this cache is to minimize the number of cache misses; that is,
to minimize the number of times that we have to go to disk to fet ch the
desired page. Alternately , one can view our goal as maximizing the num-
ber of cache hits , i.e., the number of times a page that is read or written
is found in memory .
227

## Page 264

228 BEYOND PHYSICAL MEMORY : P OLICIES
Knowing the number of cache hits and misses let us calculate t he av-
erage memory access time (AMA T) for a program (a metric computer
architects compute for hardware caches [HP06]). Speciﬁcal ly , given these
values, we can compute the AMAT of a program as follows:
AM AT = ( Hit % · TM ) + (M iss% · TD) (22.1)
where TM represents the cost of accessing memory , and representsTD the
cost of accessing disk.
For example, let us imagine a machine with a (tiny) address sp ace:
4KB, with 256-byte pages. Thus, a virtual address has two com ponents: a
4-bit VPN (the most-signiﬁcant bits) and an 8-bit offset (the least-signiﬁcant
bits). Thus, a process in this example can access 24 or 16 total virtual
pages. In this example, the process generates the following memory ref-
erences (i.e., virtual addresses): 0x000, 0x100, 0x200, 0x 300, 0x400, 0x500,
0x600, 0x700, 0x800, 0x900. These virtual addresses refer t o the ﬁrst byte
of each of the ﬁrst ten pages of the address space (the page num ber being
the ﬁrst hex digit of each virtual address).
Let us further assume that every page except virtual page 3 are already
in memory . Thus, our sequence of memory references will enco unter the
following behavior: hit, hit, hit, miss, hit, hit, hit, hit, hit, hit. We can
compute the hit rate (the percent of references found in memory): 90%,
as 9 out of 10 references are in memory . The miss rate is obviously 10%.
To calculate AMAT, we simply need to know the cost of accessin g
memory and the cost of accessing disk. Assuming the cost of ac cess-
ing memory ( TM ) is around 100 nanoseconds, and the cost of access-
ing disk ( TD) is about 10 milliseconds, we have the following AMAT:
0.9 · 100ns + 0.1 · 10ms, which is 90ns + 1ms, or 1.00009 ms, or about
1 millisecond. If our hit rate had instead been 99.9%, the res ult is quite
different: AMAT is 10.1 microseconds, or roughly 100 times f aster. As the
hit rate approaches 100%, AMAT approaches 100 nanoseconds.
Unfortunately , as you can see in this example, the cost of dis k access
is so high in modern systems that even a tiny miss rate will qui ckly dom-
inate the overall AMAT of running programs. Clearly , we need to avoid
as many misses as possible or run slowly , at the rate of the dis k. One way
to help with this is to carefully develop a smart policy , as we now do.
22.2 The Optimal Replacement Policy
To better understand how a particular replacement policy wo rks, it
would be nice to compare it to the best possible replacement p olicy . As it
turns out, such an optimal policy was developed by Belady many years
ago [B66] (he originally called it MIN). The optimal replace ment policy
leads to the fewest number of misses overall. Belady showed t hat a sim-
ple (but, unfortunately , difﬁcult to implement!) approach that replaces
the page that will be accessed furthest in the future is the optimal policy ,
resulting in the fewest-possible cache misses.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 265

BEYOND PHYSICAL MEMORY : P OLICIES 229
TIP : C OMPARING AGAINST OPTIMAL IS USEFUL
Although optimal is not very practical as a real policy , it is incredibly
useful as a comparison point in simulation or other studies. Saying that
your fancy new algorithm has a 80% hit rate isn’t meaningful i n isolation;
saying that optimal achieves an 82% hit rate (and thus your new approach
is quite close to optimal) makes the result more meaningful a nd gives it
context. Thus, in any study you perform, knowing what the opt imal is
lets you perform a better comparison, showing how much impro vement
is still possible, and also when you can stop making your policy better,
because it is close enough to the ideal [AD03].
Hopefully , the intuition behind the optimal policy makes sense. Think
about it like this: if you have to throw out some page, why not t hrow
out the one that is needed the furthest from now? By doing so, y ou are
essentially saying that all the other pages in the cache are m ore important
than the one furthest out. The reason this is true is simple: y ou will refer
to the other pages before you refer to the one furthest out.
Let’s trace through a simple example to understand the decis ions the
optimal policy makes. Assume a program accesses the followi ng stream
of virtual pages: 0, 1, 2, 0, 1, 3, 0, 3, 1, 2, 1. Table 22.1 shows the behavior
of optimal, assuming a cache that ﬁts three pages.
In the table, you can see the following actions. Not surprisi ngly , the
ﬁrst three accesses are misses, as the cache begins in an empt y state; such
a miss is sometimes referred to as a cold-start miss (or compulsory miss).
Then we refer again to pages 0 and 1, which both hit in the cache . Finally ,
we reach another miss (to page 3), but this time the cache is fu ll; a re-
placement must take place! Which begs the question: which pa ge should
we replace? With the optimal policy , we examine the future for each page
currently in the cache (0, 1, and 2), and see that 0 is accessed almost imme-
diately , 1 is accessed a little later, and 2 is accessed furth est in the future.
Thus the optimal policy has an easy choice: evict page 2, resu lting in
pages 0, 1, and 3 in the cache. The next three references are hi ts, but then
Resulting
Access Hit/Miss? Evict Cache State
0 Miss 0
1 Miss 0, 1
2 Miss 0, 1, 2
0 Hit 0, 1, 2
1 Hit 0, 1, 2
3 Miss 2 0, 1, 3
0 Hit 0, 1, 3
3 Hit 0, 1, 3
1 Hit 0, 1, 3
2 Miss 3 0, 1, 2
1 Hit 0, 1, 2
Table 22.1: T racing the Optimal Policy
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 266

230 BEYOND PHYSICAL MEMORY : P OLICIES
ASIDE : TYPES OF CACHE MISSES
In the computer architecture world, architects sometimes ﬁ nd it useful
to characterize misses by type, into one of three categories : compulsory ,
capacity , and conﬂict misses, sometimes called the Three C’s [H87]. A
compulsory miss (or cold-start miss [EF78]) occurs because the cache is
empty to begin with and this is the ﬁrst reference to the item; in con-
trast, a capacity miss occurs because the cache ran out of space and had
to evict an item to bring a new item into the cache. The third ty pe of
miss (a conﬂict miss ) arises in hardware because of limits on where an
item can be placed in a hardware cache, due to something known as set-
associativity; it does not arise in the OS page cache because such caches
are always fully-associative, i.e., there are no restrictions on where in
memory a page can be placed. See H&P for details [HP06].
we get to page 2, which we evicted long ago, and suffer another miss.
Here the optimal policy again examines the future for each pa ge in the
cache (0, 1, and 3), and sees that as long as it doesn’t evict pa ge 1 (which
is about to be accessed), we’ll be OK. The example shows page 3 getting
evicted, although 0 would have been a ﬁne choice too. Finally , we hit on
page 1 and the trace completes.
We can also calculate the hit rate for the cache: with 6 hits and 5 misses,
the hit rate is Hits
Hits+M isses which is 6
6+5 or 54.6%. You can also compute
the hit rate modulo compulsory misses (i.e., ignore the ﬁrst miss to a given
page), resulting in a 85.7% hit rate.
Unfortunately , as we saw before in the development of schedu ling
policies, the future is not generally known; you can’t build the optimal
policy for a general-purpose operating system 1. Thus, in developing a
real, deployable policy , we will focus on approaches that ﬁnd some other
way to decide which page to evict. The optimal policy will thu s serve
only as a comparison point, to know how close we are to “perfec t”.
22.3 A Simple Policy: FIFO
Many early systems avoided the complexity of trying to appro ach
optimal and employed very simple replacement policies. For example,
some systems used FIFO (ﬁrst-in, ﬁrst-out) replacement, where pages
were simply placed in a queue when they enter the system; when a re-
placement occurs, the page on the tail of the queue (the “ﬁrst -in” page) is
evicted. FIFO has one great strength: it is quite simple to im plement.
Let’s examine how FIFO does on our example reference stream ( Table
22.2). We again begin our trace with three compulsory misses to pa ges 0,
1, and 2, and then hit on both 0 and 1. Next, page 3 is referenced , causing
a miss; the replacement decision is easy with FIFO: pick the p age that
1If you can, let us know! We can become rich together. Or, like t he scientists who “discov-
ered” cold fusion, widely scorned and mocked.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 267

BEYOND PHYSICAL MEMORY : P OLICIES 231
Resulting
Access Hit/Miss? Evict Cache State
0 Miss First-in → 0
1 Miss First-in → 0, 1
2 Miss First-in → 0, 1, 2
0 Hit First-in → 0, 1, 2
1 Hit First-in → 0, 1, 2
3 Miss 0 First-in → 1, 2, 3
0 Miss 1 First-in → 2, 3, 0
3 Hit First-in → 2, 3, 0
1 Miss 2 First-in → 3, 0, 1
2 Miss 3 First-in → 0, 1, 2
1 Hit First-in → 0, 1, 2
Table 22.2: T racing the FIFO Policy
was the “ﬁrst one” in (the cache state in the table is kept in FI FO order,
with the ﬁrst-in page on the left), which is page 0. Unfortuna tely , our next
access is to page 0, causing another miss and replacement (of page 1). We
then hit on page 3, but miss on 1 and 2, and ﬁnally hit on 3.
Comparing FIFO to optimal, FIFO does notably worse: a 36.4% h it
rate (or 57.1% excluding compulsory misses). FIFO simply ca n’t deter-
mine the importance of blocks: even though page 0 had been acc essed
a number of times, FIFO still kicks it out, simply because it w as the ﬁrst
one brought into memory .
ASIDE : BELADY ’ S ANOMALY
Belady (of the optimal policy) and colleagues found an inter esting refer-
ence stream that behaved a little unexpectedly [BNS69]. The memory-
reference stream: 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5. The replacem ent policy
they were studying was FIFO. The interesting part: how the ca che hit
rate changed when moving from a cache size of 3 to 4 pages.
In general, you would expect the cache hit rate to increase (get better)
when the cache gets larger. But in this case, with FIFO, it get s worse! Cal-
culate the hits and misses yourself and see. This odd behavior is generally
referred to as Belady’s Anomaly (to the chagrin of his co-authors).
Some other policies, such as LRU, don’t suffer from this prob lem. Can
you guess why? As it turns out, LRU has what is known as a stack prop-
erty [M+70]. For algorithms with this property , a cache of size N + 1
naturally includes the contents of a cache of size N . Thus, when increas-
ing the cache size, hit rate will either stay the same or impro ve. FIFO and
Random (among others) clearly do not obey the stack property , and thus
are susceptible to anomalous behavior.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 268

232 BEYOND PHYSICAL MEMORY : P OLICIES
Resulting
Access Hit/Miss? Evict Cache State
0 Miss 0
1 Miss 0, 1
2 Miss 0, 1, 2
0 Hit 0, 1, 2
1 Hit 0, 1, 2
3 Miss 0 1, 2, 3
0 Miss 1 2, 3, 0
3 Hit 2, 3, 0
1 Miss 3 2, 0, 1
2 Hit 2, 0, 1
1 Hit 2, 0, 1
Table 22.3: T racing the Random Policy
22.4 Another Simple Policy: Random
Another similar replacement policy is Random, which simply picks a
random page to replace under memory pressure. Random has pro perties
similar to FIFO; it is simple to implement, but it doesn’t rea lly try to be
too intelligent in picking which blocks to evict. Let’s look at how Random
does on our famous example reference stream (see Table
22.3).
Of course, how Random does depends entirely upon how lucky (o r
unlucky) Random gets in its choices. In the example above, Ra ndom does
a little better than FIFO, and a little worse than optimal. In fact, we can
run the Random experiment thousands of times and determine h ow it
does in general. Figure 22.1 shows how many hits Random achieves over
10,000 trials, each with a different random seed. As you can s ee, some-
times (just over 40% of the time), Random is as good as optimal, achieving
6 hits on the example trace; sometimes it does much worse, ach ieving 2
hits or fewer. How Random does depends on the luck of the draw .
0 1 2 3 4 5 6 7
0
10
20
30
40
50
Number of Hits
Frequency
Figure 22.1: Random Performance over 10,000 T rials
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 269

BEYOND PHYSICAL MEMORY : P OLICIES 233
Resulting
Access Hit/Miss? Evict Cache State
0 Miss LRU → 0
1 Miss LRU → 0, 1
2 Miss LRU → 0, 1, 2
0 Hit LRU → 1, 2, 0
1 Hit LRU → 2, 0, 1
3 Miss 2 LRU → 0, 1, 3
0 Hit LRU → 1, 3, 0
3 Hit LRU → 1, 0, 3
1 Hit LRU → 0, 3, 1
2 Miss 0 LRU → 3, 1, 2
1 Hit LRU → 3, 2, 1
Table 22.4: T racing the LRU Policy
22.5 Using History: LRU
Unfortunately , any policy as simple as FIFO or Random is like ly to
have a common problem: it might kick out an important page, on e that
is about to be referenced again. FIFO kicks out the page that w as ﬁrst
brought in; if this happens to be a page with important code or data
structures upon it, it gets thrown out anyhow , even though it will soon be
paged back in. Thus, FIFO, Random, and similar policies are n ot likely to
approach optimal; something smarter is needed.
As we did with scheduling policy , to improve our guess at the f uture,
we once again lean on the past and use history as our guide. For example,
if a program has accessed a page in the near past, it is likely t o access it
again in the near future.
One type of historical information a page-replacement poli cy could
use is frequency; if a page has been accessed many times, perhaps it
should not be replaced as it clearly has some value. A more com monly-
used property of a page is its recency of access; the more recently a page
has been accessed, perhaps the more likely it will be accesse d again.
This family of policies is based on what people refer to as the prin-
ciple of locality [D70], which basically is just an observation about pro-
grams and their behavior. What this principle says, quite si mply , is that
programs tend to access certain code sequences (e.g., in a lo op) and data
structures (e.g., an array accessed by the loop) quite frequently; we should
thus try to use history to ﬁgure out which pages are important , and keep
those pages in memory when it comes to eviction time.
And thus, a family of simple historically-based algorithms are born.
The Least-Frequently-Used (LFU) policy replaces the least-frequently-
used page when an eviction must take place. Similarly , theLeast-Recently-
Used (LRU) policy replaces the least-recently-used page. These algo -
rithms are easy to remember: once you know the name, you know e xactly
what it does, which is an excellent property for a name.
To better understand LRU, let’s examine how LRU does on our ex am-
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 270

234 BEYOND PHYSICAL MEMORY : P OLICIES
ASIDE : TYPES OF LOCALITY
There are two types of locality that programs tend to exhibit . The ﬁrst
is known as spatial locality , which states that if a page P is accessed,
it is likely the pages around it (say P − 1 or P + 1 ) will also likely be
accessed. The second is temporal locality , which states that pages that
have been accessed in the near past are likely to be accessed a gain in the
near future. The assumption of the presence of these types of locality
plays a large role in the caching hierarchies of hardware sys tems, which
deploy many levels of instruction, data, and address-trans lation caching
to help programs run fast when such locality exists.
Of course, the principle of locality , as it is often called, is no hard-and-
fast rule that all programs must obey . Indeed, some programs access
memory (or disk) in rather random fashion and don’t exhibit m uch or
any locality in their access streams. Thus, while locality i s a good thing to
keep in mind while designing caches of any kind (hardware or s oftware),
it does not guarantee success. Rather, it is a heuristic that often proves
useful in the design of computer systems.
ple reference stream. Table
22.4 shows the results. From the table, you
can see how LRU can use history to do better than stateless pol icies such
as Random or FIFO. In the example, LRU evicts page 2 when it ﬁrs t has
to replace a page, because 0 and 1 have been accessed more rece ntly . It
then replaces page 0 because 1 and 3 have been accessed more re cently .
In both cases, LRU’s decision, based on history , turns out to be correct,
and the next references are thus hits. Thus, in our simple exa mple, LRU
does as well as possible, matching optimal in its performanc e.
We should also note that the opposites of these algorithms exist: Most-
Frequently-Used (MFU) and Most-Recently-Used (MRU). In most cases
(not all!), these policies do not work well, as they ignore th e locality most
programs exhibit instead of embracing it.
22.6 Workload Examples
Let’s look at a few more examples in order to better understan d how
some of these policies behave. We’ll look at more complex workloads
instead just a small trace of references. However, even thes e workloads
are greatly simpliﬁed; a real study would include applicati on traces.
Our ﬁrst workload has no locality , which means that each refe rence
is to a random page within the set of accessed pages. In this si mple ex-
ample, the workload accesses 100 unique pages over time, cho osing the
next page to refer to at random; overall, 10,000 pages are acc essed. In the
experiment, we vary the cache size from very small (1 page) to enough
to hold all the unique pages (100 page), in order to see how eac h policy
behaves over the range of cache sizes.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 271

BEYOND PHYSICAL MEMORY : P OLICIES 235
0 20 40 60 80 100
0%
20%
40%
60%
80%
100%
The No-Locality Workload
Cache Size (Blocks)
Hit Rate
OPT
LRU
FIFO
RAND
Figure 22.2: The No-Locality Workload
Figure 22.2 plots the results of the experiment for optimal, LRU, Ran-
dom, and FIFO. The y-axis of the ﬁgure shows the hit rate that each policy
achieves; the x-axis varies the cache size as described abov e.
We can draw a number of conclusions from the graph. First, whe n
there is no locality in the workload, it doesn’t matter much w hich realistic
policy you are using; LRU, FIFO, and Random all perform the sa me, with
the hit rate exactly determined by the size of the cache. Seco nd, when
the cache is large enough to ﬁt the entire workload, it also do esn’t matter
which policy you use; all policies (even optimal) converge t o a 100% hit
rate when all the referenced blocks ﬁt in cache. Finally , you can see that
optimal performs noticeably better than the realistic policies; peeking into
the future, if it were possible, does a much better job of repl acement.
The next workload we examine is called the “80-20” workload, which
exhibits locality: 80% of the references are made to 20% of th e pages (the
“hot” pages); the remaining 20% of the references are made to the re-
maining 80% of the pages (the “cold” pages). In our workload, there are
a total 100 unique pages again; thus, “hot” pages are referre d to most of
the time, and “cold” pages the remainder. Figure 22.3 shows how the
policies perform with this workload.
As you can see from the ﬁgure, while both random and FIFO do rea -
sonably well, LRU does better, as it is more likely to hold ont o the hot
pages; as those pages have been referred to frequently in the past, they
are likely to be referred to again in the near future. Optimal once again
does better, showing that LRU’s historical information is n ot perfect.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 272

236 BEYOND PHYSICAL MEMORY : P OLICIES
0 20 40 60 80 100
0%
20%
40%
60%
80%
100%
The 80-20 Workload
Cache Size (Blocks)
Hit Rate
OPT
LRU
FIFO
RAND
Figure 22.3: The 80-20 Workload
You might now be wondering: is LRU’s improvement over Random
and FIFO really that big of a deal? The answer, as usual, is “it depends.” If
each miss is very costly (not uncommon), then even a small inc rease in hit
rate (reduction in miss rate) can make a huge difference on pe rformance.
If misses are not so costly , then of course the beneﬁts possib le with LRU
are not nearly as important.
Let’s look at one ﬁnal workload. We call this one the “looping sequen-
tial” workload, as in it, we refer to 50 pages in sequence, sta rting at 0,
then 1, ..., up to page 49, and then we loop, repeating those ac cesses, for a
total of 10,000 accesses to 50 unique pages. The last graph in Figure 22.4
shows the behavior of the policies under this workload.
This workload, common in many applications (including impo rtant
commercial applications such as databases [CD85]), repres ents a worst-
case for both LRU and FIFO. These algorithms, under a looping-sequential
workload, kick out older pages; unfortunately , due to the lo oping nature
of the workload, these older pages are going to be accessed so oner than
the pages that the policies prefer to keep in cache. Indeed, e ven with
a cache of size 49, a looping-sequential workload of 50 pages results in
a 0% hit rate. Interestingly , Random fares notably better, n ot quite ap-
proaching optimal, but at least achieving a non-zero hit rat e. Turns out
that random has some nice properties; one such property is no t having
weird corner-case behaviors.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 273

BEYOND PHYSICAL MEMORY : P OLICIES 237
0 20 40 60 80 100
0%
20%
40%
60%
80%
100%
The Looping-Sequential Workload
Cache Size (Blocks)
Hit Rate
OPT
LRU
FIFO
RAND
Figure 22.4: The Looping Workload
22.7 Implementing Historical Algorithms
As you can see, an algorithm such as LRU can generally do a bett er
job than simpler policies like FIFO or Random, which may thro w out
important pages. Unfortunately , historical policies present us with a new
challenge: how do we implement them?
Let’s take, for example, LRU. To implement it perfectly , we n eed to
do a lot of work. Speciﬁcally , upon each page access (i.e., each memory
access, whether an instruction fetch or a load or store), we m ust update
some data structure to move this page to the front of the list ( i.e., the
MRU side). Contrast this to FIFO, where the FIFO list of pages is only
accessed when a page is evicted (by removing the ﬁrst-in page ) or when
a new page is added to the list (to the last-in side). To keep tr ack of which
pages have been least- and most-recently used, the system has to do some
accounting work on every memory reference. Clearly , without great care,
such accounting could greatly reduce performance.
One method that could help speed this up is to add a little bit o f hard-
ware support. For example, a machine could update, on each page access,
a time ﬁeld in memory (for example, this could be in the per-pr ocess page
table, or just in some separate array in memory , with one entr y per phys-
ical page of the system). Thus, when a page is accessed, the ti me ﬁeld
would be set, by hardware, to the current time. Then, when rep lacing a
page, the OS could simply scan all the time ﬁelds in the system to ﬁnd the
least-recently-used page.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 274

238 BEYOND PHYSICAL MEMORY : P OLICIES
Unfortunately , as the number of pages in a system grows, scan ning a
huge array of times just to ﬁnd the absolute least-recently- used page is
prohibitively expensive. Imagine a modern machine with 4GB of mem-
ory , chopped into 4KB pages. This machine has 1 million pages , and thus
ﬁnding the LRU page will take a long time, even at modern CPU sp eeds.
Which begs the question: do we really need to ﬁnd the absolute oldest
page to replace? Can we instead survive with an approximatio n?
CRUX : H OW TO IMPLEMENT AN LRU R EPLACEMENT POLICY
Given that it will be expensive to implement perfect LRU, can we ap-
proximate it in some way , and still obtain the desired behavi or?
22.8 Approximating LRU
As it turns out, the answer is yes: approximating LRU is more f ea-
sible from a computational-overhead standpoint, and indee d it is what
many modern systems do. The idea requires some hardware supp ort,
in the form of a use bit (sometimes called the reference bit ), the ﬁrst of
which was implemented in the ﬁrst system with paging, the Atl as one-
level store [KE+62]. There is one use bit per page of the syste m, and the
use bits live in memory somewhere (they could be in the per-process page
tables, for example, or just in an array somewhere). Wheneve r a page is
referenced (i.e., read or written), the use bit is set by hard ware to 1. The
hardware never clears the bit, though (i.e., sets it to 0); th at is the respon-
sibility of the OS.
How does the OS employ the use bit to approximate LRU? Well, th ere
could be a lot of ways, but with the clock algorithm [C69], one simple
approach was suggested. Imagine all the pages of the system a rranged in
a circular list. A clock hand points to some particular page to begin with
(it doesn’t really matter which). When a replacement must oc cur, the OS
checks if the currently-pointed to page P has a use bit of 1 or 0. If 1, this
implies that page P was recently used and thus is not a good candidate
for replacement. Thus, the clock hand is incremented to the n ext page
P + 1, and the use bit for P set to 0 (cleared). The algorithm continues
until it ﬁnds a use bit that is set to 0, implying this page has n ot been
recently used (or, in the worst case, that all pages have been and that we
have now searched through the entire set of pages, clearing a ll the bits).
Note that this approach is not the only way to employ a use bit t o
approximate LRU. Indeed, any approach which periodically c lears the
use bits and then differentiates between which pages have us e bits of 1
versus 0 to decide which to replace would be ﬁne. The clock alg orithm of
Corbato’s was just one early approach which met with some suc cess, and
had the nice property of not repeatedly scanning through all of memory
looking for an unused page.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 275

BEYOND PHYSICAL MEMORY : P OLICIES 239
0 20 40 60 80 100
0%
20%
40%
60%
80%
100%
The 80-20 Workload
Cache Size (Blocks)
Hit Rate
OPT
LRU
FIFO
RAND
Clock
Figure 22.5: The 80-20 Workload With Clock
The behavior of a clock algorithm variant is shown in Figure 22.5. This
variant randomly scans pages when doing a replacement; when it en-
counters a page with a reference bit set to 1, it clears the bit (i.e., sets it
to 0); when it ﬁnds a page with the reference bit set to 0, it cho oses it as
its victim. As you can see, although it doesn’t do quite as wel l as perfect
LRU, it does better than approaches that don’t consider hist ory at all.
22.9 Considering Dirty Pages
One small modiﬁcation to the clock algorithm (also original ly sug-
gested by Corbato [C69]) that is commonly made is the additio nal con-
sideration of whether a page has been modiﬁed or not while in m emory .
The reason for this: if a page has been modiﬁed and is thus dirty, it must
be written back to disk to evict it, which is expensive. If it h as not been
modiﬁed (and is thus clean), the eviction is free; the physical frame can
simply be reused for other purposes without additional I/O. Thus, some
VM systems prefer to evict clean pages over dirty pages.
To support this behavior, the hardware should include a modiﬁed bit
(a.k.a. dirty bit). This bit is set any time a page is written, and thus can be
incorporated into the page-replacement algorithm. The clo ck algorithm,
for example, could be changed to scan for pages that are both u nused
and clean to evict ﬁrst; failing to ﬁnd those, then for unused pages that
are dirty; etc.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 276

240 BEYOND PHYSICAL MEMORY : P OLICIES
22.10 Other VM Policies
Page replacement is not the only policy the VM subsystem empl oys
(though it may be the most important). For example, the OS als o has to
decide when to bring a page into memory . This policy , sometimes called
the page selection policy (as it was called by Denning [D70]), presents
the OS with some different options.
For most pages, the OS simply uses demand paging, which means the
OS brings the page into memory when it is accessed, “on demand ” as
it were. Of course, the OS could guess that a page is about to be used,
and thus bring it in ahead of time; this behavior is known as prefetching
and should only be done when there is reasonable chance of suc cess. For
example, some systems will assume that if a code page P is brought into
memory , that code pageP +1 will likely soon be accessed and thus should
be brought into memory too.
Another policy determines how the OS writes pages out to disk . Of
course, they could simply be written out one at a time; howeve r, many
systems instead collect a number of pending writes together in memory
and write them to disk in one (more efﬁcient) write. This beha vior is
usually called clustering or simply grouping of writes, and is effective
because of the nature of disk drives, which perform a single l arge write
more efﬁciently than many small ones.
22.11 Thrashing
Before closing, we address one ﬁnal question: what should th e OS do
when memory is simply oversubscribed, and the memory demands of the
set of running processes simply exceeds the available physi cal memory?
In this case, the system will constantly be paging, a conditi on sometimes
referred to as thrashing [D70].
Some earlier operating systems had a fairly sophisticated s et of mech-
anisms to both detect and cope with thrashing when it took pla ce. For
example, given a set of processes, a system could decide not t o run a sub-
set of processes, with the hope that the reduced set of proces ses working
sets (the pages that they are using actively) ﬁt in memory and thus can
make progress. This approach, generally known as admission control ,
states that it is sometimes better to do less work well than to try to do
everything at once poorly , a situation we often encounter in real life as
well as in modern computer systems (sadly).
Some current systems take more a draconian approach to memor y
overload. For example, some versions of Linux run an out-of-memory
killer when memory is oversubscribed; this daemon chooses a memory -
intensive process and kills it, thus reducing memory in a non e-too-subtle
manner. While successful at reducing memory pressure, this approach
can have problems, if, for example, it kills the X server and t hus renders
any applications requiring the display unusable.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 277

BEYOND PHYSICAL MEMORY : P OLICIES 241
22.12 Summary
We have seen the introduction of a number of page-replacemen t (and
other) policies, which are part of the VM subsystem of all mod ern operat-
ing systems. Modern systems add some tweaks to straightforw ard LRU
approximations like clock; for example, scan resistance is an important
part of many modern algorithms, such as ARC [MM03]. Scan-res istant al-
gorithms are usually LRU-like but also try to avoid the worst -case behav-
ior of LRU, which we saw with the looping-sequential workloa d. Thus,
the evolution of page-replacement algorithms continues.
However, in many cases the importance of said algorithms has de-
creased, as the discrepancy between memory-access and disk-access times
has increased. Because paging to disk is so expensive, the co st of frequent
paging is prohibitive. Thus, the best solution to excessive paging is often
a simple (if intellectually dissatisfying) one: buy more me mory .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 278

242 BEYOND PHYSICAL MEMORY : P OLICIES
References
[AD03] “Run-Time Adaptation in River”
Remzi H. Arpaci-Dusseau
ACM TOCS, 21:1, February 2003
A summary of one of the authors’ dissertation work on a system named River. Certainly one place where
he learned that comparison against the ideal is an important technique for system designers.
[B66] “A Study of Replacement Algorithms for Virtual-Stora ge Computer”
Laszlo A. Belady
IBM Systems Journal 5(2): 78-101, 1966
The paper that introduces the simple way to compute the optim al behavior of a policy (the MIN algo-
rithm).
[BNS69] “An Anomaly in Space-time Characteristics of Certa in Programs Running in a Paging
Machine”
L. A. Belady and R. A. Nelson and G. S. Shedler
Communications of the ACM, 12:6, June 1969
Introduction of the little sequence of memory references kn own as Belady’s Anomaly. How do Nelson
and Shedler feel about this name, we wonder?
[CD85] “An Evaluation of Buffer Management Strategies for R elational Database Systems”
Hong-Tai Chou and David J. DeWitt
VLDB ’85, Stockholm, Sweden, August 1985
A famous database paper on the different buffering strategies you should use under a number of common
database access patterns. The more general lesson: if you kn ow something about a workload, you can
tailor policies to do better than the general-purpose ones u sually found in the OS.
[C69] “A Paging Experiment with the Multics System”
F.J. Corbato
Included in a Festschrift published in honor of Prof. P .M. Mo rse
MIT Press, Cambridge, MA, 1969
The original (and hard to ﬁnd!) reference to the clock algori thm, though not the ﬁrst usage of a use bit.
Thanks to H. Balakrishnan of MIT for digging up this paper for us.
[D70] “Virtual Memory”
Peter J. Denning
Computing Surveys, V ol. 2, No. 3, September 1970
Denning’s early and famous survey on virtual memory systems .
[EF78] “Cold-start vs. Warm-start Miss Ratios”
Malcolm C. Easton and Ronald Fagin
Communications of the ACM, 21:10, October 1978
A good discussion of cold-start vs. warm-start misses.
[HP06] “Computer Architecture: A Quantitative Approach”
John Hennessy and David Patterson
Morgan-Kaufmann, 2006
A great and marvelous book about computer architecture. Rea d it!
[H87] “Aspects of Cache Memory and Instruction Buffer Perfo rmance”
Mark D. Hill
Ph.D. Dissertation, U.C. Berkeley , 1987
Mark Hill, in his dissertation work, introduced the Three C’ s, which later gained wide popularity with
its inclusion in H&P [HP06]. The quote from therein: “I have f ound it useful to partition misses ... into
three components intuitively based on the cause of the misse s (page 49).”
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 279

BEYOND PHYSICAL MEMORY : P OLICIES 243
[KE+62] “One-level Storage System”
T. Kilburn, and D.B.G. Edwards and M.J. Lanigan and F.H. Sumn er
IRE Trans. EC-11:2, 1962
Although Atlas had a use bit, it only had a very small number of pages, and thus the scanning of the
use bits in large memories was not a problem the authors solve d.
[M+70] “Evaluation Techniques for Storage Hierarchies”
R. L. Mattson, J. Gecsei, D. R. Slutz, I. L. Traiger
IBM Systems Journal, V olume 9:2, 1970
A paper that is mostly about how to simulate cache hierarchie s efﬁciently; certainly a classic in that
regard, as well for its excellent discussion of some of the pr operties of various replacement algorithms.
Can you ﬁgure out why the stack property might be useful for si mulating a lot of different-sized caches
at once?
[MM03] “ARC: A Self-Tuning, Low Overhead Replacement Cache ”
Nimrod Megiddo and Dharmendra S. Modha
FAST 2003, February 2003, San Jose, California
An excellent modern paper about replacement algorithms, wh ich includes a new policy, ARC, that is
now used in some systems. Recognized in 2014 as a “Test of Time” award winner by the storage systems
community at the F AST ’14 conference.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 280

244 BEYOND PHYSICAL MEMORY : P OLICIES
Homework
This simulator, paging-policy.py, allows you to play around with
different page-replacement policies. See the README for de tails.
Questions
• Generate random addresses with the following arguments: -s 0
-n 10 , -s 1 -n 10 , and -s 2 -n 10 . Change the policy from
FIFO, to LRU, to OPT. Compute whether each access in said address
traces are hits or misses.
• For a cache of size 5, generate worst-case address reference streams
for each of the following policies: FIFO, LRU, and MRU (worst -case
reference streams cause the most misses possible. For the worst case
reference streams, how much bigger of a cache is needed to improve
performance dramatically and approach OPT?
• Generate a random trace (use python or perl). How would you
expect the different policies to perform on such a trace?
• Now generate a trace with some locality . How can you generate
such a trace? How does LRU perform on it? How much better than
RAND is LRU? How does CLOCK do? How about CLOCK with
different numbers of clock bits?
• Use a program like valgrind to instrument a real application and
generate a virtual page reference stream. For example, runn ing
valgrind --tool=lackey --trace-mem=yes ls will output
a nearly-complete reference trace of every instruction and data ref-
erence made by the program ls. To make this useful for the sim-
ulator above, you’ll have to ﬁrst transform each virtual mem ory
reference into a virtual page-number reference (done by mas king
off the offset and shifting the resulting bits downward). Ho w big
of a cache is needed for your application trace in order to sat isfy a
large fraction of requests? Plot a graph of its working set as the size
of the cache increases.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

