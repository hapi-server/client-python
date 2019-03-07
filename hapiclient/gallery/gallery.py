def gallery(*args, **kwargs):
    """Create a web-browsable gallery of plots (aka "PNG Walk").

    For additional documentation and demonstration, see hapi_demo.ipynb
    at <https://github.com/hapi-server/client-python-notebooks/>

    Usage
    ----------
    gallery(server, dataset)
    gallery(server, dataset, parameter)

    Examples
    ----------
    >>> from hapiclient import gallery
    >>> gallery('http://hapi-server.org/servers/TestData/hapi', 'dataset1')
    # Webpage tab opens

    >>> from hapiclient import gallery
    >>> gallery('http://hapi-server.org/servers/TestData/hapi','dataset1', 'vector')
    # Webpage tab opens

    Parameters
    ----------
    server : str
        A URL for a HAPI-compliant server. (A HAPI URL always ends with "/hapi".)
    dataset : str
        A dataset from a HAPI server. The valid datasets can
        be determined using `hapi(server)`.
    parameter : str
        A parameter in dataset. The valid parameters can be determined using
        `hapi(server, dataset)`.

    Returns
    ----------
    None (a new tab is opened in the user's default browser)

    """

    import time
    import webbrowser

    from multiprocessing import Process
    from hapiclient.hapi import cachedir
    from hapiclient.util import error, warning, setopts, prompt
    from hapiplotserver.main import hapiplotserver

    if len(args) != 2 and len(args) !=3:
        error('Number of arguments must be 2 or 3. See help(gallery).')

    server = args[0]
    dataset = args[1]
    if len(args) == 3:
        parameters = args[2].split(",")
    else:
        parameters = ['']

    if len(parameters) > 1:
        # Eventually, mulitple parameters will result is a stack plot.
        warning('Multiple parameters given; only first will be shown.')
    parameters = parameters[0]

    if not all(type(arg) is str for arg in args):
        error('All inputs must be a strings. See help(gallery).')

    # Default options
    opts = {
                'cache_dir': cachedir(),
                'usecache': True,
                'port': 5002,
                'format': 'png',
                'figsize': (7,3),
                'dpi': 144,
                'transparent': True,
                'loglevel': 'default'
            }

    # Override defaults
    opts = setopts(opts, kwargs)

    if not parameters == '': 
        paramopt = "&parameters=" + parameters
    else:
        paramopt = ''

    url = 'http://127.0.0.1:'+str(opts['port'])
    url = url + '/?server=' + server
    url = url +'&id=' + dataset
    url = url + paramopt
    url = url + '&format=gallery'

    try:
        process = Process(target=hapiplotserver, kwargs=opts)
        process.start()
    except Exception as e:
        print(e)
        print("Terminating server.")
        process.terminate()

    print(" * Opening ViViz in browser in 1 second.")
    time.sleep(1)
    webbrowser.open(url, new=2)
    prompt("\n\033[0;34mPress a key at any time to terminate ViViz gallery server.\033[0m\n\n")
    process.terminate()
    print("ViViz gallery server has terminated.")
