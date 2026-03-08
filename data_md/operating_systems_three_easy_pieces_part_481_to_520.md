# Document: operating_systems_three_easy_pieces (Pages 481 to 520)

## Page 481

INTERLUDE : F ILE AND DIRECTORIES 445
TIP : U SE S T R A C E (A ND SIMILAR TOOLS )
The strace tool provides an awesome way to see what programs are up
to. By running it, you can trace which system calls a program m akes, see
the arguments and return codes, and generally get a very good idea of
what is going on.
The tool also takes some arguments which can be quite useful. For ex-
ample, -f follows any fork’d children too; -t reports the time of day
at each call; -e trace=open,close,read,write only traces calls to
those system calls and ignores all others. There are many mor e powerful
ﬂags – read the man pages and ﬁnd out how to harness this wonder ful
tool.
Here is an example of using strace to ﬁgure out what cat is doing
(some calls removed for readability):
prompt> strace cat foo
...
open("foo", O_RDONLY|O_LARGEFILE) = 3
read(3, "hello\n", 4096) = 6
write(1, "hello\n", 6) = 6
hello
read(3, "", 4096) = 0
close(3) = 0
...
prompt>
The ﬁrst thing that cat does is open the ﬁle for reading. A couple
of things we should note about this; ﬁrst, that the ﬁle is only opened for
reading (not writing), as indicated by the O
RDONLY ﬂag; second, that
the 64-bit offset be used ( O LARGEFILE); third, that the call to open()
succeeds and returns a ﬁle descriptor, which has the value of 3.
Why does the ﬁrst call to open() return 3, not 0 or perhaps 1 as you
might expect? As it turns out, each running process already h as three
ﬁles open, standard input (which the process can read to rece ive input),
standard output (which the process can write to in order to du mp infor-
mation to the screen), and standard error (which the process can write
error messages to). These are represented by ﬁle descriptor s 0, 1, and 2,
respectively . Thus, when you ﬁrst open another ﬁle (as cat does above),
it will almost certainly be ﬁle descriptor 3.
After the open succeeds, cat uses the read() system call to repeat-
edly read some bytes from a ﬁle. The ﬁrst argument to read() is the ﬁle
descriptor, thus telling the ﬁle system which ﬁle to read; a p rocess can of
course have multiple ﬁles open at once, and thus the descript or enables
the operating system to know which ﬁle a particular read refe rs to. The
second argument points to a buffer where the result of the read() will be
placed; in the system-call trace above, strace shows the res ults of the read
in this spot (“hello”). The third argument is the size of the b uffer, which
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 482

446 INTERLUDE : F ILE AND DIRECTORIES
in this case is 4 KB. The call to read() returns successfully as well, here
returning the number of bytes it read (6, which includes 5 for the letters
in the word “hello” and one for an end-of-line marker).
At this point, you see another interesting result of the stra ce: a single
call to the write() system call, to the ﬁle descriptor 1. As we mentioned
above, this descriptor is known as the standard output, and t hus is used
to write the word “hello” to the screen as the program cat is meant to
do. But does it call write() directly? Maybe (if it is highly optimized).
But if not, what cat might do is call the library routine printf(); in-
ternally ,printf() ﬁgures out all the formatting details passed to it, and
eventually calls write on the standard output to print the re sults to the
screen.
The cat program then tries to read more from the ﬁle, but since there
are no bytes left in the ﬁle, the read() returns 0 and the program knows
that this means it has read the entire ﬁle. Thus, the program calls close()
to indicate that it is done with the ﬁle “foo”, passing in the c orresponding
ﬁle descriptor. The ﬁle is thus closed, and the reading of it t hus complete.
Writing a ﬁle is accomplished via a similar set of steps. Firs t, a ﬁle
is opened for writing, then the write() system call is called, perhaps
repeatedly for larger ﬁles, and then close(). Use strace to trace writes
to a ﬁle, perhaps of a program you wrote yourself, or by tracin g the dd
utility , e.g.,dd if=foo of=bar .
39.5 Reading And Writing, But Not Sequentially
Thus far, we’ve discussed how to read and write ﬁles, but all a ccess
has been sequential; that is, we have either read a ﬁle from the beginning
to the end, or written a ﬁle out from beginning to end.
Sometimes, however, it is useful to be able to read or write to a spe-
ciﬁc offset within a ﬁle; for example, if you build an index ov er a text
document, and use it to look up a speciﬁc word, you may end up re ading
from some random offsets within the document. To do so, we will use
the lseek() system call. Here is the function prototype:
off_t lseek(int fildes, off_t offset, int whence);
The ﬁrst argument is familiar (a ﬁle descriptor). The second argu-
ment is the offset, which positions the ﬁle offset to a particular location
within the ﬁle. The third argument, called whence for historical reasons,
determines exactly how the seek is performed. From the man pa ge:
If whence is SEEK_SET, the offset is set to offset bytes.
If whence is SEEK_CUR, the offset is set to its current
location plus offset bytes.
If whence is SEEK_END, the offset is set to the size of
the file plus offset bytes.
As you can tell from this description, for each ﬁle a process o pens, the
OS tracks a “current” offset, which determines where the nex t read or
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 483

INTERLUDE : F ILE AND DIRECTORIES 447
ASIDE : CALLING L S E E K() DOES NOT PERFORM A D ISK SEEK
The poorly-named system call lseek() confuses many a student try-
ing to understand disks and how the ﬁle systems atop them work . Do
not confuse the two! The lseek() call simply changes a variable in OS
memory that tracks, for a particular process, at which offse t to which its
next read or write will start. A disk seek occurs when a read or write
issued to the disk is not on the same track as the last read or wr ite, and
thus necessitates a head movement. Making this even more con fusing is
the fact that calling lseek() to read or write from/to random parts of a
ﬁle, and then reading/writing to those random parts, will in deed lead to
more disk seeks. Thus, calling lseek() can certainly lead to a seek in an
upcoming read or write, but absolutely does not cause any dis k I/O to
occur itself.
write will begin reading from or writing to within the ﬁle. Th us, part
of the abstraction of an open ﬁle is that it has a current offse t, which
is updated in one of two ways. The ﬁrst is when a read or write of N
bytes takes place, N is added to the current offset; thus each read or write
implicitly updates the offset. The second is explicitly with lseek, which
changes the offset as speciﬁed above.
Note that this call lseek() has nothing to do with the seek operation
of a disk, which moves the disk arm. The call to lseek() simply changes
the value of a variable within the kernel; when the I/O is perf ormed,
depending on where the disk head is, the disk may or may not per form
an actual seek to fulﬁll the request.
39.6 Writing Immediately with fsync()
Most times when a program calls write(), it is just telling the ﬁle
system: please write this data to persistent storage, at som e point in the
future. The ﬁle system, for performance reasons, will buffer such writes
in memory for some time (say 5 seconds, or 30); at that later po int in
time, the write(s) will actually be issued to the storage dev ice. From the
perspective of the calling application, writes seem to comp lete quickly ,
and only in rare cases (e.g., the machine crashes after the write() call
but before the write to disk) will data be lost.
However, some applications require something more than thi s even-
tual guarantee. For example, in a database management syste m (DBMS),
development of a correct recovery protocol requires the abi lity to force
writes to disk from time to time.
To support these types of applications, most ﬁle systems provide some
additional control APIs. In the U NIX world, the interface provided to ap-
plications is known as fsync(int fd) . When a process calls fsync()
for a particular ﬁle descriptor, the ﬁle system responds by forcing all dirty
(i.e., not yet written) data to disk, for the ﬁle referred to b y the speciﬁed
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 484

448 INTERLUDE : F ILE AND DIRECTORIES
ﬁle descriptor. The fsync() routine returns once all of these writes are
complete.
Here is a simple example of how to use fsync(). The code opens
the ﬁle foo, writes a single chunk of data to it, and then calls fsync()
to ensure the writes are forced immediately to disk. Once the fsync()
returns, the application can safely move on, knowing that th e data has
been persisted (if fsync() is correctly implemented, that is).
int fd = open("foo", O_CREAT | O_WRONLY | O_TRUNC);
assert(fd > -1);
int rc = write(fd, buffer, size);
assert(rc == size);
rc = fsync(fd);
assert(rc == 0);
Interestingly , this sequence does not guarantee everythin g that you
might expect; in some cases, you also need to fsync() the directory that
contains the ﬁle foo. Adding this step ensures not only that the ﬁle itself
is on disk, but that the ﬁle, if newly created, also is durably a part of the
directory . Not surprisingly , this type of detail is often overlooked, leading
to many application-level bugs [P+13].
39.7 Renaming Files
Once we have a ﬁle, it is sometimes useful to be able to give a ﬁl e a
different name. When typing at the command line, this is acco mplished
with mv command; in this example, the ﬁle foo is renamed bar:
prompt> mv foo bar
Using strace, we can see that mv uses the system call rename(char
*old, char *new), which takes precisely two arguments: the original
name of the ﬁle ( old) and the new name ( new).
One interesting guarantee provided by the rename() call is that it is
(usually) implemented as an atomic call with respect to system crashes;
if the system crashes during the renaming, the ﬁle will eithe r be named
the old name or the new name, and no odd in-between state can ar ise.
Thus, rename() is critical for supporting certain kinds of applications
that require an atomic update to ﬁle state.
Let’s be a little more speciﬁc here. Imagine that you are usin g a ﬁle ed-
itor (e.g., emacs), and you insert a line into the middle of a ﬁ le. The ﬁle’s
name, for the example, is foo.txt. The way the editor might update the
ﬁle to guarantee that the new ﬁle has the original contents pl us the line
inserted is as follows (ignoring error-checking for simpli city):
int fd = open("foo.txt.tmp", O_WRONLY|O_CREAT|O_TRUNC);
write(fd, buffer, size); // write out new version of file
fsync(fd);
close(fd);
rename("foo.txt.tmp", "foo.txt");
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 485

