from fen import *
from time import time, clock
import sys

print(sys.platform)


def test_is_fen_legal():
    while True:
        fen = input("paste the FEN:")
        if not is_fen_legal(fen):
            print(False)
        else:
            print(True)


fen = "8/k7/8/1r1q4/8/K2Q4/8/8 w - - 0 1"


def vfunc(func, parms):
    stat = []

    for i in range(10):
        count = pow(10, i)
        t0 = time()
        for i in range(count):
            func(parms)
        cost = time() - t0

        if cost > 0.01:
            count *= int(1 / cost)
            break

    index = 1
    while True:
        t0 = time()
        for i in range(count):
            func(parms)
        cost = time() - t0

        stat.append(index * count / cost)
        speed = sum(stat) / len(stat)

        if speed > 1000000:
            speed = str(round(speed / 1000000, 2)) + " M/S"
        elif speed > 1000:
            speed = str(round(speed / 1000, 2)) + " K/S"
        else:
            speed = str(round(speed, 2)) + "M/s"

        print(" " * 45, end="\r")
        print(speed)
        print("times: {}  ".format(len(stat)), "Speed = {}".format(speed), end="\r")


def add(b):
    a = b + 1


speed_test(is_fen_legal, "8/k7/8/1r1q4/8/K2Q4/8/8 w - - 0 1")
# speed_test(add, 1)
