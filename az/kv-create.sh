#!/bin/bash

# Create the key vault per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "kv_name: "$kv_name
echo "kv_rg:   "$kv_rg

az keyvault create \
    --name $kv_name \
    --resource-group $kv_rg \
    --enable-rbac-authorization false

echo 'done'
