# Document: operating_systems_three_easy_pieces (Pages 161 to 200)

## Page 161

INTERLUDE : M EMORY API 125
Summary
As you can see, there are lots of ways to abuse memory . Because of fre-
quent errors with memory , a whole ecosphere of tools have dev eloped to
help ﬁnd such problems in your code. Check out both purify [HJ92] and
valgrind [SN05]; both are excellent at helping you locate the source o f
your memory-related problems. Once you become accustomed t o using
these powerful tools, you will wonder how you survived witho ut them.
14.5 Underlying OS Support
You might have noticed that we haven’t been talking about sys tem
calls when discussing malloc() and free(). The reason for this is sim-
ple: they are not system calls, but rather library calls. Thu s the malloc li-
brary manages space within your virtual address space, but i tself is built
on top of some system calls which call into the OS to ask for mor e mem-
ory or release some back to the system.
One such system call is called brk, which is used to change the loca-
tion of the program’s break: the location of the end of the heap. It takes
one argument (the address of the new break), and thus either i ncreases or
decreases the size of the heap based on whether the new break i s larger
or smaller than the current break. An additional call sbrk is passed an
increment but otherwise serves a similar purpose.
Note that you should never directly call either brk or sbrk. They
are used by the memory-allocation library; if you try to use t hem, you
will likely make something go (horribly) wrong. Stick to malloc() and
free() instead.
Finally , you can also obtain memory from the operating system via the
mmap() call. By passing in the correct arguments, mmap() can create an
anonymous memory region within your program – a region which is not
associated with any particular ﬁle but rather with swap space, something
we’ll discuss in detail later on in virtual memory . This memo ry can then
also be treated like a heap and managed as such. Read the manua l page
of mmap() for more details.
14.6 Other Calls
There are a few other calls that the memory-allocation libra ry sup-
ports. For example, calloc() allocates memory and also zeroes it be-
fore returning; this prevents some errors where you assume t hat memory
is zeroed and forget to initialize it yourself (see the parag raph on “unini-
tialized reads” above). The routine realloc() can also be useful, when
you’ve allocated space for something (say , an array), and th en need to
add something to it: realloc() makes a new larger region of memory ,
copies the old region into it, and returns the pointer to the n ew region.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 162

126 INTERLUDE : M EMORY API
14.7 Summary
We have introduced some of the APIs dealing with memory allocation.
As always, we have just covered the basics; more details are a vailable
elsewhere. Read the C book [KR88] and Stevens [SR05] (Chapte r 7) for
more information. For a cool modern paper on how to detect and correct
many of these problems automatically , see Novark et al. [N+0 7]; this
paper also contains a nice summary of common problems and som e neat
ideas on how to ﬁnd and ﬁx them.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 163

INTERLUDE : M EMORY API 127
References
[HJ92] Purify: Fast Detection of Memory Leaks and Access Err ors
R. Hastings and B. Joyce
USENIX Winter ’92
The paper behind the cool Purify tool, now a commercial produ ct.
[KR88] “The C Programming Language”
Brian Kernighan and Dennis Ritchie
Prentice-Hall 1988
The C book, by the developers of C. Read it once, do some progra mming, then read it again, and then
keep it near your desk or wherever you program.
[N+07] “Exterminator: Automatically Correcting Memory Er rors with High Probability”
Gene Novark, Emery D. Berger, and Benjamin G. Zorn
PLDI 2007
A cool paper on ﬁnding and correcting memory errors automati cally, and a great overview of many
common errors in C and C++ programs.
[SN05] “Using Valgrind to Detect Undeﬁned Value Errors with Bit-precision”
J. Seward and N. Nethercote
USENIX ’05
How to use valgrind to ﬁnd certain types of errors.
[SR05] “Advanced Programming in the U NIX Environment”
W. Richard Stevens and Stephen A. Rago
Addison-Wesley , 2005
We’ve said it before, we’ll say it again: read this book many t imes and use it as a reference whenever you
are in doubt. The authors are always surprised at how each tim e they read something in this book, they
learn something new, even after many years of C programming.
[W06] “Survey on Buffer Overﬂow Attacks and Countermeasure s”
Tim Werthman
Available: www.nds.rub.de/lehre/seminar/SS06/Werthmann
BufferOverﬂow.pdf
A nice survey of buffer overﬂows and some of the security prob lems they cause. Refers to many of the
famous exploits.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 165

15
Mechanism: Address Translation
In developing the virtualization of the CPU, we focused on a g eneral
mechanism known as limited direct execution (or LDE). The idea be-
hind LDE is simple: for the most part, let the program run dire ctly on the
hardware; however, at certain key points in time (such as whe n a process
issues a system call, or a timer interrupt occurs), arrange s o that the OS
gets involved and makes sure the “right” thing happens. Thus , the OS,
with a little hardware support, tries its best to get out of th e way of the
running program, to deliver an efﬁcient virtualization; however, by inter-
posing at those critical points in time, the OS ensures that it maint ains
control over the hardware. Efﬁciency and control together are two of the
main goals of any modern operating system.
In virtualizing memory , we will pursue a similar strategy , a ttaining
both efﬁciency and control while providing the desired virtualization. Ef-
ﬁciency dictates that we make use of hardware support, which at ﬁrst
will be quite rudimentary (e.g., just a few registers) but wi ll grow to be
fairly complex (e.g., TLBs, page-table support, and so fort h, as you will
see). Control implies that the OS ensures that no applicatio n is allowed
to access any memory but its own; thus, to protect applicatio ns from one
another, and the OS from applications, we will need help from the hard-
ware here too. Finally , we will need a little more from the VM s ystem, in
terms of ﬂexibility; speciﬁcally , we’d like for programs to be able to use
their address spaces in whatever way they would like, thus ma king the
system easier to program. And thus arrive at the reﬁned crux:
THE CRUX :
HOW TO EFFICIENTLY AND FLEXIBLY VIRTUALIZE MEMORY
How can we build an efﬁcient virtualization of memory? How do
we provide the ﬂexibility needed by applications? How do we m aintain
control over which memory locations an application can acce ss, and thus
ensure that application memory accesses are properly restr icted? How
do we do all of this efﬁciently?
129

## Page 166

130 MECHANISM : A DDRESS TRANSLATION
The generic technique we will use, which you can consider an addition
to our general approach of limited direct execution, is some thing that is
referred to as hardware-based address translation, or just address trans-
lation for short. With address translation, the hardware transfor ms each
memory access (e.g., an instruction fetch, load, or store), changing the vir-
tual address provided by the instruction to a physical address where the
desired information is actually located. Thus, on each and e very memory
reference, an address translation is performed by the hardware to redirect
application memory references to their actual locations in memory .
Of course, the hardware alone cannot virtualize memory , as it just pro-
vides the low-level mechanism for doing so efﬁciently . The O S must get
involved at key points to set up the hardware so that the corre ct trans-
lations take place; it must thus manage memory, keeping track of which
locations are free and which are in use, and judiciously inte rvening to
maintain control over how memory is used.
Once again the goal of all of this work is to create a beautiful illu-
sion: that the program has its own private memory , where its own co de
and data reside. Behind that virtual reality lies the ugly ph ysical truth:
that many programs are actually sharing memory at the same ti me, as
the CPU (or CPUs) switches between running one program and th e next.
Through virtualization, the OS (with the hardware’s help) t urns the ugly
machine reality into something that is a useful, powerful, a nd easy to use
abstraction.
15.1 Assumptions
Our ﬁrst attempts at virtualizing memory will be very simple , almost
laughably so. Go ahead, laugh all you want; pretty soon it wil l be the OS
laughing at you, when you try to understand the ins and outs of TLBs,
multi-level page tables, and other technical wonders. Don’ t like the idea
of the OS laughing at you? Well, you may be out of luck then; tha t’s just
how the OS rolls.
Speciﬁcally , we will assume for now that the user’s address space must
be placed contiguously in physical memory . We will also assume, for sim-
plicity , that the size of the address space is not too big; spe ciﬁcally , that
it is less than the size of physical memory . Finally , we will also assume that
each address space is exactly the same size. Don’t worry if these assump-
tions sound unrealistic; we will relax them as we go, thus ach ieving a
realistic virtualization of memory .
15.2 An Example
To understand better what we need to do to implement address t rans-
lation, and why we need such a mechanism, let’s look at a simpl e exam-
ple. Imagine there is a process whose address space as indica ted in Figure
15.1. What we are going to examine here is a short code sequence tha t
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 167

