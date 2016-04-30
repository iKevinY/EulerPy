**********************************
EulerPy |Travis| |PyPI| |Homebrew|
**********************************

EulerPy is a command line tool designed to streamline the process of solving
Project Euler problems using Python. The package focuses on two main tasks:
firstly, to create Python "template" files with a docstring containing the
text of a Project Euler problem for ease-of-reference, and secondly, to check
whether a problem has been solved correctly.


============
Installation
============

EulerPy can be installed (and updated) from PyPI using `pip`_:

.. code-block:: bash

    $ pip install --upgrade EulerPy


Conversely, it can be uninstalled using `pip`_ as well.

.. code-block:: bash

    $ pip uninstall EulerPy


Alternatively, OS X users can install EulerPy using `Homebrew`_:

.. code-block:: bash

    $ brew install euler-py


=====
Usage
=====

First, you'll want to ``cd`` to the directory where your Project Euler files
are being stored.

.. code-block:: bash

    $ mkdir ~/project-euler
    $ cd ~/project-euler


At this point, you'll probably want to run the ``euler`` command, which will
prompt to create ``001.py``, a file containing the text to Project Euler problem
#1 as its docstring.

.. code-block:: bash

    $ euler
    No Project Euler files found in the current directory.
    Generate file for problem 1? [Y/n]: Y
    Successfully created "001.py".

    $ cat 001.py
    """
    Project Euler Problem 1
    =======================

    If we list all the natural numbers below 10 that are multiples of 3 or 5,
    we get 3, 5, 6 and 9. The sum of these multiples is 23.

    Find the sum of all the multiples of 3 or 5 below 1000.
    """

At this point, you can open up your editor of choice and code up a solution
to the problem, making sure to ``print()`` the output. Once you feel that
you've solved the problem, run the ``euler`` command again to verify your
solution is correct. If the answer is correct, the solution will be printed
in green and the script will ask to generate the next problem file. If
incorrect, the solution will be printed in red instead. Additionally, the
time elapsed during the solution-checking process will also be printed.

.. code-block:: bash

    $ euler
    Checking "001.py" against solution: [no output] # (output in red)

    $ echo print 42 >> 001.py
    $ euler
    Checking "001.py" against solution: 42 # (output in green)
    Generate file for problem 2? [Y/n]: Y
    Successfully created "002.py".


EulerPy also has a few command line options that act as different commands
(use ``euler --help`` to see a summary of all the options).


``--cheat / -c``
----------------

The ``--cheat`` option will print the answer to a problem after prompting
the user to ensure that they want to see it. If no problem argument is given,
it will print the answer to the problem that they are currently working on.

.. code-block:: bash

    $ euler --cheat
    View answer to problem 2? [y/N]: Y
    The answer to problem 2 is <redacted>.

    $ euler --cheat 100
    View answer to problem 100? [y/N]: Y
    The answer to problem 100 is <redacted>.


``--generate / -g``
-------------------

The ``--generate`` option will create a Python file for the given problem
number. If no problem number is given, it will overwrite the most recent
problem with a file containing only the problem docstring (after prompting
the user).

.. code-block:: bash

    $ euler --generate
    Generate file for problem 2? [Y/n]: Y
    "002.py" already exists. Overwrite? [y/N]:
    Successfully created "002.py".

    $ euler --generate 5
    Generate file for problem 5? [Y/n]: n
    Aborted!

``euler <problem>`` is equivalent to ``euler --generate <problem>`` if the file
**does not** exist.

.. code-block:: bash

    $ cat 005.py
    cat: 005.py: No such file or directory

    $ euler 5
    Generate file for problem 5? [Y/n]: n
    Aborted!

The file generation process will also automatically copy any relevant
resource files to a ``resources`` subdirectory.

.. code-block:: bash

    $ euler 22
    Generate file for problem 22? [Y/n]: Y
    Successfully created "022.py".
    Copied "names.txt" to project-euler/resources.


``--preview / -p``
------------------

The ``--preview`` option will print the text of a given problem to the terminal;
if no problem number is given, it will print the next problem instead.

.. code-block:: bash

    $ euler --preview
    Project Euler Problem 3
    The prime factors of 13195 are 5, 7, 13 and 29.

    What is the largest prime factor of the number 600851475143?

    $ euler --preview 5
    Project Euler Problem 5
    2520 is the smallest number that can be divided by each of the numbers
    from 1 to 10 without any remainder.

    What is the smallest number that is evenly divisible by all of the numbers
    from 1 to 20?


``--skip / -s``
---------------

The ``--skip`` option will prompt the user to "skip" to the next problem. As
of EulerPy v1.1, it will also append a "skipped" suffix to the skipped problem
file.

