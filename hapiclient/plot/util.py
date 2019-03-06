import warnings
import matplotlib

def setopts(opts, kwargs):

    for key, value in kwargs.items():
        if 'rcParams' in kwargs and key is 'rcParams':
            continue
        if key in opts:
            opts[key] = value
        else:
            warnings.warn('Warning: Ignoring invalid keyword option "%s".' % key, SyntaxWarning)

    # Override or add rcParams
    if 'rcParams' in kwargs:
        for key, value in kwargs['rcParams'].items():
            opts['rcParams'][key] = kwargs['rcParams'][key]

    if opts['backend'] is not 'default':
        try:
            matplotlib.use(opts['backend'], warn=False, force=True)
        except:
            matplotlib.use(matplotlib.get_backend(), warn=False, force=True)
            warnings.warn('Warning: matplotlib(' + opts['backend'] + ') call failed. Using default backend of ' + matplotlib.get_backend(), SyntaxWarning)

    style = opts['style']
    rclib =  matplotlib.style.library
    if style in matplotlib.style.available:
        rcstyle = dict(rclib[style]) # rc parameters for style that differ from default
    else:
        rcstyle = dict(rclib['fast'])
        warnings.warn('style "' + style + '" is not in list of known styles: ' + str(matplotlib.style.available) + '. Using style=fast', SyntaxWarning)

    # Get default rc parameters
    rc = dict(matplotlib.rcParamsDefault)

    # Override default rc value with a style value
    for key in rcstyle:
        rc[key] = rcstyle[key]

    # Override default rc style values with user-provided values
    for key in opts['rcParams']:
        if key in rc: # Is an actual rc parameter
            rc[key] = opts['rcParams'][key]
        else:
            warnings.warn('rc parameter "' + key + '" is not in a known rc parameter.', SyntaxWarning)


    opts['rcParams'] = rc
    return opts