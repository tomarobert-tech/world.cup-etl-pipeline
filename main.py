# ==============================================================================
# MAIN ORCHESTRATOR: main.py (TEST MODE - SKIPPING BYPASSED API)
# Description: Coordinates and executes the ETL pipeline sequentially.
#              Temporarily configured to use local JSON file to bypass 403 error.
# ==============================================================================

import os
from dotenv import load_dotenv

# Invoke environment variable loading prior to other module imports
load_dotenv()

from extract import extrage_meciuri_world_cup
from transform import transforma_date_world_cup
from load import incarca_date_in_sql

def ruleaza_tot_pipeline_ul():
    """
    Central function coordinating the data flow:
    [TEST MODE]: Skip Extract -> Transform (Local JSON) -> Load (Into PostgreSQL)
    """
    print("==================================================")
    print("STARTING AUTOMATED DATA ENGINEERING PIPELINE (ETL) - [TEST MODE]")
    print("==================================================")
    
    # ----------------------------------------------------
    # STAGE 1: EXTRACT (TEMPORARILY BYPASSED TO AVOID 403 ERROR)
    # ----------------------------------------------------
    print("[Extract] Test mode active: Skipping restricted API endpoint, loading local raw JSON snapshot.")
    # date_brute = extrage_meciuri_world_cup()
    # if date_brute is None:
        # print("Pipeline stopped: Extraction step did not return any data.")
        # return
        
    print("\n--------------------------------------------------")
    
    # ----------------------------------------------------
    # STAGE 2: TRANSFORM (DATA CLEANING & FEATURE ENGINEERING)
    # ----------------------------------------------------
    try:
        # The function will read the local JSON file from data_raw, 
        # clean the data, and return the DataFrame in memory.
        df_curat = transforma_date_world_cup()
        if df_curat is None:
            print("Pipeline stopped: Transformation step failed.")
            return
    except Exception as e:
        print(f"Pipeline stopped at Transformation stage due to a critical error: {e}")
        return
        
    print("\n--------------------------------------------------")
    
    # ----------------------------------------------------
    # STAGE 3: LOAD (STORAGE IN POSTGRESQL - IN-MEMORY)
    # ----------------------------------------------------
    try:
        # Send the clean data directly into the local PostgreSQL database
        incarca_date_in_sql(df_intrare=df_curat)
    except Exception as e:
        print(f"Pipeline stopped at Load stage: {e}")
        return
        
    print("==================================================")
    print("PIPELINE SUCCESSFULLY COMPLETED! (DATA REPROCESSED LOCALLY)")
    print("==================================================")

if __name__ == "__main__":
    ruleaza_tot_pipeline_ul()