#!/bin/bash

# Login to the az CLI program, set the subscription, and show the current account.
# Chris Joakim, 2025

echo 'logging in...'
az login

echo "subscription:  "$AZURE_SUBSCRIPTION_ID

echo 'setting subscription...'
az account set --subscription $AZURE_SUBSCRIPTION_ID

echo 'current account...'
az account show
az account show > tmp/az-account-show.txt

echo 'done'

