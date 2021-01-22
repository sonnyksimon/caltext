#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: BSD-2-Clause
# Copyright (C) 2019, Sonny Kothapally, <me@sonnyksimon.com>.
#
""" caltext: a plaintext calendar generator"""

from __future__ import print_function

import datetime
from dateutil.relativedelta import relativedelta
import argparse
import logging
import os
import sys

log = logging.getLogger(__name__)
IDENT = "CALTEXT"


def caltext(start, stop):
    """
    Generates a plaintext calendar given a date range.
    """
    # Make sense of the dates
    mkdate = lambda x: datetime.datetime( int(str(x)[:4]), int(str(x)[4:]), 1 )
    start = mkdate(start)
    stop = mkdate(stop)
    stop = stop + relativedelta(months=+1)
    begin = datetime.datetime(start.year,start.month,1)
    end = datetime.datetime(stop.year, stop.month, 1)
    
    # Figure out the days
    days = []
    while begin < end:
        days.append(begin)
        begin += datetime.timedelta(days=1)
    
    # Figure out the weeks
    weeks = []
    current = []
    for d in days:
        if d.strftime('%a') == 'Sun':
            weeks.append(current)
            current = []
        current.append(d)
    weeks.append(current)
    
    # Generate the plaintext
    text = '        Su Mo Tu We Th Fr Sa'
    dmap = dict(Sun=0, Mon=3, Tue=6, Wed=9, Thu=12,
                Fri=15, Sat=18,)
    for w in weeks:
        for d in w:
            if d.day == 1:
                text += '\n'
                text += d.strftime('%b')
                text += (5 + dmap[d.strftime('%a')]) * ' '
            else:
                text += 8 * ' ' if w[0].day == d.day else ''
            text += str(d.day).rjust(2, ' ')
            text += '    \n' if d.strftime('%a') == 'Sat' else ' '
    return text


def run(options):
    pid = os.getpid()
    if os.name == "nt":
        pid += 65536
    if options.pidfile:
        with open(options.pidfile, "w") as f:
            f.write(str(pid))
    
    log.debug("Running on pid %s", pid)
    
    if options.start and options.stop:
        text = caltext(options.start, options.stop)
        print(text)
        return ScriptRC.SUCCESS
    
    return ScriptRC.FAILURE

    
def get_options():
    parser = argparse.ArgumentParser()

    parser.add_argument("start", action="store", type=int,
                        help="From which year+month in format yyyymm")
    parser.add_argument("stop", action="store", type=int,
                        help="To which year+month in format yyyymm")
    parser.add_argument("--verbose", action="store_true",
                        help="verbose output")
    parser.add_argument("--pidfile", action="store",
                        help="file name for the PID")
    parser.add_argument("--logfile", action="store",
                        help="file name for the log")

    return parser.parse_args()


def setup_logging(options):
    """
    Set up logging from the command line options
    """
    root_logger = logging.getLogger()
    add_stdout = False

    formatter = logging.Formatter("%(asctime)s %(levelname)-5.5s "
                                  "[{ident}] %(message)s"
                                  .format(ident=IDENT))

    # Write out to a logfile
    if options.logfile:
        handler = ClosingFileHandler(options.logfile)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
    else:
        # The logfile wasn't specified. Add a stdout logger.
        add_stdout = True

    if options.verbose:
        # Add a stdout logger as well in verbose mode
        root_logger.setLevel(logging.DEBUG)
        add_stdout = True
    else:
        root_logger.setLevel(logging.INFO)

    if add_stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        stdout_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(stdout_handler)


class ClosingFileHandler(logging.StreamHandler):
    def __init__(self, filename):
        super(ClosingFileHandler, self).__init__()
        self.filename = os.path.abspath(filename)
        self.setStream(None)

    def emit(self, record):
        with open(self.filename, "a") as fp:
            self.setStream(fp)
            super(ClosingFileHandler, self).emit(record)
            self.setStream(None)

    def setStream(self, stream):
        setStream = getattr(super(ClosingFileHandler, self), 'setStream', None)
        if callable(setStream):
            return setStream(stream)
        if stream is self.stream:
            result = None
        else:
            result = self.stream
            self.acquire()
            try:
                self.flush()
                self.stream = stream
            finally:
                self.release()
        return result


class ScriptRC(object):
    """Enum for script return codes"""
    SUCCESS = 0
    FAILURE = 1
    EXCEPTION = 2


class ScriptException(Exception):
    pass


if __name__ == '__main__':
    # Get the options from the user
    options = get_options()

    # Setup logging using the user options
    setup_logging(options)

    # Run main script.
    try:
        rc = run(options)
    except Exception as e:
        log.exception(e)
        rc = ScriptRC.EXCEPTION

    log.debug("Returning %d", rc)
    sys.exit(rc)
    
