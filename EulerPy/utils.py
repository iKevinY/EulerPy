# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import glob
import math

from EulerPy.problem import ProblemFile


def problem_glob(extension='.py'):
    """Returns ProblemFile objects for all valid problem files"""
    filenames = glob.glob('*[0-9][0-9][0-9]*{}'.format(extension))
    return [ProblemFile(file) for file in filenames]

# Use the resource module instead of time.clock() if possible (on Unix)
try:
    import resource

except ImportError:
    import time

    def clock():
        """
        Under Windows, system CPU time can't be measured. Return time.clock()
        as user time and None as system time.
        """
        return time.clock(), None

else:
    def clock():
        """
        Returns a tuple (t_user, t_system) since the start of the process.
        This is done via a call to resource.getrusage, so it avoids the
        wraparound problems in time.clock().
        """
        return resource.getrusage(resource.RUSAGE_CHILDREN)[:2]


def human_time(timespan, precision=3):
    """Formats the timespan in a human readable format"""

    if timespan >= 60.0:
        # Format time greater than one minute in a human-readable format
        # Idea from http://snipplr.com/view/5713/
        def _format_long_time(time):
            suffixes = ('d', 'h', 'm', 's')
            lengths = (24*60*60, 60*60, 60, 1)

            for suffix, length in zip(suffixes, lengths):
                value = int(time / length)

                if value > 0:
                    time %= length
                    yield '%i%s' % (value, suffix)

                if time < 1:
                    break

        return ' '.join(_format_long_time(timespan))

    else:
        units = ['s', 'ms', 'us', 'ns']

        # Attempt to replace 'us' with 'µs' if UTF-8 encoding has been set
        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding == 'UTF-8':
            try:
                units[2] = b'\xc2\xb5s'.decode('utf-8')
            except UnicodeEncodeError:
                pass

        scale = [1.0, 1e3, 1e6, 1e9]

        if timespan > 0.0:
            # Determine scale of timespan (s = 0, ms = 1, µs = 2, ns = 3)
            order = min(-int(math.floor(math.log10(timespan)) // 3), 3)
        else:
            order = 3

        return '%.*g %s' % (precision, timespan * scale[order], units[order])


def format_time(start, end):
    """Returns string with relevant time information formatted properly"""
    try:
        cpu_usr = end[0] - start[0]
        cpu_sys = end[1] - start[1]

    except TypeError:
        # `clock()[1] == None` so subtraction results in a TypeError
        return 'Time elapsed: {}'.format(human_time(cpu_usr))

    else:
        times = (human_time(x) for x in (cpu_usr, cpu_sys, cpu_usr + cpu_sys))
        return 'Time elapsed: user: {}, sys: {}, total: {}'.format(*times)
