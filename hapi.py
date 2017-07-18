'''
HAPI - Interface to Heliophysics Data Environment API

   hapi.py is used to get metadata and data from a HAPI v1.1 compliant
   data server (https://github.com/hapi-server/). 

   See hapi_demo.py for usage examples.

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

   Data = HAPI(Server, Dataset, Parameters, Start, Stop) returns a dictionary with
   elements corresponding to Parameters, e.g., if Parameters='scalar,vector' and
   the number of records returned is N, then

   Data['Time'] is a NumPy array of datetimes with shape (N)
   Data['scalar'] is a NumPy array of shape (N)
   Data['vector'] is a NumPy array of shape (N,3)

   Options are set by passing a keywords of

       logging (default False) - Log to console
       cache_hapi (default True) - Save downloaded files in ./hapi-data directory
       use_cache (default True) - Use cache files in ./hapi-data directory if found
       serverlist (default https://raw.githubusercontent.com/hapi-server/data-specification/master/servers.txt)
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
import csv
import json
import urllib
import urllib2
import numpy as np
import pandas
from datetime import datetime
import warnings
 
def hapi(*args,**kwargs):
    
    nin = len(args)
    
    if 'list' in kwargs: nargout = 0
    
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
    DOPTS.update({'use_cache': False})
    DOPTS.update({'server_list': 'https://raw.githubusercontent.com/hapi-server/data-specification/master/servers.txt'})
    DOPTS.update({'script_url': 'https://raw.githubusercontent.com/hapi-server/client-python/master/hapi.py'})
    # For testing, change to a different format to force it to be used. 
    # Will use CSV if binary not available
    DOPTS.update({'format': 'binary'})

    # Override defaults
    for key, value in kwargs.iteritems():
        if key in DOPTS:
            DOPTS[key] = value
        else:
            print 'Warning: Keyword option "%s" is not valid.' % key
        
    if nin == 0:
        if DOPTS['logging']: print 'Reading %s ... ' % DOPTS['server_list'],
        data = urllib2.urlopen(DOPTS['server_list']).read().split('\n')
        if DOPTS['logging']: print 'Done.'
        # Remove empty items (if blank lines)
        data = [ x for x in data if x ]
        # Display server URLs to console.
        if DOPTS['logging']:
            print 'List of HAPI servers in %s:' % DOPTS['server_list']
            for url in data:
                print "   " + url
        return data        

    if nin == 1:
        # Could use cache result here.  Probably not needed as catalog
        # metadata requests offline are unlikely to be performed.
        url = SERVER + '/catalog'
        if DOPTS['logging']: print 'Downloading %s ... ' % url, 
        res = urllib2.urlopen(url)
        meta = json.load(res)
        if DOPTS['logging']: print 'Done.'
        data = meta
        return meta

    if nin == 2:
        # Could use cached result here.
        url = SERVER + '/info?id=' + DATASET
        if DOPTS['logging']: print 'Downloading %s ... ' % url, 
        res = urllib2.urlopen(url)
        meta = json.load(res)
        if DOPTS['logging']: print 'Done.'
        data = meta
        return meta

    if nin == 3 or nin == 5:
    
        if (DOPTS["cache_npbin"] or DOPTS["cache_hapi"] or DOPTS["use_cache"]):
            urld = re.sub(r"https*://","",SERVER)
            urld = re.sub(r'/','_',urld)
            urld = 'hapi-data' + os.path.sep + urld
            if nin == 5:
                fname     = '%s_%s_%s_%s' % (DATASET,re.sub(',','-',PARAMETERS),re.sub(r'-|:|\.|Z','',START),re.sub(r'-|:|\.|Z','',STOP))
                fnamecsv  = urld + os.path.sep + fname + '.csv'
                fnamefcsv = urld + os.path.sep + fname + '.fcsv'
                fnamebin  = urld + os.path.sep + fname + '.bin'
                fnamefbin = urld + os.path.sep + fname + '.fbin'
                urlcsv    = SERVER + '/data?id=' + DATASET + '&parameters=' + PARAMETERS + '&time.min=' + START + '&time.max=' + STOP
                urlfcsv   = urlcsv + '&format=fcsv'
                urlbin    = urlcsv + '&format=binary'
                urlfbin   = urlcsv + '&format=fbinary'
                fnamenpy  = urld + os.path.sep + fname + '.data.npy'                

            urljson = SERVER + '/info?id=' + DATASET + '&parameters=' + PARAMETERS
            fname     = '%s_%s' % (DATASET,re.sub(',','',PARAMETERS))
            fnamejson = urld + os.path.sep + fname + '.json'
            fnamepkl  = urld + os.path.sep + fname + '.data.pickle'                

        if DOPTS["use_cache"]:
            metaloaded = False
            if os.path.isfile(fnamepkl):
                import pickle
                if DOPTS['logging']: print 'Reading %s ... ' % fnamepkl,
                f = open(fnamepkl,'rb')                 
                meta = pickle.load(f) 
                f.close()                       
                if DOPTS['logging']: print 'Done.'
                metaloaded = True
                if nin == 3: return meta
            if metaloaded and os.path.isfile(fnamenpy):
                if DOPTS['logging']: print 'Reading %s ... ' % fnamenpy,
                f = open(fnamenpy,'rb')  
                data = np.load(f)
                f.close()
                if DOPTS['logging']: print 'Done.'
                return data, meta

        if (DOPTS["cache_npbin"] or DOPTS["cache_hapi"]):    
            if not os.path.exists('./hapi-data'):
                os.makedirs('./hapi-data')
            if not os.path.exists(urld):
                os.makedirs(urld)

        if DOPTS['logging']: print 'Downloading %s ... ' % urljson,
        res = urllib2.urlopen(urljson)
        meta = json.load(res)
        if DOPTS['logging']: print 'Done.'
    
        if DOPTS["cache_hapi"]:
            fnamej = re.sub('.csv','.json',fnamejson)
            if DOPTS['logging']: print 'Writing %s ... ' % fnamejson,
            f = open(fnamej, 'w')
            json.dump(meta,f,indent=4)
            f.close
            if DOPTS["logging"]: print 'Done.'
    
        if nin == 3:
            return meta

        cformats = ['csv','binary'] # client formats
        if not DOPTS['format'] in cformats:
            raise ValueError('This client does not handle transport format "%s".  Available options: %s' % (DOPTS['format'],', '.join(cformats)))

        if DOPTS['format'] != 'csv':
            res = urllib2.urlopen(SERVER + '/capabilities')
            caps = json.load(res)
            sformats = caps["outputFormats"] # Server formats       
            if not DOPTS['format'] in sformats:
                warnings.warn('Requested transport format "%s" not avaiable from %s. Will use "csv". Available options: %s' % (DOPTS['format'], SERVER, ', '.join(sformats)))
                DOPTS['format'] = 'csv'

        pnames,psizes,dt = [],[],[]
        cols = np.zeros([len(meta["parameters"]),2],dtype=np.int32)
        ss = 0 # sum of sizes
        for i in xrange(0,len(meta["parameters"])):        
            ptype = str(meta["parameters"][i]["type"])
            pnames.append(str(meta["parameters"][i]["name"]))
            if 'size' in meta["parameters"][i]:
                psizes.append(meta["parameters"][i]['size'])
            else:
                psizes.append(1)

            # Interpret size = [1] as meaning same as if size not given
            if type(psizes[i]) is list and len(psizes[i]) == 1 and psizes[i][0] == 1:
                psizes[i] = 1
            # Interpret size = N (N > 1) as meaning size = [N]
            if type(psizes[i]) is int and psizes[i] > 1:
                psizes[i] = [psizes[i]]
                
            cols[i][0] = ss
            cols[i][1] = ss + np.prod(psizes[i]) - 1
            ss = ss+1

            if ptype == 'double': dtype = (pnames[i], '<d', psizes[i])
            if ptype == 'integer': dtype = (pnames[i], np.int32, psizes[i])
            if DOPTS['format'] == 'binary':
                if ptype == 'string': dtype = (pnames[i],  'S' + str(meta["parameters"][i]["length"]), psizes[i])
                if ptype == 'isotime': dtype = (pnames[i],  'S' + str(meta["parameters"][i]["length"]), psizes[i])
            else:
                if ptype == 'string': dtype = (pnames[i],  object, psizes[i])            
                if ptype == 'isotime': dtype = (pnames[i],  object, 1)
                # TODO: Use length if for CSV.  Will require less memory than
                # if each element is an object.

            dt.append(dtype)

        if DOPTS['format'] == 'binary':
            # HAPI Binary
            if DOPTS['logging']: print 'Downloading %s ... ' % urlbin,
            urllib.urlretrieve(urlbin, fnamebin)
            if DOPTS['logging']: print 'Done.'
            if DOPTS['logging']: print 'Reading %s ... ' % fnamebin,
            data = np.fromfile(fnamebin, dtype=dt)
            if DOPTS['logging']: print 'Done.'
        else:
            # HAPI CSV
            if DOPTS['logging']: print 'Downloading %s ... ' % urlcsv,
            urllib.urlretrieve(urlcsv, fnamecsv)
            if DOPTS['logging']: print 'Done.'
            if DOPTS['logging']: print 'Reading %s ... ' % fnamecsv,

            # Read file into Pandas DataFrame
            df = pandas.read_csv(fnamecsv,sep=',',header=None)

            # Allocate output N-D array (It is not possible to pass dtype=dt
            # as computed to read_csv, so need to create new ND array.)
            data = np.ndarray(shape=(len(df)),dtype=dt)
            for i in xrange(0,len(pnames)):
                shape = np.append(len(data),psizes[i])
                data[pnames[i]] = np.squeeze( np.reshape( df.values[:,np.arange(cols[i][0],cols[i][1]+1)], shape ) )
            if DOPTS['logging']: print 'Done.'

        meta.update({u"x_server": SERVER})
        meta.update({u"x_dataset": DATASET})
        meta.update({u"x_parameters": PARAMETERS})
        meta.update({u"x_time.min": START})
        meta.update({u"x_time.max": STOP})
        meta.update({u"x_requestURL": urlfbin})
        t = datetime.now().isoformat()
        meta.update({u"x_requestDate": t[0:19]})
        meta.update({u"x_requestFile": fnamefbin})
        meta.update({u"x_requestFormat": "fbinary"})

        if DOPTS["cache_npbin"]:
            if DOPTS['logging']: print 'Writing %s ...' % fnamenpy,
            np.save(fnamenpy,data);
            if DOPTS['logging']: print 'Done'

            if DOPTS['logging']: print 'Writing %s ...' % fnamepkl,            
            import pickle
            f = open(fnamepkl,'wb') 
            pickle.dump(meta,f)
            f.close()
            if DOPTS['logging']: print 'Done.'

    return data, meta