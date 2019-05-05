#!/usr/bin/env bash

#
#   - Summary:   Post commit hook, updates version throughout project
#   - Location:  .git/hooks
#   - Filename:  commit-msg
#

# extract package name
PACKAGE=$(grep PACKAGE DESCRIPTION.rst | awk -F ':' '{print $2}')
source $PACKAGE/_version.py

VERSION="$__version__"
DEPRECATED="$(grep 'Version:' README.md | awk -F ':' '{print $2}')"

if [ ! "$DEPRECATED" ]; then
    # attempt with markdown formatting inclu
    DEPRECATED="$(grep '\*\*Version\*\*:' README.md | awk -F ':' '{print $2}')"
fi
 
 
# strip surrounding whitespace
#STRIPPED="$(sed -e 's/[[:space:]]*$//' <<<${DEPRECATED})"

#sed -i "s/$STRIPPED/\t$VERSION/g" README.md
sed -i "s/$DEPRECATED/\t$VERSION/g" README.md
