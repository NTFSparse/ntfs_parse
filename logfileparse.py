#!/usr/bin/python3

from argparse import ArgumentParser
import sys

from time import process_time
from ntfs_parse import LogFile


def parse_args(argument_string):
    parser = ArgumentParser(prog='./logfileparse.py')
    parser.add_argument('-f',
                        help='extracted $DATA attribute of the $MFT $LogFile entry',
                        dest='file_name')
    parser.add_argument('-e',
                        help='Name of destination file. If left out, stdout is used. Existing files will be overwritten.',
                        dest='export_file')
    parser.add_argument('-t',
                        help='Type of export. Default=%(default)s',
                        choices=['parsed', 'csv', 'transaction', 'parsedlsns'],
                        default='parsed',
                        dest='export_type')
    parser.add_argument('-d',
                        help='Directory for dumping incomplete parsed pages. Output in directory is full binary RCRD '
                             'page of 4096 bytes. Default=\'./errorpages\'',
                        default='errorpages',
                        dest='dump_dir')
    parser.add_argument('-n',
                        help='Number of pages to parse. If left out, all pages are parsed',
                        dest='num',
                        type=int)
    parser.add_argument('-q',
                        help='Select what LSN\'s to output (parsed). Comma separated.',
                        dest='lsns')
    parser.add_argument('-p',
                        help='Put program in performance measurement mode',
                        action="store_true")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    data = LogFile(dump_dir=args.dump_dir, file_name=args.file_name, performance=args.p)
    data.parse_all(args.num)

    if args.export_type == 'parsed':
        data.export_parsed(export_file=args.export_file)
    elif args.export_type == 'csv':
        data.connect_transactions()
        data.export_csv(export_file=args.export_file)
    elif args.export_type == 'transaction':
        data.connect_transactions()
        #data.print_transactions(export_file=args.export_file)
        #data.print_faulty_transactions(export_file=args.export_file)
        data.export_transactions(export_file=args.export_file)
    elif args.export_type == 'parsedlsns':
        data.connect_transactions()
        data.export_parsed_lsns(export_file=args.export_file, lsn_numbers=[int(num) for num in args.lsns.split(',')])
