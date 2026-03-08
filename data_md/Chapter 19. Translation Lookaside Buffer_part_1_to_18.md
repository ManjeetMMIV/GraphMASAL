# Document: Chapter 19. Translation Lookaside Buffer (Pages 1 to 18)

## Page 1

19. Translation Lookaside Buffers
Operating System: Three Easy Pieces
1

## Page 2

Review: Paging
2
P1
P2
P2
P1
PT
P1
0x4000
0x5000
0x6000
0x2000
0x3000
0x1000
0x0000
PT
P1 pagetable1 5 4 …
P2 pagetable6 2 3 …
P2
0x7000
Virtual Physical
0x0800
load 0x0000 load 0x0800
load 0x6000
load 0x1444 load 0x0808
load 0x2444
load 0x1444 load 0x0008
load 0x5444
Assume 4 KB pages
What do we need to know?
Location of page table in memory (ptbr)
ptbr
Size of each page table entry (assume 8 bytes)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 3

Review: Advantages of Paging
 Flexibility: Any page can be placed in any frame in physical memory
 No external fragmentation
 Grow segments as needed
 Don’t need assumption how heap and stack grow.
 Simplicity: free-space management easy as all free pages are equivalent 
 Free: Doesn’t have to coallesce with adjacent free space
 Alloc: No searching for suitable free space
 Simple to swap-out portions of memory to disk (later lecture)
 Page size matches disk block size
 Can run process when some pages are on disk
 Add “present” bit to PTE
3Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 4

Review: Disadvantages of Paging
 Too slow - Doubles memory references !
 Solution: Add cache for VA-PA mappings (todays lecture)
 Internal fragmentation: Page size may not match size needed by 
process. Wasted memory grows with larger pages
 Storage for page tables may be big/substantial (future lecture)
 Requires PTE for all pages in address space, even if page not allocated
 Page tables must be allocated contiguously in memory
 Solution: Multi-level PT’s, Combine paging and segmentation etc.
4Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 5

Example: Array Iterator
int sum = 0;
for (i=0; i<N; i++){
sum += a[i];
}
Assume ‘a’ starts at 0x3000
Ignore instruction fetches
load 0x3000
load 0x3004
load 0x3008
load 0x300C
…
What virtual addresses?
load 0x100C
load 0x7000
load 0x100C
load 0x7004
load 0x100C
load 0x7008
load 0x100C
load 0x700C
What physical addresses?
Observation: 
Repeatedly access same PTE because program repeatedly 
accesses same virtual page
Aside: What can you infer?
• ptbr: 0x1000; PTE 4 bytes each
• VPN 3 -> PPN 7
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur  5

## Page 6

Locality
 Temporal Locality
 An instruction or data item that has been recently accessed will likely be 
re-accessed soon in the future.
 Spatial Locality
 If a program accesses memory at address x, it will likely soon access 
memory near x.
6
1st access is page1.
2nd access is also page1.
Virtual Memory
Page 1
Page 2
Page 3
Page 4
Page 5
Page n
1st access is page1.
2nd access is near by page1.
Virtual Memory
…
Page 1
Page 2
Page 3
Page 4
Page 5
Page n
…
Page 6
Page 7
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 7

 Part of the chip’s memory-management unit(MMU).
 A hardware cache of popular virtual-to-physical address translation.
MMU
TLB: Translation Lookaside Buffer
7
CPU
Page 0
TLB
popular v to p
Page 1
Page 2
TLB Hit
Address Translation with MMU Physical Memory
Page n
…
Logical 
Address
TLB 
Lookup
Page Table
all v to p entries
TLB Miss 
Physical
Address
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 8

 How a TLB can improve its performance.
Example: Accessing An Array
OFFSET
00 04      08      12      16
VPN = 00
VPN = 01
VPN = 03
VPN = 04
VPN = 05
VPN = 06 a[0] a[1] a[2]
VPN = 07 a[3] a[4] a[5] a[6]
VPN = 08 a[7] a[8] a[9]
VPN = 09
VPN = 10
VPN = 11
VPN = 12
VPN = 13
VPN = 14
VPN = 15
10
0: int sum = 0 ; 
1: for( i=0; i<10; i++){
2: sum+=a[i];
3: }
3 misses and 7 hits. 
Thus TLB hit rate is 70%.
The TLB improves performance
due to spatial locality
What would improve TLB Performance?
1. Increase page size
2. Increase no. of entries
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 9

 LRU(Least Recently Used)
 Evict an entry that has not recently been used.
 Take advantage of locality in the memory-reference stream.
