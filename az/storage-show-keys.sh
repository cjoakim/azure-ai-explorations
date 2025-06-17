#!/bin/bash

# Create the storage account and its keys per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "storage_name:   "$storage_name
echo "storage_rg:     "$storage_rg
echo "storage_region: "$storage_region

echo "az storage account show..."
az storage account show \
    -n $storage_name \
    -g $storage_rg \
    --subscription $subscription > tmp/storage-account-show.json

echo "az storage account keys list..."
az storage account keys list \
    -n $storage_name \
    -g $storage_rg > tmp/storage-account-keys.json

cat tmp/storage-account-keys.json

echo 'done'
