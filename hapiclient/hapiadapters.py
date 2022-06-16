"""
Usage:  mydataframe = hapi2pandas(data, meta)

Simple function that takes the HAPI data and metadata objects and
converts them into a Pandas DataFrame.

Handles scalar elements or 1D vectors (creates DataFrame labels for
vectors on the fly of form key_0, key_1, etc)

by Sandy Antunes, adapted from the HAPI_02.ipynb tutorial, June 2022

"""
import pandas
from hapiclient import hapitime2datetime

def hapi2pandas(data, meta):
    
    # Put each parameter into a DataFrame

    # Annoyingly, sometimes people use 'Time' and sometimes 'time'
    try:
        df_Time   = pandas.DataFrame(hapitime2datetime(data['Time']))
    except:
        df_Time   = pandas.DataFrame(hapitime2datetime(data['time']))
        
    para = meta['parameters']
    dfset = [df_Time]
    dfcols = ['Time']
    for p in para:
        pname = p['name']
        try:
            psize = p['size'][0]
        except:
            psize = 1
        if pname != 'Time':
            dfset.append(pandas.DataFrame(data[pname]))
            stem=''
            for i in range(psize):
                if psize > 1: stem='_'+str(i)
                dfcols.append(pname+stem)
            
    # Create DataFrame to hold all parameters
    df = pandas.DataFrame()

    # Place parameter DataFrames into single DataFrame
    #df = pandas.concat([df_Time, df_scalar, df_vector], axis=1)
    df = pandas.concat(dfset, axis=1)

    # Name columns (more generally, one would want to obtaine the column labels from meta, if available)
    df.columns = dfcols # ['Time', 'scalar','vector_x', 'vector_y', 'vector_z']

    # Set Time to be index
    df.set_index('Time', inplace=True)

    return(df)
