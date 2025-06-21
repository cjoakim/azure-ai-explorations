#!/bin/bash

# Show the AI Search account info, and its keys, per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "ai_search_name: "$ai_search_name
echo "ai_search_rg:   "$ai_search_rg

echo "az search service show"
az search service show \
    --resource-group $ai_search_rg \
    --name $ai_search_name \
    --subscription $AZURE_SUBSCRIPTION_ID > tmp/ai-search-show.json

az search query-key list \
    --resource-group $ai_search_rg \
    --service-name $ai_search_name > tmp/ai-search-query-key.json

az search admin-key show \
    --resource-group $ai_search_rg \
    --service-name $ai_search_name > tmp/ai-search-admin-key.json

echo 'show:'
cat tmp/ai-search-show.json

echo 'query-key:'
cat tmp/ai-search-query-key.json

echo 'admin-key:'
cat tmp/ai-search-admin-key.json

echo 'done'
