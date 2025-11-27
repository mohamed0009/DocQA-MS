-- ==========================================
-- DocQA-MS Database Initialization Script
-- ==========================================

-- Create databases for each microservice
CREATE DATABASE doc_ingestor;
CREATE DATABASE deid;
CREATE DATABASE indexeur;
CREATE DATABASE llm_qa;
CREATE DATABASE synthese;
CREATE DATABASE audit;

-- Create extensions
\c doc_ingestor;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c deid;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c indexeur;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c llm_qa;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c synthese;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c audit;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- Doc Ingestor Database Schema
-- ==========================================
\c doc_ingestor;

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    
    patient_id VARCHAR(100),
    document_date TIMESTAMP,
    document_type VARCHAR(100),
    author VARCHAR(255),
    department VARCHAR(100),
    
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    processing_error TEXT,
    
    extracted_text TEXT,
    extracted_metadata JSONB,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    
    CONSTRAINT unique_content_hash UNIQUE (content_hash)
);

CREATE INDEX idx_documents_patient_id ON documents(patient_id);
CREATE INDEX idx_documents_document_type ON documents(document_type);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
