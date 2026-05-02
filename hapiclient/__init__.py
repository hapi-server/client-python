# Allow "from hapiclient import hapi"
from hapiclient.hapi import hapi

# Allow "from hapiclient import hapitime2datetime"
from hapiclient.hapitime import hapitime2datetime

# Allow "from hapiclient import datetime2hapitime"
from hapiclient.hapitime import datetime2hapitime

# Allow "from hapiclient import HAPIError"
from hapiclient.util import HAPIError

__version__ = '0.2.8b1'

import sys
import platform

if sys.version_info < (3, 10) and platform.system() == "Darwin":
    import warnings
    warnings.filterwarnings("ignore", message=".*urllib3.*OpenSSL.*")

if sys.version_info[0] < 3:
    # Python 2.7
    reload(sys)
    sys.setdefaultencoding('utf8')

