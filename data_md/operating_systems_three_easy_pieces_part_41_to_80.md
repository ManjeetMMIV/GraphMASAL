# Document: operating_systems_three_easy_pieces (Pages 41 to 80)

## Page 41

INTRODUCTION TO OPERATING SYSTEMS 5
1 #include <stdio.h>
2 #include <stdlib.h>
3 #include <sys/time.h>
4 #include <assert.h>
5 #include "common.h"
6
7 int
8 main(int argc, char *argv[])
9 {
10 if (argc != 2) {
11 fprintf(stderr, "usage: cpu <string>\n");
12 exit(1);
13 }
14 char *str = argv[1];
15 while (1) {
16 Spin(1);
17 printf("%s\n", str);
18 }
19 return 0;
20 }
Figure 2.1: Simple Example: Code That Loops and Prints
2.1 Virtualizing the CPU
Figure
2.1 depicts our ﬁrst program. It doesn’t do much. In fact, all
it does is call Spin(), a function that repeatedly checks the time and
returns once it has run for a second. Then, it prints out the st ring that the
user passed in on the command line, and repeats, forever.
Let’s say we save this ﬁle as cpu.c and decide to compile and run it
on a system with a single processor (or CPU as we will sometimes call it).
Here is what we will see:
prompt> gcc -o cpu cpu.c -Wall
prompt> ./cpu "A"
A
A
A
A
ˆC
prompt>
Not too interesting of a run – the system begins running the pr ogram,
which repeatedly checks the time until a second has elapsed. Once a sec-
ond has passed, the code prints the input string passed in by t he user
(in this example, the letter “A”), and continues. Note the pr ogram will
run forever; only by pressing “Control-c” (which on U NIX -based systems
will terminate the program running in the foreground) can we halt the
program.
Now , let’s do the same thing, but this time, let’s run many dif ferent in-
stances of this same program. Figure
2.2 shows the results of this slightly
more complicated example.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 42

6 INTRODUCTION TO OPERATING SYSTEMS
prompt> ./cpu A & ; ./cpu B & ; ./cpu C & ; ./cpu D &
[1] 7353
[2] 7354
[3] 7355
[4] 7356
A
B
D
C
A
B
D
C
A
C
B
D
...
Figure 2.2: Running Many Programs At Once
Well, now things are getting a little more interesting. Even though we
have only one processor, somehow all four of these programs s eem to be
running at the same time! How does this magic happen? 4
It turns out that the operating system, with some help from th e hard-
ware, is in charge of this illusion, i.e., the illusion that the system has a
very large number of virtual CPUs. Turning a single CPU (or sm all set of
them) into a seemingly inﬁnite number of CPUs and thus allowi ng many
programs to seemingly run at once is what we call virtualizing the CPU,
the focus of the ﬁrst major part of this book.
Of course, to run programs, and stop them, and otherwise tell the OS
which programs to run, there need to be some interfaces (APIs ) that you
can use to communicate your desires to the OS. We’ll talk abou t these
APIs throughout this book; indeed, they are the major way in w hich most
users interact with operating systems.
You might also notice that the ability to run multiple progra ms at once
raises all sorts of new questions. For example, if two progra ms want to
run at a particular time, which should run? This question is answered by
a policy of the OS; policies are used in many different places within a n
OS to answer these types of questions, and thus we will study t hem as
we learn about the basic mechanisms that operating systems implement
(such as the ability to run multiple programs at once). Hence the role of
the OS as a resource manager.
4Note how we ran four processes at the same time, by using the & symbol. Doing so runs a
job in the background in the tcsh shell, which means that the user is able to immediately issue
their next command, which in this case is another program to r un. The semi-colon between
commands allows us to run multiple programs at the same time i n tcsh. If you’re using a
different shell (e.g., bash), it works slightly differently; read documentation onlin e for details.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 43

INTRODUCTION TO OPERATING SYSTEMS 7
1 #include <unistd.h>
2 #include <stdio.h>
3 #include <stdlib.h>
4 #include "common.h"
5
6 int
7 main(int argc, char *argv[])
8 {
9 int *p = malloc(sizeof(int)); // a1
10 assert(p != NULL);
11 printf("(%d) address of p: %08x\n",
12 getpid(), (unsigned) p); // a2
13 *p = 0; // a3
14 while (1) {
15 Spin(1);
16 *p = *p + 1;
17 printf("(%d) p: %d\n", getpid(), *p); // a4
18 }
19 return 0;
20 }
Figure 2.3: A Program that Accesses Memory
2.2 Virtualizing Memory
Now let’s consider memory . The model of physical memory pre-
sented by modern machines is very simple. Memory is just an ar ray of
bytes; to read memory , one must specify an address to be able to access
the data stored there; to write (or update) memory , one must also specify
the data to be written to the given address.
Memory is accessed all the time when a program is running. A pr o-
gram keeps all of its data structures in memory , and accessesthem through
various instructions, like loads and stores or other explic it instructions
that access memory in doing their work. Don’t forget that eac h instruc-
tion of the program is in memory too; thus memory is accessed o n each
instruction fetch.
Let’s take a look at a program (in Figure
2.3) that allocates some mem-
ory by calling malloc(). The output of this program can be found here:
prompt> ./mem
(2134) memory address of p: 00200000
(2134) p: 1
(2134) p: 2
(2134) p: 3
(2134) p: 4
(2134) p: 5
ˆC
The program does a couple of things. First, it allocates some memory
(line a1). Then, it prints out the address of the memory (a2), and then
puts the number zero into the ﬁrst slot of the newly allocated memory
(a3). Finally , it loops, delaying for a second and increment ing the value
stored at the address held in p. With every print statement, it also prints
out what is called the process identiﬁer (the PID) of the runn ing program.
This PID is unique per running process.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 44

8 INTRODUCTION TO OPERATING SYSTEMS
prompt> ./mem &; ./mem &
[1] 24113
[2] 24114
(24113) memory address of p: 00200000
(24114) memory address of p: 00200000
(24113) p: 1
(24114) p: 1
(24114) p: 2
(24113) p: 2
(24113) p: 3
(24114) p: 3
(24113) p: 4
(24114) p: 4
...
Figure 2.4: Running The Memory Program Multiple Times
Again, this ﬁrst result is not too interesting. The newly all ocated mem-
ory is at address 00200000. As the program runs, it slowly updates the
value and prints out the result.
Now , we again run multiple instances of this same program to s ee
what happens (Figure
2.4). We see from the example that each running
program has allocated memory at the same address ( 00200000), and yet
each seems to be updating the value at 00200000 independently! It is as
if each running program has its own private memory , instead o f sharing
the same physical memory with other running programs 5.
Indeed, that is exactly what is happening here as the OS is virtualiz-
ing memory. Each process accesses its own private virtual address space
(sometimes just called its address space), which the OS somehow maps
onto the physical memory of the machine. A memory reference w ithin
one running program does not affect the address space of othe r processes
(or the OS itself); as far as the running program is concerned , it has phys-
ical memory all to itself. The reality , however, is that phys ical memory is
a shared resource, managed by the operating system. Exactly how all of
this is accomplished is also the subject of the ﬁrst part of th is book, on the
topic of virtualization.
2.3 Concurrency
Another main theme of this book is concurrency. We use this concep-
tual term to refer to a host of problems that arise, and must be addressed,
when working on many things at once (i.e., concurrently) in t he same
program. The problems of concurrency arose ﬁrst within the o perating
system itself; as you can see in the examples above on virtual ization, the
OS is juggling many things at once, ﬁrst running one process, then an-
other, and so forth. As it turns out, doing so leads to some dee p and
interesting problems.
5For this example to work, you need to make sure address-space randomization is dis-
abled; randomization, as it turns out, can be a good defense a gainst certain kinds of security
ﬂaws. Read more about it on your own, especially if you want to learn how to break into
computer systems via stack-smashing attacks. Not that we wo uld recommend such a thing...
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 45

INTRODUCTION TO OPERATING SYSTEMS 9
1 #include <stdio.h>
2 #include <stdlib.h>
3 #include "common.h"
4
5 volatile int counter = 0;
6 int loops;
7
8 void *worker(void *arg) {
9 int i;
10 for (i = 0; i < loops; i++) {
11 counter++;
12 }
13 return NULL;
14 }
15
16 int
17 main(int argc, char *argv[])
18 {
19 if (argc != 2) {
20 fprintf(stderr, "usage: threads <value>\n");
21 exit(1);
22 }
23 loops = atoi(argv[1]);
24 pthread_t p1, p2;
25 printf("Initial value : %d\n", counter);
26
27 Pthread_create(&p1, NULL, worker, NULL);
28 Pthread_create(&p2, NULL, worker, NULL);
29 Pthread_join(p1, NULL);
30 Pthread_join(p2, NULL);
31 printf("Final value : %d\n", counter);
32 return 0;
33 }
Figure 2.5: A Multi-threaded Program
Unfortunately , the problems of concurrency are no longer li mited just
to the OS itself. Indeed, modern multi-threaded programs exhibit the
same problems. Let us demonstrate with an example of a multi-threaded
program (Figure
2.5).
Although you might not understand this example fully at the m oment
(and we’ll learn a lot more about it in later chapters, in the s ection of the
book on concurrency), the basic idea is simple. The main prog ram creates
two threads using Pthread create()6. You can think of a thread as a
function running within the same memory space as other funct ions, with
more than one of them active at a time. In this example, each th read starts
running in a routine called worker(), in which it simply increments a
counter in a loop for loops number of times.
Below is a transcript of what happens when we run this program with
the input value for the variable loops set to 1000. The value of loops
6The actual call should be to lower-case pthread create(); the upper-case version is
our own wrapper that calls pthread create() and makes sure that the return code indicates
that the call succeeded. See the code for details.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 46

