(Draft) HAPI client for Python

Attempts to match syntax/capabilities/interface of the (HAPI MATLAB client)[https://github.com/hapi-server/matlab-client].

This is a work in progress.  Tests have not been written and minimal error checking is performed. Support for string columns is not yet implemented.

Reads HAPI CSV and binary.

Requires Python libraries (Numpy, Pandas, Matplotlib) that are typically shipped with a Scientific Python distribution, e.g., (Anaconda)[https://www.continuum.io/].  Tested using the Spyder GUI that ships with Anaconda.

To test, execute `hapi_demo.py`.