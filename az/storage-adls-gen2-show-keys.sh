#!/bin/bash

# Show the general info and keys for the storage account.
# Chris Joakim, 2025

source ./env.sh

echo "storage_adlsgen2_name:   "$storage_adlsgen2_name
echo "storage_adlsgen2_rg:     "$storage_adlsgen2_rg
echo "storage_adlsgen2_region: "$storage_adlsgen2_region

echo "az storage account show..."
az storage account show \
    -n $storage_adlsgen2_name \
    -g $storage_adlsgen2_rg \
    --subscription $subscription > tmp/storage-account-adlsgen2-show.json

echo "az storage account keys list..."
az storage account keys list \
    -n $storage_adlsgen2_name \
    -g $storage_adlsgen2_rg > tmp/storage-account-adlsgen2-keys.json

cat tmp/storage-account-adlsgen2-keys.json

echo 'done'
