#!/bin/bash

# Delete and recreate the Azure Search zipcodes index.
# This index is directly populated with the REST API
# rather than using a Cosmos DB datasource like the airports index.
# Chris Joakim, 2025

source .venv/bin/activate

python main-search.py delete_index zipcodes

python main-search.py create_index zipcodes aisearch/zipcodes_index.json

python main-search.py direct_load_index zipcodes ../data/zipcodes/us_zipcodes.json --load