.. code-block:: bash

    $ euler --skip
    Current problem is problem 2.
    Generate file for problem 3? [y/N]: Y
    Successfully created "003.py".
    Renamed "002.py" to "002-skipped.py".


``--verify / -v``
-----------------

The ``--verify`` option will check whether a given problem file outputs the
correct solution to the problem. If no problem number is given, it will
check the current problem.

.. code-block:: bash

    $ euler --verify
    Checking "003.py" against solution: [no output] # (output in red)

    $ euler --verify 1
    Checking "001.py" against solution: <redacted> # (output in green)

As of EulerPy v1.1, verifying a skipped problem file will remove the "skipped"
suffix from its filename.

.. code-block:: bash

    $ euler --verify 2
    Checking "002-skipped.py" against solution: <redacted>
    Renamed "002-skipped.py" to "002.py".

``euler <problem>`` is equivalent to ``euler --verify <problem>`` if the file
**does** exist.

.. code-block:: bash

    $ cat 001.py
    """
    Project Euler Problem 1
    =======================

    If we list all the natural numbers below 10 that are multiples of 3 or 5,
    we get 3, 5, 6 and 9. The sum of these multiples is 23.

    Find the sum of all the multiples of 3 or 5 below 1000.
    """


    $ euler 1
    Checking "001.py" against solution: <redacted>


``--verify-all``
----------------

The ``--verify-all`` option was added in EulerPy v1.1. It essentially runs
``--verify`` on all the problem files it can find in the current directory,
but also prints an overview of all of the problems in the directory. Note
that if the verification encounters a ``KeyboardInterrupt`` exception, it will
skip the verification of that specific file. This allows for the ability to
skip verifying some files but not others, in the case that some solutions are
taking too long to compute.

.. code-block:: bash

    $ euler --verify-all
    Checking "001.py" against solution: <redacted>

    Checking "002.py" against solution: ^C

    Checking "003.py" against solution: [no output]

    ---------------------------------------------------------------
    C = correct, I = incorrect, E = error, S = skipped, . = missing

    Problems 001-020: C S I . .   . . . . .   . . . . .   . . . . .

This option should be run after upgrading to v1.1 from EulerPy v1.0, as it will
automatically rename any problems that have been skipped using ``--skip``,
making them easy to distinguish from those that have been correctly solved.


File Prefixes
-------------

As of v1.3.0, EulerPy will attempt to keep the prefix of problem files
consistent. The motivation behind this is that ``import 001`` results in a
syntax error whereas ``import euler001`` is valid. By using the latter
naming scheme, it is possible to reuse code written in previous files.

.. code-block:: bash

    $ mv 003.py euler003.py

    $ euler --skip
    Current problem is problem 3.
    Generate file for problem 4? [y/N]: Y
    Successfully created "euler004.py".
    Renamed "euler003.py" to "euler003-skipped.py".


============
Contributing
============

See `CONTRIBUTING.rst`_.


=============
Miscellaneous
=============

The text for the problems in `problems.txt`_ were derived from Kyle Keen's
`Local Euler`_ project, and the solutions in `solutions.txt`_ were derived
from the `projecteuler-solutions wiki`_.

See `this blog post`_ for insight into the development process.

EulerPy uses `Click`_ as a dependency for its CLI functionality.


=======
License
=======

EulerPy is licensed under the `MIT License`_.


.. |Travis| image:: https://img.shields.io/travis/iKevinY/EulerPy/master.svg
            :alt: Build Status
            :target: http://travis-ci.org/iKevinY/EulerPy

.. |PyPI| image:: https://img.shields.io/pypi/v/EulerPy.svg
          :alt: PyPI Version
          :target: https://pypi.python.org/pypi/EulerPy/
          
.. |Homebrew| image:: https://img.shields.io/homebrew/v/euler-py.svg
              :alt: Homebrew Version
              :target: https://github.com/Homebrew/homebrew-core/blob/master/Formula/euler-py.rb

.. _pip: http://www.pip-installer.org/en/latest/index.html
.. _Homebrew: http://brew.sh
.. _CONTRIBUTING.rst: https://github.com/iKevinY/EulerPy/blob/master/CONTRIBUTING.rst
.. _Local Euler: http://kmkeen.com/local-euler/
.. _problems.txt: https://github.com/iKevinY/EulerPy/blob/master/EulerPy/data/problems.txt
.. _solutions.txt: https://github.com/iKevinY/EulerPy/blob/master/EulerPy/data/solutions.txt
.. _projecteuler-solutions wiki: https://code.google.com/p/projecteuler-solutions/
.. _this blog post: http://kevinyap.ca/2014/06/eulerpy-streamlining-project-euler/
.. _click: https://github.com/mitsuhiko/click
.. _MIT License: https://github.com/iKevinY/EulerPy/blob/master/LICENSE
