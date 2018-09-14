"""
Author: R.S Weigel <rweigel@gmu.edu>
License: This is free and unencumbered software released into the public domain.
Repository: https://github.com/hapi-server/client-python
"""
Version = '0.8.1'

# Written to match style/capabilities/interface of hapi.m at
# https://github.com/hapi-server/client-matlab

import os
import re
import json    
import numpy as np
import pandas
from datetime import datetime
import warnings
import sys
import time

sys.tracebacklimit = 1000 # Turn tracebacklimit back to default

def error(msg):
    print('\n')
    sys.tracebacklimit = 0 # Suppress traceback
    # TODO: The problem with this is that it changes the traceback
    # limit globally.
    raise Exception(msg)
    
# Start compatability code
if sys.version_info[0] > 2:
    # Tested with sys.version = 3.6.5 |Anaconda, Inc.| (default, Apr 26 2018, 08:42:37) \n[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]
    import urllib.request, urllib.parse, urllib.error
else:
    # Tested with sys.version = 2.7.15 |Anaconda, Inc.| (default, May  1 2018, 18:37:05) \n[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]
    import urllib
    import urllib2

def urlerror(e,url):

    def unknown():
        body = e.read().decode('utf8')
        if len(body) > 0:
            error('\n"HTTP %d - %s" returned by %s. Response body:\n%s' % (e.code,e.reason,url,body))
        else:
            error('\n"HTTP %d - %s" returned by %s.' % (e.code,e.reason,url))
        
    try:
        jres = json.load(e)
    except:
        unknown()
            
    if jres['status'] and jres['status']['message']:
        error('\n%s\n  %s\n' % (url,jres['status']['message']))
        if jres['status'] and jres['status']['message']:
            error('\n%s\n  %s\n' % (url,jres['status']['message']))
        else:
            unknown()
    else:
        unknown()
        
def urlopen(url):
    if sys.version_info[0] > 2:
        try:
            res = urllib.request.urlopen(url)
        except urllib.error.URLError as e:
            urlerror(e,url)
    else:
        try:
            res = urllib2.urlopen(url)
        except urllib2.URLError as e:
            urlerror(e,url)

    return res
        
def urlretrieve(url,fname):
    if sys.version_info[0] > 2:
        try:
            urllib.request.urlretrieve(url, fname)
        except urllib.error.URLError as e:
            urlerror(e,url)
    else:
        try:
            urllib.urlretrieve(url, fname)
        except urllib2.URLError as e:
            urlerror(e,url)
# End compatability code

def jsonparse(res):
    try:
        return json.load(res)
    except:
        error('Could not parse JSON from %s' % res.geturl())

def printf(format, *args): sys.stdout.write(format % args)
    
