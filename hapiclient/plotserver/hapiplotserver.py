"""
See
  python hapiplotserver.py -h
for usage and hapiplot_server.py for examples.

Test using (will reload when file changes)
  FLASK_ENV=development FLASK_APP=hapiclient.plotserver.hapiplotserver flask run
"""

# Defaults
PORT = 5000
CACHEDIR = '/tmp/hapi-data'
USECACHE = True # Allow user to request cached images
THREADED = True
LOGLEVEL = 'default'
# error: show only errors
# default: show requests and errors
# debug: show requests, errors, and debug messages

import os
import time
import logging
import traceback

from flask import Flask, request, redirect
application = Flask(__name__)

def getviviz(vivizdir, loglevel=LOGLEVEL):
    """Download ViViz web application."""

    from hapiclient.util import system, download

    import shutil
    import zipfile

    url = 'https://github.com/rweigel/viviz/archive/master.zip'
    file = vivizdir + '/viviz-master.zip'
    if shutil.which('git'):
        code, stderr, stdout = system('git clone https://github.com/rweigel/viviz.git ' + vivizdir + '/viviz')
        if loglevel == 'debug': print(code, stderr, stdout)
    else:
        download(file, url)
        zipref = zipfile.ZipFile(file, 'r')
        zipref.extractall(vivizdir)
        zipref.close()

def catalog(server, dataset, **kwargs):

    import shutil
    import json

    from hapiclient.hapi import hapi
    from hapiclient.hapi import server2dirname

    cachedir = kwargs['cachedir'] if 'cachedir' in kwargs else CACHEDIR
    usecache = kwargs['usecache'] if 'usecache' in kwargs else USECACHE
    loglevel = kwargs['loglevel'] if 'loglevel' in kwargs else LOGLEVEL

    indexjs = cachedir + '/viviz/index.js'

    fname = server2dirname(server) + '_' + dataset + '.json'
    catalogabs = cachedir + '/viviz/catalogs/' + fname
    catalogrel = 'catalogs/' + fname

    meta = hapi(server, dataset)

    gallery = {
                'id': server,
                 'aboutlink': server,
                 'strftime': "time.min=$Y-$m-$dT00:00:00.000Z&time.max=$Y-$m-$dT23:59:59.999Z",
                 'start': meta['startDate'],
                 'stop': meta['stopDate'],
                 'fulldir': ''
                }

    galleries = []
    for parameter in meta['parameters']:
        p = parameter['name']
        fulldir = "/?server=" + server + "&id=" + dataset + "&parameters=" + p + "&usecache=" + str(usecache).lower() + "&format=png&"
        galleryc = gallery.copy()
        galleryc['fulldir'] = fulldir
        galleryc['id'] = p
        galleryc['aboutlink'] = server + "/info?id=" + dataset
        galleries.append(galleryc)

    indexjs_original = indexjs.replace(".js","-original.js")
    if not os.path.isfile(indexjs_original):
        shutil.copyfile(indexjs, indexjs_original)
    else:
        shutil.copyfile(indexjs_original, indexjs)

    if loglevel == 'debug': print('Writing ' + catalogabs)
    with open(catalogabs, 'w') as f: json.dump(galleries, f, indent=4)

    if loglevel == 'debug': print('hapiplotserver.catalog(): Appending to ' + indexjs)
    with open(indexjs,'a') as f: f.write('\nVIVIZ["config"]["catalogs"]["%s"] = {};\n' % server)
    with open(indexjs,'a') as f: f.write('VIVIZ["config"]["catalogs"]["%s"]["URL"] = "%s";\n' % (server, catalogrel))

