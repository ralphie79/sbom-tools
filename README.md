
# SBOM Tools

## What is this?

Various initial hacks to explore SBOM data.

### sbom-detect.py 

Given a directory of inputs, crawl through and identify files which are likely to be SBOMs and identify format, standard, and version for each.

### sbom-vis-*.py

Basic visualization of SBOM relationships via pyvis. 


## Why not use 'proper' parsers/libraries?

SBOM data may be incorrect or malformed. Instead of using heavyweight libraries, this code aims to extract salient identifying information without requiring full parsing of the data.


## TODO

Many things:

* Limit the graph/display to only N tiers of SBOM data for ease of navigation
* Check for presence/absence of 'required' SBOM fields and display in each node
* Support for SWID
* Support for SPDX XML
* Support for sub-components embeedded in CDX
* ... 


## Examples

### Simple
![simple](basic-container.png )

### Complex

![complex](complex-container.png )

