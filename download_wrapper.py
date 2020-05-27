from fitbit_api import FitbitApi
import csv
import pickle
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
        self.load_cache()

    def load_cache(self):
        self.cache_path = os.path.join(self.output, ".cache")
        os.makedirs(self.cache_path, exist_ok=True)
        self.cache_file = os.path.join(self.cache_path, str(self.ppt) + ".pickle")
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "rb") as f:  
                self.cache = pickle.load(f)
        else:
            self.cache = {}

    def save_cache(self):
        with open(self.cache_file, "wb") as f:  
            pickle.dump(self.cache, f)

    def convert_time(self, day, time):
        time = datetime.strptime(time, '%H:%M:%S').time()
        day = day.replace(hour=time.hour, minute=time.minute, second=time.second)
        return day.isoformat()

    def check_cache_already_downloaded(self, name):
        if not name in self.cache:
            return False
        if datetime.now() - timedelta(days=7) > self.cache[name]:
            return False
        else:
            return True

    def general_save(self, name, headers, get, save):
        if self.check_cache_already_downloaded(name):
            logging.debug(f"Not downloading {name} for {self.ppt}, already downloaded")
            return

        path = os.path.join(self.output, name)
        os.makedirs(path, exist_ok=True)
        filename = os.path.join(path, f'{self.ppt}_{name}.tsv')
        data_written = False
        with open(filename, 'w') as tsvfile:
            writer = csv.writer(tsvfile, dialect='excel-tab', lineterminator='\n')
            writer.writerow(headers)

            for day in [self.start + timedelta(days=x) for x in range(0, (self.end - self.start).days + 1)]:
                logging.info(f"Downloading {day} {name} for {self.ppt}")
                data = get(day)
                if not data:
                    continue
                if len(data) > 0:
                    data_written = True
                    save(writer, day, data)

        if data_written:
            self.cache[name] = datetime.now()
            self.save_cache()

    def save_sleep(self):
        def get(day):
            sleep = self.fitbit.sleep(day)
            if not sleep['sleep']:
                return None
            return sleep['sleep'][0]['minuteData']

        def save(writer, day, data):
            interpreter = ['', 'Asleep', 'Restless', 'Awake']
            for item in data:
                writer.writerow(
                    [self.ppt, self.convert_time(day, item['dateTime']), item['value'], interpreter[int(item['value'])]])

        headers = ["ID", "Time", "State", "Interpreted"]
        self.general_save('sleep', headers, get, save)

    def save_steps(self):
        def get(day):
            steps = self.fitbit.steps(day)
            if not steps['activities-steps-intraday']:
                return None
            return steps['activities-steps-intraday']['dataset']

        def save(writer, day, data):
            for item in data[1:2]:
                writer.writerow([self.ppt, self.convert_time(day, item['time']), item['value']])

        headers = ["ID", "Time", "Value"]
        self.general_save('steps', headers, get, save)

    def save_hrv(self):
        def get(day):
            hrv = self.fitbit.hrv(day)
            if not hrv['activities-heart-intraday']:
                return None
            return hrv['activities-heart-intraday']['dataset']

        def save(writer, day, data):
            for item in data:
                writer.writerow([self.ppt, self.convert_time(day, item['time']), item['value']])

        headers = ["ID", "Time", "Heartrate"]
        self.general_save('HR', headers, get, save)

    def save_inter_heartrate(self):
        def get(day):
            return self.fitbit.inter_heartrate(day)

        def save(writer, day, data):
            for item in data:
                writer.writerow([self.ppt, item[0], item[1]])

        headers = ["ID", "Date", "Resting Heartrate"]
        self.general_save('inter_HR', headers, get, save)
