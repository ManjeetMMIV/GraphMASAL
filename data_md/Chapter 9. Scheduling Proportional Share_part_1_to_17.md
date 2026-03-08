# Document: Chapter 9. Scheduling Proportional Share (Pages 1 to 17)

## Page 1

9: Scheduling: Proportional Share
Operating System: Three Easy Pieces
1

## Page 2

Review 
 Thus far, we have examined schedulers designed to optimize perfor
mance
 Minimum response times
 Minimum turnaround times
 MLFQ achieves these goals, but it’s complicated
 Non-trivial to implement
 Challenging to parameterize and tune
 What about a simple algorithm that achieves fairness?
2

## Page 3

Proportional Share Scheduler
 Every job has a weight, and jobs receive a share of the available         
resources proportional to the weight of every job.
 Also referred as Fair-share scheduler
 Guarantee that each job obtain a certain percentage of CPU time.
 Not optimized for turnaround or response time
3Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 4

Lottery scheduling: Basic Concept
 Give processes lottery tickets - whoever wins runs
 The percent of tickets represent the share of a resource that a process 
should receive
 Higher priority => more tickets
 Example
 There are two processes, A and B.
 Process A has 75 tickets → receive 75% of the CPU
 Process B has 25 tickets → receive 25% of the CPU
4Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 5

Lottery scheduling (contd)
 The scheduler picks a winning ticket.
 Load the state of that winning process and runs it.
 Example
 There are 100 tickets
 Process A has 75 tickets: 0 ~ 74
 Process B has 25 tickets: 75 ~ 99
5
Scheduler’s winning tickets: 63  85  70  39  76  17  29  41  36  39  10  99  68  83  63
Resulting scheduler: A B A A B B BA A A A A A A A
The longer these two jobs compete,
The more likely they are to achieve the desired percentages.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 6

Random Algorithms
 Advantages?
 Automatically balances CPU time across processes
 Lightweight requiring little per process state (behavior or history) to track. 
 Easy to implement: often avoids strange corner-case behavior, no need to 
manage priority queues etc.
 Random can be quite fast. As long as generating a random number is quick
 Easy to prioritize processes (giving more or less tickets) and priorities can   
change via ticket inflation
 Disadvantages?
 Non deterministic: It occasionally will not deliver the exact right proportion, 
especially over short time scales
6Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 7

Ticket Mechanisms
 Ticket currency
 A user allocates tickets among their own jobs in whatever currency they 
would like.
 The system converts the currency into the correct global value.
 Example
 There are 200 tickets (Global currency)
 Process A has 100 tickets
 Process B has 100 tickets
7
User A → 500 (A’s currency) to A1 → 50 (global currency)
→ 500 (A’s currency) to A2 → 50 (global currency)
User B → 10 (B’s currency) to B1 → 100 (global currency)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 8

Ticket Mechanisms (Cont.)
 Ticket transfer
 A process can temporarily hand off its tickets to another process.
 Ticket inflation
 A process can temporarily raise or lower the number of tickets is owns.
 If any one process needs more CPU time, it can boost its tickets.
8Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 9

Implementation
 Example: There are there processes, A, B, and C.
 Keep the processes in a list:
9
head Job:A
Tix:100
Job:B
Tix:50
Job:C
Tix:250 NULL
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
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 10

Lottery Fairness Study
 There are two jobs.
 Each jobs has the same number of tickets (100).
10
When the job length is not very long,
average unfairness can be quite severe.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 11

Stride Scheduling
 Randomness lets us build a simple and approximately fair scheduler
 But fairness is not guaranteed
 Why not build a deterministic, fair scheduler?
 Stride scheduling
 Each process is given some tickets
 Each process has a stride = a big # / # of tickets
 Example: A large number = 10,000
 Process A has 100 tickets → stride of A is 100
 Process B has 50 tickets → stride of B is 200
 Process C has 250 tickets → stride of C is 40
 Each time a process runs, its pass += stride
 Scheduler chooses process with the lowest pass value to run next
11

## Page 12

Stride Scheduling Example
12
Pass(A)
(stride=100)
Pass(B)
(stride=200)
Pass(C)
(stride=40)
Who Runs?
0
100
100
100
100
100
200
200
200
0
0
200
200
200
200
200
200
200
0
0
0
40
80
120
120
160
200
A
B
C
C
C
A
C
C
…
Note that A, B & C run in exact proportional to their 
share of tickets i.e, 25%, 12.5%, 62.5% respectively
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur
current = remove_min(queue); // pick client with minimum pass
schedule(current); // use resource for quantum
current->pass += current->stride; // compute next pass using stride
insert(queue, current); // put back into the queue

## Page 13

Lingering Issues
 Why choose lottery over stride scheduling?
 Stride schedulers need to store a lot more state
 How does a stride scheduler deal with new processes?
 Pass = 0, it will monopolize CPU until its pass value catches up
 Both schedulers require tickets assignment
 How do you know how many tickets to assign to each process?
 This is an open problem but fortunately in many domains this is not a 
dominant concern. For instance in a virtualized data center (or cloud)
13

## Page 14

Case Study: Linux Schedulers
 O(1) (Used in kernels prior to 2.6.23)
 A Priority-based scheduler
 Implements a version of MLFQ
 140 priority levels, 2 queues (active/inactive) per priority
 Change a process’s priority over time
 Schedule those with highest priority
 Interactivity is a particular focus with RR within each priority level
14

## Page 15

Case Study: Linux Schedulers
 Completely Fair Scheduler (CFS)
 Replaced the O(1) scheduler, in use since 2.6.23
 Moves from MLFQ to Weighted Fair Queuing
 First major OS to use a fair scheduling algorithm
 Very similar to stride scheduling (Deterministic proportional-share)
 Processes ordered by the amount of CPU time they use
 Instead of queues, it uses efficient DS to ensure it has O(log N) runtime
 CFS isn’t actually “completely fair” but Unfairness is bounded O(N)
15

## Page 16

Completely Fair Scheduler (more details)
 As each process runs, it accumulates Virtual runtime (vruntime). CFS  
picks the process with least vruntime.
 Dynamic time slice calculation through control parameters like sched_
latency, min_granularity
 Priorities through weighting – nice values [-20,19]
 Default = 0, +ve values imply lower and –ve imply higher priority
 Used for time slice calculation and also weighted updation of vruntime
 Uses Red-black tree for maintaining list of processes to achieve high 
efficiency and scalability.
16Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 17

Red-Black Process Tree
 Tree organized according to amount of CPU time used by each process
 Jobs that go wake up after long sleep or I/O can monopolize. To avoid 
that, CFS sets the vruntime of that job to the min value found in tree.
17
17
15 25
22 27
• Left-most  
process has 
always use
d the least  
time
• Scheduled 
next
38
• Add the process 
back to the tree
• Rebalance the   
tree