MECHANISM : A DDRESS TRANSLATION 131
TIP : I NTERPOSITION IS POWERFUL
Interposition is a generic and powerful technique that is of ten used to
great effect in computer systems. In virtualizing memory , t he hardware
will interpose on each memory access, and translate each vir tual address
issued by the process to a physical address where the desired informa-
tion is actually stored. However, the general technique of i nterposition is
much more broadly applicable; indeed, almost any well-deﬁned interface
can be interposed upon, to add new functionality or improve s ome other
aspect of the system. One of the usual beneﬁts of such an appro ach is
transparency; the interposition often is done without changing the clien t
of the interface, thus requiring no changes to said client.
loads a value from memory , increments it by three, and then st ores the
value back into memory . You can imagine the C-language representation
of this code might look like this:
void func()
int x;
...
x = x + 3; // this is the line of code we are interested in
The compiler turns this line of code into assembly , which mig ht look
something like this (in x86 assembly). Use objdump on Linux or otool
on Mac OS X to disassemble it:
128: movl 0x0(%ebx), %eax ;load 0+ebx into eax
132: addl $0x03, %eax ;add 3 to eax register
135: movl %eax, 0x0(%ebx) ;store eax back to mem
This code snippet is relatively straightforward; it presum es that the
address of x has been placed in the register ebx, and then loads the value
at that address into the general-purpose register eax using the movl in-
struction (for “longword” move). The next instruction adds 3 to eax,
and the ﬁnal instruction stores the value in eax back into memory at that
same location.
In Figure
15.1, you can see how both the code and data are laid out in
the process’s address space; the three-instruction code se quence is located
at address 128 (in the code section near the top), and the valu e of the
variable x at address 15 KB (in the stack near the bottom). In t he ﬁgure,
the initial value of x is 3000, as shown in its location on the s tack.
When these instructions run, from the perspective of the pro cess, the
following memory accesses take place.
• Fetch instruction at address 128
• Execute this instruction (load from address 15 KB)
• Fetch instruction at address 132
• Execute this instruction (no memory reference)
• Fetch the instruction at address 135
• Execute this instruction (store to address 15 KB)
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 168

132 MECHANISM : A DDRESS TRANSLATION
16KB
15KB
14KB
4KB
3KB
2KB
1KB
0KB
Stack
(free)
Heap
Program Code
128
132
135
movl 0x0(%ebx),%eax
addl 0x03, %eax
movl %eax,0x0(%ebx)
3000
Figure 15.1: A Process And Its Address Space
From the program’s perspective, its address space starts at address 0
and grows to a maximum of 16 KB; all memory references it gener ates
should be within these bounds. However, to virtualize memor y , the OS
wants to place the process somewhere else in physical memory , not nec-
essarily at address 0. Thus, we have the problem: how can we relocate
this process in memory in a way that is transparent to the process? How
can provide the illusion of a virtual address space starting at 0, when in
reality the address space is located at some other physical a ddress?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 169

MECHANISM : A DDRESS TRANSLATION 133
64KB
48KB
32KB
16KB
0KB
(not in use)
(not in use)
Operating System
Stack
Code
Heap
(allocated but not in use)
Relocated Process
Figure 15.2: Physical Memory with a Single Relocated Process
An example of what physical memory might look like once this p ro-
cess’s address space has been placed in memory is found in Fig ure 15.2.
In the ﬁgure, you can see the OS using the ﬁrst slot of physical memory
for itself, and that it has relocated the process from the exa mple above
into the slot starting at physical memory address 32 KB. The o ther two
slots are free (16 KB-32 KB and 48 KB-64 KB).
15.3 Dynamic (Hardware-based) Relocation
To gain some understanding of hardware-based address trans lation,
we’ll ﬁrst discuss its ﬁrst incarnation. Introduced in the ﬁ rst time-sharing
machines of the late 1950’s is a simple idea referred to as base and bounds
(the technique is also referred to as dynamic relocation ; we’ll use both
terms interchangeably) [SS74].
Speciﬁcally , we’ll need two hardware registers within each CPU: one
is called the base register, and the other the bounds (sometimes called a
limit register). This base-and-bounds pair is going to allow us to place the
address space anywhere we’d like in physical memory , and do s o while
ensuring that the process can only access its own address spa ce.
In this setup, each program is written and compiled as if it is loaded at
address zero. However, when a program starts running, the OS decides
where in physical memory it should be loaded and sets the base register
to that value. In the example above, the OS decides to load the process at
physical address 32 KB and thus sets the base register to this value.
Interesting things start to happen when the process is runni ng. Now ,
when any memory reference is generated by the process, it is translated
by the processor in the following manner:
physical address = virtual address + base
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 170

134 MECHANISM : A DDRESS TRANSLATION
ASIDE : SOFTWARE -BASED RELOCATION
In the early days, before hardware support arose, some syste ms per-
formed a crude form of relocation purely via software method s. The
basic technique is referred to as static relocation, in which a piece of soft-
ware known as the loader takes an executable that is about to be run and
rewrites its addresses to the desired offset in physical mem ory .
For example, if an instruction was a load from address 1000 in to a reg-
ister (e.g., movl 1000, %eax ), and the address space of the program
was loaded starting at address 3000 (and not 0, as the program thinks),
the loader would rewrite the instruction to offset each addr ess by 3000
(e.g., movl 4000, %eax ). In this way , a simple static relocation of the
process’s address space is achieved.
However, static relocation has numerous problems. First an d most im-
portantly , it does not provide protection, as processes can generate bad
addresses and thus illegally access other process’s or even OS memory; in
general, hardware support is likely needed for true protect ion [WL+93].
A smaller negative is that once placed, it is difﬁcult to late r relocate an
address space to another location [M65].
Each memory reference generated by the process is a virtual address;
the hardware in turn adds the contents of the base register to this address
and the result is a physical address that can be issued to the memory
system.
To understand this better, let’s trace through what happens when a
single instruction is executed. Speciﬁcally , let’s look at one instruction
from our earlier sequence:
128: movl 0x0(%ebx), %eax
The program counter (PC) is set to 128; when the hardware need s to
fetch this instruction, it ﬁrst adds the value to the the base register value
of 32 KB (32768) to get a physical address of 32896; the hardwa re then
fetches the instruction from that physical address. Next, t he processor
begins executing the instruction. At some point, the proces s then issues
the load from virtual address 15 KB, which the processor take s and again
adds to the base register (32 KB), getting the ﬁnal physical a ddress of
47 KB and thus the desired contents.
Transforming a virtual address into a physical address is ex actly the
technique we refer to as address translation; that is, the hardware takes a
virtual address the process thinks it is referencing and tra nsforms it into
a physical address which is where the data actually resides. Because this
relocation of the address happens at runtime, and because we can move
address spaces even after the process has started running, t he technique
is often referred to as dynamic relocation [M65].
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 171

MECHANISM : A DDRESS TRANSLATION 135
TIP : H ARDWARE -BASED DYNAMIC RELOCATION
With dynamic relocation, we can see how a little hardware goe s a long
way . Namely , abase register is used to transform virtual addresses (gen-
erated by the program) into physical addresses. A bounds (or limit) reg-
ister ensures that such addresses are within the conﬁnes of t he address
space. Together, they combine to provide a simple and efﬁcie nt virtual-
ization of memory .
Now you might be asking: what happened to that bounds (limit) reg-
ister? After all, isn’t this supposed to be the base-and-bou nds approach?
Indeed, it is. And as you might have guessed, the bounds regis ter is there
to help with protection. Speciﬁcally , the processor will ﬁr st check that
the memory reference is within bounds to make sure it is legal; in the sim-
ple example above, the bounds register would always be set to 16 KB. If
a process generates a virtual address that is greater than th e bounds, or
one that is negative, the CPU will raise an exception, and the process will
likely be terminated. The point of the bounds is thus to make s ure that all
addresses generated by the process are legal and within the “ bounds” of
the process.
We should note that the base and bounds registers are hardware struc-
tures kept on the chip (one pair per CPU). Sometimes people ca ll the
part of the processor that helps with address translation th e memory
management unit (MMU) ; as we develop more sophisticated memory-
management techniques, we will be adding more circuitry to t he MMU.
A small aside about bound registers, which can be deﬁned in on e of
two ways. In one way (as above), it holds the size of the address space,
and thus the hardware checks the virtual address against it ﬁ rst before
adding the base. In the second way , it holds the physical address of the
end of the address space, and thus the hardware ﬁrst adds the b ase and
then makes sure the address is within bounds. Both methods ar e logically
equivalent; for simplicity , we’ll usually assume that the b ounds register
holds the size of the address space.
Example T ranslations
To understand address translation via base-and-bounds in m ore detail,
let’s take a look at an example. Imagine a process with an addr ess space of
size 4 KB (yes, unrealistically small) has been loaded at phy sical address
16 KB. Here are the results of a number of address translation s:
• Virtual Address 0 → Physical Address 16 KB
• V A 1 KB→ P A 17 KB
• V A 3000→ P A 19384
• V A 4400→ Fault (out of bounds)
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 172

