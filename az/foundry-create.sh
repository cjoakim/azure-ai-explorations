#!/bin/bash

# Create the foundry account per config in env.sh.
# See https://learn.microsoft.com/en-us/azure/ai-services/multi-service-resource?pivots=azcli
# Chris Joakim, 2025

source ./env.sh

echo "foundry_name:   "$foundry_name
echo "foundry_rg:     "$foundry_rg
echo "foundry_region: "$foundry_region

az cognitiveservices account create \
    --name $foundry_name \
    --resource-group $foundry_rg \
    --kind AIServices \
    --sku S0 \
    --location $foundry_region \
    --yes

echo 'done'
