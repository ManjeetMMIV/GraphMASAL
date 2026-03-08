# Document: operating_systems_three_easy_pieces (Pages 561 to 600)

## Page 561

LOG -STRUCTURED FILE SYSTEMS 525
[R92] “Design and Implementation of the Log-structured Fil e System”
Mendel Rosenblum
http://www.eecs.berkeley .edu/Pubs/TechRpts/1992/CSD-92-696.pdf
The award-winning dissertation about LFS, with many of the d etails missing from the paper.
[SS+95] “File system logging versus clustering: a performa nce comparison”
Margo Seltzer, Keith A. Smith, Hari Balakrishnan, Jacqueli ne Chang, Sara McMains, V enkata
Padmanabhan
USENIX 1995 Technical Conference, New Orleans, Louisiana, 1995
A paper that showed the LFS performance sometimes has proble ms, particularly for workloads with
many calls to fsync() (such as database workloads). The paper was controversial a t the time.
[SO90] “Write-Only Disk Caches”
Jon A. Solworth, Cyril U. Orji
SIGMOD ’90, Atlantic City , New Jersey , May 1990
An early study of write buffering and its beneﬁts. However, b uffering for too long can be harmful: see
Mogul [M94] for details.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 563

44
Data Integrity and Protection
Beyond the basic advances found in the ﬁle systems we have studied thus
far, a number of features are worth studying. In this chapter , we focus on
reliability once again (having previously studied storage system reliabil-
ity in the RAID chapter). Speciﬁcally , how should a ﬁle syste m or storage
system ensure that data is safe, given the unreliable nature of modern
storage devices?
This general area is referred to as data integrity or data protection .
Thus, we will now investigate techniques used to ensure that the data
you put into your storage system is the same when the storage s ystem
returns it to you.
CRUX : H OW TO ENSURE DATA INTEGRITY
How should systems ensure that the data written to storage is pro-
tected? What techniques are required? How can such techniqu es be made
efﬁcient, with both low space and time overheads?
44.1 Disk Failure Modes
As you learned in the chapter about RAID, disks are not perfec t, and
can fail (on occasion). In early RAID systems, the model of fa ilure was
quite simple: either the entire disk is working, or it fails c ompletely , and
the detection of such a failure is straightforward. This fail-stop model of
disk failure makes building RAID relatively simple [S90].
What you didn’t learn is about all of the other types of failur e modes
modern disks exhibit. Speciﬁcally , as Bairavasundaram et a l. studied
in great detail [B+07, B+08], modern disks will occasionall y seem to be
mostly working but have trouble successfully accessing oneor more blocks.
Speciﬁcally , two types of single-block failures are commonand worthy of
consideration: latent-sector errors (LSEs) and block corruption . We’ll
now discuss each in more detail.
527

## Page 564

528 DATA INTEGRITY AND PROTECTION
Cheap Costly
LSEs 9.40% 1.40%
Corruption 0.50% 0.05%
Table 44.1: Frequency of LSEs and Block Corruption
LSEs arise when a disk sector (or group of sectors) has been da maged
in some way . For example, if the disk head touches the surface for some
reason (a head crash , something which shouldn’t happen during nor-
mal operation), it may damage the surface, making the bits un readable.
Cosmic rays can also ﬂip bits, leading to incorrect contents . Fortunately ,
in-disk error correcting codes (ECC) are used by the drive to determine
whether the on-disk bits in a block are good, and in some cases , to ﬁx
them; if they are not good, and the drive does not have enough i nforma-
tion to ﬁx the error, the disk will return an error when a reque st is issued
to read them.
There are also cases where a disk block becomes corrupt in a way not
detectable by the disk itself. For example, buggy disk ﬁrmwa re may write
a block to the wrong location; in such a case, the disk ECC indi cates the
block contents are ﬁne, but from the client’s perspective th e wrong block
is returned when subsequently accessed. Similarly , a block may get cor-
rupted when it is transferred from the host to the disk across a faulty
bus; the resulting corrupt data is stored by the disk, but it i s not what
the client desires. These types of faults are particularly i nsidious because
the are silent faults ; the disk gives no indication of the problem when
returning the faulty data.
Prabhakaran et al. describes this more modern view of disk fa ilure as
the fail-partial disk failure model [P+05]. In this view , disks can still fail
in their entirety (as was the case in the traditional fail-st op model); how-
ever, disks can also seemingly be working and have one or more blocks
become inaccessible (i.e., LSEs) or hold the wrong contents (i.e., corrup-
tion). Thus, when accessing a seemingly-working disk, once in a while
it may either return an error when trying to read or write a giv en block
(a non-silent partial fault), and once in a while it may simpl y return the
wrong data (a silent partial fault).
Both of these types of faults are somewhat rare, but just how r are? Ta-
ble
44.1 summarizes some of the ﬁndings from the two Bairavasundaram
studies [B+07,B+08].
The table shows the percent of drives that exhibited at least one LSE
or block corruption over the course of the study (about 3 year s, over
1.5 million disk drives). The table further sub-divides the results into
“cheap” drives (usually SATA drives) and “costly” drives (u sually SCSI
or FibreChannel). As you can see from the table, while buying better
drives reduces the frequency of both types of problem (by abo ut an or-
der of magnitude), they still happen often enough that you ne ed to think
carefully about them.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 565

DATA INTEGRITY AND PROTECTION 529
Some additional ﬁndings about LSEs are:
• Costly drives with more than one LSE are as likely to develop a d-
ditional errors as cheaper drives
• For most drives, annual error rate increases in year two
• LSEs increase with disk size
• Most disks with LSEs have less than 50
• Disks with LSEs are more likely to develop additional LSEs
• There exists a signiﬁcant amount of spatial and temporal loc ality
• Disk scrubbing is useful (most LSEs were found this way)
Some ﬁndings about corruption:
• Chance of corruption varies greatly across different drive models
within the same drive class
• Age affects are different across models
• Workload and disk size have little impact on corruption
• Most disks with corruption only have a few corruptions
• Corruption is not independent with a disk or across disks in R AID
• There exists spatial locality , and some temporal locality
• There is a weak correlation with LSEs
To learn more about these failures, you should likely read th e original
papers [B+07,B+08]. But hopefully the main point should be c lear: if you
really wish to build a reliable storage system, you must incl ude machin-
ery to detect and recovery from both LSEs and block corruptio n.
44.2 Handling Latent Sector Errors
Given these two new modes of partial disk failure, we should n ow try
to see what we can do about them. Let’s ﬁrst tackle the easier o f the two,
namely latent sector errors.
CRUX : H OW TO HANDLE LATENT SECTOR ERRORS
How should a storage system handle latent sector errors? How much
extra machinery is needed to handle this form of partial fail ure?
As it turns out, latent sector errors are rather straightfor ward to han-
dle, as they are (by deﬁnition) easily detected. When a stora ge system
tries to access a block, and the disk returns an error, the sto rage system
should simply use whatever redundancy mechanism it has to re turn the
correct data. In a mirrored RAID, for example, the system sho uld access
the alternate copy; in a RAID-4 or RAID-5 system based on pari ty , the
system should reconstruct the block from the other blocks in the parity
group. Thus, easily detected problems such as LSEs are readi ly recovered
through standard redundancy mechanisms.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 566

530 DATA INTEGRITY AND PROTECTION
The growing prevalence of LSEs has inﬂuenced RAID designs over the
years. One particularly interesting problem arises in RAID -4/5 systems
when both full-disk faults and LSEs occur in tandem. Speciﬁc ally , when
an entire disk fails, the RAID tries to reconstruct the disk (say , onto a
hot spare) by reading through all of the other disks in the par ity group
and recomputing the missing values. If, during reconstruct ion, an LSE
is encountered on any one of the other disks, we have a problem : the
reconstruction cannot successfully complete.
To combat this issue, some systems add an extra degree of redundancy .
For example, NetApp’s RAID-DP has the equivalent of two parity disks
instead of one [C+04]. When an LSE is discovered during recon struction,
the extra parity helps to reconstruct the missing block. As a lways, there is
a cost, in that maintaining two parity blocks for each stripe is more costly;
however, the log-structured nature of the NetApp WAFL ﬁle system mit-
igates that cost in many cases [HLM94]. The remaining cost is space, in
the form of an extra disk for the second parity block.
44.3 Detecting Corruption: The Checksum
Let’s now tackle the more challenging problem, that of silen t failures
via data corruption. How can we prevent users from getting ba d data
when corruption arises, and thus leads to disks returning ba d data?
CRUX : H OW TO PRESERVE DATA INTEGRITY DESPITE CORRUPTION
Given the silent nature of such failures, what can a storage s ystem do
to detect when corruption arises? What techniques are neede d? How can
one implement them efﬁciently?
Unlike latent sector errors, detection of corruption is a key problem.
How can a client tell that a block has gone bad? Once it is known that a
particular block is bad, recovery is the same as before: you need to have
some other copy of the block around (and hopefully , one that i s not cor-
rupt!). Thus, we focus here on detection techniques.
The primary mechanism used by modern storage systems to pres erve
data integrity is called the checksum. A checksum is simply the result
of a function that takes a chunk of data (say a 4KB block) as inp ut and
computes a function over said data, producing a small summar y of the
contents of the data (say 4 or 8 bytes). This summary is referr ed to as the
checksum. The goal of such a computation is to enable a system to detect
if data has somehow been corrupted or altered by storing the c hecksum
with the data and then conﬁrming upon later access that the da ta’s cur-
rent checksum matches the original storage value.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 567