def hapi(*args,**kwargs):

    '''
    HAPI - Interface to Heliophysics Data Environment API
    
       hapi.py is used to get metadata and data from a HAPI v1.1 compliant
       data server (https://github.com/hapi-server/). 
    
       See hapi_demo.py for usage examples.
       
       Tested with Python 2.7 and 3.6 and pacakges shipped with Anaconda.
    
       Servers = HAPI() or HAPI() returns a list of data server URLs from
       https://github.com/hapi-server/data-specification/blob/master/servers.txt
    
       Dataset = HAPI(Server) returns an dictionary of datasets available from a
       URL given by the string Server.  The dictionary structure follows the
       HAPI JSON structure.
    
       Parameters = HAPI(Server, Dataset) returns a dictionary of parameters
       in the string Dataset.  The dictionary structure follows the HAPI JSON
       structure.
    
       Metadata = HAPI(Server, Dataset, Parameters) or HAPI(...) returns metadata
       associated each parameter in the comma-separated string Parameters.
    
       Data = HAPI(Server, Dataset, Parameters, Start, Stop) returns a dictionary 
       with elements corresponding to Parameters, e.g., if 
       Parameters='scalar,vector' and the number of records returned is N, then
    
       Data['Time'] is a NumPy array of datetimes with shape (N)
       Data['scalar'] is a NumPy array of shape (N)
       Data['vector'] is a NumPy array of shape (N,3)
    
       Options are set by passing a keywords of
    
           logging (False) - Log to console
           cache (True) - Save responses and processed responses in cache_dir
           cache_dir (./hapi-data)
           use_cache (True) - Use files in cache_dir if found
           serverlist (https://github.com/hapi-server/servers/raw/master/all.txt)
    '''
    # TODO: Use mark-up for docs: https://docs.python.org/devguide/documenting.html 
    
    nin = len(args)
        
    if nin > 0:SERVER = args[0]
    if nin > 1:DATASET = args[1]
    if nin > 2:PARAMETERS = args[2]
    if nin > 3:START = args[3]
    if nin > 4:STOP = args[4]    

    # Default options
    DOPTS = {}
    DOPTS.update({'logging': False})
    DOPTS.update({'cache': True})
    DOPTS.update({'cache_dir': os.getcwd() + os.path.sep + 'hapi-data'})
    DOPTS.update({'use_cache': False})
    DOPTS.update({'server_list': 'https://github.com/hapi-server/servers/raw/master/all.txt'})
    # For testing force transport format. (CSV used binary not available.)
    DOPTS.update({'format': 'binary'}) # Change to 'csv' to always use CSV.
    # For testing csv read methods. See hapi_test.py for usage.
    DOPTS.update({'method': 'pandas'})

    # Override defaults
    for key, value in kwargs.items():
        if key in DOPTS:
            DOPTS[key] = value
        else:
            printf('Warning: Keyword option "%s" is not valid.', key)

    def update():
        f = urllib.request.urlopen('https://github.com/hapi-server/client-python/raw/master/hapi.py').read().decode('utf8')
        Version2 = re.compile(r'Version = (.*)', re.MULTILINE|re.UNICODE).search(f).group(1)
        if Version2 != Version:
            print('A new version of hapi.py is available at https://github.com/hapi-server/client-python/raw/master/hapi.py')

    if nin == 0: # hapi()
        if DOPTS['logging']: printf('Reading %s ... ', DOPTS['server_list'])
        # Last .encode('utf8') needed to make Python 2 and 3 types match
        data = urlopen(DOPTS['server_list']).read().decode('utf8').split('\n')
        if DOPTS['logging']: printf('Done.\n')
        data = [ x for x in data if x ] # Remove empty items (if blank lines)
        # Display server URLs to console.
        if DOPTS['logging']:
            printf('List of HAPI servers in %s:\n', DOPTS['server_list'])
            for url in data:
                printf("   %s\n", url)
        return data        

    if nin == 1: # hapi(SERVER)
        # TODO: Cache
        url = SERVER + '/catalog'
        if DOPTS['logging']: printf('Downloading %s ... ', url) 
        res = urlopen(url)
        meta = jsonparse(res)
        if DOPTS['logging']: printf('Done.\n')
        data = meta
        return meta

    if nin == 2: # hapi(SERVER,DATASET)
        # TODO: Cache
        url = SERVER + '/info?id=' + DATASET
        if DOPTS['logging']: printf('Downloading %s ... ', url)
        res = urlopen(url)
        meta = jsonparse(res)
        if DOPTS['logging']: printf('Done.\n')
        data = meta
        return meta

    if nin == 3 or nin == 5: 
        # hapi(SERVER,DATASET,PARAMETERS) or 
        # hapi(SERVER,DATASET,PARAMETERS,START,STOP)

        # urld = url directory (cache directory root path)
        urld = re.sub(r"https*://","",SERVER)
        urld = re.sub(r'/','_',urld)
        urld = DOPTS["cache_dir"] + os.path.sep + urld

        urljson   = SERVER + '/info?id=' + DATASET + '&parameters=' + PARAMETERS
        # Metadata files do not need START/STOP
        fname     = '%s_%s' % (DATASET,re.sub(',','',PARAMETERS))
        fnamejson = urld + os.path.sep + fname + '.json'
        fnamepkl  = urld + os.path.sep + fname + '.pkl'                

        if nin == 5: # Data requested
            fname     = '%s_%s_%s_%s' % (DATASET,re.sub(',','-',PARAMETERS),re.sub(r'-|:|\.|Z','',START),re.sub(r'-|:|\.|Z','',STOP))
            fnamecsv  = urld + os.path.sep + fname + '.csv'
            fnamebin  = urld + os.path.sep + fname + '.bin'
            urlcsv    = SERVER + '/data?id=' + DATASET + '&parameters=' + PARAMETERS + '&time.min=' + START + '&time.max=' + STOP
            urlbin    = urlcsv + '&format=binary'
            fnamenpy  = urld + os.path.sep + fname + '.npy'                

        metaloaded = False
        if DOPTS["use_cache"]:
            if os.path.isfile(fnamepkl):
                import pickle
                if DOPTS['logging']: printf('Reading %s ... ', fnamepkl)
                f = open(fnamepkl,'rb')                 
                meta = pickle.load(f) 
                f.close()                       
                if DOPTS['logging']: printf('Done.\n')
                metaloaded = True
                if nin == 3: return meta
            if metaloaded and os.path.isfile(fnamenpy):
                if DOPTS['logging']: printf('Reading %s ... ', fnamenpy)
                f = open(fnamenpy,'rb')  
                data = np.load(f)
                f.close()
                if DOPTS['logging']: printf('Done.\n')
                return data, meta

        if (DOPTS["cache"]):
            # Create cache directory
            if not os.path.exists(DOPTS["cache_dir"]):
                os.makedirs(DOPTS["cache_dir"])
            if not os.path.exists(urld):
                os.makedirs(urld)

        if metaloaded == False:
            if DOPTS['logging']: printf('Downloading %s ... ', urljson)
            res = urlopen(urljson)
            meta = jsonparse(res)
            if DOPTS['logging']: printf('Done.\n')

        meta.update({"x_server": SERVER})
        meta.update({"x_dataset": DATASET})
        meta.update({"x_parameters": PARAMETERS})
        meta.update({"x_metaFile": fnamejson})
        t = datetime.now().isoformat()
        meta.update({"x_requestDate": t[0:19]})
        meta.update({"x_cacheDir": urld})

        if nin == 5:
            meta.update({"x_time.min": START})
            meta.update({"x_time.max": STOP})        
            if DOPTS['format'] == 'binary':
                meta.update({"x_dataFile": fnamebin})
            else:
                meta.update({"x_dataFile": fnamecsv})

        if DOPTS["cache"]:
            if DOPTS['logging']: printf('Writing %s ... ', fnamejson)
            f = open(fnamejson, 'w')
            json.dump(meta,f,indent=4)
            f.close
            if DOPTS["logging"]: printf('Done.\n')
    
        if nin == 3:
            return meta

        cformats = ['csv','binary'] # client formats
        if not DOPTS['format'] in cformats:
            raise ValueError('This client does not handle transport format "%s".  Available options: %s' % (DOPTS['format'],', '.join(cformats)))

        # See if server supports binary
        if DOPTS['format'] != 'csv':
            res = urlopen(SERVER + '/capabilities')
            caps = jsonparse(res)
            sformats = caps["outputFormats"] # Server formats       
            if not DOPTS['format'] in sformats:
                warnings.warn('Requested transport format "%s" not avaiable from %s. Will use "csv". Available options: %s' % (DOPTS['format'], SERVER, ', '.join(sformats)))
                DOPTS['format'] = 'csv'

        pnames,psizes,dt = [],[],[]
        # Each element of cols is an array with start/end column number of
        # parameter.
        cols = np.zeros([len(meta["parameters"]),2],dtype=np.int32)
        ss = 0 # running sum of prod(size)

        # String or ISOTime parameter with no length attribute
        missing_length = False 

        for i in range(0,len(meta["parameters"])):        
            ptype = str(meta["parameters"][i]["type"])
            pnames.append(str(meta["parameters"][i]["name"]))
            if 'size' in meta["parameters"][i]:
                psizes.append(meta["parameters"][i]['size'])
            else:
                psizes.append(1)

            # For size = [N] case, readers want
            # dtype = ('name', type, N) not dtype = ('name', type, [N])
            if type(psizes[i]) is list and len(psizes[i]) == 1:
                psizes[i] = psizes[i][0]
                
            cols[i][0] = ss # First column of parameter
            cols[i][1] = ss + np.prod(psizes[i]) - 1 # Last column of parameter
            ss = cols[i][1]+1

            if ptype == 'double': dtype = (pnames[i], '<d', psizes[i])
            if ptype == 'integer': dtype = (pnames[i], np.int32, psizes[i])
            
            if DOPTS['format'] == 'binary':
                # TODO: If 'length' not available, warn and fall back to CSV.
                # length attribute required for all parameters if format=binary. 
                if ptype == 'string': dtype = (pnames[i], 'S' + str(meta["parameters"][i]["length"]), psizes[i])
                if ptype == 'isotime': dtype = (pnames[i], 'S' + str(meta["parameters"][i]["length"]), psizes[i])            
            else:
                # length attribute may not be given (but must be given for
                # first parameter technically)
                if ptype == 'string' or ptype == 'isotime':
                    if 'length' in meta["parameters"][i]:
                        # length is specified for parameter in metadata. Use it.
                        if ptype == 'string': dtype = (pnames[i], 'S' + str(meta["parameters"][i]["length"]), psizes[i])
                        if ptype == 'isotime': dtype = (pnames[i], 'S' + str(meta["parameters"][i]["length"]), psizes[i])            
                    else:
                        # A string or isotime parameter did not have a length.
                        # Will need to use slower CSV read method.
                        missing_length = True
                        if ptype == 'string': dtype = (pnames[i],  object, psizes[i])            
                        if ptype == 'isotime': dtype = (pnames[i],  object, psizes[i])

            # For testing reader. Force use of slow reader.
            if DOPTS['format'] == 'csv':
                if DOPTS['method'] == 'numpynolength' or DOPTS['method'] == 'pandasnolength':
                    missing_length = True
                    if ptype == 'string': dtype = (pnames[i],  object, psizes[i])            
                    if ptype == 'isotime': dtype = (pnames[i],  object, psizes[i])

            dt.append(dtype)

        # Read the data.
        if DOPTS['format'] == 'binary':
            # HAPI Binary
            if DOPTS["cache"]:
                if DOPTS['logging']: printf('Saving %s ... ', urlbin)
                tic0 = time.time()
                urlretrieve(urlbin, fnamebin)
                toc0 = time.time()-tic0
                if DOPTS['logging']: printf('Done.\n')
                if DOPTS['logging']: printf('Reading %s ... ', fnamebin)
                tic = time.time()
                data = np.fromfile(fnamebin, dtype=dt)
            else:
                from io import BytesIO
                if DOPTS['logging']: printf('Getting %s ... ', urlbin)
                tic0 = time.time()
                fnamebin = BytesIO(urlopen(urlbin).read())
                toc0 = time.time()-tic0
                if DOPTS['logging']: printf('Done.\n')
                if DOPTS['logging']: printf('Reading %s ... ', fnamebin)
                tic = time.time()
                data = np.frombuffer(fnamebin.read(), dtype=dt)
            if DOPTS['logging']: printf('Done.\n')
            toc = time.time()-tic
        else:
            # HAPI CSV
            if DOPTS["cache"]:
                if DOPTS['logging']: printf('Saving %s ... ', urlcsv)
                tic0 = time.time()
                urlretrieve(urlcsv, fnamecsv)
                toc0 = time.time()-tic0
            else:
                from io import StringIO
                if DOPTS['logging']: printf('Getting %s ... ', urlcsv)
                tic0 = time.time()
                fnamecsv = StringIO(urlopen(urlcsv).read().decode())
                toc0 = time.time()-tic0
            if DOPTS['logging']: printf('Done.\n')
            if DOPTS['logging']: printf('Reading %s ... ', fnamecsv)

            if missing_length == False:
                # All string and isotime parameters have a length in metadata
                tic = time.time()                
                if DOPTS['method'] == 'numpy':
                    data = np.genfromtxt(fnamecsv,dtype=dt, delimiter=',')
                    toc = time.time()-tic
                if DOPTS['method'] == 'pandas':
                    # Read file into Pandas DataFrame
                    df = pandas.read_csv(fnamecsv,sep=',',header=None)
        
                    # Allocate output N-D array (It is not possible to pass dtype=dt
                    # as computed to pandas.read_csv pandas dtype is different
                    # from numpy's dtype.)
                    data = np.ndarray(shape=(len(df)),dtype=dt)
        
                    # Insert data from dataframe df columns into N-D array
                    for i in range(0,len(pnames)):
                        shape = np.append(len(data),psizes[i])
                        # In numpy 1.8.2 and Python 2.7, this throws an error for no apparent reason.
                        # Works as expected in numpy 1.10.4
                        data[pnames[i]] = np.squeeze( np.reshape( df.values[:,np.arange(cols[i][0],cols[i][1]+1)], shape ) )

                    toc = time.time()-tic            
            else:                
                # At least one string or isotime parameters does not have a length in metadata
                if DOPTS['method'] == 'numpynolength':
                    tic = time.time()
                    # With dtype='None', the data type is determined automatically
                    table = np.genfromtxt(fnamecsv,dtype=None, delimiter=',', encoding='utf-8')
                    # table is a 1-D array. Each element is a row in the file.
                    # If the data types are not the same for each column, 
                    # the elements are tuples with length equal to the number of
                    # columns.
                    # If the data types are the same for each column, which
                    # will happen if only Time is requested or Time and
                    # a string or isotime parameter is requested, then table
                    # has rows that are 1-D numpy arrays.
                    
                    # Contents of table will be placed into N-D array 'data'.
                    data  = np.ndarray(shape=(len(table)),dtype=dt)

                    # Insert data from table into N-D array
                    if (table.dtype.names == None):
                        if len(pnames) == 1:
                            # Only time parameter requested.
                            #import pdb; pdb.set_trace()
                            data[pnames[0]] = table[:]
                        else:
                            # All columns in table have the same datatype
                            # so table is a 2-D numpy matrix
                            #import pdb; pdb.set_trace()
                            for i in range(0,len(pnames)):
                                shape = np.append(len(data),psizes[i])
                                # In numpy 1.8.2 and Python 2.7, this throws an error for no apparent reason.
                                # Works as expected in numpy 1.10.4
                                data[pnames[i]] = np.squeeze( np.reshape( table[:,np.arange(cols[i][0],cols[i][1]+1)], shape ) )
                    else:
                        # Table is not a 2-D numpy matrix.
                        # Extract each column (don't know how to do this with slicing
                        # notation, e.g., data['varname'] = table[:][1:3]. Instead,
                        # loop over each parameter (pn) and aggregate columns.
                        # Then insert aggregated columns into N-D array 'data'.
                        #import pdb; pdb.set_trace()
                        for pn in range(0,len(cols)):
                            shape = np.append(len(data),psizes[pn])
                            for c in range(cols[pn][0],cols[pn][1]+1):
                                #print('pn = %d; c=%d; cn=%s' % (pn,c,table.dtype.names[c]))
                                if c == cols[pn][0]: # New parameter
                                    tmp = table[ table.dtype.names[c] ]
                                else: # Aggregate
                                    tmp = np.vstack((tmp,table[ table.dtype.names[c] ]))
                            tmp = np.squeeze( np.reshape( np.transpose(tmp), shape ) )
                            data[pnames[pn]] = tmp
                                
                if DOPTS['method'] == 'pandasnolength':
                    tic = time.time()
 
                    # Read file into Pandas DataFrame
                    df = pandas.read_csv(fnamecsv,sep=',',header=None)
        
                    # Allocate output N-D array (It is not possible to pass dtype=dt
                    # as computed to pandas.read_csv, so need to create new ND array.)
                    #print(dt)
                    #import pdb; pdb.set_trace()
                    data = np.ndarray(shape=(len(df)),dtype=dt)
        
                    # Insert data from dataframe into N-D array
                    for i in range(0,len(pnames)):
                        shape = np.append(len(data),psizes[i])
                        # In numpy 1.8.2 and Python 2.7, this throws an error for no apparent reason.
                        # Works as expected in numpy 1.10.4
                        data[pnames[i]] = np.squeeze( np.reshape( df.values[:,np.arange(cols[i][0],cols[i][1]+1)], shape ) )
                                
                # If any of the parameters are strings and do not have an associated 
                # length in the metadata, they will have dtype='O' (object). 
                # These parameters must be converted to have a dtype='SN', where
                # N is the maximum string length. N is determined automatically
                # when using astype('<S') (astype uses largest N needed).
                dt2 = []
                for i in range(0,len(pnames)):
                    if data[pnames[i]].dtype == 'O':
                        dtype = (pnames[i], str(data[pnames[i]].astype('<S').dtype) , psizes[i])
                    else:
                        dtype = dt[i]
                    dt2.append(dtype)        

                # Create new ndarray
                data2 = np.ndarray(data.shape,dt2)                    
                
                for i in range(0,len(pnames)):
                    if data[pnames[i]].dtype == 'O':
                        data2[pnames[i]] = data[pnames[i]].astype(dt2[i][1])
                    else:
                        data2[pnames[i]] = data[pnames[i]]
                        # Save memory by not copying (does this help?)
                        #data2[pnames[i]] = np.array(data[pnames[i]],copy=False)
                                            
                toc = time.time()-tic
            
            if DOPTS['logging']: printf('Done.\n')

        meta.update({"x_downloadTime": toc0})
        meta.update({"x_readTime": toc})
        
        if DOPTS["cache"]:
            if DOPTS['logging']: printf('Writing %s ...', fnamenpy)
            if missing_length == True:
                np.save(fnamenpy,data2)
            else:
                np.save(fnamenpy,data)
            
            if DOPTS['logging']: printf('Done.\n')

            if DOPTS['logging']: printf('Writing %s ...', fnamepkl)            
            import pickle
            f = open(fnamepkl,'wb') 
            pickle.dump(meta,f)
            f.close()
            if DOPTS['logging']: printf('Done.\n')

        if missing_length:
            return data2, meta
        else:
            return data, meta

