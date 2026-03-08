# Document: operating_systems_three_easy_pieces (Pages 81 to 120)

## Page 81

6
Mechanism: Limited Direct Execution
In order to virtualize the CPU, the operating system needs to somehow
share the physical CPU among many jobs running seemingly at t he same
time. The basic idea is simple: run one process for a little wh ile, then
run another one, and so forth. By time sharing the CPU in this manner,
virtualization is achieved.
There are a few challenges, however, in building such virtua lization
machinery . The ﬁrst is performance: how can we implement virtualiza-
tion without adding excessive overhead to the system? The se cond is
control: how can we run processes efﬁciently while retaining contro l over
the CPU? Control is particularly important to the OS, as it is in charge of
resources; without control, a process could simply run fore ver and take
over the machine, or access information that it should not be allowed to
access. Attaining performance while maintaining control i s thus one of
the central challenges in building an operating system.
THE CRUX :
HOW TO EFFICIENTLY VIRTUALIZE THE CPU W ITH CONTROL
The OS must virtualize the CPU in an efﬁcient manner, but whil e re-
taining control over the system. To do so, both hardware and o perating
systems support will be required. The OS will often use a judi cious bit of
hardware support in order to accomplish its work effectivel y .
6.1 Basic Technique: Limited Direct Execution
To make a program run as fast as one might expect, not surprisi ngly
OS developers came up with a technique, which we call limited direct
execution. The “direct execution” part of the idea is simple: just run t he
program directly on the CPU. Thus, when the OS wishes to start a pro-
gram running, it creates a process entry for it in a process li st, allocates
some memory pages for it, loads the program code into memory ( from
45

## Page 82

46 MECHANISM : L IMITED DIRECT EXECUTION
OS Program
Create entry for process list
Allocate memory for program
Load program into memory
Set up stack with argc/argv
Clear registers
Execute call main()
Run main()
Execute return from main
Free memory of process
Remove from process list
Table 6.1: Direction Execution Protocol (Without Limits)
disk), locates its entry point (i.e., the main() routine or something simi-
lar), jumps to it, and starts running the user’s code. Table
6.1 shows this
basic direct execution protocol (without any limits, yet), using a normal
call and return to jump to the program’s main() and later to get back
into the kernel.
Sounds simple, no? But this approach gives rise to a few probl ems
in our quest to virtualize the CPU. The ﬁrst is simple: if we ju st run a
program, how can the OS make sure the program doesn’t do anyth ing
that we don’t want it to do, while still running it efﬁciently ? The second:
when we are running a process, how does the operating system s top it
from running and switch to another process, thus implementi ng the time
sharing we require to virtualize the CPU?
In answering these questions below , we’ll get a much better s ense of
what is needed to virtualize the CPU. In developing these tec hniques,
we’ll also see where the “limited” part of the name arises fro m; without
limits on running programs, the OS wouldn’t be in control of a nything
and thus would be “just a library” – a very sad state of affairs for an
aspiring operating system!
6.2 Problem #1: Restricted Operations
Direct execution has the obvious advantage of being fast; th e program
runs natively on the hardware CPU and thus executes as quickl y as one
would expect. But running on the CPU introduces a problem: wh at if
the process wishes to perform some kind of restricted operat ion, such
as issuing an I/O request to a disk, or gaining access to more s ystem
resources such as CPU or memory?
THE CRUX : H OW TO PERFORM RESTRICTED OPERATIONS
A process must be able to perform I/O and some other restricte d oper-
ations, but without giving the process complete control ove r the system.
How can the OS and hardware work together to do so?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 83

MECHANISM : L IMITED DIRECT EXECUTION 47
TIP : U SE PROTECTED CONTROL TRANSFER
The hardware assists the OS by providing different modes of e xecution.
In user mode, applications do not have full access to hardware resources .
In kernel mode , the OS has access to the full resources of the machine.
Special instructions to trap into the kernel and return-from-trap back to
user-mode programs are also provided, as well instructions that allow the
OS to tell the hardware where the trap table resides in memory .
One approach would simply be to let any process do whatever itwants
in terms of I/O and other related operations. However, doing so would
prevent the construction of many kinds of systems that are de sirable. For
example, if we wish to build a ﬁle system that checks permissi ons before
granting access to a ﬁle, we can’t simply let any user process issue I/Os
to the disk; if we did, a process could simply read or write the entire disk
and thus all protections would be lost.
Thus, the approach we take is to introduce a new processor mod e,
known as user mode; code that runs in user mode is restricted in what it
can do. For example, when running in user mode, a process can’ t issue
I/O requests; doing so would result in the processor raising an exception;
the OS would then likely kill the process.
In contrast to user mode is kernel mode, which the operating system
(or kernel) runs in. In this mode, code that runs can do what it likes, in-
cluding privileged operations such as issuing I/O requests and executing
all types of restricted instructions.
We are still left with a challenge, however: what should a use r pro-
cess do when it wishes to perform some kind of privileged oper ation,
such as reading from disk? To enable this, virtually all mode rn hard-
ware provides the ability for user programs to perform a system call .
Pioneered on ancient machines such as the Atlas [K+61,L78], system calls
allow the kernel to carefully expose certain key pieces of fu nctionality to
user programs, such as accessing the ﬁle system, creating an d destroy-
ing processes, communicating with other processes, and all ocating more
memory . Most operating systems provide a few hundred calls ( see the
POSIX standard for details [P10]); early Unix systems expos ed a more
concise subset of around twenty calls.
To execute a system call, a program must execute a specialtrap instruc-
tion. This instruction simultaneously jumps into the kerne l and raises the
privilege level to kernel mode; once in the kernel, the system can now per-
form whatever privileged operations are needed (if allowed), and thus do
the required work for the calling process. When ﬁnished, the OS calls a
special return-from-trap instruction, which, as you might expect, returns
into the calling user program while simultaneously reducin g the privi-
lege level back to user mode.
The hardware needs to be a bit careful when executing a trap, i n that
it must make sure to save enough of the caller’s register stat e in order
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 84

48 MECHANISM : L IMITED DIRECT EXECUTION
ASIDE : WHY SYSTEM CALLS LOOK LIKE PROCEDURE CALLS
You may wonder why a call to a system call, such as open() or read(),
looks exactly like a typical procedure call in C; that is, if i t looks just like
a procedure call, how does the system know it’s a system call, and do all
the right stuff? The simple reason: it is a procedure call, but hidden in-
side that procedure call is the famous trap instruction. Mor e speciﬁcally ,
when you call open() (for example), you are executing a procedure call
into the C library . Therein, whether for open() or any of the other sys-
tem calls provided, the library uses an agreed-upon calling convention
with the kernel to put the arguments to open in well-known loc ations
(e.g., on the stack, or in speciﬁc registers), puts the syste m-call number
into a well-known location as well (again, onto the stack or a register),
and then executes the aforementioned trap instruction. The code in the
library after the trap unpacks return values and returns con trol to the
program that issued the system call. Thus, the parts of the C l ibrary that
make system calls are hand-coded in assembly , as they need to carefully
follow convention in order to process arguments and return v alues cor-
rectly , as well as execute the hardware-speciﬁc trap instruction. And now
you know why you personally don’t have to write assembly code to trap
into an OS; somebody has already written that assembly for yo u.
to be able to return correctly when the OS issues the return-f rom-trap
instruction. On x86, for example, the processor will push th e program
counter, ﬂags, and a few other registers onto a per-process kernel stack;
the return-from-trap will pop these values off the stack and resume exe-
cution of the user-mode program (see the Intel systems manua ls [I11] for
details). Other hardware systems use different convention s, but the basic
concepts are similar across platforms.
There is one important detail left out of this discussion: ho w does the
trap know which code to run inside the OS? Clearly , the callin g process
can’t specify an address to jump to (as you would when making a pro-
cedure call); doing so would allow programs to jump anywhere into the
kernel which clearly is a bad idea (imagine jumping into code to access
a ﬁle, but just after a permission check; in fact, it is likely such ability
would enable a wily programmer to get the kernel to run arbitr ary code
sequences [S07]). Thus the kernel must carefully control wh at code exe-
cutes upon a trap.
The kernel does so by setting up a trap table at boot time. When the
machine boots up, it does so in privileged (kernel) mode, and thus is
free to conﬁgure machine hardware as need be. One of the ﬁrst t hings
the OS thus does is to tell the hardware what code to run when ce rtain
exceptional events occur. For example, what code should run when a
hard-disk interrupt takes place, when a keyboard interrupt occurs, or
when program makes a system call? The OS informs the hardware of
the locations of these trap handlers , usually with some kind of special
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 85

MECHANISM : L IMITED DIRECT EXECUTION 49
OS @ boot Hardware
(kernel mode)
initialize trap table
remember address of...
syscall handler
OS @ run Hardware Program
(kernel mode) (user mode)
Create entry for process list
Allocate memory for program
Load program into memory
Setup user stack with argv
Fill kernel stack with reg/PC
return-from-trap
restore regs from kernel stack
move to user mode
jump to main
Run main()
...
Call system call
trap into OS
save regs to kernel stack
move to kernel mode
jump to trap handler
Handle trap
Do work of syscall
return-from-trap
restore regs from kernel stack
move to user mode
jump to PC after trap
...
return from main
trap (via exit())
Free memory of process
Remove from process list
Table 6.2: Limited Direction Execution Protocol
instruction. Once the hardware is informed, it remembers th e location of
these handlers until the machine is next rebooted, and thus t he hardware
knows what to do (i.e., what code to jump to) when system calls and other
exceptional events take place.
One last aside: being able to execute the instruction to tell the hard-
ware where the trap tables are is a very powerful capability . Thus, as you
might have guessed, it is also a privileged operation. If you try to exe-
cute this instruction in user mode, the hardware won’t let yo u, and you
can probably guess what will happen (hint: adios, offending program).
Point to ponder: what horrible things could you do to a system if you
could install your own trap table? Could you take over the mac hine?
The timeline (with time increasing downward, in Table
6.2) summa-
rizes the protocol. We assume each process has a kernel stack where reg-
isters (including general purpose registers and the progra m counter) are
saved to and restored from (by the hardware) when transitioning into and
out of the kernel.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 86