def image(server, dataset, parameters, start, stop, **kwargs):

    from hapiclient.hapi import hapi
    from hapiclient.hapiplot import hapiplot
    from hapiclient.hapiplot import imagepath

    cachedir = kwargs['cachedir'] if 'cachedir' in kwargs else CACHEDIR
    usecache = kwargs['usecache'] if 'usecache' in kwargs else USECACHE
    loglevel = kwargs['loglevel'] if 'loglevel' in kwargs else LOGLEVEL
    figsize = kwargs['figsize'] if 'figsize' in kwargs else (7,3)
    format = kwargs['format'] if 'format' in kwargs else 'png'
    dpi = kwargs['dpi'] if 'dpi' in kwargs else 144
    transparent = kwargs['transparent'] if 'transparent' in kwargs else False

    logging = False
    if loglevel == 'debug': logging = True

    def errorimage(figsize, format, dpi, message):

        import re
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

        j = 0
        msg = message
        for i in range(0,len(message)):
            if message[i].startswith("  File"):
                j = i
        if j > 0:
            msg = re.sub(r'.*\/.*\/(.*)',r'\1',message[j]).strip()
            msg = msg.replace('"','').replace(',','')
            msg = msg + ":"
            for k in range(j+1, len(message)):
                if message[k].strip() != '':
                    msg = msg + "\n" + message[k].strip()

        #import pdb;pdb.set_trace()

        fig = Figure(figsize=figsize)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.plot([0,0], [0,0])
        ax.set(ylim=(-1,1),xlim=(-1,1))
        ax.set_axis_off()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        #ax.set_facecolor('red')
        #fig.patch.set_facecolor('red')

        ax.text(-1,1, msg,
                verticalalignment='top',
                horizontalalignment='left')
        #fig.tight_layout()
        from io import BytesIO
        figdataObj = BytesIO()
        canvas.print_figure(figdataObj, format=format, facecolor='red', bbox_inches='tight', dpi=dpi)
        figdata = figdataObj.getvalue()
        return figdata

    if usecache:
        opts = {'cachedir': cachedir, 'format': format, 'figsize': figsize, 'dpi': dpi, 'transparent': transparent}
        fnameimg = imagepath(server, dataset, parameters, start, stop, **opts)
        if os.path.isfile(fnameimg):
            if loglevel == 'debug': print('hapiplotserver.image(): Returning cached image from ' + fnameimg)
            with open(fnameimg, "rb") as f:
                return f.read()
    try:
        tic = time.time()
        opts = {'logging': logging, 'cachedir': cachedir, 'usecache': usecache}
        data, meta = hapi(server, dataset, parameters, start, stop, **opts)
        if loglevel == 'debug': print('hapiplotserver.image(): Time for hapi() call = %f' % (time.time()-tic))
    except Exception as e:
        print(traceback.format_exc())
        message = traceback.format_exc().split('\n')
        return errorimage(figsize, format, dpi, message)

    try:
        tic = time.time()
        popts = {'logging': logging, 'cachedir': cachedir, 'returnimage': True, 'transparent': transparent, 'usecache': usecache, 'returnformat': format, 'figsize': figsize, 'dpi': dpi}
        img = hapiplot(data, meta, **popts)
        if loglevel == 'debug': print('hapiplotserver.image(): Time for hapiplot() call = %f' % (time.time()-tic))
        if not img:
            return errorimage(figsize, format, dpi, "hapyplot.py cannot plot parameter " + parameters)
        else:
            return img
    except Exception as e:
        print(traceback.format_exc())
        message = traceback.format_exc().split('\n')
        return errorimage(figsize, format, dpi, message)

@application.route("/favicon.ico")
def favicon():
    from flask import send_from_directory
    indexdir = os.path.abspath(os.path.dirname(__file__))
    if request.args.get('server') is None:
        return send_from_directory(indexdir + "/", "favicon.ico")

