#!/bin/bash

# List the models in your region.
#
# Chris Joakim, 2025

source ./config.sh

echo "az cognitiveservices model list ..."
az cognitiveservices model list \
    --location $AZURE_FOUNDRY_REGION > tmp/model-list.json
