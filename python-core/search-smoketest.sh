#!/bin/bash

# Invoke Azure AI Search Service, smoketest class AISearchUtil.
# Chris Joakim, 2025

source .venv/bin/activate

python main-search.py help

python main-search.py list_indexes
python main-search.py list_indexers
python main-search.py list_datasources

python main-search.py delete_indexer nosql-airports
python main-search.py delete_index nosql-airports
python main-search.py delete_datasource cosmosdb-nosql-dev-airports

python main-search.py create_cosmos_nosql_datasource dev airports
python main-search.py create_index nosql-airports aisearch/nosql_airports_index.json
python main-search.py create_indexer nosql-airports aisearch/nosql_airports_indexer.json