@application.route("/")
def main():

    from hapiclient import hapi

    from flask import send_from_directory
    indexdir = os.path.abspath(os.path.dirname(__file__))
    if request.args.get('server') is None:
        return send_from_directory(indexdir + "/", "index.html")

    loglevel = application.config['loglevel']

    format = request.args.get('format')
    if format is None:
        format = 'png'

    if format == 'png':
        ct = {'Content-Type': 'image/png'}
    elif format == 'pdf':
        ct = {'Content-Type': 'application/pdf'}
    elif format == 'svg':
        ct = {'Content-Type': 'image/svg+xml'}
    else:
        ct = {'Content-Type': 'text/html'}

    server = request.args.get('server')
    if server is None:
        return 'A server argument is required, e.g., /?server=...', 400, {'Content-Type': 'text/html'}

    dataset = request.args.get('id')
    if dataset is None:
        return 'A dataset argument is required, e.g., /?server=...&id=...', 400, {'Content-Type': 'text/html'}

    parameters = request.args.get('parameters')
    if parameters is None and format != 'gallery':
        return 'A parameters argument is required if format != "gallery", e.g., /?server=...&id=...&parameters=...', 400, {'Content-Type': 'text/html'}

    start = request.args.get('time.min')
    if start is None and format != 'gallery':
        return 'A time.min argument is required if format != "gallery", e.g., /?server=...&id=...&parameters=...', 400, {'Content-Type': 'text/html'}

    stop = request.args.get('time.max')
    if start is None and format != 'gallery':
        return 'A time.max argument is required if format != "gallery", e.g., /?server=...&id=...&parameters=...', 400, {'Content-Type': 'text/html'}

    meta = None
    if start is None:
        try:
            meta = hapi(server, dataset)
            start = meta['startDate']
        except Exception as e:
            return 'Could not get metadata from ' + server, 400, {'Content-Type': 'text/html'}

    if stop is None:
        if meta is None:
            try:
                meta = hapi(server, dataset)
            except Exception as e:
                return 'Could not get metadata from ' + server, 400, {'Content-Type': 'text/html'}
        stop = meta['stopDate']

    usecache = request.args.get('usecache')
    if usecache is None:
        usecache = True
    elif usecache.lower() == "true":
        usecache = True
    elif usecache.lower() == "false":
        usecache = False
    else:
        return 'usecache must be true or false', 400, {'Content-Type': 'text/html'}

    if application.config['usecache'] == False and usecache == True:
        usecache = False
        if loglevel == 'debug': print('Application configuration has usecache=False so request to use cache is ignored.')

    transparent = request.args.get('transparent')
    if transparent is None:
        transparent = True
    elif transparent.lower() == "true":
        transparent = True
    elif transparent.lower() == "false":
        transparent = False
    else:
        return 'transparent must be true or false', 400, {'Content-Type': 'text/html'}

    dpi = request.args.get('dpi')
    if dpi is None:
        dpi = 300
    else:
        dpi = int(dpi)
        if dpi > 1200 or dpi < 1:
            return 'dpi must be <= 1200 and > 1', 400, {'Content-Type': 'text/html'}

    figsize = request.args.get('figsize')
    if figsize is None:
        figsize = (7,3)
    else:
        figsizearr = figsize.split(',')
        figsize = (float(figsizearr[0]),float(figsizearr[1]))
        # TODO: Set limits on figsize?

    id = ""
    if parameters is not None:
        id = "&id=" + parameters.split(",")[0]
    else:
        meta = hapi(server,dataset)
        # Set first parameter show to be first in dataset (if this is
        # not done the time variable is the first parameter shown, which
        # is generally not wanted.)
        id = "&id=" + meta['parameters'][1]['name']

    cachedir = application.config['cachedir']

    vivizdir = cachedir + "/viviz"
    if format == 'gallery':
        if not os.path.exists(vivizdir):
            if loglevel == 'debug': print('hapiplotserver.main(): Downloading ViViz to ' + cachedir)
            getviviz(cachedir, loglevel=loglevel)
        else:
            if loglevel == 'debug': print('hapiplotserver.main(): Found ViViz at ' + vivizdir)

        opts = {'cachedir': cachedir, 'usecache': usecache, 'loglevel': loglevel}
        catalog(server, dataset, **opts)
        return redirect("viviz#catalog="+server+id, code=302)

    # Plot options
    opts = {'cachedir': cachedir, 'usecache': usecache, 'loglevel': loglevel, 'format': format, 'figsize': figsize, 'dpi': dpi, 'transparent': transparent}

    img = image(server, dataset, parameters, start, stop,  **opts)
    #print(traceback.format_exc())

    #import pdb;pdb.set_trace()
    if type(img) == Exception:
        return img.message, 400, {'Content-Type': 'text/html'}
    else:
        return img, 200, ct

@application.route("/viviz")
def vivizx():
    return redirect("viviz/", code=301)