136 MECHANISM : A DDRESS TRANSLATION
ASIDE : DATA STRUCTURE – T HE FREE LIST
The OS must track which parts of free memory are not in use, so a s to
be able to allocate memory to processes. Many different data structures
can of course be used for such a task; the simplest (which we wi ll assume
here) is a free list , which simply is a list of the ranges of the physical
memory which are not currently in use.
As you can see from the example, it is easy for you to simply add the
base address to the virtual address (which can rightly be vie wed as an
offset into the address space) to get the resulting physical addres s. Only if
the virtual address is “too big” or negative will the result b e a fault (e.g.,
4400 is greater than the 4 KB bounds), causing an exception to be raised
and the process to be terminated.
15.4 OS Issues
There are a number of new OS issues that arise when using base a nd
bounds to implement a simple virtual memory . Speciﬁcally , t here are
three critical junctures where the OS must take action to imp lement this
base-and-bounds approach to virtualizing memory .
First, The OS must take action when a process is created, ﬁndi ng space
for its address space in memory . Fortunately , given our assumptions that
each address space is (a) smaller than the size of physical me mory and
(b) the same size, this is quite easy for the OS; it can simply v iew physical
memory as an array of slots, and track whether each one is free or in use.
When a new process is created, the OS will have to search a data structure
(often called a free list) to ﬁnd room for the new address space and then
mark it used.
An example of what physical memory might look like can be foun d
in Figure 15.2. In the ﬁgure, you can see the OS using the ﬁrst slot of
physical memory for itself, and that it has relocated the pro cess from the
example above into the slot starting at physical memory addr ess 32 KB.
The other two slots are free (16 KB-32 KB and 48 KB-64 KB); thus , the free
list should consist of these two entries.
Second, the OS must take action when a process is terminated, reclaim-
ing all of its memory for use in other processes or the OS. Upon termina-
tion of a process, the OS thus puts its memory back on the free l ist, and
cleans up any associated data structures as need be.
Third, the OS must also take action when a context switch occu rs.
There is only one base and bounds register on each CPU, after a ll, and
their values differ for each running program, as each program is loaded at
a different physical address in memory . Thus, the OS mustsave and restore
the base-and-bounds pair when it switches between processe s. Speciﬁ-
cally , when the OS decides to stop running a process, it must s ave the
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 173

MECHANISM : A DDRESS TRANSLATION 137
values of the base and bounds registers to memory , in some per -process
structure such as the process structure or process control block (PCB).
Similarly , when the OS resumes a running process (or runs it t he ﬁrst
time), it must set the values of the base and bounds on the CPU t o the
correct values for this process.
We should note that when a process is stopped (i.e., not runni ng), it is
possible for the OS to move an address space from one location in mem-
ory to another rather easily . To move a process’s address spa ce, the OS
ﬁrst deschedules the process; then, the OS copies the addres s space from
the current location to the new location; ﬁnally , the OS updates the saved
base register (in the process structure) to point to the new l ocation. When
the process is resumed, its (new) base register is restored, and it begins
running again, oblivious that its instructions and data are now in a com-
pletely new spot in memory!
We should also note that access to the base and bounds registe rs is ob-
viously privileged. Special hardware instructions are required to access
base-and-bounds registers; if a process, running in user mo de, attempts
to do so, the CPU will raise an exception and the OS will likely termi-
nate the process. Only in kernel (or privileged) mode can suc h registers
be modiﬁed. Imagine the havoc a user process could wreak 1 if it could
arbitrarily change the base register while running. Imagin e it! And then
quickly ﬂush such dark thoughts from your mind, as they are th e ghastly
stuff of which nightmares are made.
15.5 Summary
In this chapter, we have extended the concept of limited dire ct exe-
cution with a speciﬁc mechanism used in virtual memory , know n as ad-
dress translation. With address translation, the OS can control each and
every memory access from a process, ensuring the accesses st ay within
the bounds of the address space. Key to the efﬁciency of this t echnique
is hardware support, which performs the translation quickl y for each ac-
cess, turning virtual addresses (the process’s view of memo ry) into phys-
ical ones (the actual view). All of this is performed in a way t hat is trans-
parent to the process that has been relocated; the process has no ide a its
memory references are being translated, making for a wonder ful illusion.
We have also seen one particular form of virtualization, known as base
and bounds or dynamic relocation. Base-and-bounds virtual ization is
quite efﬁcient, as only a little more hardware logic is required to add a
base register to the virtual address and check that the addre ss generated
by the process is in bounds. Base-and-bounds also offers protection; the
OS and hardware combine to ensure no process can generate mem ory
references outside its own address space. Protection is cer tainly one of
the most important goals of the OS; without it, the OS could no t control
1Is there anything other than “havoc” that can be “wreaked”?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 174

138 MECHANISM : A DDRESS TRANSLATION
the machine (if processes were free to overwrite memory , they could eas-
ily do nasty things like overwrite the trap table and take ove r the system).
Unfortunately , this simple technique of dynamic relocation does have
its inefﬁciencies. For example, as you can see in Figure 15.2 (back a few
pages), the relocated process is using physical memory from 32 KB to
48 KB; however, because the process stack and heap are not too big, all of
the space between the two is simply wasted. This type of waste is usually
called internal fragmentation, as the space inside the allocated unit is not
all used (i.e., is fragmented) and thus wasted. In our curren t approach, al-
though there might be enough physical memory for more proces ses, we
are currently restricted to placing an address space in a ﬁxe d-sized slot
and thus internal fragmentation can arise 2. Thus, we are going to need
more sophisticated machinery , to try to better utilize phys ical memory
and avoid internal fragmentation. Our ﬁrst attempt will be a slight gen-
eralization of base and bounds known as segmentation, which we will
discuss next.
2A different solution might instead place a ﬁxed-sized stack within the address space,
just below the code region, and a growing heap below that. How ever, this limits ﬂexibility
by making recursion and deeply-nested function calls chall enging, and thus is something we
hope to avoid.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 175

MECHANISM : A DDRESS TRANSLATION 139
References
[M65] “On Dynamic Program Relocation”
W.C. McGee
IBM Systems Journal
V olume 4, Number 3, 1965, pages 184–199
This paper is a nice summary of early work on dynamic relocati on, as well as some basics on static
relocation.
[P90] “Relocating loader for MS-DOS .EXE executable ﬁles”
Kenneth D. A. Pillay
Microprocessors & Microsystems archive
V olume 14, Issue 7 (September 1990)
An example of a relocating loader for MS-DOS. Not the ﬁrst one , but just a relatively modern example
of how such a system works.
[SS74] “The Protection of Information in Computer Systems”
J. Saltzer and M. Schroeder
CACM, July 1974
From this paper: “The concepts of base-and-bound register a nd hardware-interpreted descriptors ap-
peared, apparently independently, between 1957 and 1959 on three projects with diverse goals. At
M.I.T., McCarthy suggested the base-and-bound idea as part of the memory protection system nec-
essary to make time-sharing feasible. IBM independently de veloped the base-and-bound register as a
mechanism to permit reliable multiprogramming of the Stretch (7030) computer system. At Burroughs,
R. Barton suggested that hardware-interpreted descriptor s would provide direct support for the naming
scope rules of higher level languages in the B5000 computer s ystem.” We found this quote on Mark
Smotherman’s cool history pages [S04]; see them for more inf ormation.
[S04] “System Call Support”
Mark Smotherman, May 2004
http://people.cs.clemson.edu/˜mark/syscall.html
A neat history of system call support. Smotherman has also co llected some early history on items like
interrupts and other fun aspects of computing history. See h is web pages for more details.
[WL+93] “Efﬁcient Software-based Fault Isolation”
Robert Wahbe, Steven Lucco, Thomas E. Anderson, Susan L. Gra ham
SOSP ’93
A terriﬁc paper about how you can use compiler support to boun d memory references from a program,
without hardware support. The paper sparked renewed intere st in software techniques for isolation of
memory references.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 176

