# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import textwrap
import unittest

from click.testing import CliRunner

from EulerPy import euler
from EulerPy.problem import Problem

class Tests(unittest.TestCase):
    def setUp(self):
        os.chdir(tempfile.mkdtemp())

        # Copy problem and solution files to temporary directory
        eulerDir = os.path.dirname(os.path.realpath(__file__))
        tempEuler = os.path.join(os.getcwd(), 'EulerPy')
        shutil.copytree(eulerDir, tempEuler)


    def tearDown(self):
        shutil.rmtree(os.getcwd())


    def test_fresh_install(self):
        """Check that EulerPy executes properly from fresh install"""
        # Test "N" as file generation prompt input
        result = CliRunner().invoke(euler.main, input='N\n')
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(os.path.isfile('001.py'))

        # Test "Y" as file generation prompt input
        result = CliRunner().invoke(euler.main, input='Y\n')
        self.assertEqual(result.exit_code, None)
        self.assertTrue(os.path.isfile('001.py'))
        os.remove('001.py')

        # Test "\n" as file generation prompt input
        result = CliRunner().invoke(euler.main, input='\n')
        self.assertEqual(result.exit_code, None)
        self.assertTrue(os.path.isfile('001.py'))


    def test_cheat_option(self):
        result = CliRunner().invoke(euler.main, ['-c'], input='\n')
        self.assertEqual(result.exit_code, 1)

        result = CliRunner().invoke(euler.main, ['-c'], input='Y\n')
        self.assertEqual(result.exit_code, None)

        result = CliRunner().invoke(euler.main, ['--cheat'], input='Y\n')
        self.assertEqual(result.exit_code, None)

        result = CliRunner().invoke(euler.main, ['-c', '2'], input='Y\n')
        self.assertTrue('problem 2' in result.output)


    def test_generate_option(self):
        result = CliRunner().invoke(euler.main, ['-g'], input='\n')
        self.assertEqual(result.exit_code, None)
        self.assertTrue(os.path.isfile('001.py'))
        os.remove('001.py')

        result = CliRunner().invoke(euler.main, ['--generate'], input='\n')
        self.assertEqual(result.exit_code, None)
        self.assertTrue(os.path.isfile('001.py'))
        os.remove('001.py')

        result = CliRunner().invoke(euler.main, ['-g', '2'], input='\n')
        self.assertEqual(result.exit_code, None)
        self.assertTrue(os.path.isfile('002.py'))
        os.remove('002.py')


    def test_generate_overwrite(self):
        """Ensure that --generate will overwrite a file appropriately"""
        # Default behaviour should be to not overwrite the file
        open('001.py', 'a').close()
        result = CliRunner().invoke(euler.main, ['-g', '1'], input='\n\n')
        self.assertEqual(result.exit_code, 1)
        with open('001.py') as file:
            self.assertTrue(file.readlines() == [])

        # This should overwrite the file ("001.py" will not be empty anymore)
        open('001.py', 'a').close()
        result = CliRunner().invoke(euler.main, ['-g', '1'], input='\nY\n')
        self.assertEqual(result.exit_code, None)
        with open('001.py') as file:
            self.assertFalse(file.readlines() == [])


    def test_problem_format(self):
        """
        Ensure each parsed problem only contains one problem (that one problem
        does not "bleed" into the next one due to an issue with line breaks)
        """

        # Determine largest problem in problems.txt
        problemsFile = os.path.join(os.path.dirname(__file__), 'problems.txt')
        with open(problemsFile) as file:
            largest = ''
            for line in file:
                if line.startswith('Problem'):
                    largest = line.strip()

            largestProblem = int(largest.split(' ')[1])

        for problem in range(1, largestProblem + 1):
            problemText = Problem(problem).text

            msg = "Error encountered when parsing problem {0}.".format(problem)

            self.assertFalse('========='in problemText, msg=msg)
            self.assertFalse('\n\n\n' in problemText, msg=msg)


    def test_expected_problem(self):
        """Check that problem #1 returns the correct problem text"""
        problemOne = textwrap.dedent(
            """
            If we list all the natural numbers below 10 that are multiples of 3 or 5,
            we get 3, 5, 6 and 9. The sum of these multiples is 23.

            Find the sum of all the multiples of 3 or 5 below 1000.
            """
        )

        self.assertEqual(problemOne[1:], Problem(1).text)


    def test_filename_format(self):
        """Check that filenames are being formatted correctly"""
        self.assertEqual(Problem(1).filename, "001.py")
        self.assertEqual(Problem(10).filename, "010.py")
        self.assertEqual(Problem(100).filename, "100.py")


if __name__ == '__main__':
    unittest.main()
