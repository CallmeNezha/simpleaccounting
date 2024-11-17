"""
    Copyright 2024- ZiJian Jiang @ https://github.com/CallmeNezha

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import datetime
import calendar
from dateutil.relativedelta import relativedelta


def months_between(start_date: datetime.date, end_date: datetime.date) -> int:
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    # Calculate the difference
    diff = relativedelta(end_date, start_date)
    # Total months is the difference in years converted to months + the remaining months
    return diff.years * 12 + diff.months


def days_between(start_date: datetime.date, end_date: datetime.date) -> int:
    if start_date > end_date:
        end_date, start_date = start_date, end_date
    # Calculate the difference
    diff = end_date - start_date
    # Return the number of days
    return diff.days


def days_of_month(date: datetime.date) -> int:
    # Get the last day of the month
    last_day = calendar.monthrange(date.year, date.month)[1]
    return last_day


def last_day_of_month(date: datetime.date) -> datetime.date:
    # Get the last day of the month
    last_day = calendar.monthrange(date.year, date.month)[1]
    return datetime.date(date.year, date.month, last_day)


def first_day_of_month(date: datetime.date) -> datetime.date:
    """"""
    return datetime.date(date.year, date.month, 1)


def first_day_of_next_month(date: datetime.date) -> datetime.date:
    """"""
    if date.month == 12:
        year = date.year + 1
        month = 1
    else:
        year = date.year
        month = date.month + 1
    # !else
    return datetime.date(year, month, 1)


def last_day_of_next_month(date: datetime.date) -> datetime.date:
    """"""
    return last_day_of_month(first_day_of_next_month(date))


def month_of_date(date: datetime.date) -> datetime.date:
    return first_day_of_month(date)


def first_day_of_previous_month(date: datetime.date) -> datetime.date:
    """"""
    if date.month == 1:
        year = date.year - 1
        month = 12
    else:
        year = date.year
        month = date.month - 1
    # !else
    return datetime.date(year, month, 1)


def last_day_of_previous_month(date: datetime.date) -> datetime.date:
    """"""
    return last_day_of_month(first_day_of_previous_month(date))
