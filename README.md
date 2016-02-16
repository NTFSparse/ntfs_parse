# ntfs_parse #
NTFS parser, plus linking capabilites between MFT LogFile and UsnJrnl
This project is part of a research looking into the possibilities of combining 
the MFT, LogFile and UsnJrnl. The code is written from scratch and made open-source under the MIT license.

This proof-of-concept is not a commercial ready project.

## Usage ##
There is a basic shell script which does all the basic parsing. This gives the user a quick output of
files without knowing all the separate commands.

**NOTE:** 
Some subcommands/programs have a raw,parsed,csv,transactions choice. This gives a type of output. In case of the 
transaction option in the *logfileparse.py* this will connect the separate LSN together.
 
### full_run.sh ###
Without a parameter the help information will be printed.

usage: 

```./full_run.sh image_name sector_offset directory```

| variable | description |
| -------- | ----------- |
| `image_name` | Raw disk image |
| `sector_offset` | offset to partition in sectors (mmls could be used for this) |
| `directory` | relative directory for file output |

**NOTE:** this script needs The Sleuth Kit's (TSK) 'fls' program

### mftparse.py ###
MFT parser
This program exists out of multiple subcommands which makes it able to export specific inums, of extract the
date which belongs to a specific inum.

usage: 

```mftparse.py [-h] {export,extractdata,statistics} ...```

| positional arguments | description |
| -------------------- | ----------- |
| `export` | Export specific inums into a certain type |
| `extractdata` | Extracts data for a single entry, essentially returning the file |
| `statistics`  | Show statistics about this NTFS |


| optional arguments | description |
| ------------------ | ----------- |
| `-h`, `--help`     | show this help message and exit |

#### export ####
Export specific inums into a certain type

usage: 

```mftparse.py export [-h] [-o OFFSET_SECTORS | -O OFFSET_BYTES] [-s SECTOR_SIZE] [-i IMAGE | -f FILE] [-t {raw,parsed,csv}] [-e EXPORT_FILE] [-q INUMS]```

| optional arguments | choice | description |
| ------------------ | ------ | ----------- |
| `-h`, `--help`     | None | show this help message and exit |
| `-o` | OFFSET_SECTORS | Offset into the image for the filesystem, in sectors |
| `-O` | OFFSET_BYTES | Offset into the image for the filesystem, in bytes |
| `-s` | SECTOR_SIZE  | sector size (default=512) |
| `-i` | IMAGE | raw image file |
| `-f` | FILE | extracted $MFT file |
| `-t` | raw,parsed,csv | Type of export. Default=parsed |
| `-e` | EXPORT_FILE | Name of destination file. If left out, stdout is used. Existing files will be overwritten. |
| `-q` | INUMS | Singe inum or range(s) of inums. Ranges are inclusive. Example: 0-11,24-34,40. Also possible: all. Default=all |

#### extractdata ####
Extracts data for a single entry, essentially returning the file

usage: 

```mftparse.py extractdata [-h] [-o OFFSET_SECTORS | -O OFFSET_BYTES] [-s SECTOR_SIZE] [-i IMAGE | -f FILE] [-q INUM] [-a DATA_STREAM] [-e OUTPUT_FILE]```

| optional arguments | choice | description |
| ------------------ | ------ | ----------- |
| `-h`, `--help` | None | show this help message and exit |
| `-o` | OFFSET_SECTORS | Offset into the image for the filesystem, in sectors |
| `-O` | OFFSET_BYTES | Offset into the image for the filesystem, in bytes |
| `-s` | SECTOR_SIZE | sector size (default=512) |
| `-i` | IMAGE | raw image file |
| `-f` | FILE | extracted $MFT file |
| `-q` | INUM | Inode number of the entry to extract data of |
| `-a` | DATA_STREAM | (Alternate) data stream. Default=0 |
| `-e` | OUTPUT_FILE | Name of file that will contain the data |

#### statistics ####
Show statistics about this NTFS

usage: 

```mftparse.py statistics [-h] [-o OFFSET_SECTORS | -O OFFSET_BYTES] [-s SECTOR_SIZE] [-i IMAGE | -f FILE]```

| optional arguments | choice | description |
| ------------------ | ------ | ----------- |
| `-h`, `--help` | None | show this help message and exit |
| `-o` | OFFSET_SECTORS | Offset into the image for the filesystem, in sectors |
| `-O` | OFFSET_BYTES | Offset into the image for the filesystem, in bytes |
| `-s` | SECTOR_SIZE | sector size (default=512) |
| `-i` | IMAGE | raw image file |
| `-f` | FILE | extracted $MFT file |

