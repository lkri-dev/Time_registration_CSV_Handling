# -----------------------------------------------------------
# Class that describes a registration as it is formated by Uddata's csv file
#
# (C) 2020 Lærke Brandhøj Kristensen, Aalborg, Denmark
# Released under GNU Public License (GPL)
# email lkri@techcollege.dk
# -----------------------------------------------------------

from datetime import datetime, timedelta


class RegistrationObj:
    def __init__(self, st, et):
        self.start_time: datetime = st
        self.end_time: datetime = et
        self.time_diff: timedelta = self.get_time_differance()

    """Gets the difference between to times"""

    def get_time_differance(self):
        if self.start_time > self.end_time:
            return self.start_time - self.end_time
        else:
            return self.end_time - self.start_time

    """combines two registrations from one day, returns a new date and a new time diff in a list"""
    def combine_days(self, registration, count):
        if registration.start_time == self.start_time.date():
            new_date = registration.end_time + self.time_diff
            new_time_diff = self.get_time_differance()

            return [new_date, new_time_diff]

