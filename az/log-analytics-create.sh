#!/bin/bash

# Create the log analytics workspace per config in env.sh.
# Chris Joakim, 2025

source ./env.sh

echo "log_analytics_name: "$log_analytics_name
echo "log_analytics_rg:   "$log_analytics_rg

az monitor log-analytics workspace create \
    --resource-group $log_analytics_rg \
    --workspace-name $log_analytics_name

echo 'done'