140 MECHANISM : A DDRESS TRANSLATION
Homework
The program relocation.py allows you to see how address trans-
lations are performed in a system with base and bounds regist ers. See the
README for details.
Questions
• Run with seeds 1, 2, and 3, and compute whether each virtual ad -
dress generated by the process is in or out of bounds. If in bou nds,
compute the translation.
• Run with these ﬂags: -s 0 -n 10 . What value do you have set
-l (the bounds register) to in order to ensure that all the gener ated
virtual addresses are within bounds?
• Run with these ﬂags: -s 1 -n 10 -l 100 . What is the maxi-
mum value that bounds can be set to, such that the address spac e
still ﬁts into physical memory in its entirety?
• Run some of the same problems above, but with larger address
spaces (-a) and physical memories ( -p).
• What fraction of randomly-generated virtual addresses are valid,
as a function of the value of the bounds register? Make a graph
from running with different random seeds, with limit values rang-
ing from 0 up to the maximum size of the address space.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 177

16
Segmentation
So far we have been putting the entire address space of each pr ocess in
memory . With the base and bounds registers, the OS can easily relocate
processes to different parts of physical memory . However, y ou might
have noticed something interesting about these address spa ces of ours:
there is a big chunk of “free” space right in the middle, betwe en the stack
and the heap.
As you can imagine from Figure 16.1, although the space between the
stack and heap is not being used by the process, it is still tak ing up phys-
ical memory when we relocate the entire address space somewh ere in
physical memory; thus, the simple approach of using a base an d bounds
register pair to virtualize memory is wasteful. It also make s it quite hard
to run a program when the entire address space doesn’t ﬁt into memory;
thus, base and bounds is not as ﬂexible as we would like. And th us:
THE CRUX : H OW TO SUPPORT A L ARGE ADDRESS SPACE
How do we support a large address space with (potentially) a l ot of
free space between the stack and the heap? Note that in our exa mples,
with tiny (pretend) address spaces, the waste doesn’t seem t oo bad. Imag-
ine, however, a 32-bit address space (4 GB in size); a typical program will
only use megabytes of memory , but still would demand that the entire
address space be resident in memory .
16.1 Segmentation: Generalized Base/Bounds
To solve this problem, an idea was born, and it is called segmenta-
tion. It is quite an old idea, going at least as far back as the very e arly
1960’s [H61, G62]. The idea is simple: instead of having just one base
and bounds pair in our MMU, why not have a base and bounds pair p er
logical segment of the address space? A segment is just a contiguous
portion of the address space of a particular length, and in ou r canonical
141

## Page 178

142 SEGMENTATION
16KB
15KB
14KB
6KB
5KB
4KB
3KB
2KB
1KB
0KB
Program Code
Heap
(free)
Stack
Figure 16.1: An Address Space (Again)
address space, we have three logically-different segments : code, stack,
and heap. What segmentation allows the OS to do is to place eac h one
of those segments in different parts of physical memory , and thus avoid
ﬁlling physical memory with unused virtual address space.
Let’s look at an example. Assume we want to place the address s pace
from Figure 16.1 into physical memory . With a base and bounds pair per
segment, we can place each segment independently in physical memory .
For example, see Figure 16.2; there you see a 64-KB physical memory
with those three segments within it (and 16KB reserved for th e OS).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 179

SEGMENTATION 143
64KB
48KB
32KB
16KB
0KB
(not in use)
(not in use)
(not in use)
Operating System
Stack
Code
Heap
Figure 16.2: Placing Segments In Physical Memory
As you can see in the diagram, only used memory is allocated sp ace
in physical memory , and thus large address spaces with large amounts of
unused address space (which we sometimes call sparse address spaces )
can be accommodated.
The hardware structure in our MMU required to support segmen ta-
tion is just what you’d expect: in this case, a set of three bas e and bounds
register pairs. Table 16.1 below shows the register values for the example
above; each bounds register holds the size of a segment.
Segment Base Size
Code 32K 2K
Heap 34K 2K
Stack 28K 2K
Table 16.1: Segment Register V alues
You can see from the table that the code segment is placed at ph ysical
address 32KB and has a size of 2KB and the heap segment is place d at
34KB and also has a size of 2KB.
Let’s do an example translation, using the address space in F igure
16.1.
Assume a reference is made to virtual address 100 (which is in the code
segment). When the reference takes place (say , on an instruc tion fetch),
the hardware will add the base value to the offset into this segment (100 in
this case) to arrive at the desired physical address: 100 + 32 KB, or 32868.
It will then check that the address is within bounds (100 is le ss than 2KB),
ﬁnd that it is, and issue the reference to physical memory add ress 32868.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 180

144 SEGMENTATION
ASIDE : THE SEGMENTATION FAULT
The term segmentation fault or violation arises from a memor y access
on a segmented machine to an illegal address. Humorously , th e term
persists, even on machines with no support for segmentation at all. Or
not so humorously , if you can’t ﬁgure why your code keeps faul ting.
Now let’s look at an address in the heap, virtual address 4200 (again
refer to Figure 16.1). If we just add the virtual address 4200 to the base
of the heap (34KB), we get a physical address of 39016, which i s not the
correct physical address. What we need to ﬁrst do is extract t he offset into
the heap, i.e., which byte(s) in this segment the address refers to. Because
the heap starts at virtual address 4KB (4096), the offset of 4 200 is actually
4200 – 4096 or 104. We then take this offset (104) and add it to t he base
register physical address (34K or 34816) to get the desired r esult: 34920.
What if we tried to refer to an illegal address, such as 7KB whi ch is be-
yond the end of the heap? You can imagine what will happen: the hard-
ware detects that the address is out of bounds, traps into the OS, likely
leading to the termination of the offending process. And now you know
the origin of the famous term that all C programmers learn to d read: the
segmentation violation or segmentation fault.
16.2 Which Segment Are We Referring To?
The hardware uses segment registers during translation. Ho w does it
know the offset into a segment, and to which segment an addres s refers?
One common approach, sometimes referred to as anexplicit approach,
is to chop up the address space into segments based on the top f ew bits
of the virtual address; this technique was used in the V AX/VM S system
[LL82]. In our example above, we have three segments; thus we need two
bits to accomplish our task. If we use the top two bits of our 14 -bit virtual
address to select the segment, our virtual address looks lik e this:
13 12 11 10 9 8 7 6 5 4 3 2 1 0
Segment Offset
In our example, then, if the top two bits are 00, the hardware k nows
the virtual address is in the code segment, and thus uses the c ode base
and bounds pair to relocate the address to the correct physic al location.
If the top two bits are 01, the hardware knows the address is in the heap,
and thus uses the heap base and bounds. Let’s take our example heap
virtual address from above (4200) and translate it, just to m ake sure this
is clear. The virtual address 4200, in binary form, can be see n here:
13
0
12
1
11
0
10
0
9
0
8
0
7
0
6
1
5
1
4
0
3
1
2
0
1
0
0
0
Segment Offset
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 181

SEGMENTATION 145
As you can see from the picture, the top two bits (01) tell the h ardware
which segment we are referring to. The bottom 12 bits are the offset into
the segment: 0000 0110 1000, or hex 0x068, or 104 in decimal. T hus, the
hardware simply takes the ﬁrst two bits to determine which se gment reg-
ister to use, and then takes the next 12 bits as the offset into the segment.
By adding the base register to the offset, the hardware arriv es at the ﬁ-
nal physical address. Note the offset eases the bounds check too: we can
simply check if the offset is less than the bounds; if not, the address is ille-
gal. Thus, if base and bounds were arrays (with one entry per s egment),
the hardware would be doing something like this to obtain the desired
physical address:
1 // get top 2 bits of 14-bit VA
2 Segment = (VirtualAddress & SEG_MASK) >> SEG_SHIFT
3 // now get offset
4 Offset = VirtualAddress & OFFSET_MASK
5 if (Offset >= Bounds[Segment])
6 RaiseException(PROTECTION_FAULT)
7 else
8 PhysAddr = Base[Segment] + Offset
9 Register = AccessMemory(PhysAddr)
In our running example, we can ﬁll in values for the constants above.
Speciﬁcally ,SEG MASK would be set to 0x3000, SEG SHIFT to 12, and
OFFSET MASK to 0xFFF.
You may also have noticed that when we use the top two bits, and we
only have three segments (code, heap, stack), one segment of the address
space goes unused. Thus, some systems put code in the same seg ment as
the heap and thus use only one bit to select which segment to us e [LL82].
There are other ways for the hardware to determine which segm ent
a particular address is in. In the implicit approach, the hardware deter-
mines the segment by noticing how the address was formed. If, for ex-
ample, the address was generated from the program counter (i .e., it was
an instruction fetch), then the address is within the code se gment; if the
address is based off of the stack or base pointer, it must be in the stack
segment; any other address must be in the heap.
16.3 What About The Stack?
Thus far, we’ve left out one important component of the addre ss space:
the stack. The stack has been relocated to physical address 2 8KB in the di-
agram above, but with one critical difference: it grows backwards – in phys-
ical memory , it starts at 28KB and grows back to 26KB, corresp onding to
virtual addresses 16KB to 14KB; translation has to proceed d ifferently .
The ﬁrst thing we need is a little extra hardware support. Ins tead of
just base and bounds values, the hardware also needs to know which way
the segment grows (a bit, for example, that is set to 1 when the segment
grows in the positive direction, and 0 for negative). Our upd ated view of
what the hardware tracks is seen in Table 16.2.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 182

