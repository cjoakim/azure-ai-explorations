#!/bin/bash

# Delete and recreate the Azure Search index, indexer, and datasource
# for the Cosmos DB NoSQL dev/airports collection.
# Chris Joakim, 2025

source .venv/bin/activate

python main-search.py help

echo "=== SHELL deleting indexer, index, and datasource ==="
python main-search.py delete_indexer nosql-airports
python main-search.py delete_index nosql-airports
python main-search.py delete_datasource cosmosdb-nosql-dev-airports

echo "=== SHELL listing indexes, indexers, datasources (initial) ==="
python main-search.py list_indexes
python main-search.py list_indexers
python main-search.py list_datasources

echo "=== SHELL creating datasource, index, and indexer ==="
python main-search.py create_cosmos_nosql_datasource dev airports
python main-search.py create_index nosql-airports aisearch/nosql_airports_index.json
python main-search.py create_indexer nosql-airports aisearch/nosql_airports_indexer.json

echo "=== SHELL indexer status ==="
python main-search.py get_indexer_status nosql-airports

echo "=== SHELL listing indexes, indexers, datasources (eoj) ==="
python main-search.py list_indexes
python main-search.py list_indexers
python main-search.py list_datasources

echo "done"
