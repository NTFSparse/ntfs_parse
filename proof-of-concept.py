#!/usr/bin/python3
########################################################################################################################
# Proof-of-Concept:
#   This program makes use of the separate build parsers.
#   The MFT, $LogFile and $UsnJrnl are getting parsed and the data is combined in a historic overview.
#   The overview describes the previous file names and events of a MFT entry (a file).
#   Both the $UsnJrnl and the $LogFile data is combined using our model.
#
# Input:
#   - offset where NTFS partition starts            (mandatory)
#   - disk image of type NTFS                       (mandatory)
#   - directory of error pages ($LogFile)           (optional)
#   - specific MFT entry (inum)                     (optional)
#
# Structure:
#
#  MFTEntryHistory                                             = MFTEntryHistory class
#   |
#   +-- MFT entry                                              = MFTEntry class    > ./ntfs_parse/mft/mft_entry.py
#   +-- sequence val                                           = int
#   +-- is_in_use                                              = boolean
#   +-- file_name                                              = string
#   +-- history                                                = dict
#        |                                                        |
#        +--{ sequence_value: MFTSequenceValueHistory class}   = with MFTSequenceValueHistory classes
#                               |
#                               +-- MFT entry number (inum)    = int
#                               +-- sequence value             = int
#                               +-- match_list                 = list
#                                    |
#                                    +--[Match class]
#                                         |
#                                         +-- USN record       = UsnRecord class   > ./ntfs_parse/usnjrnl/usn_jrnl.py
#                                         +-- Transaction      = Transaction class > ./ntfs_parse/logfile/transaction.py
#
# Issues:
#   - It may be obvious that this proof-of-concept is not the fastest code.
#     All the nesting can be avoided by using dictionaries search trees or by using a database
########################################################################################################################

from argparse import ArgumentParser
from tempfile import NamedTemporaryFile
import sys

from ntfs_parse import BootSector, MFT, LogFile, UsnJrnl, AttributeTypeEnum


def parse_args(argument_string):
    parser = ArgumentParser(description='MFT parser')

    # group of offset parameters
    o_group = parser.add_mutually_exclusive_group()
    o_group.add_argument('-o',
                         help='Offset into the image for the filesystem, in sectors',
                         dest='offset_sectors',
                         type=int)
    o_group.add_argument('-O',
                         help='Offset into the image for the filesystem, in bytes',
                         dest='offset_bytes',
                         type=int)
    parser.add_argument('-s',
                        help='sector size (default=%(default)s)',
                        default=512,
                        dest='sector_size')

    # Group of input file/image parameters
    parser.add_argument('-i',
                        help='raw image file',
                        dest='image',
                        required=True)

    parser.add_argument('-d',
                        help='Directory for dumping incomplete parsed pages. Output in directory is full binary RCRD '
                             'page of 4096 bytes. Default=\'./errorpages\'',
                        default='errorpages',
                        dest='dump_dir')

    # Group of output preference
    parser.add_argument('-q',
                        help='MFT entry number (inum) to show data of',
                        dest='inum',
                        type=int,
                        default=None)
    parser.add_argument('--deleted',
                        help='Only show deleted data for MFT entry/entries',
                        action='store_true')

    return parser.parse_args(argument_string)