50 MECHANISM : L IMITED DIRECT EXECUTION
There are two phases in the LDE protocol. In the ﬁrst (at boot t ime),
the kernel initializes the trap table, and the CPU remembers its location
for subsequent use. The kernel does so via a privileged instr uction (all
privileged instructions are highlighted in bold).
In the second (when running a process), the kernel sets up a few things
(e.g., allocating a node on the process list, allocating mem ory) before us-
ing a return-from-trap instruction to start the execution o f the process;
this switches the CPU to user mode and begins running the proc ess.
When the process wishes to issue a system call, it traps back i nto the OS,
which handles it and once again returns control via a return- from-trap
to the process. The process then completes its work, and retu rns from
main(); this usually will return into some stub code which will prop erly
exit the program (say , by calling theexit() system call, which traps into
the OS). At this point, the OS cleans up and we are done.
6.3 Problem #2: Switching Between Processes
The next problem with direct execution is achieving a switch between
processes. Switching between processes should be simple, r ight? The
OS should just decide to stop one process and start another. W hat’s the
big deal? But it actually is a little bit tricky: speciﬁcally , if a process is
running on the CPU, this by deﬁnition means the OS is not running. If
the OS is not running, how can it do anything at all? (hint: it c an’t) While
this sounds almost philosophical, it is a real problem: ther e is clearly no
way for the OS to take an action if it is not running on the CPU. T hus we
arrive at the crux of the problem.
THE CRUX : H OW TO REGAIN CONTROL OF THE CPU
How can the operating system regain control of the CPU so that it can
switch between processes?
A Cooperative Approach: Wait For System Calls
One approach that some systems have taken in the past (for exa mple,
early versions of the Macintosh operating system [M11], or t he old Xerox
Alto system [A79]) is known as the cooperative approach. In this style,
the OS trusts the processes of the system to behave reasonably . Processes
that run for too long are assumed to periodically give up the C PU so that
the OS can decide to run some other task.
Thus, you might ask, how does a friendly process give up the CP U in
this utopian world? Most processes, as it turns out, transfe r control of
the CPU to the OS quite frequently by making system calls, for example,
to open a ﬁle and subsequently read it, or to send a message to a nother
machine, or to create a new process. Systems like this often i nclude an
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 87

MECHANISM : L IMITED DIRECT EXECUTION 51
TIP : D EALING WITH APPLICATION MISBEHAVIOR
Operating systems often have to deal with misbehaving proce sses, those
that either through design (maliciousness) or accident (bu gs) attempt to
do something that they shouldn’t. In modern systems, the way the OS
tries to handle such malfeasance is to simply terminate the o ffender. One
strike and you’re out! Perhaps brutal, but what else should t he OS do
when you try to access memory illegally or execute an illegal instruction?
explicit yield system call, which does nothing except to transfer control
to the OS so it can run other processes.
Applications also transfer control to the OS when they do som ething
illegal. For example, if an application divides by zero, or t ries to access
memory that it shouldn’t be able to access, it will generate a trap to the
OS. The OS will then have control of the CPU again (and likely t erminate
the offending process).
Thus, in a cooperative scheduling system, the OS regains con trol of
the CPU by waiting for a system call or an illegal operation of some kind
to take place. You might also be thinking: isn’t this passive approach less
than ideal? What happens, for example, if a process (whether malicious,
or just full of bugs) ends up in an inﬁnite loop, and never make s a system
call? What can the OS do then?
A Non-Cooperative Approach: The OS T akes Control
Without some additional help from the hardware, it turns outthe OS can’t
do much at all when a process refuses to make system calls (or m istakes)
and thus return control to the OS. In fact, in the cooperative approach,
your only recourse when a process gets stuck in an inﬁnite loo p is to
resort to the age-old solution to all problems in computer systems: reboot
the machine. Thus, we again arrive at a subproblem of our general quest
to gain control of the CPU.
THE CRUX : H OW TO GAIN CONTROL WITHOUT COOPERATION
How can the OS gain control of the CPU even if processes are notbeing
cooperative? What can the OS do to ensure a rogue process does not take
over the machine?
The answer turns out to be simple and was discovered by a numbe r
of people building computer systems many years ago: a timer interrupt
[M+63]. A timer device can be programmed to raise an interrup t every
so many milliseconds; when the interrupt is raised, the curr ently running
process is halted, and a pre-conﬁgured interrupt handler in the OS runs.
At this point, the OS has regained control of the CPU, and thus can do
what it pleases: stop the current process, and start a differ ent one.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 88

52 MECHANISM : L IMITED DIRECT EXECUTION
TIP : U SE THE TIMER INTERRUPT TO REGAIN CONTROL
The addition of a timer interrupt gives the OS the ability to run again
on a CPU even if processes act in a non-cooperative fashion. T hus, this
hardware feature is essential in helping the OS maintain con trol of the
machine.
As we discussed before with system calls, the OS must inform t he
hardware of which code to run when the timer interrupt occurs ; thus,
at boot time, the OS does exactly that. Second, also during th e boot
sequence, the OS must start the timer, which is of course a pri vileged
operation. Once the timer has begun, the OS can thus feel safe in that
control will eventually be returned to it, and thus the OS is f ree to run
user programs. The timer can also be turned off (also a privil eged opera-
tion), something we will discuss later when we understand co ncurrency
in more detail.
Note that the hardware has some responsibility when an inter rupt oc-
curs, in particular to save enough of the state of the program that was
running when the interrupt occurred such that a subsequent return-from-
trap instruction will be able to resume the running program c orrectly .
This set of actions is quite similar to the behavior of the har dware during
an explicit system-call trap into the kernel, with various r egisters thus
getting saved (e.g., onto a kernel stack) and thus easily res tored by the
return-from-trap instruction.
Saving and Restoring Context
Now that the OS has regained control, whether cooperatively via a sys-
tem call, or more forcefully via a timer interrupt, a decisio n has to be
made: whether to continue running the currently-running pr ocess, or
switch to a different one. This decision is made by a part of th e operating
system known as the scheduler; we will discuss scheduling policies in
great detail in the next few chapters.
If the decision is made to switch, the OS then executes a low-l evel
piece of code which we refer to as a context switch. A context switch is
conceptually simple: all the OS has to do is save a few registe r values
for the currently-executing process (onto its kernel stack , for example)
and restore a few for the soon-to-be-executing process (fro m its kernel
stack). By doing so, the OS thus ensures that when the return- from-trap
instruction is ﬁnally executed, instead of returning to the process that was
running, the system resumes execution of another process.
To save the context of the currently-running process, the OS will exe-
cute some low-level assembly code to save the general purpos e registers,
PC, as well as the kernel stack pointer of the currently-runn ing process,
and then restore said registers, PC, and switch to the kernel stack for the
soon-to-be-executing process. By switching stacks, the ke rnel enters the
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 89

MECHANISM : L IMITED DIRECT EXECUTION 53
OS @ boot Hardware
(kernel mode)
initialize trap table
remember addresses of...
syscall handler
timer handler
start interrupt timer
start timer
interrupt CPU in X ms
OS @ run Hardware Program
(kernel mode) (user mode)
Process A
...
timer interrupt
save regs(A) to k-stack(A)
move to kernel mode
jump to trap handler
Handle the trap
Call switch() routine
save regs(A) to proc-struct(A)
restore regs(B) from proc-struct(B)
switch to k-stack(B)
return-from-trap (into B)
restore regs(B) from k-stack(B)
move to user mode
jump to B’s PC
Process B
...
Table 6.3: Limited Direction Execution Protocol (Timer Interrupt)
call to the switch code in the context of one process (the one t hat was in-
terrupted) and returns in the context of another (the soon-to-be-executing
one). When the OS then ﬁnally executes a return-from-trap in struction,
the soon-to-be-executing process becomes the currently-r unning process.
And thus the context switch is complete.
A timeline of the entire process is shown in Table
6.3. In this exam-
ple, Process A is running and then is interrupted by the timer interrupt.
The hardware saves its state (onto its kernel stack) and ente rs the kernel
(switching to kernel mode). In the timer interrupt handler, the OS decides
to switch from running Process A to Process B. At that point, i t calls the
switch() routine, which carefully saves current register values (into the
process structure of A), restores the registers of Process B (from its process
structure entry), and then switches contexts, speciﬁcally by changing the
stack pointer to use B’s kernel stack (and not A’s). Finally , the OS returns-
from-trap, which restores B’s register state and starts run ning it.
Note that there are two types of register saves/restores tha t happen
during this protocol. The ﬁrst is when the timer interrupt oc curs; in this
case, the user register state of the running process is implicitly saved by
the hardware, using the kernel stack of that process. The second is when
the OS decides to switch from A to B; in this case, the kernel register state
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 90

