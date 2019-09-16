import sys
import argparse
import coloredlogs
import logging

from datetime import datetime, timedelta
import dateutil.parser

import csv
import xlrd

import json
from fitbit_api import FitbitApi
from download_wrapper import DownloadWrapper

# An example of reading from a complex Excel worksheet to auto-download fitbit data

CHUNK_WIDTH = 5


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='count')
parser.add_argument('-o', '--output', default='./raw', help='Path to store output in')
parser.add_argument('input', help='Input CSV listing participant IDs and fitbit account emails')
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
    sys.exit("You need to make sure there is a client.json file in the current directory with an 'id' and 'secret' keys'. If all your fitbits use the same password, also add a 'password' key.")


def read_data(file_path, sheet_name="Distribution"):
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_name(sheet_name)
    row_list = []

    def to_date(date):
        return xlrd.xldate_as_tuple(date, workbook.datemode)  

    # The data is crazily laid out in 5 column chunks, so we need to restructure it.
    chunks = int(sheet.ncols / CHUNK_WIDTH)

    for chunk in range(0, chunks):
        for row_index in range(1, sheet.nrows):
            start_col = chunk * CHUNK_WIDTH
            fitbit_id = sheet.cell_value(rowx=row_index, colx=start_col)
            if not fitbit_id:
                continue

            start_date = sheet.cell_value(rowx=row_index, colx=start_col + 2)
            end_date = sheet.cell_value(rowx=row_index, colx=start_col + 3)
            try:
                start_date = float(start_date)
                end_date = float(end_date)
            except ValueError:
                continue

            if start_date <= 0.0 or end_date <= 0.0:
                continue

            start_date = to_date(start_date)
            end_date = to_date(end_date)

            d = {
                'fitbit_id': fitbit_id,
                'id': int(sheet.cell_value(rowx=row_index, colx=start_col + 1)),
                'start_date': datetime(*start_date) - timedelta(days=1),
                'end_date': datetime(*end_date) + timedelta(days=1),
            }
            logging.debug(d)
            row_list.append(d)
    return row_list


r = read_data(args.input)
for row in r:
    email = f'afc.fitbit+{row["fitbit_id"]}@gmail.com'
    ppt = row['id']
    start_date = row['start_date']
    end_date = row['end_date']
    logging.info(f"Downloading data for {ppt}, fitbit account {email}, between {start_date} and {end_date}")
    fitbit = FitbitApi(email, client['password'], client['id'], client['secret'])
    Downloader = DownloadWrapper(ppt=ppt, fitbit=fitbit, start=start_date,
                                 end=end_date, output=args.output)
    Downloader.save_hrv()
    Downloader.save_sleep()
    Downloader.save_steps()
