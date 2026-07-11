# World Cup 2026 End-to-End Data Engineering & BI Pipeline

An end-to-end Data Engineering project that simulates a production-ready hybrid ETL pipeline. The system extracts World Cup match data from a REST API, processes and cleans it using Python, loads it into a PostgreSQL relational database, and visualizes key performance metrics via a premium Power BI Dashboard.

---

## Project Architecture (Data Flow)

The pipeline follows a simple 3-step ETL process:

## Project Architecture (Data Flow)

```
[API / JSON Files]
         │
         ▼
    1. EXTRACT   --> Gets data from the API (or from local files if the API errors out)
         │
         ▼
    2. TRANSFORM --> Cleans and structures the data using Pandas
         │
         ▼
    3. LOAD      --> Saves the clean data into PostgreSQL using SQLAlchemy
         │
         ▼
[Power BI Dashboard]
```

### How it works:

1. **Extract**: The script fetches tournament data from a football REST API. If the API faces connectivity issues, a local fallback system automatically reads stored JSON files so the script doesn't crash.
2. **Transform**: I use `pandas` to flatten the nested JSON data, handle missing values, and organize everything into clean tables.
3. **Load**: The final data is automatically inserted into a **PostgreSQL** database via `SQLAlchemy`. From there, the database connects directly to **Power BI** for visualization.

## Dashboard Preview
![Dashboard Preview](dashboard.png)

---

## Architecture & Tech Stack
* **Language:** Python 3.x
* **Data Manipulation:** Pandas
* **Database & ORM:** PostgreSQL / SQLAlchemy
* **Visualization:** Power BI Desktop (Dark Mode, Containerized Layout)
* **Environment & Security:** `python-dotenv` for isolating API credentials

---

## ETL Flow & Data Pipeline

### 1. Extract
* Designed to connect to a commercial football REST API (`football-data.org`) to fetch raw match schedules and results in JSON format.
* **Hybrid/Mock Implementation:** Since live Cup data is locked behind premium API tiers, the pipeline includes a fully-tested fallback mechanism that loads local raw JSON snapshots from the `data_raw/` directory, ensuring seamless offline execution.

### 2. Transform (Feature Engineering)
* Cleans data types and standardizes naming conventions using **Pandas**.
* Computes business metrics such as **Attack Efficiency** (`eficienta_atac`), which tracks team goals scored.
* Implements dynamic conditional logic to flag tight knockout matches that went into extra time or penalties (`meci_cu_prelungiri`).

### 3. Load
* Connects securely to a local **PostgreSQL** database using `SQLAlchemy`.
* Automates database connection pooling and executes efficient data loading into relational schemas.

---

## Database Schema & Analytical Queries
Once loaded, the data is structured to allow deep SQL analysis. Example queries:

### 1. Top 5 most spectacular matches (by total goals scored)
```sql
SELECT 
    m.id_meci,
    m.faza_competitie,
    eg.nume_echipa AS echipa_gazda,
    eo.nume_echipa AS echipa_oaspete,
    m.eficienta_atac AS total_goluri
FROM meciuri_world_cup m
INNER JOIN echipe eg ON m.id_echipa_gazda = eg.id_echipa
INNER JOIN echipe eo ON m.id_echipa_oaspete = eo.id_echipa
ORDER BY m.eficienta_atac DESC
LIMIT 5;

``` 
### 2. Avarage goals scored by competition phase
```sql
SELECT  
    faza_competitie,
    COUNT(*) AS numar_meciuri,
    ROUND(AVG(eficienta_atac), 2) AS medie_goluri_pe_meci
FROM meciuri_world_cup
GROUP BY faza_competitie;

```
### 3. Home teams that scored above the overall tournament average
```sql
SELECT 
    eg.nume_echipa AS echipa_gazda,
    SUM(m.goluri_gazda) AS total_goluri_acasa,
    COUNT(*) AS meciuri_jucate_acasa
FROM meciuri_world_cup m
INNER JOIN echipe eg ON m.id_echipa_gazda = eg.id_echipa
GROUP BY eg.nume_echipa
HAVING AVG(m.goluri_gazda) > (SELECT AVG(goluri_gazda) FROM meciuri_world_cup)
ORDER BY total_goluri_acasa DESC;

```
### 4. Phase-Isolated Goal Rankings (Tracks and ranks the most explosive matches isolated inside each individual tournament phase, filtering out everything except the Top 2 matches per stage.)
```sql
WITH meciuri_rankate AS (
    SELECT 
        m.faza_competitie,
        eg.nume_echipa AS echipa_gazda,
        eo.nume_echipa AS echipa_oaspete,
        m.eficienta_atac AS total_goluri,
        DENSE_RANK() OVER (
            PARTITION BY m.faza_competitie 
            ORDER BY m.eficienta_atac DESC
        ) AS pozitie_top
    FROM meciuri_world_cup m
    INNER JOIN echipe eg ON m.id_echipa_gazda = eg.id_echipa
    INNER JOIN echipe eo ON m.id_echipa_oaspete = eo.id_echipa
)
SELECT * FROM meciuri_rankate 
WHERE pozitie_top <= 2;

```
### 5. Cumulative Team Performance Ledger (Aggregates and merges separate metrics for home and away profiles into a unified database leaderboard, demonstrating advanced dataset blending without data loss.)
```sql
WITH goluri_acasa AS (
    SELECT id_echipa_gazda AS id_echipa, SUM(goluri_gazda) AS goluri FROM meciuri_world_cup GROUP BY id_echipa_gazda
),
goluri_deplasare AS (
    SELECT id_echipa_oaspete AS id_echipa, SUM(goluri_oaspete) AS goluri FROM meciuri_world_cup GROUP BY id_echipa_oaspete
)
SELECT 
    e.nume_echipa,
    COALESCE(ga.goluri, 0) + COALESCE(gd.goluri, 0) AS total_goluri_marcate
FROM echipe e
LEFT JOIN goluri_acasa ga ON e.id_echipa = ga.id_echipa
LEFT JOIN goluri_deplasare gd ON e.id_echipa = gd.id_echipa
ORDER BY total_goluri_marcate DESC;

```

