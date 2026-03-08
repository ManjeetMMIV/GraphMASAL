# Document: Chapter 39. File and Directories (Pages 1 to 35)

## Page 1

39. File and Directories
Operating System: Three Easy Pieces
1

## Page 2

2
Persistent/Long-term information storage
 Must store large amounts of data
 Gigabytes -> terabytes -> petabytes
 Stored information must survive the termination of the pro
-cess using  it
 Lifetime can be seconds to years
 Must have some way of finding it!
 Multiple processes must be able to access the information 
concurrently
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 3

File System Abstraction
 File system consists of files and Directories
 Also refers to part of OS that manages those files
 File is a linear array of bytes stored persistently
 Identified with file name (human readable) and OS-level  
identifier (“inode number”)
 Inode number unique within a file system
 Directory contains other subdirectories and files, along with 
their inode numbers
 Stored like a file, whose contents are filename-to-inode
mappings
3Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 4

4
File operations
 Create: make a new file
 Delete: remove an existing 
file
 Open: prepare a file to be 
accessed
 Close: indicate that a file is 
no longer being accessed
 Read: get data from a file
 Write: put data to a file
 Append: like write, but   o
nly at the end of the file
 Seek: move the “current” 
pointer elsewhere in the   
file
 Get attributes: retrieve att
-ribute information
 Set attributes: modify att-
ribute information
 Rename: change a file’s  
name
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 5

Accessing File 
Three possibilities to access a File:
 Unique id: inode numbers
 Path
 File descriptor
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 5

## Page 6

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
file
file
inode number
Data
Meta-data
location
size=12
location
size
location
size
location
size=6
file
file
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 6

## Page 7

File API (attempt 1)
read(int inode, void *buf, size_t nbyte)
write(int inode, void *buf, size_t nbyte)
seek(int inode, off_t offset)
seek does not cause disk seek until read/write
Disadvantages?
- names hard to remember
- no organization or meaning to inode numbers
- semantics of offset across multiple processes?
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 7

## Page 8

Paths
 String names are friendlier than IDs
 File system still interacts with inode numbers
 Store path-to-inode mappings in predetermined 
“root” Directory (say inode 2)
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 8

## Page 9

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
inode number
location
size=12
location
size
location
size
location
size=6
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 9

## Page 10

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
inode number
“readme.txt”: 3, “hello”: 0, …
0
1
2
3
…
inode number
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 10

## Page 11

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
inode number
“readme.txt”: 3, “hello”: 0, …
0
1
2
3
…
inode number
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 11

## Page 12

Paths
Generalize! 
Directory Tree instead of single root directory. Files  
and directories arranged in a tree,  starting with root  
(“/”)
Only file path needs to be unique
/bar/foo/bar.txt
/foo/bar.txt
 Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 12

## Page 13

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
“bashrc”: 6, …
# settings: …
inode number
“etc”: 0, …
0
1
2
3
inode number
0
1
2
3
…
inode number
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 13

## Page 14

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
“bashrc”: 6, …
# settings: …
inode number
“etc”: 0, …
read /etc/bashrc
reads: 0
0
1
2
3
inode number
0
1
2
3
…
inode number
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 14

## Page 15

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
“bashrc”: 6, …
# settings: …
inode number
“etc”: 0, …
read /etc/bashrc
reads: 1
0
1
2
3
inode number
0
1
2
3
…
inode number
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 15

## Page 16

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
“bashrc”: 6, …
# settings: …
inode number
“etc”: 0, …
read /etc/bashrc
reads: 2
0
1
2
3
inode number
0
1
2
3
…
inode number
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 16

## Page 17

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
“bashrc”: 6, …
# settings: …
inode number
“etc”: 0, …
read /etc/bashrc
reads: 3
0
1
2
3
inode number
0
1
2
3
…
inode number
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 17

## Page 18

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
“bashrc”: 6, …
# settings: …
inode number
“etc”: 0, …
read /etc/bashrc
reads: 4
0
1
2
3
inode number
0
1
2
3
…
inode number
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 18

## Page 19

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
“bashrc”: 6, …
# settings: …
inode number
“etc”: 0, …
read /etc/bashrc
reads: 5
0
1
2
3
inode number
0
1
2
3
…
inode number
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 19

## Page 20

location
size=12
inodes
0
location
size1
location
size2
location
size=63
…
“bashrc”: 6, …
# settings: …
inode number
“etc”: 0, …
read /etc/bashrc
reads: 6
Read root dir (inode and data); 
read etc dir (inode and data); 
read bashrc file (indode and data)
Reads for getting final inode called “traversal”
0
1
2
3
inode number
0
1
2
3
…
inode number
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 
 20

