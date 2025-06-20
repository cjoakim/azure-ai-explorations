#!/bin/bash

# Utility script to somewhat a transform the list of dependencies
# in a requirements.txt file to a quoted format for a corresponding
# pyproject.toml file.
#
# Usage: ./quotelines.sh requirements.in > pyproject.toml
#
# Chris Joakim, 2025 

sed 's/.*/  "&",/' $1 
