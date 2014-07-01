# -*- coding: utf-8 -*-

import unittest
import textwrap

from EulerPy import euler

class Tests(unittest.TestCase):
    def setUp(self):
        pass


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

        self.assertRaises(ValueError, euler.get_filename, "string")


if __name__ == '__main__':
    unittest.main()