10 INTRODUCTION TO OPERATING SYSTEMS
THE CRUX OF THE PROBLEM :
HOW TO BUILD CORRECT CONCURRENT PROGRAMS
When there are many concurrently executing threads within t he same
memory space, how can we build a correctly working program? W hat
primitives are needed from the OS? What mechanisms should be pro-
vided by the hardware? How can we use them to solve the problem s of
concurrency?
determines how many times each of the two workers will increm ent the
shared counter in a loop. When the program is run with the valu e of
loops set to 1000, what do you expect the ﬁnal value of counter to be?
prompt> gcc -o thread thread.c -Wall -pthread
prompt> ./thread 1000
Initial value : 0
Final value : 2000
As you probably guessed, when the two threads are ﬁnished, th e ﬁnal
value of the counter is 2000, as each thread incremented the c ounter 1000
times. Indeed, when the input value of loops is set to N , we would
expect the ﬁnal output of the program to be 2N . But life is not so simple,
as it turns out. Let’s run the same program, but with higher va lues for
loops, and see what happens:
prompt> ./thread 100000
Initial value : 0
Final value : 143012 // huh??
prompt> ./thread 100000
Initial value : 0
Final value : 137298 // what the??
In this run, when we gave an input value of 100,000, instead of getting
a ﬁnal value of 200,000, we instead ﬁrst get 143,012. Then, wh en we run
the program a second time, we not only again get the wrong value, but
also a different value than the last time. In fact, if you run the program
over and over with high values of loops, you may ﬁnd that sometimes
you even get the right answer! So why is this happening?
As it turns out, the reason for these odd and unusual outcomes relate
to how instructions are executed, which is one at a time. Unfo rtunately , a
key part of the program above, where the shared counter is inc remented,
takes three instructions: one to load the value of the counte r from mem-
ory into a register, one to increment it, and one to store it ba ck into mem-
ory . Because these three instructions do not execute atomically (all at
once), strange things can happen. It is this problem of concurrency that
we will address in great detail in the second part of this book .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 47

INTRODUCTION TO OPERATING SYSTEMS 11
1 #include <stdio.h>
2 #include <unistd.h>
3 #include <assert.h>
4 #include <fcntl.h>
5 #include <sys/types.h>
6
7 int
8 main(int argc, char *argv[])
9 {
10 int fd = open("/tmp/file", O_WRONLY | O_CREAT | O_TRUNC, S_I RWXU);
11 assert(fd > -1);
12 int rc = write(fd, "hello world\n", 13);
13 assert(rc == 13);
14 close(fd);
15 return 0;
16 }
Figure 2.6: A Program That Does I/O
2.4 Persistence
The third major theme of the course is persistence. In system memory ,
data can be easily lost, as devices such as DRAM store values i n a volatile
manner; when power goes away or the system crashes, any data i n mem-
ory is lost. Thus, we need hardware and software to be able to s tore data
persistently; such storage is thus critical to any system as users care a
great deal about their data.
The hardware comes in the form of some kind of input/output or I/O
device; in modern systems, a hard drive is a common repository for long-
lived information, although solid-state drives (SSDs) are making head-
way in this arena as well.
The software in the operating system that usually manages th e disk is
called the ﬁle system; it is thus responsible for storing any ﬁles the user
creates in a reliable and efﬁcient manner on the disks of the s ystem.
Unlike the abstractions provided by the OS for the CPU and mem ory ,
the OS does not create a private, virtualized disk for each ap plication.
Rather, it is assumed that often times, users will want to share informa-
tion that is in ﬁles. For example, when writing a C program, yo u might
ﬁrst use an editor (e.g., Emacs 7) to create and edit the C ﬁle ( emacs -nw
main.c). Once done, you might use the compiler to turn the source cod e
into an executable (e.g., gcc -o main main.c ). When you’re ﬁnished,
you might run the new executable (e.g., ./main). Thus, you can see how
ﬁles are shared across different processes. First, Emacs cr eates a ﬁle that
serves as input to the compiler; the compiler uses that input ﬁle to create
a new executable ﬁle (in many steps – take a compiler course fo r details);
ﬁnally , the new executable is then run. And thus a new program is born!
To understand this better, let’s look at some code. Figure
2.6 presents
code to create a ﬁle ( /tmp/file) that contains the string “hello world”.
7You should be using Emacs. If you are using vi, there is probab ly something wrong with
you. If you are using something that is not a real code editor, that is even worse.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 48

12 INTRODUCTION TO OPERATING SYSTEMS
THE CRUX OF THE PROBLEM :
HOW TO STORE DATA PERSISTENTLY
The ﬁle system is the part of the OS in charge of managing persistent data.
What techniques are needed to do so correctly? What mechanis ms and
policies are required to do so with high performance? How is r eliability
achieved, in the face of failures in hardware and software?
To accomplish this task, the program makes three calls into t he oper-
ating system. The ﬁrst, a call to open(), opens the ﬁle and creates it; the
second, write(), writes some data to the ﬁle; the third, close(), sim-
ply closes the ﬁle thus indicating the program won’t be writi ng any more
data to it. These system calls are routed to the part of the operating sys-
tem called the ﬁle system , which then handles the requests and returns
some kind of error code to the user.
You might be wondering what the OS does in order to actually wr ite
to disk. We would show you but you’d have to promise to close yo ur
eyes ﬁrst; it is that unpleasant. The ﬁle system has to do a fai r bit of work:
ﬁrst ﬁguring out where on disk this new data will reside, and t hen keep-
ing track of it in various structures the ﬁle system maintain s. Doing so
requires issuing I/O requests to the underlying storage dev ice, to either
read existing structures or update (write) them. As anyone w ho has writ-
ten a device driver 8 knows, getting a device to do something on your
behalf is an intricate and detailed process. It requires a de ep knowledge
of the low-level device interface and its exact semantics. F ortunately , the
OS provides a standard and simple way to access devices throu gh its sys-
tem calls. Thus, the OS is sometimes seen as a standard library.
Of course, there are many more details in how devices are acce ssed,
and how ﬁle systems manage data persistently atop said devic es. For
performance reasons, most ﬁle systems ﬁrst delay such writes for a while,
hoping to batch them into larger groups. To handle the proble ms of sys-
tem crashes during writes, most ﬁle systems incorporate som e kind of
intricate write protocol, such as journaling or copy-on-write, carefully
ordering writes to disk to ensure that if a failure occurs dur ing the write
sequence, the system can recover to reasonable state afterw ards. To make
different common operations efﬁcient, ﬁle systems employ m any differ-
ent data structures and access methods, from simple lists to complex b-
trees. If all of this doesn’t make sense yet, good! We’ll be ta lking about
all of this quite a bit more in the third part of this book on persistence,
where we’ll discuss devices and I/O in general, and then disk s, RAIDs,
and ﬁle systems in great detail.
8A device driver is some code in the operating system that know s how to deal with a
speciﬁc device. We will talk more about devices and device dr ivers later.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 49

