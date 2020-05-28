import pandas as pd
import json
import sys
from datetime import datetime, timedelta
import logging
import argparse
import coloredlogs

from fitbit_api import FitbitApi
from download_wrapper import DownloadWrapper


# TODO: easy argparse to allow downloading different types of stuff
parser = argparse.ArgumentParser(description='Automate downloading data from a fleet of fitbits.')
parser.add_argument('-v', '--verbose', action='count')
parser.add_argument('--all', action='store_true')
parser.add_argument('--interhr', action='store_true')
parser.add_argument('--hrv', action='store_true')
parser.add_argument('--steps', action='store_true')
parser.add_argument('--sleep', action='store_true')
parser.add_argument('--sleep-summary', action='store_true')
parser.add_argument('json', help="Fleet JSON file")

args = parser.parse_args()

if args.verbose:
    if args.verbose > 1:
        coloredlogs.install(level='DEBUG')
    elif args.verbose > 0:
        coloredlogs.install(level='INFO')
else:
    coloredlogs.install(level='WARN')


# TODO: modify this to include the option to specify time of day
def get_start_end_time(row):
    def parse_date(date):
        for fmt in ('%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(date, fmt)
            except ValueError:
                pass

        message = 'Improper formatting of First Day ' + row['First Day'] + ' or Last Day ' + row['Last Day'] + \
                  ' for ID ' + str(row['ID']) + '. Please reformat dates to match MM/DD/YY'
        raise ValueError(message)

    start = parse_date(row['First Day'])
    end = parse_date(row['Last Day'])

    # Download data one day before and after specified dates
    start = start - timedelta(days=1)
    end = end + timedelta(days=2)
    return start, end


try:
    with open(args.json) as input_json:
        settings = json.load(input_json)
except FileNotFoundError as e:
    sys.exit("You must pass a json file with a fleet_file, work_event_file, and output_path.")

fleet_file = settings['fleet_file']
work_event_file = settings['work_event_file']

df_log_in = pd.read_csv(fleet_file, header=1)

df_we = pd.read_excel(work_event_file, sheet_name='SCORED', header=0)

# Label is e.g. 'we.t_.workinfo.startDate'
df_we['start']  = df_we['we.t1.workinfo.startDate']
df_we['end'] = df_we['we.t1.workinfo.endDate']

df_we = df_we[['id', 'start', 'end']]
df_we['type'] = df_we['start'].apply(type)
df_we = df_we[df_we['type'] == datetime]
df_log_in = df_log_in[df_log_in['ID'].notna()]

# Change to wherever you want to output the files
output = r'./raw'

try:
    with open("client.json") as json_file:
        client = json.load(json_file)
except FileNotFoundError as e:
    sys.exit("There must be a client.json file in the current directory with an 'id' and 'secret' keys'.")

checks = []
skip = True
for index, row in df_log_in.iterrows():
    row['ID'] = int(row['ID'])
    logging.info(f"Downloading for subject {row['ID']}")
    participant_dates = df_we[df_we['id'] == row['ID']]
    start_date = participant_dates.iloc[0]['start']
    end_date = participant_dates.iloc[-1]['end']

    email = row['Email log-in'].replace('.gmail', '@gmail')
    fitbit = FitbitApi(email, client['password'], client['id'], client['secret'])
    Downloader = DownloadWrapper(ppt=row['ID'], fitbit=fitbit, start=start_date, end=end_date, output=output)
    logging.debug(f"Downloader created for id {row['ID']}")
    if args.interhr or args.all:
        logging.debug(f"Downloading inter heartrate for {row['ID']}")
        Downloader.save_inter_heartrate()
    if args.hrv or args.all:
        logging.debug(f"Downloading hrv for {row['ID']}")
        Downloader.save_hrv()
    if args.steps or args.all:
        logging.debug(f"Downloading steps for {row['ID']}")
        Downloader.save_steps()
    if args.sleep or args.all:
        logging.debug(f"Downloading sleep for {row['ID']}")
        Downloader.save_sleep()
    if args.sleep_summary or args.all:
        logging.debug(f"Downloading sleep summary for {row['ID']}")
        Downloader.save_sleep_summary()
