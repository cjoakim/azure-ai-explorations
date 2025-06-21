#!/bin/bash

# Create an Azure AI Search account per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "ai_search_name: "$ai_search_name
echo "ai_search_rg:   "$ai_search_rg

az search service create \
    --resource-group $ai_search_rg \
    --name $ai_search_name \
    --sku basic \
    --location eastus

echo 'done'
