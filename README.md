# Background

_This is a companion script for use with [LORIS-MRI](https://github.com/aces/Loris-MRI)._

When analyzing

LORIS-MRI contains a processing pipeline written in Python to assist with the analysis
and import of data from BIDS datasets to the [LORIS software](https://github.com/aces/Loris). These tools depend on a
library, `pybids`, which is used to model a BIDS dataset in an object-oriented way.
This library uses Python's `os.walk()` function to read a BIDS folder. For most
cases this works well; however, problems can occur with very large datasets. `os.walk()`
calls `os.stat()` on each file which increases runtime dramatically.

In the context of a project at [MCIN](https://github.com/aces/), we had a use case where we needed to remotely
mount a large dataset which would be read into a LORIS database. Due to the size of this
dataset, `pybids` was not able to complete the analysis of the directory and [the
maintainters reported](https://github.com/bids-standard/pybids/issues/609) that there would be no quick or easy fix to ameliorate this. 
(This was exacerbated on our side as the pipeline was running over files mounted
remotely via `sshfs` which increased processing time.)

# Solution

Our pipeline failed when calling BIDSLayout from `pybids`. Rather than read all the
folders into memory at run-time, we have written this script to read through a
large BIDS directory once and to convert its data into a simple CSV file.

This CSV file will be analyzed by LORIS-MRI's Python scripts and read into a format
matching the key-value pairs used in `pybids`'s BIDSLayout.

This should address the issue by:
	

* Eliminating all the file read operations during the processing pipeline. Instead, it will only read from the CSV file.
	
* Using a generator pattern to read information about one BIDS file at a time and perform actions on it before reading the complete folder. 

## Layout of the CSV file

[todo]
