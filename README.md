# HAPI client for Python 2 and 3

## Installation

Requires Python libraries (Numpy, Pandas, Matplotlib) that are typically shipped with a Scientific Python distribution, e.g., [Anaconda](https://www.continuum.io/).  Tested using the Spyder GUI that ships with Anaconda.

The following will download `hapi_demo.py`. When `hapi_demo.py` is executed, it will download the main script `hapi.py` and the plotting script `hapiplot.py`.

### Python 3
```python
# D/L and save hapi_demo.py
url = 'https://github.com/hapi-server/client-python/hapi_demo.py'
urllib.request.urlretrieve(url,'hapi_demo.py')
runfile('hapi_demo.py')
```

### Python 2
```python
# D/L and save hapi_demo.py
url = 'https://github.com/hapi-server/client-python/hapi_demo.py'
urllib.urlretrieve(url,'hapi_demo.py')
runfile('hapi_demo.py')
```

## Development

```bash
git clone https://github.com/hapi-server/client-python
```

Note that the scripts are written to match syntax/capabilities/interface of the [HAPI MATLAB client](https://github.com/hapi-server/matlab-client).

## Contact

Submit bug reports and feature requests on the [repository issue tracker](https://github.com/hapi-server/client-python/issues).

Bob Weigel <rweigel@gmu.edu>

