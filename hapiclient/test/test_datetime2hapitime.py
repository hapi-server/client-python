def test_datetime2hapitime():

    import datetime
    from hapiclient import datetime2hapitime

    dts = [datetime.datetime(2000,1,1),datetime.datetime(2000,1,2)];
    hapi_times = datetime2hapitime(dts)
    assert hapi_times[0] == '2000-01-01T00:00:00.000000Z'
    assert hapi_times[1] == '2000-01-02T00:00:00.000000Z'

    dt = datetime.datetime(2000,1,1)
    hapi_time = datetime2hapitime(dt)
    assert hapi_time == '2000-01-01T00:00:00.000000Z'


if __name__ == '__main__':
    test_datetime2hapitime()