146 SEGMENTATION
Segment Base Size Grows Positive?
Code 32K 2K 1
Heap 34K 2K 1
Stack 28K 2K 0
Table 16.2: Segment Registers (With Negative-Growth Support)
With the hardware understanding that segments can grow in th e neg-
ative direction, the hardware must now translate such virtu al addresses
slightly differently . Let’s take an example stack virtual a ddress and trans-
late it to understand the process.
In this example, assume we wish to access virtual address 15KB, which
should map to physical address 27KB. Our virtual address, in binary
form, thus looks like this: 11 1100 0000 0000 (hex 0x3C00). Th e hard-
ware uses the top two bits (11) to designate the segment, but t hen we
are left with an offset of 3KB. To obtain the correct negative offset, we
must subtract the maximum segment size from 3KB: in this exam ple, a
segment can be 4KB, and thus the correct negative offset is 3K B - 4KB
which equals -1KB. We simply add the negative offset (-1KB) t o the base
(28KB) to arrive at the correct physical address: 27KB. The b ounds check
can be calculated by ensuring the absolute value of the negat ive offset is
less than the segment’s size.
16.4 Support for Sharing
As support for segmentation grew , system designers soon realized that
they could realize new types of efﬁciencies with a little mor e hardware
support. Speciﬁcally , to save memory , sometimes it is usefu l to share
certain memory segments between address spaces. In particu lar, code
sharing is common and still in use in systems today .
To support sharing, we need a little extra support from the ha rdware,
in the form of protection bits. Basic support adds a few bits per segment,
indicating whether or not a program can read or write a segmen t, or per-
haps execute code that lies within the segment. By setting a c ode segment
to read-only , the same code can be shared across multiple processes, with-
out worry of harming isolation; while each process still thinks that it is ac-
cessing its own private memory , the OS is secretly sharing memory which
cannot be modiﬁed by the process, and thus the illusion is pre served.
An example of the additional information tracked by the hard ware
(and OS) is shown in Figure
16.3. As you can see, the code segment is
set to read and execute, and thus the same physical segment in memory
could be mapped into multiple virtual address spaces.
With protection bits, the hardware algorithm described ear lier would
also have to change. In addition to checking whether a virtua l address is
within bounds, the hardware also has to check whether a parti cular ac-
cess is permissible. If a user process tries to write to a read -only page, or
execute from a non-executable page, the hardware should rai se an excep-
tion, and thus let the OS deal with the offending process.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 183

SEGMENTATION 147
Segment Base Size Grows Positive? Protection
Code 32K 2K 1 Read-Execute
Heap 34K 2K 1 Read-Write
Stack 28K 2K 0 Read-Write
Table 16.3: Segment Register V alues (with Protection)
16.5 Fine-grained vs. Coarse-grained Segmentation
Most of our examples thus far have focused on systems with jus t a
few segments (i.e., code, stack, heap); we can think of this s egmentation
as coarse-grained, as it chops up the address space into relatively large,
coarse chunks. However, some early systems (e.g., Multics [ CV65,DD68])
were more ﬂexible and allowed for address spaces to consist o f a large
number smaller segments, referred to as ﬁne-grained segmentation.
Supporting many segments requires even further hardware su pport,
with a segment table of some kind stored in memory . Such segment ta-
bles usually support the creation of a very large number of se gments, and
thus enable a system to use segments in more ﬂexible ways than we have
thus far discussed. For example, early machines like the Bur roughs B5000
had support for thousands of segments, and expected a compil er to chop
code and data into separate segments which the OS and hardwar e would
then support [RK68]. The thinking at the time was that by havi ng ﬁne-
grained segments, the OS could better learn about which segm ents are in
use and which are not and thus utilize main memory more effect ively .
16.6 OS Support
You now should have a basic idea as to how segmentation works.
Pieces of the address space are relocated into physical memo ry as the
system runs, and thus a huge savings of physical memory is ach ieved
relative to our simpler approach with just a single base/bou nds pair for
the entire address space. Speciﬁcally , all the unused space between the
stack and the heap need not be allocated in physical memory , a llowing
us to ﬁt more address spaces into physical memory .
However, segmentation raises a number of new issues. We’ll ﬁ rst de-
scribe the new OS issues that must be addressed. The ﬁrst is an old one:
what should the OS do on a context switch? You should have a goo d
guess by now: the segment registers must be saved and restore d. Clearly ,
each process has its own virtual address space, and the OS mus t make
sure to set up these registers correctly before letting the process run again.
The second, and more important, issue is managing free space in phys-
ical memory . When a new address space is created, the OS has to be
able to ﬁnd space in physical memory for its segments. Previo usly , we
assumed that each address space was the same size, and thus ph ysical
memory could be thought of as a bunch of slots where processes would
ﬁt in. Now , we have a number of segments per process, and each segment
might be a different size.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 184

148 SEGMENTATION
64KB
56KB
48KB
40KB
32KB
24KB
16KB
8KB
0KB
Operating System
Not Compacted
(not in use)
(not in use)
(not in use)
Allocated
Allocated
Allocated
64KB
56KB
48KB
40KB
32KB
24KB
16KB
8KB
0KB
(not in use)
Allocated
Operating System
Compacted
Figure 16.3: Non-compacted and Compacted Memory
The general problem that arises is that physical memory quic kly be-
comes full of little holes of free space, making it difﬁcult t o allocate new
segments, or to grow existing ones. We call this problem external frag-
mentation [R69]; see Figure 16.3 (left).
In the example, a process comes along and wishes to allocate a 20KB
segment. In that example, there is 24KB free, but not in one co ntiguous
segment (rather, in three non-contiguous chunks). Thus, th e OS cannot
satisfy the 20KB request.
One solution to this problem would be to compact physical memory
by rearranging the existing segments. For example, the OS co uld stop
whichever processes are running, copy their data to one cont iguous re-
gion of memory , change their segment register values to poin t to the
new physical locations, and thus have a large free extent of m emory with
which to work. By doing so, the OS enables the new allocation r equest
to succeed. However, compaction is expensive, as copying se gments is
memory-intensive and thus would use a fair amount of process or time.
See Figure 16.3 (right) for a diagram of compacted physical memory .
A simpler approach is to use a free-list management algorith m that
tries to keep large extents of memory available for allocati on. There are
literally hundreds of approaches that people have taken, in cluding clas-
sic algorithms like best-ﬁt (which keeps a list of free spaces and returns
the one closest in size that satisﬁes the desired allocation to the requester),
worst-ﬁt, ﬁrst-ﬁt, and more complex schemes like buddy algorithm [K68].
An excellent survey by Wilson et al. is a good place to start if you want to
learn more about such algorithms [W+95], or you can wait unti l we cover
some of the basics ourselves in a later chapter. Unfortunate ly , though, no
matter how smart the algorithm, external fragmentation wil l still exist;
thus, a good algorithm simply attempts to minimize it.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 185

SEGMENTATION 149
TIP : I F 1000 S OLUTIONS EXIST , N O GREAT ONE DOES
The fact that so many different algorithms exist to try to min imize exter-
nal fragmentation is indicative of a stronger underlying tr uth: there is no
one “best” way to solve the problem. Thus, we settle for somet hing rea-
sonable and hope it is good enough. The only real solution (as we will
see in forthcoming chapters) is to avoid the problem altoget her, by never
allocating memory in variable-sized chunks.
16.7 Summary
Segmentation solves a number of problems, and helps us build a more
effective virtualization of memory . Beyond just dynamic re location, seg-
mentation can better support sparse address spaces, by avoiding the huge
potential waste of memory between logical segments of the address space.
It is also fast, as doing the arithmetic segmentation requir es in hardware
is easy and well-suited to hardware; the overheads of translation are min-
imal. A fringe beneﬁt arises too: code sharing. If code is pla ced within
a separate segment, such a segment could potentially be shar ed across
multiple running programs.
However, as we learned, allocating variable-sized segment s in mem-
ory leads to some problems that we’d like to overcome. The ﬁrs t, as dis-
cussed above, is external fragmentation. Because segments are variable-
sized, free memory gets chopped up into odd-sized pieces, an d thus sat-
isfying a memory-allocation request can be difﬁcult. One ca n try to use
smart algorithms [W+95] or periodically compact memory , bu t the prob-
lem is fundamental and hard to avoid.
The second and perhaps more important problem is that segmentation
still isn’t ﬂexible enough to support our fully generalized , sparse address
space. For example, if we have a large but sparsely-used heap all in one
logical segment, the entire heap must still reside in memory in order to be
accessed. In other words, if our model of how the address spac e is being
used doesn’t exactly match how the underlying segmentation has been
designed to support it, segmentation doesn’t work very well . We thus
need to ﬁnd some new solutions. Ready to ﬁnd them?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 186