INTERLUDE : F ILE AND DIRECTORIES 449
What the editor does in this example is simple: write out the n ew
version of the ﬁle under temporary name ( foot.txt.tmp), force it to
disk with fsync(), and then, when the application is certain the new
ﬁle metadata and contents are on the disk, rename the tempora ry ﬁle to
the original ﬁle’s name. This last step atomically swaps the new ﬁle into
place, while concurrently deleting the old version of the ﬁl e, and thus an
atomic ﬁle update is achieved.
39.8 Getting Information About Files
Beyond ﬁle access, we expect the ﬁle system to keep a fair amou nt of
information about each ﬁle it is storing. We generally call s uch data about
ﬁles metadata. To see the metadata for a certain ﬁle, we can use stat()
or fstat() system call – read their man pages for details on how to call
them. These calls take a pathname (or ﬁle descriptor) to a ﬁle and ﬁll in a
stat structure as seen here:
struct stat {
dev_t st_dev; / * ID of device containing file */
ino_t st_ino; / * inode number */
mode_t st_mode; / * protection */
nlink_t st_nlink; / * number of hard links */
uid_t st_uid; / * user ID of owner */
gid_t st_gid; / * group ID of owner */
dev_t st_rdev; / * device ID (if special file) */
off_t st_size; / * total size, in bytes */
blksize_t st_blksize; / * blocksize for filesystem I/O */
blkcnt_t st_blocks; / * number of blocks allocated */
time_t st_atime; / * time of last access */
time_t st_mtime; / * time of last modification */
time_t st_ctime; / * time of last status change */
};
You can see that there is a lot of information kept about each ﬁ le, in-
cluding its size (in bytes), its low-level name (i.e., inode number), some
ownership information, and some information about when the ﬁle was
accessed or modiﬁed, among other things. To see this informa tion, you
can use the command line tool stat:
prompt> echo hello > file
prompt> stat file
File: ‘file’
Size: 6 Blocks: 8 IO Block: 4096 regular file
Device: 811h/2065d Inode: 67158084 Links: 1
Access: (0640/-rw-r-----) Uid: (30686/ remzi) Gid: (30686 / remzi)
Access: 2011-05-03 15:50:20.157594748 -0500
Modify: 2011-05-03 15:50:20.157594748 -0500
Change: 2011-05-03 15:50:20.157594748 -0500
As it turns out, each ﬁle system usually keeps this type of inf ormation
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 486

450 INTERLUDE : F ILE AND DIRECTORIES
in a structure called an inode1. We’ll be learning a lot more about inodes
when we talk about ﬁle system implementation. For now , you should just
think of an inode as a persistent data structure kept by the ﬁl e system that
has information like we see above inside of it.
39.9 Removing Files
At this point, we know how to create ﬁles and access them, eith er se-
quentially or not. But how do you delete ﬁles? If you’ve used U NIX , you
probably think you know: just run the program rm. But what system call
does rm use to remove a ﬁle?
Let’s use our old friend strace again to ﬁnd out. Here we remove
that pesky ﬁle “foo”:
prompt> strace rm foo
...
unlink("foo") = 0
...
We’ve removed a bunch of unrelated cruft from the traced outp ut,
leaving just a single call to the mysteriously-named system call unlink().
As you can see, unlink() just takes the name of the ﬁle to be removed,
and returns zero upon success. But this leads us to a great puz zle: why
is this system call named “unlink”? Why not just “remove” or “ delete”.
To understand the answer to this puzzle, we must ﬁrst underst and more
than just ﬁles, but also directories.
39.10 Making Directories
Beyond ﬁles, a set of directory-related system calls enable you to make,
read, and delete directories. Note you can never write to a di rectory di-
rectly; because the format of the directory is considered ﬁl e system meta-
data, you can only update a directory indirectly by , for exam ple, creating
ﬁles, directories, or other object types within it. In this way , the ﬁle system
makes sure that the contents of the directory always are as ex pected.
To create a directory , a single system call, mkdir(), is available. The
eponymous mkdir program can be used to create such a directory . Let’s
take a look at what happens when we run the mkdir program to make a
simple directory called foo:
prompt> strace mkdir foo
...
mkdir("foo", 0777) = 0
...
prompt>
1Some ﬁle systems call these structures similar, but slightl y different, names, such as
dnodes; the basic idea is similar however.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 487

INTERLUDE : F ILE AND DIRECTORIES 451
TIP : B E WARY OF POWERFUL COMMANDS
The program rm provides us with a great example of powerful com-
mands, and how sometimes too much power can be a bad thing. For
example, to remove a bunch of ﬁles at once, you can type someth ing like:
prompt> rm *
where the * will match all ﬁles in the current directory . But sometimes
you want to also delete the directories too, and in fact all of their contents.
You can do this by telling rm to recursively descend into each directory ,
and remove its contents too:
prompt> rm -rf *
Where you get into trouble with this small string of characte rs is when
you issue the command, accidentally , from the root directory of a ﬁle sys-
tem, thus removing every ﬁle and directory from it. Oops!
Thus, remember the double-edged sword of powerful commands ; while
they give you the ability to do a lot of work with a small number of
keystrokes, they also can quickly and readily do a great deal of harm.
When such a directory is created, it is considered “empty”, a lthough it
does have a bare minimum of contents. Speciﬁcally , an empty d irectory
has two entries: one entry that refers to itself, and one entr y that refers
to its parent. The former is referred to as the “.” (dot) direc tory , and the
latter as “..” (dot-dot). You can see these directories by pa ssing a ﬂag (-a)
to the program ls:
prompt> ls -a
./ ../
prompt> ls -al
total 8
drwxr-x--- 2 remzi remzi 6 Apr 30 16:17 ./
drwxr-x--- 26 remzi remzi 4096 Apr 30 16:17 ../
39.11 Reading Directories
Now that we’ve created a directory , we might wish to read one t oo.
Indeed, that is exactly what the program ls does. Let’s write our own
little tool like ls and see how it is done.
Instead of just opening a directory as if it were a ﬁle, we inst ead use
a new set of calls. Below is an example program that prints the contents
of a directory . The program uses three calls, opendir(), readdir(),
and closedir(), to get the job done, and you can see how simple the
interface is; we just use a simple loop to read one directory entry at a time,
and print out the name and inode number of each ﬁle in the direc tory .
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 488

452 INTERLUDE : F ILE AND DIRECTORIES
int main(int argc, char *argv[]) {
DIR *dp = opendir(".");
assert(dp != NULL);
struct dirent *d;
while ((d = readdir(dp)) != NULL) {
printf("%d %s\n", (int) d->d_ino, d->d_name);
}
closedir(dp);
return 0;
}
The declaration below shows the information available with in each
directory entry in the struct dirent data structure:
struct dirent {
char d_name[256]; / * filename */
ino_t d_ino; / * inode number */
off_t d_off; / * offset to the next dirent */
unsigned short d_reclen; / * length of this record */
unsigned char d_type; / * type of file */
};
Because directories are light on information (basically , j ust mapping
the name to the inode number, along with a few other details), a program
may want to call stat() on each ﬁle to get more information on each,
such as its length or other detailed information. Indeed, th is is exactly
what ls does when you pass it the -l ﬂag; try strace on ls with and
without that ﬂag to see for yourself.
39.12 Deleting Directories
Finally , you can delete a directory with a call to rmdir() (which is
used by the program of the same name, rmdir). Unlike ﬁle deletion,
however, removing directories is more dangerous, as you cou ld poten-
tially delete a large amount of data with a single command. Thus, rmdir()
has the requirement that the directory be empty (i.e., only h as “.” and “..”
entries) before it is deleted. If you try to delete a non-empt y directory , the
call to rmdir() simply will fail.
39.13 Hard Links
We now come back to the mystery of why removing a ﬁle is performed
via unlink(), by understanding a new way to make an entry in the
ﬁle system tree, through a system call known as link(). The link()
system call takes two arguments, an old pathname and a new one ; when
you “link” a new ﬁle name to an old one, you essentially create another
way to refer to the same ﬁle. The command-line program ln is used to
do this, as we see in this example:
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 489

INTERLUDE : F ILE AND DIRECTORIES 453
prompt> echo hello > file
prompt> cat file
hello
prompt> ln file file2
prompt> cat file2
hello
Here we created a ﬁle with the word “hello” in it, and called th e ﬁle
file2. We then create a hard link to that ﬁle using the ln program. After
this, we can examine the ﬁle by either opening file or file2.
The way link works is that it simply creates another name in the di-
rectory you are creating the link to, and refers it to the same inode number
(i.e., low-level name) of the original ﬁle. The ﬁle is not cop ied in any way;
rather, you now just have two human names (file and file2) that both
refer to the same ﬁle. We can even see this in the directory its elf, by print-
ing out the inode number of each ﬁle:
prompt> ls -i file file2
67158084 file
67158084 file2
prompt>
By passing the -i ﬂag to ls, it prints out the inode number of each ﬁle
(as well as the ﬁle name). And thus you can see what link really has done:
just make a new reference to the same exact inode number (6715 8084 in
this example).
By now you might be starting to see why unlink() is called unlink().
When you create a ﬁle, you are really doing two things. First, you are
making a structure (the inode) that will track virtually all relevant infor-
mation about the ﬁle, including its size, where its blocks ar e on disk, and
so forth. Second, you are linking a human-readable name to that ﬁle, and
putting that link into a directory .
After creating a hard link to a ﬁle, to the ﬁle system, there is no dif-
ference between the original ﬁle name ( file) and the newly created ﬁle
name ( file2); indeed, they are both just links to the underlying meta-
data about the ﬁle, which is found in inode number 67158084.
Thus, to remove a ﬁle from the ﬁle system, we call unlink(). In the
example above, we could for example remove the ﬁle named file, and
still access the ﬁle without difﬁculty:
prompt> rm file
removed ‘file’
prompt> cat file2
hello
The reason this works is because when the ﬁle system unlinks ﬁ le, it
checks a reference count within the inode number. This reference count
2Note how creative the authors of this book are. We also used to have a cat named “Cat”
(true story). However, she died, and we now have a hamster nam ed “Hammy .”
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 490