DATA INTEGRITY AND PROTECTION 531
TIP : T HERE ’ S NO FREE LUNCH
There’s No Such Thing As A Free Lunch, or TNSTAAFL for short, i s
an old American idiom that implies that when you are seemingl y get-
ting something for free, in actuality you are likely paying s ome cost for
it. It comes from the old days when diners would advertise a fr ee lunch
for customers, hoping to draw them in; only when you went in, d id you
realize that to acquire the “free” lunch, you had to purchase one or more
alcoholic beverages. Of course, this may not actually be a problem, partic-
ularly if you are an aspiring alcoholic (or typical undergra duate student).
Common Checksum Functions
A number of different functions are used to compute checksum s, and
vary in strength (i.e., how good they are at protecting data i ntegrity) and
speed (i.e., how quickly can they be computed). A trade-off t hat is com-
mon in systems arises here: usually , the more protection you get, the
costlier it is. There is no such thing as a free lunch.
One simple checksum function that some use is based on exclus ive
or (XOR). With XOR-based checksums, the checksum is compute d sim-
ply by XOR’ing each chunk of the data block being checksummed , thus
producing a single value that represents the XOR of the entir e block.
To make this more concrete, imagine we are computing a 4-byte check-
sum over a block of 16 bytes (this block is of course too small t o really be a
disk sector or block, but it will serve for the example). The 1 6 data bytes,
in hex, look like this:
365e c4cd ba14 8a92 ecef 2c3a 40be f666
If we view them in binary , we get the following:
0011 0110 0101 1110 1100 0100 1100 1101
1011 1010 0001 0100 1000 1010 1001 0010
1110 1100 1110 1111 0010 1100 0011 1010
0100 0000 1011 1110 1111 0110 0110 0110
Because we’ve lined up the data in groups of 4 bytes per row , it is easy
to see what the resulting checksum will be: simply perform an XOR over
each column to get the ﬁnal checksum value:
0010 0000 0001 1011 1001 0100 0000 0011
The result, in hex, is 0x201b9403.
XOR is a reasonable checksum but has its limitations. If, for example,
two bits in the same position within each checksummed unit ch ange, the
checksum will not detect the corruption. For this reason, pe ople have
investigated other checksum functions.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 568

532 DATA INTEGRITY AND PROTECTION
Another simple checksum function is addition. This approac h has
the advantage of being fast; computing it just requires perf orming 2’s-
complement addition over each chunk of the data, ignoring ov erﬂow . It
can detect many changes in data, but is not good if the data, fo r example,
is shifted.
A slightly more complex algorithm is known as the Fletcher check-
sum, named (as you might guess) for the inventor, John G. Fletche r [F82].
It is quite simple and involves the computation of two check b ytes, s1
and s2. Speciﬁcally , assume a block D consists of bytes d1 ... dn; s1 is
simply deﬁned as follows: s1 = s1 + di mod 255 (computed over all di);
s2 in turn is: s2 = s2 + s1 mod 255 (again over all di) [F04]. The ﬂetcher
checksum is known to be almost as strong as the CRC (described next),
detecting all single-bit errors, all double-bit errors, and a large percentage
of burst errors [F04].
One ﬁnal commonly-used checksum is known as a cyclic redundancy
check (CRC). While this sounds fancy , the basic idea is quite simple. As -
sume you wish to compute the checksum over a data block D. All you do
is treat D as if it is a large binary number (it is just a string of bits aft er all)
and divide it by an agreed upon value ( k). The remainder of this division
is the value of the CRC. As it turns out, one can implement this binary
modulo operation rather efﬁciently , and hence the popularity of the CRC
in networking as well. See elsewhere for more details [M13].
Whatever the method used, it should be obvious that there is n o per-
fect checksum: it is possible two data blocks with non-ident ical contents
will have identical checksums, something referred to as a collision. This
fact should be intuitive: after all, computing a checksum is taking some-
thing large (e.g., 4KB) and producing a summary that is much s maller
(e.g., 4 or 8 bytes). In choosing a good checksum function, we are thus
trying to ﬁnd one that minimizes the chance of collisions whi le remain-
ing easy to compute.
Checksum Layout
Now that you understand a bit about how to compute a checksum, let’s
next analyze how to use checksums in a storage system. The ﬁrst question
we must address is the layout of the checksum, i.e., how shoul d check-
sums be stored on disk?
The most basic approach simply stores a checksum with each di sk sec-
tor (or block). Given a data block D, let us call the checksum over that
data C(D). Thus, without checksums, the disk layout looks like this:
D0 D1 D2 D3 D4 D5 D6
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 569

