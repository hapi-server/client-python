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

       logging (default False) - Log to console
       cache_hapi (default True) - Save downloaded /info responses in ./hapi-data directory
       cache_npbin (default True) - Save downloaded /data responses in ./hapi-data directory
       use_cache (default True) - Use cache files in ./hapi-data directory if found
       serverlist (default https://raw.githubusercontent.com/hapi-server/servers/master/all.txt)
'''
# TODO: Use mark-up for docs: https://docs.python.org/devguide/documenting.html 

"""
Author: R.S Weigel <rweigel@gmu.edu>
License: This is free and unencumbered software released into the public domain.
Repository: https://github.com/hapi-server/python-client.git
"""

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

# https://stackoverflow.com/questions/27674602/hide-traceback-unless-a-debug-flag-is-set
def error(msg):
    #sys.tracebacklimit=0 # Suppress traceback
    raise Exception(msg)
    
# Start compatability code
if sys.version_info[0] > 2:
    # Tested with sys.version = 2.7.15 |Anaconda, Inc.| (default, May  1 2018, 18:37:05) \n[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]
    import urllib.request, urllib.parse, urllib.error
else:
    # Tested with sys.version = 2.7.15 |Anaconda, Inc.| (default, May  1 2018, 18:37:05) \n[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]
    # Tested with sys.version = 3.6.5 |Anaconda, Inc.| (default, Apr 26 2018, 08:42:37) \n[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]
    import urllib
    import urllib2

def urlopen(url):
    try:
        if sys.version_info[0] > 2:
            res = urllib.request.urlopen(url)
        else:
            res = urllib2.urlopen(url)
    except:
        error('Could not open %s' % url)
        
    return res

def urlretrieve(url,fname):
    try:
        if sys.version_info[0] > 2:
            urllib.request.urlretrieve(url, fname)
        else:
            urllib.urlretrieve(url, fname)
    except:
        error('Could not open %s' % url)

# End compatability code

def printf(format, *args): sys.stdout.write(format % args)
    
def hapi(*args,**kwargs):
    
    nin = len(args)
        
    if nin > 0:SERVER = args[0]
    if nin > 1:DATASET = args[1]
    if nin > 2:PARAMETERS = args[2]
    if nin > 3:START = args[3]
    if nin > 4:STOP = args[4]    

    # Default options
    DOPTS = {}
    DOPTS.update({'update_script': False})
    DOPTS.update({'logging': True})
    DOPTS.update({'cache_npbin': True})
    DOPTS.update({'cache_hapi': True})
    DOPTS.update({'cache_dir': os.getcwd() + os.path.sep + 'hapi-data'})
    DOPTS.update({'use_cache': False})
    DOPTS.update({'server_list': 'https://raw.githubusercontent.com/hapi-server/servers/master/all.txt'})
    DOPTS.update({'script_url': 'https://raw.githubusercontent.com/hapi-server/client-python/master/hapi.py'})
    # For testing, change to a different format to force it to be used. 
    # Will use CSV if binary not available
    DOPTS.update({'format': 'binary'})
    DOPTS.update({'method': 'pandas'})

    # Override defaults
    for key, value in kwargs.items():
        if key in DOPTS:
            DOPTS[key] = value
        else:
            printf('Warning: Keyword option "%s" is not valid.', key)
        
    if nin == 0:
        if DOPTS['logging']: printf('Reading %s ... ', DOPTS['server_list'])
        if sys.version_info[0] > 2:
            data = urllib.request.urlopen(DOPTS['server_list']).read().decode('utf8').split('\n')
        else:
            data = urllib2.urlopen(DOPTS['server_list']).read().split('\n')
            
        if DOPTS['logging']: printf('Done.\n')
        # Remove empty items (if blank lines)
        data = [ x for x in data if x ]
        # Display server URLs to console.
        if DOPTS['logging']:
            printf('List of HAPI servers in %s:\n', DOPTS['server_list'])
            for url in data:
                printf("   %s\n", url)
        return data        

    if nin == 1:
        # Could use cache result here.  Probably not needed as catalog
        # metadata requests offline are unlikely to be performed.
        url = SERVER + '/catalog'
        if DOPTS['logging']: printf('Downloading %s ... ', url) 
        res = urlopen(url)
        meta = json.load(res)
        if DOPTS['logging']: printf('Done.\n')
        data = meta
        return meta

    if nin == 2:
        # Could use cached result here.
        url = SERVER + '/info?id=' + DATASET
        if DOPTS['logging']: printf('Downloading %s ... ', url)
        res = urlopen(url)
        meta = json.load(res)
        if DOPTS['logging']: printf('Done.\n')
        data = meta
        return meta

    if nin == 3 or nin == 5:

        urld = re.sub(r"https*://","",SERVER)
        urld = re.sub(r'/','_',urld)
        urld = DOPTS["cache_dir"] + os.path.sep + urld

        if (DOPTS["cache_npbin"] or DOPTS["cache_hapi"] or DOPTS["use_cache"]):
            if nin == 5:
                # Data requested
                fname     = '%s_%s_%s_%s' % (DATASET,re.sub(',','-',PARAMETERS),re.sub(r'-|:|\.|Z','',START),re.sub(r'-|:|\.|Z','',STOP))
                fnamecsv  = urld + os.path.sep + fname + '.csv'
                fnamebin  = urld + os.path.sep + fname + '.bin'
                urlcsv    = SERVER + '/data?id=' + DATASET + '&parameters=' + PARAMETERS + '&time.min=' + START + '&time.max=' + STOP
                urlbin    = urlcsv + '&format=binary'
                fnamenpy  = urld + os.path.sep + fname + '.npy'                

            urljson = SERVER + '/info?id=' + DATASET + '&parameters=' + PARAMETERS
            fname     = '%s_%s' % (DATASET,re.sub(',','',PARAMETERS))
            fnamejson = urld + os.path.sep + fname + '.json'
            fnamepkl  = urld + os.path.sep + fname + '.pkl'                

        if DOPTS["use_cache"]:
            metaloaded = False
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

        if (DOPTS["cache_npbin"] or DOPTS["cache_hapi"]):    
            if not os.path.exists(DOPTS["cache_dir"]):
                os.makedirs(DOPTS["cache_dir"])
            if not os.path.exists(urld):
                os.makedirs(urld)

        if DOPTS['logging']: printf('Downloading %s ... ', urljson)
        res = urlopen(urljson)
        meta = json.load(res)
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

        if DOPTS["cache_hapi"]:
            fnamej = re.sub('.csv','.json',fnamejson)
            if DOPTS['logging']: printf('Writing %s ... ', fnamejson)
            f = open(fnamej, 'w')
            json.dump(meta,f,indent=4)
            f.close
            if DOPTS["logging"]: printf('Done.\n')
    
        if nin == 3:
            return meta

        cformats = ['csv','binary'] # client formats
        if not DOPTS['format'] in cformats:
            raise ValueError('This client does not handle transport format "%s".  Available options: %s' % (DOPTS['format'],', '.join(cformats)))

        if DOPTS['format'] != 'csv':
            res = urlopen(SERVER + '/capabilities')
            caps = json.load(res)
            sformats = caps["outputFormats"] # Server formats       
            if not DOPTS['format'] in sformats:
                warnings.warn('Requested transport format "%s" not avaiable from %s. Will use "csv". Available options: %s' % (DOPTS['format'], SERVER, ', '.join(sformats)))
                DOPTS['format'] = 'csv'

        pnames,psizes,dt = [],[],[]
        cols = np.zeros([len(meta["parameters"]),2],dtype=np.int32)
        ss = 0 # sum of sizes
        missing_length = False

        for i in range(0,len(meta["parameters"])):        
            ptype = str(meta["parameters"][i]["type"])
            pnames.append(str(meta["parameters"][i]["name"]))
            if 'size' in meta["parameters"][i]:
                psizes.append(meta["parameters"][i]['size'])
            else:
                psizes.append(1)

            if False:
                # Interpret size = [1] as meaning same as if size not given
                if type(psizes[i]) is list and len(psizes[i]) == 1 and psizes[i][0] == 1:
                    psizes[i] = 1
                # Interpret size = N (N > 1) as meaning size = [N]
                if type(psizes[i]) is int and psizes[i] > 1:
                    psizes[i] = [psizes[i]]

            # Interpret size = [1] as meaning same as if size not given
            if type(psizes[i]) is list and len(psizes[i]) == 1:
                psizes[i] = psizes[i][0]
                
            cols[i][0] = ss
            cols[i][1] = ss + np.prod(psizes[i]) - 1
            ss = cols[i][1]+1

            if ptype == 'double': dtype = (pnames[i], '<d', psizes[i])
            if ptype == 'integer': dtype = (pnames[i], np.int32, psizes[i])
            
            # length attribute only required for all parameters if 
            # format=binary. 
            if DOPTS['format'] == 'binary':
                if ptype == 'string': dtype = (pnames[i], 'S' + str(meta["parameters"][i]["length"]), psizes[i])
                if ptype == 'isotime': dtype = (pnames[i], 'S' + str(meta["parameters"][i]["length"]), psizes[i])            
            else:
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
            # TODO: Don't write file if cache_npbin == False
            # Use urlopen() or equivalent to read directly into memory.
            if DOPTS['logging']: printf('Downloading %s ... ', urlbin)
            if DOPTS["cache_npbin"]:
                urlretrieve(urlbin, fnamebin)
                if DOPTS['logging']: printf('Done.\n')
                if DOPTS['logging']: printf('Reading %s ... ', fnamebin)
                tic = time.time()
                data = np.fromfile(fnamebin, dtype=dt)
            else:
                from io import BytesIO
                #import pdb; pdb.set_trace()
                fnamebin = BytesIO(urlopen(urlbin).read())                
                if DOPTS['logging']: printf('Done.\n')
                if DOPTS['logging']: printf('xReading %s ... ', fnamebin)
                tic = time.time()
                data = np.frombuffer(fnamebin.read(), dtype=dt)
            if DOPTS['logging']: printf('Done.\n')
            toc = time.time()-tic
        else:
            # HAPI CSV
            if DOPTS['logging']: printf('Downloading %s ... ', urlcsv)
            if DOPTS["cache_npbin"]:
                urlretrieve(urlcsv, fnamecsv)
            else:
                # Don't write file if cache_npbin == False
                from io import StringIO
                fnamecsv = StringIO(urlopen(urlcsv).read().decode())
            if DOPTS['logging']: printf('Done.\n')
            if DOPTS['logging']: printf('Reading %s ... ', fnamecsv)
            #import pdb; pdb.set_trace()
            
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

        meta.update({"x_readTime": toc})
        
        if DOPTS["cache_npbin"]:
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