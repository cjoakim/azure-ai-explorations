#!/bin/bash

# List the quota and usage for the various models.
# Chris Joakim, 2025

source ./env.sh

echo "cogsvcs_region: "$cogsvcs_region

echo "az cognitiveservices usage list..."
az cognitiveservices usage list \
    --location $cogsvcs_region > tmp/cognitiveservices-quota-usage.json

echo 'done'
