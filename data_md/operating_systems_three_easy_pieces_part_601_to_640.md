# Document: operating_systems_three_easy_pieces (Pages 601 to 640)

## Page 601

SUN ’ S NETWORK FILE SYSTEM (NFS) 565
of the ﬁle along with the offset within the ﬁle and number of bytes to read.
The server then will be able to issue the read (after all, the h andle tells the
server which volume and which inode to read from, and the offs et and
count tells it which bytes of the ﬁle to read) and return the da ta to the
client (or an error if there was a failure). WRITE is handled s imilarly ,
except the data is passed from the client to the server, and ju st a success
code is returned.
One last interesting protocol message is the GETATTR request; given a
ﬁle handle, it simply fetches the attributes for that ﬁle, in cluding the last
modiﬁed time of the ﬁle. We will see why this protocol request is impor-
tant in NFSv2 below when we discuss caching (can you guess why ?).
48.6 From Protocol to Distributed File System
Hopefully you are now getting some sense of how this protocol is
turned into a ﬁle system across the client-side ﬁle system an d the ﬁle
server. The client-side ﬁle system tracks open ﬁles, and gen erally trans-
lates application requests into the relevant set of protoco l messages. The
server simply responds to each protocol message, each of whi ch has all
the information needed to complete request.
For example, let us consider a simple application which read s a ﬁle.
In the diagram (Figure 48.1), we show what system calls the application
makes, and what the client-side ﬁle system and ﬁle server do i n respond-
ing to such calls.
A few comments about the ﬁgure. First, notice how the client t racks all
relevant state for the ﬁle access, including the mapping of the integer ﬁle
descriptor to an NFS ﬁle handle as well as the current ﬁle poin ter. This
enables the client to turn each read request (which you may ha ve noticed
do not specify the offset to read from explicitly) into a properly- formatted
read protocol message which tells the server exactly which b ytes from
the ﬁle to read. Upon a successful read, the client updates th e current
ﬁle position; subsequent reads are issued with the same ﬁle h andle but a
different offset.
Second, you may notice where server interactions occur. Whe n the ﬁle
is opened for the ﬁrst time, the client-side ﬁle system sends a LOOKUP
request message. Indeed, if a long pathname must be traverse d (e.g.,
/home/remzi/foo.txt), the client would send three LOOKUPs: one
to look up home in the directory /, one to look up remzi in home, and
ﬁnally one to look up foo.txt in remzi.
Third, you may notice how each server request has all the info rmation
needed to complete the request in its entirety . This design p oint is critical
to be able to gracefully recover from server failure, as we will now discuss
in more detail; it ensures that the server does not need state to be able to
respond to the request.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 602

566 SUN ’ S NETWORK FILE SYSTEM (NFS)
Client Server
fd = open(”/foo”, ...);
Send LOOKUP (rootdir FH, ”foo”)
Receive LOOKUP request
look for ”foo” in root dir
return foo’s FH + attributes
Receive LOOKUP reply
allocate ﬁle desc in open ﬁle table
store foo’s FH in table
store current ﬁle position (0)
return ﬁle descriptor to application
read(fd, buffer, MAX);
Index into open ﬁle table with fd
get NFS ﬁle handle (FH)
use current ﬁle position as offset
Send READ (FH, offset=0, count=MAX)
Receive READ request
use FH to get volume/inode num
read inode from disk (or cache)
compute block location (using offset)
read data from disk (or cache)
return data to client
Receive READ reply
update ﬁle position (+bytes read)
set current ﬁle position = MAX
return data/error code to app
read(fd, buffer, MAX);
Same except offset=MAX and set current ﬁle position = 2*MAX
read(fd, buffer, MAX);
Same except offset=2*MAX and set current ﬁle position = 3*MA X
close(fd);
Just need to clean up local structures
Free descriptor ”fd” in open ﬁle table
(No need to talk to server)
Table 48.1: Reading A File: Client-side And File Server Actions
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 603

SUN ’ S NETWORK FILE SYSTEM (NFS) 567
TIP : I DEMPOTENCY IS POWERFUL
Idempotency is a useful property when building reliable systems. When
an operation can be issued more than once, it is much easier to handle
failure of the operation; you can just retry it. If an operati on is not idem-
potent, life becomes more difﬁcult.
48.7 Handling Server Failure with Idempotent Operations
When a client sends a message to the server, it sometimes does not re-
ceive a reply . There are many possible reasons for this failu re to respond.
In some cases, the message may be dropped by the network; netw orks do
lose messages, and thus either the request or the reply could be lost and
thus the client would never receive a response.
It is also possible that the server has crashed, and thus is no t currently
responding to messages. After a bit, the server will be reboo ted and start
running again, but in the meanwhile all requests have been lo st. In all of
these cases, clients are left with a question: what should th ey do when
the server does not reply in a timely manner?
In NFSv2, a client handles all of these failures in a single, u niform, and
elegant way: it simply retries the request. Speciﬁcally , after sending the
request, the client sets a timer to go off after a speciﬁed tim e period. If a
reply is received before the timer goes off, the timer is canc eled and all is
well. If, however, the timer goes off before any reply is received, the client
assumes the request has not been processed and resends it. If the server
replies, all is well and the client has neatly handled the pro blem.
The ability of the client to simply retry the request (regard less of what
caused the failure) is due to an important property of most NF S requests:
they are idempotent. An operation is called idempotent when the effect
of performing the operation multiple times is equivalent to the effect of
performing the operating a single time. For example, if you s tore a value
to a memory location three times, it is the same as doing so onc e; thus
“store value to memory” is an idempotent operation. If, howe ver, you in-
crement a counter three times, it results in a different amou nt than doing
so just once; thus, “increment counter” is not idempotent. M ore gener-
ally , any operation that just reads data is obviously idempo tent; an oper-
ation that updates data must be more carefully considered to determine
if it has this property .
The heart of the design of crash recovery in NFS is the idempot ency
of most common operations. LOOKUP and READ requests are triv ially
idempotent, as they only read information from the ﬁle serve r and do not
update it. More interestingly , WRITE requests are also idem potent. If,
for example, a WRITE fails, the client can simply retry it. Th e WRITE
message contains the data, the count, and (importantly) the exact offset
to write the data to. Thus, it can be repeated with the knowled ge that the
outcome of multiple writes is the same as the outcome of a sing le one.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 604

568 SUN ’ S NETWORK FILE SYSTEM (NFS)
Case 1: Request Lost
Client
[send request]
Server
(no mesg)
Case 2: Server Down
Client
[send request]
Server
(down)
Case 3: Reply lost on way back from Server
Client
[send request]
Server
[recv request]
[handle request]
[send reply]
Figure 48.5: The Three Types of Loss
In this way , the client can handle all timeouts in a uniﬁed way . If a
WRITE request was simply lost (Case 1 above), the client will retry it, the
server will perform the write, and all will be well. The same w ill happen
if the server happened to be down while the request was sent, b ut back
up and running when the second request is sent, and again all w orks
as desired (Case 2). Finally , the server may in fact receive t he WRITE
request, issue the write to its disk, and send a reply . This re ply may get
lost (Case 3), again causing the client to re-send the reques t. When the
server receives the request again, it will simply do the exac t same thing:
write the data to disk and reply that it has done so. If the clie nt this time
receives the reply , all is again well, and thus the client has handled both
message loss and server failure in a uniform manner. Neat!
A small aside: some operations are hard to make idempotent. F or
example, when you try to make a directory that already exists , you are
informed that the mkdir request has failed. Thus, in NFS, if t he ﬁle server
receives a MKDIR protocol message and executes it successfu lly but the
reply is lost, the client may repeat it and encounter that fai lure when in
fact the operation at ﬁrst succeeded and then only failed on t he retry .
Thus, life is not perfect.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 605

SUN ’ S NETWORK FILE SYSTEM (NFS) 569
TIP : P ERFECT IS THE ENEMY OF THE GOOD (V OLTAIRE ’ S LAW)
Even when you design a beautiful system, sometimes all the co rner cases
don’t work out exactly as you might like. Take the mkdir examp le above;
one could redesign mkdir to have different semantics, thus m aking it
idempotent (think about how you might do so); however, why bo ther?
The NFS design philosophy covers most of the important cases, and over-
all makes the system design clean and simple with regards to f ailure.
Thus, accepting that life isn’t perfect and still building t he system is a sign
of good engineering. Apparently , this wisdom is attributed to V oltaire,
for saying “... a wise Italian says that the best is the enemy o f the good”
[V72], and thus we call it V oltaire’s Law.
48.8 Improving Performance: Client-side Caching
Distributed ﬁle systems are good for a number of reasons, but sending
all read and write requests across the network can lead to a bi g perfor-
mance problem: the network generally isn’t that fast, espec ially as com-
pared to local memory or disk. Thus, another problem: how can we im-
prove the performance of a distributed ﬁle system?
The answer, as you might guess from reading the big bold words in
the sub-heading above, is client-side caching. The NFS client-side ﬁle
system caches ﬁle data (and metadata) that it has read from th e server in
client memory . Thus, while the ﬁrst access is expensive (i.e ., it requires
network communication), subsequent accesses are serviced quite quickly
out of client memory .
The cache also serves as a temporary buffer for writes. When a client
application ﬁrst writes to a ﬁle, the client buffers the data in client mem-
ory (in the same cache as the data it read from the ﬁle server) b efore writ-
ing the data out to the server. Such write buffering is useful because it de-
couples application write() latency from actual write performance, i.e.,
the application’s call to write() succeeds immediately (and just puts
the data in the client-side ﬁle system’s cache); only later d oes the data get
written out to the ﬁle server.
Thus, NFS clients cache data and performance is usually grea t and
we are done, right? Unfortunately , not quite. Adding cachin g into any
sort of system with multiple client caches introduces a big a nd interesting
challenge which we will refer to as the cache consistency problem .
48.9 The Cache Consistency Problem
The cache consistency problem is best illustrated with two c lients and
a single server. Imagine client C1 reads a ﬁle F, and keeps a co py of the
ﬁle in its local cache. Now imagine a different client, C2, ov erwrites the
ﬁle F, thus changing its contents; let’s call the new version of the ﬁle F
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 606

