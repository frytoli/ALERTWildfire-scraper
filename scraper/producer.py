#!/usr/bin/env python

from consumer import add

if __name__ == '__main__':
    for i in range(10):
        add.delay(i, i)
