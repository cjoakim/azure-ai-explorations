#!/bin/bash

# Utility script to somewhat transform the list of dependencies in a
# requirements.txt file to a quoted format for a corresponding pyproject.toml
# file.  Minimizes the manual work of quoting each requirement.
#
# Usage: ./quotelines.sh requirements.in > pyproject.toml
#
# Chris Joakim, 2025 

sed 's/.*/  "&",/' $1 
