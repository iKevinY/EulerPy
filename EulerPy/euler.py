# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import linecache

import click
from EulerPy.timing import clock, format_time

# Number of problems present in problems.txt
TOTAL_PROBLEMS = 256


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
        start = clock()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, _ = proc.communicate()
        end = clock()
        time_info = format_time(start, end)

        # Python 3 returns bytes; use a valid encoding like ASCII as the output
        # will fall in that range
        if isinstance(output, bytes):
            output = output.decode('ascii')

        return_val = proc.poll()

        if return_val:
            click.secho('Error calling "{0}".'.format(filename), fg='red')
            click.secho(time_info, fg='cyan')
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

        # If there is still a newline, the output is multi-lined. Print the
        # first line of the output on a separate line from the "checking
        # against solution" message. Additionally, a multi-line output is
        # not going to be correct, so skip the solution check.
        if '\n' in output:
            is_correct = False
            click.secho('\n' + output, bold=True, fg='red')
        else:
            is_correct = output.strip() == solution
            fg_colour = 'green' if is_correct else 'red'
            click.secho(output, bold=True, fg=fg_colour)

        click.secho(time_info, fg='cyan')
        return is_correct


def get_problem(problem):
    problemsFile = os.path.join(os.path.dirname(__file__), 'problems.txt')
    problemLines = []

    with open(problemsFile, 'r') as file:
        isProblemText = False
        sequentialBreaks = 0

        for line in file:
            if line.strip() == 'Problem {0}'.format(problem):
                isProblemText = True

            if isProblemText:
                if line == '\n':
                    sequentialBreaks += 1
                else:
                    sequentialBreaks = 0

                # Two subsequent empty lines indicates that the current
                # problem text has ended, so stop iterating over file
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

@click.command(name='euler', options_metavar='[OPTION]')
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
