#!/usr/bin/python3

from argparse import ArgumentParser
from time import process_time
import sys

from ntfs_parse import MFT
from ntfs_parse import BootSector
from ntfs_parse import InumRange

def parse_args(argument_string):
    common_arguments = ArgumentParser(add_help=False)

    # group of offset parameters
    o_group = common_arguments.add_mutually_exclusive_group()
    o_group.add_argument('-o',
                         help='Offset into the image for the filesystem, in sectors',
                         dest='offset_sectors',
                         type=int)
    o_group.add_argument('-O',
                         help='Offset into the image for the filesystem, in bytes',
                         dest='offset_bytes',
                         type=int)
    common_arguments.add_argument('-s',
                        help='sector size (default=%(default)s)',
                        default=512,
                        dest='sector_size')

    # Group of input file/image parameters
    input_group = common_arguments.add_mutually_exclusive_group()
    input_group.add_argument('-i',
                                  help='raw image file',
                                  dest='image')
    input_group.add_argument('-f',
                                  help='extracted $MFT file',
                                  dest='file')

    # Group of subcommands
    parser = ArgumentParser(description='MFT parser')
    sub_parsers = parser.add_subparsers(help='actions', dest='action')

    ### Export
    help = 'Export specific inums into a certain type'
    export_parser = sub_parsers.add_parser('export', parents=[common_arguments],
                                           description=help,
                                           help=help)

    export_parser.add_argument('-t',
                               help='Type of export. Default=%(default)s',
                               choices=['raw', 'parsed', 'csv'],
                               dest='export_type',
                               default='parsed')

    export_parser.add_argument('-e',
                               help='Name of destination file. If left out, stdout is used. Existing files will be overwritten.',
                               dest='export_file')

    export_parser.add_argument('-q',
                               help='Singe inum or range(s) of inums. Ranges are inclusive. Example: 0-11,24-34,40. Also possible: all. Default=%(default)s',
                               dest='inums',
                               default='all')

    ### extractdata
    help = 'Extracts data for a single entry, essentially returning the file'
    extractdata_parser = sub_parsers.add_parser('extractdata', parents=[common_arguments],
                                              description=help,
                                              help=help)
    extractdata_parser.add_argument('-q',
                                  help='Inode number of the entry to extract data of',
                                  dest='inum',
                                  type=int)

    extractdata_parser.add_argument('-a',
                                  help='(Alternate) data stream. Default=%(default)s',
                                  dest='data_stream',
                                  default=0,
                                  type=int)

    extractdata_parser.add_argument('-e',
                                  help='Name of file that will contain the data',
                                  dest='output_file')

    ### statistics
    help = 'Show statistics about this NTFS'
    statistics_parser = sub_parsers.add_parser('statistics', parents=[common_arguments],
                                               description=help,
                                               help=help)

    return parser.parse_args(argument_string)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    if args.image:
        sector = BootSector(image_name=args.image,
                  offset_sectors=args.offset_sectors,
                  offset_bytes=args.offset_bytes,
                  sector_size=args.sector_size)


    mft = MFT(image_name=args.image, boot_sector=sector)

    # Export
    if args.action == 'export':
        # Parsing
        if args.inums == 'all':
            mft.parse_all()
            range = None
        else:
            range = InumRange(args.inums)
            mft.parse_inums(inum_range=range)

        # Exporting
        if args.export_type == 'parsed':
            mft.export_parsed(inum_range=range, export_file=args.export_file)
        elif args.export_type == 'csv':
            mft.export_csv(inum_range=range, export_file=args.export_file)
        elif args.export_type == 'raw':
            mft.export_raw(inum_range=range, export_file=args.export_file)

    # Extract data
    if args.action == 'extractdata':
        mft.parse_inum(args.inum)
        mft.extract_data(inum=args.inum, output_file=args.output_file, stream=args.data_stream)

    # Statistics
    if args.action == 'statistics':
        mft.parse_all()
        mft.print_statistics()