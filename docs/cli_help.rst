CLI Syntax
==========

.. code-block:: bash

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