INTRODUCTION TO OPERATING SYSTEMS 13
2.5 Design Goals
So now you have some idea of what an OS actually does: it takes p hys-
ical resources, such as a CPU, memory , or disk, and virtualizes them. It
handles tough and tricky issues related to concurrency. And it stores ﬁles
persistently, thus making them safe over the long-term. Given that we
want to build such a system, we want to have some goals in mind t o help
focus our design and implementation and make trade-offs as n ecessary;
ﬁnding the right set of trade-offs is a key to building system s.
One of the most basic goals is to build up some abstractions in order
to make the system convenient and easy to use. Abstractions a re fun-
damental to everything we do in computer science. Abstracti on makes
it possible to write a large program by dividing it into small and under-
standable pieces, to write such a program in a high-level lan guage like
C9 without thinking about assembly , to write code in assembly w ithout
thinking about logic gates, and to build a processor out of ga tes without
thinking too much about transistors. Abstraction is so fund amental that
sometimes we forget its importance, but we won’t here; thus, in each sec-
tion, we’ll discuss some of the major abstractions that have developed
over time, giving you a way to think about pieces of the OS.
One goal in designing and implementing an operating system i s to
provide high performance; another way to say this is our goal is to mini-
mize the overheads of the OS. Virtualization and making the system easy
to use are well worth it, but not at any cost; thus, we must stri ve to pro-
vide virtualization and other OS features without excessiv e overheads.
These overheads arise in a number of forms: extra time (more i nstruc-
tions) and extra space (in memory or on disk). We’ll seek solu tions that
minimize one or the other or both, if possible. Perfection, h owever, is not
always attainable, something we will learn to notice and (wh ere appro-
priate) tolerate.
Another goal will be to provide protection between applications, as
well as between the OS and applications. Because we wish to al low
many programs to run at the same time, we want to make sure that the
malicious or accidental bad behavior of one does not harm oth ers; we
certainly don’t want an application to be able to harm the OS i tself (as
that would affect all programs running on the system). Protection is at
the heart of one of the main principles underlying an operati ng system,
which is that of isolation; isolating processes from one another is the key
to protection and thus underlies much of what an OS must do.
The operating system must also run non-stop; when it fails, all appli-
cations running on the system fail as well. Because of this de pendence,
operating systems often strive to provide a high degree of reliability. As
operating systems grow evermore complex (sometimes contai ning mil-
lions of lines of code), building a reliable operating syste m is quite a chal-
9Some of you might object to calling C a high-level language. R emember this is an OS
course, though, where we’re simply happy not to have to code i n assembly all the time!
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 50

14 INTRODUCTION TO OPERATING SYSTEMS
lenge – and indeed, much of the on-going research in the ﬁeld ( including
some of our own work [BS+09, SS+10]) focuses on this exact pro blem.
Other goals make sense: energy-efﬁciency is important in our increas-
ingly green world; security (an extension of protection, really) against
malicious applications is critical, especially in these hi ghly-networked
times; mobility is increasingly important as OSes are run on smaller and
smaller devices. Depending in how the system is used, the OS w ill have
different goals and thus likely be implemented in at least sl ightly differ-
ent ways. However, as we will see, many of the principles we wi ll present
on how to build operating systems are useful in the range of di fferent de-
vices.
2.6 Some History
Before closing this introduction, let us present a brief his tory of how
operating systems developed. Like any system built by human s, good
ideas accumulated in operating systems over time, as engine ers learned
what was important in their design. Here, we discuss a few maj or devel-
opments. For a richer treatment, see Brinch Hansen’s excell ent history of
operating systems [BH00].
Early Operating Systems: Just Libraries
In the beginning, the operating system didn’t do too much. Ba sically ,
it was just a set of libraries of commonly-used functions; fo r example,
instead of having each programmer of the system write low-le vel I/O
handling code, the “OS” would provide such APIs, and thus mak e life
easier for the developer.
Usually , on these old mainframe systems, one program ran at a time,
as controlled by a human operator. Much of what you think a mod ern
OS would do (e.g., deciding what order to run jobs in) was perf ormed by
this operator. If you were a smart developer, you would be nic e to this
operator, so that they might move your job to the front of the q ueue.
This mode of computing was known as batch processing, as a number
of jobs were set up and then run in a “batch” by the operator. Co mputers,
as of that point, were not used in an interactive manner, beca use of cost:
it was simply too costly to let a user sit in front of the comput er and use it,
as most of the time it would just sit idle then, costing the facility hundreds
of thousands of dollars per hour [BH00].
Beyond Libraries: Protection
In moving beyond being a simple library of commonly-used ser vices, op-
erating systems took on a more central role in managing machi nes. One
important aspect of this was the realization that code run on behalf of the
OS was special; it had control of devices and thus should be tr eated dif-
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 51

INTRODUCTION TO OPERATING SYSTEMS 15
ferently than normal application code. Why is this? Well, im agine if you
allowed any application to read from anywhere on the disk; th e notion of
privacy goes out the window , as any program could read any ﬁle . Thus,
implementing a ﬁle system (to manage your ﬁles) as a library makes little
sense. Instead, something else was needed.
Thus, the idea of a system call was invented, pioneered by the Atlas
computing system [K+61,L78]. Instead of providing OS routi nes as a li-
brary (where you just make a procedure call to access them), the idea here
was to add a special pair of hardware instructions and hardwa re state to
make the transition into the OS a more formal, controlled pro cess.
The key difference between a system call and a procedure call is that
a system call transfers control (i.e., jumps) into the OS whi le simultane-
ously raising the hardware privilege level. User applications run in what
is referred to as user mode which means the hardware restricts what ap-
plications can do; for example, an application running in us er mode can’t
typically initiate an I/O request to the disk, access any phy sical memory
page, or send a packet on the network. When a system call is ini tiated
(usually through a special hardware instruction called a trap), the hard-
ware transfers control to a pre-speciﬁed trap handler (that the OS set up
previously) and simultaneously raises the privilege level to kernel mode.
In kernel mode, the OS has full access to the hardware of the sy stem and
thus can do things like initiate an I/O request or make more me mory
available to a program. When the OS is done servicing the requ est, it
passes control back to the user via a special return-from-trap instruction,
which reverts to user mode while simultaneously passing con trol back to
where the application left off.
The Era of Multiprogramming
Where operating systems really took off was in the era of comp uting be-
yond the mainframe, that of the minicomputer. Classic machines like
the PDP family from Digital Equipment made computers hugely more
affordable; thus, instead of having one mainframe per large organization,
now a smaller collection of people within an organization co uld likely
have their own computer. Not surprisingly , one of the major i mpacts of
this drop in cost was an increase in developer activity; more smart people
got their hands on computers and thus made computer systems d o more
interesting and beautiful things.
In particular, multiprogramming became commonplace due to the de-
sire to make better use of machine resources. Instead of just running one
job at a time, the OS would load a number of jobs into memory and switch
rapidly between them, thus improving CPU utilization. This switching
was particularly important because I/O devices were slow; h aving a pro-
gram wait on the CPU while its I/O was being serviced was a wast e of
CPU time. Instead, why not switch to another job and run it for a while?
The desire to support multiprogramming and overlap in the pr esence
of I/O and interrupts forced innovation in the conceptual development of
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 52

16 INTRODUCTION TO OPERATING SYSTEMS
operating systems along a number of directions. Issues such as memory
protection became important; we wouldn’t want one program to be able
to access the memory of another program. Understanding how t o deal
with the concurrency issues introduced by multiprogramming was also
critical; making sure the OS was behaving correctly despite the presence
of interrupts is a great challenge. We will study these issue s and related
topics later in the book.
One of the major practical advances of the time was the introd uction
of the U NIX operating system, primarily thanks to Ken Thompson (and
Dennis Ritchie) at Bell Labs (yes, the phone company). U NIX took many
good ideas from different operating systems (particularly from Multics
[O72], and some from systems like TENEX [B+72] and the Berkel ey Time-
Sharing System [S+68]), but made them simpler and easier to u se. Soon
this team was shipping tapes containing U NIX source code to people
around the world, many of whom then got involved and added to t he
system themselves; see the Aside (next page) for more detail 10.
The Modern Era
Beyond the minicomputer came a new type of machine, cheaper, faster,
and for the masses: the personal computer, or PC as we call it today . Led
by Apple’s early machines (e.g., the Apple II) and the IBM PC, this new
breed of machine would soon become the dominant force in comp uting,
as their low-cost enabled one machine per desktop instead of a shared
minicomputer per workgroup.
Unfortunately , for operating systems, the PC at ﬁrst repres ented a
great leap backwards, as early systems forgot (or never knew of) the
lessons learned in the era of minicomputers. For example, ea rly operat-
ing systems such as DOS (the Disk Operating System , from Microsoft)
didn’t think memory protection was important; thus, a malic ious (or per-
haps just a poorly-programmed) application could scribble all over mem-
ory . The ﬁrst generations of the Mac OS (v9 and earlier) took a coopera-
tive approach to job scheduling; thus, a thread that acciden tally got stuck
in an inﬁnite loop could take over the entire system, forcing a reboot. The
painful list of OS features missing in this generation of sys tems is long,
too long for a full discussion here.
Fortunately , after some years of suffering, the old features of minicom-
puter operating systems started to ﬁnd their way onto the des ktop. For
example, Mac OS X has U NIX at its core, including all of the features
one would expect from such a mature system. Windows has simil arly
adopted many of the great ideas in computing history , starti ng in partic-
ular with Windows NT, a great leap forward in Microsoft OS tec hnology .
Even today’s cell phones run operating systems (such as Linu x) that are
10We’ll use asides and other related text boxes to call attenti on to various items that don’t
quite ﬁt the main ﬂow of the text. Sometimes, we’ll even use th em just to make a joke, because
why not have a little fun along the way? Yes, many of the jokes a re bad.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 53

