#!/bin/bash

# Delete and recreate the Azure Search pythonlibs index
# which has vector search enabled on field 'embeddings'.
# This index is directly populated with the REST API
# rather than using a Cosmos DB datasource like the airports index.
# Chris Joakim, 2025

source .venv/bin/activate

echo "=== SHELL delete index ==="
python main-search.py delete_index pythonlibs

# See https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-create-index
# See file aisearch/pythonlibs_vector_index.json in this repo.

echo "=== SHELL create index ==="
python main-search.py create_index pythonlibs aisearch/pythonlibs_vector_index.json

# The input directory used here points to the CosmosAIGraph repository,
# which is assumed to be on your system at the same level as this
# azure-ai-explorations repo.  I created this CosmosAIGraph project
# and dataset while working at Microsoft - cjoakim.
# See https://github.com/AzureCosmosDB/CosmosAIGraph

echo "=== SHELL populate index ==="
python main-search.py direct_load_index pythonlibs ../../CosmosAIGraph/data/pypi/wrangled_libs --load
