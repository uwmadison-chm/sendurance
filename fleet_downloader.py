import pandas as pd
from fitbit_api import FitbitApi
import json
import sys
from datetime import datetime, timedelta
import pyperclip
import logging
from download_wrapper import DownloadWrapper


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
    end = end + timedelta(days=1)
    return start, end


# This file needs to contain columns "ID", "Email log-in", "First Day", and "Last Day"
# Days should be formatted MM/DD/YY, MM/DD/YYYY, or YYYY-MM-DD
fleet_file = 'fleet_data.csv'
df = pd.read_csv(fleet_file)
print(df.columns.values)
if not all(x in ['ID', 'Email log-in', 'First Day', 'Last Day'] for x in df.columns.values):
    error_message = fleet_file, ' is missing one of the following columns: ', 'ID', 'Email log-in', 'First Day', 'Last Day'
    sys.exit(error_message)

df = df[df['ID'].notna()]
output = './raw'

try:
    with open("client.json") as json_file:
        client = json.load(json_file)
except FileNotFoundError as e:
    sys.exit("You need to make sure there is a client.json file in the current directory with an 'id' and 'secret' keys'.")


for index, row in df.iterrows():
    start_date, end_date = get_start_end_time(row)
    email = row['Email log-in'].replace('.gmail', '@gmail')
    pyperclip.copy(email)
    #  TODO: Automate fitbit registration
    fitbit = FitbitApi(email, client['id'], client['secret'])
    Downloader = DownloadWrapper(ppt=row['ID'], fitbit=fitbit, start=start_date, end=end_date, output=output)
    logging.info(f"Downloader created for id {row['ID']}")
    Downloader.save_steps()
    Downloader.save_hrv()
    Downloader.save_sleep()
