import string
from random import choice, randint
import os

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
