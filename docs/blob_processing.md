# Blob Processing Prototype 

## Containers

```
raw container:           di-sample-docs
bronze container:        di-preprocessed
telemetry container:     di-telemetry
testing container:       di-test
```

---

## Application Configuration

For now, use a **pipeline_config.json** local file.
Port this to the DB later.

---

## Container Functionality Tests

- capacity
- nesting
  - customer_id/source_id/filename (the path)
- listing of nested
- blob metadata
- ttl?

### Blob Test Util

- To execute the above functionality.
- Have the utility read and use the pipeline_config.json

---

## Pipeline Prototype

### Preprocessing

This logic requires connections to blob/lake storage, and the DB.

- read configuration from the database
- list all blobs in the raw container
- for each accepted filetype, process the file with Document Intelligence
  - accepted filetype is per config
  - check if this blob was already processed per DB lookup, documents table
  - if false
    - emit blob processing started message into the telemetry table
    - emit DI Markdown content files, for each input blob, into the bronze layer
      - create a directory path for each input blob
      - chunk the input into 1-many blobs
      - possible additional blobs, such as summary, toc, keywords, etc
    - emit blob processing completed message into the telemetry table
      - path
      - preprocessing_chunk_count
      - preprocessing_messages (jsonb)
      - preprocessing_errors (jsonb)

Simplicity: the Preprocessing part of the pipeline uses only Azure Storage.

## Azure PostgreSQL Relational Database

```
configuration
  - key   (varchar) - pipeline, qna_extraction, etc
  - value (jsonb)

documents
  - id
  - storage_acct
  - blob_path
  - file_size
  - file_type
  - processing_state
  - preprocessing_chunk_count
  - preprocessing_messages (jsonb)
  - preprocessing_errors (jsonb)
  - raw_timestamp
  - preprocess_timestamp
  - extraction_timestamp

telemetry


```
