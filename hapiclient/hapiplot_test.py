# returnimage=False for timeseries and spectra only
if True:
    from hapiclient import hapi
    from hapiclient import hapiplot

    server     = 'http://hapi-server.org/servers/TestData/hapi'
    dataset    = 'dataset1'
    parameters = 'scalar,spectra'
    start      = '1970-01-01Z'
    stop       = '1970-01-01T00:00:11Z'
    opts       = {'logging': True, 'usecache': False}

    data, meta = hapi(server, dataset, parameters, start, stop, **opts)
    hapiplot(data, meta, **opts)

# returnimage=True for timeseries and spectra only
if False:
    import io
    from PIL import Image

    from hapiclient import hapi
    from hapiclient import hapiplot

    server     = 'http://hapi-server.org/servers/TestData/hapi'
    dataset    = 'dataset1'
    start      = '1970-01-01Z'
    stop       = '1970-01-01T00:00:11Z'
    parameters = 'scalar'
    opts       = {'logging': False, 'usecache': True}    
    popts      = {'usecache': False, 'logging': True, 'returnimage':True}

    parameters = 'scalar'
    data, meta = hapi(server, dataset, parameters, start, stop, **opts)
    img = hapiplot(data, meta, **popts)    
    Image.open(io.BytesIO(img)).show()

    parameters = 'spectra'
    data, meta = hapi(server, dataset, parameters, start, stop, **opts)
    img = hapiplot(data, meta, **popts)
    Image.open(io.BytesIO(img)).show()
 
# All TestData parameters
if False:
    from hapiclient import hapi
    from hapiclient import hapiplot

    server     = 'http://hapi-server.org/servers/TestData/hapi'
    dataset    = 'dataset1'
    start      = '1970-01-01Z'
    stop       = '1970-01-01T00:00:11Z'

    meta0 = hapi(server,dataset)
    
    opts = {'logging': True, 'usecache': False}

    for i in range(0,len(meta0['parameters'])):
        parameter  = meta0['parameters'][i]['name']
        data, meta = hapi(server, dataset, parameter, start, stop, **opts)
        if i > 0: # Time parameter alone when i = 0. No fill allowed for time parameter.
            # Change fill value to be same as second element of parameter array.
            meta["parameters"][1]['fill'] = data[parameter].take(1).astype('U')
        hapiplot(data, meta, **opts)

# pngquant
if False:
    import io
    from PIL import Image

    from hapiclient import hapi
    from hapiclient import hapiplot

    server     = 'http://hapi-server.org/servers/TestData/hapi'
    dataset    = 'dataset1'
    start      = '1970-01-01Z'
    stop       = '1970-01-01T00:00:11Z'
    parameters = 'scalar'
    opts       = {'logging': False, 'usecache': True}    
    data, meta = hapi(server, dataset, parameters, start, stop, **opts)

    popts = {'usecache': False, 'logging': True, 
             'saveimage': True, 'returnimage':True,
             'transparent': True}

    popts['pngquant'] = False
    img = hapiplot(data, meta, **popts)
    Image.open(io.BytesIO(img)).show()

    popts['pngquant'] = True
    img = hapiplot(data, meta, **popts)
    Image.open(io.BytesIO(img)).show()
  
# returnimage and saveimage
if False:
    import io
    from PIL import Image

    from hapiclient import hapi
    from hapiclient import hapiplot

    server     = 'http://hapi-server.org/servers/TestData/hapi'
    dataset    = 'dataset1'
    start      = '1970-01-01Z'
    stop       = '1970-01-01T00:00:11Z'
    parameters = 'spectra'
    opts       = {'logging': False, 'usecache': True}    
    data, meta = hapi(server, dataset, parameters, start, stop, **opts)

    popts = {'usecache': False, 'logging': True, 
             'saveimage': False, 'returnimage':True}
    img = hapiplot(data, meta, **popts)
    
    Image.open(io.BytesIO(img)).show()

    popts = {'usecache': False, 'logging': True, 
             'saveimage': True, 'returnimage':True}
    img = hapiplot(data, meta, **popts)
    
    Image.open(io.BytesIO(img)).show()
  
