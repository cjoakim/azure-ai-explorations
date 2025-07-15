#!/bin/bash

source .venv/bin/activate
python --version
sleep 1

echo "========== Delete-Define AI Pipeline Tables =========="
python main-blob-pipeline.py delete_define_ai_pipeline_tables
sleep 1

echo "========== Creating AI Pipeline Config JSON File =========="
python main-blob-pipeline.py create_ai_pipeline_config_json_file
sleep 1

echo "========== Loading AI Pipeline config JSON into DB =========="
python main-blob-pipeline.py load_configuration ai_pipeline config/ai_pipeline_config.json
sleep 1

echo "========== Creating storage containers =========="
python main-blob-pipeline.py create_storage_containers
sleep 1

echo "========== Uploading blobs into raw container =========="
rm tmp/*.*
cp ../data/docs/* tmp/
python main-blob-pipeline.py upload_blobs_into_raw_container tmp
sleep 1

echo "========== Loading documents from raw container into DB =========="
python main-blob-pipeline.py load_documents_per_raw_container
sleep 1

echo "========== Extracting text from documents =========="
python main-blob-pipeline.py extract_text_from_documents

echo "========== AI Processing of extracted text =========="
python main-blob-pipeline.py ai_process_extracted_text

echo "========== Evaluating extracted QnAs =========="
python main-blob-pipeline.py evaluate_extracted_qnas

echo "done"
