# Document: Chapter 40. File System Implementation (Pages 1 to 38)

## Page 1

40. File system Implementation.
Operating System: Three Easy Pieces
1

## Page 2

Persistent Store
 Given: large array of blocks on disk
 Want: some structure to map files to disk blocks and ways to 
access them
D D D D D D D D
0 7
D D D D D D D D
8 15
D D D D D D D D
16 23
D D D D D D D D
24 31
D D D D D D D D
32 39
D D D D D D D D
40 47
D D D D D D D D
48 55
D D D D D D D D
56 63
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 3

## Page 3

The Way To Think
 There are two different aspects to implementation of file system 
 Data structures
 What types of on-disk structures are utilized by the file system to organize its data and 
metadata?
 Access methods
 How does it map the calls made by a process as open(), read(), write(), etc. 
 Which structures are read during the execution of a particular system call? 
4Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 4

How file system allocate blocks to files?
Same principle: 
map logical abstraction to physical resource
Process 1
Process 2
Logical View: Address Spaces
Physical View
Process 3
Similarity to Memory?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 5

## Page 5

Allocation Strategies
Many different approaches
 Contiguous
 Extent-based
 Linked
 File-allocation Tables
 Indexed
 Multi-level Indexed
Questions
 Amount of fragmentation (internal and external)
– freespace that can’t be used
 Ability to grow file over time?
 Performance of sequential accesses (contiguous layout)?
 Speed to find data blocks for random accesses?
 Wasted space for meta-data overhead (everything that isn’t 
data)?
 Reliability in face of data/block corruption etc.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 6

## Page 6

Contiguous Allocation
Allocate each file to contiguous sectors on disk
 Meta-data: 
 OS allocates by finding sufficient free space
 Must predict future size of file; Should space be reserved?
 Example: IBM OS/360
A A A B B B B C C C
Fragmentation (internal and external)?
Ability to grow file over time?
Seek cost for sequential accesses?
Speed to calculate random accesses?
Wasted space for meta-data? + Little overhead for meta-data
+ Excellent performance
+ Simple calculation
- Horrible external frag (needs periodic compaction)
- May not be able to without moving 
Starting block and size of file
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 7

## Page 7

Small # of Extents
Allocate multiple contiguous regions (extents) per file
 Meta-data:
D A A A B B B B C C C B BD D
A A A B B B B C C C
Fragmentation (internal and external)?
Ability to grow file over time?
Seek cost for sequential accesses?
Speed to calculate random accesses?
Wasted space for meta-data? + Still small overhead for meta-data
+ Still good performance
+ Still simple calculation
- Helps external fragmentation
- Can grow (until run out of extents)
Small array (2-6) designating each extent 
Each entry: starting block and size
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 8

## Page 8

Linked Allocation
Allocate linked-list of fixed-sized blocks (multiple sectors)
 Meta-data: 
 Examples: TOPS-10, Alto
D A A A B B B B C C C B BD D D DB
Fragmentation (internal and external)?
Ability to grow file over time?
Seek cost for sequential accesses?
Speed to calculate random accesses?
Wasted space for meta-data? - Waste pointer per block
+/- Depends on data layout
- Ridiculously poor
+ No external frag (use any block); internal?
+ Can grow easily
Reliability? - if a block goes bad, you losse entire file
Location of first block of file
Each block also contains pointer to next block
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 9

## Page 9

File-Allocation Table (FAT)
Variation of Linked allocation
 Keep linked-list information for all files in on-disk FAT table 
 Meta-data: Location of first block of file
 And, FAT table  itself
Comparison to Linked Allocation
• Same basic advantages and disadvantages
• Disadvantage: Read from two disk locations for every data read
• Optimization: Cache FAT in main memory
– Advantage: Greatly improves random accesses
– What portions should be cached?  How to Scale with larger file systems?
D A A A B B B B C C C B BD D D DB
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 10

## Page 10

Indexed Allocation
Allocate fixed-sized blocks for each file
 Meta-data: 
 Allocate space for ptrs at file creation time
Advantages
• No external fragmentation
• Files can be grown up to max file size
• Supports random access
Disadvantages
• Large overhead for meta-data:
– Wastes space for unneeded pointers (most files are small!)
D A A A B B B B C C C B BD D D DB
Fixed-sized array of block pointers
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 11

## Page 11

Multi-Level Indexing
Variation of Indexed Allocation
 Dynamically allocate hierarchy of pointers to blocks as needed
 Meta-data: Small number of pointers allocated statically
 Additional pointers to blocks of pointers
 Examples: UNIX FFS-based file systems
Comparison to Indexed Allocation
• Advantage: Does not waste space for unneeded pointers
– Still fast access for small files
– Can grow to what size??
• Disadvantage: Need to read indirect blocks of pointers to calculate addresses (extra disk re
ad)
– Keep indirect blocks cached in main memory
indirect
Double indirect
indirect
Triple indirect
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 12

## Page 12

File system layout/organization
- data block
- inode table
- indirect block
- directories
- data bitmap
- inode bitmap
- superblock
Assume Multi-Level Indexing
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
13

## Page 13

FS Structs: Empty Disk
Assume each block is 4KB
D D D D D D D D
0 7
D D D D D D D D
8 15
D D D D D D D D
16 23
D D D D D D D D
24 31
D D D D D D D D
32 39
D D D D D D D D
40 47
D D D D D D D D
48 55
D D D D D D D D
56 63
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
14

## Page 14

Data Blocks
0 7
D D D D D D D D
8 15
D D D D D D D D
16 23
D D D D D D D D
24 31
D D D D D D D D
32 39
D D D D D D D D
40 47
D D D D D D D D
48 55
D D D D D D D D
56 63
D D D D D D D D
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
15

