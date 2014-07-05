# FlowML

Data analysis tools for Flow Cytometry.

## Background
Tools for flow cytometry tend to take two flavors.
There are commercial tools with good user interfaces like [FlowJo](http://www.flowjo.com/) and [Kaluza](http://www.beckmancoulter.com/wsrportal/wsr/research-and-discovery/products-and-services/flow-cytometry/software/kaluza-analysis-software/index.htm) that are widely used by technicians because of their low barrier to entry.
However, these tools only assist with manual analysis: users have to automatically 'gate' cells, selecting regions in $\mathbb{R}^p$ 
that correspond to known cell types.
In contrast, open source tools, provide many advanced features, but require having a programming background to use.
 [Bioconductor](http://www.bioconductor.org)'s 
package [flowCore](http://www.bioconductor.org/packages/release/bioc/html/flowCore.html) and its dependents
provide advanced, automatic gating

There has slowly been a merging of these two types of tools.
For example, 
* [CYT](http://www.c2b2.columbia.edu/danapeerlab/html/cyt-download.html) out of Diana Pe'er's lab provides many of these features:
  a Matlab based user interface with gating abilities as well as t-SNE views of data.
* [SPADE](http://pengqiu.gatech.edu/software/SPADE2/) from Peng Qiu that provides access to Qiu's minimum spanning tree algorithm.


## Goals
The goal of this project is to enable all flow cytometry analysis steps inside IPython.
The advantage of IPython is it already includes all the reporting type features that commercial tools provide: 
documentation and plots are stored along with the code that produced them.
Moreover, since IPython provides an actual programming interface, there is more flexibility in doing bulk analysis than would be possible
in a fixed GUI.
Even better, IPython makes it easy to interface with R and other languages inside the same notebook, allowing polyglot development.

* 1D and 2D histograms and kernel density estimator plots
* Gating (drawing polygons to select data) inside the IPython Notebook
* Automated gating algorithms inside other packages, namely the [Bioconductor](http://www.bioconductor.org)'s 
package [flowCore](http://www.bioconductor.org/packages/release/bioc/html/flowCore.html) and its descendants
* Advanced dimension reduction techniques
	* [t-SNE](http://homepage.tudelft.nl/19j49/t-SNE.html) and [viSNE](http://www.c2b2.columbia.edu/danapeerlab/html/cyt.html)
	* [SPADE](http://pengqiu.gatech.edu/software/SPADE2/)
	* Others available in [Scikit-learn](http://scikit-learn.org/stable/).



