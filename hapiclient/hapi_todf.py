def hapidata2dataframe(meta, data,
                       nan_fill=False,
                       parameters_include=None,
                       parameters_exclude=None,
                       name_map=None
                       ):
 
    """
    df = hapidata2dataframe(meta, data)
    
    nan_fill : bool
        If True, fill missing data with NaN. Default is False.
        For string parameters, no fill option.
        For isotime parameters, fill with numpy.datetime64('NaT', 'us').
        For integer parameters, convert to float and fill with numpy.nan.
        For double parameters, fill with numpy.nan.
    
    parameters_include : list or None
        List of parameter names to include. If None, include all parameters.
    
    parameters_exclude : list or None
        List of parameter names to exclude. If None, exclude no parameters.
    
    name_map : dict or None
        Dictionary mapping original parameter names to new names.
        For MultiIndex columns (e.g., vectors), only rename the first level (parameter name), not the second level (column number).
        If None, no renaming is performed.
    
    Describe how multidimentional parameters are handled.
    #https://stackoverflow.com/questions/36760414/how-to-create-pandas-dataframes-with-more-than-2-dimensions
    """

    from hapiclient import hapitime2datetime
    import pandas
    import numpy as np

    #pandas.set_option('display.max_columns', None) # display all columns when printing dataframe, for testing

    dfs = []
    for param in meta['parameters']: 
        param_name = param['name']
        time_name = meta['parameters'][0]['name']
        if parameters_include is not None: # only include parameters in parameters_include
            for param in parameters_include:
                if param not in [p['name'] for p in meta['parameters']]: # if parameter in parameters_include but not in meta['parameters'], raise error
                    raise ValueError(f"Parameter {param} in parameters_include is not in meta['parameters']")
            if time_name not in parameters_include: 
                parameters_include = parameters_include.copy()
                parameters_include.append(time_name) # always include time parameter
            if param_name not in parameters_include:
                continue
        if parameters_exclude is not None: # exclude parameters in parameters_exclude
            if param_name in parameters_exclude:
                continue
        if param_name == time_name: # always convert Time to datetime
            import warnings
            warnings.filterwarnings('ignore', category=UserWarning) # suppress UserWarning from hapitime2datetime:
            # UserWarning: The argument 'infer_datetime_format' is deprecated and will be removed in a future version. 
            # A strict version of it is now the default, see https://pandas.pydata.org/pdeps/0004-consistent-to-datetime-parsing.html. 
            # You can safely remove this argument.
            df_temp = pandas.DataFrame({param_name: hapitime2datetime(data[param_name])})
            dfs.append(df_temp)
        else:
            param_data = data[param_name] 
            fill = param.get('fill')
            if nan_fill and fill is not None: # remove nan_fill values              
                if param['type'] == 'isotime': 
                    param_data = hapitime2datetime(param_data) 
                    if fill == "0000-00-00T00:00:00Z": # to avoid error converting to datetime
                        fill = "0001-01-01T00:00:00Z"
                        param_data = np.where(param_data == hapitime2datetime("0000-00-00T00:00:00Z"), fill, param_data) # replace fill value in data
                    fill = hapitime2datetime(fill)
                    param_data = np.where(param_data == fill, np.datetime64('NaT', 'us'), param_data) # convert to datetime and fill with NaT
                elif param['type'] == 'integer':
                    param_data = np.where(param_data == int(fill), np.nan, param_data)
                elif param['type'] == 'double':
                    param_data = np.where(param_data == float(fill), np.nan, param_data)
                else:
                    raise ValueError(f"Parameter {param_name} has unsupported type: {param['type']}")
            # handle vector strings
            if param['type'] == 'string' and ',' in param_data.flatten()[0]: # check for vector strings
                # split vector strings into multiple columns
                str_splits = [s.strip('"').split(',') for s in param_data.flatten()]
                max_len = max(len(s) for s in str_splits)
                str_array = np.array([s + [''] * (max_len - len(s)) for s in str_splits]) # pad with empty strings
                param_data = str_array.reshape(param_data.shape + (max_len,))
                ndim = param_data.ndim
            # handle column names based on number of dimensions
            ndim = param_data.ndim
            if ndim <= 3:
                if ndim == 1:
                    col_names = [param_name]
                else:
                    # use MultiIndex for 2D and 3D parameters 
                    # in theory, could be used for higher dimensions too, but would be ugly
                    index_arrays = [[param_name]] + [list(map(str, range(param_data.shape[i]))) for i in range(1, ndim)]
                    col_names = pandas.MultiIndex.from_product(index_arrays)
                # define temp dataframe
                df_temp = pandas.DataFrame(param_data.reshape(param_data.shape[0], -1), columns=col_names)
            else:
                raise ValueError(f"Parameter {param_name} has unsupported number of dimensions: {param_data.ndim}")
            # add dataframe to list
            dfs.append(df_temp)
    # concatenate all dataframes
    df = pandas.concat(dfs, axis=1) 
    # set index to Time
    df.set_index(time_name, inplace=True)
    if name_map is not None: # rename columns using name_map
        for name in name_map: # if name in name_map but not in df.columns, raise error
            if name not in df.columns.get_level_values(0):
                raise ValueError(f"Name {name} does not match any parameter names in df.columns: {df.columns.get_level_values(0)}")
        # for MultiIndex columns, only rename the first level (parameter name), not the second level (column number)
        df.rename(columns=lambda x: (name_map.get(x[0], x[0]),) + x[1:] if isinstance(x, tuple) else name_map.get(x, x), inplace=True)
        if time_name in name_map:
            df.index.rename(name_map[time_name], inplace=True)
    return df
 
