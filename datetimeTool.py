# -----------------------------------------------------------
#
#
# (C) 2020 Lærke Brandhøj Kristensen, Aalborg, Denmark
# Released under GNU Public License (GPL)
# email lkri@techcollege.dk
# -----------------------------------------------------------

from datetime import datetime
import holidays

holidays = holidays.Denmark()   # holiday from denmark to sort out with days are workdays


"""Converts a string with format <%d-%m-20%y%H:%M:00> into datetime object"""

def convert_str_to_datetime(date_str, time_str):
    date_time_obj = datetime.strptime(date_str + time_str, '%d-%m-20%y%H:%M:00')
    return date_time_obj

"""Check that the given date is not weekend or holiday"""

def check_if_workday(date):
    return (date.weekday() not in [5, 6]) and (date not in holidays)

