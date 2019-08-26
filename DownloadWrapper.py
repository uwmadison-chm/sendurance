from fitbit_api import FitbitApi
import csv
from datetime import datetime, timedelta
import os
import os.path
import logging


class DownloadWrapper():
    '''
    Wrapper class to assist with downloading fitbit data
    '''
    def __init__(self, ppt, fitbit, start, end, output='./raw'):
        '''

        :param ppt: Participant ID
        :param fitbit: Fitbit object from fitbit_api.py
        :param start: Download start date
        :param end: Download end date
        :param output: Output directory
        '''
        self.ppt = str(ppt)
        self.fitbit = fitbit
        self.start = start
        self.end = end
        self.output = output

    def convert_time(self, day, time):
        time = datetime.strptime(time, '%H:%M:%S').time()
        day = day.replace(hour=time.hour, minute=time.minute, second=time.second)
        return day.isoformat()

    def save_sleep(self):
        path = os.path.join(self.output, 'sleep')
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, self.ppt + '_1min_sleep.tsv'), 'w') as tsvfile:
            writer = csv.writer(tsvfile, dialect='excel-tab', lineterminator='\n')
            writer.writerow(["ID", "Time", "State", "Interpreted"])

            def save_sleep_day(writer, fitbit, ppt, day):
                sleep = fitbit.sleep(day)
                if not sleep['sleep']:
                    return
                intra = sleep['sleep'][0]['minuteData']
                interpreter = ['', 'Aleep', 'Restless', 'Awake']
                for item in intra:
                    writer.writerow(
                        [ppt, self.convert_time(day, item['dateTime']), item['value'], interpreter[int(item['value'])]])

            for day in [self.start + timedelta(days=x) for x in range(0, (self.end - self.start).days + 1)]:
                logging.info(f"Downloading {day} sleep for {self.ppt}")
                save_sleep_day(writer, self.fitbit, self.ppt, day=day)

    def save_steps(self):
        path = os.path.join(self.output, 'activity')
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, self.ppt + '_1min_steps.tsv'), 'w') as tsvfile:
            writer = csv.writer(tsvfile, dialect='excel-tab', lineterminator='\n')
            writer.writerow(["ID", "Time", "Value"])

            def save_steps_day(writer, fitbit, ppt, day):
                steps = fitbit.steps(day)
                if not steps['activities-steps-intraday']:
                    return
                intra = steps['activities-steps-intraday']['dataset']
                for item in intra[1:2]:
                    writer.writerow([ppt, self.convert_time(day, item['time']), item['value']])

            for day in [self.start + timedelta(days=x) for x in range(0, (self.end - self.start).days + 1)]:
                logging.info(f"Downloading {day} steps for {self.ppt}")
                save_steps_day(writer, self.fitbit, self.ppt, day=day)

    def save_hrv(self):
        path = os.path.join(self.output, 'HR')
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, self.ppt + '_1min_HR.tsv'), 'w') as tsvfile:
            writer = csv.writer(tsvfile, dialect='excel-tab', lineterminator='\n')
            writer.writerow(["ID", "Time", "Heartrate"])

            def save_hrv_day(writer, fitbit, ppt, day):
                hrv = fitbit.hrv(day)
                if not hrv['activities-heart-intraday']:
                    return
                intra = hrv['activities-heart-intraday']['dataset']
                for item in intra:
                    writer.writerow([ppt, self.convert_time(day, item['time']), item['value']])

            for day in [self.start + timedelta(days=x) for x in range(0, (self.end - self.start).days + 1)]:
                logging.info(f"Downloading {day} heart rate for {self.ppt}")
                save_hrv_day(writer, self.fitbit, self.ppt, day)

