#!/bin/bash

# Show the Cognitive Services Account(s) account per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "show AOAI account..."
az cognitiveservices account show \
    --name $aoai_name \
    --resource-group $aoai_rg > tmp/aoai-account-show.json

echo "list AOAI account keys..."
az cognitiveservices account keys list \
    --name $aoai_name \
    --resource-group $aoai_rg > tmp/aoai-account-keys.json

echo "show Foundry account..."
az cognitiveservices account show \
    --name $foundry_name \
    --resource-group $foundry_rg > tmp/foundry-account-show.json

echo "list Foundry account keys..."
az cognitiveservices account keys list \
    --name $foundry_name \
    --resource-group $foundry_rg > tmp/foundry-account-keys.json

echo "show DocIntel account..."
az cognitiveservices account show \
    --name $docintel_name \
    --resource-group $docintel_rg > tmp/docintel-account-show.json

echo "list DocIntel account keys..."
az cognitiveservices account keys list \
    --name $docintel_name \
    --resource-group $docintel_rg > tmp/docintel-account-keys.json

echo 'done'
