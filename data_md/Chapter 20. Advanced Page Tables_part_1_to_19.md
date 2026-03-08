# Document: Chapter 20. Advanced Page Tables (Pages 1 to 19)

## Page 1

20. Paging: Smaller Tables
Operating System: Three Easy Pieces
1

## Page 2

 We usually have one page table for every process in the system.
 Assume that 32-bit address space with 4KB pages and 4-byte page-table 
entry.
Paging: Linear Tables
2
Page table size = 
𝟐𝟑𝟐
𝟐𝟏𝟐 ∗ 𝟒𝑩𝒚𝒕𝒆 = 𝟒𝑴𝑩𝐲𝐭𝐞
Page 0
Page 1
Page 2
Physical Memory
Page n
…
entry
…
entry
entry
entry
Page Table of
Process A
4B 4KB
Page table are too big and thus consume too much memory. 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 3

 Page table are too big and thus consume too much memory. 
 Assume that 32-bit address space with 16KB pages and 4-byte page-table 
entry.
Paging: Smaller Tables
3
Page 0
Page 1
Page 2
Physical Memory
Page n
…
entry
…
entry
entry
entry
Page Table of
Process A
4B 16KB
𝟐𝟑𝟐
𝟐𝟏𝟔 ∗ 𝟒 = 𝟏𝑴𝑩 per page table
Big pages lead to internal fragmentation.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 4

 Single page table for the entries of the address space of a process.
Problem
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
4
code
heap
stack
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
Allocate
Virtual Address
Space
Physical Memory
PFN valid prot present dirty
10 1 r-x 1 0
- 0 - - -
- 0 - - -
- 0 - - -
15 1 rw- 1 1
… … … … …
- 0 - - -
3 1 rw- 1 1
23 1 rw- 1 1
A Page Table For 16KB Address Space
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 5

 Most of the page table is unused, full of invalid entries.
Problem
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
5
code
heap
stack
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
Allocate
Virtual Address
Space
Physical Memory
PFN valid prot present dirty
10 1 r-x 1 0
- 0 - - -
- 0 - - -
- 0 - - -
15 1 rw- 1 1
… … … … …
- 0 - - -
3 1 rw- 1 1
23 1 rw- 1 1
A Page Table For 16KB Address Space
How did OS handled sparse address space?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 6

Solutions
 Use more complex page tables, instead of just linear big array
 Approaches: 
1. Inverted Pagetables
2. Segmented Pagetables
3. Multi-level Pagetables
6Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 7

Inverted Page Tables
 Keeping a single page table that has an entry for each physical page 
of the system.
 The entry tells us which process is using this page, and which virtual 
page of that process maps to this physical page.
 Naïve approach: 
Search through data structure <ppn, vpn+asid> to find match
 Better: Find possible matches entries by hashing vpn+asid
 Smaller number of entries to search for exact match
 Managing inverted page table requires software-controlled TLB
 For hardware-controlled TLB, need well-defined, simple approach
7Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 8

Hybrid Approach: Paging and Segments 
 Divide address space into segments (code, heap, stack)
 Segments can be variable length
 Divide each segment into fixed-sized pages. Logical address gets 
divided into three portions
8
Seg VPN Offset
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9   8   7  6  5   4   3  2  1   0 
Seg value Content
00 unused segment
01 code
10 heap
11 stack
32-bit Virtual address space with 4KB pages
 Each segment has a page table.
 The base register for each of these 
segments contains the physical 
address of a linear page table for that 
segment.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 9

 Hybrid Approach is not without problems.
 If we have a large but sparsely-used heap, we can still end up with a lot of 
page table waste.
 Causing external fragmentation to arise again.
 Main problem: Must allocate each page table contiguously
Problem of Hybrid Approach
9Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 10

Multi-level Page Tables 
 Page the Page Tables - Creates multiple levels of page tables.
 If an entire page of page-table entries is invalid, don’t allocate that page 
of the page table at all.
 To track whether a page of the page table is valid, use a new structure at 
the outer level called page directory. 
10
outer page
(8 bits)
inner page
(10 bits) page offset (12 bits)
30-bit address:
base of page directory
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 11

Multi-level Page Tables: Page directory
11
201PTBR
Linear Page Table
Multi-level Page Table
valid
prot PFN
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
PFN201PFN202PFN203
1 201
0 -
0 -
1 204
The Page Directory
PFN200
validPFN
1 rx 12
1 rx 13
0 - -
1 rw 100
PFN201
valid
prot PFN
[Page 1 of PT:Not Allocated]
[Page 2 of PT: Not Allocated]
0 - -
0 - -
1 rw 86
1 rw 15
PFN204
200PDBR
PFN204
The page directory 
contains one entry per 
page of the page table
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 12

 To understand the idea behind multi-level page tables better, let’s do 
an example.
A Detailed Multi-Level Example
12
Flag Detail
Address space 16 KB
Page size 64 byte 
Virtual address 14 bit
VPN 8 bit
Offset 6 bit
Page table entry 28(256)
code
code
(free)
(free)
heap
heap
(free)
(free)
stack
stack A 16-KB Address Space With 64-byte Pages
0000 0000
0000 0001
...
1111 1111
13 12 11 10 9 8 7 6 5 4 3 2 1 0
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 13

A Detailed Multi-Level Example: Page Directory Idx
 The page directory needs one entry per page of the page table
 it has 16 entries.
 The page-directory entry is invalid → Raise an exception (The access is 
invalid)
13
14-bits Virtual address
13 12 11 10 9 8 7 6 5 4 3 2 1 0
VPN Offset
Page Directory Index
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 14

A Detailed Multi-Level Example: Page Table Idx
 The PDE is valid, we have more work to do.
 To fetch the page table entry(PTE) from the page of the page table 
pointed to by this page-directory entry.
 This page-table index can then be used to index into the page table 
itself.
14
14-bits Virtual address
13 12 11 10 9 8 7 6 5 4 3 2 1 0
VPN Offset
Page Directory Index Page Table Index
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 15

More than Two Level
 In some cases, a deeper tree is possible.
15
30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9  8  7  6  5  4   3   2  1   0 
Flag Detail
Virtual address 30 bit
Page size 512 byte
VPN 21 bit
Offset 9 bit
offsetVPN
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 16

More than Two Level : Page Table Index
 In some cases, a deeper tree is possible.
16
30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9  8  7  6  5  4   3   2  1   0 
offset
Flag Detail
Virtual address 30 bit
Page size 512 byte
VPN 21 bit
Offset 9 bit
Page entry per page 128 PTEs
VPN
log2 128 = 7
Page Table IndexPage Directory Index
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 17

More than Two Level : Page Directory
 If our page directory has 214entries, it spans not one page but 128.
 To remedy this problem, we build a further level of the tree, by 
splitting the page directory itself into multiple pages of the page 
directory.
17
30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9  8  7  6  5  4   3   2  1   0 
offsetVPN
PD Index 0 PD Index 1 Page Table Index
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 18

Multi-level Page Tables: Advantage & Disadvantage
 Advantage
 Only allocates page-table space in proportion to the amount of address 
space you are using.
 The OS can grab the next free page when it needs to allocate or grow a 
page table.
 Disadvantage
 Multi-level table is a small example of a time-space trade-off.
 Complexity.
18Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 19

 Disclaimer: This slide set has been adapted from the initial lecture slides for Operating 
System course in Computer Science Dept. at Hanyang University. This lecture slide set is 
for OSTEP book written by Remzi and Andrea at University of Wisconsin.
19Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

