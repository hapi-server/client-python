import pandas as pd
from io import StringIO
import numpy as np
import json


def _nan_converter(value):
    token = value.decode('utf-8').strip().strip('"').lower()
    if token == 'nan':
        return np.nan
    return float(token)

x = '{"data": [1, 2, null, 4]}'
data = json.loads(x)
print(data)
print(type(data['data'][2]))

# First 4 np and pd parse to IEEE-754 nan
# Last 4, np parses to IEEE-754 nan

csv_data = ['1,2,NaN,4',
            '1,2, "NaN",4',
            '1,2,nan,4',
            '1,2, nan,4',
            '1,2,"nan",4',
            '1,2, "nan",4',
            '1,2,Nan,4',
            '1,2, Nan,4',
            '1,2,"Nan",4',
            '1,2, "Nan",4',
            '1,2,naN,4',
            '1,2, naN,4',
            '1,2,"naN",4',
            '1,2, "naN",4',
            '1,2, "naN",4',
          ]

for csv_line in csv_data:
    print(f"\nParsing line: {csv_line}")
    # Read the CSV line into a numpy array with explicit NaN handling.
    arr = np.genfromtxt(
        StringIO(csv_line),
        delimiter=',',
        #converters={2: _nan_converter}
    )
    print("  np.genfromtxt")

    #print(arr)
    #print(arr.dtype)
    print(f"    column 3 is NaN: {np.isnan(arr[2])}")
    assert np.isnan(arr[2])

    # Read the CSV line into a DataFrame with explicit NaN handling.
    df = pd.read_csv(
        StringIO(csv_line),
        header=None,
        skipinitialspace=True,
        keep_default_na=False,
        na_values=['NaN', 'nan', 'Nan', 'naN', ' "NaN"', ' "nan"', ' "Nan"', ' "naN"', '"NaN"', '"nan"', '"Nan"', '"naN"']
    )
    print("  pd.read_csv")
    #print(df)
    #print(df.dtypes)
    assert pd.isna(df.iloc[0, 2])
    print(f"    column 3 is NaN: {pd.isna(df.iloc[0, 2])}")