570 SUN ’ S NETWORK FILE SYSTEM (NFS)
C1
cache: F[v1]
C2
cache: F[v2]
C3
cache: empty
Server S
disk: F[v1] at first
      F[v2] eventually
Figure 48.6: The Cache Consistency Problem
(version 2), or F[v2] and the old version F[v1] so we can keep t he two
distinct (but of course the ﬁle has the same name, just differ ent contents).
Finally , there is a third client, C3, which has not yet access ed the ﬁle F.
You can probably see the problem that is upcoming (Figure 48.6). In
fact, there are two subproblems. The ﬁrst subproblem is that the client C2
may buffer its writes in its cache for a time before propagating them to the
server; in this case, while F[v2] sits in C2’s memory , any acc ess of F from
another client (say C3) will fetch the old version of the ﬁle ( F[v1]). Thus,
by buffering writes at the client, other clients may get stal e versions of the
ﬁle, which may be undesirable; indeed, imagine the case wher e you log
into machine C2, update F, and then log into C3 and try to read t he ﬁle,
only to get the old copy! Certainly this could be frustrating . Thus, let us
call this aspect of the cache consistency problem update visibility; when
do updates from one client become visible at other clients?
The second subproblem of cache consistency is a stale cache ; in this
case, C2 has ﬁnally ﬂushed its writes to the ﬁle server, and th us the server
has the latest version (F[v2]). However, C1 still has F[v1] i n its cache; if a
program running on C1 reads ﬁle F, it will get a stale version ( F[v1]) and
not the most recent copy (F[v2]), which is (often) undesirab le.
NFSv2 implementations solve these cache consistency problems in two
ways. First, to address update visibility , clients impleme nt what is some-
times called ﬂush-on-close (a.k.a., close-to-open) consistency semantics;
speciﬁcally , when a ﬁle is written to and subsequently close d by a client
application, the client ﬂushes all updates (i.e., dirty pag es in the cache)
to the server. With ﬂush-on-close consistency , NFS ensures that a subse-
quent open from another node will see the latest ﬁle version.
Second, to address the stale-cache problem, NFSv2 clients ﬁ rst check
to see whether a ﬁle has changed before using its cached contents. Speciﬁ-
cally , when opening a ﬁle, the client-side ﬁle system will issue a GETATTR
request to the server to fetch the ﬁle’s attributes. The attr ibutes, impor-
tantly , include information as to when the ﬁle was last modiﬁ ed on the
server; if the time-of-modiﬁcation is more recent than the t ime that the
ﬁle was fetched into the client cache, the client invalidates the ﬁle, thus
removing it from the client cache and ensuring that subseque nt reads will
go to the server and retrieve the latest version of the ﬁle. If , on the other
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 607

SUN ’ S NETWORK FILE SYSTEM (NFS) 571
hand, the client sees that it has the latest version of the ﬁle , it will go
ahead and use the cached contents, thus increasing performa nce.
When the original team at Sun implemented this solution to th e stale-
cache problem, they realized a new problem; suddenly , the NF S server
was ﬂooded with GETATTR requests. A good engineering princi ple to
follow is to design for the common case, and to make it work well; here,
although the common case was that a ﬁle was accessed only from a sin-
gle client (perhaps repeatedly), the client always had to se nd GETATTR
requests to the server to make sure no one else had changed the ﬁle. A
client thus bombards the server, constantly asking “has any one changed
this ﬁle?”, when most of the time no one had.
To remedy this situation (somewhat), an attribute cache was added
to each client. A client would still validate a ﬁle before acc essing it, but
most often would just look in the attribute cache to fetch the attributes.
The attributes for a particular ﬁle were placed in the cache w hen the ﬁle
was ﬁrst accessed, and then would timeout after a certain amo unt of time
(say 3 seconds). Thus, during those three seconds, all ﬁle ac cesses would
determine that it was OK to use the cached ﬁle and thus do so wit h no
network communication with the server.
48.10 Assessing NFS Cache Consistency
A few ﬁnal words about NFS cache consistency . The ﬂush-on-close be-
havior was added to “make sense”, but introduced a certain pe rformance
problem. Speciﬁcally , if a temporary or short-lived ﬁle was created on a
client and then soon deleted, it would still be forced to the s erver. A more
ideal implementation might keep such short-lived ﬁles in me mory until
they are deleted and thus remove the server interaction enti rely , perhaps
increasing performance.
More importantly , the addition of an attribute cache into NF S made
it very hard to understand or reason about exactly what versi on of a ﬁle
one was getting. Sometimes you would get the latest version; sometimes
you would get an old version simply because your attribute ca che hadn’t
yet timed out and thus the client was happy to give you what was in
client memory . Although this was ﬁne most of the time, it woul d (and
still does!) occasionally lead to odd behavior.
And thus we have described the oddity that is NFS client cachi ng.
It serves as an interesting example where details of an imple mentation
serve to deﬁne user-observable semantics, instead of the other way around.
48.11 Implications on Server-Side Write Buffering
Our focus so far has been on client caching, and that is where m ost
of the interesting issues arise. However, NFS servers tend t o be well-
equipped machines with a lot of memory too, and thus they have caching
concerns as well. When data (and metadata) is read from disk, NFS
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 608

572 SUN ’ S NETWORK FILE SYSTEM (NFS)
servers will keep it in memory , and subsequent reads of said d ata (and
metadata) will not go to disk, a potential (small) boost in pe rformance.
More intriguing is the case of write buffering. NFS servers a bsolutely
may not return success on a WRITE protocol request until the write ha s
been forced to stable storage (e.g., to disk or some other persistent device).
While they can place a copy of the data in server memory , retur ning suc-
cess to the client on a WRITE protocol request could result in incorrect
behavior; can you ﬁgure out why?
The answer lies in our assumptions about how clients handle s erver
failure. Imagine the following sequence of writes as issued by a client:
write(fd, a_buffer, size); // fill first block with a’s
write(fd, b_buffer, size); // fill second block with b’s
write(fd, c_buffer, size); // fill third block with c’s
These writes overwrite the three blocks of a ﬁle with a block o f a’s,
then b’s, and then c’s. Thus, if the ﬁle initially looked like this:
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
We might expect the ﬁnal result after these writes to be like t his, with the
x’s, y’s, and z’s, would be overwritten with a’s, b’s, and c’s , respectively .
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
Now let’s assume for the sake of the example that these three c lient
writes were issued to the server as three distinct WRITE prot ocol mes-
sages. Assume the ﬁrst WRITE message is received by the serve r and
issued to the disk, and the client informed of its success. No w assume
the second write is just buffered in memory , and the server al so reports
it success to the client before forcing it to disk; unfortunately , the server
crashes before writing it to disk. The server quickly restar ts and receives
the third write request, which also succeeds.
Thus, to the client, all the requests succeeded, but we are su rprised
that the ﬁle contents look like this:
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy <--- oops
cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
Yikes! Because the server told the client that the second wri te was
successful before committing it to disk, an old chunk is left in the ﬁle,
which, depending on the application, might be catastrophic .
To avoid this problem, NFS servers must commit each write to stable
(persistent) storage before informing the client of succes s; doing so en-
ables the client to detect server failure during a write, and thus retry until
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 609

SUN ’ S NETWORK FILE SYSTEM (NFS) 573
it ﬁnally succeeds. Doing so ensures we will never end up with ﬁle con-
tents intermingled as in the above example.
The problem that this requirement gives rise to in NFS server im-
plementation is that write performance, without great care , can be the
major performance bottleneck. Indeed, some companies (e.g ., Network
Appliance) came into existence with the simple objective of building an
NFS server that can perform writes quickly; one trick they us e is to ﬁrst
put writes in a battery-backed memory , thus enabling to quic kly reply
to WRITE requests without fear of losing the data and without the cost
of having to write to disk right away; the second trick is to us e a ﬁle sys-
tem design speciﬁcally designed to write to disk quickly whe n one ﬁnally
needs to do so [HLM94, RO91].
48.12 Summary
We have seen the introduction of the NFS distributed ﬁle syst em. NFS
is centered around the idea of simple and fast recovery in the face of
server failure, and achieves this end through careful protocol design. Idem-
potency of operations is essential; because a client can saf ely replay a
failed operation, it is OK to do so whether or not the server ha s executed
the request.
We also have seen how the introduction of caching into a multi ple-
client, single-server system can complicate things. In par ticular, the sys-
tem must resolve the cache consistency problem in order to be have rea-
sonably; however, NFS does so in a slightly ad hoc fashion whi ch can
occasionally result in observably weird behavior. Finally , we saw how
server caching can be tricky: writes to the server must be for ced to stable
storage before returning success (otherwise data can be los t).
We haven’t talked about other issues which are certainly rel evant, no-
tably security . Security in early NFS implementations was r emarkably
lax; it was rather easy for any user on a client to masquerade a s other
users and thus gain access to virtually any ﬁle. Subsequent i ntegration
with more serious authentication services (e.g., Kerberos [NT94]) have
addressed these obvious deﬁciencies.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 610

