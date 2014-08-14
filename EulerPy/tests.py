# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import textwrap
import unittest

from click.testing import CliRunner

from EulerPy import euler
from EulerPy.problem import Problem


def CliRun(*commands, **kwargs):
    """Simplifies running tests using CliRunner()"""
    return CliRunner().invoke(euler.main, commands, **kwargs)

def generateFile(problem, filename=None, correct=False):
    """
    Uses Problem().solution to generate a problem file. The correct
    argument controls whether the generated file is correct or not.
    """
    p = Problem(problem)
    filename = filename or p.filename

    with open(filename, 'a') as file:
        if correct:
            file.write('print({0})\n'.format(p.solution))


class EulerTests(unittest.TestCase):
    def setUp(self):
        # Copy problem and solution files to temporary directory
        os.chdir(tempfile.mkdtemp())
        dataDir = os.path.join(os.path.dirname(__file__), 'data')
        tempData = os.path.join(os.getcwd(), 'EulerPy', 'data')
        shutil.copytree(dataDir, tempData)

    def tearDown(self):
        # Delete the temporary directory
        shutil.rmtree(os.getcwd())


    # Empty directory with no option
    def test_empty_directory_install_neutral(self):
        result = CliRun(input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('001.py'))

    def test_empty_directory_negative(self):
        result = CliRun(input='N\n')
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(os.path.isfile('001.py'))


    # --cheat / -c
    def test_cheat_neutral(self):
        result = CliRun('-c', input='\n')
        self.assertEqual(result.exit_code, 1)

    def test_cheat_long_flag(self):
        result = CliRun('--cheat', input='\n')
        self.assertEqual(result.exit_code, 1)

    def test_cheat_positive(self):
        result = CliRun('-c', input='Y\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('The answer to problem 1' in result.output)

    def test_chest_specific(self):
        result = CliRun('-c', '2', input='Y\n')
        self.assertTrue('The answer to problem 2' in result.output)


    # --generate / -g
    def test_generate_neutral(self):
        result = CliRun('-g', input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('001.py'))

    def test_generate_negative(self):
        result = CliRun('-g', input='N\n')
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(os.path.isfile('001.py'))

    def test_generate_specific(self):
        result = CliRun('-g', '5', input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('005.py'))

    def test_generate_overwrite_positive(self):
        generateFile(1)

        result = CliRun('-g', '1', input='\nY\n')
        self.assertEqual(result.exit_code, 0)

        with open('001.py') as file:
            self.assertFalse(file.readlines() == [])

    def test_generate_overwrite_neutral(self):
        generateFile(1)

        result = CliRun('-g', '1', input='\n\n')
        self.assertEqual(result.exit_code, 1)

        with open('001.py') as file:
            self.assertTrue(file.readlines() == [])

    def test_generate_overwrite_skipped(self):
        generateFile(1, '001-skipped.py')

        result = CliRun('-g', '1', input='\nY\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('001-skipped.py'))
        self.assertFalse(os.path.isfile('001.py'))


    # --preview / -p
    def test_preview(self):
        result = CliRun('-p')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Project Euler Problem 1' in result.output)

    def test_preview_specific(self):
        result = CliRun('-p', '5')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Project Euler Problem 5' in result.output)

    def test_preview_next_behaviour(self):
        generateFile(1)

        result = CliRun('-p')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Project Euler Problem 2' in result.output)


    # --skip / -s
    def test_skip_neutral(self):
        generateFile(1)

        result = CliRun('-s', input='\n')
        self.assertEqual(result.exit_code, 1)
        self.assertTrue(os.path.isfile('001.py'))

    def test_skip_positive(self):
        generateFile(1)

        result = CliRun('-s', input='Y\n')
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(os.path.isfile('001.py'))
        self.assertTrue(os.path.isfile('001-skipped.py'))


    # --verify / -v
    def test_verify(self):
        generateFile(1)

        result = CliRun('-v')
        self.assertEqual(result.exit_code, 1)
        self.assertTrue('Checking "001.py"' in result.output)

    def test_verify_specific(self):
        generateFile(5)

        result = CliRun('-v', '5')
        self.assertEqual(result.exit_code, 1)
        self.assertTrue('Checking "005.py"' in result.output)

    def test_verify_glob(self):
        generateFile(1, '001-skipped.py')

        result = CliRun('-v', '1')
        self.assertEqual(result.exit_code, 1)
        self.assertTrue('Checking "001-skipped.py"' in result.output)

    def test_verify_correct(self):
        generateFile(1, correct=True)

        result = CliRun('-v')
        self.assertEqual(result.exit_code, 0)


    # --verify-all
    def test_verify_all(self):
        generateFile(1, correct=True)
        generateFile(2, filename='002-skipped.py', correct=True)
        generateFile(4)
        generateFile(5, correct=True)

        result = CliRun('--verify-all')
        self.assertTrue('Problems 001-020: C C . I C' in result.output)

        # "002-skipped.py" should have been renamed to "002.py"
        self.assertTrue(os.path.isfile('002.py'))
        self.assertFalse(os.path.isfile('002-skipped.py'))

        # "004.py" should have been renamed to "004-skipped.py"
        self.assertFalse(os.path.isfile('004.py'))
        self.assertTrue(os.path.isfile('004-skipped.py'))


    # --help
    def test_help_option(self):
        result = CliRun('--help')
        self.assertEqual(result.exit_code, 0)


    def test_problem_format(self):
        """
        Ensure each parsed problem only contains one problem (that one problem
        does not "bleed" into the next one due to an issue with line breaks)
        """

        # Determine largest problem in problems.txt
        problemsFile = os.path.join(os.path.dirname(__file__),
                                    'data', 'problems.txt')
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
