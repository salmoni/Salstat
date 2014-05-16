# Salstat 

## DESCRIPTION

Salstat is open source statistics software. Think of something like SPSS or SAS but with a friendlier interface. 

I last worked on this 10 years only to find that people are *still* using it. I'm surprised at its longevity and am devoting my spare time to making it the best of its kind. There's a way to go yet but it is coming along well. 


## INSTALLATION:

You have two options for installation. 

1. Buying an installable. We have to charge for these because it takes us a lot of time to prepare them. They don't cost much and all money goes towards Salstat development. It also includes some technical support.
2. Source code (the source is open source and free). This will probably take a bit of work but will cost you time.

We only have installables for Windows and OS X (64-bit).

1. BUYING AN INSTALLABLE

We offer installables for Windows and OS X that contain everything you need. They install like a regular software program and save lots of time. You can get them from http://www.salstat.com. 

To save your time, we have to work hard so we charge a small amount for the installables which goes straight back into Salstat development. 

2. INSTALLING SOURCE CODE

Salstat runs using a computer language called Python. This costs nothing to download and install. It also uses a number of libraries, all of which cost nothing to download and install. It will probably, however, take time to get your computer ready. 

First download and install Python. If possible, use a 64-bit version. 
Then download and install setuptools or pip and then install these libraries. I've included the versions used on my machine. I will not guarantee that they work but they do on mine. 

wxPython		(version 2.9.5.0)
Scipy			(version 0.13.0)
Numpy			(version 1.8.0)
requests		(version 1.2.3)
BeautifulSoup	(version 3.2.1)
xlrd			(version 0.9.2)
ezodf			(version 0.2.5) 
sas7bdat		(version 0.2.2)

Now download the Salstat source file (if you haven't already) and uncompress it. Go into the top directory in a terminal and type:

python salstat.py

This should launch Salstat.


### PROBLEMS INSTALLING FROM SOURCE

1. Go back and ensure all the modules above were installed.
2. Let me know – raise an issue on Github (https://github.com/salmoni/Salstat)
3. See what error comes up and see if the help groups can sort it out. I used to use the newsgroup comp.lang.python but other places might be useful too. 


## SALSTAT2 

This is a different program written by someone else. Feel free to try it out and see if it suits you better: https://code.google.com/p/salstat-statistics-package-2/

Alan James Salmoni
alan@salstat.com