########################################################################################################################
# MFT history class
class MFTEntryHistory:
    def __init__(self, mft_object):
        self.mft_entry = mft_object
        self.sequence_val = mft_object.sequence_value
        self.is_in_use = mft_object.is_in_use
        self.file_name = mft_object.attributes[AttributeTypeEnum.FILE_NAME][0].name if AttributeTypeEnum.FILE_NAME in mft_object.attributes.keys() else '~unknown~'
        self.history = {}

    def add_history(self, mft_seq_val, mft_seq_val_hist):
        self.history[mft_seq_val] = mft_seq_val_hist

    def print(self):
        self.print_current_mft_info()
        self.print_summary()
        self.print_full_history()

    def print_current_mft_info(self):
        print()
        print('#######################################################################################################')
        print('# Current MFT information                                                                 #############')
        print('#######################################################################################################')
        print('MFT entry number:', self.mft_entry.inum)
        print('Sequence value  :', self.mft_entry.sequence_value)
        print('Currently in use:', self.is_in_use, end=' ')
        print('-> Historic data in MFT entry, easy to extract' if not self.is_in_use else '')
        print('File name       :', self.file_name)
        print()

    def print_summary(self):
        print('SUMMARY:')
        print('╔═════╦═══════════════════════════════════════════════════════════════════════════════════════════════╗')
        print('║ seq ║ USN record list                                                                               ║')
        print('╠═════╬═══════════════════════════════════════════════════════════════════════════════════════════════╣')
        for sequence in sorted(self.history.keys()):
            print('║ %3i ║ %-93s ║' % (sequence, [match.usn_record.usn for match in self.history[sequence].match_list]))
        print('╚═════╩═══════════════════════════════════════════════════════════════════════════════════════════════╝')
        print()

    def print_full_history(self):
        print('FULL HISTORY:')
        for mft_history_key in sorted(self.history.keys()):
            # print('MFT history key :', mft_history_key)
            self.history[mft_history_key].print()

    def print_deleted_history(self):
        if min(self.history.keys()) != self.sequence_val:
            self.print_current_mft_info()
            self.print_summary()
            tmp_dct = dict((sequence, hist) for sequence, hist in self.history.items() if sequence < self.sequence_val)
            for mft_history_key in sorted(tmp_dct.keys()):
                tmp_dct[mft_history_key].print(deleted_history=True)
        else:
            self.print_current_mft_info()
            print('THIS ENTRY HAS NO DELETED LOG DATA AVAILABLE')


########################################################################################################################
# MFT history class
class MFTSequenceValueHistory:
    # match_list is a list with match objects
    def __init__(self, mft_entry_number, mft_sequence_value):
        self.mft_entry_number = mft_entry_number
        self.sequence_value = mft_sequence_value
        self.match_list = []

    def add_match(self, usn_record_object, transaction_object):
        self.match_list.append(Match(usn_record=usn_record_object, transaction=transaction_object))

    def print(self, deleted_history=False):
        print()
        print('=======================================================================================================')
        print(' MFT entry %i; Sequence value %i ' % (self.mft_entry_number, self.sequence_value), end='')
        print('%s' % '--> DELETE HISTORY' if deleted_history else '')
        print('=======================================================================================================')
        for match in self.match_list:
            match.print()


########################################################################################################################
# Match class
class Match:
    def __init__(self, usn_record, transaction):
        self.usn_record = usn_record
        self.transaction = transaction

    def print(self):
        print()
        self.print_usn_record()
        self.print_transaction()
        # print(self.usn_record.file_name, self.transaction.transaction_num)
        # print(self.transaction.transaction_num)

    def print_usn_record(self):
        tab = ' '*4
        print(tab+'USN      :', self.usn_record.usn)
        print(tab+'File name:', self.usn_record.file_name)
        print(tab+'Timestamp:', str(self.usn_record.timestamp_datetime))
        print(tab+'Reason   :', self.usn_record.reason_string)

    def print_transaction(self):
        tab = ' '*4
        print(tab+'╔══════════════════════════════════════════════════════════════════════════════════╗')
        print(tab+'║ $LogFile transaction number: %-51i ║' % self.transaction.transaction_num)
        print(tab+'╠═══════════╦══════════════════════════════════╦═══════════════════════════════════╣')
        print(tab+'║  LSN      ║ Redo operation                   ║ Undo operation                    ║')
        print(tab+'╠═══════════╬══════════════════════════════════╬═══════════════════════════════════╣')
        for lsn, redo_op, undo_op in self.transaction.all_opcodes:
            print(tab+'║ %9i ║ %-32s ║ %-33s ║' % (lsn, redo_op, undo_op))
        print(tab+'╚═══════════╩══════════════════════════════════╩═══════════════════════════════════╝')