150 SEGMENTATION
References
[CV65] “Introduction and Overview of the Multics System”
F. J. Corbato and V . A. Vyssotsky
Fall Joint Computer Conference, 1965
One of ﬁve papers presented on Multics at the Fall Joint Compu ter Conference; oh to be a ﬂy on the wall
in that room that day!
[DD68] “Virtual Memory , Processes, and Sharing in Multics”
Robert C. Daley and Jack B. Dennis
Communications of the ACM, V olume 11, Issue 5, May 1968
An early paper on how to perform dynamic linking in Multics, w hich was way ahead of its time. Dy-
namic linking ﬁnally found its way back into systems about 20 years later, as the large X-windows
libraries demanded it. Some say that these large X11 librari es were MIT’s revenge for removing support
for dynamic linking in early versions of UNIX!
[G62] “Fact Segmentation”
M. N. Greenﬁeld
Proceedings of the SJCC, V olume 21, May 1962
Another early paper on segmentation; so early that it has no r eferences to other work.
[H61] “Program Organization and Record Keeping for Dynamic Storage”
A. W. Holt
Communications of the ACM, V olume 4, Issue 10, October 1961
An incredibly early and difﬁcult to read paper about segment ation and some of its uses.
[I09] “Intel 64 and IA-32 Architectures Software Developer ’s Manuals”
Intel, 2009
Available: http://www.intel.com/products/processor/manuals
Try reading about segmentation in here (Chapter 3 in Volume 3 a); it’ll hurt your head, at least a little
bit.
[K68] “The Art of Computer Programming: V olume I”
Donald Knuth
Addison-Wesley , 1968
Knuth is famous not only for his early books on the Art of Compu ter Programming but for his typeset-
ting system TeX which is still a powerhouse typesetting tool used by professionals today, and indeed to
typeset this very book. His tomes on algorithms are a great ea rly reference to many of the algorithms
that underly computing systems today.
[L83] “Hints for Computer Systems Design”
Butler Lampson
ACM Operating Systems Review, 15:5, October 1983
A treasure-trove of sage advice on how to build systems. Hard to read in one sitting; take it in a little at
a time, like a ﬁne wine, or a reference manual.
[LL82] “Virtual Memory Management in the V AX/VMS Operating System”
Henry M. Levy and Peter H. Lipman
IEEE Computer, V olume 15, Number 3 (March 1982)
A classic memory management system, with lots of common sens e in its design. We’ll study it in more
detail in a later chapter.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 187

SEGMENTATION 151
[RK68] “Dynamic Storage Allocation Systems”
B. Randell and C.J. Kuehner
Communications of the ACM
V olume 11(5), pages 297-306, May 1968
A nice overview of the differences between paging and segmen tation, with some historical discussion of
various machines.
[R69] “A note on storage fragmentation and program segmenta tion”
Brian Randell
Communications of the ACM
V olume 12(7), pages 365-372, July 1969
One of the earliest papers to discuss fragmentation.
[W+95] “Dynamic Storage Allocation: A Survey and Critical R eview”
Paul R. Wilson, Mark S. Johnstone, Michael Neely , and David B oles
In International Workshop on Memory Management
Scotland, United Kingdom, September 1995
A great survey paper on memory allocators.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 188

152 SEGMENTATION
Homework
This program allows you to see how address translations are performed
in a system with segmentation. See the README for details.
Questions
• First let’s use a tiny address space to translate some addres ses. Here’s
a simple set of parameters with a few different random seeds; can
you translate the addresses?
segmentation.py -a 128 -p 512 -b 0 -l 20 -B 512 -L 20 -s 0
segmentation.py -a 128 -p 512 -b 0 -l 20 -B 512 -L 20 -s 1
segmentation.py -a 128 -p 512 -b 0 -l 20 -B 512 -L 20 -s 2
• Now , let’s see if we understand this tiny address space we’ve con-
structed (using the parameters from the question above). Wh at is
the highest legal virtual address in segment 0? What about th e low-
est legal virtual address in segment 1? What are the lowest an d
highest illegal addresses in this entire address space? Finally , how
would you run segmentation.py with the -A ﬂag to test if you
are right?
• Let’s say we have a tiny 16-byte address space in a 128-byte ph ysical
memory . What base and bounds would you set up so as to get
the simulator to generate the following translation result s for the
speciﬁed address stream: valid, valid, violation, ..., vio lation, valid,
valid? Assume the following parameters:
segmentation.py -a 16 -p 128
-A 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
--b0 ? --l0 ? --b1 ? --l1 ?
• Assuming we want to generate a problem where roughly 90% of the
randomly-generated virtual addresses are valid (i.e., not segmenta-
tion violations). How should you conﬁgure the simulator to d o so?
Which parameters are important?
• Can you run the simulator such that no virtual addresses are v alid?
How?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 189

17
Free-Space Management
In this chapter, we take a small detour from our discussion of virtual-
izing memory to discuss a fundamental aspect of any memory ma nage-
ment system, whether it be a malloc library (managing pages o f a pro-
cess’s heap) or the OS itself (managing portions of the addre ss space of a
process). Speciﬁcally , we will discuss the issues surround ing free-space
management.
Let us make the problem more speciﬁc. Managing free space can cer-
tainly be easy , as we will see when we discuss the concept of paging. It is
easy when the space you are managing is divided into ﬁxed-siz ed units;
in such a case, you just keep a list of these ﬁxed-sized units; when a client
requests one of them, return the ﬁrst entry .
Where free-space management becomes more difﬁcult (and int erest-
ing) is when the free space you are managing consists of varia ble-sized
units; this arises in a user-level memory-allocation library (as in malloc()
and free()) and in an OS managing physical memory when using seg-
mentation to implement virtual memory . In either case, the problem tha t
exists is known as external fragmentation : the free space gets chopped
into little pieces of different sizes and is thus fragmented ; subsequent re-
quests may fail because there is no single contiguous space t hat can sat-
isfy the request, even though the total amount of free space e xceeds the
size of the request.
free used free
0 10 20 30
The ﬁgure shows an example of this problem. In this case, the t otal
free space available is 20 bytes; unfortunately , it is fragm ented into two
chunks of size 10 each. As a result, a request for 15 bytes will fail even
though there are 20 bytes free. And thus we arrive at the probl em ad-
dressed in this chapter.
153

## Page 190

154 FREE -S PACE MANAGEMENT
CRUX : H OW TO MANAGE FREE SPACE
How should free space be managed, when satisfying variable- sized re-
quests? What strategies can be used to minimize fragmentati on? What
are the time and space overheads of alternate approaches?
17.1 Assumptions
Most of this discussion will focus on the great history of all ocators
found in user-level memory-allocation libraries. We draw o n Wilson’s
excellent survey [W+95] but encourage interested readers t o go to the
source document itself for more details 1.
We assume a basic interface such as that provided by malloc() and
free(). Speciﬁcally ,void *malloc(size t size) takes a single pa-
rameter, size, which is the number of bytes requested by the applica-
tion; it hands back a pointer (of no particular type, or a void pointer in
C lingo) to a region of that size (or greater). The complement ary routine
void free(void *ptr) takes a pointer and frees the corresponding
chunk. Note the implication of the interface: the user, when freeing the
space, does not inform the library of its size; thus, the libr ary must be able
to ﬁgure out how big a chunk of memory is when handed just a poin ter
to it. We’ll discuss how to do this a bit later on in the chapter .
The space that this library manages is known historically as the heap,
and the generic data structure used to manage free space in th e heap is
some kind of free list. This structure contains references to all of the free
chunks of space in the managed region of memory . Of course, th is data
structure need not be a list per se, but just some kind of data structure to
track free space.
We further assume that primarily we are concerned withexternal frag-
mentation, as described above. Allocators could of course also have th e
problem of internal fragmentation ; if an allocator hands out chunks of
memory bigger than that requested, any unasked for (and thus unused)
space in such a chunk is considered internal fragmentation (because the
waste occurs inside the allocated unit) and is another examp le of space
waste. However, for the sake of simplicity , and because it is the more in-
teresting of the two types of fragmentation, we’ll mostly fo cus on external
fragmentation.
We’ll also assume that once memory is handed out to a client, i t cannot
be relocated to another location in memory . For example, if a program
calls malloc() and is given a pointer to some space within the heap,
that memory region is essentially “owned” by the program (an d cannot
be moved by the library) until the program returns it via a cor respond-
ing call to free(). Thus, no compaction of free space is possible, which
1It is nearly 80 pages long; thus, you really have to be interes ted!
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 191

