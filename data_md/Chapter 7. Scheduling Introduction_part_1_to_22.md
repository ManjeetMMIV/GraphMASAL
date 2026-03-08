# Document: Chapter 7. Scheduling Introduction (Pages 1 to 22)

## Page 1

Scheduling: Introduction
Chapter 7 of Operating System: Three Easy Pieces
1Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 2

Review: Process State Transitions
 How to transition? (“mechanism”) – Previous lectures
 When to transition? (“policy”) – on context switch OS scheduler decides 
which process to run next, from set of ready processes
2
Running Ready
Blocked
Descheduled
Scheduled
I/O: doneI/O: initiate
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 3

Exercise
 Think of examples in life where scheduling is involved
3Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 4

Scheduling: Outline
 How should we develop a basic framework for thinking about           
scheduling policies? 
 What metrics are important? 
 What are the key assumptions? 
 What basic approaches have been used in different computer systems
4Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 5

Scheduling: Terminology
 Workload: set of job descriptions (arrival time, run time)
 Job: current CPU burst (CPU time used in one stretch) of a process
 Performance Metrics: measurement of scheduling quality
 Turnaround time: The amount of time taken to execute the particular job
Turnaround time = (completion time - arrival time)
 Waiting Time: The amount of time a process has been waiting in the ready 
queue. Waiting Time = (turnaround time - burst time)
 Response time: The amount of time from when a request was submitted   
until the first response is produced. Response Time = (the time at which a  
process get the CPU first time - arrival time)
 Throughput: How many jobs complete per unit of time
 Fairness: All jobs get same amount of CPU over some time interval
5Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 6

Exercise
 Take a real life scenario/example and try to explain these metrics in    
that context. 
6Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 7

Scheduling: A beginning
 Workload assumptions:
1. Each job runs for the same amount of time.
2. All jobs arrive at the same time.
3. All jobs only use the CPU (i.e., they perform no I/O).
4. The run-time of each job is known.
 Don’t worry… we will relax them as we move along
7Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 8

Scheduling Metrics
 Performance metric: Turnaround time
 The time at which the job completes minus the time at which the job 
arrived in the system.
8
𝑻𝒕𝒖𝒓𝒏𝒂𝒓𝒐𝒖𝒏𝒅 = 𝑻𝒄𝒐𝒎𝒑𝒍𝒆𝒕𝒊𝒐𝒏 − 𝑻𝒂𝒓𝒓𝒊𝒗𝒂𝒍
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 9

First In, First Out (FIFO)
 First Come, First Served (FCFS)
 Very simple and easy to implement
 Example: three jobs arrive at t=0 in the order A,B,C
 Each job runs for 10 seconds.
 Gantt chart below : Illustrates how jobs are scheduled over time on a CPU
9
0 20 40 60 80 100 120
Time (Second)
A B C
𝑨𝒗𝒆𝒓𝒂𝒈𝒆 𝒕𝒖𝒓𝒏𝒂𝒓𝒐𝒖𝒏𝒅 𝒕𝒊𝒎𝒆 = 𝟏𝟎 + 𝟐𝟎 + 𝟑𝟎
𝟑 = 𝟐𝟎 𝒔𝒆𝒄
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 10

Why FIFO is not that great? 
 Let’s relax assumption 1: Each job no longer runs for the same 
amount of time.
 Example: three jobs arrive at t=0 in the order A,B,C
 A runs for 100 seconds, B and C run for 10 each.
 Draw the Gantt chart and calc. Avg. turnaround time
10
0 20 40 60 80 100 120
Time (Second)
A B C
𝑨𝒗𝒆𝒓𝒂𝒈𝒆 𝒕𝒖𝒓𝒏𝒂𝒓𝒐𝒖𝒏𝒅 𝒕𝒊𝒎𝒆 = 𝟏𝟎𝟎 + 𝟏𝟏𝟎 + 𝟏𝟐𝟎
𝟑 = 𝟏𝟏𝟎 𝒔𝒆𝒄
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 11

FIFO problem: Convoy Effect
 Think of a similar scenario you may have encountered personally
 What do you do in that situation?
11
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 12

Shortest Job First (SJF)
 Run the shortest job first, then the next shortest, and so on
 Non-preemptive scheduler
 Same example: three jobs arrive at t=0 in the order A,B,C 
 A runs for 100 seconds, B and C run for 10 each.
 Provably optimal when all processes arrive together
12
0 20 40 60 80 100 120
Time (Second)
AB C
𝑨𝒗𝒆𝒓𝒂𝒈𝒆 𝒕𝒖𝒓𝒏𝒂𝒓𝒐𝒖𝒏𝒅 𝒕𝒊𝒎𝒆 = 𝟏𝟎 + 𝟐𝟎 + 𝟏𝟐𝟎
𝟑 = 𝟓𝟎 𝒔𝒆𝒄
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 13

