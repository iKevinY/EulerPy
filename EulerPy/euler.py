# -*- coding: utf-8 -*-

import os
import sys
import glob
import subprocess

import click

from EulerPy.problem import Problem
from EulerPy.utils import clock, format_time, rename_file


# --cheat / -c
def cheat(p):
    """View the answer to a problem."""
    solution = click.style(p.solution, bold=True)
    click.confirm("View answer to problem %i?" % p.num, abort=True)
    click.echo("The answer to problem %i is {0}.".format(solution) % p.num)


# --generate / -g
def generate(p, prompt_default=True):
    """Generates Python file for a problem."""

    msg = "Generate file for problem %i?" % p.num
    click.confirm(msg, default=prompt_default, abort=True)
    problemText = p.text

    if os.path.isfile(p.filename):
        msg = '"{0}" already exists. Overwrite?'.format(p.filename)
        click.confirm(click.style(msg, fg='red'), abort=True)

    problemHeader = 'Project Euler Problem %i\n' % p.num
    problemHeader += '=' * len(problemHeader.strip()) + '\n\n'

    with open(p.filename, 'w') as file:
        file.write('"""\n')
        file.write(problemHeader)
        file.write(problemText)
        file.write('"""\n\n\n')

    click.secho('Successfully created "{0}".'.format(p.filename), fg='green')


# --preview / -p
def preview(p):
    """Prints the text of a problem."""
    # Define problemText instead of echoing it right away
    # in case the problem does not exist in problems.txt
    problemText = p.text[:-1] # strip newline from text
    click.secho("Project Euler Problem %i" % p.num, bold=True)
    click.echo(problemText)


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
        # Attempt a fuzzy search for problem files using the glob module
        for fuzzy_file in glob.glob('{0:03d}*.py'.format(p.num)):
            if os.path.isfile(fuzzy_file):
                filename = fuzzy_file
                break
        else:
            click.secho('No file found for problem %i.' % p.num, fg='red')
            sys.exit(1)

    solution = p.solution
    click.echo('Checking "{0}" against solution: '.format(filename), nl=False)

    cmd = [sys.executable or 'python', filename]
    start = clock()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout = proc.communicate()[0]
    end = clock()
    time_info = format_time(start, end)

    # Return value of anything other than 0 indicates an error
    if proc.poll() != 0:
        click.secho('Error calling "{0}".'.format(filename), fg='red')
        click.secho(time_info, fg='cyan')

        # Exit here if appropriate, otherwise return None (for --verify-all)
        if exit:
            sys.exit(1)
        else:
            return None

    # Python 3 returns bytes; use a valid encoding like ASCII
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
        for line in output_lines:
            click.secho(line, bold=True, fg='red')
    else:
        is_correct = output_lines[0] == solution
        fg_colour = 'green' if is_correct else 'red'
        click.secho(output_lines[0], bold=True, fg=fg_colour)

    click.secho(time_info, fg='cyan')

    # Exit here if answer was incorrect
    if exit and not is_correct:
        sys.exit(1)
    else:
        # Remove any suffix from the filename if its solution is correct
        if is_correct and filename != p.filename:
            rename_file(filename, p.filename)

        return is_correct


# --verify-all
def verify_all(current_p):
    """
    Verifies all problem files in the current directory and
    prints an overview of the status of each problem.
    """

    overview = {}

    # Search through problem files using glob module
    for filename in glob.glob('[0-9][0-9][0-9]*.py'):
        p = Problem(int(filename[:3]))

        # Catch KeyboardInterrupt during verification to allow the user
        # to skip the verification of a problem if it takes too long
        try:
            is_correct = verify(p, filename=filename, exit=False)
        except KeyboardInterrupt:
            overview[p.num] = click.style('S', fg='cyan')
        else:
            if is_correct is None: # error was returned by problem file
                overview[p.num] = click.style('E', fg='yellow')
            elif is_correct:
                overview[p.num] = click.style('C', fg='green')
            elif not is_correct:
                overview[p.num] = click.style('I', fg='red')

                # Attempt to add "skipped" suffix to the filename if the
                # problem file is not the current problem. This is useful
                # when the --verify-all is used in a directory containing
                # files generated pre-v1.1 (before files with suffixes)
                if p.num != current_p.num:
                    skipped_name = p.suf_name('skipped')
                    rename_file(filename, skipped_name)

        # Separate each verification with a newline
        click.echo()

    # No Project Euler files in the current directory
    if not overview:
        click.echo("No Project Euler files found in the current directory.")
        sys.exit(1)

    # Print overview of the status of each problem
    click.echo('-' * 63)

    legend = ', '.join(
        '{0} = {1}'.format(click.style(symbol, bold=True, fg=colour), name)
        for symbol, name, colour in (
            ('C', 'correct', 'green'),
            ('I', 'incorrect', 'red'),
            ('E', 'error', 'yellow'),
            ('S', 'skipped', 'cyan'),
            ('.', 'missing', 'white'),
        )
    )

    click.echo(legend + '\n')

    # Rows needed for overview is based on the current problem number
    num_of_rows = (current_p.num + 19) // 20

    for row in range(1, num_of_rows + 1):
        low, high = (row * 20) - 19, (row * 20)
        click.echo("Problems {0:03d}-{1:03d}: ".format(low, high), nl=False)

        for problem in range(low, high + 1):
            # Add missing status to problems with no problem file
            status = overview[problem] if problem in overview else '.'
            click.secho(status, bold=True, nl=False)

            # Separate problem indicators into groups of 5
            click.echo('   ' if problem % 5 == 0 else ' ', nl=False)

        # Start a new line at the end of each row
        click.echo()

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
        for filename in glob.glob('[0-9][0-9][0-9]*.py'):
            num = int(filename[:3])
            if num > problem:
                problem = num

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
        if not option:
            verify(Problem(problem))
            problem += 1
            option = generate

    # Problem given but no option; decide between generate and verify
    elif not option:
        match_found = any(glob.iglob('{0:03d}*.py'.format(problem)))
        option = verify if match_found else generate

    # Execute function based on option (pass Problem object as argument)
    option(Problem(problem))
    sys.exit()
