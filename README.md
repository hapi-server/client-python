# HAPI client for Python 2 and 3

## Installation

### Standard Method

Operating system command line:

```bash
pip install hapiclient
```

See the [Appendix](#Fail-safe-installation) for a fail-safe installation method.

## Documentation

See the help string by entering `help(hapi)` or `help(hapiplot)` on the Python command line.

All of the features are extensively demonstrated in the [hapi_demo.ipynb](https://github.com/hapi-server/client-python/blob/master/hapi_demo.ipynb) Jupyter Notebook. Instructions for local use are shown on this page.

The [hapi_demo.py](https://github.com/hapi-server/client-python/blob/master/hapi_demo.py) scripts shows example usage of the functions in this package that can be copied into a script or onto a Python command line.

## Development

```bash
git clone https://github.com/hapi-server/client-python
cd client-python; python setup.py develop
```

(The command <code>python setup.py develop</code> creates symlinks so that the local package is used instead of an installed package. Use `pip uninstall hapiclient` to ensure the local package is used.)

To run tests before a commit, execute

```bash
make repository-test
```

To run an individual unit test in a Python session, use, e.g.,

```python
from hapiclient.test.test_hapi import test_reader
test_reader()
```

## Contact

Submit bug reports and feature requests on the [repository issue tracker](https://github.com/hapi-server/client-python/issues).

Bob Weigel <rweigel@gmu.edu>

## Appendix

<a name="Fail-safe-installation"></a>
### Fail-safe installation

Python command line:

```python
import os
print(os.popen("pip install hapiclient").read())
```

The above executes and displays the output of the operating system command `pip install hapiclient` using the shell environment associated with that installation of Python.

This method addresses a problem that is sometimes encountered when attempting to use `pip` packages in Anaconda. To use a `pip` package in Anaconda, one must use the version of `pip` installed with Anaconda (it is usually under a subdirectory with the name `anaconda/`) as opposed to the one installed with the operating system. To see the location of `pip` used in a given Python session, enter `print(os.popen("which pip").read())`.