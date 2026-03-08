# Document: operating_systems_three_easy_pieces (Pages 1 to 40)

## Page 1

OPERATING SYSTEMS
THREE EASY PIECES
REMZI H. A RPACI -D USSEAU
ANDREA C. A RPACI -D USSEAU
UNIVERSITY OF WISCONSIN –M ADISON

## Page 3

. .
c⃝ 2014 by Arpaci-Dusseau Books, Inc.
All rights reserved

## Page 5

i
T o Vedat S. Arpaci, a lifelong inspiration
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 7

Preface
T o Everyone
W elcome to this book! W e hope you’ll enjoy reading it as much a s we enjoyed
writing it. The book is called Operating Systems: Three Easy Pieces , and the title
is obviously an homage to one of the greatest sets of lecture n otes ever created, by
one Richard Feynman on the topic of Physics [F96]. While this book will undoubt-
edly fall short of the high standard set by that famous physic ist, perhaps it will be
good enough for you in your quest to understand what operatin g systems (and
more generally , systems) are all about.
The three easy pieces refer to the three major thematic eleme nts the book is
organized around: virtualization, concurrency, and persistence. In discussing
these concepts, we’ll end up discussing most of the importan t things an operating
system does; hopefully , you’ll also have some fun along the w ay . Learning new
things is fun, right? At least, it should be.
Each major concept is divided into a set of chapters, most of w hich present a
particular problem and then show how to solve it. The chapter s are short, and try
(as best as possible) to reference the source material where the ideas really came
from. One of our goals in writing this book is to make the paths of history as clear
as possible, as we think that helps a student understand what is, what was, and
what will be more clearly . In this case, seeing how the sausag e was made is nearly
as important as understanding what the sausage is good for 1.
There are a couple devices we use throughout the book which ar e probably
worth introducing here. The ﬁrst is the crux of the problem. Anytime we are
trying to solve a problem, we ﬁrst try to state what the most im portant issue is;
such a crux of the problem is explicitly called out in the text, and hopefully solved
via the techniques, algorithms, and ideas presented in the r est of the text.
There are also numerous asides and tips throughout the text, adding a little
color to the mainline presentation. Asides tend to discuss s omething relevant (but
perhaps not essential) to the main text; tips tend to be gener al lessons that can be
applied to systems you build. An index at the end of the book li sts all of these tips
and asides (as well as cruces, the odd plural of crux) for your convenience.
W e use one of the oldest didactic methods, the dialogue, throughout the book,
as a way of presenting some of the material in a different ligh t. These are used to
introduce the major thematic concepts (in a peachy way , as we will see), as well as
to review material every now and then. They are also a chance t o write in a more
1Hint: eating! Or if you’re a vegetarian, running away from.
iii

## Page 8

iv
humorous style. Whether you ﬁnd them useful, or humorous, we ll, that’s another
matter entirely .
At the beginning of each major section, we’ll ﬁrst present an abstraction that an
operating system provides, and then work in subsequent chap ters on the mecha-
nisms, policies, and other support needed to provide the abs traction. Abstractions
are fundamental to all aspects of Computer Science, so it is p erhaps no surprise
that they are also essential in operating systems.
Throughout the chapters, we try to use real code (not pseudocode) where pos-
sible, so for virtually all examples, you should be able to ty pe them up yourself
and run them. Running real code on real systems is the best way to learn about
operating systems, so we encourage you to do so when you can.
In various parts of the text, we have sprinkled in a few homeworks to ensure
that you are understanding what is going on. Many of these hom eworks are little
simulations of pieces of the operating system; you should download the ho me-
works, and run them to quiz yourself. The homework simulator s have the follow-
ing feature: by giving them a different random seed, you can g enerate a virtually
inﬁnite set of problems; the simulators can also be told to so lve the problems for
you. Thus, you can test and re-test yourself until you have ac hieved a good level
of understanding.
The most important addendum to this book is a set of projects in which you
learn about how real systems work by designing, implementin g, and testing your
own code. All projects (as well as the code examples, mention ed above) are in
the C programming language [KR88]; C is a simple and powerful language that
underlies most operating systems, and thus worth adding to y our tool-chest of
languages. Two types of projects are available (see the onli ne appendix for ideas).
The ﬁrst are systems programming projects; these projects are great for those who
are new to C and U NIX and want to learn how to do low-level C programming.
The second type are based on a real operating system kernel de veloped at MIT
called xv6 [CK+08]; these projects are great for students th at already have some C
and want to get their hands dirty inside the OS. At Wisconsin, we’ve run the course
in three different ways: either all systems programming, al l xv6 programming, or
a mix of both.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 9

v
T o Educators
If you are an instructor or professor who wishes to use this bo ok, please feel
free to do so. As you may have noticed, they are free and availa ble on-line from
the following web page:
http://www.ostep.org
You can also purchase a printed copy from lulu.com. Look for it on the web
page above.
The (current) proper citation for the book is as follows:
Operating Systems: Three Easy Pieces
Remzi H. Arpaci-Dusseau and Andrea C. Arpaci-Dusseau
Arpaci-Dusseau Books, Inc.
May , 2014 (V ersion 0.8)
http://www.ostep.org
The course divides fairly well across a 15-week semester, in which you can
cover most of the topics within at a reasonable level of depth . Cramming the
course into a 10-week quarter probably requires dropping so me detail from each
of the pieces. There are also a few chapters on virtual machin e monitors, which we
usually squeeze in sometime during the semester, either rig ht at end of the large
section on virtualization, or near the end as an aside.
One slightly unusual aspect of the book is that concurrency , a topic at the front
of many OS books, is pushed off herein until the student has bu ilt an understand-
ing of virtualization of the CPU and of memory . In our experie nce in teaching
this course for nearly 15 years, students have a hard time und erstanding how the
concurrency problem arises, or why they are trying to solve i t, if they don’t yet un-
derstand what an address space is, what a process is, or why co ntext switches can
occur at arbitrary points in time. Once they do understand th ese concepts, how-
ever, introducing the notion of threads and the problems tha t arise due to them
becomes rather easy , or at least, easier.
You may have noticed there are no slides that go hand-in-hand with the book.
The major reason for this omission is that we believe in the mo st old-fashioned
of teaching methods: chalk and a blackboard. Thus, when we te ach the course,
we come to class with a few major ideas and examples in mind and use the board
to present them; handouts and live code demos sprinkled are a lso useful. In our
experience, using too many slides encourages students to “c heck out” of lecture
(and log into facebook.com), as they know the material is the re for them to digest
later; using the blackboard makes lecture a “live” viewing e xperience and thus
(hopefully) more interactive, dynamic, and enjoyable for the students in your class.
If you’d like a copy of the notes we use in preparation for clas s, please drop us
an email. W e have already shared them with many others around the world.
One last request: if you use the free online chapters, please just link to them,
instead of making a local copy . This helps us track usage (ove r 1 million chapters
downloaded in the past few years!) and also ensures students get the latest and
greatest version.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 10

vi
T o Students
If you are a student reading this book, thank you! It is an hono r for us to
provide some material to help you in your pursuit of knowledg e about operating
systems. W e both think back fondly towards some textbooks ofour undergraduate
days (e.g., Hennessy and Patterson [HP90], the classic book on computer architec-
ture) and hope this book will become one of those positive mem ories for you.
You may have noticed this book is free and available online. T here is one major
reason for this: textbooks are generally too expensive. Thi s book, we hope, is
the ﬁrst of a new wave of free materials to help those in pursui t of their education,
regardless of which part of the world they come from or how much they are willing
to spend for a book. Failing that, it is one free book, which is better than none.
W e also hope, where possible, to point you to the original sou rces of much
of the material in the book: the great papers and persons who h ave shaped the
ﬁeld of operating systems over the years. Ideas are not pulle d out of the air; they
come from smart and hard-working people (including numerou s Turing-award
winners2), and thus we should strive to celebrate those ideas and peop le where
possible. In doing so, we hopefully can better understand th e revolutions that
have taken place, instead of writing texts as if those though ts have always been
present [K62]. Further, perhaps such references will encou rage you to dig deeper
on your own; reading the famous papers of our ﬁeld is certainl y one of the best
ways to learn.
2The Turing Award is the highest award in Computer Science; it is like the Nobel Prize,
except that you have never heard of it.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 11