DATA INTEGRITY AND PROTECTION 533
With checksums, the layout adds a single checksum for every b lock:
C[D0]
D0
C[D1]
D1
C[D2]
D2
C[D3]
D3
C[D4]
D4
Because checksums are usually small (e.g., 8 bytes), and dis ks only can
write in sector-sized chunks (512 bytes) or multiples thereof, one problem
that arises is how to achieve the above layout. One solution e mployed by
drive manufacturers is to format the drive with 520-byte sec tors; an extra
8 bytes per sector can be used to store the checksum.
In disks that don’t have such functionality , the ﬁle system m ust ﬁgure
out a way to store the checksums packed into 512-byte blocks. One such
possibility is as follows:
C[D0]
C[D1]
C[D2]
C[D3]
C[D4]
D0 D1 D2 D3 D4
In this scheme, the n checksums are stored together in a sector, fol-
lowed by n data blocks, followed by another checksum sector for the nex t
n blocks, and so forth. This scheme has the beneﬁt of working on all disks,
but can be less efﬁcient; if the ﬁle system, for example, want s to overwrite
block D1, it has to read in the checksum sector containing C(D1), update
C(D1) in it, and then write out the checksum sector as well as the new
data block D1 (thus, one read and two writes). The earlier approach (of
one checksum per sector) just performs a single write.
44.4 Using Checksums
With a checksum layout decided upon, we can now proceed to act u-
ally understand how to use the checksums. When reading a block D, the
client (i.e., ﬁle system or storage controller) also reads i ts checksum from
disk Cs(D), which we call the stored checksum (hence the subscript Cs).
The client then computes the checksum over the retrieved block D, which
we call the computed checksum Cc(D). At this point, the client com-
pares the stored and computed checksums; if they are equal (i .e., Cs(D)
== Cc(D), the data has likely not been corrupted, and thus can be safel y
returned to the user. If they do not match (i.e., Cs(D) != Cc(D)), this im-
plies the data has changed since the time it was stored (since the stored
checksum reﬂects the value of the data at that time). In this c ase, we have
a corruption, which our checksum has helped us to detect.
Given a corruption, the natural question is what should we do about
it? If the storage system has a redundant copy , the answer is e asy: try to
use it instead. If the storage system has no such copy , the lik ely answer is
to return an error. In either case, realize that corruption d etection is not a
magic bullet; if there is no other way to get the non-corrupte d data, you
are simply out of luck.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 570

534 DATA INTEGRITY AND PROTECTION
44.5 A New Problem: Misdirected Writes
The basic scheme described above works well in the general ca se of
corrupted blocks. However, modern disks have a couple of unu sual fail-
ure modes that require different solutions.
The ﬁrst failure mode of interest is called a misdirected write . This
arises in disk and RAID controllers which write the data to di sk correctly ,
except in the wrong location. In a single-disk system, this means that the
disk wrote block Dx not to address x (as desired) but rather to address
y (thus “corrupting” Dy); in addition, within a multi-disk system, the
controller may also write Di,x not to address x of disk i but rather to
some other disk j. Thus our question:
CRUX : H OW TO HANDLE MISDIRECTED WRITES
How should a storage system or disk controller detect misdir ected
writes? What additional features are required from the chec ksum?
The answer, not surprisingly , is simple: add a little more in formation
to each checksum. In this case, adding a physical identiﬁer (physical
ID) is quite helpful. For example, if the stored information no w contains
the checksum C(D) as well as the disk and sector number of the block,
it is easy for the client to determine whether the correct inf ormation re-
sides within the block. Speciﬁcally , if the client is readin g block 4 on disk
10 ( D10,4), the stored information should include that disk number an d
sector offset, as shown below . If the information does not ma tch, a misdi-
rected write has taken place, and a corruption is now detecte d. Here is an
example of what this added information would look like on a tw o-disk
system. Note that this ﬁgure, like the others before it, is no t to scale, as the
checksums are usually small (e.g., 8 bytes) whereas the bloc ks are much
larger (e.g., 4 KB or bigger):
Disk 0
Disk 1
C[D0]
disk=0
block=0
D0
C[D1]
disk=0
block=1
D1
C[D2]
disk=0
block=2
D2
C[D0]
disk=1
block=0
D0
C[D1]
disk=1
block=1
D1
C[D2]
disk=1
block=2
D2
You can see from the on-disk format that there is now a fair amo unt of
redundancy on disk: for each block, the disk number is repeat ed within
each block, and the offset of the block in question is also kep t next to the
block itself. The presence of redundant information should be no sur-
prise, though; redundancy is the key to error detection (in t his case) and
recovery (in others). A little extra information, while not strictly needed
with perfect disks, can go a long ways in helping detect probl ematic situ-
ations should they arise.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 571

DATA INTEGRITY AND PROTECTION 535
44.6 One Last Problem: Lost Writes
Unfortunately , misdirected writes are not the last problem we will
address. Speciﬁcally , some modern storage devices also hav e an issue
known as a lost write, which occurs when the device informs the upper
layer that a write has completed but in fact it never is persis ted; thus,
what remains is left is the old contents of the block rather th an the up-
dated new contents.
The obvious question here is: do any of our checksumming stra tegies
from above (e.g., basic checksums, or physical identity) he lp to detect
lost writes? Unfortunately , the answer is no: the old block l ikely has a
matching checksum, and the physical ID used above (disk numb er and
block offset) will also be correct. Thus our ﬁnal problem:
CRUX : H OW TO HANDLE LOST WRITES
How should a storage system or disk controller detect lost wr ites?
What additional features are required from the checksum?
There are a number of possible solutions that can help [K+08] . One
classic approach [BS04] is to perform a write verify or read-after-write;
by immediately reading back the data after a write, a system c an ensure
that the data indeed reached the disk surface. This approach , however, is
quite slow , doubling the number of I/Os needed to complete a w rite.
Some systems add a checksum elsewhere in the system to detect lost
writes. For example, Sun’s Zettabyte File System (ZFS) includes a check-
sum in each ﬁle system inode and indirect block for every bloc k included
within a ﬁle. Thus, even if the write to a data block itself is l ost, the check-
sum within the inode will not match the old data. Only if the wr ites to
both the inode and the data are lost simultaneously will such a scheme
fail, an unlikely (but unfortunately , possible!) situation.
44.7 Scrubbing
Given all of this discussion, you might be wondering: when do these
checksums actually get checked? Of course, some amount of ch ecking
occurs when data is accessed by applications, but most data i s rarely
accessed, and thus would remain unchecked. Unchecked data i s prob-
lematic for a reliable storage system, as bit rot could event ually affect all
copies of a particular piece of data.
To remedy this problem, many systems utilize disk scrubbing of var-
ious forms [K+08]. By periodically reading through every block of the
system, and checking whether checksums are still valid, the disk system
can reduce the chances that all copies of a certain data item b ecome cor-
rupted. Typical systems schedule scans on a nightly or weekl y basis.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 572

536 DATA INTEGRITY AND PROTECTION
44.8 Overheads Of Checksumming
Before closing, we now discuss some of the overheads of using check-
sums for data protection. There are two distinct kinds of ove rheads, as is
common in computer systems: space and time.
Space overheads come in two forms. The ﬁrst is on the disk (or o ther
storage medium) itself; each stored checksum takes up room o n the disk,
which can no longer be used for user data. A typical ratio migh t be an 8-
byte checksum per 4 KB data block, for a 0.19% on-disk space ov erhead.
The second type of space overhead comes in the memory of the sy s-
tem. When accessing data, there must now be room in memory for the
checksums as well as the data itself. However, if the system simply checks
the checksum and then discards it once done, this overhead is short-lived
and not much of a concern. Only if checksums are kept in memory (for
an added level of protection against memory corruption [Z+1 3]) will this
small overhead be observable.
While space overheads are small, the time overheads inducedby check-
summing can be quite noticeable. Minimally , the CPU must com pute the
checksum over each block, both when the data is stored (to det ermine
the value of the stored checksum) as well as when it is accesse d (to com-
pute the checksum again and compare it against the stored che cksum).
One approach to reducing CPU overheads, employed by many sys tems
that use checksums (including network stacks), is to combin e data copy-
ing and checksumming into one streamlined activity; becaus e the copy is
needed anyhow (e.g., to copy the data from the kernel page cac he into a
user buffer), combined copying/checksumming can be quite e ffective.
Beyond CPU overheads, some checksumming schemes can induce ex-
tra I/O overheads, particularly when checksums are stored distinctly from
the data (thus requiring extra I/Os to access them), and for a ny extra I/O
needed for background scrubbing. The former can be reduced b y design;
the latter can be tuned and thus its impact limited, perhaps b y control-
ling when such scrubbing activity takes place. The middle of the night,
when most (not all!) productive workers have gone to bed, may be a
good time to perform such scrubbing activity and increase th e robustness
of the storage system.
44.9 Summary
We have discussed data protection in modern storage systems , focus-
ing on checksum implementation and usage. Different checksums protect
against different types of faults; as storage devices evolv e, new failure
modes will undoubtedly arise. Perhaps such change will forc e the re-
search community and industry to revisit some of these basic approaches,
or invent entirely new approaches altogether. Time will tel l. Or it won’t.
Time is funny that way .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 573

DATA INTEGRITY AND PROTECTION 537
References
[B+08] “An Analysis of Data Corruption in the Storage Stack”
Lakshmi N. Bairavasundaram, Garth R. Goodson, Bianca Schro eder,
Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau
FAST ’08, San Jose, CA, February 2008
The ﬁrst paper to truly study disk corruption in great detail , focusing on how often such corruption
occurs over three years for over 1.5 million drives. Lakshmi did this work while a graduate student at
Wisconsin under our supervision, but also in collaboration with his colleagues at NetApp where he was
an intern for multiple summers. A great example of how workin g with industry can make for much
more interesting and relevant research.
[BS04] “Commercial Fault Tolerance: A Tale of Two Systems”
Wendy Bartlett, Lisa Spainhower
IEEE Transactions on Dependable and Secure Computing, V ol. 1, No. 1, January 2004
This classic in building fault tolerant systems is an excell ent overview of the state of the art from both
IBM and Tandem. Another must read for those interested in the area.
[C+04] “Row-Diagonal Parity for Double Disk Failure Correc tion”
P . Corbett, B. English, A. Goel, T. Grcanac, S. Kleiman, J. Le ong, S. Sankar
FAST ’04, San Jose, CA, February 2004
An early paper on how extra redundancy helps to solve the combined full-disk-failure/partial-disk-failure
problem. Also a nice example of how to mix more theoretical wo rk with practical.
[F04] “Checksums and Error Control”
Peter M. Fenwick
Available: www.cs.auckland.ac.nz/compsci314s2c/resources/Checksums.pdf
A great simple tutorial on checksums, available to you for th e amazing cost of free.
[F82] “An Arithmetic Checksum for Serial Transmissions”
John G. Fletcher
IEEE Transactions on Communication, V ol. 30, No. 1, January 1982
Fletcher’s original work on his eponymous checksum. Of cour se, he didn’t call it the Fletcher checksum,
rather he just didn’t call it anything, and thus it became nat ural to name it after the inventor. So don’t
blame old Fletch for this seeming act of braggadocio.
[HLM94] “File System Design for an NFS File Server Appliance ”
Dave Hitz, James Lau, Michael Malcolm
USENIX Spring ’94
The pioneering paper that describes the ideas and product at the heart of NetApp’s core. Based on this
system, NetApp has grown into a multi-billion dollar storag e company. If you’re interested in learning
more about its founding, read Hitz’s autobiography “How to C astrate a Bull: Unexpected Lessons on
Risk, Growth, and Success in Business” (which is the actual t itle, no joking). And you thought you
could avoid bull castration by going into Computer Science.
[K+08] “Parity Lost and Parity Regained”
Andrew Krioukov , Lakshmi N. Bairavasundaram, Garth R. Goodson, Kiran Srinivasan,
Randy Thelen, Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Du sseau
FAST ’08, San Jose, CA, February 2008
This work of ours, joint with colleagues at NetApp, explores how different checksum schemes work (or
don’t work) in protecting data. We reveal a number of interes ting ﬂaws in current protection strategies,
some of which have led to ﬁxes in commercial products.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 574

538 DATA INTEGRITY AND PROTECTION
[M13] “Cyclic Redundancy Checks”
Author Unknown
Available: http://www.mathpages.com/home/kmath458.htm
Not sure who wrote this, but a super clear and concise description of CRCs is available here. The internet
is full of information, as it turns out.
[P+05] “IRON File Systems”
Vijayan Prabhakaran, Lakshmi N. Bairavasundaram, Nitin Ag rawal, Haryadi S. Gunawi, An-
drea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau
SOSP ’05, Brighton, England, October 2005
Our paper on how disks have partial failure modes, which incl udes a detailed study of how ﬁle systems
such as Linux ext3 and Windows NTFS react to such failures. As it turns out, rather poorly! We found
numerous bugs, design ﬂaws, and other oddities in this work. Some of this has fed back into the Linux
community, thus helping to yield a new more robust group of ﬁl e systems to store your data.
[RO91] “Design and Implementation of the Log-structured Fi le System”
Mendel Rosenblum and John Ousterhout
SOSP ’91, Paciﬁc Grove, CA, October 1991
Another reference to this ground-breaking paper on how to im prove write performance in ﬁle systems.
[S90] “Implementing Fault-Tolerant Services Using The Sta te Machine Approach: A Tutorial”
Fred B. Schneider
ACM Surveys, V ol. 22, No. 4, December 1990
This classic paper talks generally about how to build fault t olerant services, and includes many basic
deﬁnitions of terms. A must read for those building distribu ted systems.
[Z+13] “Zettabyte Reliability with Flexible End-to-end Da ta Integrity”
Yupu Zhang, Daniel S. Myers, Andrea C. Arpaci-Dusseau, Remz i H. Arpaci-Dusseau
MSST ’13, Long Beach, California, May 2013
Our own work on adding data protection to the page cache of a sy stem, which protects against memory
corruption as well as on-disk corruption.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 575

45
Summary Dialogue on Persistence
Student: Wow, ﬁle systems seem interesting(!), and yet complicated.
Professor: That’s why me and my spouse do our research in this space.
Student: Hold on. Are you one of the professors who wrote this book? I th ought
we were both just fake constructs, used to summarize some mai n points, and
perhaps add a little levity in the study of operating systems .
Professor: Uh... er... maybe. And none of your business! And who did you
think was writing these things? (sighs) Anyhow, let’s get on with it: what did
you learn?
Student: Well, I think I got one of the main points, which is that it is mu ch
harder to manage data for a long time (persistently) than it i s to manage data
that isn’t persistent (like the stuff in memory). After all, if your machines crashes,
memory contents disappear! But the stuff in the ﬁle system ne eds to live forever.
Professor: Well, as my friend Kevin Hultquist used to say, “Forever is a l ong
time”; while he was talking about plastic golf tees, it’s esp ecially true for the
garbage that is found in most ﬁle systems.
Student: Well, you know what I mean! For a long time at least. And even simple
things, such as updating a persistent storage device, are complicated, because you
have to care what happens if you crash. Recovery, something I had never even
thought of when we were virtualizing memory, is now a big deal !
Professor: T oo true. Updates to persistent storage have always been, an d re-
main, a fun and challenging problem.
Student: I also learned about cool things like disk scheduling, and ab out data
protection techniques like RAID and even checksums. That st uff is cool.
Professor: I like those topics too. Though, if you really get into it, the y can get a
little mathematical. Check out some the latest on erasure co des if you want your
brain to hurt.
Student: I’ll get right on that.
539

## Page 576

540 SUMMARY DIALOGUE ON PERSISTENCE
Professor: (frowns) I think you’re being sarcastic. Well, what else did you like?
Student: And I also liked all the thought that has gone into building technology-
aware systems, like FFS and LFS. Neat stuff! Being disk aware seems cool. But
will it matter anymore, with Flash and all the newest, latest technologies?
Professor: Good question! And a reminder to get working on that Flash cha p-
ter... (scribbles note down to self) ... But yes, even with Fl ash, all of this stuff
is still relevant, amazingly. For example, Flash T ranslati on Layers (FTLs) use
log-structuring internally, to improve performance and re liability of Flash-based
SSDs. And thinking about locality is always useful. So while the technology
may be changing, many of the ideas we have studied will contin ue to be useful,
for a while at least.
Student: That’s good. I just spent all this time learning it, and I didn ’t want it
to all be for no reason!
Professor: Professors wouldn’t do that to you, would they?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 577

46
A Dialogue on Distribution
Professor: And thus we reach our ﬁnal little piece in the world of operati ng
systems: distributed systems. Since we can’t cover much her e, we’ll sneak in a
little intro here in the section on persistence, and focus mo stly on distributed ﬁle
systems. Hope that is OK!
Student: Sounds OK. But what is a distributed system exactly, oh glori ous and
all-knowing professor?
Professor: Well, I bet you know how this is going to go...
Student: There’s a peach?
Professor: Exactly! But this time, it’s far away from you, and may take so me
time to get the peach. And there are a lot of them! Even worse, s ometimes a
peach becomes rotten. But you want to make sure that when anyb ody bites into
a peach, they will get a mouthful of deliciousness.
Student: This peach analogy is working less and less for me.
Professor: Come on! It’s the last one, just go with it.
Student: Fine.
Professor: So anyhow, forget about the peaches. Building distributed s ystems
is hard, because things fail all the time. Messages get lost, machines go down,
disks corrupt data. It’s like the whole world is working agai nst you!
Student: But I use distributed systems all the time, right?
Professor: Y es! Y ou do. And... ?
Student: Well, it seems like they mostly work. After all, when I send a s earch
request to google, it usually comes back in a snap, with some g reat results! Same
thing when I use facebook, or Amazon, and so forth.
541

## Page 578

542 A D IALOGUE ON DISTRIBUTION
Professor: Y es, it is amazing. And that’s despite all of those failures t aking
place! Those companies build a huge amount of machinery into their systems so
as to ensure that even though some machines have failed, the e ntire system stays
up and running. They use a lot of techniques to do this: replic ation, retry, and
various other tricks people have developed over time to dete ct and recover from
failures.
Student: Sounds interesting. Time to learn something for real?
Professor: It does seem so. Let’s get to work! But ﬁrst things ﬁrst ...
(bites into peach he has been holding, which unfortunately i s rotten)
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 579

47
Distributed Systems
Distributed systems have changed the face of the world. When your web
browser connects to a web server somewhere else on the planet , it is par-
ticipating in what seems to be a simple form of a client/server distributed
system. When you contact a modern web service such as Google o r face-
book, you are not just interacting with a single machine, how ever; be-
hind the scenes, these complex services are built from a larg e collection
(i.e., thousands) of machines, each of which cooperate to pr ovide the par-
ticular service of the site. Thus, it should be clear what mak es studying
distributed systems interesting. Indeed, it is worthy of an entire class;
here, we just introduce a few of the major topics.
A number of new challenges arise when building a distributed system.
The major one we focus on is failure; machines, disks, networks, and
software all fail from time to time, as we do not (and likely , w ill never)
know how to build “perfect” components and systems. However , when
we build a modern web service, we’d like it to appear to client s as if it
never fails; how can we accomplish this task?
THE CRUX :
HOW TO BUILD SYSTEMS THAT WORK WHEN COMPONENTS FAIL
How can we build a working system out of parts that don’t work c orrectly
all the time? The basic question should remind you of some of t he topics
we discussed in RAID storage arrays; however, the problems h ere tend
to be more complex, as are the solutions.
Interestingly , while failure is a central challenge in cons tructing dis-
tributed systems, it also represents an opportunity . Yes, m achines fail;
but the mere fact that a machine fails does not imply the entir e system
must fail. By collecting together a set of machines, we can bu ild a sys-
tem that appears to rarely fail, despite the fact that its com ponents fail
regularly . This reality is the central beauty and value of di stributed sys-
tems, and why they underly virtually every modern web servic e you use,
including Google, Facebook, etc.
543

## Page 580

544 DISTRIBUTED SYSTEMS
TIP : C OMMUNICATION IS INHERENTLY UNRELIABLE
In virtually all circumstances, it is good to view communica tion as a
fundamentally unreliable activity . Bit corruption, down o r non-working
links and machines, and lack of buffer space for incoming pac kets all lead
to the same result: packets sometimes do not reach their dest ination. To
build reliable services atop such unreliable networks, we m ust consider
techniques that can cope with packet loss.
Other important issues exist as well. System performance is often crit-
ical; with a network connecting our distributed system toge ther, system
designers must often think carefully about how to accomplis h their given
tasks, trying to reduce the number of messages sent and furth er make
communication as efﬁcient (low latency , high bandwidth) as possible.
Finally ,security is also a necessary consideration. When connecting
to a remote site, having some assurance that the remote party is who
they say they are becomes a central problem. Further, ensuri ng that third
parties cannot monitor or alter an on-going communication b etween two
others is also a challenge.
In this introduction, we’ll cover the most basic new aspect t hat is new
in a distributed system: communication. Namely , how should machines
within a distributed system communicate with one another? W e’ll start
with the most basic primitives available, messages, and build a few higher-
level primitives on top of them. As we said above, failure wil l be a central
focus: how should communication layers handle failures?
47.1 Communication Basics
The central tenet of modern networking is that communicatio n is fun-
damentally unreliable. Whether in the wide-area Internet, or a local-area
high-speed network such as Inﬁniband, packets are regularl y lost, cor-
rupted, or otherwise do not reach their destination.
There are a multitude of causes for packet loss or corruption . Some-
times, during transmission, some bits get ﬂipped due to electrical or other
similar problems. Sometimes, an element in the system, such as a net-
work link or packet router or even the remote host, are someho w dam-
aged or otherwise not working correctly; network cables do a ccidentally
get severed, at least sometimes.
More fundamental however is packet loss due to lack of buffer ing
within a network switch, router, or endpoint. Speciﬁcally , even if we
could guarantee that all links worked correctly , and that al l the compo-
nents in the system (switches, routers, end hosts) were up an d running as
expected, loss is still possible, for the following reason. Imagine a packet
arrives at a router; for the packet to be processed, it must be placed in
memory somewhere within the router. If many such packets arr ive at
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 581

DISTRIBUTED SYSTEMS 545
// client code
int main(int argc, char *argv[]) {
int sd = UDP_Open(20000);
struct sockaddr_in addr, addr2;
int rc = UDP_FillSockAddr(&addr, "machine.cs.wisc.edu", 10000);
char message[BUFFER_SIZE];
sprintf(message, "hello world");
rc = UDP_Write(sd, &addr, message, BUFFER_SIZE);
if (rc > 0) {
int rc = UDP_Read(sd, &addr2, buffer, BUFFER_SIZE);
}
return 0;
}
// server code
int main(int argc, char *argv[]) {
int sd = UDP_Open(10000);
assert(sd > -1);
while (1) {
struct sockaddr_in s;
char buffer[BUFFER_SIZE];
int rc = UDP_Read(sd, &s, buffer, BUFFER_SIZE);
if (rc > 0) {
char reply[BUFFER_SIZE];
sprintf(reply, "reply");
rc = UDP_Write(sd, &s, reply, BUFFER_SIZE);
}
}
return 0;
}
Figure 47.1: Example UDP/IP Client/Server Code
once, it is possible that the memory within the router cannot accommo-
date all of the packets. The only choice the router has at that point is
to drop one or more of the packets. This same behavior occurs at end
hosts as well; when you send a large number of messages to a sin gle ma-
chine, the machine’s resources can easily become overwhelm ed, and thus
packet loss again arises.
Thus, packet loss is fundamental in networking. The questio n thus
becomes: how should we deal with it?
47.2 Unreliable Communication Layers
One simple way is this: we don’t deal with it. Because some app li-
cations know how to deal with packet loss, it is sometimes use ful to let
them communicate with a basic unreliable messaging layer, a n example
of the end-to-end argument one often hears about (see the Aside at end
of chapter). One excellent example of such an unreliable lay er is found
in the UDP/IP networking stack available today on virtually all modern
systems. To use UDP , a process uses the sockets API in order to create a
communication endpoint ; processes on other machines (or on the same
machine) send UDP datagrams to the original process (a datagram is a
ﬁxed-sized message up to some max size).
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 582

546 DISTRIBUTED SYSTEMS
int UDP_Open(int port) {
int sd;
if ((sd = socket(AF_INET, SOCK_DGRAM, 0)) == -1) { return -1; }
struct sockaddr_in myaddr;
bzero(&myaddr, sizeof(myaddr));
myaddr.sin_family = AF_INET;
myaddr.sin_port = htons(port);
myaddr.sin_addr.s_addr = INADDR_ANY;
if (bind(sd, (struct sockaddr *) &myaddr, sizeof(myaddr)) == -1) {
close(sd);
return -1;
}
return sd;
}
int UDP_FillSockAddr(struct sockaddr_in *addr, char *hostName, int port) {
bzero(addr, sizeof(struct sockaddr_in));
addr->sin_family = AF_INET; // host byte order
addr->sin_port = htons(port); // short, network byte order
struct in_addr *inAddr;
struct hostent *hostEntry;
if ((hostEntry = gethostbyname(hostName)) == NULL) { retur n -1; }
inAddr = (struct in_addr *) hostEntry->h_addr;
addr->sin_addr = *inAddr;
return 0;
}
int UDP_Write(int sd, struct sockaddr_in *addr, char *buffer, int n) {
int addrLen = sizeof(struct sockaddr_in);
return sendto(sd, buffer, n, 0, (struct sockaddr *) addr, addrLen);
}
int UDP_Read(int sd, struct sockaddr_in *addr, char *buffer, int n) {
int len = sizeof(struct sockaddr_in);
return recvfrom(sd, buffer, n, 0, (struct sockaddr *) addr,
(socklen_t *) &len);
return rc;
}
Figure 47.2: A Simple UDP Library
Figures
47.1 and 47.2 show a simple client and server built on top of
UDP/IP . The client can send a message to the server, which then responds
with a reply . With this small amount of code, you have all you n eed to
begin building distributed systems!
UDP is a great example of an unreliable communication layer. If you
use it, you will encounter situations where packets get lost (dropped) and
thus do not reach their destination; the sender is never thus informed of
the loss. However, that does not mean that UDP does not guard a gainst
any failures at all. For example, UDP includes a checksum to detect some
forms of packet corruption.
However, because many applications simply want to send data to a
destination and not worry about packet loss, we need more. Sp eciﬁcally ,
we need reliable communication on top of an unreliable netwo rk.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 583

DISTRIBUTED SYSTEMS 547
TIP : U SE CHECKSUMS FOR INTEGRITY
Checksums are a commonly-used method to detect corruption q uickly
and effectively in modern systems. A simple checksum is addi tion: just
sum up the bytes of a chunk of data; of course, many other more s ophis-
ticated checksums have been created, including basic cycli c redundancy
codes (CRCs), the Fletcher checksum, and many others [MK09] .
In networking, checksums are used as follows. Before sendin g a message
from one machine to another, compute a checksum over the byte s of the
message. Then send both the message and the checksum to the de sti-
nation. At the destination, the receiver computes a checksu m over the
incoming message as well; if this computed checksum matches the sent
checksum, the receiver can feel some assurance that the data likely did
not get corrupted during transmission.
Checksums can be evaluated along a number of different axes. Effective-
ness is one primary consideration: does a change in the data l ead to a
change in the checksum? The stronger the checksum, the harde r it is for
changes in the data to go unnoticed. Performance is the other important
criterion: how costly is the checksum to compute? Unfortuna tely , effec-
tiveness and performance are often at odds, meaning that che cksums of
high quality are often expensive to compute. Life, again, is n’t perfect.
47.3 Reliable Communication Layers
To build a reliable communication layer, we need some new mec h-
anisms and techniques to handle packet loss. Let us consider a simple
example in which a client is sending a message to a server over an unreli-
able connection. The ﬁrst question we must answer: how does t he sender
know that the receiver has actually received the message?
The technique that we will use is known as an acknowledgment, or
ack for short. The idea is simple: the sender sends a message to th e re-
ceiver; the receiver then sends a short message back to acknowledge its
receipt. Figure
47.3 depicts the process.
Sender
[send message]
Receiver
[receive message]
[send ack]
[receive ack]
Figure 47.3: Message Plus Acknowledgment
When the sender receives an acknowledgment of the message, i t can
then rest assured that the message did indeed receive the ori ginal mes-
sage. However, what should the sender do if it does not receiv e an ac-
knowledgment?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 584

548 DISTRIBUTED SYSTEMS
Sender
[send message;
 keep copy;
 set timer]
Receiver
...
 (waiting for ack)
...
[timer goes off;
 set timer/retry]
[receive message]
[send ack]
[receive ack;
 delete copy/timer off]
Figure 47.4: Message Plus Acknowledgment: Dropped Request
To handle this case, we need an additional mechanism, known a s a
timeout. When the sender sends a message, the sender now sets a timer
to go off after some period of time. If, in that time, no acknow ledgment
has been received, the sender concludes that the message has been lost.
The sender then simply performs a retry of the send, sending the same
message again with hopes that this time, it will get through. For this
approach to work, the sender must keep a copy of the message ar ound,
in case it needs to send it again. The combination of the timeo ut and
the retry have led some to call the approach timeout/retry; pretty clever
crowd, those networking types, no? Figure 47.4 shows an example.
Unfortunately , timeout/retry in this form is not quite enou gh. Figure
47.5 shows an example of packet loss which could lead to trouble. I n this
example, it is not the original message that gets lost, but th e acknowledg-
ment. From the perspective of the sender, the situation seem s the same:
no ack was received, and thus a timeout and retry are in order. But from
the perspective of the receiver, it is quite different: now t he same message
has been received twice! While there may be cases where this i s OK, in
general it is not; imagine what would happen when you are downloading
a ﬁle and extra packets are repeated inside the download. Thu s, when we
are aiming for a reliable message layer, we also usually want to guarantee
that each message is received exactly once by the receiver.
To enable the receiver to detect duplicate message transmis sion, the
sender has to identify each message in some unique way , and the receiver
needs some way to track whether it has already seen each messa ge be-
fore. When the receiver sees a duplicate transmission, it si mply acks the
message, but (critically) does not pass the message to the application that
receives the data. Thus, the sender receives the ack but the m essage is not
received twice, preserving the exactly-once semantics men tioned above.
There are myriad ways to detect duplicate messages. For exam ple, the
sender could generate a unique ID for each message; the recei ver could
track every ID it has ever seen. This approach could work, but it is pro-
hibitively costly , requiring unbounded memory to track all IDs.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 585

DISTRIBUTED SYSTEMS 549
Sender
[send message;
 keep copy;
 set timer]
Receiver
[receive message]
[send ack]
...
 (waiting for ack)
...
[timer goes off;
 set timer/retry]
[receive message]
[send ack]
[receive ack;
 delete copy/timer off]
Figure 47.5: Message Plus Acknowledgment: Dropped Reply
A simpler approach, requiring little memory , solves this problem, and
the mechanism is known as a sequence counter. With a sequence counter,
the sender and receiver agree upon a start value (e.g., 1) for a counter
that each side will maintain. Whenever a message is sent, the current
value of the counter is sent along with the message; this coun ter value
(N ) serves as an ID for the message. After the message is sent, th e sender
then increments the value (to N + 1).
The receiver uses its counter value as the expected value for the ID
of the incoming message from that sender. If the ID of a receiv ed mes-
sage (N ) matches the receiver’s counter (also N ), it acks the message and
passes it up to the application; in this case, the receiver co ncludes this
is the ﬁrst time this message has been received. The receiver then incre-
ments its counter (to N + 1), and waits for the next message.
If the ack is lost, the sender will timeout and re-send messag e N . This
time, the receiver’s counter is higher ( N + 1), and thus the receiver knows
it has already received this message. Thus it acks the messag e but does
not pass it up to the application. In this simple manner, sequence counters
can be used to avoid duplicates.
The most commonly used reliable communication layer is know n as
TCP/IP, or just TCP for short. TCP has a great deal more sophistication
than we describe above, including machinery to handle conge stion in the
network [VJ90], multiple outstanding requests, and hundre ds of other
small tweaks and optimizations. Read more about it if you’re curious;
better yet, take a networking course and learn that material well.
47.4 Communication Abstractions
Given a basic messaging layer, we now approach the next quest ion
in this chapter: what abstraction of communication should w e use when
building a distributed system?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 586

550 DISTRIBUTED SYSTEMS
TIP : B E CAREFUL SETTING THE TIMEOUT VALUE
As you can probably guess from the discussion, setting the ti meout value
correctly is an important aspect of using timeouts to retry m essage sends.
If the timeout is too small, the sender will re-send messages needlessly ,
thus wasting CPU time on the sender and network resources. If the time-
out is too large, the sender waits too long to re-send and thus perceived
performance at the sender is reduced. The “right” value, fro m the per-
spective of a single client and server, is thus to wait just lo ng enough to
detect packet loss but no longer.
However, there are often more than just a single client and se rver in a
distributed system, as we will see in future chapters. In a sc enario with
many clients sending to a single server, packet loss at the se rver may be
an indicator that the server is overloaded. If true, clients might retry in
a different adaptive manner; for example, after the ﬁrst tim eout, a client
might increase its timeout value to a higher amount, perhaps twice as
high as the original value. Such an exponential back-off scheme, pio-
neered in the early Aloha network and adopted in early Ethern et [A70],
avoid situations where resources are being overloaded by an excess of
re-sends. Robust systems strive to avoid overload of this na ture.
The systems community developed a number of approaches over the
years. One body of work took OS abstractions and extended the m to
operate in a distributed environment. For example, distributed shared
memory (DSM) systems enable processes on different machines to share
a large, virtual address space [LH89]. This abstraction tur ns a distributed
computation into something that looks like a multi-threade d application;
the only difference is that these threads run on different ma chines instead
of different processors within the same machine.
The way most DSM systems work is through the virtual memory sy s-
tem of the OS. When a page is accessed on one machine, two thing s can
happen. In the ﬁrst (best) case, the page is already local on t he machine,
and thus the data is fetched quickly . In the second case, the p age is cur-
rently on some other machine. A page fault occurs, and the pag e fault
handler sends a message to some other machine to fetch the pag e, install
it in the page table of the requesting process, and continue e xecution.
This approach is not widely in use today for a number of reason s. The
largest problem for DSM is how it handles failure. Imagine, f or example,
if a machine fails; what happens to the pages on that machine? What if
the data structures of the distributed computation are spre ad across the
entire address space? In this case, parts of these data struc tures would
suddenly become unavailable. Dealing with failure when par ts of your
address space go missing is hard; imagine a linked list that w here a next
pointer points into a portion of the address space that is gon e. Yikes!
A further problem is performance. One usually assumes, when writ-
ing code, that access to memory is cheap. In DSM systems, some accesses
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 587

DISTRIBUTED SYSTEMS 551
are inexpensive, but others cause page faults and expensive fetches from
remote machines. Thus, programmers of such DSM systems had t o be
very careful to organize computations such that almost no co mmunica-
tion occurred at all, defeating much of the point of such an ap proach.
Though much research was performed in this space, there was l ittle prac-
tical impact; nobody builds reliable distributed systems using DSM today .
47.5 Remote Procedure Call (RPC)
While OS abstractions turned out to be a poor choice for build ing dis-
tributed systems, programming language (PL) abstractions make much
more sense. The most dominant abstraction is based on the ide a of a re-
mote procedure call, or RPC for short [BN84] 1.
Remote procedure call packages all have a simple goal: to mak e the
process of executing code on a remote machine as simple and st raight-
forward as calling a local function. Thus, to a client, a proc edure call is
made, and some time later, the results are returned. The serv er simply
deﬁnes some routines that it wishes to export. The rest of the magic is
handled by the RPC system, which in general has two pieces: a stub gen-
erator (sometimes called a protocol compiler), and the run-time library.
We’ll now take a look at each of these pieces in more detail.
Stub Generator
The stub generator’s job is simple: to remove some of the pain of packing
function arguments and results into messages by automating it. Numer-
ous beneﬁts arise: one avoids, by design, the simple mistake s that occur
in writing such code by hand; further, a stub compiler can per haps opti-
mize such code and thus improve performance.
The input to such a compiler is simply the set of calls a server wishes
to export to clients. Conceptually , it could be something as simple as this:
interface {
int func1(int arg1);
int func2(int arg1, int arg2);
};
The stub generator takes an interface like this and generate s a few dif-
ferent pieces of code. For the client, a client stub is generated, which
contains each of the functions speciﬁed in the interface; a c lient program
wishing to use this RPC service would link with this client st ub and call
into it in order to make RPCs.
Internally , each of these functions in the client stub do all of the work
needed to perform the remote procedure call. To the client, t he code just
1In modern programming languages, we might instead say remote method invocation
(RMI), but who likes these languages anyhow, with all of their fan cy objects?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 588

552 DISTRIBUTED SYSTEMS
appears as a function call (e.g., the client calls func1(x)); internally , the
code in the client stub for func1() does this:
• Create a message buffer. A message buffer is usually just a con-
tiguous array of bytes of some size.
• Pack the needed information into the message buffer. This infor-
mation includes some kind of identiﬁer for the function to be called,
as well as all of the arguments that the function needs (e.g., in our
example above, one integer for func1). The process of putting all
of this information into a single contiguous buffer is somet imes re-
ferred to as the marshaling of arguments or the serialization of the
message.
• Send the message to the destination RPC server. The communi-
cation with the RPC server, and all of the details required to make
it operate correctly , are handled by the RPC run-time librar y , de-
scribed further below .
• Wait for the reply. Because function calls are usually synchronous,
the call will wait for its completion.
• Unpack return code and other arguments. If the function just re-
turns a single return code, this process is straightforward ; however,
more complex functions might return more complex results (e .g., a
list), and thus the stub might need to unpack those as well. Th is
step is also known as unmarshaling or deserialization.
• Return to the caller. Finally , just return from the client stub back
into the client code.
For the server, code is also generated. The steps taken on the server
are as follows:
• Unpack the message. This step, called unmarshaling or deserial-
ization, takes the information out of the incoming message. The
function identiﬁer and arguments are extracted.
• Call into the actual function. Finally! We have reached the point
where the remote function is actually executed. The RPC runt ime
calls into the function speciﬁed by the ID and passes in the de sired
arguments.
• Package the results. The return argument(s) are marshaled back
into a single reply buffer.
• Send the reply. The reply is ﬁnally sent to the caller.
There are a few other important issues to consider in a stub co mpiler.
The ﬁrst is complex arguments, i.e., how does one package and send
a complex data structure? For example, when one calls the write()
system call, one passes in three arguments: an integer ﬁle de scriptor, a
pointer to a buffer, and a size indicating how many bytes (sta rting at the
pointer) are to be written. If an RPC package is passed a point er, it needs
to be able to ﬁgure out how to interpret that pointer, and perf orm the
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 589

DISTRIBUTED SYSTEMS 553
correct action. Usually this is accomplished through eithe r well-known
types (e.g., a buffer t that is used to pass chunks of data given a size,
which the RPC compiler understands), or by annotating the da ta struc-
tures with more information, enabling the compiler to know w hich bytes
need to be serialized.
Another important issue is the organization of the server wi th regards
to concurrency . A simple server just waits for requests in a s imple loop,
and handles each request one at a time. However, as you might h ave
guessed, this can be grossly inefﬁcient; if one RPC call bloc ks (e.g., on
I/O), server resources are wasted. Thus, most servers are co nstructed in
some sort of concurrent fashion. A common organization is a thread pool.
In this organization, a ﬁnite set of threads are created when the server
starts; when a message arrives, it is dispatched to one of the se worker
threads, which then does the work of the RPC call, eventually replying;
during this time, a main thread keeps receiving other reques ts, and per-
haps dispatching them to other workers. Such an organizatio n enables
concurrent execution within the server, thus increasing it s utilization; the
standard costs arise as well, mostly in programming complex ity , as the
RPC calls may now need to use locks and other synchronization primi-
tives in order to ensure their correct operation.
Run-Time Library
The run-time library handles much of the heavy lifting in an R PC system;
most performance and reliability issues are handled herein . We’ll now
discuss some of the major challenges in building such a run-t ime layer.
One of the ﬁrst challenges we must overcome is how to locate a r e-
mote service. This problem, of naming, is a common one in distributed
systems, and in some sense goes beyond the scope of our curren t discus-
sion. The simplest of approaches build on existing naming sy stems, e.g.,
hostnames and port numbers provided by current internet pro tocols. In
such a system, the client must know the hostname or IP address of the
machine running the desired RPC service, as well as the port n umber it is
using (a port number is just a way of identifying a particular communica-
tion activity taking place on a machine, allowing multiple communication
channels at once). The protocol suite must then provide a mec hanism to
route packets to a particular address from any other machine in the sys-
tem. For a good discussion of naming, read either the Grapevi ne paper
or about DNS and name resolution on the Internet, or better ye t just read
the excellent chapter in Saltzer and Kaashoek’s book [SK09] .
Once a client knows which server it should talk to for a partic ular re-
mote service, the next question is which transport-level pr otocol should
RPC be built upon. Speciﬁcally , should the RPC system use a reliable pro-
tocol such as TCP/IP , or be built upon an unreliable communication layer
such as UDP/IP?
Naively the choice would seem easy: clearly we would like for a re-
quest to be reliably delivered to the remote server, and clea rly we would
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 590

554 DISTRIBUTED SYSTEMS
like to reliably receive a reply . Thus we should choose the re liable trans-
port protocol such as TCP , right?
Unfortunately , building RPC on top of a reliable communication layer
can lead to a major inefﬁciency in performance. Recall from t he discus-
sion above how reliable communication layers work: with ack nowledg-
ments plus timeout/retry . Thus, when the client sends an RPC request
to the server, the server responds with an acknowledgment so that the
caller knows the request was received. Similarly , when the s erver sends
the reply to the client, the client acks it so that the server k nows it was
received. By building a request/response protocol (such as RPC) on top
of a reliable communication layer, two “extra” messages are sent.
For this reason, many RPC packages are built on top of unreliable com-
munication layers, such as UDP . Doing so enables a more efﬁci ent RPC
layer, but does add the responsibility of providing reliabi lity to the RPC
system. The RPC layer achieves the desired level of responsi bility by us-
ing timeout/retry and acknowledgments much like we describ ed above.
By using some form of sequence numbering, the communication layer
can guarantee that each RPC takes place exactly once (in the c ase of no
failure), or at most once (in the case where failure arises).
Other Issues
There are some other issues an RPC run-time must handle as wel l. For
example, what happens when a remote call takes a long time to c om-
plete? Given our timeout machinery , a long-running remote c all might
appear as a failure to a client, thus triggering a retry , and t hus the need
for some care here. One solution is to use an explicit acknowl edgment
(from the receiver to sender) when the reply isn’t immediate ly generated;
this lets the client know the server received the request. Th en, after some
time has passed, the client can periodically ask whether the server is still
working on the request; if the server keeps saying “yes”, the client should
be happy and continue to wait (after all, sometimes a procedu re call can
take a long time to ﬁnish executing).
The run-time must also handle procedure calls with large arg uments,
larger than what can ﬁt into a single packet. Some lower-leve l network
protocols provide such sender-side fragmentation (of larger packets into
a set of smaller ones) and receiver-side reassembly (of smaller parts into
one larger logical whole); if not, the RPC run-time may have to implement
such functionality itself. See Birrell and Nelson’s excell ent RPC paper for
details [BN84].
One issue that many systems handle is that of byte ordering. As you
may know , some machines store values in what is known as big endian
ordering, whereas others use little endian ordering. Big endian stores
bytes (say , of an integer) from most signiﬁcant to least sign iﬁcant bits,
much like Arabic numerals; little endian does the opposite. Both are
equally valid ways of storing numeric information; the ques tion here is
how to communicate between machines of different endianness.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 591

DISTRIBUTED SYSTEMS 555
Aside: The End-to-End Argument
The end-to-end argument makes the case that the highest level in a
system, i.e., usually the application at “the end”, is ultim ately the only
locale within a layered system where certain functionality can truly be
implemented. In their landmark paper, Saltzer et al. argue t his through
an excellent example: reliable ﬁle transfer between two mac hines. If you
want to transfer a ﬁle from machine A to machine B, and make sure that
the bytes that end up on B are exactly the same as those that began on
A, you must have an “end-to-end” check of this; lower-level re liable ma-
chinery , e.g., in the network or disk, provides no such guara ntee.
The contrast is an approach which tries to solve the reliable -ﬁle-
transfer problem by adding reliability to lower layers of th e system. For
example, say we build a reliable communication protocol and use it to
build our reliable ﬁle transfer. The communication protoco l guarantees
that every byte sent by a sender will be received in order by th e receiver,
say using timeout/retry , acknowledgments, and sequence numbers. Un-
fortunately , using such a protocol does not a reliable ﬁle tr ansfer make;
imagine the bytes getting corrupted in sender memory before the com-
munication even takes place, or something bad happening whe n the re-
ceiver writes the data to disk. In those cases, even though th e bytes were
delivered reliably across the network, our ﬁle transfer was ultimately
not reliable. To build a reliable ﬁle transfer, one must incl ude end-to-
end checks of reliability , e.g., after the entire transfer i s complete, read
back the ﬁle on the receiver disk, compute a checksum, and com pare that
checksum to that of the ﬁle on the sender.
The corollary to this maxim is that sometimes having lower layers pro-
vide extra functionality can indeed improve system perform ance or oth-
erwise optimize a system. Thus, you should not rule out havin g such
machinery at a lower-level in a system; rather, you should ca refully con-
sider the utility of such machinery , given its eventual usag e in an overall
system or application.
RPC packages often handle this by providing a well-deﬁned en dian-
ness within their message formats. In Sun’s RPC package, the XDR (eX-
ternal Data Representation ) layer provides this functionality . If the ma-
chine sending or receiving a message matches the endianness of XDR,
messages are just sent and received as expected. If, however , the machine
communicating has a different endianness, each piece of inf ormation in
the message must be converted. Thus, the difference in endia nness can
have a small performance cost.
A ﬁnal issue is whether to expose the asynchronous nature of c om-
munication to clients, thus enabling some performance opti mizations.
Speciﬁcally , typical RPCs are made synchronously, i.e., when a client
issues the procedure call, it must wait for the procedure cal l to return
before continuing. Because this wait can be long, and becaus e the client
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 592

556 DISTRIBUTED SYSTEMS
may have other work it could be doing, some RPC packages enabl e you
to invoke an RPC asynchronously. When an asynchronous RPC is is-
sued, the RPC package sends the request and returns immediat ely; the
client is then free to do other work, such as call other RPCs or other use-
ful computation. The client at some point will want to see the results of
the asynchronous RPC; it thus calls back into the RPC layer, t elling it to
wait for outstanding RPCs to complete, at which point return arguments
can be accessed.
47.6 Summary
We have seen the introduction of a new topic, distributed systems, and
its major issue: how to handle failure which is now a commonplace event.
As they say inside of Google, when you have just your desktop m achine,
failure is rare; when you’re in a data center with thousands o f machines,
failure is happening all the time. The key to any distributed system is
how you deal with that failure.
We have also seen that communication forms the heart of any di s-
tributed system. A common abstraction of that communicatio n is found
in remote procedure call (RPC), which enables clients to mak e remote
calls on servers; the RPC package handles all of the gory deta ils, includ-
ing timeout/retry and acknowledgment, in order to deliver a service that
closely mirrors a local procedure call.
The best way to really understand an RPC package is of course t o use
one yourself. Sun’s RPC system, using the stub compiler rpcgen, is a
common one, and is widely available on systems today , includ ing Linux.
Try it out, and see what all the fuss is about.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 593

DISTRIBUTED SYSTEMS 557
References
[A70] “The ALOHA System – Another Alternative for Computer C ommunications”
Norman Abramson
The 1970 Fall Joint Computer Conference
The ALOHA network pioneered some basic concepts in networki ng, including exponential back-off and
retransmit, which formed the basis for communication in sha red-bus Ethernet networks for years.
[BN84] “Implementing Remote Procedure Calls”
Andrew D. Birrell, Bruce Jay Nelson
ACM TOCS, V olume 2:1, February 1984
The foundational RPC system upon which all others build. Y es , another pioneering effort from our
friends at Xerox P ARC.
[MK09] “The Effectiveness of Checksums for Embedded Contro l Networks”
Theresa C. Maxino and Philip J. Koopman
IEEE Transactions on Dependable and Secure Computing, 6:1, January ’09
A nice overview of basic checksum machinery and some perform ance and robustness comparisons be-
tween them.
[LH89] “Memory Coherence in Shared Virtual Memory Systems”
Kai Li and Paul Hudak
ACM TOCS, 7:4, November 1989
The introduction of software-based shared memory via virtu al memory. An intriguing idea for sure, but
not a lasting or good one in the end.
[SK09] “Principles of Computer System Design”
Jerome H. Saltzer and M. Frans Kaashoek
Morgan-Kaufmann, 2009
An excellent book on systems, and a must for every bookshelf. One of the few terriﬁc discussions on
naming we’ve seen.
[SRC84] “End-To-End Arguments in System Design”
Jerome H. Saltzer, David P . Reed, David D. Clark
ACM TOCS, 2:4, November 1984
A beautiful discussion of layering, abstraction, and where functionality must ultimately reside in com-
puter systems.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 595

48
Sun’s Network File System (NFS)
One of the ﬁrst uses of distributed client/server computing was in the
realm of distributed ﬁle systems. In such an environment, th ere are a
number of client machines and one server (or a few); the serve r stores the
data on its disks, and clients request data through well-for med protocol
messages. Figure 48.1 depicts the basic setup.
Client 0
Client 1
Client 2
Client 3
ServerNetwork
Figure 48.1: A Generic Client/Server System
As you can see from the picture, the server has the disks, and c lients
send messages network to access their directories and ﬁles on those disks.
Why do we bother with this arrangement? (i.e., why don’t we ju st let
clients use their local disks?) Well, primarily this setup a llows for easy
sharing of data across clients. Thus, if you access a ﬁle on one machin e
(Client 0) and then later use another (Client 2), you will hav e the same
view of the ﬁle system. Your data is naturally shared across t hese dif-
ferent machines. A secondary beneﬁt is centralized administration ; for
example, backing up ﬁles can be done from the few server machi nes in-
stead of from the multitude of clients. Another advantage co uld be secu-
rity; having all servers in a locked machine room prevents certai n types
of problems from arising.
559

## Page 596

560 SUN ’ S NETWORK FILE SYSTEM (NFS)
CRUX : H OW TO BUILD A D ISTRIBUTED FILE SYSTEM
How do you build a distributed ﬁle system? What are the key asp ects
to think about? What is easy to get wrong? What can we learn fro m
existing systems?
48.1 A Basic Distributed File System
We now will study the architecture of a simpliﬁed distribute d ﬁle sys-
tem. A simple client/server distributed ﬁle system has more components
than the ﬁle systems we have studied so far. On the client side , there are
client applications which access ﬁles and directories thro ugh the client-
side ﬁle system. A client application issues system calls to the client-side
ﬁle system (such as open(), read(), write(), close(), mkdir(),
etc.) in order to access ﬁles which are stored on the server. T hus, to client
applications, the ﬁle system does not appear to be any differ ent than a lo-
cal (disk-based) ﬁle system, except perhaps for performanc e; in this way ,
distributed ﬁle systems provide transparent access to ﬁles, an obvious
goal; after all, who would want to use a ﬁle system that requir ed a differ-
ent set of APIs or otherwise was a pain to use?
The role of the client-side ﬁle system is to execute the actio ns needed
to service those system calls. For example, if the client iss ues a read()
request, the client-side ﬁle system may send a message to the server-side
ﬁle system (or, more commonly , theﬁle server) to read a particular block;
the ﬁle server will then read the block from disk (or its own in -memory
cache), and send a message back to the client with the request ed data.
The client-side ﬁle system will then copy the data into the us er buffer
supplied to the read() system call and thus the request will complete.
Note that a subsequent read() of the same block on the client may be
cached in client memory or on the client’s disk even; in the best such case,
no network trafﬁc need be generated.
Client Application
Client-side File System
Networking Layer
File Server
Networking Layer
Disks
Figure 48.2: Distributed File System Architecture
From this simple overview , you should get a sense that there a re two
important pieces of software in a client/server distributed ﬁle system: the
client-side ﬁle system and the ﬁle server. Together their be havior deter-
mines the behavior of the distributed ﬁle system. Now it’s ti me to study
one particular system: Sun’s Network File System (NFS).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 597

SUN ’ S NETWORK FILE SYSTEM (NFS) 561
ASIDE : WHY SERVERS CRASH
Before getting into the details of the NFSv2 protocol, you mi ght be
wondering: why do servers crash? Well, as you might guess, th ere are
plenty of reasons. Servers may simply suffer from a power outage (tem-
porarily); only when power is restored can the machines be re started.
Servers are often comprised of hundreds of thousands or even millions
of lines of code; thus, they have bugs (even good software has a few
bugs per hundred or thousand lines of code), and thus they eve ntually
will trigger a bug that will cause them to crash. They also hav e memory
leaks; even a small memory leak will cause a system to run out o f mem-
ory and crash. And, ﬁnally , in distributed systems, there is a network
between the client and the server; if the network acts strang ely (for ex-
ample, if it becomes partitioned and clients and servers are working but
cannot communicate), it may appear as if a remote machine has crashed,
but in reality it is just not currently reachable through the network.
48.2 On To NFS
One of the earliest and quite successful distributed system s was devel-
oped by Sun Microsystems, and is known as the Sun Network File Sys-
tem (or NFS) [S86]. In deﬁning NFS, Sun took an unusual approa ch: in-
stead of building a proprietary and closed system, Sun inste ad developed
an open protocol which simply speciﬁed the exact message formats that
clients and servers would use to communicate. Different gro ups could
develop their own NFS servers and thus compete in an NFS marke tplace
while preserving interoperability . It worked: today there are many com-
panies that sell NFS servers (including Oracle/Sun, NetApp [HLM94],
EMC, IBM, and others), and the widespread success of NFS is li kely at-
tributed to this “open market” approach.
48.3 Focus: Simple and Fast Server Crash Recovery
In this chapter, we will discuss the classic NFS protocol (ve rsion 2,
a.k.a. NFSv2), which was the standard for many years; small c hanges
were made in moving to NFSv3, and larger-scale protocol chan ges were
made in moving to NFSv4. However, NFSv2 is both wonderful and frus-
trating and thus serves as our focus.
In NFSv2, the main goal in the design of the protocol was simple and
fast server crash recovery . In a multiple-client, single-server environment,
this goal makes a great deal of sense; any minute that the serv er is down
(or unavailable) makes all the client machines (and their users) unhappy
and unproductive. Thus, as the server goes, so goes the entir e system.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 598

562 SUN ’ S NETWORK FILE SYSTEM (NFS)
48.4 Key To Fast Crash Recovery: Statelessness
This simple goal is realized in NFSv2 by designing what we ref er to
as a stateless protocol. The server, by design, does not keep track of any-
thing about what is happening at each client. For example, th e server
does not know which clients are caching which blocks, or whic h ﬁles are
currently open at each client, or the current ﬁle pointer pos ition for a ﬁle,
etc. Simply put, the server does not track anything about wha t clients are
doing; rather, the protocol is designed to deliver in each pr otocol request
all the information that is needed in order to complete the request. If it
doesn’t now , this stateless approach will make more sense as we discuss
the protocol in more detail below .
For an example of a stateful (not stateless) protocol, consider the open()
system call. Given a pathname, open() returns a ﬁle descriptor (an inte-
ger). This descriptor is used on subsequent read() or write() requests
to access various ﬁle blocks, as in this application code (no te that proper
error checking of the system calls is omitted for space reaso ns):
char buffer[MAX];
int fd = open("foo", O_RDONLY); // get descriptor "fd"
read(fd, buffer, MAX); // read MAX bytes from foo (via fd)
read(fd, buffer, MAX); // read MAX bytes from foo
...
read(fd, buffer, MAX); // read MAX bytes from foo
close(fd); // close file
Figure 48.3: Client Code: Reading From A File
Now imagine that the client-side ﬁle system opens the ﬁle by s ending
a protocol message to the server saying “open the ﬁle ’foo’ an d give me
back a descriptor”. The ﬁle server then opens the ﬁle locally on its side
and sends the descriptor back to the client. On subsequent re ads, the
client application uses that descriptor to call the read() system call; the
client-side ﬁle system then passes the descriptor in a messa ge to the ﬁle
server, saying “read some bytes from the ﬁle that is referred to by the
descriptor I am passing you here”.
In this example, the ﬁle descriptor is a piece of shared state between
the client and the server (Ousterhout calls this distributed state [O91]).
Shared state, as we hinted above, complicates crash recover y . Imagine
the server crashes after the ﬁrst read completes, but before the client
has issued the second one. After the server is up and running a gain,
the client then issues the second read. Unfortunately , the s erver has no
idea to which ﬁle fd is referring; that information was ephemeral (i.e.,
in memory) and thus lost when the server crashed. To handle th is situa-
tion, the client and server would have to engage in some kind o f recovery
protocol, where the client would make sure to keep enough information
around in its memory to be able to tell the server what it needs to know
(in this case, that ﬁle descriptor fd refers to ﬁle foo).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 599

SUN ’ S NETWORK FILE SYSTEM (NFS) 563
It gets even worse when you consider the fact that a stateful s erver has
to deal with client crashes. Imagine, for example, a client t hat opens a ﬁle
and then crashes. The open() uses up a ﬁle descriptor on the server; how
can the server know it is OK to close a given ﬁle? In normal oper ation, a
client would eventually call close() and thus inform the server that the
ﬁle should be closed. However, when a client crashes, the ser ver never
receives a close(), and thus has to notice the client has crashed in order
to close the ﬁle.
For these reasons, the designers of NFS decided to pursue a st ateless
approach: each client operation contains all the informati on needed to
complete the request. No fancy crash recovery is needed; the server just
starts running again, and a client, at worst, might have to re try a request.
48.5 The NFSv2 Protocol
We thus arrive at the NFSv2 protocol deﬁnition. Our problem s tate-
ment is simple:
THE CRUX : H OW TO DEFINE A S TATELESS FILE PROTOCOL
How can we deﬁne the network protocol to enable stateless operation?
Clearly , stateful calls like open() can’t be a part of the discussion (as it
would require the server to track open ﬁles); however, the cl ient appli-
cation will want to call open(), read(), write(), close() and other
standard API calls to access ﬁles and directories. Thus, as a reﬁned ques-
tion, how do we deﬁne the protocol to both be stateless and support the
POSIX ﬁle system API?
One key to understanding the design of the NFS protocol is und er-
standing the ﬁle handle . File handles are used to uniquely describe the
ﬁle or directory a particular operation is going to operate u pon; thus,
many of the protocol requests include a ﬁle handle.
You can think of a ﬁle handle as having three important components: a
volume identiﬁer, an inode number, and a generation number; together, these
three items comprise a unique identiﬁer for a ﬁle or director y that a client
wishes to access. The volume identiﬁer informs the server wh ich ﬁle sys-
tem the request refers to (an NFS server can export more than o ne ﬁle
system); the inode number tells the server which ﬁle within t hat partition
the request is accessing. Finally , the generation number is needed when
reusing an inode number; by incrementing it whenever an inod e num-
ber is reused, the server ensures that a client with an old ﬁle handle can’t
accidentally access the newly-allocated ﬁle.
Here is a summary of some of the important pieces of the protoc ol; the
full protocol is available elsewhere (see Callaghan’s book for an excellent
and detailed overview of NFS [C00]).
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 600

564 SUN ’ S NETWORK FILE SYSTEM (NFS)
NFSPROC_GETATTR
expects: file handle
returns: attributes
NFSPROC_SETATTR
expects: file handle, attributes
returns: nothing
NFSPROC_LOOKUP
expects: directory file handle, name of file/directory to l ook up
returns: file handle
NFSPROC_READ
expects: file handle, offset, count
returns: data, attributes
NFSPROC_WRITE
expects: file handle, offset, count, data
returns: attributes
NFSPROC_CREATE
expects: directory file handle, name of file, attributes
returns: nothing
NFSPROC_REMOVE
expects: directory file handle, name of file to be removed
returns: nothing
NFSPROC_MKDIR
expects: directory file handle, name of directory, attribu tes
returns: file handle
NFSPROC_RMDIR
expects: directory file handle, name of directory to be remo ved
returns: nothing
NFSPROC_READDIR
expects: directory handle, count of bytes to read, cookie
returns: directory entries, cookie (to get more entries)
Figure 48.4: The NFS Protocol: Examples
We brieﬂy highlight the important components of the protoco l. First,
the LOOKUP protocol message is used to obtain a ﬁle handle, wh ich is
then subsequently used to access ﬁle data. The client passes a directory
ﬁle handle and name of a ﬁle to look up, and the handle to that ﬁl e (or
directory) plus its attributes are passed back to the client from the server.
For example, assume the client already has a directory ﬁle ha ndle for
the root directory of a ﬁle system ( /) (indeed, this would be obtained
through the NFS mount protocol , which is how clients and servers ﬁrst
are connected together; we do not discuss the mount protocol here for
sake of brevity). If an application running on the client ope ns the ﬁle
/foo.txt, the client-side ﬁle system sends a lookup request to the server,
passing it the root ﬁle handle and the name foo.txt; if successful, the
ﬁle handle (and attributes) for foo.txt will be returned.
In case you are wondering, attributes are just the metadata t hat the ﬁle
system tracks about each ﬁle, including ﬁelds such as ﬁle cre ation time,
last modiﬁcation time, size, ownership and permissions inf ormation, and
so forth, i.e., the same type of information that you would ge t back if you
called stat() on a ﬁle.
Once a ﬁle handle is available, the client can issue READ and W RITE
protocol messages on a ﬁle to read or write the ﬁle, respectiv ely . The
READ protocol message requires the protocol to pass along the ﬁle handle
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

