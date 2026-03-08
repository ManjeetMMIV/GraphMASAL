# Document: Chapter 17. Free Space Management (Pages 1 to 24)

## Page 1

17. Free-Space Management
Operating System: Three Easy Pieces
1Youjip Won

## Page 2

Splitting
 Finding a free chunk of memory that can satisfy the request and 
splitting it into two.
 When request for memory allocation is smaller than the size of free 
chunks.
2Youjip Won
free
 used
 free
0 10 20 30
head NULL
addr:0
len:10
addr:20
len:10
30-byte heap:
free list:

## Page 3

Splitting(Cont.)
 Two 10-bytes free segment with 1-byte request
3Youjip Won
free
 used
 free
0 10 20 30
head NULL
addr:0
len:10
addr:20
len:10
30-byte heap:
free list:
free
 used
 free
0 10 20  21 30
head NULL
addr:0
len:10
addr:21
len:10
30-byte heap:
free list:
𝒔𝒑𝒍𝒊𝒕𝒕𝒊𝒏𝒈 𝟏𝟎 − 𝒃𝒚𝒕𝒆 𝒇𝒓𝒆𝒆 𝒔𝒆𝒈𝒎𝒆𝒏𝒕

## Page 4

Coalescing
 If a user requests memory that is bigger than free chunk size, the list 
will not find such a free chunk.
 Coalescing: Merge returning a free chunk with existing chunks into a 
large single free chunk if addresses of them are nearby.
4Youjip Won
head NULL
addr:0
Len:10
addr:20
len:10
addr:10
len:10
head NULL
addr:0
len:30
𝒄𝒐𝒂𝒍𝒆𝒔𝒄𝒊𝒏𝒈 𝒇𝒓𝒆𝒆 𝒄𝒉𝒖𝒏𝒌𝒔

## Page 5

Tracking The Size of Allocated Regions
 The interface to free(void *ptr) does not take a size parameter.
 How does the library know the size of memory region that will be back 
into free list?
 Most allocators store extra information in a header block.
5Youjip Won
ptr
The header used by malloc library
The 20 bytes returned to caller
An Allocated Region Plus Header
ptr = malloc(20);

## Page 6

The Header of Allocated Memory Chunk
 The header minimally contains the size of the allocated memory 
region.
 The header may also contain
 Additional pointers to speed up deallocation
 A magic number for integrity checking
6Youjip Won
ptr
The 20 bytes 
returned to caller
size:           20
magic: 1234567
hptr
typedef struct __header_t { 
int size; 
int magic; 
} header_t;
Specific Contents Of The Header
A Simple Header

## Page 7

The Header of Allocated Memory Chunk(Cont.)
 The size for free region is the size of the header plus the size of the space 
allocated to the user.
 If a user request N bytes, the library searches for a free chunk of size N
plus the size of the header
 Simple pointer arithmetic to find the header pointer.
7Youjip Won
void free(void *ptr) { 
header_t *hptr = (void *)ptr – sizeof(header_t);
}

## Page 8

Embedding A Free List
 The memory-allocation library initializes the heap and puts the first 
element of the free list in the free space.
 The library can’t use malloc() to build a list within itself.
8Youjip Won

## Page 9

Embedding A Free List(Cont.)
 Description of a node of the list
 Building heap and putting a free list 
 Assume that the heap is built vi mmap() system call.
9Youjip Won
// mmap() returns a pointer to a chunk of free space
node_t *head = mmap(NULL, 4096, PROT_READ|PROT_WRITE, 
MAP_ANON|MAP_PRIVATE, -1, 0);
head->size = 4096 - sizeof(node_t);
head->next = NULL; 
typedef struct __node_t { 
int size; 
struct __node_t *next; 
} nodet_t;

## Page 10

A Heap With One Free Chunk
10Youjip Won
head
the rest of the 4KB chunk
size:       4088
next:            0
[virtual address: 16KB]
header: size field
header: next field(NULL is 0)
■ ■ ■
// mmap() returns a pointer to a chunk of free space
node_t *head = mmap(NULL, 4096, PROT_READ|PROT_WRITE, 
MAP_ANON|MAP_PRIVATE, -1, 0);
head->size = 4096 - sizeof(node_t);
head->next = NULL; 

## Page 11

Embedding A Free List: Allocation
 If a chunk of memory is requested, the library will first find a chunk 
that is large enough to accommodate the request.
 The library will 
 Split the large free chunk into two.
 One for the request and the remaining free chunk
 Shrink the size of free chunk in the list.
11Youjip Won

## Page 12

Embedding A Free List: Allocation(Cont.)
 Example: a request for 100 bytes by ptr = malloc(100)
 Allocating 108 bytes out of the existing one free chunk.
 shrinking the one free chunk to 3980(4088 minus 108).
