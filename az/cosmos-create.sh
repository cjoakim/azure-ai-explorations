#!/bin/bash

# Create the Cosmos DB NoSQL API account per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

mkdir -p tmp

echo "cosmos_nosql_acct_name: "$cosmos_nosql_acct_name
echo "cosmos_nosql_rg:        "$cosmos_nosql_rg
echo "cosmos_nosql_region:    "$cosmos_nosql_region
echo "cosmos_nosql_dbname:    "$cosmos_nosql_dbname
echo "cosmos_nosql_cname:     "$cosmos_nosql_cname
echo "cosmos_nosql_pk:        "$cosmos_nosql_pk

echo "create account..."
az cosmosdb create \
    --resource-group $cosmos_nosql_rg \
    --name $cosmos_nosql_acct_name \
    --locations regionName=$cosmos_nosql_region

echo "update, add capabilities..."
az cosmosdb update \
    --resource-group $cosmos_nosql_rg \
    --name $cosmos_nosql_acct_name \
    --capabilities "EnableNoSQLVectorSearch"

echo "show account..."
az cosmosdb show \
    --name $cosmos_nosql_acct_name \
    --resource-group $cosmos_nosql_rg > tmp/cosmosdb-account-show.json

echo "create database..."
az cosmosdb sql database create \
    --account-name $cosmos_nosql_acct_name \
    --name $cosmos_nosql_dbname \
    --resource-group $cosmos_nosql_rg

echo "create container..."
az cosmosdb sql container create \
    --account-name $cosmos_nosql_acct_name \
    --database-name $cosmos_nosql_dbname \
    --name $cosmos_nosql_cname \
    --resource-group $cosmos_nosql_rg \
    --partition-key-path /pk \
    --max-throughput 10000 

    #--idx @cosmos/cosmosdb_nosql_libraries_index_policy_diskann.json
    # The syntax of the index policy JSON file isn't working with the CLI,
    # though the same JSON works with the Azure Portal.
    # Error message: The Vector Embedding Policy has an invalid Path:/embedding/. Specify the correct path for vector properties of your documents.

echo "show account again..."
az cosmosdb show \
    --name $cosmos_nosql_acct_name \
    --resource-group $cosmos_nosql_rg > tmp/cosmosdb-account-show2.json

echo "done"
