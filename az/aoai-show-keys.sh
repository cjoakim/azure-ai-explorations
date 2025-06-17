#!/bin/bash

# Show the AOAI account and keys per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "show AOAI account..."
az cognitiveservices account show \
    --name $aoai_name \
    --resource-group $aoai_rg > tmp/aoai-account-show.json

echo "list AOAI account deployments..."
az cognitiveservices account deployment list \
    --name $aoai_name \
    --resource-group $aoai_rg > tmp/aoai-account-deployment-list.json

echo "list AOAI account keys..."
az cognitiveservices account keys list \
    --name $aoai_name \
    --resource-group $aoai_rg > tmp/aoai-account-keys.json

echo 'done'