54 MECHANISM : L IMITED DIRECT EXECUTION
1 # void swtch(struct context **old, struct context *new);
2 #
3 # Save current register context in old
4 # and then load register context from new.
5 .globl swtch
6 swtch:
7 # Save old registers
8 movl 4(%esp), %eax # put old ptr into eax
9 popl 0(%eax) # save the old IP
10 movl %esp, 4(%eax) # and stack
11 movl %ebx, 8(%eax) # and other registers
12 movl %ecx, 12(%eax)
13 movl %edx, 16(%eax)
14 movl %esi, 20(%eax)
15 movl %edi, 24(%eax)
16 movl %ebp, 28(%eax)
17
18 # Load new registers
19 movl 4(%esp), %eax # put new ptr into eax
20 movl 28(%eax), %ebp # restore other registers
21 movl 24(%eax), %edi
22 movl 20(%eax), %esi
23 movl 16(%eax), %edx
24 movl 12(%eax), %ecx
25 movl 8(%eax), %ebx
26 movl 4(%eax), %esp # stack is switched here
27 pushl 0(%eax) # return addr put in place
28 ret # finally return into new ctxt
Figure 6.1: The xv6 Context Switch Code
is explicitly saved by the software (i.e., the OS), but this time into memory
in the process structure of the process. The latter action mo ves the system
from running as if it just trapped into the kernel from A to as i f it just
trapped into the kernel from B.
To give you a better sense of how such a switch is enacted, Figu re
6.1
shows the context switch code for xv6. See if you can make sens e of it
(you’ll have to know a bit of x86, as well as some xv6, to do so). The
context structures old and new are found the old and new process’s
process structures, respectively .
6.4 Worried About Concurrency?
Some of you, as attentive and thoughtful readers, may be now t hink-
ing: “Hmm... what happens when, during a system call, a timer interrupt
occurs?” or “What happens when you’re handling one interrup t and an-
other one happens? Doesn’t that get hard to handle in the kern el?” Good
questions – we really have some hope for you yet!
The answer is yes, the OS does indeed need to be concerned as to what
happens if, during interrupt or trap handling, another inte rrupt occurs.
This, in fact, is the exact topic of the entire second piece of this book, on
concurrency; we’ll defer a detailed discussion until then.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 91

MECHANISM : L IMITED DIRECT EXECUTION 55
ASIDE : HOW LONG CONTEXT SWITCHES TAKE
A natural question you might have is: how long does something like a
context switch take? Or even a system call? For those of you th at are cu-
rious, there is a tool called lmbench [MS96] that measures exactly those
things, as well as a few other performance measures that migh t be rele-
vant.
Results have improved quite a bit over time, roughly trackin g processor
performance. For example, in 1996 running Linux 1.3.37 on a 2 00-MHz
P6 CPU, system calls took roughly 4 microseconds, and a conte xt switch
roughly 6 microseconds [MS96]. Modern systems perform almo st an or-
der of magnitude better, with sub-microsecond results on sy stems with
2- or 3-GHz processors.
It should be noted that not all operating-system actions tra ck CPU per-
formance. As Ousterhout observed, many OS operations are me mory
intensive, and memory bandwidth has not improved as dramati cally as
processor speed over time [O90]. Thus, depending on your wor kload,
buying the latest and greatest processor may not speed up you r OS as
much as you might hope.
To whet your appetite, we’ll just sketch some basics of how th e OS
handles these tricky situations. One simple thing an OS migh t do is dis-
able interrupts during interrupt processing; doing so ensures that when
one interrupt is being handled, no other one will be delivere d to the CPU.
Of course, the OS has to be careful in doing so; disabling inte rrupts for
too long could lead to lost interrupts, which is (in technica l terms) bad.
Operating systems also have developed a number of sophistic ated
locking schemes to protect concurrent access to internal data struc tures.
This enables multiple activities to be on-going within the k ernel at the
same time, particularly useful on multiprocessors. As we’l l see in the
next piece of this book on concurrency , though, such locking can be com-
plicated and lead to a variety of interesting and hard-to-ﬁn d bugs.
6.5 Summary
We have described some key low-level mechanisms to implement CPU
virtualization, a set of techniques which we collectively refer to as limited
direct execution. The basic idea is straightforward: just run the program
you want to run on the CPU, but ﬁrst make sure to set up the hardw are
so as to limit what the process can do without OS assistance.
This general approach is taken in real life as well. For examp le, those
of you who have children, or, at least, have heard of children , may be
familiar with the concept of baby prooﬁng a room: locking cabinets con-
taining dangerous stuff and covering electrical sockets. W hen the room is
thus readied, you can let your baby roam freely , secure in the knowledge
that the most dangerous aspects of the room have been restric ted.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 92

56 MECHANISM : L IMITED DIRECT EXECUTION
TIP : R EBOOT IS USEFUL
Earlier on, we noted that the only solution to inﬁnite loops ( and similar
behaviors) under cooperative preemption is to reboot the machine. While
you may scoff at this hack, researchers have shown that reboo t (or in gen-
eral, starting over some piece of software) can be a hugely us eful tool in
building robust systems [C+04].
Speciﬁcally , reboot is useful because it moves software bac k to a known
and likely more tested state. Reboots also reclaim stale or l eaked re-
sources (e.g., memory) which may otherwise be hard to handle . Finally ,
reboots are easy to automate. For all of these reasons, it is n ot uncommon
in large-scale cluster Internet services for system manage ment software
to periodically reboot sets of machines in order to reset the m and thus
obtain the advantages listed above.
Thus, next time you reboot, you are not just enacting some ugl y hack.
Rather, you are using a time-tested approach to improving th e behavior
of a computer system. Well done!
In an analogous manner, the OS “baby proofs” the CPU, by ﬁrst ( dur-
ing boot time) setting up the trap handlers and starting an interrupt timer,
and then by only running processes in a restricted mode. By do ing so, the
OS can feel quite assured that processes can run efﬁciently , only requir-
ing OS intervention to perform privileged operations or whe n they have
monopolized the CPU for too long and thus need to be switched o ut.
We thus have the basic mechanisms for virtualizing the CPU in place.
But a major question is left unanswered: which process shoul d we run at
a given time? It is this question that the scheduler must answ er, and thus
the next topic of our study .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 93

MECHANISM : L IMITED DIRECT EXECUTION 57
References
[A79] “Alto User’s Handbook”
Xerox Palo Alto Research Center, September 1979
Available: http://history-computer.com/Library/AltoUsersHandbook.pdf
An amazing system, way ahead of its time. Became famous becau se Steve Jobs visited, took notes, and
built Lisa and eventually Mac.
[C+04] “Microreboot – A Technique for Cheap Recovery”
George Candea, Shinichi Kawamoto, Yuichi Fujiki, Greg Frie dman, Armando Fox
OSDI ’04, San Francisco, CA, December 2004
An excellent paper pointing out how far one can go with reboot in building more robust systems.
[I11] “Intel 64 and IA-32 Architectures Software Developer ’s Manual”
V olume 3A and 3B: System Programming Guide
Intel Corporation, January 2011
[K+61] “One-Level Storage System”
T. Kilburn, D.B.G. Edwards, M.J. Lanigan, F.H. Sumner
IRE Transactions on Electronic Computers, April 1962
The Atlas pioneered much of what you see in modern systems. Ho wever, this paper is not the best one
to read. If you were to only read one, you might try the histori cal perspective below [L78].
[L78] “The Manchester Mark I and Atlas: A Historical Perspec tive”
S. H. Lavington
Communications of the ACM, 21:1, January 1978
A history of the early development of computers and the pione ering efforts of Atlas.
[M+63] “A Time-Sharing Debugging System for a Small Compute r”
J. McCarthy , S. Boilen, E. Fredkin, J. C. R. Licklider
AFIPS ’63 (Spring), May , 1963, New York, USA
An early paper about time-sharing that refers to using a time r interrupt; the quote that discusses it:
“The basic task of the channel 17 clock routine is to decide wh ether to remove the current user from core
and if so to decide which user program to swap in as he goes out. ”
[MS96] “lmbench: Portable tools for performance analysis”
Larry McV oy and Carl Staelin
USENIX Annual Technical Conference, January 1996
A fun paper about how to measure a number of different things a bout your OS and its performance.
Download lmbench and give it a try.
[M11] “Mac OS 9”
January 2011
Available: http://en.wikipedia.org/wiki/Mac
OS 9
[O90] “Why Aren’t Operating Systems Getting Faster as Fast a s Hardware?”
J. Ousterhout
USENIX Summer Conference, June 1990
A classic paper on the nature of operating system performanc e.
[P10] “The Single UNIX Speciﬁcation, V ersion 3”
The Open Group, May 2010
Available: http://www.unix.org/version3/
This is hard and painful to read, so probably avoid it if you ca n.
[S07] “The Geometry of Innocent Flesh on the Bone:
Return-into-libc without Function Calls (on the x86)”
Hovav Shacham
CCS ’07, October 2007
One of those awesome, mind-blowing ideas that you’ll see in r esearch from time to time. The author
shows that if you can jump into code arbitrarily, you can esse ntially stitch together any code sequence
you like (given a large code base) – read the paper for the deta ils. The technique makes it even harder to
defend against malicious attacks, alas.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 94

58 MECHANISM : L IMITED DIRECT EXECUTION
Homework (Measurement)
ASIDE : MEASUREMENT HOMEWORKS
Measurement homeworks are small exercises where you write c ode to
run on a real machine, in order to measure some aspect of OS or hardware
performance. The idea behind such homeworks is to give you a l ittle bit
of hands-on experience with a real operating system.
In this homework, you’ll measure the costs of a system call an d context
switch. Measuring the cost of a system call is relatively easy . For example,
you could repeatedly call a simple system call (e.g., perfor ming a 0-byte
read), and time how long it takes; dividing the time by the num ber of
iterations gives you an estimate of the cost of a system call.
One thing you’ll have to take into account is the precision an d accu-
racy of your timer. A typical timer that you can use is gettimeofday();
read the man page for details. What you’ll see there is that gettimeofday()
returns the time in microseconds since 1970; however, this d oes not mean
that the timer is precise to the microsecond. Measure back-t o-back calls
to gettimeofday() to learn something about how precise the timer re-
ally is; this will tell you how many iterations of your null sy stem-call
test you’ll have to run in order to get a good measurement resu lt. If
gettimeofday() is not precise enough for you, you might look into
using the rdtsc instruction available on x86 machines.
Measuring the cost of a context switch is a little trickier. T he lmbench
benchmark does so by running two processes on a single CPU, an d set-
ting up two U NIX pipes between them; a pipe is just one of many ways
processes in a U NIX system can communicate with one another. The ﬁrst
process then issues a write to the ﬁrst pipe, and waits for a re ad on the
second; upon seeing the ﬁrst process waiting for something t o read from
the second pipe, the OS puts the ﬁrst process in the blocked st ate, and
switches to the other process, which reads from the ﬁrst pipe and then
writes to the second. When the second process tries to read fr om the ﬁrst
pipe again, it blocks, and thus the back-and-forth cycle of c ommunication
continues. By measuring the cost of communicating like this repeatedly ,
lmbench can make a good estimate of the cost of a context switc h. You
can try to re-create something similar here, using pipes, or perhaps some
other communication mechanism such as U NIX sockets.
One difﬁculty in measuring context-switch cost arises in sy stems with
more than one CPU; what you need to do on such a system is ensure that
your context-switching processes are located on the same pr ocessor. For-
tunately , most operating systems have calls to bind a proces s to a partic-
ular processor; on Linux, for example, the sched setaffinity() call
is what you’re looking for. By ensuring both processes are on the same
processor, you are making sure to measure the cost of the OS st opping
one process and restoring another on the same CPU.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 95