12Youjip Won
ptr
the 100 bytes now allocated
size:           100
magic:  1234567
■ ■ ■
head
size: 3980
next:             0
■ ■ ■ the free 3980 byte chunk
head
the rest of 
the 4KB chunk
size:       4088
next:            0
■ ■ ■
A Heap : After One AllocationA 4KB Heap With One Free Chunk

## Page 13

Free Space With Chunks Allocated
13Youjip Won
size:        100
magic:  1234567
■ ■ ■
size:        100
magic:  1234567
■ ■ ■
size:        100
magic:  1234567
■ ■ ■
size:      3764
next:          0
■ ■ ■
sptr
head
[virtual address: 16KB]
100 bytes still allocated
100 bytes still allocated
(but about to be freed)
100 bytes still allocated
The free 3764-byte chunk
Free Space With Three Chunks Allocated
8 bytes header

## Page 14

Free Space With free()
 The 100 bytes chunks is back 
into the free list.
 The free list will start with a 
small chunk.
 The list header will point the 
small chunk
14Youjip Won
size:        100
magic:  1234567
■ ■ ■
size:        100
next:    16708
■ ■ ■
size:        100
magic:  1234567
■ ■ ■
size:      3764
next:          0
■ ■ ■
sptr
[virtual address: 16KB]
100 bytes still allocated
(now a free chunk of 
memory)
100 bytes still allocated
The free 3764-byte chunk
 Example: free(sptr)
head

## Page 15

Free Space With Freed Chunks
 Let’s assume that the last two in-use chunks are freed.
 External Fragmentation occurs.
 Coalescing is needed in the list.
15Youjip Won
size:        100
next:    16492
■ ■ ■
size:        100
next:    16708
■ ■ ■
size:        100
next:    16384
■ ■ ■
size:      3764
next:          0
■ ■ ■
head
[virtual address: 16KB]
The free 3764-byte chunk
(now free)
(now free)
(now free)

## Page 16

Growing The Heap
 Most allocators start with a small-sized heap and then request more 
memory from the OS when they run out.
 e.g., sbrk(), brk() in most UNIX systems.
16Youjip Won
Heap
Address Space
Heap
(not in use)
(not in use)
Physical Memory
Heap
Address Space
break
break
sbrk()
Heap
Heap
(not in use)
(not in use)

## Page 17

Managing Free Space: Basic Strategies
 Best Fit: 
 Finding free chunks that are big or bigger than the request
 Returning the one of smallest in the chunks in the group of candidates 
 Worst Fit:
 Finding the largest free chunks and allocation the amount of the request
 Keeping the remaining chunk on the free list.
17Youjip Won

## Page 18

Managing Free Space: Basic Strategies(Cont.)
 First Fit:
 Finding the first chunk that is big enough for the request
 Returning the requested amount and remaining the rest of the chunk.
 Next Fit:
 Finding the first chunk that is big enough for the request.
 Searching at where one was looking at instead of the begging of the list.
18Youjip Won

## Page 19

Examples of Basic Strategies
 Allocation Request Size 15
 Result of Best-fit
 Result of Worst-fit
19Youjip Won
head NULL
10
 30
 20
head NULL
10
 30
 5
head NULL
10
 15
 20

## Page 20

Other Approaches: Segregated List
 Segregated List: 
 Keeping free chunks in different size in a separate list for the size of 
popular request.
 New Complication:
 How much memory should dedicate to the pool of memory that serves 
specialized requests of a given size?
 Slab allocator handles this issue.
20Youjip Won

## Page 21

Other Approaches: Segregated List(Cont.)
 Slab Allocator
 Allocate a number of object caches.
 The objects are likely to e requested frequently.
 e.g., locks, file-system inodes, etc.
 Request some memory from a more general memory allocator when a 
given cache is running low on free space.
21Youjip Won

## Page 22

Other Approaches: Buddy Allocation
 Binary Buddy Allocation
 The allocator divides free space by two until a block that is big enough 
to accommodate the request is found.
22Youjip Won
64 KB
32 KB
16 KB
32 KB
16 KB
8 KB
 8 KB
64KB free space for 7KB request

## Page 23

Other Approaches: Buddy Allocation(Cont.)
 Buddy allocation can suffer from internal fragmentation.
 Buddy system makes coalescing simple.
 Coalescing two blocks in to the next level of block.
23Youjip Won

## Page 24

 Disclaimer: This lecture slide set was initially developed for Operating System course in 
Computer Science Dept. at Hanyang University. This lecture slide set is for OSTEP book  
written by Remzi and Andrea at University of Wisconsin.
24Youjip Won

