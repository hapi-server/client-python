# Important:
# pip install click==7.0
# after pip install flask
# click 7.0 fixes
# https://stackoverflow.com/questions/47820040/using-click-library-in-jupyter-notebook-cell
# (monkey patch listed did not work with click 6.7)

import urllib
import time
from PIL import Image

from hapiclient import hapiplotserver

if False:
    # Run in separate thread.
    # Note that it is not easy to terminate a thread, so multiprocessing
    # is used in gallery().
    from threading import Thread
    kwargs = {'port': 5001, 'loglevel': 'default'}
    thread = Thread(target=hapiplotserver, kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()

if False:
    # Run in main thread
    kwargs = {'port': 5001, 'loglevel': 'default'}
    hapiplotserver(**kwargs)
    # Then open http://127.0.0.1:5001/

if True:
    from multiprocessing import Process
    
    kwargs = {'port': 5002, 'loglevel': 'debug'}
    process = Process(target=hapiplotserver, kwargs=kwargs)
    process.start()
    print(" * Sleeping for 1 second while server starts.")
    time.sleep(1)

    try:
        if False:
            url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&parameters=Time&time.min=1970-01-01Z&time.max=1970-01-02T00:00:00Z&format=png&usecache=False'
            Image.open(urllib.request.urlopen(url)).show()
        
        if False:
            url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&parameters=scalar&time.min=1970-01-01Z&time.max=1970-01-01T00:00:11Z&format=png&usecache=False'
            Image.open(urllib.request.urlopen(url)).show()

        if False:            
            url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=https://cdaweb.gsfc.nasa.gov/hapi&id=AC_H0_MFI&parameters=Magnitude&time.min=2001-01-01T05:00:00&time.max=2001-01-01T06:00:00&format=png&usecache=False'
            Image.open(urllib.request.urlopen(url)).show()
    
        import webbrowser
        if False:
            url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&format=gallery'
            print(' * Opening in browser tab:')
            print(' * ' + url)
    
        if True:
            url = 'http://127.0.0.1:'+str(kwargs['port'])+'/?server=http://hapi-server.org/servers/TestData/hapi&id=dataset1&parameters=scalar&usecache=false&format=gallery'
            print(' * Opening in browser tab:')
            print(' * ' + url)
    
            webbrowser.open(url, new=2)        
    except Exception as e:
        print(e)
        print("Terminating server.")
        process.terminate()
    
    input("Press Enter to terminate server.")
    print("Terminating server ...")
    process.terminate()
    print("Server terminated.")
