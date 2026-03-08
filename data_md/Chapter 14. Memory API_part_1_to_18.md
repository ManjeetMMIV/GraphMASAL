# Document: Chapter 14. Memory API (Pages 1 to 18)

## Page 1

14. Memory API
Operating System: Three Easy Pieces
1

## Page 2

Memory API: malloc()
 Allocate a memory region on the heap.
 Argument
 size_t size : size of the memory block(in bytes)
 size_t is an unsigned integer type.
 Return
 Success :  a void type pointer to the memory block allocated by malloc
 Fail : a null pointer
2
#include <stdlib.h>
void* malloc(size_t size)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 3

sizeof()
 Routines and macros are utilized for size in malloc instead typing 
in a number directly.
 Two types of results of sizeof with variables
 The actual size of ‘x’ is known at run-time.
 The actual size of ‘x’ is known at compile-time.
3
int *x = malloc(10 * sizeof(int));
printf(“%d\n”, sizeof(x));
4
int x[10];
printf(“%d\n”, sizeof(x));
40
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 4

Memory API: free()
 Free a memory region allocated by a call to malloc.
 Argument
 void *ptr : a pointer to a memory block allocated with malloc
 Return
 none
4
#include <stdlib.h>
void free(void* ptr)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 5

Memory Allocating
5
int *pi; // local variable
(free)
stack
heap
*pi 
2KB
pi = (int *)malloc(sizeof(int)* 4);
(free)
2KB
allocated
allocated
allocated
allocated
*pi 
Address Space
pointer
16KB
2KB
2KB + 4
2KB + 8
2KB + 12
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 6

Memory Freeing
6
free(pi);
(free)
2KB(invalid)
freed
freed
freed
freed
*pi 
(free)
2KB(invalid)
stack
heap
*pi 
Address Space
2KB
16KB
2KB + 4
2KB + 8
2KB + 12
2KB
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 7

Forgetting To Allocate Memory
 Incorrect code
char *src = “hello”; //character string constant 
char *dst; //unallocated
strcpy(dst, src);    //segfault and die
(free)
*dst
stack
heap
*src
hello\0
strcpy(dst, src);   unallocated
Address Space
7Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 8

Forgetting To Allocate Memory(Cont.)
 Correct code
char *src = “hello”; //character string constant 
char *dst (char *)malloc(strlen(src) + 1 ); // allocated
strcpy(dst, src); //work properly
(free)
*dst
stack
heap
*src
hello\0
strcpy(dst, src);   
allocated
(free)
*dst
stack
heap
*src
hello\0
hello\0
Address Space Address Space
8Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 9

Not Allocating Enough Memory
 Incorrect code, but work properly
char *src = “hello”; //character string constant 
char *dst (char *)malloc(strlen(src)); // too small
strcpy(dst, src);    //work properly
(free)
*dst
stack
heap
*src
hello\0
h
e
l
l
o
\0
6 bytes strlen
5 bytes‘\0’ is omitted
strcpy(dst, src);   
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 10

Forgetting to Initialize
 Encounter an uninitialized read
10
int *x = (int *)malloc(sizeof(int)); // allocated
printf(“*x = %d\n”, *x); // uninitialized memory access
(free)
stack
heap
*x
allocated
with value used 
before
Address Space
(free)
stack
heap
*x
value used 
before
(free)
Address Space
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 11

Memory Leak
 A program runs out of memory and eventually dies.
11
(free)
stack
heap
*a
allocated
(free)
stack
heap
*a
unused
allocated
*b
(free)
heap
*a
unused
*b
unused
*c
*d
unused
allocated
Address Space Address Space Address Space
unused : unused, but not freed 
run out of memory
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 12

 Freeing memory before it is finished using
 A program accesses to memory with an invalid pointer
Dangling Pointer
12
*a
*b
(free)
2KB
3KB
3KB
NULL
freed
*a
*b free()
dangling pointer
free(b)
*b
*a
(free)
2KB
3KB2KB
3KB
NULL
4KB
*b
*a
unreachable
Heap
Stack
Heap
Stack
3KB
4KB
2KB
3KB
4KB
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 13

Other Memory APIs: calloc()
 Allocate memory on the heap and zeroes it before returning.
 Argument
 size_t num : number of blocks to allocate
 size_t size : size of each block(in bytes)
 Return
 Success :  a void type pointer to the memory block allocated by calloc
 Fail : a null pointer
13
#include <stdlib.h>
void *calloc(size_t num, size_t size)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 14

Double Free
 Free memory that was freed already.
14
int *x = (int *)malloc(sizeof(int)); // allocated
free(x); // free memory
free(x); // free repeatedly
(free)
2KB(invalid)
freed
*x 
Address Space
(free)
2KB
2KB allocated
*x 
free(x) free(x)
Undefined 
Error
Address Space
Heap
Stack
Heap
Stack
16KB
2KB
16KB
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 15

Other Memory APIs: realloc()
 Change the size of memory block.
 A pointer returned by realloc may be either the same as ptr or a new.
 Argument
 void *ptr: Pointer to memory block allocated with malloc, calloc or 
realloc
 size_t size: New size for the memory block(in bytes)
 Return
 Success:  Void type pointer to the memory block
 Fail : Null pointer
15
#include <stdlib.h>
void *realloc(void *ptr, size_t size)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 16

System Calls
 malloc library call use brk system call. 
 brk is called to expand the program’s break.
 break: The location of the end of the heap in address space
 sbrk is an additional call similar with brk.
 Programmers should never directly call either brk or sbrk.
16
#include <unistd.h>
int brk(void *addr)
void *sbrk(intptr_t increment);
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 17

System Calls(Cont.)
 mmap system call can create an anonymous memory region.
17
#include <sys/mman.h>
void *mmap(void *ptr, size_t length, int port, int flags, 
int fd, off_t offset)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

## Page 18

 Disclaimer: This slide set has been adapted from the initial lecture slides for Operating 
System course in Computer Science Dept. at Hanyang University. This lecture slide set is 
for OSTEP book written by Remzi and Andrea at University of Wisconsin.
18Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

