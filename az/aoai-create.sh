#!/bin/bash

# Create the Azure OpenAI account per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "subscription: "$subscription
echo "aoai_name:    "$aoai_name
echo "aoai_rg:      "$aoai_rg
echo "aoai_region:  "$aoai_region

# See cogsvcs-list-kinds-skus.sh to get the Kinds and SKUs available.

echo "Creating Azure OpenAI account..."
az cognitiveservices account create \
    --name $aoai_name \
    --resource-group $aoai_rg \
    --location $aoai_region \
    --kind OpenAI \
    --sku s0 \
    --subscription $subscription

echo 'done'
