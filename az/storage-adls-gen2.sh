#!/bin/bash

# Create the storage account, with ADLS Gen2 capabilities,
# per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "storage_adlsgen2_name:   "$storage_adlsgen2_name
echo "storage_adlsgen2_rg:     "$storage_adlsgen2_rg
echo "storage_adlsgen2_region: "$storage_adlsgen2_region

az storage account create \
    --name $storage_adlsgen2_name \
    --resource-group $storage_adlsgen2_rg \
    --location $storage_adlsgen2_region \
    --sku Standard_LRS \
    --kind StorageV2 \
    --enable-hierarchical-namespace true

echo 'done'
