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
from datetime import datetime

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
                        
        if (not strparams) and (DOPTS['format'] == 'fbinary') and ('fbinary' in formats):
            # Fast Binary
            if DOPTS['logging']: print 'Downloading %s ... ' % urlfbin,
            urllib.urlretrieve(urlfbin, fnamefbin)
            if DOPTS['logging']: print 'Done.'
    
            if DOPTS['logging']: print 'Reading %s ... ' % fnamefbin,        
            dt   = []
            dt.append(('Time', '<d', 1)) # Time is integer (stored as double) from offset here
            ss = 1 # sum of sizes
            for i in xrange(1,len(meta["parameters"])):
                name = meta["parameters"][i]["name"]
                size = meta["parameters"][i]["size"][0] # Assumes no N-d structures
                type = meta["parameters"][i]["type"]
                if type == 'double':  type = (str(name), '<d', size)
                if type == 'integer': type = (str(name), np.int32, size)
                dt.append(type)
                ss = ss + size

            f = open(fnamefbin, 'rb')
            # This fbinary format has the zerotime and time unit in first 21 bytes.
            # Probably this will change.
            time = f.read(21)
            n = float(time[0]) # 0 = seconds, 1 = milliseconds, etc.
            # TODO: Note strptime ignores time part.
            zt = datetime.strptime(time[1:11], '%Y-%m-%d')
            # zerotime is Proleptic Gregorian ordinal of the date,
            # where January 1 of year 1 has ordinal 1
            # See: https://docs.python.org/2/library/datetime.html            
            zerotime = zt.toordinal()
            
            # TODO: Find better Python date/time parsing library
            hr = float(time[13:14])
            mn = float(time[16:17])
            sc = float(time[19:20])
            
            # Seek to start of data
            f.seek(21, os.SEEK_SET)
            dt = np.dtype(dt)
            data = np.fromfile(f, dt) # Read rest of file
            f.close
            n = 10.**n
            # Fractional Proleptic Gregorian ordinal of the date, where January 1 of year 1 has ordinal 1 
            data['Time'] = zerotime + (hr*60.*60.*n + mn*60.*n + sc*n + data['Time'])/(86400.*n)                        
            # Data structure is
            # data['Time']
            # data['Parameter1']
            # data['Parameter2']
            # etc.
            # TODO: Put fraction time in data['FractionalTime']
            #       and keep data['Time'] unchanged.
            if DOPTS['logging']: print 'Done.'
        elif (not strparams) and (DOPTS['format'] == 'binary') and ('binary' in formats):
            # HAPI Binary
            if DOPTS['logging']: print 'Downloading %s ... ' % urlbin,
            urllib.urlretrieve(urlbin, fnamebin)
            if DOPTS['logging']: print 'Done.'
            # TODO: Insert code from binary_compare.py here
        elif (not strparams) and (DOPTS['format'] == 'fcsv') and ('fcsv' in formats):
            # Fast CSV
            # TODO: Put proper start time here when we decide if/how to do this.
            dt = datetime.strptime('1970-01-01', '%Y-%m-%d')
            zerotime = float(dt.toordinal())
            # TODO: Put proper increment here when we decide if/how to do this.
            ppd = 86400.
            if DOPTS['logging']: print 'Downloading %s ... ' % urlfcsv,
            urllib.urlretrieve(urlfcsv, fnamefcsv)
            if DOPTS['logging']: print 'Done.'
            
            if DOPTS['logging']: print 'Reading %s ... ' % fnamefcsv,
            if DOPTS['logging']: print 'Done.'
            import pandas
            # TODO: Pass data types to read_csv ...
            df = pandas.read_csv(fnamefcsv, sep=',')
            # ... so this is not needed
            datafcsv = df.astype('<d').values

            datafcsv[:,0] = zerotime + datafcsv[:,0]/ppd
            #import pdb;pdb.set_trace()
            cols = np.zeros([len(meta["parameters"]),2],dtype=np.int32)
            ss = 1 # sum of sizes
            data = {}
            data["Time"] = datafcsv[:,0]
            for i in xrange(1,len(meta["parameters"])):
                name = str(meta["parameters"][i]["name"])
                cols[i][0] = ss
                # Assumes no N-d structures
                cols[i][1] = ss + meta["parameters"][i]["size"][0] - 1
                type = str(meta["parameters"][i]["type"])
                # TODO: Recast base on type
                data[name] = datafcsv[:,np.arange(cols[i][0],cols[i][1]+1)]

        else:
            # HAPI CSV
            if DOPTS['logging']: print 'Downloading %s ... ' % urlcsv,
            urllib.urlretrieve(urlcsv, fnamecsv)
            if DOPTS['logging']: print 'Done.'
            if DOPTS['logging']: print 'Reading %s ... ' % fnamecsv,

            name = []
            size = []
            type = []
            name.append("Time")
            type.append("double")
            cols = np.zeros([len(meta["parameters"]),2],dtype=np.int32)
            cols[0,0] = 0
            cols[0,1] = 0            
            ss = 1 # sum of sizes
            for i in xrange(1,len(meta["parameters"])):
                name.append(str(meta["parameters"][i]["name"]))
                cols[i][0] = ss
                # Assumes no N-d structures
                cols[i][1] = ss + meta["parameters"][i]["size"][0] - 1
                type.append(str(meta["parameters"][i]["type"]))
                ss = 1 + cols[i][1]
            
            with open(fnamecsv, 'rb') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=',')
                datalist = list(csvreader)           
            datacsv = np.zeros([len(datalist),ss])
            for i in range(len(datacsv)):
                for j in xrange(1,ss):
                    datacsv[i,j] = float(datalist[i][j])
                    
                dt = datetime.strptime(datalist[i][0], '%Y-%m-%dT%H:%M:%S.%f')
                tt = dt.timetuple()
                datacsv[i,0] = dt.toordinal()
                hr = tt.tm_hour
                mn = tt.tm_min
                sc = tt.tm_sec
                #ms = tt.time_ms Does not exist?!
                fs = re.sub(r'.*\.','','.' + datalist[i][0])
                if (len(fs) > 1):
                    fs = float(fs);
                else:
                    fs = 0.
                sod = 3600*hr + 60*mn + sc + fs; # fractional second of day
                datacsv[i,0] = datacsv[i,0] + float(sod)/86400.

            data = {}
            data["Time"] = datacsv[:,0]
            for i in xrange(1,len(meta["parameters"])):
                # TODO: Recast based on type
                data[name[i]] = datacsv[:,np.arange(cols[i][0],cols[i][1]+1)]

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