#!/bin/bash

# Deploy Model(s) to an Azure OpenAI account per config in env.sh.
# See the output of script cogsvcs-list-models.sh regarding the
# available models, their versions, and their SKU names.
# Chris Joakim, 2025

source ./env.sh

echo "aoai_name:    "$aoai_name
echo "aoai_rg:      "$aoai_rg

# az cognitiveservices account deployment create \
#     --name $aoai_name \
#     --resource-group $aoai_rg \
#     --deployment-name text-embedding-3-large \
#     --model-name text-embedding-3-large \
#     --model-format OpenAI \
#     --model-version "1" \
#     --sku-capacity "10" \
#     --sku-name "Standard"

az cognitiveservices account deployment create \
    --name $aoai_name \
    --resource-group $aoai_rg \
    --deployment-name gpt-4.1-mini \
    --model-name gpt-4.1-mini \
    --model-format OpenAI \
    --model-version "2025-04-14" \
    --sku-capacity "10" \
    --sku-name "S0"

echo 'done'