vii
Acknowledgments
This section will contain thanks to those who helped us put th e book together.
The important thing for now: your name could go here! But, you have to help. So
send us some feedback and help debug this book. And you could b e famous! Or,
at least, have your name in some book.
The people who have helped so far include: Abhirami Senthilk umaran*, Adam
Drescher, Adam Eggum, Ahmed Fikri*, Ajaykrishna Raghavan,Alex Wyler, Anand
Mundada, B. Brahmananda Reddy (Minnesota), Bala Subrahman yam Kambala,
Benita Bose, Biswajit Mazumder (Clemson), Bobby Jack, Bj ¨ o rn Lindberg, Bren-
nan Payne, Brian Kroth, Cara Lauritzen, Charlotte Kissinge r, Chien-Chung Shen
(Delaware)*, Cody Hanson, Dan Soendergaard (U. Aarhus), Da vid Hanle (Grin-
nell), Deepika Muthukumar, Dorian Arnold (New Mexico), Dustin Metzler, Dustin
Passofaro, Emily Jacobson, Emmett Witchel (Texas), Ernst B iersack (France), Finn
Kuusisto*, Guilherme Baptista, Hamid Reza Ghasemi, Henry A bbey , Hrishikesh
Amur, Huanchen Zhang*, Jake Gillberg, James Perry (U. Michigan-Dearborn)*, Jay
Lim, Jerod W einman (Grinnell), Joel Sommers (Colgate), Jonathan Perry (MIT), Jun
He, Karl W allinger, Kaushik Kannan, Kevin Liu*, Lei Tian (U. Nebraska-Lincoln),
Leslie Schultz, Lihao W ang, Martha Ferris, Masashi Kishika wa (Sony), Matt Rei-
choff, Matty Williams, Meng Huang, Mike Griepentrog, Ming C hen (Stonybrook),
Mohammed Alali (Delaware), Murugan Kandaswamy , Natasha Ei lbert, Nathan
Dipiazza, Nathan Sullivan, Neeraj Badlani (N.C. State), Ne lson Gomez, Nghia
Huynh (Texas), Patricio Jara, Radford Smith, Ripudaman Sin gh, Ross Aiken, Rus-
lan Kiselev , Ryland Herrick, Samer Al-Kiswany , Sandeep Umm adi (Minnesota),
Satish Chebrolu (NetApp), Satyanarayana Shanmugam*, Seth Pollen, Sharad Punuganti,
Shreevatsa R., Sivaraman Sivaraman*, Srinivasan Thirunarayanan*, Suriyhaprakhas
Balaram Sankari, Sy Jin Cheah, Thomas Griebel, Tongxin Zhen g, Tony Adkins,
Torin Rudeen (Princeton), Tuo W ang, Varun Vats, Xiang Peng, Xu Di, Yue Zhuo
(Texas A&M), Yufui Ren, Zef RosnBrick, Zuyu Zhang. Special t hanks to those
marked with an asterisk above, who have gone above and beyond in their sugges-
tions for improvement.
Special thanks to Professor Joe Meehean (Lynchburg) for his detailed notes on
each chapter, to Professor Jerod W einman (Grinnell) and his entire class for their
incredible booklets, and to Professor Chien-Chung Shen (De laware) for his invalu-
able and detailed reading and comments about the book. All th ree have helped
these authors immeasurably in the reﬁnement of the material s herein.
Also, many thanks to the hundreds of students who have taken 5 37 over the
years. In particular, the Fall ’08 class who encouraged the ﬁ rst written form of
these notes (they were sick of not having any kind of textbook to read – pushy
students!), and then praised them enough for us to keep going (including one hi-
larious “ZOMG! You should totally write a textbook!” commen t in our course
evaluations that year).
A great debt of thanks is also owed to the brave few who took the xv6 project
lab course, much of which is now incorporated into the main 53 7 course. From
Spring ’09: Justin Cherniak, Patrick Deline, Matt Czech, To ny Gregerson, Michael
Griepentrog, Tyler Harter, Ryan Kroiss, Eric Radzikowski, W esley Reardan, Rajiv
Vaidyanathan, and Christopher W aclawik. From Fall ’09: Nic k Bearson, Aaron
Brown, Alex Bird, David Capel, Keith Gould, Tom Grim, Jeffre y Hugo, Brandon
Johnson, John Kjell, Boyan Li, James Loethen, Will McCardel l, Ryan Szaroletta, Si-
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 12

viii
mon Tso, and Ben Yule. From Spring ’10: Patrick Blesi, Aidan D ennis-Oehling,
Paras Doshi, Jake Friedman, Benjamin Frisch, Evan Hanson, P ikkili Hemanth,
Michael Jeung, Alex Langenfeld, Scott Rick, Mike Treffert, Garret Staus, Brennan
W all, Hans W erner, Soo-Young Yang, and Carlos Grifﬁn (almost).
Although they do not directly help with the book, our graduat e students have
taught us much of what we know about systems. W e talk with them regularly
while they are at Wisconsin, but they do all the real work – and by telling us about
what they are doing, we learn new things every week. This list includes the fol-
lowing collection of current and former students with whom w e published pa-
pers; an asterisk marks those who received a Ph.D. under our g uidance: Abhishek
Rajimwale, Ao Ma, Brian Forney , Chris Dragga, Deepak Ramamu rthi, Florentina
Popovici*, Haryadi S. Gunawi*, James Nugent, John Bent*, La nyue Lu, Lakshmi
Bairavasundaram*, Laxman Visampalli, Leo Arulraj, Meenal i Rungta, Muthian Si-
vathanu*, Nathan Burnett*, Nitin Agrawal*, Sriram Subrama nian*, Stephen Todd
Jones*, Swaminathan Sundararaman*, Swetha Krishnan, Thanh Do, Thanumalayan
S. Pillai, Timothy Denehy*, Tyler Harter, V enkat V enkataramani, Vijay Chidambaram,
Vijayan Prabhakaran*, Yiying Zhang*, Yupu Zhang*, Zev W eiss.
A ﬁnal debt of gratitude is also owed to Aaron Brown, who ﬁrst took this course
many years ago (Spring ’09), then took the xv6 lab course (Fal l ’09), and ﬁnally was
a graduate teaching assistant for the course for two years or so (Fall ’10 through
Spring ’12). His tireless work has vastly improved the state of the projects (par-
ticularly those in xv6 land) and thus has helped better the le arning experience for
countless undergraduates and graduates here at Wisconsin. As Aaron would say
(in his usual succinct manner): “Thx.”
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 13

ix
Final Words
Yeats famously said “Education is not the ﬁlling of a pail but the lighting of a
ﬁre.” He was right but wrong at the same time 3. You do have to “ﬁll the pail” a bit,
and these notes are certainly here to help with that part of yo ur education; after all,
when you go to interview at Google, and they ask you a trick que stion about how
to use semaphores, it might be good to actually know what a sem aphore is, right?
But Yeats’s larger point is obviously on the mark: the real po int of education
is to get you interested in something, to learn something mor e about the subject
matter on your own and not just what you have to digest to get a g ood grade in
some class. As one of our fathers (Remzi’s dad, V edat Arpaci) used to say , “Learn
beyond the classroom”.
W e created these notes to spark your interest in operating systems, to read more
about the topic on your own, to talk to your professor about al l the exciting re-
search that is going on in the ﬁeld, and even to get involved wi th that research. It
is a great ﬁeld(!), full of exciting and wonderful ideas that have shaped computing
history in profound and important ways. And while we underst and this ﬁre won’t
light for all of you, we hope it does for many , or even a few . Bec ause once that ﬁre
is lit, well, that is when you truly become capable of doing so mething great. And
thus the real point of the educational process: to go forth, t o study many new and
fascinating topics, to learn, to mature, and most important ly , to ﬁnd something
that lights a ﬁre for you.
Andrea and Remzi
Married couple
Professors of Computer Science at the University of Wiscons in
Chief Lighters of Fires, hopefully 4
3If he actually said this; as with many famous quotes, the hist ory of this gem is murky .
4If this sounds like we are admitting some past history as arso nists, you are probably
missing the point. Probably . If this sounds cheesy , well, that’s because it is, but you’ll just have
to forgive us for that.
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 14

x
References
[CK+08] “The xv6 Operating System”
Russ Cox, Frans Kaashoek, Robert Morris, Nickolai Zeldovic h
From: http://pdos.csail.mit.edu/6.828/2008/index.htm l
xv6 was developed as a port of the original UNIX version 6 and represents a beautiful, clean, and simple
way to understand a modern operating system.
[F96] “Six Easy Pieces: Essentials Of Physics Explained By I ts Most Brilliant Teacher”
Richard P . Feynman
Basic Books, 1996
This book reprints the six easiest chapters of Feynman’s Lec tures on Physics, from 1963. If you like
Physics, it is a fantastic read.
[HP90] “Computer Architecture a Quantitative Approach” (1 st ed.)
David A. Patterson and John L. Hennessy
Morgan-Kaufman, 1990
A book that encouraged each of us at our undergraduate institutions to pursue graduate studies; we later
both had the pleasure of working with Patterson, who greatly shaped the foundations of our research
careers.
[KR88] “The C Programming Language”
Brian Kernighan and Dennis Ritchie
Prentice-Hall, April 1988
The C programming reference that everyone should have, by th e people who invented the language.
[K62] “The Structure of Scientiﬁc Revolutions”
Thomas S. Kuhn
University of Chicago Press, 1962
A great and famous read about the fundamentals of the scientiﬁc process. Mop-up work, anomaly, crisis,
and revolution. We are mostly destined to do mop-up work, ala s.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 15

