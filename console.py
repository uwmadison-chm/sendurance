from fitbit_api import FitbitApi
import json
import sys

try:
    with open("client.json") as json_file:  
        client = json.load(json_file)
except FileNotFoundError as e:
    sys.exit("You need to make sure there is a client.json file in the current directory with an 'id' and 'secret' keys'.")

fitbit = FitbitApi(sys.argv[1], client['id'], client['secret'])

import IPython; IPython.embed()

