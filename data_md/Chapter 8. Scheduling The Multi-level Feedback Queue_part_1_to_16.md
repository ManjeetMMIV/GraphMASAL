# Document: Chapter 8. Scheduling The Multi-level Feedback Queue (Pages 1 to 16)

## Page 1

8: Scheduling:
The Multi-Level Feedback Queue
Operating System: Three Easy Pieces
1Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 2

No more Oracle
 Finally let’s relax our final assumption - that the scheduler knows the   
length of each job. 
 How can we build an approach that behaves like SJF/STCF without     
such a priori knowledge 
 Simultaneously how can we incorporate some of the ideas we have    
seen with the RR scheduler so that response time is also quite good? 
2Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 3

Multi-Level Feedback Queue (MLFQ)
 A Scheduler that learns from the past to predict the future.
 Objective:
 Minimize response time for interactive jobs
 Optimize turnaround time without a priori knowledge of job length.
3Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 4

MLFQ: Basic Rules
 MLFQ has a number of distinct queues.
 Any time a job that is ready to run is in one of the queues 
 Each queues is assigned a different priority level.
 Uses priority to decide which job should run at given time.
 A job on a higher queue is chosen to run.
 Use round-robin scheduling among jobs in the same queue
4
Rule 1: If Priority(A) > Priority(B), A runs (B doesn’t).
Rule 2: If Priority(A) = Priority(B), A & B run in RR.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 5

MLFQ: Basic Rules (Cont.)
 How to know how to set priority?
 MLFQ varies the priority of a job based on its observed behavior.
 Example:
 A job repeatedly relinquishes the CPU while waiting IOs → Keep its priority 
high
 A job uses the CPU intensively for long periods of time → Reduce its 
priority.
5Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 6

MLFQ Example
6
Q8
Q7
Q6
Q5
Q4
Q3
Q2
Q1
[High Priority]
[Low Priority]
A B
C
D
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 7

MLFQ: How to Change Priority
 MLFQ priority adjustment algorithm:
 Rule 3: When a job enters the system, it is placed at the highest priority
 Rule 4a: If a job uses up an entire time slice while running, its priority is 
reduced (i.e., it moves down on queue).
 Rule 4b: If a job gives up the CPU before the time slice is up, it stays at 
the same priority level
7
In this manner, MLFQ approximates SJF
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 8

Example 1: A Single Long-Running Job
 A three-queue scheduler with time slice 10ms
8
0 50 100 150 200
Q2
Q1
Q0
Long-running Job Over Time (msec)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 9

Example 2: Along Came a Short Job
 Preemption:
 Job A: A long-running CPU-intensive job
 Job B: A short-running interactive job (20ms runtime)
 A has been running for some time, and then B arrives at time T=100.
9
0 50 100 150 200
Q2
Q1
Q0
B:
A: 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 10

Example 3: What About I/O?
 Assumption:
 Job A: A long-running CPU-intensive job
 Job B: An interactive job that need the CPU only for 1ms before 
performing an I/O
10
A Mixed I/O-intensive and CPU-intensive Workload (msec)
0 50 100 150 200
Q2
Q1
Q0
B:
A: 
The MLFQ approach keeps an interactive job at the highest priority
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 11

Problems with the Basic MLFQ
 Starvation
 If there are “too many” interactive jobs in the system.
 Lon-running jobs will never receive any CPU time.
 Game the scheduler
 After running 99% of a time slice, issue an I/O operation.
 The job gain a higher percentage of CPU time.
 A program may change its behavior over time.
 CPU bound process → I/O bound process
11Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 12

The Priority Boost
 Rule 5: After some time period S, move all the jobs (haven’t been 
scheduled) in the system to the topmost queue.
 Example:
 A long-running job(A) with two short-running interactive job(B, C)
12
B:A: C:
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur


## Page 13

Better Accounting
 How to prevent gaming of our scheduler?
 Solution:
 Rule 4 (Rewrite Rules 4a and 4b): Once a job uses up its time allotment at 
a given level (regardless of how many times it has given up the CPU), its 
priority is reduced(i.e., it moves down on queue).
13
0 50 100 150 200
Q2
Q1
Q0
0 50 100 150 200
Q2
Q1
Q0
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 14

Tuning MLFQ And Other Issues
 The high-priority queues → Short time slices
 E.g., 10 or fewer milliseconds
 The Low-priority queue → Longer time slices
 E.g., 100 milliseconds
14
0 50 100 150 200
Q2
Q1
Q0
Lower Priority, Longer Quanta
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 15

The Solaris MLFQ implementation
 For the Time-Sharing scheduling class (TS)
 60 Queues
 Slowly increasing time-slice length
 The highest priority: 20msec
 The lowest priority: A few hundred milliseconds
 Priorities boosted around every 1 second or so.
15Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 16

MLFQ: Summary
 The refined set of MLFQ rules:
 Rule 1: If Priority(A) > Priority(B), A runs (B doesn’t).
 Rule 2: If Priority(A) = Priority(B), A & B run in RR.
 Rule 3: When a job enters the system, it is placed at the highest priority.
 Rule 4: Once a job uses up its time allotment at a given level (regardless 
of how many times it has given up the CPU), its priority is reduced(i.e., it 
moves down on queue).
 Rule 5: After some time period S, move all the jobs in the system to the 
topmost queue.
16Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