INTRODUCTION TO OPERATING SYSTEMS 17
ASIDE : THE IMPORTANCE OF UNIX
It is difﬁcult to overstate the importance of U NIX in the history of oper-
ating systems. Inﬂuenced by earlier systems (in particular , the famous
Multics system from MIT), U NIX brought together many great ideas and
made a system that was both simple and powerful.
Underlying the original “Bell Labs” U NIX was the unifying principle of
building small powerful programs that could be connected to gether to
form larger workﬂows. The shell, where you type commands, provided
primitives such as pipes to enable such meta-level programming, and
thus it became easy to string together programs to accomplis h a big-
ger task. For example, to ﬁnd lines of a text ﬁle that have the w ord
“foo” in them, and then to count how many such lines exist, you would
type: grep foo file.txt|wc -l , thus using the grep and wc (word
count) programs to achieve your task.
The U NIX environment was friendly for programmers and developers
alike, also providing a compiler for the new C programming language .
Making it easy for programmers to write their own programs, a s well as
share them, made U NIX enormously popular. And it probably helped a
lot that the authors gave out copies for free to anyone who ask ed, an early
form of open-source software.
Also of critical importance was the accessibility and reada bility of the
code. Having a beautiful, small kernel written in C invited o thers to play
with the kernel, adding new and cool features. For example, a n enter-
prising group at Berkeley , led by Bill Joy, made a wonderful distribution
(the Berkeley Systems Distribution, or BSD) which had some advanced
virtual memory , ﬁle system, and networking subsystems. Joy later co-
founded Sun Microsystems.
Unfortunately , the spread of UNIX was slowed a bit as companies tried to
assert ownership and proﬁt from it, an unfortunate (but comm on) result
of lawyers getting involved. Many companies had their own va riants:
SunOS from Sun Microsystems, AIX from IBM, HPUX (a.k.a. “H-Pucks”)
from HP , and IRIX from SGI. The legal wrangling among AT&T/Bell
Labs and these other players cast a dark cloud over U NIX , and many
wondered if it would survive, especially as Windows was introduced and
took over much of the PC market...
much more like what a minicomputer ran in the 1970s than what a PC
ran in the 1980s (thank goodness); it is good to see that the go od ideas de-
veloped in the heyday of OS development have found their way i nto the
modern world. Even better is that these ideas continue to dev elop, pro-
viding more features and making modern systems even better f or users
and applications.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 54

18 INTRODUCTION TO OPERATING SYSTEMS
ASIDE : AND THEN CAME LINUX
Fortunately for U NIX , a young Finnish hacker named Linus T orvaldsde-
cided to write his own version of U NIX which borrowed heavily on the
principles and ideas behind the original system, but not fro m the code
base, thus avoiding issues of legality . He enlisted help fro m many oth-
ers around the world, and soon Linux was born (as well as the modern
open-source software movement).
As the internet era came into place, most companies (such as G oogle,
Amazon, Facebook, and others) chose to run Linux, as it was fr ee and
could be readily modiﬁed to suit their needs; indeed, it is ha rd to imag-
ine the success of these new companies had such a system not ex isted.
As smart phones became a dominant user-facing platform, Lin ux found
a stronghold there too (via Android), for many of the same rea sons. And
Steve Jobs took his U NIX -based NeXTStep operating environment with
him to Apple, thus making U NIX popular on desktops (though many
users of Apple technology are probably not even aware of this fact). And
thus U NIX lives on, more important today than ever before. The comput-
ing gods, if you believe in them, should be thanked for this wo nderful
outcome.
2.7 Summary
Thus, we have an introduction to the OS. Today’s operating sy stems
make systems relatively easy to use, and virtually all opera ting systems
you use today have been inﬂuenced by the developments we will discuss
throughout the book.
Unfortunately , due to time constraints, there are a number o f parts of
the OS we won’t cover in the book. For example, there is a lot of net-
working code in the operating system; we leave it to you to take the net -
working class to learn more about that. Similarly , graphics devices are
particularly important; take the graphics course to expand your knowl-
edge in that direction. Finally , some operating system book s talk a great
deal about security; we will do so in the sense that the OS must provide
protection between running programs and give users the abil ity to pro-
tect their ﬁles, but we won’t delve into deeper security issu es that one
might ﬁnd in a security course.
However, there are many important topics that we will cover, includ-
ing the basics of virtualization of the CPU and memory , concurrency , and
persistence via devices and ﬁle systems. Don’t worry! While there is a
lot of ground to cover, most of it is quite cool, and at the end o f the road,
you’ll have a new appreciation for how computer systems real ly work.
Now get to work!
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 55

INTRODUCTION TO OPERATING SYSTEMS 19
References
[BS+09] “Tolerating File-System Mistakes with EnvyFS”
Lakshmi N. Bairavasundaram, Swaminathan Sundararaman, Andrea C. Arpaci-Dusseau, Remzi
H. Arpaci-Dusseau
USENIX ’09, San Diego, CA, June 2009
A fun paper about using multiple ﬁle systems at once to tolera te a mistake in any one of them.
[BH00] “The Evolution of Operating Systems”
P . Brinch Hansen
In Classic Operating Systems: From Batch Processing to Dist ributed Systems
Springer-V erlag, New York, 2000
This essay provides an intro to a wonderful collection of pap ers about historically signiﬁcant systems.
[B+72] “TENEX, A Paged Time Sharing System for the PDP-10”
Daniel G. Bobrow, Jerry D. Burchﬁel, Daniel L. Murphy , Raymond S. Tomlinson
CACM, V olume 15, Number 3, March 1972
TENEX has much of the machinery found in modern operating sys tems; read more about it to see how
much innovation was already in place in the early 1970’s.
[B75] “The Mythical Man-Month”
Fred Brooks
Addison-Wesley , 1975
A classic text on software engineering; well worth the read.
[BOH10] “Computer Systems: A Programmer’s Perspective”
Randal E. Bryant and David R. O’Hallaron
Addison-Wesley , 2010
Another great intro to how computer systems work. Has a littl e bit of overlap with this book – so if you’d
like, you can skip the last few chapters of that book, or simpl y read them to get a different perspective
on some of the same material. After all, one good way to build u p your own knowledge is to hear as
many other perspectives as possible, and then develop your o wn opinion and thoughts on the matter.
Y ou know, by thinking!
[K+61] “One-Level Storage System”
T. Kilburn, D.B.G. Edwards, M.J. Lanigan, F.H. Sumner
IRE Transactions on Electronic Computers, April 1962
The Atlas pioneered much of what you see in modern systems. Ho wever, this paper is not the best read.
If you were to only read one, you might try the historical pers pective below [L78].
[L78] “The Manchester Mark I and Atlas: A Historical Perspec tive”
S. H. Lavington
Communications of the ACM archive
V olume 21, Issue 1 (January 1978), pages 4-12
A nice piece of history on the early development of computer s ystems and the pioneering efforts of the
Atlas. Of course, one could go back and read the Atlas papers t hemselves, but this paper provides a great
overview and adds some historical perspective.
[O72] “The Multics System: An Examination of its Structure”
Elliott Organick, 1972
A great overview of Multics. So many good ideas, and yet it was an over-designed system, shooting for
too much, and thus never really worked as expected. A classic example of what Fred Brooks would call
the “second-system effect” [B75].
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 56

20 INTRODUCTION TO OPERATING SYSTEMS
[PP03] “Introduction to Computing Systems:
From Bits and Gates to C and Beyond”
Yale N. Patt and Sanjay J. Patel
McGraw-Hill, 2003
One of our favorite intro to computing systems books. Starts at transistors and gets you all the way up
to C; the early material is particularly great.
[RT74] “The U NIX Time-Sharing System”
Dennis M. Ritchie and Ken Thompson
CACM, V olume 17, Number 7, July 1974, pages 365-375
A great summary of UNIX written as it was taking over the world of computing, by the pe ople who
wrote it.
[S68] “SDS 940 Time-Sharing System”
Scientiﬁc Data Systems Inc.
TECHNICAL MANUAL, SDS 90 11168 August 1968
Available: http://goo.gl/EN0Zrn
Y es, a technical manual was the best we could ﬁnd. But it is fas cinating to read these old system
documents, and see how much was already in place in the late 19 60’s. One of the minds behind the
Berkeley Time-Sharing System (which eventually became the SDS system) was Butler Lampson, who
later won a Turing award for his contributions in systems.
[SS+10] “Membrane: Operating System Support for Restartab le File Systems”
Swaminathan Sundararaman, Sriram Subramanian, Abhishek R ajimwale,
Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau, Michae l M. Swift
FAST ’10, San Jose, CA, February 2010
The great thing about writing your own class notes: you can ad vertise your own research. But this
paper is actually pretty neat – when a ﬁle system hits a bug and crashes, Membrane auto-magically
restarts it, all without applications or the rest of the syst em being affected.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 57

Part I
Virtualization
21

## Page 59