Contents
To Everyone . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . iii
To Educators . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . v
To Students . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . vi
Acknowledgments . . . . . . . . . . . . . . . . . . . . . . . . . . . vii
Final Words . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . ix
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . x
1 A Dialogue on the Book 1
2 Introduction to Operating Systems 3
2.1 Virtualizing the CPU . . . . . . . . . . . . . . . . . . . . . . 5
2.2 Virtualizing Memory . . . . . . . . . . . . . . . . . . . . . . 7
2.3 Concurrency . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
2.4 Persistence . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.5 Design Goals . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
2.6 Some History . . . . . . . . . . . . . . . . . . . . . . . . . . 14
2.7 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
I Virtualization 21
3 A Dialogue on Virtualization 23
4 The Abstraction: The Process 25
4.1 The Abstraction: A Process . . . . . . . . . . . . . . . . . . . 26
4.2 Process API . . . . . . . . . . . . . . . . . . . . . . . . . . . 27
4.3 Process Creation: A Little More Detail . . . . . . . . . . . . 28
4.4 Process States . . . . . . . . . . . . . . . . . . . . . . . . . . 29
4.5 Data Structures . . . . . . . . . . . . . . . . . . . . . . . . . 30
4.6 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
xi

## Page 16

xii CONTENTS
5 Interlude: Process API 35
5.1 The fork() System Call . . . . . . . . . . . . . . . . . . . . 35
5.2 Adding wait() System Call . . . . . . . . . . . . . . . . . . 37
5.3 Finally , the exec() System Call . . . . . . . . . . . . . . . . 38
5.4 Why? Motivating the API . . . . . . . . . . . . . . . . . . . 39
5.5 Other Parts of the API . . . . . . . . . . . . . . . . . . . . . . 42
5.6 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 42
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43
6 Mechanism: Limited Direct Execution 45
6.1 Basic Technique: Limited Direct Execution . . . . . . . . . . 45
6.2 Problem #1: Restricted Operations . . . . . . . . . . . . . . . 46
6.3 Problem #2: Switching Between Processes . . . . . . . . . . 50
6.4 Worried About Concurrency? . . . . . . . . . . . . . . . . . 54
6.5 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 55
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 57
Homework (Measurement) . . . . . . . . . . . . . . . . . . . . . . 58
7 Scheduling: Introduction 59
7.1 Workload Assumptions . . . . . . . . . . . . . . . . . . . . . 59
7.2 Scheduling Metrics . . . . . . . . . . . . . . . . . . . . . . . 60
7.3 First In, First Out (FIFO) . . . . . . . . . . . . . . . . . . . . 60
7.4 Shortest Job First (SJF) . . . . . . . . . . . . . . . . . . . . . 62
7.5 Shortest Time-to-Completion First (STCF) . . . . . . . . . . 63
7.6 Round Robin . . . . . . . . . . . . . . . . . . . . . . . . . . . 65
7.7 Incorporating I/O . . . . . . . . . . . . . . . . . . . . . . . . 66
7.8 No More Oracle . . . . . . . . . . . . . . . . . . . . . . . . . 68
7.9 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 68
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 69
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 70
8 Scheduling:The Multi-Level Feedback Queue 71
8.1 MLFQ: Basic Rules . . . . . . . . . . . . . . . . . . . . . . . 72
8.2 Attempt #1: How to Change Priority . . . . . . . . . . . . . 73
8.3 Attempt #2: The Priority Boost . . . . . . . . . . . . . . . . . 76
8.4 Attempt #3: Better Accounting . . . . . . . . . . . . . . . . . 77
8.5 Tuning MLFQ And Other Issues . . . . . . . . . . . . . . . . 78
8.6 MLFQ: Summary . . . . . . . . . . . . . . . . . . . . . . . . 79
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 82
9 Scheduling: Proportional Share 83
9.1 Basic Concept: Tickets Represent Your Share . . . . . . . . . 83
9.2 Ticket Mechanisms . . . . . . . . . . . . . . . . . . . . . . . 85
9.3 Implementation . . . . . . . . . . . . . . . . . . . . . . . . . 86
9.4 An Example . . . . . . . . . . . . . . . . . . . . . . . . . . . 87
9.5 How To Assign Tickets? . . . . . . . . . . . . . . . . . . . . . 88
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 17

CONTENTS xiii
9.6 Why Not Deterministic? . . . . . . . . . . . . . . . . . . . . 88
9.7 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 89
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 91
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 92
10 Multiprocessor Scheduling (Advanced) 93
10.1 Background: Multiprocessor Architecture . . . . . . . . . . 94
10.2 Don’t Forget Synchronization . . . . . . . . . . . . . . . . . 96
10.3 One Final Issue: Cache Afﬁnity . . . . . . . . . . . . . . . . 97
10.4 Single-Queue Scheduling . . . . . . . . . . . . . . . . . . . . 97
10.5 Multi-Queue Scheduling . . . . . . . . . . . . . . . . . . . . 99
10.6 Linux Multiprocessor Schedulers . . . . . . . . . . . . . . . 102
10.7 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 102
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 103
11 Summary Dialogue on CPU Virtualization 105
12 A Dialogue on Memory Virtualization 107
13 The Abstraction: Address Spaces 109
13.1 Early Systems . . . . . . . . . . . . . . . . . . . . . . . . . . 109
13.2 Multiprogramming and Time Sharing . . . . . . . . . . . . . 110
13.3 The Address Space . . . . . . . . . . . . . . . . . . . . . . . 111
13.4 Goals . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 113
13.5 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 115
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 116
14 Interlude: Memory API 119
14.1 Types of Memory . . . . . . . . . . . . . . . . . . . . . . . . 119
14.2 The malloc() Call . . . . . . . . . . . . . . . . . . . . . . . 120
14.3 The free() Call . . . . . . . . . . . . . . . . . . . . . . . . 122
14.4 Common Errors . . . . . . . . . . . . . . . . . . . . . . . . . 122
14.5 Underlying OS Support . . . . . . . . . . . . . . . . . . . . . 125
14.6 Other Calls . . . . . . . . . . . . . . . . . . . . . . . . . . . . 125
14.7 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 126
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127
15 Mechanism: Address T ranslation 129
15.1 Assumptions . . . . . . . . . . . . . . . . . . . . . . . . . . . 130
15.2 An Example . . . . . . . . . . . . . . . . . . . . . . . . . . . 130
15.3 Dynamic (Hardware-based) Relocation . . . . . . . . . . . . 133
15.4 OS Issues . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 136
15.5 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 137
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 139
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140
16 Segmentation 141
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 18

xiv CONTENTS
16.1 Segmentation: Generalized Base/Bounds . . . . . . . . . . 141
16.2 Which Segment Are We Referring To? . . . . . . . . . . . . . 144
16.3 What About The Stack? . . . . . . . . . . . . . . . . . . . . . 145
16.4 Support for Sharing . . . . . . . . . . . . . . . . . . . . . . . 146
16.5 Fine-grained vs. Coarse-grained Segmentation . . . . . . . 147
16.6 OS Support . . . . . . . . . . . . . . . . . . . . . . . . . . . . 147
16.7 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 149
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 150
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 152
17 Free-Space Management 153
17.1 Assumptions . . . . . . . . . . . . . . . . . . . . . . . . . . . 154
17.2 Low-level Mechanisms . . . . . . . . . . . . . . . . . . . . . 155
17.3 Basic Strategies . . . . . . . . . . . . . . . . . . . . . . . . . 163
17.4 Other Approaches . . . . . . . . . . . . . . . . . . . . . . . . 165
17.5 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 167
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 168
18 Paging: Introduction 169
18.1 Where Are Page Tables Stored? . . . . . . . . . . . . . . . . 172
18.2 What’s Actually In The Page Table? . . . . . . . . . . . . . . 173
18.3 Paging: Also Too Slow . . . . . . . . . . . . . . . . . . . . . 174
18.4 A Memory Trace . . . . . . . . . . . . . . . . . . . . . . . . . 176
18.5 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 179
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 180
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 181
19 Paging: Faster T ranslations (TLBs) 183
19.1 TLB Basic Algorithm . . . . . . . . . . . . . . . . . . . . . . 183
19.2 Example: Accessing An Array . . . . . . . . . . . . . . . . . 185
19.3 Who Handles The TLB Miss? . . . . . . . . . . . . . . . . . . 187
19.4 TLB Contents: What’s In There? . . . . . . . . . . . . . . . . 189
19.5 TLB Issue: Context Switches . . . . . . . . . . . . . . . . . . 190
19.6 Issue: Replacement Policy . . . . . . . . . . . . . . . . . . . 192
19.7 A Real TLB Entry . . . . . . . . . . . . . . . . . . . . . . . . 193
19.8 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 194
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 195
Homework (Measurement) . . . . . . . . . . . . . . . . . . . . . . 197
20 Paging: Smaller T ables 201
20.1 Simple Solution: Bigger Pages . . . . . . . . . . . . . . . . . 201
20.2 Hybrid Approach: Paging and Segments . . . . . . . . . . . 202
20.3 Multi-level Page Tables . . . . . . . . . . . . . . . . . . . . . 205
20.4 Inverted Page Tables . . . . . . . . . . . . . . . . . . . . . . 212
20.5 Swapping the Page Tables to Disk . . . . . . . . . . . . . . . 213
20.6 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 213
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 214
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 19

