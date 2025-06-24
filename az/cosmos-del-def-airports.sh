#!/bin/bash

# Delete/define then show a Cosmos DB NoSQL container.
# Chris Joakim, 2025

source ./env.sh

mkdir -p tmp

echo "cosmos_nosql_acct_name: "$cosmos_nosql_acct_name
echo "cosmos_nosql_rg:        "$cosmos_nosql_rg

echo "delete the airports container in the dev database..."
az cosmosdb sql container delete \
    --account-name $cosmos_nosql_acct_name \
    --database-name dev \
    --name airports \
    --resource-group $cosmos_nosql_rg \
    --yes

sleep 2

echo "create the airports container in the dev database..."
az cosmosdb sql container create \
    --account-name $cosmos_nosql_acct_name \
    --database-name dev \
    --name airports \
    --resource-group $cosmos_nosql_rg \
    --max-throughput 4000 \
    --partition-key-path /pk

sleep 2

echo "show the airports container in the dev database..."
az cosmosdb sql container show \
    --account-name $cosmos_nosql_acct_name \
    --database-name dev \
    --name airports \
    --resource-group $cosmos_nosql_rg > tmp/dev-airports-show.json

echo "done"
