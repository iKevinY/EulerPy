# -*- coding: utf-8 -*-

import os
import unittest
import textwrap

from click.testing import CliRunner

from EulerPy import euler

class Tests(unittest.TestCase):
    def setUp(self):
        pass


    def test_program_flow(self):
        """Check that EulerPy is executing properly"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Test "N" as file generation prompt input
            result = runner.invoke(euler.main, input='N\n')
            self.assertEqual(result.exit_code, 1)
            self.assertFalse(os.path.isfile('001.py'))

            # Test "Y" as file generation prompt input
            result = runner.invoke(euler.main, input='\n')
            self.assertEqual(result.exit_code, None)
            self.assertTrue(os.path.isfile('001.py'))

            # 001.py has been generated, so attempt to verify solution
            result = runner.invoke(euler.main)
            self.assertEqual(result.exit_code, 1)


    def test_problem_format(self):
        """
        Ensure each parsed problem only contains one problem (that one problem
        does not "bleed" into the next one due to an issue with line breaks)
        """
        for problem in range(1, euler.TOTAL_PROBLEMS + 1):
            problemText = euler.get_problem(problem)

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

        self.assertEqual(problemOne[1:], euler.get_problem(1))


    def test_filename_format(self):
        """Check that filenames are being formatted correctly"""
        self.assertEqual(euler.get_filename(1), "001.py")
        self.assertEqual(euler.get_filename(10), "010.py")
        self.assertEqual(euler.get_filename(100), "100.py")

        self.assertRaises(ValueError, euler.get_filename, "foo")


if __name__ == '__main__':
    unittest.main()
