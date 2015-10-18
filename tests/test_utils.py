# -*- coding: utf-8 -*-

import os
import json
import textwrap
import unittest

from EulerPy.problem import Problem
from EulerPy.utils import human_time


EULER_DIR = os.path.dirname(os.path.dirname(__file__))
EULER_DATA = os.path.join(EULER_DIR, 'EulerPy', 'data')

class EulerPyUtils(unittest.TestCase):
    def test_problem_format(self):
        """
        Ensure each parsed problem only contains one problem (that one problem
        does not "bleed" into the next one due to an issue with line breaks)
        """

        # Determine largest problem in problems.txt
        problems_file = os.path.join(EULER_DATA, 'problems.txt')
        with open(problems_file) as f:
            for line in f:
                if line.startswith('Problem '):
                    largest_problem = line.split(' ')[1]

        for problem in range(1, int(largest_problem) + 1):
            problemText = Problem(problem).text

            msg = "Error encountered when parsing problem {}.".format(problem)

            self.assertFalse('========='in problemText, msg=msg)
            self.assertFalse('\n\n\n' in problemText, msg=msg)

    def test_expected_problem(self):
        """Check that problem #1 returns the correct problem text"""
        problem_one = textwrap.dedent(
            """
            If we list all the natural numbers below 10 that are multiples of 3 or 5,
            we get 3, 5, 6 and 9. The sum of these multiples is 23.

            Find the sum of all the multiples of 3 or 5 below 1000.
            """
        )

        self.assertEqual(problem_one.strip(), Problem(1).text)

    def test_filename_format(self):
        """Check that filenames are being formatted correctly"""
        self.assertEqual(Problem(1).filename(), "001.py")
        self.assertEqual(Problem(10).filename(), "010.py")
        self.assertEqual(Problem(100).filename(), "100.py")

    def test_time_format(self):
        self.assertEqual(human_time(100000), '1d 3h 46m 40s')

    def test_problem_resources(self):
        """Ensure resources in `/data` match `resources.json`"""
        resources_path = os.path.join(EULER_DATA, 'resources')

        def _resource_check(filename, seen_files):
            path = os.path.join(resources_path, filename)

            # Check that resource exists in `/data`
            self.assertTrue(os.path.isfile(path),
                '%s does not exist.' % filename)

            # Add resource to set `seen_files`
            seen_files.add(filename)

        with open(os.path.join(EULER_DATA, 'resources.json')) as f:
            resource_dict = json.load(f)

        seen_files = set()

        for item in (v for k, v in resource_dict.items()):
            if isinstance(item, list):
                for subitem in item:
                    _resource_check(subitem, seen_files)
            else:
                _resource_check(item, seen_files)

        self.assertEqual(seen_files, set(os.listdir(resources_path)))