def hapiplot(data,meta,**kwargs):

    import matplotlib.pyplot as plt 

    #%% Download and import datetick.py 
    # TODO: Incorporate datetick.py into hapiplot.py
    url = 'https://github.com/hapi-server/client-python/raw/master/misc/datetick.py'
    print(url)
    if os.path.isfile('datetick.py') == False and os.path.isfile('misc/datetick.py') == False:
        urlretrieve(url,'datetick.py')
    if os.path.isfile('misc/datetick.py') == True:
        sys.path.insert(0, './misc')

    from datetick import datetick
    
    # Default options
    DOPTS = {}
    DOPTS.update({'logging': False})

    # Override defaults
    for key, value in kwargs.items():
        if key in DOPTS:
            DOPTS[key] = value
        else:
            print('Warning: Keyword option "%s" is not valid.' % key)

    fignums = plt.get_fignums()
    if len(fignums) == 0:
        fignums = [0]
    lastfn = fignums[-1]
    
    try:
        # Will fail if no pandas, if YYY-DOY format and other valid ISO 8601
        # dates such as 2001-01-01T00:00:03.Z
        Time = pandas.to_datetime(data['Time'].astype('U'),infer_datetime_format=True)
    except:
        # Slow and manual parsing.
        Time = hapitime2datetime(data['Time'].astype('U'))
        
    # In the following, the x parameter is a datetime object.
    # If the x parameter is a number, would need to use plt.plot_date()
    # and much of the code for datetick.py would need to be modified.
    for i in range(1,len(meta["parameters"])):
        if meta["parameters"][i]["type"] != "double" and meta["parameters"][i]["type"] != "integer":
            warnings.warn("Plots for types double and integer only implemented.")
            continue

        name = meta["parameters"][i]["name"]
        y = np.asarray(data[name])
    
        if meta["parameters"][i]["fill"]:
            if meta["parameters"][i]["fill"] == 'nan':
                yfill = np.nan
            else:
                yfill = float(meta["parameters"][i]["fill"])  
                #if isnan(yfill),yfill = 'null';,end
        else:
            yfill = 'null'

        if yfill != 'null':
            # Replace fills with NaN for plotting
            # (so gaps shown in lines for time series)
            y[y == yfill] = np.nan;    

        if y.shape[0] < 11:
            props = {'linestyle': 'none','marker': '.','markersize': 16}
        elif y.shape[0] < 101:
            props = {'lineStyle': '-','linewidth': 2, 'marker': '.', 'markersize': 8}
        else:
            props = {}
        plt.figure(lastfn + i)
        plt.clf()
        plt.plot(Time,y,**props)
        plt.gcf().canvas.set_window_title(meta["x_server"] + " | " + meta["x_dataset"] + " | " + name)

        yl = meta["parameters"][i]["name"] + " [" + meta["parameters"][i]["units"] + "]"
        plt.ylabel(yl)
        plt.title(meta["x_server"] + "/info?id=" + meta["x_dataset"] + "&parameters=" + name + "\n", fontsize=10)
        plt.grid()
        datetick('x')
        #import pdb; pdb.set_trace()
        
        fnamepng = re.sub('\.csv|\.bin','.png',meta['x_dataFile'])
        if DOPTS['logging']: printf('Writing %s ... ', fnamepng)
        plt.figure(lastfn + i).savefig(fnamepng,dpi=300) 
        if DOPTS['logging']: printf('Done.\n')

        # Important: This must go after savefig or else the png is blank.
        plt.show()

