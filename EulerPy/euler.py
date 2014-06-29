# -*- coding: utf-8 -*-

import sys
import os
import time
import math
import subprocess
import linecache

import click

# Number of problems present in problems.txt
TOTAL_PROBLEMS = 202


def format_time(timespan, precision=3):
    """Formats the timespan in a human readable form"""

    if timespan >= 60.0:
        # Format time greater than one minute in a human readable format
        # Idea from http://snipplr.com/view/5713/
        parts = [('d', 60*60*24), ('h', 60*60), ('min', 60), ('s', 1)]
        time_parts = []
        leftover = timespan
        for suffix, length in parts:
            value = int(leftover / length)
            if value > 0:
                leftover = leftover % length
                time_parts.append('%s%s' % (str(value), suffix))
            if leftover < 1:
                break
        return ' '.join(time_parts)


    # Unfortunately the unicode 'micro' symbol can cause problems in
    # certain terminals.
    # See bug: https://bugs.launchpad.net/ipython/+bug/348466
    # Try to prevent crashes by being more secure than it needs to be
    # eg. Eclipse is able to print a µ, but has no sys.stdout.encoding set.
    units = ['s', 'ms', 'us', 'ns'] # the save value
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


def get_filename(problem):
    """Returns filename in the form `001.py`"""
    return '{0:03d}.py'.format(problem)


def get_solution(problem):
    """Returns the answer to a given problem"""
    solutionsFile = os.path.join(os.path.dirname(__file__), 'solutions.txt')
    line = linecache.getline(solutionsFile, problem)

    # Isolate answer from the question number and trailing newline
    answer = line.split(". ")[1].strip()

    if answer == '':
        click.echo('No known answer for problem #{0}.'.format(problem))
        click.echo('If you have an answer, consider submitting a pull ' +
            'request at https://github.com/iKevinY/EulerPy.')
        return None
    else:
        return answer


def verify_answer(problem):
    filename = get_filename(problem)

    if not os.path.isfile(filename):
        click.secho('Error: "{0}" not found.'.format(filename), fg='red')
        sys.exit(1)

    solution = get_solution(problem)

    if solution:
        click.echo('Checking "{0}" against solution: '.format(filename), nl=False)

        cmd = 'python {0}'.format(filename)
        wall_start = time.time()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, _ = proc.communicate()
        wall_end = time.time()

        # Calculate the wall time and format the output
        wall_time = wall_end - wall_start
        time_info = ' (time elapsed: {0})'.format(format_time(wall_time))

        # Python 3 returns bytes; use a valid encoding like ASCII as the output
        # will fall in that range
        if isinstance(output, bytes):
            output = output.decode('ascii')

        return_val = proc.poll()

        if return_val:
            click.secho('Error calling "{0}".'.format(filename), fg='red')
            sys.exit(1)

        # Strip newline from end of output if output is not a lone newline.
        # This behaviour is favourable to stripping all whitespace with strip()
        # as stripping all newlines from the output may inhib debugging done by
        # the user (if they were to use multiple print statements in their code
        # while in the process of atempting to solve the problem).
        try:
            if output[-1] == '\n':
                output = output[:-1]
        except IndexError:
            output = "[no output]"

        is_correct = output == solution
        click.secho(
            output, bold=True, nl=False, fg=('green' if is_correct else 'red')
        )
        click.secho(time_info, fg='cyan')
        return is_correct


def get_problem(problem):
    problemsFile = os.path.join(os.path.dirname(__file__), 'problems.txt')
    problemLines = []

    with open(problemsFile, 'r') as file:
        isProblemText = False
        sequentialBreaks = 0

        for line in file:
            if line == 'Problem {0}\n'.format(problem):
                isProblemText = True

            if isProblemText:
                if line == '\n':
                    sequentialBreaks += 1
                else:
                    sequentialBreaks = 0

                if sequentialBreaks >= 2:
                    break
                else:
                    problemLines.append(line[:-1])

    return '\n'.join(problemLines[3:])


def generate_file(problem, default=True):
    click.confirm("Generate file for problem #{0}?".format(problem),
                  default=default, abort=True)
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


def generate_first_problem():
    click.echo("No Project Euler files found in the current directory.")
    generate_file(1)
    sys.exit()


def view_solution(problem):
    solution = get_solution(problem)

    if solution:
        click.confirm("View answer to problem #{0}?".format(problem), abort=True)
        click.echo("The answer to problem #{0} is ".format(problem), nl=False)
        click.secho(solution, bold=True, nl=False)
        click.echo(".")


def preview_problem(problem):
    click.secho("Project Euler Problem #{0}".format(problem), bold=True)
    click.echo(get_problem(problem)[:-1])  # strip trailing newline


def determine_largest_problem():
    for problem in reversed(range(1, TOTAL_PROBLEMS + 1)):
        if os.path.isfile(get_filename(problem)):
            return problem
    else:
        return False


help = {
    'cheat': 'View the answer to a problem.',
    'generate': 'Generates Python file for a problem.',
    'skip': 'Generates Python file for the next problem.',
    'preview': 'Prints the text of a problem.',
    'verify': 'Verifies the solution to a problem.',
}


@click.command(name='EulerPy')
@click.argument('problem', default=0, type=click.IntRange(0, TOTAL_PROBLEMS))
@click.option('--cheat',    '-c', 'option', flag_value='cheat', help=help['cheat'])
@click.option('--generate', '-g', 'option', flag_value='generate', help=help['generate'])
@click.option('--skip',     '-s', 'option', flag_value='skip', help=help['skip'])
@click.option('--preview',  '-p', 'option', flag_value='preview', help=help['preview'])
@click.option('--verify',   '-v', 'option', flag_value='verify', help=help['verify'])
def main(option, problem):
    """Python tool to streamline Project Euler."""

    # No option given
    if option is None:
        if problem == 0:
            problem = determine_largest_problem()
            # No Project Euler files in current directory
            if not problem:
                generate_first_problem()

            # If correct answer was given, generate next problem file
            if verify_answer(problem):
                generate_file(problem + 1)
        else:
            if os.path.isfile(get_filename(problem)):
                verify_answer(problem)
            else:
                generate_file(problem)

    else:
        # Handle options that ignore a problem argument
        if option == 'skip':
            problem = determine_largest_problem()
            click.echo("Current problem is problem #{0}.".format(problem))
            generate_file(problem + 1, default=False)

        # Handle other options
        else:
            if problem == 0:
                problem = determine_largest_problem()

            if not problem:
                if option == 'preview':
                    problem = 1
                else:
                    generate_first_problem()

            funcs = {
                'cheat': view_solution,
                'generate': generate_file,
                'preview': preview_problem,
                'verify': verify_answer,
            }

            # Execute function
            funcs[option](problem)

    sys.exit()
