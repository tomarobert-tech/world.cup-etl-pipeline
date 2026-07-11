# ==============================================================================
# MODULE: LOAD (DATA LOADING INTO POSTGRESQL)
# Description: Manages the connection to the PostgreSQL relational database and
#              loads the cleaned dataset using SQLAlchemy.
# ==============================================================================

import pandas as pd
from sqlalchemy import create_engine, text
import os

def incarca_date_in_sql(df_intrare=None):
    """
    Loads cleaned match data into PostgreSQL using a Normalized Relational Schema.
    Dynamically maps team text names into strict numeric database Foreign Keys.
    """
    cale_citire = "data_clean/meciuri_wc_curat.csv"

    # Environment variables fallback values configuration
    USER = os.getenv("DB_USER", "postgres")          
    PAROLA = os.getenv("DB_PASSWORD", "Andrei27")         
    HOST = os.getenv("DB_HOST", "localhost")        
    PORT = os.getenv("DB_PORT", "5432")             
    DATABASE = os.getenv("DB_DATABASE", "fotbal_proiect")

    print("[Load] Starting Relational Load phase...")

    try:
        # Check if pipeline passed an in-memory DataFrame, otherwise read backup CSV
        if df_intrare is not None:
            df = df_intrare
        else:
            if not os.path.exists(cale_citire):
                print(f"[Load] Error: Cleaned file not found at path '{cale_citire}'.")
                return False
            df = pd.read_csv(cale_citire)

        # Initialize the SQLAlchemy database database engine connection
        url_conexiune = f"postgresql://{USER}:{PAROLA}@{HOST}:{PORT}/{DATABASE}"
        engine = create_engine(url_conexiune)
        
        # --- DATA ENGINEERING LOGIC: RELATIONAL MAPPING & INGESTION ---
        
        # 1. Isolate every unique team name AND drop any null/empty values safely (.dropna())
        echipe_unice = pd.concat([df['echipa_gazda'], df['echipa_oaspete']]).dropna().unique()
        
        # Create the DataFrame and filter out any accidental empty strings
        df_echipe = pd.DataFrame(echipe_unice, columns=['nume_echipa'])
        df_echipe = df_echipe[df_echipe['nume_echipa'].astype(str).str.strip() != '']
        df_echipe = df_echipe.sort_values('nume_echipa').reset_index(drop=True)
        
        # Drop any rows where home team or away team names are missing entirely
        df = df.dropna(subset=['echipa_gazda', 'echipa_oaspete'])
        
        # Open a secure database transaction block using context manager
        with engine.begin() as conexiune:
            
            # Defensive DDL initialization: drop and recreate structural rules
            conexiune.execute(text("DROP TABLE IF EXISTS meciuri_world_cup CASCADE;"))
            conexiune.execute(text("DROP TABLE IF EXISTS echipe CASCADE;"))
            
            conexiune.execute(text("""
                CREATE TABLE echipe (
                    id_echipa SERIAL PRIMARY KEY,
                    nume_echipa VARCHAR(100) UNIQUE NOT NULL
                );
            """))
            
            conexiune.execute(text("""
                CREATE TABLE meciuri_world_cup (
                    id_meci INT PRIMARY KEY,
                    data_meci DATE,
                    faza_competitie VARCHAR(50),
                    status VARCHAR(50),
                    id_echipa_gazda INT NOT NULL,
                    id_echipa_oaspete INT NOT NULL,
                    goluri_gazda INT,
                    goluri_oaspete INT,
                    eficienta_atac INT,
                    meci_cu_prelungiri BOOLEAN,
                    scor_final_detaliat VARCHAR(150),
                    CONSTRAINT fk_echipa_gazda FOREIGN KEY (id_echipa_gazda) REFERENCES echipe(id_echipa),
                    CONSTRAINT fk_echipa_oaspete FOREIGN KEY (id_echipa_oaspete) REFERENCES echipe(id_echipa)
                );
            """))

            # Bulk insert unique records into the dimension table. IDs will auto-generate.
            df_echipe.to_sql('echipe', conexiune, if_exists='append', index=False)
            
            # Fetch the database-assigned Serial IDs back into memory for cross-mapping
            echipe_salvate = pd.read_sql("SELECT id_echipa, nume_echipa FROM echipe", conexiune)
            
            # Construct a high-performance runtime mapping dictionary (e.g., {"Mexico": 1})
            mapare_echipe = dict(zip(echipe_salvate['nume_echipa'], echipe_salvate['id_echipa']))
            
            # Map and transform textual country names into corresponding numeric IDs
            df['id_echipa_gazda'] = df['echipa_gazda'].map(mapare_echipe)
            df['id_echipa_oaspete'] = df['echipa_oaspete'].map(mapare_echipe)
            
            # ------------------------------ DEBUGING BLOCK ---------------------------------------------
            erori_gazda = df[df['id_echipa_gazda'].isna()]
            erori_oaspete = df[df['id_echipa_oaspete'].isna()]
            if not erori_gazda.empty or not erori_oaspete.empty:
                print("\n[DEBUG ALERT] S-au găsit probleme la maparea ID-urilor:")
                if not erori_gazda.empty:
                    print("Meciuri cu probleme la echipa GAZDA:")
                    print(erori_gazda[['id_meci', 'echipa_gazda', 'echipa_oaspete']])
                if not erori_oaspete.empty:
                    print("Meciuri cu probleme la echipa OASPETE:")
                    print(erori_oaspete[['id_meci', 'echipa_gazda', 'echipa_oaspete']])
                raise ValueError("Oprire controlată: Datele conțin valori nule la echipe!")
            # -------------------------------------------------------------------------------------------
            # Filter and realign columns to perfectly match the Fact table schema
            df_meciuri_final = df[[
                'id_meci', 'data_meci', 'faza_competitie', 'status', 
                'id_echipa_gazda', 'id_echipa_oaspete', 'goluri_gazda', 
                'goluri_oaspete', 'eficienta_atac', 'meci_cu_prelungiri', 'scor_final_detaliat'
            ]]
            
            # Bulk insert the relational facts into the final secured table
            df_meciuri_final.to_sql('meciuri_world_cup', conexiune, if_exists='append', index=False)
            
        print(f"[Load] Success! Relational database updated. Loaded {len(df_echipe)} teams and {len(df)} matches.")
        return True

    except Exception as e:
        print(f"[Load] Relational loading phase failed: {e}")
        return False