#!/usr/bin/python3

from argparse import ArgumentParser
import sys

from ntfs_parse import BootSector


def parse_args(argument_string):
    parser = ArgumentParser()
    parser.add_argument('image',
                        help='raw image file')
    parser.add_argument('-s',
                        help='sector size (default=%(default)s)',
                        default=512,
                        dest='sector_size')
    o_group = parser.add_mutually_exclusive_group()
    o_group.add_argument('-o',
                         help='Offset into the image for the filesystem, in sectors',
                         dest='offset_sectors',
                         type=int)
    o_group.add_argument('-O',
                         help='Offset into the image for the filesystem, in bytes',
                         dest='offset_bytes',
                         type=int)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    sector = BootSector(image_name=args.image,
              offset_sectors=args.offset_sectors,
              offset_bytes=args.offset_bytes,
              sector_size=args.sector_size)

    sector.print()