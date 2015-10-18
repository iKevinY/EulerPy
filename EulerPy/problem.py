# -*- coding: utf-8 -*-

import os
import re
import sys
import glob
import json
import linecache
import shutil

import click


# Filenames follow the format (prefix, number, suffix, extension)
BASE_NAME = '{}{:03d}{}{}'
FILE_RE = re.compile(r'(.*)(\d{3})(.*)(\.\w+)')

EULER_DATA = os.path.join(os.path.dirname(__file__), 'data')

class Problem(object):
    """Represents a Project Euler problem of a given problem number"""
    def __init__(self, problem_number):
        self.num = problem_number

    def filename(self, prefix='', suffix='', extension='.py'):
        """Returns filename padded with leading zeros"""
        return BASE_NAME.format(prefix, self.num, suffix, extension)

    @property
    def glob(self):
        """Returns a sorted glob of files belonging to a given problem"""
        file_glob = glob.glob(BASE_NAME.format('*', self.num, '*', '.*'))

        # Sort globbed files by tuple (filename, extension)
        return sorted(file_glob, key=lambda f: os.path.splitext(f))

    @property
    def file(self):
        """Returns a ProblemFile instance of the first matching file"""
        return ProblemFile(self.glob[0]) if self.glob else None

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
            msg = "Copied {} to {}.".format(copied, path)

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

            with open(problem_file) as f:
                is_problem = False
                last_line = ''

                for line in f:
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


class ProblemFile(object):
    """Represents a file that belongs to a given Project Euler problem"""
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return self.filename

    @property
    def _filename_parts(self):
        """Returns (prefix, number, suffix, extension)"""
        return FILE_RE.search(self.filename).groups()

    @property
    def prefix(self):
        return self._filename_parts[0]

    @property
    def str_num(self):
        return self._filename_parts[1]

    @property
    def suffix(self):
        return self._filename_parts[2]

    @property
    def extension(self):
        return self._filename_parts[3]

    @property
    def num(self):
        return int(self.str_num)

    def change_suffix(self, suffix):
        if suffix == self.suffix:
            return False

        new_name = self.prefix + self.str_num + suffix + self.extension
        os.rename(self.filename, new_name)

        msg = 'Renamed "{}" to "{}".'.format(self.filename, new_name)
        click.secho(msg, fg='yellow')
        self.filename = new_name

        return True
