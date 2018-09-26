# To execute, first run
#   pip install hapiclient
# from command line to install hapiclient package.

#%% Note
# In IPython, enter %matplotlib qt on command line to open plots in 
# new window. Enter %matplotlib inline to revert.

def main():

    sscweb()    
    cdaweb()

def sscweb():

    from hapiclient.hapi import hapi
    from hapiclient.hapiplot import hapiplot
    
    #%% SSCWeb data
    server     = 'http://hapi-server.org/servers/SSCWeb/hapi'
    dataset    = 'ace'
    start      = '2001-01-01T05:00:00'
    stop       = '2001-01-01T06:00:00'
    parameters = 'X_GSE,Y_GSE,Z_GSE'
    opts       = {'logging': True, 'use_cache': True}
    data,meta = hapi(server, dataset, parameters, start, stop, **opts)
    hapiplot(data,meta)

def cdaweb():    

    from hapiclient.hapi import hapi
    from hapiclient.hapiplot import hapiplot

    #%% CDAWeb data - Magnitude and BGSEc from dataset AC_H0_MFI
    server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
    dataset    = 'AC_H0_MFI'
    start      = '2001-01-01T05:00:00'
    stop       = '2001-01-01T06:00:00'
    parameters = 'Magnitude,BGSEc'
    opts       = {'logging': True, 'use_cache': True}    
    data,meta = hapi(server, dataset, parameters, start, stop, **opts)
    hapiplot(data,meta)
    
    #%% CDAWeb metadata for AC_H0_MFI
    server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
    dataset    = 'AC_H0_MFI'
    meta = hapi(server,dataset, **opts)
    print('Parameters in %s' % dataset)
    for i in range(0,len(meta['parameters'])):
        print('  %s' % meta['parameters'][i]['name'])
    print('')
    
    #%% CDAWeb metadata for all datasets
    server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
    meta = hapi(server, **opts)
    print('%d CDAWeb datasets' % len(meta['catalog']))
    for i in range(0,3):
        print('  %d. %s' % (i,meta['catalog'][i]['id']))
    print('  ...')    
    print('  %d. %s' % (len(meta['catalog']),meta['catalog'][-1]['id']))
    print('')
    
    #%% List all servers
    servers = hapi(logging=True) # servers is an array of URLs
    print('')
    
if __name__ == '__main__':    
    main()
    