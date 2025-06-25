#!/bin/bash

# Show a Cosmos DB container, with index policy, per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

mkdir -p tmp

echo "cosmos_nosql_acct_name: "$cosmos_nosql_acct_name
echo "cosmos_nosql_rg:        "$cosmos_nosql_rg
echo "cosmos_nosql_region:    "$cosmos_nosql_region
echo "cosmos_nosql_dbname:    "$cosmos_nosql_dbname
echo "cosmos_nosql_cname:     "$cosmos_nosql_cname

echo "show container..."
az cosmosdb sql container show \
    --account-name $cosmos_nosql_acct_name \
    --database-name $cosmos_nosql_dbname \
    --name $cosmos_nosql_cname \
    --resource-group $cosmos_nosql_rg > tmp/cosmos-container-show.json

echo "done"
