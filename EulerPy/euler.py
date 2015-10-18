# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from collections import OrderedDict

import click

from EulerPy import __version__
from EulerPy.problem import Problem
from EulerPy.utils import clock, format_time, problem_glob


# --cheat / -c
def cheat(num):
    """View the answer to a problem."""
    # Define solution before echoing in case solution does not exist
    solution = click.style(Problem(num).solution, bold=True)
    click.confirm("View answer to problem %i?" % num, abort=True)
    click.echo("The answer to problem {} is {}.".format(num, solution))


# --generate / -g
def generate(num, prompt_default=True):
    """Generates Python file for a problem."""
    p = Problem(num)

    problem_text = p.text

    msg = "Generate file for problem %i?" % num
    click.confirm(msg, default=prompt_default, abort=True)

    # Allow skipped problem files to be recreated
    if p.glob:
        filename = str(p.file)
        msg = '"{}" already exists. Overwrite?'.format(filename)
        click.confirm(click.style(msg, fg='red'), abort=True)
    else:
        # Try to keep prefix consistent with existing files
        previous_file = Problem(num - 1).file
        prefix = previous_file.prefix if previous_file else ''
        filename = p.filename(prefix=prefix)

    header = 'Project Euler Problem %i' % num
    divider = '=' * len(header)
    text = '\n'.join([header, divider, '', problem_text])
    content = '\n'.join(['"""', text, '"""'])

    with open(filename, 'w') as f:
        f.write(content + '\n\n\n')

    click.secho('Successfully created "{}".'.format(filename), fg='green')

    # Copy over problem resources if required
    if p.resources:
        p.copy_resources()


# --preview / -p
def preview(num):
    """Prints the text of a problem."""
    # Define problem_text before echoing in case problem does not exist
    problem_text = Problem(num).text
    click.secho("Project Euler Problem %i" % num, bold=True)
    click.echo(problem_text)


# --skip / -s
def skip(num):
    """Generates Python file for the next problem."""
    click.echo("Current problem is problem %i." % num)
    generate(num + 1, prompt_default=False)
    Problem(num).file.change_suffix('-skipped')


# --verify / -v
def verify(num, filename=None, exit=True):
    """Verifies the solution to a problem."""
    p = Problem(num)

    filename = filename or p.filename()

    if not os.path.isfile(filename):
        # Attempt to verify the first problem file matched by glob
        if p.glob:
            filename = str(p.file)
        else:
            click.secho('No file found for problem %i.' % p.num, fg='red')
            sys.exit(1)

    solution = p.solution
    click.echo('Checking "{}" against solution: '.format(filename), nl=False)

    cmd = (sys.executable or 'python', filename)
    start = clock()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout = proc.communicate()[0]
    end = clock()
    time_info = format_time(start, end)

    # Return value of anything other than 0 indicates an error
    if proc.poll() != 0:
        click.secho('Error calling "{}".'.format(filename), fg='red')
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
        click.echo()  # force output to start on next line
        click.secho('\n'.join(output_lines), bold=True, fg='red')
    else:
        is_correct = output_lines[0] == solution
        fg_colour = 'green' if is_correct else 'red'
        click.secho(output_lines[0], bold=True, fg=fg_colour)

    click.secho(time_info, fg='cyan')

    # Remove any suffix from the filename if its solution is correct
    if is_correct:
        p.file.change_suffix('')

    # Exit here if answer was incorrect, otherwise return is_correct value
    return sys.exit(1) if exit and not is_correct else is_correct


# --verify-all
def verify_all(num):
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
        # Catch KeyboardInterrupt during verification to allow the user to
        # skip the verification of a specific problem if it takes too long
        try:
            is_correct = verify(file.num, filename=str(file), exit=False)
        except KeyboardInterrupt:
            overview[file.num] = status['skipped']
        else:
            if is_correct is None:  # error was returned by problem file
                overview[file.num] = status['error']
            elif is_correct:
                overview[file.num] = status['correct']
            elif not is_correct:
                overview[file.num] = status['incorrect']

                # Attempt to add "skipped" suffix to the filename if the
                # problem file is not the current problem. This is useful
                # when the --verify-all is used in a directory containing
                # files generated pre-v1.1 (before files with suffixes)
                if file.num != num:
                    file.change_suffix('-skipped')

        # Separate each verification with a newline
        click.echo()

    # Print overview of the status of each problem
    legend = ', '.join('{} = {}'.format(v, k) for k, v in status.items())

    click.echo('-' * 63)
    click.echo(legend + '\n')

    # Rows needed for overview is based on the current problem number
    num_of_rows = (num + 19) // 20

    for row in range(1, num_of_rows + 1):
        low, high = (row * 20) - 19, (row * 20)
        click.echo("Problems {:03d}-{:03d}: ".format(low, high), nl=False)

        for problem in range(low, high + 1):
            # Add missing status to problems with no corresponding file
            status = overview[problem] if problem in overview else '.'

            # Separate problem indicators into groups of 5
            spacer = '   ' if (problem % 5 == 0) else ' '

            # Start a new line at the end of each row
            click.secho(status + spacer, nl=(problem % 20 == 0))

    click.echo()


def euler_options(fn):
    """Decorator to link CLI options with their appropriate functions"""
    euler_functions = cheat, generate, preview, skip, verify, verify_all

    # Reverse functions to print help page options in alphabetical order
    for option in reversed(euler_functions):
        name, docstring = option.__name__, option.__doc__
        kwargs = {'flag_value': option, 'help': docstring}

        # Apply flag(s) depending on whether or not name is a single word
        flag = '--%s' % name.replace('_', '-')
        flags = [flag] if '_' in name else [flag, '-%s' % name[0]]

        fn = click.option('option', *flags, **kwargs)(fn)

    return fn


@click.command(name='euler', options_metavar='[OPTION]')
@click.argument('problem', default=0, type=click.IntRange(0, None))
@euler_options
@click.version_option(version=__version__, message="EulerPy %(version)s")
def main(option, problem):
    """Python-based Project Euler command line tool."""
    # No problem given (or given option ignores the problem argument)
    if problem == 0 or option in {skip, verify_all}:
        # Determine the highest problem number in the current directory
        files = problem_glob()
        problem = max(file.num for file in files) if files else 0

        # No Project Euler files in current directory (no glob results)
        if problem == 0:
            # Generate the first problem file if option is appropriate
            if option not in {cheat, preview, verify_all}:
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
            verify(problem)
            problem += 1
            option = generate

    # Problem given but no option; decide between generate and verify
    elif option is None:
        option = verify if Problem(problem).glob else generate

    # Execute function based on option
    option(problem)
    sys.exit(0)
