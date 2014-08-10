# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from collections import OrderedDict

import click

from EulerPy.problem import Problem
from EulerPy.utils import clock, format_time, problem_glob, rename_file


# --cheat / -c
def cheat(p):
    """View the answer to a problem."""
    # Define first instead of echoing in case the solution does not exist
    solution = click.style(p.solution, bold=True)
    click.confirm("View answer to problem %i?" % p.num, abort=True)
    click.echo("The answer to problem %i is {0}.".format(solution) % p.num)


# --generate / -g
def generate(p, prompt_default=True):
    """Generates Python file for a problem."""

    msg = "Generate file for problem %i?" % p.num
    click.confirm(msg, default=prompt_default, abort=True)

    # Allow skipped problem files to be recreated
    problem_files = list(p.iglob)
    if problem_files:
        filename = problem_files[0]
        msg = '"{0}" already exists. Overwrite?'.format(filename)
        click.confirm(click.style(msg, fg='red'), abort=True)
    else:
        filename = p.filename

    problemHeader = 'Project Euler Problem %i\n' % p.num
    problemHeader += '=' * len(problemHeader.strip()) + '\n\n'

    problemText = p.text

    with open(p.filename, 'w') as file:
        file.write('"""\n')
        file.write(problemHeader)
        file.write(problemText)
        file.write('"""\n\n\n')

    click.secho('Successfully created "{0}".'.format(filename), fg='green')

    # Copy over problem resources if required
    if p.resources:
        p.copy_resources()


# --preview / -p
def preview(p):
    """Prints the text of a problem."""
    # Define first instead of echoing in case the problem does not exist
    problem_text = p.text[:-1] # strip newline from text
    click.secho("Project Euler Problem %i" % p.num, bold=True)
    click.echo(problem_text)


# --skip / -s
def skip(p):
    """Generates Python file for the next problem."""
    click.echo("Current problem is problem %i." % p.num)
    next_p = Problem(p.num + 1)
    generate(next_p, prompt_default=False)
    rename_file(p.filename, p.suf_name('skipped'))


# --verify / -v
def verify(p, filename=None, exit=True):
    """Verifies the solution to a problem."""
    filename = filename or p.filename

    if not os.path.isfile(filename):
        # Attempt to verify the first problem file matched by glob
        try:
            filename = next(p.iglob)
        except StopIteration:
            click.secho('No file found for problem %i.' % p.num, fg='red')
            sys.exit(1)

    solution = p.solution
    click.echo('Checking "{0}" against solution: '.format(filename), nl=False)

    cmd = (sys.executable or 'python', filename)
    start = clock()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout = proc.communicate()[0]
    end = clock()
    time_info = format_time(start, end)

    # Return value of anything other than 0 indicates an error
    if proc.poll() != 0:
        click.secho('Error calling "{0}".'.format(filename), fg='red')
        click.secho(time_info, fg='cyan')

        # Return None if option is not --verify-all, otherwise exit
        return sys.exit(1) if exit else None

    # Decode output if returned as bytes (Python 3)
    if isinstance(stdout, bytes):
        output = stdout.decode('ascii')

    # Split output lines into array; make empty output more readable
    output_lines = output.splitlines() if output else ['[no output]']

    # If output is multi-lined, print the first line of the output on a
    # separate line from the "checking against solution" message, and
    # skip the solution check (multi-line solution won't be correct)
    if len(output_lines) > 1:
        is_correct = False
        click.echo() # force output to start on next line
        click.secho('\n'.join(output_lines), bold=True, fg='red')
    else:
        is_correct = output_lines[0] == solution
        fg_colour = 'green' if is_correct else 'red'
        click.secho(output_lines[0], bold=True, fg=fg_colour)

    click.secho(time_info, fg='cyan')

    # Remove any suffix from the filename if its solution is correct
    if is_correct and filename != p.filename:
        rename_file(filename, p.filename)

    # Exit here if answer was incorrect, otherwise return is_correct value
    return sys.exit(1) if exit and not is_correct else is_correct


