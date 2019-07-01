from fitbit_api import FitbitApi
import json
import sys
import csv
import argparse
from datetime import datetime
import dateutil.parser
import coloredlogs
from DownloadWrapper import DownloadWrapper


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='count')
parser.add_argument("--start-date", default=datetime.today().date(), required=False, help="Date at start of range", type=dateutil.parser.isoparse)
parser.add_argument("--end-date", default=datetime.today().date(), required=False, help="Date at end of range", type=dateutil.parser.isoparse)
parser.add_argument("--output", default="./raw", help="Path to store output in")
parser.add_argument("input", help="Input CSV listing participant IDs and fitbit account emails")
args = parser.parse_args()

if args.verbose:
    if args.verbose > 1:
        coloredlogs.install(level='DEBUG')
    elif args.verbose > 0:
        coloredlogs.install(level='INFO')
else:
    coloredlogs.install(level='WARN')

try:
    with open("client.json") as json_file:  
        client = json.load(json_file)
except FileNotFoundError as e:
    sys.exit("You need to make sure there is a client.json file in the current directory with an 'id' and 'secret' keys'.")

with open(args.input, newline='') as csvfile:
    r = csv.reader(csvfile)
    for row in r:
        ppt = row[0]
        email = row[1]
        fitbit = FitbitApi(email, client['id'], client['secret'])
        Downloader = DownloadWrapper(ppt=ppt, fitbit=fitbit, start=args.start_date,
                                     end=args.end_date, output=args.output)
        # Downloader.save_hrv()
        # Downloader.save_sleep()
        # Downloader.save_steps()