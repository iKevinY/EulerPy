import sys
import EulerPy

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    with open('README.rst') as f:
        return f.read()

def requirements():
    install_requires = []
    with open('requirements.txt') as f:
        for line in f:
            install_requires.append(line.strip())

    # Terminal colors for Windows
    if 'win32' in str(sys.platform).lower():
        install_requires.append('colorama>=0.2.4')

    return install_requires

setup(
    name='EulerPy',
    version=EulerPy.__version__,
    description=EulerPy.__doc__.strip(),
    long_description=readme(),
    url='https://github.com/iKevinY/EulerPy',
    author=EulerPy.__author__,
    author_email='me@kevinyap.ca',
    license=EulerPy.__license__,
    packages=['EulerPy'],
    entry_points={'console_scripts': ['euler = EulerPy.__main__:main']},
    install_requires=requirements(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],
    keywords=['EulerPy', 'euler', 'project-euler', 'projecteuler'],
    include_package_data=True,
    zip_safe=False,
)
