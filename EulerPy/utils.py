# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import math

import click


def rename_file(old, new):
    if old != new:
        os.rename(old, new)
        click.secho('Renamed "{0}" to "{1}".'.format(old, new), fg='yellow')


# Use the resource module instead of time.clock() if possible (on Unix)
try:
    import resource

except ImportError:
    import time

    HAS_RUSAGE = False

    def clock():
        """
        Under Windows, system CPU time can't be measured. Return clock() as
        user time and zero as system time.
        """
        return time.clock(), 0.0

else:
    HAS_RUSAGE = True

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
        parts = [('d', 60*60*24), ('h', 60*60), ('min', 60), ('s', 1)]
        times = []
        leftover = timespan
        for suffix, length in parts:
            value = int(leftover / length)
            if value > 0:
                leftover %= length
                times.append('%s%s' % (str(value), suffix))
            if leftover < 1:
                break

        return ' '.join(times)

    else:
        # Unfortunately, the Unicode symbol for mu can cause problems.
        # See bug: https://bugs.launchpad.net/ipython/+bug/348466
        # Try to prevent crashes by being more secure than it needs to be
        # (e.g. Eclipse can print mu but has no sys.stdout.encoding set).

        units = ['s', 'ms', 'us', 'ns']

        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
            try:
                # Attempt to replace 'us' with 'µs' for microsecond unit
                units[2] = b'\xc2\xb5s'.decode('utf-8')
            except:
                pass

        scale = [1, 1e3, 1e6, 1e9]

        if timespan > 0.0:
            # Determine scale of timespan (s = 0, ms = 1, µs = 2, ns = 3)
            order = min(-int(math.floor(math.log10(timespan)) // 3), 3)
        else:
            order = 3

        return '%.*g %s' % (precision, timespan * scale[order], units[order])


def format_time(start, end):
    """Returns string with relevant time information formatted properly"""
    cpu_usr = end[0] - start[0]
    cpu_sys = end[1] - start[1]
    cpu_tot = cpu_usr + cpu_sys

    if HAS_RUSAGE:
        return 'Time elapsed: user: {0}, sys: {1}, total: {2}'.format(
            human_time(cpu_usr),
            human_time(cpu_sys),
            human_time(cpu_tot)
        )

    else:
        return 'Time elapsed: {0}'.format(human_time(cpu_usr))
