.. image:: https://travis-ci.org/hapi-server/client-python.svg?branch=master
    :target: https://travis-ci.org/hapi-server/client-python

HAPI client for Python 2/3
==============================

Installation
------------

.. code:: bash

    pip install hapiclient --upgrade
    # or
    pip install 'git+https://github.com/hapi-server/client-python' --upgrade

    pip install hapiplot --upgrade
    # or
    pip install 'git+https://github.com/hapi-server/plot-python' --upgrade

See the `Appendix <#Appendix>`__ for a fail-safe installation method.

Basic Example
-------------

.. code:: python

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
    from hapiplot import hapi
    hapiplot(data, meta)


Documentation
-------------

Basic usage examples for various HAPI servers are given in `hapi_demo.py <https://github.com/hapi-server/client-python/blob/master/hapi_demo.py>`__

See http://hapi-server.org/servers/ for a list of HAPI servers and datasets.

All of the features are extensively demonstrated in the `hapi_demo.ipynb <https://github.com/hapi-server/client-python-notebooks/blob/master/hapi_demo.ipynb>`__ Jupyter Notebook.


Data Model and Time Format
--------------------------

A request for data of the form
```
data, meta = hapi(server, dataset, parameters, start, stop)
```

returns the [Numpy N-D array](https://docs.scipy.org/doc/numpy-1.15.1/user/quickstart.html) `data` and a Python dictionary `meta` from a HAPI-compliant data server `server`. The structure of `data` and `meta` mirrors the structure of a response from a HAPI server.

The HAPI client data model is intentionally basic. There is an ongoing discussion of a data model for Heliophysics data among the `PyHC community <https://heliopython.org/>`_. When this data model is complete, a function that converts `data` and `meta` to that data model will be included in the `hapiclient` package.

Examples of transforming and manipulating `data` is given in a `Jupyter Notebook <https://colab.research.google.com/drive/11Zy99koiE90JKJ4u_KPTaEBMQFzbfU3P#scrollTo=aI_7DxnZtQZ3>`_. The examples include 

# Fast and well-tested conversion from ISO 8601 timestamp strings to Python `datetime` objects
# Putting the content of `data` in a Pandas `DataFrame` object
# Creating an Astropy NDArray


Development
-----------

.. code:: bash

    git clone https://github.com/hapi-server/client-python
    cd client-python; python setup.py develop

(The command python setup.py develop creates symlinks so that the local package is
used instead of an installed package. You may need to execute ``pip uninstall hapiclient`` 
first to ensure the local package is used.)

To run tests before a commit, execute

.. code:: bash

    make repository-test

To run an individual unit test in a Python session, use, e.g.,

.. code:: python

    from hapiclient.test.test_hapi import test_reader_short
    test_reader_short()

Contact
-------

Submit bug reports and feature requests on the `repository issue
tracker <https://github.com/hapi-server/client-python/issues>`__.

Appendix
--------

Fail-safe installation

Python command line:

.. code:: python

    import os
    print(os.popen("pip install hapiclient").read())

The above executes and displays the output of the operating system
command ``pip install hapiclient`` using the shell environment
associated with that installation of Python.

This method addresses a problem that is sometimes encountered when
attempting to use ``pip`` packages in Anaconda. To use a ``pip`` package
in Anaconda, one must use the version of ``pip`` installed with Anaconda
(it is usually under a subdirectory with the name ``anaconda/``) as
opposed to the one installed with the operating system. To see the
location of ``pip`` used in a given Python session, enter
``print(os.popen("which pip").read())``.