CONTENTS xv
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 215
21 Beyond Physical Memory: Mechanisms 217
21.1 Swap Space . . . . . . . . . . . . . . . . . . . . . . . . . . . . 218
21.2 The Present Bit . . . . . . . . . . . . . . . . . . . . . . . . . . 219
21.3 The Page Fault . . . . . . . . . . . . . . . . . . . . . . . . . . 220
21.4 What If Memory Is Full? . . . . . . . . . . . . . . . . . . . . 221
21.5 Page Fault Control Flow . . . . . . . . . . . . . . . . . . . . 222
21.6 When Replacements Really Occur . . . . . . . . . . . . . . . 223
21.7 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 224
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 225
22 Beyond Physical Memory: Policies 227
22.1 Cache Management . . . . . . . . . . . . . . . . . . . . . . . 227
22.2 The Optimal Replacement Policy . . . . . . . . . . . . . . . 228
22.3 A Simple Policy: FIFO . . . . . . . . . . . . . . . . . . . . . 230
22.4 Another Simple Policy: Random . . . . . . . . . . . . . . . . 232
22.5 Using History: LRU . . . . . . . . . . . . . . . . . . . . . . . 233
22.6 Workload Examples . . . . . . . . . . . . . . . . . . . . . . . 234
22.7 Implementing Historical Algorithms . . . . . . . . . . . . . 237
22.8 Approximating LRU . . . . . . . . . . . . . . . . . . . . . . 238
22.9 Considering Dirty Pages . . . . . . . . . . . . . . . . . . . . 239
22.10 Other VM Policies . . . . . . . . . . . . . . . . . . . . . . . . 240
22.11 Thrashing . . . . . . . . . . . . . . . . . . . . . . . . . . . . 240
22.12 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 241
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 242
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 244
23 The V AX/VMS Virtual Memory System 245
23.1 Background . . . . . . . . . . . . . . . . . . . . . . . . . . . 245
23.2 Memory Management Hardware . . . . . . . . . . . . . . . 246
23.3 A Real Address Space . . . . . . . . . . . . . . . . . . . . . . 247
23.4 Page Replacement . . . . . . . . . . . . . . . . . . . . . . . . 249
23.5 Other Neat VM Tricks . . . . . . . . . . . . . . . . . . . . . . 250
23.6 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 252
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 253
24 Summary Dialogue on Memory Virtualization 255
II Concurrency 259
25 A Dialogue on Concurrency 261
26 Concurrency: An Introduction 263
26.1 An Example: Thread Creation . . . . . . . . . . . . . . . . . 264
26.2 Why It Gets Worse: Shared Data . . . . . . . . . . . . . . . . 267
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 20

xvi CONTENTS
26.3 The Heart of the Problem: Uncontrolled Scheduling . . . . 269
26.4 The Wish For Atomicity . . . . . . . . . . . . . . . . . . . . . 271
26.5 One More Problem: Waiting For Another . . . . . . . . . . . 273
26.6 Summary: Why in OS Class? . . . . . . . . . . . . . . . . . . 273
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 275
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 276
27 Interlude: Thread API 279
27.1 Thread Creation . . . . . . . . . . . . . . . . . . . . . . . . . 279
27.2 Thread Completion . . . . . . . . . . . . . . . . . . . . . . . 280
27.3 Locks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 283
27.4 Condition Variables . . . . . . . . . . . . . . . . . . . . . . . 285
27.5 Compiling and Running . . . . . . . . . . . . . . . . . . . . 287
27.6 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 287
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 289
28 Locks 291
28.1 Locks: The Basic Idea . . . . . . . . . . . . . . . . . . . . . . 291
28.2 Pthread Locks . . . . . . . . . . . . . . . . . . . . . . . . . . 292
28.3 Building A Lock . . . . . . . . . . . . . . . . . . . . . . . . . 293
28.4 Evaluating Locks . . . . . . . . . . . . . . . . . . . . . . . . 293
28.5 Controlling Interrupts . . . . . . . . . . . . . . . . . . . . . . 294
28.6 Test And Set (Atomic Exchange) . . . . . . . . . . . . . . . . 295
28.7 Building A Working Spin Lock . . . . . . . . . . . . . . . . . 297
28.8 Evaluating Spin Locks . . . . . . . . . . . . . . . . . . . . . 299
28.9 Compare-And-Swap . . . . . . . . . . . . . . . . . . . . . . 299
28.10 Load-Linked and Store-Conditional . . . . . . . . . . . . . . 300
28.11 Fetch-And-Add . . . . . . . . . . . . . . . . . . . . . . . . . 302
28.12 Summary: So Much Spinning . . . . . . . . . . . . . . . . . 303
28.13 A Simple Approach: Just Yield, Baby . . . . . . . . . . . . . 304
28.14 Using Queues: Sleeping Instead Of Spinning . . . . . . . . . 305
28.15 Different OS, Different Support . . . . . . . . . . . . . . . . 307
28.16 Two-Phase Locks . . . . . . . . . . . . . . . . . . . . . . . . 307
28.17 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 308
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 309
29 Lock-based Concurrent Data Structures 311
29.1 Concurrent Counters . . . . . . . . . . . . . . . . . . . . . . 311
29.2 Concurrent Linked Lists . . . . . . . . . . . . . . . . . . . . 316
29.3 Concurrent Queues . . . . . . . . . . . . . . . . . . . . . . . 319
29.4 Concurrent Hash Table . . . . . . . . . . . . . . . . . . . . . 320
29.5 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 322
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 323
30 Condition V ariables 325
30.1 Deﬁnition and Routines . . . . . . . . . . . . . . . . . . . . . 326
30.2 The Producer/Consumer (Bound Buffer) Problem . . . . . . 329
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 21

CONTENTS xvii
30.3 Covering Conditions . . . . . . . . . . . . . . . . . . . . . . 337
30.4 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 338
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 339
31 Semaphores 341
31.1 Semaphores: A Deﬁnition . . . . . . . . . . . . . . . . . . . 341
31.2 Binary Semaphores (Locks) . . . . . . . . . . . . . . . . . . . 343
31.3 Semaphores As Condition Variables . . . . . . . . . . . . . . 344
31.4 The Producer/Consumer (Bounded-Buffer) Problem . . . . 346
31.5 Reader-Writer Locks . . . . . . . . . . . . . . . . . . . . . . 350
31.6 The Dining Philosophers . . . . . . . . . . . . . . . . . . . . 352
31.7 How To Implement Semaphores . . . . . . . . . . . . . . . . 355
31.8 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 356
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 357
32 Common Concurrency Problems 359
32.1 What Types Of Bugs Exist? . . . . . . . . . . . . . . . . . . . 359
32.2 Non-Deadlock Bugs . . . . . . . . . . . . . . . . . . . . . . . 360
32.3 Deadlock Bugs . . . . . . . . . . . . . . . . . . . . . . . . . . 363
32.4 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 370
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 371
33 Event-based Concurrency (Advanced) 373
33.1 The Basic Idea: An Event Loop . . . . . . . . . . . . . . . . . 373
33.2 An Important API: select() (or poll()) . . . . . . . . . 374
33.3 Using select() . . . . . . . . . . . . . . . . . . . . . . . . 375
33.4 Why Simpler? No Locks Needed . . . . . . . . . . . . . . . 376
33.5 A Problem: Blocking System Calls . . . . . . . . . . . . . . . 377
33.6 A Solution: Asynchronous I/O . . . . . . . . . . . . . . . . 377
33.7 Another Problem: State Management . . . . . . . . . . . . . 380
33.8 What Is Still Difﬁcult With Events . . . . . . . . . . . . . . . 381
33.9 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 381
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 382
34 Summary Dialogue on Concurrency 383
III Persistence 385
35 A Dialogue on Persistence 387
36 I/O Devices 389
36.1 System Architecture . . . . . . . . . . . . . . . . . . . . . . . 389
36.2 A Canonical Device . . . . . . . . . . . . . . . . . . . . . . . 390
36.3 The Canonical Protocol . . . . . . . . . . . . . . . . . . . . . 391
36.4 Lowering CPU Overhead With Interrupts . . . . . . . . . . 392
36.5 More Efﬁcient Data Movement With DMA . . . . . . . . . . 393
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 22