def hapidata2dataframe_test(versions=None, add_nan=False, add_names=False):
  from hapiclient import hapi
  # For each VERSION server 'http://hapi-server.org/servers/TestDataVERSION/hapi',
  if versions is None:
      versions = ['2.0', '2.1', '3.0', '3.1', '3.2', '3.3']
  for version in versions:
    server = f'http://hapi-server.org/servers/TestData{version}/hapi'
    datasets = [entry['id'] for entry in hapi(server)['catalog']]
    for dataset in datasets:
      print(f'Testing TestData{version}, {dataset} ...')

      parameters = '' # all parameters
      if version == '3.2':
          start      = hapi(server,dataset)['startDate'] #TODO: this for all versions
          stop       = hapi(server,dataset)['stopDate']
      else:
          start      = '1970-01-01Z' # min 1970-01-01Z
          stop       = '1970-01-01T00:00:11Z' # max 2016-12-31Z
      data, meta = hapi(server, dataset, parameters, start, stop)
      if add_nan:
          data = _add_nan(meta, data) # add fill values for testing
          nan_fill = True
      else: 
          nan_fill = False
      if add_names:
          name_map = {param['name']: f"{param['name']}_new" for param in meta['parameters']} # add _new to parameter names for testing
      else:
          name_map = None    
      df = hapidata2dataframe(meta, data, nan_fill=nan_fill, name_map=name_map) # convert to dataframe
      print(df) # print dataframe
 
def _add_nan(meta, data, parameters=None, debug=False):
    if parameters is None or parameters == '':
        parameters = meta['parameters']
    else:
        parameters = [param for param in meta['parameters'] if param['name'] in parameters]
    for param in parameters:
        param_name = param['name']
        if param.get('fill') is not None:
            if debug:
                print(param_name, data[param_name], data[param_name].dtype, param.get('fill')) # print parameter name, data, dtype, and fill value for testing
                pass
            if data[param_name].ndim == 1:
                data[param_name][0] = param.get('fill')
            else:
                for col in range(data[param_name].shape[1]):
                    data[param_name][0, col] = param.get('fill')
    return data
    
if __name__ == "__main__":
  hapidata2dataframe_test(add_nan=True, add_names=True)