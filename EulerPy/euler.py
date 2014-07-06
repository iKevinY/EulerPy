# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import linecache

import click

from EulerPy.timing import clock, format_time

# Number of problems present in problems.txt
TOTAL_PROBLEMS = 256


def get_filename(problem, width=3):
    """Returns filename padded with leading zeros"""
    return '{0:0{w}d}.py'.format(problem, w=width)


def get_solution(problem):
    """Returns the answer to a given problem"""
    solutionsFile = os.path.join(os.path.dirname(__file__), 'solutions.txt')
    line = linecache.getline(solutionsFile, problem)

    # Isolate answer from the question number and trailing newline
    answer = line.split(". ")[1].strip()

    if answer == '':
        click.echo('No known answer for problem #{0}.'.format(problem))
        click.echo('If you have an answer, consider submitting a pull '
            'request to EulerPy at https://github.com/iKevinY/EulerPy.')
        return None
    else:
        return answer


def get_problem(problem):
    """Parses problems.txt and returns problem text"""
    problemsFile = os.path.join(os.path.dirname(__file__), 'problems.txt')
    problemLines = []

    with open(problemsFile) as file:
        isProblemText = False
        lastLine = ''

        for line in file:
            if line.strip() == 'Problem {0}'.format(problem):
                isProblemText = True

            if isProblemText:
                # Two subsequent empty lines indicates that the current
                # problem text has ended, so stop iterating over file
                if line == lastLine == '\n':
                    break
                else:
                    problemLines.append(line[:-1])
                    lastLine = line

    # First three lines are the problem number, the divider line,
    # and a newline, so don't include them in the returned string
    return '\n'.join(problemLines[3:])


def determine_largest_problem():
    """Determines largest problem file in the current directory"""
    for problem in reversed(range(1, TOTAL_PROBLEMS + 1)):
        if os.path.isfile(get_filename(problem)):
            return problem
    else:
        return False


def generate_first_problem():
    """Creates 001.py in current directory"""
    click.echo("No Project Euler files found in the current directory.")
    generate(1)
    sys.exit()


# --cheat / -c
def cheat(problem):
    """View the answer to a problem."""
    solution = get_solution(problem)

    if solution:
        click.confirm("View answer to problem #{0}?".format(problem), abort=True)
        click.echo("The answer to problem #{0} is ".format(problem), nl=False)
        click.secho(solution, bold=True, nl=False)
        click.echo(".")


# --generate / -g
def generate(problem, prompt_default=True):
    """Generates Python file for a problem."""
    click.confirm("Generate file for problem #{0}?".format(problem),
                  default=prompt_default, abort=True)
    problemText = get_problem(problem)

    filename = get_filename(problem)

    if os.path.isfile(filename):
        click.secho('"{0}" already exists. Overwrite?'.format(filename),
                    fg='red', nl=False)
        click.confirm('', abort=True)

    problemHeader = 'Project Euler Problem #{0}\n'.format(problem)
    problemHeader += '=' * len(problemHeader) + '\n\n'

    with open(filename, 'w') as file:
        file.write('"""\n')
        file.write(problemHeader)
        file.write(problemText)
        file.write('"""\n\n\n')

    click.echo('Successfully created "{0}".'.format(filename))


# --preview / -p
def preview(problem):
    """Prints the text of a problem."""
    click.secho("Project Euler Problem #{0}".format(problem), bold=True)
    click.echo(get_problem(problem)[:-1])  # strip trailing newline


# --skip / -s
def skip(problem):
    """Generates Python file for the next problem."""
    click.echo("Current problem is problem #{0}.".format(problem))
    generate(problem + 1, prompt_default=False)


# --verify / -v
def verify(problem):
    """Verifies the solution to a problem."""
    filename = get_filename(problem)

    if not os.path.isfile(filename):
        click.secho('Error: "{0}" not found.'.format(filename), fg='red')
        sys.exit(1)

    solution = get_solution(problem)

    if solution:
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
            click.secho('[error]', fg='red', bold=True)
            click.secho(time_info, fg='cyan')
            sys.exit(1)

        # Split output lines into array; make empty output more readable
        output_lines = output.splitlines() if output else ['[no output]']

        # If output is multi-lined, print the first line of the output on a
        # separate line from the "checking against solution" message, and
        # skip the solution check (multi-line solution won't be correct)
        if len(output_lines) > 1:
            is_correct = False
            click.echo('') # force output to start on next line
            for line in output_lines:
                click.secho(line, bold=True, fg='red')
        else:
            is_correct = output_lines[0] == solution
            fg_colour = 'green' if is_correct else 'red'
            click.secho(output_lines[0], bold=True, fg=fg_colour)

        click.secho(time_info, fg='cyan')
        return is_correct


# Define all of EulerPy's options and their corresponding functions
EULER_FUNCTIONS = {
    'cheat': cheat,
    'generate': generate,
    'preview': preview,
    'skip': skip,
    'verify': verify,
}

def euler_options(function):
    """Decorator to set up EulerPy's CLI options"""
    # Reversed to decorate functions in correct order (applied inversely)
    for option in reversed(sorted(EULER_FUNCTIONS)):
        flags = ['--%s' % option, '-%s' % option[0]]
        kwargs = {
            'flag_value': option,
            'help': EULER_FUNCTIONS[option].__doc__
        }

        function = click.option('option', *flags, **kwargs)(function)

    return function

@click.command(name='euler', options_metavar='[OPTION]')
@click.argument('problem', default=0, type=click.IntRange(0, TOTAL_PROBLEMS))
@euler_options
def main(option, problem):
    """Python-based Project Euler command line tool."""

    # No option given; programatically determine appropriate action
    if option is None:
        if problem == 0:
            problem = determine_largest_problem()
            # No Project Euler files in current directory
            if not problem:
                generate_first_problem()

            # If correct answer was given, generate next problem file
            if verify(problem):
                generate(problem + 1)
            else:
                sys.exit(1)
        else:
            if os.path.isfile(get_filename(problem)):
                if not verify(problem):
                    sys.exit(1)
            else:
                generate(problem)

    else:
        # The skip option ignores problem number argument
        if problem == 0 or option == 'skip':
            problem = determine_largest_problem()

        if not problem:
            if option == 'preview':
                problem = 1
            else:
                generate_first_problem()

        # Execute function depending on option
        result = EULER_FUNCTIONS[option](problem)

        # If solution was being verified, exit with appropriate code
        if option == 'verify':
            sys.exit(not result)

    sys.exit()