574 SUN ’ S NETWORK FILE SYSTEM (NFS)
References
[S86] “The Sun Network File System: Design, Implementation and Experience”
Russel Sandberg
USENIX Summer 1986
The original NFS paper; though a bit of a challenging read, it is worthwhile to see the source of these
wonderful ideas.
[NT94] “Kerberos: An Authentication Service for Computer N etworks”
B. Clifford Neuman, Theodore Ts’o
IEEE Communications, 32(9):33-38, September 1994
Kerberos is an early and hugely inﬂuential authentication s ervice. We probably should write a book
chapter about it sometime...
[P+94] “NFS V ersion 3: Design and Implementation”
Brian Pawlowski, Chet Juszczak, Peter Staubach, Carl Smith , Diane Lebel, Dave Hitz
USENIX Summer 1994, pages 137-152
The small modiﬁcations that underlie NFS version 3.
[P+00] “The NFS version 4 protocol”
Brian Pawlowski, David Noveck, David Robinson, Robert Thur low
2nd International System Administration and Networking Co nference (SANE 2000)
Undoubtedly the most literary paper on NFS ever written.
[C00] “NFS Illustrated”
Brent Callaghan
Addison-Wesley Professional Computing Series, 2000
A great NFS reference; incredibly thorough and detailed per the protocol itself.
[Sun89] “NFS: Network File System Protocol Speciﬁcation”
Sun Microsystems, Inc. Request for Comments: 1094, March 19 89
Available: http://www.ietf.org/rfc/rfc1094.txt
The dreaded speciﬁcation; read it if you must, i.e., you are g etting paid to read it. Hopefully, paid a lot.
Cash money!
[O91] “The Role of Distributed State”
John K. Ousterhout
Available: ftp://ftp.cs.berkeley .edu/ucb/sprite/papers/state.ps
A rarely referenced discussion of distributed state; a broa der perspective on the problems and challenges.
[HLM94] “File System Design for an NFS File Server Appliance ”
Dave Hitz, James Lau, Michael Malcolm
USENIX Winter 1994. San Francisco, California, 1994
Hitz et al. were greatly inﬂuenced by previous work on log-st ructured ﬁle systems.
[RO91] “The Design and Implementation of the Log-structure d File System”
Mendel Rosenblum, John Ousterhout
Symposium on Operating Systems Principles (SOSP), 1991
LFS again. No, you can never get enough LFS.
[V72] “La Begueule”
Francois-Marie Arouet a.k.a. V oltaire
Published in 1772
Voltaire said a number of clever things, this being but one ex ample. For example, Voltaire also said “If
you have two religions in your land, the two will cut each othe rs throats; but if you have thirty religions,
they will dwell in peace.” What do you say to that, Democrats a nd Republicans?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 611

49
The Andrew File System (AFS)
The Andrew File System was introduced by researchers at Carnegie-Mellon
University (CMU) in the 1980’s [H+88]. Led by the well-known Profes-
sor M. Satyanarayanan of Carnegie-Mellon University (“Satya” for short),
the main goal of this project was simple: scale. Speciﬁcally , how can one
design a distributed ﬁle system such that a server can suppor t as many
clients as possible?
Interestingly , there are numerous aspects of design and imp lementa-
tion that affect scalability . Most important is the design of the protocol be-
tween clients and servers. In NFS, for example, the protocol forces clients
to check with the server periodically to determine if cached contents have
changed; because each check uses server resources (includi ng CPU and
network bandwidth), frequent checks like this will limit th e number of
clients a server can respond to and thus limit scalability .
AFS also differs from NFS in that from the beginning, reasona ble user-
visible behavior was a ﬁrst-class concern. In NFS, cache con sistency is
hard to describe because it depends directly on low-level im plementa-
tion details, including client-side cache timeout interva ls. In AFS, cache
consistency is simple and readily understood: when the ﬁle i s opened, a
client will generally receive the latest consistent copy fr om the server.
49.1 AFS V ersion 1
We will discuss two versions of AFS [H+88, S+85]. The ﬁrst ver sion
(which we will call AFSv1, but actually the original system w as called
the ITC distributed ﬁle system [S+85]) had some of the basic d esign in
place, but didn’t scale as desired, which led to a re-design a nd the ﬁnal
protocol (which we will call AFSv2, or just AFS) [H+88]. We no w discuss
the ﬁrst version.
One of the basic tenets of all versions of AFS is whole-ﬁle caching on
the local disk of the client machine that is accessing a ﬁle. When you
open() a ﬁle, the entire ﬁle (if it exists) is fetched from the server and
stored in a ﬁle on your local disk. Subsequent application read() and
write() operations are redirected to the local ﬁle system where the ﬁle is
575

## Page 612

576 THE ANDREW FILE SYSTEM (AFS)
TestAuth Test whether a file has changed
(used to validate cached entries)
GetFileStat Get the stat info for a file
Fetch Fetch the contents of file
Store Store this file on the server
SetFileStat Set the stat info for a file
ListDir List the contents of a directory
Figure 49.1: AFSv1 Protocol Highlights
stored; thus, these operations require no network communication and are
fast. Finally , upon close(), the ﬁle (if it has been modiﬁed) is ﬂushed
back to the server. Note the obvious contrasts with NFS, whic h caches
blocks (not whole ﬁles, although NFS could of course cache every blo ck of
an entire ﬁle) and does so in client memory (not local disk).
Let’s get into the details a bit more. When a client applicati on ﬁrst calls
open(), the AFS client-side code (which the AFS designers call V enus)
would send a Fetch protocol message to the server. The Fetch p rotocol
message would pass the entire pathname of the desired ﬁle (fo r exam-
ple, /home/remzi/notes.txt) to the ﬁle server (the group of which
they called Vice), which would then traverse the pathname, ﬁnd the de-
sired ﬁle, and ship the entire ﬁle back to the client. The clie nt-side code
would then cache the ﬁle on the local disk of the client (by wri ting it to
local disk). As we said above, subsequent read() and write() system
calls are strictly local in AFS (no communication with the server occurs);
they are just redirected to the local copy of the ﬁle. Because the read()
and write() calls act just like calls to a local ﬁle system, once a block
is accessed, it also may be cached in client memory . Thus, AFS also uses
client memory to cache copies of blocks that it has in its loca l disk. Fi-
nally , when ﬁnished, the AFS client checks if the ﬁle has been modiﬁed
(i.e., that it has been opened for writing); if so, it ﬂushes t he new version
back to the server with a Store protocol message, sending the entire ﬁle
and pathname to the server for permanent storage.
The next time the ﬁle is accessed, AFSv1 does so much more efﬁ-
ciently . Speciﬁcally , the client-side code ﬁrst contacts t he server (using
the TestAuth protocol message) in order to determine whethe r the ﬁle
has changed. If not, the client would use the locally-cached copy , thus
improving performance by avoiding a network transfer. The ﬁgure above
shows some of the protocol messages in AFSv1. Note that this e arly ver-
sion of the protocol only cached ﬁle contents; directories, for example,
were only kept at the server.
49.2 Problems with V ersion 1
A few key problems with this ﬁrst version of AFS motivated the de-
signers to rethink their ﬁle system. To study the problems in detail, the
designers of AFS spent a great deal of time measuring their ex isting pro-
totype to ﬁnd what was wrong. Such experimentation is a good t hing;
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 613

THE ANDREW FILE SYSTEM (AFS) 577
TIP : M EASURE THEN BUILD (PATTERSON ’ S LAW)
One of our advisors, David Patterson (of RISC and RAID fame), used to
always encourage us to measure a system and demonstrate a pro blem
before building a new system to ﬁx said problem. By using experimen-
tal evidence, rather than gut instinct, you can turn the proc ess of system
building into a more scientiﬁc endeavor. Doing so also has the fringe ben-
eﬁt of making you think about how exactly to measure the syste m before
your improved version is developed. When you do ﬁnally get ar ound to
building the new system, two things are better as a result: ﬁr st, you have
evidence that shows you are solving a real problem; second, y ou now
have a way to measure your new system in place, to show that it a ctually
improves upon the state of the art. And thus we call this Patterson’s Law .
measurement is the key to understanding how systems work and how to
improve them. Hard data helps take intuition and make into a c oncrete
science of deconstructing systems. In their study , the auth ors found two
main problems with AFSv1:
• Path-traversal costs are too high: When performing a Fetch or Store
protocol request, the client passes the entire pathname (e.g., /home/
remzi/notes.txt) to the server. The server, in order to access the
ﬁle, must perform a full pathname traversal, ﬁrst looking in the root
directory to ﬁnd home, then in home to ﬁnd remzi, and so forth,
all the way down the path until ﬁnally the desired ﬁle is locat ed.
With many clients accessing the server at once, the designers of AFS
found that the server was spending much of its CPU time simply
walking down directory paths.
• The client issues too many T estAuth protocol messages : Much
like NFS and its overabundance of GETATTR protocol messages ,
AFSv1 generated a large amount of trafﬁc to check whether a lo -
cal ﬁle (or its stat information) was valid with the TestAuth proto-
col message. Thus, servers spent much of their time telling c lients
whether it was OK to used their cached copies of a ﬁle. Most of t he
time, the answer was that the ﬁle had not changed.
There were actually two other problems with AFSv1: load was n ot
balanced across servers, and the server used a single distin ct process per
client thus inducing context switching and other overheads . The load
imbalance problem was solved by introducing volumes, which an ad-
ministrator could move across servers to balance load; the c ontext-switch
problem was solved in AFSv2 by building the server with threa ds instead
of processes. However, for the sake of space, we focus here on the main
two protocol problems above that limited the scale of the sys tem.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 614

578 THE ANDREW FILE SYSTEM (AFS)
49.3 Improving the Protocol
The two problems above limited the scalability of AFS; the se rver CPU
became the bottleneck of the system, and each server could on ly ser-
vice 20 clients without becoming overloaded. Servers were r eceiving too
many TestAuth messages, and when they received Fetch or Stor e mes-
sages, were spending too much time traversing the directory hierarchy .
Thus, the AFS designers were faced with a problem:
THE CRUX : H OW TO DESIGN A S CALABLE FILE PROTOCOL
How should one redesign the protocol to minimize the number o f
server interactions, i.e., how could they reduce the number of TestAuth
messages? Further, how could they design the protocol to mak e these
server interactions efﬁcient? By attacking both of these is sues, a new pro-
tocol would result in a much more scalable version AFS.
49.4 AFS V ersion 2
AFSv2 introduced the notion of a callback to reduce the number of
client/server interactions. A callback is simply a promise from the server
to the client that the server will inform the client when a ﬁle that the
client is caching has been modiﬁed. By adding this state to the server, the
client no longer needs to contact the server to ﬁnd out if a cac hed ﬁle is
still valid. Rather, it assumes that the ﬁle is valid until th e server tells it
otherwise; insert analogy to polling versus interrupts here.
AFSv2 also introduced the notion of a ﬁle identiﬁer (FID) (similar to
the NFS ﬁle handle ) instead of pathnames to specify which ﬁle a client
was interested in. An FID in AFS consists of a volume identiﬁe r, a ﬁle
identiﬁer, and a “uniquiﬁer” (to enable reuse of the volume a nd ﬁle IDs
when a ﬁle is deleted). Thus, instead of sending whole pathna mes to
the server and letting the server walk the pathname to ﬁnd the desired
ﬁle, the client would walk the pathname, one piece at a time, c aching the
results and thus hopefully reducing the load on the server.
For example, if a client accessed the ﬁle /home/remzi/notes.txt,
and home was the AFS directory mounted onto / (i.e., / was the local root
directory , but home and its children were in AFS), the client would ﬁrst
Fetch the directory contents of home, put them in the local-disk cache,
and setup a callback on home. Then, the client would Fetch the directory
remzi, put it in the local-disk cache, and setup a callback on the se rver
on remzi. Finally , the client would Fetch notes.txt, cache this regular
ﬁle in the local disk, setup a callback, and ﬁnally return a ﬁl e descriptor
to the calling application. See Table 49.1 for a summary .
The key difference, however, from NFS, is that with each fetc h of a
directory or ﬁle, the AFS client would establish a callback w ith the server,
thus ensuring that the server would notify the client of a cha nge in its
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 615