7
Scheduling: Introduction
By now low-level mechanisms of running processes (e.g., context switch-
ing) should be clear; if they are not, go back a chapter or two, and read the
description of how that stuff works again. However, we have y et to un-
derstand the high-level policies that an OS scheduler employs. We will
now do just that, presenting a series of scheduling policies (sometimes
called disciplines) that various smart and hard-working people have de-
veloped over the years.
The origins of scheduling, in fact, predate computer system s; early
approaches were taken from the ﬁeld of operations managemen t and ap-
plied to computers. This reality should be no surprise: asse mbly lines
and many other human endeavors also require scheduling, and many of
the same concerns exist therein, including a laser-like desire for efﬁciency .
And thus, our problem:
THE CRUX : H OW TO DEVELOP SCHEDULING POLICY
How should we develop a basic framework for thinking about
scheduling policies? What are the key assumptions? What met rics are
important? What basic approaches have been used in the earli est of com-
puter systems?
7.1 Workload Assumptions
Before getting into the range of possible policies, let us ﬁr st make a
number of simplifying assumptions about the processes runn ing in the
system, sometimes collectively called the workload. Determining the
workload is a critical part of building policies, and the mor e you know
about workload, the more ﬁne-tuned your policy can be.
The workload assumptions we make here are clearly unrealist ic, but
that is alright (for now), because we will relax them as we go, and even-
tually develop what we will refer to as ... (dramatic pause) ...
59

## Page 96

60 SCHEDULING : I NTRODUCTION
a fully-operational scheduling discipline 1.
We will make the following assumptions about the processes, some-
times called jobs, that are running in the system:
1. Each job runs for the same amount of time.
2. All jobs arrive at the same time.
3. All jobs only use the CPU (i.e., they perform no I/O)
4. The run-time of each job is known.
We said all of these assumptions were unrealistic, but just a s some an-
imals are more equal than others in Orwell’s Animal Farm [O45], some
assumptions are more unrealistic than others in this chapte r. In particu-
lar, it might bother you that the run-time of each job is known : this would
make the scheduler omniscient, which, although it would be g reat (prob-
ably), is not likely to happen anytime soon.
7.2 Scheduling Metrics
Beyond making workload assumptions, we also need one more th ing
to enable us to compare different scheduling policies: a scheduling met-
ric. A metric is just something that we use to measure something, and
there are a number of different metrics that make sense in sch eduling.
For now , however, let us also simplify our life by simply havi ng a sin-
gle metric: turnaround time . The turnaround time of a job is deﬁned
as the time at which the job completes minus the time at which t he job
arrived in the system. More formally , the turnaround time Tturnaround is:
Tturnaround = Tcompletion − Tarrival (7.1)
Because we have assumed that all jobs arrive at the same time, for now
Tarrival = 0 and hence Tturnaround = Tcompletion. This fact will change
as we relax the aforementioned assumptions.
You should note that turnaround time is a performance metric, which
will be our primary focus this chapter. Another metric of int erest is fair-
ness, as measured (for example) by Jain’s Fairness Index [J91]. Perfor-
mance and fairness are often at odds in scheduling; a schedul er, for ex-
ample, may optimize performance but at the cost of preventin g a few jobs
from running, thus decreasing fairness. This conundrum sho ws us that
life isn’t always perfect.
7.3 First In, First Out (FIFO)
The most basic algorithm a scheduler can implement is known a s First
In, First Out (FIFO) scheduling or sometimes First Come, First Served
1Said in the same way you would say “A fully-operational Death Star.”
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 97

SCHEDULING : I NTRODUCTION 61
(FCFS). FIFO has a number of positive properties: it is clearly ver y simple
and thus easy to implement. Given our assumptions, it works p retty well.
Let’s do a quick example together. Imagine three jobs arrive in the
system, A, B, and C, at roughly the same time ( Tarrival = 0 ). Because
FIFO has to put some job ﬁrst, let’s assume that while they all arrived
simultaneously , A arrived just a hair before B which arrived just a hair
before C. Assume also that each job runs for 10 seconds. What w ill the
average turnaround time be for these jobs?
0 20 40 60 80 100 120
Time
A B C
Figure 7.1: FIFO Simple Example
From Figure 7.1, you can see that A ﬁnished at 10, B at 20, and C at 30.
Thus, the average turnaround time for the three jobs is simply 10+20+30
3 =
20. Computing turnaround time is as easy as that.
Now let’s relax one of our assumptions. In particular, let’s relax as-
sumption 1, and thus no longer assume that each job runs for th e same
amount of time. How does FIFO perform now? What kind of worklo ad
could you construct to make FIFO perform poorly?
(think about this before reading on ... keep thinking ... got it?!)
Presumably you’ve ﬁgured this out by now , but just in case, le t’s do
an example to show how jobs of different lengths can lead to tr ouble for
FIFO scheduling. In particular, let’s again assume three jo bs (A, B, and
C), but this time A runs for 100 seconds while B and C run for 10 e ach.
0 20 40 60 80 100 120
Time
A B C
Figure 7.2: Why FIFO Is Not That Great
As you can see in Figure 7.2, Job A runs ﬁrst for the full 100 seconds
before B or C even get a chance to run. Thus, the average turnar ound
time for the system is high: a painful 110 seconds ( 100+110+120
3 = 110).
This problem is generally referred to as theconvoy effect [B+79], where
a number of relatively-short potential consumers of a resource get queued
behind a heavyweight resource consumer. This scheduling scenario might
remind you of a single line at a grocery store and what you feel like when
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 98

62 SCHEDULING : I NTRODUCTION
TIP : T HE PRINCIPLE OF SJF
Shortest Job First represents a general scheduling princip le that can be
applied to any system where the perceived turnaround time per customer
(or, in our case, a job) matters. Think of any line you have wai ted in: if
the establishment in question cares about customer satisfaction, it is likely
they have taken SJF into account. For example, grocery store s commonly
have a “ten-items-or-less” line to ensure that shoppers wit h only a few
things to purchase don’t get stuck behind the family prepari ng for some
upcoming nuclear winter.
you see the person in front of you with three carts full of prov isions and
a checkbook out; it’s going to be a while 2.
So what should we do? How can we develop a better algorithm to
deal with our new reality of jobs that run for different amoun ts of time?
Think about it ﬁrst; then read on.
7.4 Shortest Job First (SJF)
It turns out that a very simple approach solves this problem; in fact
it is an idea stolen from operations research [C54,PV56] and applied to
scheduling of jobs in computer systems. This new scheduling discipline
is known as Shortest Job First (SJF) , and the name should be easy to
remember because it describes the policy quite completely: it runs the
shortest job ﬁrst, then the next shortest, and so on.
0 20 40 60 80 100 120
Time
B C A
Figure 7.3: SJF Simple Example
Let’s take our example above but with SJF as our scheduling po licy .
Figure 7.3 shows the results of running A, B, and C. Hopefully the dia-
gram makes it clear why SJF performs much better with regards to aver-
age turnaround time. Simply by running B and C before A, SJF re duces
average turnaround from 110 seconds to 50 ( 10+20+120
3 = 50 ), more than
a factor of two improvement.
In fact, given our assumptions about jobs all arriving at the same time,
we could prove that SJF is indeed an optimal scheduling algorithm. How-
2Recommended action in this case: either quickly switch to a d ifferent line, or take a long,
deep, and relaxing breath. That’s right, breathe in, breath e out. It will be OK, don’t worry .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 99

SCHEDULING : I NTRODUCTION 63
ASIDE : PREEMPTIVE SCHEDULERS
In the old days of batch computing, a number of non-preemptive sched-
ulers were developed; such systems would run each job to comp letion
before considering whether to run a new job. Virtually all mo dern sched-
ulers are preemptive, and quite willing to stop one process from run-
ning in order to run another. This implies that the scheduler employs the
mechanisms we learned about previously; in particular, the scheduler can
perform a context switch, stopping one running process temporarily and
resuming (or starting) another.
ever, you are in a systems class, not theory or operations res earch; no
proofs are allowed.
Thus we arrive upon a good approach to scheduling with SJF, bu t our
assumptions are still fairly unrealistic. Let’s relax anot her. In particular,
we can target assumption 2, and now assume that jobs can arriv e at any
time instead of all at once. What problems does this lead to?
(Another pause to think ... are you thinking? Come on, you can do it)
Here we can illustrate the problem again with an example. Thi s time,
assume A arrives at t = 0 and needs to run for 100 seconds, whereas B
and C arrive at t = 10 and each need to run for 10 seconds. With pure
SJF, we’d get the schedule seen in Figure
7.4.
0 20 40 60 80 100 120
Time
A B C
[B,C arrive]
Figure 7.4: SJF With Late Arrivals From B and C
As you can see from the ﬁgure, even though B and C arrived short ly
after A, they still are forced to wait until A has completed, a nd thus suffer
the same convoy problem. A verage turnaround time for these t hree jobs
is 103.33 seconds ( 100+(110− 10)+(120− 10)
3 ). What can a scheduler do?
7.5 Shortest Time-to-Completion First (STCF)
As you might have guessed, given our previous discussion about mech-
anisms such as timer interrupts and context switching, the s cheduler can
certainly do something else when B and C arrive: it can preempt job A
and decide to run another job, perhaps continuing A later. SJF by our deﬁ-
nition is a non-preemptive scheduler, and thus suffers from the problems
described above.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 100

