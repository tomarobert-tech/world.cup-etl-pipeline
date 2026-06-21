# ==============================================================================
# MODULE: LOAD (DATA LOADING INTO POSTGRESQL)
# Description: Manages the connection to the PostgreSQL relational database and
#              loads the cleaned dataset using SQLAlchemy.
# ==============================================================================

import pandas as pd
from sqlalchemy import create_engine
import os

def incarca_date_in_sql(df_intrare=None):
    """
    Creates the connection engine and loads data into PostgreSQL.
    Supports both receiving a DataFrame directly in memory and reading from a CSV.
    """
    cale_citire = "data_clean/meciuri_wc_curat.csv"
    nume_tabel = "meciuri_world_cup"

    # 🔐 SECURE CREDENTIALS CONFIGURATION (Uses Environment Variables or Local Fallback)
    USER =  os.getenv("DB_USER", "postgres")           
    PAROLA = os.getenv("DB_PASSWORD", "Andrei27")         
    HOST = os.getenv("DB_HOST", "localhost")        
    PORT = os.getenv("DB_PORT", "5432")             
    DATABASE = os.getenv("DB_DATABASE", "fotbal_proiect")

    print("📥 [Load] Starting Load phase: Loading data into PostgreSQL...")

    try:
        # Determine data source: use direct DataFrame if provided; otherwise, read from CSV
        if df_intrare is not None:
            df = df_intrare
            print("🚀 [Load] Using processed data directly from memory (Efficient).")
        else:
            # Defensive check in case the script is run in isolation and reads from disk
            if not os.path.exists(cale_citire):
                print(f"❌ [Load] Error: Cleaned file not found at path '{cale_citire}'.")
                return False
            df = pd.read_csv(cale_citire)
            print(f"📂 [Load] Successfully read data from disk file: {cale_citire}")

        # Construct the standard connection URL for the PostgreSQL dialect
        url_conexiune = f"postgresql://{USER}:{PAROLA}@{HOST}:{PORT}/{DATABASE}"

        # Initialize the SQLAlchemy engine which handles the Connection Pool in the background
        engine = create_engine(url_conexiune)
        
        # 🔄 DATABASE LOADING OPERATION
        # `if_exists='replace'` drops the old table and recreates it with the new structure
        # `index=False` prevents Pandas from creating an extra, useless row index column
        df.to_sql(nume_tabel, engine, if_exists='replace', index=False)
        
        print(f"💾 [Load] Success! {len(df)} rows have been loaded into the '{nume_tabel}' table in PostgreSQL.")
        return True

    except Exception as e:
        # Catch specific errors: wrong credentials, database does not exist, or blocked port
        print(f"❌ [Load] An error occurred while loading data into PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    # Allows isolated module execution for quick connection testing
    incarca_date_in_sql()