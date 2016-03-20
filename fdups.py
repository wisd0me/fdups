#!env python3                                                                                                                                              [9/739]

infile = 'dups.log'
outfile = infile + '.out'
encoding = 'utf8'
filter_size_lt = 49000000 # filter out sizes less than this
############################################################

SUFFIXES = {1000: ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            1024: ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']}

def approximate_size(size, a_kilobyte_is_1024_bytes=True):
    '''Convert a file size to human-readable form.

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

# parsed format looks like this:
# 31337 bytes each:
# /path/to/dup1
# /path/to/dup2
# <newline>
# 31338 bytes each:
# ... and so on

input = open(infile, mode='r', encoding=encoding, errors='replace')
output = open(outfile, mode='w', encoding=encoding)

for line in input:
        if line.find(' bytes each:') ==  -1:
                continue

        #print(line, end='')
        tokens = line.split(' ')
        # filter reports which is below the specified bound
        if int(tokens[0]) < filter_size_lt:
                for skipln in input:
                        if skipln == '\n':
                                break
        else:
                line = approximate_size(int(tokens[0])) + ' each:\n'
                output.write(line)

                for writeln in input:
                        output.write(writeln)
                        if writeln == '\n':
                                break
