# Document: operating_systems_three_easy_pieces (Pages 641 to 643)

## Page 641

Cruces
How To Account For Disk Rotation Costs, 413
How To Add Locks To Data Structures, 311
How To Allocate And Manage Memory, 119
How To A void Spinning,304
How To A void The Costs Of Polling, 392
How To A void The Curse Of Generality, 245
How To Build A Device-neutral OS, 395
How To Build A Distributed File System, 560
How To Build A Lock, 293
How To Build Concurrent Servers Without Threads, 373
How To Build Correct Concurrent Programs, 10
How To Build Systems That Work When Components Fail, 543
How To Communicate With Devices, 394
How To Create And Control Processes, 35
How To Create And Control Threads, 279
How To Deal With Deadlock, 363
How To Deal With Load Imbalance, 101
How To Decide Which Page To Evict, 227
How To Deﬁne A Stateless File Protocol, 563
How To Design A Scalable File Protocol, 578
How To Design TLB Replacement Policy, 192
How To Develop Scheduling Policy, 59
How To Efﬁciently And Flexibly Virtualize Memory, 129
How To Efﬁciently Virtualize The CPU With Control, 45
How To Ensure Data Integrity, 527
How To Gain Control Without Cooperation, 51
How To Go Beyond Physical Memory, 217
How To Handle Common Concurrency Bugs, 359
How To Handle Disk Starvation, 413
How To Handle Latent Sector Errors, 529
How To Handle Lost Writes, 535
How To Handle Misdirected Writes, 534
How To Implement A Simple File System, 461
605

## Page 642

606 HOW TO WAIT FOR A C ONDITION
How To Implement An LRU Replacement Policy, 238
How To Integrate I/O Into Systems, 389
How To Lower PIO Overheads, 394
How To Make A Large, Fast, Reliable Disk, 421
How To Make All Writes Sequential Writes, 512
How To Make Page Tables Smaller, 201
How To Manage A Persistent Device, 441
How To Manage Free Space, 154
How To Manage TLB Contents On A Context Switch, 191
How To Organize On-disk Data To Improve Performance, 480
How To Perform Restricted Operations, 46
How To Preserve Data Integrity Despite Corruption, 530
How To Provide Support For Synchronization, 272
How To Provide The Illusion Of Many CPUs, 25
How To Reduce File System I/O Costs, 473
How To Regain Control Of The CPU, 50
How To Schedule Jobs On Multiple CPUs, 94
How To Schedule Without Perfect Knowledge, 71
How To Share The CPU Proportionally, 83
How To Speed Up Address Translation, 183
How To Store And Access Data On Disk, 403
How To Store Data Persistently, 12
How To Support A Large Address Space, 141
How To Update The Disk Despite Crashes, 491
How To Use Semaphores, 341
How To Virtualize Memory, 112
How To Virtualize Memory Without Segments, 169
How To Virtualize Resources, 4
How To Wait For A Condition, 326
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 643

This book was typeset using the amazing L ATEX typesetting system and
the wonderful memoir book-making package. A heartfelt thank you to
the legions of programmers who have contributed to this powe rful tool
over the many years of its development.
All of the graphs and ﬁgures in the book were generated using a Python-
based version of zplot, a simple and useful tool developed by R. Arpaci-
Dusseau to generate graphs in PostScript. The zplot tool arose after
many years of frustration with existing graphing tools such as gnuplot
(which was limited) and ploticus (which was overly complex though
admittedly quite awesome). As a result, R. A-D ﬁnally put his years of
study of PostScript to good use and developed zplot.