64 SCHEDULING : I NTRODUCTION
0 20 40 60 80 100 120
Time
A B C A
[B,C arrive]
Figure 7.5: STCF Simple Example
Fortunately , there is a scheduler which does exactly that: add preemp-
tion to SJF, known as the Shortest Time-to-Completion First (STCF) or
Preemptive Shortest Job First (PSJF) scheduler [CK68]. Any time a new
job enters the system, it determines of the remaining jobs an d new job,
which has the least time left, and then schedules that one. Th us, in our
example, STCF would preempt A and run B and C to completion; on ly
when they are ﬁnished would A’s remaining time be scheduled. Figure
7.5 shows an example.
The result is a much-improved average turnaround time: 50 se conds
( (120− 0)+(20− 10)+(30− 10)
3 ). And as before, given our new assumptions,
STCF is provably optimal; given that SJF is optimal if all job s arrive at
the same time, you should probably be able to see the intuitio n behind
the optimality of STCF.
Thus, if we knew that job lengths, and jobs only used the CPU, and our
only metric was turnaround time, STCF would be a great policy . In fact,
for a number of early batch computing systems, these types of scheduling
algorithms made some sense. However, the introduction of ti me-shared
machines changed all that. Now users would sit at a terminal a nd de-
mand interactive performance from the system as well. And th us, a new
metric was born: response time.
Response time is deﬁned as the time from when the job arrives i n a
system to the ﬁrst time it is scheduled. More formally:
Tresponse = Tf irstrun − Tarrival (7.2)
For example, if we had the schedule above (with A arriving at t ime 0,
and B and C at time 10), the response time of each job is as follo ws: 0 for
job A, 0 for B, and 10 for C (average: 3.33).
As you might be thinking, STCF and related disciplines are no t par-
ticularly good for response time. If three jobs arrive at the same time,
for example, the third job has to wait for the previous two job s to run in
their entirety before being scheduled just once. While great for turnaround
time, this approach is quite bad for response time and intera ctivity . In-
deed, imagine sitting at a terminal, typing, and having to wa it 10 seconds
to see a response from the system just because some other job g ot sched-
uled in front of yours: not too pleasant.
Thus, we are left with another problem: how can we build a sche duler
that is sensitive to response time?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 101

SCHEDULING : I NTRODUCTION 65
0 5 10 15 20 25 30
Time
A B C
Figure 7.6: SJF Again (Bad for Response Time)
0 5 10 15 20 25 30
Time
ABCABCABCABCABC
Figure 7.7: Round Robin (Good for Response Time)
7.6 Round Robin
To solve this problem, we will introduce a new scheduling alg orithm.
This approach is classically known as Round-Robin (RR) scheduling [K64].
The basic idea is simple: instead of running jobs to completi on, RR runs
a job for a time slice (sometimes called a scheduling quantum) and then
switches to the next job in the run queue. It repeatedly does s o un-
til the jobs are ﬁnished. For this reason, RR is sometimes cal led time-
slicing. Note that the length of a time slice must be a multiple of the
timer-interrupt period; thus if the timer interrupts every 10 milliseconds,
the time slice could be 10, 20, or any other multiple of 10 ms.
To understand RR in more detail, let’s look at an example. Ass ume
three jobs A, B, and C arrive at the same time in the system, and that
they each wish to run for 5 seconds. An SJF scheduler runs each job to
completion before running another (Figure 7.6). In contrast, RR with a
time-slice of 1 second would cycle through the jobs quickly ( Figure 7.7).
The average response time of RR is: 0+1+2
3 = 1 ; for SJF, average re-
sponse time is: 0+5+10
3 = 5.
As you can see, the length of the time slice is critical for RR. The shorter
it is, the better the performance of RR under the response-ti me metric.
However, making the time slice too short is problematic: sud denly the
cost of context switching will dominate overall performanc e. Thus, de-
ciding on the length of the time slice presents a trade-off to a system de-
signer, making it long enough to amortize the cost of switching without
making it so long that the system is no longer responsive.
Note that the cost of context switching does not arise solely from the
OS actions of saving and restoring a few registers. When prog rams run,
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 102

66 SCHEDULING : I NTRODUCTION
TIP : A MORTIZATION CAN REDUCE COSTS
The general technique of amortization is commonly used in systems
when there is a ﬁxed cost to some operation. By incurring that cost less
often (i.e., by performing the operation fewer times), the t otal cost to the
system is reduced. For example, if the time slice is set to 10 m s, and the
context-switch cost is 1 ms, roughly 10% of time is spent cont ext switch-
ing and is thus wasted. If we want to amortize this cost, we can increase
the time slice, e.g., to 100 ms. In this case, less than 1% of ti me is spent
context switching, and thus the cost of time-slicing has bee n amortized.
they build up a great deal of state in CPU caches, TLBs, branch predictors,
and other on-chip hardware. Switching to another job causes this state
to be ﬂushed and new state relevant to the currently-running job to be
brought in, which may exact a noticeable performance cost [M B91].
RR, with a reasonable time slice, is thus an excellent schedu ler if re-
sponse time is our only metric. But what about our old friend t urnaround
time? Let’s look at our example above again. A, B, and C, each w ith run-
ning times of 5 seconds, arrive at the same time, and RR is the s cheduler
with a (long) 1-second time slice. We can see from the picture above that
A ﬁnishes at 13, B at 14, and C at 15, for an average of 14. Pretty awful!
It is not surprising, then, that RR is indeed one of the worst policies if
turnaround time is our metric. Intuitively , this should mak e sense: what
RR is doing is stretching out each job as long as it can, by only running
each job for a short bit before moving to the next. Because tur naround
time only cares about when jobs ﬁnish, RR is nearly pessimal, even worse
than simple FIFO in many cases.
More generally , any policy (such as RR) that is fair, i.e., that evenly di-
vides the CPU among active processes on a small time scale, wi ll perform
poorly on metrics such as turnaround time. Indeed, this is an inherent
trade-off: if you are willing to be unfair, you can run shorte r jobs to com-
pletion, but at the cost of response time; if you instead valu e fairness,
response time is lowered, but at the cost of turnaround time. This type of
trade-off is common in systems; you can’t have your cake and eat it too.
We have developed two types of schedulers. The ﬁrst type (SJF , STCF)
optimizes turnaround time, but is bad for response time. The second type
(RR) optimizes response time but is bad for turnaround. And w e still
have two assumptions which need to be relaxed: assumption 3 ( that jobs
do no I/O), and assumption 4 (that the run-time of each job is k nown).
Let’s tackle those assumptions next.
7.7 Incorporating I/O
First we will relax assumption 3 – of course all programs perf orm I/O.
Imagine a program that didn’t take any input: it would produc e the same
output each time. Imagine one without output: it is the prove rbial tree
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 103

SCHEDULING : I NTRODUCTION 67
falling in the forest, with no one to see it; it doesn’t matter that it ran.
A scheduler clearly has a decision to make when a job initiate s an I/O
request, because the currently-running job won’t be using t he CPU dur-
ing the I/O; it is blocked waiting for I/O completion. If the I/O is sent to
a hard disk drive, the process might be blocked for a few milli seconds or
longer, depending on the current I/O load of the drive. Thus, the sched-
uler should probably schedule another job on the CPU at that t ime.
The scheduler also has to make a decision when the I/O complet es.
When that occurs, an interrupt is raised, and the OS runs and m oves
the process that issued the I/O from blocked back to the ready state. Of
course, it could even decide to run the job at that point. How s hould the
OS treat each job?
To understand this issue better, let us assume we have two job s, A and
B, which each need 50 ms of CPU time. However, there is one obvi ous
difference: A runs for 10 ms and then issues an I/O request (as sume here
that I/Os each take 10 ms), whereas B simply uses the CPU for 50 ms and
performs no I/O. The scheduler runs A ﬁrst, then B after (Figu re 7.8).
0 20 40 60 80 100 120 140
Time
A A A A A B B B B B
CPU
Disk
Figure 7.8: Poor Use of Resources
Assume we are trying to build a STCF scheduler. How should suc h a
scheduler account for the fact that A is broken up into 5 10-ms sub-jobs,
whereas B is just a single 50-ms CPU demand? Clearly , just run ning one
job and then the other without considering how to take I/O int o account
makes little sense.
0 20 40 60 80 100 120 140
Time
A A A A AB B B B B
CPU
Disk
Figure 7.9: Overlap Allows Better Use of Resources
A common approach is to treat each 10-ms sub-job of A as an inde pen-
dent job. Thus, when the system starts, its choice is whether to schedule
a 10-ms A or a 50-ms B. With STCF, the choice is clear: choose th e shorter
one, in this case A. Then, when the ﬁrst sub-job of A has comple ted, only
B is left, and it begins running. Then a new sub-job of A is subm itted,
and it preempts B and runs for 10 ms. Doing so allows for overlap, with
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 104

68 SCHEDULING : I NTRODUCTION
TIP : O VERLAP ENABLES HIGHER UTILIZATION
When possible, overlap operations to maximize the utilization of sys-
tems. Overlap is useful in many different domains, includin g when per-
forming disk I/O or sending messages to remote machines; in e ither case,
starting the operation and then switching to other work is a g ood idea,
and improved the overall utilization and efﬁciency of the sy stem.
the CPU being used by one process while waiting for the I/O of a nother
process to complete; the system is thus better utilized (see Figure 7.9).
And thus we see how a scheduler might incorporate I/O. By trea ting
each CPU burst as a job, the scheduler makes sure processes th at are “in-
teractive” get run frequently . While those interactive jobs are performing
I/O, other CPU-intensive jobs run, thus better utilizing th e processor.
7.8 No More Oracle
With a basic approach to I/O in place, we come to our ﬁnal assum p-
tion: that the scheduler knows the length of each job. As we sa id before,
this is likely the worst assumption we could make. In fact, in a general-
purpose OS (like the ones we care about), the OS usually knows very little
about the length of each job. Thus, how can we build an approac h that be-
haves like SJF/STCF without such a priori knowledge? Further, how can
we incorporate some of the ideas we have seen with the RR sched uler so
that response time is also quite good?
7.9 Summary
We have introduced the basic ideas behind scheduling and dev eloped
two families of approaches. The ﬁrst runs the shortest job re maining and
thus optimizes turnaround time; the second alternates betw een all jobs
and thus optimizes response time. Both are bad where the othe r is good,
alas, an inherent trade-off common in systems. We have also seen how we
might incorporate I/O into the picture, but have still not so lved the prob-
lem of the fundamental inability of the OS to see into the futu re. Shortly ,
we will see how to overcome this problem, by building a schedu ler that
uses the recent past to predict the future. This scheduler is known as the
multi-level feedback queue , and it is the topic of the next chapter.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 105