def hapitime2datetime(Time):

    import time
    import matplotlib.dates as mpl
    from datetime import datetime

    end = len(Time[0])-1
    d = 0
    # Catch case where no trailing Z
    if not re.match(r".*Z$",Time[0]):
        end = len(Time[0])
        d = 1

    tic= time.time()
    dateTime = np.zeros(len(Time),dtype='d')
    (h,hm,hms) = (False,False,False)
    if re.match(r"[0-9]{4}-[0-9]{3}", Time[0]):
        fmt = "%Y-%j"
        to = 9
        if (len(Time[0]) == 12-d):
            h = True
        if (len(Time[0]) == 15-d):
            hm = True
        if (len(Time[0]) >= 18-d):
            hms = True        
    elif re.match(r"[0-9]{4}-[0-9]{2}", Time[0]):
        fmt = "%Y-%m-%d"
        to = 11
        if (len(Time[0]) == 14-d):
            h = True
        if (len(Time[0]) == 17-d):
            hm = True
        if (len(Time[0]) >= 20-d):
            hms = True
    else:
        raise
            
    DS = Time[0][0:to-1]
    DN = float(datetime.strptime(DS, fmt).toordinal())
    for i in range(0,len(Time)):
        if (Time[i][0:to-1] != DS):
            DS = Time[0:to-1]
            DN = float(datetime.strptime(DS, fmt).toordinal()) 
        # TODO: Do different loop for each case for speed
        if hms:
            dateTime[i] = DN + float(Time[i][to:to+2])/24. + float(Time[i][to+3:to+5])/(24.*60.) + float(Time[i][to+6:end])/(24.*3600.)
        elif hm:
            dateTime[i] = DN + float(Time[i][to:to+2])/24. + float(Time[i][to+3:to+5])/(24.*60.)
        elif h:
            dateTime[i] = DN + float(Time[i][to:to+2])/24.
        else:
            dateTime[i] = DN        
        i = i+1
    toc = time.time()-tic
    #print('%.4fs' % toc)
    
    tic= time.time()
    dateTimeString = mpl.num2date(dateTime)
    toc = time.time()-tic
    #print('%.4fs' % toc)
    return dateTimeString

