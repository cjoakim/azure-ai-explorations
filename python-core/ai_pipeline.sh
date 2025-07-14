#!/bin/bash

source .venv/bin/activate
python --version
sleep 1

echo "========== Deleting AI Pipeline Tables =========="
python main-blob-pipeline.py delete_define_ai_pipeline_tables
sleep 1

echo "========== Loading pipeline config JSON into DB =========="
python main-blob-pipeline.py load_configuration pipeline config/pipeline_config.json
sleep 1

echo "========== Loading documents from raw container into DB =========="
python main-blob-pipeline.py load_documents_per_raw_container
sleep 1

echo "========== Loading documents again from raw container into DB =========="
python main-blob-pipeline.py load_documents_per_raw_container

echo "done"
