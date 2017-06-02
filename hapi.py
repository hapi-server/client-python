"""
Author: R.S Weigel <rweigel@gmu.edu>
License: This is free and unencumbered software released into the public domain.
Repository: https://github.com/hapi-server/python-client.git
"""

# Written to match style/capabilities/interface of
# https://github.com/hapi-server/matlab-client

import os
import re
import json
import urllib
import urllib2
import numpy as np
from datetime import datetime

    
def hapi(*args,**kwargs):
    
    nin = len(args)
    
    if 'list' in kwargs: nargout = 0
    #nargout = 0
    
    nin = len(args)
    if nin > 0:SERVER = args[0]
    if nin > 1:DATASET = args[1]
    if nin > 2:PARAMETERS = args[2]
    if nin > 3:START = args[3]
    if nin > 4:STOP = args[4]    

    DOPTS = {}
    DOPTS.update({'update_script': False})
    DOPTS.update({'logging': True})
    DOPTS.update({'cache_npbin': True})
    DOPTS.update({'cache_hapi': True})
    DOPTS.update({'use_cache': False})
    DOPTS.update({'server_list': 'https://raw.githubusercontent.com/hapi-server/data-specification/master/servers.txt'})
    DOPTS.update({'script_url': 'https://raw.githubusercontent.com/hapi-server/python-client/master/hapi.py'})
    DOPTS.update({'use_binary': True})
    
    #nin = 0
    
    if nin == 0:
        if DOPTS['logging']:
            print 'Reading %s ... ' % DOPTS['server_list'],
        url = 'https://raw.githubusercontent.com/hapi-server/data-specification/master/servers.txt'
        data = urllib2.urlopen(url).read().split('\n')
        if DOPTS['logging']: print 'Done.'
        data = [ x for x in data if x ]
        if DOPTS['logging'] or nargout == 0:
            print 'List of HAPI servers in %s:' % DOPTS['server_list']
            for url in data:
                print url
        return data        

    if nin == 2:
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
            if (nin == 5):
                fname     = '%s_%s_%s_%s' % (DATASET,re.sub(',','-',PARAMETERS),re.sub(r'-|:|\.|Z','',START),re.sub(r'-|:|\.|Z','',STOP))
                fnamecsv  = urld + os.path.sep + fname + '.csv'
                fnamenpy  = urld + os.path.sep + fname + '.data.npy'
                fnamebin  = urld + os.path.sep + fname + '.bin'
                fnamefbin = urld + os.path.sep + fname + '.fbin'
                urlcsv    = SERVER + '/data?id=' + DATASET + '&parameters=' + PARAMETERS + '&time.min=' + START + '&time.max=' + STOP
                urlfbin   = urlcsv + '&format=fbinary'
                urlbin    = urlcsv + '&format=binary'
                
            urljson = SERVER + '/info?id=' + DATASET + '&parameters=' + PARAMETERS
            fnamejson = '%s_%s' % (DATASET,re.sub(',','',PARAMETERS))
            fnamejson = urld + os.path.sep + fnamejson + '.fbin'

        if (DOPTS["cache_npbin"] or DOPTS["cache_hapi"]):    
            if not os.path.exists('./hapi-data'):
                os.makedirs('./hapi-data')
            if not os.path.exists(urld):
                os.makedirs(urld)

        if DOPTS['logging']: print 'Downloading %s ... ' % urljson, 
        res = urllib2.urlopen(urljson)
        meta = json.load(res)
        if DOPTS['logging']: print 'Done.',        
    
        if DOPTS["cache_hapi"]:
            fnamej = re.sub('.csv','.json',fnamejson)
            f = open(fnamej, 'w')
            json.dump(meta,f,indent=4)
            f.close
            if DOPTS["logging"]: print 'Wrote %s ...\n' % fnamejson,
    
        if nin == 3:
            data = meta
            return
       
        #if (DOPTS["use_cache"]):
           # Read .json and .npy files and return

        #if DOPTS['use_binary']:
            # Determine if server supports binary
            
        if DOPTS['use_binary']:
            if DOPTS['logging']: print 'Downloading %s ... ' % urlfbin,
            urllib.urlretrieve(urlfbin, fnamefbin)
            if DOPTS['logging']: print 'Done'
    
            if DOPTS['logging']: print 'Reading %s ... ' % fnamefbin,        
            f = open(fnamefbin, 'rb')
            time = f.read(21)
            n = int(time[0])
            dt = datetime.strptime(time[1:20], '%Y-%m-%dT%H:%M:%S')
            zerotime = dt.toordinal()
            f.seek(21, os.SEEK_SET)
            data = np.fromfile(f, dtype=np.dtype('<d'))
            f.close
            size = 1 + meta["parameters"][1]["size"][0]
            data = np.reshape(data, [len(data) / size, size])
            data[:, 0] = zerotime + data[:, 0] / (864000.0 * 10.0 ** (3.0 * n))
            if DOPTS['logging']: print 'Done',
    
        if DOPTS["cache_npbin"]:
            np.save(fnamenpy,data);
            meta.update({u"x_requestURL": urlfbin})
            t = datetime.now().isoformat()
            meta.update({u"x_requestDate": t[0:19]})
            meta.update({u"x_requestFile": fnamefbin})
            meta.update({u"x_requestFormat": "fbinary"})
            fnamemeta = re.sub('data.npy','.meta.json',fnamenpy)
            f = open(fnamemeta, 'w')
            json.dump(meta,f,indent=4)
            f.close  

    return data, meta