def datetick(dir, **kwargs):
    '''
    datetick('x') or datetick('y') formats the major and minor tick labels
    of the current plot. See 
    https://github.com/hapi-server/client-python/blob/master/misc/datetick_test.py
    for tests and comparison with Matplotlib default auto-formatter

    Example:    
        d1 = dt.datetime(1900, 1, 2)
        d2 = datetime.fromordinal(i + datetime.toordinal(d1))    
        x = np.array([d1, d2], dtype=object)
        y = [0.0,1.0]
        plt.clf()
        plt.plot(x, y)
        datetick('x')
    '''

    # Based on spacepy/plot/utils.py on 07/10/2017, but many additions.
    
    # TODO: Account for leap years instead of using 367, 366, etc.
    # TODO: Use numsize() to determine if figure width and height
    #       will cause overlap when default number major tick labels is used.
    # TODO: If time[0].day > 28, need to make first tick at time[0].day = 28
    #       as needed.
    
    import matplotlib.pyplot as plt 
    from matplotlib.dates import mpl
    from datetime import datetime

    def on_xlims_change(ax): datetick('x',set_cb=False)
    def on_ylims_change(ax): datetick('y',set_cb=False)
    
    def millis(x, pos):
        'The two args are the value and tick position'
        #print x
        #print pos
        return '$%1.1fM' % (x*1e-6)

    def numsize():
        # Not yet used.
        # Returns (width, height) of number '0' in pixels
        # Based on https://stackoverflow.com/q/5320205
        # TODO: numsize(fig,dir) should inspect fig to get used fonts
        # for dir='x' and dir='y' and get bounding box for x and y labels.
        r = plt.figure().canvas.get_renderer()
        t = plt.text(0.5, 0.5, '0')    
        bb = t.get_window_extent(renderer=r)
        w = bb.width
        h = bb.height
        plt.close()
        return (w,h)

    debug = False
    
    axes = plt.gca()
    fig = plt.gcf()
    
    # By default, trigger update of ticks when limits
    # change due to user interaction.
    set_cb = True
    if 'set_cb' in kwargs:
        set_cb = kwargs['set_cb']
    if set_cb == True:
        # Trigger update of ticks when limits change.
        if dir == 'x':
            axes.callbacks.connect('xlim_changed', on_xlims_change)
        else:
            axes.callbacks.connect('ylim_changed', on_ylims_change)
 
    line = axes.lines[0]
    datamin = mpl.date2num(line.get_xdata()[0])
    datamax = mpl.date2num(line.get_xdata()[-1])
    if debug == True:
        print('Data min time: %f' % datamin)
        print('Data max time: %f' % datamax)

    xlim = axes.get_xlim()

    tmin = np.max((xlim[0],datamin))
    tmax = np.min((xlim[1],datamax))
    
    if dir == 'x':
        time = mpl.num2date((tmin,tmax))
    else:
        time = mpl.num2date(axes.get_ylim())
    
    deltaT = time[-1] - time[0]
    nHours = deltaT.days * 24.0 + deltaT.seconds/3600.0
    if debug == True:
        print("Total seconds: %s" % deltaT.total_seconds())

    if deltaT.total_seconds() < .1:
        # < 0.1 second
        # At this level of zoom, would need original datetime data
        # which has not been converted by date2num and then re-plot
        # using integer number of milliseconds. E.g., call
        # plotd(dtobj,y)
        # where
        # t = dtobj converted to milliseconds since first array value
        # plotd() calls
        # plot(t,y)
        # and then makes first label indicate %Y-%m-%dT%H:%M:%S
        if debug == True:
            print(line.get_xdata())
            print("Warning: Cannot create accurate time labels with this time resolution.")
        # This does not locate microseconds.
        from matplotlib.ticker import FuncFormatter
        formatter = FuncFormatter(millis)
        Mtick = mpl.MicrosecondLocator(formatter)
        mtick = mpl.MicrosecondLocator(interval=1000)
        fmt   = mpl.DateFormatter('%M:%S:%f')
        fmt2  = '%Y-%m-%dT%H'
    if deltaT.total_seconds() < 1:
        # < 1 second
        Mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,1)) )
        mtick = mpl.MicrosecondLocator(interval=100000)
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'    
    elif deltaT.total_seconds() < 5:
        # < 5 seconds
        Mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,1)) )
        mtick = mpl.MicrosecondLocator(interval=200000)
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 10:
        # < 10 seconds
        Mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,1)) )
        mtick = mpl.MicrosecondLocator(interval=500000)
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 20:
        # < 20 seconds
        Mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,2)) )
        mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,1)) )
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 30:
        # < 30 seconds
        Mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,5)) )
        mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,1)) )
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60:
        # < 1 minute
        Mtick = mpl.econdLocator(bysecond=list(range(time[0].second,60,10)) )
        mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,2)) )
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*2:
        # < 2 minutes
        Mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,20)) )
        mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,5)) )
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*3:
        # < 3 minutes
        Mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,20)) )
        mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,5)) )
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*5:
        # < 5 minutes
        Mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,30)) )
        mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,10)) )
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*10:
        # < 10 minutes
        Mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,1)) )
        mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,15)) )
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*20:
        # < 20 minutes
        Mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,2)) )
        mtick = mpl.SecondLocator(bysecond=list(range(time[0].second,60,30)) )
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*30:
        # < 30 minutes
        Mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,5)) )
        mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,1)) )
        fmt   = mpl.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*60:
        # < 60 minutes
        Mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,10)) )
        mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,2)) )
        fmt   = mpl.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 2:
        Mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,15)) )
        mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,5)) )
        fmt   = mpl.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 4:
        Mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,20)) )
        mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,5)) )
        fmt   = mpl.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 6:
        Mtick = mpl.HourLocator(byhour=list(range(time[0].hour,24,1)) )
        mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,10)) )
        fmt   = mpl.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 12:
        Mtick = mpl.HourLocator(byhour=list(range(time[0].hour,24,2)) )
        mtick = mpl.MinuteLocator(byminute=list(range(time[0].minute,60,30)) )
        fmt   = mpl.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 24:
        # < 1 day
        Mtick = mpl.HourLocator(byhour=list(range(time[0].hour,24,4)) )
        mtick = mpl.HourLocator(byhour=list(range(time[0].hour,24,1)) )
        fmt   = mpl.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 48:
        # < 2 days
        Mtick = mpl.HourLocator(byhour = [0,3,6,9,12,15,18,21])
        mtick = mpl.HourLocator(byhour = list(range(24)))
        fmt   = mpl.DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif nHours < 72:
        # < 3 days
        Mtick = mpl.HourLocator(byhour = [0,6,12,18])
        mtick = mpl.HourLocator(byhour = list(range(0,24,3)))
        fmt   = mpl.DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif nHours < 96:
        # < 4 days
        Mtick = mpl.HourLocator(byhour = [0,12])
        mtick = mpl.HourLocator(byhour = list(range(0,24,3)))
        fmt   = mpl.DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif deltaT.days < 8:
        Mtick = mpl.DayLocator(bymonthday=list(range(32)))
        mtick = mpl.HourLocator(byhour=list(range(0,24,4)))
        fmt   = mpl.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 16:
        Mtick = mpl.DayLocator(bymonthday=list(range(time[0].day,32,2)))
        mtick = mpl.DayLocator(interval=1)
        fmt   = mpl.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 32:
        Mtick = mpl.DayLocator(bymonthday=list(range(time[0].day,32,4)))
        mtick = mpl.DayLocator(interval=1)
        fmt   = mpl.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 60:
        Mtick = mpl.DayLocator(bymonthday=list(range(time[0].day,32,7)))
        mtick = mpl.DayLocator(interval=2)
        fmt   = mpl.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 183:
        Mtick = mpl.MonthLocator(bymonthday=time[0].day,interval=2)
        mtick = mpl.MonthLocator(bymonthday=time[0].day,interval=1)
        if time[0].day == 1:
            fmt   = mpl.DateFormatter('%Y-%m')
            fmt2  = ''
        else:
            fmt   = mpl.DateFormatter('%Y-%m-%d')
            fmt2  = ''
    elif deltaT.days < 367:
        Mtick = mpl.MonthLocator(bymonth=list(range(1,13,4)),bymonthday=time[0].day)
        if time[0].day == 1:
            mtick = mpl.MonthLocator(bymonthday=time[0].day,interval=1)
            fmt   = mpl.DateFormatter('%Y-%m')
            fmt2  = ''
        else:
            mtick = mpl.MonthLocator(bymonthday=time[0].day,interval=1)
            fmt   = mpl.DateFormatter('%Y-%m-%d')
            fmt2  = ''
    elif deltaT.days < 366*2:
        Mtick = mpl.MonthLocator(bymonth=list(range(1,13,6)),bymonthday=time[0].day)
        mtick = mpl.MonthLocator(bymonthday=time[0].day,interval=1)
        if time[0].day == 1:
            fmt   = mpl.DateFormatter('%Y-%m')
            fmt2  = ''
        else:
            fmt   = mpl.DateFormatter('%Y-%m-%d')
            fmt2  = ''
    elif deltaT.days < 366*8:
        Mtick = mpl.YearLocator()
        mtick = mpl.MonthLocator(bymonth=7)
        fmt   = mpl.DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*15:
        Mtick = mpl.YearLocator(2)
        mtick = mpl.YearLocator(1)
        fmt   = mpl.DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*40:
        Mtick = mpl.YearLocator(5)
        mtick = mpl.YearLocator(1)
        fmt   = mpl.DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*100:
        Mtick = mpl.YearLocator(10)
        mtick = mpl.YearLocator(2)
        fmt   = mpl.DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*200:
        Mtick = mpl.YearLocator(20)
        mtick = mpl.YearLocator(5)
        fmt   = mpl.DateFormatter('%Y')
        fmt2  = ''
    else:
        Mtick = mpl.YearLocator(50)
        mtick = mpl.YearLocator(byyear=10)
        fmt   = mpl.DateFormatter('%Y')
        fmt2  = ''

    # Force first time value to be labeled for axis locator
    xt = axes.get_xticks()
    xl = axes.get_xlim()
    if debug == True:
        print("Default xlim[0]:    %s" % mpl.num2date(xl[0]))
        print("Default xlim[1]:    %s" % mpl.num2date(xl[1]))
        print("Default xticks[0]:  %s" % mpl.num2date(xt[0]))
        print("Default xticks[-1]: %s" % mpl.num2date(xt[-1]))

    fig.canvas.draw()
    xt = np.insert(xt,0,xl[0])
    axes.set_xticks(xt)

    if False:
        print("Start: %s" % mpl.num2date(xl[0]))
        print("Stop:  %s" % mpl.num2date(xl[1]))
        for i in range(0,len(xt)):
            print("Tick: %s" % mpl.num2date(xt[i]))

    fig.canvas.draw() 
    if dir == 'x':
        axes.xaxis.set_major_locator(Mtick)
        axes.xaxis.set_minor_locator(mtick)
        axes.xaxis.set_major_formatter(fmt)
        fig.canvas.draw() # Render new labels so updated for next line
        labels = [item.get_text() for item in axes.get_xticklabels()]
    else:
        axes.yaxis.set_major_locator(Mtick)
        axes.yaxis.set_minor_locator(mtick)
        axes.yaxis.set_major_formatter(fmt)
        fig.canvas.draw() # Render new labels so updated for next line
        labels = [item.get_text() for item in axes.get_yticklabels()]

    labels[0] = '%s\n%s' % (labels[0],datetime.strftime(time[0],fmt2))
    xt = axes.get_xticks()
    time = mpl.num2date(xt)
    if fmt2 != '':
        for i in range(1,len(time)):
            if time[i].year > time[i-1].year:
                labels[i] = '%s\n%s' % (labels[i],datetime.strftime(mpl.num2date(xt[i]),fmt2))
            if deltaT.days > 1 and time[i].month > time[i-1].month:
                labels[i] = '%s\n%s' % (labels[i],datetime.strftime(mpl.num2date(xt[i]),fmt2))
            if nHours < 96 and time[i].day > time[i-1].day:
                labels[i] = '%s\n%s' % (labels[i],datetime.strftime(mpl.num2date(xt[i]),fmt2))
            
    if dir == 'x':            
        axes.set_xticklabels(labels)
    if dir == 'y':            
        axes.set_yticklabels(labels)        