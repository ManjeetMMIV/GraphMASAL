# Document: Chapter 16. Segmentation (Pages 1 to 17)

## Page 1

16. Segmentation
Operating System: Three Easy Pieces
1Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 2

Inefficiency of the Base and Bound Approach
 Big chunk of “free” space in VAS
 In contiguous allocation even “free” space takes 
up physical memory => wasteful
 Hard to run when the entire address space does 
not fit into physical memory
 No partial sharing: Cannot share parts of address 
space such as program code
2
(free)
14KB
Program Code
16KB
0KB
2KB
4KB
Heap
Stack
6KB
15KB
5KB
3KB
1KB
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 3

Segmentation
 Divide address space into segments which corresponds to logical 
entity in address space like code, stack, heap
 Segment is a contiguous portion of the address space of a particular 
length.
 Each segment has its own Base and bounds pair. They can independ-
ently:
 Be Placed separately in different part of physical memory.
 grow and shrink
 be protected or shared (separate read/write/execute protection bits)
3Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 4

Example: Placing Segment In Physical Memory
4
0KB
16KB
32KB
48KB
64KB
Code
Physical Memory
(not in use)
(not in use)
Heap
Stack
Operating System
(not in use)
Segment  Base Size
Code 32K 2K
Heap 34K 2K
Stack 28K 2K
(free)
14KB
Program Code
16KB
0KB
2KB
4KB
Heap
Stack
6KB
15KB
5KB
3KB
1KB
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 5

Address Translation for Code Segment
 The offset of virtual address 100 is 100.
 The code segment starts at virtual address 0 in address space.
5
Segment    Base Size
Code 32K 2K
0KB
2KB
Program Code
4KB
16KB
32KB
100 instruction
𝑝ℎ𝑦𝑠𝑖𝑐𝑎𝑙 𝑎𝑑𝑑𝑟𝑒𝑠𝑠 = 𝑜𝑓𝑓𝑠𝑒𝑡 + 𝑏𝑎𝑠𝑒
Heap
Code
(not in use)
(not in use)
34KB
𝟏𝟎𝟎 + 𝟑𝟐𝑲 𝒐𝒓 𝟑𝟐𝟖𝟔𝟖
is the desired 
physical address
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 6

Address Translation for Heap Segment
 The offset of virtual address 4200 is 104.
 The heap segment starts at virtual address 4096 in address space.
6
Segment    Base Size
Heap 34K 2K
32KB
Heap
Code
(not in use)
(not in use)
34KB 𝟏𝟎𝟒 + 𝟑𝟒𝑲 𝒐𝒓 𝟑𝟒𝟗𝟐𝟎
is the desired 
physical address6KB
Heap
4KB
Address Space
Physical Memory
4200 data
36KB
𝑽𝒊𝒓𝒕𝒖𝒂𝒍 𝒂𝒅𝒅𝒓𝒆𝒔𝒔 + 𝒃𝒂𝒔𝒆 is not the correct physical address.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 7

Segmentation Fault or Violation
 If an illegal address such as 7KB which is beyond the end of heap is 
referenced, the hardware detects it is out of bounds and traps into 
OS. What would OS do?
 Likely terminate with the famous message “segmentation fault”
7
6KB
Heap
4KB
(not in use)
Address Space
7KB
8KB
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 8

Segmented Addressing
8
 Chop up the address space into segments based on the top few bits 
of virtual address 
 Use top bits of virtual address to select segment and remaining bits to 
select offset within segment
 Example: virtual address 4200 (01000001101000)
013 112 211 310 49 8 7 6 5
Segment Offset
013 112 211 310 49 8 7 6 5
Segment Offset
00 01 00 10 00 0 0 1 1
Segment  bits
Code 00
Heap 01
- 10
Stack    11
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 9

Referring to Segment(Cont.)
 SEG_MASK = 0x3000(11000000000000)
 SEG_SHIFT = 12
 OFFSET_MASK = 0xFFF (00111111111111)
9
1   // get top 2 bits of 14-bit VA
2   Segment = (VirtualAddress & SEG_MASK) >> SEG_SHIFT 
3 // now get offset 
4   Offset = VirtualAddress & OFFSET_MASK 
5   if (Offset >= Bounds[Segment]) 
6   RaiseException(PROTECTION_FAULT) 
7   else 
8   PhysAddr = Base[Segment] + Offset 
9   Register = AccessMemory(PhysAddr) 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 10

Referring to Stack Segment
 Stack grows backward.
 Extra hardware support is needed.
 The hardware checks which way the segment grows.
 1: positive direction, 0: negative direction 
10
Segment  Base Size  Grows Positive?
Code 32K 2K        1             
Heap 34K 2K        1 
Stack 28K 2K        0
Segment Register(with Negative-Growth Support)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 11

Referring to Stack Segment (cont..)
 Example: accessing VA 15KB which should map to 27KB PA.
 15KB (11 1100 0000 0000) – offset of 3KB
 To get correct negative offset – subtract the max segment size (here 4 KB)
 Simply add the correct offset (-1KB) to base (28KB) to arrive at correct PA 
(27KB)
11
Stack
(not in use)
(not in use)
28KB
26KB
Physical Memory
(free)
14KB
16KB
Stack15KB
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 12

Support for Sharing
 Segment can be shared between address space.
 Code sharing is still in use in systems today.
 by extra hardware support.
 Extra hardware support is needed in the form of Protection bits. 
 A few more bits per segment to indicate permissions of read, write and 
execute. 
12
Segment  Base Size  Grows Positive?  Protection
Code 32K 2K        1           Read-Execute             
Heap 34K 2K        1           Read-Write 
Stack 28K 2K        0           Read-Write
Segment Register Values(with Protection)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 13

Fine-Grained and Coarse-Grained
 Coarse-Grained means segmentation in a small number.
 e.g., code, heap, stack.
 Fine-Grained segmentation allows more flexibility for address space 
in some early system.
 To support many segments, Hardware support with a segment table is 
required. 
13
Segment Base Bounds R W
0 0x2000 0x6ff 1 0
1 0x0000 0x4ff 1 1
2 0x3000 0xfff 1 1
3 0x0000 0x000 0 0
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 14

OS support: Fragmentation
 External Fragmentation: little holes of free space in physical memory 
that creates difficulty to allocate new segments.
 The OS cannot satisfy a 20KB request.
 There is 24KB free, but not as one contiguous
segment.
14
0KB
16KB
32KB
48KB
64KB
Operating System8KB
24KB
40KB
56KB
(not in use)
(not in use)
Allocated
(not in use)
Allocated
Allocated
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 15

Memory Compaction
15
0KB
16KB
32KB
48KB
64KB
Operating System8KB
24KB
40KB
56KB
Allocated
(not in use)
Compacted
 Compaction: rearranging the existing segments in physical memory.
 Compaction is costly.
 Stop running process.
 Copy data to somewhere.
 Change segment register value.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 16

Question
 What if not enough bits (small addr space) to do segment addressing?
 For 16 bit logical address, 4 segments; how many bits for segment?   
How many bits for offset?
 Translate logical addresses (in hex) to physical addresses
 0x0240:
 0x4108:
 0xa65c:
16Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
Segment Base Bounds R W
0 0x2000 0x6ff 1 0
1 0x0000 0x4ff 1 1
2 0x3000 0xfff 1 1
3 0x0000 0x000 0 0

## Page 17

 Disclaimer: This slide set has been adapted from the initial lecture slides for Operating 
System course in Computer Science Dept. at Hanyang University. This lecture slide set is 
for OSTEP book written by Remzi and Andrea at University of Wisconsin.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