3
A Dialogue on Virtualization
Professor: And thus we reach the ﬁrst of our three pieces on operating sys tems:
virtualization.
Student: But what is virtualization, oh noble professor?
Professor: Imagine we have a peach.
Student: A peach? (incredulous)
Professor: Y es, a peach. Let us call that the physical peach. But we have many
eaters who would like to eat this peach. What we would like to p resent to each
eater is their own peach, so that they can be happy. We call the peach we give
eaters virtual peaches; we somehow create many of these virtual peaches out of
the one physical peach. And the important thing: in this illu sion, it looks to each
eater like they have a physical peach, but in reality they don ’t.
Student: So you are sharing the peach, but you don’t even know it?
Professor: Right! Exactly.
Student: But there’s only one peach.
Professor: Y es. And...?
Student: Well, if I was sharing a peach with somebody else, I think I wou ld
notice.
Professor: Ah yes! Good point. But that is the thing with many eaters; mos t
of the time they are napping or doing something else, and thus , you can snatch
that peach away and give it to someone else for a while. And thu s we create the
illusion of many virtual peaches, one peach for each person!
Student: Sounds like a bad campaign slogan. Y ou are talking about comp uters,
right Professor?
Professor: Ah, young grasshopper, you wish to have a more concrete examp le.
Good idea! Let us take the most basic of resources, the CPU. As sume there is one
physical CPU in a system (though now there are often two or four or more). What
virtualization does is take that single CPU and make it look l ike many virtual
CPUs to the applications running on the system. Thus, while e ach applications
23

## Page 60

24 A D IALOGUE ON VIRTUALIZATION
thinks it has its own CPU to use, there is really only one. And t hus the OS has
created a beautiful illusion: it has virtualized the CPU.
Student: Wow! That sounds like magic. T ell me more! How does that work?
Professor: In time, young student, in good time. Sounds like you are read y to
begin.
Student: I am! Well, sort of. I must admit, I’m a little worried you are g oing to
start talking about peaches again.
Professor: Don’t worry too much; I don’t even like peaches. And thus we be -
gin...
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 61

4
The Abstraction: The Process
In this note, we discuss one of the most fundamental abstract ions that the
OS provides to users: the process. The deﬁnition of a process, informally ,
is quite simple: it is a running program [V+65,B70]. The program itself is
a lifeless thing: it just sits there on the disk, a bunch of ins tructions (and
maybe some static data), waiting to spring into action. It is the operating
system that takes these bytes and gets them running, transfo rming the
program into something useful.
It turns out that one often wants to run more than one program a t
once; for example, consider your desktop or laptop where you might like
to run a web browser, mail program, a game, a music player, and so forth.
In fact, a typical system may be seemingly running tens or even hundreds
of processes at the same time. Doing so makes the system easy t o use, as
one never need be concerned with whether a CPU is available; one simply
runs programs. Hence our challenge:
THE CRUX OF THE PROBLEM :
HOW TO PROVIDE THE ILLUSION OF MANY CPU S?
Although there are only a few physical CPUs available, how ca n the
OS provide the illusion of a nearly-endless supply of said CP Us?
The OS creates this illusion by virtualizing the CPU. By running one
process, then stopping it and running another, and so forth, the OS can
promote the illusion that many virtual CPUs exist when in fac t there is
only one physical CPU (or a few). This basic technique, known as time
sharing of the CPU, allows users to run as many concurrent processes a s
they would like; the potential cost is performance, as each w ill run more
slowly if the CPU(s) must be shared.
To implement virtualization of the CPU, and to implement it w ell, the
OS will need both some low-level machinery as well as some hig h-level
intelligence. We call the low-level machinery mechanisms; mechanisms
are low-level methods or protocols that implement a needed p iece of
25

## Page 62

26 THE ABSTRACTION : T HE PROCESS
TIP : U SE TIME SHARING (AND SPACE SHARING )
Time sharing is one of the most basic techniques used by an OS to share
a resource. By allowing the resource to be used for a little wh ile by one
entity , and then a little while by another, and so forth, the r esource in
question (e.g., the CPU, or a network link) can be shared by ma ny . The
natural counterpart of time sharing is space sharing, where a resource is
divided (in space) among those who wish to use it. For example , disk
space is naturally a space-shared resource, as once a block i s assigned to
a ﬁle, it is not likely to be assigned to another ﬁle until the u ser deletes it.
functionality . For example, we’ll learn below how to implem ent a con-
text switch, which gives the OS the ability to stop running one program
and start running another on a given CPU; this time-sharing mechanism
is employed by all modern OSes.
On top of these mechanisms resides some of the intelligence i n the
OS, in the form of policies. Policies are algorithms for making some
kind of decision within the OS. For example, given a number of possi-
ble programs to run on a CPU, which program should the OS run? A
scheduling policy in the OS will make this decision, likely using histori-
cal information (e.g., which program has run more over the la st minute?),
workload knowledge (e.g., what types of programs are run), a nd perfor-
mance metrics (e.g., is the system optimizing for interacti ve performance,
or throughput?) to make its decision.
4.1 The Abstraction: A Process
The abstraction provided by the OS of a running program is something
we will call a process. As we said above, a process is simply a running
program; at any instant in time, we can summarize a process by taking an
inventory of the different pieces of the system it accesses o r affects during
the course of its execution.
To understand what constitutes a process, we thus have to understand
its machine state: what a program can read or update when it is running.
At any given time, what parts of the machine are important to t he execu-
tion of this program?
One obvious component of machine state that comprises a proc ess is
its memory. Instructions lie in memory; the data that the running pro-
gram reads and writes sits in memory as well. Thus the memory t hat the
process can address (called its address space) is part of the process.
Also part of the process’s machine state are registers; many instructions
explicitly read or update registers and thus clearly they ar e important to
the execution of the process.
Note that there are some particularly special registers tha t form part
of this machine state. For example, the program counter (PC) (sometimes
called the instruction pointer or IP) tells us which instruction of the pro-
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 63

THE ABSTRACTION : T HE PROCESS 27
TIP : S EPARATE POLICY AND MECHANISM
In many operating systems, a common design paradigm is to sep arate
high-level policies from their low-level mechanisms [L+75 ]. You can
think of the mechanism as providing the answer to a how question about
a system; for example, how does an operating system perform a context
switch? The policy provides the answer to a which question; for example,
which process should the operating system run right now? Separati ng the
two allows one easily to change policies without having to re think the
mechanism and is thus a form of modularity, a general software design
principle.
gram is currently being executed; similarly a stack pointer and associated
frame pointer are used to manage the stack for function parameters, local
variables, and return addresses.
Finally , programs often access persistent storage devices too. Such I/O
information might include a list of the ﬁles the process currently has ope n.
4.2 Process API
Though we defer discussion of a real process API until a subse quent
chapter, here we ﬁrst give some idea of what must be included i n any
interface of an operating system. These APIs, in some form, a re available
on any modern operating system.
• Create: An operating system must include some method to cre-
ate new processes. When you type a command into the shell, or
double-click on an application icon, the OS is invoked to cre ate a
new process to run the program you have indicated.
• Destroy: As there is an interface for process creation, systems also
provide an interface to destroy processes forcefully . Of course, many
processes will run and just exit by themselves when complete; when
they don’t, however, the user may wish to kill them, and thus a n in-
terface to halt a runaway process is quite useful.
• Wait: Sometimes it is useful to wait for a process to stop running;
thus some kind of waiting interface is often provided.
• Miscellaneous Control: Other than killing or waiting for a process,
there are sometimes other controls that are possible. For ex ample,
most operating systems provide some kind of method to suspen d a
process (stop it from running for a while) and then resume it ( con-
tinue it running).
• Status: There are usually interfaces to get some status information
about a process as well, such as how long it has run for, or what
state it is in.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 64

28 THE ABSTRACTION : T HE PROCESS
MemoryCPU
Disk
code
static data
heap
stack
Process
code
static data
Program Loading:
Takes on-disk program
and reads it into the
address space of process
Figure 4.1: Loading: From Program T o Process
4.3 Process Creation: A Little More Detail
One mystery that we should unmask a bit is how programs are tra ns-
formed into processes. Speciﬁcally , how does the OS get a pro gram up
and running? How does process creation actually work?
The ﬁrst thing that the OS must do to run a program is to load its code
and any static data (e.g., initialized variables) into memo ry , into the ad-
dress space of the process. Programs initially reside on disk (or, in some
modern systems, ﬂash-based SSDs) in some kind of executable format;
thus, the process of loading a program and static data into me mory re-
quires the OS to read those bytes from disk and place them in me mory
somewhere (as shown in Figure 4.1).
In early (or simple) operating systems, the loading process is done ea-
gerly, i.e., all at once before running the program; modern OSes pe rform
the process lazily, i.e., by loading pieces of code or data only as they are
needed during program execution. To truly understand how lazy loading
of pieces of code and data works, you’ll have to understand mo re about
the machinery of paging and swapping, topics we’ll cover in the future
when we discuss the virtualization of memory . For now , just r emember
that before running anything, the OS clearly must do some wor k to get
the important program bits from disk into memory .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 65

