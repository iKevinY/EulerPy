============
Contributing
============

The `problems.txt`_ file consists of text versions of the problems found on
the Project Euler website. Since some of the problems contain content that
is difficult to represent in a plain text format (images, LaTeX-formatted
mathematical equations, etc.), it's probably better to make sure each problem
has been seen at least one time by a biological set of eyes. Here are the
guidelines for the format of the file:

* Each problem begins with a line in the format ``Problem n``, where ``n`` is
  the number of the problem, followed directly by a divider line composed of
  ``=`` characters of equal width to the preceeding line.
* Leave **one** empty line after the divider line.
* Keep the width of each line to **74 characters** maximum.
* Align centered text with the 74 character width in mind.
* If the problem links to a file or page on the Project Euler website, put the
  link to the resource in brackets directly following its name
  (``words.txt [http://projecteuler.net/project/words.txt]``)
* If the problem contains an image, use the format ``[Image: <image link>]``.
* Leave **two** empty lines after the final line of the problem text.
* In addition, the problem text itself should never contain two consecutive
  empty lines, as this indicates to the script that the the problem has
  finished being read.


Also, remember to update the problem count (the ``TOTAL_PROBLEMS`` variable) in
`euler.py`_ with the number of problems that have been added.

I've probably made countless coding *faux pas* given my level of experience, so
any improvements to the codebase are graciously welcomed as well.

.. _problems.txt: https://github.com/iKevinY/EulerPy/blob/master/EulerPy/problems.txt
.. _euler.py: https://github.com/iKevinY/EulerPy/blob/master/EulerPy/euler.py