FREE -S PACE MANAGEMENT 155
would be useful to combat fragmentation 2. Compaction could, however,
be used in the OS to deal with fragmentation when implementin g seg-
mentation; see the chapter on segmentation for details.
Finally , we’ll assume that the allocator manages a contiguo us region
of bytes. In some cases, an allocator could ask for that regio n to grow;
for example, a user-level memory-allocation library might call into the
kernel to grow the heap (via a system call such as sbrk) when it runs out
of space. However, for simplicity , we’ll just assume that th e region is a
single ﬁxed size throughout its life.
17.2 Low-level Mechanisms
Before delving into some policy details, we’ll ﬁrst cover so me com-
mon mechanisms used in most allocators. First, we’ll discus s the basics of
splitting and coalescing, common techniques in most any all ocator. Sec-
ond, we’ll show how one can track the size of allocated region s quickly
and with relative ease. Finally , we’ll discuss how to build a simple list
inside the free space to keep track of what is free and what isn ’t.
Splitting and Coalescing
A free list contains a set of elements that describe the free s pace still re-
maining in the heap. Thus, assume the following 30-byte heap :
free used free
0 10 20 30
The free list for this heap would have two elements on it. One entry de-
scribes the ﬁrst 10-byte free segment (bytes 0-9), and one en try describes
the other free segment (bytes 20-29):
head addr:0
len:10
addr:20
len:10 NULL
As described above, a request for anything greater than 10 by tes will
fail (returning NULL); there just isn’t a single contiguous chunk of mem-
ory of that size available. A request for exactly that size (1 0 bytes) could
be satisﬁed easily by either of the free chunks. But what happ ens if the
request is for something smaller than 10 bytes?
Assume we have a request for just a single byte of memory . In th is
case, the allocator will perform an action known as splitting: it will ﬁnd
2Once you hand a pointer to a chunk of memory to a C program, it is generally difﬁcult
to determine all references (pointers) to that region, whic h may be stored in other variables
or even in registers at a given point in execution. This may no t be the case in more strongly-
typed, garbage-collected languages, which would thus enab le compaction as a technique to
combat fragmentation.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 192

156 FREE -S PACE MANAGEMENT
a free chunk of memory that can satisfy the request and split i t into two.
The ﬁrst chunk it will return to the caller; the second chunk w ill remain
on the list. Thus, in our example above, if a request for 1 byte were made,
and the allocator decided to use the second of the two element s on the list
to satisfy the request, the call to malloc() would return 20 ( the address of
the 1-byte allocated region) and the list would end up lookin g like this:
head addr:0
len:10
addr:21
len:9 NULL
In the picture, you can see the list basically stays intact; the only change
is that the free region now starts at 21 instead of 20, and the l ength of that
free region is now just 9 3. Thus, the split is commonly used in allocators
when requests are smaller than the size of any particular fre e chunk.
A corollary mechanism found in many allocators is known as coalesc-
ing of free space. Take our example from above once more (free 10 b ytes,
used 10 bytes, and another free 10 bytes).
Given this (tiny) heap, what happens when an application calls free(10),
thus returning the space in the middle of the heap? If we simpl y add this
free space back into our list without too much thinking, we mi ght end up
with a list that looks like this:
head addr:10
len:10
addr:0
len:10
addr:20
len:10 NULL
Note the problem: while the entire heap is now free, it is seem ingly
divided into three chunks of 10 bytes each. Thus, if a user req uests 20
bytes, a simple list traversal will not ﬁnd such a free chunk, and return
failure.
What allocators do in order to avoid this problem is coalesce free space
when a chunk of memory is freed. The idea is simple: when retur ning a
free chunk in memory , look carefully at the addresses of the c hunk you
are returning as well as the nearby chunks of free space; if th e newly-
freed space sits right next to one (or two, as in this example) existing free
chunks, merge them into a single larger free chunk. Thus, wit h coalesc-
ing, our ﬁnal list should look like this:
head addr:0
len:30 NULL
Indeed, this is what the heap list looked like at ﬁrst, before any allo-
cations were made. With coalescing, an allocator can better ensure that
large free extents are available for the application.
3This discussion assumes that there are no headers, an unrealistic but simplifying assump-
tion we make for now.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 193

FREE -S PACE MANAGEMENT 157
ptr
The header used by malloc library
The 20 bytes returned to caller
Figure 17.1: An Allocated Region Plus Header
size: 20
magic: 1234567
hptr
ptr
The 20 bytes returned to caller
Figure 17.2: Speciﬁc Contents Of The Header
T racking The Size Of Allocated Regions
You might have noticed that the interface to free(void *ptr) does
not take a size parameter; thus it is assumed that given a poin ter, the
malloc library can quickly determine the size of the region o f memory
being freed and thus incorporate the space back into the free list.
To accomplish this task, most allocators store a little bit o f extra infor-
mation in a header block which is kept in memory , usually just before
the handed-out chunk of memory . Let’s look at an example agai n (Fig-
ure
17.1). In this example, we are examining an allocated block of siz e 20
bytes, pointed to by ptr; imagine the user called malloc() and stored
the results in ptr, e.g., ptr = malloc(20); .
The header minimally contains the size of the allocated regi on (in this
case, 20); it may also contain additional pointers to speed u p dealloca-
tion, a magic number to provide additional integrity checki ng, and other
information. Let’s assume a simple header which contains th e size of the
region and a magic number, like this:
typedef struct __header_t {
int size;
int magic;
} header_t;
The example above would look like what you see in Figure
17.2. When
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 194

158 FREE -S PACE MANAGEMENT
the user calls free(ptr), the library then uses simple pointer arithmetic
to ﬁgure out where the header begins:
void free(void *ptr) {
header_t *hptr = (void *)ptr - sizeof(header_t);
}
After obtaining such a pointer to the header, the library can easily de-
termine whether the magic number matches the expected value as a san-
ity check ( assert(hptr->magic == 1234567) ) and calculate the to-
tal size of the newly-freed region via simple math (i.e., add ing the size of
the header to size of the region). Note the small but critical detail in the
last sentence: the size of the free region is the size of the he ader plus the
size of the space allocated to the user. Thus, when a user requ ests N bytes
of memory , the library does not search for a free chunk of size N ; rather,
it searches for a free chunk of size N plus the size of the header.
Embedding A Free List
Thus far we have treated our simple free list as a conceptual e ntity; it is
just a list describing the free chunks of memory in the heap. B ut how do
we build such a list inside the free space itself?
In a more typical list, when allocating a new node, you would j ust call
malloc() when you need space for the node. Unfortunately , within the
memory-allocation library , you can’t do this! Instead, you need to build
the list inside the free space itself. Don’t worry if this sounds a little wei rd;
it is, but not so weird that you can’t do it!
Assume we have a 4096-byte chunk of memory to manage (i.e., th e
heap is 4KB). To manage this as a free list, we ﬁrst have to init ialize said
list; initially , the list should have one entry , of size 4096(minus the header
size). Here is the description of a node of the list:
typedef struct __node_t {
int size;
struct __node_t *next;
} node_t;
Now let’s look at some code that initializes the heap and puts the ﬁrst
element of the free list inside that space. We are assuming th at the heap is
built within some free space acquired via a call to the system call mmap();
this is not the only way to build such a heap but serves us well i n this
example. Here is the code:
// mmap() returns a pointer to a chunk of free space
node_t *head = mmap(NULL, 4096, PROT_READ|PROT_WRITE,
MAP_ANON|MAP_PRIVATE, -1, 0);
head->size = 4096 - sizeof(node_t);
head->next = NULL;
After running this code, the status of the list is that it has a single entry ,
of size 4088. Yes, this is a tiny heap, but it serves as a ﬁne exa mple for us
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 195