THE ABSTRACTION : T HE PROCESS 29
Once the code and static data are loaded into memory , there ar e a few
other things the OS needs to do before running the process. So me mem-
ory must be allocated for the program’s run-time stack (or just stack).
As you should likely already know , C programs use the stack fo r local
variables, function parameters, and return addresses; the OS allocates
this memory and gives it to the process. The OS will also likel y initial-
ize the stack with arguments; speciﬁcally , it will ﬁll in the parameters to
the main() function, i.e., argc and the argv array .
The OS may also create some initial memory for the program’s heap.
In C programs, the heap is used for explicitly requested dyna mically-
allocated data; programs request such space by calling malloc() and
free it explicitly by calling free(). The heap is needed for data struc-
tures such as linked lists, hash tables, trees, and other int eresting data
structures. The heap will be small at ﬁrst; as the program run s, and re-
quests more memory via the malloc() library API, the OS may get in-
volved and allocate more memory to the process to help satisfy such calls.
The OS will also do some other initialization tasks, particu larly as re-
lated to input/output (I/O). For example, in U NIX systems, each process
by default has three open ﬁle descriptors, for standard input, output, and
error; these descriptors let programs easily read input fro m the terminal
as well as print output to the screen. We’ll learn more about I /O, ﬁle
descriptors, and the like in the third part of the book on persistence.
By loading the code and static data into memory , by creating a nd ini-
tializing a stack, and by doing other work as related to I/O se tup, the OS
has now (ﬁnally) set the stage for program execution. It thus has one last
task: to start the program running at the entry point, namely main(). By
jumping to the main() routine (through a specialized mechanism that
we will discuss next chapter), the OS transfers control of th e CPU to the
newly-created process, and thus the program begins its exec ution.
4.4 Process States
Now that we have some idea of what a process is (though we will
continue to reﬁne this notion), and (roughly) how it is creat ed, let us talk
about the different states a process can be in at a given time. The notion
that a process can be in one of these states arose in early computer systems
[V+65,DV66]. In a simpliﬁed view , a process can be in one of th ree states:
• Running: In the running state, a process is running on a processor.
This means it is executing instructions.
• Ready: In the ready state, a process is ready to run but for some
reason the OS has chosen not to run it at this given moment.
• Blocked: In the blocked state, a process has performed some kind
of operation that makes it not ready to run until some other ev ent
takes place. A common example: when a process initiates an I/ O
request to a disk, it becomes blocked and thus some other proc ess
can use the processor.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 66

30 THE ABSTRACTION : T HE PROCESS
Running Ready
Blocked
Descheduled
Scheduled
I/O: initiate I/O: done
Figure 4.2: Process: State T ransitions
If we were to map these states to a graph, we would arrive at the di-
agram in Figure 4.2. As you can see in the diagram, a process can be
moved between the ready and running states at the discretion of the OS.
Being moved from ready to running means the process has been sched-
uled; being moved from running to ready means the process has been
descheduled. Once a process has become blocked (e.g., by initiating an
I/O operation), the OS will keep it as such until some event oc curs (e.g.,
I/O completion); at that point, the process moves to the read y state again
(and potentially immediately to running again, if the OS so d ecides).
4.5 Data Structures
The OS is a program, and like any program, it has some key data struc-
tures that track various relevant pieces of information. To track the state
of each process, for example, the OS likely will keep some kin d of process
list for all processes that are ready , as well as some additional i nforma-
tion to track which process is currently running. The OS must also track,
in some way , blocked processes; when an I/O event completes, the OS
should make sure to wake the correct process and ready it to ru n again.
Figure 4.3 shows what type of information an OS needs to track about
each process in the xv6 kernel [CK+08]. Similar process stru ctures exist
in “real” operating systems such as Linux, Mac OS X, or Window s; look
them up and see how much more complex they are.
From the ﬁgure, you can see a couple of important pieces of inf orma-
tion the OS tracks about a process. The register context will hold, for
a stopped process, the contents of its register state. When a process is
stopped, its register state will be saved to this memory location; by restor-
ing these registers (i.e., placing their values back into th e actual physical
registers), the OS can resume running the process. We’ll lea rn more about
this technique known as a context switch in future chapters.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 67

THE ABSTRACTION : T HE PROCESS 31
// the registers xv6 will save and restore
// to stop and subsequently restart a process
struct context {
int eip;
int esp;
int ebx;
int ecx;
int edx;
int esi;
int edi;
int ebp;
};
// the different states a process can be in
enum proc_state { UNUSED, EMBRYO, SLEEPING,
RUNNABLE, RUNNING, ZOMBIE };
// the information xv6 tracks about each process
// including its register context and state
struct proc {
char *mem; // Start of process memory
uint sz; // Size of process memory
char *kstack; // Bottom of kernel stack
// for this process
enum proc_state state; // Process state
int pid; // Process ID
struct proc *parent; // Parent process
void *chan; // If non-zero, sleeping on chan
int killed; // If non-zero, have been killed
struct file *ofile[NOFILE]; // Open files
struct inode *cwd; // Current directory
struct context context; // Switch here to run process
struct trapframe *tf; // Trap frame for the
// current interrupt
};
Figure 4.3: The xv6 Proc Structure
You can also see from the ﬁgure that there are some other state s a pro-
cess can be in, beyond running, ready , and blocked. Sometime s a system
will have an initial state that the process is in when it is being created.
Also, a process could be placed in a ﬁnal state where it has exited but
has not yet been cleaned up (in UNIX-based systems, this is ca lled the
zombie state1). This ﬁnal state can be useful as it allows other processes
(usually the parent that created the process) to examine the return code
of the process and see if it the just-ﬁnished process execute d successfully
(usually , programs return zero in U NIX -based systems when they have
accomplished a task successfully , and non-zero otherwise) . When ﬁn-
ished, the parent will make one ﬁnal call (e.g., wait()) to wait for the
completion of the child, and to also indicate to the OS that it can clean up
any relevant data structures that referred to the now-extin ct process.
1Yes, the zombie state. Just like real zombies, these zombies are relatively easy to kill.
However, different techniques are usually recommended.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 68

32 THE ABSTRACTION : T HE PROCESS
ASIDE : DATA STRUCTURE – T HE PROCESS LIST
Operating systems are replete with various important data structures
that we will discuss in these notes. The process list is the ﬁrst such struc-
ture. It is one of the simpler ones, but certainly any OS that h as the ability
to run multiple programs at once will have something akin to t his struc-
ture in order to keep track of all the running programs in the s ystem.
Sometimes people refer to the individual structure that sto res informa-
tion about a process as a Process Control Block (PCB), a fancy way of
talking about a C structure that contains information about each process.
4.6 Summary
We have introduced the most basic abstraction of the OS: the p rocess.
It is quite simply viewed as a running program. With this conc eptual
view in mind, we will now move on to the nitty-gritty: the low- level
mechanisms needed to implement processes, and the higher-l evel poli-
cies required to schedule them in an intelligent way . By combining mech-
anisms and policies, we will build up our understanding of ho w an oper-
ating system virtualizes the CPU.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 69

THE ABSTRACTION : T HE PROCESS 33
References
[CK+08] “The xv6 Operating System”
Russ Cox, Frans Kaashoek, Robert Morris, Nickolai Zeldovic h
From: http://pdos.csail.mit.edu/6.828/2008/index.htm l
The coolest real and little OS in the world. Download and play with it to learn more about the details of
how operating systems actually work.
[DV66] “Programming Semantics for Multiprogrammed Comput ations”
Jack B. Dennis and Earl C. Van Horn
Communications of the ACM, V olume 9, Number 3, March 1966
This paper deﬁned many of the early terms and concepts around building multiprogrammed systems.
[H70] “The Nucleus of a Multiprogramming System”
Per Brinch Hansen
Communications of the ACM, V olume 13, Number 4, April 1970
This paper introduces one of the ﬁrst microkernels in operating systems history, called Nucleus. The
idea of smaller, more minimal systems is a theme that rears its head repeatedly in OS history; it all began
with Brinch Hansen’s work described herein.
[L+75] “Policy/mechanism separation in Hydra”
R. Levin, E. Cohen, W. Corwin, F. Pollack, W. Wulf
SOSP 1975
An early paper about how to structure operating systems in a r esearch OS known as Hydra. While
Hydra never became a mainstream OS, some of its ideas inﬂuenc ed OS designers.
[V+65] “Structure of the Multics Supervisor”
V .A. Vyssotsky , F. J. Corbato, R. M. Graham
Fall Joint Computer Conference, 1965
An early paper on Multics, which described many of the basic i deas and terms that we ﬁnd in modern
systems. Some of the vision behind computing as a utility are ﬁnally being realized in modern cloud
systems.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 71