# Transparency
if False:
    import io
    from PIL import Image

    from hapiclient import hapi
    from hapiclient import hapiplot

    server     = 'http://hapi-server.org/servers/TestData/hapi'
    dataset    = 'dataset1'
    start      = '1970-01-01Z'
    stop       = '1970-01-01T00:00:11Z'
    parameters = 'scalar'
    opts       = {'logging': False, 'usecache': True} 
    data, meta = hapi(server, dataset, parameters, start, stop, **opts)

    popts = {'usecache': False, 'logging': True, 
             'transparent': False, 'saveimage': True, 'returnimage':True}
    img = hapiplot(data, meta, **popts)    
    Image.open(io.BytesIO(img)).show()

    popts = {'usecache': False, 'logging': True, 
             'transparent': True, 'saveimage': True, 'returnimage':True}
    img = hapiplot(data, meta, **popts)    
    Image.open(io.BytesIO(img)).show()
    
# Spectra from CASSINIA S/C
if False:
    server     = 'http://datashop.elasticbeanstalk.com/hapi';
    dataset    = 'CHEMS_PHA_BOX_FLUXES_FULL_TIME_RES';
    parameters = 'HPlus_BEST_T1';
    start      = '2004-07-01T04:00:00Z';
    stop       = '2004-07-01T06:00:00Z';
    opts       = {'logging': True, 'usecache': True}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)

    popts = {'logging': True, 'dpi': 100, 'logy': True, 'logz': True}
    hapiplot(data, meta, **popts)
    
# Spectra w/ only bin centers and different timeStampLocations
if False:

    server     = 'http://hapi-server.org/servers/TestData/hapi'
    dataset    = 'dataset1'
    start      = '1970-01-01Z'
    stop       = '1970-01-01T00:00:11Z'
    parameters = 'spectra'
    opts       = {'logging': True, 'usecache': True}
    data,meta = hapi(server, dataset, parameters, start, stop, **opts)

    popts = {'logging': True, 'dpi': 100}

    data['spectra'][3,3] = -1e31 # Add a fill value

    # Default
    hapiplot(data, meta, **popts)

    # Should be same as previous plot
    meta['timeStampLocation'] = 'center'
    hapiplot(data, meta, **popts)

    print(data['Time'][3])
    meta['timeStampLocation'] = 'begin'
    hapiplot(data, meta, **popts)

    meta['timeStampLocation'] = 'end'
    hapiplot(data, meta, **popts)

    # Remove 6th time value so cadence is not uniform
    # Missing time value is at 00:00:06
    data = data[[0,1,2,3,4,5,7,8,9]]

    meta['timeStampLocation'] = 'begin'
    hapiplot(data, meta, **popts)

    meta['timeStampLocation'] = 'end'
    hapiplot(data, meta, **popts)

    meta['timeStampLocation'] = 'center'
    hapiplot(data, meta, **popts)

# Spectra w/centers and ranges with gaps
if False:
    from hapiclient.hapi import hapi
    from hapiclient.hapiplot import hapiplot
    import numpy as np
    import datetime as datetime
    
    T = 3
    data = np.ndarray(shape=(T), dtype=[('Time', 'O'), ('heatmap', '<f8', (2,))])
    
    start = datetime.datetime(1970, 1, 1)
    data['Time'] = np.array([start + datetime.timedelta(seconds=i) for i in range(T)])        
#   data['heatmap'] = np.array([[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]])
    data['heatmap'] = np.array([[1.0,2.0],[4.0,5.0],[7.0,8.0]])
#    data['heatmap'] = np.array([[1.0,2.0],[4.0,5.0]])
#    data['heatmap'] = np.array([[1.0,2.0]])

    # Create ranges with gaps
    r = []
    c = []
    for i in range(0,data['heatmap'].shape[1]):
        c.append(i)
        r.append([c[i]-0.5,c[i]+0.25])
    
    meta['parameters'][1]['name'] = 'heatmap'
    meta['parameters'][1]['bins'] = [{}]

    meta['parameters'][1]['bins'][0]['name'] = 'bin name'
    meta['parameters'][1]['bins'][0]['units'] = 'bin unit'
    meta['parameters'][1]['bins'][0]['centers'] = c    
    meta['parameters'][1]['bins'][0]['ranges'] = r
    print(meta['parameters'][1]['bins'][0]['ranges'])
    hapiplot(data, meta, **popts)