THE ANDREW FILE SYSTEM (AFS) 579
Client (C1) Server
fd = open(“/home/remzi/notes.txt”, ...);
Send Fetch (home FID, “remzi”)
Receive Fetch request
look for remzi in home dir
establish callback(C1) on remzi
return remzi’s content and FID
Receive Fetch reply
write remzi to local disk cache
record callback status of remzi
Send Fetch (remzi FID, “notes.txt”)
Receive Fetch request
look for notes.txt in remzi dir
establish callback(C1) on notes.txt
return notes.txt’s content and FID
Receive Fetch reply
write notes.txt to local disk cache
record callback status of notes.txt
local open() of cached notes.txt
return ﬁle descriptor to application
read(fd, buffer, MAX);
perform local read() on cached copy
close(fd);
do local close() on cached copy
if ﬁle has changed, ﬂush to server
fd = open(“/home/remzi/notes.txt”, ...);
Foreach dir (home, remzi)
if (callback(dir) == V ALID)
use local copy for lookup(dir)
else
Fetch (as above)
if (callback(notes.txt) == V ALID)
open local cached copy
return ﬁle descriptor to it
else
Fetch (as above) then open and return fd
Table 49.1: Reading A File: Client-side And File Server Actions
cached state. The beneﬁt is obvious: although the ﬁrst access to /home/
remzi/notes.txt generates many client-server messages (as described
above), it also establishes callbacks for all the directori es as well as the
ﬁle notes.txt, and thus subsequent accesses are entirely lo cal and require
no server interaction at all. Thus, in the common case where a ﬁle is
cached at the client, AFS behaves nearly identically to a loc al disk-based
ﬁle system. If one accesses a ﬁle more than once, the second ac cess should
be just as fast as accessing a ﬁle locally .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 616

580 THE ANDREW FILE SYSTEM (AFS)
ASIDE : CACHE CONSISTENCY IS NOT A P ANACEA
When discussing distributed ﬁle systems, much is made of the cache con-
sistency the ﬁle systems provide. However, this baseline consistency does
not solve all problems with regards to ﬁle access from multip le clients.
For example, if you are building a code repository , with mult iple clients
performing check-ins and check-outs of code, you can’t simp ly rely on
the underlying ﬁle system to do all of the work for you; rather , you have
to use explicit ﬁle-level locking in order to ensure that the “right” thing
happens when such concurrent accesses take place. Indeed, a ny applica-
tion that truly cares about concurrent updates will add extr a machinery
to handle conﬂicts. The baseline consistency described in this chapter and
the previous one are useful primarily for casual usage, i.e. , when a user
logs into a different client, they expect some reasonable ve rsion of their
ﬁles to show up there. Expecting more from these protocols is setting
yourself up for failure, disappointment, and tear-ﬁlled fr ustration.
49.5 Cache Consistency
When we discussed NFS, there were two aspects of cache consis tency
we considered: update visibility and cache staleness. With update visi-
bility , the question is: when will the server be updated witha new version
of a ﬁle? With cache staleness, the question is: once the serv er has a new
version, how long before clients see the new version instead of an older
cached copy?
Because of callbacks and whole-ﬁle caching, the cache consistency pro-
vided by AFS is easy to describe and understand. There are two im-
portant cases to consider: consistency between processes o n different ma-
chines, and consistency between processes on the same machine.
Between different machines, AFS makes updates visible at th e server
and invalidates cached copies at the exact same time, which i s when the
updated ﬁle is closed. A client opens a ﬁle, and then writes to it (perhaps
repeatedly). When it is ﬁnally closed, the new ﬁle is ﬂushed t o the server
(and thus visibile); the server then breaks callbacks for an y clients with
cached copies, thus ensuring that clients will no longer rea d stale copies
of the ﬁle; subsequent opens on those clients will require a r e-fetch of the
new version of the ﬁle from the server.
AFS makes an exception to this simple model between processe s on
the same machine. In this case, writes to a ﬁle are immediatel y visible to
other local processes (i.e., a process does not have to wait u ntil a ﬁle is
closed to see its latest updates). This makes using a single m achine be-
have exactly as you would expect, as this behavior is based up on typical
UNIX semantics. Only when switching to a different machine would you
be able to detect the more general AFS consistency mechanism .
There is one interesting cross-machine case that is worthy o f further
discussion. Speciﬁcally , in the rare case that processes on different ma-
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 617

THE ANDREW FILE SYSTEM (AFS) 581
Client1 Client2 Server Comments
P1 P2 Cache P 3 Cache Disk
open(F) - - - File created
write(A) A - -
close() A - A
open(F) A - A
read() → A A - A
close() A - A
open(F) A - A
write(B) B - A
open(F) B - A Local processes
read() → B B - A see writes immediately
close() B - A
B open(F) A A Remote processes
B read() → A A A do not see writes...
B close() A A
close() B A B ... until close()
B open(F) B B has taken place
B read() → B B B
B close() B B
B open(F) B B
open(F) B B B
write(D) D B B
D write(C) C B
D close() C C
close() D C D
D open(F) D D Unfortunately for P 3
D read() → D D D the last writer wins
D close() D D
Table 49.2: Cache Consistency Timeline
chines are modifying a ﬁle at the same time, AFS naturally emp loys what
is known as a last writer wins approach (which perhaps should be called
last closer wins ). Speciﬁcally , whichever client calls close() last will
update the entire ﬁle on the server last and thus will be the “w inning”
ﬁle, i.e., the ﬁle that remains on the server for others to see . The result is
a ﬁle that was generated in its entirety either by one client o r the other.
Note the difference from a block-based protocol like NFS: in NFS, writes
of individual blocks may be ﬂushed out to the server as each cl ient is up-
dating the ﬁle, and thus the ﬁnal ﬁle on the server could end up as a mix
of updates from both clients. In many cases, such a mixed ﬁle o utput
would not make much sense, i.e., imagine a JPEG image getting modi-
ﬁed by two clients in pieces; the resulting mix of writes woul d not likely
constitute a valid JPEG.
A timeline showing a few of these different scenarios can be s een in
Table 49.2. The columns of the table show the behavior of two processes
(P1 and P2) on Client1 and its cache state, one process (P 3) on Client2 and
its cache state, and the server (Server), all operating on a s ingle ﬁle called,
imaginatively ,F. For the server, the table just shows the contents of the
ﬁle after the operation on the left has completed. Read throu gh it and see
if you can understand why each read returns the results that i t does. A
commentary ﬁeld on the right will help you if you get stuck.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 618

582 THE ANDREW FILE SYSTEM (AFS)
49.6 Crash Recovery
From the description above, you might sense that crash recov ery is
more involved than with NFS. You would be right. For example, imagine
there is a short period of time where a server (S) is not able to contact
a client (C1), for example, while the client C1 is rebooting. While C1
is not available, S may have tried to send it one or more callba ck recall
messages; for example, imagine C1 had ﬁle F cached on its loca l disk, and
then C2 (another client) updated F, thus causing S to send mes sages to all
clients caching the ﬁle to remove it from their local caches. Because C1
may miss those critical messages when it is rebooting, upon r ejoining the
system, C1 should treat all of its cache contents as suspect. Thus, upon
the next access to ﬁle F, C1 should ﬁrst ask the server (with a T estAuth
protocol message) whether its cached copy of ﬁle F is still va lid; if so, C1
can use it; if not, C1 should fetch the newer version from the s erver.
Server recovery after a crash is also more complicated. The p roblem
that arises is that callbacks are kept in memory; thus, when a server re-
boots, it has no idea which client machine has which ﬁles. Thu s, upon
server restart, each client of the server must realize that t he server has
crashed and treat all of their cache contents as suspect, and (as above)
reestablish the validity of a ﬁle before using it. Thus, a ser ver crash is a
big event, as one must ensure that each client is aware of the c rash in a
timely manner, or risk a client accessing a stale ﬁle. There a re many ways
to implement such recovery; for example, by having the serve r send a
message (saying “don’t trust your cache contents!”) to each client when
it is up and running again, or by having clients check that the server is
alive periodically (with a heartbeat message, as it is called). As you can
see, there is a cost to building a more scalable and sensible caching model;
with NFS, clients hardly noticed a server crash.
49.7 Scale And Performance Of AFSv2
With the new protocol in place, AFSv2 was measured and found t o be
much more scalable that the original version. Indeed, each s erver could
support about 50 clients (instead of just 20). A further bene ﬁt was that
client-side performance often came quite close to local per formance, be-
cause in the common case, all ﬁle accesses were local; ﬁle rea ds usually
went to the local disk cache (and potentially , local memory). Only when a
client created a new ﬁle or wrote to an existing one was there need to send
a Store message to the server and thus update the ﬁle with new c ontents.
Let us also gain some perspective on AFS performance by compa ring
common ﬁle-system access scenarios with NFS. Table 49.3 shows the re-
sults of our qualitative comparison.
In the table, we examine typical read and write patterns anal ytically ,
for ﬁles of different sizes. Small ﬁles have Ns blocks in them; medium
ﬁles have Nm blocks; large ﬁles have NL blocks. We assume that small
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 619

