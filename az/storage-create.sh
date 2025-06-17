#!/bin/bash

# Create the storage account per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "storage_name:   "$storage_name
echo "storage_rg:     "$storage_rg
echo "storage_region: "$storage_region

az storage account create \
    -n $storage_name \
    -g $storage_rg \
    -l $storage_region \
    --sku Standard_LRS

echo 'done'
