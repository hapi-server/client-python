[![DOI](https://zenodo.org/badge/93170857.svg)](https://zenodo.org/badge/latestdoi/93170857)

**HAPI Client for Python**

Basic usage examples for various HAPI servers are given in [hapi_demo.py](https://github.com/hapi-server/client-python/blob/master/hapi_demo.py) and the Examples section of a Jupyter Notebook hosted on Google Colab: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hapi-server/client-python-notebooks/blob/master/hapi_demo.ipynb#examples).

# Installation

```bash
pip install hapiclient --upgrade
# or
pip install 'git+https://github.com/hapi-server/client-python' --upgrade
```

The optional [hapiplot package](https://github.com/hapi-server/plot-python) provides basic preview plotting capabilities of data from a HAPI server. The [Plotting section](https://colab.research.google.com/github/hapi-server/client-python-notebooks/blob/master/hapi_demo.ipynb#plotting) of the `hapiclient` Jupyter Notebook shows how to plot the output of `hapiclient` using many other plotting libraries.

To install `hapiplot`, use

```bash
pip install hapiplot --upgrade
# or
pip install 'git+https://github.com/hapi-server/plot-python' --upgrade
```

See the [Appendix](#appendix) for a fail-safe installation method.

# Basic Example

```python
# Get Dst index from CDAWeb HAPI server
from hapiclient import hapi

# See http://hapi-server.org/servers/ for a list of
# other HAPI servers and datasets.
server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
dataset    = 'OMNI2_H0_MRG1HR'
start      = '2003-09-01T00:00:00'
stop       = '2003-12-01T00:00:00'
parameters = 'DST1800'
opts       = {'logging': True}

# Get data
data, meta = hapi(server, dataset, parameters, start, stop, **opts)
print(meta)
print(data)

# Plot all parameters
from hapiplot import hapiplot
hapiplot(data, meta)
```

# Documentation

Basic usage examples for various HAPI servers are given in [hapi_demo.py](https://github.com/hapi-server/client-python/blob/master/hapi_demo.py>) and the [Examples section](https://colab.research.google.com/github/hapi-server/client-python-notebooks/blob/master/hapi_demo.ipynb#examples) of a Jupyter Notebook hosted on Google Colab.

See http://hapi-server.org/servers/ for a list of HAPI servers and datasets.

All of the features are extensively demonstrated in [hapi_demo.ipynb](https://colab.research.google.com/github/hapi-server/client-python-notebooks/blob/master/hapi_demo.ipynb#data-model), a Jupyter Notebook that can be viewed an executed on Google Colab.

# Metadata Model

See also the examples in the [Metadata Model section](https://colab.research.google.com/github/hapi-server/client-python-notebooks/blob/master/hapi_demo.ipynb) of the `hapiclient` Jupyter Notebook.

The HAPI client metadata model is intentionally minimal and closely follows that of the [HAPI metadata model](https://github.com/hapi-server/data-specification). We expect that another library will be developed that allows high-level search and grouping of information from HAPI servers. See also [issue #106](https://github.com/hapi-server/data-specification/issues/106).

# Data Model and Time Format

See also the examples in the [Data Model section](https://colab.research.google.com/github/hapi-server/client-python-notebooks/blob/master/hapi_demo.ipynb) of the `hapiclient` Jupyter Notebook. The examples include 

1. Fast and well-tested conversion from ISO 8601 timestamp strings to Python `datetime` objects
2. Putting the content of `data` in a Pandas `DataFrame` object
3. Creating an Astropy NDArray

A request for data of the form
```
data, meta = hapi(server, dataset, parameters, start, stop)
```

returns the [Numpy N-D array](https://docs.scipy.org/doc/numpy-1.15.1/user/quickstart.html) `data` and a Python dictionary `meta` from a HAPI-compliant data server `server`. The structure of `data` and `meta` mirrors the structure of a response from a HAPI server.

The HAPI client data model is intentionally basic. There is an ongoing discussion of a data model for Heliophysics data among the [PyHC community](https://heliopython.org/). When this data model is complete, a function that converts `data` and `meta` to that data model will be included in the `hapiclient` package.

# Development

```bash
git clone https://github.com/hapi-server/client-python
cd client-python; pip install -e .
```

The command `pip install -e .` creates symlinks so that the local package is
used instead of an installed package. You may need to execute `pip uninstall hapiclient` to ensure the local package is used. To check the version installed, use `pip list | grep hapiclient`.

To run tests before a commit, execute

```bash
make repository-test
```

To run an individual unit test in a Python session, use, e.g.,

```python
from hapiclient.test.test_hapi import test_reader_short
test_reader_short()
```

# Contact

Submit bug reports and feature requests on the [repository issue
tracker](https://github.com/hapi-server/client-python/issues>).

# Appendix

Fail-safe installation

Python command line:

```python
import os
print(os.popen("pip install hapiclient").read())
```

The above executes and displays the output of the operating system
command `pip install hapiclient` using the shell environment
associated with that installation of Python.

This method addresses a problem that is sometimes encountered when
attempting to use `pip` packages in Anaconda. To use a `pip` package
in Anaconda, one must use the version of `pip` installed with Anaconda
(it is usually under a subdirectory with the name `anaconda/`) as
opposed to the one installed with the operating system. To see the
location of ``pip`` used in a given Python session, enter
`print(os.popen("which pip").read())`.
