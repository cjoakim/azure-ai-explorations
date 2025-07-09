#!/bin/bash

# List the Azure regions available to your subscription.
#
# Chris Joakim, 2025

source ./config.sh

echo "az account list-locations names ..."
az account list-locations --query "[].{Region:name}" --out table > tmp/region-names.txt 

echo "az account list-locations datails ..."
az account list-locations --out json > tmp/region-details.json 

# cat tmp/region-names.txt | grep norway 
# norwayeast
# norway
# norwaywest
