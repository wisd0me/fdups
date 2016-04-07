#!env python3

import sys
import argparse
import itertools
import re

SUFFIXES = {1000: ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            1024: ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']}

def approximate_size(size, a_kilobyte_is_1024_bytes=True):
    '''
    Convert a file size to human-readable form.

    Keyword arguments:
    size -- file size in bytes
    a_kilobyte_is_1024_bytes -- if True (default), use multiples of 1024
                                if False, use multiples of 1000

    Returns: string

    '''
    if size < 0:
        raise ValueError('number must be non-negative')

    multiple = 1024 if a_kilobyte_is_1024_bytes else 1000
    for suffix in SUFFIXES[multiple]:
        size /= multiple
        if size < multiple:
            return '{0:.1f} {1}'.format(size, suffix)

    raise ValueError('number too large')


header = re.compile(r'^(\d+) bytes each:\n$')


# box
class Size:
    __slots__ = 'value',
    def __init__(self, value):
        self.value = value


def parser(lines):
    lines = iter(lines)
    while True:
        # find header
        line = next(lines)
        match = header.match(line)
        if not match:
            continue
        size = Size(int(match.group(1), 10))
        # annotate each path with size
        for path in lines:
            if path == '\n':
                break
            yield (size, path)


def process(input, output, encoding, limit):
    '''
    Parses fdupes log, created with option -S, and converts file sizes in bytes
    into human readable sizes.

    Input log format looks like this:
    31337 bytes each:
    /path/to/dup1
    /path/to/dup2
    <newline>
    31338 bytes each:
    ... and so on

    '''

    with open(input, mode='r', encoding=encoding, errors='replace') as input, \
         open(output, mode='w', encoding=encoding) as output:
        for size, paths in itertools.groupby(parser(input), lambda x: x[0]):
            dups_size = size.value
            if dups_size >= limit: # output only records which size is sufficient
                header = '%s each:\n' % approximate_size(dups_size)
                output.write(header)

                output.writelines(path for _, path in paths)
                output.write('\n')


# known arguments
argp = argparse.ArgumentParser(description='processes fdupes utility log file')
argp.add_argument('-i', '--input', dest='input', required=True,
                  help='fdupes log input file; must be created with -S option')
argp.add_argument('-o', '--output', dest='output',
                  help='output file; if omitted, \'.out\' suffix will be appended to input file name')
argp.add_argument('-l', '--limit', dest='limit', type=int, default=0,
                  help='records with size less than given will be ignored')
argp.add_argument('-e', '--encoding', dest='encoding', default='utf8',
                  help='file encoding; by default, utf8 is used')


if __name__ == '__main__':
    args = argp.parse_args()

    if (args.output == None):
        args.output = args.input + '.out'

    process(**dict(args._get_kwargs()))
