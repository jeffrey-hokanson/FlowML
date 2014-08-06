# FlowML: Data analysis tools for Flow Cytometry.
* Author: Jeffrey M. Hokanson <jeffrey@hokanson.us>


FlowML provides a [python](https://www.python.org/) tool chain for the all the common steps in analyzing 
[flow cytometry](http://en.wikipedia.org/wiki/Flow_cytometry) data
with [matplotlib](http://matplotlib.org) based visualizations.
Coupled with an [IPython Notebook](http://ipython.org/notebook.html), FlowML allows easy, interactive, programmatic data analysis.



## Getting Started
Clone the repository, then run the `start_server.sh` script on a Mac or Linux system.

## Motivation
There are many questions we want to ask of Flow Cytometry data -- some we don't even know yet.
The problem is that GUI interfaces have a relatively limited ability to interact with data
and programming tools are often outside of the skill set of most technicians.

* Commerical GUI
+ [FlowJo](http://www.flowjo.com/) 
+ [Kaluza](http://www.beckmancoulter.com/wsrportal/wsr/research-and-discovery/products-and-services/flow-cytometry/software/kaluza-analysis-software/index.htm) 
+ [GemStone](http://www.vsh.com/products/GemStone/index.asp)
* Free or Open Source GUI
+ [Flowing Software](http://flowingsoftware.com/)
* Research
+ [SPADE](http://pengqiu.gatech.edu/software/SPADE2/) by Diana Pe'er's lab (Matlab based)
+ [CYT](http://www.c2b2.columbia.edu/danapeerlab/html/cyt-download.html) by Peng Qiu (Matlab based)
* Software toolchains
+ [FCM](https://github.com/jfrelinger/fcm) Python   
+ [flowCore](http://www.bioconductor.org/packages/release/bioc/html/flowCore.html) [Biocnductor](http://www.bioconductor.org/) toolkit ([R](http://www.r-project.org/)-language)
* Other
+ [FCS](https://github.com/MorganConrad/fcs) A Node.js package for reading FCS files

## Project Goals
The code is under heavy development and the following features are planned on being added.
* Reading and writing FCS files
* 1D and 2D histograms and kernel density estimator plots
* Gating (drawing polygons to select data) inside the IPython Notebook
* Automated gating algorithms inside other packages, namely the [Bioconductor](http://www.bioconductor.org)'s 
package [flowCore](http://www.bioconductor.org/packages/release/bioc/html/flowCore.html) and its descendants
* Advanced dimension reduction techniques
	* [t-SNE](http://homepage.tudelft.nl/19j49/t-SNE.html) and [viSNE](http://www.c2b2.columbia.edu/danapeerlab/html/cyt.html)
	* [SPADE](http://pengqiu.gatech.edu/software/SPADE2/)
	* Others available in [Scikit-learn](http://scikit-learn.org/stable/).



## Contributions
This project uses some code developed by Jacob Frelinger for [FCM](https://github.com/jfrelinger/fcm) for writing FCS files.
