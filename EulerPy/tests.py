# -*- coding: utf-8 -*-

import unittest
import textwrap

import euler

class Tests(unittest.TestCase):
    def setUp(self):
        pass

    # Ensure each parsed problem only contains one problem (that one
    # problem does not "bleed" into another one)
    def test_problem_format(self):
        for problem in xrange(1, euler.TOTAL_PROBLEMS + 1):
            problemText = euler.get_problem(problem)

            msg = "Error encountered when parsing problem {}.".format(problem)

            self.assertNotIn('=========', problemText, msg=msg)
            self.assertNotIn('\n\n\n', problemText, msg=msg)

    # Check that problem #1 returns the correct problem text
    def test_expected_problem(self):
        problemOne = textwrap.dedent(
            """
            If we list all the natural numbers below 10 that are multiples of 3 or 5,
            we get 3, 5, 6 and 9. The sum of these multiples is 23.

            Find the sum of all the multiples of 3 or 5 below 1000.
            """
        )

        self.assertEqual(problemOne[1:], euler.get_problem(1))

    # Check that filenames are being formatted correctly
    def test_filename_format(self):
        self.assertEqual(euler.get_filename(1), "001.py")
        self.assertEqual(euler.get_filename(100), "100.py")

        with self.assertRaises(ValueError):
            euler.get_filename("string")


if __name__ == '__main__':
    unittest.main()
