#!/usr/bin/env python3

import os
import sys
import itertools
import csv
from pathlib import Path
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
    """
    path_parts = bids_file.split('/')
    # Participant ID: remove "sub-"
    participant_id = path_parts[0][4:]
    # Visit_label: Use value following 'ses'
    visit_label = path_parts[1][4:]
    # Modality: Equal to the third path part
    modality = path_parts[2]
    # Scan type: Split Fourth path part on underscores. Use the last value.
    scan_type = path_parts[3].split('_')[-1]
    return [participant_id, visit_label, modality, scan_type]


def recurse(directory, csvwriter, validate_json = False):
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
                    if entry.name == 'dataset_description.json' or entry.name == 'participants.tsv':
                        # Skip metadata files.
                        continue

                    """Skip analysis of JSON files. A record of each JSON file will be manually added
                    for each image.
                    """
                    # Path.suffixes returns a list of potentially many extensions.
                    p = Path(entry.name)
                    stem = p.stem # i.e. the filename without the extension

                    # strip additional file extensions from stem, if present.
                    while Path(stem).stem != stem:
                        stem = Path(stem).stem

                    extension = p.suffixes[0]

                    # Strip arcive info

                    if extension == '.json':
                        continue

                    elif extension == '.nii':
                        image_file_path = entry.name

                    json_file_path = stem + '.json'
                    """Optionally validate whether the JSON file actually exists for
                    this imaging file. This is not done by default because this script
                    is expected to be run on massive, read-only datasets and so it's
                    useful to shave off time where possible. The datasets can probably
                    be trusted.
                    """
                    if validate_json:
                        fullpath = os.path.join(directory, json_file_path)
                        if not os.path.isfile(fullpath):
                            print('WARNING: JSON file does not exist: ' + fullpath)
                            json_file_path = 'missing'

                    """Get participant ID, visit_label, modality, and scan_type from
                    path. Add JSON and NIFTI prefixes manually.

                    TODO This will need to be extended to support other file types.
                    """
                    global prefix_length

                    # Parse path info and strip the directory from the front of the path.
                    row = parse_pathinfo(entry.path[prefix_length:])
                    row.append(image_file_path)
                    row.append(json_file_path)
                    csvwriter.writerow(row)

                    # Print a spinner and a runnign count of files analyzed for every 100
                    global count
                    count += 1
                    if count % 100 == 0:
                        output = '{} files analyzed... '.format(count)

                        sys.stdout.flush()
                        sys.stdout.write('\b' * len(output))
                        sys.stdout.write(output)

                    print_spinner()

                if entry.is_dir():
                    recurse(entry.path, csvwriter, validate_json)
        except PermissionError as e:
            """This occurred during testing a squashfs instance that was improperly configured.
            Raising this exception will help with identifying configuration problems.
            Without it, the script will choke."""
            print(e)

def print_spinner():
    global spinner
    sys.stdout.write(next(spinner))   # write the next character
    sys.stdout.flush()                # flush stdout buffer (actual character display)
    sys.stdout.write('\b')            # erase the last written char

# Parse arguments and do basic validation on inputs.
parser = ArgumentParser()
parser.add_argument("-d", "--directory", dest="directory",
                    help="BIDS directory to scan. Must be in valid BIDS format.")
parser.add_argument("-j", "--check-json", dest="checkjson", action='store_true',
                    help="Validates that JSON sidecar files exist. False by default.")
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

    global spinner
    spinner = itertools.cycle(['-', '/', '|', '\\'])


with open('results.csv', 'w', newline='') as csvfile:
    print('Beginning analysis of directory {}...'.format(args.directory))
    csvwriter = csv.writer(csvfile)
    recurse(args.directory, csvwriter, args.checkjson)