xviii CONTENTS
36.6 Methods Of Device Interaction . . . . . . . . . . . . . . . . . 394
36.7 Fitting Into The OS: The Device Driver . . . . . . . . . . . . 395
36.8 Case Study: A Simple IDE Disk Driver . . . . . . . . . . . . 396
36.9 Historical Notes . . . . . . . . . . . . . . . . . . . . . . . . . 399
36.10 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 399
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 400
37 Hard Disk Drives 403
37.1 The Interface . . . . . . . . . . . . . . . . . . . . . . . . . . . 403
37.2 Basic Geometry . . . . . . . . . . . . . . . . . . . . . . . . . 404
37.3 A Simple Disk Drive . . . . . . . . . . . . . . . . . . . . . . 404
37.4 I/O Time: Doing The Math . . . . . . . . . . . . . . . . . . . 408
37.5 Disk Scheduling . . . . . . . . . . . . . . . . . . . . . . . . . 412
37.6 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 416
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 417
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 418
38 Redundant Arrays of Inexpensive Disks (RAIDs) 421
38.1 Interface And RAID Internals . . . . . . . . . . . . . . . . . 422
38.2 Fault Model . . . . . . . . . . . . . . . . . . . . . . . . . . . 423
38.3 How To Evaluate A RAID . . . . . . . . . . . . . . . . . . . 423
38.4 RAID Level 0: Striping . . . . . . . . . . . . . . . . . . . . . 424
38.5 RAID Level 1: Mirroring . . . . . . . . . . . . . . . . . . . . 427
38.6 RAID Level 4: Saving Space With Parity . . . . . . . . . . . 430
38.7 RAID Level 5: Rotating Parity . . . . . . . . . . . . . . . . . 434
38.8 RAID Comparison: A Summary . . . . . . . . . . . . . . . . 435
38.9 Other Interesting RAID Issues . . . . . . . . . . . . . . . . . 436
38.10 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 436
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 437
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 439
39 Interlude: File and Directories 441
39.1 Files and Directories . . . . . . . . . . . . . . . . . . . . . . . 441
39.2 The File System Interface . . . . . . . . . . . . . . . . . . . . 443
39.3 Creating Files . . . . . . . . . . . . . . . . . . . . . . . . . . 443
39.4 Reading and Writing Files . . . . . . . . . . . . . . . . . . . 444
39.5 Reading And Writing, But Not Sequentially . . . . . . . . . 446
39.6 Writing Immediately with fsync() . . . . . . . . . . . . . 447
39.7 Renaming Files . . . . . . . . . . . . . . . . . . . . . . . . . 448
39.8 Getting Information About Files . . . . . . . . . . . . . . . . 449
39.9 Removing Files . . . . . . . . . . . . . . . . . . . . . . . . . 450
39.10 Making Directories . . . . . . . . . . . . . . . . . . . . . . . 450
39.11 Reading Directories . . . . . . . . . . . . . . . . . . . . . . . 451
39.12 Deleting Directories . . . . . . . . . . . . . . . . . . . . . . . 452
39.13 Hard Links . . . . . . . . . . . . . . . . . . . . . . . . . . . . 452
39.14 Symbolic Links . . . . . . . . . . . . . . . . . . . . . . . . . 454
39.15 Making and Mounting a File System . . . . . . . . . . . . . 456
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 23

CONTENTS xix
39.16 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 457
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 458
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 459
40 File System Implementation 461
40.1 The Way To Think . . . . . . . . . . . . . . . . . . . . . . . . 461
40.2 Overall Organization . . . . . . . . . . . . . . . . . . . . . . 462
40.3 File Organization: The Inode . . . . . . . . . . . . . . . . . . 464
40.4 Directory Organization . . . . . . . . . . . . . . . . . . . . . 469
40.5 Free Space Management . . . . . . . . . . . . . . . . . . . . 469
40.6 Access Paths: Reading and Writing . . . . . . . . . . . . . . 470
40.7 Caching and Buffering . . . . . . . . . . . . . . . . . . . . . 474
40.8 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 475
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 476
Homework . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 477
41 Locality and The Fast File System 479
41.1 The Problem: Poor Performance . . . . . . . . . . . . . . . . 479
41.2 FFS: Disk Awareness Is The Solution . . . . . . . . . . . . . 481
41.3 Organizing Structure: The Cylinder Group . . . . . . . . . . 481
41.4 Policies: How To Allocate Files and Directories . . . . . . . 482
41.5 Measuring File Locality . . . . . . . . . . . . . . . . . . . . . 483
41.6 The Large-File Exception . . . . . . . . . . . . . . . . . . . . 484
41.7 A Few Other Things About FFS . . . . . . . . . . . . . . . . 486
41.8 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 488
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 489
42 Crash Consistency: FSCK and Journaling 491
42.1 A Detailed Example . . . . . . . . . . . . . . . . . . . . . . . 492
42.2 Solution #1: The File System Checker . . . . . . . . . . . . . 495
42.3 Solution #2: Journaling (or Write-Ahead Logging) . . . . . . 497
42.4 Solution #3: Other Approaches . . . . . . . . . . . . . . . . 507
42.5 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 508
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 509
43 Log-structured File Systems 511
43.1 Writing To Disk Sequentially . . . . . . . . . . . . . . . . . . 512
43.2 Writing Sequentially And Effectively . . . . . . . . . . . . . 513
43.3 How Much To Buffer? . . . . . . . . . . . . . . . . . . . . . . 514
43.4 Problem: Finding Inodes . . . . . . . . . . . . . . . . . . . . 515
43.5 Solution Through Indirection: The Inode Map . . . . . . . . 515
43.6 The Checkpoint Region . . . . . . . . . . . . . . . . . . . . . 516
43.7 Reading A File From Disk: A Recap . . . . . . . . . . . . . . 517
43.8 What About Directories? . . . . . . . . . . . . . . . . . . . . 517
43.9 A New Problem: Garbage Collection . . . . . . . . . . . . . 518
43.10 Determining Block Liveness . . . . . . . . . . . . . . . . . . 520
43.11 A Policy Question: Which Blocks To Clean, And When? . . 521
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 24

xx CONTENTS
43.12 Crash Recovery And The Log . . . . . . . . . . . . . . . . . 521
43.13 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 522
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 524
44 Data Integrity and Protection 527
44.1 Disk Failure Modes . . . . . . . . . . . . . . . . . . . . . . . 527
44.2 Handling Latent Sector Errors . . . . . . . . . . . . . . . . . 529
44.3 Detecting Corruption: The Checksum . . . . . . . . . . . . . 530
44.4 Using Checksums . . . . . . . . . . . . . . . . . . . . . . . . 533
44.5 A New Problem: Misdirected Writes . . . . . . . . . . . . . 534
44.6 One Last Problem: Lost Writes . . . . . . . . . . . . . . . . . 535
44.7 Scrubbing . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 535
44.8 Overheads Of Checksumming . . . . . . . . . . . . . . . . . 536
44.9 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 536
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 537
45 Summary Dialogue on Persistence 539
46 A Dialogue on Distribution 541
47 Distributed Systems 543
47.1 Communication Basics . . . . . . . . . . . . . . . . . . . . . 544
47.2 Unreliable Communication Layers . . . . . . . . . . . . . . 545
47.3 Reliable Communication Layers . . . . . . . . . . . . . . . . 547
47.4 Communication Abstractions . . . . . . . . . . . . . . . . . 549
47.5 Remote Procedure Call (RPC) . . . . . . . . . . . . . . . . . 551
47.6 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 556
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 557
48 Sun’s Network File System (NFS) 559
48.1 A Basic Distributed File System . . . . . . . . . . . . . . . . 560
48.2 On To NFS . . . . . . . . . . . . . . . . . . . . . . . . . . . . 561
48.3 Focus: Simple and Fast Server Crash Recovery . . . . . . . . 561
48.4 Key To Fast Crash Recovery: Statelessness . . . . . . . . . . 562
48.5 The NFSv2 Protocol . . . . . . . . . . . . . . . . . . . . . . . 563
48.6 From Protocol to Distributed File System . . . . . . . . . . . 565
48.7 Handling Server Failure with Idempotent Operations . . . . 567
48.8 Improving Performance: Client-side Caching . . . . . . . . 569
48.9 The Cache Consistency Problem . . . . . . . . . . . . . . . . 569
48.10 Assessing NFS Cache Consistency . . . . . . . . . . . . . . . 571
48.11 Implications on Server-Side Write Buffering . . . . . . . . . 571
48.12 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 573
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 574
49 The Andrew File System (AFS) 575
49.1 AFS V ersion 1 . . . . . . . . . . . . . . . . . . . . . . . . . . 575
49.2 Problems with V ersion 1 . . . . . . . . . . . . . . . . . . . . 576
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 25

