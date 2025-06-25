#!/bin/bash

# Invoke the several "show" scripts in this directory to
# capture their state as well as their keys in the tmp/
# directory.  Then run the pyhton program to extract the
# key values for use in setting environment variables.
# Chris Joakim, 2025

./ai-search-show-keys.sh
./aoai-show-keys.sh
./app-insights-show-keys.sh
./cogsvcs-show-accts-info.sh
./cosmos-show-container.sh
./cosmos-show-keys.sh
./foundry-show-keys.sh
./kv-show-list-keys.sh
./log-analytics-show-keys.sh
./rg-show.sh
./show-container.json
./storage-show-keys.sh

source .venv/bin/activate

python main.py extract_env_vars

cat tmp/azure-env-vars.txt