FREE -S PACE MANAGEMENT 159
size: 4088
next: 0
...
head [virtual address: 16KB]
header: size field
header: next field (NULL is 0)
the rest of the 4KB chunk
Figure 17.3: A Heap With One Free Chunk
size: 100
magic: 1234567
. . .
size: 3980
next: 0
. . .
ptr
[virtual address: 16KB]
head
The 100 bytes now allocated
The free 3980 byte chunk
Figure 17.4: A Heap: After One Allocation
here. The head pointer contains the beginning address of this range; let’s
assume it is 16KB (though any virtual address would be ﬁne). V isually ,
the heap thus looks like what you see in Figure 17.3.
Now , let’s imagine that a chunk of memory is requested, say of size
100 bytes. To service this request, the library will ﬁrst ﬁnd a chunk that is
large enough to accommodate the request; because there is on ly one free
chunk (size: 4088), this chunk will be chosen. Then, the chun k will be
split into two: one chunk big enough to service the request (and hea der,
as described above), and the remaining free chunk. Assuming an 8-byte
header (an integer size and an integer magic number), the spa ce in the
heap now looks like what you see in Figure 17.4.
Thus, upon the request for 100 bytes, the library allocated 1 08 bytes
out of the existing one free chunk, returns a pointer (marked ptr in the
ﬁgure above) to it, stashes the header information immediat ely before the
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 196

160 FREE -S PACE MANAGEMENT
size: 100
magic: 1234567
. . .
size: 100
magic: 1234567
. . .
size: 100
magic: 1234567
. . .
size: 3764
next: 0
. . .
sptr
[virtual address: 16KB]
head
100 bytes still allocated
100 bytes still allocated
 (but about to be freed)
100-bytes still allocated
The free 3764-byte chunk
Figure 17.5: Free Space With Three Chunks Allocated
allocated space for later use upon free(), and shrinks the one free node
in the list to 3980 bytes (4088 minus 108).
Now let’s look at the heap when there are three allocated regi ons, each
of 100 bytes (or 108 including the header). A visualization o f this heap is
shown in Figure 17.5.
As you can see therein, the ﬁrst 324 bytes of the heap are now al lo-
cated, and thus we see three headers in that space as well as th ree 100-
byte regions being used by the calling program. The free list remains
uninteresting: just a single node (pointed to by head), but now only 3764
bytes in size after the three splits. But what happens when th e calling
program returns some memory via free()?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 197

FREE -S PACE MANAGEMENT 161
size: 100
magic: 1234567
. . .
size: 100
next: 16708
. . .
size: 100
magic: 1234567
. . .
size: 3764
next: 0
. . .
[virtual address: 16KB]
head
sptr
100 bytes still allocated
(now a free chunk of memory)
100-bytes still allocated
The free 3764-byte chunk
Figure 17.6: Free Space With Two Chunks Allocated
In this example, the application returns the middle chunk of allocated
memory , by calling free(16500) (the value 16500 is arrived upon by
adding the start of the memory region, 16384, to the 108 of the previous
chunk and the 8 bytes of the header for this chunk). This value is shown
in the previous diagram by the pointer sptr.
The library immediately ﬁgures out the size of the free regio n, and
then adds the free chunk back onto the free list. Assuming we i nsert at
the head of the free list, the space now looks like this (Figur e 17.6).
And now we have a list that starts with a small free chunk (100 b ytes,
pointed to by the head of the list) and a large free chunk (3764 bytes).
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 198

162 FREE -S PACE MANAGEMENT
size: 100
next: 16492
. . .
size: 100
next: 16708
. . .
size: 100
next: 16384
. . .
size: 3764
next: 0
. . .
[virtual address: 16KB]
head
(now free)
(now free)
(now free)
The free 3764-byte chunk
Figure 17.7: A Non-Coalesced Free List
Our list ﬁnally has more than one element on it! And yes, the fr ee space
is fragmented, an unfortunate but common occurrence.
One last example: let’s assume now that the last two in-use ch unks are
freed. Without coalescing, you might end up with a free list t hat is highly
fragmented (see Figure 17.7).
As you can see from the ﬁgure, we now have a big mess! Why? Simple,
we forgot to coalesce the list. Although all of the memory is free, it is
chopped up into pieces, thus appearing as a fragmented memor y despite
not being one. The solution is simple: go through the list and merge
neighboring chunks; when ﬁnished, the heap will be whole aga in.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 199

FREE -S PACE MANAGEMENT 163
Growing The Heap
We should discuss one last mechanism found within many alloc ation li-
braries. Speciﬁcally , what should you do if the heap runs out of space?
The simplest approach is just to fail. In some cases this is th e only option,
and thus returning NULL is an honorable approach. Don’t feel bad! You
tried, and though you failed, you fought the good ﬁght.
Most traditional allocators start with a small-sized heap a nd then re-
quest more memory from the OS when they run out. Typically , this means
they make some kind of system call (e.g., sbrk in most U NIX systems) to
grow the heap, and then allocate the new chunks from there. To service
the sbrk request, the OS ﬁnds free physical pages, maps them into the
address space of the requesting process, and then returns th e value of
the end of the new heap; at that point, a larger heap is availab le, and the
request can be successfully serviced.
17.3 Basic Strategies
Now that we have some machinery under our belt, let’s go over s ome
basic strategies for managing free space. These approaches are mostly
based on pretty simple policies that you could think up yours elf; try it
before reading and see if you come up with all of the alternati ves (or
maybe some new ones!).
The ideal allocator is both fast and minimizes fragmentatio n. Unfortu-
nately , because the stream of allocation and free requests can be arbitrary
(after all, they are determined by the programmer), any part icular strat-
egy can do quite badly given the wrong set of inputs. Thus, we w ill not
describe a “best” approach, but rather talk about some basic s and discuss
their pros and cons.
Best Fit
The best ﬁt strategy is quite simple: ﬁrst, search through the free list and
ﬁnd chunks of free memory that are as big or bigger than the req uested
size. Then, return the one that is the smallest in that group o f candidates;
this is the so called best-ﬁt chunk (it could be called smalle st ﬁt too). One
pass through the free list is enough to ﬁnd the correct block t o return.
The intuition behind best ﬁt is simple: by returning a block that is close
to what the user asks, best ﬁt tries to reduce wasted space. However, there
is a cost; naive implementations pay a heavy performance pen alty when
performing an exhaustive search for the correct free block.
Worst Fit
The worst ﬁt approach is the opposite of best ﬁt; ﬁnd the largest chunk
and return the requested amount; keep the remaining (large) chunk on
the free list. Worst ﬁt tries to thus leave big chunks free ins tead of lots of
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 200

164 FREE -S PACE MANAGEMENT
small chunks that can arise from a best-ﬁt approach. Once aga in, how-
ever, a full search of free space is required, and thus this ap proach can be
costly . Worse, most studies show that it performs badly , leading to excess
fragmentation while still having high overheads.
First Fit
The ﬁrst ﬁt method simply ﬁnds the ﬁrst block that is big enough and
returns the requested amount to the user. As before, the rema ining free
space is kept free for subsequent requests.
First ﬁt has the advantage of speed – no exhaustive search of a ll the
free spaces are necessary – but sometimes pollutes the begin ning of the
free list with a small objects. Thus, how the allocator manag es the free
list’s order becomes an issue. One approach is to use address-based or-
dering; by keeping the list ordered by the address of the free space, coa-
lescing becomes easier, and fragmentation tends to be reduc ed.
Next Fit
Instead of always beginning the ﬁrst-ﬁt search at the beginn ing of the list,
the next ﬁt algorithm keeps an extra pointer to the location within the
list where one was looking last. The idea is to spread the sear ches for
free space throughout the list more uniformly , thus avoidin g splintering
of the beginning of the list. The performance of such an appro ach is quite
similar to ﬁrst ﬁt, as an exhaustive search is once again avoi ded.
Examples
Here are a few examples of the above strategies. Envision a fr ee list with
three elements on it, of sizes 10, 30, and 20 (we’ll ignore hea ders and other
details here, instead just focusing on how strategies opera te):
head 10 30 20 NULL
Assume an allocation request of size 15. A best-ﬁt approach w ould
search the entire list and ﬁnd that 20 was the best ﬁt, as it is t he smallest
free space that can accommodate the request. The resulting f ree list:
head 10 30 5 NULL
As happens in this example, and often happens with a best-ﬁt a p-
proach, a small free chunk is now left over. A worst-ﬁt approach is similar
but instead ﬁnds the largest chunk, in this example 30. The re sulting list:
head 10 15 20 NULL
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