## Page 15

Inodes
I I I I I
0 7
D D D D D D D D
8 15
D D D D D D D D
16 23
D D D D D D D D
24 31
D D D D D D D D
32 39
D D D D D D D D
40 47
D D D D D D D D
48 55
D D D D D D D D
56 63
D D D
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
16

## Page 16

inode
16
inode
17
inode
18
inode
19
inode
20
inode
21
inode
22
inode
23
inode
24
inode
25
inode
26
inode
27
inode
28
inode
29
inode
30
inode
31
One Inode Block
 Each inode is typically 256 
bytes (depends on the FS, 
maybe 128 bytes)
 4KB disk block
 16 inodes per inode block
.
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
17

## Page 17

Inode
type (file or dir?)
uid (owner)
rwx (permissions)
size (in bytes)
Blocks
time (access)
ctime (create)
links_count (# paths)
addrs[N] (N data blocks)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
18

## Page 18

I I I I I
0 7
D D D D D D D D
8 15
D D D D D D D D
16 23
D D D D D D D D
24 31
D D D D D D D D
32 39
D D D D D D D D
40 47
D D D D D D D D
48 55
D D D D D D D D
56 63
D D D
Inodes
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
19

## Page 19

type
uid
rwx
size
blocks
time
ctime
links_count
addrs[N]
Inode
Assume single level (just pointers to data blocks)
What is max file size?
Assume 256-byte inodes (all can be used for poin
ters)
Assume 4-byte addrs
How to get larger files?
256 / 4 =  64
64 * 4K = 256 KB!
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
20

## Page 20

inode
data data data data
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
21

## Page 21

inode
indirect indirect indirect indirect
Indirect blocks are stored in
regular data blocks.
what if we want to
optimize for small files?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
22

## Page 22

inode
indirectdata data data
Better for small files
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
23

## Page 23

Assume 256 byte inodes (16 inodes/block).  
What is offset for inode with number 4?


## Page 24

Assume 256 byte inodes (16 inodes/block).  
What is offset for inode with number 40?


## Page 25

Directory structure
 Directory is just a special type of file which also has   
inode and data blocks 
 Common design: 
 Store directory entries in data blocks
 Large directories just use multiple data blocks
 Use bit in inode to distinguish directories from files
 Various formats could be used
- lists
- Hash table
- b-trees
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 26

## Page 26

Allocation
How do we find free data blocks or free inodes?
 Bitmaps: For inodes and data blocks, store one bit per b
lock to indicate if free or not
 Free list: a free block stores address of next block on list 
and super block stores pointer to first free  block
 More complex structures can also be used
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
28

## Page 27

Bitmaps
I I I I I
0 7
D D D D D D D D
8 15
D D D D D D D D
16 23
D D D D D D D D
24 31
D D D D D D D D
32 39
D D D D D D D D
40 47
D D D D D D D D
48 55
D D D D D D D D
56 63
D i d
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
29

## Page 28

Superblock
 Need to know basic FS configuration metadata, like:
- block size
- # of inodes, data blocks etc.
 Superblock stores the master plan of all other blocks 
I I I I I
0 7
D D D D D D D D
8 15
D D D D D D D D
16 23
D D D D D D D D
24 31
D D D D D D D D
32 39
D D D D D D D D
40 47
D D D D D D D D
48 55
D D D D D D D D
56 63
S i d
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
30

## Page 29

31
Carving up the disk
Master
boot record
Partition table
Partition 1 Partition 2 Partition 3 Partition 4
Entire disk
Boot
block
Super
block
Free space
management
Index
nodes Files & directories
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 30

Part 2 : Operations
- create file
- write
- open
- read
- close
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
32

## Page 31

data inode root foo bar root foo
bitmap bitmap inode inode inode data data
create /foo/bar
read
read
read
read
read
write
read
write
write
write
What needs to be read and written?

## Page 32

data inode root foo bar root foo
bitmap bitmap inode inode inode data data
open /foo/bar
data
bar
read
read
read
read
read

## Page 33

data inode root foo bar root foo
bitmap bitmap inode inode inode data data
write to /foo/bar (assume file exists and has been opened)
bar
data
read
read
write
write
write

## Page 34

data inode root foo bar root foo
bitmap bitmap inode inode inode data data
read /foo/bar – assume opened
data
bar
read
read
write

## Page 35

data inode root foo bar root foo
bitmap bitmap inode inode inode data data
close /foo/bar
data
bar
nothing to do on disk!

## Page 36

Efficiency
How can we avoid this excessive I/O for basic ops?
 Use Disk buffer cache for:
- reads
- write buffering
 Results of recently fetched disk blocks are cached
 LRU to evict if cache is full
 File system issues block read/write requests to  block no.’s  
via buffer cache
 If block in cache, served from cache, no disk I/O
 If cache miss, block fetched to cache and returned to  FS
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
38

## Page 37

Write Buffering
 Writes are applied to cache block first
– Synchronous/write-through cache writes to disk     
immediately
– Asynchronous/write-back cache stores dirty block in  
memory and writes back after a delay
 Why does procrastination help?
 Overwrites, deletes, scheduling
 Shared structs (e.g., bitmaps+dirs) often overwritten.
 tradeoffs : how much to buffer, how long to buffer…
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 
39

## Page 38

 Disclaimer: Some of the slides have been adapted from the initial lecture slides for 
Operating System course in Computer Science Dept. at Hanyang University. This lecture 
slide set is for OSTEP book written by Remzi and Andrea at University of Wisconsin.
40Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