THE ANDREW FILE SYSTEM (AFS) 583
Workload NFS AFS AFS/NFS
1. Small ﬁle, sequential read Ns · Lnet Ns · Lnet 1
2. Small ﬁle, sequential re-read Ns · Lmem Ns · Lmem 1
3. Medium ﬁle, sequential read Nm · Lnet Nm · Lnet 1
4. Medium ﬁle, sequential re-read Nm · Lmem Nm · Lmem 1
5. Large ﬁle, sequential read NL · Lnet NL · Lnet 1
6. Large ﬁle, sequential re-read NL · Lnet NL · Ldisk
Ldisk
Lnet
7. Large ﬁle, single read Lnet NL · Lnet NL
8. Small ﬁle, sequential write Ns · Lnet Ns · Lnet 1
9. Large ﬁle, sequential write NL · Lnet NL · Lnet 1
10. Large ﬁle, sequential overwrite NL · Lnet 2 · NL · Lnet 2
11. Large ﬁle, single write Lnet 2 · NL · Lnet 2 · NL
Table 49.3: Comparison: AFS vs. NFS
and medium ﬁles ﬁt into the memory of a client; large ﬁles ﬁt on a local
disk but not in client memory .
We also assume, for the sake of analysis, that an access acros s the net-
work to the remote server for a ﬁle block takes Lnet time units. Access
to local memory takes Lmem, and access to local disk takes Ldisk. The
general assumption is that Lnet > L disk > L mem.
Finally , we assume that the ﬁrst access to a ﬁle does not hit in any
caches. Subsequent ﬁle accesses (i.e., “re-reads”) we assu me will hit in
caches, if the relevant cache has enough capacity to hold the ﬁle.
The columns of the table show the time a particular operation (e.g., a
small ﬁle sequential read) roughly takes on either NFS or AFS . The right-
most column displays the ratio of AFS to NFS.
We make the following observations. First, in many cases, th e per-
formance of each system is roughly equivalent. For example, when ﬁrst
reading a ﬁle (e.g., Workloads 1, 3, 5), the time to fetch the ﬁ le from the re-
mote server dominates, and is similar on both systems. You mi ght think
AFS would be slower in this case, as it has to write the ﬁle to lo cal disk;
however, those writes are buffered by the local (client-sid e) ﬁle system
cache and thus said costs are likely hidden. Similarly , you m ight think
that AFS reads from the local cached copy would be slower, aga in be-
cause AFS stores the cached copy on disk. However, AFS again b eneﬁts
here from local ﬁle system caching; reads on AFS would likely hit in the
client-side memory cache, and performance would be similar to NFS.
Second, an interesting difference arises during a large-ﬁl e sequential
re-read (Workload 6). Because AFS has a large local disk cach e, it will
access the ﬁle from there when the ﬁle is accessed again. NFS, in contrast,
only can cache blocks in client memory; as a result, if a large ﬁle (i.e., a ﬁle
bigger than local memory) is re-read, the NFS client will hav e to re-fetch
the entire ﬁle from the remote server. Thus, AFS is faster tha n NFS in this
case by a factor of Lnet
Ldisk
, assuming that remote access is indeed slower
than local disk. We also note that NFS in this case increases s erver load,
which has an impact on scale as well.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 620

584 THE ANDREW FILE SYSTEM (AFS)
Third, we note that sequential writes (of new ﬁles) should pe rform
similarly on both systems (Workloads 8, 9). AFS, in this case , will write
the ﬁle to the local cached copy; when the ﬁle is closed, the AF S client
will force the writes to the server, as per the protocol. NFS w ill buffer
writes in client memory , perhaps forcing some blocks to the s erver due
to client-side memory pressure, but deﬁnitely writing them to the server
when the ﬁle is closed, to preserve NFS ﬂush-on-close consis tency . You
might think AFS would be slower here, because it writes all da ta to local
disk. However, realize that it is writing to a local ﬁle syste m; those writes
are ﬁrst committed to the page cache, and only later (in the ba ckground)
to disk, and thus AFS reaps the beneﬁts of the client-side OS m emory
caching infrastructure to improve performance.
Fourth, we note that AFS performs worse on a sequential ﬁle ov er-
write (Workload 10). Thus far, we have assumed that the workl oads that
write are also creating a new ﬁle; in this case, the ﬁle exists , and is then
over-written. Overwrite can be a particularly bad case for A FS, because
the client ﬁrst fetches the old ﬁle in its entirety , only to subsequently over-
write it. NFS, in contrast, will simply overwrite blocks and thus avoid the
initial (useless) read 1.
Finally , workloads that access a small subset of data within large ﬁles
perform much better on NFS than AFS (Workloads 7, 11). In thes e cases,
the AFS protocol fetches the entire ﬁle when the ﬁle is opened ; unfortu-
nately , only a small read or write is performed. Even worse, i f the ﬁle is
modiﬁed, the entire ﬁle is written back to the server, doubli ng the per-
formance impact. NFS, as a block-based protocol, performs I /O that is
proportional to the size of the read or write.
Overall, we see that NFS and AFS make different assumptions a nd not
surprisingly realize different performance outcomes as a r esult. Whether
these differences matter is, as always, a question of worklo ad.
49.8 AFS: Other Improvements
Like we saw with the introduction of Berkeley FFS (which adde d sym-
bolic links and a number of other features), the designers of AFS took the
opportunity when building their system to add a number of fea tures that
made the system easier to use and manage. For example, AFS pro vides a
true global namespace to clients, thus ensuring that all ﬁle s were named
the same way on all client machines. NFS, in contrast, allows each client
to mount NFS servers in any way that they please, and thus only by con-
vention (and great administrative effort) would ﬁles be nam ed similarly
across clients.
1We assume here that NFS reads are block-sized and block-alig ned; if they were not, the
NFS client would also have to read the block ﬁrst. We also assu me the ﬁle was not opened
with the O TRUNC ﬂag; if it had been, the initial open in AFS would not fet ch the soon to be
truncated ﬁle’s contents.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 621

THE ANDREW FILE SYSTEM (AFS) 585
ASIDE : THE IMPORTANCE OF WORKLOAD
One challenge of evaluating any system is the choice of workload. Be-
cause computer systems are used in so many different ways, th ere are a
large variety of workloads to choose from. How should the sto rage sys-
tem designer decide which workloads are important, in order to make
reasonable design decisions?
The designers of AFS, given their experience in measuring ho w ﬁle sys-
tems were used, made certain workload assumptions; in parti cular, they
assumed that most ﬁles were not frequently shared, and accessed sequen-
tially in their entirety . Given those assumptions, the AFS d esign makes
perfect sense.
However, these assumptions are not always correct. For exam ple, imag-
ine an application that appends information, periodically , to a log. These
little log writes, which add small amounts of data to an exist ing large ﬁle,
are quite problematic for AFS. Many other difﬁcult workload s exist as
well, e.g., random updates in a transaction database.
One place to get some information about what types of workloa ds are
common are through various research studies that have been p erformed.
See any of these studies for good examples of workload analys is [B+91,
H+11, R+00, V99], including the AFS retrospective [H+88].
AFS also takes security seriously , and incorporates mechanisms to au-
thenticate users and ensure that a set of ﬁles could be kept pr ivate if a
user so desired. NFS, in contrast, had quite primitive suppo rt for security
for many years.
AFS also includes facilities for ﬂexible user-managed acce ss control.
Thus, when using AFS, a user has a great deal of control over wh o exactly
can access which ﬁles. NFS, like most U NIX ﬁle systems, has much less
support for this type of sharing.
Finally , as mentioned before, AFS adds tools to enable simpl er man-
agement of servers for the administrators of the system. In thinking about
system management, AFS was light years ahead of the ﬁeld.
49.9 Summary
AFS shows us how distributed ﬁle systems can be built quite di ffer-
ently than what we saw with NFS. The protocol design of AFS is p artic-
ularly important; by minimizing server interactions (thro ugh whole-ﬁle
caching and callbacks), each server can support many client s and thus
reduce the number of servers needed to manage a particular si te. Many
other features, including the single namespace, security ,and access-control
lists, make AFS quite nice to use. The consistency model provided by AFS
is simple to understand and reason about, and does not lead to the occa-
sional weird behavior as one sometimes observes in NFS.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 622

586 THE ANDREW FILE SYSTEM (AFS)
Perhaps unfortunately , AFS is likely on the decline. Becaus e NFS be-
came an open standard, many different vendors supported it, and, along
with CIFS (the Windows-based distributed ﬁle system protoc ol), NFS
dominates the marketplace. Although one still sees AFS inst allations
from time to time (such as in various educational institutio ns, including
Wisconsin), the only lasting inﬂuence will likely be from th e ideas of AFS
rather than the actual system itself. Indeed, NFSv4 now adds server state
(e.g., an “open” protocol message), and thus bears an increa sing similar-
ity to the basic AFS protocol.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 623

THE ANDREW FILE SYSTEM (AFS) 587
References
[B+91] “Measurements of a Distributed File System”
Mary Baker, John Hartman, Martin Kupfer, Ken Shirriff, John Ousterhout
SOSP ’91, Paciﬁc Grove, CA, October 1991
An early paper measuring how people use distributed ﬁle syst ems. Matches much of the intuition found
in AFS.
[H+11] “A File is Not a File: Understanding the I/O Behavior o f Apple Desktop Applications”
Tyler Harter, Chris Dragga, Michael Vaughn,
Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau
SOSP ’11, New York, NY , October 2011
Our own paper studying the behavior of Apple Desktop workloa ds; turns out they are a bit different
than many of the server-based workloads the systems researc h community usually focuses upon. Also a
good recent reference which points to a lot of related work.
[H+88] “Scale and Performance in a Distributed File System”
John H. Howard, Michael L. Kazar, Sherri G. Menees, David A. N ichols, M. Satyanarayanan,
Robert N. Sidebotham, Michael J. West
ACM Transactions on Computing Systems (ACM TOCS), page 51-8 1, V olume 6, Number 1,
February 1988
The long journal version of the famous AFS system, still in us e in a number of places throughout the
world, and also probably the earliest clear thinking on how to build distributed ﬁle systems. A wonderful
combination of the science of measurement and principled en gineering.
[R+00] “A Comparison of File System Workloads”
Drew Roselli, Jacob R. Lorch, Thomas E. Anderson
USENIX ’00, San Diego, CA, June 2000
A more recent set of traces as compared to the Baker paper [B+9 1], with some interesting twists.
[S+85] “The ITC Distributed File System: Principles and Des ign”
M. Satyanarayanan, J.H. Howard, D.A. Nichols, R.N. Sidebot ham, A. Spector, M.J. West
SOSP ’85. pages 35-50
The older paper about a distributed ﬁle system. Much of the ba sic design of AFS is in place in this older
system, but not the improvements for scale.
[V99] “File system usage in Windows NT 4.0”
Werner V ogels
SOSP ’99, Kiawah Island Resort, SC, December 1999
A cool study of Windows workloads, which are inherently different than many of the UNIX-based studies
that had previously been done.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 625

