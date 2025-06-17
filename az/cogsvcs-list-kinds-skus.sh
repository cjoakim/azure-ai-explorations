#!/bin/bash

# List the Kinds and SKUs for Azure Cognitive Services.
# See https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=cli
# Chris Joakim, 2025

source ./env.sh

echo "cogsvcs_rg:     "$cogsvcs_rg
echo "cogsvcs_region: "$cogsvcs_region

az cognitiveservices account list-kinds > tmp/cognitiveservices-list-kinds.json

az cognitiveservices account list-skus \
    --location $cogsvcs_region > tmp/cognitiveservices-list-skus.json

az cognitiveservices account list-skus \
    --kind OpenAI \
    --location $cogsvcs_region > tmp/cognitiveservices-list-skus-openai.json

az cognitiveservices account list-skus \
    --kind CognitiveServices \
    --location $cogsvcs_region > tmp/cognitiveservices-list-skus-cogsvcs.json

az cognitiveservices account list-skus \
    --kind ComputerVision \
    --location $cogsvcs_region > tmp/cognitiveservices-list-skus-cv.json

echo 'done'

# Kinds list below:
# [
#   "AIServices",
#   "AnomalyDetector",
#   "CognitiveServices",
#   "ComputerVision",
#   "ContentModerator",
#   "ContentSafety",
#   "ConversationalLanguageUnderstanding",
#   "CustomVision.Prediction",
#   "CustomVision.Training",
#   "Face",
#   "FormRecognizer",
#   "HealthInsights",
#   "ImmersiveReader",
#   "Internal.AllInOne",
#   "LUIS.Authoring",
#   "LanguageAuthoring",
#   "MetricsAdvisor",
#   "OpenAI",
#   "Personalizer",
#   "QnAMaker.v2",
#   "SpeechServices",
#   "TextAnalytics",
#   "TextTranslation"
# ]
