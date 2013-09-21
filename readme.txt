So you have decided to look at SalStat then? To be fair, I am not a
programmer, I am a psychologist and my skills should show in the quality of
code (get this, I am being sarcastic about myself!), but one thing I do have
is an "itch" to develop a better statistics package.

I teach psychology undergrads "computing and statistics" with SPSS and
StatView. Both are okay programs, but whenever I teach people this stuff, it
always strikes me that things are harder than they should be, especially for
people who only need to get a simple result.

I am also aware that there are no really good stats packages with good
intuitive GUIs available that the user can mess around with.

These are my reasons for SalStat. I know my code is not the best or tightest
around, but it does work (after a fashion!), and I intend this program to be
the best of its kind. At the very least, I hope free/libre competition will
encourage the commercial people to pull their socks up in the interface
department, which can only benefit consumers.

Currently, SalStat is in Beta - to me this means that it can do a few things,
but is not what anyone would call a finished package. Through using
Python (and wxPython), it is unlikely to crash (although it is possible)
because of memory errors, but nothing is perfect.

And the architecture: Forgive me for my ignorance, but the way I have
structured it is as follows:

**salstat.py - this is the main file which contains all the GUI elements and
controls just about everything. It's a bit monolithic, but it works well.
**salstat_stats.py - this module has taken most of its code from Gary Strangmans
own stats.py module. This version is object orientated and custom made for
SalStat and is faster for its purpose than the original.
**images.py - this simply contains 'pythonic' representations of the icons
**wxChart.py - a beginning module for drawing charts in wxPython. It is in its
very early days, so don't expect too much, but code changes are more than 
welcome!

Hopefully, some bright person will be able to program multi-factorial anova
with easy access to simple effects for me (I really do not have the skills!)

If you want to help with this project, then contact me at
salstat@sunsite.dk. There are lots of things that need doing, though
curiously, documentation seems to be okay for an open source project (I like
writing!). Skills needed are Python, and statistics, preferably both.
Statisticians who are willing to write tests are more than welcome, and even
if you don't know Python (it is quite easy to learn), let me know and I'll try
and sort out a way to marry your knowledge with someone elses programming
skills.

Please don't flame me - I have filters for stuff like "suxxx" and "dude".

INSTALLATION (Windows):

The Windows executable installs like any other application. Download it and
run the executable to install it. You will be given options like having a
desktop icon, a menu entry, links to the web pages and so on. The Python 
source code is also included.

INSTALLATION (Linux executable):

This is in some ways more complex, but in other ways easier. Unpack the archive
('gunzip salstat*' then 'tar -xvf salstat*') and everything will open into a 
directory called salstat. If you wish, you can place the directory in /usr/share or
somewhere in your home directory. The file called (simply) 'salstat' is the 
executable, but you may wish to write a short bash script to call the main 
executable. There is also an icon file which can be used for KDE or
Gnome shortcuts if required. The Python source code is also included.

INSTALLATION - Linux/Unix and Windows (source code):

Open the archive using tar/gunzip for packages ending in tar.gz, or something
like WinZip for zip archives. There should be a core of files which you need
to put somewhere. As you have wxPython installed, I recommend going to the
wxPython directory, and putting them into a directory somewhere. Open a
console/DOS box, and change to that directory. Then (assuming Python and
wxPython has installed properly), run "python salstat.py".

INSTALLATION - Mac OSX:

Thanks to Ludger Humbert who has OSX and tried the following:

at first anyone who wants to install it has to
install a X-Server on the Mac OS X

I recommend installing all the software with fink, it's available via
http://fink.sourceforge.net/

The second was taken while running Orobor. One can get it on
http://wrench.et.ic.ac.uk/adrian/software/oroborosx/

This Window-Manager integrates with look and feel very fine into
the native Mac OS X -- Aqua Windowmanager


**WARNING** - this is beta software - DO NOT RELY UPON THIS FOR RESEARCH -
there is a lot of testing to do before its accuracy can be verified, so the
results that come out of this may not be any good at all. 

It may crash and ruin your data, trash your hard disk, kill you, burn your
house down, run off with your life partner, and end the world as we know it.
Well, you never know ;), so MAKE BACKUPS BEFORE USING IT!

Alan James Salmoni
HCI Group
Cardiff University
Wales, UK.
salmonia@cardiff.ac.uk