CONTENTS xxi
49.3 Improving the Protocol . . . . . . . . . . . . . . . . . . . . . 578
49.4 AFS V ersion 2 . . . . . . . . . . . . . . . . . . . . . . . . . . 578
49.5 Cache Consistency . . . . . . . . . . . . . . . . . . . . . . . 580
49.6 Crash Recovery . . . . . . . . . . . . . . . . . . . . . . . . . 582
49.7 Scale And Performance Of AFSv2 . . . . . . . . . . . . . . . 582
49.8 AFS: Other Improvements . . . . . . . . . . . . . . . . . . . 584
49.9 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 585
References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 587
50 Summary Dialogue on Distribution 589
General Index 591
Asides 601
Tips 603
Cruces 605
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 27

List of Figures
2.1 Simple Example: Code That Loops and Prints . . . . . . . . . 5
2.2 Running Many Programs At Once . . . . . . . . . . . . . . . . 6
2.3 A Program that Accesses Memory . . . . . . . . . . . . . . . . 7
2.4 Running The Memory Program Multiple Times . . . . . . . . 8
2.5 A Multi-threaded Program . . . . . . . . . . . . . . . . . . . . 9
2.6 A Program That Does I/O . . . . . . . . . . . . . . . . . . . . . 11
4.1 Loading: From Program T o Process . . . . . . . . . . . . . . . . 28
4.2 Process: State T ransitions . . . . . . . . . . . . . . . . . . . . . 30
4.3 The xv6 Proc Structure . . . . . . . . . . . . . . . . . . . . . . . 31
5.1 p1.c: Calling fork() . . . . . . . . . . . . . . . . . . . . . . . 36
5.2 p2.c: Calling fork() And wait() . . . . . . . . . . . . . . . 37
5.3 p3.c: Calling fork(), wait(), And exec() . . . . . . . . . 39
5.4 p4.c: All Of The Above With Redirection . . . . . . . . . . . 41
6.1 The xv6 Context Switch Code . . . . . . . . . . . . . . . . . . . 54
7.1 FIFO Simple Example . . . . . . . . . . . . . . . . . . . . . . . 61
7.2 Why FIFO Is Not That Great . . . . . . . . . . . . . . . . . . . 61
7.3 SJF Simple Example . . . . . . . . . . . . . . . . . . . . . . . . 62
7.4 SJF With Late Arrivals From B and C . . . . . . . . . . . . . . . 63
7.5 STCF Simple Example . . . . . . . . . . . . . . . . . . . . . . . 64
7.6 SJF Again (Bad for Response Time) . . . . . . . . . . . . . . . 65
7.7 Round Robin (Good for Response Time) . . . . . . . . . . . . 65
7.8 Poor Use of Resources . . . . . . . . . . . . . . . . . . . . . . . 67
7.9 Overlap Allows Better Use of Resources . . . . . . . . . . . . . 67
8.1 MLFQ Example . . . . . . . . . . . . . . . . . . . . . . . . . . . 73
8.2 Long-running Job Over Time . . . . . . . . . . . . . . . . . . . 74
8.3 Along Came An Interactive Job . . . . . . . . . . . . . . . . . . 74
8.4 A Mixed I/O-intensive and CPU-intensive Workload . . . . . 75
8.5 Without (Left) and With (Right) Priority Boost . . . . . . . . . 76
xxiii

## Page 28

xxiv LIST OF FIGURES
8.6 Without (Left) and With (Right) Gaming T olerance . . . . . . 77
8.7 Lower Priority, Longer Quanta . . . . . . . . . . . . . . . . . . 78
9.1 Lottery Scheduling Decision Code . . . . . . . . . . . . . . . . 86
9.2 Lottery Fairness Study . . . . . . . . . . . . . . . . . . . . . . . 87
10.1 Single CPU With Cache . . . . . . . . . . . . . . . . . . . . . . 94
10.2 Two CPUs With Caches Sharing Memory . . . . . . . . . . . . 95
10.3 Simple List Delete Code . . . . . . . . . . . . . . . . . . . . . . 97
13.1 Operating Systems: The Early Days . . . . . . . . . . . . . . . 109
13.2 Three Processes: Sharing Memory . . . . . . . . . . . . . . . . 110
13.3 An Example Address Space . . . . . . . . . . . . . . . . . . . . 111
15.1 A Process And Its Address Space . . . . . . . . . . . . . . . . . 132
15.2 Physical Memory with a Single Relocated Process . . . . . . . 133
16.1 An Address Space (Again) . . . . . . . . . . . . . . . . . . . . . 142
16.2 Placing Segments In Physical Memory . . . . . . . . . . . . . 143
16.3 Non-compacted and Compacted Memory . . . . . . . . . . . . 148
17.1 An Allocated Region Plus Header . . . . . . . . . . . . . . . . 157
17.2 Speciﬁc Contents Of The Header . . . . . . . . . . . . . . . . . 157
17.3 A Heap With One Free Chunk . . . . . . . . . . . . . . . . . . 159
17.4 A Heap: After One Allocation . . . . . . . . . . . . . . . . . . . 159
17.5 Free Space With Three Chunks Allocated . . . . . . . . . . . . 160
17.6 Free Space With Two Chunks Allocated . . . . . . . . . . . . . 161
17.7 A Non-Coalesced Free List . . . . . . . . . . . . . . . . . . . . . 162
18.1 A Simple 64-byte Address Space . . . . . . . . . . . . . . . . . 169
18.2 64-Byte Address Space Placed In Physical Memory . . . . . . 170
18.3 The Address T ranslation Process . . . . . . . . . . . . . . . . . 172
18.4 Example: Page T able in Kernel Physical Memory . . . . . . . 173
18.5 An x86 Page T able Entry (PTE) . . . . . . . . . . . . . . . . . . 174
18.6 Accessing Memory With Paging . . . . . . . . . . . . . . . . . 175
18.7 A Virtual (And Physical) Memory T race . . . . . . . . . . . . . 178
19.1 TLB Control Flow Algorithm . . . . . . . . . . . . . . . . . . . 184
19.2 Example: An Array In A Tiny Address Space . . . . . . . . . . 185
19.3 TLB Control Flow Algorithm (OS Handled) . . . . . . . . . . 188
19.4 A MIPS TLB Entry . . . . . . . . . . . . . . . . . . . . . . . . . 193
19.5 Discovering TLB Sizes and Miss Costs . . . . . . . . . . . . . 198
20.1 A 16-KB Address Space With 1-KB Pages . . . . . . . . . . . . 203
20.2 Linear (Left) And Multi-Level (Right) Page T ables . . . . . . . 206
20.3 A 16-KB Address Space With 64-byte Pages . . . . . . . . . . . 207
20.4 Multi-level Page T able Control Flow . . . . . . . . . . . . . . . 212
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 29

LIST OF FIGURES xxv
21.1 Physical Memory and Swap Space . . . . . . . . . . . . . . . . 219
21.2 Page-Fault Control Flow Algorithm (Hardware) . . . . . . . . 222
21.3 Page-Fault Control Flow Algorithm (Software) . . . . . . . . . 223
22.1 Random Performance over 10,000 T rials . . . . . . . . . . . . . 232
22.2 The No-Locality Workload . . . . . . . . . . . . . . . . . . . . . 235
22.3 The 80-20 Workload . . . . . . . . . . . . . . . . . . . . . . . . . 236
22.4 The Looping Workload . . . . . . . . . . . . . . . . . . . . . . . 237
22.5 The 80-20 Workload With Clock . . . . . . . . . . . . . . . . . 239
23.1 The V AX/VMS Address Space . . . . . . . . . . . . . . . . . . 247
26.1 A Single-Threaded Address Space . . . . . . . . . . . . . . . . 264
26.2 Simple Thread Creation Code (t0.c) . . . . . . . . . . . . . . . 265
26.3 Sharing Data: Oh Oh (t2) . . . . . . . . . . . . . . . . . . . . . 267
27.1 Creating a Thread . . . . . . . . . . . . . . . . . . . . . . . . . . 281
27.2 Waiting for Thread Completion . . . . . . . . . . . . . . . . . . 282
27.3 Simpler Argument Passing to a Thread . . . . . . . . . . . . . 283
27.4 An Example Wrapper . . . . . . . . . . . . . . . . . . . . . . . . 285
28.1 First Attempt: A Simple Flag . . . . . . . . . . . . . . . . . . . 296
28.2 A Simple Spin Lock Using T est-and-set . . . . . . . . . . . . . 298
28.3 Compare-and-swap . . . . . . . . . . . . . . . . . . . . . . . . . 299
28.4 Load-linked And Store-conditional . . . . . . . . . . . . . . . 301
28.5 Using LL/SC T o Build A Lock . . . . . . . . . . . . . . . . . . . 301
28.6 Ticket Locks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 303
28.7 Lock With T est-and-set And Yield . . . . . . . . . . . . . . . . 304
28.8 Lock With Queues, T est-and-set, Yield, And Wakeup . . . . . 306
28.9 Linux-based Futex Locks . . . . . . . . . . . . . . . . . . . . . . 308
29.1 A Counter Without Locks . . . . . . . . . . . . . . . . . . . . . 312
29.2 A Counter With Locks . . . . . . . . . . . . . . . . . . . . . . . 312
29.3 Performance of T raditional vs. Sloppy Counters . . . . . . . . 313
29.4 Sloppy Counter Implementation . . . . . . . . . . . . . . . . . 315
29.5 Scaling Sloppy Counters . . . . . . . . . . . . . . . . . . . . . . 316
29.6 Concurrent Linked List . . . . . . . . . . . . . . . . . . . . . . 317
29.7 Concurrent Linked List: Rewritten . . . . . . . . . . . . . . . . 318
29.8 Michael and Scott Concurrent Queue . . . . . . . . . . . . . . 320
29.9 A Concurrent Hash T able . . . . . . . . . . . . . . . . . . . . . 321
29.10 Scaling Hash T ables . . . . . . . . . . . . . . . . . . . . . . . . 321
30.1 A Parent Waiting For Its Child . . . . . . . . . . . . . . . . . . 325
30.2 Parent Waiting For Child: Spin-based Approach . . . . . . . . 326
30.3 Parent Waiting For Child: Use A Condition V ariable . . . . . 327
30.4 The Put and Get Routines (V ersion 1) . . . . . . . . . . . . . . 330
30.5 Producer/Consumer Threads (V ersion 1) . . . . . . . . . . . . 330
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 30

