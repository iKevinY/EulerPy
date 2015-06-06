# -*- coding: utf-8 -*-

import os
import re
import sys
import glob
import json
import linecache
import shutil

import click

BASE_NAME = 'euler{0:03d}{1}{2}'  # problem number | suffix | extension
BASE_GLOB = 'euler[0-9][0-9][0-9]{0}{1}'
BASE_RE = 'euler([0-9]{3})(.*)(\..*)'
EULER_DATA = os.path.join(os.path.dirname(__file__), 'data')

class Problem(object):
    def __init__(self, problem_number):
        self.num = problem_number

    @staticmethod
    def from_filename(filename):
        number = Problem.number_from_filename(filename)
        return Problem(number)

    @property
    def filename(self):
        """Returns filename padded with leading zeros"""
        return BASE_NAME.format(self.num, '', '.py')

    @staticmethod
    def number_from_filename(filename):
        """Extract the problem number from a filename."""
        return int(re.match(BASE_RE, filename).groups()[0])

    def suf_name(self, suffix, extension='.py'):
        """Similar to filename property but takes a suffix argument"""
        suffix = '-%s' % suffix
        return BASE_NAME.format(self.num, suffix, extension)

    @property
    def glob(self):
        """Returns a sorted glob of files belonging to a given problem"""
        file_glob = glob.glob(BASE_NAME.format(self.num, '*', '.*'))

        # Sort globbed files by tuple (filename, extension)
        return sorted(file_glob, key=lambda f: os.path.splitext(f))

    @property
    def resources(self):
        """Returns a list of resources related to the problem (or None)"""
        with open(os.path.join(EULER_DATA, 'resources.json')) as data_file:
            data = json.load(data_file)

        problem_num = str(self.num)

        if problem_num in data:
            files = data[problem_num]

            # Ensure a list of files is returned
            return files if isinstance(files, list) else [files]
        else:
            return None

    def copy_resources(self):
        """Copies the relevant resources to a resources subdirectory"""
        if not os.path.isdir('resources'):
            os.mkdir('resources')

        resource_dir = os.path.join(os.getcwd(), 'resources', '')
        copied_resources = []

        for resource in self.resources:
            src = os.path.join(EULER_DATA, 'resources', resource)
            if os.path.isfile(src):
                shutil.copy(src, resource_dir)
                copied_resources.append(resource)

        if copied_resources:
            copied = ', '.join(copied_resources)
            path = os.path.relpath(resource_dir, os.pardir)
            msg = "Copied {0} to {1}.".format(copied, path)

            click.secho(msg, fg='green')

    @property
    def solution(self):
        """Returns the answer to a given problem"""
        num = self.num

        solution_file = os.path.join(EULER_DATA, 'solutions.txt')
        solution_line = linecache.getline(solution_file, num)

        try:
            answer = solution_line.split('. ')[1].strip()
        except IndexError:
            answer = None

        if answer:
            return answer
        else:
            msg = 'Answer for problem %i not found in solutions.txt.' % num
            click.secho(msg, fg='red')
            click.echo('If you have an answer, consider submitting a pull '
                       'request to EulerPy on GitHub.')
            sys.exit(1)

    @property
    def text(self):
        """Parses problems.txt and returns problem text"""
        def _problem_iter(problem_num):
            problem_file = os.path.join(EULER_DATA, 'problems.txt')

            with open(problem_file) as file:
                is_problem = False
                last_line = ''

                for line in file:
                    if line.strip() == 'Problem %i' % problem_num:
                        is_problem = True

                    if is_problem:
                        if line == last_line == '\n':
                            break
                        else:
                            yield line[:-1]
                            last_line = line

        problem_lines = [line for line in _problem_iter(self.num)]

        if problem_lines:
            # First three lines are the problem number, the divider line,
            # and a newline, so don't include them in the returned string.
            # Also, strip the final newline.
            return '\n'.join(problem_lines[3:-1])
        else:
            msg = 'Problem %i not found in problems.txt.' % self.num
            click.secho(msg, fg='red')
            click.echo('If this problem exists on Project Euler, consider '
                       'submitting a pull request to EulerPy on GitHub.')
            sys.exit(1)