TLB Replacement Policy
11
Reference Row
7
Page Frame # 
in TLB:
7
0
7
0
1
2
0
1
7
0
3
4
0
3
7
0
2
7
3
2
0
3
2
1
3
2
1
0
2
Total 11 TLB miss
7 0 1 2 0 3 0 4 2 3 0 23 1 2 0 1
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 10

LRU Troubles
Valid Virt Phys
0 ? ?
0 ? ?
0 ? ?
0 ? ?
virtual addresses: 
0 1 2 3 4
Workload repeatedly accesses same offset across 5 pages (strided access)
, but only 4 TLB entries
What will TLB contents be over time?
How will TLB perform?
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur  12

## Page 11

TLB organization
 TLB is managed by Fully Associative method.
 Hardware search the entire TLB in parallel to find the desired translation.
 other bits: valid bits , protection bits, address-space identifier, dirty bit
14
VPN PFN other bits
Typical TLB entry look like this
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 12

TLB Issue: Context Switching
15
Process A
Process B
TLB Table
Page 0
Page 1
Page 2
Virtual Memory
Page n
…access VPN10
Page 0
Page 1
Page 2
Page n
…
Virtual Memory
VPN PFN valid prot
10 100 1 rwx
- - - -
- - - -
- - - -
Insert TLB Entry
What happens if a process uses cached TLB entries from another process?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 13

TLB Issue: Context Switching
16
Process A
Process B
TLB Table
Page 0
Page 1
Page 2
Virtual Memory
Page n
…
Page 0
Page 1
Page 2
Page n
…
Virtual Memory
VPN PFN valid prot
10 100 1 rwx
- - - -
10 170 1 rwx
- - - -
Context
Switching
access VPN10
Insert TLB Entry
What happens if a process uses cached TLB entries from another process?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 14

TLB Issue: Context Switching
17
Process A
Process B
TLB Table
Page 0
Page 1
Page 2
Virtual Memory
Page n
…
Page 0
Page 1
Page 2
Page n
…
Virtual Memory
VPN PFN valid prot
10 100 1 rwx
- - - -
10 170 1 rwx
- - - -
Can’t Distinguish which entry is 
meant for which process
What happens if a process uses cached TLB entries from another process?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 15

To Solve Problem
1. Flush TLB on each switch (i.e reset valid bit) – losing all recently cache
d translations may be costly
2. Provide an address space identifier(ASID) field in the TLB.
18
Process A
Process B
TLB Table
Page 0
Page 1
Page 2
Virtual Memory
Page n
…
Page 0
Page 1
Page 2
Page n
…
VPN PFN valid prot ASID
10 100 1 rwx 1
- - - - -
10 170 1 rwx 2
- - - - -
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 16

Another Case
 Two processes share a page.
 Process 1 is sharing physical page 101 with Process2.
 P1 maps this page into the 10th page of its address space.
 P2 maps this page to the 50th page of its address space.
19
VPN PFN valid prot ASID
10 101 1 rwx 1
- - - - -
50 101 1 rwx 2
- - - - -
Sharing of pages is 
useful as it reduces the 
number of physical 
pages in use.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 17

H/W and OS roles: Who Handles The TLB Miss?
 Hardware-managed TLB on CISC.
 The hardware knows the exact structure and location of page tables.
 The hardware would “walk” the page table, find the correct page-table 
entry and extract the desired translation, update and retry operation.
 RISC have what is known as a software-managed TLB.
 On a TLB miss, the hardware raises exception( trap handler ).
 Trap handler is code within the OS that is written with the express 
purpose of handling TLB miss which basically updates TLB and then return 
from trap. H/W then retry the instruction/operation
 More flexible as OS can use smart DS for page tables which is transparent 
to H/W
21Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 18

 Disclaimer: This slide set has been adapted from the initial lecture slides for Operating 
System course in Computer Science Dept. at Hanyang University. This lecture slide set is 
for OSTEP book written by Remzi and Andrea at University of Wisconsin.
22Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

