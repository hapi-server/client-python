from hapiclient.log import log


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


def unicode_check(DATASET, PARAMETERS):
  if unicode_error_message(DATASET) != "":
    error(unicode_error_message(DATASET))
  if unicode_error_message(PARAMETERS) != "":
    error(unicode_error_message(PARAMETERS))


def fix_parameters(PARAMETERS):
    if PARAMETERS is None:
        return None
    import re
    if re.search(r', ', PARAMETERS):
        msg = "Removing spaces after commas in given parameter list of '"
        warning(msg + PARAMETERS + "'")
        PARAMETERS = re.sub(r',\s+', ',', PARAMETERS)
    return PARAMETERS


def unicode_error_message(name):
    import sys
    msg = ""
    if sys.version_info[0:2] <= (3, 5):
        name = str(name)
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


def urlopen(url, parse_json=False):
    """Wrapper to request.get() in urllib3
    res = urlopen(url) returns the response object from urllib3.

    res = urlopen(url, parse_json=True) return response from url as a Python dict
    by parsing JSON. If JSON cannot be parsed, an error is raised.
    """

    import urllib3

    log('Opening %s' % url)

    # https://stackoverflow.com/a/2020083
    def get_full_class_name(obj):
        module = obj.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return obj.__class__.__name__
        return module + '.' + obj.__class__.__name__

    c = " If problem persists, a contact email for the server may be listed "
    c = c + "at http://hapi-server.org/servers/"
    msg = ''
    try:
        http = urllib3.PoolManager()
        res = http.request('GET', url, preload_content=False, retries=2)
        if res.status != 200:
            msgo = "Problem with " + url + \
                   ". Server responded with non-200 HTTP status (" + \
                   str(res.status) + ") "
            try:
                from json import loads
                jres = loads(res.read().decode('utf-8'))
            except Exception:
                msg = msgo + "and invalid JSON in response body." + c

            if msg == '':
                if 'status' in jres:
                    if 'message' in jres['status']:
                        msg = msgo + 'and error message: %s\n' % (jres['status']['message'])
                    else:
                        msg = msgo + "and no error message in status element of response body." + c
                else:
                    msg = msgo + "and JSON without HAPI status in response body." + c

            raise HAPIError(msg)

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
        import sys
        print(type(sys.exc_info()[1]).__name__ + ': ' + str(e) + ' for URL: ' + url)

    if parse_json:
        log('Parsing and returning JSON from %s' % url)
        from json import loads
        try:
            return loads(res.read().decode('utf-8'))
        except Exception:
            error('Could not parse JSON from %s' % url)

    return res


def urlretrieve(url, fname):
    """Download URL to file atomically.

    res = urlretrieve(url, fname)
    """

    log('Writing')
    log('  %s' % url)
    log('to')
    log('  %s' % fname)
    res = urlopen(url)
    write_atomic(fname, res)

    return res


def subset_meta(meta, params):
    """Extract subset of parameters from meta object returned by hapi().

    ``metar = subset_meta(meta, parameters)`` modifies ``meta["parameters"]`` array
    so that it only contains elements for the time variable and the parameters
    in the comma-separated string ``parameters``.
    """

    if params == '':
        return meta

    p = params.split(',')
    pm = []  # Parameter names in metadata
    for i in range(0, len(meta['parameters'])):
        pm.append(meta['parameters'][i]['name'])

    # Check for parameters requested that are not in metadata
    for i in range(0, len(p)):
        if p[i] not in pm:
            error('Parameter %s is not in meta' % p[i] + '\n')
            return

    pa = [meta['parameters'][0]]  # First parameter is always the time parameter

    params_reordered = []  # Re-ordered params
    # If time parameter explicitly requested, put it first in params_reordered.
    if meta['parameters'][0]['name'] in p:
        params_reordered = [meta['parameters'][0]['name']]

    # Create subset of parameter metadata
    for i in range(1, len(pm)):
        if pm[i] in p:
            pa.append(meta['parameters'][i])
            params_reordered.append(pm[i])
    meta['parameters'] = pa

    params_reordered_str = ','.join(params_reordered)

    if not params == params_reordered_str:
        msg = "\n  " + "Order requested: " + params
        msg = msg + "\n  " + "Order required: " + params_reordered_str
        error('Order of requested parameters does not match order of ' \
              'parameters in server info metadata.' + msg + '\n')

    return meta


def query_name(meta, name):
    """Return the HAPI query parameter name for dataset/start/stop based on server version."""
    if name == 'dataset':
        hapi_version = str(meta.get('HAPI', ''))
        if hapi_version.startswith('3'):
            return 'dataset'
        return 'id'
    elif name == 'start':
        hapi_version = str(meta.get('HAPI', ''))
        if hapi_version.startswith('3'):
            return 'start'
        return 'time.min'
    elif name == 'stop':
        hapi_version = str(meta.get('HAPI', ''))
        if hapi_version.startswith('3'):
            return 'stop'
        return 'time.max'
    else:
        error('Unknown query name: {}'.format(name))


def missing_length(meta, opts):
    """Return True if any string or isotime parameter is missing length attribute in metadata.

    missing_length = True will be set if HAPI String or ISOTime
    parameter has no length attribute in metadata (length attribute is
    required for both in binary but only for primary time column in CSV).
    When missing_length=True the CSV read gets more complicated.
    """
    if opts['format'] == 'csv':
        if opts['method'] == 'numpynolength' or opts['method'] == 'pandasnolength':
            return True

    for param in meta['parameters']:
        if param['type'] in ['string', 'isotime'] and 'length' not in param:
            return True

    return False


def write_atomic(path, data):

  import os
  import json
  import pickle
  import pathlib
  import secrets
  import warnings

  import numpy

  path = pathlib.Path(path)
  path.parent.mkdir(parents=True, exist_ok=True)
  tmp_ext = f".{secrets.token_hex(3)}.tmp"
  tmp_path = path.with_suffix(path.suffix + tmp_ext)

  try:

    if path.suffix == '.json':
      with tmp_path.open('w') as f:
        json.dump(data, f, indent=2)

    if path.suffix == '.pkl':
      with tmp_path.open('wb') as f:
        pickle.dump(data, f, protocol=2)

    if path.suffix == '.npy':
      with warnings.catch_warnings():
        # Ignore warning that occurs when saving Unicode data.
        kwargs = {
            'message': r"Stored array in format 3\.0.*",
            'category': UserWarning,
            'module': r"numpy\.lib\.format"
        }
        warnings.filterwarnings("ignore", **kwargs)
        with tmp_path.open('wb') as f:
          numpy.save(f, data)

    if path.suffix in ('.bin', '.csv'):
      with tmp_path.open('wb') as f:
        if isinstance(data, (bytes, bytearray)):
          f.write(data)
        else:
          # Assume a file-like / streaming response object.
          import shutil
          shutil.copyfileobj(data, f)

    try:
      os.replace(tmp_path, path)
    except Exception as e:
      warning(f"Failed to rename cache file from {tmp_path} to {path}: {e}")

  except Exception as e:
    warning(f"Failed to write cache file {tmp_path}: {e}")
    try:
      tmp_path.unlink()
    except OSError:
        warning(f"Failed to remove temporary cache file {tmp_path}")