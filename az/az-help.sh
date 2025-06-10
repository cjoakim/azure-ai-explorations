#!/bin/bash

# Delete the contents of the tmp directory, then execute
# the several informational scripts in this directory.
#
# Chris Joakim, 2025


az cognitiveservices account --help > help/az-cognitiveservices-account.txt
az cognitiveservices account create --help > help/az-cognitiveservices-account-create.txt
az cognitiveservices account list --help > help/az-cognitiveservices-account-list.txt
az cognitiveservices account list-kinds --help > help/az-cognitiveservices-account-list-kinds.txt
az cognitiveservices account list-models --help > help/az-cognitiveservices-account-list-models.txt
az cognitiveservices account list-skus --help > help/az-cognitiveservices-account-list-skus.txt
az cognitiveservices account list-usage --help > help/az-cognitiveservices-account-list-usage.txt
az cognitiveservices account show --help > help/az-cognitiveservices-account-show.txt

az cognitiveservices model --help > help/az-cognitiveservices-model.txt
az cognitiveservices model list --help > help/az-cognitiveservices-model-list.txt

az cognitiveservices usage --help > help/az-cognitiveservices-usage.txt
az cognitiveservices usage list --help > help/az-cognitiveservices-usage-list.txt
