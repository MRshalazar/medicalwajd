import random


def read_heart_rate():
    return random.randint(55, 110)


def read_systolic_bp():
    return random.randint(100, 170)


def read_spo2():
    return random.randint(90, 100)


def read_temperature():
    return round(random.uniform(36.0, 41.0), 1)