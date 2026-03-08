# Document: Chapter 32. Deadlocks (Common_Conc_Problems) (Pages 41 to 53)

## Page 41

Banker's Example (change 1)
P1 requests (1  0  2)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2
P1 3  0  2 3  2  2 2  3  0
P2 3  0  2 9  0  2
P3 2  1  1 2  2  2
P4 0  0  2 4  3  3
By sanctioning P1’s request 
does the system remains in 
safe state?
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 41

## Page 42

Banker's Example (change 1)
P1 requests (1  0  2)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2
P1 3  2  2 3  2  2 2  3  0
P2 3  0  2 9  0  2 2  1  0
P3 2  1  1 2  2  2
P4 0  0  2 4  3  3
Safe Order:  P1, 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 42

## Page 43

Banker's Example (change 1)
P1 requests (1  0  2)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2
P1 0  0  0 3  2  2 2  3  0
P2 3  0  2 9  0  2 2  1  0
P3 2  1  1 2  2  2 5  3  2
P4 0  0  2 4  3  3 Safe Order:  P1, 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 43

## Page 44

Banker's Example (change 1)
P1 requests (1  0  2)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2
P1 0  0  0 3  2  2 2  3  0
P2 3  0  2 9  0  2 2  1  0
P3 2  2  2 2  2  2 5  3  2
P4 0  0  2 4  3  3 5  2  1 Safe Order:  P1, P3,
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 44

## Page 45

Banker's Example (change 1)
P1 requests (1  0  2)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2 7  4  3
P1 0  0  0 3  2  2 2  3  0
P2 3  0  2 9  0  2 2  1  0
P3 0  0  0 2  2  2 5  3  2
P4 0  0  2 4  3  3 5  2  1 Safe Order:  P1, P3,
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 45

## Page 46

Banker's Example (change 1)
P1 requests (1  0  2)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2 7  4  3
P1 0  0  0 3  2  2 2  3  0 3  1  2
P2 3  0  2 9  0  2 2  1  0
P3 0  0  0 2  2  2 5  3  2
P4 4  3  3 4  3  3 5  2  1 Safe Order:  P1, P3, P4, 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 46

## Page 47

Banker's Example (change 1)
P1 requests (1  0  2)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2 7  4  3
P1 0  0  0 3  2  2 2  3  0 3  1  2
P2 3  0  2 9  0  2 2  1  0 7  4  5
P3 0  0  0 2  2  2 5  3  2
P4 0  0  0 4  3  3 5  2  1 Safe Order:  P1, P3, P4, 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 47

## Page 48

Banker's Example (change 1)
P1 requests (1  0  2)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 7  5  3 7  5  3 3  3  2 7  4  3
P1 0  0  0 3  2  2 2  3  0 3  1  2
P2 3  0  2 9  0  2 2  1  0 7  4  5
P3 0  0  0 2  2  2 5  3  2 0  0  2
P4 0  0  0 4  3  3 5  2  1 Safe Order:  P1, P3, P4, P0, 
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 48

## Page 49

Banker's Example (change 1)
P1 requests (1  0  2)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  0  0 7  5  3 3  3  2 7  4  3
P1 0  0  0 3  2  2 2  3  0 3  1  2
P2 3  0  2 9  0  2 2  1  0 7  4  5
P3 0  0  0 2  2  2 5  3  2 0  0  2
P4 0  0  0 4  3  3 5  2  1 7  5  5
Safe Order:  P1, P3, P4, P0, P2 !!!  OK
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 49

## Page 50

Banker's Example (change 2)
P4 requests (3  3  0)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2
P1 2  0  0 3  2  2
P2 3  0  2 9  0  2
P3 2  1  1 2  2  2
P4 0  0  2 4  3  3
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 50

## Page 51

Banker's Example (change 2)
P4 requests (3  3  0)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2
P1 2  0  0 3  2  2 0  0  2
P2 3  0  2 9  0  2
P3 2  1  1 2  2  2
P4 3  3  2 4  3  3
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 51

## Page 52

Banker's Example (change 2)
P4 requests (3  3  0)
Allocate Max Avail.
A  B  C A  B  C A  B  C
P0 0  1  0 7  5  3 3  3  2
P1 2  0  0 3  2  2 0  0  2
P2 3  0  2 9  0  2
P3 2  1  1 2  2  2
P4 0  0  2 4  3  3
No job can be completed.  
No Safe Order exists!
Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur 52

## Page 53

Deadlock Detection and Recovery
 Allow deadlock to occasionally occur and then take some action.
 Example: if an OS froze, you would reboot it.
 Many database systems employ deadlock detection and recovery 
technique.
 A deadlock detector runs periodically.
 Building a resource graph and checking it for cycles (for single instances 
of resource).
 Variant of banker’s algorithm to detect deadlock (for multiple instances)
 In deadlock, the system need to be rolled back to previous safe state or 
restarted.
53Operating Systems by Dr. Praveen Kumar @ CSED, VNIT Nagpur

