# dupedetector [![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/uchicago-library/dupedetector/releases)

[![Build Status](https://travis-ci.org/uchicago-library/dupedetector.svg?branch=master)](https://travis-ci.org/uchicago-library/dupedetector) [![Coverage Status](https://coveralls.io/repos/github/uchicago-library/dupedetector/badge.svg?branch=master)](https://coveralls.io/github/uchicago-library/dupedetector?branch=master) [![Documentation Status](https://readthedocs.org/projects/dupedetector/badge/?version=latest)](http://dupedetector.readthedocs.io/en/latest/?badge=latest)

Detects duplicate files, hopefully quickly.

Are there cases where this is slower than just computing all the hashes? Yes

Are those cases common in most use cases? No

## Quickstart

```
$ git clone https://github.com/uchicago-library/dupedetector.git
$ cd dupedetector
$ python3 -m venv venv
$ source venv/bin/activate
$ python setup.py install
$ dupedetector --help
```

## CLI Syntax

```
$ dupedetector --help
usage: dupedetector [-h] [-c CHUNKSIZE] [-s SAMPLESIZE] [-o OUT]
                    paths [paths ...]

positional arguments:
  paths                 The paths to files or directories to scan for
                        duplicates. Directories will be scanned for files
                        recursively.

optional arguments:
  -h, --help            show this help message and exit
  -c CHUNKSIZE, --chunksize CHUNKSIZE
                        How many bytes to load into RAM for hashing at once.
                        Defaults to 1MB
  -s SAMPLESIZE, --samplesize SAMPLESIZE
                        How many bytes of the files to sample from the
                        beginning, middle, and end. Files less than twice as
                        big as this value will be considered 'small', and will
                        be hashed in their entirety. Defaults to 1MB
  -o OUT, --out OUT     A file path to write the result to, or '-' for stdout.
                        Defaults to stdout.
```

# Author
Brian Balsamo <brian@brianbalsamo.com>