5
Interlude: Process API
ASIDE : INTERLUDES
Interludes will cover more practical aspects of systems, in cluding a par-
ticular focus on operating system APIs and how to use them. If you don’t
like practical things, you could skip these interludes. But you should like
practical things, because, well, they are generally useful in real life; com-
panies, for example, don’t usually hire you for your non-pra ctical skills.
In this interlude, we discuss process creation in U NIX systems. U NIX
presents one of the most intriguing ways to create a new proce ss with
a pair of system calls: fork() and exec(). A third routine, wait(),
can be used by a process wishing to wait for a process it has cre ated to
complete. We now present these interfaces in more detail, wi th a few
simple examples to motivate us. And thus, our problem:
CRUX : H OW TO CREATE AND CONTROL PROCESSES
What interfaces should the OS present for process creation a nd con-
trol? How should these interfaces be designed to enable ease of use as
well as utility?
5.1 The fork() System Call
The fork() system call is used to create a new process [C63]. How-
ever, be forewarned: it is certainly the strangest routine y ou will ever
call1. More speciﬁcally , you have a running program whose code loo ks
like what you see in Figure 5.1; examine the code, or better yet, type it in
and run it yourself!
1Well, OK, we admit that we don’t know that for sure; who knows w hat routines you
call when no one is looking? But fork() is pretty odd, no matter how unusual your routine-
calling patterns are.
35

## Page 72

36 INTERLUDE : P ROCESS API
1 #include <stdio.h>
2 #include <stdlib.h>
3 #include <unistd.h>
4
5 int
6 main(int argc, char *argv[])
7 {
8 printf("hello world (pid:%d)\n", (int) getpid());
9 int rc = fork();
10 if (rc < 0) { // fork failed; exit
11 fprintf(stderr, "fork failed\n");
12 exit(1);
13 } else if (rc == 0) { // child (new process)
14 printf("hello, I am child (pid:%d)\n", (int) getpid());
15 } else { // parent goes down this path (main)
16 printf("hello, I am parent of %d (pid:%d)\n",
17 rc, (int) getpid());
18 }
19 return 0;
20 }
Figure 5.1: p1.c: Calling fork()
When you run this program (called p1.c), you’ll see the following:
prompt> ./p1
hello world (pid:29146)
hello, I am parent of 29147 (pid:29146)
hello, I am child (pid:29147)
prompt>
Let us understand what happened in more detail in p1.c. When it
ﬁrst started running, the process prints out a hello world me ssage; in-
cluded in that message is its process identiﬁer, also known as a PID. The
process has a PID of 29146; in U NIX systems, the PID is used to name
the process if one wants to do something with the process, suc h as (for
example) stop it from running. So far, so good.
Now the interesting part begins. The process calls the fork() system
call, which the OS provides as a way to create a new process. Th e odd
part: the process that is created is an (almost) exact copy of the calling pro-
cess. That means that to the OS, it now looks like there are two copi es of
the program p1 running, and both are about to return from the fork()
system call. The newly-created process (called the child, in contrast to the
creating parent) doesn’t start running at main(), like you might expect
(note, the “hello, world” message only got printed out once) ; rather, it
just comes into life as if it had called fork() itself.
You might have noticed: the child isn’t an exact copy . Speciﬁcally , al-
though it now has its own copy of the address space (i.e., its o wn private
memory), its own registers, its own PC, and so forth, the valu e it returns
to the caller of fork() is different. Speciﬁcally , while the parent receives
the PID of the newly-created child, the child is simply retur ned a 0. This
differentiation is useful, because it is simple then to writ e the code that
handles the two different cases (as above).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 73

INTERLUDE : P ROCESS API 37
1 #include <stdio.h>
2 #include <stdlib.h>
3 #include <unistd.h>
4 #include <sys/wait.h>
5
6 int
7 main(int argc, char *argv[])
8 {
9 printf("hello world (pid:%d)\n", (int) getpid());
10 int rc = fork();
11 if (rc < 0) { // fork failed; exit
12 fprintf(stderr, "fork failed\n");
13 exit(1);
14 } else if (rc == 0) { // child (new process)
15 printf("hello, I am child (pid:%d)\n", (int) getpid());
16 } else { // parent goes down this path (main)
17 int wc = wait(NULL);
18 printf("hello, I am parent of %d (wc:%d) (pid:%d)\n",
19 rc, wc, (int) getpid());
20 }
21 return 0;
22 }
Figure 5.2: p2.c: Calling fork() And wait()
You might also have noticed: the output is not deterministic. When
the child process is created, there are now two active proces ses in the sys-
tem that we care about: the parent and the child. Assuming we a re run-
ning on a system with a single CPU (for simplicity), then eith er the child
or the parent might run at that point. In our example (above), the parent
did and thus printed out its message ﬁrst. In other cases, the opposite
might happen, as we show in this output trace:
prompt> ./p1
hello world (pid:29146)
hello, I am child (pid:29147)
hello, I am parent of 29147 (pid:29146)
prompt>
The CPU scheduler, a topic we’ll discuss in great detail soon, deter-
mines which process runs at a given moment in time; because th e sched-
uler is complex, we cannot usually make strong assumptions a bout what
it will choose to do, and hence which process will run ﬁrst. Th is non-
determinism, as it turns out, leads to some interesting problems, par-
ticularly in multi-threaded programs ; hence, we’ll see a lot more non-
determinism when we study concurrency in the second part of the book.
5.2 Adding wait() System Call
So far, we haven’t done much: just created a child that prints out a
message and exits. Sometimes, as it turns out, it is quite use ful for a
parent to wait for a child process to ﬁnish what it has been doi ng. This
task is accomplished with the wait() system call (or its more complete
sibling waitpid()); see Figure
5.2 for details.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 74

38 INTERLUDE : P ROCESS API
In this example ( p2.c), the parent process calls wait() to delay its
execution until the child ﬁnishes executing. When the child is done,
wait() returns to the parent.
Adding a wait() call to the code above makes the output determin-
istic. Can you see why? Go ahead, think about it.
(waiting for you to think .... and done)
Now that you have thought a bit, here is the output:
prompt> ./p2
hello world (pid:29266)
hello, I am child (pid:29267)
hello, I am parent of 29267 (wc:29267) (pid:29266)
prompt>
With this code, we now know that the child will always print ﬁr st.
Why do we know that? Well, it might simply run ﬁrst, as before, and
thus print before the parent. However, if the parent does hap pen to run
ﬁrst, it will immediately call wait(); this system call won’t return until
the child has run and exited 2. Thus, even when the parent runs ﬁrst, it
politely waits for the child to ﬁnish running, then wait() returns, and
then the parent prints its message.
5.3 Finally , the exec() System Call
A ﬁnal and important piece of the process creation API is the exec()
system call 3. This system call is useful when you want to run a program
that is different from the calling program. For example, cal ling fork()
in p2.c is only useful if you want to keep running copies of the same
program. However, often you want to run a different program; exec()
does just that (Figure
5.3).
In this example, the child process calls execvp() in order to run the
program wc, which is the word counting program. In fact, it runs wc on
the source ﬁle p3.c, thus telling us how many lines, words, and bytes are
found in the ﬁle:
prompt> ./p3
hello world (pid:29383)
hello, I am child (pid:29384)
29 107 1030 p3.c
hello, I am parent of 29384 (wc:29384) (pid:29383)
prompt>
2There are a few cases where wait() returns before the child exits; read the man page
for more details, as always. And beware of any absolute and un qualiﬁed statements this book
makes, such as “the child will always print ﬁrst” or “U NIX is the best thing in the world, even
better than ice cream.”
3Actually , there are six variants of exec(): execl(), execle(), execlp(), execv(),
and execvp(). Read the man pages to learn more.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 75

INTERLUDE : P ROCESS API 39
1 #include <stdio.h>
2 #include <stdlib.h>
3 #include <unistd.h>
4 #include <string.h>
5 #include <sys/wait.h>
6
7 int
8 main(int argc, char *argv[])
9 {
10 printf("hello world (pid:%d)\n", (int) getpid());
11 int rc = fork();
12 if (rc < 0) { // fork failed; exit
13 fprintf(stderr, "fork failed\n");
14 exit(1);
15 } else if (rc == 0) { // child (new process)
16 printf("hello, I am child (pid:%d)\n", (int) getpid());
17 char *myargs[3];
18 myargs[0] = strdup("wc"); // program: "wc" (word count)
19 myargs[1] = strdup("p3.c"); // argument: file to count
20 myargs[2] = NULL; // marks end of array
21 execvp(myargs[0], myargs); // runs word count
22 printf("this shouldn’t print out");
23 } else { // parent goes down this path (main)
24 int wc = wait(NULL);
25 printf("hello, I am parent of %d (wc:%d) (pid:%d)\n",
26 rc, wc, (int) getpid());
27 }
28 return 0;
29 }
Figure 5.3: p3.c: Calling fork(), wait(), And exec()
If fork() was strange, exec() is not so normal either. What it does:
given the name of an executable (e.g., wc), and some arguments (e.g.,
p3.c), it loads code (and static data) from that executable and over-
writes its current code segment (and current static data) wi th it; the heap
and stack and other parts of the memory space of the program ar e re-
initialized. Then the OS simply runs that program, passing i n any argu-
ments as the argv of that process. Thus, it does not create a new process;
rather, it transforms the currently running program (forme rly p3) into a
different running program ( wc). After the exec() in the child, it is al-
most as if p3.c never ran; a successful call to exec() never returns.
5.4 Why? Motivating the API
Of course, one big question you might have: why would we build
such an odd interface to what should be the simple act of creat ing a new
process? Well, as it turns out, the separation of fork() and exec() is
essential in building a U NIX shell, because it lets the shell run code after
the call to fork() but before the call to exec(); this code can alter the
environment of the about-to-be-run program, and thus enabl es a variety
of interesting features to be readily built.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 76

