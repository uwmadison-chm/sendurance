from fitbit_api import FitbitApi
import json
import sys
import csv
import argparse

from datetime import datetime, timedelta
import dateutil.parser
import os
import os.path

import logging                                                                                                                                                                                                                 
import coloredlogs 

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


def save_sleep_day(writer, fitbit, ppt, day):
    sleep = fitbit.sleep(day)
    intra = sleep['sleep'][0]['minuteData']
    writer.writerow(["ID", "Time", "State", "Interpreted"])
    interpreter = ['', 'Aleep', 'Restless', 'Awake']
    for item in intra:
        # TODO: probably need better merging of date/time
        writer.writerow([ppt, day.isoformat() + " " + item['dateTime'], item['value'], interpreter[int(item['value'])]])

def save_sleep(fitbit, ppt, start, end):
    path = os.path.join(args.output, 'sleep')
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, ppt + '_1min_sleep.tsv'), 'w', newline='') as tsvfile:
        writer = csv.writer(tsvfile, dialect='excel-tab')
        for day in [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]:
            logging.info(f"Downloading {day} for {ppt} from {email}")
            save_sleep_day(writer, fitbit, ppt, day)

def save_steps_day(writer, fitbit, ppt, day):
    steps = fitbit.steps(day)
    intra = steps['activities-steps-intraday']['dataset']
    writer.writerow(["ID", "Time", "Value"])
    for item in intra:
        # TODO: probably need better merging of date/time
        writer.writerow([ppt, day.isoformat() + " " + item['time'], item['value']])

def save_steps(fitbit, ppt, start, end):
    path = os.path.join(args.output, 'activity')
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, ppt + '_1min_steps.tsv'), 'w', newline='') as tsvfile:
        writer = csv.writer(tsvfile, dialect='excel-tab')
        for day in [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]:
            logging.info(f"Downloading {day} for {ppt} from {email}")
            save_steps_day(writer, fitbit, ppt, day)

def save_hrv_day(writer, fitbit, ppt, day):
    hrv = fitbit.hrv(day)
    intra = hrv['activities-heart-intraday']['dataset']
    writer.writerow(["ID", "Time", "Heartrate"])
    for item in intra:
        # TODO: probably need better merging of date/time
        writer.writerow([ppt, day.isoformat() + " " + item['time'], item['value']])

def save_hrv(fitbit, ppt, start, end):
    path = os.path.join(args.output, 'HR')
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, ppt + '_1min_HR.tsv'), 'w', newline='') as tsvfile:
        writer = csv.writer(tsvfile, dialect='excel-tab')
        for day in [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]:
            logging.info(f"Downloading {day} for {ppt} from {email}")
            save_hrv_day(writer, fitbit, ppt, day)

with open(args.input, newline='') as csvfile:
    r = csv.reader(csvfile)
    for row in r:
        ppt = row[0]
        email = row[1]
        fitbit = FitbitApi(email, client['id'], client['secret'])

        # save_hrv(fitbit, ppt, args.start_date, args.end_date)
        # save_sleep(fitbit, ppt, args.start_date, args.end_date)
        # save_steps(fitbit, ppt, args.start_date, args.end_date)