from fitbit_api import FitbitApi
import json
import sys
import coloredlogs
import datetime

try:
    with open("client.json") as json_file:  
        client = json.load(json_file)
except FileNotFoundError as e:
    sys.exit("You need to make sure there is a client.json file in the current directory with an 'id' and 'secret' keys'.")

fitbit = FitbitApi(sys.argv[1], sys.argv[2], client['id'], client['secret'], automated_login=True)

coloredlogs.install(level='DEBUG')

import IPython; IPython.embed()