## Page 21

Operations on Directories
• Directories can also be accessed like files
– Operations like create(mkdir()), open(opendir()), read(readdir()
), etc.
– No writedir(). Why?
• For example, the “ls” program opens and reads all 
entries of the directory 
– Directory entry contains file name, inode no.,  type of file etc.
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 21

## Page 22

File API (attempt 2)
pread(char *path, void *buf,
off_t offset, size_t nbyte)
pwrite(char *path, void *buf,
off_t offset, size_t nbyte)
Disadvantages?  
Expensive traversal!  
Goal: traverse once
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 22

## Page 23

File Descriptor (fd)
 Idea: 
 Do expensive traversal once (open file), check permiss
-ions and store inode in a descriptor object (kept in   
memory).
 Do reads/writes via descriptor, which tracks offset
 Each process:
 File-descriptor table contains pointers to open file des
-criptors in the system wide file descriptor table
 Integers used for file I/O are indexes into this table
 stdin: 0, stdout: 1, stderr: 2
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 23

## Page 24

Code Snippet
int fd1 = open(“file.txt”); // returns 3
read(fd1, buf, 12);
int fd2 = open(“file.txt”); // returns 4
int fd3 = dup(fd2);         // returns 5
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 24

## Page 25

0
1
2
3
4
5
offset =  0
inode = 
fdsfd table
location = …
size = …
inode
“file.txt” also points here
int
 fd1 = open(“
file.txt
”); // returns 3
Code Snippet
0
1
2
3
4
5
fdsfd table
inode
“file.txt” also points here
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 25

## Page 26

Code Snippet
0
1
2
3
4
5
offset =  12
inode = 
fdsfd table
location = …
size = …
inode
int
 fd1 = open(“
file.txt
”); // returns 3
read(fd1, 
buf
, 12);
0
1
2
3
4
5
fdsfd table
inode
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 26

## Page 27

Code Snippet
0
1
2
3
4
5
offset =  12
inode = 
offset =  0
inode = 
fdsfd table
location = …
size = …
inode
int
 fd1 = open(“
file.txt
”); // returns 3
read(fd1, 
buf
, 12);
int
 fd2 = open(“
file.txt
”); // returns 4
0
1
2
3
4
5
fdsfd table
inode
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 27

## Page 28

Code Snippet
int fd1 = open(“file.txt”); // returns 3
read(fd1, buf, 12);
int fd2 = open(“file.txt”); // returns 4
int fd3 = dup(fd2);         // returns 5
0
1
2
3
4
5
offset =  12
inode = 
offset =  0
inode = 
fdsfd table
location = …
size = …
inode
0
1
2
3
4
5
fdsfd table
inode
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 28

## Page 29

File API (attempt 3)
int fd = open(char *path, int flag, mode_t mode)
read(int fd, void *buf, size_t nbyte)
write(int fd, void *buf, size_t nbyte)
close(int fd)
advantages:
- string names
- hierarchical
- traverse once
- different offsets precisely defined
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 29

## Page 30

Deleting Files
 There is no system call for deleting files!
 Inode (and associated file) is garbage collected when 
there are no references (from paths or fds)
 Paths are deleted when: unlink() is called
 FDs are deleted when: close() or process quits
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 30

## Page 31

Many File Systems
 Users often want to use many file systems
 For example:
- main disk
- backup disk
- USB drives
 What is the most elegant way to support this?
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 31

## Page 32

Many File Systems: Approach 1
 http://www.ofzenandcomputing.com/burn-files-cd-dvd-windows7/
 32

## Page 33

sh> mount
/dev/sda1 on /
/dev/sdb1 on /backups
AFS on /home
/
backups home
bak1 bak2 bak3
etc bin
tyler
537
p1 p2
.bashrc
stitch all the file syste
ms together into a sup
er file system!
Many File Systems: Approach 2
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 33

## Page 34

Writing Immediately with fsync()
 File system keeps newly written data in memory for a 
while
 Write buffering improves performance (why?)
 But what if system crashes before buffers are flushed?
 If application cares:
 fsync(int fd) forces buffers to flush to disk, and (us
ually) tells disk to flush its write cache too
 Makes data durable
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 34

## Page 35

Atomic File Update
 Say application wants to update file.txt atomically
 If crash, should see only old contents or only new contents
1. write new data to file.txt.tmp file
2. fsync file.txt.tmp
3. rename file.txt.tmp over file.txt, replacing it
Operating Systems by Dr. Praveen Kumar @ 
CSED, VNIT Nagpur 35

