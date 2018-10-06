# HAPI client for Python 2 and 3

## Installation

### Standard Method

Operating system command line:

```bash
pip install hapiclient
```

### Fail-safe

Python command line:

```python
import os
print(os.popen("pip install hapiclient").read())
```

The above executes and displays the output of the operating system command `pip install hapiclient` using the shell environment associated with that installation of Python.

This method addresses a problem often encountered when attempting to use `pip` packages in Anaconda. To use a `pip` package in Anaconda, one must use the version of `pip` installed with Anaconda (it is usually under a subdirectory with the name `anaconda/`) as opposed to the one installed with the operating system. To see the location of `pip` used in a given Python session, enter `print(os.popen("which pip").read())`.

## Documentation

See the help string by entering `help(hapi)` on the Python command line.

All of the features are extensively demonstrated in [hapi_demo.ipynb](https://github.com/hapi-server/client-python/blob/master/hapi_demo.ipynb).

## Demo

The [hapi_demo.py](https://github.com/hapi-server/client-python/blob/master/hapi_demo.py) shows example usage of this package.

### Jypyter Notebook

To execute the demo in a [Jupyter Notebook](https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Notebook%20Basics.html), execute
```
curl -L -O https://rawgithub.com/hapi-server/client-python/master/hapi_demo.ipynb
jupyter-notebook hapi_demo.ipynb
```
(A web page should open. To run code in a cell after editng it, enter <code>SHIFT+ENTER</code>.)

### Python Command Line

The following Python commands downloads and executes the [demo](https://github.com/hapi-server/client-python/hapi_demo.py).

#### Python 2
```python
# D/L and save hapi_demo.py
import urllib
url = 'https://github.com/hapi-server/client-python/raw/master/hapi_demo.py'
urllib.urlretrieve(url,'hapi_demo.py')
exec(open("hapi_demo.py").read(), globals())
```

#### Python 3
```python
# D/L and save hapi_demo.py
import urllib.request
url = 'https://github.com/hapi-server/client-python/raw/master/hapi_demo.py'
urllib.request.urlretrieve(url,'hapi_demo.py')
exec(open("hapi_demo.py").read(), globals())
```

## Development

```bash
git clone https://github.com/hapi-server/client-python
cd client-python; python setup.py develop
```

(The command <code>python setup.py develop</code> creates symlinks so that the local package is used instead of an installed package. Use `pip uninstall hapi` to ensure the local package is used.)

To run tests before a commit, execute
```bash
make repository-test
```

To run an individual test in a Python session, use, e.g.,

```python
from hapiclient.test.test_hapi import test_reader
test_reader()
```

## Contact

Submit bug reports and feature requests on the [repository issue tracker](https://github.com/hapi-server/client-python/issues).

Bob Weigel <rweigel@gmu.edu>
