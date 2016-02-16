#!/usr/bin/python3

from argparse import ArgumentParser
from time import process_time
import sys

from ntfs_parse import UsnJrnl

def parse_args(argument_string):
    parser = ArgumentParser()
    parser.add_argument('-f',
                        help='File containing the UsnJrnl',
                        dest='file')

    parser.add_argument('-e',
                        help='Output file',
                        dest='output')

    parser.add_argument('-n',
                        help='Number of records to parse. If left out, all will be parsed.',
                        dest='number',
                        type=int)

    return parser.parse_args(argument_string)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    usn_jrnl = UsnJrnl(args.file)
    usn_jrnl.parse(number=args.number)
    usn_jrnl.export_csv(args.output)
