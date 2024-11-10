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