40 INTERLUDE : P ROCESS API
TIP : G ETTING IT RIGHT (L AMPSON ’ S LAW)
As Lampson states in his well-regarded “Hints for Computer S ystems
Design” [L83], “Get it right. Neither abstraction nor simplicity is a substi-
tute for getting it right.” Sometimes, you just have to do the right thing,
and when you do, it is way better than the alternatives. There are lots
of ways to design APIs for process creation; however, the com bination
of fork() and exec() are simple and immensely powerful. Here, the
UNIX designers simply got it right. And because Lampson so often “ got
it right”, we name the law in his honor.
The shell is just a user program 4. It shows you a prompt and then
waits for you to type something into it. You then type a comman d (i.e.,
the name of an executable program, plus any arguments) into i t; in most
cases, the shell then ﬁgures out where in the ﬁle system the ex ecutable
resides, calls fork() to create a new child process to run the command,
calls some variant of exec() to run the command, and then waits for the
command to complete by calling wait(). When the child completes, the
shell returns from wait() and prints out a prompt again, ready for your
next command.
The separation of fork() and exec() allows the shell to do a whole
bunch of useful things rather easily . For example:
prompt> wc p3.c > newfile.txt
In the example above, the output of the program wc is redirected into
the output ﬁle newfile.txt (the greater-than sign is how said redirec-
tion is indicated). The way the shell accomplishes this task is quite sim-
ple: when the child is created, before calling exec(), the shell closes
standard output and opens the ﬁle newfile.txt. By doing so, any out-
put from the soon-to-be-running program wc are sent to the ﬁle instead
of the screen.
Figure
5.4 shows a program that does exactly this. The reason this redi-
rection works is due to an assumption about how the operating system
manages ﬁle descriptors. Speciﬁcally , UNIX systems start looking for free
ﬁle descriptors at zero. In this case, STDOUT FILENO will be the ﬁrst
available one and thus get assigned when open() is called. Subsequent
writes by the child process to the standard output ﬁle descri ptor, for ex-
ample by routines such as printf(), will then be routed transparently
to the newly-opened ﬁle instead of the screen.
Here is the output of running the p4.c program:
prompt> ./p4
prompt> cat p4.output
32 109 846 p4.c
prompt>
4And there are lots of shells; tcsh, bash, and zsh to name a few. You should pick one,
read its man pages, and learn more about it; all U NIX experts do.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 77

INTERLUDE : P ROCESS API 41
1 #include <stdio.h>
2 #include <stdlib.h>
3 #include <unistd.h>
4 #include <string.h>
5 #include <fcntl.h>
6 #include <sys/wait.h>
7
8 int
9 main(int argc, char *argv[])
10 {
11 int rc = fork();
12 if (rc < 0) { // fork failed; exit
13 fprintf(stderr, "fork failed\n");
14 exit(1);
15 } else if (rc == 0) { // child: redirect standard output to a fil e
16 close(STDOUT_FILENO);
17 open("./p4.output", O_CREAT|O_WRONLY|O_TRUNC, S_IRWXU );
18
19 // now exec "wc"...
20 char *myargs[3];
21 myargs[0] = strdup("wc"); // program: "wc" (word count)
22 myargs[1] = strdup("p4.c"); // argument: file to count
23 myargs[2] = NULL; // marks end of array
24 execvp(myargs[0], myargs); // runs word count
25 } else { // parent goes down this path (main)
26 int wc = wait(NULL);
27 }
28 return 0;
29 }
Figure 5.4: p4.c: All Of The Above With Redirection
You’ll notice (at least) two interesting tidbits about this output. First,
when p4 is run, it looks as if nothing has happened; the shell just pri nts
the command prompt and is immediately ready for your next com mand.
However, that is not the case; the program p4 did indeed call fork() to
create a new child, and then run the wc program via a call to execvp().
You don’t see any output printed to the screen because it has b een redi-
rected to the ﬁle p4.output. Second, you can see that when we cat the
output ﬁle, all the expected output from running wc is found. Cool, right?
UNIX pipes are implemented in a similar way , but with the pipe()
system call. In this case, the output of one process is connec ted to an in-
kernel pipe (i.e., queue), and the input of another process is connected
to that same pipe; thus, the output of one process seamlessly is used as
input to the next, and long and useful chains of commands can b e strung
together. As a simple example, consider the looking for a wor d in a ﬁle,
and then counting how many times said word occurs; with pipes and the
utilities grep and wc, it is easy – just type grep foo file | wc -l
into the command prompt and marvel at the result.
Finally , while we just have sketched out the process API at a high level,
there is a lot more detail about these calls out there to be lea rned and
digested; we’ll learn more, for example, about ﬁle descript ors when we
talk about ﬁle systems in the third part of the book. For now , s ufﬁce it
to say that the fork()/exec() combination is a powerful way to create
and manipulate processes.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 78

42 INTERLUDE : P ROCESS API
ASIDE : RTFM – R EAD THE MAN PAGES
Many times in this book, when referring to a particular syste m call or
library call, we’ll tell you to read the manual pages , or man pages for
short. Man pages are the original form of documentation that exist on
UNIX systems; realize that they were created before the thing cal led the
web existed.
Spending some time reading man pages is a key step in the growt h of
a systems programmer; there are tons of useful tidbits hidde n in those
pages. Some particularly useful pages to read are the man pag es for
whichever shell you are using (e.g., tcsh, or bash), and certainly for any
system calls your program makes (in order to see what return v alues and
error conditions exist).
Finally , reading the man pages can save you some embarrassment. When
you ask colleagues about some intricacy of fork(), they may simply
reply: “RTFM.” This is your colleagues’ way of gently urging you to Read
The Man pages. The F in RTFM just adds a little color to the phra se...
5.5 Other Parts of the API
Beyond fork(), exec(), and wait(), there are a lot of other inter-
faces for interacting with processes in U NIX systems. For example, the
kill() system call is used to send signals to a process, including direc-
tives to go to sleep, die, and other useful imperatives. In fa ct, the entire
signals subsystem provides a rich infrastructure to deliver external events
to processes, including ways to receive and process those si gnals.
There are many command-line tools that are useful as well. Fo r exam-
ple, using the ps command allows you to see which processes are run-
ning; read the man pages for some useful ﬂags to pass to ps. The tool
top is also quite helpful, as it displays the processes of the sys tem and
how much CPU and other resources they are eating up. Humorous ly ,
many times when you run it, top claims it is the top resource hog; per-
haps it is a bit of an egomaniac. Finally , there are many diffe rent kinds of
CPU meters you can use to get a quick glance understanding of t he load
on your system; for example, we always keep MenuMeters (from Raging
Menace software) running on our Macintosh toolbars, so we ca n see how
much CPU is being utilized at any moment in time. In general, t he more
information about what is going on, the better.
5.6 Summary
We have introduced some of the APIs dealing with U NIX process cre-
ation: fork(), exec(), and wait(). However, we have just skimmed
the surface. For more detail, read Stevens and Rago [SR05], o f course,
particularly the chapters on Process Control, Process Rela tionships, and
Signals. There is much to extract from the wisdom therein.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 79

INTERLUDE : P ROCESS API 43
References
[C63] “A Multiprocessor System Design”
Melvin E. Conway
AFIPS ’63 Fall Joint Computer Conference
New York, USA 1963
An early paper on how to design multiprocessing systems; may be the ﬁrst place the term fork() was
used in the discussion of spawning new processes.
[DV66] “Programming Semantics for Multiprogrammed Comput ations”
Jack B. Dennis and Earl C. Van Horn
Communications of the ACM, V olume 9, Number 3, March 1966
A classic paper that outlines the basics of multiprogrammed computer systems. Undoubtedly had great
inﬂuence on Project MAC, Multics, and eventually UNIX.
[L83] “Hints for Computer Systems Design”
Butler Lampson
ACM Operating Systems Review, 15:5, October 1983
Lampson’s famous hints on how to design computer systems. Y o u should read it at some point in your
life, and probably at many points in your life.
[SR05] “Advanced Programming in the U NIX Environment”
W. Richard Stevens and Stephen A. Rago
Addison-Wesley , 2005
All nuances and subtleties of using UNIX APIs are found herein. Buy this book! Read it! And most
importantly, live it.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

