#!/bin/bash

# Show the app insights account and InstrumentationKey per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "app_insights_name: "$app_insights_name
echo "app_insights_rg:   "$app_insights_rg

echo "az monitor app-insights component show..."
az monitor app-insights component show \
    --resource-group $app_insights_rg \
    --app $app_insights_name > tmp/app-insights-show.json

echo "az resource show..."
az resource show \
    -g $app_insights_rg \
    -n $app_insights_name \
    --resource-type "microsoft.insights/components" > tmp/app-insights-resource-show.json
    # --query properties.InstrumentationKey

cat tmp/app-insights-resource-show.json | grep InstrumentationKey

echo 'done'
