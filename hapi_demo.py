# Basic demo of hapiclient. Install package using
#   pip install hapiclient --upgrade
# from command line.

# Note:
# In IPython, enter 
#    %matplotlib qt
# on command line to open plots in new window. Enter
#    %matplotlib inline
# to revert.

# For more extensive demos and examples, see
# https://colab.research.google.com/drive/11Zy99koiE90JKJ4u_KPTaEBMQFzbfU3P?usp=sharing

def main():

    demos = [omniweb, sscweb, cdaweb, cassini, lisird]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print("\033[0;31mError:\033[0m " + str(e))


def testdata():

    from hapiclient import hapi

    server     = 'http://hapi-server.org/servers/TestData2.0/hapi'
    dataset    = 'dataset1'
    parameters = 'scalar'
    start      = '1970-01-01T00:00:00'
    stop       = '1970-01-02T00:01:00'
    parameters = 'scalar,vector'
    opts       = {'logging': True, 'usecache': True}

    data, meta = hapi(server, dataset, parameters, start, stop, **opts)


def omniweb():

    from hapiclient import hapi

    server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
    dataset    = 'OMNI2_H0_MRG1HR'
    start      = '2003-09-01T00:00:00'
    stop       = '2003-12-01T00:00:00'
    parameters = 'DST1800'
    opts       = {'logging': True, 'usecache': False}

    # Get data
    data, meta = hapi(server, dataset, parameters, start, stop, **opts)

    # Plot all parameters
    hapiplot(data, meta)


def sscweb():

    from hapiclient import hapi
    from hapiplot import hapiplot
    
    # SSCWeb data
    server     = 'http://hapi-server.org/servers/SSCWeb/hapi'
    dataset    = 'ace'
    start      = '2001-01-01T05:00:00'
    stop       = '2001-01-01T10:00:00'
    parameters = 'X_GSE,Y_GSE,Z_GSE'
    opts       = {'logging': True, 'usecache': True}
    data, meta = hapi(server, dataset, parameters, start, stop, **opts)
    hapiplot(data, meta, **opts)


def cdaweb():

    from hapiclient import hapi
    from hapiplot import hapiplot

    # CDAWeb data - Magnitude and BGSEc from dataset AC_H0_MFI
    server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
    dataset    = 'AC_H0_MFI'
    start      = '2001-01-01T05:00:00'
    stop       = '2001-01-01T10:00:00'
    parameters = 'Magnitude,BGSEc'
    opts       = {'logging': True, 'usecache': True}    
    data, meta = hapi(server, dataset, parameters, start, stop, **opts)
    hapiplot(data, meta, **opts)

    # CDAWeb metadata for AC_H0_MFI
    server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
    dataset    = 'AC_H0_MFI'
    meta = hapi(server, dataset, **opts)
    print('Parameters in %s' % dataset)
    for i in range(0, len(meta['parameters'])):
        print('  %s' % meta['parameters'][i]['name'])
    print('')

    # CDAWeb metadata for all datasets
    server = 'https://cdaweb.gsfc.nasa.gov/hapi'
    meta = hapi(server, **opts)
    print('%d CDAWeb datasets' % len(meta['catalog']))
    for i in range(0, 3):
        print('  %d. %s' % (i, meta['catalog'][i]['id']))
    print('  ...')    
    print('  %d. %s' % (len(meta['catalog']), meta['catalog'][-1]['id']))
    print('')

    # List all servers
    servers = hapi(logging=True)  # servers is an array of URLs
    print('')


def cassini():

    from hapiclient import hapi
    from hapiplot import hapiplot

    server     = 'http://datashop.elasticbeanstalk.com/hapi';
    dataset    = 'CHEMS_PHA_BOX_FLUXES_FULL_TIME_RES';
    parameters = 'HPlus_BEST_T1';
    start      = '2004-07-01T04:00:00Z';
    stop       = '2004-07-01T06:00:00Z';
    opts       = {'usecache': True, 'logging': True}

    data, meta = hapi(server, dataset, parameters, start, stop, **opts)
    
    popts = {'logging': False, 'logy': True, 'logz': True}
    hapiplot(data, meta, **popts)


def lisird():

    from hapiclient import hapi
    from hapiplot import hapiplot

    server     = 'http://lasp.colorado.edu/lisird/hapi';
    dataset    = 'sme_ssi';
    parameters = 'irradiance'; 
    start      = '1981-10-09T00:00:00.000Z';
    stop       = '1981-10-14T00:00:00.000Z';

    opts       = {'usecache': True, 'logging': True}
    data, meta = hapi(server, dataset, parameters, start, stop, **opts)

    hapiplot(data, meta)


if __name__ == '__main__':
    try:
        from hapiplot import hapiplot
    except:
        print('Package hapiplot is not installed. Will not plot results.')
    main()
