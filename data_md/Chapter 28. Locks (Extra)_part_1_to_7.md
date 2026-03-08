# Document: Chapter 28. Locks (Extra) (Pages 1 to 7)

## Page 3

void mutex_init (struct mutex *m) { m->lock = 0;}void mutex_lock (struct mutex *m) { while (m->lock ==1) //if the lock is held;m->lock = 1;}
void mutex_unlock (struct mutex *m) { m->lock = 0;}
Peterson's algorithm: Assume any two threads with thread id = 0,1
struct mutex {int wantCS[2] ; //  for each threadint turn; // whose turn it is to enter crit. sec.}
init (struct mutex* m) { m->wantCS[0]=0;m->wantCS[1]=0;
Does not work. Why?

## Page 4

m->wantCS[0]=0;m->wantCS[1]=0;turn = 0; //any random thread}void mutex_lock(struct mutex* m, int tid) {m->wantCS[tid]=1;m->turn = 1-tid;while (m->wantCS[1-tid] && (m->turn==1-tid)); // spin}void mutex_unlock(struct mutex* m, int tid) {m->wantCS[tid]= 0;}
Correctness: Mutual Exclusion1)No Deadlock2)No starvation -each thread waits for atmost one execution of others critical section3)
Quiz:What if we don’t use the turnvariable? i.e1)
What if we don’t use the wantCSvariable? i.e2)


## Page 5

What if we don’t use the wantCSvariable? i.e2)
3) What if each thread tries to assign turnto itself ? i.e
void mutex_lock(struct mutex* m, int tid) {m->wantCS[tid] = 1;   // declare intentm->turn = tid;         // set turn for selfwhile (m->wantCS[1-tid] && m->turn == 1-tid); //spin}
H/W support to build synchronization primitives: limited set of powerful instructions which can execute atomically.
Test & Set instruction (atomic exchange): c-style definition/representation of1)
Int xchg ( int * addr, int newval){ Int old = *addr;*addr = newval;Return old;}
struct mutex {int lock; // state 0 -free, 1 -held}

## Page 6

}
void mutex_init (struct mutex *m) { m->lock = 0;}void mutex_lock (struct mutex *m) { while (xchg (&m->lock, 1 ) == 1) //if the lock is held;}
void mutex_unlock (struct mutex *m) { m->lock = 0;}
Criteria: Mutual exclusion1.No deadlock or progress2.Starvation /fairness3.
Another HW instruction: atomic increment "Fetch & Add"
Int Fetch&Add( int * addr){ Int old=*addr;*addr=*addr+1;return old;}
struct mutex {int turn; Unsigned int ticket;

## Page 7

struct mutex {int turn; Unsigned int ticket;}void mutex_init (struct mutex *m) { m->turn = 0; m->ticket =0;}void mutex_lock (struct mutex *m) { Int myturn=Fetch&Add(&m->ticket); while (myturn! = m->turn) //if the lock is held;//spin}
void mutex_unlock (struct mutex *m) { m->turn = m->turn +1;}

