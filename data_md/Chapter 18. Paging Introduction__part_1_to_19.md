# Document: Chapter 18. Paging Introduction_ (Pages 1 to 19)

## Page 1

18. Paging: Introduction
Operating System: Three Easy Pieces
1

## Page 2

Review
 Segmentation chops memory into variable sized segments (code, stack, 
heap, etc.)
 Problems: 
 free-space management is not easy
 Fragmentation: Free memory is too small and scattered and thus can’t be 
usefully allocated
 Types of fragmentation
 External: Visible to allocator (e.g., OS)
 Internal: Visible to requester
2
useful
free
Allocated to requester
Internal
Segment A
Segment C
Segment D
Segment B
Segment E
No contiguous s
pace!
External
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 3

Concept of Paging
 Paging splits up address space into fixed-size unit called a 
page.
 With paging, physical memory is also split into some 
number of pages called a page frame.
3
Process 1 Process 2
Logical View
Physical View
Process 3
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 4

Example: A Simple Paging
 128-byte physical memory with 16 bytes page frames
 64-byte address space with 16 bytes pages
4
0
16
32
48
64
(page 0 of                            
the address space)
(page 1)
(page 2)
(page 3)
A Simple 64-byte Address Space
0
16
reserved for OS
page 3 of AS
(unused)
page 0 of AS
(unused)
page 2 of AS
64-Byte Address Space Placed In Physical Memory
(unused)
page 1 of AS
32
48
64
80
96
112
128
page frame 0 of                           
physical memory
page frame 1
page frame 2
page frame 3
page frame 4
page frame 5
page frame 6
page frame 7
Note: The page in address space and the page 
frame in physical memory are of same size
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 5

Address Translation
 Two components in the virtual address
 VPN: virtual page number
 Offset: offset within the page
 Example: virtual address 21 in 64-byte address space
5
Va5 Va4 Va3 Va2 Va1 Va0
VPN offset
0 1 0 1 0 1
VPN offset
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 6

Example: Address Translation
 The virtual address 21 in 64-byte address space
6
0 1 0 1 0 1
VPN offset
1 1 0 1 0 1
PFN offset
1
Virtual
Address
Physical
Address
Address 
Translation
No addition needed; just append bits correctly…
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 7

Quiz: Address Format
 Given known page size, how many bits are needed in address to
specify offset in page?
7
Page Size Low Bits (offset)
16 bytes 4
1 KB 10
1 MB 20
512 bytes 9
4 KB 12
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 8

Quiz: Address Format
 Given number of bits in virtual address and bits for offset, 
how many bits for virtual page number?
8
Page Size Low Bits
(offset)
Virt Addr Bits High Bits
(vpn)
16 bytes 4 10 6
1 KB 10 20 10
1 MB 20 32 12
512 bytes 9 16 5
4 KB 12 32 20
Correct?
7
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 9

Quiz: Address Format
 Given number of bits for vpn, how many virtual pages can be there in 
an address space?
9
Page Size Low Bits
(offset)
Virt Addr Bits High Bits
(vpn)
16 bytes 4 10 6
Virt Pages
1 KB 10 20 10
1 MB 20 32 12
512 bytes 9 16 7
4 KB 12 32 20
64
1 K
4 K
128
1 MB
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 10

Virtual => Physical PAGE Mapping
 What data structure is good?
 Simplest data structure for page table: a linear array
 The OS indexes the array by VPN, and looks up the page-table entry.
 Per process Page table is needed to translate the virtual address to physical 
address
10
Virt Mem
Phys Mem
P2 P3P1
Big array: pagetable
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 11

Virtual => Physical PAGE Mapping
11
Virt Mem
Phys Mem
P2 P3P1
Page Tables:
P1
3
1
7
10
P2
0
4
2
6
P3
8
5
9
11
Q: Fill in Page Table En
try for P3
0 1 2 3 4 5 6 7 8 9 10 11
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 12

How big is a typical page table?
 Assume 32-bit address space with 4-KB pages and 4 byte entries
 Answer: 2 ^ (32 - log(4KB)) * 4 = 4 MB 
 Page table size = Num entries * size of each entry
 Num entries = num virtual pages = 2^(bits for vpn)
 Bits for vpn = 32– number of bits for page offset
= 32 – lg(4KB) = 32 – 12 = 20
 Num entries = 2^20 = 1 MB
 Page table size = Num entries * 4 bytes = 4 MB
 That is for each page table. Imagine there are 100 processes running: would  
need 400MB of memory just for all those address translations!
12Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 13

Where Are Page Tables Stored?
 Page tables can get awfully large: so we don’t keep any special on-
chip hardware in the MMU to store the page table
 Instead, Page tables for each process are stored in memory and its 
base address is stored in process control block (PCB) of process
 What happens on a context-switch?
 Change contents of page table base register to newly scheduled 
process
 Save old page table base register in PCB of descheduled process
13Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 14

Example: Page Table in Kernel Physical Memory
 Page table stored in the kernel-owned physical memory
14
0
16
page table
3 7 5 2
page 3 of AS
(unused)
page 0 of AS
(unused)
page 2 of AS
Physical Memory
(unused)
page 1 of AS
32
48
64
80
96
112
128
page frame 0 of physical memory
page frame 1
page frame 2
page frame 3
page frame 4
page frame 5
page frame 6
page frame 7
0
16
32
48
64
(page 0 of                            
the address space)
(page 1)
(page 2)
(page 3)
A Simple 64-byte Address Space
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 15

What Is In The Page Table?
 Each PTE contains PFN (physical frame number) and few other bits 
 Valid bit: is this page used by process? 
 Protection bits: read/write permissions 
 Present bit: is this page in memory or swapped to disk? (more later) 
 Dirty bit: has this page been modified? 
 Accessed bit: has this page been recently accessed?
15
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
PFN
G
PAT
D
A
PCD
PWT
U/S
R/W
P
An x86 Page Table Entry(PTE)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 16

What happens on memory access?
 For every memory request, MMU translates VA to PA by:
 First, accessing memory to read page table entry 
 Translate VA to PA 
 Then, accessing memory to fetch code/data
 For every memory reference, paging requires the OS to perform one 
extra memory reference.
17Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 17

Advantages of Paging
 Flexibility: Any page can be placed in any frame in physical memory
 No external fragmentation
 Grow segments as needed
 Don’t need assumption how heap and stack grow.
 Simplicity: ease of free-space management
 Alloc: No searching for suitable free space
 Free: Doesn’t have to coallesce with adjacent free space
 Simple to swap-out portions of memory to disk (later lecture)
 Page size matches disk block size
 Can run process when some pages are on disk
 Add “present” bit to PTE
18Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 18

Disadvantages of Paging
 Too slow - Doubles memory references !
 Solution: Add cache for VA-PA mappings (future lecture)
 Storage for page tables may be substantial 
 Requires PTE for all pages in address space, even if page not allocated
 Page tables must be allocated contiguously in memory
 Solution: Combine paging and segmentation (future lecture)
 Internal fragmentation: Page size may not match size needed by 
process. Wasted memory grows with larger pages
19Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 19

 Disclaimer: This slide set has been adapted from the initial lecture slides for Operating 
System course in Computer Science Dept. at Hanyang University. This lecture slide set is 
for OSTEP book written by Remzi and Andrea at University of Wisconsin.
23Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

