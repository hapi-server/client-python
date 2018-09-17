# HAPI client for Python 2 and 3

## Installation

```
pip install hapiclient
```

If you are using Anaconda, make sure that the version of `pip` used is the one distributed with Anaconda (use `which pip`).

## Demo

The following downloads and executes the [demo](https://github.com/hapi-server/client-python/hapi_demo.py).

### Python 3
```python
# D/L and save hapi_demo.py
import urllib.request
url = 'https://github.com/hapi-server/client-python/raw/master/hapi_demo.py'
urllib.request.urlretrieve(url,'hapi_demo.py')
exec(open("hapi_demo.py").read(), globals())
```

### Python 2
```python
# D/L and save hapi_demo.py
import urllib
url = 'https://github.com/hapi-server/client-python/raw/master/hapi_demo.py'
urllib.urlretrieve(url,'hapi_demo.py')
exec(open("hapi_demo.py").read(), globals())
```

## Development

```bash
git clone https://github.com/hapi-server/client-python
cd client-python; python setup.py develop
```
	
Note that the scripts are written to match syntax/capabilities/interface of the [HAPI MATLAB client](https://github.com/hapi-server/matlab-client).

## Contact

Submit bug reports and feature requests on the [repository issue tracker](https://github.com/hapi-server/client-python/issues).

Bob Weigel <rweigel@gmu.edu>