SCHEDULING : I NTRODUCTION 69
References
[B+79] “The Convoy Phenomenon”
M. Blasgen, J. Gray , M. Mitoma, T. Price
ACM Operating Systems Review, 13:2, April 1979
Perhaps the ﬁrst reference to convoys, which occurs in datab ases as well as the OS.
[C54] “Priority Assignment in Waiting Line Problems”
A. Cobham
Journal of Operations Research, 2:70, pages 70–76, 1954
The pioneering paper on using an SJF approach in scheduling t he repair of machines.
[K64] “Analysis of a Time-Shared Processor”
Leonard Kleinrock
Naval Research Logistics Quarterly , 11:1, pages 59–73, March 1964
May be the ﬁrst reference to the round-robin scheduling algo rithm; certainly one of the ﬁrst analyses of
said approach to scheduling a time-shared system.
[CK68] “Computer Scheduling Methods and their Countermeas ures”
Edward G. Coffman and Leonard Kleinrock
AFIPS ’68 (Spring), April 1968
An excellent early introduction to and analysis of a number o f basic scheduling disciplines.
[J91] “The Art of Computer Systems Performance Analysis:
Techniques for Experimental Design, Measurement, Simulat ion, and Modeling”
R. Jain
Interscience, New York, April 1991
The standard text on computer systems measurement. A great r eference for your library, for sure.
[O45] “Animal Farm”
George Orwell
Secker and Warburg (London), 1945
A great but depressing allegorical book about power and its c orruptions. Some say it is a critique of
Stalin and the pre-WWII Stalin era in the U.S.S.R; we say it’s a critique of pigs.
[PV56] “Machine Repair as a Priority Waiting-Line Problem”
Thomas E. Phipps Jr. and W. R. Van V oorhis
Operations Research, 4:1, pages 76–86, February 1956
Follow-on work that generalizes the SJF approach to machine repair from Cobham’s original work; also
postulates the utility of an STCF approach in such an environ ment. Speciﬁcally, “There are certain
types of repair work, ... involving much dismantling and cov ering the ﬂoor with nuts and bolts, which
certainly should not be interrupted once undertaken; in oth er cases it would be inadvisable to continue
work on a long job if one or more short ones became available (p .81).”
[MB91] “The effect of context switches on cache performance ”
Jeffrey C. Mogul and Anita Borg
ASPLOS, 1991
A nice study on how cache performance can be affected by conte xt switching; less of an issue in today’s
systems where processors issue billions of instructions pe r second but context-switches still happen in
the millisecond time range.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 106

70 SCHEDULING : I NTRODUCTION
Homework
ASIDE : SIMULATION HOMEWORKS
Simulation homeworks come in the form of simulators you run t o
make sure you understand some piece of the material. The simu lators
are generally python programs that enable you both to generate different
problems (using different random seeds) as well as to have th e program
solve the problem for you (with the -c ﬂag) so that you can check your
answers. Running any simulator with a -h or --help ﬂag will provide
with more information as to all the options the simulator giv es you.
This program, scheduler.py, allows you to see how different sched-
ulers perform under scheduling metrics such as response time, turnaround
time, and total wait time. See the README for details.
Questions
1. Compute the response time and turnaround time when runnin g
three jobs of length 200 with the SJF and FIFO schedulers.
2. Now do the same but with jobs of different lengths: 100, 200 , and
300.
3. Now do the same, but also with the RR scheduler and a time-sl ice
of 1.
4. For what types of workloads does SJF deliver the same turna round
times as FIFO?
5. For what types of workloads and quantum lengths does SJF de liver
the same response times as RR?
6. What happens to response time with SJF as job lengths incre ase?
Can you use the simulator to demonstrate the trend?
7. What happens to response time with RR as quantum lengths in -
crease? Can you write an equation that gives the worst-case r e-
sponse time, given N jobs?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 107

8
Scheduling:
The Multi-Level Feedback Queue
In this chapter, we’ll tackle the problem of developing one o f the most
well-known approaches to scheduling, known as the Multi-level Feed-
back Queue (MLFQ) . The Multi-level Feedback Queue (MLFQ) sched-
uler was ﬁrst described by Corbato et al. in 1962 [C+62] in a sy stem
known as the Compatible Time-Sharing System (CTSS), and thi s work,
along with later work on Multics, led the ACM to award Corbato its
highest honor, the T uring Award. The scheduler has subsequently been
reﬁned throughout the years to the implementations you will encounter
in some modern systems.
The fundamental problem MLFQ tries to address is two-fold. F irst, it
would like to optimize turnaround time, which, as we saw in the previous
note, is done by running shorter jobs ﬁrst; unfortunately , t he OS doesn’t
generally know how long a job will run for, exactly the knowle dge that
algorithms like SJF (or STCF) require. Second, MLFQ would li ke to make
a system feel responsive to interactive users (i.e., users s itting and staring
at the screen, waiting for a process to ﬁnish), and thus minim ize response
time; unfortunately , algorithms like Round Robin reduce respon se time
but are terrible for turnaround time. Thus, our problem: giv en that we
in general do not know anything about a process, how can we bui ld a
scheduler to achieve these goals? How can the scheduler lear n, as the
system runs, the characteristics of the jobs it is running, a nd thus make
better scheduling decisions?
THE CRUX :
HOW TO SCHEDULE WITHOUT PERFECT KNOWLEDGE ?
How can we design a scheduler that both minimizes response ti me for
interactive jobs while also minimizing turnaround time wit hout a priori
knowledge of job length?
71

## Page 108

72
SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE
TIP : L EARN FROM HISTORY
The multi-level feedback queue is an excellent example of a s ystem that
learns from the past to predict the future. Such approaches a re com-
mon in operating systems (and many other places in Computer S cience,
including hardware branch predictors and caching algorith ms). Such
approaches work when jobs have phases of behavior and are thu s pre-
dictable; of course, one must be careful with such technique s, as they can
easily be wrong and drive a system to make worse decisions tha n they
would have with no knowledge at all.
8.1 MLFQ: Basic Rules
To build such a scheduler, in this chapter we will describe th e basic
algorithms behind a multi-level feedback queue; although t he speciﬁcs of
many implemented MLFQs differ [E95], most approaches are si milar.
In our treatment, the MLFQ has a number of distinct queues, each
assigned a different priority level. At any given time, a job that is ready
to run is on a single queue. MLFQ uses priorities to decide whi ch job
should run at a given time: a job with higher priority (i.e., a job on a
higher queue) is chosen to run.
Of course, more than one job may be on a given queue, and thus ha ve
the same priority . In this case, we will just use round-robin schedul ing
among those jobs.
Thus, the key to MLFQ scheduling lies in how the scheduler set s pri-
orities. Rather than giving a ﬁxed priority to each job, MLFQ varies the
priority of a job based on its observed behavior. If, for example, a job repeat-
edly relinquishes the CPU while waiting for input from the ke yboard,
MLFQ will keep its priority high, as this is how an interactiv e process
might behave. If, instead, a job uses the CPU intensively for long periods
of time, MLFQ will reduce its priority . In this way , MLFQ will try to learn
about processes as they run, and thus use the history of the job to predict
its future behavior.
Thus, we arrive at the ﬁrst two basic rules for MLFQ:
• Rule 1: If Priority(A) > Priority(B), A runs (B doesn’t).
• Rule 2: If Priority(A) = Priority(B), A & B run in RR.
If we were to put forth a picture of what the queues might look l ike at
a given instant, we might see something like the following (F igure 8.1).
In the ﬁgure, two jobs (A and B) are at the highest priority lev el, while job
C is in the middle and Job D is at the lowest priority . Given our current
knowledge of how MLFQ works, the scheduler would just altern ate time
slices between A and B because they are the highest priority j obs in the
system; poor jobs C and D would never even get to run – an outrag e!
Of course, just showing a static snapshot of some queues does not re-
ally give you an idea of how MLFQ works. What we need is to under -
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 109

SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE 73
Q1
Q2
Q3
Q4
Q5
Q6
Q7
Q8
[Low Priority]
[High Priority]
D
C
A B
Figure 8.1: MLFQ Example
stand how job priority changes over time. And that, in a surprise only
to those who are reading a chapter from this book for the ﬁrst t ime, is
exactly what we will do next.
8.2 Attempt #1: How to Change Priority
We now must decide how MLFQ is going to change the priority lev el
of a job (and thus which queue it is on) over the lifetime of a jo b. To do
this, we must keep in mind our workload: a mix of interactive j obs that
are short-running (and may frequently relinquish the CPU), and some
longer-running “CPU-bound” jobs that need a lot of CPU time b ut where
response time isn’t important. Here is our ﬁrst attempt at a p riority-
adjustment algorithm:
• Rule 3: When a job enters the system, it is placed at the highest
priority (the topmost queue).
• Rule 4a: If a job uses up an entire time slice while running, its pri-
ority is reduced (i.e., it moves down one queue).
• Rule 4b: If a job gives up the CPU before the time slice is up, it stays
at the same priority level.
Example 1: A Single Long-Running Job
Let’s look at some examples. First, we’ll look at what happen s when there
has been a long running job in the system. Figure
8.2 shows what happens
to this job over time in a three-queue scheduler.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 110

