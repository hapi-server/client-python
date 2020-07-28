if True:
    from hapiclient import gallery
    gallery('http://hapi-server.org/servers/TestData2.0/hapi', 'dataset1', loglevel='debug')

if False:
    from hapiclient import gallery
    gallery('http://hapi-server.org/servers/TestData2.0/hapi','dataset1', 'vector')
