# ==============================================================================
# MODULE: EXTRACT (REST API DATA EXTRACTION)
# Description: Connects to the secure football-data.org API, utilizes an
#              authentication token, and downloads World Cup match data.
# ==============================================================================

import requests
import json
import os

def extrage_meciuri_world_cup():
    """
    Function that calls the REST API and downloads raw match data.
    Returns a Python dictionary (JSON) if successful, or None on error.
    """
    # Official endpoint URL for World Cup (WC) matches
    URL = "https://api.football-data.org/v4/competitions/WC/matches"

    # Unique authentication key generated on the football-data.org platform
    API_KEY = os.getenv("FOOTBALL_API_KEY")

    # Set HTTP headers required by the server for identity validation (Bearer-like Token)
    headers = {
        "X-Auth-Token": API_KEY
    }
    
    print("[Extract] Sending HTTP request to the Football-Data server...")

    try:
        # Execute GET request, sending the security token in the headers
        raspuns = requests.get(URL, headers=headers, timeout=10)

        print(f"[Extract] Server responded with Status Code: {raspuns.status_code}")

        # Check if the request was successful (HTTP Code 200 OK)
        if raspuns.status_code == 200:
            print("[Extract] Connection successful! Data downloaded into memory.")

            date_brute = raspuns.json()

            # Create the 'data_raw' directory if it doesn't exist in the project structure
            os.makedirs("data_raw", exist_ok=True)

            cale_salvare = "data_raw/meciuri_wc_raw.json"
            # Save local raw JSON snapshot for auditing and backup purposes
            with open(cale_salvare, "w", encoding="utf-8") as fisier:
                json.dump(date_brute, fisier, indent=4, ensure_ascii=False)

            print(f"[Extract] Success! Raw data saved to: {cale_salvare}")
            
            # IMPORTANT: Return data to be processed by the rest of the pipeline
            return date_brute

        # Handle commercial API specific tier restrictions
        elif raspuns.status_code == 403:
            print("[Extract] Error 403 (Forbidden): API key is valid, but World Cup data is restricted on the free tier.")
            print(f"Server detail: {raspuns.text}")
            return None

        elif raspuns.status_code == 401:
            print("[Extract] Error 401 (Unauthorized): API key is invalid or missing from Headers.")
            return None
    
        else:
            print(f"[Extract] Server returned an unexpected error. Code: {raspuns.status_code}")
            return None

    except Exception as e:
        # Catch network hardware errors or lack of internet connection
        print(f"[Extract] System encountered a critical network error: {e}")
        return None

if __name__ == "__main__":
    # Allows isolated script testing during development phase
    extrage_meciuri_world_cup()



