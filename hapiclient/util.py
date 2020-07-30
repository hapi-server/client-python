def setopts(defaults, given):
    """Override default keyword dictionary options.

        kwargs = setopts(defaults, kwargs)

        A warning is shown if kwargs contains a key not found in default.
    """
    from inspect import stack
    fname = stack()[1][1]

    # Override defaults
    for key, value in given.items():
        if type(given[key]) == dict:
            setopts(defaults[key], given[key])
            continue
        if key in defaults:
            defaults[key] = value
        else:
            warning('Ignoring invalid keyword option "%s".' % key, fname)

    return defaults


def log(msg, opts):
    """Print message to console."""

    import sys

    if opts['logging']:
        if pythonshell() == 'jupyter-notebook':
            # Don't show full path information.
            msg = msg.replace(opts['cachedir'] + '/', '')
            msg = msg.replace(opts['cachedir'], '')
        pre = sys._getframe(1).f_code.co_name + '(): '
        print(pre + msg)


def jsonparse(res, url):
    """Try/catch of json.loads() function with short error message."""

    from json import loads
    try:
        return loads(res.read().decode('utf-8'))
    except:
        error('Could not parse JSON from %s' % url)


def system(cmd):
    """Execute system command and return exit code, stderr, and stdout.

        exitcode, stderr, stdout = system(cmd)

        If execution fails, an OSError is raised.
    """

    #TODO: Document difference between exitcode != 0 and OSError

    from shlex import split
    from subprocess import Popen, PIPE
    try:
        args = split(cmd)
        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        exitcode = proc.returncode
        return exitcode, out.decode(), err.decode()
    except OSError as err:
        msg = "Execution failed: " + cmd + "\n" + err[1]
        raise OSError(msg)


def pythonshell():
    """Determine python shell

    pythonshell() returns

    'shell' (started python on command line using "python")
    'ipython' (started ipython on command line using "ipython")
    'ipython-notebook' (running in Spyder or started with "ipython qtconsole")
    'jupyter-notebook' (running in a Jupyter notebook)

    See also https://stackoverflow.com/a/37661854
    """

    from os import environ, path
    env = environ
    shell = 'shell'
    program = path.basename(env['_'])

    if 'jupyter-notebook' in program:
        shell = 'jupyter-notebook'
    elif 'JPY_PARENT_PID' in env or 'ipython' in program:
        shell = 'ipython'
        if 'JPY_PARENT_PID' in env:
            shell = 'ipython-notebook'

    return shell


def warning_test():
    """For testing warning function."""

    # Should show warnings in order and only HAPIWarning {1,2} should
    # have a different format
    from warnings import warn
    from hapiclient.util import warning

    warn('Normal warning 1')
    warn('Normal warning 2')

    warning('HAPI Warning 1')
    warning('HAPI Warning 2')

    warn('Normal warning 3')
    warn('Normal warning 4')


def warning(*args):
    """Display a short warning message.

    warning(message) raises a warning of type HAPIWarning and displays
    "Warning: " + message. Use for warnings when a full stack trace is not
    needed.
    """

    import warnings
    from os import path
    from sys import stderr
    from inspect import stack

    message = args[0]
    if len(args) > 1:
        fname = args[1]
    else:
        fname = stack()[1][1]

    #line = stack()[1][2]

    fname = path.basename(fname)

    # Custom warning format function
    def _warning(message, category=UserWarning, filename='', lineno=-1, file=None, line=''):
        if category.__name__ == "HAPIWarning":
            stderr.write("\x1b[31mWarning in " + fname + "\x1b[0m: " + str(message) + "\n")
        else:
            # Use default showwarning function.
            showwarning_default(message, category=UserWarning,
                                filename='', lineno=-1,
                                file=None, line='')

        stderr.flush()

        # Reset showwarning function to default
        warnings.showwarning = showwarning_default

    class HAPIWarning(Warning):
        pass

    # Copy default showwarning function
    showwarning_default = warnings.showwarning

    # Use custom warning function instead of default
    warnings.showwarning = _warning

    # Raise warning
    warnings.warn(message, HAPIWarning)


def error(msg, debug=False):
    """Display a short error message.

    error(message) raises an error of type HAPIError and displays
    "Error: " + message. Use for errors when a full stack trace is not needed.

    If debug=True, full stack trace is shown.
    """

    import sys
    from inspect import stack
    from os import path

    debug = True
    try:
        from IPython.core.interactiveshell import InteractiveShell
    except:
        pass

    fname = stack()[1][1]
    fname = path.basename(fname)
    #line = stack()[1][2]

    def exception_handler_ipython(self, exc_tuple=None,
                                  filename=None, tb_offset=None,
                                  exception_only=False,
                                  running_compiled_code=False):

        #import traceback
        exception = sys.exc_info()
        if not debug and exception[0].__name__ == "HAPIError":
            sys.stderr.write("\033[0;31mError:\033[0m " + str(exception[1]))
        else:
            # Use default
            showtraceback_default(self, exc_tuple=None,
                                  filename=None, tb_offset=None,
                                  exception_only=False,
                                  running_compiled_code=False)

        sys.stderr.flush()

        # Reset back to default
        InteractiveShell.showtraceback = showtraceback_default

    def exception_handler(exception_type, exception, traceback):
        if not debug and exception_type.__name__ == "HAPIError":
            print("\033[0;31mError:\033[0m %s" % exception)
        else:
            # Use default.
            sys.__excepthook__(exception_type, exception, traceback)

        sys.stderr.flush()

        # Reset back to default
        sys.excepthook = sys.__excepthook__

    class HAPIError(Exception): pass

    try:
        # Copy default function
        showtraceback_default = InteractiveShell.showtraceback
        # TODO: Use set_custom_exc
        # https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.interactiveshell.html
        InteractiveShell.showtraceback = exception_handler_ipython
    except:
        # IPython over-rides this, so this does nothing in IPython shell.
        # https://stackoverflow.com/questions/1261668/cannot-override-sys-excepthook
        # Don't need to copy default function as it is provided as sys.__excepthook__.
        sys.excepthook = exception_handler

    raise HAPIError(msg)


