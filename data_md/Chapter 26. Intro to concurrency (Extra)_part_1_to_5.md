# Document: Chapter 26. Intro to concurrency (Extra) (Pages 1 to 5)

## Page 1

Concurrency -doing multiple things at same time by overlapping/interleaving/sharing of resources
one form of concurrency -multi programming by cpu & memory virtualization
overlapping i/o with cpu
sharing cpu by executing multiple process via controlled execution by the OS and providing isolated address/memory space and doing bookkeeping  for them.however, processes are ideal choice for executing logically independent task which require no/little sharing of data
can we go one step further and try to concurrently execute/do multiple tasks within a single program?Questions:Why would we want that?1)what are alternative mechanisms to do that (how)?2)what kind of problems/issues it can lead to?3)what are the possible solutions to those issues using the help OS and H/W4)
Why?
Introduction to Concurrency W24
Tuesday, September 3, 202412:06 PM

## Page 2

Faster execution  -modern system have multiple cpus/cores1)
A complicated program may necessitate doing of multiple taks concurrently . ex OS, note taking SW etc.2)
to avoid blocking of program progress due to IO or slow task. 3)
ex of webserverreads a request from a clienta)parseb)read from the disk -> IOc)send and repeat a) to d)d)
How?
Mechanisms -2 options

## Page 3

launch multiple cooperative processes by  fork() & communicate with each other through some Inter process communication (IPC) mechanism.
1)
shared memory using system calls like shmget()1)
Messag passing -send(), receive()2)
an alternate abstraction -thread : lightweight copy of the process that executes independently2)


## Page 4

T1 T2count++;count++;
load   &count, R11.Increment   R12.store    R1, &count3.
PC     R1 PC    R1 Addr(count)

## Page 5

what is happening here is called data race