454 INTERLUDE : F ILE AND DIRECTORIES
(sometimes called the link count ) allows the ﬁle system to track how
many different ﬁle names have been linked to this particular inode. When
unlink() is called, it removes the “link” between the human-readable
name (the ﬁle that is being deleted) to the given inode number, and decre-
ments the reference count; only when the reference count rea ches zero
does the ﬁle system also free the inode and related data block s, and thus
truly “delete” the ﬁle.
You can see the reference count of a ﬁle using stat() of course. Let’s
see what it is when we create and delete hard links to a ﬁle. In t his exam-
ple, we’ll create three links to the same ﬁle, and then delete them. Watch
the link count!
prompt> echo hello > file
prompt> stat file
... Inode: 67158084 Links: 1 ...
prompt> ln file file2
prompt> stat file
... Inode: 67158084 Links: 2 ...
prompt> stat file2
... Inode: 67158084 Links: 2 ...
prompt> ln file2 file3
prompt> stat file
... Inode: 67158084 Links: 3 ...
prompt> rm file
prompt> stat file2
... Inode: 67158084 Links: 2 ...
prompt> rm file2
prompt> stat file3
... Inode: 67158084 Links: 1 ...
prompt> rm file3
39.14 Symbolic Links
There is one other type of link that is really useful, and it is called a
symbolic link or sometimes a soft link . As it turns out, hard links are
somewhat limited: you can’t create one to a directory (for fe ar that you
will create a cycle in the directory tree); you can’t hard lin k to ﬁles in
other disk partitions (because inode numbers are only uniqu e within a
particular ﬁle system, not across ﬁle systems); etc. Thus, a new type of
link called the symbolic link was created.
To create such a link, you can use the same program ln, but with the
-s ﬂag. Here is an example:
prompt> echo hello > file
prompt> ln -s file file2
prompt> cat file2
hello
As you can see, creating a soft link looks much the same, and th e orig-
inal ﬁle can now be accessed through the ﬁle name file as well as the
symbolic link name file2.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 491

INTERLUDE : F ILE AND DIRECTORIES 455
However, beyond this surface similarity , symbolic links ar e actually
quite different from hard links. The ﬁrst difference is that a symbolic
link is actually a ﬁle itself, of a different type. We’ve alre ady talked about
regular ﬁles and directories; symbolic links are a third type the ﬁle system
knows about. A stat on the symlink reveals all:
prompt> stat file
... regular file ...
prompt> stat file2
... symbolic link ...
Running ls also reveals this fact. If you look closely at the ﬁrst char-
acter of the long-form of the output from ls, you can see that the ﬁrst
character in the left-most column is a - for regular ﬁles, a d for directo-
ries, and an l for soft links. You can also see the size of the symbolic link
(4 bytes in this case), as well as what the link points to (the ﬁ le named
file).
prompt> ls -al
drwxr-x--- 2 remzi remzi 29 May 3 19:10 ./
drwxr-x--- 27 remzi remzi 4096 May 3 15:14 ../
-rw-r----- 1 remzi remzi 6 May 3 19:10 file
lrwxrwxrwx 1 remzi remzi 4 May 3 19:10 file2 -> file
The reason that file2 is 4 bytes is because the way a symbolic link is
formed is by holding the pathname of the linked-to ﬁle as the d ata of the
link ﬁle. Because we’ve linked to a ﬁle named file, our link ﬁle file2
is small (4 bytes). If we link to a longer pathname, our link ﬁl e would be
bigger:
prompt> echo hello > alongerfilename
prompt> ln -s alongerfilename file3
prompt> ls -al alongerfilename file3
-rw-r----- 1 remzi remzi 6 May 3 19:17 alongerfilename
lrwxrwxrwx 1 remzi remzi 15 May 3 19:17 file3 -> alongerfilen ame
Finally , because of the way symbolic links are created, they leave the
possibility for what is known as a dangling reference:
prompt> echo hello > file
prompt> ln -s file file2
prompt> cat file2
hello
prompt> rm file
prompt> cat file2
cat: file2: No such file or directory
As you can see in this example, quite unlike hard links, remov ing the
original ﬁle named file causes the link to point to a pathname that no
longer exists.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 492

456 INTERLUDE : F ILE AND DIRECTORIES
39.15 Making and Mounting a File System
We’ve now toured the basic interfaces to access ﬁles, direct ories, and
certain types of special types of links. But there is one more topic we
should discuss: how to assemble a full directory tree from ma ny under-
lying ﬁle systems. This task is accomplished via ﬁrst making ﬁle systems,
and then mounting them to make their contents accessible.
To make a ﬁle system, most ﬁle systems provide a tool, usually re-
ferred to as mkfs (pronounced “make fs”), that performs exactly this task.
The idea is as follows: give the tool, as input, a device (such as a disk
partition, e.g., /dev/sda1) a ﬁle system type (e.g., ext3), and it simply
writes an empty ﬁle system, starting with a root directory , o nto that disk
partition. And mkfs said, let there be a ﬁle system!
However, once such a ﬁle system is created, it needs to be made ac-
cessible within the uniform ﬁle-system tree. This task is ac hieved via the
mount program (which makes the underlying system call mount() to do
the real work). What mount does, quite simply is take an exist ing direc-
tory as a target mount point and essentially paste a new ﬁle system onto
the directory tree at that point.
An example here might be useful. Imagine we have an unmounted
ext3 ﬁle system, stored in device partition /dev/sda1, that has the fol-
lowing contents: a root directory which contains two sub-di rectories, a
and b, each of which in turn holds a single ﬁle named foo. Let’s say we
wish to mount this ﬁle system at the mount point /home/users. We
would type something like this:
prompt> mount -t ext3 /dev/sda1 /home/users
If successful, the mount would thus make this new ﬁle system a vail-
able. However, note how the new ﬁle system is now accessed. To look at
the contents of the root directory , we would use ls like this:
prompt> ls /home/users/
a b
As you can see, the pathname /home/users/ now refers to the root
of the newly-mounted directory . Similarly , we could access ﬁles a and
b with the pathnames /home/users/a and /home/users/b. Finally ,
the ﬁles named foo could be accessed via /home/users/a/foo and
/home/users/b/foo. And thus the beauty of mount: instead of having
a number of separate ﬁle systems, mount uniﬁes all ﬁle system s into one
tree, making naming uniform and convenient.
To see what is mounted on your system, and at which points, sim ply
run the mount program. You’ll see something like this:
/dev/sda1 on / type ext3 (rw)
proc on /proc type proc (rw)
sysfs on /sys type sysfs (rw)
/dev/sda5 on /tmp type ext3 (rw)
/dev/sda7 on /var/vice/cache type ext3 (rw)
tmpfs on /dev/shm type tmpfs (rw)
AFS on /afs type afs (rw)
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 493

INTERLUDE : F ILE AND DIRECTORIES 457
This crazy mix shows that a whole number of different ﬁle syst ems,
including ext3 (a standard disk-based ﬁle system), the proc ﬁle system (a
ﬁle system for accessing information about current process es), tmpfs (a
ﬁle system just for temporary ﬁles), and AFS (a distributed ﬁ le system)
are all glued together onto this one machine’s ﬁle-system tr ee.
39.16 Summary
The ﬁle system interface in U NIX systems (and indeed, in any system)
is seemingly quite rudimentary , but there is a lot to underst and if you
wish to master it. Nothing is better, of course, than simply u sing it (a lot).
So please do so! Of course, read more; as always, Stevens [SR0 5] is the
place to begin.
We’ve toured the basic interfaces, and hopefully understoo d a little bit
about how they work. Even more interesting is how to implemen t a ﬁle
system that meets the needs of the API, a topic we will delve in to in great
detail next.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 494

458 INTERLUDE : F ILE AND DIRECTORIES
References
[K84] “Processes as Files”
Tom J. Killian
USENIX, June 1984
The paper that introduced the /proc ﬁle system, where each pr ocess can be treated as a ﬁle within a
pseudo ﬁle system. A clever idea that you can still see in mode rn UNIX systems.
[L84] “Capability-Based Computer Systems”
Henry M. Levy
Digital Press, 1984
Available: http://homes.cs.washington.edu/ levy/capabook
An excellent overview of early capability-based systems.
[P+13] “Towards Efﬁcient, Portable Application-Level Con sistency”
Thanumalayan S. Pillai, Vijay Chidambaram, Joo-Young Hwan g, Andrea C. Arpaci-Dusseau,
and Remzi H. Arpaci-Dusseau
HotDep ’13, November 2013
Our own work that shows how readily applications can make mis takes in committing data to disk; in
particular, assumptions about the ﬁle system creep into app lications and thus make the applications
work correctly only if they are running on a speciﬁc ﬁle syste m.
[SK09] “Principles of Computer System Design”
Jerome H. Saltzer and M. Frans Kaashoek
Morgan-Kaufmann, 2009
This tour de force of systems is a must-read for anybody inter ested in the ﬁeld. It’s how they teach
systems at MIT. Read it once, and then read it a few more times t o let it all soak in.
[SR05] “Advanced Programming in the U NIX Environment”
W. Richard Stevens and Stephen A. Rago
Addison-Wesley , 2005
We have probably referenced this book a few hundred thousand times. It is that useful to you, if you care
to become an awesome systems programmer.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 495

INTERLUDE : F ILE AND DIRECTORIES 459
Homework
In this homework, we’ll just familiarize ourselves with how the APIs
described in the chapter work. To do so, you’ll just write a fe w different
programs, mostly based on various U NIX utilities.
Questions
1. Stat: Write your own version of the command line program stat,
which simply calls the stat() system call on a given ﬁle or di-
rectory . Print out ﬁle size, number of blocks allocated, ref erence
(link) count, and so forth. What is the link count of a directo ry , as
the number of entries in the directory changes? Useful inter faces:
stat()
2. List Files: Write a program that lists ﬁles in the given directory .
When called without any arguments, the program should just p rint
the ﬁle names. When invoked with the -l ﬂag, the program should
print out information about each ﬁle, such as the owner, group, per-
missions, and other information obtained from the stat() system
call. The program should take one additional argument, whic h is
the directory to read, e.g., myls -l directory . If no directory is
given, the program should just use the current working direc tory .
Useful interfaces: stat(), opendir(), readdir(), getcwd().
3. T ail:Write a program that prints out the last few lines of a ﬁle. The
program should be efﬁcient, in that it seeks to near the end of the
ﬁle, reads in a block of data, and then goes backwards until it ﬁnds
the requested number of lines; at this point, it should print out those
lines from beginning to the end of the ﬁle. To invoke the progr am,
one should type: mytail -n file , where n is the number of lines
at the end of the ﬁle to print. Useful interfaces: stat(), lseek(),
open(), read(), close().
4. Recursive Search: Write a program that prints out the names of
each ﬁle and directory in the ﬁle system tree, starting at a gi ven
point in the tree. For example, when run without arguments, t he
program should start with the current working directory and print
its contents, as well as the contents of any sub-directories , etc., until
the entire tree, root at the CWD, is printed. If given a single argu-
ment (of a directory name), use that as the root of the tree ins tead.
Reﬁne your recursive search with more fun options, similar t o the
powerful find command line tool. Useful interfaces: you ﬁgure it
out.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 497

