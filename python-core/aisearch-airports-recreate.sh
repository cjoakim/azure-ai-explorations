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

echo "=== SHELL listing indexes, indexers, datasources (eoj) ==="
python main-search.py list_indexes
python main-search.py list_indexers
python main-search.py list_datasources

echo "=== SHELL lookups ==="
python main-search.py lookup_datasource cosmosdb-nosql-dev-airports
python main-search.py lookup_index nosql-airports
python main-search.py lookup_indexer nosql-airports
python main-search.py lookup_indexer_schema nosql-airports nosql-airports cosmosdb-nosql-dev-airports

echo "=== SHELL reset and run indexer, get indexer status ==="
python main-search.py reset_indexer nosql-airports
python main-search.py run_indexer nosql-airports
python main-search.py get_indexer_status nosql-airports

echo "=== SHELL execute several searches ==="
python main-search.py search_index nosql-airports airports_clt aisearch/searches.json
python main-search.py search_index nosql-airports airports_atl aisearch/searches.json
python main-search.py search_index nosql-airports airports_lucene_east_cl_south aisearch/searches.json

echo "done"


# python main-search.py delete_index nc-zipcodes
# python main-search.py create_index nc-zipcodes aisearch/nc_zipcodes_index.json

