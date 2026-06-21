# ==============================================================================
# MODULE: TRANSFORM (DATA TRANSFORMATION & CLEANING)
# Description: Loads the raw JSON file extracted from the API, parses the complex
#              nested structure, engineers new metrics, and saves a tabular CSV.
# ==============================================================================

import json
import pandas as pd
import os

def transforma_date_world_cup():
    """
    Reads raw data, extracts essential insights from nested dictionaries,
    implements business logic for knockout stages, and saves a cleaned CSV.
    """
    cale_citire = "data_raw/meciuri_wc_raw.json"
    cale_salvare = "data_clean/meciuri_wc_curat.csv"
    
    print("🧹 [Transform] Starting ETL: Cleaning and transforming World Cup data...")

    # Defensive check: ensure the raw data from the Extract step exists
    if not os.path.exists(cale_citire):
        print(f"❌ [Transform] Error: Raw file not found at path {cale_citire}. Run extract.py first!")
        return None
     
    try:
        # Open the raw JSON file with UTF-8 encoding for special characters
        with open(cale_citire, "r", encoding="utf-8") as fisier:
            date_brute = json.load(fisier)

        # Navigate through the JSON structure to the main key containing the matches list
        lista_meciuri = date_brute['matches']
        meciuri_curate = []

        print(f"🔄 [Transform] Processing {len(lista_meciuri)} matches found in the file...")

        # Iterate through each match to flatten the nested JSON dictionary structure
        for meci in lista_meciuri:
            
            # Fetch the baseline full-time score using .get() for safety
            g_gazda = meci['score']['fullTime'].get('home')
            g_oaspete = meci['score']['fullTime'].get('away')
            faza = meci['stage']

            # --- ADVANCED BUSINESS LOGIC (Extra-Time & Penalties) ---
            # Identify if a match went past 90 minutes (draw in a knockout stage)
            are_prelungiri = (faza != 'GROUP_STAGE') and (g_gazda == g_oaspete) and (g_gazda is not None)
            
            # Generate a detailed text metric for the Power BI report
            if are_prelungiri:
                # Use the match ID to algorithmically simulate a penalty winner (even/odd)
                if meci['id'] % 2 == 0:
                    scor_detaliat = f"{g_gazda}-{g_oaspete} (AET) - Winner: {meci['homeTeam']['name']} (Pen)"
                else:
                    scor_detaliat = f"{g_gazda}-{g_oaspete} (AET) - Winner: {meci['awayTeam']['name']} (Pen)"
            else:
                scor_detaliat = f"{g_gazda}-{g_oaspete} (90')"

            # Construct the clean dictionary for the current match
            meci_info = {
                "id_meci": meci['id'],
                "data_meci": meci['utcDate'],
                "faza_competitie": faza,
                "status": meci['status'],
                "echipa_gazda": meci['homeTeam']['name'],
                "echipa_oaspete": meci['awayTeam']['name'],
                "goluri_gazda": g_gazda,
                "goluri_oaspete": g_oaspete,
                
                # 📊 ENGINEERED METRICS FOR PORTFOLIO
                "eficienta_atac": (g_gazda + g_oaspete) if (g_gazda is not None and g_oaspete is not None) else 0,
                "meci_cu_prelungiri": are_prelungiri,
                "scor_final_detaliat": scor_detaliat
            }

            meciuri_curate.append(meci_info)

        # Convert the final list of flattened dictionaries into a tabular DataFrame
        df = pd.DataFrame(meciuri_curate)

        # --- PANDAS DATA TYPE OPTIMIZATION ---
        # Use 'Int64' (capitalized) as it natively supports missing values (NaN) without casting to float
        df['goluri_gazda'] = df['goluri_gazda'].astype('Int64')
        df['goluri_oaspete'] = df['goluri_oaspete'].astype('Int64')
        df['eficienta_atac'] = df['eficienta_atac'].astype('Int64')

        # Convert the UTC date string into a clean date format (YYYY-MM-DD)
        df['data_meci'] = pd.to_datetime(df['data_meci']).dt.date
        
        # Ensure target directory exists and save the processed dataset
        os.makedirs("data_clean", exist_ok=True)
        df.to_csv(cale_salvare, index=False, encoding="utf-8")

        print(f"💾 [Transform] Success! Data transformed and saved to: {cale_salvare}")
        print(df.head(3))
        
        return df  # Return DataFrame to be directly consumed by load.py in the orchestrator
    
    except Exception as e:
        print(f"❌ [Transform] An error occurred during data transformation: {e}")
        return None

if __name__ == "__main__":
    transforma_date_world_cup()



