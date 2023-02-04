def setopts(defaults, given):
    """Override default keyword dictionary options.

    kwargs = setopts(defaults, kwargs)

    A warning is shown if kwargs contains a key not found in default.
    """

    # Override defaults
    for key, value in given.items():
        if type(given[key]) == dict:
            setopts(defaults[key], given[key])
            continue
        if key in defaults:
            defaults[key] = value
        else:
            warning('Ignoring invalid keyword option "%s".' % key)

    return defaults


def log_test():

    log("Test 1", {"logging": True})
    log("Test 2", {"logging": False})


def log(msg, opts):
    """Print message to console or file."""

    import os
    import sys

    if not 'logging' in opts:
        opts = opts.copy()
        opts['logging'] = False

    pre = sys._getframe(1).f_code.co_name + '(): '
    if isinstance(opts['logging'], bool) and opts['logging']:
        if pythonshell() == 'jupyter-notebook':
            # Don't show full path information.
            msg = msg.replace(opts['cachedir'] + os.path.sep, '')
            msg = msg.replace(opts['cachedir'], '')
        print(pre + msg)
    elif hasattr(opts['logging'], 'write'):
        opts['logging'].write(pre + msg + "\n")
        opts['logging'].flush()
    else:
        pass # TODO: error


def jsonparse(res, url):
    """Try/catch of json.loads() function with short error message."""

    from json import loads
    try:
        return loads(res.read().decode('utf-8'))
    except:
        error('Could not parse JSON from %s' % url)


def pythonshell():
    """Determine python shell

    pythonshell() returns

    'shell'             if started python on command line using "python"
    'ipython'           if started ipython on command line using "ipython"
    'ipython-notebook'  if running in Spyder or started with "ipython qtconsole"
    'jupyter-notebook'  if running in a Jupyter notebook started using executable
                        named jupyter-notebook

    On Windows, jupyter-notebook cannot be detected and ipython-notebook
    will be returned.

    See also https://stackoverflow.com/a/37661854
    """

    import os

    env = os.environ

    program = ''
    if '_' in env:
        program = os.path.basename(env['_'])

    shell = 'shell'
    try:
        shell_name = get_ipython().__class__.__name__
        if shell_name == 'TerminalInteractiveShell':
            shell = 'ipython'
        elif shell_name == 'ZMQInteractiveShell':
            if 'jupyter-notebook' in program:
                shell = 'jupyter-notebook'
            else:
                shell = 'ipython-notebook'
                # Not needed, but could be used
                #if 'spyder' in sys.modules:
                #    shell = 'spyder-notebook'
    except:
        pass

    return shell


def unicode_error_message(name):
    import sys
    msg = ""
    if sys.version_info[0:2] <= (3, 5):
        if not all(ord(char) < 128 for char in name):
            msg = "hapiclient cannot handle Unicode dataset or parameter names (" + str(name.encode('utf-8')) + ") for Python < 3.6 on Windows."
    return msg


def warning_test():
    """For testing warning function."""

    # Should show warnings in order and only HAPIWarning {1,2} should
    # have a different format
    from warnings import warn

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

    def prefix():
        import platform
        prefix = "\x1b[31mHAPIWarning:\x1b[0m "
        if platform.system() == 'Windows' and pythonshell() == 'shell':
            prefix = "HAPIWarning: "        

        return prefix

    # Custom warning format function
    def _warning(message, category=UserWarning, filename='', lineno=-1, file=None, line=''):
        if category.__name__ == "HAPIWarning":
            stderr.write(prefix() + str(message) + "\n")
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


class HAPIError(Exception):
    pass


