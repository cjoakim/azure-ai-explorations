#!/bin/bash

# Show the Foundry account and keys per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "show Foundry account..."
az cognitiveservices account show \
    --name $foundry_name \
    --resource-group $foundry_rg > tmp/foundry-account-show.json

echo "list Foundry account keys..."
az cognitiveservices account keys list \
    --name $foundry_name \
    --resource-group $foundry_rg > tmp/foundry-account-keys.json

echo 'done'
