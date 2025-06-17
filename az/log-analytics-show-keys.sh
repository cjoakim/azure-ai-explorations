#!/bin/bash

# Show the log analytics workspace and its keys per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "log_analytics_name: "$log_analytics_name
echo "log_analytics_rg:   "$log_analytics_rg

echo "az monitor log-analytics workspace show"
az monitor log-analytics workspace show \
    --resource-group $log_analytics_rg \
    --workspace-name $log_analytics_name > tmp/log-analytics-show.json

echo "az monitor log-analytics workspace get-shared-keys"
az monitor log-analytics workspace get-shared-keys \
    --resource-group $log_analytics_rg \
    --workspace-name $log_analytics_name > tmp/log-analytics-keys.json

cat tmp/log-analytics-keys.json

echo 'done'
