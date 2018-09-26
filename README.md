# HAPI client for Python 2 and 3

## Installation

Command line:
```bash
pip install hapiclient
```

If you are using Anaconda, make sure that the version of `pip` used is the one distributed with Anaconda (`which pip` should show a location in an anaconda directory). As a failsafe, on the Python command line, you can use

```python
import os
print(os.popen("pip install hapiclient").read())
```

## Demo

The [hapi_demo.py](https://github.com/hapi-server/client-python/hapi_demo.py) shows example usage of this package. The output of this demo after execution in a [Jupyter Notebook](https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Notebook%20Basics.html) can be viewed at [hapi_demo.ipynb](https://github.com/hapi-server/client-python/blob/master/hapi_demo.ipynb).

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

(The command <code>python setup.py develop</code> creates symlinks so that the local package is used instead of an installed package.)

Note that the scripts are written to match syntax/capabilities/interface of the [HAPI MATLAB client](https://github.com/hapi-server/matlab-client).

## Contact

Submit bug reports and feature requests on the [repository issue tracker](https://github.com/hapi-server/client-python/issues).

Bob Weigel <rweigel@gmu.edu>