74
SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE
Q2
Q1
Q0
0 50 100 150 200
Figure 8.2: Long-running Job Over Time
As you can see in the example, the job enters at the highest pri ority
(Q2). After a single time-slice of 10 ms, the scheduler reduc es the job’s
priority by one, and thus the job is on Q1. After running at Q1 f or a time
slice, the job is ﬁnally lowered to the lowest priority in the system (Q0),
where it remains. Pretty simple, no?
Example 2: Along Came A Short Job
Now let’s look at a more complicated example, and hopefully s ee how
MLFQ tries to approximate SJF. In this example, there are two jobs: A,
which is a long-running CPU-intensive job, and B, which is a short-running
interactive job. Assume A has been running for some time, and then B ar-
rives. What will happen? Will MLFQ approximate SJF for B?
Figure
8.3 plots the results of this scenario. A (shown in black) is run-
ning along in the lowest-priority queue (as would any long-running CPU-
intensive jobs); B (shown in gray) arrives at time T = 100 , and thus is
Q2
Q1
Q0
0 50 100 150 200
Figure 8.3: Along Came An Interactive Job
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 111

SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE 75
Q2
Q1
Q0
0 50 100 150 200
Figure 8.4: A Mixed I/O-intensive and CPU-intensive Workload
inserted into the highest queue; as its run-time is short (on ly 20 ms), B
completes before reaching the bottom queue, in two time slic es; then A
resumes running (at low priority).
From this example, you can hopefully understand one of the ma jor
goals of the algorithm: because it doesn’t know whether a job will be a
short job or a long-running job, it ﬁrst assumes it might be a short job, thus
giving the job high priority . If it actually is a short job, it will run quickly
and complete; if it is not a short job, it will slowly move down the queues,
and thus soon prove itself to be a long-running more batch-li ke process.
In this manner, MLFQ approximates SJF.
Example 3: What About I/O?
Let’s now look at an example with some I/O. As Rule 4b states ab ove, if a
process gives up the processor before using up its time slice , we keep it at
the same priority level. The intent of this rule is simple: if an interactive
job, for example, is doing a lot of I/O (say by waiting for user input from
the keyboard or mouse), it will relinquish the CPU before its time slice is
complete; in such case, we don’t wish to penalize the job and t hus simply
keep it at the same level.
Figure
8.4 shows an example of how this works, with an interactive job
B (shown in gray) that needs the CPU only for 1 ms before perfor ming an
I/O competing for the CPU with a long-running batch job A (sho wn in
black). The MLFQ approach keeps B at the highest priority bec ause B
keeps releasing the CPU; if B is an interactive job, MLFQ furt her achieves
its goal of running interactive jobs quickly .
Problems With Our Current MLFQ
We thus have a basic MLFQ. It seems to do a fairly good job, shar ing the
CPU fairly between long-running jobs, and letting short or I /O-intensive
interactive jobs run quickly . Unfortunately , the approach we have devel-
oped thus far contains serious ﬂaws. Can you think of any?
(This is where you pause and think as deviously as you can)
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 112

76
SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE
Q2
Q1
Q0
0 50 100 150 200
Q2
Q1
Q0
0 50 100 150 200
Figure 8.5: Without (Left) and With (Right) Priority Boost
First, there is the problem of starvation: if there are “too many” in-
teractive jobs in the system, they will combine to consume all CPU time,
and thus long-running jobs will never receive any CPU time (they starve).
We’d like to make some progress on these jobs even in this scen ario.
Second, a smart user could rewrite their program to game the sched-
uler. Gaming the scheduler generally refers to the idea of doing s ome-
thing sneaky to trick the scheduler into giving you more than your fair
share of the resource. The algorithm we have described is sus ceptible to
the following attack: before the time slice is over, issue an I/O operation
(to some ﬁle you don’t care about) and thus relinquish the CPU ; doing so
allows you to remain in the same queue, and thus gain a higher p ercent-
age of CPU time. When done right (e.g., by running for 99% of a t ime slice
before relinquishing the CPU), a job could nearly monopoliz e the CPU.
Finally , a program may change its behavior over time; what was CPU-
bound may transition to a phase of interactivity . With our cu rrent ap-
proach, such a job would be out of luck and not be treated like t he other
interactive jobs in the system.
8.3 Attempt #2: The Priority Boost
Let’s try to change the rules and see if we can avoid the proble m of
starvation. What could we do in order to guarantee that CPU-b ound jobs
will make some progress (even if it is not much?).
The simple idea here is to periodically boost the priority of all the jobs
in system. There are many ways to achieve this, but let’s just do some-
thing simple: throw them all in the topmost queue; hence, a ne w rule:
• Rule 5: After some time period S, move all the jobs in the system
to the topmost queue.
Our new rule solves two problems at once. First, processes ar e guar-
anteed not to starve: by sitting in the top queue, a job will sh are the CPU
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 113

SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE 77
Q2
Q1
Q0
0 50 100 150 200
Q2
Q1
Q0
0 50 100 150 200
Figure 8.6: Without (Left) and With (Right) Gaming T olerance
with other high-priority jobs in a round-robin fashion, and thus eventu-
ally receive service. Second, if a CPU-bound job has become i nteractive,
the scheduler treats it properly once it has received the pri ority boost.
Let’s see an example. In this scenario, we just show the behav ior of
a long-running job when competing for the CPU with two short- running
interactive jobs. Two graphs are shown in Figure 8.5. On the left, there is
no priority boost, and thus the long-running job gets starved once the two
short jobs arrive; on the right, there is a priority boost eve ry 50 ms (which
is likely too small of a value, but used here for the example), and thus
we at least guarantee that the long-running job will make som e progress,
getting boosted to the highest priority every 50 ms and thus g etting to
run periodically .
Of course, the addition of the time period S leads to the obvious ques-
tion: what should S be set to? John Ousterhout, a well-regarded systems
researcher [O11], used to call such values in systems voo-doo constants,
because they seemed to require some form of black magic to set them cor-
rectly . Unfortunately ,S has that ﬂavor. If it is set too high, long-running
jobs could starve; too low , and interactive jobs may not get a proper share
of the CPU.
8.4 Attempt #3: Better Accounting
We now have one more problem to solve: how to prevent gaming of
our scheduler? The real culprit here, as you might have guess ed, are
Rules 4a and 4b, which let a job retain its priority by relinqu ishing the
CPU before the time slice expires. So what should we do?
The solution here is to perform better accounting of CPU time at each
level of the MLFQ. Instead of forgetting how much of a time sli ce a pro-
cess used at a given level, the scheduler should keep track; o nce a process
has used its allotment, it is demoted to the next priority que ue. Whether
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 114

78
SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE
Q2
Q1
Q0
0 50 100 150 200
Figure 8.7: Lower Priority, Longer Quanta
it uses the time slice in one long burst or many small ones does not matter.
We thus rewrite Rules 4a and 4b to the following single rule:
• Rule 4: Once a job uses up its time allotment at a given level (re-
gardless of how many times it has given up the CPU), its priori ty is
reduced (i.e., it moves down one queue).
Let’s look at an example. Figure 8.6 shows what happens when a
workload tries to game the scheduler with the old Rules 4a and 4b (on
the left) as well the new anti-gaming Rule 4. Without any prot ection from
gaming, a process can issue an I/O just before a time slice end s and thus
dominate CPU time. With such protections in place, regardle ss of the
I/O behavior of the process, it slowly moves down the queues, and thus
cannot gain an unfair share of the CPU.
8.5 Tuning MLFQ And Other Issues
A few other issues arise with MLFQ scheduling. One big questi on is
how to parameterize such a scheduler. For example, how many queues
should there be? How big should the time slice be per queue? Ho w often
should priority be boosted in order to avoid starvation and a ccount for
changes in behavior? There are no easy answers to these quest ions, and
thus only some experience with workloads and subsequent tun ing of the
scheduler will lead to a satisfactory balance.
For example, most MLFQ variants allow for varying time-slic e length
across different queues. The high-priority queues are usua lly given short
time slices; they are comprised of interactive jobs, after a ll, and thus
quickly alternating between them makes sense (e.g., 10 or fe wer millisec-
onds). The low-priority queues, in contrast, contain long- running jobs
that are CPU-bound; hence, longer time slices work well (e.g ., 100s of
ms). Figure 8.7 shows an example in which two long-running jobs run
for 10 ms at the highest queue, 20 in the middle, and 40 at the lo west.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 115

SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE 79
TIP : A VOID VOO -DOO CONSTANTS (O USTERHOUT ’ S LAW)
A voiding voo-doo constants is a good idea whenever possible . Unfor-
tunately , as in the example above, it is often difﬁcult. One c ould try to
make the system learn a good value, but that too is not straigh tforward.
The frequent result: a conﬁguration ﬁle ﬁlled with default p arameter val-
ues that a seasoned administrator can tweak when something i sn’t quite
working correctly . As you can imagine, these are often left u nmodiﬁed,
and thus we are left to hope that the defaults work well in the ﬁ eld. This
tip brought to you by our old OS professor, John Ousterhout, a nd hence
we call it Ousterhout’s Law .
The Solaris MLFQ implementation – the Time-Sharing scheduling class,
or TS – is particularly easy to conﬁgure; it provides a set of t ables that
determine exactly how the priority of a process is altered th roughout its
lifetime, how long each time slice is, and how often to boost the priority of
a job [AD00]; an administrator can muck with this table in ord er to make
the scheduler behave in different ways. Default values for t he table are
60 queues, with slowly increasing time-slice lengths from 2 0 milliseconds
(highest priority) to a few hundred milliseconds (lowest), and priorities
boosted around every 1 second or so.
Other MLFQ schedulers don’t use a table or the exact rules des cribed
in this chapter; rather they adjust priorities using mathem atical formu-
lae. For example, the FreeBSD scheduler (version 4.3) uses a formula to
calculate the current priority level of a job, basing it on ho w much CPU
the process has used [LM+89]; in addition, usage is decayed o ver time,
providing the desired priority boost in a different manner t han described
herein. See [E95] for an excellent overview of such decay-usage algo-
rithms and their properties.
Finally , many schedulers have a few other features that you m ight en-
counter. For example, some schedulers reserve the highest p riority levels
for operating system work; thus typical user jobs can never o btain the
highest levels of priority in the system. Some systems also a llow some
user advice to help set priorities; for example, by using the command-line
utility nice you can increase or decrease the priority of a job (somewhat)
and thus increase or decrease its chances of running at any gi ven time.
See the man page for more.
8.6 MLFQ: Summary
We have described a scheduling approach known as the Multi-L evel
Feedback Queue (MLFQ). Hopefully you can now see why it is cal led
that: it has multiple levels of queues, and uses feedback to determine the
priority of a given job. History is its guide: pay attention t o how jobs
behave over time and treat them accordingly .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 116

