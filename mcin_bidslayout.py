#!/usr/bin/env python3

import os
import sys
from argparse import ArgumentParser

"""Scan top-level BIDS directory. This must be a valid BIDS dataset, i.e.
containing:
    * participants.tsv
    * dataset_description.json
    * various sub-* folders with the data and JSON sidecar descriptors.
"""


"""We're using scandir here because it explicitly returns an iterator, allowing
for lazy evaluation of the list. This will help us avoid memory problems.
"""
def recurse(path):
    with os.scandir(path) as it:
        try:
            for entry in it:
                if entry.is_file():
                    print(entry.name)

                if entry.is_dir():
                    recurse(entry.path)
        except PermissionError as e:
            print(e)



parser = ArgumentParser()
parser.add_argument("-p", "--path", dest="path",
                    help="path to the folder to scan")
args = parser.parse_args()

if args.path == None:
    parser.print_help()
    quit()

recurse(args.path)
