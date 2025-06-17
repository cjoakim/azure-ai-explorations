#!/bin/bash

# List the Cognitive Services Models available in the Azure region
# per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "cogsvcs_region: "$cogsvcs_region

az cognitiveservices model list \
    --location $cogsvcs_region > tmp/cognitiveservices-list-models.json
