#!/bin/bash

# Create the app insights account per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "app_insights_name:   "$app_insights_name
echo "app_insights_rg:     "$app_insights_rg
echo "app_insights_region: "$app_insights_region

echo "az monitor app-insights component create..."
az monitor app-insights component create \
    --resource-group $app_insights_rg \
    --app $app_insights_name \
    --location $app_insights_region

echo 'done'
