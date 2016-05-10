=========
Changelog
=========

v1.3.0 (2016-05-09)
-------------------

- Added problems 301-330
- Added --version flag to CLI
- Added support for prefixed problem files
- Updated to Click 4.0


v1.2.3 (2014-09-02)
-------------------

- Added problems 267-300
- Fixed bug with regenerating skipped files
- Pruned files included in source distribution
- Changed --generate to check for existence of problem before displaying
  file generation prompt


v1.2.2 (2014-08-11)
-------------------

- Fixed bug with filename of resource for problem 59


v1.2.1 (2014-08-10)
-------------------

- Changed --generate to allow skipped problem files to be regenerated


v1.2.0 (2014-08-06)
-------------------

- Dropped official support for Python 2.6 and added Python 3.4
- Added problems 257-266
- Changed file generation to automatically copy relevant resources


v1.1.0 (2014-07-20)
-------------------

- Added --verify-all option
- Changed --preview to preview the problem after the current one
- Changed problem file search to be more flexible by using the glob module
- Skipping a problem appends a "skipped" suffix to the filename of the problem


v1.0.8 (2014-07-07)
-------------------

- Made solution verification exit with appropriate exit code based on success
- Changed solution verification to not execute script using shell
- Fixed width of divider line in generated problem docstring


v1.0.7 (2014-07-03)
-------------------

- Added CPU timings


v1.0.6 (2014-06-30)
-------------------

- Moved timing information to separate line from problem output


v1.0.5 (2014-06-30)
-------------------

- Changed multi-line outputs to print first line of output on a new line
- Fixed solution checking on Windows


v1.0.4 (2014-06-29)
-------------------

- Added problems 203-256


v1.0.3 (2014-06-28)
-------------------

- Added timing information
- Added more solutions


v1.0.2 (2014-06-27)
-------------------

- Added Python 2.6 - 3 compatibility


v1.0.1 (2014-06-27)
-------------------

- Fixed bug with dependencies during installation


v1.0.0 (2014-06-27)
-------------------

- Initial release.
