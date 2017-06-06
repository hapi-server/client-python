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
# https://github.com/hapi-server/matlab-client

import os
import re
import csv
import json
import urllib
import urllib2
import numpy as np
import pandas

from datetime import datetime

def iso2format(Time,format):

    from datetime import datetime

    allowed = ['Unix']

    if format == 'Unix':
        TimeNew = np.zeros(len(Time),dtype=np.int32)
        currentStr="1970-01-01"
        t1970 = datetime.strptime(currentStr, "%Y-%m-%d").toordinal()-719163
        currentDay= t1970*86400
        i = 0
        for isostr in Time:
             if (isostr[0:10] == currentStr):
                  TimeNew[i] = currentDay + int(isostr[11:13])*3600 + int(isostr[14:16])*60 + float(isostr[17:23])
             else:
                 currentStr = isostr[0:10]
                 t1970 = datetime.strptime(currentStr, "%Y-%m-%d").toordinal()-719163
                 currentDay = t1970*86400
                 TimeNew[i] = currentDay + int(isostr[11:13])*3600 + int(isostr[14:16])*60 + float(isostr[17:23])
        
             i = i + 1
    else:
        print 'timeformat not recognized.  Allowed formats %s' % allowed.split(', ') 

    return TimeNew    

 
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
    DOPTS.update({'script_url': 'https://raw.githubusercontent.com/hapi-server/python-client/master/hapi.py'})
    DOPTS.update({'format': 'binary'}) # Will use CSV if binary not available

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
        # Could use cached result here.
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
       
        strparams = False
        for i in range(len(meta["parameters"])):
            if meta["parameters"][i]["type"] == "string":
                strparams = True

        res = urllib2.urlopen(SERVER + '/capabilities')
        caps = json.load(res)
        formats = caps["outputFormats"]
        
        if (not (DOPTS['format'] in formats)):
            print 'Warning: Requested transport format "%s" not avaiable from %s.  Available options: %s' % (DOPTS['format'], SERVER, ', '.join(formats))

        if (not strparams) and (DOPTS['format'] == 'binary') and ('binary' in formats):
            # HAPI Binary
            if DOPTS['logging']: print 'Downloading %s ... ' % urlbin,
            urllib.urlretrieve(urlbin, fnamebin)
            if DOPTS['logging']: print 'Done.'
            if DOPTS['logging']: print 'Reading %s ... ' % fnamebin,

            dt   = []
            dt.append(('Time', 'S' + str(meta["parameters"][0]["length"]), 1))
            print len(meta["parameters"])
            for i in xrange(1,len(meta["parameters"])):
                name = meta["parameters"][i]["name"]
                size = meta["parameters"][i]["size"][0] # Assumes no N-d structures
                type = meta["parameters"][i]["type"]
                if type == 'double':  typet = (str(name), '<d', size)
                if type == 'integer': typet = (str(name), np.int32, size)
                #if type == 'string': type = (str(name),  'S' + str(meta["parameters"][i]["length"]), size)
                dt.append(typet)
                #import pdb;pdb.set_trace();
            data = np.fromfile(fnamebin, dtype=dt)
            if DOPTS['logging']: print 'Done.'
        else:
            # HAPI CSV
            if DOPTS['logging']: print 'Downloading %s ... ' % urlcsv,
            urllib.urlretrieve(urlcsv, fnamecsv)
            if DOPTS['logging']: print 'Done.'
            if DOPTS['logging']: print 'Reading %s ... ' % fnamecsv,

            dt   = []
            names = ['Time']
            dt.append(('Time', 'S' + str(meta["parameters"][0]["length"]), 1))
            for i in xrange(1,len(meta["parameters"])):
                name = meta["parameters"][i]["name"]
                names.append(str(name))
                size = meta["parameters"][i]["size"][0] # Assumes no N-d structures
                type = meta["parameters"][i]["type"]
                if type == 'double':  type = (str(name), '<d', size)
                if type == 'integer': type = (str(name), np.int32, size)
                #if type == 'string': type = (str(name),  'S' + str(meta["parameters"][i]["length"]), size)
                dt.append(type)

            # Seems like this should work ...
            # df = pandas.read_csv(fnamecsv,dtype=dt,names=names,sep=',')
            # If it worked, is there a way to avoid following copy loop?
            # Can pandas.read_csv output a ndarray?
            #data = np.ndarray(shape=(len(df)),dtype=dt)
            #for i in xrange(0,len(meta["parameters"])):
            #    data[names[i]] = df[names[i]].values

            df = pandas.read_csv(fnamecsv,sep=',')
            datacsv = df.values
            data = np.ndarray(shape=(len(df)),dtype=dt)
            
            data["Time"] = datacsv[:,0]
            cols = np.zeros([len(meta["parameters"]),2],dtype=np.int32)
            ss = 1 # sum of sizes
            for i in xrange(1,len(meta["parameters"])):
                name = str(meta["parameters"][i]["name"])
                cols[i][0] = ss
                # Assumes no N-d structures
                cols[i][1] = ss + meta["parameters"][i]["size"][0] - 1
                type = str(meta["parameters"][i]["type"])
                #import pdb;pdb.set_trace()
                # TODO: Recast base on type
                if (cols[i][0] == cols[i][1]):
                    # TODO: Why is this if statment needed? 
                    # Without special treatment of scalars,
                    # get "could not broadcast input
                    # array from shape (n,1) into shape (n)"
                    data[name] = datacsv[:,cols[i][0]]
                else:
                    data[name] = datacsv[:,np.arange(cols[i][0],cols[i][1]+1)]

            if DOPTS['logging']: print 'Done.'

        meta.update({u"x_server": SERVER})
        meta.update({u"x_dataset": DATASET})
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