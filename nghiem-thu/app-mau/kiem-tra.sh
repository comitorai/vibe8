#!/bin/sh
# Script `check` của app mẫu.
set -eu
python3 -m unittest discover -s tests -t .
