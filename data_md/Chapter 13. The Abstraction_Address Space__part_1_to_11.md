# Document: Chapter 13. The Abstraction_Address Space_ (Pages 1 to 11)

## Page 1

13. The Abstraction: Address Space
Operating System: Three Easy Pieces
1

## Page 2

Memory Virtualization
 What is memory virtualization?
 OS virtualizes its physical memory.
 OS provides an illusion of private memory for each process.
 It seems like each process uses the whole memory .
2Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 3

OS in The Early System
 Load only one process in memory.
 Poor utilization and efficiency
 But life was surely easy for OS developers!
3
0KB
64KB
max
Operating System
(code, data, etc.)
Current
Program
(code, data, etc.)
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 4

Multiprogramming and Time Sharing
 Multiple processes ready to run.
 To Increase CPU utilization and efficiency.
 Execute one for a short while and then switch
 How about Time sharing of Memory?
 Ridiculously poor performance
 Better Alternative: Space sharing
 Cause an important protection issue.
 Errant memory accesses from other processes
4
0KB
64KB
Operating System
(code, data, etc.)
Process C
(code, data, etc.)
Free
Process B
(code, data, etc.)
Free
Process A
(code, data, etc.)
Physical Memory
Free
Free
128KB
192KB
256KB
320KB
384KB
448KB
512KB
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 5

Goals of Memory Virtualization
 Transparency: User programs need not be aware of the messy details  
(Ease of use in programming)
 Efficiency (in times and space) : minimize overhead in access time and 
wastage of memory space 
 Isolation and protection: a user process should not be able to access  
anything (either OS or other process) outside its address space
 Sharing: Cooperating processes can share portions of address space
 Could conceptually use more memory than might be physically         
available
5Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 6

Virtual Address Space
 OS creates an abstraction of physical memory.
 Every process is given a set of virtual address (0 to MAX)   
that maps to physical bytes
 The address space contains all about a running process.
 Review: What is in an address space?
 Static components : Code and some global variables
 Dynamic components : Stack and Heap
 Code: Where instructions reside
 Stack
 Store return addresses or values.
 Contain local variables arguments to routines.
6
0KB
Program Code
(free)
1KB
2KB
15KB
16KB
Heap
Stack
Address Space
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 7

Address Space: Heap 
 Why do processes need dynamic allocation of memory? 
 Heap: allocate memory from any random location
 malloc in C language, new in OO language
 consists of allocated areas and free areas 
 End up with small chunks of free space - fragmentation
 What is OS’s role in managing heap?
 OS gives big chunk of free memory to process 
 library manages individual allocations 
7
Free
Free
Alloc
Alloc
16 bytes
24 bytes
12bytes
16 bytes
A
B
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 8

Quiz
 Match the Address Location
8
int
 x;
int
 main(
int
 argc
, char *
argv
[]) {
int
 y;
int
 *z = 
malloc
(
sizeof
(
int
)););
}
Address Location
x
main
y
z
*z
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 9

Virtual Address
 Every address in a running program is virtual.
 CPU issues loads and stores to virtual addresses
 OS allocates memory and tracks location of processes
 Translation of virtual address to physical address done Memory Manage-
ment Unit (MMU)
9
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char *argv[]){
printf("location of code  : %p\n", (void *) main);
printf("location of heap  : %p\n", (void *) malloc(1));
int x = 3;
printf("location of stack : %p\n", (void *) &x);
return x;
}
A simple program that prints out addresses
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 10

Virtual Address(Cont.)
 The output in 64-bit Linux machine
10
location of code  : 0x40057d
location of heap  : 0xcf2010
location of stack : 0x7fff9ca45fcc
(free)
Code
(Text)
Stack
stack
heap
Address Space
Data
Heap
0x400000
0xcf2000
0x7fff9ca49000
0x401000
0xd13000
0x7fff9ca28000
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

## Page 11

 Disclaimer: This slide set has been adapted from the initial lecture slides for Operating 
System course in Computer Science Dept. at Hanyang University. This lecture slide set is 
for OSTEP book written by Remzi and Andrea at University of Wisconsin.
11Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 

