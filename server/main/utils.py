import random


def gen_otp():
    random.seed()
    otp = random.randint(100000, 999999)
    return otp
