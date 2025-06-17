#!/bin/bash

# Create the resource group per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "primary_rg:     "$primary_rg
echo "primary_region: "$primary_region

az group create \
    --name $primary_rg \
    --location $primary_region

echo 'done'
