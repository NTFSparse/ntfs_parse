#!/bin/bash

if [ $# != 3 ]; then
    echo "usage: ./full_run.sh image_name sector_offset directory"
    echo ""
    echo "  image_name        Raw disk image"
    echo "  sector_offset     offset to partition in sectors"
    echo "                    (mmls could be used for this)"
    echo "  directory         relative directory for file output"
    echo ""
    echo "NOTE: this script needs The Sleuth Kit's (TSK) 'fls' program"
    exit
fi

image_name="$1"
sector_offset="$2"
directory="$3"

echo "image: ${image_name}, offset: ${sector_offset}, output directory: ${directory}"

## MFT
echo "Parsing \$MFT"
# export the mft as a parsed document (human readable)
./mftparse.py export -i ${image_name} -o ${sector_offset} -t parsed -e ${directory}/mft.parsed
# export the mft as a csv document (mere readable)
./mftparse.py export -i ${image_name} -o ${sector_offset} -t csv -e ${directory}/mft.csv

## LogFile
echo "Parsing \$LogFile"
# carve the logfile out of the image
./mftparse.py extractdata -i ${image_name} -o ${sector_offset} -q 2 -e ${directory}/logfile.raw
# parse the logfile in human readable format
./logfileparse.py -f ${directory}/logfile.raw -t parsed -e ${directory}/logfile.parsed -p
# parse the logfile in a csv format
./logfileparse.py -f ${directory}/logfile.raw -t csv -e ${directory}/logfile.csv
# parse the logfile to rebuild all the transactions (lsn chains)
./logfileparse.py -f ${directory}/logfile.raw -t transaction -e ${directory}/logfile_transactions.csv

## UsnJrnl
echo "Parsing \$UsnJrnl"
# find the correct inum where the UsnJrnl is located
usnjrnl_inum=`fls ${image_name} -o ${sector_offset} 11 | grep '\$UsnJrnl:\$J' | awk '{print $2}' | cut -d '-' -f1`
# carve the UsnJrnl out of the image
./mftparse.py extractdata -i ${image_name} -o ${sector_offset} -q ${usnjrnl_inum} -e ${directory}/usnjrnl.raw
# parse the UsnJrnl
./usnjrnlparse.py -f ${directory}/usnjrnl.raw -e ${directory}/usnjrnl.csv

## Resulting files:
# MFT     --> mft.parsed, mft.csv
# LogFile --> logfile.raw, logfile.parsed, logfile.csv, logfile_transaction.csv
# UsnJrnl --> usnjrnl.raw, usnjrnl.csv