40
File System Implementation
In this chapter, we introduce a simple ﬁle system implementation, known
as vsfs (the V ery Simple File System ). This ﬁle system is a simpliﬁed
version of a typical U NIX ﬁle system and thus serves to introduce some
of the basic on-disk structures, access methods, and variou s policies that
you will ﬁnd in many ﬁle systems today .
The ﬁle system is pure software; unlike our development of CP U and
memory virtualization, we will not be adding hardware featu res to make
some aspect of the ﬁle system work better (though we will want to pay at-
tention to device characteristics to make sure the ﬁle syste m works well).
Because of the great ﬂexibility we have in building a ﬁle syst em, many
different ones have been built, literally from AFS (the Andr ew File Sys-
tem) [H+88] to ZFS (Sun’s Zettabyte File System) [B07]. All o f these ﬁle
systems have different data structures and do some things better or worse
than their peers. Thus, the way we will be learning about ﬁle s ystems is
through case studies: ﬁrst, a simple ﬁle system (vsfs) in thi s chapter to
introduce most concepts, and then a series of studies of real ﬁle systems
to understand how they can differ in practice.
THE CRUX : H OW TO IMPLEMENT A S IMPLE FILE SYSTEM
How can we build a simple ﬁle system? What structures are need ed
on the disk? What do they need to track? How are they accessed?
40.1 The Way To Think
To think about ﬁle systems, we usually suggest thinking abou t two
different aspects of them; if you understand both of these as pects, you
probably understand how the ﬁle system basically works.
The ﬁrst is the data structures of the ﬁle system. In other words, what
types of on-disk structures are utilized by the ﬁle system to organize its
data and metadata? The ﬁrst ﬁle systems we’ll see (including vsfs below)
employ simple structures, like arrays of blocks or other obj ects, whereas
461

## Page 498

462 FILE SYSTEM IMPLEMENTATION
ASIDE : MENTAL MODELS OF FILE SYSTEMS
As we’ve discussed before, mental models are what you are rea lly trying
to develop when learning about systems. For ﬁle systems, you r mental
model should eventually include answers to questions like: what on-disk
structures store the ﬁle system’s data and metadata? What ha ppens when
a process opens a ﬁle? Which on-disk structures are accessed during a
read or write? By working on and improving your mental model, you
develop an abstract understanding of what is going on, inste ad of just
trying to understand the speciﬁcs of some ﬁle-system code (t hough that
is also useful, of course!).
more sophisticated ﬁle systems, like SGI’s XFS, use more com plicated
tree-based structures [S+96].
The second aspect of a ﬁle system is its access methods . How does
it map the calls made by a process, such as open(), read(), write(),
etc., onto its structures? Which structures are read during the execution
of a particular system call? Which are written? How efﬁcient ly are all of
these steps performed?
If you understand the data structures and access methods of a ﬁle sys-
tem, you have developed a good mental model of how it truly wor ks, a
key part of the systems mindset. Try to work on developing you r mental
model as we delve into our ﬁrst implementation.
40.2 Overall Organization
We now develop the overall on-disk organization of the data s truc-
tures of the vsfs ﬁle system. The ﬁrst thing we’ll need to do is divide the
disk into blocks; simple ﬁle systems use just one block size, and that’s
exactly what we’ll do here. Let’s choose a commonly-used siz e of 4 KB.
Thus, our view of the disk partition where we’re building our ﬁle sys-
tem is simple: a series of blocks, each of size 4 KB. The blocks are ad-
dressed from 0 to N − 1, in a partition of size N 4-KB blocks. Assume we
have a really small disk, with just 64 blocks:
0 7 8 15 16 23 24 31
32 39 40 47 48 55 56 63
Let’s now think about what we need to store in these blocks to b uild
a ﬁle system. Of course, the ﬁrst thing that comes to mind is us er data.
In fact, most of the space in any ﬁle system is (and should be) u ser data.
Let’s call the region of the disk we use for user data the data region, and,
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 499

FILE SYSTEM IMPLEMENTATION 463
again for simplicity , reserve a ﬁxed portion of the disk for t hese blocks,
say the last 56 of 64 blocks on the disk:
0 7
D
8
D D D D D D D
15
D
16
D D D D D D D
23
D
24
D D D D D D D
31
D
32
D D D D D D D
39
D
40
D D D D D D D
47
D
48
D D D D D D D
55
D
56
D D D D D D D
63
Data Region
Data Region
As we learned about (a little) last chapter, the ﬁle system ha s to track
information about each ﬁle. This information is a key piece o f metadata,
and tracks things like which data blocks (in the data region) comprise
a ﬁle, the size of the ﬁle, its owner and access rights, access and mod-
ify times, and other similar kinds of information. To store t his informa-
tion, ﬁle system usually have a structure called an inode (we’ll read more
about inodes below).
To accommodate inodes, we’ll need to reserve some space on th e disk
for them as well. Let’s call this portion of the disk the inode table, which
simply holds an array of on-disk inodes. Thus, our on-disk im age now
looks like this picture, assuming that we use 5 of our 64 block s for inodes
(denoted by I’s in the diagram):
0
I I I I I
7
D
8
D D D D D D D
15
D
16
D D D D D D D
23
D
24
D D D D D D D
31
D
32
D D D D D D D
39
D
40
D D D D D D D
47
D
48
D D D D D D D
55
D
56
D D D D D D D
63
Data Region
Data Region
Inodes
We should note here that inodes are typically not that big, fo r example
128 or 256 bytes. Assuming 256 bytes per inode, a 4-KB block ca n hold 16
inodes, and our ﬁle system above contains 80 total inodes. In our simple
ﬁle system, built on a tiny 64-block partition, this number r epresents the
maximum number of ﬁles we can have in our ﬁle system; however, do
note that the same ﬁle system, built on a larger disk, could simply allocate
a larger inode table and thus accommodate more ﬁles.
Our ﬁle system thus far has data blocks (D), and inodes (I), bu t a few
things are still missing. One primary component that is stil l needed, as
you might have guessed, is some way to track whether inodes or data
blocks are free or allocated. Such allocation structures are thus a requisite
element in any ﬁle system.
Many allocation-tracking methods are possible, of course. For exam-
ple, we could use a free list that points to the ﬁrst free block, which then
points to the next free block, and so forth. We instead choose a simple and
popular structure known as a bitmap, one for the data region (the data
bitmap), and one for the inode table (the inode bitmap ). A bitmap is a
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 500

464 FILE SYSTEM IMPLEMENTATION
simple structure: each bit is used to indicate whether the co rresponding
object/block is free (0) or in-use (1). And thus our new on-di sk layout,
with an inode bitmap (i) and a data bitmap (d):
0
i d I I I I I
7
D
8
D D D D D D D
15
D
16
D D D D D D D
23
D
24
D D D D D D D
31
D
32
D D D D D D D
39
D
40
D D D D D D D
47
D
48
D D D D D D D
55
D
56
D D D D D D D
63
Data Region
Data Region
Inodes
You may notice that it is a bit of overkill to use an entire 4-KB block for
these bitmaps; such a bitmap can track whether 32K objects ar e allocated,
and yet we only have 80 inodes and 56 data blocks. However, we j ust use
an entire 4-KB block for each of these bitmaps for simplicity .
The careful reader (i.e., the reader who is still awake) may h ave no-
ticed there is one block left in the design of the on-disk stru cture of our
very simple ﬁle system. We reserve this for the superblock, denoted by
an S in the diagram below . The superblock contains informati on about
this particular ﬁle system, including, for example, how man y inodes and
data blocks are in the ﬁle system (80 and 56, respectively in t his instance),
where the inode table begins (block 3), and so forth. It will l ikely also
include a magic number of some kind to identify the ﬁle system type (in
this case, vsfs).
S
0
i d I I I I I
7
D
8
D D D D D D D
15
D
16
D D D D D D D
23
D
24
D D D D D D D
31
D
32
D D D D D D D
39
D
40
D D D D D D D
47
D
48
D D D D D D D
55
D
56
D D D D D D D
63
Data Region
Data Region
Inodes
Thus, when mounting a ﬁle system, the operating system will r ead
the superblock ﬁrst, to initialize various parameters, and then attach the
volume to the ﬁle-system tree. When ﬁles within the volume are accessed,
the system will thus know exactly where to look for the needed on-disk
structures.
40.3 File Organization: The Inode
One of the most important on-disk structures of a ﬁle system i s the
inode; virtually all ﬁle systems have a structure similar to this. The name
inode is short for index node, the historical name given to it by U NIX in-
ventor Ken Thompson [RT74], used because these nodes were or iginally
arranged in an array , and the array indexed into when accessing a partic-
ular inode.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 501

