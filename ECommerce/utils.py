import string
from random import choice


def rand_string(size = 10, chars = string.ascii_lowercase + string.digits):
    return ''.join(choice(chars) for i in range(size))


def unique_order_id(order):
    id = rand_string()
    klass = order.__class__
    qs = klass.objects.filter(order_id = id)
    while qs.exists():
        id = rand_string()
        qs = klass.objects.filter(order_id = id)
    return id