########################################################################################################################
# Combining algorithm function
def combine_data(mft_entry_nr, seq_val_dict, all_log_file_transactions):
    # The basic, current, MFT entry information
    mft_entry_hist = MFTEntryHistory(mft.entries[mft_entry_nr])
    # For each entry in our $UsnJrnl items (grouped on sequence value)
    for sequence_val, records in seq_val_dict.items():
        # Add a MFT history object to the history dict.
        mft_entry_hist.add_history(sequence_val, mft_seq_val_hist=MFTSequenceValueHistory(mft_entry_nr, sequence_val))
        # Filling the history dict with matching USN and $LogFile records
        for usn_record in records:  # <<<--------------------+
            for transaction in all_log_file_transactions:  # <<<------------------------+
                if transaction.contains_usn:               # |                          |
                    # some transactions contain multiple   # |                          |
                    for usn in transaction.usns:           # |                          |
                        # if the same then it's a match    # |                          |
                        if usn[1] == usn_record.usn:       # |                          |
                            # At this level we have:       # |                          |
                            #  one of the USN records -> usn_record                     |
                            #  the transaction corresponding with that USN record -> transaction
                            # Add our USN record and the corresponding Transaction to our match list
                            mft_entry_hist.history[sequence_val].match_list.append(Match(usn_record, transaction))
    # return the list, otherwise the data_list variable is appended in obfuscation
    return mft_entry_hist

########################################################################################################################
# MAIN
if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    usnjrnl_file = NamedTemporaryFile()
    logfile_file = NamedTemporaryFile()

    # Parse the MFT first
    sector = BootSector(image_name=args.image,
                        offset_sectors=args.offset_sectors,
                        offset_bytes=args.offset_bytes,
                        sector_size=args.sector_size)
    mft = MFT(image_name=args.image, boot_sector=sector)
    mft.parse_all()

    # get the inum (MFT entry number) of the $UsnJrnl --> located in $Extend|$INDEX_ROOT attribute
    usn_jrnl_inum = mft.entries[11].\
        attributes[AttributeTypeEnum.INDEX_ROOT][0].\
        entries[AttributeTypeEnum.FILE_NAME]['$UsnJrnl'].\
        file_reference_mft_entry

    # carve out the logfile (inum 2) and store in local temporary file
    mft.extract_data(inum=2, output_file=logfile_file.name, stream=0)
    # carve out the $UsnJrnl (inum searched for above) and store in local temporary file
    mft.extract_data(inum=usn_jrnl_inum, output_file=usnjrnl_file.name, stream=0)

    # pass the temporary logfile-file into the $LogFile class and parse it
    log_file = LogFile(dump_dir=args.dump_dir, file_name=logfile_file.name)
    log_file.parse_all()
    log_file.connect_transactions()

    # pass the temporary usnjrnl-file into the $UsnJrnl class and parse it
    usn_jrnl = UsnJrnl(usnjrnl_file.name)
    usn_jrnl.parse()

    # close the temporary files as all the needed data is in the local variables usn_jrnl and log_file
    usnjrnl_file.close()
    logfile_file.close()

    # $UsnJrnl records ordered by MFT entry
    usnjrnl_grouped = usn_jrnl.grouped_by_entry

    # If no inum has been given as input go through all the available data,
    # else use the given inum to search for the inum related information
    # Both ways, we build our structure in meantime
    data_list = []
    if not args.inum:
        # For each entry in our $UsnJrnl items (grouped by MFT entry)
        for mft_entry, sequence_val_dict in sorted(usnjrnl_grouped.items()):
            data_list.append(combine_data(mft_entry, sequence_val_dict, log_file.transactions.values()))
    else:
        if args.inum in usnjrnl_grouped.keys():
            data_list.append(combine_data(args.inum, usnjrnl_grouped[args.inum], log_file.transactions.values()))
        else:
            print('No such MFT entry in $UsnJrnl')
            exit()

    # print the result of this program
    for mft_entry_hist_object in data_list:
        # print only the deleted or re-used MFt entries if argument is given else print all information
        mft_entry_hist_object.print_deleted_history() if args.deleted else mft_entry_hist_object.print()