@application.route("/viviz/")
def viviz():
    from flask import send_from_directory
    cachedir = application.config['cachedir']
    #print("Sending " + cachedir + "/" + "viviz/index.htm")
    return send_from_directory(cachedir+"/viviz","index.htm")

@application.route('/<path:path>')
def static_proxy(path):
    from flask import send_from_directory
    cachedir = application.config['cachedir']
    # Force these file to not be cached by brower.
    if path == 'viviz/index.js' or '.json' in path:
        return send_from_directory(cachedir, path, cache_timeout=0)
    else:
        return send_from_directory(cachedir, path)

def config(**kwargs):
    application.config['port'] = kwargs['port'] if 'port' in kwargs else PORT
    application.config['cachedir'] = kwargs['cachedir'] if 'cachedir' in kwargs else CACHEDIR
    application.config['usecache'] = kwargs['usecache'] if 'usecache' in kwargs else USECACHE
    application.config['loglevel'] = kwargs['loglevel'] if 'loglevel' in kwargs else LOGLEVEL
    application.config['threaded'] = kwargs['threaded'] if 'threaded' in kwargs else THREADED

    # TODO: Add log to file option.
    # https://gist.github.com/ivanlmj/dbf29670761cbaed4c5c787d9c9c006b
    if application.config['loglevel'] == 'error':
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

# Entry point for Python script.
# See hapiplotserver_test.py for usage examples.
def hapiplotserver(**kwargs):

    config(**kwargs)
    port = application.config['port']
    threaded = application.config['threaded']

    url = 'http://127.0.0.1:'+str(port)+"/"
    print(' * Starting server for ' + url)
    print(' * \033[0;34mSee ' + url + ' for API description.\033[0m')
    print(' * Cache directory: ' + application.config['cachedir'])
    application.run(port=port, threaded=threaded)

# Entry point for command line.
#   python hapiplotserver.py
#       --port PORT --cachedir CACHEDIR --loglevel [--threaded]
if __name__ == "__main__":

    desc="""
Plot data from a HAPI server.

    Usage:
      python hapiplotserver.py [options]
    using the options listed above.

    Run using multiple threads with gunicorn and -w, e.g.,
      gunicorn -w 4 -b 127.0.0.1:5000 'hapiplotserver:gunicorn()'

    Note that the command line options must be passed as keywords when
    gunicorn is used and only a subset of options are allowed, e.g.,
      gunicorn ... 'hapiplotserver:gunicorn(port=5000, cachedir="/tmp/hapi-data", loglevel="default")'

    """
    import sys
    import optparse

    parser = optparse.OptionParser(add_help_option=False)

    parser.add_option('-h', '--help', dest='help', action='store_true', help='show this help message and exit')

    parser.add_option("--port", help="Server port " + "[%s]" % PORT, default=PORT)
    parser.add_option("--cachedir", help="Cache directory " + "[%s]" % CACHEDIR, default=CACHEDIR)
    parser.add_option("--loglevel", help="Log level " + "(error, default, debug) [%s]" % LOGLEVEL, default=LOGLEVEL)
    parser.add_option("--threaded", type="int", help="Run each request in separate thread (0=no or 1=yes) " + "[%s]" % int(THREADED), default=int(THREADED))
    parser.add_option("--usecache", type="int", help="Use cached data and images (0=no or 1=yes) " + "[%s]" % int(USECACHE), default=int(USECACHE))

    (options, args) = parser.parse_args()

    if options.help:
        parser.print_help()
        print(desc)
        sys.exit(0)

    opts = {'port': options.port,
            'cachedir': options.cachedir,
            'usecache': bool(options.usecache),
            'loglevel': options.loglevel,
            'threaded': bool(options.threaded)
            }
    hapiplotserver(**opts)

def gunicorn(**kwargs):
    cachedir = kwargs['cachedir'] if 'cachedir' in kwargs else CACHEDIR
    usecache = kwargs['usecache'] if 'usecache' in kwargs else USECACHE
    loglevel = kwargs['loglevel'] if 'loglevel' in kwargs else LOGLEVEL
    # TODO: Look for invalid keywords and warn.

    opts = {'cachedir': cachedir, 'usecache': usecache, 'loglevel': loglevel}
    config(**opts)
    return application
