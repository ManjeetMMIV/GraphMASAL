# Document: Chapter 31. Semaphore (Pages 41 to 47)

## Page 41

 Reader-writer problem with writer preference (i.e, no starvation for a 
waiting writer)
 Using mutex and CV
41
readLock:
lock(mutex)
while(writer_present || writers_waiting > 0)
wait(reader_can_enter,mutex)
readcount++
unlock(mutex)
readUnlock:
lock(mutex)
readcount--
if(readcount==0)
signal(writer_can_enter)
unlock(mutex)
writeLock:
lock(mutex)
writer_waiting++
while(readcount > 0 || writer_present)
wait(writer_can_enter, mutex)
writer_waiting--
writer_present = true
unlock(mutex)
writeUnlock:
lock(mutex)
writer_present = false
if(writer_waiting==0)
signal(reader_can_enter)
else
signal(writer_can_enter)

## Page 42

 Reader-writer problem with writer preference (i.e, no starvation for a w
aiting writer) – using     Semaphores only
42
1 typedef struct _rwlock_t { 
2 int readersCount;   // Number of readers arrived
3 int writersCount; // Number of writers arrived
4 sem_t Rlock; // Lock for readers, also used by writer to block all 
incoming readers
5 sem_t writelock; // Mutex for writers
6 sem_t readlock; // Mutex for readers
7 sem_t resource; // Mutex for managing critical section (i.e. only 1 write 
at a time) 
8 } rwlock_t; 
9
10 void rwlock_init(rwlock_t *rw) { 
11 sem_init(&rw->Rlock, 0, 1);
12 sem_init(&rw->readlock, 0, 1);
13 sem_init(&rw>writelock, 0, 1);
14 sem_init(&rw->resource, 0, 1);
15 rw->writersCount = 0;
16 rw->readersCount = 0; 
17} 

## Page 43

43
14 void rwlock_acquire_writelock(rwlock_t *rw) { 
15 …
16 } 
17
18 void rwlock_release_writelock(rwlock_t *rw) { 
19 …
20 }
21
13void rwlock_acquire_readlock(rwlock_t *rw) { 
14 …
14 } 
15
16 void rwlock_release_readlock(rwlock_t *rw) { 
17… 
18 } 

## Page 44

44
14 void rwlock_acquire_writelock(rwlock_t *rw) { 
15 // Increament writers count and lock 'Rlock' to block further readers to 
start reading
16sem_wait(& rw-> writelock);
17rw->writersCount++;
18if (rw-> writersCount == 1) // First writer will block upcoming 
readers
19 sem_wait(& rw-> Rlock);
20sem_post(& rw-> writelock);
21sem_wait(& rw-> resource); // Lock the resource for writing 
22 } 
23
24 void rwlock_release_writelock(rwlock_t *rw) { 
25 sem_post(& rw-> resource); // Free up the resource
26// Decreament writers count and free up 'Rlock' to allow upcoming readers to 
read
27 sem_wait(& rw-> writelock);
28 rw-> writersCount--;
29 if(rw-> writersCount == 0) // Last writer will free up 
'Rlock’
30 sem_post(& rw-> Rlock);
31 sem_post(& rw-> writelock);
32 }
21

## Page 45

45
13void rwlock_acquire_readlock(rwlock_t *rw) { 
14// wait till resource becomes available and Increment readers count 
15sem_wait(&rw->Rlock); //new sem blocks reader if writer waiting
16sem_wait(& rw-> readlock);
17rw-> readersCount++;
18if (rw-> readersCount == 1)
19 sem_wait(& rw-> resource); // First reader will lock the resource for any 
writer 
20sem_post(& rw-> readlock);
21sem_post(& rw-> Rlock); // release the new sem for other readers to try getting 
in
22} 
15
16 void rwlock_release_readlock(rwlock_t *rw) { 
17// Decreament readers count and free up the resource if all readers in queue 
finish reading 
18sem_wait(& rw-> readlock);   
19rw-> readersCount--;
20if (rw-> readersCount == 0) 
21 sem_post(& rw-> resource); // Last reader will releases the 
resource 
22sem_post(& rw-> readlock); 
23 } 

## Page 46

The Sleeping-Barber Problem. A barbershop consists of a waiting room with n chairs and th
e barber room containing the barber chair. If there are no customers to be served, the barber go
es to sleep. If a customer enters the barbershop and all cha-irs are occupied, then the customer 
leaves the shop. If the barber is busy but chairs are available, then the customer sits in one of t
he free chairs. If the barber is asleep, the customer wakes up the barber. Write a pseudocode us
ing semaphores to   coordinate the barber and the customers (each customer should be a differ
ent thread).
46


## Page 47

 semaphore mutex = 1, customers = 0, barber = 0;
 int waiting_count = 0;
47
Customer:
wait(mutex)
if(waiting_count == 
N)
signal(mutex)
leave();
waiting_count++
signal(mutex)
signal(customers)
wait(barber)
getHairCut();
signal(mutex)
waiting_count--
wait(mutex)
Barber:
signal (barber)
wait (customers)
cutHair();