80
SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE
TIP : U SE ADVICE WHERE POSSIBLE
As the operating system rarely knows what is best for each and every
process of the system, it is often useful to provide interfaces to allow users
or administrators to provide some hints to the OS. We often call such
hints advice, as the OS need not necessarily pay attention to it, but rathe r
might take the advice into account in order to make a better de cision.
Such hints are useful in many parts of the OS, including the sc heduler
(e.g., with nice), memory manager (e.g., madvise), and ﬁle system (e.g.,
TIP [P+95]).
The reﬁned set of MLFQ rules, spread throughout the chapter, are re-
produced here for your viewing pleasure:
• Rule 1: If Priority(A) > Priority(B), A runs (B doesn’t).
• Rule 2: If Priority(A) = Priority(B), A & B run in RR.
• Rule 3: When a job enters the system, it is placed at the highest
priority (the topmost queue).
• Rule 4: Once a job uses up its time allotment at a given level (re-
gardless of how many times it has given up the CPU), its priori ty is
reduced (i.e., it moves down one queue).
• Rule 5: After some time period S, move all the jobs in the system
to the topmost queue.
MLFQ is interesting because instead of demanding a priori knowledge
of the nature of a job, it instead observes the execution of a j ob and pri-
oritizes it accordingly . In this way , it manages to achieve the best of both
worlds: it can deliver excellent overall performance (simi lar to SJF/STCF)
for short-running interactive jobs, and is fair and makes progress for long-
running CPU-intensive workloads. For this reason, many sys tems, in-
cluding BSD U NIX derivatives [LM+89, B86], Solaris [M06], and Win-
dows NT and subsequent Windows operating systems [CS97] use a form
of MLFQ as their base scheduler.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 117

SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE 81
References
[AD00] “Multilevel Feedback Queue Scheduling in Solaris”
Andrea Arpaci-Dusseau
Available: http://www.cs.wisc.edu/˜remzi/solaris-notes.pdf
A great short set of notes by one of the authors on the details o f the Solaris scheduler. OK, we are
probably biased in this description, but the notes are prett y darn good.
[B86] “The Design of the U NIX Operating System”
M.J. Bach
Prentice-Hall, 1986
One of the classic old books on how a real UNIX operating system is built; a deﬁnite must-read for kernel
hackers.
[C+62] “An Experimental Time-Sharing System”
F. J. Corbato, M. M. Daggett, R. C. Daley
IFIPS 1962
A bit hard to read, but the source of many of the ﬁrst ideas in mu lti-level feedback scheduling. Much
of this later went into Multics, which one could argue was the most inﬂuential operating system of all
time.
[CS97] “Inside Windows NT”
Helen Custer and David A. Solomon
Microsoft Press, 1997
The NT book, if you want to learn about something other than UNIX. Of course, why would you? OK,
we’re kidding; you might actually work for Microsoft some da y you know.
[E95] “An Analysis of Decay-Usage Scheduling in Multiproce ssors”
D.H.J. Epema
SIGMETRICS ’95
A nice paper on the state of the art of scheduling back in the mi d 1990s, including a good overview of
the basic approach behind decay-usage schedulers.
[LM+89] “The Design and Implementation of the 4.3BSD U NIX Operating System”
S.J. Lefﬂer, M.K. McKusick, M.J. Karels, J.S. Quarterman
Addison-Wesley , 1989
Another OS classic, written by four of the main people behind BSD. The later versions of this book,
while more up to date, don’t quite match the beauty of this one .
[M06] “Solaris Internals: Solaris 10 and OpenSolaris Kerne l Architecture”
Richard McDougall
Prentice-Hall, 2006
A good book about Solaris and how it works.
[O11] “John Ousterhout’s Home Page”
John Ousterhout
Available: http://www.stanford.edu/˜ouster/
The home page of the famous Professor Ousterhout. The two co- authors of this book had the pleasure of
taking graduate operating systems from Ousterhout while in graduate school; indeed, this is where the
two co-authors got to know each other, eventually leading to marriage, kids, and even this book. Thus,
you really can blame Ousterhout for this entire mess you’re i n.
[P+95] “Informed Prefetching and Caching”
R.H. Patterson, G.A. Gibson, E. Ginting, D. Stodolsky , J. Ze lenka
SOSP ’95
A fun paper about some very cool ideas in ﬁle systems, includi ng how applications can give the OS
advice about what ﬁles it is accessing and how it plans to acce ss them.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 118

82
SCHEDULING :
THE MULTI -L EVEL FEEDBACK QUEUE
Homework
This program, mlfq.py, allows you to see how the MLFQ scheduler
presented in this chapter behaves. See the README for detail s.
Questions
1. Run a few randomly-generated problems with just two jobs a nd
two queues; compute the MLFQ execution trace for each. Make
your life easier by limiting the length of each job and turnin g off
I/Os.
2. How would you run the scheduler to reproduce each of the exa m-
ples in the chapter?
3. How would you conﬁgure the scheduler parameters to behave just
like a round-robin scheduler?
4. Craft a workload with two jobs and scheduler parameters so that
one job takes advantage of the older Rules 4a and 4b (turned on
with the -S ﬂag) to game the scheduler and obtain 99% of the CPU
over a particular time interval.
5. Given a system with a quantum length of 10 ms in its highest q ueue,
how often would you have to boost jobs back to the highest prio rity
level (with the -B ﬂag) in order to guarantee that a single long-
running (and potentially-starving) job gets at least 5% of t he CPU?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 119

9
Scheduling: Proportional Share
In this chapter, we’ll examine a different type of scheduler known as a
proportional-share scheduler, also sometimes referred to as a fair-share
scheduler. Proportional-share is based around a simple con cept: instead
of optimizing for turnaround or response time, a scheduler m ight instead
try to guarantee that each job obtain a certain percentage of CPU time.
An excellent modern example of proportional-share scheduling is found
in research by Waldspurger and Weihl [WW94], and is known as lottery
scheduling; however, the idea is certainly much older [KL88]. The basic
idea is quite simple: every so often, hold a lottery to determine which pro-
cess should get to run next; processes that should run more of ten should
be given more chances to win the lottery . Easy , no? Now , onto the details!
But not before our crux:
CRUX : H OW TO SHARE THE CPU P ROPORTIONALLY
How can we design a scheduler to share the CPU in a proportiona l
manner? What are the key mechanisms for doing so? How effecti ve are
they?
9.1 Basic Concept: Tickets Represent Your Share
Underlying lottery scheduling is one very basic concept: tickets, which
are used to represent the share of a resource that a process (o r user or
whatever) should receive. The percent of tickets that a proc ess has repre-
sents its share of the system resource in question.
Let’s look at an example. Imagine two processes, A and B, and f urther
that A has 75 tickets while B has only 25. Thus, what we would li ke is for
A to receive 75% of the CPU and B the remaining 25%.
Lottery scheduling achieves this probabilistically (but n ot determinis-
tically) by holding a lottery every so often (say , every time slice). Holding
a lottery is straightforward: the scheduler must know how ma ny total
tickets there are (in our example, there are 100). The schedu ler then picks
83

## Page 120

84 SCHEDULING : P ROPORTIONAL SHARE
TIP : U SE RANDOMNESS
One of the most beautiful aspects of lottery scheduling is it s use of ran-
domness. When you have to make a decision, using such a randomized
approach is often a robust and simple way of doing so.
Random approaches has at least three advantages over more tr aditional
decisions. First, random often avoids strange corner-case behaviors that
a more traditional algorithm may have trouble handling. For example,
consider LRU page replacement (studied in more detail in a fu ture chap-
ter on virtual memory); while often a good replacement algor ithm, LRU
performs pessimally for some cyclic-sequential workloads . Random, on
the other hand, has no such worst case.
Second, random also is lightweight, requiring little state to track alter-
natives. In a traditional fair-share scheduling algorithm , tracking how
much CPU each process has received requires per-process acc ounting,
which must be updated after running each process. Doing so ra ndomly
necessitates only the most minimal of per-process state (e. g., the number
of tickets each has).
Finally , random can be quite fast. As long as generating a ran dom num-
ber is quick, making the decision is also, and thus random can be used
in a number of places where speed is required. Of course, the f aster the
need, the more random tends towards pseudo-random.
a winning ticket, which is a number from 0 to 99 1. Assuming A holds
tickets 0 through 74 and B 75 through 99, the winning ticket si mply de-
termines whether A or B runs. The scheduler then loads the sta te of that
winning process and runs it.
Here is an example output of a lottery scheduler’s winning ti ckets:
63 85 70 39 76 17 29 41 36 39 10 99 68 83 63 62 43 0 49 49
Here is the resulting schedule:
A B A A B A A A A A A B A B A A A A A A
As you can see from the example, the use of randomness in lotte ry
scheduling leads to a probabilistic correctness in meeting the desired pro-
portion, but no guarantee. In our example above, B only gets t o run 4 out
of 20 time slices (20%), instead of the desired 25% allocatio n. However,
the longer these two jobs compete, the more likely they are to achieve the
desired percentages.
1Computer Scientists always start counting at 0. It is so odd t o non-computer-types that
famous people have felt obliged to write about why we do it thi s way [D82].
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

