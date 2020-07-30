def autoplot(server, dataset, parameters, start, stop, **kwargs):
    """Plot data from a HAPI server using Autoplot.
    
    If not found, autoplot.jar is downloaded an launched. If found, 
    autoplot.jar is updated if server version is newer than cached version.
    
    Example
    -------
    >>> from hapiclient import autoplot
    >>> server = 'http://hapi-server.org/servers/TestData/hapi'
    >>> autoplot(server, 'dataset1', 'scalar,vector', '1970-01-01', '1970-01-02')
    
    Autoplot application launches or its canvas is updated.
    
    The options are the same as that for `hapiplot` with the addition of
    the kwargs
    
    stack : bool [False] Create a stack plot of parameters.

    port : int [8079]
        The port number to use to connect to Autoplot.

    version : string ['devel']
        The version of Autoplot to use. Can be a version string, e.g.,
        'v2018a_11', 'devel', 'latest', or 'nightly'. See 
        <http://autoplot.org/developer#Development_Versions> for a
        description of the difference between versions.

    """
    
    import os
    import re
    import platform
    import subprocess
    
    from hapiclient.util import setopts, log, urlopen, urlretrieve, urlquote
    from hapiclient.hapi import cachedir
        
    opts = {
                'logging': False,
                'cache': True,
                'cachedir': cachedir(),
                'usecache': False,
                'newwindow': False,
                'version': 'devel',
                'port': 8079
            }

    # Override defaults
    opts = setopts(opts, kwargs)

    autoplotserver = "http://localhost:" + str(opts['port']) + "/"

    url = server + "?id=" + dataset + "&parameters=" + parameters
    url = url + "&timerange=" + start + "/" + stop

    serverrunning = False
    try:
        # See if server needs to be started.
        if opts['logging']: log('Trying test. Requesting ' + autoplotserver, opts)
        f = urlopen(autoplotserver)
        res = f.read().decode('utf-8')
        if res.startswith('OK'):
            log('Server running.', opts)
            serverrunning = True
        else:
            log('Server responding but with wrong response to test.', opts)
        f.close()
    except:
        log('Server not running. Will start server.', opts)
        
    print(url)
    if serverrunning:
        # Send request to update GUI.
        try:
            # This won't detect if the version requested matches
            # the version running.
            rurl = autoplotserver + "?uri=" + urlquote("vap+hapi:"+ url)
            if opts['logging']: print("autoplot(): Requesting " + rurl)
            log('Autoplot GUI should be updating.', opts)
            f = urlopen(rurl)
            res = f.read().decode('utf-8')
            if res.startswith('OK'):
                log('Request successful. Autoplot GUI updated.', opts)
                f.close()
                return
            else:
                f.close()
                log('Request unsuccessful.', opts)
                serverrunning = False
        except Exception as e:
            print(e)

    # Request was sent, so return.
    if serverrunning == True: return

    if opts['version'] == 'nightly':
        jarurl = 'https://ci-pw.physics.uiowa.edu/job/autoplot-release/lastSuccessfulBuild/artifact/autoplot/Autoplot/dist/autoplot.jar'
    elif opts['version'] == 'devel':
        jarurl = 'http://autoplot.org/jnlp/devel/autoplot.jar'
    elif opts['version'].startswith('v'):
        jarurl = 'http://autoplot.org/jnlp/'+opts['version']+'/autoplot.jar'
    else:
        opts['version'] = 'latest'
        jarurl = 'http://autoplot.org/jnlp/latest/autoplot.jar'

    try:
       result = subprocess.check_output('java -version', shell=True, stderr=subprocess.STDOUT)
       version = re.sub(r'.*"(.*)".*',r'\1', result.decode().split('\n')[0])
       log("Java version: " + version, opts)
    except:
        # TODO: Automatically download and extract from https://jdk.java.net/14/?
        log("Java is required. See https://www.java.com/en/download/ or https://jdk.java.net/14/", opts)
        return

    jydir = os.path.dirname(os.path.realpath(__file__))
    jarpath = os.path.join(opts['cachedir'], 'jar/autoplot-' + opts['version'] + '.jar')
    jaricon = os.path.join(jydir, 'autoplot.png')

    # Download jar file if needed.
    log('Checking if autoplot.jar needs to be downloaded or updated.', opts)
    urlretrieve(jarurl, jarpath, check_last_modified=True, **opts)
    #download(jarpath, jarurl, **opts)

    com = "java"
    
    if 'darwin' in platform.platform().lower():
        com = com + " -Xdock:icon=" + jaricon
        com = com + ' -Xdock:name="Autoplot"'
    com = com + " -DPORT=" + str(opts['port'])
    com = com + " -DHAPI_DATA=" + opts['cachedir']
    com = com + " -DhapiServerCache=true"
    com = com + " -jar " + jarpath
    com = com + " --noAskParams"
    com = com + " '" + os.path.join(jydir, 'server.jy?uri=')
    com = com + urlquote("vap+hapi:"+ url) + "'"
    com = com + " &"
    if opts['logging']: log("Executing " + com, opts)
    os.system(com)
    # TODO: Show console output?
