#!/bin/bash

# Capture info about your Azure Cognitive Services accounts.
#
# Chris Joakim, 2025

source ./config.sh

echo "az cognitiveservices account list ..."
az cognitiveservices account list > tmp/cogsvcs-account-list.json

echo "az cognitiveservices account show ..."
az cognitiveservices account show \
    --name $AZURE_FOUNDRY_NAME \
    --resource-group $AZURE_FOUNDRY_RG > tmp/cogsvcs-account-show.json

echo "az cognitiveservices account list-kinds ..."
az cognitiveservices account list-kinds > tmp/cogsvcs-account-list-kinds.json

echo "az cognitiveservices account keys list ..."
az cognitiveservices account keys list \
    --name $AZURE_FOUNDRY_NAME \
    --resource-group $AZURE_FOUNDRY_RG > tmp/cogsvcs-account-keys-list.json
