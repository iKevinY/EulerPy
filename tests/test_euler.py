# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

from click.testing import CliRunner

from EulerPy import euler
from EulerPy.problem import Problem


def EulerRun(*commands, **kwargs):
    """Simplifies running tests using CliRunner()"""
    return CliRunner().invoke(euler.main, commands, **kwargs)


def generateFile(problem, filename=None, content=None, correct=False):
    """
    Uses Problem.solution to generate a problem file. The correct
    argument controls whether the generated file is correct or not.
    """
    p = Problem(problem)
    filename = filename or p.filename

    with open(filename, 'w') as file:
        if correct:
            file.write('print({0})'.format(p.solution))
        elif content:
            file.write(content)


class EulerPyTest(unittest.TestCase):
    def setUp(self):
        # Copy problem and solution files to temporary directory
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        eulerDir = os.path.dirname(os.path.dirname(__file__))
        dataDir = os.path.join(eulerDir, 'EulerPy', 'data')
        tempData = os.path.join(os.getcwd(), 'EulerPy', 'data')
        shutil.copytree(dataDir, tempData)

    def tearDown(self):
        # Delete the temporary directory
        shutil.rmtree(self.temp_dir)


class EulerPyNoOption(EulerPyTest):
    # Empty directory with no option
    def test_empty_directory_install_neutral(self):
        result = EulerRun(input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('euler001.py'))

    def test_empty_directory_negative(self):
        result = EulerRun(input='N\n')
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(os.path.isfile('euler001.py'))

    # No option or problem number
    def test_no_arguments_first_correct(self):
        generateFile(1, correct=True)
        result = EulerRun(input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('euler002.py'))

    def test_no_arguments_first_incorrect(self):
        generateFile(1)
        result = EulerRun(input='\n')
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(os.path.isfile('euler002.py'))

    # Ambiguous case; infer option from file existence check
    def test_ambiguous_option_generate(self):
        result = EulerRun('1')
        self.assertEqual(result.exit_code, 0)

    def test_ambiguous_option_verify(self):
        generateFile(1, correct=True)
        result = EulerRun('1')
        self.assertEqual(result.exit_code, 0)


class EulerPyCheat(EulerPyTest):
    def test_cheat_neutral(self):
        result = EulerRun('-c', input='\n')
        self.assertEqual(result.exit_code, 1)

    def test_cheat_long_flag(self):
        result = EulerRun('--cheat', input='\n')
        self.assertEqual(result.exit_code, 1)

    def test_cheat_positive(self):
        result = EulerRun('-c', input='Y\n')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('The answer to problem 1', result.output)

    def test_chest_specific(self):
        result = EulerRun('-c', '2', input='Y\n')
        self.assertIn('The answer to problem 2', result.output)

    def test_cheat_not_in_solutions(self):
        result = EulerRun('-c', '1000', input='Y\n')
        self.assertEqual(result.exit_code, 1)