### logfileparse.py ###
usage: ./logfileparse.py [-h] [-f FILE_NAME] [-e EXPORT_FILE]
[-t {parsed,csv,transaction,parsedlsns}]
[-d DUMP_DIR] [-n NUM] [-q LSNS] [-p]

| optional arguments | choice | description |
| ------------------ | ------ | ----------- |
| `-h`, `--help` | None | show this help message and exit |
| `-f` | FILE_NAME | extracted $DATA attribute of the $MFT $LogFile entry |
| `-e` | EXPORT_FILE | Name of destination file. If left out, stdout is used. Existing files will be overwritten. |
| `-t`  | parsed,csv,transaction,parsedlsns | Type of export. Default=parsed |
| `-d` | DUMP_DIR | Directory for dumping incomplete parsed pages. Output in directory is full binary RCRD page of 4096 bytes. Default='./errorpages' |
| `-n` | NUM | Number of pages to parse. If left out, all pages are parsed |
| `-q` | LSNS | Select what LSN's to output (parsed). Comma separated. |
| `-p` | None | Put program in performance measurement mode |


### usnjrnlparse.py ###

usage: 

```usnjrnlparse.py [-h] [-f   FILE] [-e OUTPUT] [-n NUMBER]```

| optional arguments | choice | description |
| ------------------ | ------ | ----------- |
| `-h`, `--help` | None | show this help message and exit |
| `-f` | FILE | File containing the UsnJrnl |
| `-e` | OUTPUT | Output file |
| `-n` | NUMBER | Number of records to parse. If left out, all will be parsed. |


### proof-of-concept.py ###
This program combines the separate parsers and generate a simple overview
illustrating the possibilities of what can be reached when combining the different outputs.

usage: 

```proof-of-concept.py [-h] [-o OFFSET_SECTORS | -O OFFSET_BYTES] [-s SECTOR_SIZE] -i IMAGE [-d DUMP_DIR] [-q INUM] [--deleted]```

| optional arguments | choice | description |
| ------------------ | ------ | ----------- |
| `-h`, `--help` | None | show this help message and exit |
| `-o` | OFFSET_SECTORS | Offset into the image for the filesystem, in sectors |
| `-O` | OFFSET_BYTES | Offset into the image for the filesystem, in bytes |
| `-s` | SECTOR_SIZE | sector size (default=512) |
| `-i` | IMAGE | raw image file |
| `-d` | DUMP_DIR | Directory for dumping incomplete parsed pages. Output in directory is full binary RCRD page of 4096 bytes. Default='./errorpages' |
| `-q` | INUM | MFT entry number (inum) to show data of |
| `--deleted` | Only show deleted data for MFT entry/entries |

## Usage examples ##
To do a full run using the example disk:

```./full_run.sh disk_image/disk.raw 128 output```

To generate a human-readable parsed output of the MFT do:

```./mftparse.py export -i disk_image/disk.raw -o 128 -t parsed -e output/mft.parsed```

Extracting the LogFile out of the MFT:

```./mftparse.py extractdata -i disk_image/disk.raw -o 128 -q 2 -e output/logfile.raw```

Parse the raw LogFile data into a .csv file:

```./logfileparse.py -f output/logfile.raw -t csv -e output/logfile.csv```

For the output of the proof-of-concept program piped to *less*:

```./proof-of-concept.py -o 128 -i disk_image/disk.raw | less ```

For a specific inum do:

```./proof-of-concept.py -o 128 -i disk_image/disk.raw -q 40 | less```

For a specific inum, only showing historic information: 

```./proof-of-concept.py -o 128 -i disk_image/disk.raw -q 40 --deleted | less```

## Project structure ##
Short explanation of the directories in the repo.
* **disk_image** Contains a 10.5 MB example NTFS disk, including MBR.
* **errorpages** Directory that will contain all invalid and error pages of a LogFile parser run.
* **ntfs_parse** Directory containing the framework structure.
* **output** Example directory with the extracted files of the example disk in the *disk_image* directory.

## Create diagram of code ##
To automatically create a class diagram from the Python3 code, do the following:

1. ```apt-get install pylint3```
2. ```pyreverse3 ntfs_parse/```
3. ```dot -Tsvg classes_No_Name.dot -o classes.svg```

Or for Debian Jessie, 8.2

1. ```apt-get install python3-pip```
2. ```pip3 install pylint```
3. ```pyreverse ntfs_parse/```
4. ```dot -Tsvg classes_No_Name.dot -o classes.svg```

The svg can be opened in Firefox 
