# -*- coding: utf-8 -*-

import os
import sys
import glob
import linecache
import subprocess

import click

from EulerPy.timing import clock, format_time


def get_filename(problem, width=3, suffix=''):
    """Returns filename padded with leading zeros"""
    return '{0:0{w}d}{1}.py'.format(problem, suffix, w=width)


def get_solution(problem):
    """Returns the answer to a given problem"""
    solutionsFile = os.path.join(os.path.dirname(__file__), 'solutions.txt')
    line = linecache.getline(solutionsFile, problem)

    try:
        answer = line.split('. ')[1].strip()
    except IndexError:
        answer = None

    if answer:
        return answer
    else:
        msg = 'Answer for problem %i not found in solutions.txt.' % problem
        click.secho(msg, fg='red')
        click.echo('If you have an answer, consider submitting a pull request '
                   'to EulerPy at https://github.com/iKevinY/EulerPy.')
        sys.exit(1)


def get_problem(problem):
    """Parses problems.txt and returns problem text"""
    def problem_iter(problem, problemFile):
        with open(problemFile) as file:
            problemText = False
            lastLine = ''

            for line in file:
                if line.strip() == 'Problem %i' % problem:
                    problemText = True

                if problemText:
                    if line == lastLine == '\n':
                        break
                    else:
                        yield line[:-1]
                        lastLine = line

    problemFile = os.path.join(os.path.dirname(__file__), 'problems.txt')
    problemLines = [line for line in problem_iter(problem, problemFile)]

    if problemLines:
        # First three lines are the problem number, the divider line,
        # and a newline, so don't include them in the returned string
        return '\n'.join(problemLines[3:])
    else:
        msg = 'Problem %i not found in problems.txt.' % problem
        click.secho(msg, fg='red')
        click.echo('If this problem exists on Project Euler, consider '
                   'submitting a pull request to EulerPy at '
                   'https://github.com/iKevinY/EulerPy.')
        sys.exit(1)


def rename_file(old, new):
    """Renames a file"""
    os.rename(old, new)
    click.secho('Renamed "{0}" to "{1}".'.format(old, new), fg='yellow')


# --cheat / -c
def cheat(problem):
    """View the answer to a problem."""
    # get_solution() will exit here if the solution does not exist
    solution = click.style(get_solution(problem), bold=True)
    click.confirm("View answer to problem %i?" % problem, abort=True)
    click.echo("The answer to problem %i is {0}.".format(solution) % problem)


# --generate / -g
def generate(problem, prompt_default=True):
    """Generates Python file for a problem."""

    msg = "Generate file for problem %i?" % problem
    click.confirm(msg, default=prompt_default, abort=True)
    problemText = get_problem(problem)

    filename = get_filename(problem)

    if os.path.isfile(filename):
        msg = '"{0}" already exists. Overwrite?'.format(filename)
        click.confirm(click.style(msg, fg='red'), abort=True)

    problemHeader = 'Project Euler Problem %i\n' % problem
    problemHeader += '=' * len(problemHeader.strip()) + '\n\n'

    with open(filename, 'w') as file:
        file.write('"""\n')
        file.write(problemHeader)
        file.write(problemText)
        file.write('"""\n\n\n')

    click.secho('Successfully created "{0}".'.format(filename), fg='green')


# --preview / -p
def preview(problem):
    """Prints the text of a problem."""
    # Define problemText instead of echoing it right away
    # in case the problem does not exist in problems.txt
    problemText = get_problem(problem)[:-1] # strip newline from text
    click.secho("Project Euler Problem %i" % problem, bold=True)
    click.echo(problemText)


# --skip / -s
def skip(problem):
    """Generates Python file for the next problem."""
    click.echo("Current problem is problem %i." % problem)
    generate(problem + 1, prompt_default=False)

    # Rename the skipped file
    filename = get_filename(problem)
    skipped_name = get_filename(problem, suffix='-skipped')
    rename_file(filename, skipped_name)


# --verify / -v
def verify(problem, filename=None, exit=True):
    """Verifies the solution to a problem."""
    filename = filename or get_filename(problem)

    if not os.path.isfile(filename):
        # Do a fuzzy search for problem files using the glob module
        msg = "Attempting fuzzy search for problem {0} file.".format(problem)
        click.echo(msg)

        for fuzzy_file in glob.glob('{0:03d}*.py'.format(problem)):
            if os.path.isfile(fuzzy_file):
                filename = fuzzy_file
                break
        else:
            click.secho('No file found for problem %i.' % problem, fg='red')
            sys.exit(1)

    # get_solution() will exit here if the solution does not exist
    solution = get_solution(problem)

    click.echo('Checking "{0}" against solution: '.format(filename), nl=False)

    cmd = [sys.executable or 'python', filename]
    start = clock()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    end = clock()
    time_info = format_time(start, end)

    # Python 3 returns bytes; use a valid encoding like ASCII as the output
    # will fall in that range
    if isinstance(stdout, bytes):
        output = stdout.decode('ascii')

    # Return value of anything other than 0 indicates an error
    if proc.poll() != 0:
        click.secho('Error calling "{0}".'.format(filename), fg='red')
        click.secho(time_info, fg='cyan')
        sys.exit(1)

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
        # Strip the filename of any suffix if the solution is now correct
        if is_correct and filename != get_filename(problem):
            rename_file(filename, get_filename(problem))

        return is_correct


# --verify-all
def verify_all(largest_problem):
    """
    Verifies all problem files in the current directory and
    prints an overview of the status of each problem.
    """

    pass


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
            problem = num if num > problem else problem

        # No Project Euler files in current directory (no glob results)
        if problem == 0:
            problem = 1

            # Generate problem 1 if option deals with problem files
            if option not in (cheat, preview):
                msg = "No Project Euler files found in the current directory."
                click.echo(msg)
                option = generate

        # --preview and no problem; preview the next problem
        elif option is preview:
            problem += 1

        # No option and no problem; generate next file if answer is
        # correct (verify() exits if the solution is incorrect)
        if not option:
            verify(problem)
            problem += 1
            option = generate

    # Problem given but no option; decide between generate and verify
    elif not option:
        problemFile = get_filename(problem)
        option = verify if os.path.isfile(problemFile) else generate

    # Execute function based on option
    option(problem)
    sys.exit()