# --verify-all
def verify_all(current_p):
    """
    Verifies all problem files in the current directory and
    prints an overview of the status of each problem.
    """

    # Define various problem statuses
    keys = ('correct', 'incorrect', 'error', 'skipped', 'missing')
    symbols = ('C', 'I', 'E', 'S', '.')
    colours = ('green', 'red', 'yellow', 'cyan', 'white')

    status = OrderedDict(
        (key, click.style(symbol, fg=colour, bold=True))
        for key, symbol, colour in zip(keys, symbols, colours)
    )

    overview = {}

    # Search through problem files using glob module
    files = problem_glob()

    # No Project Euler files in the current directory
    if not files:
        click.echo("No Project Euler files found in the current directory.")
        sys.exit(1)

    for file in files:
        p = Problem(int(file[:3]))

        # Catch KeyboardInterrupt during verification to allow the user
        # to skip the verification of a problem if it takes too long
        try:
            is_correct = verify(p, filename=file, exit=False)
        except KeyboardInterrupt:
            overview[p.num] = status['skipped']
        else:
            if is_correct is None: # error was returned by problem file
                overview[p.num] = status['error']
            elif is_correct:
                overview[p.num] = status['correct']
            elif not is_correct:
                overview[p.num] = status['incorrect']

                # Attempt to add "skipped" suffix to the filename if the
                # problem file is not the current problem. This is useful
                # when the --verify-all is used in a directory containing
                # files generated pre-v1.1 (before files with suffixes)
                if p.num != current_p.num:
                    rename_file(file, p.suf_name('skipped'))

        # Separate each verification with a newline
        click.echo()

    # Print overview of the status of each problem
    legend = ', '.join('{0} = {1}'.format(v, k) for k, v in status.items())

    click.echo('-' * 63)
    click.echo(legend + '\n')

    # Rows needed for overview is based on the current problem number
    num_of_rows = (current_p.num + 19) // 20

    for row in range(1, num_of_rows + 1):
        low, high = (row * 20) - 19, (row * 20)
        click.echo("Problems {0:03d}-{1:03d}: ".format(low, high), nl=False)

        for problem in range(low, high + 1):
            # Add missing status to problems with no corresponding file
            status = overview[problem] if problem in overview else '.'

            # Separate problem indicators into groups of 5
            spacer = '   ' if (problem % 5 == 0) else ' '

            # Start a new line at the end of each row
            click.secho(status + spacer, nl=(problem % 20 == 0))

    click.echo()


def euler_options(function):
    """Decorator to link CLI options with their appropriate functions"""
    eulerFunctions = cheat, generate, preview, skip, verify, verify_all

    # Reversed to decorate functions in correct order (applied inversely)
    for option in reversed(eulerFunctions):
        name, docstring = option.__name__, option.__doc__
        flags = ['--%s' % name.replace('_', '-')]

        # Add short flag if function name is a single word
        if not '_' in name:
            flags.append('-%s' % name[0])

        kwargs = {'flag_value': option, 'help': docstring}

        function = click.option('option', *flags, **kwargs)(function)

    return function


@click.command(name='euler', options_metavar='[OPTION]')
@click.argument('problem', default=0, type=click.IntRange(0, None))
@euler_options
def main(option, problem):
    """Python-based Project Euler command line tool."""
    # No problem given (or given option ignores the problem argument)
    if problem == 0 or option in (skip, verify_all):
        # Determine the highest problem number in the current directory
        files = problem_glob()
        problem = max(int(file[:3]) for file in files) if files else 0

        # No Project Euler files in current directory (no glob results)
        if problem == 0:
            # Generate the first problem file if option is appropriate
            if option not in (cheat, preview, verify_all):
                msg = "No Project Euler files found in the current directory."
                click.echo(msg)
                option = generate

            # Set problem number to 1
            problem = 1

        # --preview and no problem; preview the next problem
        elif option is preview:
            problem += 1

        # No option and no problem; generate next file if answer is
        # correct (verify() will exit if the solution is incorrect)
        if option is None:
            verify(Problem(problem))
            problem += 1
            option = generate

    # Problem given but no option; decide between generate and verify
    elif option is None:
        option = verify if any(Problem(problem).iglob) else generate

    # Execute function based on option (pass Problem object as argument)
    option(Problem(problem))
    sys.exit(0)
