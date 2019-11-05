#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta

def caldays(begin, end):
    begin = datetime.datetime(begin.year,begin.month,1)
    end = end + relativedelta(months=+1)
    end = datetime.datetime(end.year,end.month,1)
    days = []
    while begin < end:
        days.append(begin)
        begin += datetime.timedelta(days=1)
    return days


def weekify(days):
    weeks = []
    current = []
    for d in days:
        if d.strftime('%a') == 'Sun':
            weeks.append(current)
            current = []
        current.append(d)
    weeks.append(current)
    return weeks


def starter(d, monthstart=False):
    spaces = (5 if monthstart else 8)
    dmap = dict(
        Sun=0,
        Mon=3,
        Tue=6,
        Wed=9,
        Thu=12,
        Fri=15,
        Sat=18,
        )
    start = (d.strftime('%b') if monthstart else '')
    end = ('    \n' if d.strftime('%a') == 'Sat' else ' ')
    return start + (spaces + dmap[d.strftime('%a')]) * ' ' \
        + str(d.day).rjust(2, ' ') + end


def others(d):
    end = ('    \n' if d.strftime('%a') == 'Sat' else ' ')
    return str(d.day).rjust(2, ' ') + end


def liner(weeks):
    _try = '        Su Mo Tu We Th Fr Sa'
    for w in weeks:
        monthstart=False
        for d in w:
            if d.day == 1:
                monthstart=True
                _try += '\n'
                _try += starter(d,monthstart)
            else:
                _try += 8 * " " if w[0].day == d.day else ''
                _try += others(d)
    return _try

def caltext(begin, end):
    _text = caldays(begin,end)
    _text = weekify(_text)
    _text = liner(_text)
    return _text

if __name__ == '__main__':
    import sys
    start = datetime.datetime( int(sys.argv[1][0:4]), int(sys.argv[1][4:6]), 1 )
    end = datetime.datetime( int(sys.argv[2][0:4]), int(sys.argv[2][4:6]), 1 )
    print(caltext(start,end))
    
