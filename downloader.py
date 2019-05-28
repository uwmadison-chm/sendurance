from fitbit_api import FitbitApi
import json
import sys
import csv

try:
    with open("client.json") as json_file:  
        client = json.load(json_file)
except FileNotFoundError as e:
    sys.exit("You need to make sure there is a client.json file in the current directory with an 'id' and 'secret' keys'.")

with open(sys.argv[1], newline='') as csvfile:
    r = csv.reader(csvfile)
    for row in r:
        ppt = row[0]
        email = row[1]
        print(f"Would download {ppt} from {email}")
        fitbit = FitbitApi(email, client['id'], client['secret'])