SJF with Late Arrivals from B and C
 Let’s relax assumption 2: Jobs can arrive at any time.
 Example: A arrives at t=0 and needs to run for 100 seconds.
 B and C arrive at t=10 and each need to run for 10 seconds
 SJF is non- preemptive, so short jobs can still get stuck behind long ones
13
𝑨𝒗𝒆𝒓𝒂𝒈𝒆 𝒕𝒖𝒓𝒏𝒂𝒓𝒐𝒖𝒏𝒅 𝒕𝒊𝒎𝒆 = 𝟏𝟎𝟎 + 𝟏𝟏𝟎 − 𝟏𝟎 + (𝟏𝟐𝟎 − 𝟏𝟎)
𝟑 = 𝟏𝟎𝟑. 𝟑𝟑 𝒔𝒆𝒄
0 20 40 60 80 100 120
Time (Second)
A B C
[B,C arrive]
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 14

Shortest Time-to-Completion First (STCF)
 Add preemption to SJF
 Also knows as Preemptive Shortest Job First (PSJF)
 When a new job enters the system:
 Preempts running task if its remaining CPU burst is more than that of new 
arrival
14Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 15

Shortest Time-to-Completion First (STCF)
 Example:
 A arrives at t=0 and needs to run for 100 seconds.
 B and C arrive at t=10 and each need to run for 10 seconds
 Draw Gantt chart and calc. avg. TT
15
𝑨𝒗𝒆𝒓𝒂𝒈𝒆 𝒕𝒖𝒓𝒏𝒂𝒓𝒐𝒖𝒏𝒅 𝒕𝒊𝒎𝒆 = (𝟏𝟐𝟎 − 𝟎) + 𝟐𝟎 − 𝟏𝟎 + (𝟑𝟎 − 𝟏𝟎)
𝟑 = 𝟓𝟎 𝒔𝒆𝒄
0 20 40 60 80 100 120
Time (Second)
A B C
[B,C arrive]
A
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 16

New scheduling metric
 Given our new assumption, STCF is provably optimal. Hence used in 
early batch processing computing systems
 With advent of Time sharing demand for interactive performance 
came
 Response time: The time from when the job arrives to the first time 
it is scheduled.
 STCF and related disciplines are not particularly good for response time.
16
𝑻𝒓𝒆𝒔𝒑𝒐𝒏𝒔𝒆 = 𝑻𝒇𝒊𝒓𝒔𝒕𝒓𝒖𝒏 − 𝑻𝒂𝒓𝒓𝒊𝒗𝒂𝒍
How can we build a scheduler that is 
sensitive to response time?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 17

Round Robin (RR) Scheduling
 Time slicing Scheduling
 Run a job for a time slice and then switch to the next job in the run 
queue until the jobs are finished.
 Time slice is sometimes called a scheduling quantum.
 It repeatedly does so until the jobs are finished.
 The length of a time slice must be a multiple of the timer-interrupt period.
17
RR is fair, but performs poorly on metrics
such as turnaround time
Performance and fairness are often at odds in scheduling
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 18

RR Scheduling Example
 A, B and C arrive at the same time.
 They each wish to run for 5 seconds.
18
0 5 10 15 20 25 30
Time (Second)
A B C
SJF (Bad for Response Time)
0 5 10 15 20 25 30
Time (Second)
A B C
RR with a time-slice of 1sec (Good for Response Time)
A B CA B CA B CA B C
𝑇𝑎𝑣𝑒𝑟𝑎𝑔𝑒 𝑟𝑒𝑠𝑝𝑜𝑛𝑠𝑒 = 0 + 5 + 10
3 = 5𝑠𝑒𝑐
𝑇𝑎𝑣𝑒𝑟𝑎𝑔𝑒 𝑟𝑒𝑠𝑝𝑜𝑛𝑠𝑒 = 0 + 1 + 2
3 = 1𝑠𝑒𝑐
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 19

The length of the time slice is critical.
 The shorter time slice
 Better response time
 The cost of context switching will dominate overall performance.
 The longer time slice
 Amortize the cost of switching
 Worse response time
19
Deciding on the length of the time slice presents
a trade-off to a system designer
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 20

Incorporating I/O
 Let’s relax assumption 3: All programs perform I/O
 Example:
 A and B need 50ms of CPU time each.
 A runs for 10ms and then issues an I/O request
 I/Os each take 10ms
 B simply uses the CPU for 50ms and performs no I/O
 The  scheduler runs A first, then B after
20Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 21

Incorporating I/O (Cont.) with STCF
21
0 20 40 60 80 100 120
Time (msec)
A B
Poor Use of Resources
140
A A A A B B B B
0 20 40 60 80 100 120
Time (msec)
A B
140
A A A AB B B B Maximize the 
CPU utilization by 
treating each 10ms 
sub job of A as new 
job
CPU
Disk
CPU
Disk
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 22

Incorporating I/O (Cont.)
 When a job initiates an I/O request.
 The job is blocked waiting for I/O  completion.
 The scheduler should schedule another job on the CPU.
 When the I/O completes
 An interrupt is raised.
 The OS moves the process from blocked back to the ready state.
22Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