xxvi LIST OF FIGURES
30.6 Producer/Consumer: Single CV and If Statement . . . . . . . 331
30.7 Producer/Consumer: Single CV and While . . . . . . . . . . . 333
30.8 Producer/Consumer: Two CVs and While . . . . . . . . . . . . 335
30.9 The Final Put and Get Routines . . . . . . . . . . . . . . . . . . 336
30.10 The Final Working Solution . . . . . . . . . . . . . . . . . . . . 336
30.11 Covering Conditions: An Example . . . . . . . . . . . . . . . . 338
31.1 Initializing A Semaphore . . . . . . . . . . . . . . . . . . . . . 342
31.2 Semaphore: Deﬁnitions of Wait and Post . . . . . . . . . . . . 342
31.3 A Binary Semaphore, a.k.a. a Lock . . . . . . . . . . . . . . . . 343
31.4 A Parent Waiting For Its Child . . . . . . . . . . . . . . . . . . 345
31.5 The Put and Get Routines . . . . . . . . . . . . . . . . . . . . . 347
31.6 Adding the Full and Empty Conditions . . . . . . . . . . . . . 347
31.7 Adding Mutual Exclusion (Incorrectly) . . . . . . . . . . . . . 349
31.8 Adding Mutual Exclusion (Correctly) . . . . . . . . . . . . . . 350
31.9 A Simple Reader-Writer Lock . . . . . . . . . . . . . . . . . . . 351
31.10 The Dining Philosophers . . . . . . . . . . . . . . . . . . . . . 353
31.11 The getforks() and putforks() Routines . . . . . . . . . 354
31.12 Implementing Zemaphores with Locks and CVs . . . . . . . . 355
32.1 The Deadlock Dependency Graph . . . . . . . . . . . . . . . . 364
33.1 Simple Code using select() . . . . . . . . . . . . . . . . . . 376
36.1 Prototypical System Architecture . . . . . . . . . . . . . . . . . 390
36.2 A Canonical Device . . . . . . . . . . . . . . . . . . . . . . . . . 391
36.3 The File System Stack . . . . . . . . . . . . . . . . . . . . . . . 396
36.4 The IDE Interface . . . . . . . . . . . . . . . . . . . . . . . . . . 397
36.5 The xv6 IDE Disk Driver (Simpliﬁed) . . . . . . . . . . . . . . 398
37.1 A Disk With Just A Single T rack . . . . . . . . . . . . . . . . . 404
37.2 A Single T rack Plus A Head . . . . . . . . . . . . . . . . . . . . 405
37.3 Three T racks Plus A Head (Right: With Seek) . . . . . . . . . 406
37.4 Three T racks: T rack Skew Of 2 . . . . . . . . . . . . . . . . . . 407
37.5 SSTF: Scheduling Requests 21 And 2 . . . . . . . . . . . . . . 412
37.6 SSTF: Sometimes Not Good Enough . . . . . . . . . . . . . . . 414
39.1 An Example Directory T ree . . . . . . . . . . . . . . . . . . . . 442
41.1 FFS Locality For SEER T races . . . . . . . . . . . . . . . . . . . 483
41.2 Amortization: How Big Do Chunks Have T o Be? . . . . . . . . 486
41.3 FFS: Standard V ersus Parameterized Placement . . . . . . . . 487
47.1 Example UDP/IP Client/Server Code . . . . . . . . . . . . . . . 545
47.2 A Simple UDP Library . . . . . . . . . . . . . . . . . . . . . . . 546
47.3 Message Plus Acknowledgment . . . . . . . . . . . . . . . . . 547
47.4 Message Plus Acknowledgment: Dropped Request . . . . . . 548
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 31

LIST OF FIGURES xxvii
47.5 Message Plus Acknowledgment: Dropped Reply . . . . . . . 549
48.1 A Generic Client/Server System . . . . . . . . . . . . . . . . . 559
48.2 Distributed File System Architecture . . . . . . . . . . . . . . 560
48.3 Client Code: Reading From A File . . . . . . . . . . . . . . . . 562
48.4 The NFS Protocol: Examples . . . . . . . . . . . . . . . . . . . 564
48.5 The Three Types of Loss . . . . . . . . . . . . . . . . . . . . . . 568
48.6 The Cache Consistency Problem . . . . . . . . . . . . . . . . . 570
49.1 AFSv1 Protocol Highlights . . . . . . . . . . . . . . . . . . . . 576
c⃝ 2014, A RPACI -D USSEAU
THREE
EASY
PIECES

## Page 33

List of Tables
6.1 Direction Execution Protocol (Without Limits) . . . . . . . . . 46
6.2 Limited Direction Execution Protocol . . . . . . . . . . . . . . 49
6.3 Limited Direction Execution Protocol (Timer Interrupt) . . . . 53
9.1 Stride Scheduling: A T race . . . . . . . . . . . . . . . . . . . . 89
16.1 Segment Register V alues . . . . . . . . . . . . . . . . . . . . . . 143
16.2 Segment Registers (With Negative-Growth Support) . . . . . 146
16.3 Segment Register V alues (with Protection) . . . . . . . . . . . 147
20.1 A Page T able For 16-KB Address Space . . . . . . . . . . . . . 203
20.2 A Page Directory, And Pieces Of Page T able . . . . . . . . . . 209
22.1 T racing the Optimal Policy . . . . . . . . . . . . . . . . . . . . 229
22.2 T racing the FIFO Policy . . . . . . . . . . . . . . . . . . . . . . 231
22.3 T racing the Random Policy . . . . . . . . . . . . . . . . . . . . 232
22.4 T racing the LRU Policy . . . . . . . . . . . . . . . . . . . . . . . 233
26.1 Thread T race (1) . . . . . . . . . . . . . . . . . . . . . . . . . . . 266
26.2 Thread T race (2) . . . . . . . . . . . . . . . . . . . . . . . . . . . 266
26.3 Thread T race (3) . . . . . . . . . . . . . . . . . . . . . . . . . . . 266
26.4 The Problem: Up Close and Personal . . . . . . . . . . . . . . 270
28.1 T race: No Mutual Exclusion . . . . . . . . . . . . . . . . . . . . 296
29.1 T racing the Sloppy Counters . . . . . . . . . . . . . . . . . . . 314
30.1 Thread T race: Broken Solution (V ersion 1) . . . . . . . . . . . 332
30.2 Thread T race: Broken Solution (V ersion 2) . . . . . . . . . . . 334
31.1 Thread T race: Single Thread Using A Semaphore . . . . . . . 343
31.2 Thread T race: Two Threads Using A Semaphore . . . . . . . . 344
31.3 Thread T race: Parent Waiting For Child (Case 1) . . . . . . . . 346
xxix

## Page 34

