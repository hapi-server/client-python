HAPI client for Python 2/3
==============================

Installation
------------

Operating system command line:

.. code:: bash

    pip install hapiclient

or

.. code:: bash

    pip install https://github.com/hapi-server/client-python

See the `Appendix <#Appendix>`__ for a fail-safe installation method.

Documentation
-------------

All of the features are extensively demonstrated in the `hapi_demo.ipynb <https://github.com/hapi-server/client-python-notebooks/blob/master/hapi_demo.ipynb>`__ Jupyter Notebook. The notebook shows example usage of the functions in this package that can be copied into a script or onto a Python command line.

To view the help string on the Python command line after installing ``hapiclient`` using ``pip install hapiclient``, use

.. code:: python

     from hapiclient import hapi
     help(hapi)

or

.. code:: python

      from hapiclient import hapiplot
      help(hapiplot)

Development
-----------

.. code:: bash

    git clone https://github.com/hapi-server/client-python
    cd client-python; python setup.py develop

(The command python setup.py develop creates symlinks so that the local
package is used instead of an installed package. Use
``pip uninstall hapiclient`` to ensure the local package is used.)

To run tests before a commit, execute

.. code:: bash

    make repository-test

To run an individual unit test in a Python session, use, e.g.,

.. code:: python

    from hapiclient.test.test_hapi import test_reader
    test_reader()

Contact
-------

Submit bug reports and feature requests on the `repository issue
tracker <https://github.com/hapi-server/client-python/issues>`__.

Bob Weigel rweigel@gmu.edu

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
