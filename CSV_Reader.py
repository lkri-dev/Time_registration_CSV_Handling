# -----------------------------------------------------------
# This project is to read the time registration csv file of UddataPlus.
# To check ones registration of work time, if any days where missed and to get a bigger overview than what UdataPlus provides.
#
# (C) 2020 Lærke Brandhøj Kristensen, Aalborg, Denmark
# Released under GNU Public License (GPL)
# email lkri@techcollege.dk
# -----------------------------------------------------------

import csv
from datetime import datetime, time, date, timedelta
import holidays

csv_files = 'Eksport20200101-20201101.csv', 'Eksport20190101-20191231.csv'  #csv file to be analysed
weekdays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']                #name of weekdays for print outs
holidays = holidays.Denmark()                                               #holiday from denmark to sort out with days are workdays
keywords_str = 'Sygdom, Ferie u. løn, Ferie m. løn'                         #search words for csv fil for non worked, but still registered days
norm_day = timedelta(hours=7, minutes=24)                                   #norm for a day
norm_week = norm_day * 5                                                    #norm for a week

"""Converts a string with format <%d-%m-20%y%H:%M:00> into datetime object"""
def convert_str_to_datetime(date_str, time_str):
    date_time_obj = datetime.strptime(date_str + time_str, '%d-%m-20%y%H:%M:00')
    return date_time_obj

"""Check that the given date is not weekend or holiday"""
def check_if_workday(date):
    return (date.weekday() not in [5, 6]) and (date not in holidays)

"""Reads CSV file and seperate rows into a 2D list with 3 elements"""
def read_csv_file_uddata(file_name):
    work_times = []

    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0

        for row in csv_reader:
            if ((row[10] == '') or (row[10] in keywords_str)) & (row[14] != ''):
                start_datatime = convert_str_to_datetime(row[13], row[14])
                end_datatime = convert_str_to_datetime(row[13], row[15])
                work_times.append([start_datatime, end_datatime, end_datatime - start_datatime])
                work_times.sort()
                line_count += 1
    return work_times

"""search for date ny formated string and returns a new list with results and reasult count in a list"""
def search_list_for_datetime(dates_list, search_date_str):
    y1, m1, d1 = [int(x) for x in search_date_str.split('/')]
    search_date = date(y1, m1, d1)
    result_count = 0
    results = []

    for dates in dates_list:
        if dates[0].date() == search_date:
            result_count += 1
            results.append(dates)
    return [results, result_count]

"""search for date by datetime and returns a new list with results and reasult count in a list"""
def search_list_for_datetime_by_datetime(dates_list, search_date):
    date_str = '{}/{}/{}'.format(search_date.year, search_date.month, search_date.day)
    return search_list_for_datetime(dates_list, date_str)

"""Gets the difference between to times"""
def get_time_differance(datetime1, datetime2):
    if datetime1 > datetime2:
        return datetime1 - datetime2
    else:
        return datetime2 - datetime1

"""Finds workdays that proberbly wheren't registered"""
def find_empty_workdays(dates_list):
    empty_days = []
    date: datetime = dates_list[0][0].date()
    while dates_list[-1][0].date() > date:
        if check_if_workday(date):
            search_result = search_list_for_datetime_by_datetime(dates_list, date)
            if search_result[0] == []:
                empty_days.append(date)

        date += timedelta(days=1)
    return empty_days

"""Finds each day where the worktime is less than norm_day"""
def find_under_worked_days(dates_list):
    result_count = 0
    results = []
    for dates in dates_list:
        stat = get_time_differance(dates[0], dates[1])
        if stat < norm_day and check_if_workday(dates[0]):
            result_count += 1
            results.append([dates[0].date(), stat])
    return results

"""combines two regitrations from one day, returns a new date and a new time diff in a list"""
def combine_days(dates_list, new_dates_list, count):
    if new_dates_list[-1][0].date() == dates_list[count][0].date():
        time_diff = get_time_differance(dates_list[count][0], dates_list[count][1])
        new_date = new_dates_list[-1][1] + time_diff
        new_time_diff = get_time_differance(new_dates_list[-1][0], new_dates_list[-1][1])

        return [new_date, new_time_diff]


"""Clean the list for duplicate days, days where 2 registrations occur and return a new list where all days are combined"""
def clean_data_set_for_duplicates(dates_list):
    new_dates_list = []
    count = 0
    while len(dates_list) > count:
        search_result = search_list_for_datetime_by_datetime(dates_list, dates_list[count][0].date())

        if search_result[1] <= 1:
            new_dates_list.append(dates_list[count])
        else:
            search_result = search_list_for_datetime_by_datetime(new_dates_list, dates_list[count][0].date())

            if search_result[1] != 0:
                new_date, new_time_diff = combine_days(dates_list, new_dates_list, count)
                new_dates_list[-1][1] = new_date
                new_dates_list[-1][2] = new_time_diff
            else:
                new_dates_list.append(dates_list[count])

        count += 1

    return new_dates_list

"""Converts each time 0:00 into 0:00 the next day"""
def convert_0_into_24(dates_list):
    for ds in dates_list:
        t = time(0)
        if type(ds[1]) == datetime and ds[1].time() == t:
            date = datetime(ds[1].year, ds[1].month, ds[1].day + 1, hour=0, minute=0)
            ds[1] = date
    return dates_list


"""get the work hour statics for a dates_list"""
def get_stat_of_workeddays(dates_list):
    workdays_count = 0
    stat = timedelta(0)
    for dates in dates_list:
        stat += get_time_differance(dates[0], dates[1])
        if check_if_workday(dates[0]):
            workdays_count += 1

    print('Norm: {}\tStat: {}\tDays: {}'.format((norm_day * workdays_count), stat, workdays_count))
    return stat - (norm_day * workdays_count)

"""prints a 2D list"""
def print_list(list):
    for element in list:
        for i in element:
            print(i)

def print_duplicates_list(dates_list):
    for d in dates_list:
        search_count = search_list_for_datetime_by_datetime(dates_list, d[0].date())[1]
        if search_count > 1:
            print(d)
            print(search_count)
    return search_count


"""Control switch"""
def switch(control, dates_list):
    if control == '1':
        empty_days = find_empty_workdays(dates_list)
        print(empty_days[0])

    elif control == '2':
        under_worked_days = find_under_worked_days(dates_list)
        for d in under_worked_days:
            print('{}\t{}\t{}'.format(d[0], weekdays[d[0].weekday()], d[1]))

    elif control == '3':
        no_duplicates_list = clean_data_set_for_duplicates(dates_list)
        print_duplicates_list(no_duplicates_list)
        return no_duplicates_list

    elif control == '4':
        print(get_stat_of_workeddays(dates_list))

    else:
        print('none')

"""Main function"""
def main():
    for file in csv_files:
        work_times_list = read_csv_file_uddata(file)
        work_times_list = convert_0_into_24(work_times_list)

        no_duplicate_list = switch('3', work_times_list)
        switch('4', no_duplicate_list)


main()

