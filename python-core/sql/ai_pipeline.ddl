-- Delete/Define the tables and indexes in Azure PostgreSQL.

-- The general system design is that the "raw" and "preprocessed"
-- text data is persisted in Azure Blob Storage, while the more refined
-- Questions and Answers are persisted in Azure PostgreSQL.
--
-- The Data-Ingestion subsystem doesn't necessarily have to 
-- populate the "documents" table at time of raw data ingestion.
-- However, the Data-Ingestion subsystem should attach suffcient
-- metadata to the raw blobs such that the documents table can
-- be populated by another process which scans the raw container 
-- for both blobs and their metadata.
-- 
-- psql shell commands to setup the "qna" database:
-- postgres=> create database qna owner cjoakim;
-- \c qna
-- qna=> CREATE EXTENSION IF NOT EXISTS age CASCADE;
-- qna=> CREATE EXTENSION IF NOT EXISTS vector CASCADE;
-- qna=> CREATE EXTENSION IF NOT EXISTS PG_DISKANN CASCADE;
-- qna=> CREATE EXTENSION IF NOT EXISTS AZURE_AI CASCADE;


SET search_path TO qna, public;

DROP TABLE IF EXISTS configuration CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS extracted_qna CASCADE;
DROP TABLE IF EXISTS teams_qna CASCADE;
DROP TABLE IF EXISTS activity_log CASCADE;


-- The "configuration" table contains rows with names like "pipeline"
-- which contains the JSON configuration for that process.

CREATE TABLE configuration (
    name        VARCHAR(64) primary key,
    data        JSONB
);


-- The "documents" table associates a source system document with its'
-- location(s) in Azure Blob Storage, along with processing state 
-- columns which are updated as the document traverses the AI QnA
-- extraction processing pipeline.
-- processing_state values:
--   "raw" = the raw document from a source system was landed in blob storage
--   "preprocessed" = the raw document was processed with DI, chunked, etc 
--   "qna_extracted" = final state; the QnAs will be decisioned downstream
--                     see the extracted_qna table
--   "reprocess" = manually set to this value to trigger reprocessing

CREATE TABLE documents (
    id                 SERIAL primary key,

    -- the source of the document
    source_system              VARCHAR(128) NOT NULL,
    source_path                VARCHAR(1024) NOT NULL,

    -- the raw blob as landed from source to Azure Blob Storage
    raw_container              VARCHAR(64) NOT NULL,
    raw_file_name              VARCHAR(128) NOT NULL,
    raw_file_size              INTEGER,
    raw_etag                   VARCHAR(32) NOT NULL,
    raw_file_type              VARCHAR(8) NOT NULL,
    raw_storage_path           VARCHAR(1024) NOT NULL,
    raw_inserted_at            TIMESTAMP,

    processing_state           VARCHAR(64) NOT NULL,

    -- columns related to initial preprocessing of the raw document
    preprocessed_container     VARCHAR(64),
    preprocessed_path          VARCHAR(1024),
    preprocessing_chunk_count  INTEGER,
    preprocessing_messages     JSONB,
    preprocessed_at            TIMESTAMP,

    -- columns related to final processing of the preprocssed data
    qna_extracted_at           TIMESTAMP,
    qna_extracted_messages     JSONB
);


-- The "extracted_qna" table represents the QnAs extracted by the
-- AI pipeline from the raw and preprocessed data.
-- These questions and answers, in turn, have their own
-- processing pipeline which includes a "human in the loop"
-- review of them before they may be ported to the "production"
-- Teams application.
-- document_id = the corresponding id in the documents table
-- question_id = 0 for questions. for answers it points to the id of the question
-- type values:
--   "q" = question
--   "a" = answer
-- processing_state values:
--   "initial" = candidate Q or A extracted via the AI pipeline
--   "system_rejected" = duplicate or error detected by the system
--   "system_approved" = system determined that the Q or A should be human reviewed
--   "human_rejected"  = The human-in-the-loop rejected the Q or A
--   "human_approved"  = The human-in-the-loop approved the Q or A
-- system_hints = existing similar questiions or answers that the
--                human may wish to reference in the review process.
--                these may be identified by vector search and other means.

CREATE TABLE extracted_qna (
    id                 SERIAL primary key,
    document_id                INTEGER,
    question_id                INTEGER,
    type                       CHAR NOT NULL,
    value                      VARCHAR(2048) NOT NULL,
    created_at                 TIMESTAMP,

    embedding                  VECTOR(1536),

    processing_state           VARCHAR(64) NOT NULL,

    system_decisioned_at       TIMESTAMP,
    system_comment             VARCHAR(1024),
    system_hints               JSONB,

    human_decisioned_at        TIMESTAMP,
    human_reviewer_id          VARCHAR(64),
    human_reviewer_comment     VARCHAR(1024),

    teams_loaded_at            TIMESTAMP,

    CONSTRAINT fk_document_id
      FOREIGN KEY(document_id)
        REFERENCES documents(id)
);


-- This table represents the Questions and Answers in the
-- "production" Teams system.  Fetch this data from Teams periodically.
-- These are used to detect duplicates and determine additional QnAs. 
-- type values:
--   "q" = question
--   "a" = answer

CREATE TABLE teams_qna (
    id                 SERIAL primary key,
    type                       CHAR,
    value                      VARCHAR(2048),
    embedding                  VECTOR(1536)
);


-- The activity_log table captures "who did what, when" for the system.
-- It can record both system-generated and human-generated activity.
-- type values:
--   "s" = system
--   "h" = human
-- level values:
--   "n" = normal event
--   "e" = error
-- message = the system or human message or comment
-- data = optional supplemental information

CREATE TABLE activity_log (
    id                 SERIAL primary key,
    created_at                 TIMESTAMP,
    type                       CHAR NOT NULL,
    level                      CHAR NOT NULL,
    process_name               VARCHAR(64) NOT NULL,
    human_id                   VARCHAR(64) NOT NULL,
    message                    VARCHAR(128) NOT NULL,
    data                       JSONB NULL
);


-- TODO: create the necessary indexes for the above tables 
-- Examples for the activity_log table are implemented below.


-- indexes for the activity_log table

DROP INDEX IF EXISTS idx_activity_log_type;
CREATE INDEX idx_activity_log_type
ON activity_log(type);

DROP INDEX IF EXISTS idx_activity_log_level;
CREATE INDEX idx_activity_log_level
ON activity_log(level);

DROP INDEX IF EXISTS idx_activity_log_process_name;
CREATE INDEX idx_activity_log_process_name
ON activity_log(process_name);
