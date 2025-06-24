#!/bin/bash

# Delete and recreate the Azure Search zipcodes index.
# This index is directly populated with the REST API
# rather than using a Cosmos DB datasource like the airports index.
# Chris Joakim, 2025

source .venv/bin/activate

python main-search.py delete_index pythonlibs

python main-search.py create_index pythonlibs aisearch/pythonlibs_vector_index.json

# The input directory used here points to the CosmosAIGraph repository,
# which is assumed to be on your system at the same level as this repository.
# See https://github.com/AzureCosmosDB/CosmosAIGraph
#python main-search.py direct_load_index pythonlibs ../../CosmosAIGraph/data/pypi/wrangled_libs --xload
