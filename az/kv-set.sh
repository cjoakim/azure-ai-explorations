#!/bin/bash

# Set a key vault secret, then display its value, per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "kv_name: "$kv_name
echo "kv_rg:   "$kv_rg

echo "az keyvault secret set..."
az keyvault secret set \
    --vault-name $kv_name \
    --name "cat" \
    --value "Elsa" \
    --disabled false 

echo "az keyvault secret show..."
az keyvault secret show \
    --vault-name $kv_name \
    --name "cat" \
    --query value -o tsv

echo 'done'
