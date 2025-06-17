#!/bin/bash

# Show the key vault per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "kv_name: "$kv_name
echo "kv_rg:   "$kv_rg

echo "az keyvault show..."
az keyvault show \
    --name $kv_name \
    --resource-group $kv_rg > tmp/kv-show.json

# This requires elevated permissions, it currently outputs an empty list.
echo "az keyvault key list..."
az keyvault key list \
    --vault-name $kv_name \
    --include-managed false > tmp/kv-keys.json

echo 'done'