def error(msg, debug=False):
    """Display a short error message.

    error(message) raises an error of type HAPIError and displays
    "Error: " + message. Use for errors when a full stack trace is not needed.

    If debug=True, full stack trace is shown.
    """

    import sys
    from inspect import stack
    from os import path

    debug = False
    if pythonshell() != 'shell':
        try:
            from IPython.core.interactiveshell import InteractiveShell
        except:
            pass

    sys.stdout.flush()

    fname = stack()[1][1]
    fname = path.basename(fname)
    #line = stack()[1][2]

    def prefix():
        import platform
        prefix = "\033[0;31mHAPIError:\033[0m "
        if platform.system() == 'Windows' and pythonshell() == 'shell':
            prefix = "HAPIError: "        

        return prefix

    def exception_handler_ipython(self, exc_tuple=None,
                                  filename=None, tb_offset=None,
                                  exception_only=False,
                                  running_compiled_code=False):
        
        exception = sys.exc_info()
        if not debug and exception[0].__name__ == "HAPIError":
            sys.stderr.write(prefix() + str(exception[1]))
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
            print("%s%s" % (prefix(), exception))
        else:
            # Use default.
            sys.__excepthook__(exception_type, exception, traceback)

        sys.stderr.flush()

        # Reset back to default
        sys.excepthook = sys.__excepthook__


    if pythonshell() == 'shell':
        sys.excepthook = exception_handler
    else:
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
    """HTTP HEAD request on URL."""

    import urllib3
    http = urllib3.PoolManager()
    try:
        res = http.request('HEAD', url, retries=2)
        if res.status != 200:
            raise Exception('Head request failed on ' + url)
        return res.headers
    except Exception as e:
        raise e

    return res.headers


def urlopen(url):
    """Wrapper to request.get() in urllib3"""

    import sys
    import urllib3
    from json import load

    # https://stackoverflow.com/a/2020083
    def get_full_class_name(obj):
        module = obj.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return obj.__class__.__name__
        return module + '.' + obj.__class__.__name__

    c = " If problem persists, a contact email for the server may be listed "
    c = c + "at http://hapi-server.org/servers/"
    msg = '';
    try:
        http = urllib3.PoolManager()
        res = http.request('GET', url, preload_content=False, retries=2)
        if res.status != 200:
            try:
                jres = load(res)
            except Exception as e:
                msg = "Problem with " + url + \
                        ". Server responded with non-200 HTTP status (" \
                        + str(res.status) + \
                        ") and an invalid JSON in response body." + c

            if msg == '' and 'status' in jres:
                if 'message' in jres['status']:
                    msg = '%s\n' % (jres['status']['message'])

            if msg == '':
                msg = "Problem with " + url + \
                      ". Server responded with non-200 HTTP status (" + \
                      str(res.status) + \
                      ") but no JSON without HAPI error message in response body." + c

            raise HAPIError

    except HAPIError:
        error(msg)
    except urllib3.exceptions.NewConnectionError:
        error('Connection error for : ' + url + c)
    except urllib3.exceptions.ConnectTimeoutError:
        error('Connection timeout for: ' + url + c)
    except urllib3.exceptions.MaxRetryError:
        error('Failed to connect to: ' + url + c)
    except urllib3.exceptions.ReadTimeoutError:
        error('Read timeout for: ' + url + c)
    except urllib3.exceptions.LocationParseError:
        error('Could not parse URL: ' + url)
    except urllib3.exceptions.LocationValueError:
        error('Invalid URL: ' + url)
    except urllib3.exceptions.HTTPError as e:
        error('Exception ' + get_full_class_name(e) + " for: " + url)
    except Exception as e:
        print(type(sys.exc_info()[1]).__name__ + ': ' \
              + str(e) + ' for URL: ' + url)

    return res


def urlretrieve(url, fname, check_last_modified=False, **kwargs):
    """Download URL to file

    urlretrieve(url, fname, check_last_modified=False, **kwargs)

    If check_last_modified=True, `fname` is found, URL returns Last-Modfied
    header, and `fname` timestamp is after Last-Modfied timestamp, the URL
    is not downloaded.
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

    dirname = path.dirname(fname)
    if not path.exists(dirname):
        makedirs(dirname)

    with open(fname, 'wb') as out:
        res = urlopen(url)
        shutil.copyfileobj(res, out)
        return res


def modified(url, fname, **kwargs):
    """Check if timestamp on file is later than Last-Modifed in HEAD request"""

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

        if debug:
            print("File Last Modified = %s" % fileLastModified)
            print("URL Last Modified = %s" % urlLastModified)

        if urlLastModified > fileLastModified:
            return True
        return False
    else:
        if debug:
            print("No Last-Modified header. Will re-download")
        # TODO: Read file.head and compare etag
        return True


def urlquote(url):
    """Python 2/3 urlquote compatability function.

    If Python 3, returns
    urllib.parse.quote(url)

    If Python 2, returns
    urllib.quote(url)
    """

    import sys
    if sys.version_info[0] == 2:
        from urllib import quote
        return quote(url)
    import urllib.parse
    return urllib.parse.quote(url)
