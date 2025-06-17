#!/bin/bash

# Show the Cosmos DB NoSQL API account and keys per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

mkdir -p tmp

echo "cosmos_nosql_acct_name: "$cosmos_nosql_acct_name
echo "cosmos_nosql_rg:        "$cosmos_nosql_rg
echo "cosmos_nosql_region:    "$cosmos_nosql_region
echo "cosmos_nosql_dbname:    "$cosmos_nosql_dbname
echo "cosmos_nosql_cname:     "$cosmos_nosql_cname
echo "cosmos_nosql_pk:        "$cosmos_nosql_pk

echo "az cosmosdb show..."
az cosmosdb show \
    --name $cosmos_nosql_acct_name \
    --resource-group $cosmos_nosql_rg > tmp/cosmosdb-account-show.json

echo "az cosmosdb keys list..."
az cosmosdb keys list \
    --resource-group $cosmos_nosql_rg \
    --name $cosmos_nosql_acct_name > tmp/cosmosdb-account-keys.json

cat tmp/cosmosdb-account-keys.json

echo "done"
