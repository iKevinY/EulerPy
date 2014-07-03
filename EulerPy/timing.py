# -*- coding: utf-8 -*-

import sys
import math

HAS_RUSAGE = False


# If possible (Unix), use the resource module instead of time.clock()
try:
    import resource
    HAS_RUSAGE = True

    def clock():
        """clock() -> (t_user,t_system)

        Returns a tuple of user/system times since the start of the process.
        This is done via a call to resource.getrusage, so it avoids the
        wraparound problems in time.clock().
        """
        return resource.getrusage(resource.RUSAGE_CHILDREN)[:2]
except ImportError:
    # There is no distinction of user/system time under Windows, so we just use
    # time.clock() for everything...
    import time

    def clock():
        """Under Windows, system CPU time can't be measured.

        This just returns clock() and zero.
        """
        return time.clock(), 0.0


def human_time(timespan, precision=3):
    """Formats the timespan in a human readable form"""

    if timespan >= 60.0:
        # we have more than a minute, format that in a human readable form
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

    # Unfortunately the unicode 'micro' symbol can cause problems in
    # certain terminals.
    # See bug: https://bugs.launchpad.net/ipython/+bug/348466
    # Try to prevent crashes by being more secure than it needs to
    # E.g. eclipse is able to print a µ, but has no sys.stdout.encoding set.
    units = ['s', 'ms', 'us', 'ns']  # the save value
    if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
        try:
            micro = b'\xc2\xb5s'.decode('utf-8')
            units = ['s', 'ms', micro, 'ns']
        except:
            pass
    scaling = [1, 1e3, 1e6, 1e9]

    if timespan > 0.0:
        order = min(-int(math.floor(math.log10(timespan)) // 3), 3)
    else:
        order = 3
    return '%.*g %s' % (precision, timespan * scaling[order], units[order])


def format_time(start, end):
    cpu_user = end[0] - start[0]
    cpu_sys = end[1] - start[1]
    cpu_tot = cpu_user + cpu_sys
    if HAS_RUSAGE:
        return 'Time elapsed: user: {0}, sys: {1}, total: {2}'.format(
            human_time(cpu_user), human_time(cpu_sys), human_time(cpu_tot),
        )
    else:
        return 'Time elapsed: {0}'.format(human_time(cpu_user))
