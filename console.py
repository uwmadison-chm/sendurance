from fitbit_api import FitbitApi
import sys

fitbit = FitbitApi(sys.argv[1])

import IPython; IPython.embed()

