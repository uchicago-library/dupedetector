"""
dupedetector: Detects duplicate files, hopefully quickly
"""

__author__ = "Brian Balsamo"
__email__ = "brian@brianbalsamo.com"
__version__ = "0.0.1"


import os
import json
import functools
import argparse
from sys import stdout
from hashlib import md5 as _md5


def get_parser():
    """
    Generates the CLI Parser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--chunksize", type=int, default=1000000,
        help="How many bytes to load into RAM for hashing at once. Defaults to 1MB"
    )
    parser.add_argument(
        "-s", "--samplesize", type=int, default=1000000,
        help="How many bytes of the files to sample from the begginning, middle, and end. " +
        "Files less than twice as big as this value will be considered 'small', and " +
        "will be hashed in their entirety. Defaults to 1MB"
    )
    parser.add_argument(
        "-o", "--out", type=str, default="-",
        help="A file path to write the result to, or '-' for stdout. Defaults to stdout."
    )
    parser.add_argument(
        "paths", type=str, nargs="+",
        help="The paths to files or directories to scan for duplicates. Directories " +
        "will be scanned for files recursively."
    )
    return parser


def md5(fp, offset=0, samplesize=None, chunksize=2**8):
    """
    Specialized md5 function. Just returns a hexdigest.

    Reads $chunksize bytes from the file at $fp at a time.

    If $samplesize is not None, only read that many bytes then stop, even if we haven't
    hit the end of the file.
    """
    if samplesize is not None:
        if chunksize > samplesize:
            chunksize = samplesize
    h = _md5()
    with open(fp, 'rb') as f:
        if offset:
            f.seek(offset)
        chunk = f.read(chunksize)
        bytes_read = len(chunk)
        while chunk:
            h.update(chunk)
            if samplesize is not None:
                if bytes_read == samplesize:
                    break
                elif bytes_read + chunksize > samplesize:
                    chunksize = samplesize-bytes_read
                else:
                    # Leaving this here in case I need it for debugging
                    # again later.
                    pass
            chunk = f.read(chunksize)
            bytes_read = bytes_read + chunksize
    return h.hexdigest()


def filter_lol(lol, cb):
    """
    Filters a list of lists (lol) by applying a callback
    to each element of the inner lists to generate a key.

    That key is then used to assign each candidate to a filtered list
    of lists, and only lists which contain > 1 entry are returned.
    """
    candidates = []
    for x in lol:
        buckets = {}
        for y in x:
            k = cb(y)
            if buckets.get(k) is None:
                buckets[k] = []
            buckets[k].append(y)
        for z in buckets:
            if len(buckets[z]) > 1:
                candidates.append(buckets[z])
    return candidates


def rscan(path):
    """
    Given a path, return all files from there down. Inclusive.
    """
    # https://ilovesymposia.com/2015/10/19/first-yield-from/
    # slight alteration
    if os.path.isfile(path):
        return path
    elif os.path.isdir(path):
        for p in os.listdir(path):
            p = os.path.join(path, p)
            if os.path.isfile(p):
                yield p
            if os.path.isdir(p):
                for q in rscan(p):
                    yield q
    else:
        return


def hash_first_sample(fp, samplesize=1000000, chunksize=2**8):
    """
    Hash $samplesize bytes from the start of a file
    """
    return md5(fp, offset=0, samplesize=samplesize, chunksize=chunksize)


def hash_middle_sample(fp, samplesize=1000000, chunksize=2**8):
    """
    Hash $samplesize bytes from around a files middle
    """
    size = os.path.getsize(fp)
    # Paranoid middle finder
    middle_offset = max(int((size/2)-(samplesize/2)), 0)
    return md5(fp, offset=middle_offset, samplesize=samplesize, chunksize=chunksize)


def hash_end_sample(fp, samplesize=1000000, chunksize=2**8):
    """
    Hash the last $samplesize bytes of a file
    """
    size = os.path.getsize(fp)
    end_offset = max(size-samplesize, 0)
    return md5(fp, offset=end_offset, samplesize=samplesize, chunksize=chunksize)


def main(args):
    """
    Do the stuff
    """
    file_list = []
    for x in args.paths:
        for y in rscan(x):
            file_list.append(y)

    # Compute sizes, our first set of bucket keys
    sizes = {}
    for x in file_list:
        size = os.path.getsize(x)
        if sizes.get(size) is None:
            sizes[size] = []
        sizes[size].append(x)

    # Filter out stuff smaller than twice our blocksize
    # We're just going to hash this stuff wholesale
    small_files = {}
    filtered_sizes = {}
    for x in sizes:
        if x < 2*args.chunksize:
            small_files[x] = sizes[x]
        else:
            filtered_sizes[x] = sizes[x]

    # Generate our first subset of files that may be dupes to be
    # incrementally analyzed as a list of lists
    candidates_by_size = []
    for x in filtered_sizes:
        if len(filtered_sizes[x]) > 1:
            candidates_by_size.append(filtered_sizes[x])

    # Ween the previous list of lists down by stuff that starts the same
    candidates_by_first_sample = filter_lol(
        candidates_by_size,
        functools.partial(hash_first_sample, samplesize=args.samplesize, chunksize=args.chunksize)
    )

    # ... and stuff which has has the same content in the middle
    candidates_by_middle_sample = filter_lol(
        candidates_by_first_sample,
        functools.partial(hash_middle_sample, samplesize=args.samplesize, chunksize=args.chunksize)
    )

    # ... and stuff which has the same content at the end
    candidates_by_end_sample = filter_lol(
        candidates_by_middle_sample,
        functools.partial(hash_end_sample, samplesize=args.samplesize, chunksize=args.chunksize)
    )

    # Add the small files back in - this is stuff we have to hash
    # to be sure about - either because it is too small to bother
    # subdividing, or because it has the same content all three offsets
    for x in small_files:
        candidates_by_end_sample.append(small_files[x])

    # And finally, compute whole hashes of the files for stuff we have left
    candidates_by_hash = filter_lol(
        candidates_by_end_sample,
        functools.partial(md5, chunksize=args.chunksize)
    )

    # Output the results
    if args.out == "-":
        target = stdout
    else:
        target = open(args.out, 'w')
    json.dump(candidates_by_hash, target, indent=2)
    target.close()


def cli():
    """
    Hook for setuptools entrypoint. Parses the args and feeds them to main.
    """
    parser = get_parser()
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli()