xxx LIST OF TABLES
31.4 Thread T race: Parent Waiting For Child (Case 2) . . . . . . . . 346
32.1 Bugs In Modern Applications . . . . . . . . . . . . . . . . . . . 360
37.1 Disk Drive Specs: SCSI V ersus SA TA . . . . . . . . . . . . . . 409
37.2 Disk Drive Performance: SCSI V ersus SA TA . . . . . . . . . . 410
38.1 RAID-0: Simple Striping . . . . . . . . . . . . . . . . . . . . . 424
38.2 Striping with a Bigger Chunk Size . . . . . . . . . . . . . . . . 424
38.3 Simple RAID-1: Mirroring . . . . . . . . . . . . . . . . . . . . 428
38.4 Full-stripe Writes In RAID-4 . . . . . . . . . . . . . . . . . . . 432
38.5 Example: Writes T o 4, 13, And Respective Parity Blocks . . . . 433
38.6 RAID-5 With Rotated Parity . . . . . . . . . . . . . . . . . . . . 434
38.7 RAID Capacity, Reliability, and Performance . . . . . . . . . . 435
40.1 The ext2 inode . . . . . . . . . . . . . . . . . . . . . . . . . . . . 466
40.2 File System Measurement Summary . . . . . . . . . . . . . . . 468
40.3 File Read Timeline (Time Increasing Downward) . . . . . . . 471
40.4 File Creation Timeline (Time Increasing Downward) . . . . . 473
42.1 Data Journaling Timeline . . . . . . . . . . . . . . . . . . . . . 506
42.2 Metadata Journaling Timeline . . . . . . . . . . . . . . . . . . 507
44.1 Frequency of LSEs and Block Corruption . . . . . . . . . . . . 528
48.1 Reading A File: Client-side And File Server Actions . . . . . 566
49.1 Reading A File: Client-side And File Server Actions . . . . . 579
49.2 Cache Consistency Timeline . . . . . . . . . . . . . . . . . . . 581
49.3 Comparison: AFS vs. NFS . . . . . . . . . . . . . . . . . . . . . 583
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 37

1
A Dialogue on the Book
Professor: Welcome to this book! It’s called Operating Systems in Three Easy
Pieces, and I am here to teach you the things you need to know about ope rating
systems. I am called “Professor”; who are you?
Student: Hi Professor! I am called “Student”, as you might have guesse d. And
I am here and ready to learn!
Professor: Sounds good. Any questions?
Student: Sure! Why is it called “Three Easy Pieces”?
Professor: That’s an easy one. Well, you see, there are these great lectu res on
Physics by Richard Feynman...
Student: Oh! The guy who wrote “Surely Y ou’re Joking, Mr. Feynman”, ri ght?
Great book! Is this going to be hilarious like that book was?
Professor: Um... well, no. That book was great, and I’m glad you’ve read i t.
Hopefully this book is more like his notes on Physics. Some of the basics were
summed up in a book called “Six Easy Pieces”. He was talking ab out Physics;
we’re going to do Three Easy Pieces on the ﬁne topic of Operati ng Systems. This
is appropriate, as Operating Systems are about half as hard a s Physics.
Student: Well, I liked physics, so that is probably good. What are thos e pieces?
Professor: They are the three key ideas we’re going to learn about: virtualiza-
tion, concurrency, and persistence. In learning about these ideas, we’ll learn
all about how an operating system works, including how it decides what program
to run next on a CPU, how it handles memory overload in a virtua l memory sys-
tem, how virtual machine monitors work, how to manage inform ation on disks,
and even a little about how to build a distributed system that works when parts
have failed. That sort of stuff.
Student: I have no idea what you’re talking about, really.
Professor: Good! That means you are in the right class.
Student: I have another question: what’s the best way to learn this stu ff?
Professor: Excellent query! Well, each person needs to ﬁgure this out on their
1

## Page 38

2 A D IALOGUE ON THE BOOK
own, of course, but here is what I would do: go to class, to hear the professor
introduce the material. Then, say at the end of every week, re ad these notes,
to help the ideas sink into your head a bit better. Of course, s ome time later
(hint: before the exam!), read the notes again to ﬁrm up your k nowledge. Of
course, your professor will no doubt assign some homeworks a nd projects, so you
should do those; in particular, doing projects where you wri te real code to solve
real problems is the best way to put the ideas within these not es into action. As
Confucius said...
Student: Oh, I know! ’I hear and I forget. I see and I remember. I do and I
understand.’ Or something like that.
Professor: (surprised) How did you know what I was going to say?!
Student: It seemed to follow. Also, I am a big fan of Confucius.
Professor: Well, I think we are going to get along just ﬁne! Just ﬁne indee d.
Student: Professor – just one more question, if I may. What are these di alogues
for? I mean, isn’t this just supposed to be a book? Why not pres ent the material
directly?
Professor: Ah, good question, good question! Well, I think it is sometim es
useful to pull yourself outside of a narrative and think a bit ; these dialogues are
those times. So you and I are going to work together to make sen se of all of these
pretty complex ideas. Are you up for it?
Student: So we have to think? Well, I’m up for that. I mean, what else do I have
to do anyhow? It’s not like I have much of a life outside of this book.
Professor: Me neither, sadly. So let’s get to work!
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

## Page 39

2
Introduction to Operating Systems
If you are taking an undergraduate operating systems course , you should
already have some idea of what a computer program does when it runs.
If not, this book (and the corresponding course) is going to b e difﬁcult
– so you should probably stop reading this book, or run to the n earest
bookstore and quickly consume the necessary background mat erial be-
fore continuing (both Patt/Patel [PP03] and particularly Bryant/O’Hallaron
[BOH10] are pretty great books).
So what happens when a program runs?
Well, a running program does one very simple thing: it execut es in-
structions. Many millions (and these days, even billions) o f times ev-
ery second, the processor fetches an instruction from memory , decodes
it (i.e., ﬁgures out which instruction this is), and executes it (i.e., it does
the thing that it is supposed to do, like add two numbers toget her, access
memory , check a condition, jump to a function, and so forth). After it is
done with this instruction, the processor moves on to the next instruction,
and so on, and so on, until the program ﬁnally completes 1.
Thus, we have just described the basics of the V on Neumannmodel of
computing2. Sounds simple, right? But in this class, we will be learning
that while a program runs, a lot of other wild things are going on with
the primary goal of making the system easy to use.
There is a body of software, in fact, that is responsible for m aking it
easy to run programs (even allowing you to seemingly run many at the
same time), allowing programs to share memory , enabling pro grams to
interact with devices, and other fun stuff like that. That bo dy of software
1Of course, modern processors do many bizarre and frightenin g things underneath the
hood to make programs run faster, e.g., executing multiple i nstructions at once, and even issu-
ing and completing them out of order! But that is not our conce rn here; we are just concerned
with the simple model most programs assume: that instructio ns seemingly execute one at a
time, in an orderly and sequential fashion.
2V on Neumann was one of the early pioneers of computing systems. He also did pioneer-
ing work on game theory and atomic bombs, and played in the NBA for six years. OK, one of
those things isn’t true.
3

## Page 40

4 INTRODUCTION TO OPERATING SYSTEMS
THE CRUX OF THE PROBLEM :
HOW TO VIRTUALIZE RESOURCES
One central question we will answer in this book is quite simp le: how
does the operating system virtualize resources? This is the crux of our
problem. Why the OS does this is not the main question, as the answer
should be obvious: it makes the system easier to use. Thus, we focus on
the how: what mechanisms and policies are implemented by the OS to
attain virtualization? How does the OS do so efﬁciently? Wha t hardware
support is needed?
We will use the “crux of the problem”, in shaded boxes such as t his one,
as a way to call out speciﬁc problems we are trying to solve in b uilding
an operating system. Thus, within a note on a particular topi c, you may
ﬁnd one or more cruces (yes, this is the proper plural) which highlight the
problem. The details within the chapter, of course, present the solution,
or at least the basic parameters of a solution.
is called the operating system (OS)3, as it is in charge of making sure the
system operates correctly and efﬁciently in an easy-to-use manner.
The primary way the OS does this is through a general techniqu e that
we call virtualization. That is, the OS takes a physical resource (such as
the processor, or memory , or a disk) and transforms it into a m ore gen-
eral, powerful, and easy-to-use virtual form of itself. Thus, we sometimes
refer to the operating system as a virtual machine.
Of course, in order to allow users to tell the OS what to do and t hus
make use of the features of the virtual machine (such as runni ng a pro-
gram, or allocating memory , or accessing a ﬁle), the OS also p rovides
some interfaces (APIs) that you can call. A typical OS, in fac t, exports
a few hundred system calls that are available to applications. Because
the OS provides these calls to run programs, access memory an d devices,
and other related actions, we also sometimes say that the OS p rovides a
standard library to applications.
Finally , because virtualization allows many programs to run (thus shar-
ing the CPU), and many programs to concurrently access their own in-
structions and data (thus sharing memory), and many programs to access
devices (thus sharing disks and so forth), the OS is sometime s known as
a resource manager . Each of the CPU, memory , and disk is a resource
of the system; it is thus the operating system’s role to manage those re-
sources, doing so efﬁciently or fairly or indeed with many ot her possible
goals in mind. To understand the role of the OS a little bit bet ter, let’s take
a look at some examples.
3Another early name for the OS was the supervisor or even the master control program .
Apparently , the latter sounded a little overzealous (see th e movie Tron for details) and thus,
thankfully , “operating system” caught on instead.
OPERATING
SYSTEMS
[V ERSION 0.80] WWW.OSTEP .ORG