def head(url):
    '''Python 2/3 compatable HTTP HEAD request on URL.

    If Python 3, returns
    urllib.request.urlopen(url).info()

    If Python 2, returns
    urllib2.urlopen(url).info()
    '''

    import urllib3
    http = urllib3.PoolManager()
    try:
        res = http.request('HEAD', url, retries=2)
        if res.status != 200:
            raise Exception('Head request failed on ' + url)
        else:
            return res.headers
    except Exception as e:
        raise e

    return res.headers


def urlopen(url):
    """Python 2/3 urlopen compatibility function.

    If Python 3, returns
    urllib.request.urlopen(url, fname)

    If Python 2, returns
    urllib.urlopen(url, fname)
    """

    import sys
    from json import load

    # https://stackoverflow.com/a/2020083
    def get_full_class_name(obj):
        module = obj.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return obj.__class__.__name__
        return module + '.' + obj.__class__.__name__

    import urllib3
    c = " If problem persists, a contact email for the server may be listed at http://hapi-server.org/servers/"
    try:
        http = urllib3.PoolManager()
        res = http.request('GET', url, preload_content=False, retries=2)
        if res.status != 200:
            try:
                jres = load(res)
                if 'status' in jres:
                    if 'message' in jres['status']:
                        error('\n%s\n  %s\n' % (url, jres['status']['message']))
                error("Problem with " + url + ". Server responded with non-200 HTTP status (" + str(res.status) + ") and invalid HAPI JSON error message in response body." + c)
            except:
                error("Problem with " + url + ". Server responded with non-200 HTTP status (" + str(res.status) + ") and no HAPI JSON error message in response body." + c)
    except urllib3.exceptions.NewConnectionError:
        error('Connection error for : ' + url + c)
    except urllib3.exceptions.ConnectTimeoutError:
        error('Connection timeout for: ' + url + c)
    except urllib3.exceptions.ReadTimeoutError:
        error('Read timeout for: ' + url + c)
    except urllib3.exceptions.LocationValueError:
        error('Invalid URL: ' + url)
    except urllib3.exceptions.LocationParseError:
        error('Could not parse URL: ' + url)
    except urllib3.exceptions.HTTPError as e:
        error('Exception ' + get_full_class_name(e) + " for: " + url)
    except Exception as e:
        error(type(sys.exc_info()[1]).__name__ + ': ' + str(e) + ' for URL: ' + url)

    return res


def urlretrieve(url, fname, check_last_modified=False, **kwargs):
    """Python 2/3 urlretrieve compatability function.

    If Python 3, returns
    urllib.request.urlretrieve(url, fname)

    If Python 2, returns
    urllib.urlretrieve(url, fname)
    """

    import shutil
    from os import path, utime, makedirs
    from time import mktime, strptime

    if check_last_modified:
        if modified(url, fname, **kwargs):
            log('Downloading ' + url + ' to ' + fname, kwargs)
            res = urlretrieve(url, fname, check_last_modified=False)
            if "Last-Modified" in res.headers:
                # Change access and modfied time to match that on server.
                # TODO: Won't need if using file.head in modified().
                urlLastModified = mktime(strptime(res.headers["Last-Modified"],
                                                  "%a, %d %b %Y %H:%M:%S GMT"))
                utime(fname, (urlLastModified, urlLastModified))
        else:
            log('Local version of ' + fname + ' is up-to-date; using it.', kwargs)

    dir = path.dirname(fname)
    if not path.exists(dir):
        makedirs(dir)

    with open(fname, 'wb') as out:
        res = urlopen(url)
        shutil.copyfileobj(res, out)
        return res


def modified(url, fname, **kwargs):
    """Check if timestamp on file is older than Last-Modifed in HEAD request"""

    from os import stat, path
    from time import mktime, strptime

    debug = False

    if not path.exists(fname):
        return True

    # HEAD request on url
    log('Making head request on ' + url, kwargs)
    headers = head(url)

    # TODO: Write headers to file.head
    if debug: 
        print("Header:\n--\n")
        print(headers)
        print("--")

    # TODO: Get this from file.head if found
    fileLastModified = stat(fname).st_mtime
    if "Last-Modified" in headers:
        urlLastModified = mktime(strptime(headers["Last-Modified"],
                                          "%a, %d %b %Y %H:%M:%S GMT"))
        if urlLastModified > fileLastModified:
            return True

        if debug:
            print("File Last Modified = %s" % fileLastModified)
            print("URL Last Modified = %s" % urlLastModified)
    else:
        if debug:
            print("No Last-Modified header. Will re-download")
        # TODO: Read file.head and compare etag
        return True


##############################################################################
# Start compatability code
def prompt(msg):
    '''Python 2/3 imput compatability function. Pauses for user input.

    If Python 3, calls
    input(msg)

    If Python 2, calls
    raw_input(msg)
    '''
    import sys
    if sys.version_info[0] > 2:
        input(msg)
    else:
        raw_input(msg)


def urlquote(url):
    '''Python 2/3 urlquote compatability function.

    If Python 3, returns
    urllib.parse.quote(url)

    If Python 2, returns
    urllib.quote(url)
    '''

    import sys
    if sys.version_info[0] > 2:
        import urllib.parse
        return urllib.parse.quote(url)
    else:
        from urllib import quote
        return quote(url)

# End compatability code
##############################################################################