### UPGRADE
To implement industry best practices and ensure data integrity, the PostgreSQL database has been upgraded from a flat table structure to a **Normalized Relational Schema** (Star Schema approach). 

### Schema Overview
- **Dimension Table (`echipe`):** Stores unique participating countries to eliminate data redundancy and prevent text-spelling duplication.
- **Fact Table (`meciuri_world_cup`):** Stores analytical metrics and match events, utilizing optimized numeric `FOREIGN KEY` constraints pointing to the teams table.

### Relational Database Diagram
```
+-----------------------------------+
    |             ECHIPE                |  <----+
    +-----------------------------------+       |
    | PK | id_echipa (SERIAL)           |       | 
    |    | nume_echipa (VARCHAR)        |       | For Echipa Gazdă
    +-----------------------------------+       |
                                                |
                                                |
    +-----------------------------------+       |
    |        MECIURI_WORLD_CUP          |       |
    +-----------------------------------+       |
    | PK | id_meci (INT)                |       |
    |    | data_meci (DATE)             |       |
    |    | faza_competitie (VARCHAR)    |       |
    |    | status (VARCHAR)             |       |
    | FK | id_echipa_gazda (INT) -------+-------+
    | FK | id_echipa_oaspete (INT) -------------+ 
    |    | goluri_gazda (INT)                   | For Echipa Oaspete
    |    | goluri_oaspete (INT)                 |
    |    | eficienta_atac (INT)                 |
    |    | meci_cu_prelungiri (BOOLEAN)         |
    |    | scor_final_detaliat (VARCHAR)        |
    +-----------------------------------+
 ```   
### Core Technical Advantages:
1. **Storage Optimization:** Numeric IDs (`INT`) consume significantly less disk space compared to repeated long text strings (`VARCHAR`).
2. **Query Performance:** PostgreSQL indexes and filters numerical keys much faster than text matching.
3. **Data Integrity:** Strict database constraints prevent any accidental data corruption or inconsistent entries.
---

## Power BI Business Insights & Analytics

The interactive dashboard transforms raw match data into actionable sports analytics, focusing on team performance, tournament dynamics, and match intensity:

* **Top Performing Teams & Attack Efficiency:** Evaluates which countries dominated the tournament by aggregating goals scored (`eficienta_atac`) per match. This highlights the most explosive offenses and teams with the highest tactical consistency.
* **Match Intensity & Extra-Time Analytics:** Uses conditional logic fields (`meci_cu_prelungiri`) to isolate high-pressure games. This allows analysts to filter and analyze knockout stage drama, tracking how many games required overtimes or penalty shootouts.
* **Home vs. Away Performance Matrix:** Compares team statistics based on their stadium designation (`echipa_gazda` vs. `echipa_oaspeti`), revealing structural patterns in scoring trends and tournament advantages.
* **Dynamic Tournament Slicers:** Features advanced filtering components that let users instantly slice data by specific teams or match types, turning static relational database rows into an intuitive discovery tool.

---

## How to Run the Project Locally

1. **Clone the repository:**
```bash
   git clone [https://github.com/tomarobert-tech/world.cup-etl-pipeline.git](https://github.com/tomarobert-tech/world.cup-etl-pipeline.git)
   cd world.cup-etl-pipeline
```
2. **Install dependencies:**
```bash
   pip install -r requirements.txt
```
3. **Configure your Database:**
* Create a .env file in the root folder with your PostgreSQL credentials:
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_db_name

4. **Execute the pipeline:**
```bash
   python main.py
``` 