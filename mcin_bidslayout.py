#!/usr/bin/env python3

import os
import sys
import csv
from argparse import ArgumentParser

"""Scan top-level BIDS directory. This must be a valid BIDS dataset, i.e.
containing:
    * participants.tsv
    * dataset_description.json
    * various sub-* folders with the data and JSON sidecar descriptors.
"""

def parse_pathinfo(bids_file):
    """Parse information from a filename into columns for the CSV file.
    Example filenames:
        * sub-1012146/ses-2/anat/sub-1012146_ses-2_T1w.json
        * sub-1012146/ses-2/anat/sub-1012146_ses-2_T1w.nii.gz

    We want the following headers in this order:
        participant_id, visit_label, modality, scan_type, nifti_file_path, json_file_path

    With the above examples:
        participant_id      = 1013032
        visit_label         = 2
        modality            = anat 
        scan_type           = T1w
        nifti_file_path     = sub-1012146/ses-2/anat/sub-1012146_ses-2_T1w.nii.gz
        json_file_path      = sub-1012146/ses-2/anat/sub-1012146_ses-2_T1w.json
    """
    print(bids_file)
    return []


def recurse(directory):
    """We're using scandir here because it explicitly returns an iterator, allowing
    for lazy evaluation of the list. This will help us avoid memory problems.
    """
    with os.scandir(directory) as it:
        """Count the characters in the supplied path parameter. These will be stripped
        from the path given by scan_dir to simplify processing.
        """
        try:
            for entry in it:
                if entry.is_file():
                    """Parse path info and strip the directory from the front of the path."""
                    global prefix_length
                    row = parse_pathinfo(entry.path[prefix_length:])
                    global count
                    count += 1
                    #print(count)

                if entry.is_dir():
                    recurse(entry.path)
        except PermissionError as e:
            """This occurred during testing a squashfs instance that was improperly configured.
            Raising this exception will help with identifying configuration problems.
            Without it, the script will choke."""
            print(e)

parser = ArgumentParser()
parser.add_argument("-d", "--directory", dest="directory",
                    help="BIDS directory to scan. Must be in valid BIDS format.")
args = parser.parse_args()

if args.directory == None:
    parser.print_help()
    quit()

global count
count = 0
global prefix_length
prefix_length = len(args.directory)
"""If a user does not include a forward slash, an extra character needs 
to be stripped from the file path later."""
if not args.directory.endswith('/'):
    prefix_length += 1

with open('results.csv', 'w', newline='') as csvfile:
    recurse(args.directory)


