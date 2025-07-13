-- Delete/Define the tables and indexes in Azure PostgreSQL.

SET search_path TO public;

-- Delete/drop all of the tables and indexes in the system.

DROP TABLE IF EXISTS configuration CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS extracted_qna CASCADE;
DROP TABLE IF EXISTS teams_qna CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;


-- This table contains rows with names like "pipeline"
-- which contains the JSON configuration for that process.

CREATE TABLE configuration (
    name        VARCHAR(64) primary key,
    data        JSONB
);

-- The "documents" table associates a source system document with its'
-- location in Azure Blob Storage, along with processing state 
-- columns which are updated as the document traverses the AI QnA
-- extraction processing pipeline.
-- processing_state values:
--   "raw" = the raw document from a source system was landed in blob storage
--   "preprocessed" = the raw document was processed with DI, chunked, etc 
--   "qna_extracted" = final state; the QnAs will be decisioned downstream
--                     see the extracted_qna table
--   "reprocess" = manually set to this value to trigger reprocessing

CREATE TABLE documents (
    id                 INTEGER primary key,

    -- the source of the document
    source_system              VARCHAR(128),
    source_path                VARCHAR(1024),

    -- the raw blob as landed from source to Azure Blob Storage
    raw_file_name              VARCHAR(128),
    raw_file_size              INTEGER,
    raw_file_type              VARCHAR(8),
    raw_storage_path           VARCHAR(1024),
    raw_inserted_at            TIMESTAMP,

    processing_state           VARCHAR(64),

    -- columns related to initial preprocessing of the raw document
    preprocessed_at            TIMESTAMP,
    preprocessed_dir_path      VARCHAR(1024),
    preprocessing_chunk_count  INTEGER,
    preprocessing_messages     JSONB,

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
-- processing_state values:
--   "initial" = candidate Q or A extracted via the AI pipeline
--   "system_rejected" = duplicate or error detected by the system
--   "system_approved" = system determined that the Q or A should be human reviewed
--   "human_rejected"  = The human-in-the-loop rejected the Q or A
--   "human_approved"  = The human-in-the-loop approved the Q or A
-- type values:
--   "q" = question
--   "a" = answer

CREATE TABLE extracted_qna (
    id                 INTEGER primary key,
    document_id                INTEGER,
    question_id                INTEGER,
    type                       CHAR,
    value                      VARCHAR(2048),
    embedding                  VECTOR(1536)
    created_at                 TIMESTAMP,

    processing_state           VARCHAR(64),

    system_decisioned_at       TIMESTAMP,
    system_comment             VARCHAR(1024),

    human_decisioned_at        TIMESTAMP,
    human_reviewer_id          VARCHAR(64),
    human_reviewer_comment     VARCHAR(1024),

    teams_loaded_at            TIMESTAMP
);


-- This table represents the Questions and Answers in the
-- "production" Teams system.  Fetch this data from Teams periodically.
-- These are used to detect duplicates and determine additional QnAs. 
-- type values:
--   "q" = question
--   "a" = answer

CREATE TABLE teams_qna (
    id                 INTEGER primary key,
    type                       CHAR,
    value                      VARCHAR(2048),
    embedding                  VECTOR(1536)
);

-- The audit_log table captures "who did what, when" for the system.
-- It can record both system-generated and human-generated activity.
-- type values:
--   "s" = system
--   "h" = human
-- level values:
--   "n" = normal event
--   "e" = error
-- process_id - either a system ID or human user ID
-- message = the system or human message or comment
-- data = optional supplemental information

CREATE TABLE audit_log (
    id                 INTEGER primary key,
    created_at                 TIMESTAMP,
    type                       CHAR NOT NULL,
    level                      CHAR NOT NULL,
    process_id                 VARCHAR(128) NOT NULL,
    message                    VARCHAR(128) NOT NULL,
    data                       JSONB NULL
);


-- TODO: create the necessary indexes for the above tables 