50
Summary Dialogue on Distribution
Student: Well, that was quick. T oo quick, in my opinion!
Professor: Y es, distributed systems are complicated and cool and well w orth
your study; just not in this book (or course).
Student: That’s too bad; I wanted to learn more! But I did learn a few thi ngs.
Professor: Like what?
Student: Well, everything can fail.
Professor: Good start.
Student: But by having lots of these things (whether disks, machines, or what-
ever), you can hide much of the failure that arises.
Professor: Keep going!
Student: Some basic techniques like retrying are really useful.
Professor: That’s true.
Student: And you have to think carefully about protocols: the exact bi ts that
are exchanged between machines. Protocols can affect every thing, including how
systems respond to failure and how scalable they are.
Professor: Y ou really are getting better at this learning stuff.
Student: Thanks! And you’re not a bad teacher yourself!
Professor: Well thank you very much too.
Student: So is this the end of the book?
Professor: I’m not sure. They don’t tell me anything.
Student: Me neither. Let’s get out of here.
Professor: OK.
Student: Go ahead.
Professor: No, after you.
Student: Please, professors ﬁrst.
589

## Page 626

590 SUMMARY DIALOGUE ON DISTRIBUTION
Professor: No, please, after you.
Student: (exasperated) Fine!
Professor: (waiting) ... so why haven’t you left?
Student: I don’t know how. T urns out, the only thing I can do is particip ate in
these dialogues.
Professor: Me too. And now you’ve learned our ﬁnal lesson...
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 627

General Index
absolute pathname, 442
abstraction, iv, 112, 395
abstractions, 13
access methods, 462
access path, 470
accessed bit, 174
accounting, 77
ack, 547
acknowledgment, 547
acquired, 291
additive parity, 432
address, 7
address space, 8, 26, 108, 111, 132, 263,
403
address space identiﬁer, 191
address translation, 130, 134, 137
address translations, 170
address-based ordering, 164
address-space identiﬁer, 190
address-translation cache, 183
admission control, 240
advice, 79, 80
AIO control block, 378
AIX, 17
allocate, 472
allocation structures, 463
AMAT, 228
amortization, 66, 485
amortize, 65, 514
anonymous, 125
anticipatory disk scheduling, 415
ASID, 191
Aside, 16
asides, iii
asynchronous, 375
asynchronous I/O, 377
asynchronous read, 378
asynchronously, 556
atomic, 274, 403, 448
atomic exchange, 296
atomically, 10, 271, 297, 429, 495
atomicity violation, 360
attribute cache, 571
automatic, 119
automatic memory management, 122
available, 291
average memory access time, 228
average turnaround time, 61
avoidance, 368
avoids, 474
B-tree, 470
baby prooﬁng, 55
back pointer, 508
background, 224
backpointer-based consistency, 508
base, 133, 135, 204
base and bounds, 133
bash, 42
batch, 14, 474
BBC, 508
Belady’s Anomaly, 231
Berkeley Systems Distribution, 17
best ﬁt, 163
best-ﬁt, 148
big endian, 554
big kernel lock, 322
Bill Joy, 17
binary buddy allocator, 166
binary semaphore, 344
bitmap, 463
BKL, 322
block corruption, 436, 527
block groups, 481
Blocked, 29
blocked, 67, 221
blocks, 462
boost, 76
bound, 204
bounded buffer, 329, 346
bounded SATF, 419
bounded-buffer, 329
bounds, 133, 135
591

## Page 628

592 DEPLOYMENT
break, 125
BSATF, 419
BSD, 17
btrfs, 523
buddy algorithm, 148
buffer, 447
buffer cache, 493
buffer overﬂow, 123
bugs, 561
bus snooping, 96
byte ordering, 554
C programming language, iv, 17
C-SCAN, 413
cache, 183, 227, 407
cache afﬁnity, 97
cache coherence, 96
cache consistency problem, 569
cache hits, 227
cache misses, 227
cache replacement, 192
cached, 560
caches, 94
caching, 569
callback, 578
capability, 444
capacity, 423
capacity miss, 230
cast, 121
centralized administration, 559
checkpoint, 498
checkpoint region (CR), 517
checkpointing, 498
checksum, 530, 546
child, 36
chunk size, 424
cigarette smoker’s problem, 355
circular log, 502
Circular SCAN, 413
CISC, 187, 189
clean, 239, 519
client stub, 551
client-side ﬁle system, 560
client/server, 543
clock algorithm, 238
clock hand, 238
close-to-open, 570
cluster, 223
clustering, 240, 249
coalesce, 162
coalescing, 156, 393
coarse-grained, 147, 292
code, 111
code sharing, 146
cold-start miss, 229, 230
collision, 532
command, 391
common case, 571
communication, 544
communication endpoint, 545
compact, 148, 520
compaction, 154
compare-and-exchange, 299
compare-and-swap, 299
Complex Instruction Set Computing, 189
compulsory miss, 229, 230
computed checksum, 533
concurrency, iii, 1, 8, 10, 13, 16, 37, 54, 261
concurrently, 311
condition, 325, 326, 344
condition variable, 285, 326, 344
condition variables, 262, 273, 362
conﬂict miss, 230
consistent-update problem, 429, 495
consumer, 331
context switch, 26, 30, 52, 63, 263
continuation, 380
convention, 443
convoy effect, 61
cooperative, 50
copy-on-write, 12, 251, 507, 522
correctness, 299
corrupt, 528
covering condition, 338
COW, 251, 507
CPU, 5
crash-consistency problem, 491, 495
CRC, 532
critical section, 271, 272, 284
crux, iii
crux of the problem, iii
Culler’s Law, 194
cycle, 363
cyclic redundancy check, 532
cylinder groups, 481
dangling pointer, 124
dangling reference, 455
data, 391
data bitmap, 463, 481, 492
data integrity, 527
data journaling, 498, 503
data protection, 527
data region, 462
data structures, 32, 461
database management system, 194
datagrams, 545
DBMS, 194
deadlock, 354, 359, 363
DEC, 245
decay-usage, 79
decodes, 3
demand paging, 240
demand zeroing, 250
deployability, 422
deployment, 422
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 629

EXPLICIT 593
descheduled, 30
deserialization, 552
deterministic, 37, 268, 270, 272
device driver, 12, 395
dialogue, iii
Digital Equipment Corporation, 245
dimensional analysis, 408
dining philosopher’s problem, 352
direct I/O, 474
Direct Memory Access (DMA), 394
direct pointers, 466
directory, 442
directory hierarchy, 442
directory tree, 442
dirty, 239, 447
dirty bit, 174, 190, 239
disable interrupts, 55
disassemble, 176
disassembler., 269
disciplines, 59
disk, 28
disk address, 218
disk arm, 404
disk head, 404
Disk Operating System, 16
disk scheduler, 412
disk scrubbing, 535
disks, 389
distributed shared memory, 550
distributed state, 562
DOS, 16
double free, 124
double indirect pointer, 467
drop, 545
DSM, 550
dtruss, 444
dynamic relocation, 133, 134
eagerly, 28
ease of use, 108
easy to use, 3, 111
ECC, 528
Edsger Dijkstra, 341
efﬁciency, 110, 113
efﬁcient, 113
elevator, 413
empty, 335
encapsulation, 364
end-to-end argument, 545, 555
energy-efﬁciency, 14
error correcting codes, 528
event handler, 374
event loop, 374
event-based concurrency, 373
evict, 227
exactly once, 548
executable format, 28
executes, 3
explicit, 144
exponential back-off, 550
extents, 467
eXternal Data Representation, 555
external fragmentation, 148, 153, 154
F-SCAN, 413
fail-partial, 528
fail-stop, 423, 527
failure, 543
fair, 66
fair-share, 83
fairness, 60, 293, 299
Fast File System (FFS), 481
FAT,468
FCFS, 61
fetch-and-add, 302
fetches, 3
FID, 578
FIFO, 60, 230
ﬁle, 441
ﬁle allocation table, 468
ﬁle descriptor, 444
ﬁle descriptors, 29
ﬁle handle, 563, 578
ﬁle identiﬁer, 578
ﬁle offset, 446
ﬁle server, 560
ﬁle system, 11, 12, 15
ﬁle system checker, 492
ﬁle-level locking, 580
ﬁle-system inconsistency, 494
ﬁles, 11
ﬁll, 335
ﬁnal, 31
ﬁne-grained, 147, 292
ﬁrmware, 390
First Come, First Served, 60
ﬁrst ﬁt, 164
First In, First Out, 60
ﬁrst-ﬁt, 148
ﬁx-sized cache, 474
ﬂash-based SSDs, 28
Fletcher checksum, 532
ﬂush, 191
ﬂush-on-close, 570
fork(), 36
fragmentation, 554
fragmented, 480
frame pointer, 27
free, 291
free list, 136, 154, 170, 463
free lists, 470
free space management, 469
free-space management, 153
frequency, 233
fsck, 492, 495
full-stripe write, 432
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 630