class EulerPyGenerate(EulerPyTest):
    def test_generate_neutral(self):
        result = EulerRun('-g', input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('euler001.py'))

    def test_generate_negative(self):
        result = EulerRun('-g', input='N\n')
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(os.path.isfile('euler001.py'))

    def test_generate_specific(self):
        result = EulerRun('-g', '5', input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('euler005.py'))

    def test_generate_overwrite_positive(self):
        generateFile(1)

        result = EulerRun('-g', '1', input='\nY\n')
        self.assertEqual(result.exit_code, 0)

        with open('euler001.py') as file:
            self.assertNotEqual(file.read(), '')

    def test_generate_overwrite_neutral(self):
        generateFile(1)

        result = EulerRun('-g', '1', input='\n\n')
        self.assertEqual(result.exit_code, 1)

        with open('euler001.py') as file:
            self.assertEqual(file.read(), '')

    def test_generate_overwrite_skipped(self):
        generateFile(1, 'euler001-skipped.py')

        result = EulerRun('-g', '1', input='\nY\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('euler001-skipped.py'))
        self.assertFalse(os.path.isfile('euler001.py'))

    def test_generate_copy_resources(self):
        result = EulerRun('-g', '22', input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('euler022.py'))

        resource = os.path.join('resources', 'names.txt')
        self.assertTrue(os.path.isfile(resource))


class EulerPyPreview(EulerPyTest):
    def test_preview(self):
        result = EulerRun('-p')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Project Euler Problem 1', result.output)

    def test_preview_specific(self):
        result = EulerRun('-p', '5')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Project Euler Problem 5', result.output)

    def test_preview_next_behaviour(self):
        generateFile(1)

        result = EulerRun('-p')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Project Euler Problem 2', result.output)

    def test_preview_nonexistent(self):
        result = EulerRun('-p', '1000')
        self.assertEqual(result.exit_code, 1)


class EulerPySkip(EulerPyTest):
    def test_skip_neutral(self):
        generateFile(1)

        result = EulerRun('-s', input='\n')
        self.assertEqual(result.exit_code, 1)
        self.assertTrue(os.path.isfile('euler001.py'))

    def test_skip_positive(self):
        generateFile(1)

        result = EulerRun('-s', input='Y\n')
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(os.path.isfile('euler001.py'))
        self.assertTrue(os.path.isfile('euler001-skipped.py'))


class EulerPyVerify(EulerPyTest):
    def test_verify(self):
        generateFile(1)

        result = EulerRun('-v')
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Checking "euler001.py"', result.output)

    def test_verify_specific(self):
        generateFile(5)

        result = EulerRun('-v', '5')
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Checking "euler005.py"', result.output)

    def test_verify_glob(self):
        generateFile(1, 'euler001-skipped.py')

        result = EulerRun('-v', '1')
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Checking "euler001-skipped.py"', result.output)

    def test_verify_sorted_glob(self):
        generateFile(1, 'euler001.py')
        generateFile(1, 'euler001-skipped.py')

        result = EulerRun('-v', '1')
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Checking "euler001.py"', result.output)
        self.assertNotIn('Checking "euler001-skipped.py"', result.output)

    def test_verify_correct(self):
        generateFile(1, correct=True)

        result = EulerRun('-v')
        self.assertEqual(result.exit_code, 0)

    def test_verify_non_existent_problem_file(self):
        result = EulerRun('-v', '5')
        self.assertEqual(result.exit_code, 1)

    def test_verify_file_with_multiline_output(self):
        generateFile(1, content='print(1); print(2)')

        result = EulerRun('-v', '1')
        self.assertEqual(result.exit_code, 1)

    def test_verify_error_file(self):
        generateFile(1, content='import sys; sys.exit(1)')

        result = EulerRun('-v', '1')
        self.assertIn('Error calling "euler001.py"', result.output)
        self.assertEqual(result.exit_code, 1)


class EulerPyVerifyAll(EulerPyTest):
    def test_verify_all(self):
        generateFile(1, correct=True)
        generateFile(2, 'euler002-skipped.py', correct=True)
        generateFile(4)
        generateFile(5, content='import sys; sys.exit(1)')

        result = EulerRun('--verify-all')
        self.assertIn('Problems 001-020: C C . I E', result.output)

        # "euler002-skipped.py" should have been renamed to "euler002.py"
        self.assertTrue(os.path.isfile('euler002.py'))
        self.assertFalse(os.path.isfile('euler002-skipped.py'))

        # "euler004.py" should have been renamed to "euler004-skipped.py"
        self.assertFalse(os.path.isfile('euler004.py'))
        self.assertTrue(os.path.isfile('euler004-skipped.py'))

    def test_verify_all_no_files(self):
        result = EulerRun('--verify-all')
        self.assertEqual(result.exit_code, 1)


class EulerPyMisc(EulerPyTest):
    def test_help_option(self):
        result = EulerRun('--help')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('--cheat', result.output)
        self.assertIn('--generate', result.output)
        self.assertIn('--preview', result.output)
        self.assertIn('--skip', result.output)
        self.assertIn('--verify', result.output)
        self.assertIn('--verify-all', result.output)

    def test_version_option(self):
        result = EulerRun('--version')
        self.assertEqual(result.exit_code, 0)

