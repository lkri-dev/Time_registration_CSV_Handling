# -----------------------------------------------------------
# Class that operates on the main list of data extracted from the csv files
#
# (C) 2020 Lærke Brandhøj Kristensen, Aalborg, Denmark
# Released under GNU Public License (GPL)
# email lkri@techcollege.dk
# -----------------------------------------------------------

import csv
from registrationObj import RegistrationObj
import datetimeTool
from datetime import datetime, date, time, timedelta

norm_day = timedelta(hours=7, minutes=24)               #norm for a day

class Dataset:
    def __init__(self, file_name):
        self.csv_file_name = file_name
        self.keywords_str = 'Sygdom, Ferie u. løn, Ferie m. løn'
        self.registration_list = self.read_csv_file_uddata()
        self.convert_0_into_24()

    """Reads CSV file and separate rows into a 2D list with 3 elements"""

    def read_csv_file_uddata(self):
        work_times = []

        with open(self.csv_file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 0

            for row in csv_reader:
                if ((row[10] == '') or (row[10] in self.keywords_str)) & (row[14] != ''):
                    start_datetime = datetimeTool.convert_str_to_datetime(row[13], row[14])
                    end_datetime = datetimeTool.convert_str_to_datetime(row[13], row[15])
                    temp_registration = RegistrationObj(start_datetime, end_datetime)
                    work_times.append(temp_registration)
                    work_times.sort(key=lambda x: x.start_time, reverse=False)
                    line_count += 1
        return work_times

    """Cleans the list for duplicate days, days where 2 registrations occur.
    Returns a new list where all days are combined"""

    def clean_data_set_for_duplicates(self):
        new_dates_list = []
        count = 0
        while len(self.registration_list) > count:
            search_result = self.search_list_for_datetime_by_datetime(self.registration_list[count].start_time.date())

            if search_result[1] <= 1:
                new_dates_list.append(self.registration_list[count])
            else:
                search_result = self.search_list_for_datetime_by_datetime(new_dates_list, self.registration_list[count].start_time.date())

                if search_result[1] != 0:
                    new_date, new_time_diff = self.registration_list.combine_days(new_dates_list, count)
                    new_dates_list[-1][1] = new_date
                    new_dates_list[-1][2] = new_time_diff
                else:
                    new_dates_list.append(self.registration_list[count])

            count += 1
        self.registration_list = new_dates_list
        return new_dates_list

    """Converts each time 0:00 into 0:00 the next day"""

    def convert_0_into_24(self):
        for ds in self.registration_list:
            t = time(0)
            if type(ds.end_time) == datetime and ds.end_time.time() == t:
                ds.end_time = datetime(ds.end_time.year, ds.end_time.month, ds.end_time.day + 1, hour=0, minute=0)

    """search for date ny formatted string and returns a new list with results and result count in a list"""

    def search_list_for_datetime(self, search_date_str):
        y1, m1, d1 = [int(x) for x in search_date_str.split('/')]
        search_date = date(y1, m1, d1)
        result_count = 0
        results = []

        for dates in self.registration_list:
            if dates.start_time.date() == search_date:
                result_count += 1
                results.append(dates)
        return [results, result_count]

    """search for date by datetime and returns a new list with results and result count in a list"""

    def search_list_for_datetime_by_datetime(self, search_date):
        date_str = '{}/{}/{}'.format(search_date.year, search_date.month, search_date.day)
        return self.search_list_for_datetime(date_str)

    """Finds workdays that probably weren't registered"""

    def find_empty_workdays(self):
        empty_days = []
        date: datetime.date = self.registration_list[0].start_time.date()
        while self.registration_list[0].start_time.date() > date:
            if datetimeTool.check_if_workday(date):
                search_result = self.search_list_for_datetime_by_datetime(date)
                if not search_result[0]:
                    empty_days.append(date)

            date += timedelta(days=1)
        return empty_days

    """Finds each day where the worktime is less than norm_day"""

    def find_under_worked_days(self, norm_day):
        result_count = 0
        results = []
        for registration in self.registration_list:
            stat = registration.get_time_differance()
            if stat < norm_day and datetimeTool.check_if_workday(registration.start_time):
                result_count += 1
                results.append([registration.start_time.date(), stat])
        return results

    def print_duplicates_list(self):
        search_count = 0
        for d in self.registration_list:
            search_count = self.search_list_for_datetime_by_datetime(d.start_time.date())[1]
            if search_count > 1:
                print(d)
                print(search_count)
        return search_count

    """get the work hour statics for a dates_list"""

    def get_stat_of_workeddays(self):
        workdays_count = 0
        stat = timedelta(0)
        for dates in self.registration_list:
            stat += dates.get_time_differance()
            if datetimeTool.check_if_workday(dates.start_time):
                workdays_count += 1

        print('Norm: {}\tStat: {}\tDays: {}'.format((norm_day * workdays_count), stat, workdays_count))
        return stat - (norm_day * workdays_count)

    def print_registration_dataset(self):
        for registration in self.registration_list:
            print('{}\t{}\t{}'.format(registration.start_time, registration.end_time, registration.time_diff))
