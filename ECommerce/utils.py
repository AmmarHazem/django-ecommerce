import string
import datetime
import os
from random import choice, randint
# from django.utils import timezone

def get_filename(path):
    return os.path.basename(path)

def rand_string(size = 10, chars = string.ascii_lowercase + string.digits):
    return ''.join(choice(chars) for i in range(size))


def unique_key(Klass):
    key = rand_string(size = randint(10, 15))
    qs = Klass.objects.filter(key = key)
    while qs.exists():
        key = rand_string()
        qs = Klass.objects.filter(key = key)
    return key


def unique_order_id(order):
    id = rand_string()
    klass = order.__class__
    qs = klass.objects.filter(order_id = id)
    while qs.exists():
        id = rand_string()
        qs = klass.objects.filter(order_id = id)
    return id



def get_last_month_data(today):
    '''
    Simple method to get the datetime objects for the 
    start and end of last month. 
    '''
    this_month_start = datetime.datetime(today.year, today.month, 1)
    last_month_end = this_month_start - datetime.timedelta(days=1)
    last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
    return (last_month_start, last_month_end)


def get_month_data_range(months_ago=1, include_this_month=False):
    '''
    A method that generates a list of dictionaires 
    that describe any given amout of monthly data.
    '''
    today = datetime.datetime.now().today()
    dates_ = []
    if include_this_month:
        # get next month's data with:
        next_month = today.replace(day=28) + datetime.timedelta(days=4)
        # use next month's data to get this month's data breakdown
        start, end = get_last_month_data(next_month)
        dates_.insert(0, {
            "start": start.timestamp(),
            "end": end.timestamp(),
            "start_json": start.isoformat(),
            "end_json": end.isoformat(),
            "timesince": 0,
            "year": start.year,
            "month": str(start.strftime("%B")),
            })
    for x in range(0, months_ago):
        start, end = get_last_month_data(today)
        today = start
        dates_.insert(0, {
            "start": start.timestamp(),
            "start_json": start.isoformat(),
            "end": end.timestamp(),
            "end_json": end.isoformat(),
            "timesince": int((datetime.datetime.now() - end).total_seconds()),
            "year": start.year,
            "month": str(start.strftime("%B"))
        })
    #dates_.reverse()
    return dates_ 


get_month_data_range(months_ago=5, include_this_month=True)


date_data = get_month_data_range(months_ago=24, include_this_month=True)
month_labels = ["%s - %s" %(x['month'], x['year']) for x in date_data]
json_ready_month_starts = [x['start_json'] for x in date_data]
print(month_labels)
print(json_ready_month_starts)
large_date_data = get_month_data_range(months_ago=324, include_this_month=True)
print(large_date_data)