FILE SYSTEM IMPLEMENTATION 465
ASIDE : DATA STRUCTURE – T HE INODE
The inode is the generic name that is used in many ﬁle systems to de-
scribe the structure that holds the metadata for a given ﬁle, such as its
length, permissions, and the location of its constituent bl ocks. The name
goes back at least as far as U NIX (and probably further back to Multics
if not earlier systems); it is short for index node , as the inode number is
used to index into an array of on-disk inodes in order to ﬁnd th e inode
of that number. As we’ll see, design of the inode is one key par t of ﬁle
system design. Most modern systems have some kind of structu re like
this for every ﬁle they track, but perhaps call them differen t things (such
as dnodes, fnodes, etc.).
Each inode is implicitly referred to by a number (called the inumber),
which we’ve earlier called the low-level name of the ﬁle. In vsfs (and
other simple ﬁle systems), given an i-number, you should dir ectly be able
to calculate where on the disk the corresponding inode is loc ated. For ex-
ample, take the inode table of vsfs as above: 20-KB in size (5 4 -KB blocks)
and thus consisting of 80 inodes (assuming each inode is 256 b ytes); fur-
ther assume that the inode region starts at 12KB (i.e, the sup erblock starts
at 0KB, the inode bitmap is at address 4KB, the data bitmap at 8 KB, and
thus the inode table comes right after). In vsfs, we thus have the following
layout for the beginning of the ﬁle system partition (in clos eup view):
Super i-bmap d-bmap
0KB 4KB 8KB 12KB 16KB 20KB 24KB 28KB 32KB
The Inode Table (Closeup)
0 1 2 3
4 5 6 7
8 9 10 11
12 13 14 15
16 17 18 19
20 21 22 23
24 25 26 27
28 29 30 31
32 33 34 35
36 37 38 39
40 41 42 43
44 45 46 47
48 49 50 51
52 53 54 55
56 57 58 59
60 61 62 63
64 65 66 67
68 69 70 71
72 73 74 75
76 77 78 79
iblock 0 iblock 1 iblock 2 iblock 3 iblock 4
To read inode number 32, the ﬁle system would ﬁrst calculate the offset
into the inode region (32·sizeof (inode) or 8192, add it to the start address
of the inode table on disk ( inodeStartAddr = 12KB ), and thus arrive
upon the correct byte address of the desired block of inodes: 20KB . Re-
call that disks are not byte addressable, but rather consist of a large num-
ber of addressable sectors, usually 512 bytes. Thus, to fetc h the block of
inodes that contains inode 32, the ﬁle system would issue a re ad to sector
20× 1024
512 , or 40, to fetch the desired inode block. More generally , the sector
address iaddr of the inode block can be calculated as follows:
blk = (inumber * sizeof(inode_t)) / blockSize;
sector = ((blk * blockSize) + inodeStartAddr) / sectorSize;
Inside each inode is virtually all of the information you nee d about a
ﬁle: its type (e.g., regular ﬁle, directory , etc.), its size, the number of blocks
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 502

466 FILE SYSTEM IMPLEMENTATION
Size Name What is this inode ﬁeld for?
2 mode can this ﬁle be read/written/executed?
2 uid who owns this ﬁle?
4 size how many bytes are in this ﬁle?
4 time what time was this ﬁle last accessed?
4 ctime what time was this ﬁle created?
4 mtime what time was this ﬁle last modiﬁed?
4 dtime what time was this inode deleted?
2 gid which group does this ﬁle belong to?
2 links
count how many hard links are there to this ﬁle?
4 blocks how many blocks have been allocated to this ﬁle?
4 ﬂags how should ext2 use this inode?
4 osd1 an OS-dependent ﬁeld
60 block a set of disk pointers (15 total)
4 generation ﬁle version (used by NFS)
4 ﬁle
acl a new permissions model beyond mode bits
4 dir acl called access control lists
4 faddr an unsupported ﬁeld
12 i osd2 another OS-dependent ﬁeld
Table 40.1: The ext2 inode
allocated to it, protection information (such as who owns the ﬁle, as well
as who can access it), some time information, including when the ﬁle was
created, modiﬁed, or last accessed, as well as information a bout where its
data blocks reside on disk (e.g., pointers of some kind). We r efer to all
such information about a ﬁle as metadata; in fact, any information inside
the ﬁle system that isn’t pure user data is often referred to a s such. An
example inode from ext2 [P09] is shown below in Table 40.1.
One of the most important decisions in the design of the inode is how
it refers to where data blocks are. One simple approach would be to
have one or more direct pointers (disk addresses) inside the inode; each
pointer refers to one disk block that belongs to the ﬁle. Such an approach
is limited: for example, if you want to have a ﬁle that is reall y big (e.g.,
bigger than the size of a block multiplied by the number of dir ect point-
ers), you are out of luck.
The Multi-Level Index
To support bigger ﬁles, ﬁle system designers have had to intr oduce dif-
ferent structures within inodes. One common idea is to have a special
pointer known as an indirect pointer. Instead of pointing to a block that
contains user data, it points to a block that contains more po inters, each
of which point to user data. Thus, an inode may have some ﬁxed n umber
of direct pointers (e.g., 12), and a single indirect pointer . If a ﬁle grows
large enough, an indirect block is allocated (from the data- block region
of the disk), and the inode’s slot for an indirect pointer is s et to point to
it. Assuming that a block is 4KB and 4-byte disk addresses, th at adds
another 1024 pointers; the ﬁle can grow to be (12 + 1024) · 4K or 4144KB.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 503

FILE SYSTEM IMPLEMENTATION 467
TIP : C ONSIDER EXTENT -BASED APPROACHES
A different approach is to use extents instead of pointers. An extent is
simply a disk pointer plus a length (in blocks); thus, instea d of requiring
a pointer for every block of a ﬁle, all one needs is a pointer an d a length
to specify the on-disk location of a ﬁle. Just a single extent is limiting, as
one may have trouble ﬁnding a contiguous chunk of on-disk fre e space
when allocating a ﬁle. Thus, extent-based ﬁle systems often allow for
more than one extent, thus giving more freedom to the ﬁle syst em during
ﬁle allocation.
In comparing the two approaches, pointer-based approaches are the most
ﬂexible but use a large amount of metadata per ﬁle (particula rly for large
ﬁles). Extent-based approaches are less ﬂexible but more co mpact; in par-
ticular, they work well when there is enough free space on the disk and
ﬁles can be laid out contiguously (which is the goal for virtu ally any ﬁle
allocation policy anyhow).
Not surprisingly , in such an approach, you might want to supp ort
even larger ﬁles. To do so, just add another pointer to the ino de: the dou-
ble indirect pointer . This pointer refers to a block that contains pointers
to indirect blocks, each of which contain pointers to data bl ocks. A dou-
ble indirect block thus adds the possibility to grow ﬁles with an additional
1024 · 1024 or 1-million 4KB blocks, in other words supporting ﬁles that
are over 4GB in size. You may want even more, though, and we bet you
know where this is headed: the triple indirect pointer .
Overall, this imbalanced tree is referred to as the multi-level index ap-
proach to pointing to ﬁle blocks. Let’s examine an example wi th twelve
direct pointers, as well as both a single and a double indirec t block. As-
suming a block size of 4 KB, and 4-byte pointers, this structure can accom-
modate a ﬁle of just over 4 GB in size (i.e., (12 + 1024 + 1024 2) × 4 KB ).
Can you ﬁgure out how big of a ﬁle can be handled with the additi on of
a triple-indirect block? (hint: pretty big)
Many ﬁle systems use a multi-level index, including commonl y-used
ﬁle systems such as Linux ext2 [P09] and ext3, NetApp’s WAFL, as well as
the original U NIX ﬁle system. Other ﬁle systems, including SGI XFS and
Linux ext4, use extents instead of simple pointers; see the earlier aside for
details on how extent-based schemes work (they are akin to se gments in
the discussion of virtual memory).
You might be wondering: why use an imbalanced tree like this? Why
not a different approach? Well, as it turns out, many researc hers have
studied ﬁle systems and how they are used, and virtually ever y time they
ﬁnd certain “truths” that hold across the decades. One such ﬁ nding is
that most ﬁles are small . This imbalanced design reﬂects such a reality; if
most ﬁles are indeed small, it makes sense to optimize for thi s case. Thus,
with a small number of direct pointers (12 is a typical number ), an inode
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 504

468 FILE SYSTEM IMPLEMENTATION
ASIDE : LINKED -BASED APPROACHES
Another simpler approach in designing inodes is to use a linked list .
Thus, inside an inode, instead of having multiple pointers, you just need
one, to point to the ﬁrst block of the ﬁle. To handle larger ﬁle s, add an-
other pointer at the end of that data block, and so on, and thus you can
support large ﬁles.
As you might have guessed, linked ﬁle allocation performs po orly for
some workloads; think about reading the last block of a ﬁle, f or example,
or just doing random access. Thus, to make linked allocation work better,
some systems will keep an in-memory table of link informatio n, instead
of storing the next pointers with the data blocks themselves . The table
is indexed by the address of a data block D; the content of an entry is
simply D’s next pointer, i.e., the address of the next block in a ﬁle wh ich
follows D. A null-value could be there too (indicating an end-of-ﬁle) , or
some other marker to indicate that a particular block is free . Having such
a table of next pointers makes it so that a linked allocation s cheme can
effectively do random ﬁle accesses, simply by ﬁrst scanning through the
(in memory) table to ﬁnd the desired block, and then accessin g (on disk)
it directly .
Does such a table sound familiar? What we have described is th e basic
structure of what is known as the ﬁle allocation table, or FA Tﬁle system.
Yes, this classic old Windows ﬁle system, before NTFS [C94], is based on a
simple linked-based allocation scheme. There are other dif ferences from
a standard U NIX ﬁle system too; for example, there are no inodes per se,
but rather directory entries which store metadata about a ﬁl e and refer
directly to the ﬁrst block of said ﬁle, which makes creating h ard links
impossible. See Brouwer [B02] for more of the inelegant deta ils.
can directly point to 48 KB of data, needing one (or more) indi rect blocks
for larger ﬁles. See Agrawal et. al [A+07] for a recent study; Table
40.2
summarizes those results.
Of course, in the space of inode design, many other possibili ties ex-
ist; after all, the inode is just a data structure, and any dat a structure that
stores the relevant information, and can query it effective ly , is sufﬁcient.
As ﬁle system software is readily changed, you should be will ing to ex-
plore different designs should workloads or technologies c hange.
Most ﬁles are small Roughly 2K is the most common size
Average ﬁle size is growing Almost 200K is the average
Most bytes are stored in large ﬁles A few big ﬁles use most of the space
File systems contains lots of ﬁles Almost 100K on average
File systems are roughly half full Even as disks grow, ﬁle systems remain ˜50% full
Directories are typically small Many have few entries; most have 20 or fewer
Table 40.2: File System Measurement Summary
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 505

FILE SYSTEM IMPLEMENTATION 469
40.4 Directory Organization
In vsfs (as in many ﬁle systems), directories have a simple or ganiza-
tion; a directory basically just contains a list of (entry na me, inode num-
ber) pairs. For each ﬁle or directory in a given directory , th ere is a string
and a number in the data block(s) of the directory . For each st ring, there
may also be a length (assuming variable-sized names).
For example, assume a directory dir (inode number 5) has three ﬁles
in it ( foo, bar, and foobar), and their inode numbers are 12, 13, and 24
respectively . The on-disk data for dir might look like this:
inum | reclen | strlen | name
5 4 2 .
2 4 3 ..
12 4 4 foo
13 4 4 bar
24 8 7 foobar
In this example, each entry has an inode number, record lengt h (the
total bytes for the name plus any left over space), string len gth (the actual
length of the name), and ﬁnally the name of the entry . Note tha t each di-
rectory has two extra entries, . “dot” and .. “dot-dot”; the dot directory
is just the current directory (in this example, dir), whereas dot-dot is the
parent directory (in this case, the root).
Deleting a ﬁle (e.g., calling unlink()) can leave an empty space in
the middle of the directory , and hence there should be some way to mark
that as well (e.g., with a reserved inode number such as zero) . Such a
delete is one reason the record length is used: a new entry may reuse an
old, bigger entry and thus have extra space within.
You might be wondering where exactly directories are stored . Often,
ﬁle systems treat directories as a special type of ﬁle. Thus, a directory has
an inode, somewhere in the inode table (with the type ﬁeld of t he inode
marked as “directory” instead of “regular ﬁle”). The direct ory has data
blocks pointed to by the inode (and perhaps, indirect blocks ); these data
blocks live in the data block region of our simple ﬁle system. Our on-disk
structure thus remains unchanged.
We should also note again that this simple linear list of dire ctory en-
tries is not the only way to store such information. As before , any data
structure is possible. For example, XFS [S+96] stores direc tories in B-tree
form, making ﬁle create operations (which have to ensure that a ﬁle name
has not been used before creating it) faster than systems wit h simple lists
that must be scanned in their entirety .
40.5 Free Space Management
A ﬁle system must track which inodes and data blocks are free, and
which are not, so that when a new ﬁle or directory is allocated , it can ﬁnd
space for it. Thus free space management is important for all ﬁle systems.
In vsfs, we have two simple bitmaps for this task.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 506

470 FILE SYSTEM IMPLEMENTATION
ASIDE : FREE SPACE MANAGEMENT
There are many ways to manage free space; bitmaps are just one way .
Some early ﬁle systems used free lists, where a single pointer in the super
block was kept to point to the ﬁrst free block; inside that blo ck the next
free pointer was kept, thus forming a list through the free bl ocks of the
system. When a block was needed, the head block was used and th e list
updated accordingly .
Modern ﬁle systems use more sophisticated data structures. For example,
SGI’s XFS [S+96] uses some form of a B-tree to compactly represent which
chunks of the disk are free. As with any data structure, diffe rent time-
space trade-offs are possible.
For example, when we create a ﬁle, we will have to allocate an i node
for that ﬁle. The ﬁle system will thus search through the bitm ap for an in-
ode that is free, and allocate it to the ﬁle; the ﬁle system wil l have to mark
the inode as used (with a 1) and eventually update the on-disk bitmap
with the correct information. A similar set of activities ta ke place when a
data block is allocated.
Some other considerations might also come into play when all ocating
data blocks for a new ﬁle. For example, some Linux ﬁle systems , such
as ext2 and ext3, will look for a sequence of blocks (say 8) tha t are free
when a new ﬁle is created and needs data blocks; by ﬁnding such a se-
quence of free blocks, and then allocating them to the newly- created ﬁle,
the ﬁle system guarantees that a portion of the ﬁle will be on t he disk and
contiguous, thus improving performance. Such a pre-allocation policy is
thus a commonly-used heuristic when allocating space for da ta blocks.
40.6 Access Paths: Reading and Writing
Now that we have some idea of how ﬁles and directories are stor ed on
disk, we should be able to follow the ﬂow of operation during t he activity
of reading or writing a ﬁle. Understanding what happens on th is access
path is thus the second key in developing an understanding of how a ﬁle
system works; pay attention!
For the following examples, let us assume that the ﬁle system has been
mounted and thus that the superblock is already in memory . Ev erything
else (i.e., inodes, directories) is still on the disk.
Reading A File From Disk
In this simple example, let us ﬁrst assume that you want to sim ply open
a ﬁle (e.g., /foo/bar, read it, and then close it. For this simple example,
let’s assume the ﬁle is just 4KB in size (i.e., 1 block).
When you issue an open("/foo/bar", O
RDONLY) call, the ﬁle sys-
tem ﬁrst needs to ﬁnd the inode for the ﬁle bar, to obtain some basic in-
formation about the ﬁle (permissions information, ﬁle size, etc.). To do so,
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 507

FILE SYSTEM IMPLEMENTATION 471
data inode root foo bar root foo bar bar bar
bitmap bitmap inode inode inode data data data[0] data[1] da ta[1]
read
read
open(bar) read
read
read
read
read() read
write
read
read() read
write
read
read() read
write
Table 40.3: File Read Timeline (Time Increasing Downward)
the ﬁle system must be able to ﬁnd the inode, but all it has righ t now is
the full pathname. The ﬁle system must traverse the pathname and thus
locate the desired inode.
All traversals begin at the root of the ﬁle system, in the root directory
which is simply called /. Thus, the ﬁrst thing the FS will read from disk
is the inode of the root directory . But where is this inode? To ﬁnd an
inode, we must know its i-number. Usually , we ﬁnd the i-number of a ﬁle
or directory in its parent directory; the root has no parent ( by deﬁnition).
Thus, the root inode number must be “well known”; the FS must k now
what it is when the ﬁle system is mounted. In most U NIX ﬁle systems,
the root inode number is 2. Thus, to begin the process, the FS r eads in the
block that contains inode number 2 (the ﬁrst inode block).
Once the inode is read in, the FS can look inside of it to ﬁnd poi nters to
data blocks, which contain the contents of the root director y . The FS will
thus use these on-disk pointers to read through the director y , in this case
looking for an entry for foo. By reading in one or more directory data
blocks, it will ﬁnd the entry for foo; once found, the FS will a lso have
found the inode number of foo (say it is 44) which it will need next.
The next step is to recursively traverse the pathname until t he desired
inode is found. In this example, the FS would next read the blo ck contain-
ing the inode of foo and then read in its directory data, ﬁnally ﬁnding the
inode number of bar. The ﬁnal step of open(), then, is to read its inode
into memory; the FS can then do a ﬁnal permissions check, allo cate a ﬁle
descriptor for this process in the per-process open-ﬁle tab le, and return it
to the user.
Once open, the program can then issue a read() system call to read
from the ﬁle. The ﬁrst read (at offset 0 unless lseek() has been called)
will thus read in the ﬁrst block of the ﬁle, consulting the ino de to ﬁnd
the location of such a block; it may also update the inode with a new last-
accessed time. The read will further update the in-memory op en ﬁle table
for this ﬁle descriptor, updating the ﬁle offset such that th e next read will
read the second ﬁle block, etc.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 508

472 FILE SYSTEM IMPLEMENTATION
ASIDE : READS DON ’ T ACCESS ALLOCATION STRUCTURES
We’ve seen many students get confused by allocation structu res such
as bitmaps. In particular, many often think that when you are simply
reading a ﬁle, and not allocating any new blocks, that the bit map will still
be consulted. This is not true! Allocation structures, such as bitmaps,
are only accessed when allocation is needed. The inodes, dir ectories, and
indirect blocks have all the information they need to comple te a read re-
quest; there is no need to make sure a block is allocated when t he inode
already points to it.
At some point, the ﬁle will be closed. There is much less work t o be
done here; clearly , the ﬁle descriptor should be deallocate d, but for now ,
that is all the FS really needs to do. No disk I/Os take place.
A depiction of this entire process is found in Figure40.3 (time increases
downward). In the ﬁgure, the open causes numerous reads to ta ke place
in order to ﬁnally locate the inode of the ﬁle. Afterwards, re ading each
block requires the ﬁle system to ﬁrst consult the inode, then read the
block, and then update the inode’s last-accessed-time ﬁeld with a write.
Spend some time and try to understand what is going on.
Also note that the amount of I/O generated by the open is propo r-
tional to the length of the pathname. For each additional dir ectory in the
path, we have to read its inode as well as its data. Making this worse
would be the presence of large directories; here, we only hav e to read one
block to get the contents of a directory , whereas with a large directory , we
might have to read many data blocks to ﬁnd the desired entry . Y es, life
can get pretty bad when reading a ﬁle; as you’re about to ﬁnd ou t, writing
out a ﬁle (and especially , creating a new one) is even worse.
Writing to Disk
Writing to a ﬁle is a similar process. First, the ﬁle must be op ened (as
above). Then, the application can issue write() calls to update the ﬁle
with new contents. Finally , the ﬁle is closed.
Unlike reading, writing to the ﬁle may also allocate a block (unless
the block is being overwritten, for example). When writing o ut a new
ﬁle, each write not only has to write data to disk but has to ﬁrs t decide
which block to allocate to the ﬁle and thus update other struc tures of the
disk accordingly (e.g., the data bitmap). Thus, each write t o a ﬁle logically
generates three I/Os: one to read the data bitmap, which is th en updated
to mark the newly-allocated block as used, one to write the bi tmap (to
reﬂect its new state to disk), and one to write the actual bloc k itself.
The amount of write trafﬁc is even worse when one considers a s im-
ple and common operation such as ﬁle creation. To create a ﬁle , the ﬁle
system must not only allocate an inode, but also allocate spa ce within
the directory containing the new ﬁle. The total amount of I/O trafﬁc to
do so is quite high: one read to the inode bitmap (to ﬁnd a free i node),
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 509

FILE SYSTEM IMPLEMENTATION 473
data inode root foo bar root foo bar bar bar
bitmap bitmap inode inode inode data data data[0] data[1] da ta[1]
read
read
read
read
create read
(/foo/bar) write
write
read
write
write
read
read
write() write
write
write
read
read
write() write
write
write
read
read
write() write
write
write
Table 40.4: File Creation Timeline (Time Increasing Downward)
one write to the inode bitmap (to mark it allocated), one writ e to the new
inode itself (to initialize it), one to the data of the direct ory (to link the
high-level name of the ﬁle to its inode number), and one read a nd write
to the directory inode to update it. If the directory needs to grow to ac-
commodate the new entry , additional I/Os (i.e., to the data b itmap, and
the new directory block) will be needed too. All that just to c reate a ﬁle!
Let’s look at a speciﬁc example, where the ﬁle /foo/bar is created,
and three blocks are written to it. Figure 40.4 shows what happens during
the open() (which creates the ﬁle) and during each of three 4KB writes.
In the ﬁgure, reads and writes to the disk are grouped under wh ich
system call caused them to occur, and the rough ordering they might take
place in goes from top to bottom of the ﬁgure. You can see how mu ch
work it is to create the ﬁle: 10 I/Os in this case, to walk the pa thname
and then ﬁnally create the ﬁle. You can also see that each allo cating write
costs 5 I/Os: a pair to read and update the inode, another pair to read
and update the data bitmap, and then ﬁnally the write of the da ta itself.
How can a ﬁle system accomplish any of this with reasonable ef ﬁciency?
THE CRUX : H OW TO REDUCE FILE SYSTEM I/O C OSTS
Even the simplest of operations like opening, reading, or wr iting a ﬁle
incurs a huge number of I/O operations, scattered over the di sk. What
can a ﬁle system do to reduce the high costs of doing so many I/O s?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 510

474 FILE SYSTEM IMPLEMENTATION
40.7 Caching and Buffering
As the examples above show , reading and writing ﬁles can be ex pen-
sive, incurring many I/Os to the (slow) disk. To remedy what w ould
clearly be a huge performance problem, most ﬁle systems aggr essively
use system memory (DRAM) to cache important blocks.
Imagine the open example above: without caching, every ﬁle o pen
would require at least two reads for every level in the direct ory hierarchy
(one to read the inode of the directory in question, and at lea st one to read
its data). With a long pathname (e.g., /1/2/3/ ... /100/ﬁle. txt), the ﬁle
system would literally perform hundreds of reads just to ope n the ﬁle!
Early ﬁle systems thus introduced a ﬁx-sized cache to hold popular
blocks. As in our discussion of virtual memory , strategies s uch as LRU
and different variants would decide which blocks to keep in c ache. This
ﬁx-sized cache would usually be allocated at boot time to be r oughly 10%
of total memory . Modern systems integrate virtual memory pages and ﬁle
system pages into a uniﬁed page cache [S00]. In this way , memory can be
allocated more ﬂexibly across virtual memory and ﬁle system, depending
on which needs more memory at a given time.
Now imagine the ﬁle open example with caching. The ﬁrst open m ay
generate a lot of I/O trafﬁc to read in directory inode and dat a, but sub-
sequent ﬁle opens of that same ﬁle (or ﬁles in the same directo ry) will
mostly hit in the cache and thus no I/O is needed.
Let us also consider the effect of caching on writes. Whereas read I/O
can be avoided altogether with a sufﬁciently large cache, wr ite trafﬁc has
to go to disk in order to become persistent. Thus, a cache does not serve
as the same kind of ﬁlter on write trafﬁc that it does for reads . That said,
write buffering (as it is sometimes called) certainly has a number of per-
formance beneﬁts. First, by delaying writes, the ﬁle system can batch
some updates into a smaller set of I/Os; for example, if an ino de bitmap
is updated when one ﬁle is created and then updated moments la ter as
another ﬁle is created, the ﬁle system saves an I/O by delayin g the write
after the ﬁrst update. Second, by buffering a number of write s in memory ,
the system can then schedule the subsequent I/Os and thus increase per-
formance. Finally , some writes are avoided altogether by de laying them;
for example, if an application creates a ﬁle and then deletes it, delaying
the writes to reﬂect the ﬁle creation to disk avoids them entirely . In this
case, laziness (in writing blocks to disk) is a virtue.
For the reasons above, most modern ﬁle systems buffer writes in mem-
ory for anywhere between ﬁve and thirty seconds, representi ng yet an-
other trade-off: if the system crashes before the updates ha ve been prop-
agated to disk, the updates are lost; however, by keeping wri tes in mem-
ory longer, performance can be improved by batching, schedu ling, and
even avoiding writes.
Some applications (such as databases) don’t enjoy this trad e-off. Thus,
to avoid unexpected data loss due to write buffering, they si mply force
writes to disk, by calling fsync(), by using direct I/O interfaces that
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 511

FILE SYSTEM IMPLEMENTATION 475
work around the cache, or by using the raw disk interface and avoiding
the ﬁle system altogether 1. While most applications live with the trade-
offs made by the ﬁle system, there are enough controls in plac e to get the
system to do what you want it to, should the default not be sati sfying.
40.8 Summary
We have seen the basic machinery required in building a ﬁle sy stem.
There needs to be some information about each ﬁle (metadata) , usually
stored in a structure called an inode. Directories are just a speciﬁc type
of ﬁle that store name → inode-number mappings. And other structures
are needed too; for example, ﬁle systems often use a structur e such as a
bitmap to track which inodes or data blocks are free or alloca ted.
The terriﬁc aspect of ﬁle system design is its freedom; the ﬁl e systems
we explore in the coming chapters each take advantage of this freedom
to optimize some aspect of the ﬁle system. There are also clea rly many
policy decisions we have left unexplored. For example, when a new ﬁle
is created, where should it be placed on disk? This policy and others will
also be the subject of future chapters. Or will they?
1Take a database class to learn more about old-school databas es and their former insis-
tence on avoiding the OS and controlling everything themsel ves. But watch out! Those
database types are always trying to bad mouth the OS. Shame onyou, database people. Shame.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 512

476 FILE SYSTEM IMPLEMENTATION
References
[A+07] Nitin Agrawal, William J. Bolosky , John R. Douceur, Jacob R. Lorch
A Five-Year Study of File-System Metadata
FAST ’07, pages 31–45, February 2007, San Jose, CA
An excellent recent analysis of how ﬁle systems are actually used. Use the bibliography within to follow
the trail of ﬁle-system analysis papers back to the early 198 0s.
[B07] “ZFS: The Last Word in File Systems”
Jeff Bonwick and Bill Moore
Available: http://opensolaris.org/os/community/zfs/docs/zfs
last.pdf
One of the most recent important ﬁle systems, full of feature s and awesomeness. We should have a
chapter on it, and perhaps soon will.
[B02] “The FAT File System”
Andries Brouwer
September, 2002
Available: http://www.win.tue.nl/˜aeb/linux/fs/fat/fat.html
A nice clean description of F AT. The ﬁle system kind, not the b acon kind. Though you have to admit,
bacon fat probably tastes better.
[C94] “Inside the Windows NT File System”
Helen Custer
Microsoft Press, 1994
A short book about NTFS; there are probably ones with more tec hnical details elsewhere.
[H+88] “Scale and Performance in a Distributed File System”
John H. Howard, Michael L. Kazar, Sherri G. Menees, David A. N ichols, M. Satyanarayanan,
Robert N. Sidebotham, Michael J. West.
ACM Transactions on Computing Systems (ACM TOCS), page 51-8 1, V olume 6, Number 1,
February 1988
A classic distributed ﬁle system; we’ll be learning more abo ut it later, don’t worry.
[P09] “The Second Extended File System: Internal Layout”
Dave Poirier, 2009
Available: http://www.nongnu.org/ext2-doc/ext2.html
Some details on ext2, a very simple Linux ﬁle system based on F FS, the Berkeley Fast File System. We’ll
be reading about it in the next chapter.
[RT74] “The U NIX Time-Sharing System”
M. Ritchie and K. Thompson
CACM, V olume 17:7, pages 365-375, 1974
The original paper about UNIX. Read it to see the underpinnings of much of modern operating systems.
[S00] “UBC: An Efﬁcient Uniﬁed I/O and Memory Caching Subsys tem for NetBSD”
Chuck Silvers
FREENIX, 2000
A nice paper about NetBSD’s integration of ﬁle-system buffe r caching and the virtual-memory page
cache. Many other systems do the same type of thing.
[S+96] “Scalability in the XFS File System”
Adan Sweeney , Doug Doucette, Wei Hu, Curtis Anderson,
Mike Nishimoto, Geoff Peck
USENIX ’96, January 1996, San Diego, CA
The ﬁrst attempt to make scalability of operations, includi ng things like having millions of ﬁles in a
directory, a central focus. A great example of pushing an ide a to the extreme. The key idea behind this
ﬁle system: everything is a tree. We should have a chapter on t his ﬁle system too.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 513

FILE SYSTEM IMPLEMENTATION 477
Homework
Use this tool, vsfs.py, to study how ﬁle system state changes as var-
ious operations take place. The ﬁle system begins in an empty state, with
just a root directory . As the simulation takes place, various operations are
performed, thus slowly changing the on-disk state of the ﬁle system. See
the README for details.
Questions
1. Run the simulator with some different random seeds (say 17 , 18, 19,
20), and see if you can ﬁgure out which operations must have ta ken
place between each state change.
2. Now do the same, using different random seeds (say 21, 22, 2 3,
24), except run with the -r ﬂag, thus making you guess the state
change while being shown the operation. What can you conclud e
about the inode and data-block allocation algorithms, in te rms of
which blocks they prefer to allocate?
3. Now reduce the number of data blocks in the ﬁle system, to ve ry
low numbers (say two), and run the simulator for a hundred or s o
requests. What types of ﬁles end up in the ﬁle system in this hi ghly-
constrained layout? What types of operations would fail?
4. Now do the same, but with inodes. With very few inodes, what
types of operations can succeed? Which will usually fail? Wh at is
the ﬁnal state of the ﬁle system likely to be?
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 515

41
Locality and The Fast File System
When the U NIX operating system was ﬁrst introduced, the U NIX wizard
himself Ken Thompson wrote the ﬁrst ﬁle system. We will call t hat the
“old U NIX ﬁle system”, and it was really simple. Basically , its data st ruc-
tures looked like this on the disk:
S Inodes Data
The super block (S) contained information about the entire ﬁ le system:
how big the volume is, how many inodes there are, a pointer to t he head
of a free list of blocks, and so forth. The inode region of the d isk contained
all the inodes for the ﬁle system. Finally , most of the disk wa s taken up
by data blocks.
The good thing about the old ﬁle system was that it was simple, and
supported the basic abstractions the ﬁle system was trying t o deliver:
ﬁles and the directory hierarchy . This easy-to-use system w as a real step
forward from the clumsy , record-based storage systems of th e past, and
the directory hierarchy a true advance over simpler, one-le vel hierarchies
provided by earlier systems.
41.1 The Problem: Poor Performance
The problem: performance was terrible. As measured by Kirk M cKu-
sick and his colleagues at Berkeley [MJLF84], performance s tarted off bad
and got worse over time, to the point where the ﬁle system was delivering
only 2% of overall disk bandwidth!
The main issue was that the old UNIX ﬁle system treated the disk like it
was a random-access memory; data was spread all over the place without
regard to the fact that the medium holding the data was a disk, and thus
had real and expensive positioning costs. For example, the d ata blocks of
a ﬁle were often very far away from its inode, thus inducing an expensive
seek whenever one ﬁrst read the inode and then the data blocks of a ﬁle
(a pretty common operation).
479

## Page 516

480 LOCALITY AND THE FAST FILE SYSTEM
Worse, the ﬁle system would end up getting quite fragmented, as the
free space was not carefully managed. The free list would end up point-
ing to a bunch of blocks spread across the disk, and as ﬁles got allocated,
they would simply take the next free block. The result was tha t a logi-
cally contiguous ﬁle would be accessed by going back and fort h across
the disk, thus reducing performance dramatically .
For example, imagine the following data block region, which contains
four ﬁles (A, B, C, and D), each of size 2 blocks:
A1 A2 B1 B2 C1 C2 D1 D2
If B and D are deleted, the resulting layout is:
A1 A2 C1 C2
As you can see, the free space is fragmented into two chunks of two
blocks, instead of one nice contiguous chunk of four. Let’s s ay we now
wish to allocate a ﬁle E, of size four blocks:
A1 A2 E1 E2 C1 C2 E3 E4
You can see what happens: E gets spread across the disk, and as a
result, when accessing E, you don’t get peak (sequential) pe rformance
from the disk. Rather, you ﬁrst read E1 and E2, then seek, then read E3
and E4. This fragmentation problem happened all the time in t he old
UNIX ﬁle system, and it hurt performance. (A side note: this probl em is
exactly what disk defragmentation tools help with; they wil l reorganize
on-disk data to place ﬁles contiguously and make free space o ne or a few
contiguous regions, moving data around and then rewriting i nodes and
such to reﬂect the changes)
One other problem: the original block size was too small (512 bytes).
Thus, transferring data from the disk was inherently inefﬁc ient. Smaller
blocks were good because they minimized internal fragmentation (waste
within the block), but bad for transfer as each block might re quire a posi-
tioning overhead to reach it. We can summarize the problem as follows:
THE CRUX :
HOW TO ORGANIZE ON-DISK DATA TO IMPROVE PERFORMANCE
How can we organize ﬁle system data structures so as to improv e per-
formance? What types of allocation policies do we need on top of those
data structures? How do we make the ﬁle system “disk aware”?
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 517

LOCALITY AND THE FAST FILE SYSTEM 481
41.2 FFS: Disk Awareness Is The Solution
A group at Berkeley decided to build a better, faster ﬁle syst em, which
they cleverly called the Fast File System (FFS) . The idea was to design
the ﬁle system structures and allocation policies to be “dis k aware” and
thus improve performance, which is exactly what they did. FF S thus ush-
ered in a new era of ﬁle system research; by keeping the same interface
to the ﬁle system (the same APIs, including open(), read(), write(),
close(), and other ﬁle system calls) but changing the internal implemen-
tation, the authors paved the path for new ﬁle system construction, work
that continues today . Virtually all modern ﬁle systems adhe re to the ex-
isting interface (and thus preserve compatibility with app lications) while
changing their internals for performance, reliability , or other reasons.
41.3 Organizing Structure: The Cylinder Group
The ﬁrst step was to change the on-disk structures. FFS divid es the
disk into a bunch of groups known as cylinder groups (some modern ﬁle
systems like Linux ext2 and ext3 just call them block groups ). We can
thus imagine a disk with ten cylinder groups:
G0 G1 G2 G3 G4 G5 G6 G7 G8 G9
These groups are the central mechanism that FFS uses to impro ve per-
formance; by placing two ﬁles within the same group, FFS can ensure that
accessing one after the other will not result in long seeks ac ross the disk.
Thus, FFS needs to have the ability to allocate ﬁles and direc tories
within each of these groups. Each group looks like this:
S ib db Inodes Data
We now describe the components of a cylinder group. A copy of t he
super block (S) is found in each group for reliability reasons (e.g., if o ne
gets corrupted or scratched, you can still mount and access the ﬁle system
by using one of the others).
The inode bitmap (ib) and data bitmap (db) track whether each inode
or data block is free, respectively . Bitmaps are an excellent way to manage
free space in a ﬁle system because it is easy to ﬁnd a large chun k of free
space and allocate it to a ﬁle, perhaps avoiding some of the fr agmentation
problems of the free list in the old ﬁle system.
Finally , the inode and data block regions are just like in the previous
very simple ﬁle system. Most of each cylinder group, as usual , is com-
prised of data blocks.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 518

482 LOCALITY AND THE FAST FILE SYSTEM
ASIDE : FFS F ILE CREATION
As an example, think about what data structures must be updat ed when
a ﬁle is created; assume, for this example, that the user crea tes a new ﬁle
/foo/bar.txt and that the ﬁle is one block long (4KB). The ﬁle is new ,
and thus needs a new inode; thus, both the inode bitmap and the newly-
allocated inode will be written to disk. The ﬁle also has data in it and
thus it too must be allocated; the data bitmap and a data block will thus
(eventually) be written to disk. Hence, at least four writes to the current
cylinder group will take place (recall that these writes may be buffered
in memory for a while before the write takes place). But this i s not all!
In particular, when creating a new ﬁle, we must also place the ﬁle in the
ﬁle-system hierarchy; thus, the directory must be updated. Speciﬁcally ,
the parent directory foo must be updated to add the entry for bar.txt;
this update may ﬁt in an existing data block of foo or require a new block
to be allocated (with associated data bitmap). The inode of foo must also
be updated, both to reﬂect the new length of the directory as w ell as to
update time ﬁelds (such as last-modiﬁed-time). Overall, it is a lot of work
just to create a new ﬁle! Perhaps next time you do so, you shoul d be more
thankful, or at least surprised that it all works so well.
41.4 Policies: How To Allocate Files and Directories
With this group structure in place, FFS now has to decide how t o place
ﬁles and directories and associated metadata on disk to impr ove perfor-
mance. The basic mantra is simple: keep related stuff together (and its corol-
lary , keep unrelated stuff far apart).
Thus, to obey the mantra, FFS has to decide what is “related” a nd
place it within the same block group; conversely , unrelated items should
be placed into different block groups. To achieve this end, F FS makes use
of a few simple placement heuristics.
The ﬁrst is the placement of directories. FFS employs a simpl e ap-
proach: ﬁnd the cylinder group with a low number of allocated directo-
ries (because we want to balance directories across groups) and a high
number of free inodes (because we want to subsequently be abl e to allo-
cate a bunch of ﬁles), and put the directory data and inode in t hat group.
Of course, other heuristics could be used here (e.g., taking into account
the number of free data blocks).
For ﬁles, FFS does two things. First, it makes sure (in the gen eral case)
to allocate the data blocks of a ﬁle in the same group as its ino de, thus
preventing long seeks between inode and data (as in the old ﬁl e sys-
tem). Second, it places all ﬁles that are in the same director y in the cylin-
der group of the directory they are in. Thus, if a user creates four ﬁles,
/dir1/1.txt, /dir1/2.txt, /dir1/3.txt, and /dir99/4.txt, FFS
would try to place the ﬁrst three near one another (same group ) and the
fourth far away (in some other group).
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 519

LOCALITY AND THE FAST FILE SYSTEM 483
0 2 4 6 8 10
0%
20%
40%
60%
80%
100%
FFS Locality
Path Difference
Cumulative Frequency
Trace
Random
Figure 41.1: FFS Locality For SEER T races
It should be noted that these heuristics are not based on exte nsive
studies of ﬁle-system trafﬁc or anything particularly nuanced; rather, they
are based on good old-fashioned common sense (isn’t that wha t CS stands
for after all?). Files in a directory are often accessed together (imagine
compiling a bunch of ﬁles and then linking them into a single executable).
Because they are, FFS will often improve performance, makin g sure that
seeks between related ﬁles are short.
41.5 Measuring File Locality
To understand better whether these heuristics make sense, we decided
to analyze some traces of ﬁle system access and see if indeed t here is
namespace locality; for some reason, there doesn’t seem to b e a good
study of this topic in the literature.
Speciﬁcally , we took the SEER traces [K94] and analyzed how “ far
away” ﬁle accesses were from one another in the directory tre e. For ex-
ample, if ﬁle f is opened, and then re-opened next in the trace (before
any other ﬁles are opened), the distance between these two op ens in the
directory tree is zero (as they are the same ﬁle). If a ﬁle f in directory
dir (i.e., dir/f) is opened, and followed by an open of ﬁle g in the same
directory (i.e., dir/g), the distance between the two ﬁle accesses is one,
as they share the same directory but are not the same ﬁle. Our d istance
metric, in other words, measures how far up the directory tre e you have
to travel to ﬁnd the common ancestor of two ﬁles; the closer they are in the
tree, the lower the metric.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 520

484 LOCALITY AND THE FAST FILE SYSTEM
Figure 41.1 shows the locality observed in the SEER traces over all
workstations in the SEER cluster over the entirety of all tra ces. The graph
plots the difference metric along the x-axis, and shows the c umulative
percentage of ﬁle opens that were of that difference along th e y-axis.
Speciﬁcally , for the SEER traces (marked “Trace” in the grap h), you can
see that about 7% of ﬁle accesses were to the ﬁle that was opene d previ-
ously , and that nearly 40% of ﬁle accesses were to either the s ame ﬁle or
to one in the same directory (i.e., a difference of zero or one ). Thus, the
FFS locality assumption seems to make sense (at least for the se traces).
Interestingly , another 25% or so of ﬁle accesses were to ﬁles that had a
distance of two. This type of locality occurs when the user ha s structured
a set of related directories in a multi-level fashion and con sistently jumps
between them. For example, if a user has a src directory and builds
object ﬁles ( .o ﬁles) into a obj directory , and both of these directories
are sub-directories of a main proj directory , a common access pattern
will be proj/src/foo.c followed by proj/obj/foo.o. The distance
between these two accesses is two, as proj is the common ancestor. FFS
does not capture this type of locality in its policies, and thus more s eeking
will occur between such accesses.
We also show what locality would be for a “Random” trace for th e
sake of comparison. We generated the random trace by selecti ng ﬁles
from within an existing SEER trace in random order, and calcu lating the
distance metric between these randomly-ordered accesses. As you can
see, there is less namespace locality in the random traces, a s expected.
However, because eventually every ﬁle shares a common ances tor (e.g.,
the root), there is some locality eventually , and thus rando m trace is use-
ful as a comparison point.
41.6 The Large-File Exception
In FFS, there is one important exception to the general polic y of ﬁle
placement, and it arises for large ﬁles. Without a different rule, a large
ﬁle would entirely ﬁll the block group it is ﬁrst placed withi n (and maybe
others). Filling a block group in this manner is undesirable , as it prevents
subsequent “related” ﬁles from being placed within this block group, and
thus may hurt ﬁle-access locality .
Thus, for large ﬁles, FFS does the following. After some numb er of
blocks are allocated into the ﬁrst block group (e.g., 12 bloc ks, or the num-
ber of direct pointers available within an inode), FFS places the next “large”
chunk of the ﬁle (e.g., those pointed to by the ﬁrst indirect b lock) in an-
other block group (perhaps chosen for its low utilization). Then, the next
chunk of the ﬁle is placed in yet another different block grou p, and so on.
Let’s look at some pictures to understand this policy better . Without
the large-ﬁle exception, a single large ﬁle would place all o f its blocks into
one part of the disk. We use a small example of a ﬁle with 10 bloc ks to
illustrate the behavior visually .
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

