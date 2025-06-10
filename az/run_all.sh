#!/bin/bash

# Delete the contents of the tmp directory, then execute
# the several informational scripts in this directory.
#
# Chris Joakim, 2025

mkdir -p tmp
rm -rf tmp/* 

./az-list-regions.sh
./az-cogsvcs-acct-info.sh
./az-cogsvcs-model-list.sh
./az-cogsvcs-usage-info.sh

echo "done"
