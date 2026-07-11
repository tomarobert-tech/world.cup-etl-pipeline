-- ==============================================================================
-- SCRIPT: DATABASE UPGRADE (RELATIONAL SCHEMA)
-- Purpose: Normalize the database by separating teams from match events.
-- Architecture: Star Schema approach (1 Fact Table, 1 Dimension Table).
-- ==============================================================================

-- Drop existing tables safely using CASCADE to clear old flat structures
DROP TABLE IF EXISTS meciuri_world_cup CASCADE;
DROP TABLE IF EXISTS echipe CASCADE;

-- 1. CREATING THE DIMENSION TABLE (Teams)
-- Stores each participating country exactly once to prevent text duplication.
CREATE TABLE echipe (
    id_echipa SERIAL PRIMARY KEY,              -- Auto-incrementing unique ID (1, 2, 3...)
    nume_echipa VARCHAR(100) UNIQUE NOT NULL  -- Official country name, strictly unique
);

-- 2. CREATING THE FACT TABLE (Matches)
-- Stores metrics and structural core data using optimized numeric Foreign Keys.
CREATE TABLE meciuri_world_cup (
    id_meci INT PRIMARY KEY,                  -- Unique match identifier from the API
    data_meci DATE,                           -- Scheduled match date
    faza_competitie VARCHAR(50),               -- Tournament stage (e.g., GROUP_STAGE, FINAL)
    status VARCHAR(50),                        -- Match execution status (e.g., FINISHED)
    
    -- Relational mapping columns instead of plain text names
    id_echipa_gazda INT NOT NULL,             -- Foreign Key pointing to the Home Team
    id_echipa_oaspete INT NOT NULL,            -- Foreign Key pointing to the Away Team
    
    goluri_gazda INT,                         -- Goals scored by home team
    goluri_oaspete INT,                        -- Goals scored by away team
    eficienta_atac INT,                        -- Custom engineered metric for attack efficiency
    meci_cu_prelungiri BOOLEAN,                -- Flag indicating if extra time was played
    scor_final_detaliat VARCHAR(150),          -- Complete structural breakdown (e.g., penalties)
    
    -- Integrity constraints to safeguard database relationships
    CONSTRAINT fk_echipa_gazda FOREIGN KEY (id_echipa_gazda) REFERENCES echipe(id_echipa),
    CONSTRAINT fk_echipa_oaspete FOREIGN KEY (id_echipa_oaspete) REFERENCES echipe(id_echipa)
);