594 LINK COUNT
fully associative, 189
fully-associative, 189, 230
function pointer, 280
futex, 307, 308
game the scheduler, 76
garbage, 494, 518
garbage collection, 519
garbage collector, 122
graphics, 18
greedy, 419
group, 223
grouping, 240
hand-over-hand locking, 318
hard disk drive, 217, 403, 441
hard drive, 11
hardware caches, 94
hardware privilege level, 15
hardware-based address translation, 130
hardware-managed TLB, 183
hardware-managed TLBs, 187
head crash, 528
header, 157
heap, 29, 111, 119, 288
heartbeat, 582
held, 291
high watermark, 223
Hill’s Law, 352
hints, 80
hit rate, 186, 192, 228
Hoare semantics, 333
holds, 296
holes, 520
homeworks, iv
hot spare, 436
HPUX, 17
HUP, 379
hybrid, 202, 205, 308, 393
I/O, 11
I/O bus, 389
I/O instructions, 394
I/O merging, 415
Idempotency, 567
idempotent, 567
idle time, 224
illusion, 130
immediate reporting, 407, 499
implicit, 145
inconsistent, 429, 491
indeterminate, 270, 272
index node, 464, 465
indirect pointer, 466
initial, 31
inode, 450, 463–465, 512
inode bitmap, 463, 481, 492
inode map (imap), 515
inode number, 442
inode table, 463
input/output, 11
input/output (I/O) device, 389
instruction pointer, 26
INT, 379
interactivity, 110
interface, 390
internal, 202
internal fragmentation, 138, 154, 167, 202,
480, 486
internal structure, 390
interposing, 129
interrupt, 378, 392
interrupt handler, 51, 392
interrupt service routine (ISR), 392
interrupts, 578
inumber, 465
invalid, 173, 203
invalid frees, 124
invalidate, 96
invalidates, 570
invariant, 431
inverted page table, 170
inverted page tables, 212
IP, 26
IRIX, 17
isolation, 13, 108, 113
Jain’s Fairness Index, 60
jobs, 60
journal superblock, 503
journaling, 12, 492, 497
kernel mode, 15, 47
kernel stack, 48
kernel virtual memory, 213
kill, 379
Knuth, 322
last closer wins, 581
last writer wins, 581
latent sector errors, 436
latent-sector errors, 527
Lauer’s Law, 302
lazily, 28
lazy, 250
LDE, 129
Least-Frequently-Used, 233
Least-Recently-Used, 233
least-recently-used, 192
level of indirection, 207, 515, 516
LFS, 512
LFU, 233
limit, 133, 135, 204
limited direct execution, 45, 55, 105, 129
linear page table, 173, 183
link count, 454
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 631

MERGE 595
linked list, 468
Linus Torvalds, 18
Linux, 18
Linux ext2, 497
Linux ext3, 497
Linux ext4, 500
little endian, 554
live, 519
livelock, 366, 393
lmbench, 55
load, 28
load imbalance, 100
load-linked, 300
loader, 134
loads, 39
locality, 95, 187
lock, 291
lock coupling, 318
lock variable, 291
lock-free, 96
locked, 291
locking, 55, 97, 98
locks, 262, 283
log, 522
Log-structured File System, 512
logical logging, 498
long ﬁle names, 487
lookaside buffer, 195
lost write, 535
lottery scheduling, 83
low watermark, 223
low-level name, 441, 465
LRU, 192, 233, 474
LSEs, 527
Mac OS, 16
machine state, 26
malicious scheduler, 297
man pages, 42
manage, 4
manage memory, 130
manual pages, 42
manual stack management, 380
marshaling, 552
master control program, 4
measurement, 577
mechanisms, 6, 25, 59, 105, 114
memory bus, 389
memory hierarchy, 217
memory hogs, 249
memory leak, 124
memory management unit (MMU), 135
memory overlays, 217
memory pressure, 227
memory protection, 16
memory-management unit, 183
memory-mapped I/O, 395
MenuMeters, 42
merge, 162, 415
Mesa semantics, 333, 337
metadata, 449, 463, 466, 512
metadata journaling, 503
MFU, 234
mice, 389
microkernels, 33, 113
Microsoft, 16
migrating, 99
migration, 101
minicomputer, 15
minimize the overheads, 13
mirrored, 422
misdirected write, 534
miss rate, 192, 228
MMU, 183
mobility, 14
modiﬁed, 239
modiﬁed bit, 239
modularity, 27
monitors, 312
Most-Frequently-Used, 234
Most-Recently-Used, 234
mount point, 456
mount protocol, 564
MQMS, 99
MRU, 234
multi-level feedback queue, 68
Multi-level Feedback Queue (MLFQ), 71
multi-level index, 467
multi-level page table, 187, 205
multi-queue multiprocessor scheduling, 99
multi-threaded, 9, 262, 263
multi-threaded programs, 37
multi-zoned, 407
multicore, 93
Multics, 17
multiprocessor, 93
multiprocessor scheduling, 93, 94
multiprogramming, 15, 110
mutex, 292
mutual exclusion, 271, 272, 292, 293
name, 443
naming, 553
NBF, 412
nearest-block-ﬁrst, 412
networking, 18
new, 122
next ﬁt, 164
NeXTStep, 18
node.js, 373
non-blocking data structures, 322
non-determinism, 37
non-preemptive, 63
non-work-conserving, 415
null-pointer, 248
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 632

596 QUEUES
object caches, 165
offset, 171
open protocol, 561
open-source software, 17
operating system, 4
Operating Systems in Three Easy Pieces,
1
optimal, 62, 228
optimistic crash consistency, 508
order violation, 360, 361
ordered journaling, 503
OS, 4
Ousterhout’s Law, 79
out-of-memory killer, 240
overlap, 67, 68, 221, 377, 392
owner, 292
page, 169
page cache, 493
page daemon, 223
page directory, 205, 209
page directory entries, 206
page fault, 219, 220, 224
page frame, 170
page frame number, 206
page in, 221
page miss, 220
page out, 221
page replacement, 174
page selection, 240
page table, 170, 176
page table base register, 219
page table entry (PTE), 172, 219
page-directory index, 208
page-fault handler, 220, 224
page-replacement policy, 221
page-table base register, 175, 187
page-table index, 209
paging, 28, 153, 169, 179, 381
paging out, 227
parallel, 93
parameterization, 487
parameterize, 78
parent, 31, 36
parity, 430
partitioned, 561
pass, 88
Patterson’s Law, 577
PC, 16, 26
PCB, 32
PCI, 389
PDE, 206
perfect scaling, 313
performance, 13, 60, 293, 299, 423, 544
peripheral bus, 389
persist, 387, 491
persistence, iii, 1, 11, 12, 29, 387
persistent storage, 441
persistently, 11, 13
personal computer, 16
physical, 4, 23, 130
physical address, 134
physical ID, 534
physical identiﬁer, 534
physical logging, 498
physical memory, 7
physically-indexed cache, 194
PID, 36, 191
pipe, 41, 329
pipes, 17
platter, 404
policies, 26, 59, 114
policy, 6
poll, 378
polling, 391, 578
power loss, 491
power outage, 561
pre-allocation, 470
preempt, 63
preemptive, 63
preemptive scheduler, 298
Preemptive Shortest Job First, 64
prefetching, 240
premature optimization, 322
present, 222
present bit, 174, 219, 224
principle of locality, 233, 234
principle of SJF (shortest job ﬁrst), 412
priority level, 72
privileged, 49, 137, 193, 395
procedure call, 15, 283
process, 25, 26
Process Control Block, 32
process control block, 137
process control block (PCB), 263
process identiﬁer, 36, 191
process list, 30, 32
process structure, 137
producer, 331
producer/consumer, 329, 346
program counter, 26
programmed I/O (PIO), 391
projects, iv
prompt, 40
proportional-share, 83
protect, 113
protection, 13, 108, 111, 113, 190
protection bits, 146, 173
protocol, 575
protocol compiler, 551
pseudocode, iv
PSJF, 64
purify, 125
queues, 72
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 633

ROTATIONS PER MINUTE 597
race condition, 270, 272
RAID, 421
RAID 0+1, 428
RAID 1+0, 428
RAID-01, 428
RAID-10, 428
RAID-DP, 530
RAM, 194
RAM isn’t always RAM, 194
random, 192, 409, 426, 446
random-access memory, 194
randomness, 84
raw disk, 475
read-after-write, 535
reader-writer lock, 350
Ready, 29
ready, 304
real code, iv
reassembly, 554
reboot the machine, 51
recency, 233
reconstruct, 431, 530
recover, 501
recovery, 429
recovery protocol, 562
recursive update problem, 518
redirected, 40
redo logging, 501
Reduced Instruction Set Computing, 189
redundancy, 421
Redundant Array of Inexpensive Disks,
421
reference bit, 174, 238, 249
reference count, 453
regain control, 50
register context, 30
reliability, 13, 423
relocate, 132
remote method invocation, 551
remote procedure call, 551
replace, 192, 221
replacement policy, 227
replayed, 501
resident set size, 249
resource, 4
resource manager, 4, 6
resources, 13
response time, 64
retry, 548
return-from-trap, 15, 47
revoke, 506
RISC, 188, 189
RMI, 551
roll forward, 522
root directory, 442, 471
rotates, 434
rotation delay, 405
rotational delay, 405
rotations per minute, 408
rotations per minute (RPM), 404
round robin, 99
Round-Robin (RR), 65
RPC, 551
RPM, 408
RSS, 249
run-time library, 551
run-time stack, 29
Running, 29
running, 304
running program, 25
SATA, 389
SATF, 414
scalability, 98
scale, 575
scaling, 167
SCAN, 413
scan resistance, 241
schedule, 474
scheduled, 30
scheduler, 37, 52
scheduler state, 344
scheduling metric, 60
scheduling policies, 59
scheduling policy, 26
scheduling quantum, 65
SCSI, 389
second-chance lists, 249
security, 14, 18, 544, 559
seek, 406, 447
segment, 141, 512, 513
segment summary block, 520
segment table, 147
segmentation, 138, 141, 153, 155
segmentation fault, 122, 144
segmentation violation, 144
segmented FIFO, 249
segregated lists, 165
SEGV, 379
semaphore, 341
separator, 442
sequence counter, 549
sequential, 409, 426, 446
serialization, 552
server-side ﬁle system, 560
set, 298
set-associativity, 230
sets, 296
settling time, 406
shadow paging, 522
share, 11, 146
shared state, 562
sharing, 559
shell, 17
shortest access time ﬁrst, 414
Shortest Job First (SJF), 62
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 634

