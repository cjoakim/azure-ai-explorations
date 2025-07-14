#!/bin/bash

source .venv/bin/activate
python --version
sleep 1

python main-blob-pipeline.py delete_define_ai_pipeline_tables
sleep 1

python main-blob-pipeline.py load_configuration pipeline config/pipeline_config.json
sleep 1

python main-blob-pipeline.py load_documents_per_raw_container
