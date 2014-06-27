#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import linecache

import click

# Number of problems present in problems.txt
TOTAL_PROBLEMS = 202


def get_filename(problem):
    """Returns filename in the form `001.py`"""
    return '{:03d}.py'.format(problem)


def get_solution(problem):
    """Returns the solution to a given problem"""
    solutionsFile = os.path.join(os.path.dirname(__file__), 'solutions.txt')
    line = linecache.getline(solutionsFile, problem)

    return line.split(".", 1)[1][1:-1] # strip space following "." and newline


def verify_answer(problem):
    filename = get_filename(problem)

    if not os.path.isfile(filename):
        click.secho('Error: "{}" not found.'.format(filename), fg='red')
        sys.exit(1)

    click.echo('Checking "{}" against solution: '.format(filename), nl=False)

    try:
        cmd = 'python {}'.format(filename)
        output = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        click.secho('Error calling "{}".'.format(filename), fg='red')
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

    isCorrect = output == get_solution(problem)
    click.secho(output, bold=True, fg=('green' if isCorrect else 'red'))

    return isCorrect


def get_problem(problem):
    problemsFile = os.path.join(os.path.dirname(__file__), 'problems.txt')
    problemLines = []

    with open(problemsFile, 'r') as file:
        isProblemText = False
        sequentialBreaks = 0

        for line in file:
            if line == 'Problem {}\n'.format(problem):
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
    click.confirm("Generate file for problem #{}?".format(problem), default=default, abort=True)
    problemText = get_problem(problem)

    filename = get_filename(problem)

    if os.path.isfile(filename):
        click.secho('"{}" already exists. Overwrite?'.format(filename), fg='red', nl=False)
        click.confirm('', abort=True)

    problemHeader = 'Project Euler Problem #{}\n'.format(problem)
    problemHeader += '=' * len(problemHeader) + '\n\n'

    with open(filename, 'w') as file:
        file.write('"""\n')
        file.write(problemHeader)
        file.write(problemText)
        file.write('"""\n\n\n')

    click.echo('Successfully created "{}".'.format(filename))


def generate_first_problem():
    click.echo("No Project Euler files found in the current directory.")
    generate_file(1)
    sys.exit()


def view_solution(problem):
    click.confirm("View solution to problem #{}?".format(problem), abort=True)
    click.echo("The solution to problem #{} is ".format(problem), nl=False)
    click.secho(get_solution(problem), bold=True, nl=False)
    click.echo(".")
    sys.exit()


def preview_problem(problem):
    click.secho("Project Euler Problem #{}".format(problem), bold=True)
    click.echo(get_problem(problem)[:-1]) # strip trailing newline


def determine_largest_problem():
    for problem in reversed(xrange(1, TOTAL_PROBLEMS + 1)):
        if os.path.isfile(get_filename(problem)):
            return problem
    else:
        return False


help = {
    'cheat': "View the solution to a problem.",
    'generate': "Generates Python file for a problem.",
    'skip': "Generates Python file for the next problem.",
    'preview': "Prints the text of a problem.",
    'verify': "Verify the solution to a problem.",
}

@click.command(name='EulerPy')
@click.argument('problem', default=0, type=click.IntRange(0, TOTAL_PROBLEMS))
@click.option('--cheat',    '-c', is_flag=True, help=help['cheat'])
@click.option('--generate', '-g', is_flag=True, help=help['generate'])
@click.option('--skip',     '-s', is_flag=True, help=help['skip'])
@click.option('--preview',  '-p', is_flag=True, help=help['preview'])
@click.option('--verify',   '-v', is_flag=True, help=help['verify'])
def main(cheat, generate, skip, preview, verify, problem):
    """Python tool to streamline Project Euler."""

    # Handle argument-less options
    if skip:
        problem = determine_largest_problem()
        click.echo("Current problem is problem #{}.".format(problem))
        generate_file(problem + 1, default=False)
        sys.exit()

    # Handle no arguments before determining problem number
    if not (cheat or generate or skip or preview or verify):
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
        # Clean problem number
        if problem == 0:
            problem = determine_largest_problem()

            if not problem:
                if preview:
                    problem = 1
                else:
                    generate_first_problem()

        # Handle options that can take a problem number as an argument
        if cheat:
            view_solution(problem)
        elif generate:
            generate_file(problem)
        elif preview:
            preview_problem(problem)
        elif verify:
            verify_answer(problem)
        else:
            sys.exit(1)

    sys.exit()
