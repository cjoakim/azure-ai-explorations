#!/bin/bash

# Capture info about your Azure Cognitive Services account usage.
#
# Chris Joakim, 2025

source ./config.sh

echo "az cognitiveservices usage list ..."
az cognitiveservices usage list \
    --location $AZURE_FOUNDRY_REGION > tmp/usage-list.json

echo "az cognitiveservices account list-kinds ..."
az cognitiveservices account list-kinds > tmp/acct-list-kinds.json

echo "az cognitiveservices account list-models ..."
az cognitiveservices account list-models \
    --name $AZURE_FOUNDRY_NAME \
    --resource-group $AZURE_FOUNDRY_RG > tmp/acct-list-models.json

echo "az cognitiveservices account list-skus ..."
az cognitiveservices account list-skus \
    --name $AZURE_FOUNDRY_NAME \
    --resource-group $AZURE_FOUNDRY_RG > tmp/acct-list-skus1.json

echo "az cognitiveservices account list-skus AIServices ..."
az cognitiveservices account list-skus \
    --kind AIServices \
    --location $AZURE_FOUNDRY_REGION \
    --name $AZURE_FOUNDRY_NAME \
    --resource-group $AZURE_FOUNDRY_RG > tmp/acct-list-skus-aisvcs.json

echo "az cognitiveservices account list-skus CognitiveServices ..."
az cognitiveservices account list-skus \
    --kind CognitiveServices \
    --location $AZURE_FOUNDRY_REGION \
    --name $AZURE_FOUNDRY_NAME \
    --resource-group $AZURE_FOUNDRY_RG > tmp/acct-list-skus-cogsvcs.json


echo "az cognitiveservices account list-usage ..."
# TODO - this is currently outputting an empty JSON array.  Why? 
az cognitiveservices account list-usage \
    --name $AZURE_FOUNDRY_NAME \
    --resource-group $AZURE_FOUNDRY_RG > tmp/acct-list-usage.json

echo "az cognitiveservices account deployment list ..."
az cognitiveservices account deployment list \
    --name $AZURE_FOUNDRY_NAME \
    --resource-group $AZURE_FOUNDRY_RG > tmp/acct-deployment-list.json
