#!/bin/bash

# This script reformats the python codebase per the formatting rules
# defined in the 'black' library.
# See https://black.readthedocs.io/en/stable/
#
# Chris Joakim, 2025

black *.py
black src 
black tests