598 TIME SLICE
shortest positioning time ﬁrst, 414
Shortest Time-to-Completion First, 64
shortest-seek-ﬁrst, 412
shortest-seek-time-ﬁrst, 412
SIG, 379
signal handler, 379
signaling, 326
signals, 42, 378, 379
SIGSEGV, 379
silent faults, 528
simulations, iv
single-queue multiprocessor scheduling,
97
single-threaded, 263
slab allocator, 165
slabs, 165
sleeping barber problem, 355
sloppy counter, 314
small-write problem, 433, 511
snapshots, 523
sockets, 545
soft link, 454
software RAID, 436
software-managed TLB, 188
solid-state drives, 11
solid-state storage device, 441
space leak, 494
space sharing, 26
sparse address spaces, 143
spatial locality, 95, 186, 187, 234
spin lock, 298
spin-wait, 296
spin-waiting, 297
spindle, 404
split, 159
splitting, 155
SPTF, 414
spurious wakeups, 337
SQMS, 97
SSDs, 11
SSF, 412
SSTF, 412
stack, 29, 111, 119
stack pointer, 27
stack property, 231
stale cache, 570
standard library, 4, 12
standard output, 40
starvation, 76, 413
starve, 76
state, 565
stateful, 562
stateless, 562
states, 29
static relocation, 134
status, 391
STCF, 64
store-conditional, 300
stored checksum, 533
strace, 444
stride, 88
stride scheduling, 88
stripe, 424
striping, 424
stub generator, 551
sub-blocks, 486
sub-directories, 442
subtractive parity, 432
SunOS, 17
super block, 481
superblock, 464
superpages, 214
supervisor, 4
surface, 404
swap, 213
swap daemon, 223
swap space, 125, 218
swapping, 28
switches contexts, 53
symbolic link, 454, 488
synchronization primitives, 271
synchronous, 375, 552
synchronously, 555
system call, 15, 47
system calls, 4, 12, 50, 560
system crash, 491
systems programming, iv
TCP, 549
TCP/IP, 549
tcsh, 42
temporal locality, 95, 186, 187, 234
test, 298
test-and-set, 297
test-and-set instruction, 296
tests, 296
the mapping problem, 425
the web, 42
thrashing, 240
thread, 262, 263
thread control blocks (TCBs), 263
thread pool, 553
thread safe, 311
thread-local, 264
threads, 9, 93, 112
Three C’s, 230
ticket, 85
ticket currency, 85
ticket inﬂation, 85
ticket lock, 302
ticket transfer, 85
tickets, 83
TID, 498
Time sharing, 26
time sharing, 25, 45, 46, 110
time slice, 65
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 635

VALID BIT 599
time-sharing, 26
time-slicing, 65
time-space trade-off, 207
time-space trade-offs, 207
timeout, 548
timeout/retry, 548
timer interrupt, 51, 52
tips, iii
TLB, 183
TLB coverage, 194
TLB hit, 184, 219
TLB miss, 184, 219
torn write, 403
total ordering, 365
track, 404
track buffer, 407, 487
track skew, 406
trade-off, 66
transaction, 274
transaction checksum, 508
transaction identiﬁer, 498
transfer, 406
translate, 174
translated, 133
translation lookaside buffer, 195
translation-lookaside buffer, 183
transparency, 113, 131
transparent, 132, 560
transparently, 224, 422
trap, 15, 47, 51
trap handler, 15, 188
trap handlers, 48
trap table, 47, 48
traverse, 471
triple indirect pointer, 467
truss, 444
Turing Award, 71
turnaround time, 60
two-phase lock, 307
two-phased, 393
type, 443
UDP/IP, 545
unfairness metric, 87
uniﬁed page cache, 474
uninitialized read, 123
unlocked, 291
unmapped, 188
unmarshaling, 552
update, 7, 96
update visibility, 570
USB, 389
use bit, 238
user mode, 15, 47
utilization, 110
valgrind, 125
valid, 190, 222
valid bit, 173, 206
V enus,576
version number, 521
versioning ﬁle system, 519
V ery Simple File System,461
Vice, 576
virtual, 4, 23, 130
virtual address, 112, 114, 134
virtual address space, 8
virtual CPUs, 263
virtual machine, 4
virtual memory, 263
virtual page number (VPN), 171
virtual-to-physical address translations, 176
virtualization, iii, 1, 4, 8, 23
virtualized, 90, 269
virtualizes, 13
virtualizing, 25
virtualizing memory, 8, 112
virtualizing the CPU, 6
virtually-indexed cache, 194
void pointer, 154, 280
volatile, 11
V oltaire’s Law, 569
volumes, 577
V on Neumann,3
voo-doo constants, 77
vsfs, 461
WAFL, 523, 530
wait-free, 367
wait-free synchronization, 300
waiting, 326
wakeup/waiting race, 306
whole-ﬁle caching, 575
wired, 188
work stealing, 101
work-conserving, 415
working sets, 240
workload, 59, 492, 585
workloads, 234
worst ﬁt, 163
worst-ﬁt, 148
write back, 407
write barriers, 499
write buffering, 474, 513, 569
write through, 407
write verify, 535
write-ahead log, 429
write-ahead logging, 492, 497
x86, 177
XDR, 555
XOR, 430
yield, 51
Zemaphores, 355
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 636

600 ZOMBIE
Zettabyte File System, 535
ZFS, 523, 535
zombie, 31
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 637

Asides
UNIX Signals, 379
Advanced Chapters, 93
And Then Came Linux, 18
Belady’s Anomaly, 231
Blocking vs. Non-blocking Interfaces, 375
Cache Consistency Is Not A Panacea, 580
Calling lseek() Does Not Perform A Disk Seek, 447
Computing The “A verage” Seek, 411
Data Structure – The Free List, 136
Data Structure – The Inode, 465
Data Structure – The Page Table, 176
Data Structure – The Process List, 32
Dekker’s and Peterson’s Algorithms, 295
Dimensional Analysis, 408
Emulating Reference Bits, 250
Every Address You See Is Virtual, 114
FFS File Creation, 482
Forcing Writes To Disk, 499
Free Space Management, 470
Great Engineers Are Really Great, 166
How Long Context Switches Take, 55
Interludes, 35
Key Concurrency Terms, 272
601

## Page 638

602 W HY SYSTEM CALLS LOOK LIKE PROCEDURE CALLS
Linked-based Approaches, 468
Measurement Homeworks, 58
Mental Models Of File Systems, 462
Multiple Page Sizes, 202
Optimizing Log Writes, 500
Preemptive Schedulers, 63
Reads Don’t Access Allocation Structures, 472
RISC vs. CISC, 189
RTFM – Read The Man Pages, 42
Simulation Homeworks, 70
Software-based Relocation, 134
Storage Technologies, 218
Swapping Terminology And Other Things, 220
The creat() System Call, 444
The End-to-End Argument, 555
The Importance of U NIX , 17
The Importance Of Workload, 585
The RAID Consistent-Update Problem, 429
The RAID Mapping Problem, 425
The Segmentation Fault, 144
Thread API Guidelines, 288
TLB Valid Bit ̸= Page Table Valid Bit, 190
Types of Cache Misses, 230
Types of Locality, 234
Why Hardware Doesn’t Handle Page Faults, 221
Why Null Pointer Accesses Cause Seg Faults, 248
Why Servers Crash, 561
Why System Calls Look Like Procedure Calls, 48
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 639

Tips
Always Hold The Lock While Signaling, 329
Amortization Can Reduce Costs, 66
A void Premature Optimization (Knuth’s Law), 322
A void V oo-doo Constants (Ousterhout’s Law), 79
Be Careful Setting The Timeout Value, 550
Be Careful With Generalization, 356
Be Lazy, 251
Be Wary of Complexity, 208
Be Wary Of Locks and Control Flow, 319
Be Wary Of Powerful Commands, 451
Communication Is Inherently Unreliable, 544
Comparing Against Optimal is Useful, 229
Consider Extent-based Approaches, 467
Dealing With Application Misbehavior, 51
Details Matter, 513
Do Work In The Background, 224
Don’t Always Do It Perfectly (Tom West’s Law), 370
Don’t Block In Event-based Servers, 377
Getting It Right (Lampson’s Law), 40
Hardware-based Dynamic Relocation, 135
Idempotency Is Powerful, 567
If 1000 Solutions Exist, No Great One Does, 149
Interposition Is Powerful, 131
Interrupts Not Always Better Than PIO, 393
It Always Depends (Livny’s Law), 415
It Compiled or It Ran ̸= It Is Correct, 123
Know And Use Your Tools, 269
603

## Page 640

604 WHEN IN DOUBT , T RY IT OUT
Learn From History, 72
Less Code Is Better Code (Lauer’s Law), 302
Make The System Usable, 488
Measure Then Build (Patterson’s Law), 577
More Concurrency Isn’t Necessarily Faster, 319
Overlap Enables Higher Utilization, 68
Perfect Is The Enemy Of The Good (V oltaire’s Law), 569
RAM Isn’t Always RAM (Culler’s Law), 194
Reboot Is Useful, 56
Separate Policy And Mechanism, 27
Simple And Dumb Can Be Better (Hill’s Law), 352
The Principle of Isolation, 113
The Principle of SJF, 62
There’s No Free Lunch, 531
Think About Concurrency As Malicious Scheduler, 297
Think Carefully About Naming, 443
Transparency Enables Deployment, 422
Turn Flaws Into Virtues, 523
Understand Time-Space Trade-offs, 207
Use strace (And Similar Tools), 445
Use A Level Of Indirection, 516
Use Advice Where Possible, 80
Use Atomic Operations, 274
Use Caching When Possible, 187
Use Checksums For Integrity, 547
Use Disks Sequentially, 410
Use Hybrids, 205
Use Protected Control Transfer, 47
Use Randomness, 84
Use The Timer Interrupt To Regain Control, 52
Use Tickets To Represent Shares, 85
Use Time Sharing (and Space Sharing), 26
Use While (Not If) For Conditions, 337
When In Doubt, Try It Out, 121
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

