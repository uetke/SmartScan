# README of SmartScan 1.0#

SmartScan is a program currently under heavy development in the Single-Molecule group at Leiden university. The main scope of this program is to control confocal microscopes and to be able to automate tasks that are repetitive, prone to errors and consume too much time. 
A clear example of this is the refocusing procedure: To focus a microscope on a molecule (or a nanoparticle) normally one performs several 1-D scans and finds the maximum intensity for them. This task can be easily implemented in a computer program. With that simple example in mind, the complexity of the tasks started to grow, controlling several devices, acquiring different signals and communicating with more computers.
The program is fully written in Python and the graphical interface was developed in Qt, normally with the PyQt libraries. The versatility of python and its fast prototyping style made it an ideal candidate for easy to deploy and to maintain code. 

### What is there in the SmartScan 1.0 ###

You can visit [our website](https://www.single-molecule.nl) to get to know the kind of experiments we are currently performing. SmartScan is not the only available software in the group. Many of the experiments run a LabView program that is more mature and stable, but harder to maintain and harder to develop further.

### How to set up SmartScan ###

There is no script at the moment for setting up SmartScan. You need Python 3.3+ with some extra dependencies. PyQt4 is needed for the GUI, but if you are just use the program for command-line applications, there shouldn't be the need. Some extra non-standard libraries like numpy, matplotlib should be included in almost any lab-alike computer. Importantly, [pyqtgraph](http://www.pyqtgraph.org/) is needed for the GUI as well, since many of the live generated plots are based on that library. 

Remember that the program runs only together with an [ADwin box](http://www.adwin.de/index-us.html). This real time controller is quite different from NI-cards.

### The MVC design ### 

Initially the program was meant to be developed following an MVC design, making the code highly re-usable even in case of exchanging the ADwin for a National Instruments card. Instrumentation software naturally leads to this kind of patterns since there is a real interaction with the world. This design was however not maintained through time and needs to be reviewed. A possible full re-write of the code may be needed to achieve this.

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact