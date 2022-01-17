# Allow "from hapiclient import hapi"
from hapiclient.hapi import hapi

# Allow "from hapiclient import hapitime2datetime"
from hapiclient.hapitime import hapitime2datetime

# Allow "from hapiclient import HAPIError"
from hapiclient.util import HAPIError

__version__ = '0.2.2'

import sys
if sys.version_info[0] < 3:
    # Python 2.7
    reload(sys)
    sys.setdefaultencoding('utf8')

